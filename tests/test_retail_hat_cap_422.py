"""Hats and caps (gen#422): the Accessories leaves held bags and umbrellas, and no beanie or cap.

A demo search for ``red beanie`` or ``white baseball cap`` found nothing or an unrelated item.
:mod:`type_specs.hat_cap` holds the type and draws it as its own shape. These checks hold what the
issue asked for: five kinds and their materials as structured entries, the size as the SKU axis
(one size, S/M, L/XL), the six main colors (gen#275), two brands, a drawing of its own whose kind
changes what is drawn, a place in the tree that follows gen#248 (``Womens > Accessories``, no
top-level Accessories root), the query shapes of the issue returning the type first on the
baseline ranker, and text-match decoys.
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

SPEC = type_registry.specs()["hat_cap"]
ROWS = SPEC.rows
PTYPE = "Hat"
PATH = ("Womens", "Accessories", "Hats & Caps")
KINDS = {"Beanie", "Baseball Cap", "Bucket Hat", "Fedora", "Sun Hat"}
SIZES = {"One Size", "S/M", "L/XL"}
IDS = frozenset(f"BRD-{r.code}" for r in ROWS)


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(**params) -> str:
    return kit.render("hat", kit.Fill("solid", "#123456", "#654321"), params=params)


def test_the_type_sits_under_womens_accessories_and_no_accessories_root() -> None:
    assert ROWS
    assert {r.path for r in ROWS} == {PATH}
    assert {r.product_type for r in ROWS} == {PTYPE}
    docs = [d for d in scale.templates() if d["product_id"] in IDS]
    assert len(docs) == len(ROWS)
    assert {tuple(d["category_path"]) for d in docs} == {PATH}
    assert "Accessories" not in {d["category_path"][0] for d in scale.templates()}


def test_every_kind_of_the_issue_is_sold_by_two_brands_and_unisex() -> None:
    assert {_attr(r, "hat_style") for r in ROWS} == KINDS
    assert len({r.brand for r in ROWS}) >= 2
    assert {_attr(r, "audience") for r in ROWS} == {"Unisex"}
    assert len({_attr(r, "material") for r in ROWS}) >= 4


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    assert ROWS
    for row in ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert {"hat_style", "material", "hat_size", "color"} <= keys, row.code


def test_the_sku_axis_is_the_size_in_all_three_forms() -> None:
    assert {s for r in ROWS for s, _ in r.sizes} == SIZES
    for row in ROWS:
        assert row.size_key == "hat_size" and row.sizes, row.code
        assert {s for s, _ in row.sizes} in ({"One Size"}, {"S/M", "L/XL"}), row.code


def test_the_type_offers_the_six_main_colors_with_no_exception() -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in ROWS for c in r.colors}


def test_the_styles_are_templates_and_not_derived() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not SPEC.derivable
    assert IDS and not (IDS & kept)


def test_every_style_draws_as_the_hat_shape_of_its_own() -> None:
    assert {r.shape for r in ROWS} == {"hat"}
    assert "hat" in kit.SHAPES


def test_each_kind_draws_differently() -> None:
    kinds = {k: _svg(kind=k) for k in sorted(KINDS)}
    assert len(set(kinds.values())) == len(KINDS)


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg_that_prints_no_text(row) -> None:
    svg = kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))
    xml.dom.minidom.parseString(svg)
    assert "<text" not in svg


def test_the_param_values_match_the_row_attributes() -> None:
    assert ROWS
    for row in ROWS:
        assert dict(row.params) == {"kind": _attr(row, "hat_style")}


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
    "query", ["red beanie", "white baseball cap", "bucket hat", "fedora", "sun hat", "beanie"]
)
def test_the_issue_query_returns_the_type_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, size=3)
    assert top and top[0]["product_type"] == PTYPE, [d["title"] for d in top]


def test_the_type_carries_text_match_decoys_whose_structured_fields_deny_their_text() -> None:
    assert len(SPEC.decoys) >= 3
    assert {d.cls for d in SPEC.decoys} >= {4, 5, 7}
    for d in SPEC.decoys:
        assert d.row.product_type == PTYPE
        text = f"{d.row.title} {d.row.description}".lower()
        if d.cls == 4:
            assert "wool" in text and _attr(d.row, "material") != "Wool", d.row.code
        if d.cls == 7:
            assert "pellbrook" in text and d.row.brand != "Pellbrook", d.row.code


@pytest.mark.timeout(300)
def test_every_style_and_decoy_reaches_the_100k_build_and_meets_the_standard() -> None:
    every = IDS | type_registry.decoy_ids_of(SPEC)
    docs = scale.documents(scale.build(100_000))
    mine = [d for d in docs if d["product_id"] in every]
    assert {d["product_id"] for d in mine} == every
    assert check_catalog(mine, one_class_per_key=True) == []
