"""A set or pack of N draws N, or prints N on its image (gen#728, the 2026-11-04 scan).

The maintainer saw a "Set of 4" espresso cup set drawn with 8 cups ("that looks pretty bad if
the set of 4 shows 8"), and the scan that followed found 61 product types whose title states a
count. The issue's Done-when, one test each:

2. a discrete-item set (a screwdriver set, a set of chopping boards, a dinosaur figure set, a
   drill bit case) draws exactly N, read from the record; above 24 the count is printed;
3. a piece set whose drawing shows its parts rather than N items (a dinner set, a cutlery set, a
   tool kit) carries its count printed on the image;
4. every (type, title N, SKU count) of the ceiling build is rendered once, and the count it
   draws must be the title's.

The table of 1. is ``pack_counts.table``, quoted in ``docs/retail-prototype/pack-copies-728.md``.
"""

from __future__ import annotations

import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import kit, pack_copies, pack_counts
from synthetic_ecommerce_data.domains.retail.kit_drills import BIT_CLASS


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


@pytest.fixture(scope="module")
def rows(ceiling):
    return pack_counts.rows(ceiling.records)


def test_every_counted_title_draws_its_count(rows):
    """Guard (gen#728): a set of 4 drew 8, a screwdriver set of 6 drew one screwdriver. Metric:
    rows of the ceiling build, one SKU per (type, title N, SKU count), whose image draws another
    count than the title states, by copies laid out, the outer box, the shape's own count or the
    count printed on it."""
    assert len(rows) > 100
    wrong = [
        (r.product_type, r.title_n, r.drawn, r.how, r.title) for r in rows if r.drawn != r.title_n
    ]
    assert wrong == [], wrong[:8]


def test_a_count_above_24_is_printed_or_boxed(rows):
    """Guard (gen#728): past 24 items a shopper cannot count them (a 1000 piece puzzle's grid).
    Metric: rows above :data:`pack_copies.MOST_DRAWN` drawn neither printed nor as the outer box."""
    big = [r for r in rows if r.title_n > pack_copies.MOST_DRAWN]
    assert big
    assert [(r.title, r.how) for r in big if r.how not in ("printed", "outer box")] == []


#: The types whose count is printed, the table's named mismatches (Done-when 3): their drawing
#: shows the set's parts, or more than 24 items.
PRINTED = {
    "Arts and Crafts Kit",
    "Cutlery Set",
    "Dinner Set",
    "Drill Bit Set",
    "Jigsaw Puzzle",
    "Socket Set",
    "Tool Kit",
}


def test_the_printed_types_are_the_named_ones(rows):
    """Guard (gen#728): a drawing that shows its count (a knife block's five knives and the block,
    a single pair of socks) should not carry a tag as well. Metric: the types with a printed row."""
    assert {r.product_type for r in rows if r.how == "printed"} == PRINTED


def test_laid_out_copies_are_the_count_drawn(rows):
    """Guard (gen#728): the count read off an image is the copies it really draws. Metric: rows
    laid out as copies whose ``pack-copy`` uses are not their count."""
    copied = [r for r in rows if r.how == "copies"]
    assert {"Screwdriver Set", "Chopping Board", "Toy Figure"} <= {r.product_type for r in copied}
    assert [(r.title, r.uses, r.drawn) for r in copied if r.uses != r.drawn] == []


@pytest.mark.parametrize("product_type", ["Dinner Set", "Cutlery Set", "Socket Set", "Tool Kit"])
def test_a_piece_set_not_drawn_item_by_item_prints_its_count(rows, product_type):
    """Guard (gen#728): a socket set of 94 drew a plain box. Metric: each row of the type is
    ``printed`` and its image carries the count in the tag's text."""
    typed = [r for r in rows if r.product_type == product_type]
    assert typed
    assert {r.how for r in typed} == {"printed"}, [(r.title, r.how) for r in typed]


def test_the_count_tag_prints_its_number():
    """Guard (gen#728): the tag carries the count a shopper reads. Metric: its text."""
    tag = pack_copies.count_tag(94)
    assert 'data-count="94"' in tag
    assert re.search(r">94<", tag), tag
    assert re.search(r">pieces<", tag), tag


@pytest.mark.parametrize("bits", [3, 13, 18, 23])
def test_a_drill_bit_case_draws_every_bit_up_to_23(bits):
    """Guard (gen#728): a 19 piece wood set (18 bits and the case) drew 9 bits, and the shape
    stopped at 13. Metric: the bits drawn."""
    svg = kit.render("drill_bit_set", kit.Fill("solid", "#2a4d8f", "#333333", "#f2d14b"),
                     params={"shank": "round", "bits": str(bits)})  # fmt: skip
    assert svg.count(f'class="{BIT_CLASS}"') == bits


def test_each_drill_bit_set_names_its_bits_from_its_contents(ceiling):
    """Guard (gen#728): ``bits`` was typed by hand beside the contents and disagreed (9 of 18).
    Metric: each set's ``bits`` against its title's pieces less the case."""
    sets = [r for r in ceiling.records if r["drawing"]["shape"] == "drill_bit_set"]
    assert sets
    wrong = [
        (r["title"], r["drawing"]["params"]["bits"])
        for r in sets
        if pack_copies.title_count(r["title"])
        not in (None, int(r["drawing"]["params"]["bits"]) + 1)
    ]
    assert wrong == []
