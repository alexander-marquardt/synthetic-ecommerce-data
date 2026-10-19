"""Plants named after a color and a scent (gen#509): lavender, sage, rosemary, thyme, olive
trees and eucalyptus each have a plant node, so a bare "lavender" has a category node the
category-node policy can route to (as "champagne" and "oranges" do).

The other senses of the words stay true: Sage is a color word of its own (a sage cushion), Olive
already was, and the candle range carries lavender, sage and eucalyptus fragrances.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402
import kit  # noqa: E402
import kit_garden  # noqa: E402,F401 -- registers the shapes
import scale  # noqa: E402
import type_colors  # noqa: E402

#: A plant node and the fewest styles it holds at the ceiling (the issue asks for about 10).
FLOOR = 8
PLANTS = ("Garden", "Plants")
NODES = (
    (*PLANTS, "Lavender"),
    (*PLANTS, "Herbs", "Sage"),
    (*PLANTS, "Herbs", "Rosemary"),
    (*PLANTS, "Herbs", "Thyme"),
    (*PLANTS, "Olive Trees"),
    (*PLANTS, "Eucalyptus"),
)


@pytest.fixture(scope="module")
def records() -> list[dict]:
    return scale.build(10**6).records


def _colors(rec: dict) -> set[str]:
    return {s["color"] for s in rec["skus"] if "color" in s}


@pytest.mark.parametrize("node", NODES, ids=lambda n: " > ".join(n[2:]))
def test_every_plant_node_holds_at_least_eight_styles(records, node):
    held = [r for r in records if tuple(r["category_path"]) == node]
    assert len(held) >= FLOOR, f"{' > '.join(node)} holds {len(held)} styles"


@pytest.mark.parametrize("node", NODES, ids=lambda n: " > ".join(n[2:]))
def test_a_plant_node_is_named_for_the_word_a_shopper_types(records, node):
    """The leaf is the shopper's word (a plural for a tree), so a query naming it routes to it."""
    held = [r for r in records if tuple(r["category_path"]) == node]
    leaf = node[-1].lower().rstrip("s")
    assert held, f"{' > '.join(node)} holds no style"
    assert all(leaf in r["title"].lower() for r in held)


def test_every_style_of_a_plant_node_is_a_plant(records):
    held = [r for r in records if tuple(r["category_path"]) in NODES]
    assert held, "no plant node holds a style"
    assert {r["product_type"] for r in held} == {"Plant"}


def test_a_herb_and_a_lavender_plant_are_drawn_as_a_potted_herb():
    assert "potted_herb" in kit.SHAPES


def test_the_potted_herb_blooms_only_when_the_row_says_so():
    assert "potted_herb" in kit.SHAPES
    fill = kit.Fill("solid", "#b5603a", "#4f7a3a")
    plain = kit.render("potted_herb", fill, params={})
    bloom = kit.render("potted_herb", fill, params={"bloom": "#8c6bb1"})
    assert plain != bloom
    assert "#8c6bb1" in bloom and "#8c6bb1" not in plain


def test_sage_is_a_color_word_a_shopper_can_type():
    assert "Sage" in colorwords.COLOR_WORDS
    assert colorwords.plain("Sage") == "Sage"


def test_a_sage_and_an_olive_style_exist_in_clothing_and_home_textiles(records):
    for color in ("Sage", "Olive"):
        tops = collections.Counter(r["category_path"][0] for r in records if color in _colors(r))
        assert tops["Home"] or tops["Womens"] or tops["Mens"], f"{color}: {dict(tops)}"
    cushions = [
        r for r in records if r["category_path"][:3] == ["Home", "Soft Furnishings", "Cushions"]
    ]
    for color in ("Sage", "Olive"):
        assert any(color in _colors(r) for r in cushions), f"no {color} cushion"


def test_every_sage_or_olive_color_sits_on_a_type_whose_allow_list_holds_it(records):
    seen = 0
    for r in records:
        for color in _colors(r) & {"Sage", "Olive"}:
            seen += 1
            assert type_colors.permits(r["category_path"], color), (
                f"{r['title']} ({' > '.join(r['category_path'])}) carries {color}"
            )
    assert seen, "no Sage or Olive style to check"


@pytest.mark.parametrize("scent", ("Lavender", "Sage", "Eucalyptus"))
def test_the_scented_candles_carry_the_scent(records, scent):
    candles = [
        r
        for r in records
        if r["category_path"][:3] == ["Gifts", "Home Fragrance", "Scented Candles"]
    ]
    held = [
        r
        for r in candles
        if any(a["key"] == "fragrance" and scent in str(a["value"]) for a in r["attributes"])
    ]
    assert held, f"no {scent} candle"
    assert any(scent.lower() in r["title"].lower() for r in held)
