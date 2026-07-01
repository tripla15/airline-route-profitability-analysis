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
