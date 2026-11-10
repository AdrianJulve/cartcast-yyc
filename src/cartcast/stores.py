"""Turn City of Calgary business-licence records into a grocery-store list."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pandas as pd


def _coords(rec: dict[str, Any]) -> tuple[float | None, float | None]:
    point = rec.get("point")
    if isinstance(point, dict) and "coordinates" in point:
        lon, lat = point["coordinates"][:2]
        return float(lat), float(lon)
    lat, lon = rec.get("latitude"), rec.get("longitude")
    return (float(lat), float(lon)) if lat and lon else (None, None)


def _has_word(name: str, words: list[str]) -> bool:
    """True if any keyword appears as a whole word (a trailing S is allowed)."""
    return any(re.search(r"\b" + re.escape(w) + r"S?\b", name) for w in words)


def classify(name: str, settings: dict[str, Any]) -> str | None:
    """'supermarket', 'specialty', or None if the trade name isn't a food retailer."""
    cfg = settings["stores"]
    upper = name.upper()
    if _has_word(upper, cfg.get("exclude_keywords", [])):
        return None
    if _has_word(upper, cfg["supermarket_keywords"]):
        return "supermarket"
    if _has_word(upper, cfg["specialty_keywords"]):
        return "specialty"
    return None


def load_stores(json_path: Path | str, settings: dict[str, Any]) -> pd.DataFrame:
    """Columns: name, address, community, lat, lon, kind. Deduplicated by name+address."""
    records = json.loads(Path(json_path).read_text(encoding="utf-8"))
    rows = []
    for rec in records:
        name = (rec.get("tradename") or "").strip()
        kind = classify(name, settings)
        lat, lon = _coords(rec)
        if not kind or lat is None:
            continue
        rows.append(
            {
                "name": name.title(),
                "address": (rec.get("address") or "").title(),
                "community": (rec.get("comdistnm") or "Unknown").title(),
                "lat": lat,
                "lon": lon,
                "kind": kind,
            }
        )
    df = pd.DataFrame(rows, columns=["name", "address", "community", "lat", "lon", "kind"])
    return df.drop_duplicates(subset=["name", "address"]).reset_index(drop=True)
