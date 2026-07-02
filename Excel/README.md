# Excel Sub-Project Directory

This directory contains the Excel data models, cleaned quarterly tables, and interactive presentation dashboard.

## Folder Structure

### 1. `Master_Tables_file.xlsx` (The Master Workbook)
The primary analytical spreadsheet containing:
* **`Fact_Financials_Master`:** The consolidated star-schema fact table containing financial records for 10 airlines over 56 quarters.
* **`Dim_Time`:** The central calendar hub mapping date keys to chronological quarters.
* **`Oil_Prices_Avg_Qtr`:** Average quarterly WTI oil prices with price buckets.
* **`covid_19_clean_complete`:** US quarterly cumulative COVID-19 case counts.
* **Pivot Tables:** Built-in sheets (`PVT_Prrofitability`, `PVT_Shocks`, `PVT_Recovery`) analyzing specific query questions.
* **`Statistical_Analysis`:** A premium, fully-formulated worksheet detailing carrier stats, period averages, oil bucket metrics, and CARES Act distortions using live Excel formulas.

### 2. `Processed Data/`
Houses the individual cleaned tables exported from initial data prep steps:
* **`BTS_data_processed.xlsx`:** Cleaned and normalized airline financial records.
* **`Oil_Qtr.xlsx`:** Processed quarterly WTI spot averages.
* **`Covid_US_Cases_Quarter.xlsx`:** Cleaned quarterly COVID case counts.

---

## Technical Highlights
* **Power Pivot Data Model:** Tables are joined on `Date_Key` to enforce a hub-and-spoke star schema directly within the Excel data environment.
* **Dynamic Formulas:** Summary statistics are computed using live calculations (`MINIFS`, `MAXIFS`, `AVERAGEIFS`, and `SUMPRODUCT`) to allow interactive auditing.
