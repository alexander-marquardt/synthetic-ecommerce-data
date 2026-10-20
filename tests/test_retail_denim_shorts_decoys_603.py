"""Decoys of "denim shorts": the query fails without interpretation (gen#603).

With interpretation off, ``denim shorts`` must not be answered by the real denim shorts alone.
Three kinds of decoy hold the words with the wrong product, and every one keeps its structured
fields true (the fabric above all). The real denim shorts carry titles long enough to name a cut,
a rise, a wash or a length, as a shop's would, and the decoys are about as long, so the title-length
normalisation of a text search does not put the real ones first.
"""

from __future__ import annotations

import re
import statistics
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

QUERY = "denim shorts"
#: The fabric each decoy pair of shorts truly has. A row of another product type has none.
TRUE_FABRIC = {
    "DS01": "Linen",
    "DS02": "Jersey",
    "DS03": "Cotton",
    "DS04": "Cotton",
    "DS05": "Jersey",
    "DS06": "Cotton Jersey",
}
#: A real title names the cut, the rise, the wash or the length.
NAMES_A_DETAIL = {"rise", "length", "wash", "fit", "hem", "cut-off", "longline", "turn-up"}
BARE_TITLES = {"denim shorts", "mini denim shorts"}


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z][a-z-]*", text.lower())


def _fabric(doc: dict) -> str | None:
    values = [a["value"] for a in doc.get("attributes", []) if a["key"] == "fabric"]
    return values[0] if values else None


@cache
def _rows() -> tuple[dr.Decoy, ...]:
    return tuple(d for d in dr.TABLE if d.query == QUERY)


@cache
def _docs() -> dict[str, dict]:
    """The decoy documents, by row code."""
    return {d.code: doc for d, doc in zip(dr.TABLE, dr.docs(), strict=True) if d.query == QUERY}


@cache
def _real() -> tuple[dict, ...]:
    """The real denim shorts: a Shorts leaf whose fabric is Denim."""
    return tuple(
        t
        for t in scale.templates()
        if t["category_path"][-1] == "Shorts"
        and _fabric(t) == "Denim"
        and not t["product_id"].startswith("PLT-D")
    )


def _leaf(doc: dict) -> str:
    return doc["category_path"][-1]


def test_the_table_holds_decoys_of_denim_shorts() -> None:
    assert len(_rows()) >= 8, "expected the decoys of three kinds for 'denim shorts'"


def test_a_decoy_is_one_of_the_three_kinds() -> None:
    docs = _docs()
    # (a) shorts that are not denim, with "denim" as a color or a look in the title.
    a = [
        c
        for c, doc in docs.items()
        if _leaf(doc) == "Shorts" and "denim" in _tokens(doc["title"]) and _fabric(doc) != "Denim"
    ]
    # (b) shorts sold with, or worn with, a denim item.
    b = [
        c
        for c, doc in docs.items()
        if _leaf(doc) == "Shorts"
        and "denim" in _tokens(doc["title"] + " " + doc["description"])
        and re.search(r"denim (belt bag|jacket)", doc["title"].lower())
    ]
    # (c) denim items that are not shorts but say shorts.
    c = [
        k for k, doc in docs.items() if _leaf(doc) != "Shorts" and "shorts" in _tokens(doc["title"])
    ]
    assert len(a) >= 3, a
    assert len(b) >= 2, b
    assert {_leaf(docs[k]) for k in c} >= {"Denim Jackets", "Hangers"}, c


def test_each_decoy_keeps_its_true_fabric() -> None:
    docs = _docs()
    assert set(TRUE_FABRIC) <= set(docs)
    for code, fabric in TRUE_FABRIC.items():
        assert _leaf(docs[code]) == "Shorts", code
        assert _fabric(docs[code]) == fabric, (code, docs[code]["title"])
    for code, doc in docs.items():
        if code not in TRUE_FABRIC:
            assert _leaf(doc) != "Shorts", code
            assert _fabric(doc) is None, code


def test_no_decoy_pair_of_shorts_is_denim() -> None:
    for code, doc in _docs().items():
        if _leaf(doc) == "Shorts":
            assert _fabric(doc) not in (None, "Denim"), code


def test_the_real_denim_shorts_have_detailed_titles() -> None:
    real = _real()
    assert len(real) >= 2
    for t in real:
        title = t["title"]
        assert title.lower() not in BARE_TITLES, title
        assert NAMES_A_DETAIL & set(_tokens(title)), title


def test_the_decoys_are_about_as_long_as_the_real_titles() -> None:
    assert _rows(), "no decoys of 'denim shorts' to measure"
    real = statistics.median(len(t["title"].split()) for t in _real())
    decoy = statistics.median(len(d.title.split()) for d in _rows())
    assert abs(real - decoy) <= 1.5, (real, decoy)
    for d in _rows():
        assert 5 <= len(d.title.split()) <= 10, d.title


@cache
def _index() -> br.Index:
    return br.Index(scale.build(10**6).records)


def test_a_raw_search_shows_four_decoys_in_the_first_twelve() -> None:
    mine = {f"PLT-D{d.code}" for d in _rows()}
    top = [d["product_id"] for d in br.rank(_index(), QUERY, 12)]
    assert len(mine & set(top)) >= 4, top


@pytest.mark.parametrize("title", sorted(BARE_TITLES))
def test_no_product_is_titled_only_denim_shorts(title: str) -> None:
    found = [t["product_id"] for t in scale.templates() if t["title"].lower() == title]
    assert not found, found
