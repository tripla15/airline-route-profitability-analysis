# Skies Under Pressure: Graduation Project Overview

**Project Name**: Skies Under Pressure: Aviation Profitability vs. Global Macro-Shocks  
**Target Scope**: The Core 10 US Passenger Airlines over a 14-year timeline (2009 to 2022).  
**Airlines Tracked**: Delta Air Lines, United Airlines, American Airlines, Southwest Airlines, JetBlue Airways, Alaska Airlines, Spirit Airlines, Frontier Airlines, Hawaiian Airlines, and Allegiant Air.  

---

## 1. Core Objective & Business Logic

This graduation project builds a multi-layered analytical model to study how external macroeconomic shocks dictate the survival and efficiency of the US aviation sector. Instead of viewing financial performance in isolation, it maps cause-and-effect relationships between:
1. **The Supply Shock**: Global Crude Oil Prices acting as the trigger for jet fuel cost volatility.
2. **The Demand Shock**: US COVID-19 Cases representing the black-swan event that collapsed travel demand.
3. **The Financial Reality**: Bureau of Transportation Statistics (Fact Sheet) data measuring the mathematical fallout on corporate revenue, operating margins, and load factors.

### Ironclad Business Logic & Structural Rules:
- **The Master Grain (Year_Quarter)**: Every single dataset was strictly aggregated to the `Year_Quarter` and `Airline_Name` level (e.g., `2020-Q3`). Daily or monthly records were blocked from final analytical views to prevent false precision and duplicate row explosions during joins.
- **The CARES Act Catch**: Between `2020-Q2` and `2021-Q2`, the US government gave airlines billions in bailouts under the Payroll Support Program (PSP), which artificially inflated `net_income` (reported as non-operating income). Therefore, **`operating_income` is strictly used as the primary metric** to track true crisis damage, with `net_income` used only to expose the bailout illusion.
- **The Unified Standalone Architecture**: The project requires 5 completely isolated deliverables (Excel, SQL, Python, Tableau, and Power BI). Each tool independently processes the core pipelines from raw extraction to final dashboard presentation.

---

## 2. Real Challenges Faced & Executive Decisions Made

### Challenge 1: The Skytrax Granularity & Scope Retreat
* **The Reality**: The team initially attempted a 4-pillar architecture including passenger satisfaction reviews (Skytrax). However, the raw data was heavily skewed toward international carriers. After applying filters for the 10 US airlines and the 2009–2022 timeline, the dataset collapsed to practically zero usable rows.
* **The Decision**: An executive decision was made to drop the Skytrax dataset entirely. This eliminated data engineering bottlenecks (text-parsing anomalies and locale translation mismatches) and reframed the project as a pure macroeconomic financial analysis.

### Challenge 2: The "BTS Subtotal & Region" Trap
* **The Reality**: The raw US Government BTS portal inserted automatic "TOTAL" rows for every year and split data across regional columns (Domestic, Latin America, Atlantic). If loaded directly, the math would have double-counted every quarter.
* **The Decision**: In Excel, the `Quarter` column was filtered to remove "TOTAL" rows (keeping only 1, 2, 3, 4) and regional columns were deleted to preserve only the final total column.

### Challenge 3: The Load Factor Math Failure
* **The Reality**: Because Load Factor is a percentage, the BTS left the `TOTAL` column completely blank in the raw files (since adding percentages mathematically breaks).
* **The Decision**: The team performed a rescue operation by pulling the raw Load Factor files again, isolating the `DOMESTIC` column, converting it to a Decimal Number, and using the `Average` function to safely compress 3 monthly percentages into 1 quarterly percentage.

### Challenge 4: The Financial Null Replacement Trap
* **The Reality**: Columns like `Ancillary_Revenue`, `Catering_Cost`, and `Handling_Cost` had null values. Standard data science practices suggest replacing nulls with the median, but doing so would have fabricated fake revenue/expenses and broken the `Total_Cost` summations.
* **The Decision**: Nulls in transactional financial columns were replaced with `0` to protect the accounting integrity of the dataset.

### Challenge 5: Operating Income & Fuel Cost Monthly Duplication
* **The Reality**: The BTS data for Operating Income and Fuel Cost contained three rows per quarter because airlines reported fuel purchases and operating income monthly. Merging this directly caused a massive duplicate row explosion (from 120 rows to 1,354 rows).
* **The Decision**: The data was aggregated using a `Group By` function on `Airline_Name` and `Year_Quarter`, using the `Sum` operation to combine the monthly expenditures into a single quarterly total before merging.

### Challenge 6: The Power Query "Pivot Trap"
* **The Reality**: When attempting to pivot the financial data from a "Long" to a "Wide" format for SQL, Power Query scattered metrics diagonally across different lines and filled the rest with nulls.
* **The Decision**: The team enforced the strict "Rule of Four". Before pivoting, the table was stripped down to exactly four columns: `Airline_Name`, `Year_Quarter`, `Metric_Name`, and `Metric_Value`. The pivot was executed using **Don't Aggregate** as a tripwire to catch duplicates.

---

## 3. The Database Design (Star Schema Architecture)

To prevent ambiguous loops, Cartesian products, or inflated values, fact tables are never connected directly to each other. The database relies on a strict hub-and-spoke configuration:

### Dimension Tables:
- **`Dim_Time` (or `dim_date_quarter`)**: The universal central bridge. A single-column lookup table containing a continuous list of all 56 quarters (2009-Q1 to 2022-Q4). It holds the `CARES_Flag` (1 or 0) to centrally manage bailout highlighting.
- **`Dim_Airline`**: A canonical lookup table standardizing airline identities (e.g., matching "Delta Air Lines Inc." to "Delta Airlines") to enforce referential integrity.

### Fact Tables (Connected via One-to-Many Relationships):
- **`Fact_Financials`**: The wide master table containing one unique row per airline per quarter. Contains `net_income`, `load_factor`, `operating_revenue`, `operating_income`, `fuel_cost`, and `CARES_FLAG1`.
- **`Fact_Crude_Oil`**: Aggregated to exactly one row per quarter containing `Oil_Price_Qtr_Avg` and `Oil_Bucket`.
- **`Fact_COVID_US`**: Aggregated into quarterly totals containing `Covid_US_Cases_Quarterly`.
