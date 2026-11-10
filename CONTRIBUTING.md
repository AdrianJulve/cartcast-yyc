# Contributing

Contributions are welcome. The process below keeps changes reviewable and keeps
`main` in a working state.

## Setup

```bash
git clone https://github.com/AdrianJulve/cartcast-yyc.git
cd cartcast-yyc
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -e ".[dev]"
python -m cartcast build          # uses the committed real-data snapshot
python -m cartcast serve           # http://localhost:8000
```

## Workflow

1. Open or pick an issue using one of the templates.
2. Create a branch from `main` named `type/short-description`, for example
   `feat/basket-presets`, `fix/map-labels` or `docs/store-rules`.
3. Write commit messages in the [Conventional Commits](https://www.conventionalcommits.org/)
   format, for example `feat: add family of 6 preset` or `fix: handle suppressed prices`.
4. Run `make check`, or `python -m pytest` and `ruff check .` if `make` is not installed.
   CI runs the same checks.
5. Open a pull request using the template. The maintainer reviews it before it is merged.
6. Squash and merge, then delete the branch.

## Where to make changes

| Change | File |
|---|---|
| Basket items, quantities, household sizes | `config/basket.yaml` |
| Substitutions | `config/swaps.yaml` |
| Geography, sources, store keywords, outlook range | `config/settings.yaml` |
| Data loading and calculations | `src/cartcast/*.py`, with tests in `tests/` |
| Dashboard layout and behaviour | `src/cartcast/templates/dashboard.html` |
| Documentation | `README.md`, `docs/` |

After editing `basket.yaml` or `swaps.yaml`, run `python -m cartcast validate`
(or add `--sample` to check against the sample data). It reports any product name
that does not match StatCan and suggests the closest match.

## Code style

- Python 3.10 or later, formatted and linted with ruff (`make format`).
- New calculations need a test with a small fixture that can be checked by hand.
- Sample data must not be presented as real. Sample builds are marked in the dashboard footer.

## Data

- Do not commit files in `data/raw/`. They can be downloaded again and are ignored by git.
- Do commit `data/snapshot/` after running `cartcast fetch`. It is the real data the dashboard is built from.
- Cite any new dataset in the dashboard footer and in `docs/data-sources.md`.
- Use CPI figures for any statement about inflation. Average prices are not an
  inflation measure (see `docs/methodology.md`).
