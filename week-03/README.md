# Week 3 — Seasonality, Trend & a Phase 2 Starting Point

**Phase:** 1 of 4 — Foundation & Exploration (final week of this phase)

## What shipped this week

1. Replaced Week 2's `demand_cv` metric (which came back "moderate" for all
   180 rows and didn't differentiate anything) with trend + seasonality
   analysis per product — a metric that actually spreads products out.
2. Built a Phase 2 preview: ABC classification by revenue and a fast/mid/slow
   mover split by units — and found that the units split is close to noise,
   while the revenue split is really a price-tier split, not a popularity one.
3. Drafted the Phase 2 task list, grounded in what this week's preview
   actually found rather than written as a generic template.

## Repo structure

```
week-03/
├── README.md                          ← you are here
├── scripts/
│   ├── 01_seasonality_trend.py
│   └── 02_abc_classification_preview.py
├── data_clean/                        seasonality_trend.csv, abc_classification.csv
├── charts/
│   └── most_seasonal_products.png
└── docs/
    ├── seasonality_trend.md
    ├── abc_classification_preview.md
    └── phase2_task_list.md            ⚠ draft scope for Phase 2
```

## How to reproduce

```bash
cd week-03/scripts
python3 01_seasonality_trend.py           # -> ../docs/seasonality_trend.md, ../charts/
python3 02_abc_classification_preview.py  # -> ../docs/abc_classification_preview.md
```

Requires `pandas`, `numpy`, and `matplotlib`. Reads Week 1's `fact_sales.csv`
and `products.csv` directly from `../week-01/data_clean/` (not duplicated
here).

## Headline findings this week

1. **Seasonal amplitude at least spreads products out where `demand_cv` didn't** —
   14% to 38% of mean monthly volume across the 30 SKUs — but only 3 of 30
   products pass a statistical significance check (one-way ANOVA, p<0.05),
   which is only marginally above what 30 tests at that threshold would show
   by chance alone. Treat as candidates to monitor, not confirmed seasonality.
   No product shows a genuine multi-year growth/decline trend.
2. **Units sold barely vary across products (44,022-47,066, ~7% spread) —
   but unit price varies ~380x (Rs 310-119,000).** That means revenue
   concentration (Class A = 6 products, 65.4% of revenue) is a price-tier
   effect, not a popularity effect, and any "fast/slow mover by units" split
   is close to noise in this dataset.
3. **2 products are high-revenue but slow movers by units** (Engine Block
   EB-600, Transmission Assembly TA-800) — a different stocking risk profile
   than typical top sellers, flagged for Phase 2 to cross-check against
   supplier/lead-time risk.

## Phase 1 wrap-up

This closes Phase 1 (Foundation & Exploration). Across weeks 1-3: fixed a
filename-mismatch + missing-supplier-table problem, root-caused a stock-ledger
data artifact, and built two rounds of features — ending with a concrete,
evidence-based draft of what Phase 2 should actually prioritise rather than a
generic plan.
