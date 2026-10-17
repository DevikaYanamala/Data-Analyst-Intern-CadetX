# Week 3 — Seasonality & Trend in Monthly Sales

Week 2's `demand_cv` flagged every single product-branch row as "moderate" volatility -- a split that didn't actually separate any product from any other. This looks at the same monthly data two different ways instead: **trend** (growing/declining/flat over 2019-2024) and **seasonality** (which calendar months consistently run high or low, after removing that trend). Grain: per-product, pooling all 6 branches (30 rows).

## Does this actually differentiate products?

Seasonal amplitude ranges from **14% to 38%** of each product's average monthly volume across the 30 products -- unlike `demand_cv`, this metric spreads products out rather than bucketing them all the same way. See `data_clean/seasonality_trend.csv` for the full table.

## Most seasonal products

| product_id   | product_name         |   seasonal_amplitude_pct_of_mean | peak_month   | low_month   |   anova_pvalue |
|:-------------|:---------------------|---------------------------------:|:-------------|:------------|---------------:|
| P020         | Pivot Pin PP-12      |                             38.4 | Aug          | Jun         |         0.0054 |
| P016         | Radiator RD-250      |                             34.6 | Jul          | Feb         |         0.0224 |
| P028         | Light Assembly LA-18 |                             34.4 | Mar          | Feb         |         0.0333 |
| P009         | Starter Motor SM-700 |                             31   | Aug          | Feb         |         0.0786 |
| P019         | Swing Motor SWM-350  |                             29.4 | Dec          | Apr         |         0.1317 |

See `charts/most_seasonal_products.png` for the top 3 plotted directly -- look at it before trusting the amplitude ranking alone. Visually these look fairly noisy month-to-month rather than a clean repeating peak/trough curve, which is worth being honest about. So each product was also checked with a one-way ANOVA (units grouped by calendar month, 6 years = 6 observations per month) to test whether the month-to-month difference is statistically real rather than just a couple of outlier months swinging the amplitude score.

**3 of 30 products show statistically significant month-to-month variation (p < 0.05).** The top 3 by amplitude all pass this test (p = 0.0054, 0.0224, 0.0333) -- so despite looking noisy on the chart, there is a real, non-random month-to-month pattern there, just not necessarily a smooth single-peak seasonal curve.

**One more caveat, though:** with 30 products each tested at p < 0.05, roughly 1-2 "significant" results would be expected by chance alone even if nothing real were going on (this is the multiple-comparisons problem). Getting 3 is only marginally above that chance baseline, so this isn't strong enough evidence on its own -- treat these 3 as candidates to monitor with more data, not as confirmed seasonal products to build a firm stocking plan around yet.

## Trend direction across all 30 products

| trend_direction   |   count |
|:------------------|--------:|
| flat              |      30 |

**All 30 products came back "flat"** with the +/-15% total-change threshold used here -- no product shows a sustained multi-year rise or fall in demand. That's itself worth noting: combined with Week 2's stock-ledger finding (IN/OUT movements behaving like independent random draws), it fits a pattern of this simulated dataset not encoding real long-run business dynamics -- demand here looks seasonally patterned month-to-month but not structurally growing or shrinking year-over-year. Worth re-checking with a looser or tighter threshold before treating "no trend" as final.

## Why this matters

A product with a strong seasonal peak can have stock built up ahead of that month instead of reacting after demand has already risen. A product with a clear decline trend is a candidate to reassess reorder levels downward rather than keep restocking at a level sized for its earlier, higher demand. These are exactly the kind of per-product distinctions `demand_cv` failed to surface in Week 2.
