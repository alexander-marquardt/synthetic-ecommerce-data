"""A styled image draws its product clear of its logo and licence line, at every size (gen#932).

``house_styles.product_transform`` fits the product into the rows the logo's text
(``house_styles.reach``) and a licensed product's licence line (``film_emblems.licence_band``)
leave free. It used to fit a fixed span of the kit's sheet, so a drawing that reaches past that
span still crossed them: an XL hoodie's hood rose into the logo and over "Licensed from Barry
Plotter Studios", and a turned all-in-one's ground shadow dipped into a logo at the foot. These
tests read every hoodie and all-in-one SKU's own image and measure the product's box
(``sheet_extent.reach`` of ``<g class="product">``) against those rows.
"""

from __future__ import annotations

import pytest

from synthetic_ecommerce_data.domains.retail import (
    barry_plotter,
    export,
    film_emblems,
    house_styles,
    image_release,
    scale,
    sheet_extent,
)

SHAPES = ("hoodie", "all_in_one")
#: Rounding in the transform's own numbers (one decimal place in its translate).
SLACK = 0.06


def _free_rows(rec: dict) -> tuple[float, float]:
    """The first and last row of the sheet the product may take: below a logo's text at the top
    (and the licence line under it), above a logo's text at the foot (and the line over it)."""
    style = house_styles.HOUSE_STYLES[rec["brand"]]
    top, bottom = house_styles.reach(style, rec["brand"])
    if film_emblems.emblem_of_id(rec["product_id"]):
        _, (more_top, more_bottom) = film_emblems.licence_band(top, bottom)
        top, bottom = top + more_top, bottom + more_bottom
    return top, house_styles.SIZE - bottom


def _product_rows(svg: str) -> tuple[float, float]:
    """The top and bottom of the product's box on the sheet."""
    defs = svg[svg.index("<defs>") + 6 : svg.index("</defs>")] if "<defs>" in svg else ""
    product = svg[svg.index('<g class="product"') : svg.index('<g class="brand">')]
    box = sheet_extent.reach(
        f'<svg xmlns="http://www.w3.org/2000/svg"><defs>{defs}</defs>{product}</svg>'
    )
    assert box is not None
    return box[1], box[3]


@pytest.fixture(scope="module")
def measured() -> list[tuple[dict, dict, tuple[float, float], tuple[float, float]]]:
    """``(record, sku, product rows, free rows)`` for every hoodie and all-in-one SKU whose
    brand sets a logo, each drawing rendered once."""
    docs = [d for d in scale.templates() if d["drawing"]["shape"] in SHAPES]
    out = []
    drawn: dict[str, tuple[float, float]] = {}
    for d in docs:
        if house_styles.HOUSE_STYLES[d["brand"]].mark == house_styles.NO_MARK:
            continue
        free = _free_rows(d)
        for s in d["skus"]:
            key = export.drawing_id(d, s)
            if key not in drawn:
                drawn[key] = _product_rows(image_release.render(d, s).decode())
            out.append((d, s, drawn[key], free))
    return out


def test_every_hoodie_and_all_in_one_is_drawn_clear_of_the_logo_and_licence_line(measured) -> None:
    assert len(measured) > 400
    crossing = [
        (s["sku"], d["brand"], s.get("size"), round(y0, 1), round(y1, 1), lo, hi)
        for d, s, (y0, y1), (lo, hi) in measured
        if y0 < lo - SLACK or y1 > hi + SLACK
    ]
    assert crossing == []


def test_the_ranges_xl_hoodies_and_all_in_ones_are_among_those_measured(measured) -> None:
    """The SKUs the issue found crossing: the range's XL hoodies of Harbour & Pine and Larkmoor,
    and its all-in-ones of Quillon Sleep and Little Fernby."""
    seen = {
        (d["brand"], d["drawing"]["shape"])
        for d, s, _, _ in measured
        if d["product_id"] in barry_plotter.ids()
    }
    assert {
        ("Harbour & Pine", "hoodie"),
        ("Larkmoor", "hoodie"),
        ("Quillon Sleep", "all_in_one"),
        ("Little Fernby", "all_in_one"),
    } <= seen
