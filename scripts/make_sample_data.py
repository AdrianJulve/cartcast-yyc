"""Generate the offline SAMPLE dataset in ``data/sample/``.

The files use the exact column layouts of the real sources so the same loaders
work on both:

* ``prices_sample.csv`` — StatCan 18-10-0245-01 layout
* ``cpi_sample.csv``    — StatCan 18-10-0004-01 layout
* ``stores_sample.json``— City of Calgary Socrata (vdjc-pybd) record layout

Prices are SYNTHETIC. Each series is anchored on the real Alberta average price
for June 2024 (StatCan via Alberta Open Data) and then simulated forwards and
backwards with category trends and noise. Store names are fictional. Never
present sample figures as real — run ``cartcast fetch`` for live data.

Usage:  python scripts/make_sample_data.py
"""

from __future__ import annotations

import csv
import json
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "data" / "sample"
SEED = 20261116
START = (2022, 1)
END = (2026, 9)
ANCHOR = (2024, 6)

# Real Alberta average retail prices, June 2024 (StatCan table 18-10-0245-01).
ALBERTA_JUNE_2024 = {
    "Beef stewing cuts, per kilogram": 20.50,
    "Beef striploin cuts, per kilogram": 29.09,
    "Beef top sirloin cuts, per kilogram": 25.97,
    "Ground beef, per kilogram": 13.52,
    "Pork loin cuts, per kilogram": 10.40,
    "Pork rib cuts, per kilogram": 9.91,
    "Whole chicken, per kilogram": 7.05,
    "Chicken breasts, per kilogram": 15.44,
    "Chicken thigh, per kilogram": 12.20,
    "Bacon, 500 grams": 6.98,
    "Wieners, 400 grams": 4.40,
    "Canned tuna, 170 grams": 1.63,
    "Milk, 1 litre": 2.98,
    "Milk, 2 litres": 5.20,
    "Milk, 4 litres": 6.01,
    "Cream, 1 litre": 4.95,
    "Butter, 454 grams": 6.25,
    "Block cheese, 500 grams": 6.97,
    "Yogurt, 500 grams": 3.53,
    "Eggs, 1 dozen": 4.97,
    "Apples, per kilogram": 6.35,
    "Oranges, per kilogram": 4.41,
    "Oranges, 1.36 kilograms": 6.50,
    "Bananas, per kilogram": 1.78,
    "Pears, per kilogram": 5.62,
    "Lemons, unit": 0.94,
    "Grapes, per kilogram": 8.42,
    "Cantaloupe, unit": 3.96,
    "Avocado, unit": 2.10,
    "Potatoes, 4.54 kilograms": 8.38,
    "Tomatoes, per kilogram": 4.93,
    "Cabbage, per kilogram": 2.89,
    "Carrots, 1.36 kilograms": 5.03,
    "Onions, per kilogram": 5.98,
    "Onions, 1.36 kilograms": 5.87,
    "Celery, unit": 3.44,
    "Cucumber, unit": 2.00,
    "Mushrooms, 227 grams": 2.92,
    "Broccoli, unit": 4.19,
    "Peppers, per kilogram": 7.43,
    "Beef rib cuts, per kilogram": 29.45,
    "Pork shoulder cuts, per kilogram": 11.04,
    "Chicken drumsticks, per kilogram": 8.49,
    "Canned salmon, 213 grams": 4.40,
    "Limes, unit": 0.72,
    "Potatoes, per kilogram": 4.77,
    "Sweet potatoes, per kilogram": 5.53,
    "Iceberg lettuce, unit": 3.43,
    "Romaine lettuce, unit": 3.45,
    "Frozen french fried potatoes, 750 grams": 3.50,
    "Frozen green beans, 750 grams": 3.88,
    "Frozen broccoli, 500 grams": 3.83,
    "Frozen corn, 750 grams": 3.68,
    "Frozen mixed vegetables, 750 grams": 3.74,
    "Frozen peas, 750 grams": 3.61,
    "White bread, 675 grams": 3.40,
    "Dry or fresh pasta, 500 grams": 3.26,
    "Cereal, 400 grams": 4.13,
    "Wheat flour, 2.5 kilograms": 5.11,
    "White sugar, 2 kilograms": 3.14,
    "Apple juice, 2 litres": 4.12,
    "Orange juice, 2 litres": 5.58,
    "Roasted or ground coffee, 340 grams": 6.62,
    "Tea (20 bags)": 4.64,
    "Ketchup, 1 litre": 4.26,
    "Vegetable oil, 3 litres": 11.90,
    "Baby food, 128 millilitres": 1.59,
    "Peanut butter, 1 kilogram": 6.17,
    "Mayonnaise, 890 millilitres": 6.31,
    "Canned baked beans, 398 millilitres": 1.91,
    "Canned tomatoes, 796 millilitres": 2.15,
    "Canned soup, 284 millilitres": 1.70,
    "Canned beans and lentils, 540 millilitres": 1.73,
    "Dried lentils, 900 grams": 3.70,
    "Deodorant, 85 grams": 7.91,
    "Toothpaste, 100 millilitres": 4.06,
    "Shampoo, 400 millilitres": 6.95,
    "Salmon, per kilogram": 27.83,
    "Shrimp, 300 grams": 7.28,
    "Meatless burgers, 226 grams": 6.58,
    "Soy milk, 1.89 litres": 4.42,
    "Nut milk, 1.89 litres": 4.39,
    "Margarine, 907 grams": 7.49,
    "Strawberries, 454 grams": 3.86,
    "Squash, per kilogram": 5.03,
    "Salad greens, 142 grams": 4.85,
    "Frozen pizza, 390 grams": 4.77,
    "Frozen spinach, 300 grams": 1.72,
    "Frozen strawberries, 600 grams": 5.01,
    "Flatbread and pita, 500 grams": 4.08,
    "Crackers and crisp breads, 200 grams": 3.15,
    "Cookies and sweet biscuits, 300 grams": 3.42,
    "Brown rice, 900 grams": 6.26,
    "White rice, 2 kilograms": 7.51,
    "Canola oil, 3 litres": 8.47,
    "Olive oil, 1 litre": 17.31,
    "Infant formula, 900 grams": 44.59,
    "Canned corn, 341 millilitres": 1.73,
    "Canned peach, 398 millilitres": 2.46,
    "Canned pear, 398 millilitres": 2.91,
    "Dry beans and legumes, 900 grams": 3.38,
    "Tofu, 350 grams": 2.78,
    "Hummus, 227 grams": 4.00,
    "Salsa, 418 millilitres": 4.72,
    "Pasta sauce, 650 millilitres": 3.03,
    "Salad dressing, 475 millilitres": 3.35,
    "Almonds, 200 grams": 4.62,
    "Peanuts, 450 grams": 4.17,
    "Sunflower seeds, 400 grams": 4.82,
    "Laundry detergent, 4.43 litres": 13.75,
}

# (annual trend, monthly noise sd, seasonal amplitude) by keyword; first match wins.
PROFILES = [
    ("beef", 0.10, 0.045, 0.0),
    ("coffee", 0.11, 0.02, 0.0),
    ("olive oil", -0.04, 0.02, 0.0),
    ("chicken", 0.045, 0.04, 0.0),
    ("pork", 0.03, 0.045, 0.0),
    ("salmon", 0.03, 0.04, 0.0),
    ("eggs", 0.01, 0.012, 0.0),
    ("milk", 0.02, 0.005, 0.0),
    ("butter", 0.0, 0.03, 0.0),
    ("cheese", 0.02, 0.015, 0.0),
    ("bananas", 0.01, 0.006, 0.0),
    ("per kilogram", 0.025, 0.035, 0.06),
    ("unit", 0.025, 0.04, 0.08),
    ("frozen", 0.03, 0.02, 0.0),
]
DEFAULT_PROFILE = (0.03, 0.015, 0.0)


def months():
    y, m = START
    while (y, m) <= END:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def months_from_anchor(y: int, m: int) -> int:
    return (y - ANCHOR[0]) * 12 + (m - ANCHOR[1])


def profile(name: str):
    low = name.lower()
    for key, trend, sd, season in PROFILES:
        if key in low:
            return trend, sd, season
    return DEFAULT_PROFILE


def statcan_row(
    table_vector: int,
    ref: str,
    geo: str,
    product_col: str,
    product: str,
    uom: str,
    value: float | None,
    coordinate: str,
) -> dict[str, str]:
    return {
        "REF_DATE": ref,
        "GEO": geo,
        "DGUID": "",
        product_col: product,
        "UOM": uom,
        "UOM_ID": "81",
        "SCALAR_FACTOR": "units",
        "SCALAR_ID": "0",
        "VECTOR": f"v{table_vector}",
        "COORDINATE": coordinate,
        "VALUE": "" if value is None else f"{value:.2f}",
        "STATUS": "",
        "SYMBOL": "",
        "TERMINATED": "",
        "DECIMALS": "2",
    }


def make_prices(rng: random.Random) -> int:
    cols = [
        "REF_DATE",
        "GEO",
        "DGUID",
        "Products",
        "UOM",
        "UOM_ID",
        "SCALAR_FACTOR",
        "SCALAR_ID",
        "VECTOR",
        "COORDINATE",
        "VALUE",
        "STATUS",
        "SYMBOL",
        "TERMINATED",
        "DECIMALS",
    ]
    rows = []
    for p_i, (product, anchor) in enumerate(ALBERTA_JUNE_2024.items(), start=1):
        trend, sd, season = profile(product)
        # Smooth random walk around the trend so series look like real prices.
        walk, level = 0.0, {}
        ordered = list(months())
        for y, m in ordered:
            walk = 0.6 * walk + rng.gauss(0, sd)
            k = months_from_anchor(y, m)
            seasonal = season * math.sin(2 * math.pi * (m - 3) / 12)
            level[(y, m)] = anchor * (1 + trend) ** (k / 12) * (1 + walk + seasonal)
        shift = anchor / level[ANCHOR]  # pin June 2024 to the real value exactly
        for g_i, geo in enumerate(("Canada", "Alberta")):
            geo_factor = 1.0 if geo == "Alberta" else 0.985
            for y, m in ordered:
                value = level[(y, m)] * shift * geo_factor
                if geo == "Alberta" and rng.random() < 0.004:
                    value = None  # mimic occasional StatCan suppression
                rows.append(
                    statcan_row(
                        900000 + p_i * 10 + g_i,
                        f"{y}-{m:02d}",
                        geo,
                        "Products",
                        product,
                        "Dollars",
                        value,
                        f"{g_i + 1}.{p_i}",
                    )
                )
    with (OUT / "prices_sample.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def make_cpi(rng: random.Random) -> int:
    pcol = "Products and product groups"
    cols = [
        "REF_DATE",
        "GEO",
        "DGUID",
        pcol,
        "UOM",
        "UOM_ID",
        "SCALAR_FACTOR",
        "SCALAR_ID",
        "VECTOR",
        "COORDINATE",
        "VALUE",
        "STATUS",
        "SYMBOL",
        "TERMINATED",
        "DECIMALS",
    ]
    # Rough 2022-01 starting levels (2002=100) and annual rates; synthetic.
    series = {
        ("Alberta", "All-items"): (152.0, 0.032),
        ("Alberta", "Food purchased from stores"): (165.0, 0.046),
        ("Calgary, Alberta", "All-items"): (151.0, 0.033),
        ("Calgary, Alberta", "Food purchased from stores"): (164.0, 0.047),
        ("Canada", "All-items"): (145.3, 0.031),
        ("Alberta", "Shelter"): (160.0, 0.04),  # extra product the loader must filter out
    }
    rows = []
    for s_i, ((geo, prod), (start, rate)) in enumerate(series.items(), start=1):
        noise = 0.0
        for k, (y, m) in enumerate(months()):
            noise = 0.7 * noise + rng.gauss(0, 0.004)
            value = start * (1 + rate) ** (k / 12) * (1 + noise)
            rows.append(
                statcan_row(
                    800000 + s_i, f"{y}-{m:02d}", geo, pcol, prod, "2002=100", value, f"{s_i}.1"
                )
            )
    with (OUT / "cpi_sample.csv").open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=cols, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


COMMUNITIES = [
    ("BELTLINE", 51.040, -114.075),
    ("BRIDGELAND/RIVERSIDE", 51.054, -114.040),
    ("KENSINGTON", 51.053, -114.093),
    ("FOREST LAWN", 51.038, -113.968),
    ("MARLBOROUGH", 51.057, -113.960),
    ("SADDLE RIDGE", 51.130, -113.945),
    ("TUSCANY", 51.125, -114.250),
    ("BOWNESS", 51.088, -114.205),
    ("MAHOGANY", 50.900, -113.935),
    ("SUNDANCE", 50.905, -114.050),
    ("SHAWNESSY", 50.905, -114.070),
    ("CRANSTON", 50.880, -113.990),
    ("DOVER", 51.020, -113.975),
    ("OGDEN", 50.990, -114.005),
    ("HUNTINGTON HILLS", 51.115, -114.065),
    ("EDGEMONT", 51.125, -114.140),
    ("SIGNAL HILL", 51.020, -114.180),
    ("WOODBINE", 50.940, -114.130),
    ("MCKENZIE TOWNE", 50.915, -113.960),
    ("EVANSTON", 51.175, -114.105),
]
SAMPLE_NAMES = [
    ("SAMPLE SUPERMARKET", "RETAIL DEALER - PREMISES"),
    ("SAMPLE FRESH MARKET", "RETAIL DEALER - PREMISES"),
    ("SAMPLE HALAL MEAT & GROCERY", "RETAIL DEALER - PREMISES"),
    ("SAMPLE ASIAN FOOD CENTRE", "RETAIL DEALER - PREMISES; FOOD SERVICE - PREMISES (NO SEATING)"),
    ("SAMPLE BUTCHER SHOP", "RETAIL DEALER - PREMISES"),
    ("SAMPLE PRODUCE CO", "RETAIL DEALER - PREMISES"),
    ("SAMPLE SUPERMARKET EXPRESS", "RETAIL DEALER - PREMISES"),
    ("SAMPLE FLEA MARKET", "RETAIL DEALER - PREMISES"),  # excluded keyword
    ("SAMPLE AUTO PARTS", "RETAIL DEALER - PREMISES"),  # not food
]


def make_stores(rng: random.Random) -> int:
    records = []
    bid = 1000
    for comm, lat, lon in COMMUNITIES:
        for _ in range(rng.randint(2, 5)):
            name, types = rng.choice(SAMPLE_NAMES)
            bid += rng.randint(1, 50)
            records.append(
                {
                    "getbusid": str(bid),
                    "tradename": f"{name} #{bid % 97}",
                    "homeoccind": "N",
                    "address": f"{rng.randint(100, 9999)} {rng.randint(1, 130)} AV "
                    f"{rng.choice(['NE', 'NW', 'SE', 'SW'])}",
                    "comdistcd": comm[:3],
                    "comdistnm": comm,
                    "licencetypes": types,
                    "first_iss_dt": f"20{rng.randint(5, 25):02d}-0{rng.randint(1, 9)}-15",
                    "exp_dt": "2027-03-31T00:00:00.000",
                    "jobstatusdesc": rng.choice(["Licensed", "Licensed", "Pending Renewal"]),
                    "point": {
                        "type": "Point",
                        "coordinates": [
                            round(lon + rng.uniform(-0.018, 0.018), 6),
                            round(lat + rng.uniform(-0.011, 0.011), 6),
                        ],
                    },
                }
            )
    (OUT / "stores_sample.json").write_text(json.dumps(records, indent=1), encoding="utf-8")
    return len(records)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(SEED)
    print("prices rows:", make_prices(rng))
    print("cpi rows:   ", make_cpi(rng))
    print("store recs: ", make_stores(rng))
    print("wrote", OUT)


if __name__ == "__main__":
    main()
