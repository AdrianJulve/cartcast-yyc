"""Load and validate the YAML configuration in ``config/``."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = REPO_ROOT / "config"
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SAMPLE_DIR = DATA_DIR / "sample"
PROCESSED_DIR = DATA_DIR / "processed"
SITE_DIR = REPO_ROOT / "site"


@dataclass(frozen=True)
class BasketItem:
    product: str
    qty: float
    aisle: str


@dataclass(frozen=True)
class Swap:
    source: str
    target: str
    ratio: float = 1.0
    group: str = "Other"


@dataclass
class Config:
    settings: dict[str, Any]
    households: dict[str, dict[str, Any]]
    default_household: str
    items: list[BasketItem]
    aisle_rules: dict[str, list[str]]
    swaps: list[Swap] = field(default_factory=list)

    def aisle_for(self, product: str) -> str:
        """Best-guess aisle for a product name using keyword rules."""
        name = product.lower()
        for item in self.items:
            if item.product == product:
                return item.aisle
        # Longest keyword wins so "soy milk" beats "milk".
        best, best_len = "Pantry", 0
        for aisle, words in self.aisle_rules.items():
            for word in words:
                if word in name and len(word) > best_len:
                    best, best_len = aisle, len(word)
        return best


def _read_yaml(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_config(config_dir: Path | str = CONFIG_DIR) -> Config:
    config_dir = Path(config_dir)
    settings = _read_yaml(config_dir / "settings.yaml")
    basket = _read_yaml(config_dir / "basket.yaml")
    swaps_raw = _read_yaml(config_dir / "swaps.yaml").get("swaps", [])

    items = [
        BasketItem(product=i["product"], qty=float(i["qty"]), aisle=i.get("aisle", "Pantry"))
        for i in basket.get("items", [])
    ]
    swaps = [
        Swap(
            source=s["from"],
            target=s["to"],
            ratio=float(s.get("ratio", 1.0)),
            group=s.get("group", "Other"),
        )
        for s in swaps_raw
    ]
    households = basket.get("households", {"family4": {"label": "Family of 4", "scale": 1.0}})
    default = basket.get("default_household", next(iter(households)))
    if default not in households:
        raise ValueError(f"default_household '{default}' is not defined in households")

    return Config(
        settings=settings,
        households=households,
        default_household=default,
        items=items,
        aisle_rules=basket.get("aisle_rules", {}),
        swaps=swaps,
    )
