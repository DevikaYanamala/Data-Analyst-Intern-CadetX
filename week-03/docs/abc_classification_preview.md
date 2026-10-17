# Week 3 — ABC Classification Preview (Phase 2 starting point)

**This is a preview, not the full Phase 2 analysis** -- Phase 2 is scoped to go much deeper on product performance. This gives it a concrete table to start from instead of a blank page.

## ABC classes by revenue (Pareto on cumulative share)

| abc_class   |   n_products |
|:------------|-------------:|
| A           |            6 |
| B           |            7 |
| C           |           17 |

Class A (6 products) accounts for 65.4% of total revenue on its own.

| product_id   | product_name                 |   revenue_share_pct |   cum_revenue_pct |
|:-------------|:-----------------------------|--------------------:|------------------:|
| P015         | Engine Block EB-600          |               21.24 |             21.24 |
| P014         | Transmission Assembly TA-800 |               14.84 |             36.08 |
| P021         | Boom Cylinder BC-400         |                8.46 |             44.54 |
| P019         | Swing Motor SWM-350          |                7.22 |             51.76 |
| P004         | Track Chain TC-45            |                7.16 |             58.92 |
| P010         | Turbocharger TB-900          |                6.47 |             65.39 |

## Fast / mid / slow movers by units sold

| mover_speed   |   n_products |
|:--------------|-------------:|
| fast          |           10 |
| mid           |           10 |
| slow          |           10 |

**Caveat before trusting this split:** total units sold per product only ranges from 44,022 to 47,066 across all 30 products -- a spread of about 7% of the mean. Every product sells almost the same volume. That means "fast/mid/slow mover by units" is splitting products on very small differences, the same way `demand_cv` did in Week 2 -- treat this tercile split as noise, not signal, until it's checked against a less uniform volume pattern (or confirmed this is really how the business behaves).

What IS a real, large difference between these products is `unit_price` (products.csv ranges from Rs 310 to Rs 119,000 -- a ~380x spread). Since volume is nearly flat across products but revenue concentration is real (Class A alone is 65.4% of revenue), **the ABC split above is effectively a price-tier split, not a popularity split** -- worth stating that plainly in any write-up rather than implying Class A products are the bestsellers.

## Where value and volume disagree

**2 product(s)** are Class A (high revenue) but slow movers by units -- likely high unit price rather than high volume. These need a different stocking logic (lower safety stock in units, but each stockout is expensive) than a typical Class A item:

| product_id   | product_name                 |   revenue_share_pct |   total_units |
|:-------------|:-----------------------------|--------------------:|--------------:|
| P015         | Engine Block EB-600          |               21.24 |         45222 |
| P014         | Transmission Assembly TA-800 |               14.84 |         45035 |

**5 product(s)** are Class C (low revenue share) but fast movers by units -- likely cheap, high-volume parts. Worth checking these aren't being under-stocked just because their revenue contribution looks small:

| product_id   | product_name          |   revenue_share_pct |   total_units |
|:-------------|:----------------------|--------------------:|--------------:|
| P016         | Radiator RD-250       |                1.72 |         46306 |
| P029         | Pressure Sensor PS-90 |                0.68 |         47066 |
| P012         | Brake Pad BP-40       |                0.44 |         45972 |
| P028         | Light Assembly LA-18  |                0.38 |         46164 |
| P007         | Hydraulic Hose HH-60  |                0.25 |         46468 |

