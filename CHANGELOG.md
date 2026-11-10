# Changelog

Notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Calgary food benchmark from the Market Basket Measure (StatCan Table 11-10-0066-01), adjusted for household size.
- Real-data snapshot in `data/snapshot/`, written by `cartcast fetch` and committed so the dashboard builds from real data by default.
- `cartcast snapshot` command.

- Base map for the store map (OpenStreetMap standard tiles, no API key needed) with zoom and drag.
- Cross-filtering across every visual by month, aisle, product, community and store type, with a filter bar.
- Basket, Stores and Data pages in the sidebar.

### Changed
- Store keywords now match whole words, and more non-food businesses are excluded (florists, pet stores, cannabis shops, music schools and others).
- Selecting a store again, selecting empty map, the filter chip or Esc now clears the community selection.
- The README image is a screenshot of the live dashboard.
- The grocery inflation figure now uses the Calgary CMA CPI, with Alberta as a fallback.
- `cartcast build` reads the snapshot by default. Use `--sample` for the synthetic data.
- The refresh workflow runs weekly and on every push to `main`, commits the refreshed snapshot, and deploys the live site.
- Removed the sample data banner. Sample builds are only used for tests and are marked in the footer.
- Rewrote documentation, interface text, CLI output and code comments in plain language. Removed emojis and decorative punctuation.

## [0.1.0] - 2026-11-09

### Added
- Data pipeline for StatCan tables 18-10-0245-01 (prices) and 18-10-0004-01 (CPI), and City of Calgary business licences (`vdjc-pybd`).
- `cartcast` command-line tool with `fetch`, `validate`, `build` and `serve`.
- Interactive dashboard with an editable basket, household sizes, substitutions, price changes, aisle shares, a store map, an outlook range and shareable links.
- Offline sample dataset and the script that generates it.
- Tests, ruff linting, a CI workflow, and a monthly workflow that refreshes the data and deploys to GitHub Pages.
- Design mockup, documentation and presentation plan.
