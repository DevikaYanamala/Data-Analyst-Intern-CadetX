"""
Week 1 — Cleaning, Referential Validation & Integration
Heavy Supplier & Warehouse Analytics

Loads each table by its TRUE identity (see 01_profiling.py for the
filename-mismatch mapping), cleans obvious issues, checks foreign-key
integrity across the schema, and builds the joined analytical tables used
for Week 1 KPIs.

Run: python3 02_clean_validate_join.py
"""
import pandas as pd
import numpy as np
import os

RAW_DIR = "/root/.claude/uploads/200f17a8-57f9-51d7-9d2d-10e62d7f0b6d"
BASE = os.path.dirname(__file__)
OUT_DIR = os.path.join(BASE, "..", "data_clean")
DOC_DIR = os.path.join(BASE, "..", "docs")

FILE_MAP = {
    "3c0d8a74-customers.csv":              "branches",
    "0ac895b7-invoices.csv":               "inventory_master",
    "5542ee3f-purchase_orders_header.csv": "products",
    "5cb0d9ba-sales_orders_header.csv":    "purchase_orders_lines",
    "5e829e3e-products.csv":               "payments",
    "92d30516-payments.csv":               "invoices",
    "c2fdb3fb-sales_orders_lines.csv":     "sales_orders_header",
    "e6365aa6-purchase_orders_lines.csv":  "purchase_orders_header",
    "f23eb42d-suppliers.csv":              "stock_ledger",
    "f61b37a3-inventory_master.csv":       "customers",
    "fc71da79-stock_ledger.csv":           "sales_orders_lines",
}

T = {}
for fname, true_name in FILE_MAP.items():
    T[true_name] = pd.read_csv(os.path.join(RAW_DIR, fname))

# ---------------------------------------------------------------
# CLEANING
# ---------------------------------------------------------------

# branches: numeric warehouse_capacity out of "45230 sqft"
b = T["branches"].copy()
b["warehouse_capacity_sqft"] = b["warehouse_capacity"].str.replace(" sqft", "", regex=False).astype(int)
b = b.drop(columns=["warehouse_capacity"])
T["branches"] = b

# date columns to parse per table
DATE_COLS = {
    "customers": ["customer_since", "last_purchase_date"],
    "products": ["last_purchase_date"],
    "invoices": ["invoice_date", "due_date"],
    "payments": ["payment_date"],
    "sales_orders_header": ["order_date", "delivery_date"],
    "purchase_orders_header": ["order_date", "expected_delivery_date", "received_date"],
    "stock_ledger": ["movement_date"],
}
for tbl, cols in DATE_COLS.items():
    for c in cols:
        T[tbl][c] = pd.to_datetime(T[tbl][c], errors="coerce")

# drop exact duplicate rows everywhere (none found in profiling, this is a safety net)
for name in T:
    before = len(T[name])
    T[name] = T[name].drop_duplicates()
    after = len(T[name])
    if before != after:
        print(f"  dropped {before - after} exact-duplicate rows from {name}")

# ---------------------------------------------------------------
# REFERENTIAL INTEGRITY CHECKS
# ---------------------------------------------------------------
checks = []

def fk_check(child_name, child_col, parent_name, parent_col):
    child = T[child_name]
    parent_vals = set(T[parent_name][parent_col].unique())
    orphans = child[~child[child_col].isin(parent_vals)]
    checks.append((f"{child_name}.{child_col} -> {parent_name}.{parent_col}",
                    len(child), len(orphans)))
    return orphans

fk_check("customers", "branch_id", "branches", "branch_id")
fk_check("inventory_master", "product_id", "products", "product_id")
fk_check("inventory_master", "branch_id", "branches", "branch_id")
fk_check("sales_orders_header", "customer_id", "customers", "customer_id")
fk_check("sales_orders_header", "branch_id", "branches", "branch_id")
fk_check("sales_orders_lines", "so_id", "sales_orders_header", "so_id")
fk_check("sales_orders_lines", "product_id", "products", "product_id")
fk_check("purchase_orders_header", "branch_id", "branches", "branch_id")
fk_check("purchase_orders_lines", "po_id", "purchase_orders_header", "po_id")
fk_check("purchase_orders_lines", "product_id", "products", "product_id")
fk_check("invoices", "so_id", "sales_orders_header", "so_id")
fk_check("invoices", "customer_id", "customers", "customer_id")
fk_check("invoices", "branch_id", "branches", "branch_id")
fk_check("payments", "invoice_id", "invoices", "invoice_id")
fk_check("stock_ledger", "product_id", "products", "product_id")
fk_check("stock_ledger", "branch_id", "branches", "branch_id")

# supplier_id has no master table to check against — flagged separately
n_suppliers = T["purchase_orders_header"]["supplier_id"].nunique()
supplier_ids = sorted(T["purchase_orders_header"]["supplier_id"].unique())

with open(os.path.join(DOC_DIR, "validation_report.md"), "w") as f:
    f.write("# Week 1 — Referential Integrity & Validation Report\n\n")
    f.write("| relationship | child rows | orphan rows | integrity |\n|---|---|---|---|\n")
    for rel, total, orphans in checks:
        status = "OK" if orphans == 0 else f"**{orphans} ORPHANS**"
        f.write(f"| {rel} | {total:,} | {orphans:,} | {status} |\n")
    f.write(f"\n## Missing table: `suppliers`\n\n")
    f.write(f"`purchase_orders_header.supplier_id` references **{n_suppliers} distinct suppliers** "
            f"(`{', '.join(supplier_ids)}`), but no supplier master file (supplier_id, supplier_name, "
            f"rating, lead time, category, etc.) was included in this upload. Supplier-side analysis "
            f"this week is therefore limited to supplier_id-level aggregates from purchase orders — "
            f"full supplier profiling is blocked until that file is provided.\n")
    dup_inv = T["invoices"]["invoice_id"].duplicated().sum()
    dup_pay = T["payments"]["payment_id"].duplicated().sum()
    f.write(f"\n## Duplicate key values (not full-row duplicates)\n\n")
    f.write(f"- `invoices.invoice_id`: {dup_inv} values appear on more than one row "
            f"(197 duplicate combinations found in profiling) — needs a source-side fix; "
            f"kept as-is here and flagged rather than silently dropped.\n")
    f.write(f"- `payments.payment_id`: {dup_pay} values appear on more than one row — same treatment.\n")

    # ---- Key finding: IN/OUT quantity imbalance drives runaway stock ----
    sl = T["stock_ledger"]
    mv = sl.groupby("movement_type")["quantity"].agg(["count", "mean"]).round(1)
    in_mean = mv.loc["IN", "mean"] if "IN" in mv.index else float("nan")
    out_mean = mv.loc["OUT", "mean"] if "OUT" in mv.index else float("nan")
    sample = sl[(sl["product_id"] == "P001") & (sl["branch_id"] == "DEL001")].sort_values("movement_date")
    first_bal = sample["running_balance"].iloc[0]
    last_bal = sample["running_balance"].iloc[-1]
    inv_master = T["inventory_master"]
    cur_stock_max = inv_master["current_stock"].max()
    max_stock_max = inv_master["max_stock"].max()

    f.write("\n## Key data-quality finding: runaway stock accumulation\n\n")
    f.write(f"`stock_ledger` IN movements average **{in_mean:.0f} units** per transaction while OUT "
            f"movements average only **{out_mean:.0f} units** — receipts are ~{in_mean/out_mean:.0f}x "
            f"larger than shipments. Because this repeats across ~2,200 days of history, `running_balance` "
            f"climbs almost monotonically rather than oscillating around a stable level: for `P001` at "
            f"`DEL001` it goes from **{first_bal}** (2019) to **{last_bal:,}** (2025).\n\n")
    f.write(f"`inventory_master.current_stock` is simply the latest `running_balance` per product/branch "
            f"(verified: ratio is exactly 1.00 across all 180 rows), so it inherits this — current stock "
            f"reaches **{cur_stock_max:,} units**, while `max_stock_level` (the supposed capacity ceiling "
            f"from `products`/`inventory_master`) tops out at **{max_stock_max:,} units**. Current stock is "
            f"~{cur_stock_max/max_stock_max:.0f}x its own stated maximum, and physically implausible for a "
            f"45,230 sqft warehouse holding 38.5 kg hydraulic pumps.\n\n")
    f.write("**Implication for this week's KPIs:** stockout/reorder-level metrics and "
            "current-stock-based turnover (KPI 1 and KPI 2 in `kpis_week1.md`) are computed as specified, "
            "but read as unreliable until this is resolved — the reorder/safety/max-stock thresholds appear "
            "to have been generated independently of the ledger's running balance, not calibrated against it. "
            "Recommend raising this with the programme team and treating it as a Week 2 priority "
            "(`Data Integrity & Error Detection`, `Inventory Movement Anomaly Detection` in the task "
            "catalogue) before building further inventory-health analysis on top of `current_stock`.\n")

print("Validation report written.")
for rel, total, orphans in checks:
    flag = "OK" if orphans == 0 else f"!! {orphans} orphans"
    print(f"  {rel:55s} {flag}")

# ---------------------------------------------------------------
# SAVE CLEANED TABLES UNDER THEIR TRUE NAMES
# ---------------------------------------------------------------
for name, df in T.items():
    df.to_csv(os.path.join(OUT_DIR, f"{name}.csv"), index=False)

# ---------------------------------------------------------------
# INTEGRATED / JOINED ANALYTICAL TABLES
# ---------------------------------------------------------------

# 1) Sales fact: line-level sales joined up to header, customer, branch, product
sales_fact = (
    T["sales_orders_lines"]
    .merge(T["sales_orders_header"][["so_id", "customer_id", "branch_id", "order_date",
                                      "delivery_date", "order_status", "sales_channel"]],
           on="so_id", how="left")
    .merge(T["products"][["product_id", "product_name", "category", "brand", "unit_cost"]],
           on="product_id", how="left")
    .merge(T["branches"][["branch_id", "branch_name", "region"]], on="branch_id", how="left")
)
sales_fact.to_csv(os.path.join(OUT_DIR, "fact_sales.csv"), index=False)

# 2) Inventory fact: current stock joined to product economics and branch
inventory_fact = (
    T["inventory_master"]
    .merge(T["products"][["product_id", "product_name", "category", "unit_cost", "unit_price",
                           "criticality_level", "lead_time_days"]], on="product_id", how="left")
    .merge(T["branches"][["branch_id", "branch_name", "region", "warehouse_capacity_sqft"]],
           on="branch_id", how="left")
)
inventory_fact["stock_value"] = inventory_fact["current_stock"] * inventory_fact["unit_cost"]
inventory_fact["below_safety_stock"] = inventory_fact["current_stock"] <= inventory_fact["safety_stock"]
inventory_fact["at_or_below_reorder"] = inventory_fact["current_stock"] <= inventory_fact["reorder_level"]
inventory_fact.to_csv(os.path.join(OUT_DIR, "fact_inventory.csv"), index=False)

# 3) Purchase order fact: line-level POs joined to header + branch
po_fact = (
    T["purchase_orders_lines"]
    .merge(T["purchase_orders_header"][["po_id", "supplier_id", "branch_id", "order_date",
                                         "expected_delivery_date", "received_date", "po_status"]],
           on="po_id", how="left")
    .merge(T["products"][["product_id", "product_name", "category"]], on="product_id", how="left")
)
po_fact["lead_time_days_actual"] = (po_fact["received_date"] - po_fact["order_date"]).dt.days
po_fact.to_csv(os.path.join(OUT_DIR, "fact_purchase_orders.csv"), index=False)

print("\nJoined fact tables written: fact_sales.csv, fact_inventory.csv, fact_purchase_orders.csv")
print(f"fact_sales rows:            {len(sales_fact):,}")
print(f"fact_inventory rows:        {len(inventory_fact):,}")
print(f"fact_purchase_orders rows:  {len(po_fact):,}")
