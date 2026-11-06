"""#884: a pack or a set is drawn with no tilt; a single product keeps its tilt.

#860 turned every product's figure by its own angle within its type's orientation. A cup set
drawn as 2, 4 or 8 cups then sat on a slant and overlapped. The issue's Done-when, one test
group each:

1. a product drawn as a pack (any SKU of it holds more than one item, read from its pack data)
   is drawn level on every SKU, retail and industrial, so its SKUs still share one angle (#849);
   a set type is level by its orientation, ``level``, in the orientation tables;
2. a single product keeps its #860 tilt: a tea cup, a jar of peanut butter (the maintainer,
   narrowing #884: "singular products look OK tilted in general .. packs look a bit strange").
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


# --- set types are level, by their orientation -------------------------------------------


def test_level_is_the_one_angle_zero():
    assert product_look.ORIENTATIONS.get("level") == (0,)


@pytest.mark.parametrize(
    "shape", ["badminton_set", "cutlery_set", "dinner_set", "drill_bit_set", "gift_set",
              "luggage_set"],
)  # fmt: skip
def test_a_retail_set_type_is_level(shape):
    assert retail_orientation.of(shape) == "level"


@pytest.mark.parametrize("type_key", ["bit_socket_sets", "kit_assortment", "pin_punch_sets"])
def test_an_industrial_set_or_kit_is_level(type_key):
    assert domain.orientation(type_key) == "level"


# --- 2. a single product keeps its tilt -----------------------------------------------------


@pytest.mark.parametrize(
    ("shape", "orientation"),
    [("jar", "upright"), ("bottle", "upright"), ("tea_cup", "upright"), ("dress", "slight"),
     ("bra", "slight"), ("trousers", "slight")],
)  # fmt: skip
def test_a_single_products_shape_keeps_its_860_orientation(shape, orientation):
    assert retail_orientation.of(shape) == orientation


def test_a_single_peanut_butter_jar_and_a_single_tea_cup_keep_their_tilt():
    """The maintainer's examples, out of scope as singles: every peanut butter jar of the
    grocery build and the single tea cup and saucer are drawn at their product's #860 angle."""
    jars = [
        r for r in grocery.build()
        if "Peanut Butter" in r["title"] and r["drawing"]["shape"] == "jar"
    ]  # fmt: skip
    (cup,) = [r for r in image_release.records() if r["product_id"] == "PLT-DRKSAU"]
    assert len(jars) > 3
    turned = 0
    for rec in [*jars, cup]:
        assert not any(pack_copies.count(rec, sku) > 1 for sku in rec["skus"]), rec["product_id"]
        angle = product_look.angle_of(rec["product_id"], "upright")
        turned += angle != 0
        for sku in rec["skus"]:
            svg = image_release.render(rec, sku).decode()
            assert _turns(svg, RETAIL_TURN) == ({float(angle)} if angle else set()), sku["sku"]
    assert turned > 3
