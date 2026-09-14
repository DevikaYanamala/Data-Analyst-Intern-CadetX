# Week 2 — Supplier Integration & Analysis

`suppliers.csv` received and joined. Referential integrity check: purchase_orders_header.supplier_id -> suppliers.supplier_id -- **24000/24000 rows OK, 0 orphans**.

8 suppliers on file, spanning 3 regions (East China, North China, South China) and 3 supplier types (Distributor, Local Vendor, OEM).

## Supplier contribution

Top 5 of 8 suppliers = **63.2%** of total PO value.

| supplier_id   | supplier_name                   | supplier_type   |   reliability_score |   lead_time_days |   grand_total |   share_pct |
|:--------------|:--------------------------------|:----------------|--------------------:|-----------------:|--------------:|------------:|
| SUP0005       | Tianjin OEM Supplies            | OEM             |                   3 |               28 |   5.70212e+10 |        12.9 |
| SUP0001       | Shenzhen OEM Supplies           | OEM             |                   5 |               19 |   5.5643e+10  |        12.6 |
| SUP0003       | Shanghai Distributor Supplies   | Distributor     |                   4 |               16 |   5.56398e+10 |        12.6 |
| SUP0007       | Suzhou Local Vendor Supplies    | Local Vendor    |                   5 |               12 |   5.55977e+10 |        12.6 |
| SUP0008       | Hangzhou OEM Supplies           | OEM             |                   4 |               26 |   5.53549e+10 |        12.5 |
| SUP0006       | Qingdao Distributor Supplies    | Distributor     |                   3 |               10 |   5.50936e+10 |        12.5 |
| SUP0004       | Ningbo Distributor Supplies     | Distributor     |                   3 |               18 |   5.40602e+10 |        12.2 |
| SUP0002       | Guangzhou Local Vendor Supplies | Local Vendor    |                   5 |               10 |   5.3276e+10  |        12.1 |

## Reliability vs. dependency risk

**1 supplier(s)** are both in the top-5 by spend AND rated reliability <= 3/5 -- concentration risk sitting on top of reliability risk:

| supplier_name        |   share_pct |   reliability_score |
|:---------------------|------------:|--------------------:|
| Tianjin OEM Supplies |        12.9 |                   3 |

## Lead time: stated vs. actual, by supplier

Positive gap = supplier runs slower than what they quote.

| supplier_name                   |   stated_days |   actual_median_days |   count |   gap_days |
|:--------------------------------|--------------:|---------------------:|--------:|-----------:|
| Guangzhou Local Vendor Supplies |            10 |                   10 |    2635 |          0 |
| Hangzhou OEM Supplies           |            26 |                   26 |    2722 |          0 |
| Ningbo Distributor Supplies     |            18 |                   18 |    2664 |          0 |
| Qingdao Distributor Supplies    |            10 |                   10 |    2752 |          0 |
| Shanghai Distributor Supplies   |            16 |                   16 |    2723 |          0 |
| Shenzhen OEM Supplies           |            19 |                   19 |    2653 |          0 |
| Suzhou Local Vendor Supplies    |            12 |                   12 |    2727 |          0 |
| Tianjin OEM Supplies            |            28 |                   28 |    2754 |          0 |

## Single-source product risk

0 of 30 products are sourced from exactly one supplier (100% dependency) -- any disruption at that supplier stops that product's inbound supply entirely.

