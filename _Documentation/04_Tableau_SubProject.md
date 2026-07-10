# Phase 4: Tableau Implementation Documentation

This document describes the relationship modeling, calculated fields, worksheets setup, and dashboard design executed in the Tableau standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Logical Relationship Canvas Setup

In Tableau, we imported the sheets from `Master_Tables_file.xlsx` and built the data model on the **Logical Layer** (using Tableau's Relationship Noodles). Relationships preserve the native grain of each table and prevent duplicated data during joins.

*   The conformed dimension table **`Dim_Time`** is placed at the top center of the canvas.
*   **`Fact_Financials_Master`**, **`Oil_Prices_Avg_Qtr`**, and **`covid_19_clean_complete`** are dragged into the canvas as child tables, connecting to `Dim_Time` on `Date_Key`.
*   Each relationship is configured with a **One-to-Many (1:*)** cardinality (with `Dim_Time` on the `1` side).

---

## 2. Calculated Fields Library

We constructed the following calculated fields in the Tableau workbook to support the visualizations:

1.  **Revenue Margin:**
    *   Formula: `SUM([Operating Income]) / SUM([Operating Revenue])`
    *   Default Format: Percentage (0 decimal places).
2.  **Bailout Cushion:**
    *   Formula:
        ```tableau
        SUM(IF [Cares Flag] = 'CARES_Period' THEN [Net Income] - [Operating Income] END)
        ```
    *   Default Format: Currency (USD, 0 decimal places).

---

## 3. Sheet Construction Details

We built 5 distinct worksheets in the workbook:

### Worksheet 1: Avg Quarterly Operating Income (CARES vs Normal)
*   **Rows:** `Airline Name` (from `Fact_Financials_Master`)
*   **Columns:** `Cares Flag`, `Average Operating Income` (Measure changed to Average).
*   **Color:** `Cares Flag` mapped to color (CARES_Period: Crimson `#DC2626`, Normal_Period: Blue `#2563EB`).

### Worksheet 2: Recovery Profile (Annual Income vs Revenue)
*   **Columns:** `Year` (from `Dim_Time`) (Filtered to keep `2018` to `2022`).
*   **Rows:** `SUM(Operating Revenue)` and `SUM(Net Income)`.
*   **Marks card:** Both set to **Line** (Operating Revenue: Blue `#2563EB`, Net Income: Amber `#D97706`).
*   **Dual Axis:** Right-clicked Net Income and checked **Dual Axis**.

### Worksheet 3: Operating Revenue for Airlines
*   **Rows:** `Airline Name`
*   **Columns:** `SUM(Operating Revenue)`
*   **Sort:** Sorted descending.
*   **Color:** Set to Blue (`#2563EB`).

### Worksheet 4: Net Financial Assistance (Bailout Cushion)
*   **Rows:** `Airline Name`
*   **Columns:** `Bailout Cushion`
*   **Color:** `Bailout Cushion` mapped to color. Configured an Orange-Blue diverging palette centered at `0` (positive: Amber `#D97706`, negative: Crimson `#DC2626`).
*   **Sort:** Sorted descending.

### Worksheet 5: Revenue Margin vs Oil Price Bucket (Combo)
*   **Columns:** `Oil Bucket` (from `Oil_Prices_Avg_Qtr`). Sorted manually: `Below_50`, `50_to_80`, `80_to_100`, `100_Plus`.
*   **Rows:** `Measure Values` (filtered to keep only `SUM(Operating Revenue)` and `SUM(Operating Income)`) and `Revenue Margin`.
*   **Color:** `Measure Names` mapped to color (Operating Revenue: Amber `#D97706`, Operating Income: Blue `#2563EB`).
*   **Dual Axis:** Right-clicked `Revenue Margin` and checked **Dual Axis** (Mark type: Line, Color: Green `#22C55E`).

---

## 4. Interactive Dashboard Configuration

*   **Grid Assembly:** Combined all 5 sheets into a single dashboard using vertical and horizontal layout containers.
*   **Slicers:** Placed global filter cards for `Airline Name`, `Year`, and `Cares Flag` on the left sidebar.
*   **Worksheet Shading:** Set the dashboard canvas background to Slate Dark (`#0F172A`) and set individual sheet backgrounds to dark slate (`#1E293B`) to represent rounded container cards.
