"""Jewellery and watches (gen#423): five spec types, each a shape of its own, with decoys.

The catalogue already sold necklaces, bracelets, rings (gen#207) and three earrings and watches
(the legacy tables), but held no hoop or drop earrings, no analog or digital watch and no
fitness band, and the legacy `Earrings` and `Watch` types cannot take spec rows (a type is
registered through a spec or the legacy list, never both: gen#413 slice 3 moves them). The five
types here are new product types beside them, one spec module each.

The query shapes of the issue are run on the baseline ranking (:mod:`baseline_rank`) of the
seed-0 build: a text-only query whose intended type must come first. A query that a policy
decides is held on the structured fields instead: "rose gold ring size N" (rose bouquets match
the words), and "womens watch 32 mm", "water resistant watch 100 m" and "black silicone watch"
(the baseline puts a dress, the legacy "Mesh Watch, 50m Water Resistance" and a sandal first:
the unit, the number and the color are what a policy reads, and the fields below carry them).
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

import baseline_rank as br  # noqa: E402
import kit  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

NEW_TYPES = ("Hoop Earrings", "Drop Earrings", "Analog Watch", "Digital Watch", "Fitness Band")
KEYS = {t: t.lower().replace(" ", "_") for t in NEW_TYPES}
#: The query shapes of the issue and the product types that must rank first (text only).
QUERIES = {
    "silver necklace": {"Necklace"},
    "gold hoop earrings": {"Hoop Earrings", "Earrings"},  # the legacy gold hoop is one too
    "pearl earrings": {"Drop Earrings", "Hoop Earrings"},
    "charm bracelet": {"Bracelet"},
    "mens leather strap watch": {"Analog Watch"},
    "fitness band": {"Fitness Band"},
    "drop earrings": {"Drop Earrings"},
}
SKU_GROWTH = 150


@pytest.fixture(scope="module")
def ceiling() -> list[dict]:
    return scale.build(10**6).records


@pytest.fixture(scope="module")
def index(ceiling: list[dict]) -> br.Index:
    return br.Index(ceiling)


@pytest.fixture(scope="module")
def templates() -> list[dict]:
    return scale.templates()


def _of(templates: list[dict], ptype: str) -> list[dict]:
    return [r for r in templates if r["product_type"] == ptype]


def test_the_five_types_are_specs_not_legacy_rows() -> None:
    assert {KEYS[t] for t in NEW_TYPES} <= set(type_registry.specs())
    assert (
        type_registry.registration_problems(
            {(r["department"][0], r["product_type"]) for r in scale.templates(baseline=False)}
        )
        == []
    )


@pytest.mark.parametrize("ptype", NEW_TYPES)
def test_each_type_has_two_styles_from_two_invented_brands(
    templates: list[dict], ptype: str
) -> None:
    rows = [r for r in _of(templates, ptype) if r["product_id"] not in scale.DECOY_IDS]
    assert len(rows) >= 2, ptype
    assert len({r["brand"] for r in rows}) >= 2, ptype


@pytest.mark.parametrize("ptype", NEW_TYPES)
def test_each_type_is_drawn_by_a_shape_of_its_own(templates: list[dict], ptype: str) -> None:
    shape = {r["drawing"]["shape"] for r in _of(templates, ptype)}
    assert len(shape) == 1 and shape <= set(kit.SHAPES), (ptype, shape)
    others = {
        r["drawing"]["shape"] for r in templates
        if r["product_type"] in NEW_TYPES and r["product_type"] != ptype
    }  # fmt: skip
    assert not shape & others, (ptype, shape & others)


@pytest.mark.parametrize("ptype", NEW_TYPES)
def test_each_type_carries_text_match_decoys_of_its_own_word(
    templates: list[dict], ptype: str
) -> None:
    spec = type_registry.specs().get(KEYS[ptype])
    assert spec is not None and len(spec.decoys) >= 2, ptype
    word = ptype.split()[0].lower()
    for d in spec.decoys:
        doc = next(r for r in templates if r["product_id"] == f"BRD-{d.row.code}")
        assert word in doc["title"].lower() or word in doc["description"].lower(), doc["title"]
        assert doc["product_type"] == ptype


def test_the_department_grows_by_at_least_150_skus(templates: list[dict]) -> None:
    n = sum(r["sku_count"] for r in templates if r["product_type"] in NEW_TYPES)
    assert n >= SKU_GROWTH, n


def _watches(ceiling: list[dict]) -> list[dict]:
    return [r for r in ceiling if r["product_type"] in ("Analog Watch", "Digital Watch")]


def _attr(rec: dict, key: str) -> str:
    return next((a["value"] for a in rec["attributes"] if a["key"] == key), "")


#: The queries a policy decides, each held on the fields instead: the baseline puts a dress, the
#: legacy "Mesh Watch, 50m Water Resistance" and a sandal first, so a text rank says nothing.
STRUCTURED = {
    "womens watch 32 mm": lambda ceiling: [
        r for r in _watches(ceiling)
        if _attr(r, "audience") == "Womens" and any(s.get("case_mm") == "32" for s in r["skus"])
    ],
    "water resistant watch 100 m": lambda ceiling: [
        r for r in _watches(ceiling) if _attr(r, "water_resistance") == "100"
    ],
    "black silicone watch": lambda ceiling: [
        r for r in ceiling
        if r["product_type"] == "Digital Watch" and _attr(r, "strap") == "Silicone"
        and any(s.get("color") == "Black" for s in r["skus"])
    ],
}  # fmt: skip


@pytest.mark.parametrize("query", sorted({*QUERIES, *STRUCTURED}))
def test_a_query_shape_ranks_its_type_first(
    index: br.Index, ceiling: list[dict], query: str
) -> None:
    if query in STRUCTURED:
        assert STRUCTURED[query](ceiling), query
        return
    top = br.rank(index, query, 1)[0]
    assert top["product_type"] in QUERIES[query], (query, top["product_type"], top["title"])


def test_rose_gold_ring_size_n_is_a_ring_sku(ceiling: list[dict]) -> None:
    """The words find rose bouquets (the "rose gold" color class); the fields tell the truth."""
    hits = [
        r for r in ceiling
        if r["product_type"] == "Ring"
        and any(s.get("metal", "").startswith("Rose Gold") and s.get("ring_size_uk") == "N"
                for s in r["skus"])
    ]  # fmt: skip
    assert hits


@pytest.mark.parametrize(
    ("ptype", "options"),
    [
        ("Analog Watch", {"leather", "mesh", "fabric"}),
        ("Digital Watch", {"silicone"}),
        ("Fitness Band", {"silicone"}),
    ],
)
def test_a_watch_states_its_strap_case_diameter_and_water_resistance(
    templates: list[dict], ptype: str, options: set[str]
) -> None:
    rows = _of(templates, ptype)
    keys = collections.Counter(a["key"] for r in rows for a in r["attributes"])
    for key in ("strap", "water_resistance", "audience"):
        assert keys[key] >= len(rows), (ptype, key)
    assert {
        a["value"].lower() for r in rows for a in r["attributes"] if a["key"] == "strap"
    } & options
    assert all(s.get("case_mm") for r in rows for s in r["skus"]), ptype


def _watches(ceiling: list[dict]) -> list[dict]:
    return [r for r in ceiling if r["product_type"] in ("Analog Watch", "Digital Watch")]


def _attr(rec: dict, key: str) -> str:
    return next((a["value"] for a in rec["attributes"] if a["key"] == key), "")


@pytest.mark.parametrize("ptype", ["Hoop Earrings", "Drop Earrings"])
def test_an_earring_color_is_always_a_metal(templates: list[dict], ptype: str) -> None:
    """The color of jewellery is its metal: the main-color completion (gen#275) must not give a
    pair of earrings a red or a blue, so each earring type is an excepted type."""
    colors = {c["color"] for r in _of(templates, ptype) for c in r["color_options"]}
    assert colors <= {"Gold", "Silver", "Rose Gold"}, (ptype, colors)
