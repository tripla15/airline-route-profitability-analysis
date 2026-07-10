# Phase 2: SQL Implementation Documentation

This document details the database schema design, DDL scripts, data ingestion strategy, and analytical queries executed in the SQL standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Relational Database Design (Star Schema)

To model the dataset relationally, we designed a Star Schema matching the Power Pivot architecture. The conformed time dimension table (`dim_date`) is the conformed parent table, and the other tables are joined to it via foreign keys.

```sql
-- DDL Schema for Skies Under Pressure Database
-- Designed as a Star Schema matching the Power Pivot model configuration in MySQL

-- 1. Create dim_date (Conformed Calendar Dimension)
CREATE TABLE dim_date (
    Date_Key INT AUTO_INCREMENT PRIMARY KEY,
    Year_Qtr VARCHAR(7) NOT NULL,
    Year INT NOT NULL
);

-- 2. Create fact_bts (Financial Fact Table)
CREATE TABLE fact_bts (
    Date_Key INT,
    Airline_name VARCHAR(50) NOT NULL,
    Fuel_cost BIGINT,
    Operating_revenue BIGINT,
    Operating_income INT,
    Load_factor DECIMAL(6,2),
    Net_income INT,
    Cares_flag VARCHAR(20) NOT NULL,
    FOREIGN KEY (Date_Key) REFERENCES dim_date(Date_Key)
);

-- 3. Create fact_covid (COVID-19 Tracker Fact Table)
CREATE TABLE fact_covid (
    Date_Key INT,
    Confirmed INT NOT NULL,
    FOREIGN KEY (Date_Key) REFERENCES dim_date(Date_Key)
);

-- 4. Create fact_oil_price (Oil Price Fact Table)
CREATE TABLE fact_oil_price (
    Date_Key INT,
    Price DECIMAL(15,2),
    FOREIGN KEY (Date_Key) REFERENCES dim_date(Date_Key)
);
```

---

## 2. Ingestion & Preprocessing Strategy

The data loading pipeline is handled programmatically in SQL to prepare raw data for queries:
1.  **Date Formatting:** Dates in the raw CSV files are converted from string formats using `STR_TO_DATE(..., '%m/%d/%Y')`.
2.  **Date Dimension Generation:** The `dim_date` table is populated dynamically by cross-joining Year and Quarter tables from 2009 to 2022.
3.  **Aggregation Grain:** Daily COVID-19 confirmed cases are filtered for the US and aggregated to quarterly maximums using window functions (`ROW_NUMBER() OVER (PARTITION BY Year_Qtr ORDER BY Confirmed DESC)`). Monthly WTI crude oil prices are aggregated to quarterly averages using `AVG(Price)`.
4.  **Relationship Mapping:** All tables are joined on `Year_Qtr` to fill the conformed `Date_Key`, then the text quarter columns are dropped, and foreign key constraints are established.

---

## 3. Query Library & Results

We developed an analytical query library containing 8 business queries using SQL window functions, CTEs, and conditional aggregations to validate our project metrics.

### Query 1: Average Quarterly Operating Income (CARES vs Normal)
Compares average quarterly operating incomes across CARES bailout and normal periods:
```sql
SELECT Cares_flag , ROUND(AVG(Operating_income),2) AS Avg_Operating_Income
FROM fact_bts
GROUP BY Cares_flag;
```

### Query 2: Recovery Profile: Annual Income vs Revenue (2018-2022)
Tracks annual totals to evaluate the pandemic shock and subsequent recovery window:
```sql
SELECT
    d.Year,
    SUM(b.Operating_income) AS Total_Operating_Income,
    SUM(b.Operating_revenue) AS Total_Operating_Revenue
FROM fact_bts b
JOIN dim_date d ON b.Date_key = d.Date_key
WHERE d.Year BETWEEN '2018' AND '2022'
GROUP BY d.Year
ORDER BY d.Year;
```

### Query 3: Operating Revenue for Airlines
Ranks the 10 airlines based on total operating revenues descending:
```sql
SELECT
    Airline_name,
    SUM(Operating_revenue) AS Total_Operating_Revenue
FROM fact_bts
GROUP BY Airline_name
ORDER BY Total_Operating_Revenue DESC;
```

### Query 4: Average Load Factor by Airline
Ranks airlines based on passenger capacity utilization:
```sql
SELECT
    Airline_name,
    ROUND(AVG(Load_factor),2) AS Avg_Load_Factor
FROM fact_bts
GROUP BY Airline_name
ORDER BY Avg_Load_Factor DESC;
```

### Query 5: Average Fuel Cost by Year
Extracts the historical annual fuel expense averages:
```sql
SELECT
    d.Year,
    ROUND(AVG(b.Fuel_cost),2) AS Avg_Fuel_Cost
FROM fact_bts b
JOIN dim_date d ON b.Date_key = d.Date_key
GROUP BY d.Year
ORDER BY d.Year;
```

### Query 6: Total Confirmed COVID Cases
Tracks annual US cumulative COVID case counts:
```sql
SELECT
    d.Year,
    SUM(c.Confirmed) AS Total_Confirmed_Cases
FROM fact_covid c
JOIN dim_date d ON c.Date_key = d.Date_key
GROUP BY d.Year
ORDER BY d.Year;
```

### Query 7: Top Airline by Net Income
Ranks airlines by their total cumulative net income:
```sql
SELECT
    Airline_name,
    SUM(Net_income) AS Total_Net_Income
FROM fact_bts
GROUP BY Airline_name
ORDER BY Total_Net_Income DESC;
```

### Query 8: Top Year_Qtr by Total Revenue
Finds the highest-performing quarters in history based on total revenue:
```sql
SELECT
    d.Year_Qtr,
    SUM(b.Operating_revenue) AS Total_Revenue
FROM fact_bts b
JOIN dim_date d ON b.Date_key = d.Date_key
GROUP BY d.Year_Qtr
ORDER BY Total_Revenue DESC;
```
