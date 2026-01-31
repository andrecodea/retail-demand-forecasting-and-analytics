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
    Generates a line plot of revenue over time.
    
    :param df: Supermarket sales dataframe.
    :type df: pd.DataFrame
    :return: Line plot of revenue over time.
    :rtype: Figure | None
    """
    try:
        df_copy= df.copy()
        df_daily = df_copy.groupby("Date")[["Total", "Gross income"]].sum().reset_index()
        
        fig = px.line(
            df_daily,
            x="Date",
            y=["Total", "Gross income"],
            title="Revenue & Gross Income by Date (U$)",
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
                thickness=0.05,
                bgcolor="#F0F2F6",   
                bordercolor="#D1D5DB",
                borderwidth=1,       
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

        # Ajusta o layout do plot
        fig.update_layout(
            xaxis=dict(tickfont=dict(size=14), title_font=dict(size=14)), # Ajusta os tickers e os títulos do eixo x
            yaxis=dict(tickfont=dict(size=14),title_font=dict(size=14)), # Ajusta os tickers e os títulos do eixo y
            title_font=dict(size=30), # Ajusta o tamanho do título do gráfico
            legend_font_size=14 # Ajusta o tamanho dos rótulos
            )   

        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

# Faturamento por produto
def plot_revenue_by_product(df:pd.DataFrame):
    """
    Generates a horizontal bar plot of revenue by product.
    
    :param df: DataFrame containing product categories and their revenues.
    :type df: pd.DataFrame
    :return: Bar plot of revenue by product | None
    :rtype: Figure | None
    """

    # Geração do bar plot
    try:
        # Copia, agrupa e ordena o df
        df_copy = df.copy()
        df_prod = df_copy.groupby("Product line")[["Total"]].sum().reset_index()
        df_prod_sorted = df_prod.sort_values("Total", ascending=True)

        # Gera a figura
        fig = px.bar(
            df_prod_sorted,
            x="Total",
            y="Product line",
            orientation="h",
            color = "Product line",
            color_discrete_sequence=px.colors.qualitative.Pastel, # Palette
            text_auto=True,
            text="Total",
            title="Revenue by Product Line (U$)"
        )

        # Aumenta o tamanho da fonte dos rótulos e altera o formato 
        fig.update_traces(texttemplate="%{value:$,d}", textfont_size=14)
        fig.update_layout(
            xaxis=dict(
                tickfont=dict(size=14),
                title_font=dict(size=14)
                ),
            yaxis=dict(
                tickfont=dict(size=14),
                title_font=dict(size=14)),
            title_font=dict(size=30),
            legend_font_size=14)   


        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

# Faturamento por filial
def plot_revenue_by_branch(df: pd.DataFrame):
    """
    Generates a bar plot of revenue by branch.
    
    :param df: DataFrame containing the branches and their respective revenues.
    :type df: pd.DataFrame
    :return: Bar plot of revenue by by branch | None
    :rtype: Figure | None
    """

    # Geração do bar plot
    try:

        # Copia e agrupa o df
        df_copy = df.copy()
        df_branch = df_copy.groupby("City")[["Total"]].sum().reset_index()

        # Gera a figura
        fig = px.bar(
            df_branch,
            x="City",
            y="Total",
            color="City",
            color_discrete_sequence=px.colors.qualitative.Pastel,
            title="Revenue by Branch (U$)",
            text="Total"
        )

        # Faz trimming e remove a legenda
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            showlegend=False 
        )

        # Aumenta o tamanho da fonte dos rótulos e altera o formato 
        fig.update_traces(texttemplate="%{label}: %{value:$,d}", textfont_size=14)
        
        # Aumenta o tamanho do título
        fig.update_layout(
            xaxis=dict(
                tickfont=dict(size=14),
                title_font=dict(size=14)
                ),
            yaxis=dict(
                tickfont=dict(size=14),
                title_font=dict(size=14)),
            title_font=dict(size=30))   

        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

# Faturamento por método de pagamento
def plot_revenue_by_payment(df: pd.DataFrame):
    """
    Generates a pie plot of the payment method distribuition.
    
    :param df: DataFrame containing the revenue per payment method.
    :type df: pd.DataFrame
    :return: Pie plot of revenue by payment method | None
    :rtype: Figure | None
    """
    try:
        df_copy = df.copy()

        df_payment = df_copy.groupby("Payment")[["Total"]].sum().reset_index()

        fig = go.Figure(data=[go.Pie(
            values=df_payment["Total"],
            labels=df_payment["Payment"],
            textinfo="label+percent",
            hole=0.6,
            marker=dict(colors=px.colors.qualitative.Pastel),
            pull=0.02
        )])

        # Aumenta o tamanho dos rótulos
        fig.update_traces(textfont_size=14)
        
        # Aumenta o tamanho do título
        fig.update_layout(title=dict(
            text= "Revenue by Payment Method (%)",
            font=dict(size=28),
            ),
            legend_font_size=14)
        
        return fig
    except Exception as e:
        logging.error(f"Error to generate plot: {e}")
        return None

# Forecast de faturamento com intervalo de confiança
def plot_forecast_with_confidence(df:pd.DataFrame):
    """
    Gera um line plot para forecasting de faturamento com intervalo de confiança de 95%.
    
    :param df: DataFrame com os dados de forecasting (LinearRegression)
    :type df: pd.DataFrame
    :return: Line plot of revenue forecast | None
    :rtype: Figure | None
    """
    try:
        fig = go.Figure()

        # Intervalo de confiança de 95%
        fig.add_trace(go.Scatter(
            x=list((df['Date']) + list(df["Date"])[::-1]),
            y=list(df['Upper']) + list(df['Lower'])[::-1],
            fill='toself', fillcolor='rgba(0, 100, 255, 0.2)',
            line=dict(color='rgba(255,255,255,0)', hoverinfo='skip', name='Confidence Interval (95%)')
        ))

        # Linha do forecasting
        fig.add_trace(go.Scatter(
            x=df[df['Type'] == 'Prediction']['Date'],
            y=df[df['Type'] == 'Prediction']['Total'],
            mode='lines', line=dict(color='red', width=2, dash='dash'), name="Forecast"
        ))

        # Histórico
        df_history = df[df["Type"] == 'Realized']
        fig.add_trace(go.Scatter(
            x=df_history['Date'], y=df_history['Total'],
            mode='markers', marker=dict(color='black', size=5, opacity=0.5), name="Actual Sales"
        ))

        # Atualiza título e rótulos
        fig.update_layout(
            title=dict(
                text="Sales Forecast (Next Days)",
                margin=dict(l=0, r=0, t=50, b=0,
                font=dict(size=28)),
            legend=dict(orientation='h', y=1.02, x=1, xanchor='right')
            
        ))

        return fig
    except Exception as e:
        logger.error(f"Error generating plot: {e}")
        return None