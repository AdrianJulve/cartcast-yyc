from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from cartcast.config import CONFIG_DIR, BasketItem, load_config

STATCAN_HEADER = (
    "REF_DATE,GEO,DGUID,Products,UOM,UOM_ID,SCALAR_FACTOR,SCALAR_ID,VECTOR,COORDINATE,"
    "VALUE,STATUS,SYMBOL,TERMINATED,DECIMALS\n"
)


@pytest.fixture
def cfg():
    return load_config(CONFIG_DIR)


@pytest.fixture
def tiny_prices_csv(tmp_path: Path) -> Path:
    """Two products, three months, two geos, one suppressed cell."""
    rows = [
        ("2025-01", "Alberta", "Apples, per kilogram", "5.00"),
        ("2025-02", "Alberta", "Apples, per kilogram", "5.50"),
        ("2026-01", "Alberta", "Apples, per kilogram", "6.00"),
        ("2025-01", "Alberta", "Milk, 4 litres", "6.00"),
        ("2025-02", "Alberta", "Milk, 4 litres", ""),
        ("2026-01", "Alberta", "Milk, 4 litres", "6.60"),
        ("2025-01", "Canada", "Apples, per kilogram", "9.99"),
    ]
    body = "".join(f'{d},{g},,"{p}",Dollars,81,units,0,v1,1.1,{v},,,,2\n' for d, g, p, v in rows)
    path = tmp_path / "prices.csv"
    path.write_text(STATCAN_HEADER + body, encoding="utf-8")
    return path


@pytest.fixture
def wide() -> pd.DataFrame:
    idx = pd.to_datetime(["2025-01-01", "2025-02-01", "2025-03-01"])
    return pd.DataFrame(
        {
            "A, per kilogram": [10.0, 11.0, 12.0],
            "B, 500 grams": [2.0, None, 3.0],
            "C, per kilogram": [5.0, 5.0, 4.0],
        },
        index=idx,
    )


@pytest.fixture
def items() -> list[BasketItem]:
    return [
        BasketItem("A, per kilogram", 1.0, "Meat & fish"),
        BasketItem("B, 500 grams", 2.0, "Pantry"),
    ]


@pytest.fixture
def stores_json(tmp_path: Path) -> Path:
    recs = [
        {
            "tradename": "SAFEWAY #12",
            "address": "1 MAIN ST SW",
            "comdistnm": "BELTLINE",
            "point": {"type": "Point", "coordinates": [-114.07, 51.04]},
        },
        {
            "tradename": "SAFEWAY #12",
            "address": "1 MAIN ST SW",
            "comdistnm": "BELTLINE",
            "point": {"type": "Point", "coordinates": [-114.07, 51.04]},
        },  # duplicate
        {
            "tradename": "CORNER HALAL GROCERY",
            "address": "2 AV NE",
            "comdistnm": "MARLBOROUGH",
            "point": {"type": "Point", "coordinates": [-113.96, 51.05]},
        },
        {
            "tradename": "SUNDAY FLEA MARKET",
            "address": "3 AV SE",
            "comdistnm": "OGDEN",
            "point": {"type": "Point", "coordinates": [-114.0, 50.99]},
        },  # excluded keyword
        {
            "tradename": "BOB'S AUTO",
            "address": "4 AV NW",
            "comdistnm": "BOWNESS",
            "point": {"type": "Point", "coordinates": [-114.2, 51.08]},
        },  # not food
        {"tradename": "NOWHERE MARKET", "address": "5 AV NW", "comdistnm": "BOWNESS"},  # no point
    ]
    path = tmp_path / "stores.json"
    path.write_text(json.dumps(recs), encoding="utf-8")
    return path
