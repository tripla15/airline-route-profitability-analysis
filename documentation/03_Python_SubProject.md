# Phase 3: Python Implementation Documentation

This document describes the programmatic data pipeline, financial analysis, and visualization generation executed in the Python standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Programmatic Cleaning and Joining Pipeline

The Python pipeline was built using `pandas`, `numpy`, `matplotlib`, and `seaborn` to execute a standalone analytical workflow.

```python
import pandas as pd
import numpy as np

# Load sheets directly from Excel
excel_path = "Excel/Master_Tables_file.xlsx"
dim_time = pd.read_excel(excel_path, sheet_name="Dim_Time")
fact_fin = pd.read_excel(excel_path, sheet_name="Fact_Financials_Master")
oil_prices = pd.read_excel(excel_path, sheet_name="Oil_Price_Qtr_Avg")
covid_cases = pd.read_excel(excel_path, sheet_name="covid_19_clean_complete")

# Merge data sets on Date_Key
merged = pd.merge(fact_fin, dim_time, on="Date_Key", how="left")
merged = pd.merge(merged, oil_prices.drop(columns=["Oil_Bucket"], errors="ignore"), on="Date_Key", how="left")
merged = pd.merge(merged, covid_cases, on="Date_Key", how="left")
merged["Covid_US_Cases_Quarterly"] = merged["Covid_US_Cases_Quarterly"].fillna(0).astype(int)

# Create helper columns
merged["Operating_Margin"] = merged["operating_income"] / merged["operating_revenue"]
```

---

## 2. Statistical Analysis & Key Calculations

The Python script performs several key calculations to address the business questions:

### 1. Weighted Operating Margin Ranking
We calculate the weighted profit margin per carrier across all 56 quarters:
$$\text{Weighted Operating Margin} = \frac{\sum \text{operating\_income}}{\sum \text{operating\_revenue}}$$
- **Result**: Allegiant ranked first at **11.73%**, while American Airlines ranked last at **0.77%**.

### 2. Pearson Correlation Coefficients
We calculate the linear relationship between WTI spot prices and airline performance:
- WTI Oil Price vs. Operating Income: $r = 0.0755$
- WTI Oil Price vs. Operating Margin: $r = 0.2555$
*Insight*: The positive correlation demonstrates that fuel cost drops are not the primary driver of airline profits. Instead, global demand-pull inflation (higher macroeconomic activity driving both oil prices and passenger travel demand) dominates.

### 3. COVID Operating Income Collapse
We subtract the average quarterly operating income during the COVID Shock period (`2020-Q1` to `2021-Q2`) from the Pre-COVID baseline. Legacy network carriers suffered the largest absolute declines (American Airlines at **-$3.64 billion** per quarter), while Allegiant was the most resilient (crashes limited to **-$94 million** per quarter).

### 4. CARES Act Distortion Gap
We calculate the quarterly average gap between Net Income and Operating Income:
$$\text{Bailout Distortion Gap} = \text{net\_income} - \text{operating\_income}$$
During the CARES period, the distortion gap was largest for American Airlines (**+$1.77 million** per quarter), showing that government grant support hid severe operational losses.

---

## 3. Publication-Ready Visualizations

The script generates 4 high-resolution plots, saved directly to the [python/plots/](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/python/plots) directory:

### Plot 1: `01_operating_margins_ranking.png`
- **Type**: Horizontal Bar Chart.
- **Description**: Ranks the 10 airlines by weighted operating margin, with a red dashed reference line at X = 0.
- **Color Theme**: Teal (`#2a9d8f`).

### Plot 2: `02_oil_vs_loss_probability.png`
- **Type**: Dual-Axis Bar and Line Chart.
- **Description**: Displays the probability of airline losses as columns (left Y-axis) and the average WTI Crude Oil price as a line (right Y-axis) across the oil price buckets.
- **Color Theme**: Columns in Amber (`#c17c00`), line in Crimson (`#b23a48`).

### Plot 3: `03_cares_net_vs_operating_gap.png`
- **Type**: Clustered Column Chart.
- **Description**: Compares Average Net Income vs. Average Operating Income during the CARES Act window, showing the bailout distortion.
- **Color Theme**: Net Income in Teal (`#2a9d8f`), Operating Income in Crimson (`#b23a48`).

### Plot 4: `04_load_factor_vs_operating_margin.png`
- **Type**: Dual-Axis Line Chart with Timeline Shading.
- **Description**: Compares average industry Load Factor (left Y-axis) vs. Weighted Operating Margin (right Y-axis) from 2019-Q1 to 2022-Q4, with a shaded red band highlighting the COVID shock period.
- **Color Theme**: Load Factor in Navy (`#1f4e79`), Operating Margin in Teal (`#2a9d8f`).
