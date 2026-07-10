Create database Covid_airline_crise;

use covid_airline_crise;
set sql_safe_updates =0;

# ========================fact_covid table preprocessing=========================

ALTER TABLE fact_covid
ADD COLUMN Date_clean DATE NULL;

UPDATE fact_covid
SET Date_clean = STR_TO_DATE(`Date`, '%m/%d/%Y');

ALTER TABLE fact_covid
DROP COLUMN `Date`;

ALTER TABLE fact_covid
CHANGE COLUMN Date_clean `Date` DATE NOT NULL;

ALTER TABLE fact_covid
Rename column Date_clean to Date;

alter table fact_covid
add column Qtr int not null;

update fact_covid
set Qtr = quarter(Date);

alter table fact_covid
add column Year_Qtr varchar(7) not null ;

update fact_covid
set Year_Qtr = concat( year(Date) , '-Q' , Qtr);

# put Country name in State records if State records are empty.
UPDATE fact_covid
SET State = Country
WHERE State ='';

alter table fact_covid
drop column lat, 
drop column `Long`,
drop column Deaths,
drop column Recovered,
drop column Active,
drop column `WHO Region`,
drop column Date,
drop column Qtr,
drop column State;

ALTER TABLE fact_covid
RENAME COLUMN `Country/Region` TO `Country`,
RENAME COLUMN `Provance/State` TO `State`;

alter table fact_covid
modify column Country varchar(35);

Alter table fact_covid 
add column id int auto_increment not null primary key;

DELETE FROM fact_covid
WHERE id NOT IN (
    SELECT id
    FROM (
        SELECT id,
               ROW_NUMBER() OVER (
                   PARTITION BY Year_Qtr
                   ORDER BY Confirmed DESC
               ) AS rn
        FROM fact_covid
    ) t
    WHERE rn = 1
);

Alter table fact_covid 
drop column id;

Alter table fact_covid 
drop column Country;

#===================================================================
#==============fact_oil_price table preprocessing==================

alter table fact_oil_price
drop column percentChange,
drop column `change`,
modify column `date` Date,
add column Year_Qtr varchar(7),
modify column price decimal(15,2);

update fact_oil_price
set Year_Qtr = concat(year(date) , '-Q' , quarter(date));

alter table fact_oil_price
drop column `date`;

alter table fact_oil_price
add column id int not null auto_increment primary key;

UPDATE fact_oil_price c
JOIN (
    SELECT
        Year_Qtr,
        AVG(Price) AS AvgPrice,
        MIN(id) AS FirstID
    FROM fact_oil_price
    GROUP BY Year_Qtr
) t
ON c.id = t.FirstID
SET c.Price = t.AvgPrice;

DELETE c
FROM fact_oil_price c
JOIN (
    SELECT
        Year_Qtr,
        MIN(id) AS FirstID
    FROM fact_oil_price
    GROUP BY Year_Qtr
) t
ON c.Year_Qtr = t.Year_Qtr
WHERE c.id <> t.FirstID;

alter table fact_oil_price
drop column id;

#===================================================================
#=================fact_bts table preprocessing======================

alter table fact_bts
rename column fuel_cost to Fuel_cost,
rename column operating_revenue to Operating_revenue,
rename column operating_income to Operating_income,
rename column load_factor to Load_factor,
rename column net_income to Net_income,
rename column Airline_Name to Airline_name,
rename column ﻿Year_Quarter to Year_Qtr,
modify column Year_Qtr varchar(7),
modify column Airline_Name varchar(20),
modify column load_factor decimal(6,2),
modify column operating_income int ;

update fact_bts
set fuel_cost = fuel_cost/1000;


#===================================================================
#=================Creating Dim_date table======================



CREATE TABLE dim_date (
    Date_Key INT AUTO_INCREMENT PRIMARY KEY,
    Year_Qtr VARCHAR(7) NOT NULL,
    Year INT NOT NULL
);

INSERT INTO dim_date (Year_Qtr, Year)
SELECT CONCAT(y.Year, '-Q', q.Qtr) AS Year_Qtr,
       y.Year
FROM
(
    SELECT 2009 AS Year UNION ALL
    SELECT 2010 UNION ALL
    SELECT 2011 UNION ALL
    SELECT 2012 UNION ALL
    SELECT 2013 UNION ALL
    SELECT 2014 UNION ALL
    SELECT 2015 UNION ALL
    SELECT 2016 UNION ALL
    SELECT 2017 UNION ALL
    SELECT 2018 UNION ALL
    SELECT 2019 UNION ALL
    SELECT 2020 UNION ALL
    SELECT 2021 UNION ALL
    SELECT 2022
) y
CROSS JOIN
(
    SELECT 1 AS Qtr UNION ALL
    SELECT 2 UNION ALL
    SELECT 3 UNION ALL
    SELECT 4
) q
ORDER BY y.Year, q.Qtr;

#============================================================
#===========Add Date_fact Column for each fact table=========

ALTER TABLE fact_bts
ADD COLUMN Date_Key INT;

ALTER TABLE fact_covid
ADD COLUMN Date_Key INT;

ALTER TABLE fact_oil_price
ADD COLUMN Date_Key INT;

#========================================================================
#===========join fact tables on dim_date to fill date_key column=========

UPDATE fact_bts f
JOIN dim_date d
ON f.Year_Qtr = d.Year_Qtr
SET f.Date_Key = d.Date_Key;

UPDATE fact_covid f
JOIN dim_date d
ON f.Year_Qtr = d.Year_Qtr
SET f.Date_Key = d.Date_Key;

UPDATE fact_oil_price f
JOIN dim_date d
ON f.Year_Qtr = d.Year_Qtr
SET f.Date_Key = d.Date_Key;

#========================================================================
#=================Delete Year_Qtr column from all fact tables============

ALTER TABLE fact_bts
DROP COLUMN Year_Qtr;

ALTER TABLE fact_covid
DROP COLUMN Year_Qtr;

ALTER TABLE fact_oil_price
DROP COLUMN Year_Qtr;

#========================================================================
#=====================Establish foreign key constraints==================

ALTER TABLE fact_bts
ADD CONSTRAINT FK_fact_bts_date
FOREIGN KEY (Date_Key)
REFERENCES dim_date(Date_Key);


ALTER TABLE fact_covid
ADD CONSTRAINT FK_fact_covid_date
FOREIGN KEY (Date_Key)
REFERENCES dim_date(Date_Key);


ALTER TABLE fact_oil_price
ADD CONSTRAINT FK_fact_oil_price_date
FOREIGN KEY (Date_Key)
REFERENCES dim_date(Date_Key);

#========================================================================
#===========================Showing tables===============================

select * from dim_date;
select * from fact_bts;
select * from fact_covid;
select * from fact_oil_price;

#========================================================================
#===========================Analytical queries===========================

#==================1.Average Quarterly Operating Income==================
SELECT Cares_flag , ROUND(AVG(Operating_income),2) AS Avg_Operating_Income
FROM fact_bts

GROUP BY Cares_flag;

#==================2.Recovery Profile: Annual Income vs Revenue==================
SELECT
    d.Year,
    SUM(b.Operating_income) AS Total_Operating_Income,
    SUM(b.Operating_revenue) AS Total_Operating_Revenue
FROM fact_bts b
JOIN dim_date d
ON b.Date_key = d.Date_key
where d.Year between '2018' and '2022'
GROUP BY d.Year
ORDER BY d.Year;

#======================3.Operating Revenue for Airlines=========================
SELECT
    Airline_name,
    SUM(Operating_revenue) AS Total_Operating_Revenue
FROM fact_bts
GROUP BY Airline_name
ORDER BY Total_Operating_Revenue DESC;


#===========================4.Average Load Factor by Airline===========================

SELECT
    Airline_name,
    ROUND(AVG(Load_factor),2) AS Avg_Load_Factor
FROM fact_bts
GROUP BY Airline_name
ORDER BY Avg_Load_Factor DESC;

#===========================5.Average Fuel Cost by Year===========================

SELECT
    d.Year,
    ROUND(AVG(b.Fuel_cost),2) AS Avg_Fuel_Cost
FROM fact_bts b
JOIN dim_date d
ON b.Date_key = d.Date_key
GROUP BY d.Year
ORDER BY d.Year;

#===========================6.Total Confirmed COVID Cases===========================

SELECT
    d.Year,
    SUM(c.Confirmed) AS Total_Confirmed_Cases
FROM fact_covid c
JOIN dim_date d
ON c.Date_key = d.Date_key
GROUP BY d.Year
ORDER BY d.Year;

#===========================7.Top Airline by Net Income===========================

SELECT
    Airline_name,
    SUM(Net_income) AS Total_Net_Income
FROM fact_bts
GROUP BY Airline_name
ORDER BY Total_Net_Income DESC;

#===========================8.Top Year_Qtr by total revenue===========================

SELECT
    d.Year_Qtr,
    SUM(b.Operating_revenue) AS Total_Revenue
FROM fact_bts b
JOIN dim_date d
ON b.Date_key = d.Date_key
GROUP BY d.Year_Qtr
ORDER BY Total_Revenue DESC;