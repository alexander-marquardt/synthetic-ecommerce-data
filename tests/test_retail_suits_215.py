"""Retail suits and tailoring (gen#215): the Mens tailoring types, each drawn as its own shape.

``mens_depth_rows`` holds the rows and ``kit_suits`` draws them. These checks hold what the issue
asks for: every type has at least three invented brands and three styles, each key attribute is a
structured entry (not only a word in the title), each style draws as its own shape with the params
its record states, the six main colors are offered, and a jacket, trousers and waistcoat of one
set match.
"""

from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import kit  # noqa: E402
import mens_depth_rows  # noqa: E402
import type_colors  # noqa: E402

#: type -> (its own shape, the key attributes each of its styles states as structured entries).
TYPES = {
    "Suit Jacket": ("suit_jacket", {"fit", "material", "lapel", "buttons", "occasion"}),
    "Suit Trousers": ("suit_trousers", {"fit", "material", "leg_length"}),
    "Waistcoat": ("waistcoat", {"fit", "material", "buttons"}),
    "Dinner Suit": ("dinner_suit", {"fit", "material", "lapel"}),
    "Formal Accessories": ("formal_accessory", {"material", "accessory_type"}),
}
GENERIC = {"coat", "trousers", "box", "box_wide", "top"}
MAIN = {"Red", "Blue", "Green", "Yellow", "Black", "White"}
#: Each shape's params, the values the kit draws for each and the marker the drawing stamps.
PARAMS = {
    "suit_jacket": {
        "fit": ("slim", "tailored", "regular"),
        "lapel": ("notch", "peak", "shawl"),
        "buttons": ("2", "3"),
    },
    "suit_trousers": {"fit": ("slim", "tailored", "regular"), "leg": ("short", "regular", "long")},
    "waistcoat": {"fit": ("slim", "tailored", "regular"), "buttons": ("4", "5", "6")},
    "dinner_suit": {"fit": ("slim", "tailored", "regular"), "lapel": ("peak", "shawl")},
    "formal_accessory": {"item": ("tie", "bow_tie", "braces", "cummerbund", "pocket_square")},
}
MARKER = {"fit": "fit-{}", "lapel": "lapel-{}", "leg": "leg-{}", "buttons": "buttons-{}",
          "item": "item-{}"}  # fmt: skip

#: The stamps the kit puts on a drawing; stripped, what is left is the geometry alone.
STAMP = re.compile(r' class="(?:fit|lapel|leg|buttons|item)-[a-z_0-9]+"')
#: What the record says -> the value the kit draws (Relaxed is cut as regular; the kit has no more).
STATED = {"relaxed": "regular", "two_button": "2", "three_button": "3", "four_button": "4",
          "five_button": "5", "six_button": "6"}  # fmt: skip

DECOYS = mens_depth_rows.decoy_ids()
ROWS = [r for r in mens_depth_rows.ROWS if f"BRD-{r.code}" not in DECOYS]


def _styles(ptype: str):
    return [r for r in ROWS if r.product_type == ptype]


def _svg(shape: str, **params: str) -> str:
    assert shape in kit.SHAPES, shape
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_has_three_brands_and_three_styles_under_the_tailoring_category(ptype: str) -> None:
    rows = _styles(ptype)
    assert len({r.brand for r in rows}) >= 3
    assert len(rows) >= 3
    assert {r.path[:2] for r in rows} == {("Mens", "Suits & Tailoring")}


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_draws_as_its_own_shape(ptype: str) -> None:
    shape, _ = TYPES[ptype]
    assert shape in kit.SHAPES and shape not in GENERIC
    assert {r.shape for r in _styles(ptype)} == {shape}
    assert {r.shape for r in mens_depth_rows.ROWS if r.product_type == ptype} == {shape}


@pytest.mark.parametrize("ptype", TYPES)
def test_every_key_attribute_is_a_structured_entry(ptype: str) -> None:
    _, keys = TYPES[ptype]
    missing = {}
    for r in _styles(ptype):
        doc = export.standard_document(r.doc())
        have = {e["key"] for e in doc["attributes"]}
        if keys - have:
            missing[r.code] = sorted(keys - have)
    assert missing == {}


@pytest.mark.parametrize(("shape", "param"), [(s, p) for s, ps in PARAMS.items() for p in ps])
def test_a_param_changes_the_drawing_and_is_stamped_on_it(shape: str, param: str) -> None:
    values = PARAMS[shape][param]
    drawn = {v: _svg(shape, **{param: v}) for v in values}
    assert len(set(drawn.values())) == len(values)
    for v, svg in drawn.items():
        assert f'class="{MARKER[param].format(v)}"' in svg


@pytest.mark.parametrize(("shape", "param"), [(s, p) for s, ps in PARAMS.items() for p in ps])
def test_a_param_changes_the_geometry_not_only_the_stamp(shape: str, param: str) -> None:
    values = PARAMS[shape][param]
    bare = {v: STAMP.sub("", _svg(shape, **{param: v})) for v in values}
    assert len(set(bare.values())) == len(values), "the stamp alone tells the values apart"


def test_a_jacket_is_cut_closer_to_the_body_as_the_fit_narrows() -> None:
    def body(fit: str) -> list[tuple[float, float]]:
        svg = _svg("suit_jacket", fit=fit)
        d = re.search(rf'class="fit-{fit}"><path d="([^"]+)"', svg).group(1)
        return [(float(x), float(y)) for x, y in re.findall(r"[ML]([\d.]+),([\d.]+)", d)]

    waist = {f: next(x for x, y in body(f) if y == 210.0) for f in ("slim", "tailored", "regular")}
    hem = {f: next(x for x, y in body(f) if y == 330.0) for f in waist}
    assert waist["slim"] > waist["tailored"] > waist["regular"]
    assert hem["slim"] > hem["tailored"] > hem["regular"]


def test_a_jacket_draws_as_many_buttons_as_it_states() -> None:
    for n in (2, 3):
        svg = _svg("suit_jacket", buttons=str(n))
        assert svg.count('class="button"') == n


@pytest.mark.parametrize("ptype", TYPES)
def test_a_style_draws_what_its_record_states(ptype: str) -> None:
    shape, _ = TYPES[ptype]
    for r in _styles(ptype):
        params = dict(r.params)
        assert set(params) == set(PARAMS[shape]), r.code
        for k, v in params.items():
            assert v in PARAMS[shape][k], (r.code, k, v)
        stated = {a[0]: a[2].lower().replace(" ", "_") for a in r.attrs}
        for key in ("fit", "buttons"):
            if key in params and key in stated:
                assert STATED.get(stated[key], stated[key]) == params[key], (r.code, key)
        if "lapel" in params:
            assert stated["lapel"] == params["lapel"], r.code
        if "leg" in params:
            assert stated["leg_length"] == params["leg"], r.code
        if "item" in params:
            assert stated["accessory_type"] == params["item"], r.code


@pytest.mark.parametrize("ptype", TYPES)
def test_styles_of_a_type_differ_on_what_a_shopper_filters(ptype: str) -> None:
    drawings = {r.params for r in _styles(ptype)}
    assert len(drawings) >= 3


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_offers_the_six_main_colors(ptype: str) -> None:
    import scale

    styles = [r for r in scale.templates() if r["product_type"] == ptype]
    offered = {type_colors.base_color(o["color"]) for r in styles for o in r["color_options"]}
    # tailoring comes in suiting colors (type_colors, gen#448): asked for those it comes in
    comes_in = {c for c in MAIN if any(type_colors.permits(r["category_path"], c) for r in styles)}
    assert offered >= comes_in


def test_a_set_is_a_jacket_trousers_and_waistcoat_of_one_cloth() -> None:
    sets: dict[str, list] = defaultdict(list)
    for r in ROWS:
        for a in r.attrs:
            if a[0] == "suit_set":
                sets[a[2]].append(r)
    assert len(sets) >= 5
    for name, pieces in sets.items():
        kinds = sorted(p.product_type for p in pieces)
        assert kinds == ["Suit Jacket", "Suit Trousers", "Waistcoat"]
        assert len({p.brand for p in pieces}) == 1, name
        assert len({tuple(c[0] for c in p.colors) for p in pieces}) == 1, name
        assert len({dict((a[0], a[2]) for a in p.attrs)["material"] for p in pieces}) == 1, name
        assert len({dict((a[0], a[2]) for a in p.attrs)["fit"] for p in pieces}) == 1, name
        assert all(name in p.title and name in p.description for p in pieces)


def test_a_suit_jacket_names_its_fit_in_the_title_and_the_record() -> None:
    for r in _styles("Suit Jacket"):
        fit = dict((a[0], a[2]) for a in r.attrs)["fit"]
        assert re.search(rf"\b{fit}\b", r.title, re.I), r.title


def test_a_decoy_accessory_states_its_accessory_type() -> None:
    decoys = [
        r
        for r in mens_depth_rows.ROWS
        if f"BRD-{r.code}" in DECOYS and r.product_type == "Formal Accessories"
    ]
    assert decoys
    for r in decoys:
        assert any(a[0] == "accessory_type" for a in r.attrs), r.code
