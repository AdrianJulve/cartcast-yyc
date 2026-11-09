# Data dictionary

## `data/processed/summary.json`

| Field | Type | Description |
|---|---|---|
| `meta.latest_month` | `YYYY-MM` | Most recent month with price data |
| `meta.is_sample` | boolean | `true` when built from `data/sample/` |
| `meta.generated_at` | ISO 8601, UTC | Time of the build |
| `weekly_cost` | dollars | Cost of the default basket for the default household in the latest month |
| `weekly_cost_prev` | dollars | The same figure for the previous month |
| `outlook_band` | list of `[low, high]` | Projected weekly cost for each of the next months |
| `aisle_shares` | `{aisle: 0 to 1}` | Share of the basket cost in each aisle |
| `movers` | list of `{product, yoy}` | 12-month change in average price, in percent, for each basket item |
| `swaps` | list of objects | Applicable substitutions, largest saving first. Fields: `from`, `to`, `group`, `price_from`, `price_to`, `qty_from`, `qty_to`, `weekly_saving` |

## `data/processed/dashboard.json`

This is the payload embedded in the site.

| Field | Description |
|---|---|
| `months` | Month labels for every price series, covering the chart history plus 12 earlier months |
| `products[name].series` | Alberta average price for each month, with gaps filled from the previous month |
| `products[name].aisle` | Aisle from the basket config, or from the keyword rules |
| `basket` | Default items as `{product, qty, aisle}`, with quantities per week for a family of four |
| `households` | `{key: {label, scale}}` |
| `swaps` | Substitution rules as `{from, to, ratio, group}` |
| `outlook` | `{months, annual_low, annual_high}` |
| `cpi.series["GEO \| product"]` | `{months, index, yoy}` |
| `cpi.food_yoy` | Latest 12-month change for Food purchased from stores in the headline geography |
| `stores` | List of `{name, address, community, lat, lon, kind}` |
| `summary` | Same contents as `summary.json` |

## Configuration files

Each file in `config/` has comments at the top describing its fields.
