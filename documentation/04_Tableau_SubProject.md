# Phase 4: Tableau Implementation Documentation

This document describes the relationship modeling, calculated fields, worksheets setup, and dashboard design executed in the Tableau standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Logical Relationship Canvas Setup

In Tableau, we imported the sheets from `Master_Tables_file.xlsx` and built the data model on the **Logical Layer** (using Tableau's Relationship Noodles). Relationships preserve the native grain of each table and prevent duplicated data during joins.

- The conformed dimension table **`Dim_Time`** is placed at the top center of the canvas.
- **`Fact_Financials_Master`**, **`Oil_Price_Qtr_Avg`**, and **`covid_19_clean_complete`** are dragged into the canvas as child tables, connecting to `Dim_Time` on `Date_Key`.
- Each relationship is configured with a **One-to-Many (1:*)** cardinality (with `Dim_Time` on the `1` side).

---

## 2. Calculated Fields Library

We constructed the following calculated fields in the Tableau workbook to support the visualizations:

1. **Weighted Operating Margin**:
   - Formula: `SUM([operating_income]) / SUM([operating_revenue])`
   - Default Format: Percentage (2 decimal places).
2. **Bailout Distortion Gap**:
   - Formula: `SUM([net_income]) - SUM([operating_income])`
   - Default Format: Currency (USD, 0 decimal places).
3. **Period Group**:
   - Formula: 
     ```tableau
     IF [Date Key] < 45 THEN "Pre_COVID"
     ELSEIF [Date Key] <= 50 THEN "COVID_Shock"
     ELSE "Recovery"
     END
     ```
4. **Is Loss Quarter**:
   - Formula: `IF [operating_income] < 0 THEN 1 ELSE 0 END`
5. **Loss Probability**:
   - Formula: `SUM([Is Loss Quarter]) / COUNT([Fact_Financials_Master])`
   - Default Format: Percentage (1 decimal place).

---

## 3. Sheet Construction Details

We built 4 distinct worksheets in the workbook:

### Worksheet 1: Operating Margin Ranking
- **Rows**: `Airline Name` (from `Fact_Financials_Master`)
- **Columns**: `Weighted Operating Margin`
- **Sort**: Sorted by columns descending.
- **Color**: `Weighted Operating Margin` dragged to color, using a Teal gradient.
- **Reference Line**: Added a constant reference line at X = 0 (dashed red).

### Worksheet 2: Oil Price vs. Loss Probability (Dual Axis)
- **Columns**: `Oil Bucket` (from `Oil_Price_Qtr_Avg`). Sorted manually as: `Below_50`, `50_to_80`, `80_to_100`, `100_Plus`.
- **Rows**: `Loss Probability` and `Oil Price Qtr Avg` (from `Oil_Price_Qtr_Avg`).
- **Marks Card Configuration**:
  - `Loss Probability`: Mark type set to **Bar** (Color: Amber `#c17c00`).
  - `Oil Price Qtr Avg`: Mark type set to **Line** with marker dots (Color: Crimson `#b23a48`).
- **Dual Axis**: Right-clicked `Oil Price Qtr Avg` pill on the Rows shelf and checked **Dual Axis**.

### Worksheet 3: CARES Act Distortion
- **Columns**: `Airline Name`, `Measure Names`
- **Rows**: `Measure Values` (filtered to keep only `net_income` and `operating_income` from `Fact_Financials_Master`).
- **Color**: `Measure Names` mapped to color (Net Income: Teal, Operating Income: Crimson).
- **Filter**: `CARES Flag` added to filters, set to keep only `CARES_Period` rows.

### Worksheet 4: Load Factor vs. Operating Margin Recovery
- **Columns**: `Year Quarter` (from `Dim_Time`) (Filtered to keep `>= 2019-Q1`).
- **Rows**: `AVG(load_factor)` and `Weighted Operating Margin`.
- **Marks**: Both set to **Line** (Load Factor: Navy, Operating Margin: Teal).
- **Reference Band**: Added a vertical reference band on the X-axis from `2020-Q1` to `2021-Q2` (shaded light red) labeled "COVID Shock Period".

---

## 4. Interactive Dashboard Configuration

- **Grid Assembly**: Combined all 4 sheets into a single dashboard using vertical and horizontal layout containers.
- **Slicers**: Placed filters for `Period Group` and `Airline Name` at the top header block.
- **Filter Connections**: Configured the dashboard filters to **Apply to Worksheets** $\rightarrow$ **Selected Worksheets** $\rightarrow$ checked all 4 sheets, ensuring synchronized cross-filtering.
