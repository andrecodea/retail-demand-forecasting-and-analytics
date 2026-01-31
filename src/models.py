import pandas as pd
import logging as log
import numpy as np
import datetime as dt
from datetime import timedelta
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression

def apply_clustering(df, n_clusters=4) -> pd.DataFrame:
    """
    Aplica K-Means para segmentar clientes.


    
    :param df: Objeto DataFrame contendo as colunas 'Total', 'Rating' e 'Quantity'.
    :param n_clusters: Quantidade de grupos desejados.
    :return: Retorna a um novo objeto DataFrame com a coluna 'Cluster'. Retorna o df original em exceções.
    :rtype: DataFrame
    """
    df_out = df.copy()

    # 1. Selecionar colunas obrigatórias
    required_features = ["Total", "Rating", "Quantity"]

    if not all(col in df_out.columns for col in required_features):
        return df_out

    if df_out.empty or len(df_out) < n_clusters:
        df_out['Cluster'] = 'N/A'
        return df_out
    
    try:
        df_model = df[required_features]

        # 2. Padronizar os dados
        scaler = StandardScaler()
        scaled_features = scaler.fit_transform(df_model)

        # 3. Criar e treinar o KMeans
        kmeans = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
            )
        df_out['Cluster'] = kmeans.fit_predict(scaled_features).astype(str)
    except Exception as e:
        log.error(f"Erro ao clusterizar: {e}")
        df_out['Cluster'] = 'Erro'

    return df_out

def apply_linear_regression(df, horizon_days=365): 

    df_out = df.copy()

    df_daily = df_out.groupby("Date")[["Total"]].sum().reset_index()

    # Feature Engineering: 01/01/2023 -> 738521
    df_daily['Date_Ordinal'] = df_daily['Date'].map(dt.datetime.toordinal)

    X = df_daily[['Date_Ordinal']]
    y = df_daily['Total']

    model = LinearRegression()
    model.fit(X, y)

    last_date = df_daily['Date'].max()
    future_dates = [last_date + dt.timedelta(days=x) for x in range(1, horizon_days + 1)]

    X_future = np.array([d.toordinal() for d in future_dates]).reshape(-1, 1)
    y_future = model.predict(X_future)

    df_pred = pd.DataFrame({'Date': future_dates, 'Total': y_future})
    df_pred['Type'] = 'Prediction'

    last_real = df_daily.iloc[-1]

    link_point = pd.DataFrame(
        {
            'Date': [last_real['Date']],
            'Total': [last_real['Total']],
            'Type' : ["Prediction"]
        }
    )

    df_pred = pd.concat([link_point, df_pred], ignore_index=True)

    df_daily['Type'] = 'Realized'
    viz_cols = ['Date', 'Total', 'Type']
    df_final = pd.concat([df_daily[viz_cols], df_pred[viz_cols]])

    tendency = model.coef_[0]

    return df_final, tendency
    