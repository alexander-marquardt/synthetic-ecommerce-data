"""#1101, slice 1: a size and category guard wins over the shape table, so a large item is level.

The maintainer, 2026-11-21, from a demo screenshot of a tilted sofa: "sofas should not be tilted.
I think most furniture should not. Neither should mountain bikes. Can you have the generator do a
sanity check on what it is tilting?" A product's angle was its shape's set alone, and a shape
nobody was sure of went to ``upright`` (+-36 degrees): on main d4e5232e, 100 of the 119 products
under Home > Large Appliances were turned. :func:`.orientation.level_because` now draws a product
in a never-tilt category, or one that states a height or length over 60 cm, level whatever its
shape, beside the pack rule (#884).

The slice is five products from the built catalogue (``scale.templates()`` at d4e5232e), recorded
by id in ``tests/fixtures/tilt_slice_1101.json``: the Four Seater Corner Sofa, the Wrenfield
MT26-21-26 mountain bike, the GoodLook Fairmile GLN-260DW fridge freezer (turned 24 degrees on
main), the 2 Door Pine Wardrobe and the Fashion Knitted Gloves (any angle, the maintainer's ruling
on #860).
"""

from __future__ import annotations

import copy
import json
import pathlib
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.domains.retail import image_release, orientation

NS = "{http://www.w3.org/2000/svg}"

SLICE = json.loads(
    (pathlib.Path(__file__).parent / "fixtures" / "tilt_slice_1101.json").read_text()
)

#: The slice's products by what the issue calls them.
NAMED = {
    "sofa": "PLT-SOFCRN",
    "mountain bike": "BRD-BIKMT262126",
    "fridge": "BRD-GLA001",
    "wardrobe": "BRD-WD2HG",
    "glove": "BRD-DCGLV1",
}


def _angle(rec: dict) -> int:
    return product_look.angle_of(rec["product_id"], orientation.of_product(rec))


def _turns(rec: dict) -> list[str]:
    """The ``turn`` group transforms of every SKU's SVG: the group that holds the rotate (#849)."""
    return [
        g.get("transform")
        for sku in rec["skus"]
        for g in ET.fromstring(image_release.render(rec, sku, styled=True)).iter(f"{NS}g")
        if g.get("class") == "turn"
    ]


def test_the_slice_holds_the_five_named_products():
    assert sorted(r["product_id"] for r in SLICE) == sorted(NAMED.values())
    by_id = {r["product_id"]: r for r in SLICE}
    assert "Mountain Bikes" in by_id[NAMED["mountain bike"]]["category_path"]
    assert by_id[NAMED["fridge"]]["drawing"]["shape"] == "fridge"
    assert by_id[NAMED["glove"]]["drawing"]["shape"] == "gloves"


def test_only_the_glove_is_turned():
    turned = {r["product_id"]: _angle(r) for r in SLICE if _angle(r)}
    assert list(turned) == [NAMED["glove"]], turned


@pytest.mark.parametrize("name", sorted(NAMED), ids=str)
def test_every_sku_of_only_the_glove_is_drawn_turned(name):
    rec = next(r for r in SLICE if r["product_id"] == NAMED[name])
    turns = _turns(rec)
    if name == "glove":
        assert len(turns) == len(rec["skus"]), turns
    else:
        assert turns == [], f"{name} {rec['product_id']} is turned: {turns[0]}"


@pytest.mark.parametrize("name", ["sofa", "mountain bike", "fridge", "wardrobe"], ids=str)
def test_the_category_wins_over_a_tiltable_shape(name):
    """Drawn with the glove's ``any`` shape, each large product is still level: the guard reads
    its category, not its shape."""
    rec = copy.deepcopy(next(r for r in SLICE if r["product_id"] == NAMED[name]))
    rec["drawing"]["shape"] = "gloves"
    assert orientation.level_because(rec) == "category"
    assert orientation.of_product(rec) == "level"


@pytest.mark.parametrize(
    ("field", "value", "cm"),
    [
        ("length_cm", 170, 170.0),
        ("height_cm", "61", 61.0),
        ("height", "6 ft", 6 * 30.48),
        ("dimensions", "60 x 90 cm", 90.0),
        ("dimensions", "30 x 20 cm, 40 x 28 cm", 40.0),
    ],
)
def test_a_stated_size_over_60_cm_is_level_whatever_the_shape(field, value, cm):
    """The glove, outside any never-tilt category, given one SKU that states a size."""
    rec = copy.deepcopy(next(r for r in SLICE if r["product_id"] == NAMED["glove"]))
    rec["skus"][0][field] = value
    assert orientation.stated_cm(rec) == pytest.approx(cm)
    assert orientation.level_because(rec) == ("size" if cm > orientation.MAX_TILT_CM else None)


def test_a_run_length_in_metres_is_not_a_size():
    """A cable's or a hose's ``length_m`` is the run, drawn coiled: it keeps the shape's tilt."""
    rec = copy.deepcopy(next(r for r in SLICE if r["product_id"] == NAMED["glove"]))
    rec["skus"][0]["length_m"] = 10
    assert orientation.stated_cm(rec) is None
    assert orientation.level_because(rec) is None
    assert orientation.of_product(rec) == "any"
