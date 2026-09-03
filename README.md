# Heavy Supplier & Warehouse Analytics

Applied data analytics project — analysing supplier, product, inventory and
warehouse data to build a data-driven warehouse intelligence capability.

**Contributor:** Devika ([devikayanamala611@gmail.com](mailto:devikayanamala611@gmail.com))
**Working mode:** Solo (programme is designed for a 3-person team; noted in sprint notes)

## Weekly log

| Week | Phase | What shipped |
|---|---|---|
| 1 | Foundation & Exploration | Filename/data-integrity audit, profiling, referential-integrity validation, cleaned + joined dataset, data dictionary, 5 first-cut KPIs |

## Repo structure

```
week-01/
├── README.md                 ← you are here
├── scripts/
│   ├── 01_profiling.py       structural profiling of all 11 tables
│   ├── 02_clean_validate_join.py   cleaning, FK checks, joined fact tables
│   └── 03_kpis.py            5 foundation KPIs
├── data_clean/                cleaned CSVs (true names) + joined fact tables + KPI outputs
└── docs/
    ├── data_dictionary.md    ⚠ start here — explains the filename mismatch
    ├── profiling_report.md
    ├── validation_report.md  ⚠ key data-quality finding on inventory stock
    ├── kpis_week1.md
    └── sprint_notes.md
```

## How to reproduce

```bash
cd week-01/scripts
python3 01_profiling.py           # -> ../docs/profiling_report.md
python3 02_clean_validate_join.py # -> ../data_clean/*.csv, ../docs/validation_report.md
python3 03_kpis.py                # -> ../docs/kpis_week1.md
```

Requires `pandas`. Raw source CSVs are read from the original upload
location referenced in the scripts — point `RAW_DIR` at your own copy of
the 11 files if reproducing elsewhere, and see `data_dictionary.md` for
which real table is behind which filename.

## Headline findings this week

1. **All 11 uploaded CSVs have filenames that don't match their contents** —
   documented and worked around; see `docs/data_dictionary.md`.
2. **The real supplier master table is missing** from this upload — only a
   bare `supplier_id` is available via purchase orders.
3. **Schema integrity is otherwise solid** — all 16 foreign-key checks
   across the dataset passed with zero orphan rows.
4. **`inventory_master.current_stock` shows signs of runaway accumulation** —
   stock-ledger receipts run ~16x larger than shipments on average, so
   balances climb almost every year rather than holding steady. Flagged
   as a priority for Week 2 before building further inventory-health work
   on top of it.
