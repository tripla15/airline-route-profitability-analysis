-- ==============================================================================
-- SQL Analytical Query Library — Skies Under Pressure
-- Standard SQL queries answering the 7 relevant project business questions
-- Updated to match the Excel Power Pivot logical names exactly
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- QUESTION 1: Operating Profit Margin Ranking
-- Which US passenger airlines had the highest operating profit margins?
-- Calculates the weighted operating profit margin and averages for the entire period.
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- QUESTION 2: Oil Price Shock Impact on Profitability
-- Summarizes operating outcomes and oil prices by crude oil market price bucket.
-- ------------------------------------------------------------------------------
SELECT 
    o.Oil_Bucket,
    COUNT(f.Date_Key) AS Total_Quarters,
    AVG(o.Oil_Price_Qtr_Avg) AS Avg_WTI_Price,
    SUM(f.operating_income) AS Total_Operating_Profit,
    AVG(f.operating_income) AS Avg_Quarterly_Operating_Income
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


-- ------------------------------------------------------------------------------
-- QUESTION 3: COVID-19 Damage to Operating Income
-- Compares average operating income before COVID vs. during the COVID shock.
-- Shows the delta (collapse value) ranked from deepest collapse to least.
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- QUESTION 4: CARES Act Distortion Check
-- Did government bailouts hide true operational losses during the crisis?
-- Compares Net Income vs. Operating Income during the CARES period (2020-Q2 to 2021-Q2).
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- QUESTION 5: COVID Financial Recovery Speed
-- Identifies the earliest quarter starting 2020-Q2 where each airline's operating margin became positive.
-- ------------------------------------------------------------------------------
WITH Chronological_Post_Shock AS (
    SELECT 
        f.Airline_Name,
        t.Year_Quarter,
        f.operating_income,
        ROW_NUMBER() OVER (PARTITION BY f.Airline_Name ORDER BY f.Date_Key) AS rn
    FROM Fact_Financials_Master f
    JOIN Dim_Time t ON f.Date_Key = t.Date_Key
    WHERE f.Date_Key >= 46 AND f.operating_income > 0  -- Date_Key 46 corresponds to 2020-Q2
)
SELECT 
    f.Airline_Name,
    COALESCE(c.Year_Quarter, 'Did not recover by 2022') AS First_Positive_Quarter
FROM (SELECT DISTINCT Airline_Name FROM Fact_Financials_Master) f
LEFT JOIN Chronological_Post_Shock c ON f.Airline_Name = c.Airline_Name AND c.rn = 1
ORDER BY 
    CASE WHEN First_Positive_Quarter = 'Did not recover by 2022' THEN 1 ELSE 0 END,
    First_Positive_Quarter ASC;


-- ------------------------------------------------------------------------------
-- QUESTION 6: Oil Price Loss Thresholds
-- Calculates the loss probability (share of quarters with negative operating income)
-- across WTI crude oil price buckets.
-- ------------------------------------------------------------------------------
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


-- ------------------------------------------------------------------------------
-- QUESTION 7: Load Factor vs Financial Recovery
-- Compares capacity utilization (load factor) and operating margins across three main time periods:
-- Pre-COVID (pre-2020), COVID-Shock (2020-Q1 to 2021-Q2), and Recovery (post-2021-Q2).
-- ------------------------------------------------------------------------------
WITH Categorized_Periods AS (
    SELECT 
        f.Airline_Name,
        f.load_factor,
        (f.operating_income * 1.0 / f.operating_revenue) AS operating_margin,
        CASE 
            WHEN t.Year_Quarter < '2020-Q1' THEN 'Pre_COVID'
            WHEN t.Year_Quarter BETWEEN '2020-Q1' AND '2021-Q2' THEN 'COVID_Shock'
            ELSE 'Recovery'
        END AS Period_Group
    FROM Fact_Financials_Master f
    JOIN Dim_Time t ON f.Date_Key = t.Date_Key
)
SELECT 
    Airline_Name,
    Period_Group,
    AVG(load_factor) AS Avg_Load_Factor,
    AVG(operating_margin) AS Avg_Operating_Margin
FROM Categorized_Periods
GROUP BY Airline_Name, Period_Group
ORDER BY Airline_Name, 
    CASE Period_Group
        WHEN 'Pre_COVID' THEN 1
        WHEN 'COVID_Shock' THEN 2
        WHEN 'Recovery' THEN 3
    END;
