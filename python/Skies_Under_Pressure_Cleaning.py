import os
import pandas as pd

script_dir = os.path.dirname(os.path.abspath(__file__))
raw_oil = pd.read_csv(os.path.join(script_dir, "..", "Raw Data", "crude-oil-price.csv"))
raw_covid = pd.read_csv(os.path.join(script_dir, "..", "Raw Data", "covid_19_clean_complete.csv"))

raw_oil['date'] = pd.to_datetime(raw_oil['date'])
oil_filtered = raw_oil[(raw_oil['date'].dt.year >= 2009) & (raw_oil['date'].dt.year <= 2022)].copy()
oil_filtered['Year_Quarter'] = oil_filtered['date'].dt.year.astype(str) + "-Q" + oil_filtered['date'].dt.quarter.astype(str)
oil_processed = oil_filtered.groupby('Year_Quarter')['price'].mean().reset_index()
oil_processed.columns = ['Year_Quarter', 'Oil_Price_Qtr_Avg']

raw_covid['Date'] = pd.to_datetime(raw_covid['Date'])
covid_us = raw_covid[raw_covid['Country/Region'] == 'US'].copy()
covid_us['Year_Quarter'] = covid_us['Date'].dt.year.astype(str) + "-Q" + covid_us['Date'].dt.quarter.astype(str)
covid_processed = covid_us.groupby('Year_Quarter')['Confirmed'].max().reset_index()
covid_processed.columns = ['Year_Quarter', 'COVID_US_Qtr_Cases']

oil_processed.to_excel(os.path.join(script_dir, "..", "Excel", "Processed Data", "Oil_Qtr.xlsx"), index=False)
covid_processed.to_excel(os.path.join(script_dir, "..", "Excel", "Processed Data", "Covid_US_Cases_Quarter.xlsx"), index=False)

print("Data preprocessing completed successfully!")
