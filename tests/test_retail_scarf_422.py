"""Scarves (gen#422): the Accessories leaves held no scarf.

A demo search for ``silk scarf`` found a silk tie or a planted cap. :mod:`type_specs.scarf` holds
the type and draws it as its own shape. These checks hold what the issue asked for: four kinds
(knitted, woven, silk square, snood), the material and the length in centimetres as structured
entries, the six main colors as the SKUs (gen#275), two brands, a drawing of its own whose kind
changes what is drawn, a place in the tree that follows gen#248 (``Womens > Accessories``, no
top-level Accessories root), and text-match decoys.
``tests/test_retail_accessories_queries_422.py`` holds the query shapes.
"""

from __future__ import annotations

import xml.dom.minidom

import pytest

from synthetic_ecommerce_data.core.standard import check_catalog
from synthetic_ecommerce_data.domains.retail import (
    export,
    kit,
    main_colors,
    scale,
    tree_guard,
    type_registry,
)

SPEC = type_registry.specs()["scarf"]
ROWS = SPEC.rows
PTYPE = "Scarf"
PATH = ("Womens", "Accessories", "Scarves")
KINDS = {"Knitted", "Woven", "Silk Square", "Snood"}
IDS = frozenset(f"BRD-{r.code}" for r in ROWS)


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(**params) -> str:
    return kit.render("scarf", kit.Fill("solid", "#123456", "#654321"), params=params)


def test_the_type_sits_under_womens_accessories_and_no_accessories_root() -> None:
    assert ROWS
    assert {r.path for r in ROWS} == {PATH}
    assert {r.product_type for r in ROWS} == {PTYPE}
    docs = [d for d in scale.templates() if d["product_id"] in IDS]
    assert len(docs) == len(ROWS)
    assert {tuple(d["category_path"]) for d in docs} == {PATH}
    assert "Accessories" not in {d["category_path"][0] for d in scale.templates()}


def test_every_kind_of_the_issue_is_sold_by_two_brands_and_unisex() -> None:
    assert {_attr(r, "scarf_style") for r in ROWS} == KINDS
    assert len({r.brand for r in ROWS}) >= 2
    assert {_attr(r, "audience") for r in ROWS} == {"Unisex"}


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    assert ROWS
    for row in ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert {"scarf_style", "material", "item_length", "color"} <= keys, row.code


def test_the_length_is_measured_in_centimetres() -> None:
    assert ROWS
    for row in ROWS:
        doc = export.standard_document(row.doc())
        length = next(e for e in doc["attributes"] if e["key"] == "item_length")
        assert length["unit_code"] == "CMT", row.code
        assert float(length["value"]) == float(_attr(row, "item_length")), row.code


def test_the_sku_axis_is_the_color_alone() -> None:
    for doc in (d for d in scale.templates() if d["product_id"] in IDS):
        assert doc["sku_count"] == len(doc["color_options"]), doc["product_id"]


def test_the_type_offers_the_six_main_colors_with_no_exception() -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in ROWS for c in r.colors}


def test_the_styles_are_templates_and_not_derived() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not SPEC.derivable
    assert IDS and not (IDS & kept)


def test_every_style_draws_as_the_scarf_shape_of_its_own() -> None:
    assert {r.shape for r in ROWS} == {"scarf"}
    assert "scarf" in kit.SHAPES


def test_each_kind_draws_differently() -> None:
    kinds = {k: _svg(kind=k) for k in sorted(KINDS)}
    assert len(set(kinds.values())) == len(KINDS)


def test_a_snood_and_a_square_have_no_tails_and_a_knitted_scarf_has_two() -> None:
    tail = "M138,184 L118,312"
    assert tail in _svg(kind="Knitted") and tail in _svg(kind="Woven")
    assert tail not in _svg(kind="Snood") and tail not in _svg(kind="Silk Square")


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg_that_prints_no_text(row) -> None:
    svg = kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))
    xml.dom.minidom.parseString(svg)
    assert "<text" not in svg


def test_the_param_values_match_the_row_attributes() -> None:
    assert ROWS
    for row in ROWS:
        assert dict(row.params) == {"kind": _attr(row, "scarf_style")}


def test_the_tree_guard_accepts_the_leaf() -> None:
    paths = [tuple(r.path) for r in ROWS]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []


#: Every decoy of the type by code: its gen#311 class (4 absent feature, 5 shade in the description,
#: 6 incidental word in a range name, 7 brand). Adding or dropping one shows in this test.
DECOY_CLASSES = {"DCSCF1": 4, "DCSCF2": 5, "DCSCF4": 6, "DCSCF5": 6, "DCSCF3": 7}
_MAIN_COLORS = {"black", "red", "blue", "green", "yellow", "white"}


def test_the_type_carries_text_match_decoys_whose_structured_fields_deny_their_text() -> None:
    assert {d.row.code: d.cls for d in SPEC.decoys} == DECOY_CLASSES
    for d in SPEC.decoys:
        code = d.row.code
        assert d.row.product_type == PTYPE, code
        title, desc = d.row.title.lower(), d.row.description.lower()
        text = f"{title} {desc}"
        colors = [color[0].lower() for color in d.row.colors]
        word = d.query.split()[0]
        assert word in text, code
        if d.cls == 4:
            assert "silk" in text and _attr(d.row, "material") != "Silk", code
        if d.cls == 5:  # the shade is in the description only, and the structured color is another
            assert word == "blue" and "blue" in desc and "blue" not in title, code
            assert "blue" not in colors, code
        if d.cls == 6:  # a range name that leads the title holds the word; the fields do not
            assert title.split()[0] == word and word not in desc, code
            assert word not in colors, code
            assert word not in {str(v).lower() for _, _, v, *_ in d.row.attrs}, code
        if d.cls == 7:
            assert "pellbrook" in text and d.row.brand != "Pellbrook", code
    six = {d.query.split()[0] for d in SPEC.decoys if d.cls == 6}
    assert six & _MAIN_COLORS and six - _MAIN_COLORS  # one color word and one category noun


@pytest.mark.timeout(300)
def test_every_style_and_decoy_reaches_the_100k_build_and_meets_the_standard() -> None:
    every = IDS | type_registry.decoy_ids_of(SPEC)
    docs = scale.documents(scale.build(100_000))
    mine = [d for d in docs if d["product_id"] in every]
    assert {d["product_id"] for d in mine} == every
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
