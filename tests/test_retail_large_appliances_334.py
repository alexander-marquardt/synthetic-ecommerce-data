"""Large appliances (gen#334): fridges and freezers, dishwashers and laundry, with their decoys.

Home > Large Appliances holds eight kinds of fridge and freezer, four of dishwasher and five of
laundry appliance, at least six products each (a color is a SKU, not a product), and the class-8
decoys of the words "dishwasher", "washing machine" and "fridge": products whose title holds the
word and whose structured fields say they are something else.
"""

from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_product_words as dpw  # noqa: E402
import scale  # noqa: E402

ROOT = ["Home", "Large Appliances"]
LEAVES = {"Fridges & Freezers": 8, "Dishwashers": 4, "Laundry": 5}


@pytest.fixture(scope="module")
def appliances() -> list[dict]:
    return [r for r in scale.templates() if r["category_path"][:2] == ROOT]


def _kind(record: dict) -> str:
    return next(a["value"] for a in record["attributes"] if a["key"] == "appliance_type")


@pytest.mark.parametrize("leaf", sorted(LEAVES))
def test_a_leaf_holds_every_kind_the_issue_lists_with_at_least_six_products_each(appliances, leaf):
    own = [r for r in appliances if r["category_path"][2] == leaf]
    typed = [r for r in own if any(a["key"] == "appliance_type" for a in r["attributes"])]
    kinds = Counter(_kind(r) for r in typed)
    assert len(kinds) == LEAVES[leaf], kinds
    assert min(kinds.values()) >= 6, kinds


def test_there_are_at_least_sixty_large_appliance_products(appliances):
    assert len({r["product_id"] for r in appliances}) >= 60


def test_a_black_edition_fridge_is_stainless_and_a_red_spot_machine_is_white(appliances):
    by_title = {r["title"]: r for r in appliances}
    fridge = by_title.get("Black Edition Fridge Freezer")
    washer = by_title.get("Washing Machine with Red Spot Dial")
    assert fridge and washer, sorted(by_title)
    assert {c["color"] for c in fridge["color_options"]} == {"Silver"}
    assert ("finish", "Stainless Steel") in {(a["key"], a["value"]) for a in fridge["attributes"]}
    assert {c["color"] for c in washer["color_options"]} == {"White"}


@pytest.mark.parametrize("query", ["dishwasher", "washing machine", "fridge"])
def test_each_appliance_word_has_at_least_three_class_8_decoys(query):
    rows = [r for r in dpw.TABLE if r.query == query]
    assert len(rows) >= 3, [r.title for r in rows]
    assert all(query in r.title.lower() for r in rows)
    assert all(r.ptype not in {"Dishwasher", "Fridge & Freezer", "Laundry Appliance"} for r in rows)
