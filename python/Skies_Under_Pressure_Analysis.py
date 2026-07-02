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
# VISUALIZATIONS
# ==========================================

# Chart 1: Weighted Operating Margin
plt.figure(figsize=(10, 6))
colors = ['green' if x >= 0 else 'red' for x in airline_stats['Weighted_Margin_Pct']]
plt.barh(airline_stats['Airline_Name'], airline_stats['Weighted_Margin_Pct'], color=colors, edgecolor='black')
plt.axvline(0, color='black', linestyle='--')
plt.title('Overall Weighted Operating profit Margin (2009-2022)')
plt.xlabel('Weighted Margin (%)')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '01_weighted_margin_ranking.png'))
plt.close()

# Chart 2: Oil Buckets vs Loss Probability
oil_stats = df.groupby('Oil_Bucket', observed=True).agg(
    Loss_Probability=('operating_income', lambda x: (x < 0).mean() * 100),
    Avg_Price=('Oil_Price_Qtr_Avg', 'mean')
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()
ax1.bar(oil_stats['Oil_Bucket'], oil_stats['Loss_Probability'], color='orange', alpha=0.7, edgecolor='black', label='Loss Prob')
ax2.plot(oil_stats['Oil_Bucket'], oil_stats['Avg_Price'], color='blue', marker='o', linewidth=2, label='Oil Price')
ax1.set_ylabel('Loss Probability (%)', color='orange')
ax2.set_ylabel('Avg WTI Oil Price ($/bbl)', color='blue')
plt.title('Loss Probability vs. WTI Oil Price Buckets')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '02_oil_vs_loss_probability.png'))
plt.close()

# Chart 3: COVID Collapse - Pre vs Shock
collapse = df.groupby(['Airline_Name', 'Period_Group'], observed=True)['operating_income'].mean().unstack()
collapse = collapse[['Pre_COVID', 'COVID_Shock']].dropna().reset_index()

x = np.arange(len(collapse))
width = 0.35
plt.figure(figsize=(12, 6))
plt.bar(x - width/2, collapse['Pre_COVID']/1000, width, label='Pre-COVID', color='lightblue', edgecolor='black')
plt.bar(x + width/2, collapse['COVID_Shock']/1000, width, label='COVID Shock', color='salmon', edgecolor='black')
plt.xticks(x, collapse['Airline_Name'], rotation=45, ha='right')
plt.ylabel('Avg Quarterly Operating Income ($ Millions)')
plt.title('COVID Operating Income Collapse')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '03_covid_collapse_pre_vs_shock.png'))
plt.close()

# Chart 4: CARES Act distortion
cares_data = df[df['CARES_FLAG'] == 'CARES_Period'].groupby('Airline_Name').agg(
    Avg_Net=('net_income', 'mean'),
    Avg_Op=('operating_income', 'mean')
).reset_index()
x = np.arange(len(cares_data))
plt.figure(figsize=(12, 6))
plt.bar(x - width/2, cares_data['Avg_Net']/1000, width, label='Net Income (Post-Bailout)', color='teal', edgecolor='black')
plt.bar(x + width/2, cares_data['Avg_Op']/1000, width, label='Operating Income (True Ops)', color='crimson', edgecolor='black')
plt.xticks(x, cares_data['Airline_Name'], rotation=45, ha='right')
plt.ylabel('Quarterly Average Value ($ Millions)')
plt.title('CARES Act distortion (Net vs Operating Income)')
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '04_cares_distortion_gap.png'))
plt.close()

# Chart 5: Load Factor vs Operating Margin Timeline
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
plt.title('Industry Recovery Timeline')
# Rotate labels and display every 4th label to avoid overlap
ax1.set_xticks(timeline['Year_Quarter'][::4])
ax1.set_xticklabels(timeline['Year_Quarter'][::4], rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '05_recovery_timeline.png'))
plt.close()

# Chart 6: Quarters to Profitability
q5_data = []
for name, grp in df[df['Date_Key'] >= 46].groupby('Airline_Name'):
    profitable_qtrs = grp[grp['operating_income'] > 0].sort_values('Date_Key')
    if not profitable_qtrs.empty:
        q5_data.append({'Airline': name, 'Quarters': int(profitable_qtrs.iloc[0]['Date_Key'] - 46)})
    else:
        q5_data.append({'Airline': name, 'Quarters': 12}) # 12 is max (not recovered)
q5_df = pd.DataFrame(q5_data).sort_values('Quarters')

plt.figure(figsize=(10, 6))
plt.barh(q5_df['Airline'], q5_df['Quarters'], color='purple', edgecolor='black')
plt.title('Quarters to Reach First Profitable Quarter (From 2020-Q2)')
plt.xlabel('Number of Quarters')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '06_recovery_speed.png'))
plt.close()

# Chart 7: Heatmap
plt.figure(figsize=(8, 6))
sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
plt.title('Correlation Matrix of Variables')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '07_correlation_heatmap.png'))
plt.close()

# Chart 8: Fuel cost vs margin scatter
plt.figure(figsize=(10, 6))
for name, grp in df.groupby('Airline_Name'):
    fuel_ratio = (grp['fuel_cost_k'] / grp['operating_revenue']) * 100
    plt.scatter(fuel_ratio, grp['operating_margin_pct'], label=name, alpha=0.7)
plt.xlabel('Fuel Cost / Operating Revenue (%)')
plt.ylabel('Operating Margin (%)')
plt.title('Fuel Cost Ratio vs Operating Margin')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '08_fuel_cost_vs_margin_scatter.png'))
plt.close()

# Chart 9: Revenue area chart
yearly_rev_pivot = df.pivot_table(index='Year_Quarter', columns='Airline_Name', values='operating_revenue', aggfunc='sum')
yearly_rev_pivot = yearly_rev_pivot / 1000 # Convert to Millions
yearly_rev_pivot.plot(kind='area', figsize=(12, 6), alpha=0.7)
plt.ylabel('Revenue ($ Millions)')
plt.title('Total Quarterly revenue per Airline')
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, '09_stacked_revenue_by_airline.png'))
plt.close()

print("All outputs generated successfully!")
