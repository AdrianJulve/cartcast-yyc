"""Load the Market Basket Measure food threshold (StatCan Table 11-10-0066-01).

The Market Basket Measure (MBM) is Canada's official poverty line. Its food
component is the yearly cost of a nutritious diet (Health Canada's National
Nutritious Food Basket) for a family of two adults and two children, priced for
each MBM region. Calgary is its own region, so this is the only official,
Calgary-specific food cost that Statistics Canada publishes.

Column names are matched by prefix (``Base year``, ``Dollar concept``,
``Component``) so small changes in StatCan's labels do not break the loader.
"""

from __future__ import annotations

import math
import re
from pathlib import Path

import pandas as pd


def _col(columns, prefix: str) -> str | None:
    for col in columns:
        if col.lower().startswith(prefix.lower()):
            return col
    return None


def _base_rank(label: str) -> int:
    """'2023-base' -> 2023, so the newest base can be chosen."""
    found = re.findall(r"\d{4}", str(label))
    return int(found[0]) if found else 0


def load_mbm_food(csv_path: Path | str, geo_contains: str = "Calgary") -> pd.DataFrame:
    """Yearly MBM food threshold for one region, in current dollars.

    Returns columns ``year``, ``value``, ``geo`` and ``base`` for the newest base
    year available. Raises ValueError if no matching rows are found.
    """
    df = pd.read_csv(csv_path, dtype=str)
    comp = _col(df.columns, "Component")
    base = _col(df.columns, "Base")
    dollars = _col(df.columns, "Dollar")
    if comp is None or "GEO" not in df.columns:
        raise ValueError(f"{csv_path} does not look like StatCan table 11-10-0066-01")

    df = df[df["GEO"].str.contains(geo_contains, case=False, na=False)]
    df = df[df[comp].str.contains("food", case=False, na=False)]
    if dollars:
        df = df[df[dollars].str.contains("current", case=False, na=False)]
    if df.empty:
        raise ValueError(f"No MBM food rows for a geography containing '{geo_contains}'")

    if base:
        newest = max(df[base].dropna().unique(), key=_base_rank)
        df = df[df[base] == newest]
    out = pd.DataFrame(
        {
            "year": pd.to_numeric(df["REF_DATE"].str[:4], errors="coerce"),
            "value": pd.to_numeric(df["VALUE"], errors="coerce"),
            "geo": df["GEO"],
            "base": df[base] if base else "",
        }
    ).dropna(subset=["year", "value"])
    out["year"] = out["year"].astype(int)
    return out.sort_values("year").reset_index(drop=True)


def weekly_benchmark(annual_family4: float, household_size: int) -> float:
    """Weekly food benchmark for a household of ``household_size`` people.

    MBM thresholds for other family sizes are derived from the family-of-four
    value with the square-root equivalence scale: threshold x sqrt(size) / 2.
    """
    return annual_family4 / 52 * math.sqrt(max(1, household_size)) / 2
