"""A plain search for "socks" meets believable products that are not socks (gen#774).

The top 24 products of a plain ``multi_match`` for ``socks`` were all real socks, so the demo had
nothing to show between interpretation off and on. A real boot sock's ``text`` field says "socks"
three times (title, category node, category leaf) and is short, which beats any field a decoy with
one mention can reach. So each decoy here says the word three times in a short description, and a
real sock's title is long enough that its ``text`` no longer takes every place on length alone.

``_plain_scores`` is the ``multi_match`` over ``title``, ``description`` and ``text``, the score
of the best field, on the ``text`` a flat document carries. ``STATS`` holds what
``catalog_combined_2026-11-01a`` answered in ``_explain`` for the term ``socks``, so the test reads
fixed numbers and no cluster.
"""

from __future__ import annotations

import importlib
import json
import math
import re
from collections import Counter
from functools import cache

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core import standard
from synthetic_ecommerce_data.domains.retail import decoy_contract, export
from synthetic_ecommerce_data.domains.retail import decoy_product_words as dpw

#: Documents of the index, and per field the documents holding ``socks`` and the mean length.
DOCS = 309626
STATS = {
    "title": (402, 8.842352),
    "description": (410, 33.590908),
    "text": (414, 37.457554),
}
K1, B = 1.2, 0.75
QUERY = "socks"
TOP = 12
MIN_DECOYS = 3
#: The fewest words a real sock's title may have: "Mens Bamboo Ankle Socks" was four.
MIN_TITLE_WORDS = 5
MIN_BOOT_TITLE_WORDS = 7
MENTIONS = 3
CABLE_MENTIONS = 1
SPILL_SOCKS = "synthetic_ecommerce_data.domains.industrial.product_types.safety.spill_socks"
#: The apparel decoys of classes 1, 2, 6 and 7, and the men's decoys of classes 6 and 7: their class
#: holds them to a shape of their own.
SHORT_BY_RULE = re.compile(r"[A-Z]+-(D(A\d\d|SSCHOOL_SOCKS)[1267]\d\d|MDS\d\d[67]\d)")
#: The apparel decoys of the other classes, whose title takes the detail of ``sock_titles``.
GENERATED_BOOT_SOCK = re.compile(r"PLT-DA\d\d[0345]\d\d")
SOCK_TYPES = ("Socks", "Boot Socks", "School Socks")
TITLES = (
    "Moisturising Gel Socks",
    "Exfoliating Foot Peel Socks",
    "Mesh Wash Bag for Socks",
    "Socks and Underwear Drawer Organiser",
    "Socks Puppet Craft Kit",
    "Cable Pulling Socks",
)


def _words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9']+", text.lower())


def _bm25(field: str, value: str) -> float:
    tokens = _words(value)
    tf = tokens.count(QUERY)
    if not tf:
        return 0.0
    n, avgdl = STATS[field]
    idf = math.log(1 + (DOCS - n + 0.5) / (n + 0.5))
    return idf * tf * (K1 + 1) / (tf + K1 * (1 - B + B * len(tokens) / avgdl))


@cache
def _records() -> tuple[dict, ...]:
    """Every record of the build that says the word, in any field."""
    return tuple(r for r in ceiling_build().records if QUERY in json.dumps(r).lower())


@cache
def _plain_scores() -> dict[str, float]:
    """product id -> the best score of its SKUs."""
    best: Counter[str] = Counter()
    for rec in _records():
        flat = standard.flat_documents(export.standard_document(rec), export.NUMERIC_FACTS)
        for doc in flat:
            score = max(_bm25(f, doc.get(f, "")) for f in STATS)
            best[doc["product_id"]] = max(best[doc["product_id"]], score)
    return dict(best)


def _rows() -> list[dpw.Row]:
    return [r for r in dpw.ROWS if r.query == QUERY]


def _ids() -> set[str]:
    return {f"PLT-{r.code}" for r in _rows()}


def _top() -> list[str]:
    scores = _plain_scores()
    return sorted(scores, key=lambda pid: (-scores[pid], pid))[:TOP]


def test_the_issue_titles_are_decoys_of_the_query() -> None:
    assert sorted(r.title for r in _rows()) == sorted(TITLES)


def test_every_decoy_title_holds_the_plural() -> None:
    assert _rows()
    for row in _rows():
        assert QUERY in _words(row.title), row.title


def test_a_plain_match_shows_three_decoys_in_the_top_twelve() -> None:
    assert _ids(), "no socks decoys"
    top = _top()
    assert len(set(top) & _ids()) >= MIN_DECOYS, top


def test_a_decoy_is_sure_of_its_place_whatever_the_ties() -> None:
    """A decoy counts only when no more than twelve products, ties included, score as high."""
    scores = _plain_scores()
    assert _ids() <= set(scores), sorted(_ids() - set(scores))
    sure = [i for i in _ids() if sum(1 for v in scores.values() if v >= scores[i] - 1e-9) <= TOP]
    assert len(sure) >= MIN_DECOYS, sorted(scores.values(), reverse=True)[:TOP]


def test_real_sock_titles_are_not_short() -> None:
    socks = {r["product_id"]: r["title"] for r in ceiling_build().records
             if r["product_type"] in SOCK_TYPES and QUERY in _words(r["title"])}  # fmt: skip
    assert len(socks) > 100
    short = {p: t for p, t in socks.items()
             if len(_words(t)) < MIN_TITLE_WORDS and not SHORT_BY_RULE.fullmatch(p)}  # fmt: skip
    assert short == {}


def test_a_generated_boot_sock_title_is_the_longest() -> None:
    """A boot sock has the shortest ``text`` of the sock types, so its title adds the most."""
    boots = {r["product_id"]: r["title"] for r in ceiling_build().records
             if r["product_type"] == "Boot Socks"
             and GENERATED_BOOT_SOCK.fullmatch(r["product_id"])}  # fmt: skip
    assert boots
    assert {p: t for p, t in boots.items() if len(_words(t)) < MIN_BOOT_TITLE_WORDS} == {}


def test_each_decoy_but_the_cable_grip_says_the_word_three_times() -> None:
    """Three mentions in a short description is the shape that reaches a boot sock's score."""
    counts = {r.title: _words(r.desc).count(QUERY) for r in _rows()}
    assert counts.pop("Cable Pulling Socks") == CABLE_MENTIONS
    assert set(counts.values()) == {MENTIONS}


def test_no_decoy_sits_in_a_socks_node() -> None:
    """The category policy keeps the Socks nodes in Best, so a decoy outside them is dropped."""
    docs = dpw.docs()
    found = [d for d in docs if d["product_id"] in _ids()]
    assert len(found) == len(TITLES)
    for doc in found:
        assert not any("sock" in node.lower() for node in doc["category_path"]), doc["title"]
        assert not decoy_contract.matches(QUERY, doc), doc["title"]


def test_each_decoy_declares_the_category_policy() -> None:
    assert _rows()
    assert {r.policy for r in _rows()} == {"category"}


def test_the_industrial_spill_socks_serve_the_query() -> None:
    row = importlib.import_module(SPILL_SOCKS).SPEC.breadth
    assert QUERY in _words(row.item)
    assert not any("sock" in node.lower() for node in row.category)
