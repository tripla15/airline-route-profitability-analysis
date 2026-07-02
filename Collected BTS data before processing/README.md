# Collected BTS Data Directory

This directory preserves the raw, unedited downloads directly extracted from the Bureau of Transportation Statistics (BTS) Form 41 reporting databases. 

## Directory Structure

### 1. `BTS Data_CSV/`
Contains the raw CSV sheets of financial reporting elements extracted from BTS Form 41 Schedule P-12 (Revenues, operating costs, and net income indices).

### 2. `BTS_Load_Factor/`
Contains raw passenger traffic reports (T-100 Segment database) used to extract quarterly load factors (the percentage of available aircraft seats filled by revenue passengers).

### 3. `BTS_OLD/`
Archived reference data and preliminary query outputs used during the early schema prototyping phases.

### 4. Consolidated Files:
* **`BTS_Fuel_Cost_ALL_Carriers.csv`:** Consolidated raw quarterly fuel spend records across all US passenger carriers.
* **`BTS_Operating_Income_ALL_Carriers.csv`:** Consolidated raw quarterly operating revenue and income statements.

---

## Purpose
This folder is kept intact to serve as an audit trail. Analysts can trace transformations from the exact state of government downloads through to the final cleaned star-schema tables.
