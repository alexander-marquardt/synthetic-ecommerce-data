"""Gloves (gen#422): the Accessories leaves held bags and umbrellas, and no gloves.

A demo search for ``touchscreen gloves`` or ``leather gloves`` found nothing or a baseball glove.
:mod:`type_specs.gloves` holds the type and draws it as its own shape. These checks hold what the
issue asked for: four kinds (knitted, leather, touchscreen, mittens) and the lining as structured
entries, the size as the SKU axis, the six main colors (gen#275), two brands, a drawing of its own
whose kind changes what is drawn, a place in the tree that follows gen#248 (``Womens >
Accessories``, no top-level Accessories root), the query shapes of the issue returning the type
first on the baseline ranker, and text-match decoys.
"""

from __future__ import annotations

import sys
import xml.dom.minidom
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import baseline_rank as br  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

SPEC = type_registry.specs()["gloves"]
ROWS = SPEC.rows
PTYPE = "Gloves"
PATH = ("Womens", "Accessories", "Gloves")
KINDS = {"Knitted", "Leather", "Touchscreen", "Mittens"}
LININGS = {"Fleece", "Wool", "Thermal", "Unlined"}
IDS = frozenset(f"BRD-{r.code}" for r in ROWS)


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(**params) -> str:
    return kit.render("gloves", kit.Fill("solid", "#123456", "#654321"), params=params)


def test_the_type_sits_under_womens_accessories_and_no_accessories_root() -> None:
    assert ROWS
    assert {r.path for r in ROWS} == {PATH}
    assert {r.product_type for r in ROWS} == {PTYPE}
    docs = [d for d in scale.templates() if d["product_id"] in IDS]
    assert len(docs) == len(ROWS)
    assert {tuple(d["category_path"]) for d in docs} == {PATH}
    assert "Accessories" not in {d["category_path"][0] for d in scale.templates()}


def test_every_kind_of_the_issue_is_sold_by_two_brands_and_unisex() -> None:
    assert {_attr(r, "glove_style") for r in ROWS} == KINDS
    assert {_attr(r, "lining") for r in ROWS} == LININGS
    assert len({r.brand for r in ROWS}) >= 2
    assert {_attr(r, "audience") for r in ROWS} == {"Unisex"}


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    assert ROWS
    for row in ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert {"glove_style", "lining", "glove_size_letter", "color"} <= keys, row.code


def test_the_glove_size_letter_has_an_output_key_no_other_option_shares() -> None:
    """The baseball glove's ``glove_size_in`` states ``glove_size`` in inches; two options with
    one output key and one unit between them fail the standard once the whole catalogue is built
    (``one_class_per_key``), which a check over this type's documents alone never shows."""
    key = export.OPTIONS["glove_size_letter"][0]
    assert [o for o, (k, _, _) in export.OPTIONS.items() if k == key] == ["glove_size_letter"]
    assert export.OPTIONS["glove_size_in"][0] == "glove_size" != key


def test_the_sku_axis_is_the_glove_size() -> None:
    for row in ROWS:
        assert row.size_key == "glove_size_letter", row.code
        assert [s for s, _ in row.sizes] == ["S", "M", "L", "XL"], row.code


def test_the_type_offers_the_six_main_colors_with_no_exception() -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in ROWS for c in r.colors}


def test_the_styles_are_templates_and_not_derived() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not SPEC.derivable
    assert IDS and not (IDS & kept)


def test_every_style_draws_as_the_gloves_shape_of_its_own() -> None:
    assert {r.shape for r in ROWS} == {"gloves"}
    assert "gloves" in kit.SHAPES


def test_each_kind_draws_differently() -> None:
    kinds = {k: _svg(kind=k) for k in sorted(KINDS)}
    assert len(set(kinds.values())) == len(KINDS)


def test_mittens_have_no_finger_gaps_and_gloves_do() -> None:
    separator = "M172,146 L172,262"
    assert separator in _svg(kind="Knitted") and separator not in _svg(kind="Mittens")


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg_that_prints_no_text(row) -> None:
    svg = kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))
    xml.dom.minidom.parseString(svg)
    assert "<text" not in svg


def test_the_param_values_match_the_row_attributes() -> None:
    assert ROWS
    for row in ROWS:
        assert dict(row.params) == {"kind": _attr(row, "glove_style")}


def test_the_tree_guard_accepts_the_leaf() -> None:
    paths = [tuple(r.path) for r in ROWS]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ROWS]
    assert tree_guard.misplaced_title_findings(rows) == []


@pytest.fixture(scope="module")
def index() -> br.Index:
    return br.Index(scale.templates())


@pytest.mark.parametrize(
    "query", ["touchscreen gloves", "leather gloves", "knitted gloves", "mittens", "gloves"]
)
def test_the_issue_query_returns_the_type_first(index: br.Index, query: str) -> None:
    """The first hit that is no planted text-match decoy (``PLT-D...`` or its own) is a style."""
    top = br.rank(index, query, size=12)
    planted = type_registry.decoy_ids_of(SPEC)
    first = next(
        (
            d
            for d in top
            if not d["product_id"].startswith("PLT-D") and d["product_id"] not in planted
        ),
        None,
    )
    assert first and first["product_id"] in IDS, [d["title"] for d in top]


#: Every decoy of the type by code: its gen#311 class (4 absent feature, 5 shade in the description,
#: 6 incidental word in a range name, 7 brand). Adding or dropping one shows in this test.
DECOY_CLASSES = {"DCGLV1": 4, "DCGLV2": 5, "DCGLV4": 6, "DCGLV5": 6, "DCGLV3": 7}
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
            assert "touchscreen" in text and _attr(d.row, "glove_style") != "Touchscreen", code
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
