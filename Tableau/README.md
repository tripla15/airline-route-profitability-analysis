# Tableau Sub-Project Directory

This folder contains the interactive Tableau Desktop dashboard workbook.

## Deliverable File
*   **`Skies-Under-Pressure.twb`:** The primary Tableau report workbook. It references our star-schema Excel tables dynamically and renders the executive reporting layout.

---

## Data Model & Connections
The workbook connects to our master Excel workbook (`Excel/Master_Tables_file.xlsx`):
*   **Primary Tables:** `Dim_Time`, `Fact_Financials_Master`, `Oil_Prices_Avg_Qtr`, and `covid_19_clean_complete`.
*   **Relationship Mapping:** Joined on **`Date Key`** using Tableau's logical relationship model.

---

## Custom Calculated Fields (Measures)
Calculations are written inside Tableau to ensure dynamic evaluation across dimensions:

1.  **Revenue Margin:**
    ```tableau
    SUM([Operating Income]) / SUM([Operating Revenue])
    ```
2.  **Bailout Cushion (Net Financial Assistance):**
    Tracks the artificial profit gap (Net Income - Operating Income) during the CARES Act bailout window:
    ```tableau
    SUM(IF [Cares Flag] = 'CARES_Period' THEN [Net Income] - [Operating Income] END)
    ```

---

## Dashboard Visualizations Replicated
*   **Sheet 1 (Avg Quarterly Operating Income):** Side-by-side bar chart showing carrier earnings under normal vs. CARES periods.
*   **Sheet 2 (Recovery Profile):** Dual-axis line chart tracking annual revenue against net income (2018–2022).
*   **Sheet 3 (Operating Revenue for Airlines):** Horizontal bar chart sorting carrier revenue scales descending.
*   **Sheet 4 (Net Financial Assistance):** Diverging bar chart showing the bailout cushion per carrier, color-graded dynamically.
*   **Sheet 5 (Revenue Margin vs Oil Price Bucket):** Clustered bar chart of operating revenues and incomes combined with a dual-axis line showing margin percentages.
