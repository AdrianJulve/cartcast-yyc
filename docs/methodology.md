# Methodology

## Basket cost

```
weekly_cost(month) = Σ  price(product, month) × qty(product) × household_scale
```

- `price` is the Alberta average retail price from StatCan 18-10-0245-01 for that product's own unit: per kg, per package, or per unit.
- `qty` is the number of those units per week for a family of four (`config/basket.yaml`).
- `household_scale` adjusts for household size (single 0.35, couple 0.6, family of 4 1.0, family of 6 1.45). These are planning assumptions, not survey results. Say so if asked.
- A suppressed price carries the previous month's value forward.
- The monthly figure in the KPI is `weekly × 52 / 12`.

## "What moved" (12-month change)

`price(latest) / price(latest − 12 months) − 1` per item.

**Caveat (from StatCan):** average prices are good for comparing price *levels* in a
month. They are not a pure measure of price change, because product mix, package
size and retailer coverage shift over time. CartCast therefore:

1. labels these numbers as **"change in average price"**, never "inflation";
2. uses the **CPI** (18-10-0004-01, *Food purchased from stores*) for the inflation KPI.

Say this out loud in the presentation. It shows the audience you understand the data.

## Smart swaps

For a swap `from → to` with quantity ratio `r` (`config/swaps.yaml`):

```
weekly_saving = qty_from × price_from − (qty_from × r) × price_to
```

A swap is only suggested when `weekly_saving > 0` for the current month, and only
the best swap per basket item is shown. Ratios convert pack sizes, e.g. 1 kg of
fresh salmon ≈ 4.7 × 213 g cans (r = 4.7). Swaps assume nutritional and culinary
equivalence is "close enough". That's a judgement call, documented in the config.

## Outlook band

Starting from the latest weekly cost `C`, for month `m = 1…3`:

```
low  = C × (1 + 0.04)^(m/12)
high = C × (1 + 0.06)^(m/12)
```

The 4–6% range is Canada's Food Price Report 2026 forecast for overall food prices.
It's a scenario band, not a model prediction for this specific basket.

## Store classification

Keyword matching on business-licence trade names. See `docs/data-sources.md` for its
limitations.

## Known limitations

- Prices are province-wide (Alberta), not Calgary- or store-specific.
- Average prices exclude sales, loyalty discounts and store-brand differences.
- The basket is an illustrative "typical" basket, not a nutrition-validated food basket.
- The store list depends on licence data quality and keyword rules.
