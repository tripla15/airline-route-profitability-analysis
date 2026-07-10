# Python Sub-Project Directory

This folder contains the complete, unified data engineering and analytical reporting notebook.

## Deliverable File
*   **`Skies_Under_Pressure_Notebook.ipynb`:** The primary interactive Jupyter Notebook. It handles the complete pipeline sequentially:
    1.  **Data Preprocessing:** Ingests raw Crude Oil and COVID-19 datasets, cleans and filters them, and exports them directly into the Excel processed data directory.
    2.  **Data Ingestion & Merging:** Loads the master fact tables and dimensions, joining them on the primary key (`Date_Key`).
    3.  **Unit Corrections:** Aligns the transaction currency grains.
    4.  **Statistical Calculations:** Calculates descriptive statistics, period metrics, and Pearson correlation matrices.
    5.  **Visual Reporting:** Renders the 5 dashboard replica charts and 3 additional insight charts directly inline.

---

## Setup & Running

**Prerequisites:**
Install the required data science libraries:
```bash
pip install pandas numpy matplotlib seaborn openpyxl
```

**Running the notebook:**
Open the notebook in VS Code (with the Jupyter extension installed) or run:
```bash
jupyter notebook Skies_Under_Pressure_Notebook.ipynb
```
Select your Python kernel, and run all cells sequentially.
