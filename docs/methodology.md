# Methodology

## Basket cost

The weekly cost of the basket in a given month is:

```
weekly_cost = sum over items of (price x qty x household_scale)
```

- `price` is the Alberta average retail price from StatCan Table 18-10-0245-01, in the product's own unit (per kilogram, per package or per item).
- `qty` is the number of those units bought per week by a family of four, set in `config/basket.yaml`.
- `household_scale` adjusts quantities for household size: 0.35 for a single adult, 0.6 for a couple, 1.0 for a family of four and 1.45 for a family of six. These are planning assumptions, not survey results.
- When a price is suppressed for a month, the previous month's price is used.
- The monthly figure shown on the dashboard is the weekly cost multiplied by 52 and divided by 12.

## Change in average price

For each item, the dashboard shows the latest price divided by the price 12 months
earlier, minus 1.

Statistics Canada notes that average prices are useful for comparing price levels
within a month, but are not a pure measure of price change, because the mix of
products, package sizes and retailers changes over time. For that reason the
dashboard:

1. labels these figures "change in average price" and never calls them inflation, and
2. uses the CPI (Table 18-10-0004-01, Food purchased from stores) for the inflation figure.

## Substitutions

For a substitution from product A to product B with a quantity ratio `r`, set in
`config/swaps.yaml`:

```
weekly_saving = qty_A x price_A - (qty_A x r) x price_B
```

A substitution is suggested only when the saving is positive in the latest month.
Only the largest saving for each basket item is shown. The ratio converts between
package sizes; for example, 1 kg of fresh salmon is about 4.7 cans of 213 g, so
`r = 4.7`. Each pair in the config is assumed to be a reasonable replacement in
everyday cooking. This is a judgement, and the pairs can be edited.

## Outlook range

Starting from the latest weekly cost `C`, the low and high projections for month
`m` (1 to 3) are:

```
low  = C x 1.04 ^ (m / 12)
high = C x 1.06 ^ (m / 12)
```

The 4 and 6 percent rates are the range forecast for overall food prices in
Canada's Food Price Report 2026. The range is a scenario, not a forecast for this
specific basket.

## Calgary food benchmark

The benchmark is the food component of the Market Basket Measure (MBM) for Calgary,
from StatCan Table 11-10-0066-01. It is the yearly cost of a nutritious diet for a
family of two adults and two children. The weekly benchmark for a household of `n`
people is:

```
weekly_benchmark = annual_food_threshold / 52 x sqrt(n) / 2
```

This uses the square-root equivalence scale that Statistics Canada applies to MBM
thresholds for other family sizes. The dashboard shows the basket cost as a
percentage of the benchmark.

Two cautions apply. The MBM year usually lags the price data by one or two years,
and the MBM food basket is a nutrition standard, while the CartCast basket is a
list of common purchases. The comparison shows scale, not whether a basket is
nutritionally adequate.

## Store classification

Stores are classified by matching keywords in business licence trade names. The
limitations are described in `docs/data-sources.md`.

## Store distances

Distances on the map are straight-line distances between coordinates. Walking
times assume 4.8 km/h. Real walking routes are longer, so both figures are lower
bounds. The 1 km and 2 km rings show common short walking distances.

## Limitations

- Item prices are averages for Alberta, because StatCan does not publish them for Calgary or for individual stores. The inflation figure, food benchmark and store list are specific to Calgary.
- Average prices do not reflect sales, loyalty discounts or differences between store brands and national brands.
- The default basket is illustrative. It has not been checked against a nutritional standard such as a nutritious food basket.
- The store list depends on the quality of the licence data and on the keyword rules.
