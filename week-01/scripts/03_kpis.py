"""
Week 1 — First-Cut KPIs
Heavy Supplier & Warehouse Analytics

Computes the five foundation KPIs proposed for Week 1 against the cleaned,
joined data produced by 02_clean_validate_join.py.

Run: python3 03_kpis.py
"""
import pandas as pd
import os

BASE = os.path.dirname(__file__)
DATA = os.path.join(BASE, "..", "data_clean")
DOC_DIR = os.path.join(BASE, "..", "docs")

branches   = pd.read_csv(os.path.join(DATA, "branches.csv"))
products   = pd.read_csv(os.path.join(DATA, "products.csv"))
fact_sales = pd.read_csv(os.path.join(DATA, "fact_sales.csv"), parse_dates=["order_date"])
fact_inv   = pd.read_csv(os.path.join(DATA, "fact_inventory.csv"))
fact_po    = pd.read_csv(os.path.join(DATA, "fact_purchase_orders.csv"), parse_dates=["order_date", "received_date"])
po_header  = pd.read_csv(os.path.join(DATA, "purchase_orders_header.csv"), parse_dates=["order_date", "received_date"])

out = ["# Week 1 — First-Cut KPI Results\n",
       "Computed on the cleaned, joined dataset. These are starting points for "
       "Phase 2 (Weeks 4-6), not final numbers.\n"]

# ---------------------------------------------------------------
# KPI 1 — Inventory turnover ratio (annualised), per product
# units sold (last 12 months of data) / average stock on hand (proxy: current_stock)
# ---------------------------------------------------------------
max_date = fact_sales["order_date"].max()
last_12m = fact_sales[fact_sales["order_date"] >= max_date - pd.Timedelta(days=365)]
units_sold = last_12m.groupby("product_id")["quantity"].sum().rename("units_sold_12m")

avg_stock = fact_inv.groupby("product_id")["current_stock"].mean().rename("avg_stock_on_hand")
turnover = pd.concat([units_sold, avg_stock], axis=1).fillna(0)
turnover["turnover_ratio"] = (turnover["units_sold_12m"] / turnover["avg_stock_on_hand"]).round(2)
turnover = turnover.merge(products[["product_id", "product_name", "category"]],
                           left_index=True, right_on="product_id").sort_values("turnover_ratio", ascending=False)
turnover.to_csv(os.path.join(DATA, "kpi_inventory_turnover.csv"), index=False)

out.append("\n## 1. Inventory turnover ratio (12-month units sold ÷ avg stock on hand)\n")
out.append("\n> **Caveat:** `current_stock` shows signs of runaway accumulation — see "
            "\"Key data-quality finding\" in `validation_report.md`. Treat this KPI as directional "
            "only until that's resolved; the near-zero ratios below likely understate real turnover.\n")
out.append(f"\nFleet-wide median turnover: **{turnover['turnover_ratio'].median():.2f}x**. "
            f"Fastest mover: **{turnover.iloc[0]['product_name']}** ({turnover.iloc[0]['turnover_ratio']}x). "
            f"Slowest: **{turnover.iloc[-1]['product_name']}** ({turnover.iloc[-1]['turnover_ratio']}x).\n")
out.append("\n| product | category | units sold (12m) | avg stock | turnover |\n|---|---|---|---|---|\n")
for _, r in turnover.head(5).iterrows():
    out.append(f"| {r['product_name']} | {r['category']} | {r['units_sold_12m']:.0f} | "
                f"{r['avg_stock_on_hand']:.0f} | {r['turnover_ratio']}x |\n")

# ---------------------------------------------------------------
# KPI 2 — Stockout incidence rate (share of SKU-branch rows at/under safety stock)
# ---------------------------------------------------------------
stockout_rate = fact_inv["below_safety_stock"].mean() * 100
reorder_rate = fact_inv["at_or_below_reorder"].mean() * 100
by_branch = fact_inv.groupby("branch_name")["below_safety_stock"].mean().mul(100).round(1).sort_values(ascending=False)

out.append("\n## 2. Stockout incidence rate\n")
out.append("\n> **Caveat:** same runaway-accumulation issue as KPI 1 — `safety_stock`/`reorder_level` "
            "(hundreds of units) look uncalibrated against the inflated `current_stock` (100K+ units), "
            "which is almost certainly why this reads as 0%. Not read as \"inventory is healthy.\"\n")
out.append(f"\n**{stockout_rate:.1f}%** of SKU-branch combinations are at or below safety stock; "
            f"**{reorder_rate:.1f}%** are at or below reorder level.\n")
out.append("\n| branch | % SKUs at/below safety stock |\n|---|---|\n")
for branch, pct in by_branch.items():
    out.append(f"| {branch} | {pct}% |\n")

# ---------------------------------------------------------------
# KPI 3 — SKU count & stock value per branch
# ---------------------------------------------------------------
by_branch_val = fact_inv.groupby("branch_name").agg(
    sku_count=("product_id", "nunique"),
    total_stock_value=("stock_value", "sum"),
    warehouse_capacity_sqft=("warehouse_capacity_sqft", "first"),
).sort_values("total_stock_value", ascending=False)
by_branch_val.to_csv(os.path.join(DATA, "kpi_stock_value_by_branch.csv"))

out.append("\n## 3. SKU count & stock value per branch\n")
out.append("\n> **Caveat:** `total_stock_value` = `current_stock` × `unit_cost`, so it inherits the same "
            "runaway-accumulation issue as KPI 1/2 — read the *relative* ranking across branches as useful, "
            "not the absolute Rs figures.\n")
out.append("\n| branch | SKUs stocked | total stock value (Rs) | warehouse capacity (sqft) |\n|---|---|---|---|\n")
for branch, r in by_branch_val.iterrows():
    out.append(f"| {branch} | {int(r['sku_count'])} | {r['total_stock_value']:,.0f} | {int(r['warehouse_capacity_sqft']):,} |\n")

# ---------------------------------------------------------------
# KPI 4 — Supplier concentration (from purchase_orders_header; no supplier master yet)
# ---------------------------------------------------------------
supplier_value = po_header.groupby("supplier_id")["grand_total"].sum().sort_values(ascending=False)
total_po_value = supplier_value.sum()
top5_share = supplier_value.head(5).sum() / total_po_value * 100

out.append("\n## 4. Supplier concentration\n")
out.append(f"\nTop 5 of {supplier_value.shape[0]} suppliers (by supplier_id — no supplier master file "
            f"was provided, so names/attributes aren't available yet) account for "
            f"**{top5_share:.1f}%** of total purchase order value. All {supplier_value.shape[0]} shown "
            f"below — concentration is low; spend is close to evenly split across suppliers.\n")
out.append("\n| supplier_id | PO value (Rs) | % of total |\n|---|---|---|\n")
for sid, val in supplier_value.items():
    out.append(f"| {sid} | {val:,.0f} | {val/total_po_value*100:.1f}% |\n")

# ---------------------------------------------------------------
# KPI 5 — Order fulfilment lead time (purchase orders: order -> received)
# ---------------------------------------------------------------
received = po_header.dropna(subset=["received_date"]).copy()
received["lead_time_days"] = (received["received_date"] - received["order_date"]).dt.days
median_lt = received["lead_time_days"].median()
p90_lt = received["lead_time_days"].quantile(0.9)
by_branch_lt = received.groupby("branch_id")["lead_time_days"].median().round(1)

out.append("\n## 5. Purchase order fulfilment lead time\n")
out.append(f"\nMedian lead time (order → received): **{median_lt:.0f} days**. "
            f"90th percentile: **{p90_lt:.0f} days**. "
            f"({len(po_header) - len(received)} of {len(po_header)} POs still open / not yet received.)\n")
out.append("\n| branch | median lead time (days) |\n|---|---|\n")
for branch, days in by_branch_lt.items():
    out.append(f"| {branch} | {days} |\n")

with open(os.path.join(DOC_DIR, "kpis_week1.md"), "w") as f:
    f.writelines(out)

print("KPI report written to docs/kpis_week1.md")
print(f"Median turnover: {turnover['turnover_ratio'].median():.2f}x")
print(f"Stockout incidence: {stockout_rate:.1f}%")
print(f"Top-5 supplier concentration: {top5_share:.1f}%")
print(f"Median PO lead time: {median_lt:.0f} days")
