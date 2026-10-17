# Phase 2 Task List (draft) — Product Performance

**Phase:** 2 of 4. Phase 1 (Foundation & Exploration, weeks 1-3) closes out with this week.
This is a first draft, written against what Week 3's preview actually found —
not a generic template. Scope and priorities below should be revisited once
Phase 2 formally starts.

## What Week 3 found that Phase 2 needs to deal with

1. **Volume doesn't differentiate products — price does.** Total units sold
   per product ranges only ~44,000-47,000 (a ~7% spread) across all 30 SKUs,
   while `unit_price` ranges from Rs 310 to Rs 119,000 (a ~380x spread). Any
   "fast/slow mover" framing in Phase 2 needs to be built on revenue or margin,
   not units — a units-based split is close to noise in this dataset (see
   `docs/abc_classification_preview.md`).
2. **Seasonal amplitude is promising but not statistically confirmed yet.**
   It ranges 14%-38% of mean monthly volume across products and spreads them
   out usefully (unlike `demand_cv`), but only 3 of 30 pass an ANOVA
   significance check — barely above what chance alone would produce at
   p<0.05 across 30 tests (see `docs/seasonality_trend.md`). Re-test with
   more years of data before building a stocking plan on specific peak
   months. Separately: none of the 30 products show a genuine multi-year
   growth or decline trend — don't build a "declining products" workstream
   on this data without re-validating that finding first.
3. **ABC-by-revenue is really a price-tier split**, not a popularity split —
   6 products (Class A) carry 65.4% of revenue almost entirely because they're
   expensive, not because they sell more. Phase 2's product-performance
   framing should separate "high value" from "high demand" explicitly rather
   than collapsing them into one "top products" list.

## Draft task list for Phase 2

- [ ] Re-run the ABC/fast-mover split using **margin** (unit_price - unit_cost)
      × units, not just revenue — check whether high-price Class A products are
      also high-margin, or just high-ticket.
- [ ] Build branch-level seasonality (this week's seasonality work was pooled
      across branches) — a product's peak month may differ by region/branch.
- [ ] Cross-reference the 2 Class-A/slow-mover products (Engine Block EB-600,
      Transmission Assembly TA-800) against their supplier dependency
      (`week-02/data_clean/product_supplier_dependency.csv`) and reorder-lead-
      time flags (`week-02/data_clean/features_week2.csv`) — a high-value,
      low-volume item stocking out is a bigger loss per incident, so it's worth
      checking whether these two are also sitting on a risky supplier or a
      lead-time gap.
- [ ] Decide whether "fast/slow mover" belongs in Phase 2 at all given finding
      #1 — if units genuinely don't vary, consider dropping that framing rather
      than forcing a split onto flat data.
- [ ] Pull the 77 product-branch combinations flagged in Week 2
      (`reorder_covers_lead_time == False`) and check how many fall into
      Class A/B by revenue — prioritise fixing reorder points on high-value
      products first.
- [ ] Revisit `demand_volatility_tier` thresholds from Week 2 (everything came
      back "moderate") now that seasonality amplitude gives a working example
      of a metric that *does* spread products out — use that as a sanity check
      for whatever new thresholds get picked.

## Explicitly out of scope for now

- Full demand forecasting (mentioned in early sprint notes as Phase 3 work) —
  Phase 2 should produce the segmentation Phase 3 forecasting would use, not
  the forecast itself.
- Any conclusion about real-world seasonality drivers (e.g. "construction
  season") — this dataset's seasonality may or may not reflect anything a
  real warehouse would see; it should be validated, not assumed.
