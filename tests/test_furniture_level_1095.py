"""#1095, slice 1: every furniture item is drawn upright and level, at 0 degrees on every SKU.

The maintainer, 2026-11-20: tilted beds look wrong in the R&I demo, and then every Furniture item.
A product's angle is :func:`.product_look.angle_of` its id over its shape's orientation set, and
every furniture shape was ``upright`` (+-36 degrees, #849): on main 102 of the 124 products under
Home > Furniture (362 of their 450 SKU images, 13 of the 16 beds) were drawn turned. Every shape
the furniture modules register, and every shape a Home > Furniture product draws, is now in the
``level`` set, as a bicycle is (#1049). Lamps, lighting, garden furniture and cribs are slice 2.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.domains.retail import image_release, orientation, scale
from synthetic_ecommerce_data.domains.retail.orientations import (
    furniture,
    home_furniture,
    seating,
    storage_furniture,
)

NS = "{http://www.w3.org/2000/svg}"

#: The modules naming the orientation of the shapes the four furniture kits register.
MODULES = (furniture, seating, home_furniture, storage_furniture)

#: Those shapes, in whichever set, and the furniture other kits register.
FURNITURE_SHAPES: tuple[str, ...] = (
    *(s for m in MODULES for name in orientation._SETS for s in getattr(m, name, ())),
    "bed_frame",
    "chairbed",
    "sofa",
)


def _furniture() -> list[dict]:
    return [rec for rec in scale.templates() if rec["category_path"][:2] == ["Home", "Furniture"]]


FURNITURE = _furniture()

#: The issue's three named beds: -36 degrees, -24 degrees and 0 on main.
NAMED = ("Pine Panel Bed Frame", "Upholstered Bed Frame", "Shaker")


def test_the_built_catalogue_sells_furniture_and_the_named_beds():
    assert len(FURNITURE) >= 120
    beds = [rec["title"] for rec in FURNITURE if rec["drawing"]["shape"] == "bed_frame"]
    assert len(beds) >= 16
    for name in NAMED:
        assert any(name in title for title in beds), name


def test_the_furniture_modules_name_their_shapes_level_and_none_upright():
    assert len(FURNITURE_SHAPES) >= 27
    for module in MODULES:
        assert not getattr(module, "UPRIGHT", ()), module.__name__
    for shape in FURNITURE_SHAPES:
        assert orientation.of(shape) == "level", shape


def test_every_shape_a_furniture_product_draws_is_level():
    drawn = {rec["drawing"]["shape"] for rec in FURNITURE}
    assert drawn <= set(FURNITURE_SHAPES), sorted(drawn - set(FURNITURE_SHAPES))
    turned = sorted(
        f"{rec['product_id']} {rec['title']}: {angle}"
        for rec in FURNITURE
        if (angle := product_look.angle_of(rec["product_id"], orientation.of_product(rec)))
    )
    assert turned == [], f"{len(turned)} of {len(FURNITURE)} turned: {turned[:5]}"


@pytest.mark.parametrize("rec", FURNITURE, ids=lambda rec: rec["product_id"])
def test_no_sku_of_a_furniture_product_is_turned(rec):
    """No SKU's SVG holds a ``turn`` group, the group that carries the product's rotate (#849)."""
    for sku in rec["skus"]:
        root = ET.fromstring(image_release.render(rec, sku, styled=True))
        turns = [g.get("transform") for g in root.iter(f"{NS}g") if g.get("class") == "turn"]
        assert turns == [], f"{sku['sku']} is turned: {turns[0]}"
