# Week 2 — Feature Engineering Notes

Feature table: `data_clean/features_week2.csv`, one row per product-branch (30 products x 6 branches = 180 rows).

| feature | how it's built | why |
|---|---|---|
| avg_monthly_units | mean of monthly `sales_orders_lines.quantity` | baseline demand level |
| demand_cv | std / mean of monthly units | volatility -- flags erratic vs steady demand |
| demand_volatility_tier | cv bucketed: stable / moderate / volatile | quick filter for Phase 3 forecast-method choice |
| days_of_safety_stock | safety_stock / avg_daily_units | deliberately uses `safety_stock` (hundreds), not `current_stock` (inflated, see stock_anomaly_investigation.md) |
| reorder_covers_lead_time | reorder_level/avg_daily_units >= lead_time_days | flags SKUs where the reorder trigger may fire too late relative to supplier lead time |

## Distribution of volatility tiers

| demand_volatility_tier   |   count |
|:-------------------------|--------:|
| moderate                 |     180 |

## Products where the reorder point may not cover lead time

77 of 180 product-branch combos flagged -- candidates for the reorder-point-optimisation task in Phase 3.
