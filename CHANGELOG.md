# Changelog

Notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Calgary food benchmark from the Market Basket Measure (StatCan Table 11-10-0066-01), adjusted for household size.
- Real-data snapshot in `data/snapshot/`, written by `cartcast fetch` and committed so the dashboard builds from real data by default.
- `cartcast snapshot` command.

### Changed
- The grocery inflation figure now uses the Calgary CMA CPI, with Alberta as a fallback.
- `cartcast build` reads the snapshot by default. Use `--sample` for the synthetic data.
- The monthly workflow commits the refreshed snapshot before deploying.
- Rewrote documentation, interface text, CLI output and code comments in plain language. Removed emojis and decorative punctuation.

## [0.1.0] - 2026-11-09

### Added
- Data pipeline for StatCan tables 18-10-0245-01 (prices) and 18-10-0004-01 (CPI), and City of Calgary business licences (`vdjc-pybd`).
- `cartcast` command-line tool with `fetch`, `validate`, `build` and `serve`.
- Interactive dashboard with an editable basket, household sizes, substitutions, price changes, aisle shares, a store map, an outlook range and shareable links.
- Offline sample dataset and the script that generates it.
- Tests, ruff linting, a CI workflow, and a monthly workflow that refreshes the data and deploys to GitHub Pages.
- Design mockup, documentation and presentation plan.
