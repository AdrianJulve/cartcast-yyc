"""Basket costing, swaps, aisle shares and the price outlook."""

from __future__ import annotations

import difflib
from dataclasses import dataclass, replace

import pandas as pd

from .config import BasketItem, Swap
from .prices import suggest

# Names at least this similar are treated as the same product (for example a
# small wording change by StatCan). Anything less similar is left out.
AUTO_MATCH_CUTOFF = 0.88
MIN_BASKET_ITEMS = 5


@dataclass(frozen=True)
class ValidationIssue:
    product: str
    suggestions: list[str]
    resolved: str | None = None

    def __str__(self) -> str:
        if self.resolved:
            return f"'{self.product}' not found; using the closest StatCan name '{self.resolved}'"
        hint = f". Closest matches: {', '.join(self.suggestions)}" if self.suggestions else ""
        return f"Unknown product '{self.product}' will be left out{hint}"


def validate_products(names: list[str], available: list[str]) -> list[ValidationIssue]:
    """One issue per name that is not an exact match, with any automatic match."""
    known = set(available)
    issues = []
    for name in names:
        if name in known:
            continue
        close = difflib.get_close_matches(name, available, n=1, cutoff=AUTO_MATCH_CUTOFF)
        issues.append(ValidationIssue(name, suggest(name, available), close[0] if close else None))
    return issues


def resolve_config(
    items: list[BasketItem], swaps: list[Swap], available: list[str]
) -> tuple[list[BasketItem], list[Swap], list[ValidationIssue]]:
    """Map basket and swap names onto the products in the data.

    Close matches are substituted, unknown names are dropped, and every change is
    returned as an issue so it can be reported.
    """
    names = sorted(
        {i.product for i in items} | {s.source for s in swaps} | {s.target for s in swaps}
    )
    issues = validate_products(names, available)
    mapping = {n: n for n in names if n in set(available)}
    mapping.update({i.product: i.resolved for i in issues if i.resolved})

    resolved_items = [replace(i, product=mapping[i.product]) for i in items if i.product in mapping]
    resolved_swaps = [
        replace(s, source=mapping[s.source], target=mapping[s.target])
        for s in swaps
        if s.source in mapping and s.target in mapping
    ]
    if len(resolved_items) < MIN_BASKET_ITEMS:
        raise ValueError(
            f"Only {len(resolved_items)} basket products match the data:\n  "
            + "\n  ".join(map(str, issues))
        )
    return resolved_items, resolved_swaps, issues


def basket_cost(wide: pd.DataFrame, items: list[BasketItem], scale: float = 1.0) -> pd.Series:
    """Weekly basket cost per month.

    When an item's price is missing for a month, its previous price is used so
    that one suppressed value does not cause a jump in the series.
    """
    cols = [i.product for i in items if i.product in wide.columns]
    qty = pd.Series({i.product: i.qty * scale for i in items if i.product in wide.columns})
    filled = wide[cols].ffill()
    return (filled * qty).sum(axis=1, min_count=1).rename("basket_cost")


def aisle_shares(wide: pd.DataFrame, items: list[BasketItem], month: pd.Timestamp) -> pd.Series:
    """Share (0 to 1) of the basket's cost in each aisle for one month."""
    row = wide.ffill().loc[month]
    costs: dict[str, float] = {}
    for item in items:
        if item.product in row.index and pd.notna(row[item.product]):
            costs[item.aisle] = costs.get(item.aisle, 0.0) + item.qty * float(row[item.product])
    total = sum(costs.values())
    if total == 0:
        return pd.Series(dtype=float)
    return pd.Series(costs).div(total).sort_values(ascending=False)


def swap_savings(
    wide: pd.DataFrame,
    items: list[BasketItem],
    swaps: list[Swap],
    month: pd.Timestamp,
    scale: float = 1.0,
) -> pd.DataFrame:
    """Weekly savings for every applicable swap, largest first."""
    row = wide.ffill().loc[month]
    qty = {i.product: i.qty * scale for i in items}
    out = []
    for s in swaps:
        if s.source not in qty or s.source not in row.index or s.target not in row.index:
            continue
        p_from, p_to = row[s.source], row[s.target]
        if pd.isna(p_from) or pd.isna(p_to):
            continue
        q_from = qty[s.source]
        q_to = q_from * s.ratio
        saving = q_from * p_from - q_to * p_to
        if saving > 0:
            out.append(
                {
                    "from": s.source,
                    "to": s.target,
                    "group": s.group,
                    "price_from": float(p_from),
                    "price_to": float(p_to),
                    "qty_from": q_from,
                    "qty_to": q_to,
                    "weekly_saving": float(saving),
                }
            )
    cols = ["from", "to", "group", "price_from", "price_to", "qty_from", "qty_to", "weekly_saving"]
    return (
        pd.DataFrame(out, columns=cols)
        .sort_values("weekly_saving", ascending=False)
        .reset_index(drop=True)
    )


def outlook_band(last_value: float, months: int, annual_low: float, annual_high: float):
    """Low/high projections for the next ``months`` months, compounding monthly."""
    band = []
    for m in range(1, months + 1):
        band.append(
            (
                last_value * (1 + annual_low) ** (m / 12),
                last_value * (1 + annual_high) ** (m / 12),
            )
        )
    return band
