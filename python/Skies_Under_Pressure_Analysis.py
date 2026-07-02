"""
Skies Under Pressure: Aviation Profitability vs. Global Macro-Shocks
=======================================================================
Python Standalone Analysis Pipeline
Datasets: BTS Financials, WTI Crude Oil Prices, US COVID-19 Cases
Airlines: 10 Core US Passenger Carriers, 2009-Q1 to 2022-Q4 (56 quarters)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

EXCEL_PATH   = r"F:\Engineering 2nd year\Extracurriculars\1. DEPI\Final Project\Excel\Master_Tables_file.xlsx"
OUTPUT_DIR   = r"F:\Engineering 2nd year\Extracurriculars\1. DEPI\Final Project\Python"
PLOTS_DIR    = os.path.join(OUTPUT_DIR, "plots")
os.makedirs(PLOTS_DIR, exist_ok=True)

# Project color palette
NAVY     = '#1F4E79'
AMBER    = '#C17C00'
CRIMSON  = '#B23A48'
CHARCOAL = '#2F2F2F'
BG       = '#F7F7F5'
TEAL     = '#2A9D8F'
GOLD     = '#E9C46A'
SAGE     = '#6B9E78'

# Global plot style
plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': BG,
    'axes.edgecolor': CHARCOAL,
    'axes.labelcolor': CHARCOAL,
    'text.color': CHARCOAL,
    'xtick.color': CHARCOAL,
    'ytick.color': CHARCOAL,
    'font.family': 'DejaVu Sans',
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'figure.titlesize': 15,
    'figure.titleweight': 'bold',
    'legend.fontsize': 10,
    'legend.framealpha': 0.85,
})

AIRLINE_COLORS = {
    'American Airlines': '#003087',
    'Delta Airlines':    '#E01933',
    'United Airlines':   '#005DAA',
    'Southwest Airlines':'#F9B612',
    'Alaska Airlines':   '#00508F',
    'JetBlue Airlines':  '#003876',
    'Spirit Airlines':   '#FFD700',
    'Frontier Airlines': '#00843D',
    'Hawaiian Airlines': '#5C2D91',
    'Allegiant Airlines':'#F04E23',
}

BUCKET_ORDER = ['Below_50', '50_to_80', '80_to_100', '100_Plus']
BUCKET_LABELS = ['< $50/bbl', '$50–$80/bbl', '$80–$100/bbl', '> $100/bbl']

# ─────────────────────────────────────────────────────────────────────────────
# 1. DATA LOADING & MERGING
# ─────────────────────────────────────────────────────────────────────────────

print("=" * 60)
print("  SKIES UNDER PRESSURE - PYTHON ANALYSIS PIPELINE")
print("=" * 60)
print("\n[1] Loading data from Excel...")

dim_time    = pd.read_excel(EXCEL_PATH, sheet_name='Dim_Time')
fact_fin    = pd.read_excel(EXCEL_PATH, sheet_name='Fact_Financials_Master')
oil_prices  = pd.read_excel(EXCEL_PATH, sheet_name='Oil_Prices_Avg_Qtr')
covid_cases = pd.read_excel(EXCEL_PATH, sheet_name='covid_19_clean_complete')

print(f"    Fact_Financials_Master : {fact_fin.shape[0]:,} rows × {fact_fin.shape[1]} cols")
print(f"    Oil_Prices_Avg_Qtr     : {oil_prices.shape[0]:,} rows × {oil_prices.shape[1]} cols")
print(f"    covid_19_clean_complete: {covid_cases.shape[0]:,} rows × {covid_cases.shape[1]} cols")
print(f"    Dim_Time               : {dim_time.shape[0]:,} rows × {dim_time.shape[1]} cols")

# Merge everything on Date_Key
print("\n[2] Merging datasets on Date_Key...")
merged = fact_fin.copy()
merged = merged.merge(dim_time, on='Date_Key', how='left')
merged = merged.merge(
    oil_prices.rename(columns={'Oil_Bucket': 'Oil_Bucket_Oil'}),
    on='Date_Key', how='left'
)
merged = merged.merge(covid_cases, on='Date_Key', how='left')
merged['Covid_US_Cases_Quarterly'] = merged['Covid_US_Cases_Quarterly'].fillna(0).astype(int)

# ─── UNIT CORRECTIONS ────────────────────────────────────────────────────────
# operating_revenue, operating_income, net_income are in $thousands
# load_factor is on 0–100 scale (percentage points, not decimal)
# fuel_cost is in raw dollars → convert to thousands for consistency
# ─────────────────────────────────────────────────────────────────────────────
merged['fuel_cost_k']         = merged['fuel_cost'] / 1000          # → $thousands
merged['load_factor_pct']     = merged['load_factor']               # 78.6 means 78.6%
merged['load_factor_dec']     = merged['load_factor'] / 100         # 0.786 decimal
merged['operating_margin_pct']= (merged['operating_income'] / merged['operating_revenue']) * 100

# Period grouping
def period_group(qtr):
    y, q = int(qtr[:4]), qtr[5:]
    if y < 2020:
        return 'Pre_COVID'
    elif (y == 2020) or (y == 2021 and q in ('Q1', 'Q2')):
        return 'COVID_Shock'
    else:
        return 'Recovery'

merged['Period_Group'] = merged['Year_Quarter'].apply(period_group)

# Ordered categoricals
merged['Oil_Bucket'] = pd.Categorical(merged['Oil_Bucket'], categories=BUCKET_ORDER, ordered=True)
merged['Period_Group'] = pd.Categorical(merged['Period_Group'],
                                         categories=['Pre_COVID', 'COVID_Shock', 'Recovery'],
                                         ordered=True)

print(f"    Master merged table: {merged.shape[0]:,} rows × {merged.shape[1]} cols")
print(f"    Airlines: {sorted(merged['Airline_Name'].unique())}")
print(f"    Quarters: {merged['Year_Quarter'].nunique()} (Date_Key 1–56)")

# ─────────────────────────────────────────────────────────────────────────────
# 2. STATISTICAL ANALYSIS SUITE
# ─────────────────────────────────────────────────────────────────────────────

print("\n[3] Running statistical analysis...")

# ── 2a. Descriptive statistics per airline ───────────────────────────────────
desc_by_airline = merged.groupby('Airline_Name').agg(
    Quarters_Tracked        = ('Date_Key', 'count'),
    Total_Revenue_M         = ('operating_revenue', lambda x: round(x.sum() / 1000, 1)),   # → $millions
    Total_Op_Income_M       = ('operating_income', lambda x: round(x.sum() / 1000, 1)),
    Total_Net_Income_M      = ('net_income', lambda x: round(x.sum() / 1000, 1)),
    Avg_Quarterly_Revenue_K = ('operating_revenue', lambda x: round(x.mean(), 0)),
    Avg_Quarterly_OpIncome_K= ('operating_income', lambda x: round(x.mean(), 0)),
    Std_OpIncome_K          = ('operating_income', lambda x: round(x.std(), 0)),
    Min_OpIncome_K          = ('operating_income', lambda x: round(x.min(), 0)),
    Max_OpIncome_K          = ('operating_income', lambda x: round(x.max(), 0)),
    Avg_Load_Factor_Pct     = ('load_factor_pct', lambda x: round(x.mean(), 2)),
    Std_Load_Factor_Pct     = ('load_factor_pct', lambda x: round(x.std(), 2)),
    Avg_Op_Margin_Pct       = ('operating_margin_pct', lambda x: round(x.mean(), 2)),
    Weighted_Op_Margin_Pct  = ('operating_income', lambda x: round(
                                    x.sum() / merged.loc[x.index, 'operating_revenue'].sum() * 100, 2)),
    Loss_Quarters           = ('operating_income', lambda x: (x < 0).sum()),
    Profit_Quarters         = ('operating_income', lambda x: (x >= 0).sum()),
).reset_index()
desc_by_airline['Loss_Rate_Pct'] = (desc_by_airline['Loss_Quarters'] / desc_by_airline['Quarters_Tracked'] * 100).round(1)
desc_by_airline = desc_by_airline.sort_values('Weighted_Op_Margin_Pct', ascending=False).reset_index(drop=True)
desc_by_airline.index += 1  # 1-based ranking

# ── 2b. Period comparison table ──────────────────────────────────────────────
period_summary = merged.groupby(['Period_Group'], observed=True).agg(
    Airline_Quarter_Obs     = ('Date_Key', 'count'),
    Avg_Load_Factor_Pct     = ('load_factor_pct', lambda x: round(x.mean(), 2)),
    Avg_Op_Margin_Pct       = ('operating_margin_pct', lambda x: round(x.mean(), 2)),
    Avg_Op_Income_K         = ('operating_income', lambda x: round(x.mean(), 0)),
    Avg_Revenue_K           = ('operating_revenue', lambda x: round(x.mean(), 0)),
    Avg_WTI_Price           = ('Oil_Price_Qtr_Avg', lambda x: round(x.mean(), 2)),
    Loss_Rate_Pct           = ('operating_income', lambda x: round((x < 0).mean() * 100, 1)),
).reset_index()

# ── 2c. Pearson correlation matrix ───────────────────────────────────────────
corr_cols = {
    'WTI_Oil_Price'      : 'Oil_Price_Qtr_Avg',
    'COVID_Cases_M'      : 'Covid_US_Cases_Quarterly',
    'Operating_Income_K' : 'operating_income',
    'Operating_Margin_Pct': 'operating_margin_pct',
    'Load_Factor_Pct'    : 'load_factor_pct',
    'Fuel_Cost_K'        : 'fuel_cost_k',
    'Net_Income_K'       : 'net_income',
}
corr_df = merged[list(corr_cols.values())].copy()
corr_df.columns = list(corr_cols.keys())
corr_matrix = corr_df.corr(method='pearson').round(3)

# ── 2d. YoY revenue growth ───────────────────────────────────────────────────
yearly = merged.groupby(['Airline_Name', merged['Year_Quarter'].str[:4].rename('Year')]).agg(
    Annual_Revenue_K  = ('operating_revenue', 'sum'),
    Annual_OpIncome_K = ('operating_income', 'sum'),
).reset_index()
yearly['Revenue_YoY_Pct'] = yearly.groupby('Airline_Name')['Annual_Revenue_K'].pct_change() * 100
yearly['Revenue_YoY_Pct'] = yearly['Revenue_YoY_Pct'].round(1)

# ── 2e. Per-airline per-period breakdown ─────────────────────────────────────
airline_period = merged.groupby(['Airline_Name', 'Period_Group'], observed=True).agg(
    Avg_Load_Factor_Pct  = ('load_factor_pct', lambda x: round(x.mean(), 2)),
    Avg_Op_Margin_Pct    = ('operating_margin_pct', lambda x: round(x.mean(), 2)),
    Avg_Op_Income_K      = ('operating_income', lambda x: round(x.mean(), 0)),
).unstack('Period_Group')
airline_period.columns = ['_'.join(c) for c in airline_period.columns]
airline_period = airline_period.reset_index()

# Save all statistical tables
print("\n[4] Saving statistical tables to CSV...")
desc_by_airline.to_csv(os.path.join(OUTPUT_DIR, 'stat_01_descriptive_by_airline.csv'), index=False)
period_summary.to_csv(os.path.join(OUTPUT_DIR, 'stat_02_period_comparison.csv'), index=False)
corr_matrix.to_csv(os.path.join(OUTPUT_DIR, 'stat_03_correlation_matrix.csv'))
airline_period.to_csv(os.path.join(OUTPUT_DIR, 'stat_04_airline_by_period.csv'), index=False)

# Business question result tables
q1 = desc_by_airline[['Airline_Name', 'Weighted_Op_Margin_Pct', 'Avg_Op_Margin_Pct',
                        'Total_Op_Income_M', 'Total_Revenue_M', 'Loss_Rate_Pct']].copy()
q1.columns = ['Airline', 'Weighted_Margin_%', 'Avg_Qtr_Margin_%',
               'Total_OpIncome_$M', 'Total_Revenue_$M', 'Loss_Rate_%']
q1.to_csv(os.path.join(OUTPUT_DIR, 'q1_margin_ranking.csv'), index=False)

cares_data = merged[merged['CARES_FLAG'] == 'CARES_Period']
q4 = cares_data.groupby('Airline_Name').agg(
    Avg_Net_Income_K    = ('net_income', 'mean'),
    Avg_Op_Income_K     = ('operating_income', 'mean'),
).reset_index()
q4['Bailout_Gap_K'] = q4['Avg_Net_Income_K'] - q4['Avg_Op_Income_K']
q4 = q4.sort_values('Bailout_Gap_K', ascending=False).reset_index(drop=True)
q4.to_csv(os.path.join(OUTPUT_DIR, 'q4_cares_distortion.csv'), index=False)

q5_rows = []
for name, grp in merged[merged['Date_Key'] >= 46].groupby('Airline_Name'):
    pos = grp[grp['operating_income'] > 0].sort_values('Date_Key')
    if not pos.empty:
        q5_rows.append({'Airline_Name': name,
                        'First_Profit_Quarter': pos.iloc[0]['Year_Quarter'],
                        'Quarters_to_Recovery': pos.iloc[0]['Date_Key'] - 46})
    else:
        q5_rows.append({'Airline_Name': name,
                        'First_Profit_Quarter': 'Not recovered by 2022-Q4',
                        'Quarters_to_Recovery': None})
q5 = pd.DataFrame(q5_rows).sort_values('Quarters_to_Recovery', na_position='last').reset_index(drop=True)
q5.to_csv(os.path.join(OUTPUT_DIR, 'q5_recovery_speed.csv'), index=False)

# ─────────────────────────────────────────────────────────────────────────────
# 3. VISUALIZATIONS
# ─────────────────────────────────────────────────────────────────────────────

print("\n[5] Generating visualizations...")

def save_fig(name):
    path = os.path.join(PLOTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches='tight', facecolor=BG)
    plt.close()
    print(f"    Saved: {name}")

# ── CHART 1: Weighted Operating Margin Ranking ───────────────────────────────
fig, ax = plt.subplots(figsize=(11, 7))
fig.patch.set_facecolor(BG)

colors = [NAVY if v >= 0 else CRIMSON for v in desc_by_airline['Weighted_Op_Margin_Pct']]
bars = ax.barh(desc_by_airline['Airline_Name'], desc_by_airline['Weighted_Op_Margin_Pct'],
               color=colors, edgecolor='white', linewidth=0.6, height=0.65)
ax.axvline(0, color=CHARCOAL, linewidth=1.2, linestyle='--', alpha=0.6)

for bar, val in zip(bars, desc_by_airline['Weighted_Op_Margin_Pct']):
    offset = 0.15 if val >= 0 else -0.15
    ha = 'left' if val >= 0 else 'right'
    ax.text(val + offset, bar.get_y() + bar.get_height()/2,
            f'{val:.2f}%', va='center', ha=ha, fontsize=10, fontweight='bold', color=CHARCOAL)

ax.set_xlabel('Weighted Operating Profit Margin  (Total Operating Income ÷ Total Revenue)', labelpad=10)
ax.set_title('US Passenger Airlines: 14-Year Weighted Operating Profit Margin (2009–2022)', pad=15)
ax.invert_yaxis()
ax.set_facecolor(BG)
ax.grid(axis='x', alpha=0.3, color=CHARCOAL)
ax.spines[['top', 'right']].set_visible(False)
fig.text(0.5, -0.02, 'Source: Bureau of Transportation Statistics (BTS) Form 41 Schedule P-12',
         ha='center', fontsize=9, color='gray', style='italic')
plt.tight_layout()
save_fig('01_weighted_margin_ranking.png')

# ── CHART 2: Oil Price Buckets vs Loss Probability (Dual Axis) ───────────────
oil_analysis = merged.groupby('Oil_Bucket', observed=True).agg(
    Loss_Probability = ('operating_income', lambda x: (x < 0).mean()),
    Avg_Oil_Price    = ('Oil_Price_Qtr_Avg', 'mean'),
    Avg_Op_Income_K  = ('operating_income', 'mean'),
    Quarter_Count    = ('operating_income', 'count'),
).reset_index()

fig, ax1 = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
ax2 = ax1.twinx()

bar_width = 0.5
x_pos = np.arange(len(BUCKET_ORDER))
bars = ax1.bar(x_pos, oil_analysis['Loss_Probability'] * 100, width=bar_width,
               color=AMBER, alpha=0.85, edgecolor='white', zorder=2)
ax2.plot(x_pos, oil_analysis['Avg_Oil_Price'], color=CRIMSON,
         marker='o', linewidth=2.5, markersize=9, zorder=3, label='Avg WTI Price ($/bbl)')

for bar, val in zip(bars, oil_analysis['Loss_Probability'] * 100):
    ax1.text(bar.get_x() + bar.get_width()/2, val + 0.8, f'{val:.1f}%',
             ha='center', fontsize=11, fontweight='bold', color=AMBER)

ax1.set_xticks(x_pos)
ax1.set_xticklabels(BUCKET_LABELS, fontsize=11)
ax1.set_ylabel('Loss Probability  (% of quarters with negative Op. Income)', color=AMBER, labelpad=10)
ax2.set_ylabel('Average WTI Crude Oil Price ($/barrel)', color=CRIMSON, labelpad=10)
ax1.tick_params(axis='y', colors=AMBER)
ax2.tick_params(axis='y', colors=CRIMSON)
ax1.set_ylim(0, 45)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
ax1.set_facecolor(BG)
ax1.grid(axis='y', alpha=0.25, color=CHARCOAL)
ax1.spines[['top', 'right']].set_visible(False)
ax2.spines[['top']].set_visible(False)
ax1.set_title('Loss Probability & Average Oil Price by WTI Crude Oil Price Bucket', pad=15)
ax2.legend(loc='upper right')
fig.text(0.5, -0.02, 'Each bar = share of airline-quarters that ended with operating loss, grouped by prevailing WTI price range.',
         ha='center', fontsize=9, color='gray', style='italic')
plt.tight_layout()
save_fig('02_oil_vs_loss_probability.png')

# ── CHART 3: COVID Collapse — Pre vs Shock per Airline ───────────────────────
collapse = merged.groupby(['Airline_Name', 'Period_Group'], observed=True)['operating_income'].mean().unstack()
collapse = collapse[['Pre_COVID', 'COVID_Shock']].dropna()
collapse['Collapse_K'] = collapse['COVID_Shock'] - collapse['Pre_COVID']
collapse = collapse.sort_values('Collapse_K').reset_index()

fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
x = np.arange(len(collapse))
w = 0.38
b1 = ax.bar(x - w/2, collapse['Pre_COVID'] / 1000, width=w, label='Pre-COVID Avg (2009–2019)', color=NAVY, alpha=0.9)
b2 = ax.bar(x + w/2, collapse['COVID_Shock'] / 1000, width=w, label='COVID Shock Avg (2020-Q1–2021-Q2)', color=CRIMSON, alpha=0.9)
ax.axhline(0, color=CHARCOAL, linewidth=1.0)
ax.set_xticks(x)
ax.set_xticklabels(collapse['Airline_Name'], rotation=35, ha='right', fontsize=10)
ax.set_ylabel('Average Quarterly Operating Income ($M)', labelpad=10)
ax.set_title('COVID-19 Operating Income Collapse: Pre-COVID Baseline vs. COVID Shock Period', pad=15)
ax.legend(loc='upper right')
ax.set_facecolor(BG)
ax.grid(axis='y', alpha=0.25, color=CHARCOAL)
ax.spines[['top', 'right']].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}M'))
fig.text(0.5, -0.02, 'Values in $millions (thousands of dollars). Legacy network carriers show deepest absolute collapse.',
         ha='center', fontsize=9, color='gray', style='italic')
plt.tight_layout()
save_fig('03_covid_collapse_pre_vs_shock.png')

# ── CHART 4: CARES Act Distortion — Net vs Operating Income ──────────────────
fig, ax = plt.subplots(figsize=(12, 7))
fig.patch.set_facecolor(BG)
x = np.arange(len(q4))
w = 0.38
ax.bar(x - w/2, q4['Avg_Net_Income_K'] / 1000, width=w,
       label='Avg Net Income (Post-Bailout)', color=TEAL, alpha=0.9)
ax.bar(x + w/2, q4['Avg_Op_Income_K'] / 1000, width=w,
       label='Avg Operating Income (True Operations)', color=CRIMSON, alpha=0.9)
ax.axhline(0, color=CHARCOAL, linewidth=1.2, linestyle='--')
ax.set_xticks(x)
ax.set_xticklabels(q4['Airline_Name'], rotation=35, ha='right', fontsize=10)
ax.set_ylabel('Quarterly Average Value ($M)', labelpad=10)
ax.set_title('CARES Act Distortion Window: Net Income vs. Operating Income (2020-Q2 to 2021-Q2)', pad=15)
ax.legend(loc='upper right')
ax.set_facecolor(BG)
ax.grid(axis='y', alpha=0.25, color=CHARCOAL)
ax.spines[['top', 'right']].set_visible(False)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}M'))
fig.text(0.5, -0.02, 'Gap = federal PSP grant income. Positive gap = government support made losses look smaller than true operational reality.',
         ha='center', fontsize=9, color='gray', style='italic')
plt.tight_layout()
save_fig('04_cares_distortion_gap.png')

# ── CHART 5: Industry Recovery Timeline — Load Factor & Margin ───────────────
timeline = merged[merged['Year_Quarter'] >= '2019-Q1'].groupby('Year_Quarter').agg(
    Avg_Load_Factor_Pct  = ('load_factor_pct', 'mean'),
    Avg_Op_Margin_Pct    = ('operating_margin_pct', 'mean'),
).reset_index().sort_values('Year_Quarter')

fig, ax1 = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor(BG)
ax2 = ax1.twinx()

labels = timeline['Year_Quarter'].tolist()
x = np.arange(len(labels))
shock_start = labels.index('2020-Q1')
shock_end   = labels.index('2021-Q2')

ax1.fill_between(x, 0, 100,
                  where=[(shock_start <= i <= shock_end) for i in range(len(x))],
                  color=CRIMSON, alpha=0.08, label='COVID Shock & CARES Window')
ax1.plot(x, timeline['Avg_Load_Factor_Pct'], color=NAVY, marker='s',
         linewidth=2.5, markersize=7, label='Avg Load Factor (Left Axis, %)')
ax2.plot(x, timeline['Avg_Op_Margin_Pct'], color=TEAL, marker='D',
         linewidth=2.5, markersize=7, linestyle='--', label='Avg Op. Margin % (Right Axis)')
ax2.axhline(0, color='gray', linewidth=1.0, linestyle='-.')

ax1.set_xticks(x)
ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
ax1.set_ylabel('Average Load Factor (%)', color=NAVY, labelpad=10)
ax2.set_ylabel('Average Operating Profit Margin (%)', color=TEAL, labelpad=10)
ax1.tick_params(axis='y', colors=NAVY)
ax2.tick_params(axis='y', colors=TEAL)
ax1.set_ylim(0, 105)
ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
ax2.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
ax1.set_facecolor(BG)
ax1.grid(axis='y', alpha=0.2, color=CHARCOAL)
ax1.spines[['top']].set_visible(False)
ax2.spines[['top']].set_visible(False)

lines1, lbls1 = ax1.get_legend_handles_labels()
lines2, lbls2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, lbls1 + lbls2, loc='lower left', fontsize=9)
ax1.set_title('Industry Recovery Timeline: Load Factor vs. Operating Margin (2019-Q1 – 2022-Q4)', pad=15)
fig.text(0.5, -0.03, 'Shaded zone = COVID Shock and CARES Act support window. Load factor is % of seats filled per quarter.',
         ha='center', fontsize=9, color='gray', style='italic')
plt.tight_layout()
save_fig('05_recovery_timeline.png')

# ── CHART 6: Airline-level Recovery Bars ─────────────────────────────────────
q5_plot = q5[q5['Quarters_to_Recovery'].notna()].copy()
q5_plot['Quarters_to_Recovery'] = q5_plot['Quarters_to_Recovery'].astype(int)
q5_sorted = q5_plot.sort_values('Quarters_to_Recovery')

fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(BG)
palette = [AIRLINE_COLORS.get(a, NAVY) for a in q5_sorted['Airline_Name']]
bars = ax.barh(q5_sorted['Airline_Name'], q5_sorted['Quarters_to_Recovery'],
               color=palette, edgecolor='white', height=0.6)
for bar, qtr, fq in zip(bars, q5_sorted['Quarters_to_Recovery'], q5_sorted['First_Profit_Quarter']):
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'{qtr}Q  ({fq})', va='center', fontsize=10, color=CHARCOAL)
ax.set_xlabel('Quarters to First Positive Operating Income (from 2020-Q2)', labelpad=10)
ax.set_title('COVID-19 Recovery Speed: Quarters to First Profitable Operating Quarter', pad=15)
ax.set_facecolor(BG)
ax.grid(axis='x', alpha=0.25, color=CHARCOAL)
ax.spines[['top', 'right']].set_visible(False)
ax.set_xlim(0, max(q5_sorted['Quarters_to_Recovery']) + 4)
not_recovered = q5[q5['Quarters_to_Recovery'].isna()]['Airline_Name'].tolist()
if not_recovered:
    fig.text(0.5, -0.03, f'Not recovered by 2022-Q4: {", ".join(not_recovered)}',
             ha='center', fontsize=9, color=CRIMSON, style='italic')
plt.tight_layout()
save_fig('06_recovery_speed.png')

# ── CHART 7: Correlation Heatmap ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 7))
fig.patch.set_facecolor(BG)
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, mask=mask, annot=True, fmt='.2f', cmap='RdYlBu_r',
            center=0, vmin=-1, vmax=1, linewidths=0.5,
            ax=ax, cbar_kws={'shrink': 0.8, 'label': 'Pearson r'})
ax.set_title('Pearson Correlation Matrix: Financial & Macro-Shock Variables', pad=15)
ax.set_facecolor(BG)
plt.tight_layout()
save_fig('07_correlation_heatmap.png')

# ── CHART 8: Fuel Cost vs Operating Margin Scatter ───────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor(BG)
for airline, grp in merged.groupby('Airline_Name'):
    color = AIRLINE_COLORS.get(airline, NAVY)
    fuel_pct = (grp['fuel_cost_k'] / grp['operating_revenue']) * 100
    ax.scatter(fuel_pct, grp['operating_margin_pct'],
               color=color, alpha=0.45, s=30, label=airline)
ax.axhline(0, color=CHARCOAL, linewidth=1.0, linestyle='--', alpha=0.6)
ax.set_xlabel('Fuel Cost as % of Operating Revenue', labelpad=10)
ax.set_ylabel('Operating Profit Margin (%)', labelpad=10)
ax.set_title('Fuel Cost Burden vs. Operating Profit Margin (All Airlines, 2009–2022)', pad=15)
ax.legend(loc='upper right', fontsize=8, ncol=2)
ax.set_facecolor(BG)
ax.grid(alpha=0.2, color=CHARCOAL)
ax.spines[['top', 'right']].set_visible(False)
fig.text(0.5, -0.02, 'Each dot = one airline-quarter. Fuel cost ratio = quarterly fuel spend ÷ operating revenue.',
         ha='center', fontsize=9, color='gray', style='italic')
plt.tight_layout()
save_fig('08_fuel_cost_vs_margin_scatter.png')

# ── CHART 9: Revenue Trend — Stacked Area by Airline ────────────────────────
yearly_rev = merged.groupby(['Year_Quarter', 'Airline_Name'])['operating_revenue'].sum().unstack(fill_value=0)
yearly_rev = yearly_rev / 1000  # → $millions

fig, ax = plt.subplots(figsize=(14, 7))
fig.patch.set_facecolor(BG)
airline_colors_list = [AIRLINE_COLORS.get(c, NAVY) for c in yearly_rev.columns]
ax.stackplot(yearly_rev.index, yearly_rev.T, labels=yearly_rev.columns,
             colors=airline_colors_list, alpha=0.82)
ax.set_xlabel('Quarter', labelpad=10)
ax.set_ylabel('Total Industry Revenue ($M)', labelpad=10)
ax.set_title('US Passenger Aviation: Total Quarterly Revenue by Airline (2009-Q1 – 2022-Q4)', pad=15)
tick_positions = [i for i, q in enumerate(yearly_rev.index) if q.endswith('Q1')]
ax.set_xticks(tick_positions)
ax.set_xticklabels([yearly_rev.index[i][:4] for i in tick_positions], fontsize=10)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'${x:,.0f}M'))
ax.legend(loc='upper left', fontsize=8, ncol=2)
ax.set_facecolor(BG)
ax.grid(axis='y', alpha=0.2, color=CHARCOAL)
ax.spines[['top', 'right']].set_visible(False)
plt.tight_layout()
save_fig('09_stacked_revenue_by_airline.png')

# ─────────────────────────────────────────────────────────────────────────────
# 4. PRINT SUMMARY REPORT
# ─────────────────────────────────────────────────────────────────────────────

print("\n" + "=" * 60)
print("  ANALYSIS RESULTS SUMMARY")
print("=" * 60)

print("\n-- Q1: 14-Year Weighted Operating Profit Margin Ranking --")
print(q1.to_string(index=False))

print("\n-- Industry Period Comparison --")
print(period_summary.to_string(index=False))

print("\n-- Q4: CARES Act Distortion (2020-Q2 to 2021-Q2) --")
print(q4.to_string(index=False))

print("\n-- Q5: Recovery Speed --")
print(q5.to_string(index=False))

print("\n-- Oil Shock: Loss Probability by WTI Bucket --")
print(oil_analysis[['Oil_Bucket', 'Avg_Oil_Price', 'Loss_Probability', 'Avg_Op_Income_K', 'Quarter_Count']].to_string(index=False))

print("\n-- Pearson Correlation (WTI Oil & COVID vs. Financials) --")
print(corr_matrix[['WTI_Oil_Price', 'COVID_Cases_M']].to_string())

print("\n" + "=" * 60)
print("  ALL DONE — charts saved to python/plots/")
print(f"  CSV tables saved to python/")
print("=" * 60)
