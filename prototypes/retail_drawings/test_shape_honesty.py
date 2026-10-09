"""Every product is drawn as its own kind, never as a generic stand-in outside its categories.

The shape audit of the 179-product preview found 36 products drawn with a
generic or borrowed shape: rose bouquets as fruit (``round_produce``), socks
and wallets as a ``box``, beds as ``box_wide``, table lamps as a ``box``
although ``table_lamp`` exists. A generic shape is honest for a few
categories only (packaged food in a box, a storage organiser as a wide box).
:data:`HONEST_FOR` is that allow-list; a sample that uses a generic shape
outside it fails, and the failure names the row. A new product kind gets its
own shape (``kit_more.py`` holds the ones the audit asked for).
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import build_preview4 as bp4  # noqa: E402
import kit  # noqa: E402
import kit_more  # noqa: E402,F401 -- registers the shapes below

#: Generic shape -> the category paths (``" > "`` joined, matched as a
#: prefix) where it draws the product honestly.
HONEST_FOR: dict[str, tuple[str, ...]] = {
    "box": ("Food & Drink",),
    # A storage organiser is a fabric box with compartments, so a wide box is its kind.
    # A boxed food gift sits at the food node nearest its contents (one food tree).
    "box_wide": (
        "Food & Drink > Chocolate & Sweets > Chocolate Boxes",
        "Food & Drink > Bakery > Cakes",
        "Food & Drink > Drinks > Tea",
        "Home > Storage",
    ),
    # Still generic, honest nowhere now: loose fruit draws as its own
    # ``produce_pile`` (kit_produce.py), so any round_produce use fails.
    "round_produce": (),
    "pouch": (
        "Beauty > Accessories",
        "Beauty > Gift Sets > Make-Up Gift Sets",
        "Beauty > Mother & Baby > Hospital Bags",
        "Beauty > Suncare > Summer Sets",
        "Beauty > Travel & Minis",
    ),
    "top": (
        "Men > Tops",
        "Women > Tops > T-Shirts",
        "Women > Tops > Jersey Tops",
        "Women > Tops > Long Sleeve Tops",
        "Women > Knitwear > Jumpers",
    ),
    # A kind's own shape lent to a neighbour the audit also caught.
    "cake": ("Food & Drink > Bakery > Cakes",),
    "gift_bag": ("Beauty > Gift Sets", "Gifts > Gift Wrap"),
    "moisturiser_jar": ("Beauty > Skincare",),
    "mattress_topper": ("Home > Bedding > Mattress Toppers",),
}

#: The shapes the audit asked for, each drawn in the record's fill.
NEW_SHAPES = (
    "bouquet", "socks", "bed_frame", "watch", "earrings", "compact", "cardigan",
    "bodysuit", "wallet", "keyring", "charging_pad", "chairbed", "mattress",
    "potted_tree", "pudding", "panettone", "trophy",
)  # fmt: skip

SAMPLES = [rec for recs in bp4.samples().values() for rec in recs]


def _path(rec: dict) -> str:
    return " > ".join(rec["category_path"])


def _honest(shape: str, path: str) -> bool:
    return any(path == p or path.startswith(p + " > ") for p in HONEST_FOR[shape])


def test_no_generic_shape_outside_the_categories_where_it_is_honest() -> None:
    offenders = [
        f"{rec['product_id']} {rec['title']!r} ({_path(rec)}) is drawn as {rec['drawing']['shape']}"
        for rec in SAMPLES
        if rec["drawing"]["shape"] in HONEST_FOR
        and not _honest(rec["drawing"]["shape"], _path(rec))
    ]
    assert offenders == []


def test_every_allow_list_entry_is_used_by_a_sample() -> None:
    """The allow-list stays exact: an entry no sample needs is removed, not kept 'just in case'."""
    used = {
        (rec["drawing"]["shape"], p)
        for rec in SAMPLES
        for p in HONEST_FOR.get(rec["drawing"]["shape"], ())
        if _path(rec) == p or _path(rec).startswith(p + " > ")
    }
    unused = [(s, p) for s, ps in HONEST_FOR.items() for p in ps if (s, p) not in used]
    assert unused == []


def test_table_lamps_are_drawn_as_a_table_lamp() -> None:
    lamps = [rec for rec in SAMPLES if rec["category_path"][-1] == "Table Lamps"]
    assert [rec["drawing"]["shape"] for rec in lamps] == ["table_lamp"]


@pytest.mark.parametrize("shape", NEW_SHAPES)
def test_a_new_shape_paints_the_records_color_and_pattern(shape: str) -> None:
    assert shape in kit.SHAPES
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid
    assert "url(#fill-b)" in striped


@pytest.mark.parametrize("shape", NEW_SHAPES)
def test_a_new_shape_is_used_by_a_sample(shape: str) -> None:
    assert shape in {rec["drawing"]["shape"] for rec in SAMPLES}


def test_a_sock_drawing_shows_the_packs_pair_count() -> None:
    socks = [rec for rec in SAMPLES if rec.get("product_type") == "Socks"]
    assert len(socks) == 7
    for rec in socks:
        n = rec["units_per_pack"]
        assert rec["drawing"]["shape"] == "socks", rec["title"]
        assert rec["drawing"].get("params", {}).get("pairs") == str(n), rec["title"]
        svg = bp4.drawing_svg(rec)
        # One pair is two socks; a pack fans one sock per pair under a band naming the count.
        assert svg.count('class="sock"') == (2 if n == 1 else n), rec["title"]
        assert (f"{n} pairs" in svg) == (n > 1), rec["title"]


@pytest.mark.parametrize("stems", [5, 7, 9])
def test_a_bouquet_draws_its_stem_count_with_its_foliage(stems: int) -> None:
    assert "bouquet" in kit.SHAPES
    svg = kit.render(
        "bouquet", kit.Fill("solid", "#b0182f"), params={"stems": str(stems), "foliage": "#d4af37"}
    )
    assert svg.count('class="bloom"') == stems
    assert len(re.findall(r'class="leaf" fill="#d4af37"', svg)) >= 4


def test_bouquet_records_carry_their_foliage() -> None:
    """A bouquet's foliage color comes from its record: gold eucalyptus is drawn gold."""
    foliage = {
        rec["title"]: rec["drawing"].get("params", {}).get("foliage")
        for rec in SAMPLES
        if rec["category_path"][-1] == "Bouquets"
    }
    assert foliage == {
        "Orange Rose Bouquet": None,
        "Blush Rose & Gold Eucalyptus Bouquet": "#d4af37",
        "Classic Red Rose Bouquet": None,
        "White Rose Bouquet with Gold Foliage": "#d4af37",
    }


def test_round_produce_stays_registered_as_honest_nowhere() -> None:
    """Without its empty entry a round_produce use would pass unchecked."""
    assert HONEST_FOR["round_produce"] == ()
    assert not _honest("round_produce", "Food > Fruit & Veg > Fruit")
