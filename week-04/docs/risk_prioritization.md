# Week 4 — Risk Prioritization

Combines margin-based value (this week), supplier single-sourcing + reliability (Week 2), and reorder-vs-lead-time flags (Week 2) into one ranked list. `priority_score` = margin class (A=2/B=1/C=0) + 1 if single-sourced + 1 if that supplier's reliability <= 3/5 + 1 if flagged in any branch for reorder-level-may-not-cover-lead-time. Max possible = 5.

## Top 10 by priority score

| product_id   | product_name                 | margin_abc_class   | single_sourced   |   reliability_score |   n_branches_flagged |   priority_score |
|:-------------|:-----------------------------|:-------------------|:-----------------|--------------------:|---------------------:|-----------------:|
| P015         | Engine Block EB-600          | A                  | False            |                   3 |                    6 |                4 |
| P021         | Boom Cylinder BC-400         | A                  | False            |                   3 |                    5 |                4 |
| P004         | Track Chain TC-45            | A                  | False            |                   3 |                    6 |                4 |
| P019         | Swing Motor SWM-350          | A                  | False            |                   3 |                    5 |                4 |
| P011         | Hydraulic Cylinder HC-200    | A                  | False            |                   3 |                    4 |                4 |
| P030         | Fuel Pump FP-350             | A                  | False            |                   3 |                    3 |                4 |
| P014         | Transmission Assembly TA-800 | A                  | False            |                   5 |                    6 |                3 |
| P010         | Turbocharger TB-900          | A                  | False            |                   4 |                    6 |                3 |
| P024         | Track Roller TR-60           | B                  | False            |                   3 |                    3 |                3 |
| P001         | Hydraulic Pump HP-300        | B                  | False            |                   5 |                    2 |                2 |

## Products needing attention first

6 product(s) score 4 or 5 (out of 5) -- high value AND multiple risk factors stacked on the same SKU:

| product_id   | product_name              | margin_abc_class   | supplier_name                |   reliability_score |   n_branches_flagged |
|:-------------|:--------------------------|:-------------------|:-----------------------------|--------------------:|---------------------:|
| P015         | Engine Block EB-600       | A                  | Tianjin OEM Supplies         |                   3 |                    6 |
| P021         | Boom Cylinder BC-400      | A                  | Ningbo Distributor Supplies  |                   3 |                    5 |
| P004         | Track Chain TC-45         | A                  | Tianjin OEM Supplies         |                   3 |                    6 |
| P019         | Swing Motor SWM-350       | A                  | Tianjin OEM Supplies         |                   3 |                    5 |
| P011         | Hydraulic Cylinder HC-200 | A                  | Tianjin OEM Supplies         |                   3 |                    4 |
| P030         | Fuel Pump FP-350          | A                  | Qingdao Distributor Supplies |                   3 |                    3 |

**4 of these 6 products trace back to the same supplier: Tianjin OEM Supplies.** This matches Week 2's finding that this supplier is both a top-5-by-spend supplier AND has a below-average reliability score (3/5) -- concentration risk and reliability risk landing on the same supplier, now shown to carry through to multiple specific high-value products, not just an abstract spend percentage.

**None of the top 10 are single-sourced** (`single_sourced` is False throughout) -- consistent with Week 2's finding that 0 of 30 products are single-sourced. The risk here is entirely driven by margin class, supplier reliability, and reorder-lead-time gaps, not single-sourcing -- worth keeping that distinction clear rather than conflating "risky" with "single-sourced."

## Caveat

This score is a simple additive heuristic, not a validated risk model -- the weights (1 point per factor) are a starting point, not tuned. Useful for sorting a list to look at first, not for a confident "this product is N times riskier than that one" claim.
