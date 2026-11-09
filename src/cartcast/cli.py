"""Command-line interface: ``cartcast fetch | validate | build | serve``."""

from __future__ import annotations

import argparse
import contextlib
import functools
import http.server
import socketserver
import sys
from pathlib import Path

from .basket import validate_products
from .build import build_payload, render_site, resolve_inputs, write_processed
from .config import RAW_DIR, SITE_DIR, load_config
from .prices import load_prices
from .sources import download_calgary_stores, download_statcan_table


def cmd_fetch(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    src = cfg.settings["sources"]
    targets = args.only or ["prices", "cpi", "stores"]
    if "prices" in targets:
        print("↓ StatCan 18-10-0245-01 (average retail prices)…")
        path = download_statcan_table(src["prices"]["url"], src["prices"]["table_id"], RAW_DIR)
        print("  saved", path)
    if "cpi" in targets:
        print("↓ StatCan 18-10-0004-01 (CPI — large file, this can take a minute)…")
        path = download_statcan_table(src["cpi"]["url"], src["cpi"]["table_id"], RAW_DIR)
        print("  saved", path)
    if "stores" in targets:
        print("↓ City of Calgary business licences (grocery retailers)…")
        print("  saved", download_calgary_stores(cfg.settings, RAW_DIR / "stores.json"))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    inputs = resolve_inputs(args.sample)
    prices = load_prices(inputs.prices, cfg.settings["geography"]["prices"])
    available = sorted(prices["product"].unique())
    names = [i.product for i in cfg.items]
    names += [s.source for s in cfg.swaps] + [s.target for s in cfg.swaps]
    issues = validate_products(sorted(set(names)), available)
    for issue in issues:
        print("✗", issue)
    if not issues:
        print(f"✓ All {len(set(names))} basket and swap products found in {inputs.prices.name}")
    return 1 if issues else 0


def cmd_build(args: argparse.Namespace) -> int:
    cfg = load_config(args.config)
    inputs = resolve_inputs(args.sample)
    for p in (inputs.prices, inputs.cpi, inputs.stores):
        if not p.exists():
            hint = "run `cartcast fetch` first" if not args.sample else "run `make sample`"
            print(f"Missing input {p} — {hint}.", file=sys.stderr)
            return 2
    payload = build_payload(cfg, inputs)
    write_processed(payload)
    out = render_site(payload, Path(args.out))
    s = payload["summary"]
    label = "SAMPLE data" if inputs.is_sample else "live data"
    print(f"✓ Built {out} from {label}, latest month {payload['meta']['latest_month']}")
    print(
        f"  Weekly basket: ${s['weekly_cost']:.2f} · {len(payload['stores'])} stores · "
        f"{len(s['swaps'])} swaps"
    )
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

    p = sub.add_parser("fetch", help="download the latest open data")
    p.add_argument("--only", nargs="+", choices=["prices", "cpi", "stores"])
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("validate", help="check basket/swap product names against the data")
    p.add_argument("--sample", action="store_true", help="validate against sample data")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("build", help="build data/processed and the static dashboard")
    p.add_argument("--sample", action="store_true", help="use bundled sample data (offline)")
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
