"""Download raw data from Statistics Canada and City of Calgary Open Data.

Only the standard library is used for HTTP so the pipeline runs anywhere.
"""

from __future__ import annotations

import io
import json
import time
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

USER_AGENT = "cartcast-yyc/0.1 (+https://github.com/AdrianJulve/cartcast-yyc)"


def _get(url: str, *, timeout: int = 120, retries: int = 3) -> bytes:
    last_err: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read()
        except Exception as err:  # noqa: BLE001 - retry any network error
            last_err = err
            time.sleep(2 * attempt)
    raise RuntimeError(f"Failed to download {url}: {last_err}") from last_err


def download_statcan_table(url: str, table_id: str, dest_dir: Path) -> Path:
    """Download a StatCan full-table CSV zip and extract the data CSV.

    StatCan publishes every table as ``<id>-eng.zip`` containing ``<id>.csv``
    (the data) and ``<id>_MetaData.csv``. Returns the path of the data CSV.
    """
    dest_dir.mkdir(parents=True, exist_ok=True)
    payload = _get(url, timeout=600)
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        wanted = f"{table_id}.csv"
        names = zf.namelist()
        if wanted not in names:
            raise RuntimeError(f"{wanted} not found in archive (contains: {names})")
        out = dest_dir / wanted
        with zf.open(wanted) as src, out.open("wb") as dst:
            while chunk := src.read(1 << 20):
                dst.write(chunk)
        meta = f"{table_id}_MetaData.csv"
        if meta in names:
            (dest_dir / meta).write_bytes(zf.read(meta))
    return out


def build_store_query(settings: dict[str, Any]) -> str:
    """SoQL ``$where`` clause for grocery-like retail licences."""
    cfg = settings["stores"]

    def any_of(field: str, values: list[str]) -> str:
        return "(" + " OR ".join(f"{field} like '%{v}%'" for v in values) + ")"

    status = ", ".join(f"'{s}'" for s in cfg["status_any"])
    words = cfg["supermarket_keywords"] + cfg["specialty_keywords"]
    general = (
        any_of("licencetypes", cfg["licence_types_any"])
        + " AND "
        + any_of("upper(tradename)", words)
    )
    super_types = cfg.get("supermarket_licence_types_any", cfg["licence_types_any"])
    supers = (
        any_of("licencetypes", super_types)
        + " AND "
        + any_of("upper(tradename)", cfg["supermarket_keywords"])
    )
    return f"jobstatusdesc in ({status}) AND (({general}) OR ({supers}))"


def download_calgary_stores(settings: dict[str, Any], dest: Path, page_size: int = 5000) -> Path:
    """Page through the Socrata API and save matching licences as JSON."""
    base = settings["sources"]["stores"]["url"]
    where = build_store_query(settings)
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        params = urllib.parse.urlencode(
            {"$where": where, "$limit": page_size, "$offset": offset, "$order": "getbusid"}
        )
        batch = json.loads(_get(f"{base}?{params}"))
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return dest
