"""A retail product is drawn as its own kind, and labeled with its own noun.

Alex's report: "Lemon Rim Block, Twin Pack" (Toilet Cleaner) was a yellow drinking cup
(the ``tub`` shape) whose label read "Toilet", a fragment of its category. At the ceiling
build (seed 0, at the time), these four faults sat in the drawings:

* every toilet cleaner drew as a ``tub`` or a plain ``bottle`` and said "Toilet";
* five drinking vessels (two mugs, a tumbler, a cup, a travel cup) drew as a ``tin``;
* a ``tub`` carried a cleaner that is not a tub of anything;
* 43 (type, label) pairs named something other than the title's product noun.

The first three are fixed here; :data:`LABEL_DEBT` lists the label pairs still owed, and
the ratchet below fails when a pair is paid but left listed, or a new one appears.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
sys.path.insert(0, str(RETAIL))

import kit  # noqa: E402
import scale  # noqa: E402

#: The scale build that exhausts every template (``tests/test_retail_scale.py`` CAPACITY).
CEILING_SKUS = 76_417 * 2

#: Titles whose product really is a tub (a pot of tablets, wipes, beads, a drink powder).
TUB_NOUNS = re.compile(r"\b(Wipes|Tablets|Pods|Capsules|Beads|Chocolate|Yogurt|Pot)\b")
VESSEL = re.compile(r"\b(Mug|Mugs|Cup|Cups|Tumbler|Travel Cup)\b")
CUT = re.compile(r",|\d| for | with | of | in | to ")

#: (product type, label) pairs whose label is not the title's product noun yet.
LABEL_DEBT: frozenset[tuple[str, str]] = frozenset({
        ("Air Freshener", "Diffuser"),
        ("Air Freshener", "Gel"),
        ("Air Freshener", "Reeds"),
        ("Cake", "Lemon"),
        ("Car Boot Organiser", "Boot Tidy"),
        ("Chutney", "Chutney"),
        ("Coffee", "Coffee"),
        ("Cushion", "Bolster"),
        ("Duvet", "10.5 Tog"),
        ("Duvet", "13.5 Tog"),
        ("Fabric Softener", "Softener"),
        ("Foundation", "Serum"),
        ("Gift Bag", "Small"),
        ("Gift Set", "Bath"),
        ("Gift Set", "Glow"),
        ("Gift Set", "Hair"),
        ("Gift Set", "Lip"),
        ("Gift Set", "Skin"),
        ("Gift Set", "Summer"),
        ("Jam", "Jam"),
        ("Letterbox Gift", "Brownies"),
        ("Letterbox Gift", "Tea"),
        ("Make-Up Bag", "Top Gift"),
        ("Moisturiser", "SPF 20"),
        ("Olive Oil", "Olive Oil"),
        ("Plant", "Apple"),
        ("Plant", "Bay"),
        ("Plant", "Olive"),
        ("Safety Boots", "S3"),
        ("Scented Candle", "Candle"),
        ("Shoe Care Kit", "Polish"),
        ("Shower Gel", "Lemon"),
        ("Tea", "Tea"),
        ("Toy Vehicle", "Fire"),
        ("Toy Vehicle", "Tow"),
        ("Travel Set", "Travel"),
        ("Wash Bag", "Wash"),
})


@pytest.fixture(scope="module")
def records() -> list[dict[str, Any]]:
    """Every style, grocery included: the one catalog is drawn by the one set of honesty rules."""
    return scale.build(CEILING_SKUS).records


def _noun(title: str) -> str:
    head = CUT.split(title)[0].split()
    return head[-1].lower().rstrip("s") if head else ""


def _label_pairs(records: list[dict[str, Any]]) -> set[tuple[str, str]]:
    return {
        (r["product_type"], r["drawing"]["label"])
        for r in records
        if r["drawing"].get("label")
        and r["drawing"]["label"].split()[-1].lower().rstrip("s") != _noun(r["title"])
    }


def test_every_drawn_shape_is_registered(records):
    unknown = sorted({r["drawing"]["shape"] for r in records} - set(kit.SHAPES))
    assert unknown == []


def _expected_loo_shape(title: str) -> str:
    if "Block" in title:
        return "rim_block"
    return "tub" if "Tablets" in title else "angled_bottle"


def test_a_toilet_cleaner_is_not_drawn_as_a_cup(records):
    loo = [r for r in records if r["product_type"] == "Toilet Cleaner"]
    wrong = [
        f"{r['title']!r}: {r['drawing']['shape']} labeled {r['drawing']['label']!r}"
        for r in loo
        if r["drawing"]["shape"] != _expected_loo_shape(r["title"])
    ]
    assert len(loo) == 20
    assert wrong == []


def test_a_twin_pack_rim_block_draws_two_units_and_says_rim_block(records):
    blocks = [r for r in records if "Rim Block" in r["title"]]
    assert len(blocks) == 4
    for r in blocks:
        drawing = r["drawing"]
        assert drawing["label"] == "Rim Block", r["title"]
        assert drawing.get("params") == {"units": "2"}, r["title"]
    drawing = blocks[0]["drawing"]
    fill = kit.Fill("solid", drawing["base"], drawing["accent"], drawing["third"])
    svg = kit.render(drawing["shape"], fill, drawing["label"], params=drawing["params"])
    assert svg.count(">Rim Block<") == 2


def test_a_tub_is_only_a_tub_of_something(records):
    wrong = [
        f"{r['title']!r} ({r['product_type']})"
        for r in records
        if r["drawing"]["shape"] == "tub" and not TUB_NOUNS.search(r["title"])
    ]
    assert wrong == []


#: The home mug and the Gifts mug (gen#425: a tapered body with a design on its side).
MUG_SHAPES = {"mug", "gift_mug"}


def test_a_drinking_vessel_is_drawn_as_a_mug(records):
    wrong = [
        f"{r['title']!r}: {r['drawing']['shape']}"
        for r in records
        if r["product_type"] in {"Mug", "Tumbler", "Cup", "Travel Cup", "Cup Set"}
        and r["drawing"]["shape"] not in MUG_SHAPES
    ]
    assert wrong == []


def test_a_label_is_the_titles_product_noun_not_a_category_fragment(records):
    owed = _label_pairs(records)
    assert sorted(owed - LABEL_DEBT) == [], "a label that is not the title's noun"
    assert sorted(LABEL_DEBT - owed) == [], "paid off: remove it from LABEL_DEBT"


#: Shapes that draw something to drink from, never a bottle of cleaner.
DRINKWARE = frozenset({"mug", "tumbler", "cup", "travel_cup", "glass"})


def test_a_cleaner_is_not_drawn_as_drinkware_and_no_label_is_a_path_segment(records):
    """The cleaning family (#151): never drinkware, and labeled by its noun."""
    cleaning = [r for r in records if r["category_path"][0] == "Cleaning"]
    assert len(cleaning) > 400
    drinkware = [
        f"{r['title']!r}: {r['drawing']['shape']}"
        for r in cleaning
        if r["drawing"]["shape"] in DRINKWARE
    ]
    fragments = [
        f"{r['title']!r}: {r['drawing']['label']!r} in {r['category_path']}"
        for r in cleaning
        if r["drawing"].get("label") in r["category_path"]
        # a label equal to the whole leaf is the product's own noun only when the title says it
        and r["drawing"]["label"].split()[-1].lower().rstrip("s") != _noun(r["title"])
    ]
    assert drinkware == []
    assert fragments == []
