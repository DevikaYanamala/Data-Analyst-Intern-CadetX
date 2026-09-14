"""
Week 2 — Supplier Integration
Heavy Supplier & Warehouse Analytics

Week 1 flagged that no supplier master table was available. A corrected,
complete copy of the dataset has since turned up with `suppliers.csv`
included (verified: every other file is byte-identical to Week 1's data,
just correctly labeled this time -- same underlying dataset, one file
added). This script folds it in: validates the FK, and builds real
supplier-side analysis that Week 1 could only gesture at.

Run: python3 01_integrate_suppliers.py
"""
import pandas as pd
import os

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
DATA = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
SUPPLIERS_SRC = "/mnt/user-data/uploads/hswd/HeavySuppliersWarehouseDatasets/suppliers.csv"

suppliers = pd.read_csv(SUPPLIERS_SRC)
suppliers.to_csv(os.path.join(DATA, "suppliers.csv"), index=False)

po_header = pd.read_csv(os.path.join(WEEK1_DATA, "purchase_orders_header.csv"), parse_dates=["order_date", "received_date"])
po_lines = pd.read_csv(os.path.join(WEEK1_DATA, "purchase_orders_lines.csv"))
products = pd.read_csv(os.path.join(WEEK1_DATA, "products.csv"))

# FK check
orphans = po_header[~po_header["supplier_id"].isin(suppliers["supplier_id"])]
assert len(orphans) == 0, f"{len(orphans)} POs reference a supplier_id not in suppliers.csv"

out = ["# Week 2 — Supplier Integration & Analysis\n\n",
       f"`suppliers.csv` received and joined. Referential integrity check: "
       f"purchase_orders_header.supplier_id -> suppliers.supplier_id -- "
       f"**{len(po_header) - len(orphans)}/{len(po_header)} rows OK, {len(orphans)} orphans**.\n\n",
       f"{len(suppliers)} suppliers on file, spanning "
       f"{suppliers['region'].nunique()} regions ({', '.join(sorted(suppliers['region'].unique()))}) "
       f"and {suppliers['supplier_type'].nunique()} supplier types "
       f"({', '.join(sorted(suppliers['supplier_type'].unique()))}).\n\n"]

# ---- Supplier contribution & concentration ----
by_supplier = (po_header.merge(suppliers, on="supplier_id")
               .groupby(["supplier_id", "supplier_name", "supplier_type", "reliability_score", "lead_time_days"])
               ["grand_total"].sum().sort_values(ascending=False))
total_value = by_supplier.sum()
by_supplier_df = by_supplier.reset_index()
by_supplier_df["share_pct"] = (by_supplier_df["grand_total"] / total_value * 100).round(1)
by_supplier_df.to_csv(os.path.join(DATA, "supplier_contribution.csv"), index=False)

top5_share = by_supplier_df.head(5)["share_pct"].sum()
out.append(f"## Supplier contribution\n\nTop 5 of {len(by_supplier_df)} suppliers = "
           f"**{top5_share:.1f}%** of total PO value.\n\n")
out.append(by_supplier_df.to_markdown(index=False) + "\n\n")

# ---- Reliability vs dependency: are the suppliers we lean on hardest also the risky ones? ----
by_supplier_df["dependency_rank"] = by_supplier_df["share_pct"].rank(ascending=False)
low_reliability_high_dependency = by_supplier_df[
    (by_supplier_df["reliability_score"] <= 3) & (by_supplier_df["dependency_rank"] <= 5)
]
out.append("## Reliability vs. dependency risk\n\n")
if len(low_reliability_high_dependency) > 0:
    out.append(f"**{len(low_reliability_high_dependency)} supplier(s)** are both in the top-5 by spend "
               f"AND rated reliability <= 3/5 -- concentration risk sitting on top of reliability risk:\n\n")
    out.append(low_reliability_high_dependency[["supplier_name", "share_pct", "reliability_score"]].to_markdown(index=False) + "\n\n")
else:
    out.append("No overlap found between the top-5 suppliers by spend and low-reliability suppliers.\n\n")

# ---- Lead time: stated vs actual, per supplier ----
received = po_header.dropna(subset=["received_date"]).merge(suppliers, on="supplier_id")
received["actual_lead_time"] = (received["received_date"] - received["order_date"]).dt.days
lt_by_supplier = received.groupby(["supplier_name", "lead_time_days"])["actual_lead_time"].agg(["median", "count"]).reset_index()
lt_by_supplier["gap_days"] = (lt_by_supplier["median"] - lt_by_supplier["lead_time_days"]).round(1)
lt_by_supplier = lt_by_supplier.sort_values("gap_days", ascending=False)
lt_by_supplier.to_csv(os.path.join(DATA, "supplier_lead_time_gap.csv"), index=False)

out.append("## Lead time: stated vs. actual, by supplier\n\n")
out.append("Positive gap = supplier runs slower than what they quote.\n\n")
out.append(lt_by_supplier.rename(columns={"lead_time_days": "stated_days", "median": "actual_median_days"}).to_markdown(index=False) + "\n\n")

# ---- Product-level supplier dependency (single-source risk) ----
prod_supplier = (po_lines.merge(po_header[["po_id", "supplier_id"]], on="po_id")
                  .groupby(["product_id", "supplier_id"])["line_total"].sum().reset_index())
n_suppliers_per_product = prod_supplier.groupby("product_id")["supplier_id"].nunique().rename("n_suppliers")
top_share_per_product = (prod_supplier.groupby("product_id")["line_total"]
                          .apply(lambda s: s.max() / s.sum() * 100).round(1).rename("top_supplier_share_pct"))
dependency = pd.concat([n_suppliers_per_product, top_share_per_product], axis=1).merge(
    products[["product_id", "product_name"]], left_index=True, right_on="product_id")
single_sourced = dependency[dependency["n_suppliers"] == 1].sort_values("product_name")
dependency.to_csv(os.path.join(DATA, "product_supplier_dependency.csv"), index=False)

out.append(f"## Single-source product risk\n\n{len(single_sourced)} of {len(dependency)} products are "
           f"sourced from exactly one supplier (100% dependency) -- any disruption at that supplier "
           f"stops that product's inbound supply entirely.\n\n")

with open(os.path.join(DOC_DIR, "supplier_analysis.md"), "w") as f:
    f.writelines(out)

print("Supplier analysis written to docs/supplier_analysis.md")
print(f"Top-5 supplier concentration: {top5_share:.1f}%")
print(f"Single-sourced products: {len(single_sourced)}/{len(dependency)}")
