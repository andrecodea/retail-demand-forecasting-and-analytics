import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")

# ====================================
# 1. FUNÇÕES DE CARREGAMENTO E TRATAMENTO
# ====================================

# 1.1. Carregamento de Dados
@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Lê o CSV, converte datas e cria colunas auxiliares.
    Retorna o DataFrame pronto pra tratamento.
    """

    df = pd.read_csv("data/supermarket_sales.csv", sep=";", decimal=",")

    # Converte pra datetime e ordena por data
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values(by="Date")

    # Engenharia de atributos: 01/10/2026 -> 2026-10
    # zfill(2) garante que o mes 1 vire '01'
    df["Month"] = df["Date"].apply(lambda x: f"{x.year}-{str(x.month).zfill(2)}")

    return df

# 1.2 Filtragem de Dados via Streamlit
def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera a sidebar com aplicação de filtro selecionado ao DataFrame
    """
    month = st.sidebar.selectbox("Month", df["Month"].unique())

    # DataFrame filtrado
    df_filtered = df[df["Month"] == month]

    return df_filtered

# ====================================
# 2. FUNÇÕES DE PLOTAGEM 
# ====================================

# 2.1 Faturamento Diário
def plot_daily_revenue(df: pd.DataFrame):
    """
    Plota o faturamento diário.
    Retorna um gráfico de barras.
    """
    fig = px.bar(
        df,
        x="Date",
        y="Total",
        color="City",
        title= "Daily Revenue ($)",
        )
    return fig

# 2.2 Faturamento por Categoria de Produtos
def plot_revenue_by_product(df: pd.DataFrame):
    """
    Plota o faturamento por categoria de produto.
    Retorna um gráfico de barras.
    """
    # Groupby pra somar vendas por categoria
    df_products = df.groupby("Product line")[["Total"]].sum().reset_index()
    fig = px.bar(df_products, x="Total", y="Product line", color="Product line",
                 title = "Revenue by Product Category", orientation="h")
    
    return fig

# 2.3 Faturamento por Filial
def plot_revenue_by_branch(df: pd.DataFrame):
    """
    Plota o faturamento por filial.
    Retorna um gráfico de barras.
    """
    city_total = df.groupby("City")[["Total"]].sum().reset_index()
    fig = px.bar(city_total, x="City", y="Total", title="Revenue by Branch ($)")

    return fig

# 2.4 Tipo de Pagamento
def plot_revenue_by_payment_method(df: pd.DataFrame):
    """
    Plota o faturamento por método de pagamento.
    Retorna um gráfico de pizza (Pie).
    """
    fig = px.pie(df, values="Total", names="Payment", title="Revenue by Payment Method ($)")
    return fig

# 2.5 Avaliação Média
def plot_mean_ratings_by_branch(df: pd.DataFrame):
    """
    Plota a média das avaliações de clientes por filial.
    Retorna um gráfico de barras.
    """

    city_rating = df.groupby("City")[["Rating"]].mean().reset_index()
    fig = px.bar(city_rating, x="City", y="Rating", title="Mean Ratings per Branch")

    # Trava o eixo Y até o 10º valor
    fig.update_yaxes(range=[0, 10])
    return fig

# ====================================
# 3. FUNÇÃO PRINCIPAL 
# ====================================

def main():
    
    # 3.1 Carregamento dos Dados
    df_raw = load_data()

    # 3.2 Filtragem dos Dados
    df_filtered = filter_data(df_raw)

    # 3.3 Definição das Colunas pro Dashboard
    col1, col2 = st.columns(2)
    col3, col4, col5 = st.columns(3)

    # 3.4 Organização da Renderização dos Plots via Streamlit
    col1.plotly_chart(plot_daily_revenue(df_filtered), use_container_width=True)
    col2.plotly_chart(plot_revenue_by_product(df_filtered), use_container_width=True)
    col3.plotly_chart(plot_revenue_by_branch(df_filtered), use_container_width=True)
    col4.plotly_chart(plot_revenue_by_payment_method(df_filtered), use_container_width=True)
    col5.plotly_chart(plot_mean_ratings_by_branch(df_filtered), use_container_width=True)

# ====================================
# EXECUÇÃO
# ====================================
if __name__ == "__main__":
    main()