# Changelog

Notable changes to this project are recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- Reset view button on both maps, below the zoom buttons.
- Address search on the Stores page. Suggestions come from the City of Calgary parcel address list as you type, together with matching stores. Choosing an address places a pin and shows nearby stores and the nearest supermarket. Only real Calgary addresses can be pinned.
- Calgary food benchmark from the Market Basket Measure (StatCan Table 11-10-0066-01), adjusted for household size.
- Real-data snapshot in `data/snapshot/`, written by `cartcast fetch` and committed so the dashboard builds from real data by default.
- `cartcast snapshot` command.

- Base map for the store map (OpenStreetMap standard tiles, no API key needed) with zoom and drag.
- Cross-filtering across every visual by month, aisle, product, community and store type, with a filter bar.
- Basket, Stores and Data pages in the sidebar.

- Store details card, food access check for any spot on the map, and community summaries, with distance rings and a line to the nearest supermarket.
- Clear basket and Restore default basket buttons, each with Undo, and empty-basket states across the dashboard.
- Store licence type, status and first-issued year in the store data.

- Light and dark mode toggle in the header. The choice is saved in the browser, and the first visit follows the system setting. Both themes meet WCAG AA contrast for text.
- Product picker on the Basket page with search, aisle tabs and multi-select. Tick any number of products, then add them together with one button, with Undo.

### Fixed
- On phones and narrow windows the Stores map collapsed to nothing, so it was missing once a store was selected. It now keeps a fixed share of the screen, and choosing a store from the list or the search box scrolls the map back into view.
- On phones the Basket page ran past the edge of the screen. The aisle tabs and buttons now wrap, and the table shows the item, quantity, weekly cost and remove button.
- Directions opened whichever business Google found nearest a store's coordinates, which could be a neighbouring shop. They now use the store's name and street address.
- Shops in Market Mall such as the Apple Store, Uniqlo and Specsavers were listed as grocers because the mall's name contains "market". Place names are now ignored when matching, specialty stores must hold a food licence, and pharmacies, coffee shops, restaurants, newsstands and charities are left out.
- Buttons in the store details card could run past the edge of the card when a name was long. The directions button now always reads "Directions", and long labels are shortened to fit.
- Selecting a store on the overview stretched the bottom row and left the Substitutions and Basket cost by aisle cards mostly empty. On wide screens the store details now sit beside the map without changing the row height. On narrower screens the details are capped in height, and the other two cards spread their rows to fill the space.
- Map zoom jumped several levels at once with trackpads and fast wheels, and zooming during a drag, or with the right mouse button held, moved the map to an unrelated place. Wheel zoom now moves one level at a time, only the left button pans, and a drag continues smoothly after a zoom.
- The maps now stop at the whole-city view when zooming out and at street level when zooming in, and the view cannot be dragged away from Calgary.
- The line chart and price change chart could be drawn at the wrong size after returning to the overview or when other content changed height. Each chart now redraws whenever its own box changes size.
- Dropdown options were unreadable in dark mode on some systems.
- Supermarkets with a fuel licence on the same record were left out, including the Seton and Signal Hill Superstores and Silverado Sobeys.
- Costco was left out because it holds a wholesaler licence rather than a retail one.
- Independent supermarkets with only a food service licence were left out.
- Staples, flooring and pawn shops named "Superstore", a carpet store and in-store sushi counters were shown as supermarkets.
- Store dots were too large at the city view. They are now smaller when zoomed out and grow as you zoom in.
- Distance ring labels, the community outline and marker outlines on the map drew without their colours.
- Most supermarkets were missing from the map. The store query only accepted the "Licensed" and "Pending Renewal" statuses, but about two-thirds of active licences are "Renewal Licensed". All active statuses are now included.
- Walmart stores were missing because the licence data spells the name "WAL-MART".
- Chain gas bars, liquor stores, cannabis stores, car washes and home health stores are now excluded by licence type and name.
- Butchers and bakeries that hold only a no-seating food licence are now included.

### Changed
- On phones and tablets, hints that mention the keyboard or mouse now give the touch equivalent, for example tapping the close button in place of pressing Esc.
- The community summary is easier to find and to tell apart from a store's details. With a community filter on, a store or pin card has a button that opens the summary, the summary card has a labelled Clear filter button in place of the close icon, and the Esc hints say that Esc closes open details first and clears filters second.
- A pinned address or spot now has the same community filter button as a store, beside Directions.
- Rewrote the method notes on the Data page, with a formula for each figure, and removed the build notes panel. Sources now span the full width.
- The Basket button in the header now toggles. On the Basket page it is highlighted, and selecting it again returns to the previous page.
- The dashboard now uses the full width and height of the screen. The 1680 px width limit is gone, and on the overview the charts and map grow to fill tall screens.
- Shortened the README. Commands, configuration, deployment and the project layout moved to `docs/development.md`.
- A push that changes the store rules or data code now downloads fresh data before deploying.
- Store keywords now match whole words, and more non-food businesses are excluded (florists, pet stores, cannabis shops, music schools and others).
- Selecting a store again, selecting empty map, the filter chip or Esc now clears the community selection.
- The README image is a screenshot of the live dashboard in light mode.
- The sparkline in the basket card sits beside the label, and moves below the text on narrow screens so it no longer covers it.
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
- Design mockup and documentation.
