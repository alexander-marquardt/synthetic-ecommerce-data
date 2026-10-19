"""The retail ``pattern`` facet holds tartan, floral, breton stripe and patchwork (gen#408).

The coverage review of gen#188 asked for the patterns a shopper types before a category. The
ceiling build held leopard and polka dot but no tartan, floral, breton stripe or patchwork. The
wanted values are written out here on purpose: the test does not read the module that adds them.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402 -- the prototype's own directory is its import root
import scale  # noqa: E402

#: The six values the coverage review asked for, as the facet spells them (lower case).
WANTED = ("leopard", "tartan", "polka dot", "floral", "breton stripe", "patchwork")

#: value -> (top of the category path, product types where a shopper types it before the category).
WHERE = {
    "tartan": ("Womens", {"Skirt"}),
    "floral": ("Womens", {"Dress", "Blouse"}),
    "breton stripe": ("Womens", {"Top"}),
    "patchwork": ("Home", {"Cushion"}),
}


@pytest.fixture(scope="module")
def nested() -> list[dict[str, Any]]:
    built = scale.build(sum(t["sku_count"] for t in scale.templates()) + 3000)
    return scale.documents(built)


def _values(entries: list[dict[str, Any]], key: str) -> list[str]:
    return [e["value"] for e in entries if e["key"] == key]


def test_the_pattern_facet_holds_each_of_the_six_wanted_values(
    nested: list[dict[str, Any]],
) -> None:
    facet = {p for doc in nested for p in _values(doc["attributes"], "pattern")}
    assert sorted(set(WANTED) - facet) == []


@pytest.mark.parametrize("value", sorted(WHERE))
def test_each_missing_value_is_on_a_product_where_a_shopper_types_it_before_the_category(
    nested: list[dict[str, Any]], value: str
) -> None:
    root, types = WHERE[value]
    found = {
        doc["product_type"]
        for doc in nested
        if value in _values(doc["attributes"], "pattern") and doc["category_path"][0] == root
    }
    assert found & types == found and found, found


@pytest.mark.parametrize(
    ("authored", "color", "pattern"),
    [
        ("Red Tartan", "Red", "Tartan"),
        ("Pink Floral", "Pink", "Floral"),
        ("Navy Breton Stripe", "Navy", "Breton Stripe"),
        ("Multi Patchwork", "Multi", "Patchwork"),
    ],
)
def test_split_takes_the_new_patterns_out_of_the_color(
    authored: str, color: str, pattern: str
) -> None:
    assert colorwords.split(authored) == (color, pattern)


def test_the_color_of_a_product_with_a_new_pattern_stays_a_plain_color(
    nested: list[dict[str, Any]],
) -> None:
    """The gen#188 guard on these products: a color facet holds a color word, never the pattern."""
    new = set(WHERE)
    words = colorwords.COLOR_WORDS | colorwords.MODIFIERS
    seen, bad = 0, set()
    for doc in nested:
        if not new & set(_values(doc["attributes"], "pattern")):
            continue
        for v in doc["variants"]:
            for c in _values(v["attributes"], "color"):
                seen += 1
                if not colorwords.is_plain(c) or not any(w in words for w in c.split()):
                    bad.add(c)
    assert seen > 10
    assert sorted(bad) == []


def test_a_pattern_row_draws_a_motif_the_kit_has() -> None:
    """A flower print names a kit shape (``daisy``), never the category ``flowers``: the drawing
    kit raises on a name it has no shape for."""
    import motifs
    import pattern_rows

    named = {d["drawing"]["motif"] for d in pattern_rows.docs() if "motif" in d["drawing"]}
    assert named
    for name in named:
        assert motifs.registry().get(name) is not None, name


def test_the_pattern_rows_open_no_tree_node_of_their_own() -> None:
    """A skirt sits in ``Womens > Skirts``: a ``Mini Skirts`` node would pull every other
    "Mini Skirt" title into it (the gen#283 tree-nesting rule)."""
    import pattern_rows

    paths = {tuple(d["category_path"]) for d in pattern_rows.docs() if "Skirt" in d["title"]}
    assert paths == {("Womens", "Skirts")}


def test_a_pattern_row_description_does_not_name_a_neckline() -> None:
    """gen#181: a boat or slash top names its neckline in the title on some tops only, and
    never in the description."""
    import pattern_rows

    for d in pattern_rows.docs():
        assert not re.search(r"\b(boat|slash)", d["description"].lower()), d["product_id"]
