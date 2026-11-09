# Changelog

Notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- Rewrote documentation, interface text, CLI output and code comments in plain language. Removed emojis and decorative punctuation.

## [0.1.0] - 2026-11-09

### Added
- Data pipeline for StatCan tables 18-10-0245-01 (prices) and 18-10-0004-01 (CPI), and City of Calgary business licences (`vdjc-pybd`).
- `cartcast` command-line tool with `fetch`, `validate`, `build` and `serve`.
- Interactive dashboard with an editable basket, household sizes, substitutions, price changes, aisle shares, a store map, an outlook range and shareable links.
- Offline sample dataset and the script that generates it.
- Tests, ruff linting, a CI workflow, and a monthly workflow that refreshes the data and deploys to GitHub Pages.
- Design mockup, documentation and presentation plan.
