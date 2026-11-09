"""Load and reshape StatCan table 18-10-0245-01 (monthly average retail prices)."""

from __future__ import annotations

import difflib
from pathlib import Path

import pandas as pd

PRICE_COLUMNS = ["REF_DATE", "GEO", "Products", "UOM", "VALUE"]


def load_prices(csv_path: Path | str, geo: str = "Alberta") -> pd.DataFrame:
    """Return tidy prices: columns ``month`` (Timestamp), ``product``, ``price``.

    Rows with missing values (StatCan suppresses some cells) are dropped.
    """
    df = pd.read_csv(csv_path, usecols=lambda c: c in PRICE_COLUMNS, dtype={"VALUE": "float64"})
    missing = {"REF_DATE", "GEO", "Products", "VALUE"} - set(df.columns)
    if missing:
        raise ValueError(f"{csv_path} is missing expected StatCan columns: {sorted(missing)}")
    df = df[df["GEO"] == geo]
    if df.empty:
        raise ValueError(f"No rows for GEO='{geo}' in {csv_path}")
    out = pd.DataFrame(
        {
            "month": pd.to_datetime(df["REF_DATE"], format="%Y-%m"),
            "product": df["Products"].astype(str),
            "price": df["VALUE"],
        }
    ).dropna(subset=["price"])
    return out.sort_values(["product", "month"]).reset_index(drop=True)


def to_wide(prices: pd.DataFrame) -> pd.DataFrame:
    """Months as rows, products as columns."""
    wide = prices.pivot_table(index="month", columns="product", values="price", aggfunc="mean")
    return wide.sort_index()


def latest_month(prices: pd.DataFrame) -> pd.Timestamp:
    return prices["month"].max()


def suggest(name: str, candidates: list[str], n: int = 3) -> list[str]:
    """Closest product names, for helpful validation errors."""
    return difflib.get_close_matches(name, candidates, n=n, cutoff=0.5)


def yoy_change(wide: pd.DataFrame, product: str, month: pd.Timestamp | None = None) -> float | None:
    """12-month % change in average price for one product (None if unavailable).

    StatCan cautions that average prices are not a pure inflation measure; this is
    shown as "price change" and the CPI is used for inflation.
    """
    if product not in wide.columns:
        return None
    month = month if month is not None else wide.index.max()
    prior = month - pd.DateOffset(years=1)
    try:
        now, then = wide.at[month, product], wide.at[prior, product]
    except KeyError:
        return None
    if pd.isna(now) or pd.isna(then) or then == 0:
        return None
    return float((now / then - 1) * 100)
