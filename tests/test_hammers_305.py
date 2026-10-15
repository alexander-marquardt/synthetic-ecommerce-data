"""One Hammers category with several kinds of hammer, and one ``product_type`` format (#305).

Read off the COMMITTED catalogs (``golden-catalog/`` for the modelled tools,
``prototypes/retail_drawings`` for the retail styles), so a regenerated catalog from a
broken generator is still red: ``test_catalog_golden.py`` holds the committed files to the
build.
"""

from __future__ import annotations

import collections
import json
import math
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402

#: The one node every hammer lives under: the combined tree reads ``Tools > Hand Tools > Hammers``.
HAMMERS = ["Hand Tools", "Hammers"]

KINDS = frozenset({
    "hammer_ball_pein",
    "hammer_claw",
    "hammer_framing",
    "hammer_club",
    "hammer_sledge",
    "hammer_rubber_mallet",
    "hammer_dead_blow",
})

#: A product type is a snake_case id.
SNAKE = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)*$")


@pytest.fixture(scope="module")
def tools() -> list[dict]:
    with (ROOT / "golden-catalog" / "flat.jsonl").open() as f:
        return [json.loads(line) for line in f]


@pytest.fixture(scope="module")
def retail() -> list[dict]:
    return scale.templates()


def _is_hammer(doc: dict) -> bool:
    key = doc["product_type"].lower().replace(" ", "_")
    return "hammer" in key or "mallet" in key


def test_every_hammer_is_under_the_one_hammers_node(tools, retail) -> None:
    hammers = [d for d in (*tools, *retail) if _is_hammer(d)]
    assert hammers
    stray = collections.Counter(
        (d["product_type"], tuple(d["category_path"]))
        for d in hammers
        if d["category_path"] != HAMMERS
    )
    assert dict(stray) == {}


def test_at_least_six_kinds_are_present_and_they_are_the_declared_ones(tools) -> None:
    kinds = {d["product_type"] for d in tools if d["category_path"] == HAMMERS}
    assert len(kinds) >= 6
    assert kinds == KINDS


def test_the_composite_parents_are_gone(tools) -> None:
    levels = {level for d in tools for level in d["category_path"]}
    assert levels & {"Hammers, Striking & Demolition Tools", "Hammers & Mallets"} == set()


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_each_kind_has_several_brands_and_sizes_and_the_hammer_attributes(tools, kind) -> None:
    docs = [d for d in tools if d["product_type"] == kind]
    assert len({d["brand"] for d in docs}) >= 3
    by_name = collections.defaultdict(set)
    for d in docs:
        for a in d["attributes"]:
            by_name[a["name"]].add(a["value"])
    for name in ("Head Weight", "Handle Material", "Face Dia.", "Overall Length"):
        assert name in by_name, (kind, name)
    assert len(by_name["Head Weight"]) >= 3


def test_every_hammer_product_type_is_a_snake_case_id(tools, retail) -> None:
    bad = sorted({d["product_type"] for d in (*tools, *retail) if _is_hammer(d)} - KINDS)
    assert bad == []
    assert all(SNAKE.match(k) for k in KINDS)


def test_no_category_leaf_mixes_product_type_formats(tools, retail) -> None:
    """A leaf whose products are snake_case ids for some and display names for others."""
    formats: dict[tuple[str, ...], set[bool]] = collections.defaultdict(set)
    for d in (*tools, *retail):
        formats[tuple(d["category_path"])].add(bool(SNAKE.match(d["product_type"])))
    assert [path for path, seen in formats.items() if len(seen) > 1] == []


def test_no_product_concept_is_spelled_in_both_formats(tools, retail) -> None:
    """``Claw Hammer`` and ``hammer_claw`` / ``claw_hammer`` would be one concept twice."""
    types = {d["product_type"] for d in (*tools, *retail)}
    spelled = collections.defaultdict(set)
    for t in types:
        spelled[re.sub(r"[^a-z0-9]+", "_", t.lower()).strip("_")].add(t)
    assert {k: v for k, v in spelled.items() if len(v) > 1} == {}


# -- text-match decoys (gen#294 rule): every hammer kind carries them, attributes stay true ----

#: What each decoy class puts in the title (the item), by its shape.
#: (A brand's voice may put a qualifier before the item, so each shape is searched for.)
CATEGORY_WORD = re.compile(
    r"\b(?P<noun>Ball Pein|Claw|Framing|Club|Sledge|Mallet|Dead Blow) Series\b"
)
MATERIAL_LOOK = re.compile(r"\b(?P<word>Hickory|Ash|Fiberglass)-Look\b")
INCIDENTAL = re.compile(r"\b(?P<word>Hickory|Ash|Fiberglass) (?:Creek|Ridge|Lane|Hollow)\b")
OWN_NOUN = {
    "hammer_ball_pein": "Ball Pein", "hammer_claw": "Claw", "hammer_framing": "Framing",
    "hammer_club": "Club", "hammer_sledge": "Sledge", "hammer_rubber_mallet": "Mallet",
    "hammer_dead_blow": "Dead Blow",
}


def _lines(tools: list[dict], kind: str) -> dict[str, dict]:
    """One doc per product of ``kind``, with its handle material."""
    out: dict[str, dict] = {}
    for d in tools:
        if d["product_type"] == kind:
            handle = next(a["value"] for a in d["attributes"] if a["name"] == "Handle Material")
            out.setdefault(d["product_id"], {"title": d["parent_title"], "handle": handle})
    return out


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_each_kind_carries_three_decoys_of_each_class_and_their_attributes_stay_true(
    tools, kind
) -> None:
    lines = _lines(tools, kind)
    category, material, incidental = [], [], []
    for line in lines.values():
        item = line["title"].split(" -- ")[-1]
        if (m := CATEGORY_WORD.search(item)) is not None:
            category.append(m["noun"])
        elif (m := MATERIAL_LOOK.search(item)) is not None:
            material.append(m["word"])
            assert m["word"] != line["handle"], line
        elif (m := INCIDENTAL.search(item)) is not None:
            incidental.append(m["word"])
            assert m["word"] != line["handle"], line
    assert len(category) >= 3 and len(material) >= 3 and len(incidental) >= 3, (
        kind, len(category), len(material), len(incidental))
    # The category word is ANOTHER kind's noun, never the kind's own.
    assert OWN_NOUN[kind] not in category
    assert set(category) <= set(OWN_NOUN.values())


ITEM = {
    "hammer_ball_pein": "Ball Pein Hammer", "hammer_claw": "Claw Hammer",
    "hammer_framing": "Framing Hammer", "hammer_club": "Club Hammer",
    "hammer_sledge": "Sledge Hammer", "hammer_rubber_mallet": "Rubber Mallet",
    "hammer_dead_blow": "Dead Blow Hammer",
}


def _incidental_docs(tools: list[dict], kind: str) -> list[dict]:
    return [
        d for d in tools if d["product_type"] == kind and INCIDENTAL.search(d["title"])
    ]


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_every_incidental_word_decoy_indexed_title_is_five_words_or_fewer(tools, kind) -> None:
    """gen#320: the INDEXED ``title`` (brand, qualifier and size included) is 5 words or fewer.

    The rule of gen#294 (c6178459887) puts the incidental word in a short title so text
    search ranks the decoy above real hits; the SKU title is what is indexed.
    """
    docs = _incidental_docs(tools, kind)
    assert len(docs) >= 3
    counts = {d["title"]: len(d["title"].split()) for d in docs}
    assert max(counts.values()) <= 5, (kind, counts)
    # gen#311: the decoy title names only the misleading word.
    assert all(ITEM[kind] in t for t in counts), counts


def _tokens(text: str) -> list[str]:
    return re.findall(r"\w+", text.lower())


def _bm25_ranking(docs: list[dict], query: list[str]) -> list[dict]:
    """A no-policy BM25 (k1=1.2, b=0.75) over the ``title`` field, best first."""
    tokenised = [_tokens(d["title"]) for d in docs]
    avg = sum(map(len, tokenised)) / len(tokenised)
    n = len(docs)
    df = {q: sum(q in t for t in tokenised) for q in query}
    scored = []
    for d, toks in zip(docs, tokenised, strict=True):
        score = 0.0
        for q in query:
            tf = toks.count(q)
            if tf:
                idf = math.log(1 + (n - df[q] + 0.5) / (df[q] + 0.5))
                score += idf * tf * 2.2 / (tf + 1.2 * (0.25 + 0.75 * len(toks) / avg))
        scored.append((score, d))
    # Ties break by title length, then by title: a stable, policy-free order.
    scored.sort(key=lambda p: (-p[0], len(p[1]["title"]), p[1]["title"]))
    return [d for score, d in scored if score > 0]


@pytest.mark.parametrize("kind", sorted(KINDS))
def test_an_incidental_word_decoy_is_in_the_top_three_for_each_of_its_queries(tools, kind) -> None:
    """gen#320: in the no-policy proxy a decoy outranks the real hits, for the bare word
    (a decoy of any kind) and for the word with the kind's item (a decoy of this kind)."""
    every = {d["sku"] for k in KINDS for d in _incidental_docs(tools, k)}
    by_word: dict[str, set[str]] = collections.defaultdict(set)
    for d in _incidental_docs(tools, kind):
        by_word[INCIDENTAL.search(d["title"])["word"]].add(d["sku"])
    assert by_word
    for word, skus in by_word.items():
        for query, wanted in ((word, every), (f"{word} {ITEM[kind]}", skus)):
            ranked = _bm25_ranking(tools, _tokens(query))
            assert {d["sku"] for d in ranked[:3]} & wanted, (
                query, [d["title"] for d in ranked[:3]])
