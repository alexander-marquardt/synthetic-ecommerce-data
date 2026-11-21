"""Each produce SKU's served picture draws its own pack, big (gen#1111, slices 2 and 5).

A grocery line's drawing is made from its first pack, and before slice 2 every other SKU kept it:
a Single lemon drew a pile of 3, a 1 kg bag drew the Single's 3 loose fruit, and a 4 pack lay
loose instead of netted. ``pack_scale`` then set a Single's count of 1 against 1 kg's 1000 g and
shrank it to its 0.6 floor. Each SKU now draws its own pack (Single: one loose fruit, a 4 pack: 4
in a net, a weight: a bag of as many as it holds), and a pile takes no ``pack_scale`` factor: the
count drawn already shows the size. Fill is the share of the plain sheet's product area
(``TURN_AREA``) the fruits paint in ``image_release.render``'s own SVG, as slice 1 measures it.

A line of small fruit sells weights that each hold more than 7 fruits (250 g of grapes is about
50), so before slice 5 its 250g, 500g and 1kg each drew one identical 7-fruit bag. A line's
weights are now counted together (``kit_produce.weight_counts``): the largest draws its own count
and each smaller weight draws fewer, so each weight is its own heap.
"""

from __future__ import annotations

import functools
import re
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
def _build() -> tuple[dict, ...]:
    return tuple(grocery.build(400))


@functools.cache
def _lines() -> dict[str, dict]:
    """Each named family's first line in a small grocery build."""
    out: dict[str, dict] = {}
    for rec in _build():
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


def _want_form(pack_size: str) -> str:
    """The form the issue asks a pack drawn in: a Single loose, a count ("4 pack") netted, a
    weight ("1kg", "500g") bagged. Written here, not read from the code under test."""
    if pack_size == "Single":
        return "loose"
    if re.fullmatch(r"\d+ pack", pack_size):
        return "net"
    assert re.fullmatch(r"\d+(?:\.\d+)?k?g", pack_size), pack_size
    return "bag"


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
            _want_form(size),
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


#: The small-fruit lines whose every weight holds 7 or more fruits (gen#1111, slice 5).
SMALL = ("GRP", "BLK", "CHY", "CAR")


def _weights(rec: dict) -> list[dict]:
    return [sku for sku in rec["skus"] if _want_form(sku["pack_size"]) == "bag"]


@pytest.mark.parametrize("code", SMALL)
def test_each_weight_of_a_small_fruit_line_draws_its_own_heap(code: str) -> None:
    recs = [
        rec
        for rec in _build()
        if rec["product_id"].split("-")[1] == code and rec["drawing"]["shape"] == "produce_pile"
    ]
    assert any(len(_weights(rec)) > 1 for rec in recs), f"{code}: no line sells two weights"
    for rec in recs:
        drawn = {}
        for sku in sorted(_weights(rec), key=lambda s: s["net_weight_g"]):
            svg = _served(rec, sku)
            got = _fill(svg)
            assert got >= FLOOR, f"{sku['sku']} {sku['pack_size']}: {got:.0%} of the product area"
            drawn[sku["pack_size"]] = (svg.count('class="fruit"'), svg)
        counts = [n for n, _ in drawn.values()]
        pictures = len({svg for _, svg in drawn.values()})
        assert pictures == len(drawn), f"{rec['product_id']}: {pictures} picture(s) for {counts}"
        assert counts == sorted(set(counts)), f"{rec['product_id']}: a larger weight, more fruits"
        assert all(kit_produce.MIN_FRUIT <= n <= kit_produce.MAX_FRUIT for n in counts), counts


@pytest.mark.parametrize(
    ("fruit", "grams", "want"),
    [
        ("grape", (250, 500, 1000), (3, 5, 7)),  # each 7 or more fruits: two fewer per halving
        ("carrot", (500, 1000), (5, 7)),  # 500 g is 7 carrots: it steps down as well
        ("cherry", (250, 400, 500), (5, 6, 7)),  # and one fewer at least than the next size up
        ("onion", (500, 1000), (3, 7)),  # counts that already differ stay each weight's own
        ("potato", (1000, 2000), (6, 7)),
        ("lemon", (1000,), (7,)),  # a line of one weight draws its own count
    ],
)
def test_a_lines_weights_are_counted_together(
    fruit: str, grams: tuple[int, ...], want: tuple[int, ...]
) -> None:
    got = kit_produce.weight_counts(fruit, grams)
    assert tuple(got[g] for g in grams) == want
