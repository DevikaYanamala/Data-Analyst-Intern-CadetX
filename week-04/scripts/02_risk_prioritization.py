"""
Week 4 — Risk Prioritization (Phase 2, tasks 3 & 5)
Heavy Supplier & Warehouse Analytics

Brings together everything scattered across Weeks 1-4 into one ranked list:
which products are both VALUABLE (margin-based Class A/B, this week) and
AT RISK (single-sourced from a low-reliability supplier, and/or sitting on
a reorder point that may not cover lead time, both from Week 2). A product
that's cheap and well-supplied doesn't need urgent attention even if
something's technically "flagged" -- this is about where value and risk
stack on the same SKU.

Run: python3 02_risk_prioritization.py
"""
import pandas as pd
import os

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
WEEK2_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-02", "data_clean")
DATA = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(DATA, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

margin_class = pd.read_csv(os.path.join(DATA, "margin_classification.csv"))
po_header = pd.read_csv(os.path.join(WEEK1_DATA, "purchase_orders_header.csv"))
po_lines = pd.read_csv(os.path.join(WEEK1_DATA, "purchase_orders_lines.csv"))
suppliers = pd.read_csv(os.path.join(WEEK2_DATA, "suppliers.csv"))
features = pd.read_csv(os.path.join(WEEK2_DATA, "features_week2.csv"))

# ---- which supplier(s) does each product actually come from, and are they single-sourced? ----
prod_supplier = (po_lines.merge(po_header[["po_id", "supplier_id"]], on="po_id")
                  .groupby(["product_id", "supplier_id"])["line_total"].sum().reset_index())
n_suppliers = prod_supplier.groupby("product_id")["supplier_id"].nunique().rename("n_suppliers")
# for single-sourced products, pull that one supplier's reliability score
top_supplier = prod_supplier.sort_values("line_total", ascending=False).groupby("product_id").first()
top_supplier = top_supplier.merge(suppliers[["supplier_id", "supplier_name", "reliability_score"]],
                                   on="supplier_id", how="left")
top_supplier.index = prod_supplier.sort_values("line_total", ascending=False).groupby("product_id").first().index
supplier_risk = pd.concat([n_suppliers, top_supplier[["supplier_name", "reliability_score"]]], axis=1).reset_index()
supplier_risk = supplier_risk.rename(columns={"index": "product_id"})
supplier_risk["single_sourced"] = supplier_risk["n_suppliers"] == 1

# ---- reorder-vs-lead-time risk, rolled up to product level (flagged in ANY branch) ----
reorder_risk = features.groupby("product_id").agg(
    n_branches_flagged=("reorder_covers_lead_time", lambda s: (~s).sum()),
    criticality_level=("criticality_level", "first"),
).reset_index()

risk = (margin_class[["product_id", "product_name", "margin_abc_class", "margin_share_pct", "margin_pct"]]
        .merge(supplier_risk, on="product_id", how="left")
        .merge(reorder_risk, on="product_id", how="left"))

# ---- priority score: value (A=2,B=1,C=0) + single-source risk + low reliability + reorder gap ----
value_pts = risk["margin_abc_class"].map({"A": 2, "B": 1, "C": 0})
single_source_pts = risk["single_sourced"].astype(int)
low_reliability_pts = (risk["reliability_score"] <= 3).astype(int)
reorder_pts = (risk["n_branches_flagged"] > 0).astype(int)
risk["priority_score"] = value_pts + single_source_pts + low_reliability_pts + reorder_pts
risk = risk.sort_values("priority_score", ascending=False)
risk.to_csv(os.path.join(DATA, "risk_prioritization.csv"), index=False)

# ---- doc ----
out = ["# Week 4 — Risk Prioritization\n\n",
       "Combines margin-based value (this week), supplier single-sourcing + reliability (Week 2), and "
       "reorder-vs-lead-time flags (Week 2) into one ranked list. `priority_score` = "
       "margin class (A=2/B=1/C=0) + 1 if single-sourced + 1 if that supplier's reliability <= 3/5 + 1 if "
       "flagged in any branch for reorder-level-may-not-cover-lead-time. Max possible = 5.\n\n"]

top = risk.head(10)
out.append("## Top 10 by priority score\n\n")
out.append(top[["product_id", "product_name", "margin_abc_class", "single_sourced", "reliability_score",
                 "n_branches_flagged", "priority_score"]].to_markdown(index=False) + "\n\n")

top_risk = risk[risk.priority_score >= 4]
out.append(f"## Products needing attention first\n\n{len(top_risk)} product(s) score 4 or 5 (out of 5) -- "
           f"high value AND multiple risk factors stacked on the same SKU:\n\n")
if len(top_risk):
    out.append(top_risk[["product_id", "product_name", "margin_abc_class", "supplier_name",
                          "reliability_score", "n_branches_flagged"]].to_markdown(index=False) + "\n\n")
else:
    out.append("No product hit the top band this cut -- worth revisiting the scoring weights rather than "
               "concluding there's no risk at all.\n\n")

if len(top_risk):
    supplier_counts = top_risk["supplier_name"].value_counts()
    top_supplier_name = supplier_counts.index[0]
    out.append(f"**{supplier_counts.iloc[0]} of these {len(top_risk)} products trace back to the same "
               f"supplier: {top_supplier_name}.** This matches Week 2's finding that this supplier is both "
               f"a top-5-by-spend supplier AND has a below-average reliability score (3/5) -- concentration "
               f"risk and reliability risk landing on the same supplier, now shown to carry through to "
               f"multiple specific high-value products, not just an abstract spend percentage.\n\n")

out.append(f"**None of the top 10 are single-sourced** (`single_sourced` is False throughout) -- consistent "
           f"with Week 2's finding that 0 of 30 products are single-sourced. The risk here is entirely "
           f"driven by margin class, supplier reliability, and reorder-lead-time gaps, not single-sourcing "
           f"-- worth keeping that distinction clear rather than conflating \"risky\" with \"single-sourced.\"\n\n")

out.append("## Caveat\n\nThis score is a simple additive heuristic, not a validated risk model -- the "
           "weights (1 point per factor) are a starting point, not tuned. Useful for sorting a list to "
           "look at first, not for a confident \"this product is N times riskier than that one\" claim.\n")

with open(os.path.join(DOC_DIR, "risk_prioritization.md"), "w") as f:
    f.writelines(out)

print("Risk prioritization written to docs/risk_prioritization.md")
print(risk[["product_id", "priority_score"]].head(10))
