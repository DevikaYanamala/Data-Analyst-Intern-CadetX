# Sprint Notes — Week 1

**Programme:** Heavy Supplier & Warehouse Analytics — Data Analytics & Data Science
**Working mode:** Solo (team not yet formed)
**Phase:** 1 of 4 — Foundation & Exploration

## What was planned

Profile all source data, resolve data-quality issues, build a validated
joined dataset, write a data dictionary, and compute a first cut of
foundation KPIs — the standard Week 1 scope from the programme's task
catalogue (Category A: Data Foundation & Preparation).

## What got done

- Identified and documented a **filename-vs-content mismatch across all 11
  uploaded CSVs** — every file's name and its actual columns pointed to
  different tables. Re-identified all 11 by header inspection and worked
  from true identity throughout (`docs/data_dictionary.md`).
- Flagged that the real **supplier master table was never uploaded** —
  `purchase_orders_header.supplier_id` has no attributes to join to (8
  distinct supplier IDs, no names/ratings/lead times available).
- Profiled all 11 tables: row counts, dtypes, null rates, duplicate rows,
  key cardinality (`docs/profiling_report.md`).
- Ran referential-integrity checks across every foreign key in the schema —
  **all 16 relationship checks passed with zero orphan rows**
  (`docs/validation_report.md`).
- Found and documented a real data-quality issue: `stock_ledger` IN
  movements average ~16x the size of OUT movements, so `running_balance`
  (and therefore `inventory_master.current_stock`) grows almost
  monotonically from 2019 to 2025 rather than oscillating around a stable
  level — current stock is now ~280x the tables' own `max_stock_level`.
  Documented with evidence in `validation_report.md`; flagged as a Week 2
  priority rather than silently "fixed" with a guess.
- Cleaned units (`warehouse_capacity` → integer sqft) and parsed all date
  columns across 7 tables.
- Built three joined analytical tables: `fact_sales`, `fact_inventory`,
  `fact_purchase_orders` (`data_clean/`).
- Computed five first-cut KPIs against the cleaned data: inventory
  turnover, stockout incidence, SKU count & stock value per branch,
  supplier concentration, and PO fulfilment lead time
  (`docs/kpis_week1.md`) — two of the five are explicitly caveated as
  unreliable until the stock-accumulation issue is resolved.

## Blockers

- No supplier master file — supplier-side analysis (Category D of the
  catalogue) can only use bare `supplier_id`s until it arrives.
- `current_stock` / stock-health KPIs need the IN/OUT imbalance in
  `stock_ledger` investigated before they can be trusted for Phase 2
  (fast/slow-mover, ABC classification, stockout work).
- Working solo this week — the programme is designed for a 3-person team
  (2 Data Analysts + 1 Data Scientist); scope this week was sized down
  accordingly to what's realistic for one person in the time available,
  prioritising foundation correctness over breadth.

## Next up (Week 2 candidates)

- Investigate the stock-ledger accumulation issue directly — check whether
  it's a generation artifact or whether the movement quantities need a
  different interpretation (e.g. IN quantities aren't all "received" units).
- If a team forms: reallocate profiling/cleaning to match the original
  roadmap; if staying solo: move into Phase 1's remaining catalogue items
  (feature engineering for later forecasting work) before starting Phase 2.
- Chase the missing `suppliers.csv` file through the portal.
