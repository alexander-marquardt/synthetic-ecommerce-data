"""Sunglasses (gen#422): the Accessories leaves held bags and umbrellas, and no sunglasses.

A demo search for ``polarised sunglasses`` or ``aviator sunglasses`` found nothing or an unrelated
item. :mod:`type_specs.sunglasses` holds the type and draws it as its own shape. These checks hold
what the issue asked for: the five frames, the three lenses and UV400 as structured entries, the
six main colors across the type (gen#275), two brands, a drawing of its own whose params change
what is drawn, a place in the tree that follows gen#248 (no top-level Accessories root), the
query shapes of the issue returning the type first on the baseline ranker, and text-match decoys.
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

SPEC = type_registry.specs()["sunglasses"]
ROWS = SPEC.rows
PTYPE = "Sunglasses"
PATH = ("Womens", "Accessories", "Sunglasses")
FRAMES = {"Aviator", "Wayfarer", "Round", "Cat-Eye", "Sport"}
LENSES = {"Polarised", "Gradient", "Mirrored"}
IDS = frozenset(f"BRD-{r.code}" for r in ROWS)


def _attr(row, key: str) -> str:
    return next(a[2] for a in row.attrs if a[0] == key)


def _svg(**params) -> str:
    return kit.render("sunglasses", kit.Fill("solid", "#123456", "#654321"), params=params)


def test_the_type_sits_under_womens_accessories_and_no_accessories_root() -> None:
    assert ROWS
    assert {r.path for r in ROWS} == {PATH}
    assert {r.product_type for r in ROWS} == {PTYPE}
    docs = [d for d in scale.templates() if d["product_id"] in IDS]
    assert len(docs) == len(ROWS)
    assert {tuple(d["category_path"]) for d in docs} == {PATH}
    assert {d["category_path"][0] for d in scale.templates()} >= {"Womens"}
    assert "Accessories" not in {d["category_path"][0] for d in scale.templates()}


def test_every_frame_of_the_issue_is_sold_by_two_brands_and_unisex() -> None:
    assert {_attr(r, "frame_shape") for r in ROWS} == FRAMES
    assert len({r.brand for r in ROWS}) >= 2
    assert {_attr(r, "audience") for r in ROWS} == {"Unisex"}


def test_every_lens_is_offered_and_every_pair_states_uv400() -> None:
    assert {_attr(r, "lens_type") for r in ROWS} == LENSES
    assert {_attr(r, "uv400") for r in ROWS} == {"Yes"}


def test_every_key_attribute_is_a_structured_entry_in_the_export() -> None:
    assert ROWS
    for row in ROWS:
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert {"frame_shape", "lens_type", "uv400", "color"} <= keys, row.code


def test_the_type_offers_the_six_main_colors_with_no_exception() -> None:
    assert PTYPE not in main_colors.EXCEPTIONS
    assert set(main_colors.MAIN_COLORS) <= {c[0] for r in ROWS for c in r.colors}


def test_the_styles_are_templates_and_not_derived() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not SPEC.derivable
    assert IDS and not (IDS & kept)


def test_every_style_draws_as_the_sunglasses_shape_of_its_own() -> None:
    assert {r.shape for r in ROWS} == {"sunglasses"}
    assert "sunglasses" in kit.SHAPES


def test_each_frame_and_each_lens_draws_differently() -> None:
    frames = {f: _svg(frame=f, lens="Gradient") for f in sorted(FRAMES)}
    assert len(set(frames.values())) == len(FRAMES)
    lenses = {m: _svg(frame="Round", lens=m) for m in sorted(LENSES)}
    assert len(set(lenses.values())) == len(LENSES)


def test_each_lens_is_painted_in_its_own_tint() -> None:
    """The lens fill, not only a mark on it, tells them apart: dark, a fade, pale."""
    names = ("Polarised", "Gradient", "Mirrored")
    polarised, gradient, mirrored = (_svg(frame="Round", lens=m) for m in names)
    assert 'fill="url(#sunglasses-lens-gradient)"' in gradient
    assert 'fill="url(#sunglasses-lens-gradient)"' not in polarised + mirrored
    assert 'fill="#2b333c"' in polarised and 'fill="#2b333c"' not in mirrored
    assert 'fill="#9db4c6"' in mirrored and 'fill="#9db4c6"' not in polarised + gradient


@pytest.mark.parametrize("row", ROWS, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg_that_prints_no_text(row) -> None:
    svg = kit.render(row.shape, kit.Fill("solid", "#123456", "#654321"), params=dict(row.params))
    xml.dom.minidom.parseString(svg)
    assert "<text" not in svg


def test_the_param_values_match_the_row_attributes() -> None:
    assert ROWS
    for row in ROWS:
        params = dict(row.params)
        assert params == {"frame": _attr(row, "frame_shape"), "lens": _attr(row, "lens_type")}


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
    "query", ["polarised sunglasses", "aviator sunglasses", "round sunglasses", "sunglasses"]
)
def test_the_issue_query_returns_the_type_first(index: br.Index, query: str) -> None:
    top = br.rank(index, query, size=3)
    assert top and top[0]["product_type"] == PTYPE, [d["title"] for d in top]


#: Every decoy of the type by code: its gen#311 class (4 absent feature, 5 shade in the description,
#: 6 incidental word in a range name, 7 brand). Adding or dropping one is a decision this test shows.
DECOY_CLASSES = {"DCSGL1": 4, "DCSGL2": 5, "DCSGL4": 6, "DCSGL5": 6, "DCSGL3": 7}
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
            assert "uv400" in text and _attr(d.row, "uv400") == "No", code
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
