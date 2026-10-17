# Week 4 — Margin-Based Classification

Re-classifying the same 30 products by total margin contribution (unit margin x units sold) instead of revenue, and checking where that changes the picture from Week 3's revenue-based ABC.

## Margin-based ABC classes

| margin_abc_class   |   n_products |
|:-------------------|-------------:|
| A                  |            8 |
| B                  |            7 |
| C                  |           15 |

Class A by margin (8 products) = 68.8% of total margin contribution.

| product_id   | product_name                 |   margin_pct |   margin_share_pct |   cum_margin_pct |
|:-------------|:-----------------------------|-------------:|-------------------:|-----------------:|
| P015         | Engine Block EB-600          |         19.7 |              19.37 |            19.37 |
| P014         | Transmission Assembly TA-800 |         18   |              12.31 |            31.68 |
| P021         | Boom Cylinder BC-400         |         22.9 |               8.96 |            40.64 |
| P019         | Swing Motor SWM-350          |         21.6 |               7.21 |            47.85 |
| P004         | Track Chain TC-45            |         18.3 |               6.06 |            53.91 |
| P011         | Hydraulic Cylinder HC-200    |         22.1 |               5.18 |            59.09 |
| P010         | Turbocharger TB-900          |         17.2 |               5.14 |            64.23 |
| P030         | Fuel Pump FP-350             |         25.1 |               4.6  |            68.83 |

## Where margin-based and revenue-based classes disagree

4 of 30 products land in a different class depending on which metric is used:

| product_id   | product_name              | revenue_abc_class   | margin_abc_class   |   margin_pct |   revenue_share_pct |   margin_share_pct |
|:-------------|:--------------------------|:--------------------|:-------------------|-------------:|--------------------:|-------------------:|
| P011         | Hydraulic Cylinder HC-200 | B                   | A                  |         22.1 |                5.08 |               5.18 |
| P030         | Fuel Pump FP-350          | B                   | A                  |         25.1 |                3.97 |               4.6  |
| P018         | Wheel Rim WR-24           | C                   | B                  |         27.4 |                2.01 |               2.54 |
| P024         | Track Roller TR-60        | C                   | B                  |         28.2 |                1.79 |               2.33 |

## Products worth a second look

6 product(s) are revenue Class A but have below-median margin % -- high sales value doesn't necessarily mean high profitability per unit:

| product_id   | product_name                 |   margin_pct |   revenue_share_pct |
|:-------------|:-----------------------------|-------------:|--------------------:|
| P015         | Engine Block EB-600          |         19.7 |               21.24 |
| P014         | Transmission Assembly TA-800 |         18   |               14.84 |
| P021         | Boom Cylinder BC-400         |         22.9 |                8.46 |
| P019         | Swing Motor SWM-350          |         21.6 |                7.22 |
| P004         | Track Chain TC-45            |         18.3 |                7.16 |
| P010         | Turbocharger TB-900          |         17.2 |                6.47 |

