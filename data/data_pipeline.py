import pandas as pd
import streamlit as st
import logging
from datetime import timedelta, date

"""Data loading and sidebar filter utilities for the dashboard.

This module exposes two helpers:
- `load_data()`: loads and returns the cached transactions DataFrame.
- `sidebar_filters(df)`: renders sidebar controls and returns the
  filtered DataFrame based on user selections.
"""

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@st.cache_data
def load_data() -> pd.DataFrame:
    """Load the extended supermarket sales CSV and return a DataFrame.

    The function reads `data/supermarket_sales_extended.csv`, parses the
    'Date' column into datetimes, sorts by date and caches the result
    via Streamlit's `st.cache_data` decorator to avoid repeated IO.

    Returns
    - pd.DataFrame: parsed and sorted sales DataFrame.

    Raises
    - Streamlit will stop the app on failure and log the underlying error.
    """
    try:
        df = pd.read_csv("data/supermarket_sales_extended.csv", sep=';', decimal=',')
        df["Date"] = pd.to_datetime(df["Date"])  # parse dates
        df = df.sort_values("Date")

        logger.info("DataFrame created successfully.")
        return df
    except Exception as e:
        logger.error(f"Error while loading CSV: {e}")
        st.error(f"Error while loading CSV: {e}")
        st.stop()


def sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Render sidebar filters and return the filtered DataFrame.

    The function adds a temporary 'Month_Label' column used for month
    selection, renders Streamlit multiselect controls for months and
    cities, and returns the DataFrame filtered accordingly.

    Parameters
    - df (pd.DataFrame): source sales DataFrame.

    Returns
    - pd.DataFrame: filtered DataFrame according to user selections.
    """
    try:
        df_view = df.copy()

        # Temporary month label for selection
        df_view["Month_Label"] = df_view["Date"].dt.strftime("%b")

        st.sidebar.header("Global Filters")

        months = sorted(df_view["Month_Label"].unique(), reverse=True)
        cities = sorted(df_view["City"].unique())

        selected_months = st.sidebar.multiselect("Month analysis range", months, placeholder="Select one or more months")

        selected_city = st.sidebar.multiselect("Select the branch for analysis", cities, default=cities, placeholder="Select one or more branches")

        if selected_months:
            df_view = df_view[df_view["Month_Label"].isin(selected_months)]

        if selected_city:
            df_view = df_view[df_view["City"].isin(selected_city)]

        return df_view
    except Exception as e:
        logger.error(f"Error while generating sidebar: {e}")
        st.error(f"Error while generating sidebar: {e}")
        st.stop()