import pandas as pd
import logging as log
import numpy as np
import datetime as dt
from datetime import timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from openai import OpenAI
from dotenv import load_dotenv
from prophet import Prophet
from sklearn.metrics import silhouette_score, r2_score, mean_absolute_error, mean_squared_error
import time
import logging

load_dotenv()

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def apply_clustering(df, n_clusters=4):
    """Apply K-Means clustering and return labeled DataFrame plus metrics.

    The function selects the features ['Total', 'Rating', 'Quantity'],
    scales them with a StandardScaler, fits KMeans and appends the
    cluster labels as a string column 'Cluster'. It also computes
    inertia and silhouette score when possible.

    Parameters
    - df (pd.DataFrame): input dataset containing required features.
    - n_clusters (int): number of clusters to fit (default: 4).

    Returns
    - tuple: (df_out (pd.DataFrame), metrics (dict|None)). `metrics` is
      None if clustering could not be performed.
    """
    df_out = df.copy()
    required_features = ["Total", "Rating", "Quantity"]

    if not all(col in df_out.columns for col in required_features):
        return df_out, None

    if df_out.empty or len(df_out) < n_clusters:
        df_out["Cluster"] = "N/A"
        return df_out, None

    try:
        df_model = df[required_features]
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_model)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        labels = kmeans.fit_predict(scaled_features)

        df_out["Cluster"] = labels.astype(str)

        # Métricas de qualidade
        inertia = kmeans.inertia_
        sil_score = silhouette_score(scaled_features, labels)

        metrics = {"Inertia": inertia, "Silhouette Score": sil_score}

    except Exception as e:
        log.error(f"Error clustering: {e}")
        df_out["Cluster"] = "Error"
        metrics = None

    return df_out, metrics


def apply_prophet_forecast(df, horizon_days=365):
    """Train a Prophet model on weekly-aggregated data and return forecast.

    The function aggregates daily totals to weekly frequency (resample 'W')
    to reduce noise, fits a Prophet model with yearly seasonality and
    Brazilian holidays, and returns a DataFrame with predictions,
    a weekly tendency value and performance metrics (R2, MAE, RMSE).

    Parameters
    - df (pd.DataFrame): input DataFrame with a 'Date' datetime index or
      column and a 'Total' column with numeric values.
    - horizon_days (int): intended forecast horizon in days (currently
      mapped to ~52 weekly periods internally).

    Returns
    - tuple: (df_final (pd.DataFrame)|None, tendency (float)|None, metrics (dict)|None)
    """
    try:
        # 1) Aggregate to weekly series
        df_daily = df.groupby("Date")[["Total"]].sum()
        df_train = df_daily.resample("W").sum().reset_index()
        df_train = df_train.rename(columns={"Date": "ds", "Total": "y"})

        if len(df_train) < 10:
            return None, None, None

        # 2) Fit Prophet (weekly seasonality disabled because data is weekly)
        model = Prophet(yearly_seasonality=True, weekly_seasonality=False)
        model.add_country_holidays(country_name="BR")
        model.fit(df_train)

        # 3) Forecast 52 weeks (~1 year)
        future = model.make_future_dataframe(periods=52, freq="W")
        forecast = model.predict(future)

        # Metrics: compare overlapping predictions with historical data
        metric_df = forecast.set_index("ds")[["yhat"]].join(df_train.set_index("ds")[['y']], how="inner")
        y_true = metric_df['y']
        y_pred = metric_df['yhat']

        r2 = r2_score(y_true, y_pred)
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))

        metrics = {"R2 Score": r2, "MAE (Weekly)": mae, "RMSE": rmse}

        # Format output DataFrame
        df_final = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        df_final = df_final.rename(columns={"ds": "Date", "yhat": "Total", "yhat_lower": "Lower", "yhat_upper": "Upper"})

        last_real_date = df_train['ds'].max()
        df_final['Type'] = df_final['Date'].apply(lambda x: 'Realized' if x <= last_real_date else 'Prediction')

        # Overwrite realized values with actuals for better presentation
        df_final.loc[df_final['Type'] == 'Realized', 'Total'] = df_train['y'].values

        # Weekly tendency (average weekly growth)
        total_growth = df_final['Total'].iloc[-1] - df_train['y'].iloc[-1]
        tendency = total_growth / 52

        return df_final, tendency, metrics

    except Exception as e:
        log.error(f"Error in Prophet: {e}")
        return None, None, None


def generate_forecast_analysis(df_history, df_forecast, tendency):
    """Generate a short AI-driven financial analysis via streaming API.

    The function crafts a concise system prompt and streams responses
    from the OpenAI-compatible client to measure TTFT (time-to-first-token)
    and total latency. It returns the full text and a metrics dict.

    Parameters
    - df_history (pd.DataFrame): historical input data used for context.
    - df_forecast (pd.DataFrame): forecast DataFrame produced by Prophet.
    - tendency (float): computed weekly tendency value.

    Returns
    - tuple: (text (str), metrics (dict)) where metrics contains 'TTFT' and 'Latency'.
    """
    try:
        total_rev = df_history["Total"].sum()
        pred_val_end = df_forecast['Total'].iloc[-1]

        system_prompt = "You are a Senior Financial Analyst. Be concise and data-driven."
        prompt = f"""
        Analyze financial outlook:
        - Hist Revenue: U$ {total_rev:,.2f}
        - Trend: U$ {tendency:,.2f}/day
        - Forecast End: U$ {pred_val_end:,.2f}
        Write a short, concise, data driven report (max 150 words).
        Restrain yourself from using Markdown elements.
        """

        client = OpenAI(base_url="https://openrouter.ai/api/v1")

        start_time = time.time()

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            stream=True,
        )

        full_response = ""
        ttft = 0
        first_token = True

        for chunk in stream:
            if chunk.choices[0].delta.content:
                if first_token:
                    ttft = time.time() - start_time
                    first_token = False
                full_response += chunk.choices[0].delta.content

        end_time = time.time()
        total_latency = end_time - start_time

        metrics = {"TTFT": ttft, "Latency": total_latency}

        return full_response, metrics

    except Exception as e:
        log.error(f"AI Forecast error: {e}")
        return "Analysis unavailable.", {"TTFT": 0, "Latency": 0}


def generate_segmentation_analysis(df_clusters):
    """Generate a short AI-driven customer segmentation analysis via streaming.

    Uses cluster averages as context and streams a concise strategic
    recommendation. Returns the text and timing metrics (TTFT, Latency).
    """
    try:
        cluster_summary = df_clusters.groupby('Cluster')[["Total", "Rating", "Quantity"]].mean().to_dict()

        system_prompt = "You are a Customer Strategist."
        prompt = f"""
        Analyze 3 clusters (averages): {cluster_summary}
        Identify VIP vs Risk groups. Suggest 1 action. Max 150 words.
        Restrain yourself from using Markdown elements.
        """

        client = OpenAI(base_url="https://openrouter.ai/api/v1")

        start_time = time.time()

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
            stream=True,
        )

        full_response = ""
        ttft = 0
        first_token = True

        for chunk in stream:
            if chunk.choices[0].delta.content:
                if first_token:
                    ttft = time.time() - start_time
                    first_token = False
                full_response += chunk.choices[0].delta.content

        end_time = time.time()
        total_latency = end_time - start_time

        metrics = {"TTFT": ttft, "Latency": total_latency}

        return full_response, metrics

    except Exception as e:
        log.error(f"AI Segmentation error: {e}")
        return "Analysis unavailable.", {"TTFT": 0, "Latency": 0}