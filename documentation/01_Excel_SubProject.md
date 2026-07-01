# Phase 1: Excel Implementation Documentation

This document outlines the design, data transformations, and analysis executed in the Excel standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Data Ingestion & Power Query Cleaning

The first stage of the project involved extracting raw, disjointed spreadsheets and compiling them into clean, structured tables inside Excel. This was done using **Power Query** to enforce structural logic and resolve multiple data quality challenges.

### Cleaning Operations Executed:
- **Filtering BTS Subtotals (Challenge 2)**: The raw BTS financial sheets contained automatic subtotal rows (such as annual totals) and split data across regions (Domestic, Latin America, Atlantic). In Power Query, we filtered out all rows in the `Quarter` column containing "TOTAL", and deleted regional columns to preserve only the consolidated total column.
- **Normalizing Load Factors (Challenge 3)**: The BTS raw files left the quarterly total load factors blank. We pulled the raw load factor records, isolated the `DOMESTIC` column, converted it to a Decimal Number, and applied an `Average` function to aggregate the 3 monthly values into 1 quarterly percentage per carrier.
- **Handling Null Financial Cells (Challenge 4)**: Financial columns like `Ancillary_Revenue` and `Catering_Cost` had missing records. Replacing them with the median would fabricate fake financial transactions and break cost summations. We strictly replaced all null values in transactional columns with `0` to protect accounting integrity.
- **Aggregating Monthly Duplications (Challenge 5)**: Fuel cost and operating income records were reported monthly, creating a duplicate row explosion when merged with quarterly tables. We applied a `Group By` operation on `Airline_Name` and `Year_Quarter`, using the `Sum` aggregation to combine the 3 monthly expenditures into a single quarterly total.
- **Pivoting via the "Rule of Four" (Challenge 6)**: Pivoting the long-format financial table to wide format scattered metrics diagonally across lines. We resolved this by reducing the table to exactly four columns before pivoting: `Airline_Name`, `Year_Quarter`, `Metric_Name`, and `Metric_Value`. The pivot was executed using **Don't Aggregate** to successfully align the data.

---

## 2. Power Pivot Data Modeling

Once the cleaned tables were loaded, we opened the **Power Pivot** window to construct the data model. The relationships are configured as a Star Schema, with the conformed dimension table `Dim_Time` at the center filtering the other tables.

### Relationships Configured:
- **`Dim_Time`** (1) $\rightarrow$ **`Fact_Financials_Master`** (`*`) on the column `Date_Key`
- **`Dim_Time`** (1) $\rightarrow$ **`Oil_Price_Qtr_Avg`** (`*`) on the column `Date_Key`
- **`Dim_Time`** (1) $\rightarrow$ **`covid_19_clean_complete`** (`*`) on the column `Date_Key`

*Rationale*: By using `Dim_Time` as the central dimension table with a `1` to `*` relationship, any time-series slicer or filter applied to a quarter or year will automatically filter the corresponding financials, oil price averages, and COVID case counts simultaneously.

---

## 3. Pivot Table Analysis Layer

To answer the business questions, we built pivot tables in three dedicated analysis sheets:

### Sheet 1: `PVT_Prrofitability`
- **Fields**:
  * Rows: `Fact_Financials_Master[Airline_Name]`
  * Columns: `Dim_Time[Year]`
  * Values: `SUM(operating_income)` and `SUM(operating_revenue)`
- **Calculations**: Operating profit margin ranking per carrier.

### Sheet 2: `PVT_Shocks`
- **Fields**:
  * Rows: `Dim_Time[Year_Quarter]`
  * Columns: None
  * Values: `AVERAGE(Oil_Price_Qtr_Avg[Oil_Price_Qtr_Avg])` and `SUM(Fact_Financials_Master[operating_income])`
- **Calculations**: Compares WTI Crude Oil price buckets vs. operating losses.

### Sheet 3: `PVT_Recovery`
- **Fields**:
  * Rows: `Dim_Time[Year_Quarter]`
  * Columns: `Fact_Financials_Master[Airline_Name]`
  * Values: `AVERAGE(Fact_Financials_Master[load_factor])` and `SUM(Fact_Financials_Master[operating_income])`
- **Calculations**: Analyzes the capacity utilization recovery vs. financial recovery timeline post-COVID.

---

## 4. Sheet Dashboard Design

Using the pivot tables as the data source, we built an interactive dashboard:
- **KPI Cards**: Displaying overall operating margin, WTI Crude Oil averages, and cumulative COVID-19 confirmed cases.
- **Charts**:
  * Clustered Column Chart comparing Net Income vs. Operating Income during the CARES Act period (highlighting the bailout distortion).
  * Dual-Axis Line and Column Chart showing capacity load factor trends compared to operating profit margin recovery.
- **Slicers**: Connected to all pivot tables using **Report Connections** to enable dynamic, synchronized filtering by **Airline Name** and **Period Group**.
