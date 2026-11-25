"""Drills, drivers, ladders, tool kits and volt meters are drawn large and lit (#1215).

Every SKU of every built template that draws one of these shapes is rendered as the plain sheet and
measured with #1129's sweep (``picture_fill_1129.measure``): the share of the product area
(``house_styles.TURN_AREA``) it paints, its highlight and its shadow. Each shape is measured too in
each value of its params and each main color, since a new row may sell any of them."""

from __future__ import annotations

import sys
from itertools import product
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import picture_fill_1129 as pf  # noqa: E402

from synthetic_ecommerce_data.domains.retail import (  # noqa: E402
    image_release,
    kit,
    kit_drills,
    scale,
)
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS  # noqa: E402

#: The shape each type of the slice draws: the type, and each param's values.
TYPES: dict[str, tuple[str, dict[str, tuple[str, ...]]]] = {
    "drill_driver": ("Drill Driver", {"pack": ("compact", "standard", "large")}),
    "combi_drill": ("Combi Drill", {"pack": ("compact", "standard", "large")}),
    "hammer_drill": ("Hammer Drill", {"power": ("cordless", "corded")}),
    "corded_drill": ("Corded Drill", {"handle": ("pistol", "side")}),
    "impact_driver": ("Impact Driver", {"batteries": ("0", "1", "2")}),
    "sds_drill": ("SDS Hammer Drill", {"power": ("corded", "cordless")}),
    "tool_kit": ("Tool Kit", {"case": ("case", "bag")}),
    "step_ladder": ("Step Ladder", {"steps": ("2", "3", "4", "5"), "kind": ("stool", "ladder")}),
    "volt_meter": ("Volt Meter", {"form": ("handheld", "clamp")}),
}
FLOOR = 0.50


def _params(shape: str) -> list[dict[str, str]]:
    values = TYPES[shape][1]
    return [dict(zip(values, combo, strict=True)) for combo in product(*values.values())]


def _bad(svg: str) -> pf.Measure | None:
    got = pf.measure(svg, pf.TURN_AREA)
    ok = got.cover >= FLOOR and got.highlight and got.shadow and not got.flat
    return None if ok else got


def test_every_shape_of_the_kit_but_the_bit_set_is_held():
    assert set(TYPES) == set(kit_drills.SHAPES) - {"drill_bit_set"}


@pytest.mark.parametrize("shape", TYPES)
def test_every_sku_fills_half_the_area_with_a_highlight_and_a_shadow(shape):
    short, checked = [], 0
    for rec in scale.templates():
        if rec["drawing"]["shape"] != shape:
            continue
        assert rec["product_type"] == TYPES[shape][0]
        for sku in rec["skus"]:
            checked += 1
            got = _bad(image_release.render(rec, sku, styled=False))
            if got:
                short.append((sku["sku"], got))
    assert checked >= 9, (shape, checked)
    assert short == [], f"{len(short)} of {checked} {shape} SKUs: {short[:3]}"


@pytest.mark.parametrize("shape", TYPES)
def test_every_param_and_main_color_fills_half_the_area_with_a_highlight_and_a_shadow(shape):
    short = []
    for params, (name, color) in product(_params(shape), MAIN_COLORS.items()):
        got = _bad(kit.render(shape, kit.Fill("solid", color, "#333333"), params=params))
        if got:
            short.append((params, name, got))
    assert short == [], short[:3]


@pytest.mark.parametrize("shape", TYPES)
def test_the_drawing_stays_inside_the_product_area(shape):
    from synthetic_ecommerce_data.domains.retail import sheet_extent

    x0, y0, x1, y1 = pf.TURN_AREA
    for params in _params(shape):
        draw = kit.shapes()[shape]
        body = "".join(draw("#d9342b", kit.Fill("solid", "#d9342b"), None, **params))
        a0, b0, a1, b1 = sheet_extent.reach(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{body}</svg>'
        )
        assert (x0 <= a0, y0 <= b0, a1 <= x1, b1 <= y1) == (True,) * 4, (params, a0, b0, a1, b1)
