"""
Week 4 — Margin-Based Classification (Phase 2, task 1)
Heavy Supplier & Warehouse Analytics

Week 3's ABC classification was revenue-based, and it also found that
revenue concentration there is really a price-tier effect (units barely
vary across products; unit_price varies ~380x). Revenue doesn't say
anything about whether a product is actually PROFITABLE to stock, though
-- a high-price product can still have a thin margin. This re-does the
classification using margin instead, and checks where the two rankings
agree or disagree.

Run: python3 01_margin_based_classification.py
"""
import pandas as pd
import os

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
WEEK3_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-03", "data_clean")
DATA = os.path.join(os.path.dirname(__file__), "..", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
os.makedirs(DATA, exist_ok=True)
os.makedirs(DOC_DIR, exist_ok=True)

fact_sales = pd.read_csv(os.path.join(WEEK1_DATA, "fact_sales.csv"))
products = pd.read_csv(os.path.join(WEEK1_DATA, "products.csv"))
revenue_abc = pd.read_csv(os.path.join(WEEK3_DATA, "abc_classification.csv"))

units_by_product = fact_sales.groupby("product_id")["quantity"].sum().rename("total_units")
margin_df = products[["product_id", "product_name", "category", "unit_cost", "unit_price"]].copy()
margin_df["unit_margin"] = margin_df["unit_price"] - margin_df["unit_cost"]
margin_df["margin_pct"] = (margin_df["unit_margin"] / margin_df["unit_price"] * 100).round(1)
margin_df = margin_df.merge(units_by_product, on="product_id", how="left")
margin_df["total_margin"] = margin_df["unit_margin"] * margin_df["total_units"]

margin_df = margin_df.sort_values("total_margin", ascending=False).reset_index(drop=True)
margin_df["margin_share_pct"] = (margin_df["total_margin"] / margin_df["total_margin"].sum() * 100).round(2)
margin_df["cum_margin_pct"] = margin_df["margin_share_pct"].cumsum().round(2)

def abc_class(cum_pct):
    if cum_pct <= 70:
        return "A"
    elif cum_pct <= 90:
        return "B"
    return "C"
margin_df["margin_abc_class"] = margin_df["cum_margin_pct"].apply(abc_class)

combined = margin_df.merge(
    revenue_abc[["product_id", "abc_class", "revenue_share_pct"]].rename(columns={"abc_class": "revenue_abc_class"}),
    on="product_id", how="left"
)
combined["class_changed"] = combined["margin_abc_class"] != combined["revenue_abc_class"]
combined.to_csv(os.path.join(DATA, "margin_classification.csv"), index=False)

# ---- doc ----
out = ["# Week 4 — Margin-Based Classification\n\n",
       "Re-classifying the same 30 products by total margin contribution (unit margin x units sold) "
       "instead of revenue, and checking where that changes the picture from Week 3's revenue-based ABC.\n\n"]

class_counts = margin_df["margin_abc_class"].value_counts().reindex(["A", "B", "C"])
out.append("## Margin-based ABC classes\n\n")
out.append(class_counts.to_frame("n_products").to_markdown() + "\n\n")

margin_a = margin_df[margin_df.margin_abc_class == "A"]
out.append(f"Class A by margin ({len(margin_a)} products) = {margin_a['margin_share_pct'].sum():.1f}% of total "
           f"margin contribution.\n\n")
out.append(margin_a[["product_id", "product_name", "margin_pct", "margin_share_pct", "cum_margin_pct"]].to_markdown(index=False) + "\n\n")

changed = combined[combined.class_changed].sort_values("margin_share_pct", ascending=False)
out.append(f"## Where margin-based and revenue-based classes disagree\n\n{len(changed)} of 30 products land "
           f"in a different class depending on which metric is used:\n\n")
out.append(changed[["product_id", "product_name", "revenue_abc_class", "margin_abc_class",
                     "margin_pct", "revenue_share_pct", "margin_share_pct"]].to_markdown(index=False) + "\n\n")

low_margin_high_rev = combined[(combined.revenue_abc_class == "A") & (combined.margin_pct < combined["margin_pct"].median())]
out.append("## Products worth a second look\n\n")
if len(low_margin_high_rev):
    out.append(f"{len(low_margin_high_rev)} product(s) are revenue Class A but have below-median margin % "
               f"-- high sales value doesn't necessarily mean high profitability per unit:\n\n")
    out.append(low_margin_high_rev[["product_id", "product_name", "margin_pct", "revenue_share_pct"]].to_markdown(index=False) + "\n\n")
else:
    out.append("No revenue-Class-A / below-median-margin overlap found.\n\n")

with open(os.path.join(DOC_DIR, "margin_classification.md"), "w") as f:
    f.writelines(out)

print("Margin classification written to docs/margin_classification.md")
print(class_counts)
print(f"Products that changed class: {len(changed)}/30")
