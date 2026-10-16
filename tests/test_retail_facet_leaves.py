"""A jean's fit and a bra's shape are filters, not category leaves (``facet_leaves``).

The build filed every jean under a fit leaf (``Womens/Jeans/Skinny Jeans``) and every bra
under one of about 50 style leaves, so a "skinny" or "plunge" filter was a tree walk and the
same fact lived twice. Those leaves collapse into ``<Root>/Jeans``, ``<Root>/Trousers`` and
``Womens/Lingerie/Bras`` (its purpose nodes stay), and their facts are the facets the
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
    assert {("Womens", "Jeans"), ("Mens", "Jeans"), ("Womens", "Trousers")} <= roots


def test_the_purpose_nodes_are_the_only_children_of_bras(rows):
    paths = {tuple(r["category_path"]) for r in rows if r["product_type"] == "Bra"}
    base = ("Womens", "Lingerie", "Bras")
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


def test_a_bra_keeps_its_fibre_content_as_a_detail_and_its_fibre_as_fabric(pairs):
    moved = 0
    for rec, doc in pairs:
        old = [a["value"] for a in rec["attributes"] if a["key"] == "fabric"]
        if rec["product_type"] == "Bra" and old:
            assert doc["fibre_content"] == old[0]
            assert BRA_FIBRES[old[0]] in _values(doc, "fabric")
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


#: The closed list a ``fabric`` value comes from: the fibre or weave a shopper names (gen#187).
SHOPPER_FABRICS = {
    "Bamboo", "Boucle", "Chenille", "Corduroy", "Cotton", "Denim", "Faux Fur", "Faux Leather",
    "Flannel", "Fleece", "Jersey", "Knitted", "Lace", "Lace Trim", "Linen", "Mesh", "Microfiber",
    "Modal", "Nylon", "Oxford", "Plush", "Polyester", "Satin", "Seamless", "Shell", "Silk",
    "Suiting", "Towelling", "Tricot", "Twill", "Velour", "Velvet", "Waffle",
}  # fmt: skip
#: A bra's old ``fabric`` (its fibre content) -> the fibre a shopper names.
BRA_FIBRES = {
    "Cotton, Elastane": "Cotton",
    "Modal, Elastane": "Modal",
    "Recycled Polyamide, Elastane": "Nylon",
    "Recycled Polyester, Elastane": "Polyester",
}
#: A grade or a blend: never a ``fabric``.
GRADES = {"Organic Cotton", "Turkish Cotton", "Zero Twist Cotton", "Elastane", "Viscose"}


def _values(doc, key):
    return [a["value"] for a in doc["attributes"] if a["key"] == key]


def test_every_fabric_comes_from_the_closed_shopper_list(docs):
    """``fabric`` is a fibre or weave a shopper names, never a percentage, a comma-joined
    fibre list or a grade, on any product type (gen#166, gen#187)."""
    held = {v for d in docs for v in _values(d, "fabric")}
    assert held <= SHOPPER_FABRICS, held - SHOPPER_FABRICS
    assert not held & GRADES
    assert {"Cotton", "Linen", "Denim", "Oxford", "Flannel", "Bamboo", "Silk"} <= held


def test_no_retail_document_has_a_composition_attribute(docs):
    assert not {k for d in docs for k in (a["key"] for a in d["attributes"])} & {"composition"}
    assert not {k for d in docs for v in d["variants"] for k in (a["key"] for a in v["attributes"])
                } & {"composition"}  # fmt: skip


#: Each non-bra ``fabric`` value that is not itself a shopper fabric -> (its fabric, its blend).
MOVED = {
    "100% Cotton": ("Cotton", "100% Cotton"),
    "70% Cotton, 28% Polyester, 2% Elastane": ("Cotton", "70% Cotton, 28% Polyester, 2% Elastane"),
    "92% Cotton, 6% Polyester, 2% Elastane": ("Cotton", "92% Cotton, 6% Polyester, 2% Elastane"),
    "98% Cotton, 2% Elastane": ("Cotton", "98% Cotton, 2% Elastane"),
    "Bamboo": ("Bamboo", None),
    "Organic Cotton": ("Cotton", "Organic Cotton"),
    "Turkish Cotton": ("Cotton", "Turkish Cotton"),
    "Zero Twist Cotton": ("Cotton", "Zero Twist Cotton"),
    "100% Cotton Oxford": ("Oxford", "100% Cotton"),
    "Brushed Cotton Flannel": ("Flannel", "Cotton"),
    "Mid Weight Denim": ("Denim", None),
    "Washed Linen": ("Linen", None),
    "Cotton Blend": ("Cotton", "Cotton Blend"),
    "Cotton Jersey": ("Jersey", "Cotton"),
    "Silk Dupion": ("Silk", "Silk Dupion"),
}


#: A move that is a call on one product type's text, not a fact about the value (gen#291): the
#: tailored shorts' "Polyester Blend" is the suiting their description names.
TYPED_MOVED = {("Shorts", "Polyester Blend"): ("Suiting", "Polyester Blend")}


#: "Leather-Look" and "Leather Look" are one phrase; a guard reads both spellings (gen#291).
LEATHER_LOOK = re.compile(r"leather[\s-]*look", re.IGNORECASE)


def test_the_leather_look_guard_reads_both_spellings():
    """A guard that reads only the hyphen stays green over the space spelling, because the
    hyphenated class-4 decoys keep it non-empty (gen#291)."""
    assert all(LEATHER_LOOK.search(t) for t in ("Leather Look Bag", "Leather-Look Bag"))


def test_the_blend_is_a_detail_not_a_facet(built, docs):
    """A non-bra record's fabric is the fibre or weave a shopper names, and the blend or grade
    it held is the document's ``fibre_content``: a field, in no attribute and no facet."""
    moved = collections.Counter()
    for rec, doc in zip(built.records, docs, strict=True):
        old = [a["value"] for a in rec["attributes"] if a["key"] == "fabric"]
        assert "fibre_content" not in {a["key"] for a in doc["attributes"]}
        if rec["product_type"] == "Bra" or not old:
            continue
        fabric, blend = TYPED_MOVED.get(
            (rec["product_type"], old[0]), MOVED.get(old[0], (old[0], None)))
        assert _values(doc, "fabric") == [fabric], rec["product_id"]
        assert doc.get("fibre_content") == blend, rec["product_id"]
        moved[rec["product_type"]] += bool(blend)
    assert {v for r in built.records for a in r["attributes"] if a["key"] == "fabric"
            for v in [a["value"]] if r["product_type"] != "Bra"} >= (
        set(MOVED) | {value for _, value in TYPED_MOVED})
    assert {t for t, n in moved.items() if n} == {
        "Jeans", "Shirt", "Towel", "Soft Toy", "Leggings", "Vest", "Shorts", "Boxers", "Lampshade"}


def test_the_flat_document_carries_the_blend_and_never_facets_it(docs):
    from synthetic_ecommerce_data.core import standard

    flat = [r for d in docs if d.get("fibre_content") for r in standard.flat_documents(d)]
    assert flat
    for row in flat:
        assert row["fibre_content"] and "fibre_content" not in row["facets"]
        assert "composition" not in row["facets"]


def test_no_fabric_is_a_blend_or_a_use_word(docs):
    """A blend names fibres (``fibre_content``); Sports, Cargo and Compression name a use, a
    pocket or a fit (gen#258); Leather-Look is Faux Leather again."""
    fabrics = {v for d in docs for v in _values(d, "fabric")}
    assert fabrics & {"Cotton Blend", "Polyester Blend", "Cotton Jersey", "Sports", "Cargo",
                      "Compression"} == set()
    assert {f for f in fabrics if LEATHER_LOOK.search(f)} == set()
    assert {"Faux Leather", "Jersey", "Twill", "Knitted", "Suiting"} <= fabrics


def test_a_faux_leather_product_is_never_titled_leather_look(built):
    """``Faux Leather`` is the one name. A "Leather-Look" title is a class-4 decoy (a material
    named but absent), whose fabric is anything else: a title that says it over a faux
    leather fabric is the second name for the one fabric, in either spelling."""
    named = [r for r in built.records if LEATHER_LOOK.search(r["title"])]
    assert named
    assert [
        (r["product_id"], r["title"])
        for r in named
        if "Faux Leather" in [
            a["value"] for a in r["attributes"] if a["key"] in ("fabric", "material")
        ]
    ] == []


def test_a_fabric_move_is_keyed_by_product_type_and_value():
    """A "Polyester Blend" on a type no move names stays as it is, so the closed-list guard
    flags it; it is never silently Suiting because the tailored shorts' text said so."""
    entries = [{"key": "fabric", "value": "Polyester Blend"}]
    shorts = {"product_type": "Shorts", "category_path": ["Mens", "Shorts"], "title": "Shorts"}
    skirt = {"product_type": "Skirt", "category_path": ["Womens", "Skirts"], "title": "Skirt"}
    assert facet_leaves.fibre_content(entries, "Shorts") == "Polyester Blend"
    assert facet_leaves.fibre_content(entries, "Skirt") is None
    assert facet_leaves.leaf_facets(shorts, entries) == (
        [("fabric", "Fabric", "Suiting")], {"fabric"})
    assert facet_leaves.leaf_facets(skirt, entries) == ([], set())
