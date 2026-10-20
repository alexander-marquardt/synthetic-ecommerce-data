"""Cream sofas and armchairs for the query "face cream" (gen#541).

A well-known failure on public retail sites: ``face cream`` returns cream-colored sofas, because
the color word is matched alone. The set in ``feature_decoys/face_cream_cream_sofa.py`` makes the
catalogue able to show it. It holds three families:

* **Baby Face** furniture: "Baby Face" is a real upholstery fabric, so the title holds both words
  of the query. Without a policy these lead the page; the category and the product type
  (Sofa, Armchair, not Face Cream) keep them out of Best.
* **Facing** corner sofas: "Right-Hand Facing" is real furniture naming, and the title field is
  not stemmed, so ``facing`` is not ``face``. They match on ``cream`` alone and stay below the
  top 10: the baseline is already better than a stemming engine, which is their point.
* **Cream only** pieces whose title has no "face"; "face fabric" is in the description.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_rows as dr  # noqa: E402
import scale  # noqa: E402
from distractors import tokens  # noqa: E402

QUERY = "face cream"

#: title -> the leaf of Home > Furniture it sits in (all hold the words "face" and "cream").
BABY_FACE = {
    "Cream Baby Face Fabric Sofa": "Sofas",
    "Cream Baby Face Fabric Corner Sofa": "Corner Sofas",
    "Cream Baby Face Fabric Armchair": "Armchairs",
    "Cream Baby Face Fabric Footstool": "Footstools",
}
#: title -> leaf: "Facing" is not "face" in an unstemmed title; "cream" is the only word held.
FACING = {
    "Textured Chenille Right-Hand Facing Corner Sofa, Cream": "Corner Sofas",
    "Textured Chenille Left-Hand Facing Corner Sofa, Cream": "Corner Sofas",
    "Textured Chenille 2 Seater Sofa, Cream": "Sofas",
    "Textured Chenille Snuggle Chair, Cream": "Armchairs",
    "Textured Chenille Footstool, Cream": "Footstools",
}
#: title -> leaf: no "face" in the title; the description says "face fabric".
CREAM_ONLY = {
    "Cream Boucle Three-Seater Sofa": "Sofas",
    "Cream Linen Armchair": "Armchairs",
}
#: the home decor decoys: "face" as a line-art motif, and a throw with no "face" at all.
DECOR = {
    "Cream Abstract Face Line-Art Cushion": "Cushions",
    "Cream Chunky Knit Throw": "Throws",
}
NEW = {**BABY_FACE, **FACING, **CREAM_ONLY, **DECOR}


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def by_title(ceiling: list[dict]) -> dict[str, dict]:
    return {r["title"]: r for r in ceiling}


def _doc(by_title: dict[str, dict], title: str) -> dict:
    doc = by_title.get(title)
    assert doc is not None, f"no product titled {title!r}"
    return doc


def _colors(doc: dict) -> set[str]:
    return {c["color"] for c in doc.get("color_options") or []}


def test_every_decoy_of_the_set_is_in_the_catalogue_as_a_single_cream_template(by_title):
    for title in NEW:
        doc = _doc(by_title, title)
        assert _colors(doc) == {"Cream"}, (title, _colors(doc))
        assert doc["product_id"] in dr.BY_ID, title
        assert dr.BY_ID[doc["product_id"]].query == QUERY, title


@pytest.mark.parametrize("family", [BABY_FACE, FACING, CREAM_ONLY])
def test_the_furniture_decoys_sit_in_home_furniture_under_their_own_leaf(by_title, family):
    for title, leaf in family.items():
        path = _doc(by_title, title)["category_path"]
        assert path[:2] == ["Home", "Furniture"] and path[-1] == leaf, (title, path)


def test_the_lead_title_and_its_baby_face_siblings_exist(by_title):
    _doc(by_title, "Cream Baby Face Fabric Sofa")
    for title in BABY_FACE:
        assert title.startswith("Cream Baby Face Fabric "), title
        assert _doc(by_title, title)["category_path"][0] == "Home", title


def test_the_facing_corner_sofas_exist_on_both_hands_with_their_siblings(by_title):
    corners = [t for t in FACING if "Facing" in t]
    assert {"Right-Hand" in t for t in corners} == {True, False}
    for title in corners:
        assert _doc(by_title, title)["category_path"][-1] == "Corner Sofas", title
    assert any("Snuggle Chair" in t for t in FACING)
    assert any("Footstool" in t for t in FACING)


def test_cream_sofas_and_armchairs_titled_cream_number_six_to_ten(ceiling):
    """The metric: 1 before this set; about 6 to 10 after."""
    n = sum(
        1
        for r in ceiling
        if r["category_path"][:2] == ["Home", "Furniture"]
        and r["category_path"][2] in ("Sofas", "Corner Sofas", "Armchairs")
        and "Cream" in _colors(r)
        and "cream" in tokens(r["title"])
    )
    assert 6 <= n <= 10, n


def test_which_decoys_hold_both_words_in_the_title_and_which_only_one_or_in_the_description(
    by_title,
):
    for title in [*BABY_FACE, "Cream Abstract Face Line-Art Cushion"]:
        assert {"face", "cream"} <= set(tokens(title)), title
    for title in FACING:
        words = set(tokens(title))
        assert "cream" in words and "face" not in words, title
        assert "face" not in tokens(_doc(by_title, title)["description"]), title
    for title in ("Cream Boucle Three-Seater Sofa", "Cream Linen Armchair"):
        assert "face" not in tokens(title), title
        assert "face fabric" in _doc(by_title, title)["description"].lower(), title
    throw = _doc(by_title, "Cream Chunky Knit Throw")
    assert "face" not in tokens(throw["title"] + " " + throw["description"])


def test_without_a_policy_the_lead_baby_face_sofa_is_in_the_top_10_and_the_facing_sofas_are_not(
    ceiling,
):
    top = [d["title"] for d in br.rank(br.Index(ceiling), QUERY, 10)]
    assert "Cream Baby Face Fabric Sofa" in top, top
    assert not set(FACING) & set(top), sorted(set(FACING) & set(top))


def test_with_the_product_type_read_no_decoy_of_the_set_is_a_face_cream(by_title):
    for title in NEW:
        assert _doc(by_title, title)["product_type"] != "Face Cream", title
        assert "Face Cream" not in _doc(by_title, title)["category_path"], title


def test_best_for_face_cream_is_skincare_there_are_enough_real_face_creams(ceiling):
    real = [
        r
        for r in ceiling
        if r["product_type"] == "Face Cream" and {"face", "cream"} <= set(tokens(r["title"]))
    ]
    assert len(real) >= 8, len(real)


def test_the_module_says_which_query_the_facing_sofas_answer_and_why_there_is_no_policy():
    import feature_decoys.face_cream_cream_sofa as fc

    doc = fc.__doc__ or ""
    assert "face cream" in doc and "Facing" in doc and "no policy" in doc
