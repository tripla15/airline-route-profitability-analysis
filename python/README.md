# Python Sub-Project Directory

This folder contains the programmatic analysis scripts, the interactive Jupyter notebook, and exported statistical files and charts.

## Files Manifest

### 1. `Skies_Under_Pressure_Analysis.py`
A production-grade Python script executing the full ETL and analytical pipeline. It:
* Ingests source data from the master Excel workbook.
* Corrects unit mismatches (converting fuel costs to $Thousands to align with revenues).
* Runs the statistical analysis suite.
* Exports 4 CSV summary tables.
* Saves 9 publication-quality charts.

### 2. `Skies_Under_Pressure_Notebook.ipynb`
The interactive Jupyter Notebook version of the analysis. It is designed for step-by-step review, displaying code cells, inline Markdown explanations, and visualizations sequentially in a notebook interface.

### 3. `plots/`
Contains the 9 generated data visualizations (PNG files) with professional typography, custom carrier color schemes, and dual-axis alignments.

### 4. CSV Exports (Analytical summaries):
* `stat_01_descriptive_by_airline.csv` — Full-horizon performance statistics per carrier.
* `stat_02_period_comparison.csv` — Grouped stats comparing Pre-COVID, COVID Shock, and Recovery phases.
* `stat_03_correlation_matrix.csv` — Pearson $r$ matrix detailing oil and COVID relationships.
* `stat_04_airline_by_period.csv` — Cross-tabulated carrier metrics grouped by period.

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
