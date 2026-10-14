"""Near-white shades on apparel and every bra shape in every main color (gen#302).

A color-group demo ("womens cream jumper", "ladies ivory cardigan", "white minimiser bras")
needs the products: a near-white shade next to white on knitwear, tops and dresses, at least
150 women's jumpers so a page of 10 does not repeat one style, and each of the five bra shapes
a shopper names in each of the five main colors a bra comes in. The expected values are
written out here, not read from the rows module, so dropping one from the rows fails this file.

The counts are taken over :func:`scale.templates`: every row is a template, and a derived
style only adds to them, so a count met here is met by the ceiling build.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402
import facet_leaves  # noqa: E402
import scale  # noqa: E402

SHADES = ("Cream", "Ivory", "Off White")
#: The product types a near-white shade sits on: knitwear, tops and dresses.
APPAREL = frozenset({"Jumper", "Cardigan", "Dress", "Top", "Blouse"})
MIN_SKUS_PER_SHADE = 20
MIN_TYPES_PER_SHADE = 3
MIN_JUMPER_SKUS = 150
BRA_SHAPES = ("Minimiser", "Plunge", "Balcony", "Full Cup", "T-Shirt")
BRA_COLORS = ("White", "Black", "Beige", "Red", "Blue")


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _women(rec: dict) -> bool:
    return rec["category_path"][0] == "Women"


def test_off_white_is_a_plain_color_value():
    assert colorwords.is_plain("Off White")
    assert not colorwords.is_plain("Off")


@pytest.mark.parametrize("shade", SHADES)
def test_a_near_white_shade_has_enough_skus_on_apparel(templates, shade):
    n = sum(
        1
        for r in templates
        if _women(r) and r["product_type"] in APPAREL
        for s in r["skus"]
        if s.get("color") == shade
    )
    assert n >= MIN_SKUS_PER_SHADE, f"{shade}: {n} apparel SKUs"


@pytest.mark.parametrize("shade", SHADES)
def test_a_near_white_shade_spans_three_apparel_types(templates, shade):
    types = {
        r["product_type"]
        for r in templates
        if _women(r) and r["product_type"] in APPAREL
        for s in r["skus"]
        if s.get("color") == shade
    }
    assert len(types) >= MIN_TYPES_PER_SHADE, f"{shade}: {sorted(types)}"


def test_white_sits_next_to_the_shades_on_apparel(templates):
    assert any(
        s.get("color") == "White"
        for r in templates
        if _women(r) and r["product_type"] in APPAREL
        for s in r["skus"]
    )


def test_a_page_of_womens_jumpers_does_not_repeat_one_style(templates):
    jumpers = [r for r in templates if r["category_path"][:3] == ["Women", "Knitwear", "Jumpers"]]
    n = sum(len(r["skus"]) for r in jumpers)
    assert n >= MIN_JUMPER_SKUS, f"{n} jumper SKUs in {len(jumpers)} styles"


def _bra_colors(templates: list[dict]) -> dict[str, collections.Counter]:
    out: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in templates:
        if r["product_type"] != "Bra":
            continue
        leaf = facet_leaves.BRA_LEAVES.get(r["category_leaf"])
        if leaf is None:
            continue
        for s in r["skus"]:
            out[leaf[0]][s["color"]] += 1
    return out


@pytest.mark.parametrize("shape", BRA_SHAPES)
@pytest.mark.parametrize("color", BRA_COLORS)
def test_every_bra_shape_exists_in_every_main_color(templates, shape, color):
    n = _bra_colors(templates)[shape][color]
    assert n > 0, f"{color} {shape} bra: {n} SKUs"
