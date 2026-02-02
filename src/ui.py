import streamlit as st
import pandas as pd

"""UI helpers for Streamlit: KPI and dataset renderers.

Functions:
- display_kpi(df): render top-level KPI cards.
- display_dataset(df): render styled DataFrame for exploration.
"""

# Exibe KPIs
def display_kpi(df: pd.DataFrame):
    """Render main KPI cards for the dashboard.

    Parameters
    - df (pd.DataFrame): sales DataFrame with at least columns
      'Total', 'Gross income' and 'Rating'.
    """

    st.header("Main Metrics")

    # Valores formatados
    total_revenue = f'U$ {df["Total"].sum():,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    total_gross_income = f'U$ {df["Gross income"].sum():,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
    total_sales = df.shape[0]
    average_rating = f'{df["Rating"].mean():.2f}'

    # KPI columns
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(label="Total Revenue", value=total_revenue, delta_color="normal", border=True)
    col2.metric(label="Total Gross income", value=total_gross_income, delta_color="normal", border=True)
    col3.metric(label="Total Sales", value=total_sales, delta_color="normal", border=True)
    col4.metric(label="Average Rating", value=average_rating, delta_color="normal", border=True)


def display_dataset(df: pd.DataFrame):
    """Render the full dataset table with formatted columns.

    Parameters
    - df (pd.DataFrame): DataFrame to display. 'Month_Label' column
      (if present) will be dropped for presentation.
    """

    # Cabeçalho da tabela
    st.header("Full Dataset")

    dataframe_formatting = {
        "Total": "U$ {:.2f}",
        "Unit price": "U$ {:.2f}",
        "Gross margin percentage": lambda x: "{:.1%}".format(x).replace('.', ','),
        "Gross income": "U$ {:.2f}",
        "Date": "{:%d/%m/%Y}",
        "Rating": "{:.1f}",
        "Quantity": "{:.0f}",
    }

    st.dataframe(df.drop(columns=["Month_Label"], errors='ignore').style.format(dataframe_formatting), use_container_width=True)