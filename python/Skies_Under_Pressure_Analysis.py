import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# Resolve paths relative to this script's location
script_dir = os.path.dirname(os.path.abspath(__file__))
excel_file = os.path.join(script_dir, "..", "Excel", "Master_Tables_file.xlsx")
plots_dir = os.path.join(script_dir, "plots")
os.makedirs(plots_dir, exist_ok=True)

# 1. Load the Excel sheets
dim_time = pd.read_excel(excel_file, sheet_name='Dim_Time')
fact_fin = pd.read_excel(excel_file, sheet_name='Fact_Financials_Master')
oil_prices = pd.read_excel(excel_file, sheet_name='Oil_Prices_Avg_Qtr')
covid_cases = pd.read_excel(excel_file, sheet_name='covid_19_clean_complete')

# 2. Merge the data on Date_Key
df = fact_fin.merge(dim_time, on='Date_Key', how='left')
df = df.merge(oil_prices.rename(columns={'Oil_Bucket': 'Oil_Bucket_Oil'}), on='Date_Key', how='left')
df = df.merge(covid_cases, on='Date_Key', how='left')
df['Covid_US_Cases_Quarterly'] = df['Covid_US_Cases_Quarterly'].fillna(0)

# Fix units (financials are in $thousands, fuel_cost in raw $, load_factor is 0-100)
df['fuel_cost_k'] = df['fuel_cost'] / 1000
df['operating_margin_pct'] = (df['operating_income'] / df['operating_revenue']) * 100

# Group quarters into Pre-COVID, COVID, and Recovery periods
def get_period(qtr):
    year = int(qtr[:4])
    quarter = qtr[5:]
    if year < 2020:
        return 'Pre_COVID'
    elif year == 2020 or (year == 2021 and quarter in ['Q1', 'Q2']):
        return 'COVID_Shock'
    else:
        return 'Recovery'

df['Period_Group'] = df['Year_Quarter'].apply(get_period)

# Define bucket order for oil
oil_order = ['Below_50', '50_to_80', '80_to_100', '100_Plus']
df['Oil_Bucket'] = pd.Categorical(df['Oil_Bucket'], categories=oil_order, ordered=True)

# ==========================================
# STATISTICAL SUITE (STUDENT ANALYSIS)
# ==========================================

# 1. Descriptive stats per airline
airline_stats = df.groupby('Airline_Name').agg(
    Quarters_Count=('Date_Key', 'count'),
    Total_Revenue_M=('operating_revenue', lambda x: round(x.sum() / 1000, 1)),
    Total_Op_Income_M=('operating_income', lambda x: round(x.sum() / 1000, 1)),
    Avg_Load_Factor_Pct=('load_factor', 'mean'),
    Weighted_Margin_Pct=('operating_income', lambda x: round(x.sum() / df.loc[x.index, 'operating_revenue'].sum() * 100, 2)),
    Loss_Quarters=('operating_income', lambda x: (x < 0).sum())
).reset_index()
airline_stats['Loss_Rate_Pct'] = (airline_stats['Loss_Quarters'] / airline_stats['Quarters_Count'] * 100).round(1)
airline_stats = airline_stats.sort_values('Weighted_Margin_Pct', ascending=False).reset_index(drop=True)
airline_stats.to_csv(os.path.join(script_dir, 'stat_01_descriptive_by_airline.csv'), index=False)

# 2. Comparison across periods
period_summary = df.groupby('Period_Group', observed=True).agg(
    Avg_Load_Factor=('load_factor', 'mean'),
    Avg_Margin=('operating_margin_pct', 'mean'),
    Avg_WTI_Price=('Oil_Price_Qtr_Avg', 'mean'),
    Loss_Rate_Pct=('operating_income', lambda x: (x < 0).mean() * 100)
).reset_index()
period_summary.to_csv(os.path.join(script_dir, 'stat_02_period_comparison.csv'), index=False)

# 3. Pearson Correlation matrix
corr_cols = ['Oil_Price_Qtr_Avg', 'Covid_US_Cases_Quarterly', 'operating_income', 'operating_margin_pct', 'load_factor', 'fuel_cost_k']
corr_matrix = df[corr_cols].corr().round(3)
corr_matrix.to_csv(os.path.join(script_dir, 'stat_03_correlation_matrix.csv'))

# 4. YoY revenue growth table
df['Year'] = df['Year_Quarter'].str[:4].astype(int)
yearly_rev = df.groupby(['Airline_Name', 'Year'])['operating_revenue'].sum().reset_index()
yearly_rev['YoY_Growth_Pct'] = yearly_rev.groupby('Airline_Name')['operating_revenue'].pct_change() * 100
yearly_rev.to_csv(os.path.join(script_dir, 'stat_04_airline_by_period.csv'), index=False)

# ==========================================
# VISUALIZATIONS (DASHBOARD REPLICAS)
# ==========================================

# Chart 1: Average Quarterly Operating Income (CARES vs Normal period) per Airline
# Group by Airline and CARES_FLAG to calculate average operating income
period_op_inc = df.groupby(['Airline_Name', 'CARES_FLAG'])['operating_income'].mean().unstack()
period_op_inc = period_op_inc.sort_values('Normal_Period', ascending=False).reset_index()

x = np.arange(len(period_op_inc))
width = 0.35
plt.figure(figsize=(12, 6))
plt.bar(x - width/2, period_op_inc['CARES_Period']/1000, width, label='CARES Period (2020-Q2 to 2021-Q2)', color='#B23A48', edgecolor='black')
plt.bar(x + width/2, period_op_inc['Normal_Period']/1000, width, label='Normal Period', color='#1F4E79', edgecolor='black')
plt.xticks(x, period_op_inc['Airline_Name'], rotation=45, ha='right')
plt.ylabel('Avg Quarterly Operating Income ($ Millions)')
plt.title('Dashboard Chart 1: Average Quarterly Operating Income (CARES vs Normal Period)')
plt.axhline(0, color='black', linestyle='-', linewidth=0.8)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '01_average_operating_income_cares_vs_normal.png'))
plt.close()

# Chart 2: Recovery Profile: Annual Income vs Revenue (2018-2022)
annual_summary = df[(df['Year'] >= 2018) & (df['Year'] <= 2022)].groupby('Year').agg(
    Revenue=('operating_revenue', 'sum'),
    Net_Income=('net_income', 'sum')
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()
ax1.plot(annual_summary['Year'].astype(str), annual_summary['Revenue']/1000000, color='#1F4E79', marker='o', linewidth=2.5, label='Operating Revenue')
ax2.plot(annual_summary['Year'].astype(str), annual_summary['Net_Income']/1000000, color='#F9B612', marker='s', linewidth=2.5, linestyle='--', label='Net Income')
ax1.set_xlabel('Year')
ax1.set_ylabel('Total Operating Revenue ($ Millions)', color='#1F4E79')
ax2.set_ylabel('Total Net Income ($ Millions)', color='#F9B612')
ax1.tick_params(axis='y', labelcolor='#1F4E79')
ax2.tick_params(axis='y', labelcolor='#F9B612')
plt.title('Dashboard Chart 2: Recovery Profile (Annual Revenue vs Net Income)')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '02_recovery_profile_annual_income_vs_revenue.png'))
plt.close()

# Chart 3: Operating Revenue for Airlines
revenue_ranking = df.groupby('Airline_Name')['operating_revenue'].sum().reset_index()
revenue_ranking = revenue_ranking.sort_values('operating_revenue', ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(revenue_ranking['Airline_Name'], revenue_ranking['operating_revenue']/1000000, color='#F9B612', edgecolor='black', height=0.6)
plt.title('Dashboard Chart 3: Total Operating Revenue for Airlines (2009-2022)')
plt.xlabel('Total Revenue ($ Millions)')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '03_operating_revenue_ranking.png'))
plt.close()

# Chart 4: Net Financial Assistance by Airline (Bailout Cushion)
cares_df = df[df['CARES_FLAG'] == 'CARES_Period']
bailout_cushion = cares_df.groupby('Airline_Name').apply(
    lambda x: (x['net_income'].sum() - x['operating_income'].sum()) / 1000
).reset_index(name='Bailout_Cushion_M')
bailout_cushion = bailout_cushion.sort_values('Bailout_Cushion_M', ascending=True)

plt.figure(figsize=(10, 6))
colors = ['#B23A48' if x < 0 else '#F9B612' for x in bailout_cushion['Bailout_Cushion_M']]
plt.barh(bailout_cushion['Airline_Name'], bailout_cushion['Bailout_Cushion_M'], color=colors, edgecolor='black', height=0.6)
plt.title('Dashboard Chart 4: Net Financial Assistance by Airline (Bailout Cushion)')
plt.xlabel('Bailout Cushion ($ Millions)')
plt.axvline(0, color='black', linestyle='-', linewidth=0.8)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '04_net_financial_assistance_bailout_cushion.png'))
plt.close()

# Chart 5: Revenue Margin (Revenue & Income) vs Oil Price Brackets
oil_bracket_summary = df.groupby('Oil_Bucket', observed=True).agg(
    Revenue=('operating_revenue', 'sum'),
    Income=('operating_income', 'sum')
).reset_index()

x = np.arange(len(oil_bracket_summary))
width = 0.35
plt.figure(figsize=(10, 6))
plt.bar(x - width/2, oil_bracket_summary['Revenue']/1000000, width, label='Operating Revenue', color='#F9B612', edgecolor='black')
plt.bar(x + width/2, oil_bracket_summary['Income']/1000000, width, label='Operating Income', color='#1F4E79', edgecolor='black')
plt.xticks(x, oil_bracket_summary['Oil_Bucket'])
plt.ylabel('Total Value ($ Millions)')
plt.title('Dashboard Chart 5: Operating Revenue & Income vs Oil Price Brackets')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '05_revenue_and_income_by_oil_price_bracket.png'))
plt.close()

# ==========================================
# ADDITIONAL INSIGHTFUL CHARTS
# ==========================================

# Chart 6: COVID Collapse - Pre vs Shock
collapse = df.groupby(['Airline_Name', 'Period_Group'], observed=True)['operating_income'].mean().unstack()
collapse = collapse[['Pre_COVID', 'COVID_Shock']].dropna().reset_index()

x_coll = np.arange(len(collapse))
w_coll = 0.35
plt.figure(figsize=(12, 6))
plt.bar(x_coll - w_coll/2, collapse['Pre_COVID']/1000, w_coll, label='Pre-COVID', color='lightblue', edgecolor='black')
plt.bar(x_coll + w_coll/2, collapse['COVID_Shock']/1000, w_coll, label='COVID Shock', color='salmon', edgecolor='black')
plt.xticks(x_coll, collapse['Airline_Name'], rotation=45, ha='right')
plt.ylabel('Avg Quarterly Operating Income ($ Millions)')
plt.title('Additional Chart 6: COVID Operating Income Collapse')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '06_covid_operating_income_collapse.png'))
plt.close()

# Chart 7: Load Factor vs Operating Margin Timeline
timeline = df.groupby('Year_Quarter').agg(
    Avg_LF=('load_factor', 'mean'),
    Avg_Margin=('operating_margin_pct', 'mean')
).reset_index()

fig, ax1 = plt.subplots(figsize=(14, 6))
ax2 = ax1.twinx()
ax1.plot(timeline['Year_Quarter'], timeline['Avg_LF'], color='darkblue', marker='s', label='Avg Load Factor (%)')
ax2.plot(timeline['Year_Quarter'], timeline['Avg_Margin'], color='green', marker='o', linestyle='--', label='Avg Operating Margin (%)')
ax1.set_ylabel('Load Factor (%)', color='darkblue')
ax2.set_ylabel('Operating Margin (%)', color='green')
plt.title('Additional Chart 7: Industry Recovery Timeline')
ax1.set_xticks(timeline['Year_Quarter'][::4])
ax1.set_xticklabels(timeline['Year_Quarter'][::4], rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '07_industry_recovery_timeline.png'))
plt.close()

# Chart 8: Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Additional Chart 8: Correlation Matrix of Variables')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '08_correlation_heatmap.png'))
plt.close()

print("All outputs generated successfully!")
