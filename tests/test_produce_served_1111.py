"""Each produce SKU's served picture draws its own pack, big (gen#1111, slice 2).

A grocery line's drawing is made from its first pack, and before slice 2 every other SKU kept it:
a Single lemon drew a pile of 3, a 1 kg bag drew the Single's 3 loose fruit, and a 4 pack lay
loose instead of netted. ``pack_scale`` then set a Single's count of 1 against 1 kg's 1000 g and
shrank it to its 0.6 floor. Each SKU now draws its own pack (Single: one loose fruit, a 4 pack: 4
in a net, a weight: a bag of as many as it holds), and a pile takes no ``pack_scale`` factor: the
count drawn already shows the size. Fill is the share of the plain sheet's product area
(``TURN_AREA``) the fruits paint in ``image_release.render``'s own SVG, as slice 1 measures it.
"""

from __future__ import annotations

import functools
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    distractors,
    export,
    grocery,
    image_release,
    kit_produce,
    pack_scale,
    sheet_cover,
)
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA

FLOOR = 0.5
#: The lines the maintainer's report named (lemons) and the ones he expects to match.
LINES = ("LEM", "ORA", "APP", "ONI")
DRAWN = ("path", "rect", "circle", "ellipse")


@functools.cache
def _lines() -> dict[str, dict]:
    """Each named family's first line in a small grocery build."""
    out: dict[str, dict] = {}
    for rec in grocery.build(400):
        code = rec["product_id"].split("-")[1]
        if code in LINES and rec["drawing"]["shape"] == "produce_pile":
            out.setdefault(code, rec)
    assert sorted(out) == sorted(LINES)
    return out


def _fruit_only(svg: str) -> str:
    """``svg`` with every painted shape outside a ``fruit`` group made invisible, so a bag's film,
    a net, a tag or the ground shadow does not count, and every transform around a fruit stays."""
    root = ET.fromstring(svg)

    def hide(el: ET.Element, inside: bool) -> None:
        inside = inside or el.get("class") == "fruit"
        if not inside and el.tag.rsplit("}", 1)[-1] in DRAWN:
            el.set("opacity", "0")
        for child in el:
            hide(child, inside)

    hide(root, False)
    return ET.tostring(root, encoding="unicode")


def _served(rec: dict, sku: dict) -> str:
    return image_release.render(rec, sku, styled=False).decode()


def _fill(svg: str) -> float:
    return sheet_cover.cover(_fruit_only(svg), TURN_AREA, step=4.0)


def _form(svg: str) -> str:
    if 'clipPath id="net-' in svg:
        return "net"
    return "bag" if 'fill-opacity=".55"' in svg else "loose"


@pytest.mark.parametrize("code", LINES)
def test_each_pack_of_a_line_draws_its_own_count_and_form(code: str) -> None:
    rec = _lines()[code]
    drawn = {}
    for sku in rec["skus"]:
        svg = _served(rec, sku)
        drawn[sku["pack_size"]] = (svg.count('class="fruit"'), _form(svg))
    want = {
        size: (
            1 if size == "Single" else int(size.split()[0]) if size.endswith("pack") else None,
            kit_produce.pack_form(size),
        )
        for size in drawn
    }
    for size, (n, form) in drawn.items():
        assert form == want[size][1], (code, size, drawn)
        if want[size][0] is not None:
            assert n == want[size][0], (code, size, drawn)
        else:  # a weight: a bag of at least the fewest a pile draws
            assert kit_produce.MIN_FRUIT <= n <= kit_produce.MAX_FRUIT, (code, size, drawn)
    assert len(set(drawn.values())) == len(drawn), (code, drawn)
    counts = {n for n, _ in drawn.values()}
    assert len(counts) == len(drawn), f"{code}: each pack draws a different count: {drawn}"


@pytest.mark.parametrize("code", LINES)
def test_no_pile_of_fruit_is_shrunk_by_its_pack(code: str) -> None:
    rec = _lines()[code]
    for sku in rec["skus"]:
        assert pack_scale.factor(rec, sku) is None, (code, sku["pack_size"])
        assert "pack_scale" not in export.drawing_spec(rec, sku), (code, sku["pack_size"])


def _served_cases() -> list[tuple[str, int]]:
    return [(code, i) for code in LINES for i in range(3)]


@pytest.mark.parametrize(("code", "i"), _served_cases())
def test_every_served_pack_fills_half_its_product_area(code: str, i: int) -> None:
    rec = _lines()[code]
    if i >= len(rec["skus"]):
        pytest.skip(f"{code} sells {len(rec['skus'])} packs")
    sku = rec["skus"][i]
    got = _fill(_served(rec, sku))
    assert got >= FLOOR, f"{sku['sku']} {sku['pack_size']}: {got:.0%} of the product area"


def test_the_bag_of_lemons_keeps_its_four_and_fills_half() -> None:
    rec = distractors.LEMONS
    sku = rec["skus"][0]
    svg = _served(rec, sku)
    assert svg.count('class="fruit"') == distractors.LEMON_PACK
    assert _form(svg) == "bag"
    assert _fill(svg) >= FLOOR
