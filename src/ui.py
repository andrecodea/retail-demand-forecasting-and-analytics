import streamlit as st
import pandas as pd
# Display de KPIs
def display_kpi(df:pd.DataFrame):
    st.header("Main Metrics")
    total_revenue = f"U$ {df["Total"].sum():,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    total_sales = df.shape[0]
    average_rating = f"{df["Rating"].mean():.2f}"

    col1, col2, col3 = st.columns(3)


    col1.metric(
     value=total_revenue,
     label="Total Revenue",
     delta_color="normal",
     border=True,
     )
    
    col2.metric(
     value=total_sales,
     label="Total Sales",
     delta_color="normal",
     border=True
    )
     
    
    col3.metric(
     value=average_rating,
     label="Average Rating",
     delta_color="normal",
     border=True
     )

def display_dataset(df:pd.DataFrame):
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
        st.dataframe(
                df.drop(columns=["Month_Label"], errors='ignore').style.format(dataframe_formatting),
                use_container_width=True)