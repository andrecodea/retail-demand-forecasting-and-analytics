import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import timedelta
from src import tabs
from data import data_pipeline
import logging

logging.basicConfig(level=logging.INFO)
logger=logging.getLogger(__name__)

# Streamlit app entrypoint for the sales dashboard.

# This module exposes a `main()` function that boots the Streamlit UI:
# - loads and prepares data via `data_pipeline.load_data()`,
# - applies sidebar filters via `data_pipeline.sidebar_filters()`,
# - renders the four main tabs implemented in `src.tabs`.

# Behavior
# - Handles and logs unexpected errors to avoid crashing the UI.
# - Caches heavy artifacts in called modules when applicable.

# Usage
# - Run `streamlit run app.py` to start the dashboard.


# Configura o layout da página como wide, dá um título e um favicon.
st.set_page_config(
    layout="wide", 
    page_title="Intelligent Sales Dashboard",
    page_icon="📊"
    )

def main():
    """Run the Streamlit application.

    The function loads data, applies sidebar filters and renders the
    dashboard tabs. Any exceptions are logged and presented to the
    user as a Streamlit error message to preserve the app session.

    Returns
    - None
    """
    try:
        st.title("Retail Demand Forecasting & Analysis Dashboard")

        with st.spinner("Loading database..."):
            # Carrega dados
            df = data_pipeline.load_data()

            # Aplica filtros da sidebar
            df_filtered = data_pipeline.sidebar_filters(df)

            if df_filtered.empty:
                st.warning("No data found with these filters. Try to select other filters.")
                return

        # Abre abas principais
        tab1, tab2, tab3, tab4 = st.tabs(["Dashboard", "Segmentation", "Forecast", "Reports"])

        with tab1:
            tabs.sales_dashboard(df_filtered)
        with tab2:
            tabs.customer_segmentation(df_filtered)
        with tab3:
            tabs.revenue_forecast(df_filtered)
        with tab4:
            tabs.reports_tab(df_filtered)
    except Exception as e:
        logger.error(f"Error running app: {e}")
        st.error("Error running app")

if __name__ == "__main__":
    main()