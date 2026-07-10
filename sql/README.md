# SQL Sub-Project Directory

This folder contains the relational database design model and schema queries for our project.

## Database Engine
*   **Engine:** MySQL
*   **Modeling Client:** MySQL Workbench

---

## Deliverables Manifest

### 1. `skies-under-pressure-model.mwb`
The database design model created in MySQL Workbench. It defines the physical relationships and star-schema topology:
*   **`dim_date`:** The central date key dimension table.
*   **`fact_bts`:** The airline quarterly financial statement fact table.
*   **`fact_covid`:** The pandemic case tracking fact table.
*   **`fact_oil_price`:** The crude oil spot price tracking fact table.
*   *Foreign Key Constraints:* All fact tables are joined to `dim_date` using foreign key mappings on the `Date_Key` field.

### 2. `skies-under-pressure-queries.sql`
A single SQL script containing the full database workflow:
*   **Preprocessing Cells:** Cleans and aggregates date formats, filters timelines, groups raw prices/cases to quarterly grains, and calculates averages.
*   **Date Dimension Creation:** Dynamically generates the calendar table `dim_date` (2009–2022).
*   **Date Key Joins:** Updates the fact tables with foreign keys and drops obsolete quarter/date strings.
*   **8 Analytical Queries:**
    1.  *Average Quarterly Operating Income* (CARES vs Normal period).
    2.  *Recovery Profile:* Annual operating revenue vs. net income (2018–2022).
    3.  *Operating Revenue for Airlines:* Total revenue ranking descending.
    4.  *Average Load Factor by Airline:* Efficiency ranking descending.
    5.  *Average Fuel Cost by Year:* Annual average WTI/fuel price trends.
    6.  *Total Confirmed COVID Cases:* Annual pandemic waves.
    7.  *Top Airline by Net Income:* Total net income ranking.
    8.  *Top Year_Qtr by Total Revenue:* Highest revenue quarters in history.

---

## How to Execute
1.  Open **MySQL Workbench** and connect to your database instance.
2.  Import and execute `skies-under-pressure-queries.sql` to preprocess the raw imports, create the star-schema mapping, and execute the analytical queries.
3.  Open `skies-under-pressure-model.mwb` to view and modify the EER relational schema diagrams.
