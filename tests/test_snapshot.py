import json

import pandas as pd

from cartcast import snapshot as snap
from cartcast.build import build_payload, resolve_inputs
from cartcast.config import SAMPLE_DIR


def _make_snapshot(tmp_path, cfg):
    """Write a snapshot from the sample files, as `cartcast fetch` does from raw files."""
    s = cfg.settings
    geo = s["geography"]
    parts = {
        snap.PRICES_FILE: snap.write_prices(
            SAMPLE_DIR / "prices_sample.csv", tmp_path / snap.PRICES_FILE, geo["prices"], 40
        ),
        snap.CPI_FILE: snap.write_cpi(
            SAMPLE_DIR / "cpi_sample.csv",
            tmp_path / snap.CPI_FILE,
            geo["cpi"],
            geo["cpi_products"],
            since="2020-01",
        ),
        snap.MBM_FILE: snap.write_mbm(
            SAMPLE_DIR / "mbm_sample.csv", tmp_path / snap.MBM_FILE, "Calgary"
        ),
        snap.STORES_FILE: snap.write_stores(
            SAMPLE_DIR / "stores_sample.json", tmp_path / snap.STORES_FILE, s
        ),
    }
    snap.write_manifest(tmp_path, parts, s)
    return parts


def test_snapshot_files_are_filtered(tmp_path, cfg):
    parts = _make_snapshot(tmp_path, cfg)

    prices = pd.read_csv(tmp_path / snap.PRICES_FILE)
    assert set(prices["GEO"]) == {"Alberta"}
    assert prices["REF_DATE"].nunique() == 40
    assert parts[snap.PRICES_FILE]["latest_month"] == "2026-09"

    cpi = pd.read_csv(tmp_path / snap.CPI_FILE)
    assert set(cpi["GEO"]) == {"Alberta", "Calgary, Alberta"}
    assert "Shelter" not in set(cpi["Products and product groups"])
    assert cpi["REF_DATE"].min() >= "2020-01"

    mbm = pd.read_csv(tmp_path / snap.MBM_FILE)
    assert set(mbm["GEO"]) == {"Calgary, Alberta"}

    stores = json.loads((tmp_path / snap.STORES_FILE).read_text())
    assert stores and all("AUTO" not in r["tradename"] for r in stores)
    assert parts[snap.STORES_FILE]["records"] < parts[snap.STORES_FILE]["downloaded"]

    manifest = snap.read_manifest(tmp_path)
    assert set(manifest["files"]) == set(parts)
    assert manifest["fetched_at"].endswith("Z")


def test_build_from_snapshot(tmp_path, cfg):
    _make_snapshot(tmp_path, cfg)
    inputs = resolve_inputs(sample=False, snapshot_dir=tmp_path)
    assert inputs.is_sample is False and inputs.fetched_at
    payload = build_payload(cfg, inputs)
    assert payload["meta"]["is_sample"] is False
    assert payload["cpi"]["headline_geo"] == "Calgary, Alberta"
    assert payload["mbm"]["geo"] == "Calgary, Alberta"


def test_cpi_falls_back_to_alberta(tmp_path, cfg):
    _make_snapshot(tmp_path, cfg)
    cpi = pd.read_csv(tmp_path / snap.CPI_FILE)
    cpi[cpi["GEO"] != "Calgary, Alberta"].to_csv(tmp_path / snap.CPI_FILE, index=False)
    payload = build_payload(cfg, resolve_inputs(sample=False, snapshot_dir=tmp_path))
    assert payload["cpi"]["headline_geo"] == "Alberta"
    assert payload["cpi"]["food_yoy"] is not None


def test_build_without_mbm_file(tmp_path, cfg):
    _make_snapshot(tmp_path, cfg)
    (tmp_path / snap.MBM_FILE).unlink()
    payload = build_payload(cfg, resolve_inputs(sample=False, snapshot_dir=tmp_path))
    assert payload["mbm"] is None
