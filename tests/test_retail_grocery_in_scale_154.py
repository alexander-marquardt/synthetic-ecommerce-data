"""Grocery joins the main retail build (gen#154): one catalog, one image release, one flat file.

``scale.templates()`` ends with the grocery styles (:func:`grocery.build`), so a build past
the other templates carries Food & Drink at grocery depth, ``image_release`` ships their
drawings in the same archive, and the flat export carries ``ingredients`` top-level.
The seeded derivation never draws from a grocery style: its allergen, dietary and
ingredient facts are the grocery build's own and a re-drawn title would contradict them.
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

import grocery  # noqa: E402
import image_release  # noqa: E402
import scale  # noqa: E402

#: The grocery styles and SKUs (``tests/test_grocery_154.py``'s 10K build).
GROCERY_STYLES = 3_305
GROCERY_SKUS = 10_042
#: The main build's own Food & Drink styles (honey, jam, tea, coffee, chutney, ...): kept.
MAIN_FOOD_STYLES = 55
MAIN_FOOD_SKUS = 61
#: The templates before grocery, and the SKUs they hold (``tests/test_retail_scale.py``'s).
MAIN_TEMPLATES = 927
MAIN_TEMPLATE_SKUS = 27_928


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


@pytest.fixture(scope="module")
def built(templates) -> scale.Scaled:
    """The templates and a few hundred derived SKUs: every template is in, none exhausted."""
    return scale.build(sum(t["sku_count"] for t in templates) + 500)


def _food(recs: list[dict]) -> list[dict]:
    return [r for r in recs if r["department"][0] == "Food & Drink"]


def test_grocery_styles_follow_the_main_templates_unchanged(templates):
    assert len(templates) == MAIN_TEMPLATES + GROCERY_STYLES
    assert templates[MAIN_TEMPLATES:] == grocery.build()
    assert sum(t["sku_count"] for t in templates) == MAIN_TEMPLATE_SKUS + GROCERY_SKUS


def test_a_build_inside_the_main_templates_is_what_it_was(templates):
    """A smaller build is a prefix of a larger one: grocery comes last, so a 20K build moves not."""
    small = scale.build(20_000)
    assert [r["product_id"] for r in small.records] == [
        t["product_id"] for t in templates[: len(small.records)]
    ]
    assert not [r for r in small.records if r["product_id"].startswith("GRC-")]


def test_the_main_food_styles_are_kept_and_no_title_or_id_repeats(templates):
    main = templates[:MAIN_TEMPLATES]
    kept = _food(main)
    assert (len(kept), sum(r["sku_count"] for r in kept)) == (MAIN_FOOD_STYLES, MAIN_FOOD_SKUS)
    titles = collections.Counter(r["title"] for r in templates)
    ids = collections.Counter(r["product_id"] for r in templates)
    assert [t for t, n in titles.items() if n > 1] == []
    assert [i for i, n in ids.items() if n > 1] == []


def test_honey_is_planted_once_by_the_main_build_and_never_derived_twice(built):
    """The main build's one honey jar stays; grocery plants the rest; no style derives from either
    grocery or that jar a second time."""
    assert [r["product_id"] for r in built.records[:MAIN_TEMPLATES] if r["category_leaf"] == "Honey"] == [
        "PLT-HONBLS"
    ]
    assert [p for p, t in built.template_of.items() if t == "PLT-HONBLS"] == []


def test_derived_styles_never_come_from_a_grocery_style(built):
    assert len(built.template_of) > 0
    assert [p for p, t in built.template_of.items() if t.startswith("GRC-")] == []
    assert not [r for r in built.records[len(built.records) - len(built.template_of):] if r["product_id"].startswith("GRC-")]


def test_the_flat_export_carries_food_and_drink_with_ingredients_top_level(built):
    docs = scale.documents(built)
    rows = scale.flat(docs)
    assert len(rows) == built.skus
    food = [r for r in rows if r["department"] == "Food & Drink"]
    assert len(food) >= GROCERY_SKUS
    with_list = [r for r in food if r.get("ingredients")]
    assert len(with_list) > 9_000
    assert all(isinstance(r["ingredients"], list) for r in with_list)
    assert {"contains", "free_from"} <= {k for r in food for k in r}


def test_the_image_release_ships_the_grocery_drawings(built):
    files = image_release.image_files(built.records)
    members = {path for path, _ in files}
    grocery_skus = [s for r in built.records if r["product_id"].startswith("GRC-") for s in r["skus"]]
    assert len(grocery_skus) == GROCERY_SKUS
    by_id = {r["product_id"]: r for r in built.records}
    missing = [
        s["sku"]
        for pid, r in by_id.items()
        if pid.startswith("GRC-")
        for s in r["skus"]
        if image_release.member_path(image_release.export.image_id(r, s)) not in members
    ]
    assert missing == []
