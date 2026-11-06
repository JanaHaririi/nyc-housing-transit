# NYC Housing × Street Safety

**Live website:** https://nyc-housing-transit.onrender.com
*(Free hosting: if the site has been idle, the first visit can take about a minute to load.)*

Data Engineering & Visualization, Milestone 1 (Winter 2026), German International University.

Do the New York neighbourhoods with the most housing complaints also have the most serious traffic crashes? This project cleans and integrates two NYC Open Data datasets, answers 8 research questions in a Jupyter notebook, and presents the results in an interactive Dash website.

## Datasets
| Domain | Dataset | Link |
|---|---|---|
| Housing & Development | HPD Housing Maintenance Code Complaints and Problems | https://data.cityofnewyork.us/d/ygpa-z7cr |
| Transportation | NYC DOT Serious Injury Response, Tracking & Analysis Program (SIRTA) | https://data.cityofnewyork.us/d/xeqp-qz8h |

The datasets are integrated at **ZIP code × year** (and **borough × month** for seasonal patterns), covering **2022–2025**.

## Repository structure
```
nyc-housing-transit/
├── notebooks/nyc_housing_transit.ipynb   # EDA, cleaning, integration, 8 research questions
├── data/
│   ├── processed/                        # integrated tables used by the website
│   │   ├── zip_year.csv
│   │   ├── borough_month.csv
│   │   └── crash_points.csv
│   └── raw/                              # local copies of the raw data (not on GitHub, too large)
├── app/
│   ├── app.py                            # Dash website
│   └── assets/style.css                  # website styling
├── requirements.txt                      # libraries for the website
└── .python-version                       # Python version (3.13)
```

## Setup (run locally on Windows)
1. Install **Python 3.13** from python.org.
2. Clone the repository and open the folder in VS Code:
   ```
   git clone https://github.com/JanaHaririi/nyc-housing-transit.git
   cd nyc-housing-transit
   ```
3. Create a virtual environment and install the libraries:
   ```
   py -V:3.13 -m venv .venv
   .venv\Scripts\python -m pip install -r requirements.txt
   .venv\Scripts\python -m pip install numpy matplotlib seaborn requests ipykernel
   ```
4. **Notebook:** open `notebooks/nyc_housing_transit.ipynb`, select the `.venv` kernel and click **Run All**.
   The first run downloads the data from NYC Open Data (about 10 minutes) and saves it to `data/raw/`; later runs load the saved copy in seconds.
5. **Website:** run
   ```
   .venv\Scripts\python app\app.py
   ```
   and open http://127.0.0.1:8050 in a browser.

## Deployment (Render)
The website is deployed on [Render](https://render.com) (free plan) directly from this GitHub repository:
1. On Render, choose **New → Web Service** and connect this repository.
2. Settings:
   - **Language:** Python 3
   - **Branch:** `main`
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn --chdir app app:server`
   - **Instance type:** Free
3. Render installs the libraries from `requirements.txt`, uses Python 3.13 from `.python-version`, and redeploys automatically after every push to `main`.

## Website features
- Dropdown filters: borough, year, housing measure, crash measure
- Search mode: typing e.g. *"Bronx 2024 heat fatalities"* sets the filters automatically
- A central **Generate Report** button that updates every number and chart
- Five interactive chart types: scatter, map, line, bar and heatmap (two of them cross-domain)
- A story section: the question, the data, the findings, the limits and the impact for New Yorkers

## Contributions
This project was completed **individually** by **Jana Mohamed El Hariri (10005950)**, with the professor's approval to work alone as a special case. I completed all parts of the project, scoped as a 4-member team (8 research questions and 8 visualizations):
- Dataset selection and data loading
- Exploratory data analysis
- Pre-integration cleaning of both datasets, including nearest-address ZIP imputation
- Integration and post-integration cleaning
- All 8 research questions and visualizations
- The Dash website and its deployment on Render
- Documentation (notebook, README)

AI assistance (Claude, Anthropic) was used throughout; every prompt is listed in Section 9 of the notebook.