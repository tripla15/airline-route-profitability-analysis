import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set style for publication-ready plots
sns.set_theme(style="whitegrid")
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 12,
    'axes.titlesize': 14,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.titlesize': 16,
    'figure.figsize': (10, 6)
})

# Define project color palette
NAVY = '#1f4e79'
TEAL = '#2a9d8f'
AMBER = '#c17c00'
CRIMSON = '#b23a48'
CHARCOAL = '#2f2f2f'
BACKGROUND = '#f7f7f5'

# Define directory paths
excel_path = r"F:\Engineering 2nd year\Extracurriculars\1. DEPI\Final Project\Excel\Master_Tables_file.xlsx"
output_dir = r"F:\Engineering 2nd year\Extracurriculars\1. DEPI\Final Project\python"
plots_dir = os.path.join(output_dir, "plots")

print("Loading Excel sheets...")
dim_time = pd.read_excel(excel_path, sheet_name="Dim_Time")
fact_fin = pd.read_excel(excel_path, sheet_name="Fact_Financials_Master")
oil_prices = pd.read_excel(excel_path, sheet_name="Oil_Prices_Avg_Qtr")
covid_cases = pd.read_excel(excel_path, sheet_name="covid_19_clean_complete")

# Clean and merge datasets
print("Merging data...")
merged = pd.merge(fact_fin, dim_time, on="Date_Key", how="left")

# Join with oil (drop Oil_Bucket from oil_prices to avoid duplicates)
oil_prices_clean = oil_prices.drop(columns=["Oil_Bucket"], errors="ignore")
merged = pd.merge(merged, oil_prices_clean, on="Date_Key", how="left")

# Join with COVID (fill missing with 0 for pre-COVID quarters)
merged = pd.merge(merged, covid_cases, on="Date_Key", how="left")
merged["Covid_US_Cases_Quarterly"] = merged["Covid_US_Cases_Quarterly"].fillna(0).astype(int)

# Create helper columns
merged["Operating_Margin"] = merged["operating_income"] / merged["operating_revenue"]

def get_period_group(qtr):
    year = int(qtr.split('-')[0])
    q = qtr.split('-')[1]
    if year < 2020:
        return "Pre_COVID"
    elif year == 2020:
        return "COVID_Shock"
    elif year == 2021:
        if q in ["Q1", "Q2"]:
            return "COVID_Shock"
        else:
            return "Recovery"
    else:  # year >= 2022
        return "Recovery"

merged["Period_Group"] = merged["Year_Quarter"].apply(get_period_group)

# ----------------- BUSINESS QUESTIONS ANALYSIS -----------------

print("Analyzing Business Questions...")

# Q1: Operating Profit Margin Ranking
q1_rank = merged.groupby("Airline_Name").agg(
    total_revenue=("operating_revenue", "sum"),
    total_operating_income=("operating_income", "sum"),
    avg_load_factor=("load_factor", "mean")
).reset_index()
q1_rank["weighted_operating_margin"] = q1_rank["total_operating_income"] / q1_rank["total_revenue"]
q1_rank = q1_rank.sort_values("weighted_operating_margin", ascending=False).reset_index(drop=True)

# Q2: Oil Price Shock Correlation
q2_corr = merged[["Oil_Price_Qtr_Avg", "operating_income", "Operating_Margin"]].corr().iloc[0]

# Q3: COVID Operating Income Collapse
q3_collapse = merged.groupby(["Airline_Name", "Period_Group"])["operating_income"].mean().unstack().reset_index()
q3_collapse["COVID_Collapse_Value"] = q3_collapse["COVID_Shock"] - q3_collapse["Pre_COVID"]
q3_collapse = q3_collapse.sort_values("COVID_Collapse_Value", ascending=True).reset_index(drop=True)

# Q4: CARES Act Distortion Gap
cares_data = merged[merged["CARES_FLAG"] == "CARES_Period"]
q4_cares = cares_data.groupby("Airline_Name").agg(
    avg_net_income=("net_income", "mean"),
    avg_operating_income=("operating_income", "mean")
).reset_index()
q4_cares["Bailout_Distortion_Gap"] = q4_cares["avg_net_income"] - q4_cares["avg_operating_income"]
q4_cares = q4_cares.sort_values("Bailout_Distortion_Gap", ascending=False).reset_index(drop=True)

# Q5: COVID Recovery Speed (first positive quarter after 2020-Q2)
post_shock_start = merged[merged["Date_Key"] >= 46]  # Date_Key 46 corresponds to 2020-Q2
recovered_airlines = []
for name, group in post_shock_start.groupby("Airline_Name"):
    sorted_group = group.sort_values("Date_Key")
    pos_quarters = sorted_group[sorted_group["operating_income"] > 0]
    if not pos_quarters.empty:
        first_pos_qtr = pos_quarters.iloc[0]["Year_Quarter"]
        recovered_airlines.append({"Airline_Name": name, "First_Positive_Quarter": first_pos_qtr, "Recovery_Sort_Key": pos_quarters.iloc[0]["Date_Key"]})
    else:
        recovered_airlines.append({"Airline_Name": name, "First_Positive_Quarter": "Did not recover by 2022", "Recovery_Sort_Key": 999})
q5_recovery = pd.DataFrame(recovered_airlines).sort_values("Recovery_Sort_Key").drop(columns=["Recovery_Sort_Key"]).reset_index(drop=True)

# Q6: Oil Price Loss Thresholds
merged["Is_Loss_Quarter"] = np.where(merged["operating_income"] < 0, 1, 0)
# Reorder Oil_Bucket to be logical
bucket_order = ["Below_50", "50_to_80", "80_to_100", "100_Plus"]
merged["Oil_Bucket"] = pd.Categorical(merged["Oil_Bucket"], categories=bucket_order, ordered=True)
q6_oil_thresholds = merged.groupby("Oil_Bucket", observed=False).agg(
    loss_quarter_count=("Is_Loss_Quarter", "sum"),
    total_quarter_count=("Is_Loss_Quarter", "count"),
    avg_operating_income=("operating_income", "mean")
).reset_index()
q6_oil_thresholds["Loss_Probability"] = q6_oil_thresholds["loss_quarter_count"] / q6_oil_thresholds["total_quarter_count"]

# Q7: Load Factor vs Finance Recovery
q7_load_finance = merged.groupby(["Airline_Name", "Period_Group"]).agg(
    avg_load_factor=("load_factor", "mean"),
    avg_operating_margin=("Operating_Margin", "mean")
).unstack().reset_index()

# Save analytical tables
print("Saving tables...")
q1_rank.to_csv(os.path.join(output_dir, "py_q1_margins_ranking.csv"), index=False)
q3_collapse.to_csv(os.path.join(output_dir, "py_q3_covid_collapse.csv"), index=False)
q4_cares.to_csv(os.path.join(output_dir, "py_q4_cares_distortion.csv"), index=False)
q5_recovery.to_csv(os.path.join(output_dir, "py_q5_recovery_speed.csv"), index=False)
q6_oil_thresholds.to_csv(os.path.join(output_dir, "py_q6_oil_loss_thresholds.csv"), index=False)

# ----------------- VISUALIZATIONS GENERATION -----------------

print("Generating plots...")

# Chart 1: Operating margins ranking
plt.figure(figsize=(10, 6))
sns.barplot(
    data=q1_rank,
    y="Airline_Name",
    x="weighted_operating_margin",
    color=TEAL,
    edgecolor="black"
)
plt.axvline(0, color="red", linestyle="--", linewidth=1.2)
plt.title("US Passenger Airlines: Weighted Operating Profit Margin (2009–2022)")
plt.xlabel("Weighted Operating Profit Margin (Operating Income / Revenue)")
plt.ylabel("Airline Name")
for idx, row in q1_rank.iterrows():
    plt.text(
        row["weighted_operating_margin"] + (0.002 if row["weighted_operating_margin"] >= 0 else -0.015),
        idx,
        f"{row['weighted_operating_margin'] * 100:.2f}%",
        va='center',
        ha='left',
        fontsize=9,
        weight='bold'
    )
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "01_operating_margins_ranking.png"), dpi=300)
plt.close()

# Chart 2: Oil Price loss thresholds
fig, ax1 = plt.subplots(figsize=(10, 6))
ax2 = ax1.twinx()
sns.barplot(
    data=q6_oil_thresholds,
    x="Oil_Bucket",
    y="Loss_Probability",
    color=AMBER,
    edgecolor="black",
    ax=ax1,
    alpha=0.85
)
ax2.plot(
    q6_oil_thresholds["Oil_Bucket"],
    q6_oil_thresholds["avg_operating_income"] / 1e3,  # In Thousands
    color=CRIMSON,
    marker="o",
    linewidth=2.5,
    markersize=8
)
ax1.set_title("Airline Loss Probability & Average Profit by WTI Crude Oil Price Bucket")
ax1.set_xlabel("WTI Crude Oil Price Bucket ($ per barrel)")
ax1.set_ylabel("Loss Probability (Share of Quarters in Loss)", color=AMBER)
ax2.set_ylabel("Average Operating Income ($ Thousands)", color=CRIMSON)
ax1.tick_params(axis='y', labelcolor=AMBER)
ax2.tick_params(axis='y', labelcolor=CRIMSON)
ax1.yaxis.set_major_formatter(lambda x, pos: f"{x * 100:.0f}%")
ax2.yaxis.set_major_formatter(lambda x, pos: f"{x / 1e3:.0f}k" if abs(x) >= 1e3 else f"{x:.0f}")
ax2.axhline(0, color="gray", linestyle="--", linewidth=1)
for idx, val in enumerate(q6_oil_thresholds["Loss_Probability"]):
    ax1.text(idx, val - 0.05, f"{val * 100:.1f}%", ha='center', color='white', weight='bold')
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "02_oil_vs_loss_probability.png"), dpi=300)
plt.close()

# Chart 3: CARES Act distortion gap
plt.figure(figsize=(11, 7))
melted_cares = pd.melt(
    q4_cares,
    id_vars="Airline_Name",
    value_vars=["avg_net_income", "avg_operating_income"],
    var_name="Metric",
    value_name="Value"
)
melted_cares["Value"] = melted_cares["Value"] / 1e6  # Convert to Millions
melted_cares["Metric"] = melted_cares["Metric"].replace({
    "avg_net_income": "Average Net Income (Post-Bailout)",
    "avg_operating_income": "Average Operating Income (True Operations)"
})

sns.barplot(
    data=melted_cares,
    x="Airline_Name",
    y="Value",
    hue="Metric",
    palette=[TEAL, CRIMSON],
    edgecolor="black"
)
plt.title("CARES Act Distortion Window: Net Income vs. Operating Profit/Loss (2020-Q2 to 2021-Q2)")
plt.xlabel("Airline Name")
plt.ylabel("Quarterly Average Value ($ Millions)")
plt.xticks(rotation=45, ha='right')
plt.axhline(0, color="black", linewidth=0.8)
plt.legend(title="Financial Metric", loc="upper right")
plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "03_cares_net_vs_operating_gap.png"), dpi=300)
plt.close()

# Chart 4: Load Factor vs. Operating Margin Recovery
timeline_avg = merged.groupby("Year_Quarter").agg(
    avg_load_factor=("load_factor", "mean"),
    avg_operating_margin=("Operating_Margin", "mean")
).reset_index()

timeline_covid = timeline_avg[timeline_avg["Year_Quarter"] >= "2019-Q1"].reset_index(drop=True)

fig, ax1 = plt.subplots(figsize=(12, 6.5))
ax2 = ax1.twinx()

ax1.plot(
    timeline_covid["Year_Quarter"],
    timeline_covid["avg_load_factor"],
    color=NAVY,
    marker="s",
    linewidth=2.5,
    label="Average Load Factor (Left Axis)"
)
ax2.plot(
    timeline_covid["Year_Quarter"],
    timeline_covid["avg_operating_margin"],
    color=TEAL,
    marker="D",
    linewidth=2.5,
    linestyle="--",
    label="Average Operating Margin (Right Axis)"
)

ax1.set_title("Industry Recovery Timeline: Average Load Factor vs. Operating Profit Margin (2019-Q1 to 2022-Q4)")
ax1.set_xlabel("Year and Quarter")
ax1.set_ylabel("Load Factor (Seats Filled)", color=NAVY)
ax2.set_ylabel("Operating Profit Margin", color=TEAL)

ax1.tick_params(axis='x', rotation=45)
ax1.tick_params(axis='y', labelcolor=NAVY)
ax2.tick_params(axis='y', labelcolor=TEAL)
ax1.yaxis.set_major_formatter(lambda x, pos: f"{x * 100:.0f}%")
ax2.yaxis.set_major_formatter(lambda x, pos: f"{x * 100:.0f}%")
ax2.axhline(0, color="gray", linestyle="-.", linewidth=1)

ax1.axvspan("2020-Q1", "2021-Q2", color='red', alpha=0.1, label="COVID Shock Period")
ax1.text("2020-Q3", 0.35, "COVID Shock & CARES Support Window", color=CRIMSON, weight='bold', ha='center')

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left")

plt.tight_layout()
plt.savefig(os.path.join(plots_dir, "04_load_factor_vs_operating_margin.png"), dpi=300)
plt.close()

print("\n--- Summary of Business Questions Results ---")
print("1. Ranking by Weighted Operating Margin:")
print(q1_rank[["Airline_Name", "weighted_operating_margin"]])
print("\n2. Oil Shock Correlation:")
print(f"Oil Price Qtr Avg vs. Operating Income Correlation: {q2_corr['operating_income']:.4f}")
print(f"Oil Price Qtr Avg vs. Operating Margin Correlation: {q2_corr['Operating_Margin']:.4f}")
print("\n3. COVID Collapse Value:")
print(q3_collapse[["Airline_Name", "COVID_Collapse_Value"]])
print("\n4. CARES Act Distortion Gap (Net - Operating):")
print(q4_cares[["Airline_Name", "Bailout_Distortion_Gap"]])
print("\n5. Recovery speed:")
print(q5_recovery)
print("\n6. Loss thresholds by oil bucket:")
print(q6_oil_thresholds)

print("\nAll scripts and visualizations generated successfully.")
