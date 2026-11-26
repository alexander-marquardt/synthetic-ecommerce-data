"""Furniture fills its picture: each SKU's drawing covers half the product area or more (#1214).

Every SKU of every built template that draws one of these shapes is rendered as the plain sheet
and measured with #1129's sweep (``picture_fill_1129.measure``): the share of the product area
(``house_styles.TURN_AREA``) it paints, its highlight and its shadow. A product sold in sizes or
packs is measured at each of them. Slice 1 is ``kit_furniture``'s seven types, slice 2 the sofas
of ``kit_seating``."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.domains.retail import (  # noqa: E402
    image_release,
    scale,
    size_ladder,
)

#: The shape each type of the issue's list draws, and the type.
TYPES = {
    "dining_table": "Dining Table",
    "dining_chair": "Dining Chair",
    "coffee_table": "Coffee Table",
    "side_table": "Side Table",
    "bookcase": "Bookcase",
    "mirror": "Mirror",
    "wardrobe": "Wardrobe",
    "sofa_seats": "Sofa",
    "sofa_version": "Sofa",
    "corner_sofa": "Corner Sofa",
    "u_sofa": "Corner Sofa",
    "chaise_sofa": "Chaise Sofa",
    "modular_sofa": "Modular Sofa",
    "recliner_sofa": "Recliner Sofa",
    "sofa_bed": "Sofa Bed",
}
#: The SKUs a shape's built templates hold at least, so an emptied shape cannot pass unseen.
FEWEST = {"u_sofa": 4}
FLOOR = 0.50
#: The named exceptions: a mirror about 1 to 3 (40 x 150 cm, 50 x 160 cm) or 1 to 4 (45 x 170 cm).
#: A solid box of 1 to 3.2 as tall as the product area covers 30% of it.
FLOORS = {("mirror", "full_length"): 0.30, ("mirror", "floor"): 0.36}


def _kind(rec: dict) -> tuple[str, str]:
    drawing = rec["drawing"]
    return drawing["shape"], (drawing.get("params") or {}).get("kind", "")


@pytest.mark.parametrize("shape", TYPES)
def test_every_sku_fills_its_floor_with_a_highlight_and_a_shadow(shape):
    short, checked = [], 0
    for rec in scale.templates():
        if rec["drawing"]["shape"] != shape or rec["product_type"] != TYPES[shape]:
            continue
        floor = FLOORS.get(_kind(rec), FLOOR)
        for sku in rec["skus"]:
            svg = image_release.render(rec, sku, styled=False)
            got = pf.measure(svg, pf.TURN_AREA)
            checked += 1
            if got.cover < floor or not got.highlight or not got.shadow or got.flat:
                short.append((sku["sku"], floor, got))
    assert checked >= FEWEST.get(shape, 12), (shape, checked)
    assert short == [], f"{len(short)} of {checked} {shape} SKUs: {short[:3]}"


def test_an_exception_names_a_product_the_catalogue_sells():
    sold = {_kind(rec) for rec in scale.templates()}
    assert set(FLOORS) <= sold


@pytest.mark.parametrize("shape", ["dining_table", "bookcase", "mirror", "sofa_bed"])
def test_a_size_of_furniture_is_drawn_smaller_but_not_under_the_floor(shape):
    """The shared ladder's smallest rung, 0.55 of 0.90, keeps 37% of the largest one's area."""
    kept = (size_ladder.bottom({"drawing": {"shape": shape}}) / size_ladder.TOP) ** 2
    assert 0.80 <= kept < 0.95, (shape, kept)


SOFAS = [shape for shape in TYPES if "sofa" in shape]


@pytest.mark.parametrize("shape", SOFAS)
def test_a_sofa_stands_on_a_ground_shadow_the_fill_does_not_count(shape):
    rec = next(r for r in scale.templates() if r["drawing"]["shape"] == shape)
    svg = image_release.render(rec, rec["skus"][0], styled=False)
    assert 'class="ground"' in svg
    counted = pf.measure(svg, pf.TURN_AREA, skip=()).cover
    assert pf.measure(svg, pf.TURN_AREA).cover < counted, "the shadow shows past the sofa's edge"
