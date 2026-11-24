"""Women's crossbody, shoulder, clutch and belt bags and men's messenger and laptop bags (gen#1114).

The catalog held five Handbag styles whose ``bag_style`` was Crossbody, Shoulder or Clutch and no
leaf for any of the three; it held no messenger bag and no laptop bag, and five waist bags that are
decoys. Each is now a type of its own under ``Womens > Accessories > Bags`` or ``Mens > Accessories
> Bags``, a derivable spec drawn by its own shape of :mod:`kit_bags` or :mod:`kit_bags_carry`. A
style's SKUs are its colors times its sizes; its title shows its form and its material. These checks hold the leaf, the six main colors,
the drawing, the text-match decoys, the range at the ceiling build, the rule that a derived style
keeps the form and closure its text and drawing show, and the demo queries of the PRs.
"""

# ruff: noqa: E501 -- the type table and the long comprehensions read better whole.

from __future__ import annotations

import importlib
import re

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.core.letter_case import sentence_case
from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import (
    audience,
    facet_leaves,
    kit,
    line_grammar,
    main_colors,
    scale,
    scale_text,
    type_registry,
)

WOMENS = ("Womens", "Accessories", "Bags")
MENS = ("Mens", "Accessories", "Bags")
#: key -> (product type, leaf, shape, forms, materials a derived style may take, SKU floor).
TYPES = {
    "crossbody_bag": ("Crossbody Bag", "Crossbody Bags", "crossbody_bag",
                      {"Saddle", "Camera", "Satchel"}, {"Leather", "Faux Leather", "Canvas", "Nylon"}, 300),
    "shoulder_bag": ("Shoulder Bag", "Shoulder Bags", "shoulder_bag",
                     {"Hobo", "Baguette", "Crescent"}, {"Leather", "Faux Leather", "Suede"}, 200),
    "clutch_bag": ("Clutch Bag", "Clutch Bags", "clutch_bag",
                   {"Envelope", "Foldover", "Frame"}, {"Satin", "Velvet", "Faux Leather"}, 120),
    "belt_bag": ("Belt Bag", "Belt Bags", "belt_bag",
                 {"Crescent", "Box", "Pouch"}, {"Leather", "Faux Leather", "Canvas", "Nylon"}, 150),
    "messenger_bag": ("Messenger Bag", "Messenger Bags", "messenger_bag",
                      {"Courier", "Satchel", "Utility"}, {"Leather", "Faux Leather", "Canvas", "Nylon"}, 300),
    "laptop_bag": ("Laptop Bag", "Laptop Bags", "laptop_bag",
                   {"Briefcase", "Top Load", "Folio"}, {"Leather", "Faux Leather", "Canvas", "Nylon"}, 450),
}  # fmt: skip
KEYS = tuple(TYPES)
#: The men's types; the other types are women's.
MENS_KEYS = ("messenger_bag", "laptop_bag")
#: The key of a type's sizes, and the families of the line grammar that name the types' ranges.
SIZE_KEY = {"messenger_bag": "capacity_l", "laptop_bag": "screen_size_in"}
FAMILIES = ("bags", "bags_carry")
#: The shapes whose strap is a named part ("with Red Strap" is drawn).
STRAPS = ("crossbody_bag", "belt_bag", "messenger_bag")
#: The attributes a derived style keeps from its template (the text and the drawing follow them).
BUILD_KEYS = {"bag_shape", "closure", "strap"}
#: The PR's demo queries -> (product type, the entry a matching SKU's style must hold).
QUERIES = {
    "black crossbody bag": ("Crossbody Bag", ("color", "Black")),
    "satin clutch bag": ("Clutch Bag", ("material", "Satin")),
    "black messenger bag": ("Messenger Bag", ("color", "Black")),
    "leather laptop bag": ("Laptop Bag", ("material", "Leather")),
}


def _parent(key: str) -> tuple[str, ...]:
    return MENS if key in MENS_KEYS else WOMENS


def _spec(key: str) -> type_registry.TypeSpec:
    specs = type_registry.specs()
    assert key in specs, f"{key} is not a registered type"
    return specs[key]


def _mine(ceiling, key: str) -> list[dict]:
    return [r for r in ceiling.records if r["product_type"] == TYPES[key][0]]


def _values(row) -> dict[str, str]:  # noqa: ANN001
    return {a[0]: str(a[2]) for a in row.attrs}


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


@pytest.mark.parametrize("key", KEYS)
def test_the_type_is_a_derivable_leaf_of_its_own_under_bags(key: str) -> None:
    spec = _spec(key)
    ptype, leaf, shape, forms, materials, _floor = TYPES[key]
    assert spec.product_type == ptype
    assert spec.derivable
    assert len(spec.rows) >= 4
    assert len({r.brand for r in spec.rows}) >= 3
    for row in (*spec.rows, *(d.row for d in spec.decoys)):
        assert row.path == (*_parent(key), leaf), row.code
        assert row.shape == shape and shape in kit.shapes(), row.code
        values = _values(row)
        assert dict(row.params) == {k: values[k].lower() for k in ("bag_shape", "material")}, row.code
        assert values["audience"] == (audience.MENS if key in MENS_KEYS else audience.WOMENS), row.code
        if key in SIZE_KEY:
            assert row.size_key == SIZE_KEY[key] and len(row.sizes) >= 2, row.code
    for row in spec.rows:  # the title shows the form and the material
        values = _values(row)
        assert values["bag_shape"] in row.title and values["material"] in row.title, row.code
    assert {_values(r)["bag_shape"] for r in spec.rows} == forms
    assert {_values(r)["material"] for r in spec.rows} == materials


@pytest.mark.parametrize("key", KEYS)
def test_the_type_offers_the_six_main_colors_with_no_exception(key: str) -> None:
    ptype = TYPES[key][0]
    assert ptype not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in _spec(key).rows for c in r.colors}


@pytest.mark.parametrize("key", KEYS)
def test_each_form_and_each_material_draws_a_different_figure(key: str) -> None:
    _spec(key)
    _ptype, _leaf, shape, forms, materials, _floor = TYPES[key]
    fill = kit.Fill("solid", "#c8312e", "#2a2a2e")
    drawn = {(f, m): kit.render(shape, fill, uid="f", params={"bag_shape": f.lower(), "material": m.lower()})
             for f in forms for m in materials}  # fmt: skip
    assert len(set(drawn.values())) == len(drawn)


@pytest.mark.parametrize("key", KEYS)
def test_a_bag_is_no_garment_so_its_material_is_no_fabric(key: str) -> None:
    for row in _spec(key).rows:
        rec = {"department": [row.department], "product_type": row.product_type}
        assert not facet_leaves.is_textile(rec), row.code


@pytest.mark.parametrize("family", FAMILIES)
def test_no_lead_word_of_the_family_is_in_any_template_text(family: str) -> None:
    """A lead a text uses is no derived model (gen#851): it leaves the deal, and the names after it
    move. The games draw "Arcade" and a kids' film "ballroom" (gen#1120)."""
    module = importlib.import_module(f"synthetic_ecommerce_data.domains.retail.line_grammar_families.{family}")
    words = line_grammar.text_words(scale.templates(baseline=False))
    assert [w for w in module.LEADS if w.lower() in words] == []


@pytest.mark.parametrize("key", KEYS)
def test_the_type_plants_text_match_decoys(key: str) -> None:
    decoys = _spec(key).decoys
    assert len(decoys) >= 3
    assert any(d.cls == 6 for d in decoys), "no incidental-word decoy (class 6)"
    for d in decoys:  # the text holds the query's word and the entries say another value
        word = d.query.split()[0]
        assert word in f"{d.row.title} {d.row.description}".lower(), d.row.code
        stated = {_values(d.row)["material"].lower(), *(c[0].lower() for c in d.row.colors)}
        assert word not in stated, d.row.code


@pytest.mark.parametrize(("key", "form"), [(k, f) for k in STRAPS for f in sorted(TYPES[k][3])])
def test_the_red_strap_a_decoy_names_is_drawn_on_every_form(key: str, form: str) -> None:
    _spec(key)
    fill = kit.Fill("solid", "#1f1f22", detail=("strap", "#c8322b"))
    svg = kit.render(TYPES[key][2], fill, params={"bag_shape": form.lower(), "material": "nylon"})
    assert 'stroke="#c8322b"' in svg and 'data-part="strap"' in svg


@pytest.mark.parametrize("key", KEYS)
def test_the_ceiling_holds_the_range(key: str, ceiling) -> None:
    assert sum(r["sku_count"] for r in _mine(ceiling, key)) >= TYPES[key][5]


@pytest.mark.parametrize("key", KEYS)
def test_a_template_offers_no_build_key_for_a_derived_style_to_change(key: str, ceiling) -> None:
    authored = [r for r in _mine(ceiling, key) if r["product_id"] not in ceiling.template_of]
    assert authored
    pools = scale_text.value_pools(authored)
    offered = {k for r in authored for k in scale_text.variable_keys(r, pools)}
    assert offered & BUILD_KEYS == set()
    assert "material" in offered


@pytest.mark.parametrize("key", KEYS)
def test_a_derived_style_keeps_the_form_and_draws_the_material_it_states(key: str, ceiling) -> None:
    by_id = {r["product_id"]: r for r in ceiling.records}
    derived = [r for r in _mine(ceiling, key) if r["product_id"] in ceiling.template_of]
    assert derived
    wrong = []
    for r in derived:
        new = {a["key"]: str(a["value"]) for a in r["attributes"]}
        old = {a["key"]: str(a["value"]) for a in by_id[ceiling.template_of[r["product_id"]]]["attributes"]}
        params = r["drawing"]["params"]
        if any(new.get(k) != old.get(k) for k in BUILD_KEYS):
            wrong.append((r["title"], "build"))
        if params["material"] != new["material"].lower() or params["bag_shape"] != new["bag_shape"].lower():
            wrong.append((r["title"], "drawing"))
        if not re.search(rf"\b{new['material']}\b", r["title"]):
            wrong.append((r["title"], "title"))
    assert wrong == []


@pytest.mark.parametrize("key", KEYS)
def test_census_the_type_meets_the_output_standard_under_bags(key: str, ceiling) -> None:
    mine = _mine(ceiling, key)
    assert mine
    docs = scale.documents(scale.Scaled(mine, {}))
    assert check_catalog(docs, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {tuple(d["category_path"][:3]) for d in docs} == {tuple(map(sentence_case, _parent(key)))}
    titles = [r["title"] for r in mine]
    assert len(set(titles)) == len(titles)


@pytest.mark.parametrize("query", sorted(QUERIES))
def test_the_demo_query_has_matching_skus_and_a_decoy_to_tell_apart(query: str, ceiling) -> None:
    ptype, (key, value) = QUERIES[query]
    styles = [r for r in ceiling.records if r["product_type"] == ptype]
    if key == "color":
        match = [s for r in styles for s in r["skus"] if s["color"] == value]
    else:
        match = [r for r in styles if any(a["key"] == key and a["value"] == value for a in r["attributes"])]
        decoys = [d for s in type_registry.specs().values() if s.product_type == ptype for d in s.decoys]
        assert any(d.query == query for d in decoys)
    assert len(match) >= 8
