# Power BI Sub-Project Directory

This folder contains the interactive MS Power BI Desktop dashboard model and dataset configurations.

## Deliverable File
*   **`skies-under-pressure-analysis.pbix`:** The primary Power BI report file containing data model mappings, custom DAX calculations, and the visual reporting canvas.

---

## Data Model & Relationships
The dataset is structured as a star-schema matching our Excel Power Pivot configuration:
*   **`Fact_Financials_Master`:** The central transaction table containing quarterly financial records.
*   **`Dim_Time`:** The date dimension table.
*   **Relationship:** Joined via `Date_Key` with a **1-to-Many (1:*)** cardinality and **Single** cross-filter direction pointing from `Dim_Time` to `Fact_Financials_Master`.

---

## Custom DAX Measures
The calculations are handled dynamically using Data Analysis Expressions (DAX):

1.  **Total Operating Revenue:**
    ```dax
    Total Operating Revenue = SUM(Fact_Financials_Master[operating_revenue])
    ```
2.  **Total Operating Income:**
    ```dax
    Total Operating Income = SUM(Fact_Financials_Master[operating_income])
    ```
3.  **Revenue Margin:**
    ```dax
    Revenue Margin = DIVIDE([Total Operating Income], [Total Operating Revenue], 0)
    ```
4.  **Bailout Cushion (Net Financial Assistance):**
    Tracks the artificial profit gap (Net Income - Operating Income) during the CARES bailout window:
    ```dax
    Bailout Cushion = 
    CALCULATE(
        SUM(Fact_Financials_Master[net_income]) - SUM(Fact_Financials_Master[operating_income]),
        Fact_Financials_Master[CARES_FLAG] = "CARES_Period"
    )
    ```

---

## Dashboard Visualizations Replicated
*   **KPI Cards:** Displaying Total Operating Revenue, Total Operating Income, and Revenue Margin (%).
*   **Chart 1 (Clustered Column):** Average Quarterly Operating Income (CARES vs Normal period).
*   **Chart 2 (Dual-Axis Line):** Annual Revenue vs Net Income timeline (2018–2022).
*   **Chart 3 (Horizontal Bar):** Operating Revenue ranking by airline.
*   **Chart 4 (Horizontal Bar):** Net Financial Assistance (Bailout Cushion) sorted by carrier.
*   **Chart 5 (Clustered Column):** Total Operating Revenue and Operating Income grouped by WTI crude oil price buckets.
