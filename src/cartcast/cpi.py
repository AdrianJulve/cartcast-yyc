"""Load StatCan table 18-10-0004-01 (Consumer Price Index) for selected geos/products.

The full CPI table is large, so it is streamed in chunks and filtered as it is read.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import pandas as pd


def _product_column(columns: Iterable[str]) -> str:
    for col in columns:
        if col.startswith("Products"):
            return col
    raise ValueError("No 'Products…' column found in CPI file")


def load_cpi(
    csv_path: Path | str,
    geos: list[str],
    products: list[str],
    chunksize: int = 250_000,
) -> pd.DataFrame:
    """Return tidy CPI: ``month``, ``geo``, ``product``, ``index``, ``yoy`` (%)."""
    header = pd.read_csv(csv_path, nrows=0).columns
    pcol = _product_column(header)
    keep = ["REF_DATE", "GEO", pcol, "UOM", "VALUE"]
    frames = []
    for chunk in pd.read_csv(csv_path, usecols=lambda c: c in keep, chunksize=chunksize):
        mask = chunk["GEO"].isin(geos) & chunk[pcol].isin(products)
        if "UOM" in chunk.columns:
            mask &= chunk["UOM"].astype(str).str.startswith("2002=100")
        if mask.any():
            frames.append(chunk[mask])
    if not frames:
        raise ValueError(f"No CPI rows for geos={geos} products={products}")
    df = pd.concat(frames)
    out = pd.DataFrame(
        {
            "month": pd.to_datetime(df["REF_DATE"], format="%Y-%m"),
            "geo": df["GEO"],
            "product": df[pcol],
            "index": pd.to_numeric(df["VALUE"], errors="coerce"),
        }
    ).dropna(subset=["index"])
    out = out.sort_values(["geo", "product", "month"]).reset_index(drop=True)
    out["yoy"] = out.groupby(["geo", "product"])["index"].pct_change(periods=12) * 100
    return out


def latest_yoy(cpi: pd.DataFrame, geo: str, product: str) -> tuple[pd.Timestamp, float] | None:
    sub = cpi[(cpi["geo"] == geo) & (cpi["product"] == product)].dropna(subset=["yoy"])
    if sub.empty:
        return None
    row = sub.iloc[-1]
    return row["month"], float(row["yoy"])
