"""Assemble the dashboard payload and render the static site."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from importlib import resources
from pathlib import Path
from typing import Any

import pandas as pd

from . import __version__
from .basket import aisle_shares, basket_cost, outlook_band, swap_savings, validate_products
from .config import PROCESSED_DIR, RAW_DIR, SAMPLE_DIR, SITE_DIR, Config
from .cpi import latest_yoy, load_cpi
from .prices import load_prices, to_wide, yoy_change
from .stores import load_stores

DATA_PLACEHOLDER = "/*__CARTCAST_DATA__*/null"


@dataclass(frozen=True)
class Inputs:
    prices: Path
    cpi: Path
    stores: Path
    is_sample: bool


def resolve_inputs(sample: bool) -> Inputs:
    if sample:
        return Inputs(
            SAMPLE_DIR / "prices_sample.csv",
            SAMPLE_DIR / "cpi_sample.csv",
            SAMPLE_DIR / "stores_sample.json",
            True,
        )
    return Inputs(
        RAW_DIR / "18100245.csv", RAW_DIR / "18100004.csv", RAW_DIR / "stores.json", False
    )


def _clean(value: Any) -> Any:
    """Make values JSON-safe (NaN -> None, numpy -> python, rounding)."""
    if isinstance(value, float):
        return None if math.isnan(value) else round(value, 4)
    if isinstance(value, dict):
        return {k: _clean(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_clean(v) for v in value]
    if hasattr(value, "item"):
        return _clean(value.item())
    return value


def build_payload(cfg: Config, inputs: Inputs) -> dict[str, Any]:
    s = cfg.settings
    dash = s["dashboard"]

    prices = load_prices(inputs.prices, geo=s["geography"]["prices"])
    wide = to_wide(prices).ffill()
    latest = wide.index.max()

    issues = validate_products([i.product for i in cfg.items], list(wide.columns))
    if issues:
        raise ValueError("Basket config has unknown products:\n  " + "\n  ".join(map(str, issues)))

    # Keep enough history for the chart plus 12 months for year-over-year change.
    n_months = int(dash["history_months"]) + 12
    window = wide.iloc[-n_months:]
    months = [m.strftime("%Y-%m") for m in window.index]

    products = {
        name: {
            "aisle": cfg.aisle_for(name),
            "series": [None if pd.isna(v) else round(float(v), 2) for v in window[name]],
        }
        for name in window.columns
        if pd.notna(window[name].iloc[-1])
    }

    scale = float(cfg.households[cfg.default_household]["scale"])
    cost = basket_cost(wide, cfg.items, scale)
    band = outlook_band(
        float(cost.iloc[-1]),
        int(dash["outlook_months"]),
        float(dash["outlook_annual_low"]),
        float(dash["outlook_annual_high"]),
    )

    cpi = load_cpi(inputs.cpi, s["geography"]["cpi"], s["geography"]["cpi_products"])
    cpi_window = cpi[cpi["month"] > latest - pd.DateOffset(months=n_months)]
    cpi_series = {
        f"{geo} | {prod}": {
            "months": [m.strftime("%Y-%m") for m in grp["month"]],
            "index": grp["index"].round(1).tolist(),
            "yoy": grp["yoy"].round(2).tolist(),
        }
        for (geo, prod), grp in cpi_window.groupby(["geo", "product"])
    }
    headline_geo = s["geography"]["cpi_headline_geo"]
    food = latest_yoy(cpi, headline_geo, "Food purchased from stores")
    allitems = latest_yoy(cpi, headline_geo, "All-items")

    stores = load_stores(inputs.stores, s)

    swaps_df = swap_savings(wide, cfg.items, cfg.swaps, latest, scale)
    shares = aisle_shares(wide, cfg.items, latest)
    movers = sorted(
        ({"product": i.product, "yoy": yoy_change(wide, i.product, latest)} for i in cfg.items),
        key=lambda r: -(r["yoy"] if r["yoy"] is not None else -1e9),
    )

    sources = [
        {"key": k, "name": v["name"], "page": v.get("page"), "licence": v.get("licence")}
        for k, v in s["sources"].items()
    ]

    payload = {
        "meta": {
            "title": dash["title"],
            "tagline": dash["tagline"],
            "version": __version__,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "latest_month": latest.strftime("%Y-%m"),
            "price_geo": s["geography"]["prices"],
            "is_sample": inputs.is_sample,
            "sources": sources,
        },
        "months": months,
        "history_months": int(dash["history_months"]),
        "products": products,
        "households": cfg.households,
        "default_household": cfg.default_household,
        "basket": [{"product": i.product, "qty": i.qty, "aisle": i.aisle} for i in cfg.items],
        "swaps": [
            {"from": w.source, "to": w.target, "ratio": w.ratio, "group": w.group}
            for w in cfg.swaps
        ],
        "outlook": {
            "months": int(dash["outlook_months"]),
            "annual_low": float(dash["outlook_annual_low"]),
            "annual_high": float(dash["outlook_annual_high"]),
        },
        "cpi": {
            "series": cpi_series,
            "headline_geo": headline_geo,
            "food_yoy": food[1] if food else None,
            "food_month": food[0].strftime("%Y-%m") if food else None,
            "all_items_yoy": allitems[1] if allitems else None,
        },
        "stores": stores.to_dict(orient="records"),
        "summary": {
            "weekly_cost": float(cost.iloc[-1]),
            "weekly_cost_prev": float(cost.iloc[-2]) if len(cost) > 1 else None,
            "outlook_band": band,
            "aisle_shares": shares.round(4).to_dict(),
            "movers": movers,
            "swaps": swaps_df.to_dict(orient="records"),
        },
    }
    return _clean(payload)


def render_site(payload: dict[str, Any], out_dir: Path = SITE_DIR) -> Path:
    template = resources.files("cartcast").joinpath("templates/dashboard.html").read_text("utf-8")
    if DATA_PLACEHOLDER not in template:
        raise RuntimeError("Dashboard template is missing the data placeholder")
    # Escape "</" so data can never close the <script> tag early.
    data = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = template.replace(DATA_PLACEHOLDER, data)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / "index.html"
    out.write_text(html, encoding="utf-8")
    return out


def write_processed(payload: dict[str, Any], out_dir: Path = PROCESSED_DIR) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "dashboard.json").write_text(json.dumps(payload, indent=1), encoding="utf-8")
    (out_dir / "summary.json").write_text(
        json.dumps({"meta": payload["meta"], **payload["summary"]}, indent=2), encoding="utf-8"
    )
