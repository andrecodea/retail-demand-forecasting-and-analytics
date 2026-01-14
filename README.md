# Sales Dashboard
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Plotly](https://img.shields.io/badge/Plotly%20-%20white?style=for-the-badge&logo=Plotly&labelColor=black&color=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit%20-%20white%20?style=for-the-badge&logo=Streamlit&color=white)

This is an interactive Streamlit application to visualize and explore supermarket sales using the `supermarket_sales.csv` dataset.

For the Portuguese version of this README see [README.pt.md](README.pt.md).

Key visualizations:
- Monthly revenue by branch
- Revenue by product line
- Performance by payment method
- Total revenue and aggregated metrics
- Average branch ratings

![Demo](assets/sales-dash-demo.gif)

**Dataset**
The project uses the `supermarket_sales.csv` file, which contains sales records including date, branch, product line, unit price, quantity, total, payment method and rating. These fields are grouped and aggregated to produce the visualizations.

**How to run (local)**
1. Create and activate a virtual environment (optional):

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\\Scripts\\Activate.ps1
# Windows cmd
\.venv\\Scripts\\activate.bat
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the Streamlit app:

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually `http://localhost:8501`) to interact with the dashboard.

**Repository structure**
- `app.py` : main Streamlit script with dashboard logic
- `supermarket_sales.csv` : dataset used by the app
- `requirements.txt` : project dependencies
- `assets/` : images and GIFs used in the README and app
- `README.md` : this English README
- `README.pt.md` : Portuguese README (copy)

**Development summary**
1. Read the CSV with `pandas.read_csv()` and convert date columns to `datetime`.
2. Clean and format data as needed (sorting, type conversions).
3. Add interactive filters in Streamlit (sidebar) to select branch, product, period and more.
4. Group data with `groupby()` and aggregate using `sum()` / `mean()` to compute metrics by category.
5. Plot charts using Plotly Express (`px.bar`, `px.pie`, `px.line`) embedded in Streamlit.

If you want, I can also:
- Add Docker instructions;
- Add a `requirements-dev.txt` with lint/test tools;
- Create a small sample dataset for quick tests.

---
Updated to include an English translation and a link to the Portuguese README.
---
Atualizado para fornecer instruções de execução e contexto do dataset.

