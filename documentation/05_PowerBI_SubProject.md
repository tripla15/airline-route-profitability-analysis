# Phase 5: Power BI Implementation Documentation

This document describes the star-schema data modeling, DAX measures, visual setups, and dashboard layouts implemented in the Power BI standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Data Model View & Star Schema

The Power BI model was built as a clean star schema in the **Model View**, ensuring that a single conformed time dimension filters all other transactional data tables.

- **Central Table**: `Dim_Time` contains the columns `Date_Key`, `Year_Quarter`, and `Year`.
- **Relationships**:
  * `Dim_Time` (1) $\rightarrow$ `Fact_Financials_Master` (`*`) on `Date_Key`. Cross filter direction: **Single**.
  * `Dim_Time` (1) $\rightarrow$ `Oil_Price_Qtr_Avg` (`*`) on `Date_Key`. Cross filter direction: **Single**.
  * `Dim_Time` (1) $\rightarrow$ `covid_19_clean_complete` (`*`) on `Date_Key`. Cross filter direction: **Single**.

This setup ensures that any date slice applied to `Dim_Time` cascades to filter financials, WTI prices, and COVID case numbers.

---

## 2. Calculated Columns & DAX Measures

To support the analytics layer, we wrote calculated columns and DAX measures inside a dedicated container table (`_Measures_Library`):

### 1. Calculated Column (Dim_Time Table)
- **`Period Group`**:
  ```dax
  Period Group = 
  IF(
      Dim_Time[Date_Key] < 45, 
      "Pre_COVID",
      IF(Dim_Time[Date_Key] <= 50, "COVID_Shock", "Recovery")
  )
  ```

### 2. DAX Measures
- **`Weighted Operating Margin`**:
  ```dax
  Weighted Operating Margin = 
  DIVIDE(
      SUM(Fact_Financials_Master[operating_income]), 
      SUM(Fact_Financials_Master[operating_revenue]), 
      0
  )
  ```
  *(Format: Percentage, 2 decimal places)*
- **`Bailout Distortion Gap`**:
  ```dax
  Bailout Distortion Gap = 
  SUM(Fact_Financials_Master[net_income]) - SUM(Fact_Financials_Master[operating_income])
  ```
  *(Format: Currency, 0 decimal places)*
- **`Loss Quarters Count`**:
  ```dax
  Loss Quarters Count = 
  CALCULATE(
      COUNTROWS(Fact_Financials_Master), 
      Fact_Financials_Master[operating_income] < 0
  )
  ```
- **`Loss Probability`**:
  ```dax
  Loss Probability = 
  DIVIDE(
      [Loss Quarters Count], 
      COUNTROWS(Fact_Financials_Master), 
      0
  )
  ```
  *(Format: Percentage, 1 decimal place)*
- **`Avg WTI Oil Price`**:
  ```dax
  Avg WTI Oil Price = AVERAGE(Oil_Price_Qtr_Avg[Oil_Price_Qtr_Avg])
  ```
- **`Total COVID Cases`**:
  ```dax
  Total COVID Cases = SUM(covid_19_clean_complete[Covid_US_Cases_Quarterly])
  ```

---

## 3. Visuals & Dashboard Construction

We built an enterprise-level, single-page interactive report layout:

### Slicers
- **`Period Group Slicer`**: Horizontal/Tile style, placed at the top left using `Dim_Time[Period Group]`.
- **`Airline Name Slicer`**: Dropdown style, placed next to the Period Group slicer.

### Report Charts
1. **Airline Margins Ranking (Clustered Bar Chart)**
   - Y-Axis: `Fact_Financials_Master[Airline_Name]`
   - X-Axis: `[Weighted Operating Margin]`
   - Sort: Sorted by margin descending. Color: Teal (`#2a9d8f`). A dashed red reference line is added at X = 0.
2. **Oil Price vs. Loss Probability (Line and Clustered Column Chart)**
   - Shared X-Axis: `Oil_Price_Qtr_Avg[Oil_Bucket]`
   - Column Y-Axis: `[Loss Probability]` (Amber: `#c17c00`)
   - Line Y-Axis: `[Avg WTI Oil Price]` (Navy: `#1f4e79`)
   - Sort Order: Sorted chronologically by oil price range.
3. **CARES Act Net vs. Operating Income (Clustered Column Chart)**
   - X-Axis: `Fact_Financials_Master[Airline_Name]`
   - Y-Axis: `SUM(Fact_Financials_Master[net_income])` (Teal) and `SUM(Fact_Financials_Master[operating_income])` (Crimson)
   - Visual Filter: `Fact_Financials_Master[CARES_Flag]` is `CARES_Period` to show the bailout distortion.
4. **Industry Recovery Trend (Line and Stacked Column Chart)**
   - Shared X-Axis: `Dim_Time[Year_Quarter]` (filtered to `>= 2019-Q1`)
   - Column Y-Axis: `AVERAGE(Fact_Financials_Master[load_factor])` (Navy)
   - Line Y-Axis: `[Weighted Operating Margin]` (Teal)
   - Reference Band: Shaded red band on the plot area from `2020-Q1` to `2021-Q2` indicating the COVID shock period.
