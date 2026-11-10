# Data sources

## 1. Monthly average retail prices for selected products (StatCan Table 18-10-0245-01)

- Table page: <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810024501>
- Download: `https://www150.statcan.gc.ca/n1/tbl/csv/18100245-eng.zip`, which contains `18100245.csv` and `18100245_MetaData.csv`.
- Geography: Canada, the provinces, Whitehorse and Yellowknife. CartCast uses `GEO = "Alberta"`. StatCan does not publish these prices for Calgary.
- Frequency: monthly, released about five to six weeks after the reference month.
- Method: prices come from retailers' scanner (point-of-sale) data. Each product is either a specific size (for example `Eggs, 1 dozen`) or standardized to one (for example `Block cheese, 500 grams`). Fresh produce and meat are priced per kilogram.
- Columns used: `REF_DATE` (month), `GEO`, `Products` (product) and `VALUE` (price).

Known issues:

- Some values are suppressed and appear as blanks. The loader drops them, and the dashboard uses the previous month's price in their place.
- StatCan occasionally renames products when it updates the list. `cartcast validate` reports names that no longer match and suggests the closest current names.
- StatCan advises against using average prices to measure change over time. See `docs/methodology.md`.

## 2. Consumer Price Index, monthly, not seasonally adjusted (StatCan Table 18-10-0004-01)

- Table page: <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1810000401>
- Download: `https://www150.statcan.gc.ca/n1/tbl/csv/18100004-eng.zip`. The file is large, so it is read in chunks.
- Filters: `GEO` is "Alberta" or "Calgary, Alberta"; the product is "All-items" or "Food purchased from stores"; `UOM` is "2002=100".
- Derived field: the 12-month percentage change, calculated as the index divided by the index 12 months earlier, minus 1.
- Used for: the grocery inflation figure on the dashboard. The Calgary CMA series is used when it is available, and Alberta otherwise (`cpi_headline_geo` and `cpi_fallback_geo` in `config/settings.yaml`).

## 3. Market Basket Measure thresholds (StatCan Table 11-10-0066-01)

- Table page: <https://www150.statcan.gc.ca/t1/tbl1/en/tv.action?pid=1110006601>
- Download: `https://www150.statcan.gc.ca/n1/tbl/csv/11100066-eng.zip`
- Dimensions: Geography (MBM region), Base year, Dollar concept and Component. Calgary is its own MBM region.
- Filters: the geography contains "Calgary", the component is Food, the dollar concept is current dollars, and the newest base year is used.
- What it measures: the yearly cost of a nutritious diet, based on Health Canada's National Nutritious Food Basket, for a family of two adults and two children. It is part of the Market Basket Measure, Canada's official poverty line.
- Frequency: annual. The latest year is usually one to two years behind the current date.
- Used for: the Calgary food benchmark in the "Basket cost by aisle" panel.

## 4. Calgary Business Licences (City of Calgary Open Data, `vdjc-pybd`)

- Dataset page: <https://data.calgary.ca/d/vdjc-pybd>
- API: `https://data.calgary.ca/resource/vdjc-pybd.json` (Socrata SoQL)
- Fields used: `tradename`, `address`, `comdistnm` (community), `licencetypes`, `jobstatusdesc` and `point` (GeoJSON longitude and latitude).
- Query: the licence type includes "RETAIL DEALER - PREMISES", the status is "Licensed" or "Pending Renewal", and the trade name contains one of the grocery keywords listed in `config/settings.yaml` under `stores`.
- Classification: a store is a supermarket if its name matches a chain or supermarket keyword, and specialty otherwise. Names that match an exclusion keyword, such as "flea market", are removed.
- Limitation: there is no grocery licence category, so keyword matching will miss some stores and include a few that are not grocers. The keyword lists can be adjusted in the config.

## 5. Canada's Food Price Report 2026

- Report page: <https://www.dal.ca/sites/agri-food/research/canada-s-food-price-report-2026.html>
- Used for: the outlook range only. The report forecasts a 4 to 6 percent increase in overall food prices in 2026, set in `dashboard.outlook_annual_low` and `dashboard.outlook_annual_high`.
- Other figures from the report used in the presentation: an average family of four is expected to spend $17,571.79 on food in 2026, up to $994.63 more than in 2025. Food prices are 27 percent higher than five years ago, and Alberta is among the provinces forecast to rise above the national average.

## Snapshot (`data/snapshot/`)

`cartcast fetch` downloads the full tables into `data/raw/`, which is ignored by git,
then writes the rows the dashboard needs into `data/snapshot/`:

| File | Contents |
|---|---|
| `prices_alberta.csv` | Alberta rows from Table 18-10-0245-01 for the last 60 months |
| `cpi_calgary_alberta.csv` | Calgary and Alberta rows for All-items and Food purchased from stores, from 2015 |
| `mbm_calgary.csv` | All Calgary rows from Table 11-10-0066-01 |
| `stores_calgary.json` | Licence records classified as food retailers |
| `manifest.json` | Download time, row counts and latest periods for each file |

The snapshot is committed so that anyone can rebuild the dashboard from the same
real data. The monthly workflow refreshes it.

## Sample dataset (`data/sample/`)

The sample files are synthetic and are generated by `scripts/make_sample_data.py`
with a fixed random seed, so the output is reproducible. They use the same column
layouts as the real sources. Price series start from the real Alberta average
prices for June 2024 and are simulated from there. Store names begin with "SAMPLE".
The dashboard shows a banner whenever sample data is used.
