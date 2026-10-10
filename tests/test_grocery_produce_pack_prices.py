"""A weight pack of a per-item fruit is priced as a handful of items, not as 1000 of them.

``grocery._price`` scaled the first pack's price by pack size, and a "1kg" pack counted as 1000
against a "Single" fruit's 1, so a kilogram of limes cost 145 to 165. A family that mixes count
packs and weight packs now declares ``item_g``, the typical weight of one item.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import grocery  # noqa: E402
import grocery_rows  # noqa: E402

PRODUCE = [f for f in grocery_rows.FAMILIES if f.shape == "produce_pile"]
#: A pack of fresh fruit at a supermarket costs a few pounds; 25 is about five times the dearest
#: real one (a 1kg pack of cherries or a large punnet of berries), so only a unit error crosses it.
MAX_PACK_PRICE = 25.0
MIN_PACK_PRICE = 0.3
#: Bulk discount and pack rounding move the price per kg, never by a factor near 3.
PER_KG_FACTOR = 3.0


def _packs(fam):
    return [grocery.parse_pack(p) for p in fam.packs]


@pytest.mark.parametrize("fam", PRODUCE, ids=lambda f: f.code)
def test_every_pack_price_is_plausible(fam) -> None:
    first = _packs(fam)[0]
    for i in range(3):
        for brand in fam.brands:
            for pack in _packs(fam):
                price = grocery._price(fam, pack, first, i, brand)
                size = pack["pack_size"]
                assert MIN_PACK_PRICE <= price <= MAX_PACK_PRICE, (fam.code, size, price)


def _mixed(fam) -> bool:
    packs = _packs(fam)
    weighed = ["net_weight_g" in p for p in packs]
    return any(weighed) and not all(weighed)


MIXED = [f for f in grocery_rows.FAMILIES if _mixed(f)]


def test_the_mixed_families_include_the_produce_that_sells_by_the_kilogram() -> None:
    assert {"LIM", "LEM", "ORA"} <= {f.code for f in MIXED}


@pytest.mark.parametrize("fam", MIXED, ids=lambda f: f.code)
def test_price_per_kg_agrees_between_count_and_weight_packs(fam) -> None:
    packs = _packs(fam)
    assert getattr(fam, "item_g", 0) > 0, f"{fam.code} mixes pack kinds, declares no item_g"
    first = packs[0]
    brand = fam.brands[0]
    per_kg = []
    for pack in packs:
        grams = pack.get("net_weight_g") or pack["units_per_pack"] * fam.item_g
        per_kg.append(grocery._price(fam, pack, first, 0, brand) / grams * 1000)
    assert max(per_kg) / min(per_kg) <= PER_KG_FACTOR, per_kg
