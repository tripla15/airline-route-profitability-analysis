# Phase 3: Python Implementation Documentation

This document describes the programmatic data pipeline, financial analysis, and visualization generation executed in the Python standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Unified Notebook Architecture

The Python subproject is implemented as a single, self-contained Jupyter Notebook (`Skies_Under_Pressure_Notebook.ipynb`) containing both the preprocessing and analytical pipelines. Running the notebook sequentially executes:
1.  **Extract & Ingest:** Loads raw CSV datasets (`crude-oil-price.csv` and `covid_19_clean_complete.csv`).
2.  **Transform & Preprocess:** Filters WTI crude oil prices (2009–2022) to compute quarterly averages and filters US cumulative COVID cases to extract quarterly maximum confirmed cases.
3.  **Export Cleaned Sheets:** Saves these processed sheets directly into the Excel processed data folder.
4.  **Load & Merge Model:** Ingests the conformed dimension and fact tables from the master Excel workbook, joining them on `Date_Key`.
5.  **Compute Statistics:** Calculates descriptive statistics, period summaries, YoY growth, and Pearson correlations.
6.  **Renders Visualizations:** Draws all charts directly inline.

---

## 2. In-Memory Statistical Calculations

The notebook performs the following calculations to address the project questions:

### 1. Weighted Operating Margin Ranking
We calculate the true weighted operating margin per airline across all 56 quarters:
$$\text{Weighted Operating Margin} = \frac{\sum \text{operating\_income}}{\sum \text{operating\_revenue}} \times 100$$

### 2. Pearson Correlation Coefficients
We calculate the linear relationship between macro variables and operational metrics:
*   WTI Oil Price vs. Operating Margin: $r = 0.25$
*   COVID-19 Cases vs. Operating Margin: $r = -0.73$
*   *Insight:* The strong negative correlation validates that pandemic travel bans and fleet groundings had a far more destructive impact on airline profitability than fuel price fluctuations.

### 3. CARES Act Bailout Cushion
We isolate the bailout gap (reported Net Income minus true Operating Income) during the CARES period (`2020-Q2` to `2021-Q2`):
$$\text{Bailout Cushion} = \text{net\_income} - \text{operating\_income}$$
This reveals that government Payroll Support Program (PSP) subsidies artificially padded bottom-line net incomes while carriers suffered massive operational losses.

---

## 3. Visualization Suite (Visual Themes)

All charts are rendered directly inline in VS Code and use a slate-dark theme matching the Excel and Power BI dashboards:
*   **Canvas Facecolor:** `#0F172A` (Master Dark Canvas)
*   **Axes Background:** `#1E293B` (Container Panels)
*   **Text & Titles:** `#FFFFFF` (Solid White)
*   **Labels & Ticks:** `#94A3B8` (Muted Gray)
*   **Borders & Grids:** `#334155` (Slate Gray)

### Visualizations Rendered
1.  **Chart 1: Average Quarterly Operating Income** (Clustered Column Chart). Displays CARES period averages in Crimson (`#DC2626`) and normal averages in Blue (`#2563EB`).
2.  **Chart 2: Recovery Profile (Annual Income vs Revenue)** (Dual-Axis Line Chart). Renders Operating Revenue in Blue (`#2563EB`) and Net Income in Amber (`#D97706`).
3.  **Chart 3: Operating Revenue for Airlines** (Horizontal Bar Chart). Renders total revenues in Blue (`#2563EB`).
4.  **Chart 4: Net Financial Assistance (Bailout Cushion)** (Horizontal Bar Chart). Highlights positive cushions in Amber (`#D97706`) and negative cushions in Crimson (`#DC2626`).
5.  **Chart 5: Operating Revenue & Income vs Oil Price Brackets** (Dual-Axis Combo Chart). Plots Revenue columns in Amber (`#D97706`), Income columns in Blue (`#2563EB`), and a line showing Margin in Green (`#22C55E`).
6.  **Chart 6: COVID Collapse (Pre vs Shock)** (Clustered Column Chart). Pre-COVID in Blue (`#2563EB`) and Shock in Red (`#DC2626`).
7.  **Chart 7: Load Factor vs Operating Margin Timeline** (Dual-Axis Line Chart). Load Factor in Blue (`#2563EB`) and Margin in Green (`#22C55E`).
8.  **Chart 8: Correlation Matrix of Variables** (Seaborn Heatmap). Renders the Pearson correlation values.
