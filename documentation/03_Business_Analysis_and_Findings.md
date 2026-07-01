# Stage 3: Business Analysis and Findings — Skies Under Pressure

This section presents the empirical findings of our analysis, integrating the outputs of our SQL and Python pipelines to answer the 7 core business questions.

---

## 1. Operating Profit Margin Ranking (Objective 1)
To compare carriers of different sizes fairly, we rank them by **Weighted Operating Margin** (Total Operating Income / Total Operating Revenue) across the 2009–2022 timeline:

| Rank | Airline Name | Total Operating Income ($) | Total Operating Revenue ($) | Weighted Operating Margin | Average Quarterly Margin |
|---|---|---|---|---|---|
| **1** | Allegiant Airlines | 2,004,462,920 | 17,089,211,000 | **11.73%** | 9.57% |
| **2** | Alaska Airlines | 6,474,865,000 | 80,026,901,000 | **8.09%** | 3.30% |
| **3** | Delta Airlines | 40,909,498,000 | 511,941,627,000 | **7.99%** | 0.97% |
| **4** | Southwest Airlines | 17,470,403,000 | 243,285,408,000 | **7.18%** | 6.46% |
| **5** | Hawaiian Airlines | 1,518,639,240 | 28,748,645,000 | **5.28%** | 4.38% |
| **6** | JetBlue Airlines | 4,004,039,160 | 81,786,288,000 | **4.90%** | 3.01% |
| **7** | Spirit Airlines | 1,476,339,050 | 31,826,265,000 | **4.64%** | 2.82% |
| **8** | United Airlines | 14,105,015,400 | 453,207,144,000 | **3.11%** | 0.91% |
| **9** | Frontier Airlines | 488,328,380 | 24,981,992,000 | **1.95%** | 1.01% |
| **10** | American Airlines | 3,437,026,150 | 446,401,682,000 | **0.77%** | -0.34% |

### Economic Interpretation:
- **Niche Market Protection**: Ultra-low-cost carrier (ULCC) Allegiant achieved the highest weighted margin (11.73%). Allegiant focuses on underserved routes connecting small cities to leisure destinations (e.g. Fargo to Las Vegas). By operating with low flight frequencies (often only 2-3 times per week) on high-demand days, it minimizes fixed overheads.
- **Legacy Operating Leverage**: Legacy network carriers (American, United, Delta) must maintain large hub infrastructures, complex hub-and-spoke schedules, and diverse aircraft fleets. This results in high fixed costs. American Airlines ranked last with a thin weighted margin of 0.77% and a negative average quarterly margin (-0.34%), reflecting its high debt load and labor costs.

---

## 2. Oil Price Shock Correlation (Objective 2)
The global Pearson correlation coefficients between WTI Crude Oil Price Averages and airline financial metrics are:
- **Oil Price vs. Operating Income**: $r = 0.0755$
- **Oil Price vs. Operating Margin**: $r = 0.2555$

### Economic Interpretation:
A positive correlation is counterintuitive because rising oil prices increase jet fuel expenses, which should decrease profits. However, this positive correlation points to a **demand-pull inflation** effect. 

Rising oil prices are typically driven by strong global macroeconomic expansion. During these periods, consumer confidence and business activity are high. This robust passenger demand allows airlines to raise ticket prices and pass fuel surcharges onto customers. Conversely, when oil prices collapse, it is often a leading indicator of global recessions (e.g. 2009 and 2020), during which passenger demand collapses, causing steep airline losses despite low fuel costs.

---

## 3. COVID-19 Operating Income Collapse (Objective 3)
The absolute drop in average quarterly operating income between the `Pre_COVID` baseline and the `COVID_Shock` period is shown below:

| Airline Name | Pre-COVID Avg ($) | COVID Shock Avg ($) | Operating Income Collapse ($) |
|---|---|---|---|
| **American Airlines** | 495,992,825 | -3,139,067,022 | **-3,635,059,847** |
| **United Airlines** | 606,810,915 | -2,405,267,923 | **-3,012,078,839** |
| **Delta Airlines** | 106,270,864 | -1,817,046,167 | **-2,880,317,030** |
| **Southwest Airlines** | 473,083,750 | -1,279,941,250 | **-1,753,025,000** |
| **Alaska Airlines** | 165,302,227 | -579,914,250 | **-745,216,477** |
| **JetBlue Airlines** | 224,964,967 | -406,299,167 | **-631,264,134** |
| **Spirit Airlines** | 86,758,228 | -174,755,000 | **-261,513,228** |
| **Hawaiian Airlines** | 86,211,940 | -148,100,167 | **-234,312,107** |
| **Frontier Airlines** | 41,313,911 | -127,869,200 | **-169,183,111** |
| **Allegiant Airlines** | 49,610,653 | -44,399,428 | **-94,010,081** |

### Economic Interpretation:
The scale of the collapse corresponds directly to airline size and network complexity. Legacy network carriers suffered multi-billion dollar quarterly declines because international routes and high-margin corporate business travel were completely shut down. Low-cost and ultra-low-cost carriers (LCCs/ULCCs) suffered smaller absolute declines because their simpler domestic networks were easier to scale down.

---

## 4. CARES Act Distortion Gap (Objective 4)
Comparing Average Net Income vs. Average Operating Income during the CARES Act window (`2020-Q2` to `2021-Q2`) reveals the bailout distortion gap:

| Rank | Airline Name | Avg Net Income ($) | Avg Operating Income ($) | Bailout Distortion Gap ($) |
|---|---|---|---|---|
| **1** | American Airlines | -1,489,051,400 | -3,259,713,192 | **1,770,661,792** |
| **2** | United Airlines | -1,430,786,400 | -2,691,985,692 | **1,261,199,292** |
| **3** | Southwest Airlines | -503,330,600 | -1,438,369,200 | **935,038,600** |
| **4** | Alaska Airlines | -201,365,600 | -581,660,600 | **380,295,000** |
| **5** | JetBlue Airlines | -239,949,520 | -521,822,556 | **281,873,036** |
| **6** | Hawaiian Airlines | -89,520,380 | -202,935,736 | **113,415,356** |
| **7** | Frontier Airlines | -47,975,440 | -144,604,280 | **96,628,840** |
| **8** | Spirit Airlines | -173,074,380 | -224,402,496 | **51,328,116** |
| **9** | Allegiant Airlines | -13,546,420 | -60,197,862 | **46,651,442** |
| **10** | Delta Airlines | -2,042,393,200 | -1,676,333,400 | **-366,059,800** |

### Policy Interpretation:
The **Bailout Distortion Gap** shows how much government cash support altered reported corporate net profits. 
- For American Airlines, the distortion averaged **$1.77 billion per quarter**, hiding more than half of its true operational losses.
- Delta Air Lines is a notable exception, showing a negative gap. This indicates that Delta recognized severe asset write-downs and early retirement expenses for older fleets during this period, which were recorded in net income but excluded from operations.

---

## 5. Post-COVID Financial Recovery Speed (Objective 5)
The earliest quarter starting `2020-Q2` where each airline returned to positive operating income:

| Airline Name | First Positive Quarter | Recovery Speed |
|---|---|---|
| **Allegiant Airlines** | 2021-Q2 | 4 Quarters (Fastest) |
| **Alaska Airlines** | 2021-Q3 | 5 Quarters |
| **Delta Airlines** | 2021-Q3 | 5 Quarters |
| **JetBlue Airlines** | 2021-Q3 | 5 Quarters |
| **Southwest Airlines** | 2021-Q4 | 6 Quarters |
| **American Airlines** | 2022-Q2 | 8 Quarters |
| **Frontier Airlines** | 2022-Q2 | 8 Quarters |
| **United Airlines** | 2022-Q2 | 8 Quarters |
| **Hawaiian Airlines** | 2022-Q3 | 9 Quarters |
| **Spirit Airlines** | Did not recover by 2022 | Unrecovered |

### Economic Interpretation:
Airlines focused on domestic leisure travel (Allegiant) recovered first due to the rapid return of US domestic tourist demand. Legacy carriers (American, United) required 8 quarters to recover due to their reliance on slower-recovering business and international travel. Spirit Airlines remained unprofitable through 2022, impacted by fuel cost inflation and pilot labor constraints.

---

## 6. Oil Price Loss Thresholds (Objective 6)
We calculate the frequency of loss quarters (operating income < 0) across WTI Crude Oil Price buckets:

| Oil Price Bucket ($/bbl) | Loss Quarters | Total Quarters | Loss Probability | Avg Quarterly Operating Income ($) |
|---|---|---|---|---|
| **Below 50** | 43 | 130 | **33.08%** | 53,706,167 |
| **50 to 80** | 45 | 230 | **19.57%** | 203,768,293 |
| **80 to 100** | 26 | 140 | **18.57%** | 153,550,990 |
| **100 Plus** | 10 | 60 | **16.67%** | 275,716,146 |

### Economic Interpretation:
Airline loss probability is highest (33.08%) when WTI crude is below $50/bbl. This occurs because cheap oil is a symptom of severe macroeconomic recessions (such as 2009 and 2020), which depress passenger demand and load factors, causing operational losses despite low fuel expenses.

---

## 7. Load Factor vs. Financial Recovery (Objective 7)
Comparing capacity utilization (load factor) and operating margins across the three periods:

- **Pre_COVID**: Average load factor was **83.2%** with stable operating margins (5% to 15% range).
- **COVID_Shock**: Average load factor crashed to **53.9%** (with 2020-Q2 dipping below 30% for many carriers), leading to deeply negative operating margins (averaging -45%).
- **Recovery**: Average load factors returned to **82.8%**, indicating passenger volume recovery. However, operating margins remained compressed compared to pre-COVID levels due to inflation in fuel and labor costs.
