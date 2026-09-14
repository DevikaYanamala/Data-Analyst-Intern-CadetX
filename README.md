# Heavy Supplier & Warehouse Analytics

Applied data analytics project — analysing supplier, product, inventory and
warehouse data to build a data-driven warehouse intelligence capability.

**Contributor:** Devika ([devikayanamala611@gmail.com](mailto:devikayanamala611@gmail.com))
**Working mode:** Solo (programme is designed for a 3-person team; noted in each week's sprint notes)

## Weekly log

| Week | Phase | What shipped |
|---|---|---|
| [1](week-01/) | Foundation & Exploration | Filename/data-integrity audit, profiling, referential-integrity validation, cleaned + joined dataset, data dictionary, 5 first-cut KPIs |
| [2](week-02/) | Foundation & Exploration | Supplier master integrated, stock-ledger anomaly root-caused, feature engineering for later phases |

## Repo structure

```
├── week-01/    foundation: profiling, cleaning, first KPIs (see week-01/README.md)
├── week-02/    supplier integration, anomaly root cause, features (see week-02/README.md)
└── ...         (week-03 onward, added as the programme progresses)
```

Each week's folder is self-contained: its own `scripts/`, `data_clean/`,
`docs/`, and a `README.md` explaining that week's work. Start with each
week's README for the headline findings, and `docs/sprint_notes.md` for
what was planned vs. done.

## Note on this repo's history

Week 1's `docs/data_dictionary.md` documents a filename-mismatch issue in
the originally-downloaded dataset (every file's name didn't match its
contents) and a missing supplier master file. Both are resolved as of
Week 2 — a corrected copy of the dataset arrived with correct filenames
and `suppliers.csv` included, verified byte-identical to the original data
otherwise. Nothing about the analysis needed to be redone as a result,
only extended.
