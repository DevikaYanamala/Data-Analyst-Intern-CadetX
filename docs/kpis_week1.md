# Week 1 — First-Cut KPI Results
Computed on the cleaned, joined dataset. These are starting points for Phase 2 (Weeks 4-6), not final numbers.

## 1. Inventory turnover ratio (12-month units sold ÷ avg stock on hand)

> **Caveat:** `current_stock` shows signs of runaway accumulation — see "Key data-quality finding" in `validation_report.md`. Treat this KPI as directional only until that's resolved; the near-zero ratios below likely understate real turnover.

Fleet-wide median turnover: **0.07x**. Fastest mover: **Pressure Sensor PS-90** (0.08x). Slowest: **Idler Wheel IW-55** (0.06x).

| product | category | units sold (12m) | avg stock | turnover |
|---|---|---|---|---|
| Pressure Sensor PS-90 | Sensors | 8158 | 105830 | 0.08x |
| Fuel Pump FP-350 | Engine | 8133 | 105382 | 0.08x |
| Air Filter AF-120 | Filters | 7487 | 108352 | 0.07x |
| Track Chain TC-45 | Undercarriage | 7650 | 106480 | 0.07x |
| Hydraulic Pump HP-300 | Hydraulic | 7463 | 107331 | 0.07x |

## 2. Stockout incidence rate

> **Caveat:** same runaway-accumulation issue as KPI 1 — `safety_stock`/`reorder_level` (hundreds of units) look uncalibrated against the inflated `current_stock` (100K+ units), which is almost certainly why this reads as 0%. Not read as "inventory is healthy."

**0.0%** of SKU-branch combinations are at or below safety stock; **0.0%** are at or below reorder level.

| branch | % SKUs at/below safety stock |
|---|---|
| Ahmedabad West Hub | 0.0% |
| Chennai South Hub | 0.0% |
| Delhi Central | 0.0% |
| Hyderabad Logistics | 0.0% |
| Kolkata East Depot | 0.0% |
| Pune Distribution | 0.0% |

## 3. SKU count & stock value per branch

> **Caveat:** `total_stock_value` = `current_stock` × `unit_cost`, so it inherits the same runaway-accumulation issue as KPI 1/2 — read the *relative* ranking across branches as useful, not the absolute Rs figures.

| branch | SKUs stocked | total stock value (Rs) | warehouse capacity (sqft) |
|---|---|---|---|
| Chennai South Hub | 30 | 47,798,163,500 | 41,890 |
| Pune Distribution | 30 | 47,728,085,910 | 38,750 |
| Delhi Central | 30 | 47,709,094,440 | 45,230 |
| Hyderabad Logistics | 30 | 47,224,691,630 | 36,210 |
| Ahmedabad West Hub | 30 | 46,129,795,000 | 34,120 |
| Kolkata East Depot | 30 | 44,702,846,930 | 29,880 |

## 4. Supplier concentration

Top 5 of 8 suppliers (by supplier_id — no supplier master file was provided, so names/attributes aren't available yet) account for **63.2%** of total purchase order value. All 8 shown below — concentration is low; spend is close to evenly split across suppliers.

| supplier_id | PO value (Rs) | % of total |
|---|---|---|
| SUP0005 | 57,021,219,036 | 12.9% |
| SUP0001 | 55,642,967,178 | 12.6% |
| SUP0003 | 55,639,766,618 | 12.6% |
| SUP0007 | 55,597,719,406 | 12.6% |
| SUP0008 | 55,354,898,599 | 12.5% |
| SUP0006 | 55,093,574,929 | 12.5% |
| SUP0004 | 54,060,209,221 | 12.2% |
| SUP0002 | 53,275,953,255 | 12.1% |

## 5. Purchase order fulfilment lead time

Median lead time (order → received): **18 days**. 90th percentile: **28 days**. (2370 of 24000 POs still open / not yet received.)

| branch | median lead time (days) |
|---|---|
| AHM001 | 18.0 |
| CHN001 | 18.0 |
| DEL001 | 18.0 |
| HYD001 | 17.0 |
| KOL001 | 18.0 |
| PUN001 | 18.0 |
