import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
import ml_utils
import plots
import data.data_pipeline as data_pipeline
import tabs

st.set_page_config(
    layout="wide", 
    page_title="Intelligent Sales Dashboard",
    page_icon="📊"
    )

def main():
    st.title("Intelligent Sales Dashboard")

    with st.spinner("Loading database..."):
        # Carregamento dos Dados
        df = data_pipeline.load_data()

        # Filtragem dos Dados
        df_filtered = data_pipeline.sidebar_filters(df)

        if df_filtered.empty:
            st.warning("No data found with these filters. Try to select other filters.")
            return


    # ====================================
    # DASHBOARD
    # ====================================

    # 3.4 Abas do aplicativo
    tab1, tab2, tab3 = st.tabs(["📊 Sales Dashboard", "👥 Customer Segmentation", "📈 Revenue Forecast"])

    # Aba 1: Dataviz
    with tab1:
        tabs.sales_dashboard(df_filtered)

    # Aba 2: Machine Learning
    with tab2:
        tabs.customer_segmentation(df_filtered)
 
    with tab3:
        tabs.revenue_forecast(df_filtered)


if __name__ == "__main__":
    main()