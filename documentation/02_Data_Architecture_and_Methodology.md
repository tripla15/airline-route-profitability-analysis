# Stage 2: Data Architecture and Methodology — Skies Under Pressure

To support consistent results across Excel, SQL, Python, Tableau, and Power BI, the project's data architecture is structured as a conformed Star Schema. This design resolves grain mismatches by aggregating all datasets to a unified quarterly grain before executing joins, eliminating row-multiplication errors.

---

## 1. Relational Database Dictionary

### Table 1: `Dim_Time` (Conformed Time Dimension)
Serves as the Single Source of Truth (SSoT) for time fields. It maps sequential integers to standard quarters.

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `Date_Key` | `INTEGER` | `PRIMARY KEY` | Surrogate time key mapping chronologically from 1 to 56. |
| `Year_Quarter` | `VARCHAR(7)` | `UNIQUE`, `NOT NULL` | Time label formatted as `YYYY-Q#` (e.g., `2020-Q2`). |
| `Year` | `INTEGER` | `NOT NULL` | Calendar year extracted from the quarter label (e.g., `2020`). |

### Table 2: `Oil_Price_Qtr_Avg` (Oil Price Data Table)
Contains quarterly averages of West Texas Intermediate (WTI) Crude Oil spot prices.

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `Date_Key` | `INTEGER` | `FOREIGN KEY`, `NOT NULL` | References `Dim_Time(Date_Key)`. |
| `Oil_Price_Qtr_Avg`| `DECIMAL(10, 4)`| `NOT NULL` | Unweighted average WTI spot price per barrel during the quarter. |
| `Oil_Bucket` | `VARCHAR(20)` | `NOT NULL` | Category grouping: `Below_50`, `50_to_80`, `80_to_100`, `100_Plus`. |

### Table 3: `covid_19_clean_complete` (COVID-19 Case Tracker)
Tracks the scale of the pandemic in the United States.

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `Date_Key` | `INTEGER` | `FOREIGN KEY`, `NOT NULL` | References `Dim_Time(Date_Key)`. |
| `Covid_US_Cases_Quarterly`| `INTEGER`| `NOT NULL` | Maximum cumulative confirmed US cases recorded at the quarter's end. |

### Table 4: `Fact_Financials_Master` (Financial Facts Master Table)
Stores quarterly financial and operational records for the 10 target US carriers.

| Column Name | Data Type | Constraint | Description |
|---|---|---|---|
| `Date_Key` | `INTEGER` | `FOREIGN KEY`, `NOT NULL` | Part of Composite PK. References `Dim_Time(Date_Key)`. |
| `Airline_Name` | `VARCHAR(50)` | `NOT NULL` | Part of Composite PK. Standardized airline name. |
| `net_income` | `BIGINT` | `NOT NULL` | Corporate net profit/loss (includes non-operating bails). |
| `load_factor` | `DECIMAL(5, 4)` | `NOT NULL` | Capacity utilization ratio (seats filled / seats available). |
| `operating_revenue` | `BIGINT` | `NOT NULL` | Total revenue generated from passenger and cargo operations. |
| `operating_income` | `DECIMAL(15, 2)`| `NOT NULL` | Operating Profit/Loss (revenue minus operating costs). |
| `fuel_cost` | `BIGINT` | `NOT NULL` | Total expenditure on aviation jet fuel during the quarter. |
| `CARES_FLAG1` | `VARCHAR(20)` | `NOT NULL` | Identifier: `CARES_Period` (2020-Q2 to 2021-Q2) or `Normal_Period`. |
| `CARES_Flag` | `VARCHAR(20)` | `NOT NULL` | Duplicate flag for Power Pivot compatibility. |

---

## 2. Preprocessing & Data Cleaning Workflows

### WTI Crude Oil Price Consolidation
Raw daily spot prices from the Energy Information Administration (EIA) contained trading-day gaps (weekends and federal holidays). We calculated an unweighted quarterly average:
$$\text{Oil\_Price\_Qtr\_Avg} = \frac{1}{N}\sum_{i=1}^{N} \text{Daily\_Price}_i$$
Where $N$ represents the active trading days in each quarter. The resulting values were categorized into logical buckets to identify operational break points:
- **`Below_50`**: WTI price $< \$50$/barrel.
- **`50_to_80`**: WTI price $\ge \$50$/barrel and $< \$80$/barrel (historical operating sweet spot).
- **`80_to_100`**: WTI price $\ge \$80$/barrel and $< \$100$/barrel (elevated fuel cost pressure).
- **`100_Plus`**: WTI price $\ge \$100$/barrel (severe energy shock).

### US COVID-19 Case Aggregation
The raw Johns Hopkins University dataset tracks daily cumulative confirmed cases. Because cases are cumulative, summing them quarterly would multiply the numbers incorrectly. Instead, we captured the maximum snapshot value at the end of each quarter:
$$\text{Covid\_US\_Cases\_Quarterly} = \max_{t \in \text{Quarter}} (\text{Cumulative\_Cases}_t)$$
This captures the cumulative scale of the pandemic at the close of each quarter. Quarters before `2020-Q1` are set to `0`.

### BTS Financial Cleaning
Form 41 Schedule P-12 reports from the Bureau of Transportation Statistics required significant cleaning:
- **Carrier Standardizing**: Resolved naming inconsistencies (e.g. mapping "Delta Air Lines Inc." and "Delta Airlines" to a single string: "Delta Airlines").
- **Airline Filtering**: Filtered out regional partners and international carriers to isolate the 10 target domestic passenger airlines.
- **Metric Normalization**: Checked that financial metrics were reported in absolute dollar values and load factors were standard ratios.

---

## 3. The CARES Act Payroll Support Program (PSP) Policy Distortion

During the COVID-19 pandemic, the US Congress enacted the CARES Act, establishing the Payroll Support Program (PSP) to prevent a collapse of the commercial aviation sector. Under PSP I, II, and III, the federal government provided approximately **$54 billion** in direct payroll support to US passenger airlines between April 2020 and October 2021.

### Accounting Classification & Net Income Distortion
In corporate financial reporting, these federal relief funds were classified as **non-operating income** (specifically, government grants). Consequently:
- **Net Income** includes these non-operating grants. The influx of federal cash offset operational losses on paper, making severely distressed airlines look financially stable.
- **Operating Income (Operating Profit/Loss)** is calculated as:
  $$\text{Operating Income} = \text{Operating Revenue} - \text{Operating Expenses}$$
  Because operating expenses include payroll costs, but operating revenue excludes the government grants, this metric isolates the carrier's actual operational performance.

To evaluate true baseline performance during the crisis, this study creates a **`CARES_Flag`** column marking quarters from **`2020-Q2`** to **`2021-Q2`** as `CARES_Period`. We designate **`Operating Income`** as the primary performance metric, while **`Net Income`** is used only to measure the bailout distortion gap:
$$\text{Bailout Distortion Gap} = \text{Net Income} - \text{Operating Income}$$
A large positive gap shows where government support hid operational losses, which is critical for an honest evaluation of carrier performance during the pandemic.
