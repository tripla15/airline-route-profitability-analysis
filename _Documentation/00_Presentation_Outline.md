# Graduation Presentation Outline — Skies Under Pressure

This outline is designed for your team's live presentation to the DEPI judging panel. It structures the slides to show visual progress, clear methodology, and business findings without cluttering the screen with text.

---

## Slide 1: Title Slide
- **Visual**: High-resolution image of a commercial airliner grounded on a tarmac during sunset (represents both financial sunset/pressure and fleet groundings).
- **Slide Text**:
  * Title: **Skies Under Pressure: Macroeconomic Shocks and US Aviation Stability (2009–2022)**
  * Subtitle: DEPI Graduation Project — Data Analytics Track
  * Team Members: [Names of Team Members]
  * Supervisor: [Supervisor Name]
- **Speaker Notes (Ahmed)**:
  * "Good morning/afternoon, esteemed judges. Today, our team is presenting our graduation project, 'Skies Under Pressure'. We analyze the operational resilience of the US aviation sector when faced with two of the most severe external shocks in modern history: the 2014-2015 oil market crash and the COVID-19 pandemic."

---

## Slide 2: Introduction & Motivation
- **Visual**: Timeline diagram (2009–2022) highlighting:
  * 2009–2014: Post-Recession Baseline
  * 2014–2015: WTI Crude Oil Price Collapse
  * 2020–2021: COVID-19 Global Disruption & CARES Act
- **Slide Text**:
  * **Research Problem**: How do external energy shocks (fuel costs) and public health crises (demand collapse) interact to destabilize airline operating margins?
  * **Why it matters**: Jet fuel accounts for 20-30% of airline costs; pandemic demand groundings represent a total revenue stoppage. Understanding these relationships is critical for carrier survival.
- **Speaker Notes**:
  * "Instead of looking at financials in a vacuum, we built a unified framework to isolate cause-and-effect relationships. We mapped external variables—WTI crude oil prices and US COVID-19 tracking numbers—directly to airline accounting margins across 14 years."

---

## Slide 3: Project Methodology & Data Architecture
- **Visual**: Data connection flow diagram showing:
  * BTS Financials (Quarterly) $\rightarrow$ Joined on `Date_Key + Airline_Name`
  * WTI Crude Prices (Daily $\rightarrow$ Quarterly Average) $\rightarrow$ Joined on `Date_Key`
  * COVID cases (Daily Cumulative $\rightarrow$ Max Snapshot) $\rightarrow$ Joined on `Date_Key`
- **Slide Text**:
  * **Unified Aggregation Grain**: Normalized all data to **Airline-Quarter** (`Year_Quarter`, e.g., `2020-Q2`) using integer `Date_Key` to prevent row-multiplication join errors.
  * **Primary Target Carriers**: 10 major US airlines representing different business models (Legacy Network, Low-Cost, Ultra-Low-Cost).
  * **Bailout Adjustment**: Identified the CARES Act period (`2020-Q2` to `2021-Q2`) where federal funding distorted net income. Designated `Operating Profit/Loss` as our baseline operational metric.
- **Speaker Notes**:
  * "Our biggest technical challenge was joining datasets of different grains—daily oil prices, daily COVID cases, and quarterly financials. We solved this by developing a central dimension table, `Dim_Time`, and aggregating all global variables to the unified quarter grain before executing joins."

---

## Slide 4: Datasets & Preprocessing
- **Visual**: Carousel of three raw screenshots vs. cleaned data tables.
  * Left: Messy BTS reporting sheet.
  * Center: Raw Johns Hopkins daily cumulative COVID case CSV.
  * Right: WTI Crude Daily prices.
- **Slide Text**:
  * **BTS Financials (Form 41)**: Extracted core revenues, operating profits, net income, fuel costs, and load factors.
  * **EIA Crude Oil Prices**: Standardized WTI daily prices into quarterly averages.
  * **JHU COVID-19 Tracker**: Filtered for US, computed maximum quarterly cumulative confirmed cases.
  * *Note*: Skytrax customer satisfaction review data was dropped due to high chronological variance and small sample sizes for target carriers.
- **Speaker Notes**:
  * "Preprocessing took massive effort. We filtered out international carriers, resolved naming inconsistencies (like 'Delta Airlines' vs 'Delta Air Lines'), handled missing values, and created custom classification columns like CARES flags and oil price buckets."

---

## Slide 5: Analytical Tools & Implementations
- **Visual**: A grid showing logos of the 5 tools used, with brief outputs of each:
  * **Excel**: Power Pivot star schema model.
  * **SQL**: DDL schemas and CTE query files.
  * **Python**: Pandas programmatic cleaning pipeline.
  * **Tableau / Power BI**: Dashboard screenshots.
- **Slide Text**:
  * **Standalone Deliverable Rule**: Each of the 5 tools was built as a complete standalone system handling its own loading, cleaning, modeling, and dashboarding.
- **Speaker Notes**:
  * "To demonstrate end-to-end technical competency, we didn't just export cleaned data from one tool to another. Each tool contains its own independent pipeline, starting from raw or semi-processed sources, ensuring cross-tool consistency."

---

## Slide 6: Finding 1 — Airline Profitability Ranking
- **Visual**: Horizontal bar chart showing Weighted Operating Profit Margin by airline (Plot 1 from Python/Excel).
- **Slide Text**:
  * **Top Performer**: Allegiant Airlines (11.73% margin).
  * **Legacy Network Performance**: Delta (7.99%), United (3.11%), American (0.77%).
  * **Ultra-Low-Cost Compression**: Frontier (1.95%), Spirit (4.64%).
- **Speaker Notes**:
  * "Our analysis shows that smaller niche airlines, like Allegiant, maintained the highest profit margins over the 14-year period due to their low-utilization, low-fixed-cost business model. Legacy carriers, despite having massive revenues, struggled with high fixed overheads, with American Airlines ranking lowest with a thin 0.77% margin."

---

## Slide 7: Finding 2 — WTI Crude Oil Price Loss Thresholds
- **Visual**: Dual-axis bar/line chart of Loss Probability vs. WTI Price Bucket (Plot 2).
- **Slide Text**:
  * **Under $50/bbl**: Loss probability is **33.08%** (driven by the 2009 recession and 2020 COVID collapses).
  * **$50 to $80/bbl**: Sweet spot for airlines with only **19.57%** loss probability.
  * **Over $100/bbl**: Counterintuitively, loss probability is lowest at **16.67%** (driven by strong macroeconomic demand periods that support high ticket prices).
- **Speaker Notes**:
  * "Surprisingly, the highest probability of airline operational losses occurred when WTI crude prices fell below $50 per barrel. This is because oil price collapses are lagging indicators of global demand recessions (like 2009 and 2020), which hurt airlines far worse than the fuel savings help them."

---

## Slide 8: Finding 3 — COVID Shock & CARES Act Distortion
- **Visual**: Grouped column chart comparing Net Income vs. Operating Income during the CARES period (Plot 3).
- **Slide Text**:
  * **American Airlines**: Reported average Net Loss of **-$1.49M** vs. actual Operating Loss of **-$3.26M** (distortion of **$1.77M** per quarter).
  * **Bailout Gap**: Federal grants allowed net income to look significantly healthier than the underlying operating reality.
- **Speaker Notes**:
  * "During the COVID shock (2020-Q2 to 2021-Q2), the CARES Act injected billions of dollars into US carriers. This created a massive distortion. For example, American Airlines' reported net losses were cut in half compared to their actual operational losses, proving that net income was a misleading metric during the crisis."

---

## Slide 9: Finding 4 — Industry Recovery Dynamics
- **Visual**: Dual-axis time-series chart showing Load Factor vs. Operating Margin (2019-Q1 to 2022-Q4) (Plot 4).
- **Slide Text**:
  * **Deepest Collapse**: 2020-Q2 (Operating margins dropped to **-45.2%**, load factors crashed below **50%**).
  * **Fastest Recovery**: Allegiant recovered to positive operations first (2021-Q2), while Spirit did not recover by the end of 2022.
  * **Lagging Load Factor**: Profit margins recovered faster than load factors due to aggressive capacity cuts and increased average fares.
- **Speaker Notes**:
  * "In 2020-Q2, the industry experienced a near-total collapse. However, recovery was highly asymmetrical. Allegiant recovered by 2021-Q2, leveraging domestic leisure travel, while ultra-low-cost Spirit remained in operational deficit through 2022 due to severe cost inflation."

---

## Slide 10: Strategic Recommendations & Conclusion
- **Visual**: Clean Summary Table mapping:
  * **Macro Risk** $\rightarrow$ **Operational Strategy** $\rightarrow$ **Financial Impact**
- **Slide Text**:
  * **Fuel Hedging**: Dynamic fuel purchase contracts are critical, but must be paired with demand forecasting.
  * **Capacity Agility**: The ability to ground fleets quickly (Ultra-Low-Cost model) is safer in a demand collapse than maintaining massive networks (Legacy model).
  * **Liquidity Cushions**: Airlines must maintain cash reserves to withstand a minimum of 4 quarters of demand stoppage without relying on government intervention.
- **Speaker Notes**:
  * "In conclusion, our project demonstrates that demand shocks are far more dangerous to airlines than fuel price spikes. We recommend that carriers build flexible leasing networks and strong cash cushions. Thank you, and we now open the floor for any questions."
