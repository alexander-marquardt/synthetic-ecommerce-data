"""A fresh Grapes leaf, a Steak parent with a child per cut, and allergen coverage (gen#296).

"grapes" could only text-match grape juice, grape sweets and wine; "steak" lived in one
Packaged Meat family. The grocery build now holds Fruit > Grapes, a fresh-meat Steak PARENT with
one child per cut (each label names the product on its own: "Skirt Steak", never "Skirt", which
is also a garment), and the steak knives, sauce and seasoning stay in their own categories as
the decoys. The build prints the share of its rows with ``contains`` filled, and every dietary
label comes from one closed list.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import grocery  # noqa: E402
import grocery_rows  # noqa: E402
import scale  # noqa: E402

STEAK = ("Food & Drink", "Meat & Fish", "Fresh Meat", "Steak")
GRAPES = ("Food & Drink", "Fruit & Vegetables", "Fresh Fruit", "Grapes")
CUTS = ("Sirloin", "Ribeye", "Rump", "Fillet", "Chuck", "T-Bone", "Flank", "Skirt")
DIETARY = ("Vegan", "Vegetarian", "Gluten Free", "Dairy Free", "Nut Free", "Organic")


@cache
def _recs() -> tuple[dict, ...]:
    return tuple(grocery.build(grocery.TARGET))


def _under(path: tuple[str, ...]) -> list[dict]:
    return [r for r in _recs() if tuple(r["category_path"][: len(path)]) == path]


def test_steak_is_a_fresh_meat_parent_with_one_child_per_cut() -> None:
    children = Counter(r["category_path"][len(STEAK)] for r in _under(STEAK)
                       if len(r["category_path"]) > len(STEAK))
    assert sorted(children) == sorted(f"{cut} Steak" for cut in CUTS)
    assert [r for r in _under(STEAK) if len(r["category_path"]) == len(STEAK)] == []


def test_the_steak_node_holds_forty_products_across_six_children() -> None:
    styles = _under(STEAK)
    assert len(styles) >= 40
    assert len({r["category_path"][-1] for r in styles}) >= 6


def test_every_steak_title_names_its_cut_and_sits_in_that_child() -> None:
    styles = _under(STEAK)
    assert styles
    for r in styles:
        leaf = r["category_path"][-1]
        assert leaf in r["title"], (r["title"], leaf)
        assert r["title"].lower().count("steak") == 1, r["title"]


def test_no_node_label_is_a_bare_garment_word() -> None:
    assert "Skirt" not in {r["category_path"][-1] for r in _recs()}


def test_grapes_is_a_fresh_fruit_leaf_with_twenty_products() -> None:
    styles = _under(GRAPES)
    assert len(styles) >= 20
    assert {tuple(r["category_path"]) for r in styles} == {GRAPES}
    assert all("grape" in r["title"].lower() for r in styles)


@pytest.fixture(scope="module")
def _top() -> dict[str, list[dict]]:
    built = br.Index(scale.build(10**6).records)
    return {q: br.rank(built, q, 10) for q in ("grapes", "steak")}


def _leaf_path(doc: dict) -> tuple[str, ...]:
    return tuple(doc["category_path"])


def test_a_plain_search_for_grapes_puts_a_decoy_in_the_top_ten(_top: dict) -> None:
    decoys = [d["title"] for d in _top["grapes"] if _leaf_path(d)[:4] != GRAPES]
    assert decoys, [d["title"] for d in _top["grapes"]]
    assert any(_leaf_path(d)[:4] == GRAPES for d in _top["grapes"])


def test_a_plain_search_for_steak_puts_a_decoy_in_the_top_ten(_top: dict) -> None:
    decoys = [d["title"] for d in _top["steak"] if _leaf_path(d)[:4] != STEAK]
    assert decoys, [d["title"] for d in _top["steak"]]


def test_steak_sauce_and_seasoning_stay_in_their_own_categories() -> None:
    by_title = {r["title"]: r for r in _recs()}
    sauces = [r for t, r in by_title.items() if "Steak Sauce" in t]
    seasonings = [r for t, r in by_title.items() if "Steak Seasoning" in t]
    assert len(sauces) >= 3 and len(seasonings) >= 3
    for r in (*sauces, *seasonings):
        assert tuple(r["category_path"][:4]) != STEAK
        assert r["category_path"][1] == "Food Cupboard"


def test_the_dietary_labels_come_from_one_closed_list() -> None:
    assert tuple(grocery_rows.DIETARY) == DIETARY
    seen = {v for r in grocery.flat(grocery.documents(list(_recs())))
            for v in r["facets"].get("dietary", ())}
    assert seen <= set(DIETARY)
    assert {"Dairy Free", "Vegan", "Gluten Free"} <= seen


def _traced(facets: dict) -> set[str]:
    return {a.lower() for k in ("contains", "may_contain") for a in facets.get(k, ())}


def test_dairy_free_means_no_milk_contained_or_traced() -> None:
    rows = [r for r in grocery.flat(grocery.documents(list(_recs())))
            if r["category_path"][0] == "Food & Drink"]
    with_milk, without_milk = 0, 0
    for r in rows:
        f = r["facets"]
        milk = "milk" in _traced(f)
        labelled = "Dairy Free" in f.get("dietary", ())
        assert labelled != milk, (r["title"], f)
        with_milk += milk
        without_milk += not milk
    assert with_milk and without_milk


def test_an_egg_row_without_milk_is_still_dairy_free() -> None:
    rows = [r for r in grocery.flat(grocery.documents(list(_recs())))
            if "eggs" in r["facets"].get("contains", ()) and "milk" not in _traced(r["facets"])]
    assert rows
    assert all("Dairy Free" in r["facets"].get("dietary", ()) for r in rows)


def test_the_coverage_report_gives_the_share_of_rows_with_contains_filled() -> None:
    report = grocery.coverage_report(list(_recs()))
    assert set(report) == {"food_rows", "contains_filled", "contains_share"}
    rows = [r for r in grocery.flat(grocery.documents(list(_recs())))
            if r["category_path"][0] == "Food & Drink"]
    filled = sum(bool(r["facets"].get("contains")) for r in rows)
    assert report["food_rows"] == len(rows)
    assert report["contains_filled"] == filled
    assert report["contains_share"] == round(filled / len(rows), 4)
    assert 0 < report["contains_share"] < 1


def test_the_cli_prints_the_coverage_report(capsys: pytest.CaptureFixture[str]) -> None:
    assert grocery.main(["--skus", "2000"]) == 0
    printed = json.loads(capsys.readouterr().out)
    assert "contains_share" in printed
