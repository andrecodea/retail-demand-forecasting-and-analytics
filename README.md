# Sales Dashboard
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Plotly](https://img.shields.io/badge/Plotly%20-%20white?style=for-the-badge&logo=Plotly&labelColor=black&color=white)
![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Streamlit](https://img.shields.io/badge/Streamlit%20-%20white%20?style=for-the-badge&logo=Streamlit&color=white)

<img src="/assets/sales_analytics.gif" width="750" height="750"/>

This repository contains a Streamlit-based sales dashboard for retail
analytics. It demonstrates an end-to-end flow from data ingestion,
feature computation and visualization to clustering, forecasting and
automated PDF report generation.

This README is a technical manual describing architecture, modules,
metrics produced, runtime instructions and troubleshooting notes.

Contents
- Overview
- Architecture & Modules
- Data: format and generation
- Metrics and outputs
- How to run (development)
- Environment & security notes
- Troubleshooting and validation

Overview
--------
The application loads a transactional supermarket sales dataset,
applies interactive sidebar filters and exposes four main tabs:

- Dashboard: KPI cards and summary visualizations (time series,
	product/branch breakdowns, payment distribution).
- Segmentation: unsupervised customer segmentation using K-Means and a
	3D interactive scatter visualization.
- Forecast: weekly-aggregated Prophet forecast with confidence
	intervals and model performance metrics.
- Reports: generates an integrated PDF (ReportLab) combining plots and
	AI-written narratives (via streaming LLM API) and exposes a cached
	preview + download.

Architecture & Modules
----------------------
High-level layout (workspace root):

- `app.py` — Streamlit entrypoint. Loads data, builds sidebar filters
	and controls tab flow.
- `data/`
	- `data_pipeline.py` — data loader (`load_data`) and sidebar filter
		renderer (`sidebar_filters`). The loader is cached with
		`st.cache_data` to avoid repeated IO.
	- `data_generator.py` — synthetic dataset generator used to create
		`data/supermarket_sales_extended.csv` from the small sample CSV.
- `src/`
	- `models.py` — model and analysis routines
		- `apply_clustering(df, n_clusters)` → returns clustered DataFrame
			and metrics (Inertia, Silhouette Score).
		- `apply_prophet_forecast(df, horizon_days)` → returns forecast
			DataFrame, weekly tendency, and metrics (R2, MAE (weekly), RMSE).
		- `generate_forecast_analysis(...)`, `generate_segmentation_analysis(...)`
			— stream responses from OpenAI-compatible client and return
			text plus latency metrics (TTFT and total latency).
	- `plots.py` — Plotly helpers that create figures used in the UI.
	- `ui.py` — small wrappers for KPI cards and DataFrame display.
	- `reports.py` — report composition using ReportLab and embedded
		images; returns a `BytesIO` buffer for download.
	- `tabs.py` — Streamlit tab implementations which coordinate UI,
		plotting and model calls.

	Architecture Diagram
	--------------------
	The diagram below shows the high-level components and data flow.

	```mermaid
	flowchart TB
	    subgraph Data
	        GEN["data/data_generator.py"]
	        CSV["data/supermarket_sales_extended.csv"]
	    end
	
	    subgraph App["Streamlit App"]
	        DP["data/data_pipeline.py"]
	        APP["app.py"]
	        TABS["src/tabs.py"]
	        UI["src/ui.py"]
	        PLOTS["src/plots.py"]
	        MODELS["src/models.py"]
	        REPORTS["src/reports.py"]
	    end
	
	    subgraph Cloud["External API"]
	        LLM["OpenAI / OpenRouter"]
	    end
	
	    %% Fluxo de Dados
	    GEN --> CSV
	    CSV --> DP
	    DP --> APP
	    
	    %% Fluxo da Aplicação
	    APP --> TABS
	    TABS --> UI
	    TABS --> PLOTS
	    TABS --> MODELS
	    
	    %% Lógica de Negócio
	    MODELS -- "Forecast Data" --> PLOTS
	    MODELS -- "Cluster Data" --> PLOTS
	    MODELS -- "Streaming" --> LLM
	    
	    %% Geração de Relatório
	    PLOTS --> REPORTS
	    MODELS --> REPORTS
	    REPORTS -- "PDF Bytes" --> APP
	    APP -.->|"session_state (Cache)"| REPORTS
	
	    %% Estilos
	    style APP fill:#f9f,stroke:#333,stroke-width:2px
	    style DP fill:#bbf,stroke:#333,stroke-width:1px
	    style MODELS fill:#bfb,stroke:#333,stroke-width:1px
	    style REPORTS fill:#ffd,stroke:#333,stroke-width:1px
	    style LLM fill:#fff,stroke:#f00,stroke-width:2px,stroke-dasharray: 5 5
 	```

Data: format and generation
---------------------------
Primary dataset: `data/supermarket_sales_extended.csv` (semicolon-`
;` separated, comma decimal). Expected columns used across modules:

- `Date` (datetime), `Total` (numeric), `Gross income`, `Product line`,
	`City`, `Payment`, `Rating`, `Quantity`, `Unit price`.

Generation
- Use `python data/data_generator.py` to regenerate a synthetic dataset
	(overwrites the extended CSV). The generator samples categories with
	configurable weights and writes `data/supermarket_sales_extended.csv`.

Loading
- `data_pipeline.load_data()` reads the extended CSV, parses `Date`,
	sorts by date and caches the result in Streamlit to avoid repeated
	disk IO during interactive sessions.

Metrics and outputs
-------------------
The project exposes the following numeric outputs and metrics:

Clustering (K-Means)
- Inertia: internal cluster compactness reported by scikit-learn.
- Silhouette Score: average silhouette across samples (higher is
	better). Computed on standardized features `['Total','Rating','Quantity']`.

Forecasting (Prophet)
- R2 Score: coefficient of determination computed on historical
	overlap between predictions and actuals (weekly-aggregated).
- MAE (Weekly): Mean Absolute Error computed on weekly totals (note
	that the model and metrics are computed at weekly frequency).
- RMSE: root mean squared error.
- Tendency: average weekly growth computed as (last_pred - last_real)/52.

GenAI / LLM metrics
- TTFT (Time To First Token): measured during streaming API calls to
	indicate responsiveness of the AI assistant.
- Latency: total time to receive the entire streamed response.

Reports
- The Reports tab compiles forecast and segmentation plots (PNG from
	Plotly) and AI narratives into a two-page PDF (ReportLab). The PDF
	bytes are cached in `st.session_state` for fast preview and download.

How to run (development)
------------------------
1. Create and activate a virtual environment (Windows PowerShell example):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. (Optional) Generate synthetic dataset if `data/supermarket_sales_extended.csv` is missing:

```powershell
python data/data_generator.py
```

3. Start the Streamlit app:

```powershell
streamlit run app.py
```

Environment variables and LLM integration
----------------------------------------
- The project may use an OpenAI-compatible client for streaming LLM
	calls (`OpenAI` client configured with `base_url` pointing to
	OpenRouter or other endpoints). Provide API keys via a `.env` file
	or environment variables as required by your client. Typical variable
	names: `OPENAI_API_KEY` or provider-specific keys.

Security note: do not commit API keys to version control.

Caching and performance
-----------------------
- `st.cache_data` is used in `data_pipeline.load_data()` to cache the
	loaded DataFrame and avoid repeated CSV parsing during interactive
	use.
- Heavy operations (forecasting, clustering) are invoked on demand and
	some outputs (PDF bytes, genai metrics) are stored in
	`st.session_state` to speed up the UI when re-rendering.

Testing and validation
----------------------
- Unit tests are not included by default. To validate changes locally,
	run the app and inspect numeric KPIs and model metrics in the UI.
- For quick sanity checks:

```python
from src import models
# load a small df and run
# df = pd.read_csv('data/supermarket_sales_extended.csv', sep=';', decimal=',')
# df_final, tendency, metrics = models.apply_prophet_forecast(df)
```

Troubleshooting
---------------
- CSV loading errors: ensure `data/supermarket_sales_extended.csv` exists
	and uses `;` separator with `,` decimal (same format produced by
	`data_generator.py`).
- LLM calls failing: check network and that API key and endpoint are
	correct; streaming endpoints may require different client config.
- Plot rendering issues: Plotly figures are created in `src/plots.py`;
	errors are logged via the module-level logger.

Contributing notes
------------------
- Public functions across modules now include English docstrings with
	parameter and return descriptions. Inline technical comments are in
	concise Portuguese per project convention.

License
-------
See `LICENSE` at the repository root.

Further help
------------
If you want, I can:

- Run a quick lint pass (flake8/ruff) and fix small style issues.
- Start the app and report runtime errors in the console.
- Add unit tests for `models.apply_clustering` and
	`models.apply_prophet_forecast` to validate metric computation.

---

