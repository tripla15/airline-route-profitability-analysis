# Raw Data Directory

This folder contains the unprocessed, raw datasets representing global macroeconomic shock variables used in this study. 

## Files Included

### 1. `crude-oil-price.csv`
* **Source:** U.S. Energy Information Administration (EIA) / Our World in Data.
* **Granularity:** Monthly average spot prices of West Texas Intermediate (WTI) Crude Oil (measured in USD per barrel).
* **Time Horizon:** 2009–2022.
* **Fields:**
  * `Entity`, `Code`, `Year`: Metadata labels.
  * `WTI Crude Oil Price (USD/bbl)`: The monthly average price index.

### 2. `covid_19_clean_complete.csv`
* **Source:** Johns Hopkins University Center for Systems Science and Engineering (CSSE) COVID-19 Data Repository.
* **Granularity:** Daily cumulative case tracking records for the United States.
* **Time Horizon:** 2020-01-22 to 2022-12-31.
* **Fields:**
  * `Date`: Day of recording.
  * `Cases`: Cumulative count of positive COVID-19 cases in the US.

---

## Processing Workflow
These files serve as the raw inputs for our cleaning and aggregation scripts. They are subsequently processed (removing empty rows, extracting quarterly statistics, and mapping date keys) before being integrated into our analytical models.
