import pandas as pd
import logging
from datetime import timedelta, date
import plotly.express as px
import plotly.graph_objects as go

"""Plot helpers for the sales dashboard.

Each function accepts a pre-filtered pandas DataFrame and returns a
Plotly Figure or None on error. Comments are concise and technical in
Portuguese; docstrings provide usage details in English.
"""

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def plot_revenue_by_date(df: pd.DataFrame):
    """Create a line chart of total and gross income over time.

    The function groups data by 'Date', sums 'Total' and 'Gross income',
    and returns a Plotly line figure with a date range slider pre-set
    to the last 30 days (when possible).

    Parameters
    - df (pd.DataFrame): DataFrame containing at least 'Date', 'Total',
      and 'Gross income' columns.

    Returns
    - plotly.graph_objs._figure.Figure | None
    """
    try:
        df_copy = df.copy()
        df_daily = df_copy.groupby("Date")[['Total', 'Gross income']].sum().reset_index()

        fig = px.line(
            df_daily,
            x="Date",
            y=["Total", "Gross income"],
            title="Revenue & Gross Income by Date (U$)",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )

        # Define initial range (last 30 days)
        if not df_daily.empty:
            max_date = df_daily["Date"].max()
            min_date = df_daily["Date"].min()
            date_range = max_date - timedelta(days=30)
            if date_range < min_date:
                date_range = min_date
            initial_range = [date_range, max_date]
        else:
            initial_range = None

        # Configure x-axis slider and layout
        fig.update_xaxes(
            range=initial_range,
            rangeslider=dict(visible=True, thickness=0.05, bgcolor="#F0F2F6", bordercolor="#D1D5DB", borderwidth=1),
            type="date",
        )

        fig.update_yaxes(rangemode="tozero")

        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(orientation='h', y=1.02, x=1, xanchor='right'),
            xaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)),
            yaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)),
            title_font=dict(size=30),
            legend_font_size=14,
        )

        return fig
    except Exception as e:
        logging.error(f"Error generating plot: {e}")
        return None


def plot_revenue_by_product(df: pd.DataFrame):
    """Create a horizontal bar chart of revenue per product line.

    Parameters
    - df (pd.DataFrame): DataFrame containing 'Product line' and 'Total'.

    Returns
    - plotly.graph_objs._figure.Figure | None
    """
    try:
        # Copy, group and sort
        df_copy = df.copy()
        df_prod = df_copy.groupby("Product line")[['Total']].sum().reset_index()
        df_prod_sorted = df_prod.sort_values("Total", ascending=True)

        fig = px.bar(
            df_prod_sorted,
            x="Total",
            y="Product line",
            orientation="h",
            color="Product line",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text_auto=True,
            text="Total",
            title="Revenue by Product Line (U$)",
        )

        fig.update_traces(texttemplate="%{value:$,d}", textfont_size=14)
        fig.update_layout(
            xaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)),
            yaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)),
            title_font=dict(size=30),
            legend_font_size=14,
        )

        return fig
    except Exception as e:
        logging.error(f"Error generating plot: {e}")
        return None


def plot_revenue_by_branch(df: pd.DataFrame):
    """Create a bar chart of revenue by branch (city).

    Parameters
    - df (pd.DataFrame): DataFrame containing 'City' and 'Total'.

    Returns
    - plotly.graph_objs._figure.Figure | None
    """
    try:
        df_copy = df.copy()
        df_branch = df_copy.groupby("City")[['Total']].sum().reset_index()

        fig = px.bar(
            df_branch,
            x="City",
            y="Total",
            color="City",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Revenue by Branch (U$)",
            text="Total",
        )

        # Trim layout and hide legend
        fig.update_layout(margin=dict(l=0, r=0, t=50, b=0), showlegend=False)
        fig.update_traces(texttemplate="%{label}: %{value:$,d}", textfont_size=14)
        fig.update_layout(xaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)), yaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)), title_font=dict(size=30))

        return fig
    except Exception as e:
        logging.error(f"Error generating plot: {e}")
        return None


def plot_revenue_by_payment(df: pd.DataFrame):
    """Create a donut chart showing payment method distribution by revenue.

    Parameters
    - df (pd.DataFrame): DataFrame containing 'Payment' and 'Total'.

    Returns
    - plotly.graph_objs._figure.Figure | None
    """
    try:
        df_copy = df.copy()
        df_payment = df_copy.groupby("Payment")[['Total']].sum().reset_index()

        fig = go.Figure(data=[
            go.Pie(
                values=df_payment['Total'],
                labels=df_payment['Payment'],
                textinfo='label+percent',
                hole=0.6,
                marker=dict(colors=px.colors.qualitative.Pastel),
                pull=0.02,
            )
        ])

        fig.update_traces(textfont_size=14)
        fig.update_layout(title=dict(text="Revenue by Payment Method (%)", font=dict(size=28)), legend_font_size=14)

        return fig
    except Exception as e:
        logging.error(f"Error generating plot: {e}")
        return None


def plot_forecast_with_confidence(df: pd.DataFrame):
    """Create a sales forecast line chart with a 95% confidence band.

    The DataFrame is expected to have columns: 'Date', 'Total', 'Upper',
    'Lower', and 'Type' (Realized|Prediction).

    Returns
    - plotly.graph_objs._figure.Figure | None
    """
    try:
        fig = go.Figure()

        dates = df['Date'].tolist()
        upper = df['Upper'].tolist()
        lower = df['Lower'].tolist()

        # Confidence band (95%)
        fig.add_trace(go.Scatter(x=dates + dates[::-1], y=upper + lower[::-1], fill='toself', fillcolor='rgba(0, 100, 255, 0.2)', line=dict(color='rgba(255,255,255,0)'), hoverinfo='skip', name='Confidence Interval (95%)'))

        # Forecast line
        pred_data = df[df['Type'] == 'Prediction']
        fig.add_trace(go.Scatter(x=pred_data['Date'], y=pred_data['Total'], mode='lines', line=dict(color='red', width=2), name="Forecast"))

        # Actual history
        hist_data = df[df['Type'] == 'Realized']
        fig.add_trace(go.Scatter(x=hist_data['Date'], y=hist_data['Total'], mode='lines+markers', marker=dict(color=px.colors.qualitative.Pastel, size=5, opacity=0.5), name="Actual Sales"))

        fig.update_layout(title=dict(text="Sales Forecast (Next Year)", font=dict(size=24)), margin=dict(l=0, r=0, t=50, b=0), legend=dict(orientation='h', y=1.02, x=1, xanchor='right'), hovermode="x unified")

        return fig
    except Exception as e:
        logger.error(f"Error generating plot: {e}")
        return None


# Clusterização 3D de consumidores
def plot_clusters_3d(df_clustered: pd.DataFrame):
    """Create a 3D scatter plot to visualize customer segmentation.

    The DataFrame must contain 'Total', 'Rating', 'Quantity' and 'Cluster'.

    Returns
    - plotly.graph_objs._figure.Figure | None
    """
    try:
        fig = px.scatter_3d(df_clustered, x="Total", y="Rating", z="Quantity", color="Cluster", title="Customer Segmentation (3 Groups)", opacity=0.7, symbol="Cluster", color_discrete_sequence=px.colors.qualitative.Set1)

        # Camera orientation
        camera = dict(eye=dict(x=-2.0, y=2.0, z=1.0))

        fig.update_layout(scene_camera=camera, margin=dict(l=0, r=0, t=50, b=0), title_font=dict(size=24), legend=dict(orientation='h', y=0, x=0))
        return fig
    except Exception as e:
        logger.error(f"Error generating 3D plot: {e}")
        return None