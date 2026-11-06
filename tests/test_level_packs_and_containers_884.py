"""#884: a pack, a set and an upright good are drawn with no tilt.

#860 turned every product's figure by its own angle within its type's orientation. A cup set
drawn as 2, 4 or 8 cups then sat on a slant, and so did a jar of peanut butter. The issue's
Done-when, one test group each:

1. a product drawn as a pack (any SKU of it holds more than one item) is drawn level on every
   SKU, retail and industrial, so its SKUs still share one angle (#849);
2. upright goods (jars, bottles, cans, boxes, cups) and set shapes are drawn level, and which
   ones is data: the ``level`` orientation of their shape or type in the orientation tables.
"""

from __future__ import annotations

import functools
import json
import re
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import domain
from synthetic_ecommerce_data.core.bundle import flat_facets, records
from synthetic_ecommerce_data.core.drawing import draw_product, product_look
from synthetic_ecommerce_data.domains.retail import grocery, image_release, pack_copies
from synthetic_ecommerce_data.domains.retail import orientation as retail_orientation

GOLDEN = Path(__file__).resolve().parent.parent / "golden-catalog"
#: The retail product's turn: the ``turn`` group's rotate.
RETAIL_TURN = re.compile(r'<g class="turn" transform="[^"]*rotate\((-?[\d.]+)\)')
#: An industrial figure's turn: the group around its shapes.
INDUSTRIAL_TURN = re.compile(r'<g transform="rotate\((-?[\d.]+) ')


def _turns(svg: str, turn: re.Pattern) -> set[float]:
    return {float(a) for a in turn.findall(svg)} - {0.0}


# --- 1. a pack is drawn level -------------------------------------------------------------


def test_every_sku_of_the_espresso_cup_set_is_drawn_level():
    """The issue's own example: the cup set in 2, 4 and 8 packs, turned -36 degrees on main."""
    (rec,) = [r for r in image_release.records() if r["product_id"] == "PLT-DRKSET"]
    packs = sorted(pack_copies.count(rec, sku) for sku in rec["skus"])
    assert packs == [2, 4, 8]
    for sku in rec["skus"]:
        assert _turns(image_release.render(rec, sku).decode(), RETAIL_TURN) == set(), sku["sku"]


def test_every_retail_product_with_a_pack_sku_is_level_on_every_sku():
    """Over the retail image release: a product any SKU of which holds several items draws no
    SKU turned, the single one beside its packs included."""
    turned = []
    packed = 0
    for rec in image_release.records():
        if not any(pack_copies.count(rec, sku) > 1 for sku in rec["skus"]):
            continue
        packed += 1
        for sku in rec["skus"]:
            if _turns(image_release.render(rec, sku).decode(), RETAIL_TURN):
                turned.append((rec["product_id"], sku["sku"]))
    assert packed > 20
    assert turned == []


@functools.cache
def _golden() -> list[dict]:
    lines = (GOLDEN / "nested.jsonl").read_text("utf-8").splitlines()
    return [json.loads(line) for line in lines if line]


def test_an_industrial_pack_card_is_drawn_level():
    """A pack type's product (end mills, ear plugs) with a SKU of more than one unit fans its
    items upright, with no turn on any SKU."""
    facets = flat_facets(GOLDEN)
    turned = []
    packed = 0
    for parent in _golden():
        if not domain.is_pack_type(parent["product_type"]):
            continue
        recs = records(parent, facets)
        if not any(int(r.get("Units per Pack") or 1) > 1 for r in recs):
            continue
        packed += 1
        drawn = draw_product(parent["product_type"], parent["brand"], recs, parent["product_id"])
        if any(_turns(data.decode(), INDUSTRIAL_TURN) for data, _ in drawn):
            turned.append(parent["product_id"])
    assert packed > 0
    assert turned == []


# --- 2. upright goods and sets are level, by their orientation ------------------------------


def test_level_is_the_one_angle_zero():
    assert product_look.ORIENTATIONS.get("level") == (0,)


@pytest.mark.parametrize(
    "shape",
    ["jar", "moisturiser_jar", "bottle", "angled_bottle", "tin", "box", "carton", "tub",
     "espresso_cup", "tea_cup", "mug", "drinking_glass", "cutlery_set", "dinner_set"],
)  # fmt: skip
def test_a_retail_upright_good_or_set_is_level(shape):
    assert retail_orientation.of(shape) == "level"


@pytest.mark.parametrize(
    "type_key", ["bearing_greases", "tapping_fluids", "bit_socket_sets", "kit_assortment"]
)
def test_an_industrial_container_or_kit_is_level(type_key):
    assert domain.orientation(type_key) == "level"


def test_a_peanut_butter_jar_is_drawn_level():
    """The maintainer's example: every peanut butter jar of the grocery build, turned 24, 12 or
    -12 degrees on main."""
    jars = [
        r for r in grocery.build()
        if "Peanut Butter" in r["title"] and r["drawing"]["shape"] == "jar"
    ]  # fmt: skip
    assert len(jars) > 3
    turned = [
        (rec["product_id"], sku["sku"])
        for rec in jars
        for sku in rec["skus"]
        if _turns(image_release.render(rec, sku).decode(), RETAIL_TURN)
    ]
    assert turned == []
