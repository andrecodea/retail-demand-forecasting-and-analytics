import streamlit as st
import pandas as pd
import plotly.express as px
from src import models, plots, ui, reports
from data import data_pipeline as dp
from datetime import datetime
import base64
import logging
import time

"""UI tab definitions for the Streamlit app.

This module defines the main Streamlit tabs used in the sales dashboard
application: dashboard view, customer segmentation, revenue forecasting,
and integrated report generation. Each tab function receives a filtered
DataFrame from the sidebar and renders interactive components, charts,
and downloadable artifacts. Exceptions are logged and surfaced to the
user via Streamlit error messages.
"""

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carrega dados via pipeline
df = dp.load_data()


def sales_dashboard(df_filtered):
    """Render the main sales dashboard.

    This function assembles high-level KPIs and four summary charts
    (revenue by date, product, branch, and payment method) using the
    provided, already-filtered DataFrame. It also displays the
    underlying dataset table. All chart rendering is delegated to the
    `plots` module and KPI rendering to the `ui` module.

    Parameters
    - df_filtered (pd.DataFrame): DataFrame filtered by user selections
      in the sidebar. Must contain columns required by the plotting
      helpers (e.g., 'Total', 'Branch', 'Product', 'Payment').

    Raises
    - Any exceptions during plotting are caught and logged; the UI
      shows a generic error message to the user.
    """

    try:
        ui.display_kpi(df_filtered)
        st.space()
        col1, col2 = st.columns(2)
        st.space()
        col3, col4 = st.columns(2)
        st.space()
        col1.plotly_chart(plots.plot_revenue_by_date(df_filtered), width="stretch")
        col2.plotly_chart(plots.plot_revenue_by_product(df_filtered), width="stretch")
        col3.plotly_chart(plots.plot_revenue_by_branch(df_filtered), width="stretch")
        col4.plotly_chart(plots.plot_revenue_by_payment(df_filtered), width="stretch")

        ui.display_dataset(df_filtered)
    except Exception as e:
        logger.error(f"Error generating dashboard tab: {e}")
        st.error("Error generating dashboard tab.")


def customer_segmentation(df_filtered):
    """Render a customer segmentation analysis using clustering.

    The function applies an unsupervised clustering algorithm (fixed
    K=3) to the provided DataFrame via `models.apply_clustering`, then
    displays model metrics (e.g., Silhouette Score), a 3D scatterplot of
    the clusters, and a simple profile table summarizing cluster means
    for key features such as total spend and rating.

    Parameters
    - df_filtered (pd.DataFrame): Pre-filtered DataFrame containing the
      customer-level features required by the clustering routine.

    Returns
    - None: Outputs are rendered directly to the Streamlit app.
    """

    try:
        # Subtítulo e nota técnica
        st.subheader("Customer Segmentation")
        st.info("Analysis based on 3 strategic groups (Fixed K=3).")

        # Executa clustering e coleta métricas
        df_clustered, metrics = models.apply_clustering(df_filtered, n_clusters=3)

        # Mostra métricas resumidas
        if metrics:
            st.metric("Silhouette Score", f"{metrics['Silhouette Score']:.2f}")

        # Plota clusters em 3D
        fig_3d = plots.plot_clusters_3d(df_clustered)
        if fig_3d:
            st.plotly_chart(fig_3d, use_container_width=True)

        # Tabela de perfis por cluster
        st.markdown("#### Profiles")
        summary = df_clustered.groupby("Cluster")[['Total', 'Rating']].mean()
        st.dataframe(summary.style.format("{:.2f}"))
    except Exception as e:
        logger.error(f"Error generating customer segmentation tab: {e} ")
        st.error("Error generating customer segmentation tab.")


def revenue_forecast(df_filtered):
    """Render a time-series revenue forecast using Prophet.

    The routine calls `models.apply_prophet_forecast` to train and
    generate a forecast for the requested horizon (default 365 days).
    When successful, it shows model metrics (R^2, MAE), a trend KPI,
    and a forecast chart with confidence intervals.

    Parameters
    - df_filtered (pd.DataFrame): Pre-filtered historical revenue data
      containing a datetime column and a target value column used by
      the forecasting helper.

    Notes
    - If forecasting fails, the UI displays an error message.
    """

    # Subtítulo e nota
    st.subheader("Revenue Forecast (Prophet)")
    st.info("AI-powered forecast considering seasonality and holidays.")

    # Executa Prophet
    df_final, tendency, metrics = models.apply_prophet_forecast(df_filtered, horizon_days=365)

    # Renderiza métricas e gráfico
    if df_final is not None:
        if metrics:
            kpi1, kpi2, kpi3 = st.columns(3)
            kpi1.metric("Model Precision (R²)", f"{metrics['R2 Score']:.2%}")
            kpi2.metric("Avg Error (Weekly)", f"U$ {metrics['MAE (Weekly)']:.2f}")
            kpi3.metric("Trend (Weekly)", f"U$ {tendency:.2f}")

        fig = plots.plot_forecast_with_confidence(df_final)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not run Prophet forecast.")


def reports_tab(df_filtered):
    """Generate and present an integrated PDF report for Finance and
    Customer analyses.

    The function orchestrates three main phases: data processing
    (forecast + clustering), GenAI analysis for narrative sections,
    and PDF compilation including embedded plots. Generated artifacts
    and run metrics are cached in `st.session_state` to allow preview
    and download without re-running heavy computations.

    Parameters
    - df_filtered (pd.DataFrame): Filtered dataset used as input for
      forecasting and clustering pipelines.

    Session State Keys
    - report_pdf_data (bytes | None): Raw PDF bytes for download.
    - report_preview_html (str | None): Base64 iframe HTML for preview.
    - gen_metrics (dict | None): Timing and latency metrics from the
      GenAI analysis steps.

    Returns
    - None: All outputs are rendered into the Streamlit app and the
      PDF bytes are saved to session state for download.
    """

    # Cabeçalho
    st.header("📑 Integrated Intelligence Report")
    st.markdown("Generates a structured PDF with separate analyses for Finance and Customers.")

    # Inicializa cache no session_state
    if "report_pdf_data" not in st.session_state:
        st.session_state.report_pdf_data = None
    if "report_preview_html" not in st.session_state:
        st.session_state.report_preview_html = None
    if "gen_metrics" not in st.session_state:
        st.session_state.gen_metrics = None

    # Geração do relatório (botão)
    if st.button("Generate Full Report", type="primary"):
        report_start_time = time.time()

        # Processamento de dados: forecast + clustering
        with st.spinner("Processing Data (Forecast & Clustering)..."):
            try:
                df_forecast, tendency, _ = models.apply_prophet_forecast(df_filtered, horizon_days=365)
                df_clusters, _ = models.apply_clustering(df_filtered, n_clusters=3)

                fig_forecast = plots.plot_forecast_with_confidence(df_forecast)
                fig_clusters = plots.plot_clusters_3d(df_clusters)

                img_forecast = fig_forecast.to_image(format="png", width=1000, height=500, scale=2) if fig_forecast else None
                img_clusters = fig_clusters.to_image(format="png", width=1000, height=600, scale=2) if fig_clusters else None
            except Exception as e:
                st.error(f"Error preparing data: {e}")
                return

        # GenAI analyses (narratives + metrics)
        with st.spinner("🤖 AI Analyst 1/2: Analyzing Financials..."):
            text_forecast, metrics_fin = models.generate_forecast_analysis(df_filtered, df_forecast, tendency)

        with st.spinner("🤖 AI Analyst 2/2: Analyzing Customers..."):
            text_segmentation, metrics_seg = models.generate_segmentation_analysis(df_clusters)

        # Compilação do PDF
        with st.spinner("📄 Compiling PDF..."):
            try:
                kpis = {
                    "Total Revenue": f"U$ {df_filtered['Total'].sum():,.2f}",
                    "Yearly Forecast Trend": f"U$ {tendency:.2f}/day",
                    "Active Clusters": "3 Groups",
                }

                pdf_buffer = reports.create_pdf_report(
                    text_forecast,
                    text_segmentation,
                    kpis,
                    img_forecast,
                    img_clusters,
                )

                pdf_bytes = pdf_buffer.getvalue()
                base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
                preview_html = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="700" type="application/pdf"></iframe>'

                report_end_time = time.time()
                total_gen_time = report_end_time - report_start_time

                st.session_state.report_pdf_data = pdf_bytes
                st.session_state.report_preview_html = preview_html
                st.session_state.gen_metrics = {
                    "total_time": total_gen_time,
                    "fin_ttft": metrics_fin["TTFT"],
                    "fin_lat": metrics_fin["Latency"],
                    "seg_ttft": metrics_seg["TTFT"],
                    "seg_lat": metrics_seg["Latency"],
                }

                st.success("Report Generated Successfully!")
            except Exception as e:
                st.error(f"Error generating PDF: {e}")

    st.divider()

    # Mostra métricas de performance se presentes
    if st.session_state.gen_metrics:
        m = st.session_state.gen_metrics
        st.markdown("##### ⚡ LLM & System Performance (Last Run)")
        k1, k2, k3, k4, k5 = st.columns(5)

        k1.metric("Total Report Time", f"{m['total_time']:.2f}s")
        k2.metric("Fin. Analyst TTFT", f"{m['fin_ttft']*1000:.0f}ms")
        k3.metric("Fin. Analyst Latency", f"{m['fin_lat']:.2f}s")
        k4.metric("Seg. Analyst TTFT", f"{m['seg_ttft']*1000:.0f}ms")
        k5.metric("Seg. Analyst Latency", f"{m['seg_lat']:.2f}s")

        st.divider()

    # Preview e download do PDF gerado (cache)
    if st.session_state.report_pdf_data is not None:
        st.markdown("### 📄 Preview (Cached)")
        st.markdown(st.session_state.report_preview_html, unsafe_allow_html=True)
        st.space()
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Download Final PDF",
                data=st.session_state.report_pdf_data,
                file_name="retail_strategy_v2.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )

        # Limpa cache e força nova geração
        if st.button("Clear & Generate New Report"):
            st.session_state.report_pdf_data = None
            st.session_state.report_preview_html = None
            st.session_state.gen_metrics = None
            st.rerun()