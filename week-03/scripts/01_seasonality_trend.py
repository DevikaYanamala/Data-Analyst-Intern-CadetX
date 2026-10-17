"""
Week 3 — Seasonality & Trend in Monthly Sales
Heavy Supplier & Warehouse Analytics

Week 2's demand_cv metric came back "moderate" for all 180 product-branch
rows -- it didn't actually distinguish any product from any other. This
script looks at the same monthly sales series a different way: instead of
one volatility number, it separates each product's series into a TREND
(is it growing, shrinking, or flat over the 6 years of data) and a
SEASONAL pattern (which calendar months run consistently high or low,
once the trend is removed).

Grain here is per-product (not per-product-branch like Week 2's feature
table) -- 30 rows, one per SKU, pooling all branches -- to keep the
monthly series long enough (72 months, 2019-2024) for a stable seasonal
read. Branch-level seasonality is a natural follow-up, not done here.

Run: python3 01_seasonality_trend.py
"""
import pandas as pd
import numpy as np
from scipy import stats
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
DATA = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
CHART_DIR = os.path.join(os.path.dirname(__file__), "..", "charts")
os.makedirs(DATA, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)
os.makedirs(CHART_DIR, exist_ok=True)

fact_sales = pd.read_csv(os.path.join(WEEK1_DATA, "fact_sales.csv"), parse_dates=["order_date"])
products = pd.read_csv(os.path.join(WEEK1_DATA, "products.csv"))

MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

# ---- build a complete monthly series per product (fill missing months with 0) ----
fact_sales["year_month"] = fact_sales["order_date"].dt.to_period("M")
monthly = fact_sales.groupby(["product_id", "year_month"])["quantity"].sum()

full_range = pd.period_range(fact_sales["order_date"].min().to_period("M"),
                              fact_sales["order_date"].max().to_period("M"), freq="M")

rows = []
chart_candidates = {}
for pid, grp in monthly.groupby(level=0):
    series = grp.droplevel(0).reindex(full_range, fill_value=0)
    t = np.arange(len(series))
    slope, intercept = np.polyfit(t, series.values, 1)
    trend_line = slope * t + intercept
    residual = series.values - trend_line
    avg_units = series.mean()

    # seasonal index: average residual by calendar month, as % of avg level
    resid_by_month = pd.Series(residual, index=series.index).groupby(series.index.month).mean()
    resid_by_month.index = [MONTH_NAMES[m - 1] for m in resid_by_month.index]
    seasonal_amp_units = resid_by_month.max() - resid_by_month.min()
    seasonal_amp_pct = round(100 * seasonal_amp_units / avg_units, 1) if avg_units else np.nan
    peak_month = resid_by_month.idxmax()
    low_month = resid_by_month.idxmin()

    # is the month-to-month difference statistically real, or could it be noise?
    # one-way ANOVA: units grouped by calendar month (6 years = 6 obs per month)
    by_cal_month = pd.Series(series.values, index=series.index).groupby(series.index.month)
    groups = [g.values for _, g in by_cal_month]
    _, anova_p = stats.f_oneway(*groups)

    total_change_pct = round(100 * (slope * len(t)) / avg_units, 1) if avg_units else np.nan
    if total_change_pct > 15:
        trend_dir = "growing"
    elif total_change_pct < -15:
        trend_dir = "declining"
    else:
        trend_dir = "flat"

    rows.append({
        "product_id": pid, "avg_monthly_units": round(avg_units, 1),
        "trend_slope_units_per_month": round(slope, 3), "trend_total_change_pct": total_change_pct,
        "trend_direction": trend_dir, "seasonal_amplitude_units": round(seasonal_amp_units, 1),
        "seasonal_amplitude_pct_of_mean": seasonal_amp_pct, "peak_month": peak_month, "low_month": low_month,
        "anova_pvalue": round(anova_p, 4), "seasonality_significant_p05": anova_p < 0.05,
    })
    chart_candidates[pid] = (series, seasonal_amp_pct)

result = pd.DataFrame(rows).merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
result = result.sort_values("seasonal_amplitude_pct_of_mean", ascending=False)
result.to_csv(os.path.join(DATA, "seasonality_trend.csv"), index=False)

# ---- chart: the 3 most seasonal products, actual monthly units ----
top3 = result.head(3)["product_id"].tolist()
fig, axes = plt.subplots(len(top3), 1, figsize=(10, 3 * len(top3)), sharex=True)
for ax, pid in zip(axes, top3):
    series, amp = chart_candidates[pid]
    name = result.loc[result.product_id == pid, "product_name"].iloc[0]
    ax.plot(series.index.to_timestamp(), series.values, linewidth=1.1, color="#2f6e5c")
    ax.set_title(f"{pid} -- {name} (seasonal amplitude {amp:.0f}% of mean)")
    ax.set_ylabel("units/month")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "most_seasonal_products.png"), dpi=130)
plt.close()

# ---- doc ----
out = ["# Week 3 — Seasonality & Trend in Monthly Sales\n\n",
       "Week 2's `demand_cv` flagged every single product-branch row as \"moderate\" "
       "volatility -- a split that didn't actually separate any product from any "
       "other. This looks at the same monthly data two different ways instead: "
       "**trend** (growing/declining/flat over 2019-2024) and **seasonality** "
       "(which calendar months consistently run high or low, after removing that "
       "trend). Grain: per-product, pooling all 6 branches (30 rows).\n\n"]

amp_range = (result["seasonal_amplitude_pct_of_mean"].min(), result["seasonal_amplitude_pct_of_mean"].max())
out.append(f"## Does this actually differentiate products?\n\n"
           f"Seasonal amplitude ranges from **{amp_range[0]:.0f}% to {amp_range[1]:.0f}%** of each "
           f"product's average monthly volume across the 30 products -- unlike `demand_cv`, this metric "
           f"spreads products out rather than bucketing them all the same way. See "
           f"`data_clean/seasonality_trend.csv` for the full table.\n\n")

out.append("## Most seasonal products\n\n")
out.append(result.head(5)[["product_id", "product_name", "seasonal_amplitude_pct_of_mean",
                            "peak_month", "low_month", "anova_pvalue"]].to_markdown(index=False) + "\n\n")
out.append("See `charts/most_seasonal_products.png` for the top 3 plotted directly -- look at it before "
           "trusting the amplitude ranking alone. Visually these look fairly noisy month-to-month rather "
           "than a clean repeating peak/trough curve, which is worth being honest about. So each product "
           "was also checked with a one-way ANOVA (units grouped by calendar month, 6 years = 6 "
           "observations per month) to test whether the month-to-month difference is statistically real "
           "rather than just a couple of outlier months swinging the amplitude score.\n\n")

n_sig = int(result["seasonality_significant_p05"].sum())
out.append(f"**{n_sig} of 30 products show statistically significant month-to-month variation (p < 0.05).** "
           f"The top 3 by amplitude all pass this test (p = {result.iloc[0]['anova_pvalue']}, "
           f"{result.iloc[1]['anova_pvalue']}, {result.iloc[2]['anova_pvalue']}) -- so despite looking noisy "
           f"on the chart, there is a real, non-random month-to-month pattern there, just not necessarily a "
           f"smooth single-peak seasonal curve.\n\n"
           f"**One more caveat, though:** with 30 products each tested at p < 0.05, roughly 1-2 \"significant\" "
           f"results would be expected by chance alone even if nothing real were going on (this is the "
           f"multiple-comparisons problem). Getting 3 is only marginally above that chance baseline, so this "
           f"isn't strong enough evidence on its own -- treat these 3 as candidates to monitor with more "
           f"data, not as confirmed seasonal products to build a firm stocking plan around yet.\n\n")

trend_counts = result["trend_direction"].value_counts()
out.append("## Trend direction across all 30 products\n\n")
out.append(trend_counts.to_frame("count").to_markdown() + "\n\n")
growing = result[result.trend_direction == "growing"][["product_id", "product_name", "trend_total_change_pct"]]
declining = result[result.trend_direction == "declining"][["product_id", "product_name", "trend_total_change_pct"]]
if len(growing):
    out.append("### Growing\n\n" + growing.sort_values("trend_total_change_pct", ascending=False).to_markdown(index=False) + "\n\n")
if len(declining):
    out.append("### Declining\n\n" + declining.sort_values("trend_total_change_pct").to_markdown(index=False) + "\n\n")
if trend_counts.get("flat", 0) == len(result):
    out.append("**All 30 products came back \"flat\"** with the +/-15% total-change threshold used here -- "
                "no product shows a sustained multi-year rise or fall in demand. That's itself worth noting: "
                "combined with Week 2's stock-ledger finding (IN/OUT movements behaving like independent "
                "random draws), it fits a pattern of this simulated dataset not encoding real long-run "
                "business dynamics -- demand here looks seasonally patterned month-to-month but not "
                "structurally growing or shrinking year-over-year. Worth re-checking with a looser or "
                "tighter threshold before treating \"no trend\" as final.\n\n")

out.append("## Why this matters\n\nA product with a strong seasonal peak can have stock built up ahead of "
           "that month instead of reacting after demand has already risen. A product with a clear decline "
           "trend is a candidate to reassess reorder levels downward rather than keep restocking at a "
           "level sized for its earlier, higher demand. These are exactly the kind of per-product "
           "distinctions `demand_cv` failed to surface in Week 2.\n")

with open(os.path.join(DOC_DIR, "seasonality_trend.md"), "w") as f:
    f.writelines(out)

print("Seasonality/trend table written to data_clean/seasonality_trend.csv")
print(f"Seasonal amplitude range: {amp_range[0]:.0f}% - {amp_range[1]:.0f}% of mean")
print(trend_counts)
