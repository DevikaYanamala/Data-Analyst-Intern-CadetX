# Week 2 — Stock Ledger Anomaly: Root-Cause Investigation

Week 1 found `current_stock` reaching ~208x its own stated `max_stock_level`. This digs into whether that's a real (if unusual) business pattern, or a data-generation artifact.

## 1. IN vs OUT: count AND size

| movement_type   |   n_events |   mean_qty |       total_qty |
|:----------------|-----------:|-----------:|----------------:|
| ADJUSTMENT      |       2454 |       27.3 | 66990           |
| IN              |     127611 |      159.8 |     2.03978e+07 |
| OUT             |     107165 |       10.5 |     1.12483e+06 |

If this were a genuine bulk-replenishment pattern (few large restocks feeding many small sales), we'd expect far *fewer* IN events than OUT events. Instead there are **127,611 IN events vs 107,165 OUT events** -- IN is actually MORE frequent, not less, while also averaging ~15x larger per event. That combination doesn't match a real replenishment strategy -- it matches two unrelated random distributions generating IN and OUT sizes independently of each other.

Total volume: **20,397,795 units IN** vs **1,124,832 units OUT** across the full history -- a net surplus of **19,272,963 units** that becomes opening balance for nothing, since there's no evidence of it being shipped, scrapped, or written off anywhere in the schema.

## 2. Growth trend (P001 @ DEL001, as a representative sample)

Linear fit to `running_balance` over time: slope = **52.70 units/day** (R² of the fit isn't the point here -- the point is the sign and steadiness: balance climbs nearly every year in the year-by-year table from Week 1's validation report, consistent with a steady positive drift rather than a seasonal or cyclical stocking pattern that would revert toward a baseline).

See `charts/stock_runaway_p001_del001.png` -- a near-monotonic climb, not an oscillation around a stable operating level.

## 3. Do ADJUSTMENT entries correct for this?

2,454 ADJUSTMENT rows exist, averaging 27.3 units each (66,990 total). That's negligible next to the ~19,272,963 unit surplus from IN/OUT alone -- adjustments aren't correcting the drift, they're a separate, much smaller category of movement.

## Verdict

The evidence points to a **data-generation artifact**, not a real warehouse condition: IN and OUT quantities appear to be drawn from two independent random ranges (IN ~ uniform 20-300, OUT ~ uniform 1-20) with no logic tying replenishment size to actual consumption, and IN events are *more* frequent than OUT events rather than less -- the opposite of what a real bulk-purchasing strategy would look like. Recommendation: treat `current_stock` and anything derived from it (this week's and Week 1's stock-value and turnover KPIs) as **directional only**, and flag this to whoever maintains the dataset as a likely generator bug in how `stock_ledger` quantities were simulated.
