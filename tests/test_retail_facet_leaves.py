"""A jean's fit and a bra's shape are filters, not category leaves (``facet_leaves``).

The build filed every jean under a fit leaf (``Women/Jeans/Skinny Jeans``) and every bra
under one of about 50 style leaves, so a "skinny" or "plunge" filter was a tree walk and the
same fact lived twice. Those leaves collapse into ``<Root>/Jeans``, ``<Root>/Trousers`` and
``Women/Lingerie/Bras`` (its purpose nodes stay), and their facts are the facets the
downstream attribute markers read: ``leg_fit``, ``rise``, ``length``, ``wiring``,
``bra_shape``, ``padding``, ``back_style`` and ``fabric``.

Every test reads the seed-0 build run to its ceiling, once.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import facet_leaves  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import words  # noqa: E402

#: The facet names the downstream attribute markers read, by the product type that has them.
CONTRACT = {
    "Jeans": {"leg_fit", "rise", "length"},
    "Bra": {"wiring", "bra_shape", "padding", "back_style", "fabric"},
}
#: The facets whose values a collapsed leaf named.
LEAF_FACETS = ("leg_fit", "bra_shape", "padding", "back_style", "fabric")
KIND_NODES = {"Jeans": "Jeans", "Trousers": "Trousers", "Bra": "Bras"}


@pytest.fixture(scope="module")
def built():
    return scale.build(10_000_000)


@pytest.fixture(scope="module")
def docs(built):
    return scale.documents(built)


@pytest.fixture(scope="module")
def rows(docs):
    return scale.flat(docs)


@pytest.fixture(scope="module")
def pairs(built, docs):
    """(build record, its document) for every jean, pair of trousers and bra."""
    both = zip(built.records, docs, strict=True)
    return [(r, d) for r, d in both if r["product_type"] in KIND_NODES]


@pytest.fixture(scope="module")
def values(rows):
    """facet key -> every value the catalog's jeans, trousers and bras hold for it."""
    out = collections.defaultdict(set)
    for r in rows:
        if r["product_type"] in KIND_NODES:
            for key in LEAF_FACETS:
                out[key].update(r["facets"].get(key, ()))
    return out


def _named(text: str, value: str) -> bool:
    return f" {words(value).strip()} " in words(text)


def test_no_node_under_jeans_trousers_or_bras_names_a_filter_value(rows, values):
    assert all(values[k] for k in LEAF_FACETS)
    bad = set()
    for r in rows:
        node = KIND_NODES.get(r["product_type"])
        if node is None:
            continue
        below = r["category_path"][r["category_path"].index(node) + 1:]
        bad |= {(n, k, v) for n in below for k in LEAF_FACETS for v in values[k] if _named(n, v)}
    assert not bad


def test_jeans_and_trousers_end_at_their_kind_node(rows):
    ends = collections.Counter(
        (r["product_type"], r["category_path"][-1]) for r in rows
        if r["product_type"] in ("Jeans", "Trousers")
    )  # fmt: skip
    assert set(ends) == {("Jeans", "Jeans"), ("Trousers", "Trousers")}
    roots = {(r["category_path"][0], r["product_type"]) for r in rows
             if r["product_type"] in ("Jeans", "Trousers")}  # fmt: skip
    assert {("Women", "Jeans"), ("Men", "Jeans"), ("Women", "Trousers")} <= roots


def test_the_purpose_nodes_are_the_only_children_of_bras(rows):
    paths = {tuple(r["category_path"]) for r in rows if r["product_type"] == "Bra"}
    base = ("Women", "Lingerie", "Bras")
    assert base in paths
    assert {p[len(base):] for p in paths} == {()} | {(n,) for n in facet_leaves.PURPOSE_BRAS}
    assert all(p[: len(base)] == base for p in paths)


def test_every_jean_has_a_leg_fit_and_every_bra_a_bra_shape(rows):
    for r in rows:
        if r["product_type"] in ("Jeans", "Trousers"):
            fits = r["facets"].get("leg_fit", [])
            assert fits and fits[1:] in ([], [facet_leaves.CROPPED]), r["product_id"]
        if r["product_type"] == "Bra":
            assert len(r["facets"].get("bra_shape", ())) == 1, r["product_id"]


def test_bra_style_and_leg_style_are_gone(docs, rows):
    keys = {a["key"] for d in docs for a in d["attributes"]}
    assert not keys & {"bra_style", "leg_style"}
    assert not {k for r in rows for k in r["facets"]} & {"bra_style", "leg_style"}


def test_the_downstream_marker_fields_are_on_jeans_and_bras(rows):
    held = collections.defaultdict(set)
    for r in rows:
        held[r["product_type"]] |= set(r["facets"])
    for ptype, keys in CONTRACT.items():
        assert keys <= held[ptype], (ptype, keys - held[ptype])


def test_every_value_the_old_leaf_named_is_a_facet_value(pairs, values):
    for rec, doc in pairs:
        leaf = rec["category_path"][-1]
        have = {(a["key"], a["value"]) for a in doc["attributes"]}
        for key in LEAF_FACETS:
            named = {v for v in values[key] if _named(leaf, v)}
            # "Super Skinny" also names "Skinny"; the longest value is the leaf's.
            named = {v for v in named if not any(v != w and _named(w, v) for w in named)}
            if named:
                assert {(key, v) for v in named} <= have, (rec["product_id"], leaf, key)


def test_a_bra_keeps_each_fact_its_old_leaf_implied(pairs):
    for rec, doc in pairs:
        if rec["product_type"] != "Bra":
            continue
        want = [
            [f] if isinstance(f, str) else list(f or ())
            for f in facet_leaves.BRA_LEAVES[rec["category_path"][-1]]
        ]
        attrs = doc["attributes"]
        got = [[a["value"] for a in attrs if a["key"] == k] for k in facet_leaves.BRA_KEYS]
        # The leaf's facts are all there; the text may state more (the next test).
        assert all(set(w) <= set(g) for g, w in zip(got, want, strict=True)), rec["product_id"]


def test_a_bra_fibre_content_moves_to_composition(pairs):
    moved = 0
    for rec, doc in pairs:
        old = [a["value"] for a in rec["attributes"] if a["key"] == "fabric"]
        if rec["product_type"] == "Bra" and old:
            assert [a["value"] for a in doc["attributes"] if a["key"] == "composition"] == old
            moved += 1
    assert moved


def test_a_jean_keeps_the_fit_its_old_leaf_named(pairs):
    for rec, doc in pairs:
        leaf = rec["category_path"][-1]
        fit = [a["value"] for a in doc["attributes"] if a["key"] == "leg_fit"]
        if rec["product_type"] in ("Jeans", "Trousers") and leaf != rec["product_type"]:
            assert fit[:1] == [leaf.rsplit(" ", 1)[0]], (rec["product_id"], leaf)


def test_a_jean_whose_text_says_cropped_is_also_cropped(pairs):
    cropped = 0
    for rec, doc in pairs:
        if rec["product_type"] not in ("Jeans", "Trousers"):
            continue
        fits = [a["value"] for a in doc["attributes"] if a["key"] == "leg_fit"]
        said = _named(f"{rec['title']} {rec.get('description', '')}", "Cropped")
        assert ("Cropped" in fits) == said, (rec["product_id"], fits)
        cropped += said and fits[0] != "Cropped"
    assert cropped  # a cropped balloon or barrel jean, filed under its own fit


def test_titles_and_image_ids_are_the_build_records(pairs):
    assert pairs
    for rec, doc in pairs:
        assert doc["title"] == rec["title"]
        assert doc["image_id"] == export.image_id(rec, rec["skus"][0])
        assert doc["product_type"] == rec["product_type"]
        if rec["product_type"] in ("Jeans", "Trousers"):
            fits = [a["value"] for a in doc["attributes"] if a["key"] == "leg_fit"]
            assert fits and _named(rec["title"], fits[0]), (rec["product_id"], fits)


def test_the_kind_node_is_the_product_type(rows):
    for r in rows:
        node = KIND_NODES.get(r["product_type"])
        if node:
            assert r["category_path"][-1] in {node, *facet_leaves.PURPOSE_BRAS}
            assert r["category_leaf"] == r["category_path"][-1]


def test_no_facet_has_two_values_that_differ_only_in_case_or_hyphenation(rows):
    seen = collections.defaultdict(lambda: collections.defaultdict(set))
    for r in rows:
        for key, vals in r["facets"].items():
            for v in vals:
                # "Push-Up" and "Push Up" are one value; "3-4" (years) and "34" are two.
                seen[key][re.sub(r"[\s\-_]+", " ", str(v).lower()).strip()].add(v)
    split = {k: [sorted(vs) for vs in by.values() if len(vs) > 1] for k, by in seen.items()}
    assert not {k: v for k, v in split.items() if v}


def test_wiring_has_one_non_wired_spelling(rows):
    wiring = {v for r in rows for v in r["facets"].get("wiring", ())}
    assert wiring == {"Underwired", "Non-Wired"}


def _longest_named(text: str, vocab: set[str]) -> set[str]:
    named = {v for v in vocab if _named(text, v)}
    return {v for v in named if not any(v != w and _named(w, v) for w in named)}


def test_a_bra_carries_every_value_its_title_names(pairs, values):
    """The leaf is not the only place a bra states a shape, padding, back or fabric: a "Lace
    Demi Cup Bra" sits under Demi Cup Bras, so only the title says Lace. A key the document
    lacks is never judged by ``text_contradictions``, so this reads the missing ones."""
    checked = 0
    for rec, doc in pairs:
        if rec["product_type"] != "Bra":
            continue
        text = rec["title"]  # a description denies ("non padded") or lists fibres
        for key in facet_leaves.BRA_KEYS:
            have = {a["value"] for a in doc["attributes"] if a["key"] == key}
            named = _longest_named(text, values[key])
            assert named <= have, (rec["product_id"], rec["title"], key, named - have)
            checked += bool(named)
    assert checked


#: Fabric values that name only a fibre. A shopper filters these under Composition; ``Linen``
#: and ``Cotton`` are left out because a bra's lace-or-cotton cup and a linen cushion are
#: fabrics a shopper names (the issue keeps them in ``fabric``).
FIBRE_ONLY = {
    "Organic Cotton", "Turkish Cotton", "Zero Twist Cotton", "Bamboo", "Polyester", "Elastane",
    "Recycled Polyester", "Recycled Polyamide", "Modal", "Viscose", "Wool", "Silk", "Nylon",
}  # fmt: skip


def _values(doc, key):
    return [a["value"] for a in doc["attributes"] if a["key"] == key]


def test_no_fabric_holds_fibre_content(built, docs):
    """``fabric`` is a fabric or weave a shopper names, never a percentage, a comma-joined
    fibre list or a fibre alone, on any product type (gen#166)."""
    bad = {
        (d["product_type"], v)
        for d in docs
        for v in _values(d, "fabric")
        if "%" in v or "," in v or v in FIBRE_ONLY
    }
    assert not bad
    assert any(_values(d, "fabric") for d in docs)


def test_fibre_content_moves_to_composition_on_every_type(built, docs):
    """A non-bra record's fibre content is its document's composition, and the fabric it
    held keeps only the fabric or weave ("100% Cotton Oxford" is an Oxford shirt)."""
    moved = collections.Counter()
    for rec, doc in zip(built.records, docs, strict=True):
        old = [a["value"] for a in rec["attributes"] if a["key"] == "fabric"]
        if rec["product_type"] == "Bra" or not old:
            continue
        fabric, composition = facet_leaves.FABRIC_MOVES.get(old[0], (old[0], None))
        assert _values(doc, "fabric") == ([fabric] if fabric else []), rec["product_id"]
        assert _values(doc, "composition") == ([composition] if composition else [])
        moved[rec["product_type"]] += bool(composition)
    assert {t for t, n in moved.items() if n} == {"Jeans", "Shirt", "Towel", "Soft Toy"}
