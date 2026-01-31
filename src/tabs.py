import streamlit as st
import pandas as pd
import plotly.express as px
from src import models, plots, ui
from data import data_pipeline as dp
from datetime import datetime

df = dp.load_data()

def sales_dashboard(df_filtered):
    ui.display_kpi(df_filtered)
    st.space()
    col1, col2 = st.columns(2)
    st.space()
    col3, col4 = st.columns(2)
    st.space()
    col1.plotly_chart(plots.plot_revenue_by_date(df_filtered), width='stretch')
    col2.plotly_chart(plots.plot_revenue_by_product(df_filtered), width='stretch')
    col3.plotly_chart(plots.plot_revenue_by_branch(df_filtered), width='stretch')
    col4.plotly_chart(plots.plot_revenue_by_payment(df_filtered), width='stretch')
    
    ui.display_dataset(df_filtered)

def customer_segmentation(df_filtered):
    st.subheader("Customer Segmentation (K-Means)")        
    col_ai_1, col_ai_2 = st.columns(2)
    with col_ai_1:
        st.info("The model (K-Means) groups transactions based on: Spendage (Total), ratings, and amount of products purchased (Quantity).")
        cluster_amt = st.slider("Number of Groups (K)", 2, 5, 3)
        process_btn = st.button("Run K-Means")
    with col_ai_2:
        if process_btn:
            with st.spinner("The model is identifying patterns..."):
                df_clustered = models.apply_clustering(df_filtered, n_clusters=cluster_amt)
                st.toast("Model processed successfully!", icon="✅")
                fig_3d = px.scatter_3d(
                df_clustered,
                x="Total",
                y="Rating",
                z="Quantity",
                color="Cluster",
                title="Clusterization by Purchase Behavior",
                opacity=0.7,
                symbol="Cluster"
                )
                st.plotly_chart(fig_3d, use_container_width=True)
    if process_btn:
        st.markdown("### Who are these groups?")
        cluster_summary = df_clustered.groupby('Cluster')[['Total', 'Rating', 'Quantity']].mean().reset_index()
        st.dataframe(cluster_summary.style.format({
            "Total": "U$ {:.2f}",
            "Rating": "{:.1f}",
            "Quantity": "{:.0f}"
        }),
        use_container_width=True)
        st.markdown("""
        **How to interpret**
        - **Cluster X:** Spends a lot, but low ratings? -> *Churn risk*
        - **Cluster Y:** Spends a little, but high ratings? -> *Ticket increase opportunity*
        """)

def revenue_forecast(df_filtered):
    st.subheader("Revenue Forecast (Linear Regression)")

    col_input, col_graph = st.columns([1, 3])

    with col_input:
        st.markdown("### Configuration")
        days = st.slider("Prediction Horizon (Days)", 7, 365, 30)
        st.info("The model uses linear regression over the filtered history to predict future tendency.")

    with col_graph:
        df_final, tendency = models.apply_linear_regression(df, horizon_days=days)

        delta_color = "normal" if tendency > 0 else "inverse"
        st.metric(
              label="Daily Estimated Tendency",
              value=f"U$ {tendency:.2f} / day",
              delta="Increase" if tendency > 0 else "Decrease",
              delta_color=delta_color
         )

        #st.plotly_chart(plots.plot_forecast_with_confidence(df_final), width="stretch")