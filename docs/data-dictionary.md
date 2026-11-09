# Data dictionary

## `data/processed/summary.json`

| Field | Type | Meaning |
|---|---|---|
| `meta.latest_month` | `YYYY-MM` | Most recent month with prices |
| `meta.is_sample` | bool | `true` when built from `data/sample/` |
| `meta.generated_at` | ISO 8601 UTC | Build time |
| `weekly_cost` | $ | Default basket cost, default household, latest month |
| `weekly_cost_prev` | $ | Same, previous month |
| `outlook_band` | `[[low, high], …]` | Projected weekly cost for the next N months |
| `aisle_shares` | `{aisle: 0–1}` | Share of basket cost by aisle |
| `movers` | `[{product, yoy}]` | 12-month change in average price (%) per basket item |
| `swaps` | `[{from, to, group, price_from, price_to, qty_from, qty_to, weekly_saving}]` | Applicable swaps, best first |

## `data/processed/dashboard.json` (embedded in the site)

| Field | Meaning |
|---|---|
| `months` | Month labels for every price series (history + 12 for yoy) |
| `products[name].series` | Alberta average price per month, forward-filled |
| `products[name].aisle` | Aisle from the basket config or keyword rules |
| `basket` | Default items `{product, qty, aisle}` (qty per week for a family of 4) |
| `households` | `{key: {label, scale}}` |
| `swaps` | Swap rules `{from, to, ratio, group}` |
| `outlook` | `{months, annual_low, annual_high}` |
| `cpi.series["GEO \| product"]` | `{months, index, yoy}` |
| `cpi.food_yoy` | Latest 12-month change, Food purchased from stores, headline geography |
| `stores` | `[{name, address, community, lat, lon, kind}]` |
| `summary` | Same as `summary.json` |

## Config files

See the comments at the top of `config/basket.yaml`, `config/swaps.yaml` and
`config/settings.yaml`.
