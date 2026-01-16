# Importa utils
import pandas as pd
import logging
from datetime import timedelta, date
import plotly.express as px
import plotly.graph_objects as go

# Configura o logger pra observabilidade
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Faturamento por data
def plot_revenue_by_date(df:pd.DataFrame):
    """
    Docstring for plot_revenue_by_date
    
    :param df: DataFrame de vendas de supermercado.
    :type df: pd.DataFrame
    :return: Gráfico de linha do faturamento e lucro ao longo dos anos | Nulo
    :rtype: Figure | None
    """
    try:
        df_copy= df.copy()
        df_daily = df_copy.groupby("Date")[["Total", "Gross income"]].sum().reset_index()
        
        fig = px.line(
            df_daily,
            x="Date",
            y=["Total", "Gross income"],
            title="Revenue by Date (U$)",
            markers=True,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # Cria um range de datas pra poder aplicar a filtragem
        if not df_daily.empty:
            max_date = df_daily["Date"].max()
            min_date = df_daily["Date"].min()
            
            date_range = max_date- timedelta(days=30)
            
            if date_range < min_date:
                date_range = min_date
                
            initial_range = [date_range, max_date]
        else:
            initial_range = None

        # Configura o slider de data e uma lista de ranges pra filtrar nativamente
        fig.update_xaxes(
            range=initial_range,
            rangeslider=dict(
                visible=True,
                thickness=0.05,      # Altura: 0.05 = 5% do gráfico (Bem mais fino)
                bgcolor="#F0F2F6",   # Cor de fundo (Cinza claro padrão do Streamlit)
                bordercolor="#D1D5DB", # Cor da borda (Cinza médio)
                borderwidth=1,       # Espessura da borda
            ),
            type="date"
                )
        
        # Faz com que a viz do slider não suma
        fig.update_yaxes(rangemode="tozero")
        
        # Modifica o layout pra ter margem e rótulos
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            legend=dict(orientation='h', y=1.02, x=1, xanchor='right')
        )

        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

# Faturamento por produto
def plot_revenue_by_product(df:pd.DataFrame):
    """
    Docstring for plot_revenue_by_product
    
    :param df: Description
    :type df: pd.DataFrame
    :return: Gráfico de linha do faturamento por produto| Nulo
    :rtype: Figure | None
    """
    try:
        df_copy = df.copy()
        df_prod = df_copy.groupby("Product line")[["Total"]].sum().reset_index()
        df_prod_sorted = df_prod.sort_values("Total", ascending=True)
        fig = px.bar(
            df_prod_sorted,
            x="Total",
            y="Product line",
            orientation="h",
            color = "Product line",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            text_auto=True,
            text="Total"
        )

        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

def plot_revenue_by_branch(df: pd.DataFrame):
    try:
        df_copy = df.copy()

        df_branch = df_copy.groupby("City")[["Total"]].sum().reset_index()

        fig = px.bar(
            df_branch,
            x="City",
            y="Total",
            color="City",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Revenue by Branch",
            text="City"
        )

        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False 
        )

        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

def plot_revenue_by_payment(df: pd.DataFrame):
    try:
        df_copy = df.copy()

        df_payment = df_copy.groupby("Payment")[["Total"]].sum().reset_index()

        fig = px.pie(
            df_payment,
            values="Total",
            names="Payment",
            hole=0.6,
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Revenue by Payment Method",
        )

        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None
    
def plot_forecast_with_confidence(df_future):
    pass