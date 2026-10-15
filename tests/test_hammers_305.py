"""One Hammers category with several kinds of hammer, and one ``product_type`` format (#305).

Read off the COMMITTED catalogs (``golden-catalog/`` for the modelled tools,
``prototypes/retail_drawings`` for the retail styles), so a regenerated catalog from a
broken generator is still red: ``test_catalog_golden.py`` holds the committed files to the
build.
"""

from __future__ import annotations

import collections
import json
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
