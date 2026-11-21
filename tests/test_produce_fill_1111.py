"""The produce kit fills its picture with round, fresh fruit (gen#1111, slices 1 and 3).

Before gen#1111, a pile of fruit was drawn at each fruit's small table size inside a layout
made for up to seven, so three lemons covered about a tenth of the picture and read as flat
blobs. Fill here is the share of the product area the house style frames (``TURN_AREA``, the
plain sheet's 344 x 334 box) that the fruits themselves paint, measured by :mod:`sheet_cover`;
the ground shadow, a bag's film, a net and a tag are not counted. A banana, carrot or cherry
pile is a hand, a bunch or a heap, so it fills the area as a round fruit's pile does.
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import kit, kit_produce, sheet_cover, sheet_extent
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


#: A banana, a carrot or a pair of cherries is long or thin. A pile of 3 or more is drawn in its
#: own arrangement (a hand, a bunch, a heap) and holds ``FLOOR`` (gen#1111, slice 3); one or two
#: alone (a Single banana) cannot fill a square and hold this lower floor, which the
#: pre-gen#1111 drawings (about 0.1) did not meet.
LONG = {"banana", "carrot", "cherries"}
LONG_FLOOR = 0.25


#: The shapes drawn as one round body, which a pack of one or two shows (a lemon, an onion).
ROUND = {"orange", "lemon", "apple", "tomato", "onion", "potato"}


def _counts(fruit: str) -> range:
    """The counts a fruit is held to: 1-7 for a round body or a long fruit, else from 3."""
    fewest = 1 if kit_produce.FRUIT[fruit][0] in ROUND | LONG else kit_produce.MIN_FRUIT
    return range(fewest, kit_produce.MAX_FRUIT + 1)


def _floor(fruit: str, count: int) -> float:
    alone = kit_produce.FRUIT[fruit][0] in LONG and count < kit_produce.MIN_FRUIT
    return LONG_FLOOR if alone else FLOOR


@pytest.mark.parametrize("pack", kit_produce.PACKS)
def test_every_pile_fills_half_its_product_area(pack: str) -> None:
    under = {
        (fruit, count): round(share, 3)
        for fruit in kit_produce.FRUIT
        for count in _counts(fruit)
        if (share := _fill(_pile(fruit, count, pack))) < _floor(fruit, count)
    }
    floors = f"{FLOOR:.0%}, one or two long fruits {LONG_FLOOR:.0%}"
    assert not under, f"{pack}: under its floor ({floors}): {under}"


#: Fruit -> (the point it is held by, its far end, in the shape's own units; the most the held
#: points may spread, as a share of how far the far ends spread). A hand of bananas hangs from
#: one crown, and a bunch of carrots is tied at its tops while its roots fan out.
HELD = {
    "banana": ((119.0, 112.0), (326.0, 290.0), 0.25),
    "carrot": ((200.0, 124.0), (200.0, 348.0), 0.75),
}


def _ends(svg: str, point: tuple[float, float]) -> list[tuple[float, float]]:
    """Where ``point`` of each fruit's own shape lands on the sheet."""
    root = ET.fromstring(svg)
    return [
        sheet_extent._apply(sheet_extent._transform(el.get("transform")), point)
        for el in root
        if el.get("class") == "fruit"
    ]


def _span(points: list[tuple[float, float]]) -> float:
    return max(math.dist(p, q) for p in points for q in points)


@pytest.mark.parametrize("fruit", sorted(HELD))
def test_a_hand_hangs_from_one_crown_and_a_bunch_is_tied_at_its_tops(fruit: str) -> None:
    held, far, share = HELD[fruit]
    for count in range(kit_produce.MIN_FRUIT, kit_produce.MAX_FRUIT + 1):
        svg = _pile(fruit, count, "loose")
        crowns, ends = _span(_ends(svg, held)), _span(_ends(svg, far))
        assert crowns <= share * ends, (fruit, count, round(crowns), round(ends))


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
