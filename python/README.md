# Python Sub-Project Directory

This folder contains the programmatic analysis scripts, the interactive Jupyter notebook, and exported statistical files and charts.

## Files Manifest

### 1. `Skies_Under_Pressure_Cleaning.py`
A simple Python script to preprocess raw macroeconomic datasets:
* Loads raw monthly WTI oil prices, filters for 2009–2022, and aggregates them into quarterly averages.
* Loads raw daily COVID-19 US cumulative cases and extracts the quarterly maximum cumulative case counts.
* Exports the cleaned tables directly to the Excel processed data folder.

### 2. `Skies_Under_Pressure_Cleaning.ipynb`
The interactive Jupyter Notebook version of the data cleaning and preprocessing pipeline.

### 3. `Skies_Under_Pressure_Analysis.py`
A Python script executing the main analytical and reporting pipeline. It:
* Ingests the processed Excel worksheets.
* Corrects unit mismatches and runs the statistical analysis suite.
* Exports 4 CSV summary tables.
* Saves 8 publication-quality charts (including replicas of the 5 dashboard visuals).

### 4. `Skies_Under_Pressure_Notebook.ipynb`
The interactive Jupyter Notebook version of the analysis. It displays code cells, light student-style markdown annotations, and inline visualizations sequentially.

### 5. `plots/`
Contains the 8 generated data visualizations (5 dashboard replica charts and 3 additional insight charts).

### 6. CSV Exports (Analytical summaries):
* `stat_01_descriptive_by_airline.csv` — Full-horizon performance statistics per carrier.
* `stat_02_period_comparison.csv` — Grouped stats comparing Pre-COVID, COVID Shock, and Recovery phases.
* `stat_03_correlation_matrix.csv` — Pearson $r$ matrix detailing oil and COVID relationships.
* `stat_04_airline_by_period.csv` — YoY revenue growths and period distributions per airline.

---

## Setup & Running

**Prerequisites:**
Install required libraries:
```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

**Running the pipeline script:**
```bash
python Skies_Under_Pressure_Analysis.py
```

**Opening the interactive notebook:**
```bash
jupyter notebook Skies_Under_Pressure_Notebook.ipynb
```
