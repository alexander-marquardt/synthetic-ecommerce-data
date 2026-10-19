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
    "floral": ("Womens", {"Dress"}),
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


def _styles_with(fill: str) -> list[dict[str, Any]]:
    """The template styles that sell a colorway with this fill."""
    return [
        d
        for d in scale.templates()
        if fill in {o["pattern"] for o in d.get("color_options", [])}
    ]


def test_a_flower_print_draws_a_motif_the_kit_has() -> None:
    """A flower print names a kit shape (``daisy``), never the category ``flowers``: the drawing
    kit raises on a name it has no shape for."""
    import motifs

    floral = [d for d in _styles_with("print") if "Pink Floral" in str(d["color_options"])]
    assert floral
    for d in floral:
        assert motifs.registry().get(d["drawing"]["motif"]) is not None, d["drawing"]


def test_the_patchwork_cushion_is_drawn_with_a_patchwork_fill_not_a_gingham_one() -> None:
    """A patchwork cushion drawn as gingham shows a check to a shopper who typed patchwork."""
    cushion = [d for d in _styles_with("patchwork") if d["product_type"] == "Cushion"]
    assert cushion
    for d in cushion:
        assert d["drawing"]["pattern"] == "patchwork", d["drawing"]


def test_the_kit_patchwork_tile_is_pieced_squares_not_a_check() -> None:
    """The patchwork tile holds four differently colored squares; gingham holds two."""
    import kit

    def fills(pattern: str) -> set[str]:
        svg = kit.pattern_defs(kit.Fill(pattern, "#c46a4a", "#26365c"), "p")
        return set(re.findall(r'fill="(#[0-9a-f]{6})"', svg))

    assert len(fills("patchwork")) == 4
    assert len(fills("gingham")) == 2


def test_the_pattern_values_add_no_style_and_no_sku() -> None:
    """The product count is frozen: the four pattern words ride on colorways of styles main already
    sold, so they add no template. The build holds 11,351 templates and 101,620 template
    SKUs: main's 11,324 and 101,460 plus the 27 templates and 160 SKUs of the gen#509 plant rows.
    A new style would raise both: the PR that lifts the freeze must move them."""
    tpls = scale.templates()
    assert len(tpls) == 11351
    assert sum(t["sku_count"] for t in tpls) == 101620
