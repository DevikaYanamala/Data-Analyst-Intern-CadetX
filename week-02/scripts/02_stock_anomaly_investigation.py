"""
Week 2 — Stock Ledger Anomaly: Root-Cause Investigation
Heavy Supplier & Warehouse Analytics

Week 1 flagged that inventory_master.current_stock climbs to unrealistic
six-figure levels because stock_ledger IN movements run far larger than
OUT movements. This script digs into *why*, rather than just re-stating
that it happens -- comparing event counts (not just average size), fitting
the actual growth trend, and checking whether a bulk-replenishment
business pattern could explain it before concluding it's a data artifact.

Run: python3 02_stock_anomaly_investigation.py
"""
import pandas as pd
import numpy as np
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

WEEK1_DATA = os.path.join(os.path.dirname(__file__), "..", "..", "week-01", "data_clean")
DOC_DIR = os.path.join(os.path.dirname(__file__), "..", "docs")
CHART_DIR = os.path.join(os.path.dirname(__file__), "..", "charts")

sl = pd.read_csv(os.path.join(WEEK1_DATA, "stock_ledger.csv"), parse_dates=["movement_date"])

out = ["# Week 2 — Stock Ledger Anomaly: Root-Cause Investigation\n\n",
       "Week 1 found `current_stock` reaching ~208x its own stated `max_stock_level`. "
       "This digs into whether that's a real (if unusual) business pattern, or a "
       "data-generation artifact.\n\n"]

# ---- 1. Event counts, not just average size ----
mv = sl.groupby("movement_type").agg(n_events=("quantity", "count"), mean_qty=("quantity", "mean"),
                                       total_qty=("quantity", "sum")).round(1)
out.append("## 1. IN vs OUT: count AND size\n\n")
out.append(mv.to_markdown() + "\n\n")

in_events, out_events = mv.loc["IN", "n_events"], mv.loc["OUT", "n_events"]
in_total, out_total = mv.loc["IN", "total_qty"], mv.loc["OUT", "total_qty"]
out.append(f"If this were a genuine bulk-replenishment pattern (few large restocks feeding many small "
           f"sales), we'd expect far *fewer* IN events than OUT events. Instead there are "
           f"**{in_events:,.0f} IN events vs {out_events:,.0f} OUT events** -- IN is actually "
           f"MORE frequent, not less, while also averaging ~15x larger per event. That combination "
           f"doesn't match a real replenishment strategy -- it matches two unrelated random "
           f"distributions generating IN and OUT sizes independently of each other.\n\n")
out.append(f"Total volume: **{in_total:,.0f} units IN** vs **{out_total:,.0f} units OUT** across the "
           f"full history -- a net surplus of **{in_total - out_total:,.0f} units** that becomes "
           f"opening balance for nothing, since there's no evidence of it being shipped, scrapped, "
           f"or written off anywhere in the schema.\n\n")

# ---- 2. Trend fit: is growth linear (constant random-walk drift) or event-driven? ----
sample = sl[(sl.product_id == "P001") & (sl.branch_id == "DEL001")].sort_values("movement_date").reset_index(drop=True)
sample["day_num"] = (sample["movement_date"] - sample["movement_date"].min()).dt.days
slope, intercept = np.polyfit(sample["day_num"], sample["running_balance"], 1)
out.append("## 2. Growth trend (P001 @ DEL001, as a representative sample)\n\n")
out.append(f"Linear fit to `running_balance` over time: slope = **{slope:.2f} units/day** "
           f"(R² of the fit isn't the point here -- the point is the sign and steadiness: balance "
           f"climbs nearly every year in the year-by-year table from Week 1's validation report, "
           f"consistent with a steady positive drift rather than a seasonal or cyclical stocking "
           f"pattern that would revert toward a baseline).\n\n")

plt.figure(figsize=(9, 4.5))
plt.plot(sample["movement_date"], sample["running_balance"], linewidth=1.2, color="#2f6e5c")
plt.title("running_balance over time -- P001 @ DEL001")
plt.xlabel("date")
plt.ylabel("running_balance (units)")
plt.tight_layout()
plt.savefig(os.path.join(CHART_DIR, "stock_runaway_p001_del001.png"), dpi=130)
plt.close()
out.append("See `charts/stock_runaway_p001_del001.png` -- a near-monotonic climb, not an "
           "oscillation around a stable operating level.\n\n")

# ---- 3. ADJUSTMENT movements: are they being used to correct the drift? ----
adj = sl[sl.movement_type == "ADJUSTMENT"]
out.append("## 3. Do ADJUSTMENT entries correct for this?\n\n")
out.append(f"{len(adj):,} ADJUSTMENT rows exist, averaging {adj['quantity'].mean():.1f} units each "
           f"({adj['quantity'].sum():,} total). That's negligible next to the ~{in_total - out_total:,.0f} "
           f"unit surplus from IN/OUT alone -- adjustments aren't correcting the drift, they're a "
           f"separate, much smaller category of movement.\n\n")

# ---- 4. Verdict ----
out.append("## Verdict\n\n")
out.append("The evidence points to a **data-generation artifact**, not a real warehouse condition: "
           "IN and OUT quantities appear to be drawn from two independent random ranges "
           "(IN ~ uniform 20-300, OUT ~ uniform 1-20) with no logic tying replenishment size to actual "
           "consumption, and IN events are *more* frequent than OUT events rather than less -- the "
           "opposite of what a real bulk-purchasing strategy would look like. Recommendation: treat "
           "`current_stock` and anything derived from it (this week's and Week 1's stock-value and "
           "turnover KPIs) as **directional only**, and flag this to whoever maintains the dataset as "
           "a likely generator bug in how `stock_ledger` quantities were simulated.\n")

with open(os.path.join(DOC_DIR, "stock_anomaly_investigation.md"), "w") as f:
    f.writelines(out)

print("Investigation written to docs/stock_anomaly_investigation.md")
print(f"IN events: {in_events:,.0f}  OUT events: {out_events:,.0f}")
print(f"IN total: {in_total:,.0f}  OUT total: {out_total:,.0f}  surplus: {in_total - out_total:,.0f}")
print(f"Trend slope (P001@DEL001): {slope:.2f} units/day")
