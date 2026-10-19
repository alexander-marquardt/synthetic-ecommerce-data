"""Retail suits and tailoring, the rest of gen#215: a Trouser Suit and a Boys Suit.

PR #349 built the five Mens tailoring types (``test_retail_suits_215.py``). The issue also asks
for a Women's Trouser Suit (jacket style, trouser fit, fabric) and a Boys' Suit (age sizes, two or
three pieces), and its trigger is the one Suit Jacket row drawn with the generic ``coat`` shape.
These checks hold that: each type is a registered spec with its own drawing shape, at least three
invented brands and three styles, its key attributes as structured entries, age sizes for the
boys, the six main colors, a drawing that states what the record states, and the old row redrawn.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import class_rows  # noqa: E402
import decoy_apparel  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_suit_sets  # noqa: E402,F401 -- registers trouser_suit and boys_suit
import kit_suits  # noqa: E402
import sheet_extent  # noqa: E402
import type_registry  # noqa: E402

#: type -> (spec key, its own shape, the category path, the key attributes every style states).
TYPES = {
    "Trouser Suit": (
        "trouser_suit",
        "trouser_suit",
        ("Womens", "Suits & Tailoring", "Trouser Suits"),
        {"jacket_style", "leg_fit", "fabric", "piece_count"},
    ),
    "Boys Suit": (
        "boys_suit",
        "boys_suit",
        ("Kids", "Boys", "Suits"),
        {"piece_count", "fit", "fabric"},
    ),
}
GENERIC = {"coat", "trousers", "suit_jacket", "suit_trousers", "box", "box_wide", "top"}
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
#: shape -> param -> the values the kit draws, and the class each value stamps on the drawing.
PARAMS = {
    "trouser_suit": {
        "jacket": ("single", "double", "collarless"),
        "fit": ("slim", "straight", "wide"),
    },
    "boys_suit": {"pieces": ("2", "3"), "fit": ("slim", "regular")},
}
MARKER = {
    ("trouser_suit", "jacket"): "jacket-{}",
    ("trouser_suit", "fit"): "legfit-{}",
    ("boys_suit", "pieces"): "pieces-{}",
    ("boys_suit", "fit"): "fit-{}",
}
STAMP = re.compile(r' class="(?:jacket|legfit|pieces|fit)-[a-z_0-9]+"')
AGES = ("3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs", "11-12 Yrs", "13-14 Yrs")


def _spec(ptype: str):
    key = TYPES[ptype][0]
    spec = type_registry.specs().get(key)
    assert spec is not None, f"{key} is not a registered spec"
    return spec


def _svg(shape: str, **params: str) -> str:
    assert shape in kit.SHAPES, f"{shape} is not a kit shape"
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _stated(row) -> dict[str, str]:
    return {a[0]: a[2] for a in row.attrs}


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_is_a_spec_with_three_brands_and_three_styles_under_its_path(ptype: str) -> None:
    spec = _spec(ptype)
    _, _, path, _ = TYPES[ptype]
    assert spec.product_type == ptype
    assert len({r.brand for r in spec.rows}) >= 3
    assert len(spec.rows) >= 3
    assert {r.path for r in spec.rows} == {path}


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_draws_as_its_own_shape(ptype: str) -> None:
    _, shape, _, _ = TYPES[ptype]
    assert shape in kit.SHAPES and shape not in GENERIC
    assert {r.shape for r in _spec(ptype).rows} == {shape}


@pytest.mark.parametrize("ptype", TYPES)
def test_every_key_attribute_is_a_structured_entry(ptype: str) -> None:
    keys = TYPES[ptype][3]
    missing = {}
    for r in _spec(ptype).rows:
        have = {e["key"] for e in export.standard_document(r.doc())["attributes"]}
        if keys - have:
            missing[r.code] = sorted(keys - have)
    assert missing == {}


@pytest.mark.parametrize(("shape", "param"), [(s, p) for s, ps in PARAMS.items() for p in ps])
def test_a_param_changes_the_drawing_and_is_stamped_on_it(shape: str, param: str) -> None:
    values = PARAMS[shape][param]
    drawn = {v: _svg(shape, **{param: v}) for v in values}
    assert len(set(drawn.values())) == len(values)
    for v, svg in drawn.items():
        assert f'class="{MARKER[shape, param].format(v)}"' in svg


@pytest.mark.parametrize(("shape", "param"), [(s, p) for s, ps in PARAMS.items() for p in ps])
def test_a_param_changes_the_geometry_not_only_the_stamp(shape: str, param: str) -> None:
    values = PARAMS[shape][param]
    bare = {v: STAMP.sub("", _svg(shape, **{param: v})) for v in values}
    assert len(set(bare.values())) == len(values), "the stamp alone tells the values apart"


def test_a_double_breasted_jacket_draws_a_second_column_of_buttons() -> None:
    single = _svg("trouser_suit", jacket="single").count('class="button"')
    double = _svg("trouser_suit", jacket="double").count('class="button"')
    assert double == single + 2, (single, double)


def test_a_collarless_jacket_draws_the_neck_facing_and_no_lapel() -> None:
    svg = _svg("trouser_suit", jacket="collarless")
    facing = kit_suits._lapel_paths("none")[0]
    assert f'd="{facing}"' in svg, "the collarless jacket lacks its neck facing"
    for lapel in ("notch", "peak", "shawl"):
        assert f'd="{kit_suits._lapel_paths(lapel)[0]}"' not in svg, lapel


@pytest.mark.parametrize("shape", PARAMS)
def test_every_reading_stays_on_the_sheet(shape: str) -> None:
    for param, values in PARAMS[shape].items():
        for v in values:
            assert sheet_extent.overrun(_svg(shape, **{param: v})) <= 0, (shape, param, v)


def test_a_trouser_suit_shows_a_jacket_and_trousers_and_a_boys_suit_its_pieces() -> None:
    assert _svg("trouser_suit").count('class="piece"') == 2
    for n in (2, 3):
        assert _svg("boys_suit", pieces=str(n)).count('class="piece"') == n


@pytest.mark.parametrize("ptype", TYPES)
def test_a_style_draws_what_its_record_states(ptype: str) -> None:
    _, shape, _, _ = TYPES[ptype]
    for r in _spec(ptype).rows:
        params = dict(r.params)
        assert set(params) == set(PARAMS[shape]), r.code
        for k, v in params.items():
            assert v in PARAMS[shape][k], (r.code, k, v)
        stated = _stated(r)
        if shape == "trouser_suit":
            assert stated["jacket_style"].split()[0].lower() == params["jacket"], r.code
            assert stated["leg_fit"].split()[0].lower() == params["fit"], r.code
            assert stated["piece_count"] == "2", r.code
        else:
            assert stated["piece_count"] == params["pieces"], r.code
            assert stated["fit"].lower() == params["fit"], r.code


@pytest.mark.parametrize("ptype", TYPES)
def test_styles_of_a_type_differ_on_what_a_shopper_filters(ptype: str) -> None:
    assert len({r.params for r in _spec(ptype).rows}) >= 3
    assert len({_stated(r)["fabric"] for r in _spec(ptype).rows}) >= 3


def test_a_boys_suit_is_sold_in_age_sizes_and_two_and_three_pieces() -> None:
    rows = _spec("Boys Suit").rows
    for r in rows:
        sizes = [s for s, _ in r.sizes]
        assert len(sizes) >= 5 and all(s.endswith(" Yrs") for s in sizes), r.code
        assert set(sizes) <= set(AGES), r.code
        assert r.audience == "kids", r.code
    assert {_stated(r)["piece_count"] for r in rows} == {"2", "3"}
    assert all(r.title.startswith("Boys ") for r in rows)


def test_a_trouser_suit_is_sold_in_adult_sizes_to_women() -> None:
    for r in _spec("Trouser Suit").rows:
        doc = export.standard_document(r.doc())
        assert doc["category_path"][0] == "Womens", r.code
        assert r.title.startswith("Womens "), r.code
        assert len({s for s, _ in r.sizes}) >= 5, r.code


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_offers_the_six_main_colors(ptype: str) -> None:
    import scale

    offered = {
        c["color"]
        for r in scale.templates()
        if r["product_type"] == ptype
        for c in r["color_options"]
    }
    assert offered >= MAIN


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_carries_three_decoys_of_each_of_the_seven_classes(ptype: str) -> None:
    mine = [t for t in decoy_apparel.types() if t.product_type == ptype]
    assert len(mine) == 1, "the type has no apparel decoy plan"
    assert mine[0].classes == {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3}


def test_the_one_old_suit_jacket_row_is_drawn_as_a_suit_jacket_not_a_coat() -> None:
    old = [s for s, _ in class_rows.BOMBER if s.code == "SUITCK"]
    assert len(old) == 1
    assert old[0].shape == "suit_jacket"
    params = dict(old[0].params)
    assert set(params) == {"fit", "lapel", "buttons"}
    assert f'class="lapel-{params["lapel"]}"' in _svg("suit_jacket", **params)
