"""
Week 2 — Feature Engineering for Analytics
Heavy Supplier & Warehouse Analytics

Builds a per-product-branch feature table for later phases (demand
forecasting, stockout risk, reorder optimisation in Phase 3). Notably
avoids leaning on `current_stock` as an absolute level (see
stock_anomaly_investigation.md) -- features here use sales-side demand
signals and ratios that are more robust to that issue.

Run: python3 03_feature_engineering.py
"""
import pandas as pd
import numpy as np
import os

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
DATA = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")

fact_sales = pd.read_csv(os.path.join(WEEK1_DATA, "fact_sales.csv"), parse_dates=["order_date"])
fact_inv = pd.read_csv(os.path.join(WEEK1_DATA, "fact_inventory.csv"))
products = pd.read_csv(os.path.join(WEEK1_DATA, "products.csv"))

# ---- Demand signal: monthly units sold per product-branch ----
fact_sales["year_month"] = fact_sales["order_date"].dt.to_period("M")
monthly = fact_sales.groupby(["product_id", "branch_id", "year_month"])["quantity"].sum().reset_index()

demand_stats = monthly.groupby(["product_id", "branch_id"])["quantity"].agg(
    avg_monthly_units="mean", std_monthly_units="std", n_months_active="count"
).reset_index()
demand_stats["demand_cv"] = (demand_stats["std_monthly_units"] / demand_stats["avg_monthly_units"]).round(2)
demand_stats["avg_daily_units"] = (demand_stats["avg_monthly_units"] / 30.4).round(2)

# ---- Days of supply, using safety_stock/reorder_level (small, stable scale) instead of current_stock ----
inv_small = fact_inv[["product_id", "branch_id", "safety_stock", "reorder_level", "max_stock",
                       "criticality_level", "lead_time_days"]]
features = demand_stats.merge(inv_small, on=["product_id", "branch_id"], how="left")
features["days_of_safety_stock"] = (features["safety_stock"] / features["avg_daily_units"]).round(1)
features["reorder_covers_lead_time"] = (
    (features["reorder_level"] / features["avg_daily_units"]) >= features["lead_time_days"]
)

# ---- Demand volatility tier (useful for later safety-stock/forecast-method choice) ----
def volatility_tier(cv):
    if pd.isna(cv):
        return "unknown"
    if cv < 0.3:
        return "stable"
    elif cv < 0.6:
        return "moderate"
    return "volatile"
features["demand_volatility_tier"] = features["demand_cv"].apply(volatility_tier)

features = features.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
features.to_csv(os.path.join(DATA, "features_week2.csv"), index=False)

# ---- Doc ----
out = ["# Week 2 — Feature Engineering Notes\n\n",
       "Feature table: `data_clean/features_week2.csv`, one row per product-branch "
       "(30 products x 6 branches = 180 rows).\n\n",
       "| feature | how it's built | why |\n|---|---|---|\n",
       "| avg_monthly_units | mean of monthly `sales_orders_lines.quantity` | baseline demand level |\n",
       "| demand_cv | std / mean of monthly units | volatility -- flags erratic vs steady demand |\n",
       "| demand_volatility_tier | cv bucketed: stable / moderate / volatile | quick filter for Phase 3 forecast-method choice |\n",
       "| days_of_safety_stock | safety_stock / avg_daily_units | deliberately uses `safety_stock` (hundreds), not `current_stock` (inflated, see stock_anomaly_investigation.md) |\n",
       "| reorder_covers_lead_time | reorder_level/avg_daily_units >= lead_time_days | flags SKUs where the reorder trigger may fire too late relative to supplier lead time |\n\n",
       "## Distribution of volatility tiers\n\n",
       features["demand_volatility_tier"].value_counts().to_frame("count").to_markdown() + "\n\n",
       "## Products where the reorder point may not cover lead time\n\n",
       f"{(~features['reorder_covers_lead_time']).sum()} of {len(features)} product-branch combos "
       f"flagged -- candidates for the reorder-point-optimisation task in Phase 3.\n"]

with open(os.path.join(DOC_DIR, "feature_engineering.md"), "w") as f:
    f.writelines(out)

print("Feature table written to data_clean/features_week2.csv")
print(features["demand_volatility_tier"].value_counts())
print(f"Reorder-may-not-cover-lead-time flags: {(~features['reorder_covers_lead_time']).sum()}/{len(features)}")
