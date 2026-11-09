import pandas as pd
import pytest

from cartcast.prices import load_prices, suggest, to_wide, yoy_change


def test_load_prices_filters_geo_and_drops_missing(tiny_prices_csv):
    df = load_prices(tiny_prices_csv, geo="Alberta")
    assert set(df.columns) == {"month", "product", "price"}
    assert (df["price"] != 9.99).all(), "Canada row should be filtered out"
    assert len(df) == 5, "suppressed (blank) value should be dropped"
    assert df["month"].dtype.kind == "M"


def test_load_prices_unknown_geo_raises(tiny_prices_csv):
    with pytest.raises(ValueError, match="No rows"):
        load_prices(tiny_prices_csv, geo="Atlantis")


def test_yoy_change(tiny_prices_csv):
    wide = to_wide(load_prices(tiny_prices_csv))
    jan26 = pd.Timestamp("2026-01-01")
    assert yoy_change(wide, "Apples, per kilogram", jan26) == pytest.approx(20.0)
    assert yoy_change(wide, "Milk, 4 litres", jan26) == pytest.approx(10.0)
    assert yoy_change(wide, "Not a product", jan26) is None
    # No observation 12 months before Feb 2025 -> None
    assert yoy_change(wide, "Apples, per kilogram", pd.Timestamp("2025-02-01")) is None


def test_suggest_finds_close_names():
    names = ["Ground beef, per kilogram", "Milk, 4 litres", "Eggs, 1 dozen"]
    assert suggest("Ground beef per kilogram", names)[0] == "Ground beef, per kilogram"
    assert suggest("zzzz", names) == []
