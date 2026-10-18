"""Belts (gen#422): the Accessories leaves held bags and umbrellas, and no belt for a shopper.

A demo search for ``black leather belt`` or ``mens belt 34 inch`` found nothing or a jeans belt
distractor. :mod:`type_specs.belt` holds the type and draws it as its own shape. These checks hold
what the issue asked for: four materials and three buckles as structured entries, the width in
centimetres, the waist size in inches as the SKU axis, the six main colors (gen#275), two brands,
a drawing of its own whose params change what is drawn, a place in the tree that follows gen#248
(men's belts under ``Mens > Accessories``, no top-level Accessories root), the query shapes of the
issue returning the type first on the baseline ranker, and text-match decoys.
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

SPEC = type_registry.specs()["belt"]
ROWS = SPEC.rows
PTYPE = "Belt"
PATH = ("Mens", "Accessories", "Belts")
MATERIALS = {"Leather", "Faux Leather", "Canvas", "Webbing"}
BUCKLES = {"Pin", "Plate", "Automatic"}
IDS = frozenset(f"BRD-{r.code}" for r in ROWS)


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(**params) -> str:
    return kit.render("belt_buckled", kit.Fill("solid", "#123456", "#654321"), params=params)


def test_the_type_sits_under_mens_accessories_and_no_accessories_root() -> None:
    assert ROWS
    assert {r.path for r in ROWS} == {PATH}
    assert {r.product_type for r in ROWS} == {PTYPE}
    docs = [d for d in scale.templates() if d["product_id"] in IDS]
    assert len(docs) == len(ROWS)
    assert {tuple(d["category_path"]) for d in docs} == {PATH}
    assert "Accessories" not in {d["category_path"][0] for d in scale.templates()}


def test_every_material_and_buckle_is_offered_by_two_brands_to_men() -> None:
    assert {_attr(r, "material") for r in ROWS} == MATERIALS
    assert {_attr(r, "buckle") for r in ROWS} == BUCKLES
    assert len({r.brand for r in ROWS}) >= 2
    assert {_attr(r, "audience") for r in ROWS} == {"Mens"}


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    assert ROWS
    for row in ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert {"material", "buckle", "belt_width", "waist_size", "color"} <= keys, row.code
        width = next(e for e in doc["attributes"] if e["key"] == "belt_width")
        assert width["unit_code"] == "CMT", row.code


def test_the_sku_axis_is_the_waist_size_in_inches() -> None:
    for row in ROWS:
        doc = export.standard_document(row.doc())
        waists = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == "waist_size"]
        assert {e["unit_code"] for e in waists} == {"INH"}, row.code
        assert {float(e["value"]) for e in waists} >= {30.0, 34.0, 38.0}, row.code
        assert len(row.sizes) >= 5 and len(row.colors) >= 6


def test_the_type_offers_the_six_main_colors_with_no_exception() -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in ROWS for c in r.colors}


def test_the_styles_are_templates_and_not_derived() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not SPEC.derivable
    assert IDS and not (IDS & kept)


def test_every_style_draws_as_the_belt_shape_of_its_own() -> None:
    assert {r.shape for r in ROWS} == {"belt_buckled"}
    assert "belt_buckled" in kit.SHAPES
    assert kit.SHAPES["belt_buckled"] is not kit.SHAPES["belt"]


def test_each_buckle_and_each_material_draws_differently() -> None:
    buckles = {b: _svg(material="Leather", buckle=b) for b in sorted(BUCKLES)}
    assert len(set(buckles.values())) == len(BUCKLES)
    materials = {m: _svg(material=m, buckle="Pin") for m in sorted(MATERIALS)}
    assert len(set(materials.values())) == len(MATERIALS)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg_that_prints_no_text(row) -> None:
    svg = kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))
    xml.dom.minidom.parseString(svg)
    assert "<text" not in svg


def test_the_param_values_match_the_row_attributes() -> None:
    assert ROWS
    for row in ROWS:
        params = dict(row.params)
        assert params == {"material": _attr(row, "material"), "buckle": _attr(row, "buckle")}


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
    "query", ["black leather belt", "mens belt 34 inch", "leather belt", "canvas belt", "belt"]
)
def test_the_issue_query_returns_the_type_first(index: br.Index, query: str) -> None:
    """The first hit that is no planted text-match decoy (``PLT-D...`` or its own) is a style.

    A product of another type that holds only one query word in its title ("Canvas Platform
    Trainers" for "canvas belt", gen#421) may out-sell a belt through the popularity draw, so the
    hit that counts is the first to name, in its title, every query word a belt title uses.
    """
    belt_words = {w for r in ROWS for w in r.title.lower().split()}
    needed = [w for w in query.split() if w in belt_words]
    # The window holds the planted decoys that outrank the belt on purpose: every apparel type
    # plants a "Black Leather-Look ..." class 4 decoy (gen#311), so "black leather belt" meets
    # about two dozen before the first real belt. The window grew with the decoy types (gen#510).
    top = br.rank(index, query, size=60)
    planted = type_registry.decoy_ids_of(SPEC)
    first = next(
        (
            d
            for d in top
            if not d["product_id"].startswith("PLT-D")
            and d["product_id"] not in planted
            and all(word in d["title"].lower() for word in needed)
        ),
        None,
    )
    assert first and first["product_id"] in IDS, [d["title"] for d in top]


#: Every decoy of the type by code: its gen#311 class (4 absent feature, 5 shade in the description,
#: 6 incidental word in a range name, 7 brand). Adding or dropping one shows in this test.
DECOY_CLASSES = {"DCBLT1": 4, "DCBLT2": 5, "DCBLT4": 6, "DCBLT5": 6, "DCBLT3": 7}
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
            assert "automatic" in text and _attr(d.row, "buckle") != "Automatic", code
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
