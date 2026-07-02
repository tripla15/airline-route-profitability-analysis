# SQL Sub-Project Directory

This folder contains the complete relational database implementation, schema definition scripts, data injection procedures, and core business queries.

## Database Engine
* **Engine:** SQLite 3
* **Database File:** `skies_under_pressure.db`

## Script Manifest

### 1. `01_schema_ddl.sql`
Defines the relational database structure, primary and foreign key constraints, and index settings:
* **`Fact_Financials_Master`:** The core transactional table.
* **`Dim_Time`:** Calendar dimension.
* **`Dim_Airlines`:** Carrier reference dimension.
* **`Dim_Oil` & `Dim_Covid`:** Macro variable dimensions.

### 2. `02_insert_data.sql`
Populates the relational schema with records mapped from our cleaned datasets.

### 3. `03_business_queries.sql`
Contains the SQL queries answering the 7 core analytical questions:
* **Q1:** Overall airline margin ranking.
* **Q2:** Industry performance breakdown by period (Pre vs. Shock vs. Recovery).
* **Q3:** Oil price spikes vs. fuel expense ratios.
* **Q4:** CARES Act policy distortion tracking.
* **Q5:** Quarters required to reach post-pandemic profitability.
* **Q6:** Oil price bucket loss probability calculation.
* **Q7:** Correlation-analog query linking macro shifts to margin changes.

---

## How to Execute
To rebuild the database and run queries:
```bash
# 1. Initialize schema and load data
sqlite3 skies_under_pressure.db < 01_schema_ddl.sql
sqlite3 skies_under_pressure.db < 02_insert_data.sql

# 2. Execute business queries
sqlite3 skies_under_pressure.db < 03_business_queries.sql
```
