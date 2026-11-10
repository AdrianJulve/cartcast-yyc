# Development

## Setup

```bash
git clone https://github.com/AdrianJulve/cartcast-yyc.git
cd cartcast-yyc
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

The committed snapshot in `data/snapshot/` is enough to build the dashboard:

```bash
python -m cartcast build
python -m cartcast serve           # http://localhost:8000
```

To download fresh data first, run `python -m cartcast fetch`. The CPI table is a
large download, so the first fetch takes a few minutes. Commit `data/snapshot/`
afterwards so GitHub Actions builds from the same data.

Add `--sample` to `build` or `validate` to use the synthetic sample data, which
works offline. If `make` is installed, `make help` lists shortcuts such as
`make demo` and `make check`.

## Commands

| Command | Description |
|---|---|
| `cartcast fetch [--only prices cpi mbm stores]` | Download the sources into `data/raw/` and update `data/snapshot/` |
| `cartcast snapshot` | Rebuild `data/snapshot/` from files already in `data/raw/` |
| `cartcast validate [--sample] [--strict]` | Check basket and substitution product names against the data |
| `cartcast build [--sample] [--out DIR]` | Build from the snapshot (or sample data) into `data/processed/` and `site/index.html` |
| `cartcast serve [--port 8000]` | Serve the built site locally |

## Configuration

- Basket: `config/basket.yaml`. Product names must match StatCan. Run `cartcast validate` to check them.
- Substitutions: `config/swaps.yaml`. The `ratio` field converts between package sizes. For example, 1 kg of fresh salmon is about 4.7 cans of 213 g.
- Geography: `geography.prices` in `config/settings.yaml` accepts any province.
- Store rules: `stores` in `config/settings.yaml` (licence types, statuses and name keywords).
- Outlook range: `dashboard.outlook_annual_low` and `dashboard.outlook_annual_high`.

## Deployment

1. In the repository settings, open Pages and set the source to GitHub Actions.
2. Run the "Refresh data and deploy dashboard" workflow from the Actions tab, or push to `main`.

The workflow runs every Monday to pick up new data and on every push to `main`. A
push that changes the store rules or the data code downloads fresh data before
deploying. The dashboard footer shows when the data was last downloaded.

## Project structure

```
cartcast-yyc/
├── config/                 basket.yaml, swaps.yaml, settings.yaml
├── src/cartcast/           pipeline package and CLI
│   ├── sources.py          downloads (StatCan zip files, Socrata API)
│   ├── prices.py, cpi.py   StatCan table loaders
│   ├── mbm.py              Market Basket Measure food threshold
│   ├── snapshot.py         compact real-data extracts
│   ├── stores.py           business licence classification
│   ├── basket.py           basket cost, substitutions, aisle shares, outlook
│   ├── build.py, cli.py    site rendering and commands
│   └── templates/dashboard.html
├── data/
│   ├── snapshot/           real data used by the dashboard (committed)
│   ├── sample/             synthetic dataset for tests (committed)
│   ├── raw/                downloaded files (ignored by git)
│   └── processed/          build output (ignored by git)
├── scripts/make_sample_data.py
├── tests/
├── design/                 dashboard mockup (PNG and HTML)
├── docs/
└── .github/                workflows, issue and pull request templates
```
