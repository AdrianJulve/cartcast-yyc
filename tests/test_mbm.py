import math

import pytest

from cartcast.config import SAMPLE_DIR
from cartcast.mbm import load_mbm_food, weekly_benchmark


def test_load_mbm_food_filters_region_component_dollars_and_base():
    df = load_mbm_food(SAMPLE_DIR / "mbm_sample.csv", "Calgary")
    assert set(df["geo"]) == {"Calgary, Alberta"}
    assert set(df["base"]) == {"2023-base"}, "newest base year should be chosen"
    assert df["year"].tolist() == [2023, 2024]
    # Current dollars only: constant-dollar rows are 10% lower in the sample.
    assert df["value"].iloc[-1] > 12400


def test_load_mbm_food_unknown_region_raises():
    with pytest.raises(ValueError, match="No MBM food rows"):
        load_mbm_food(SAMPLE_DIR / "mbm_sample.csv", "Atlantis")


def test_weekly_benchmark_uses_square_root_scale():
    annual = 52 * 200.0  # $200 a week for a family of four
    assert weekly_benchmark(annual, 4) == pytest.approx(200.0)
    assert weekly_benchmark(annual, 1) == pytest.approx(100.0)
    assert weekly_benchmark(annual, 6) == pytest.approx(200.0 * math.sqrt(6) / 2)
