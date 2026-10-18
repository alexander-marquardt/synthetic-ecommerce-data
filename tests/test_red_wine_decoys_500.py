"""A plain "red wine" search meets real red-wine groceries that are not wine (gen#500).

Red wine vinegar is a top hit on some sites for "red wine": it holds both words, in a title
as short as a wine's, and it is not wine. The catalog plants it under Food Cupboard > Vinegar
in two brands and two pack sizes, beside a red wine gravy and a beef in red wine ready meal.
All are ordinary supermarket products (class 10 of :mod:`decoy_rows`). They are not wine: no
grape, country, wine style or strength, and no path under Wine.
"""

from __future__ import annotations

import sys
from functools import cache
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import decoy_rows as dr  # noqa: E402
import scale  # noqa: E402

VINEGAR = ["Food & Drink", "Food Cupboard", "Vinegar"]
WINE_ONLY = {"grape", "country", "wine_style", "abv"}
GROCERIES = ("Red Wine Vinegar", "Red Wine Gravy", "Beef in Red Wine")


@cache
def _docs() -> tuple[dict, ...]:
    return tuple(dr.docs())


def _named(phrase: str) -> list[dict]:
    return [d for d in _docs() if phrase in d["title"]]


@pytest.mark.parametrize("phrase", GROCERIES)
def test_each_red_wine_grocery_exists_and_is_not_wine(phrase: str) -> None:
    docs = _named(phrase)
    assert docs, phrase
    for d in docs:
        assert "Wine" not in d["category_path"], d["title"]
        assert not WINE_ONLY & {a["key"] for a in d["attributes"]}, d["title"]
        assert d["product_type"] != "Wine", d["title"]


def test_red_wine_vinegar_sits_under_vinegar_in_two_brands_and_two_packs() -> None:
    docs = _named("Red Wine Vinegar")
    assert docs
    assert all(d["category_path"] == VINEGAR for d in docs)
    assert len({d["brand"] for d in docs}) >= 2
    assert {"250ml", "500ml"} <= {t for d in docs for t in d["title"].replace(",", " ").split()}


def test_every_red_wine_grocery_is_class_10_and_a_decoy_of_the_red_wine_query() -> None:
    rows = [r for r in dr.TABLE if any(g in r.title for g in GROCERIES)]
    assert rows
    assert all(r.cls == 10 and r.query == "red wine" and not r.true_hit for r in rows)


def test_a_plain_red_wine_search_scores_a_vinegar_in_the_top_10() -> None:
    index = br.Index(scale.build(10**6).records)
    top = [d["title"] for d in br.rank(index, "red wine", 10)]
    assert any("Red Wine Vinegar" in t for t in top), top
