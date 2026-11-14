"""Sports & Outdoors, fishing and golf, slice 1 (gen#959).

The retail Sports & Outdoors department held 1,093 SKUs at the ceiling build against the 11,000
of the #837 mix, and no fishing or golf product, so a search for ``golf balls`` or ``fishing reel``
found nothing. Slice 1 adds a Fishing family (rods, reels, tackle boxes) and a Golf family (clubs,
balls, gloves), each type a derivable spec of its own in ``type_specs/`` drawn by
:mod:`kit_fishing_golf`. These checks hold the slice's Done-when: the ceiling build has at least
3,000 SKUs under the department; each new type's styles have unique ids, titles, twin keys and
SKUs; the rows and their drawings are the same on every call; and a golden slice pins each type's
first derived styles, so a change that moves them shows here.
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, scale, type_registry
from synthetic_ecommerce_data.domains.retail.sports_helpers import DEPARTMENT

TYPES = ("Fishing Rod", "Fishing Reel", "Tackle Box", "Golf Club", "Golf Ball", "Golf Glove")
KEYS = {
    "Fishing Rod": "fishing_rod",
    "Fishing Reel": "fishing_reel",
    "Tackle Box": "tackle_box",
    "Golf Club": "golf_club",
    "Golf Ball": "golf_ball",
    "Golf Glove": "golf_glove",
}
#: The slice's floor at the ceiling build (the gate comment of gen#959).
FLOOR = 3_000


@pytest.fixture(scope="module")
def sports() -> list[dict]:
    return [r for r in ceiling_build().records if r["category_path"][0] == DEPARTMENT]


def test_the_ceiling_build_holds_the_slice_floor_of_sports_skus(sports) -> None:
    skus = sum(r["sku_count"] for r in sports)
    assert skus >= FLOOR, skus


def test_every_type_of_the_slice_is_derived_in_the_ceiling_build(sports) -> None:
    derived = set(ceiling_build().template_of)
    kinds = {r["product_type"] for r in sports if r["product_id"] in derived}
    assert set(TYPES) <= kinds, sorted(set(TYPES) - kinds)


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_has_unique_ids_titles_and_twin_keys(sports, ptype) -> None:
    mine = [r for r in sports if r["product_type"] == ptype]
    assert mine
    for field in ("product_id", "title"):
        repeats = [v for v, n in collections.Counter(r[field] for r in mine).items() if n > 1]
        assert repeats == [], field
    twins = [k for k, n in collections.Counter(scale.twin_key(r) for r in mine).items() if n > 1]
    assert twins == []
    skus = [s["sku"] for r in mine for s in r["skus"]]
    assert len(skus) == len(set(skus))


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_rows_and_drawings_are_deterministic(ptype) -> None:
    spec = type_registry.specs()[KEYS[ptype]]
    assert spec.derivable
    assert [r.doc() for r in spec.rows] == [r.doc() for r in spec.rows]
    fill = kit.Fill("solid", "#123456", "#654321")
    for row in spec.rows:
        params = dict(row.params)
        first = kit.render(row.shape, fill, params=params)
        assert first == kit.render(row.shape, fill, params=params)


def _golden(sports: list[dict], ptype: str) -> list[tuple]:
    derived = set(ceiling_build().template_of)
    mine = sorted((r for r in sports if r["product_type"] == ptype and r["product_id"] in derived),
                  key=lambda r: r["product_id"])  # fmt: skip
    return [(r["product_id"], r["title"], r["sku_count"], r["price"]) for r in mine[:3]]


#: Each type's first three derived styles by product id (seed 0, ceiling build).
GOLDEN: dict[str, list[tuple]] = {
    "Fishing Rod": [
        ("BRD-090958B9198F", "Torley Medium Fiberglass Spinning Fishing Rod", 12, 41.0),
        ("BRD-0D5F1D0F2695", "Hepridge Medium Fiberglass Casting Fishing Rod", 6, 63.0),
        ("BRD-0EB768D023F8", "Claydale Heavy Fiberglass Fly Fishing Rod", 6, 79.0),
    ],
    "Fishing Reel": [
        ("BRD-062CA0F7D510", "Mergarth Aluminum 3 Bearing Spinning Fishing Reel", 12, 42.0),
        ("BRD-0654A32212EB", "Gilington Aluminum 5 Bearing Baitcasting Fishing Reel", 12, 17.0),
        ("BRD-08D13BABC85D", "Lincroft Graphite 5 Bearing Spinning Fishing Reel", 12, 55.0),
    ],
    "Tackle Box": [
        ("BRD-048D1B5CA18B", "Wykeridge 2 Tray Drawer Tackle Box", 8, 18.5),
        ("BRD-05D95C54AC61", "Hawholme 2 Tray Hip Roof Tackle Box", 4, 25.0),
        ("BRD-06A41B8EA7EC", "Oxthorpe 3 Tray Drawer Tackle Box", 4, 16.0),
    ],
    "Golf Club": [
        ("BRD-061454920FCD", "Edenbrook Graphite Driver Golf Club", 8, 62.0),
        ("BRD-084930823321", "Thurness Steel Fairway Wood Golf Club", 6, 79.0),
        ("BRD-0D1525BCCAE1", "Kelgate Steel Driver Golf Club", 8, 65.0),
    ],
    "Golf Ball": [
        ("BRD-08134E2AC941", "Fernmouth Urethane 4-Piece Golf Balls", 12, 10.5),
        ("BRD-0E9B6CA81DA4", "Wraycroft Urethane 2-Piece Golf Balls", 12, 11.0),
        ("BRD-10BDF9821931", "Rockborough Urethane 4-Piece Golf Balls", 12, 12.0),
    ],
    "Golf Glove": [
        ("BRD-100228D32570", "Ormstead Cabretta Leather Golf Glove, Left Hand", 16, 17.0),
        ("BRD-145EDF083F79", "Torness Synthetic Golf Glove, Right Hand", 16, 11.0),
        ("BRD-24BC6EB2F440", "Belthwaite Synthetic Golf Glove, Left Hand", 12, 11.5),
    ],
}


@pytest.mark.parametrize("ptype", TYPES)
def test_each_type_golden_slice(sports, ptype) -> None:
    assert _golden(sports, ptype) == GOLDEN[ptype]
