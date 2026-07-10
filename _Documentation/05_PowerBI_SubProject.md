# Phase 5: Power BI Implementation Documentation

This document describes the star-schema data modeling, DAX measures, visual setups, and dashboard layouts implemented in the Power BI standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Data Model View & Star Schema

The Power BI model was built as a clean star schema in the **Model View**, ensuring that a conformed time dimension filters all other transactional data tables.

*   **Central Table:** `Dim_Time` contains the columns `Date_Key`, `Year_Quarter`, and `Year`.
*   **Relationships:**
    *   `Dim_Time` (1) $\rightarrow$ `Fact_Financials_Master` (`*`) on `Date_Key`. Cross filter direction: **Single**.
    *   `Dim_Time` (1) $\rightarrow$ `Oil_Prices_Avg_Qtr` (`*`) on `Date_Key`. Cross filter direction: **Single**.
    *   `Dim_Time` (1) $\rightarrow$ `covid_19_clean_complete` (`*`) on `Date_Key`. Cross filter direction: **Single**.

---

## 2. Calculated DAX Measures

To support the analytics layer, we wrote calculated DAX measures inside the `Fact_Financials_Master` table:

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
    *(Format: Percentage, 0 decimal places)*
4.  **Bailout Cushion (Net Financial Assistance):**
    Tracks the artificial profit gap (Net Income - Operating Income) during the CARES Act bailout window:
    ```dax
    Bailout Cushion = 
    CALCULATE(
        SUM(Fact_Financials_Master[net_income]) - SUM(Fact_Financials_Master[operating_income]),
        Fact_Financials_Master[CARES_FLAG] = "CARES_Period"
    )
    ```
    *(Format: Currency, 0 decimal places)*

---

## 3. Visuals & Dashboard Construction

We built a single-page interactive report canvas using your slate dark theme:
*   **Canvas Background:** Set canvas background shading to **`#0F172A`** (0% transparency).
*   **Card Containers:** Visual cards and chart backgrounds are shaded dark slate **`#1E293B`** with a thin border color **`#334155`**.
*   **Typography:** Visual titles are solid white (**`#FFFFFF`**), and X/Y axis tick labels are configured in muted gray (**`#94A3B8`**).

### Visual Slicers
*   **`Airline Name Slicer`:** Vertical list, placed in the left sidebar.
*   **`Year Slicer`:** Horizontal/Tile style, placed below the Airline slicer.
*   **`CARES/Normal Period Slicer`:** Horizontal/Tile style, placed below the Year slicer.

### Replicated Visual Charts
1.  **Average Quarterly Operating Income (Clustered Column Chart)**
    *   X-Axis: `Cares Flag` (CARES_Period vs. Normal_Period).
    *   Y-Axis: `Average Operating Income` (using average aggregation).
    *   Color Accent: CARES_Period is Crimson (`#DC2626`), and Normal_Period is Blue (`#2563EB`).
2.  **Recovery Profile (Line and Clustered Column Chart)**
    *   Shared X-Axis: `Dim_Time[Year]` (filtered to `2018` to `2022`).
    *   Column Y-Axis: `Total Operating Revenue` (Blue `#2563EB`).
    *   Line Y-Axis: `Total Net Income` (Amber `#D97706`).
3.  **Operating Revenue for Airlines (Horizontal Bar Chart)**
    *   Y-Axis: `Airline_Name`
    *   X-Axis: `Total Operating Revenue`
    *   Color Accent: Blue (`#2563EB`). Sorted descending.
4.  **Net Financial Assistance (Horizontal Bar Chart)**
    *   Y-Axis: `Airline_Name`
    *   X-Axis: `Bailout Cushion`
    *   Color Accent: Conditional color formatting set to color negative cushions Crimson (`#DC2626`) and positive cushions Amber (`#D97706`). Sorted descending.
5.  **Revenue Margin vs Oil Price Bucket (Line and Clustered Column Chart)**
    *   Shared X-Axis: `Oil_Prices_Avg_Qtr[Oil_Bucket]`.
    *   Column Y-Axis: `Total Operating Revenue` (Amber `#D97706`) and `Total Operating Income` (Blue `#2563EB`).
    *   Line Y-Axis: `Revenue Margin` (Green `#22C55E`).
