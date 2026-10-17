# Week 4 — Margin-Based Value & Risk Prioritization

**Phase:** 2 of 4 — Product Performance (first week)

## What shipped this week

1. Re-classified all 30 products by margin contribution instead of revenue
   (Week 3 found revenue-based ABC was really a price-tier split) — 4
   products land in a different class depending on which metric is used.
2. Built a combined risk-prioritization score tying together margin-based
   value (this week) with supplier single-sourcing, supplier reliability,
   and reorder-vs-lead-time gaps (all from Week 2) into one ranked list.
3. Traced the top-risk products back to specific suppliers — 4 of the 6
   highest-priority products share the same supplier Week 2 already flagged
   for carrying both concentration and reliability risk.

This picks up directly from the Phase 2 task list drafted at the end of
Week 3 (`week-03/docs/phase2_task_list.md`) — items 1, 3, and 5 from that
list. Branch-level seasonality and the demand_volatility_tier revisit
(items 2 and 6) are not done here — carried forward, noted below.

## Repo structure

```
week-04/
├── README.md                          ← you are here
├── scripts/
│   ├── 01_margin_based_classification.py
│   └── 02_risk_prioritization.py
├── data_clean/                        margin_classification.csv, risk_prioritization.csv
└── docs/
    ├── margin_classification.md
    └── risk_prioritization.md         ⚠ concrete product/supplier watchlist
```

## How to reproduce

```bash
cd week-04/scripts
python3 01_margin_based_classification.py  # -> ../docs/margin_classification.md
python3 02_risk_prioritization.py          # -> ../docs/risk_prioritization.md (reads script 1's output)
```

Run in order — script 2 reads script 1's `data_clean/margin_classification.csv`.
Reads `fact_sales.csv`, `products.csv`, `purchase_orders_header.csv`,
`purchase_orders_lines.csv` from `../week-01/data_clean/`, and
`suppliers.csv`, `features_week2.csv` from `../week-02/data_clean/`
(none duplicated here).

## Headline findings this week

1. **Margin-based classification shifts 4 of 30 products into a different
   class than revenue-based ABC did.** High sales value doesn't always mean
   high profitability per unit — worth using margin, not revenue, for any
   Phase 2 "which products matter most" decision going forward.
2. **6 products score 4+/5 on the combined risk-priority scale** — high
   margin value stacked with a low-reliability supplier and/or a reorder
   point that may not cover lead time. 4 of those 6 come from the same
   supplier (Tianjin OEM Supplies), which Week 2 already flagged as both a
   top-5-by-spend AND below-average-reliability supplier.
3. **None of the top-risk products are single-sourced** — risk here comes
   from reliability and reorder timing, not from having only one supplier
   option. Worth not conflating those two kinds of risk in any write-up.

## Carried forward to Week 5

- Branch-level seasonality (Week 3's seasonality work was pooled across all
  6 branches — a product's peak month may differ by region).
- Revisit `demand_volatility_tier` thresholds from Week 2 now that there's a
  working example (margin class) of a split that actually differentiates
  products, to use as a sanity check.
- The risk-priority score here is an untuned additive heuristic (stated
  explicitly in `docs/risk_prioritization.md`) — worth validating the
  weights rather than treating the ranking as final.
