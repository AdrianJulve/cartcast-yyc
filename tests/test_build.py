import json

from cartcast.build import DATA_PLACEHOLDER, build_payload, render_site, resolve_inputs
from cartcast.cli import main


def test_sample_payload_shape(cfg):
    payload = build_payload(cfg, resolve_inputs(sample=True))
    assert payload["meta"]["is_sample"] is True
    assert payload["meta"]["latest_month"] == payload["months"][-1]
    assert len(payload["months"]) == payload["history_months"] + 12
    for item in payload["basket"]:
        series = payload["products"][item["product"]]["series"]
        assert len(series) == len(payload["months"])
    s = payload["summary"]
    assert s["weekly_cost"] > 0
    assert abs(sum(s["aisle_shares"].values()) - 1) < 1e-3
    assert payload["stores"], "sample stores should load"
    assert payload["cpi"]["food_yoy"] is not None
    json.dumps(payload)  # must be serialisable (no NaN / numpy types)


def test_render_site_injects_and_escapes(tmp_path, cfg):
    payload = build_payload(cfg, resolve_inputs(sample=True))
    payload["meta"]["tagline"] = "</script><script>alert(1)</script>"
    out = render_site(payload, tmp_path)
    html = out.read_text(encoding="utf-8")
    assert DATA_PLACEHOLDER not in html
    assert "</script><script>alert(1)" not in html
    assert '"is_sample":true' in html


def test_cli_build_and_validate_sample(tmp_path):
    assert main(["validate", "--sample"]) == 0
    assert main(["build", "--sample", "--out", str(tmp_path)]) == 0
    assert (tmp_path / "index.html").exists()
