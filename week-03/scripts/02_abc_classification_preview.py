"""
Week 3 — ABC Classification Preview
Heavy Supplier & Warehouse Analytics

A first cut at the "which products actually matter" question that Phase 2
(product performance, fast/slow movers, ABC classification) will go much
deeper on. This is deliberately a PREVIEW, not the full Phase 2 work --
it's here so Week 3 ends with a concrete starting point for that phase
rather than just a plan written in the abstract.

Two independent cuts on the same 30 products:
  - ABC by revenue (classic Pareto: A = top ~70% of cumulative revenue,
    B = next ~20%, C = the rest)
  - Fast/mid/slow mover by total units sold (volume, not value)

These don't have to agree -- a product can be high-value/low-volume or
the reverse, and that mismatch is itself useful to flag.

Run: python3 02_abc_classification_preview.py
"""
import pandas as pd
import os

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
DATA = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(DATA, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

fact_sales = pd.read_csv(os.path.join(WEEK1_DATA, "fact_sales.csv"))
products = pd.read_csv(os.path.join(WEEK1_DATA, "products.csv"))

by_product = fact_sales.groupby("product_id").agg(
    total_revenue=("line_grand_total", "sum"), total_units=("quantity", "sum")
).reset_index()

# ---- ABC by revenue ----
by_product = by_product.sort_values("total_revenue", ascending=False).reset_index(drop=True)
by_product["revenue_share_pct"] = (by_product["total_revenue"] / by_product["total_revenue"].sum() * 100).round(2)
by_product["cum_revenue_pct"] = by_product["revenue_share_pct"].cumsum().round(2)

def abc_class(cum_pct):
    if cum_pct <= 70:
        return "A"
    elif cum_pct <= 90:
        return "B"
    return "C"
by_product["abc_class"] = by_product["cum_revenue_pct"].apply(abc_class)

# ---- fast/mid/slow mover by units (terciles) ----
by_product = by_product.sort_values("total_units", ascending=False).reset_index(drop=True)
n = len(by_product)
third = n // 3
mover = ["fast"] * third + ["mid"] * (n - 2 * third) + ["slow"] * third
by_product["mover_speed"] = mover[:n]

by_product = by_product.merge(products[["product_id", "product_name", "category"]], on="product_id", how="left")
by_product = by_product.sort_values("cum_revenue_pct")
by_product.to_csv(os.path.join(DATA, "abc_classification.csv"), index=False)

# ---- doc ----
out = ["# Week 3 — ABC Classification Preview (Phase 2 starting point)\n\n",
       "**This is a preview, not the full Phase 2 analysis** -- Phase 2 is scoped to go much deeper on "
       "product performance. This gives it a concrete table to start from instead of a blank page.\n\n"]

class_counts = by_product["abc_class"].value_counts().reindex(["A", "B", "C"])
out.append("## ABC classes by revenue (Pareto on cumulative share)\n\n")
out.append(class_counts.to_frame("n_products").to_markdown() + "\n\n")
a_products = by_product[by_product.abc_class == "A"]
out.append(f"Class A ({len(a_products)} products) accounts for {a_products['revenue_share_pct'].sum():.1f}% "
           f"of total revenue on its own.\n\n")
out.append(a_products[["product_id", "product_name", "revenue_share_pct", "cum_revenue_pct"]].to_markdown(index=False) + "\n\n")

out.append("## Fast / mid / slow movers by units sold\n\n")
out.append(by_product["mover_speed"].value_counts().reindex(["fast", "mid", "slow"]).to_frame("n_products").to_markdown() + "\n\n")

units_min, units_max = by_product["total_units"].min(), by_product["total_units"].max()
units_spread_pct = round(100 * (units_max - units_min) / by_product["total_units"].mean(), 1)
out.append(f"**Caveat before trusting this split:** total units sold per product only ranges from "
           f"{units_min:,.0f} to {units_max:,.0f} across all 30 products -- a spread of about "
           f"{units_spread_pct:.0f}% of the mean. Every product sells almost the same volume. That means "
           f"\"fast/mid/slow mover by units\" is splitting products on very small differences, the same "
           f"way `demand_cv` did in Week 2 -- treat this tercile split as noise, not signal, until it's "
           f"checked against a less uniform volume pattern (or confirmed this is really how the business "
           f"behaves).\n\n"
           f"What IS a real, large difference between these products is `unit_price` (products.csv ranges "
           f"from Rs 310 to Rs 119,000 -- a ~380x spread). Since volume is nearly flat across products but "
           f"revenue concentration is real (Class A alone is {a_products['revenue_share_pct'].sum():.1f}% of revenue), "
           f"**the ABC split above is effectively a price-tier split, not a popularity split** -- worth "
           f"stating that plainly in any write-up rather than implying Class A products are the "
           f"bestsellers.\n\n")

# ---- mismatch: where value and volume disagree ----
mismatch = by_product[(by_product.abc_class == "A") & (by_product.mover_speed == "slow")]
mismatch2 = by_product[(by_product.abc_class == "C") & (by_product.mover_speed == "fast")]
out.append("## Where value and volume disagree\n\n")
if len(mismatch):
    out.append(f"**{len(mismatch)} product(s)** are Class A (high revenue) but slow movers by units -- "
                f"likely high unit price rather than high volume. These need a different stocking logic "
                f"(lower safety stock in units, but each stockout is expensive) than a typical Class A item:\n\n")
    out.append(mismatch[["product_id", "product_name", "revenue_share_pct", "total_units"]].to_markdown(index=False) + "\n\n")
else:
    out.append("No Class A / slow-mover overlap found in this cut.\n\n")
if len(mismatch2):
    out.append(f"**{len(mismatch2)} product(s)** are Class C (low revenue share) but fast movers by units -- "
                f"likely cheap, high-volume parts. Worth checking these aren't being under-stocked just "
                f"because their revenue contribution looks small:\n\n")
    out.append(mismatch2[["product_id", "product_name", "revenue_share_pct", "total_units"]].to_markdown(index=False) + "\n\n")

with open(os.path.join(DOC_DIR, "abc_classification_preview.md"), "w") as f:
    f.writelines(out)

print("ABC classification preview written to docs/abc_classification_preview.md")
print(class_counts)
print(by_product["mover_speed"].value_counts())
