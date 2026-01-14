# Sales Dashboard
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Plotly](https://img.shields.io/badge/Plotly%20-%20white?style=for-the-badge&logo=Plotly&labelColor=black&color=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit%20-%20white%20?style=for-the-badge&logo=Streamlit&color=white)

Uma aplicação interativa construída com Streamlit para visualizar e explorar vendas de supermercado a partir do dataset `supermarket_sales.csv`.

Principais visualizações:
- Receita mensal por filial (branch)
- Receita por linha de produto (product line)
- Desempenho por forma de pagamento
- Receita total e métricas agregadas
- Avaliação média das filiais (rating)

![Demo](assets/sales-dash-demo.gif)

**Dataset**
O projeto utiliza o arquivo `supermarket_sales.csv`, que contém registros de vendas incluindo data, filial, linha de produto, preço unitário, quantidade, total, método de pagamento e avaliação (rating). Esses campos são agrupados e agregados para gerar as visualizações.

**Como executar (local)**
1. Crie e ative um ambiente virtual (opcional):

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# Windows cmd
.\.venv\Scripts\activate.bat
```

2. Instale dependências:

```bash
pip install -r requirements.txt
```

3. Rode a aplicação Streamlit:

```bash
streamlit run app.py
```

Abra o endereço mostrado no terminal (normalmente `http://localhost:8501`) para interagir com o dashboard.

**Estrutura do repositório**
- `app.py` : script principal do Streamlit com a lógica do dashboard.
- `supermarket_sales.csv` : arquivo de dados usado pelo app.
- `requirements.txt` : dependências do projeto.
- `assets/` : imagens e GIFs usados no README e na interface.
- `README.md` : documentação em inglês.
- `README.pt.md` : documentação em português (este arquivo).

**Resumo do processo de desenvolvimento**
1. Ler o CSV com `pandas.read_csv()` e converter colunas de data para `datetime`.
2. Limpar e formatar os dados quando necessário (ordenar, converter tipos).
3. Criar filtros interativos em Streamlit (sidebar) para selecionar filial, produto, período e outros.
4. Agrupar dados com `groupby()` e agregar com `sum()` / `mean()` para obter métricas por categoria.
5. Plotar gráficos com Plotly Express (`px.bar`, `px.pie`, `px.line`) integrados ao Streamlit.

Se quiser, posso também:
- Adicionar instruções para dockerização;
- Incluir um arquivo `requirements-dev.txt` com ferramentas de lint/testes;
- Criar um exemplo de dataset reduzido para testes rápidos.

---
Atualizado para fornecer instruções de execução e contexto do dataset.
