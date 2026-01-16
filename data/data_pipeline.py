import pandas as pd
import streamlit as st
import logging 
from datetime import timedelta, date


# Configura o logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega os dados a partir do CSV
@st.cache_data # -> salva os dados em cache
def load_data() -> pd.DataFrame:
    """
    Carrega o dataset em formato CSV e o transforma em um DataFrame.

    Returns
        DataFrame de dados de vendas de supermercado.
    """
    # Tenta carregar o CSV e transformá-lo em um DataFrame
    try:
        df = pd.read_csv("data/supermarket_sales_extended.csv", sep=';', decimal=',')

        # Transforma datas em texto para formato datetime
        df["Date"] = pd.to_datetime(df["Date"])

        # Ordena o df pelas datas
        df = df.sort_values("Date")

        logger.info(f"DataFrame created successfully.")

        return df
    
    except Exception as e:
        logger.error(f"Error while loading CSV: {e}")
        st.error(f"Error while loading CSV: {e}")
        st.stop()

# Gera a sidebar com os filtros disponíveis
def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Docstring for sidebar_filters
    
    :param df: Description
    :type df: pd.DataFrame
    :return: Description
    :rtype: DataFrame
    """
    
    try:

        # Copia o df original
        df_view = df.copy()
        
        # Cria colunas temporais novas
        df_view["Month_Label"] = df_view["Date"].dt.strftime("%b") # -> 01 - Jan

        # Define o header da sidebar
        st.sidebar.header("Global Filters")

        # Cria as listas de filtros disponíveis
        months = sorted(df_view["Month_Label"].unique(), reverse=True)
        cities = sorted(df_view["City"].unique())


        # Gera os seletores de filtros disponíveis
        selected_months = st.sidebar.multiselect(
            "Month analysis range",
            months,
            default=months
        )

        selected_city = st.sidebar.multiselect(
            "Select the branch for analysis",
            cities,
            default=cities,
            )

        # O filtro é aplicado caso as listas de filtros disponíveis existam/tenham conteúdo
        if selected_months:
            df_view = df_view[df_view["Month_Label"].isin(selected_months)]

        if selected_city:
            df_view = df_view[df_view["City"].isin(selected_city)]

        # Retorna o df filtrado com as colunas de "Year" e "Month_Label" removidas
        return df_view

    # Logging e exibição de mensagem de erro em caso de exceção
    except Exception as e:
        logger.error(f"Error while generating sidebar: {e}")
        st.error(f"Error while generating sidebar: {e}")
        st.stop()