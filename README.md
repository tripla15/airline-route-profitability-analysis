# Skies Under Pressure

**Project Type:** DEPI Graduation Project - Data Analytics Track


Drive Folder Link: https://drive.google.com/drive/folders/1fHcvCEqZiPnLxDSBSvkseah-Vqd6wry5?usp=sharing

**Author:** Team 5

**Timeline Focus:** 2009–2022

---

## Project Overview

This project analyzes how external macroeconomic factors affect the financial performance and stability of the US passenger aviation sector. Rather than viewing financial outcomes in isolation, the study isolates specific cause-and-effect relationships between two major external variables—crude oil market price shifts and the COVID-19 pandemic—and airline operational margins.

**Scope:**

* **Timeline:** 14 Years (2009 to 2022, consolidated by financial quarters)
* **Target Carriers (10):** Delta Air Lines, United Airlines, American Airlines, Southwest Airlines, JetBlue Airways, Alaska Airlines, Spirit Airlines, Frontier Airlines, Hawaiian Airlines, and Allegiant Air.

---

## Core Objectives

The analytical framework tracks the interplay between global disruption data and internal carrier accounting records:

1. **Fuel Cost Impact:** Using crude oil price metrics as a factor driving airline jet fuel expenses and operating margins.
2. **Market Demand Impact:** Monitoring US COVID-19 tracking numbers to measure the impact of sudden travel drops and fleet groundings.
3. **Financial Tracking:** Using standardized metrics from the Bureau of Transportation Statistics (BTS) to track the explicit revenue and margin impacts across different carrier business models.

---

## Data Architecture Constraints

### 1. Unified Aggregation Grain

To ensure data consistency and prevent database multi-row calculation errors during joins, every source dataset is normalized and aggregated to the uniform grain of **Airline** and **Year_Quarter** (e.g., `2020-Q3`). Raw daily or monthly variations are consolidated out of final analytical tables.

### 2. Financial Metrics Adjustment (CARES Act Period)

Between 2020-Q2 and 2021-Q2, federal funding via the CARES Act significantly altered reported corporate net incomes. To evaluate true baseline performance during this crisis window, **`OPERATING_PROFIT_LOSS`** is designated as the primary tracking metric. Net Income is used as a secondary comparison metric to highlight this policy-driven reporting gap.

### 3. Independent Implementations

The project requires **5 separate standalone deliverables** (Excel, SQL, Python, Tableau, and Power BI). To demonstrate cross-tool competency, each framework independently handles its own data loading, table transformations, analytical querying, and final interactive report layouts.

---

## Data Sources

| Domain | Source | Engineering Description |
| --- | --- | --- |
| **Financial Baseline** | Bureau of Transportation Statistics (BTS) | Form 41 Schedule P-12 reports covering core revenues and expenses. |
| **Fuel Price Variable** | U.S. Energy Information Administration (EIA) | Historical WTI Crude Oil prices, aggregated into unweighted quarterly averages. |
| **Pandemic Tracking** | Johns Hopkins University / OWID | Daily cumulative US COVID-19 cases, using maximum snapshot values per quarter. |

---

## Repository Structure

```
airline-route-profitability-analysis/
├── README.md
│
├── Collected BTS data before processing/  # Storage directory preserving original raw downloads
│   ├── BTS Data_CSV/
│   ├── BTS_Load_Factor/
│   ├── BTS_OLD/
│   ├── BTS_Fuel_Cost_ALL_Carriers.csv
│   └── BTS_Operating_Income_ALL_Carriers.csv
│
│
├── Excel/                                 # Excel models and data processing sheets
│   ├── BTS_Data.xlsx
│   ├── Oil_Qtr.xlsx
│   └── Processed Data/                    # Cleaned/processed datasets for analysis
│       ├── BTS_data_processed.xlsx
│       ├── Oil_Qtr.xlsx
│       └── covid_19_clean_Final.xlsx
│
├── Power BI/                              # Power BI desktop model and reporting workspace
│   ├── README.md
│   └── skies-under-pressure-analysis.pbix
│
├── SQL/                                  # MySQL database schemas and analytical queries
│   ├── README.md
│   ├── skies-under-pressure-model.mwb    # MySQL Workbench visual EER model
│   └── skies-under-pressure-queries.sql  # SQL queries (preprocessing & analysis)
│
├── Python/                                # Programmatic analysis notebook
│   ├── README.md
│   └── Skies_Under_Pressure_Notebook.ipynb
│
├── Tableau/                               # Tableau desktop visualization workbook
│   ├── README.md
│   └── Skies-Under-Pressure.twb
│
└── Raw Data/                              # Unprocessed raw global variable data
    ├── covid_19_clean_complete.csv
    └── crude-oil-price.csv
```

---

## Technical Implementations

* **Excel:** Initial data prep, table modeling using Power Pivot, and an interactive sheet dashboard.
* **SQL:** Relational schema design, primary/foreign key constraint enforcement, database indexing, and analytical querying using CTEs and window functions.
* **Python (Pandas / NumPy / Matplotlib):** Programmatic cleaning pipelines, data validation, mathematical correlation metrics, and automated chart export configurations.
* **Tableau:** Relationship modeling layer connecting logical tables to build integrated sheets and dashboard actions.
* **Power BI:** Star-schema architecture setup, calculation layers using dynamic DAX measures (`CALCULATE`, `DIVIDE`), and synchronized filter panel layouts.

---

## Key Findings

> *To be completed upon final review. Preliminary tracking indicates significant operational profit margin compression during fuel price peaks, along with varying recovery timelines between low-cost carriers and legacy point-to-point networks following the pandemic demand shift.*

---

## How to Navigate This Project

1. **Source Data**: Review [Raw Data/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Raw%20Data) to inspect raw external datasets.
2. **Raw Collected Data**: Review [Collected BTS data before processing/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Collected%20BTS%20data%20before%20processing) to inspect raw aviation datasets.
3. **Processed Data**: Review [Excel/Processed Data/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Excel/Processed%20Data) to see cleaned and aligned quarterly datasets.
4. **Excel Workbooks**: Open [Excel/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Excel) to explore the Power Pivot data models and dashboard sheets.
5. **Python Pipeline**: Open [Python/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Python) to view the unified preprocessing and analysis notebook.
6. **Power BI Dashboard**: Open [Power BI/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Power%20BI) to inspect the Power BI model.
7. **Tableau Workbook**: Open [Tableau/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/Tableau) to inspect the Tableau sheet visualizations.

---

## Reviewer Notes

* **Pipeline Verification:** The `collected_data/` directory archives the initial reporting outputs directly from government sources to allow end-to-end auditability of our cleaning transformations.
* **Scope Reduction:** Customer satisfaction analysis (via the Skytrax text review dataset) was removed during initial engineering. Exploratory evaluation showed that after filtering for our specific 10 carriers, the records had significant chronological gaps and small sample sizes. Aggregating this thin text data into a strict financial quarterly grain introduced high statistical variance, so it was dropped to preserve the integrity of the core macro analysis.
