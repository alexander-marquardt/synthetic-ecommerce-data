"""Lingerie titles that carry the plural "cups" (gen#508).

A bare ``cups`` names drinkware in Home and a garment part in Lingerie. On a real retail site the
first page of ``cups`` is bras, because their titles say "with Removable Cups" or "Moulded Cups".
The catalogue's bras said "Cup" in the singular only ("Full Cup Bra"), so the demo could not show
the lingerie half of the class. Twenty-one EXISTING rows are retitled (17 bras, 2 swimsuits and 2
bikini tops; the generator is frozen, so no style is added), and each states the cups it names as
an attribute. The floors are written out here, not read from the rows, so dropping rows fails this
file; the swimwear floors are two because only four swimwear rows state ``padded`` Yes.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import facet_leaves  # noqa: E402
import scale  # noqa: E402

#: The plural a bare "cups" matches in a lingerie title.
CUPS_TITLE = re.compile(r"\b(Removable|Padded|Moulded|Spacer) Cups\b")
#: The words of drinkware: a lingerie row that used one would be a decoy of the sibling queries.
DRINKWARE = re.compile(r"\b(mugs?|espresso|tumblers?|saucers?|teacups?|coffee|tea)\b", re.I)


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    return [r for r in scale.templates() if CUPS_TITLE.search(r["title"])]


def _vals(doc: dict, key: str) -> set[str]:
    return {str(e["value"]) for e in doc["attributes"] if e["key"] == key}


def test_the_catalog_holds_twenty_titles_that_name_their_cups_in_the_plural(rows):
    assert len({r["title"] for r in rows}) >= 20, len(rows)


def test_the_plural_cups_titles_are_existing_rows_not_new_styles():
    """The generator is frozen (166,990 SKUs final): a title change adds no style."""
    assert not (RETAIL / "cups_plural_rows.py").exists()


@pytest.mark.parametrize(
    ("kind", "floor"),
    [("Bralette", 2), ("Sports Bra", 3), ("T-Shirt Bra", 4), ("Swimsuit", 2), ("Bikini Top", 2)],
)
def test_each_lingerie_type_the_issue_names_has_a_floor_of_titles_with_cups(rows, kind, floor):
    named = [r for r in rows if kind in r["title"] or r["product_type"] == kind]
    assert len(named) >= floor, [r["title"] for r in rows]


def test_every_title_with_cups_is_lingerie_or_swimwear(rows):
    assert rows
    for r in rows:
        assert r["department"][0] in ("Lingerie & Nightwear", "Clothing"), r["title"]
        assert r["category_path"][1] in ("Lingerie", "Swimwear"), r["title"]


def test_every_title_with_removable_padded_or_moulded_cups_states_them_as_an_attribute(rows):
    assert rows
    for rec in rows:
        doc = export.standard_document(rec)
        cups = CUPS_TITLE.search(rec["title"]).group(1)
        if rec["product_type"] == "Bra":
            want = {"Removable": "Removable Cups", "Padded": "Padded", "Moulded": "Moulded", "Spacer": "Lightly Lined"}[cups]
            assert want in _vals(doc, "padding"), (rec["title"], _vals(doc, "padding"))
        else:
            assert cups == "Padded", rec["title"]
            assert _vals(doc, "padded") == {"Yes"}, (rec["title"], _vals(doc, "padded"))


def test_a_bra_whose_title_does_not_name_removable_cups_does_not_state_them():
    states = facet_leaves.stated_bra_facets("Padded Balcony Bra with Removable Straps")
    assert not [v for k, v in states if k == "padding" and "Removable" in v], states
    assert ("padding", "Padded") in states


def test_the_title_words_removable_cups_state_the_padding_value():
    states = facet_leaves.stated_bra_facets("Lace Bralette with Removable Cups")
    assert ("padding", "Removable Cups") in states


def test_no_title_or_description_with_cups_names_drinkware(rows):
    assert rows
    for r in rows:
        text = f"{r['title']} {r['description']}"
        assert not DRINKWARE.search(text), (r["title"], DRINKWARE.search(text).group(0))
