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


#: The closed list a ``fabric`` value comes from, read from its one source (gen#187).
SHOPPER_FABRICS = facet_leaves.SHOPPER_FABRICS
#: A bra's old ``fabric`` (its fibre content) -> the fibre a shopper names.
BRA_FIBRES = {
    "Cotton, Elastane": "Cotton",
    "Modal, Elastane": "Modal",
    "Recycled Polyamide, Elastane": "Nylon",
    "Recycled Polyester, Elastane": "Polyester",
}
#: A grade or a blend: never a ``fabric``.
GRADES = {"Organic Cotton", "Turkish Cotton", "Zero Twist Cotton", "Elastane"}


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


#: The 2026-10-13 coverage review's shopper-named fibres and materials (gen#187): the facet key
#: and a product type that carries each. A garment's fibre is a ``fabric``; a homeware type's
#: material stays the type's own ``material`` facet.
COVERAGE = {
    "Silk": ("fabric", "Skirt"),
    "Leather": ("fabric", "Skirt"),
    "Faux Leather": ("fabric", "Skirt"),
    "Suede": ("fabric", "Skirt"),
    "Faux Suede": ("fabric", "Skirt"),
    "Cashmere": ("fabric", "Coat"),
    "Jersey": ("fabric", "Shorts"),
    "Wool": ("fabric", "Coat"),
    "Crochet": ("fabric", "Skirt"),
    "Muslin": ("fabric", "Skirt"),
    "Voile": ("fabric", "Skirt"),
    "Waffle": ("fabric", "Dressing Gown"),
    "Brushed Cotton": ("fabric", "Shirt"),
    "Seagrass": ("material", "Storage Basket"),
    "Bone China": ("material", "Plate"),
    "Melamine": ("material", "Plate"),
    "Stainless Steel": ("material", "Saucepan"),
    "Cast Iron": ("material", "Frying Pan"),
}
#: The coverage values that were not ``fabric`` values before gen#187's second part.
NEW_FABRICS = {"Brushed Cotton", "Cashmere", "Crochet", "Faux Suede", "Leather", "Muslin",
               "Suede", "Voile", "Wool"}  # fmt: skip


def test_every_coverage_review_value_is_a_facet_value_on_a_type_that_uses_it(rows):
    for value, (key, ptype) in COVERAGE.items():
        held = [r for r in rows if r["product_type"] == ptype and value in r["facets"].get(key, ())]
        assert held, (value, key, ptype)


def test_every_fibre_the_coverage_review_names_is_on_the_closed_list():
    assert {v for v, (key, _) in COVERAGE.items() if key == "fabric"} <= SHOPPER_FABRICS
    assert NEW_FABRICS <= SHOPPER_FABRICS


def test_a_material_that_names_wool_cashmere_or_brushed_cotton_is_also_that_fabric(built, docs):
    """A coat's "Wool Cashmere blend", a jumper's "Merino wool" and a shirt's "Brushed Cotton"
    are ``material`` entries of the Mens and knitwear rows; the fibre a shopper names is also
    the document's ``fabric``, so "wool coat" finds them without reading a free-text material."""
    seen = collections.defaultdict(set)
    for rec, doc in zip(built.records, docs, strict=True):
        if any(a["key"] == "fabric" for a in rec["attributes"]):
            continue
        for a in rec["attributes"]:
            if a["key"] == "material" and a["value"] in facet_leaves.MATERIAL_FABRICS:
                want = facet_leaves.MATERIAL_FABRICS[a["value"]]
                assert set(want) <= set(_values(doc, "fabric")), rec["product_id"]
                seen[a["value"]].add(rec["product_type"])
    assert seen["Wool Cashmere blend"] == {"Coat"}
    assert seen["Brushed Cotton"] == {"Shirt", "Mens Trousers"}
    assert {"Jumper", "Cardigan", "Suit Jacket"} <= seen["Wool blend"]


def test_the_closed_material_table_names_only_closed_list_fabrics():
    named = {f for fabrics in facet_leaves.MATERIAL_FABRICS.values() for f in fabrics}
    assert named <= SHOPPER_FABRICS


def test_each_new_fabric_has_a_text_match_decoy_and_a_product_that_carries_it(built, docs):
    """gen#294: a shopper who types "suede" is also shown the cotton skirt with a suede trim,
    whose structured fabric says it is not suede. Each new value is carried by a product and
    named in the title or description of another that does not carry it."""
    carries, decoys = collections.defaultdict(list), collections.defaultdict(list)
    for rec, doc in zip(built.records, docs, strict=True):
        have = set(_values(doc, "fabric"))
        text = words(f"{rec['title']} {rec.get('description', '')}")
        for value in NEW_FABRICS:
            if value in have:
                carries[value].append(rec["product_id"])
            elif f" {words(value).strip()} " in text:
                decoys[value].append(rec["product_id"])
    assert {v for v in NEW_FABRICS if not carries[v]} == set()
    assert {v for v in NEW_FABRICS if not decoys[v]} == set()


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


# gen#187, the 2026-10-15 review: a garment's fibre is its fabric whatever row states it.

#: A closed-list fibre in a text, as the tests read it: not before a hyphen ("Leather-Look",
#: "Cashmere-Feel", "Wool-Free", "Fleece-Lined" claim no fibre).
FIBRE_WORD = re.compile(
    r"\b(" + "|".join(sorted(map(re.escape, SHOPPER_FABRICS), key=len, reverse=True)) + r")\b(?!-)",
    re.IGNORECASE,
)


def _textile(built, docs):
    """(record, document) for every garment that is not a bra."""
    return [
        (r, d)
        for r, d in zip(built.records, docs, strict=True)
        if facet_leaves.is_textile(r) and r["product_type"] != "Bra"
    ]


def test_stated_fabrics_reads_the_fibre_a_title_names_and_not_a_look_a_feel_or_a_lining():
    stated = facet_leaves.stated_fabrics
    assert stated("Mens Stretch Cotton Slim Fit Chinos") == ("Cotton",)
    assert stated("Brushed Cotton Flannel Shirt") == ("Brushed Cotton", "Flannel")
    assert stated("Faux Leather Leggings") == ("Faux Leather",)
    assert stated("Lace Trim Camisole") == ("Lace Trim",)
    assert stated("Waffle Knit Crew Neck Jumper") == ("Waffle",)
    assert stated("Linen Viscose Slim Fit Shirt") == ("Linen", "Viscose")
    for decoy in (
        "Mens Leather-Look Chinos", "Grey Cashmere-Feel Tights", "Mens Wool-Free Chinos",
        "100 Denier Fleece-Lined Tights", "Cottonwood Shirt", "Cotton-Free Shirt",
    ):  # fmt: skip
        assert stated(decoy) == (), decoy


def test_viscose_is_a_shopper_fabric_and_a_viscose_dress_carries_it(built, docs):
    assert "Viscose" in SHOPPER_FABRICS
    held = [d for r, d in _textile(built, docs) if r["product_type"] == "Dress"]
    assert any("Viscose" in _values(d, "fabric") for d in held)


def test_a_fibre_a_garment_title_states_is_one_of_its_fabrics(built, docs):
    """"cotton top", "wool bomber", "jersey top": a garment with no ``fabric`` of its own whose
    title names a fibre carries it, unless the title only says it looks, feels or is free of it."""
    checked = collections.Counter()
    for rec, doc in _textile(built, docs):
        if any(a["key"] == "fabric" for a in rec["attributes"]):
            continue
        have = " ".join(_values(doc, "fabric")).lower()
        for fibre in FIBRE_WORD.findall(rec["title"]):
            assert fibre.lower() in have, (rec["product_id"], rec["title"], have)
            checked[rec["product_type"]] += 1
    kinds = {"Top", "Trousers", "Tee", "T-Shirt", "Dress", "Pyjamas", "Bomber Jacket", "Socks"}
    assert kinds <= set(checked)


def test_the_wool_titled_products_the_review_named_carry_wool(built, docs):
    want = {"Wool Check Bomber Jacket", "Wool Blend Bomber Jacket", "Wool Walking Socks"}
    pairs = _textile(built, docs)
    seen = {r["title"]: _values(d, "fabric") for r, d in pairs if r["title"] in want}
    assert set(seen) == want
    assert all("Wool" in fabrics for fabrics in seen.values()), seen


def test_a_garment_material_that_names_cotton_linen_or_viscose_is_that_fabric(built, docs):
    """Dress, Polo Shirt, Pyjamas, Top, Blouse and Jacket carried a ``material`` only (Dress
    ``Cotton``, ``Linen blend``, ``Viscose``): "cotton dress" found none of them."""
    cases = [("Dress", "Cotton", "Cotton"), ("Dress", "Linen blend", "Linen"),
             ("Dress", "Viscose", "Viscose"), ("Dress", "Jersey", "Jersey"),
             ("Dress", "Satin", "Satin"), ("Polo Shirt", "Cotton", "Cotton"),
             ("Pyjamas", "Cotton", "Cotton"), ("Top", "Cotton blend", "Cotton"),
             ("Blouse", "Satin", "Satin"), ("Jacket", "Nylon", "Nylon"),
             ("Shirt", "Linen Viscose", "Viscose")]  # fmt: skip
    for ptype, material, fibre in cases:
        held = [
            d for r, d in _textile(built, docs)
            if r["product_type"] == ptype and material in _values(d, "material")
        ]  # fmt: skip
        assert held, (ptype, material)
        assert all(fibre in _values(d, "fabric") for d in held), (ptype, material, fibre)


def test_every_garment_material_that_names_a_fibre_has_a_row_or_a_reason(built):
    """The table is pinned both ways: a new ``material`` that names a closed-list fibre and is in
    neither :data:`MATERIAL_FABRICS` nor :data:`MATERIAL_NOT_FABRIC` fails here, so its author
    decides; a row carries every fibre its material names."""
    materials = {
        a["value"] for r in built.records if facet_leaves.is_textile(r)
        for a in r["attributes"] if a["key"] == "material"
    }  # fmt: skip
    rows, reasons = facet_leaves.MATERIAL_FABRICS, facet_leaves.MATERIAL_NOT_FABRIC
    assert not set(rows) & set(reasons)
    for material in sorted(materials):
        named = {f.title() for f in FIBRE_WORD.findall(material)}
        if not named:
            continue
        assert material in rows or material in reasons, material
        if material in rows:
            held = {n for fibre in rows[material] for n in named if n in fibre}
            assert named <= held, (material, named, rows[material])
    assert {m for m in reasons} <= materials
    assert {v for fibres in rows.values() for v in fibres} <= SHOPPER_FABRICS


def test_a_brushed_cotton_flannel_shirt_is_found_by_both_words(built, docs):
    held = [
        d for r, d in _textile(built, docs)
        if "Brushed Cotton Flannel" in [a["value"] for a in r["attributes"] if a["key"] == "fabric"]
    ]  # fmt: skip
    assert held
    assert all({"Flannel", "Brushed Cotton"} <= set(_values(d, "fabric")) for d in held)


def test_a_bag_a_belt_a_watch_a_shoe_and_homeware_get_no_fabric_from_their_text(built, docs):
    """Their fibre or material stays the type's own ``material`` or ``upper_material`` facet: the
    fabric marker reads ``fabric``, and a second facet for one concept would be two names."""
    types = set()
    for rec, doc in zip(built.records, docs, strict=True):
        if facet_leaves.is_textile(rec):
            continue
        own = {a["value"] for a in rec["attributes"] if a["key"] == "fabric"}
        own = {(facet_leaves.fabric_move(rec["product_type"], v) or (v,))[0] for v in own}
        assert set(_values(doc, "fabric")) <= own, (rec["product_id"], rec["title"])
        types.add(rec["product_type"])
    assert types >= facet_leaves.NON_TEXTILE_TYPES
    belts = [d for r, d in zip(built.records, docs, strict=True) if r["product_type"] == "Belt"]
    assert belts and all("Leather" in _values(d, "material") for d in belts)
