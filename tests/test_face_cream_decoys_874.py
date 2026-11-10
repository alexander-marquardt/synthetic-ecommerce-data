"""With interpretation off, "face cream" meets believable decoys in its top twelve (gen#874).

The served search with interpretation off multiplies a product's text score by 3 for each typed word
its title holds and by 2.5 more when the title holds the typed phrase (prism#14050; the debug
``score_explanation`` reads ``base x (1 + typed word "face") x (1 + rb:title_phrase_match) x (1 +
typed word "cream") x (1 + merchandising_score_boost)``). Every real face cream says "Face Cream";
no decoy did, so the 23 real creams took the top 23 and the demo had no "before" picture. The
decoys of ``feature_decoys/face_cream_874.py`` hold the phrase in a short title, and the real
creams of ``type_specs/face_cream.py`` say who they are for, so a short title no longer wins on
length alone.

``_score`` is that product of factors over the title's BM25. ``STATS`` holds what
``catalog_combined_2026-11-09-1810`` answered in ``_explain`` for ``title:face`` and
``title:cream``, so the test reads fixed numbers and no cluster. The popularity factor is the
customization's business-signal tuning: ``merchandising_score`` over 100 and the sales over
10,000. Margin is left out: it adds about 0.1 to every product alike.
"""

from __future__ import annotations

import math
import re
from functools import cache

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import decoy_rows as dr
from synthetic_ecommerce_data.domains.retail import export

#: Documents of the index with a title, and per term the documents whose title holds it.
DOCS = 383891
DF = {"face": 160, "cream": 1374}
AVGDL = 7.89428
K1, B = 1.2, 0.75
#: ``(1 + 2.00)`` per typed word the title holds, and ``(1 + 1.50)`` for the phrase in the title.
TYPED_WORD = 3.0
PHRASE = 2.5
QUERY = "face cream"
TOP = 12
MIN_DECOYS = 3
TITLES = (
    "Baby Face Cream Sofa",
    "Baby Face Cream Cushion",
    "Face Cream Travel Jars",
    "Face Cream Sample Pots",
)
#: The three class rows the committed Elasticsearch proof pins keep their titles (gen#542).
PINNED = frozenset({"PLT-FCDAYC", "PLT-FCNGHT", "PLT-FCCALM"})
#: "Renewal Night Face Cream with Retinol": a real cream's title says more than the type.
MIN_TITLE_WORDS = 6


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _bm25(words: list[str], term: str) -> float:
    tf = words.count(term)
    if not tf:
        return 0.0
    idf = math.log(1 + (DOCS - DF[term] + 0.5) / (DF[term] + 0.5))
    return idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(words) / AVGDL))


def _score(rec: dict) -> float:
    words = _words(rec["title"])
    query = _words(QUERY)
    base = sum(_bm25(words, t) for t in query)
    typed = TYPED_WORD ** sum(1 for t in query if t in words)
    phrase = PHRASE if f" {QUERY} " in f" {' '.join(words)} " else 1.0
    popularity = 1 + export.merchandising(rec) / 100 + (rec.get("sold_last_5_days") or 0) / 10000
    return base * typed * phrase * popularity


@cache
def _records() -> tuple[dict, ...]:
    """Every record whose title holds a word of the query."""
    query = set(_words(QUERY))
    return tuple(r for r in ceiling_build().records if query & set(_words(r["title"])))


@cache
def _scores() -> dict[str, float]:
    return {r["product_id"]: _score(r) for r in _records()}


def _by_title() -> dict[str, dict]:
    return {r["title"]: r for r in _records()}


def _ids() -> set[str]:
    """The decoys of the issue, by product id."""
    found = _by_title()
    return {found[t]["product_id"] for t in TITLES if t in found}


def _top() -> list[str]:
    scores = _scores()
    return sorted(scores, key=lambda pid: (-scores[pid], pid))[:TOP]


def test_the_issue_titles_are_decoys_of_the_query() -> None:
    found = _by_title()
    assert sorted(t for t in TITLES if t in found) == sorted(TITLES)
    for title in TITLES:
        assert dr.BY_ID[found[title]["product_id"]].query == QUERY, title


def test_every_decoy_title_holds_the_typed_phrase() -> None:
    for title in TITLES:
        assert f" {QUERY} " in f" {' '.join(_words(title))} ", title


def test_a_plain_match_shows_three_decoys_in_the_top_twelve() -> None:
    top = _top()
    assert len(set(top) & _ids()) >= MIN_DECOYS, top


def test_a_decoy_is_sure_of_its_place_whatever_the_ties() -> None:
    """A decoy counts only when no more than twelve products, ties included, score as high."""
    scores = _scores()
    assert _ids(), "no face cream decoys"
    sure = [i for i in _ids() if sum(1 for v in scores.values() if v >= scores[i] - 1e-9) <= TOP]
    assert len(sure) >= MIN_DECOYS, sorted(scores.values(), reverse=True)[:TOP]


def test_no_decoy_is_a_face_cream_so_interpretation_drops_it() -> None:
    """The Face Creams route of class 12 boosts the leaf; a decoy outside it falls below."""
    found = _by_title()
    for title in TITLES:
        doc = found[title]
        assert doc["product_type"] != "Face Cream", title
        assert not any("face cream" in node.lower() for node in doc["category_path"]), title


def test_real_face_cream_titles_are_not_short() -> None:
    real = {r["product_id"]: r["title"] for r in _records()
            if r["product_type"] == "Face Cream" and r["product_id"] not in PINNED
            and not r["product_id"].startswith("PLT-D")}  # fmt: skip
    assert len(real) >= 20, len(real)
    short = {p: t for p, t in real.items() if len(_words(t)) < MIN_TITLE_WORDS}
    assert short == {}
