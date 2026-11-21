"""The produce kit fills its picture with round, fresh fruit (gen#1111, slice 1).

Before gen#1111, a pile of fruit was drawn at each fruit's small table size inside a layout
made for up to seven, so three lemons covered about a tenth of the picture and read as flat
blobs. Fill here is the share of the product area the house style frames (``TURN_AREA``, the
plain sheet's 344 x 334 box) that the fruits themselves paint, measured by :mod:`sheet_cover`;
the ground shadow, a bag's film, a net and a tag are not counted.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import kit, kit_produce, sheet_cover
from synthetic_ecommerce_data.domains.retail.house_styles import TURN_AREA
from synthetic_ecommerce_data.domains.retail.kit import Fill

FLOOR = 0.5
BASE = "#f2e04b"


def _pile(fruit: str, count: int, pack: str) -> str:
    fill = Fill("solid", BASE, "#ffffff")
    parts = kit.SHAPES["produce_pile"](
        BASE, fill, "Lemons", fruit=fruit, count=count, seed=f"T-{fruit}-{count}", pack=pack
    )
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{"".join(parts)}</svg>'


def _fill(svg: str) -> float:
    """The fruits' own share of the product area: a bag's film, a net and a tag do not count,
    so a bag of tiny fruit does not pass on the bag alone."""
    root = ET.fromstring(svg)
    fruits = [ET.tostring(el, encoding="unicode") for el in root if el.get("class") == "fruit"]
    alone = f'<svg xmlns="http://www.w3.org/2000/svg">{"".join(fruits)}</svg>'
    return sheet_cover.cover(alone, TURN_AREA, step=4.0)


def test_the_kit_lays_out_one_to_seven_fruits() -> None:
    assert sorted(kit_produce.PILES) == list(range(1, 8))


@pytest.mark.parametrize("pack", kit_produce.PACKS)
def test_every_pile_fills_half_its_product_area(pack: str) -> None:
    under = {
        (fruit, count): round(share, 3)
        for fruit in kit_produce.FRUIT
        for count in sorted(kit_produce.PILES)
        if (share := _fill(_pile(fruit, count, pack))) < FLOOR
    }
    assert not under, f"{pack}: under {FLOOR:.0%} of the product area: {under}"


def test_every_fruit_is_glossed_and_the_pile_stands_on_a_shadow() -> None:
    for fruit in kit_produce.FRUIT:
        svg = _pile(fruit, 3, "loose")
        fruits = re.findall(r'<g class="fruit".*?</g>', svg)
        assert len(fruits) == 3, fruit
        assert all("url(#gloss-" in g for g in fruits), fruit  # a highlight and a shade on each
        assert 'class="ground"' in svg, fruit


def test_sheet_cover_measures_a_circle_and_its_clip() -> None:
    svg = '<svg xmlns="http://www.w3.org/2000/svg">{}</svg>'
    circle = svg.format('<circle cx="200" cy="200" r="100" fill="red"/>')
    assert sheet_cover.cover(circle, (0, 0, 400, 400)) == pytest.approx(3.1416 / 16, abs=0.003)
    clipped = svg.format(
        '<clipPath id="c"><rect x="0" y="0" width="200" height="400"/></clipPath>'
        '<circle cx="200" cy="200" r="100" fill="red" clip-path="url(#c)"/>'
        '<path d="M0,0 L400,0" fill="none" stroke="black"/>'
    )
    assert sheet_cover.cover(clipped, (0, 0, 400, 400)) == pytest.approx(3.1416 / 32, abs=0.003)
