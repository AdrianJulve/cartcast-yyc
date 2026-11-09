"""Basket costing, swaps, aisle shares and the price outlook."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import BasketItem, Swap
from .prices import suggest


@dataclass(frozen=True)
class ValidationIssue:
    product: str
    suggestions: list[str]

    def __str__(self) -> str:
        hint = f" — did you mean: {', '.join(self.suggestions)}?" if self.suggestions else ""
        return f"Unknown product '{self.product}'{hint}"


def validate_products(names: list[str], available: list[str]) -> list[ValidationIssue]:
    known = set(available)
    return [ValidationIssue(n, suggest(n, available)) for n in names if n not in known]


def basket_cost(wide: pd.DataFrame, items: list[BasketItem], scale: float = 1.0) -> pd.Series:
    """Weekly basket cost per month.

    A month with a missing price for one item carries that item's last known
    price forward so a single suppressed cell doesn't make the line jump.
    """
    cols = [i.product for i in items if i.product in wide.columns]
    qty = pd.Series({i.product: i.qty * scale for i in items if i.product in wide.columns})
    filled = wide[cols].ffill()
    return (filled * qty).sum(axis=1, min_count=1).rename("basket_cost")


def aisle_shares(wide: pd.DataFrame, items: list[BasketItem], month: pd.Timestamp) -> pd.Series:
    """Share (0–1) of the basket's cost in each aisle for one month."""
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
