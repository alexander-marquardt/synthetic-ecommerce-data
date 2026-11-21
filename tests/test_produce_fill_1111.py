"""The produce kit fills its picture with round, fresh fruit (gen#1111, slices 1, 3 and 4).

Before gen#1111, a pile of fruit was drawn at each fruit's small table size inside a layout
made for up to seven, so three lemons covered about a tenth of the picture and read as flat
blobs. Fill here is the share of the product area the house style frames (``TURN_AREA``, the
plain sheet's 344 x 334 box) that the fruits themselves paint, measured by :mod:`sheet_cover`;
the ground shadow, a bag's film, a net and a tag are not counted. A banana, carrot or cherry
pile is a hand, a bunch or a heap, so it fills the area as a round fruit's pile does. A punnet
shows a heap of produce through its clear tray, and a fruit or vegetable motif drawn alone fills
the area as a Single fruit does (slice 4).
"""

from __future__ import annotations

import math
import re
import xml.etree.ElementTree as ET

import pytest

from synthetic_ecommerce_data.domains.retail import (
    kit,
    kit_motifs,
    kit_produce,
    kit_punnet,
    sheet_cover,
    sheet_extent,
)
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


def _sheet(parts: list[str]) -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400">{"".join(parts)}</svg>'


def _cover(elements: list[ET.Element]) -> float:
    inner = "".join(ET.tostring(el, encoding="unicode") for el in elements)
    svg = f'<svg xmlns="http://www.w3.org/2000/svg">{inner}</svg>'
    return sheet_cover.cover(svg, TURN_AREA, step=4.0)


#: The fruit and vegetable motifs: each is drawn alone as a product too (a strawberry plant's
#: picture, a growing kit's mushroom), so one fills the product area as a Single fruit does.
MOTIFS = sorted(m for m, c in kit_motifs.CATEGORY.items() if c in {"fruit", "vegetables"})
#: A carrot alone is long and thin, as one or two long fruits in a pile are, so it holds
#: ``LONG_FLOOR``; before slice 4 of gen#1111 it covered 0.12.
LONG_MOTIFS = {"carrot"}


@pytest.mark.parametrize("motif", MOTIFS)
def test_every_fruit_and_vegetable_motif_fills_half_its_product_area(motif: str) -> None:
    fill = Fill("solid", BASE, "#ffffff")
    share = sheet_cover.cover(_sheet(kit.SHAPES[motif](BASE, fill, None)), TURN_AREA, step=4.0)
    floor = LONG_FLOOR if motif in LONG_MOTIFS else FLOOR
    assert share >= floor, (motif, round(share, 3), floor)


@pytest.mark.parametrize("produce", sorted(kit_punnet.PRODUCE))
def test_every_punnet_shows_produce_over_half_its_product_area(produce: str) -> None:
    """The produce a punnet shows: what its ``fruit`` items paint, less what the opaque label band
    hides. The tray is clear film, so nothing else drawn over the produce hides it."""
    fill = Fill("solid", "#2f6b3c", "#ffffff")
    root = ET.fromstring(_sheet(kit.SHAPES["punnet"]("#2f6b3c", fill, "Veg", produce=produce)))
    items = list(root)
    fruit = [el for el in items if el.get("class") == "fruit"]
    label = [el for el in items if el.get("class") == "label"]
    shown = _cover(fruit + label) - _cover(label)
    assert shown >= FLOOR, (produce, round(shown, 3))
    over = items[items.index(fruit[0]) :]
    opaque = [
        el.get("d", el.tag)[:40]
        for el in over
        if el.get("class") not in {"fruit", "label"}
        and el.get("fill", "none") != "none"
        and float(el.get("fill-opacity", "1")) >= 1
    ]
    assert not opaque, (produce, opaque)


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
