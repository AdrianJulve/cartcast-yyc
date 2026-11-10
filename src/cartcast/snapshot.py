"""Write a compact copy of the real source data to ``data/snapshot/``.

The raw StatCan downloads are large (the CPI table covers every product and
geography in Canada), so they are not committed. After ``cartcast fetch``, this
module keeps only the rows the dashboard needs:

* Alberta average retail prices for the last N months
* CPI rows for Calgary and Alberta
* the Calgary Market Basket Measure rows
* City of Calgary licences classified as food retailers

The snapshot is small enough to commit, so the dashboard can be rebuilt from
real data without downloading anything.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .stores import food_retailer_kind

PRICES_FILE = "prices_alberta.csv"
CPI_FILE = "cpi_calgary_alberta.csv"
MBM_FILE = "mbm_calgary.csv"
STORES_FILE = "stores_calgary.json"
MANIFEST_FILE = "manifest.json"

STORE_FIELDS = [
    "getbusid",
    "tradename",
    "address",
    "comdistnm",
    "licencetypes",
    "jobstatusdesc",
    "first_iss_dt",
    "point",
]


def write_prices(raw_csv: Path, out_csv: Path, geo: str, months: int) -> dict[str, Any]:
    keep = ["REF_DATE", "GEO", "Products", "UOM", "VALUE"]
    df = pd.read_csv(raw_csv, usecols=lambda c: c in keep, dtype=str)
    df = df[df["GEO"] == geo]
    if df.empty:
        raise ValueError(f"No price rows for GEO='{geo}' in {raw_csv}")
    recent = sorted(df["REF_DATE"].unique())[-months:]
    df = df[df["REF_DATE"].isin(recent)]
    df.to_csv(out_csv, index=False)
    return {
        "rows": len(df),
        "first_month": recent[0],
        "latest_month": recent[-1],
        "products": int(df["Products"].nunique()),
    }


def write_cpi(
    raw_csv: Path, out_csv: Path, geos: list[str], products: list[str], since: str = "2015-01"
) -> dict[str, Any]:
    header = pd.read_csv(raw_csv, nrows=0).columns
    pcol = next(c for c in header if c.startswith("Products"))
    keep = ["REF_DATE", "GEO", pcol, "UOM", "VALUE"]
    frames = []
    for chunk in pd.read_csv(raw_csv, usecols=lambda c: c in keep, dtype=str, chunksize=250_000):
        mask = chunk["GEO"].isin(geos) & chunk[pcol].isin(products) & (chunk["REF_DATE"] >= since)
        if mask.any():
            frames.append(chunk[mask])
    if not frames:
        raise ValueError(f"No CPI rows for {geos} / {products} in {raw_csv}")
    df = pd.concat(frames)
    df.to_csv(out_csv, index=False)
    found = sorted(df["GEO"].unique())
    return {"rows": len(df), "latest_month": df["REF_DATE"].max(), "geographies": found}


def write_mbm(raw_csv: Path, out_csv: Path, geo_contains: str) -> dict[str, Any]:
    df = pd.read_csv(raw_csv, dtype=str)
    df = df[df["GEO"].str.contains(geo_contains, case=False, na=False)]
    if df.empty:
        raise ValueError(f"No MBM rows for a geography containing '{geo_contains}'")
    cols = [
        c
        for c in df.columns
        if c in ("REF_DATE", "GEO", "VALUE")
        or c.lower().startswith(("base", "dollar", "component"))
    ]
    df[cols].to_csv(out_csv, index=False)
    return {
        "rows": len(df),
        "latest_year": df["REF_DATE"].max(),
        "geographies": sorted(df["GEO"].unique()),
    }


def write_stores(raw_json: Path, out_json: Path, settings: dict[str, Any]) -> dict[str, Any]:
    records = json.loads(raw_json.read_text(encoding="utf-8"))
    kept = [
        {k: r[k] for k in STORE_FIELDS if k in r}
        for r in records
        if food_retailer_kind(r, settings) and r.get("point")
    ]
    out_json.write_text(json.dumps(kept, indent=1), encoding="utf-8")
    return {"records": len(kept), "downloaded": len(records)}


def write_manifest(out_dir: Path, parts: dict[str, Any], settings: dict[str, Any]) -> Path:
    path = out_dir / MANIFEST_FILE
    previous = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    manifest = {
        "fetched_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "files": {**previous.get("files", {}), **parts},
        "sources": {k: v.get("page") for k, v in settings["sources"].items()},
    }
    path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return path


def read_manifest(out_dir: Path) -> dict[str, Any]:
    path = out_dir / MANIFEST_FILE
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
