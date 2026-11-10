"""Command-line interface for CartCast YYC (fetch, snapshot, validate, build, serve)."""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import socketserver
import sys
from pathlib import Path

from . import snapshot as snap
from .basket import validate_products
from .build import build_payload, render_site, resolve_inputs, write_processed
from .config import RAW_DIR, SITE_DIR, SNAPSHOT_DIR, Config, load_config
from .prices import load_prices
from .sources import download_calgary_stores, download_statcan_table

TARGETS = ["prices", "cpi", "mbm", "stores"]
RAW_FILES = {
    "prices": RAW_DIR / "18100245.csv",
    "cpi": RAW_DIR / "18100004.csv",
    "mbm": RAW_DIR / "11100066.csv",
    "stores": RAW_DIR / "stores.json",
}


def write_snapshot(cfg: Config, targets: list[str], out_dir: Path = SNAPSHOT_DIR) -> None:
    """Copy the rows the dashboard needs from data/raw/ into data/snapshot/."""
    s = cfg.settings
    geo = s["geography"]
    out_dir.mkdir(parents=True, exist_ok=True)
    parts = {}
    if "prices" in targets:
        parts[snap.PRICES_FILE] = snap.write_prices(
            RAW_FILES["prices"],
            out_dir / snap.PRICES_FILE,
            geo["prices"],
            int(s.get("snapshot", {}).get("price_months", 60)),
        )
    if "cpi" in targets:
        parts[snap.CPI_FILE] = snap.write_cpi(
            RAW_FILES["cpi"], out_dir / snap.CPI_FILE, geo["cpi"], geo["cpi_products"]
        )
    if "mbm" in targets:
        parts[snap.MBM_FILE] = snap.write_mbm(
            RAW_FILES["mbm"], out_dir / snap.MBM_FILE, geo.get("mbm_geo_contains", "Calgary")
        )
    if "stores" in targets:
        parts[snap.STORES_FILE] = snap.write_stores(
            RAW_FILES["stores"], out_dir / snap.STORES_FILE, s
        )
    snap.write_manifest(out_dir, parts, s)
    for name, info in parts.items():
        print(f"  Snapshot {name}: {info}")


def cmd_fetch(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    src = cfg.settings["sources"]
    targets = args.only or TARGETS
    if "prices" in targets:
        print("Downloading StatCan 18-10-0245-01 (average retail prices)...")
        download_statcan_table(src["prices"]["url"], src["prices"]["table_id"], RAW_DIR)
    if "cpi" in targets:
        print(
            "Downloading StatCan 18-10-0004-01 (CPI, a large file; this can take a few minutes)..."
        )
        download_statcan_table(src["cpi"]["url"], src["cpi"]["table_id"], RAW_DIR)
    if "mbm" in targets:
        print("Downloading StatCan 11-10-0066-01 (Market Basket Measure)...")
        download_statcan_table(src["mbm"]["url"], src["mbm"]["table_id"], RAW_DIR)
    if "stores" in targets:
        print("Downloading City of Calgary business licences (grocery retailers)...")
        download_calgary_stores(cfg.settings, RAW_FILES["stores"])
    print(f"Writing the snapshot to {SNAPSHOT_DIR} ...")
    write_snapshot(cfg, targets)
    print("Done. Run `cartcast build` next, then commit data/snapshot/.")
    return 0


def cmd_snapshot(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    targets = [t for t in TARGETS if RAW_FILES[t].exists()]
    if not targets:
        print("No raw files in data/raw/. Run `cartcast fetch` first.", file=sys.stderr)
        return 2
    write_snapshot(cfg, targets)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    inputs = resolve_inputs(args.sample)
    if not inputs.prices.exists():
        print(f"Missing {inputs.prices}. Run `cartcast fetch` first.", file=sys.stderr)
        return 2
    prices = load_prices(inputs.prices, cfg.settings["geography"]["prices"])
    available = sorted(prices["product"].unique())
    names = [i.product for i in cfg.items]
    names += [s.source for s in cfg.swaps] + [s.target for s in cfg.swaps]
    issues = validate_products(sorted(set(names)), available)
    for issue in issues:
        print("ERROR:", issue)
    if not issues:
        print(f"OK: all {len(set(names))} basket and swap products found in {inputs.prices.name}")
    return 1 if issues else 0


def cmd_build(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    inputs = resolve_inputs(args.sample)
    for p in inputs.required:
        if not p.exists():
            hint = "Run `make sample`." if args.sample else "Run `cartcast fetch` first."
            print(f"Missing input file: {p}. {hint}", file=sys.stderr)
            return 2
    payload = build_payload(cfg, inputs)
    write_processed(payload)
    out = render_site(payload, Path(args.out))
    s = payload["summary"]
    label = "sample data" if inputs.is_sample else "the real-data snapshot"
    print(f"Built {out} from {label}. Latest month: {payload['meta']['latest_month']}")
    print(
        f"Weekly basket: ${s['weekly_cost']:.2f}, {len(payload['stores'])} stores, "
        f"{len(s['swaps'])} substitutions"
    )
    cpi = payload["cpi"]
    print(f"Grocery inflation ({cpi['headline_geo']}): {cpi['food_yoy']}")
    if payload["mbm"]:
        m = payload["mbm"]
        print(f"MBM food threshold ({m['geo']}, {m['year']}): ${m['annual_family4']:,.0f} a year")
    return 0


def cmd_serve(args: argparse.Namespace) -> int:
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(args.dir))
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        print(f"Serving {args.dir} at http://localhost:{args.port}  (Ctrl+C to stop)")
        with contextlib.suppress(KeyboardInterrupt):
            httpd.serve_forever()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cartcast", description=__doc__)
    parser.add_argument("--config", default=None, help="config directory (default: ./config)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("fetch", help="download real data and update data/snapshot/")
    p.add_argument("--only", nargs="+", choices=TARGETS)
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("snapshot", help="rebuild data/snapshot/ from files already in data/raw/")
    p.set_defaults(func=cmd_snapshot)

    p = sub.add_parser("validate", help="check basket and substitution names against the data")
    p.add_argument("--sample", action="store_true", help="validate against sample data")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("build", help="build the dashboard from the snapshot (or sample data)")
    p.add_argument("--sample", action="store_true", help="use the synthetic sample data")
    p.add_argument("--out", default=str(SITE_DIR), help="output folder (default: ./site)")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("serve", help="preview the built dashboard locally")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--dir", type=Path, default=SITE_DIR)
    p.set_defaults(func=cmd_serve)

    args = parser.parse_args(argv)
    if args.config is None:
        from .config import CONFIG_DIR

        args.config = CONFIG_DIR
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
