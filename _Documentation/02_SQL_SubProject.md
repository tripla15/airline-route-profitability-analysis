# Phase 2: SQL Implementation Documentation

This document details the database schema design, DDL scripts, data ingestion strategy, and analytical queries executed in the SQL standalone phase of the **Skies Under Pressure** graduation project.

---

## 1. Relational Database Design (Star Schema)

To model the dataset relationally, we designed a Star Schema matching the Power Pivot architecture. The time dimension table (`Dim_Time`) is the conformed parent table, and the other tables are joined to it via foreign keys.

```sql
-- DDL Schema for Skies Under Pressure Database
-- Designed as a Star Schema matching the Power Pivot model configuration

-- 1. Create Dim_Time (Time Dimension)
CREATE TABLE Dim_Time (
    Date_Key INT PRIMARY KEY,
    Year_Quarter VARCHAR(7) UNIQUE NOT NULL,
    Year INT
);

-- 2. Create Oil_Price_Qtr_Avg (Oil Price Data Table)
CREATE TABLE Oil_Price_Qtr_Avg (
    Date_Key INT NOT NULL,
    Oil_Price_Qtr_Avg DECIMAL(10, 4) NOT NULL,
    Oil_Bucket VARCHAR(20) NOT NULL,
    FOREIGN KEY (Date_Key) REFERENCES Dim_Time(Date_Key)
);

-- 3. Create covid_19_clean_complete (Covid Tracker Data Table)
CREATE TABLE covid_19_clean_complete (
    Date_Key INT NOT NULL,
    Covid_US_Cases_Quarterly INT NOT NULL,
    FOREIGN KEY (Date_Key) REFERENCES Dim_Time(Date_Key)
);

-- 4. Create Fact_Financials_Master (Financial Facts Master Table)
CREATE TABLE Fact_Financials_Master (
    Date_Key INT NOT NULL,
    Airline_Name VARCHAR(50) NOT NULL,
    net_income BIGINT NOT NULL,
    load_factor DECIMAL(5, 4) NOT NULL,
    operating_revenue BIGINT NOT NULL,
    operating_income DECIMAL(15, 2) NOT NULL,
    fuel_cost BIGINT NOT NULL,
    CARES_FLAG1 VARCHAR(20) NOT NULL,
    CARES_Flag VARCHAR(20) NOT NULL,
    PRIMARY KEY (Date_Key, Airline_Name),
    FOREIGN KEY (Date_Key) REFERENCES Dim_Time(Date_Key)
);
```

---

## 2. Ingestion & Insertion Strategy

Manually loading Excel data into a relational database can introduce errors and mismatches. To automate this process:
1. We developed a Python ingestion script (`generate_sql_data.py`).
2. The script extracts the cleaned datasets from the active sheets of `Master_Tables_file.xlsx`.
3. It maps fields to the SQL schema, adds missing fields (such as calendar `Year` in the time dimension), and generates a SQL insertion file ([02_insert_data.sql](file:///F:/Engineering%202nd%20year/Extracurriculars/1.%20DEPI/Final%20Project/sql/02_insert_data.sql)) containing 560 ANSI-compliant `INSERT` statements.
4. It compiles and populates a local SQLite database (`skies_under_pressure.db`), enabling immediate testing.

---

## 3. Query Library & Results

We developed an analytical query library using advanced SQL constructs (Common Table Expressions, window functions, and conditional aggregations) to answer the business questions.

### Query 1: Airline Profit Margin Ranking
Ranks the 10 airlines by Weighted Operating Profit Margin (`SUM(operating_income) / SUM(operating_revenue)`):
```sql
SELECT 
    Airline_Name,
    SUM(operating_income) AS Total_Operating_Income,
    SUM(operating_revenue) AS Total_Operating_Revenue,
    (SUM(operating_income) * 1.0 / SUM(operating_revenue)) AS Weighted_Operating_Margin,
    AVG(operating_income * 1.0 / operating_revenue) AS Avg_Quarterly_Operating_Margin,
    RANK() OVER (ORDER BY (SUM(operating_income) * 1.0 / SUM(operating_revenue)) DESC) AS Margin_Rank
FROM Fact_Financials_Master
GROUP BY Airline_Name
ORDER BY Margin_Rank;
```

### Query 2: COVID-19 Operating Income Collapse
Calculates the average quarterly operating income collapse between the pre-COVID baseline and the COVID shock period (`2020-Q1` to `2021-Q2`):
```sql
WITH Period_Averages AS (
    SELECT 
        f.Airline_Name,
        AVG(CASE WHEN t.Year_Quarter < '2020-Q1' THEN f.operating_income END) AS Pre_COVID_Avg,
        AVG(CASE WHEN t.Year_Quarter BETWEEN '2020-Q1' AND '2021-Q2' THEN f.operating_income END) AS COVID_Shock_Avg
    FROM Fact_Financials_Master f
    JOIN Dim_Time t ON f.Date_Key = t.Date_Key
    GROUP BY f.Airline_Name
)
SELECT 
    Airline_Name,
    Pre_COVID_Avg,
    COVID_Shock_Avg,
    (COVID_Shock_Avg - Pre_COVID_Avg) AS COVID_Collapse_Value
FROM Period_Averages
ORDER BY COVID_Collapse_Value ASC;
```

### Query 3: CARES Act Payroll Support distortion gap
Exposes the bailout distortion gap by comparing Average Net Income vs. Average Operating Income during the CARES period:
```sql
SELECT 
    Airline_Name,
    AVG(net_income) AS Avg_Net_Income,
    AVG(operating_income) AS Avg_Operating_Income,
    AVG(net_income - operating_income) AS Bailout_Distortion_Gap,
    RANK() OVER (ORDER BY AVG(net_income - operating_income) DESC) AS Distortion_Rank
FROM Fact_Financials_Master
WHERE CARES_Flag = 'CARES_Period'
GROUP BY Airline_Name
ORDER BY Distortion_Rank;
```

### Query 4: Oil Price Loss Thresholds
Calculates the frequency of loss quarters (operating income < 0) across WTI crude oil price buckets:
```sql
SELECT 
    o.Oil_Bucket,
    COUNT(CASE WHEN f.operating_income < 0 THEN 1 END) AS Loss_Quarters,
    COUNT(*) AS Total_Quarters,
    (COUNT(CASE WHEN f.operating_income < 0 THEN 1 END) * 1.0 / COUNT(*)) AS Loss_Probability,
    AVG(f.operating_income) AS Avg_Operating_Income
FROM Fact_Financials_Master f
JOIN Oil_Price_Qtr_Avg o ON f.Date_Key = o.Date_Key
GROUP BY o.Oil_Bucket
ORDER BY 
    CASE o.Oil_Bucket
        WHEN 'Below_50' THEN 1
        WHEN '50_to_80' THEN 2
        WHEN '80_to_100' THEN 3
        WHEN '100_Plus' THEN 4
    END;
```

*Results Summary*: Run against the database, Query 1 ranks Allegiant first (11.73% margin) and American last (0.77%). Query 4 demonstrates that the highest probability of loss (33.08%) occurs when WTI prices drop below $50/bbl, correlating with global economic recessions.
