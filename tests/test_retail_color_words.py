"""The shopper-facing color is a plain color word, never an object or a food (gen#150).

A yellow tee had the color "Lemon". ``prototypes/retail_drawings/colorwords.py`` maps
each authored fashion shade to its plain color; these tests hold the ceiling build (every
template exhausted, so every derived style too) to it, at the three places a shopper
meets a color: the style's ``color_options``, each SKU's ``color`` and the exported
``color`` facet. The denylist is written out here on purpose: it does not read the
allowlist it checks.
"""

from __future__ import annotations

import collections
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import colorwords  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402
from retail_figures import figures  # noqa: E402

#: Today's ceiling SKUs, as ``retail_figures.figures()`` measures it (gen#162, gen#536).
CEILING_SKUS = figures()["ceiling"]["skus"]
#: Words of an object, a food or a plant that are not a color. A color value holding one
#: is a fashion name where a color word belongs. Shopper color words (gen#195) that are also a
#: food, a stone or a fabric are a plain color value of their own now (see
#: ``tests/test_retail_seasonal_195.py``), so they are not here.
# "sage" left the list in gen#509: a shopper types "sage cushion" for the color, as for "olive"
# (gen#195), so it is a color value of its own; "Sage Leaf" is still caught by "leaf".
DENYLIST = frozenset({
    "lemon", "lime", "cherry", "peach", "chocolate", "coffee", "plum",
    "mustard", "cocoa", "honey", "toffee", "latte", "mocha", "espresso",
    "hazelnut", "walnut", "oak", "oat", "almond", "ginger", "apple", "melba",
    "watermelon", "wine", "fig", "jam", "damson", "mulberry", "bramble", "leaf",
    "moss", "forest", "ochre", "brick", "terracotta", "tobacco", "pearl",
    "oyster", "slate", "pewter", "smoke", "ice", "brass", "mink", "fawn", "sand",
    "kraft", "calico", "tabby", "cognac", "chestnut", "claret", "poppy",
    "orchid", "petal", "sprig", "star", "confetti", "candy", "breton", "glaze",
    "porcelain", "bare", "linen", "petrol", "midnight", "sky", "dove",
    "cloud", "storm", "glacier", "citrus", "cinder", "kiln", "post", "box", "tea", "shell",
    "oxblood", "celadon", "rosewood", "mauve", "coral reef", "glow", "haze", "pop", "field",
})  # fmt: skip


@pytest.fixture(scope="module")
def ceiling() -> scale.Scaled:
    return scale.build(CEILING_SKUS * 2)


def _swatch_names(records) -> collections.Counter:
    return collections.Counter(c["color"] for r in records for c in r.get("color_options", ()))


def _sku_colors(records) -> collections.Counter:
    return collections.Counter(s["color"] for r in records for s in r["skus"] if "color" in s)


def _facet_colors(records) -> collections.Counter:
    out: collections.Counter = collections.Counter()
    for r in records:
        doc = export.standard_document(r)
        out.update(a["value"] for a in doc["attributes"] if a["key"] == "color")
        out.update(
            a["value"] for v in doc["variants"] for a in v["attributes"] if a["key"] == "color"
        )
    return out


def _denied(values) -> list[str]:
    """The values holding a denied word; "breton stripe" is a pattern's name (gen#408), so it is
    taken out first: "Breton Blue" is still a fashion name."""
    return sorted(
        v
        for v in values
        if DENYLIST & set(v.lower().replace("breton stripe", "").replace("/", " ").split())
    )


def test_no_color_value_names_an_object_or_a_food(ceiling):
    for where in (_swatch_names, _sku_colors, _facet_colors):
        assert _denied(where(ceiling.records)) == [], where.__name__


def test_every_color_value_is_a_color_word_a_qualifier_or_a_shade_code(ceiling):
    for where in (_swatch_names, _sku_colors, _facet_colors):
        values = where(ceiling.records)
        assert values, where.__name__
        assert sorted(v for v in values if not colorwords.is_plain(v)) == [], where.__name__


def test_the_lemon_tee_is_yellow_and_still_named_lemon_in_its_title(ceiling):
    tee = next(r for r in ceiling.records if r["title"] == "Lemon Crew Neck Tee")
    assert {s["color"] for s in tee["skus"]} == {"Yellow"}
    assert [c["color"] for c in tee["color_options"]] == ["Yellow"]
    facet = [a["value"] for a in export.standard_document(tee)["attributes"] if a["key"] == "color"]
    assert facet == ["Yellow"]


def test_two_shades_of_one_color_stay_apart_by_a_tone():
    assert colorwords.plain("Lemon") == "Yellow"
    assert colorwords.plain("Mustard") == "Dark Yellow"
    assert colorwords.plain("Navy") == "Navy"
    assert len({colorwords.plain(s) for s in ("Lemon", "Mustard", "Ochre")}) == 2


def test_the_mapping_never_names_a_denied_word_or_a_non_color(ceiling):
    assert _denied(colorwords.PLAIN.values()) == []
    assert [v for v in colorwords.PLAIN.values() if not colorwords.is_plain(v)] == []
    assert _denied(colorwords.PLAIN) != [], "the denylist should catch the authored names"


def test_a_style_keeps_every_color_the_template_authored(ceiling):
    """A mapping that merged two shades of a style would drop SKUs: the ceiling is pinned.

    The pin moved with the plain names (#150): a SKU grid is drawn by color name.
    """
    assert ceiling.skus == CEILING_SKUS
    for r in ceiling.records:
        colors = [c["color"] for c in r.get("color_options", ())]
        assert len(colors) == len(set(colors)), r["product_id"]
        assert {s["color"] for s in r["skus"] if "color" in s} == set(colors), r["product_id"]
