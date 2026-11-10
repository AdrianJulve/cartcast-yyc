import pandas as pd
import pytest

from cartcast.basket import (
    aisle_shares,
    basket_cost,
    outlook_band,
    swap_savings,
    validate_products,
)
from cartcast.config import Swap


def test_basket_cost_forward_fills_missing(wide, items):
    cost = basket_cost(wide, items)
    # Jan: 10*1 + 2*2 = 14 ; Feb: 11 + 2*2 (B carried forward) = 15 ; Mar: 12 + 3*2 = 18
    assert cost.tolist() == [14.0, 15.0, 18.0]


def test_basket_cost_scales_by_household(wide, items):
    assert basket_cost(wide, items, scale=0.5).iloc[-1] == pytest.approx(9.0)


def test_aisle_shares_sum_to_one(wide, items):
    shares = aisle_shares(wide, items, pd.Timestamp("2025-03-01"))
    assert shares.sum() == pytest.approx(1.0)
    assert shares["Meat & fish"] == pytest.approx(12 / 18)


def test_swap_savings_uses_ratio_and_skips_unhelpful(wide, items):
    swaps = [
        Swap("A, per kilogram", "C, per kilogram", 1.0, "Protein"),  # 12 -> 4, saves 8
        Swap("B, 500 grams", "A, per kilogram", 0.5, "Pantry"),  # 2*3=6 vs 1*12=12 -> no saving
        Swap("Missing", "A, per kilogram"),
    ]
    out = swap_savings(wide, items, swaps, pd.Timestamp("2025-03-01"))
    assert out["from"].tolist() == ["A, per kilogram"]
    assert out.loc[0, "weekly_saving"] == pytest.approx(8.0)


def test_outlook_band_compounds_monthly():
    band = outlook_band(100.0, 12, 0.04, 0.06)
    assert len(band) == 12
    assert band[-1][0] == pytest.approx(104.0)
    assert band[-1][1] == pytest.approx(106.0)
    assert all(lo < hi for lo, hi in band)


def test_validate_products_suggests():
    issues = validate_products(
        ["Eggs, 1 dozn", "Milk, 4 litres"], ["Eggs, 1 dozen", "Milk, 4 litres"]
    )
    assert len(issues) == 1
    assert issues[0].resolved == "Eggs, 1 dozen"
    assert "Eggs, 1 dozen" in str(issues[0])


def test_resolve_config_matches_close_names_and_drops_unknown():
    from cartcast.basket import resolve_config
    from cartcast.config import BasketItem as BI

    available = [
        "Eggs, 1 dozen",
        "Milk, 4 litres",
        "Bread, 675 grams",
        "Apples, per kilogram",
        "Bananas, per kilogram",
        "Carrots, 1.36 kilograms",
        "Butter, 454 grams",
    ]
    items = [BI(n, 1.0, "Pantry") for n in available[:5]]
    items.append(BI("Butter, 454 gram", 1.0, "Dairy & eggs"))  # close: StatCan wording change
    items.append(BI("Saffron, 1 gram", 1.0, "Pantry"))  # not in the data
    swaps = [Swap("Butter, 454 gram", "Eggs, 1 dozen"), Swap("Saffron, 1 gram", "Eggs, 1 dozen")]

    out_items, out_swaps, issues = resolve_config(items, swaps, available)
    names = [i.product for i in out_items]
    assert "Butter, 454 grams" in names and "Saffron, 1 gram" not in names
    assert [(s.source, s.target) for s in out_swaps] == [("Butter, 454 grams", "Eggs, 1 dozen")]
    resolved = {i.product: i.resolved for i in issues}
    assert resolved == {"Butter, 454 gram": "Butter, 454 grams", "Saffron, 1 gram": None}


def test_resolve_config_fails_when_too_few_items_match():
    from cartcast.basket import resolve_config
    from cartcast.config import BasketItem as BI

    with pytest.raises(ValueError, match="Only 1 basket products"):
        resolve_config([BI("Milk, 4 litres", 1, "x"), BI("Nope", 1, "x")], [], ["Milk, 4 litres"])
