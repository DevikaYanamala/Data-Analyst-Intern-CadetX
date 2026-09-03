# Data Dictionary — Heavy Supplier & Warehouse Analytics

## ⚠️ Filename mismatch — read this first

The eleven CSVs downloaded from the portal this week have **filenames that do
not match their contents**. Every file's header row identifies a different
table than the name on the file. This dictionary describes each table by its
**true identity** (verified from its actual columns), not its filename.

| Uploaded filename | Actually contains |
|---|---|
| `customers.csv` | **branches** (warehouse/branch master) |
| `invoices.csv` | **inventory_master** (current stock per product per branch) |
| `purchase_orders_header.csv` | **products** (product master) |
| `sales_orders_header.csv` | **purchase_orders_lines** |
| `products.csv` | **payments** |
| `payments.csv` | **invoices** |
| `sales_orders_lines.csv` | **sales_orders_header** |
| `purchase_orders_lines.csv` | **purchase_orders_header** |
| `suppliers.csv` | **stock_ledger** |
| `inventory_master.csv` | **customers** |
| `stock_ledger.csv` | **sales_orders_lines** |

**Also missing:** a real `suppliers.csv` (supplier_id, supplier_name, rating,
category, lead time, etc.) was never included — only 11 of the 12 files
listed in the programme brief arrived, and none of the 11 contain supplier
attributes. `purchase_orders_header` carries a `supplier_id` foreign key
(8 distinct values: SUP0001–SUP0008) with nothing to join it to. Flagged for
the portal team; supplier-side KPIs this week use `supplier_id` alone.

All scripts in `/scripts` read files by their **true identity**, and all
cleaned outputs in `/data_clean` are saved under their **correct** names —
so everything downstream of this week is unambiguous. Only the raw upload
folder still carries the wrong filenames.

---

## Tables

### `branches` (6 rows) — one per warehouse
| field | type | meaning |
|---|---|---|
| branch_id | string, PK | e.g. `DEL001` |
| branch_name | string | e.g. Delhi Central |
| city / state / region | string | location |
| warehouse_type | string | Central / Regional / Branch / Service Hub |
| warehouse_capacity_sqft | int | cleaned from `"45230 sqft"` text |
| service_center_available | string | Yes/No |
| manager_id | int | branch manager reference |
| total_employees | int | headcount |
| avg_monthly_revenue | int | Rs |
| monthly_operational_cost | int | Rs |
| market_demand_index | int | 1–10 relative demand score |

### `customers` (500 rows) — one per customer
| field | type | meaning |
|---|---|---|
| customer_id | string, PK | e.g. `C0001` |
| customer_type | string | segment, e.g. Retail |
| industry_segment | string | e.g. Construction |
| city / state / region | string | location |
| pincode | int | postal code |
| branch_id | string, FK → branches | home branch |
| credit_limit / current_balance | int | Rs |
| payment_terms | string | e.g. Advance, Net 30 |
| customer_since | date | onboarding date |
| last_purchase_date | date | most recent order |
| total_purchase_value | int | lifetime Rs |
| customer_rating | int | 1–5 |

### `products` (30 rows) — one per SKU
| field | type | meaning |
|---|---|---|
| product_id | string, PK | e.g. `P001` |
| product_name / category / machine_type / brand / model_compatibility | string | catalogue attributes |
| unit_cost / unit_price / margin_percentage | number | economics |
| gst_rate | int | 18 or 28 |
| weight_kg / dimensions_cm / material_type | — | physical spec |
| warranty_months | int | |
| reorder_level / safety_stock / max_stock_level | int | planning thresholds (see data-quality note) |
| lead_time_days | int | supplier lead time assumption |
| criticality_level / usage_frequency | string | Low/Medium/High |
| uom | string | piece / set / cartridge |
| last_purchase_price / last_purchase_date | — | most recent procurement |

### `inventory_master` (180 rows = 30 products × 6 branches)
| field | type | meaning |
|---|---|---|
| product_id | string, FK → products | |
| branch_id | string, FK → branches | |
| opening_stock | int | period-opening qty |
| reorder_level / safety_stock / max_stock | int | thresholds (small scale, hundreds) |
| current_stock | int | **latest `stock_ledger.running_balance`** — see data-quality note, six-figure scale |
| warehouse_bin | string | bin location code |

### `suppliers` — **not provided this upload**
Only referenced via `supplier_id` in `purchase_orders_header`. No attributes available yet.

### `sales_orders_header` (20,000 rows) — one per sales order
| field | type | meaning |
|---|---|---|
| so_id | string, PK | e.g. `SO-990591` |
| customer_id | string, FK → customers | |
| branch_id | string, FK → branches | fulfilling branch |
| order_date / delivery_date | date | |
| order_status | string | Delivered / Pending |
| payment_terms | string | |
| total_order_value / total_gst_amount / grand_total | number | Rs |
| sales_channel | string | Counter Sale / Online / etc. |

### `sales_orders_lines` (130,402 rows) — one per line item
| field | type | meaning |
|---|---|---|
| so_id | string, FK → sales_orders_header | |
| line_number | int | line position within order |
| product_id | string, FK → products | |
| quantity / unit_price / gst_rate | number | |
| line_total / gst_amount / line_grand_total | number | Rs |

### `purchase_orders_header` (24,000 rows) — one per purchase order
| field | type | meaning |
|---|---|---|
| po_id | string, PK | e.g. `PO-141186` |
| supplier_id | string | **FK with no master table (see above)** |
| branch_id | string, FK → branches | receiving branch |
| order_date / expected_delivery_date / received_date | date | `received_date` is null for ~9.9% of rows (not yet received) |
| po_status | string | Received / Pending |
| total_cost / total_gst_amount / grand_total | number | Rs |

### `purchase_orders_lines` (155,495 rows) — one per line item
| field | type | meaning |
|---|---|---|
| po_id | string, FK → purchase_orders_header | |
| line_number | int | |
| product_id | string, FK → products | |
| quantity / unit_cost / gst_rate | number | |
| line_total / gst_amount / line_grand_total | number | Rs |

### `invoices` (18,033 rows)
| field | type | meaning |
|---|---|---|
| invoice_id | string, PK* | *197 duplicate combinations found — flagged, not deduped blindly |
| so_id | string, FK → sales_orders_header | |
| customer_id | string, FK → customers | |
| branch_id | string, FK → branches | |
| invoice_date / due_date | date | |
| total_order_value / total_gst_amount / grand_total | number | Rs |
| payment_status | string | Paid / Unpaid / Partial |

### `payments` (19,257 rows)
| field | type | meaning |
|---|---|---|
| payment_id | string, PK* | *202 duplicate combinations found — flagged |
| invoice_id | string, FK → invoices | |
| payment_date | date | |
| payment_amount | number | Rs |
| payment_method | string | Cheque / Credit Card / Cash / Bank Transfer |

### `stock_ledger` (237,230 rows) — every stock movement
| field | type | meaning |
|---|---|---|
| movement_id | string, PK | |
| product_id | string, FK → products | |
| branch_id | string, FK → branches | |
| movement_type | string | IN / OUT / ADJUSTMENT |
| movement_date | date | |
| quantity | int | units moved |
| reference_type | string | SO / PO / ADJ |
| reference_id | string | links back to the originating sales or purchase order |
| running_balance | int | cumulative stock after this movement — see data-quality note |

---

## Entity relationships (as verified — all checks passed)

```
branches ──< customers ──< sales_orders_header ──< sales_orders_lines >── products
   │                              │
   │                              └──< invoices ──< payments
   │
   └──< purchase_orders_header ──< purchase_orders_lines >── products
   │        (supplier_id: no master table)
   │
   └──< inventory_master >── products
   │
   └──< stock_ledger >── products  (reference_id → so_id / po_id by reference_type)
```

Every foreign key listed above was checked against its parent table on this
week's data — zero orphan rows. Full results in `validation_report.md`.
