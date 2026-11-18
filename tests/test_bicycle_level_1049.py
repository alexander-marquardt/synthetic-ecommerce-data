"""#1049, slice 1: a bicycle is drawn level, and a level adult bike spans most of its figure area.

The maintainer, from the search results for ``bicycle``: "I don't think bikes should have an angle
.. also, they should be larger." A bike rests on its two wheels, and turned up to 36 degrees (the
``upright`` set, #849) it read as falling or wheelieing. ``bicycle`` is now in the ``level`` set.

THE SIZE, MEASURED. Retail draws a bike in the kit's own units, not by ``type_scale`` (that is the
industrial sheet), and no larger kind sets its extent. The figure area is the box a product is
drawn inside, :data:`.house_styles.TURN_AREA`: 344 units across. Level, each adult kind's full-size
drawing spans most of it (road 318 units, electric 312, mountain 376). A bike looked a third of the
sheet wide because three factors multiplied: the turn's fit-scale (0.909 at 24 degrees, down to
0.707), the size ladder's smallest frame (0.55 / 0.90 of full size, gen#339 and gen#718), and the
house style's product scale (0.86 or 0.78). Slice 1 removed the first.

SLICE 2: EVERY SKU. A bicycle has a size ladder of its own (:data:`.size_ladder.BOTTOMS`): its
smallest frame draws at 0.82 of full size, not the shared 0.61. The road, electric and kids
drawings are as wide as the figure area at full size, so every SKU, every frame size and the kids'
bike included, spans at least 80% of it, and its sizes still draw apart (gen#718).
"""

from __future__ import annotations

import functools
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    house_styles,
    image_release,
    orientation,
    scale,
    sheet_extent,
    size_ladder,
)

NS = "{http://www.w3.org/2000/svg}"
#: The figure area's width, in the kit's units.
AREA_WIDTH = house_styles.TURN_AREA[2] - house_styles.TURN_AREA[0]
#: The share of it every bicycle SKU's drawing spans at least (the issue's target).
FILL = 0.80
#: The kinds sold to adults, beside the kids' bike.
ADULT = ("Road", "Mountain", "Electric")
#: The issue's two products, turned -24 and +24 degrees on main.
NAMED = ("BRD-BIKOB22RD2826", "BRD-BIKRMRD222826")


def _bikes() -> list[dict]:
    return [rec for rec in scale.templates() if rec["drawing"]["shape"] == "bicycle"]


BIKES = _bikes()


def _kind(rec: dict) -> str:
    return next(a["value"] for a in rec["attributes"] if a["key"] == "bike_type")


@functools.cache
def _root(product_id: str, sku_id: str) -> ET.Element:
    rec = next(r for r in BIKES if r["product_id"] == product_id)
    sku = next(s for s in rec["skus"] if s["sku"] == sku_id)
    return ET.fromstring(image_release.render(rec, sku, styled=True))


def _product(root: ET.Element) -> ET.Element:
    found = [g for g in root.iter(f"{NS}g") if g.get("class") == "product"]
    assert len(found) == 1, f"expected one product group, found {len(found)}"
    return found[0]


def _drawn_width(root: ET.Element) -> float:
    """The width the product's drawing covers in the kit's units: inside the house style's
    product transform, with the sheet's ``<defs>`` so a pattern fill can be measured."""
    wrap = ET.Element(f"{NS}svg")
    defs = root.find(f"{NS}defs")
    if defs is not None:
        wrap.append(defs)
    wrap.extend(list(_product(root)))
    box = sheet_extent.reach(ET.tostring(wrap))
    assert box is not None
    return box[2] - box[0]


def test_the_built_catalogue_sells_bikes_of_every_kind_and_both_named_products():
    assert len(BIKES) >= 40
    assert {_kind(rec) for rec in BIKES} == {*ADULT, "Kids"}
    assert set(NAMED) <= {rec["product_id"] for rec in BIKES}


def test_the_bicycle_shape_is_level():
    assert orientation.of("bicycle") == "level"


@pytest.mark.parametrize("rec", BIKES, ids=lambda rec: rec["product_id"])
def test_no_sku_of_a_bicycle_is_turned(rec):
    """No SKU's SVG holds a ``turn`` group, the group that carries the product's rotate (#849)."""
    assert orientation.of_product(rec) == "level"
    for sku in rec["skus"]:
        root = _root(rec["product_id"], sku["sku"])
        turned = [g for g in root.iter(f"{NS}g") if g.get("class") == "turn"]
        assert turned == [], f"{sku['sku']} is turned: {turned[0].get('transform')}"
        assert "rotate(" not in (_product(root).get("transform") or "")


@pytest.mark.parametrize("rec", BIKES, ids=lambda rec: rec["product_id"])
def test_every_sku_of_a_bicycle_spans_most_of_the_figure_area(rec):
    """Every SKU: each frame size on the bicycle's own ladder, and the kids' bike (slice 2)."""
    for sku in rec["skus"]:
        width = _drawn_width(_root(rec["product_id"], sku["sku"]))
        assert width >= FILL * AREA_WIDTH, (
            f"{sku['sku']} ({_kind(rec)}, size scale {size_ladder.size_scale(rec, sku)}) spans "
            f"{width:.0f} of the figure area's {AREA_WIDTH:.0f} units, under {FILL:.0%}"
        )
