# Contributing to CartCast YYC

Thanks for helping. This is a team course project, so the workflow below keeps
everyone's changes reviewable and keeps `main` always presentable.

## Set up

```bash
git clone https://github.com/AdrianJulve/cartcast-yyc.git
cd cartcast-yyc
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
make install            # or: pip install -e ".[dev]"
make build-sample serve # open http://localhost:8000
```

No `make` on Windows? Run the commands directly: `python -m cartcast build --sample`
then `python -m cartcast serve`.

## Workflow

1. **Pick or open an issue.** Use the templates (bug, feature, data issue).
2. **Branch from `main`.** Name branches `type/short-description`, e.g.
   `feat/basket-presets`, `fix/map-labels`, `docs/presentation-script`, `data/new-swaps`.
3. **Commit small and often.** Use [Conventional Commits](https://www.conventionalcommits.org/):
   `feat: add family-of-6 preset`, `fix: handle suppressed prices`, `docs: update demo script`.
4. **Run the checks.** `make check` runs lint, tests and a sample build, the same as CI.
5. **Open a pull request** using the template. At least one teammate reviews before merging.
6. **Squash-merge** into `main`. Delete the branch afterwards.

## What goes where

| Change | Edit |
|---|---|
| Basket items, quantities, household sizes | `config/basket.yaml` |
| Swap suggestions | `config/swaps.yaml` |
| Geography, sources, store keywords, outlook range | `config/settings.yaml` |
| Data loading or calculations | `src/cartcast/*.py` (+ tests in `tests/`) |
| Dashboard look and behaviour | `src/cartcast/templates/dashboard.html` |
| Presentation plan and talking points | `docs/presentation-plan.md` |

After editing `basket.yaml` or `swaps.yaml`, run `make validate` (live data) or
`python -m cartcast validate --sample`. It flags product names that don't match
StatCan exactly and suggests the closest names.

## Code style

- Python 3.10+, formatted and linted with `ruff` (`make format`).
- Every new calculation gets a test using a tiny hand-checkable fixture.
- Never present sample data as real. The sample banner must stay.

## Data rules

- Don't commit anything in `data/raw/`. It's re-downloadable and git-ignored.
- Cite sources in the dashboard footer and in `docs/data-sources.md`.
- Average prices are not an inflation measure. Use CPI figures for inflation claims
  (see `docs/methodology.md`).
