# Stage 4: Technical Implementations — Skies Under Pressure

To demonstrate technical capability across the data analytics stack, this project was built as 5 separate standalone pipelines. Each tool independently handles its own data loading, cleaning, star-schema modeling, analytical calculations, and visual report presentation.

---

## 1. Excel Standalone Pipeline
- **Modeling Tool**: Excel **Power Pivot** (Data Model).
- **Data Model Relationships**:
  - Developed a star schema where the conformed dimension table `Dim_Time` acts as the parent table (`1`), filtering the three child data tables (`*`): `Fact_Financials_Master`, `Oil_Price_Qtr_Avg`, and `covid_19_clean_complete` on the `Date_Key` column.
- **DAX Measures**:
  - Created calculated columns and measures inside Power Pivot:
    * `Weighted Operating Margin` = `DIVIDE(SUM(Fact_Financials_Master[operating_income]), SUM(Fact_Financials_Master[operating_revenue]), 0)`
    * `Operating Profit Margin` = `SUM([operating_income]) / SUM([operating_revenue])`
- **Pivot Table Analysis Sheets**:
  - Created dedicated sheets to summarize calculations:
    * `PVT_Prrofitability`: Displays operating income and operating revenue by airline and calendar year/quarter.
    * `PVT_Shocks`: Aggregates operating income alongside average quarterly WTI crude oil prices to analyze price impacts.
    * `PVT_Recovery`: Evaluates post-COVID recovery timelines and load factor performance.
- **Interactive Dashboard**:
  - Built an interactive dashboard featuring KPI cards, pivot charts, and timeline slicers for `Period Group` and `Airline Name`.

---

## 2. SQL Database Pipeline
- **Database Engine**: SQLite (embedded in python) and PostgreSQL.
- **Schema DDL**:
  - Designed the database schema with primary key and foreign key constraints to ensure referential integrity:
    * `Dim_Time` (Surrogate Key `Date_Key` PK).
    * `Oil_Price_Qtr_Avg` (`Date_Key` FK).
    * `covid_19_clean_complete` (`Date_Key` FK).
    * `Fact_Financials_Master` (Composite Primary Key `(Date_Key, Airline_Name)`, with `Date_Key` as FK referencing `Dim_Time`).
- **Data Loading**:
  - Wrote a Python script to extract processed data from the Excel sheets and generate standard ANSI `INSERT` statements to load all 560 financial facts.
- **Query Library**:
  - Developed a query library using CTEs, window functions (`RANK() OVER`), and conditional aggregations to answer all business questions.
  - Optimized queries by joining `Oil_Price_Qtr_Avg` to group by `Oil_Bucket` instead of referencing the fact table directly, matching the conformed star-schema design.

---

## 3. Python Programmatic Pipeline
- **Libraries Used**: `pandas`, `numpy`, `matplotlib`, `seaborn`, `openpyxl`.
- **Data Processing Workflow**:
  - Loaded Excel sheets into Pandas DataFrames.
  - Merged datasets using left joins on `Date_Key`.
  - Classified quarters into `Period_Group` and calculated weighted profit margins.
- **Analytical Outputs**:
  - Saved consolidated query results to CSV tables in the `python/` folder.
- **Visualization Export Configuration**:
  - Generated and saved 4 publication-ready figures to `python/plots/`:
    * `01_operating_margins_ranking.png` (Horizontal bar chart of margins).
    * `02_oil_vs_loss_probability.png` (Dual-axis bucket and line chart).
    * `03_cares_net_vs_operating_gap.png` (Clustered column distortion chart).
    * `04_load_factor_vs_operating_margin.png` (Dual-axis timeline chart of recovery).

---

## 4. Tableau Visualization Pipeline
- **Data Connection**: Created logical relationships on the relationship canvas in Tableau Desktop.
- **Logical Relationships**:
  - Connected `Dim_Time` (Parent) to `Fact_Financials_Master`, `Oil_Price_Qtr_Avg`, and `covid_19_clean_complete` on `Date_Key` with a One-to-Many cardinality.
- **Calculated Fields**:
  - `Weighted Operating Margin` = `SUM([operating_income]) / SUM([operating_revenue])`
  - `Bailout Distortion Gap` = `SUM([net_income]) - SUM([operating_income])`
  - `Period Group` = `IF [Date Key] < 45 THEN "Pre_COVID" ELSEIF [Date Key] <= 50 THEN "COVID_Shock" ELSE "Recovery" END`
- **Worksheet Configuration**:
  - Built 4 separate worksheets (Operating Margin Ranking, WTI loss thresholds dual-axis, CARES act distortion gap, and load factor timeline).
- **Dashboard Layout**:
  - Combined worksheets into a single dashboard layout with synchronized filters for `Period Group` and `Airline Name`.

---

## 5. Power BI Enterprise Pipeline
- **Modeling Tool**: Power BI Desktop.
- **Star Schema Relationships**:
  - Designed the model view with a central conformed dimension `Dim_Time` filtering `Fact_Financials_Master`, `Oil_Price_Qtr_Avg`, and `covid_19_clean_complete` via a One-to-Many (`1:*`) relationship.
- **DAX Layer**:
  - Built calculated columns and measures inside a measures container table:
    * `Weighted Operating Margin = DIVIDE(SUM(Fact_Financials_Master[operating_income]), SUM(Fact_Financials_Master[operating_revenue]), 0)`
    * `Bailout Distortion Gap = SUM(Fact_Financials_Master[net_income]) - SUM(Fact_Financials_Master[operating_income])`
    * `Loss Probability = DIVIDE([Loss Quarters Count], COUNTROWS(Fact_Financials_Master), 0)`
- **Dashboard Layout**:
  - Implemented an interactive single-page canvas matching the corporate color palette with slicers for `Period Group` and `Airline Name`.
