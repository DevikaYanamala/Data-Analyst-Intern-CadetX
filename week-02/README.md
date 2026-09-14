# Week 2 — Supplier Integration & Stock Anomaly Investigation

**Phase:** 1 of 4 — Foundation & Exploration (weeks 1–3)

## What shipped this week

1. Integrated the previously-missing supplier master table and built real
   supplier contribution, reliability, dependency, and lead-time analysis.
2. Root-caused the stock-ledger accumulation issue flagged in Week 1 —
   traced it to IN/OUT movement quantities that behave like two unrelated
   random distributions, not a real warehousing pattern.
3. Built a first feature table for later forecasting/optimisation work.

## Repo structure

```
week-02/
├── README.md                       ← you are here
├── scripts/
│   ├── 01_integrate_suppliers.py
│   ├── 02_stock_anomaly_investigation.py
│   └── 03_feature_engineering.py
├── data_clean/                     NEW this week only: suppliers, dependency
│                                    & feature CSVs. Base tables (products,
│                                    fact_sales, stock_ledger, etc.) live in
│                                    ../week-01/data_clean/ and aren't duplicated.
├── charts/
│   └── stock_runaway_p001_del001.png
└── docs/
    ├── supplier_analysis.md
    ├── stock_anomaly_investigation.md  ⚠ root-cause finding
    ├── feature_engineering.md
    └── sprint_notes.md
```

## How to reproduce

```bash
cd week-02/scripts
python3 01_integrate_suppliers.py          # -> ../docs/supplier_analysis.md
python3 02_stock_anomaly_investigation.py  # -> ../docs/stock_anomaly_investigation.md, ../charts/
python3 03_feature_engineering.py          # -> ../data_clean/features_week2.csv, ../docs/feature_engineering.md
```

Requires `pandas` and `matplotlib`. Scripts read Week 1's cleaned tables
directly from `../week-01/data_clean/` (not duplicated here) plus
`suppliers.csv` from the corrected dataset copy — see
`../week-01/docs/data_dictionary.md` for the filename-mismatch background
that Week 1 worked through. Run Week 1's scripts first if starting fresh.

## Headline findings this week

1. **Supplier master now integrated** — 8 suppliers, all POs validated
   against it cleanly. Top 5 suppliers = 63.2% of PO value; one of those
   five (Tianjin OEM Supplies) also carries a below-average reliability
   score, putting concentration risk and reliability risk on the same
   supplier.
2. **The Week 1 stock-accumulation mystery is resolved**: it's a data
   artifact, not a real inventory condition. IN movements are *more*
   frequent than OUT movements (127,611 vs 107,165) while also averaging
   ~15x larger — the opposite of what a genuine bulk-purchasing strategy
   would look like. Recommend treating `current_stock` as unreliable for
   any absolute-level analysis going forward.
3. **77 of 180 product-branch combinations** have a reorder level that may
   not cover the supplier's lead time given current demand — a concrete,
   actionable list for Phase 3.
