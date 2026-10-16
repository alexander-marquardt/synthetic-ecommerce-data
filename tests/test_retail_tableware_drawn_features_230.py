"""A tableware image draws the feature its title names, and one material has one value (gen#230).

Found reviewing gen#222: a "Bamboo Chopping Board with Juice Groove" drew a hanging hole and no
groove, "Ribbed Highball Glasses" drew a smooth tumbler, a Cream utensil set painted its heads
grey-taupe, and the single cutlery said ``Stainless Steel 18/10`` where the cutlery set, the
utensils and the colander say ``Stainless Steel``, so a material facet listed one metal twice.

Guard: a title that names a drawn feature fails here until the image draws it; a material
that differs from another only by a trailing grade fails here by key.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
sys.path.insert(0, str(HERE))

import kit  # noqa: E402
import scale  # noqa: E402
import tableware_rows  # noqa: E402

DOCS = tableware_rows.docs()

#: A word a tableware title may name -> the class the image gives the part it draws for it.
NAMED_FEATURES = {"groove": 'class="groove"', "ribbed": 'class="ribs"'}


def _svg(doc: dict, base: str = "#d9b77e") -> str:
    d = doc["drawing"]
    fill = kit.Fill("solid", base, d["accent"], d["third"])
    return kit.render(d["shape"], fill, d["label"], params=d["params"])


def _named(word: str) -> list[dict]:
    return [d for d in DOCS if word in d["title"].lower()]


def test_the_titles_that_name_a_feature_exist() -> None:
    """Guard on the guard: the parametrised check below is not vacuous."""
    assert {d["product_id"] for d in _named("groove")} >= {"BRD-BRDBAM"}
    assert {d["product_id"] for d in _named("ribbed")} >= {"BRD-GLSHIB"}


@pytest.mark.parametrize("word", NAMED_FEATURES)
def test_a_title_that_names_a_feature_draws_it(word: str) -> None:
    missing = [d["product_id"] for d in _named(word) if NAMED_FEATURES[word] not in _svg(d)]
    assert missing == []


@pytest.mark.parametrize("word", NAMED_FEATURES)
def test_a_style_that_does_not_name_the_feature_does_not_draw_it(word: str) -> None:
    """The part is drawn for the title that names it, not for every row of the shape."""
    shapes = {d["drawing"]["shape"] for d in _named(word)}
    drawn = [
        d["product_id"]
        for d in DOCS
        if d["drawing"]["shape"] in shapes
        and word not in d["title"].lower()
        and NAMED_FEATURES[word] in _svg(d)
    ]
    assert drawn == []


def test_a_utensil_set_paints_its_heads_in_the_records_color() -> None:
    """The set stands in a pot of the record's color and its heads are that color too: a
    darkened head reads as grey-taupe on a Cream set."""
    (doc,) = [d for d in DOCS if d["product_id"] == "BRD-UTNSET"]
    for base in ("#efe8d8", "#9a9a9a"):
        svg = _svg(doc, base)
        heads = set(re.findall(r'fill="([^"]+)"[^>]*class="head"', svg))
        pots = set(re.findall(r'fill="([^"]+)"[^>]*class="pot"', svg))
        assert pots == {base}, svg[:400]
        assert heads == pots, (base, heads, pots)


def _material_values() -> dict[tuple[str, str], set[str]]:
    grade = re.compile(r"\s+\d+/\d+$")
    spellings: dict[tuple[str, str], set[str]] = defaultdict(set)
    for t in scale.templates():
        for a in t.get("attributes", ()):
            if a["key"] in {"material", "metal", "blade_steel", "lid_material"}:
                value = str(a["value"])
                spellings[(a["key"], grade.sub("", value).lower())].add(value)
    return spellings


def test_one_material_is_one_value_in_a_key() -> None:
    split = {k: sorted(v) for k, v in _material_values().items() if len(v) > 1}
    assert split == {}


def test_the_stainless_steel_material_has_rows_in_every_tableware_type_that_sells_it() -> None:
    """Guard on the guard: the cutlery (single and set), utensils and colander share it."""
    rows = {
        d["product_type"]
        for d in DOCS
        for a in d["attributes"]
        if a["key"] == "material" and a["value"] == "Stainless Steel"
    }
    assert rows >= {"Cutlery", "Kitchen Utensil", "Colander"}


def _all_named(phrase: str) -> list[dict]:
    """Every authored template whose title names ``phrase``, wherever its rows live."""
    return [t for t in scale.templates() if phrase in t["title"].lower()]


def test_every_template_that_names_a_juice_groove_draws_one() -> None:
    """Review of gen#415: the scan above reads only ``tableware_rows``, so the steak serving
    board in ``distractor_rows`` drew no groove. Scan every template by its shape."""
    named = _all_named("juice groove")
    assert {t["product_id"] for t in named} >= {"BRD-BRDBAM", "PLT-DSK09"}  # not vacuous
    missing = [t["product_id"] for t in named if NAMED_FEATURES["groove"] not in _svg(t)]
    assert missing == []
