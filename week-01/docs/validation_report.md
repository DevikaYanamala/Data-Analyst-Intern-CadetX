# Week 1 — Referential Integrity & Validation Report

| relationship | child rows | orphan rows | integrity |
|---|---|---|---|
| customers.branch_id -> branches.branch_id | 500 | 0 | OK |
| inventory_master.product_id -> products.product_id | 180 | 0 | OK |
| inventory_master.branch_id -> branches.branch_id | 180 | 0 | OK |
| sales_orders_header.customer_id -> customers.customer_id | 20,000 | 0 | OK |
| sales_orders_header.branch_id -> branches.branch_id | 20,000 | 0 | OK |
| sales_orders_lines.so_id -> sales_orders_header.so_id | 130,402 | 0 | OK |
| sales_orders_lines.product_id -> products.product_id | 130,402 | 0 | OK |
| purchase_orders_header.branch_id -> branches.branch_id | 24,000 | 0 | OK |
| purchase_orders_lines.po_id -> purchase_orders_header.po_id | 155,495 | 0 | OK |
| purchase_orders_lines.product_id -> products.product_id | 155,495 | 0 | OK |
| invoices.so_id -> sales_orders_header.so_id | 18,033 | 0 | OK |
| invoices.customer_id -> customers.customer_id | 18,033 | 0 | OK |
| invoices.branch_id -> branches.branch_id | 18,033 | 0 | OK |
| payments.invoice_id -> invoices.invoice_id | 19,257 | 0 | OK |
| stock_ledger.product_id -> products.product_id | 237,230 | 0 | OK |
| stock_ledger.branch_id -> branches.branch_id | 237,230 | 0 | OK |

## Missing table: `suppliers`

`purchase_orders_header.supplier_id` references **8 distinct suppliers** (`SUP0001, SUP0002, SUP0003, SUP0004, SUP0005, SUP0006, SUP0007, SUP0008`), but no supplier master file (supplier_id, supplier_name, rating, lead time, category, etc.) was included in this upload. Supplier-side analysis this week is therefore limited to supplier_id-level aggregates from purchase orders — full supplier profiling is blocked until that file is provided.

## Duplicate key values (not full-row duplicates)

- `invoices.invoice_id`: 197 values appear on more than one row (197 duplicate combinations found in profiling) — needs a source-side fix; kept as-is here and flagged rather than silently dropped.
- `payments.payment_id`: 202 values appear on more than one row — same treatment.

## Key data-quality finding: runaway stock accumulation

`stock_ledger` IN movements average **160 units** per transaction while OUT movements average only **10 units** — receipts are ~15x larger than shipments. Because this repeats across ~2,200 days of history, `running_balance` climbs almost monotonically rather than oscillating around a stable level: for `P001` at `DEL001` it goes from **186** (2019) to **115,928** (2025).

`inventory_master.current_stock` is simply the latest `running_balance` per product/branch (verified: ratio is exactly 1.00 across all 180 rows), so it inherits this — current stock reaches **121,013 units**, while `max_stock_level` (the supposed capacity ceiling from `products`/`inventory_master`) tops out at **582 units**. Current stock is ~208x its own stated maximum, and physically implausible for a 45,230 sqft warehouse holding 38.5 kg hydraulic pumps.

**Implication for this week's KPIs:** stockout/reorder-level metrics and current-stock-based turnover (KPI 1 and KPI 2 in `kpis_week1.md`) are computed as specified, but read as unreliable until this is resolved — the reorder/safety/max-stock thresholds appear to have been generated independently of the ledger's running balance, not calibrated against it. Recommend raising this with the programme team and treating it as a Week 2 priority (`Data Integrity & Error Detection`, `Inventory Movement Anomaly Detection` in the task catalogue) before building further inventory-health analysis on top of `current_stock`.
