# Sprint Notes — Week 2

**Programme:** Heavy Supplier & Warehouse Analytics — Data Analytics & Data Science
**Working mode:** Solo
**Phase:** 1 of 4 — Foundation & Exploration (final week of this phase)

## What was planned

Close out the two blockers carried over from Week 1 — the missing supplier
master table and the unexplained inventory runaway — and start feature
engineering ahead of Phase 2/3.

## What got done

- **Supplier master integrated.** A corrected copy of the dataset turned up
  with `suppliers.csv` included (verified byte-identical to Week 1's data
  everywhere else — same dataset, one file added, correctly labeled this
  time). Joined it in, validated the FK (24,000/24,000 clean), and built
  real supplier analysis: contribution/concentration, reliability vs.
  dependency overlap, lead-time gap by supplier, and single-source product
  risk (`docs/supplier_analysis.md`).
- **Root-caused the stock-ledger anomaly from Week 1**, rather than just
  re-flagging it. Compared IN vs OUT *event counts* (not just average
  size) — IN events (127,611) actually outnumber OUT events (107,165),
  which rules out a genuine bulk-replenishment explanation (that would need
  far fewer, larger IN events). Fit the actual growth trend for a sample
  product/branch and checked whether ADJUSTMENT entries correct for the
  drift (they don't — negligible next to the ~19.3M unit IN/OUT surplus
  across the dataset). Verdict: this reads as a data-generation artifact
  (IN and OUT quantities look like two independent random ranges with no
  logic tying replenishment to consumption), not a real warehouse
  condition. Full writeup and a trend chart in
  `docs/stock_anomaly_investigation.md` / `charts/`.
- **Feature engineering for later phases** — built a 180-row (30 products
  x 6 branches) feature table using demand-side signals rather than
  `current_stock` directly, given the finding above: average/volatility of
  monthly units sold, a volatility tier, days-of-safety-stock, and a flag
  for reorder points that may not cover suppliers' lead time
  (`docs/feature_engineering.md`, `data_clean/features_week2.csv`).

## Findings worth flagging up

- All 8 suppliers hit their *stated* lead time exactly (median gap = 0
  days for every one) — no real-world variance at all, which is itself
  suspicious and likely another simulation simplification rather than
  something to read as "suppliers are perfectly reliable."
- 0 of 30 products are single-sourced — dependency risk here is lower than
  Week 1's supplier-concentration number alone suggested, since spend
  concentration and single-sourcing turn out to be different risks.
- 77 of 180 product-branch combinations have a reorder level that may not
  cover the supplier's lead time at current demand — a concrete candidate
  list for Phase 3's reorder-point-optimisation task.
- Demand volatility (CV of monthly units) came back "moderate" for all 180
  rows with the thresholds used — not a useful split as-is; worth
  revisiting the CV thresholds once real forecasting work starts in Phase
  3, rather than treating this as "everything behaves the same."

## Blockers

- None carried over — both of Week 1's open items are now closed out.

## Next up (Week 3 — last week of Phase 1)

- Since demand volatility didn't differentiate products this week, look at
  seasonality/trend within the monthly series directly instead of just CV.
- Start drafting the Phase 2 task list (product performance, fast/slow
  movers, ABC classification) using the Week 2 feature table as a
  starting point.
