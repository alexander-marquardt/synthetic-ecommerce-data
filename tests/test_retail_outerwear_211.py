"""Retail outerwear (gen#211): trench coats, raincoats, parkas, puffer jackets, gilets, peacoats,
utility jackets, shackets, boleros, windbreakers and hoodies.

Each type is its own spec under ``type_specs/`` (gen#351) and ``kit_outerwear`` draws it. These
checks hold what the issue asked for: every type has three styles from three invented brands for
Womens, most also for Mens, each style draws as its own shape with the variant axis as a param,
each key attribute is a structured entry in the export (the color and size keys too), a mark a
record states is a mark the drawing shows, each type carries text-match decoys (gen#294's rule),
and the styles reach the scaled build.
"""

from __future__ import annotations

import re
import sys
import xml.dom.minidom
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import decoy_apparel  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

SIZE = {"color", "size"}
#: product type -> (spec key, shape, the key attributes every style states).
TYPES = {
    "Trench Coat": ("trench_coat", "trench_coat",
                    {"garment_length", "belted", "breasting", "fabric", "water_repellent"} | SIZE),
    "Raincoat": ("raincoat", "raincoat",
                 {"garment_length", "hood", "waterproof_rating", "breathable", "lining", "fabric"}
                 | SIZE),
    "Parka": ("parka", "parka",
              {"garment_length", "hood", "hood_type", "fill", "warmth_rating",
               "waterproof"} | SIZE),
    "Puffer Jacket": ("puffer_jacket", "puffer",
                      {"garment_length", "hood", "fill", "packable", "quilting"} | SIZE),
    "Gilet": ("gilet", "gilet", {"fill", "use", "fabric"} | SIZE),
    "Peacoat": ("peacoat", "peacoat", {"garment_length", "breasting", "fabric"} | SIZE),
    "Utility Jacket": ("utility_jacket", "utility_jacket",
                       {"jacket_style", "fabric", "pocket_count", "collar"} | SIZE),
    "Shacket": ("shacket", "shacket", {"fabric", "texture", "garment_weight"} | SIZE),
    "Bolero": ("bolero", "bolero",
               {"bolero_style", "fabric", "sleeve_length", "occasion", "garment_length"} | SIZE),
    "Windbreaker": ("windbreaker", "windbreaker",
                    {"jacket_style", "packable", "hood", "zip_style", "fabric"} | SIZE),
    "Hoodie": ("hoodie", "hoodie", {"zip_style", "fabric", "fit"} | SIZE),
}  # fmt: skip
#: shape -> (parameter, readings): the first reading is the default; two readings must draw
#: differently.
VARIANTS = [
    ("trench_coat", "length", ("mid", "long", "short")),
    ("trench_coat", "belt", ("yes", "no")),
    ("trench_coat", "breasted", ("double", "single")),
    ("raincoat", "length", ("mid", "long", "short")),
    ("raincoat", "hood", ("none", "fixed", "packaway")),
    ("parka", "length", ("long", "mid", "short")),
    ("parka", "hood", ("fixed", "faux_fur")),
    ("puffer", "length", ("regular", "cropped", "longline")),
    ("puffer", "hood", ("no", "yes")),
    ("puffer", "quilt", ("channel", "diamond")),
    ("gilet", "padding", ("padded", "quilted", "fleece")),
    ("peacoat", "length", ("short", "mid", "long")),
    ("peacoat", "breasted", ("double", "single")),
    ("utility_jacket", "pockets", ("4", "2")),
    ("utility_jacket", "collar", ("point", "stand")),
    ("shacket", "teddy", ("no", "yes")),
    ("bolero", "style", ("bolero", "shrug", "cape")),
    ("bolero", "sleeve", ("long", "three_quarter", "short", "none")),
    ("windbreaker", "zip", ("full", "half")),
    ("windbreaker", "hood", ("no", "yes")),
    ("hoodie", "zip", ("pullover", "through")),
]
IDS = [f"{s}-{p}" for s, p, _ in VARIANTS]


def _spec(ptype: str) -> type_registry.TypeSpec:
    spec = type_registry.specs().get(TYPES[ptype][0])
    assert spec is not None, f"{ptype}: no spec type_specs/{TYPES[ptype][0]}.py"
    spec.docs()  # states the spec's brand owners
    return spec


def _rows(ptype: str) -> list:
    return list(_spec(ptype).rows)


def _all_rows() -> list:
    return [r for p in TYPES for r in _rows(p)]


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _doc(row) -> dict:
    return export.standard_document(row.doc())


def _keys(row) -> set[str]:
    doc = _doc(row)
    return {e["key"] for e in doc["attributes"]} | {
        e["key"] for v in doc["variants"] for e in v["attributes"]
    }


def _values(row, key: str) -> list[str]:
    return [str(e["value"]) for e in _doc(row)["attributes"] if e["key"] == key]


def test_the_eleven_types_are_registered_each_as_its_own_spec() -> None:
    assert [_spec(p).key for p in TYPES] == [k for k, _, _ in TYPES.values()]
    assert {_spec(p).product_type for p in TYPES} == set(TYPES)
    assert not any(_spec(p).derivable for p in TYPES), "the range grows by authored rows"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_has_three_styles_from_three_invented_brands(ptype: str) -> None:
    rows = _rows(ptype)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3
    assert len({r.title for r in rows}) == len(rows)
    assert {r.brand for r in rows} <= {b for b, _ in _spec(ptype).owners}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_draws_as_the_types_own_shape(ptype: str) -> None:
    shape = TYPES[ptype][1]
    assert {r.shape for r in _rows(ptype)} == {shape}
    assert shape in kit.SHAPES
    assert [p for p, t in TYPES.items() if t[1] == shape] == [ptype], "one shape per type"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_type_is_named_and_filed_under_coats_and_jackets(ptype: str) -> None:
    roots = set()
    for row in _rows(ptype):
        assert row.department == "Clothing" and row.path[1] == "Coats & Jackets"
        assert _doc(row)["product_type"] == ptype
        assert row.path[-1] == _doc(row)["category_leaf"]
        roots.add(row.path[0])
    assert "Womens" in roots and roots <= {"Womens", "Mens"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_key_attribute_is_a_structured_entry_not_a_word_in_the_title(ptype: str) -> None:
    want = TYPES[ptype][2]
    missing = {r.code: want - _keys(r) for r in _rows(ptype)}
    assert {c: m for c, m in missing.items() if m} == {}


def test_the_attribute_values_a_shopper_filters_on_are_all_stated() -> None:
    seen = {
        (p, k): {v for r in _rows(p) for v in _values(r, k)}
        for p, k in [("Trench Coat", "garment_length"), ("Trench Coat", "belted"),
                     ("Trench Coat", "breasting"), ("Raincoat", "garment_length"),
                     ("Raincoat", "hood_type"), ("Puffer Jacket", "fill"),
                     ("Puffer Jacket", "garment_length"), ("Gilet", "fill"), ("Gilet", "use"),
                     ("Shacket", "fabric"), ("Bolero", "bolero_style"),
                     ("Windbreaker", "zip_style"), ("Hoodie", "zip_style"),
                     ("Utility Jacket", "jacket_style")]
    }  # fmt: skip
    assert {"Short", "Mid-Length", "Long"} <= seen["Trench Coat", "garment_length"]
    assert seen["Trench Coat", "belted"] == {"Yes", "No"}
    assert seen["Trench Coat", "breasting"] == {"Double-Breasted", "Single-Breasted"}
    assert {"Short", "Mid-Length", "Long"} <= seen["Raincoat", "garment_length"]
    assert {"Fixed", "Packaway"} <= seen["Raincoat", "hood_type"]
    assert {"Down", "Feather", "Synthetic"} <= seen["Puffer Jacket", "fill"]
    assert {"Cropped", "Regular", "Longline"} <= seen["Puffer Jacket", "garment_length"]
    assert {"Padded", "Fleece", "Quilted"} <= seen["Gilet", "fill"]
    assert seen["Gilet", "use"] == {"Performance", "Casual"}
    assert {"Flannel", "Corduroy", "Fleece"} <= seen["Shacket", "fabric"]
    assert {"Bolero", "Shrug", "Cape"} <= seen["Bolero", "bolero_style"]
    assert seen["Windbreaker", "zip_style"] == {"Half-Zip", "Full-Zip"}
    assert seen["Hoodie", "zip_style"] == {"Zip-Through", "Pullover"}
    assert {"Utility", "Chore", "Field"} <= seen["Utility Jacket", "jacket_style"]


def test_puffer_jacket_left_the_legacy_list_and_the_ceiling_followed() -> None:
    legacy = type_registry.legacy_types()
    assert ("Clothing", "Puffer Jacket") not in legacy
    assert len(legacy) == type_registry.LEGACY_CEILING


# --------------------------------------------------------------------------
# Drawings: the variant axis is a param, two readings draw differently, and a record states
# what the drawing shows.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("variant", VARIANTS, ids=IDS)
def test_a_shapes_param_changes_the_drawing(variant: tuple) -> None:
    shape, param, readings = variant
    assert shape in kit.SHAPES, f"no {shape} shape registered"
    drawn = [_svg(shape=shape, **{param: r}) for r in readings]
    assert len(set(drawn)) == len(readings), "every reading draws differently"
    assert _svg(shape=shape) == drawn[0], "the default is the first reading"
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid and "url(#fill-b)" in striped
    xml.dom.minidom.parseString(solid)


def test_every_style_draws_its_params_and_prints_no_size() -> None:
    known: dict[str, set[str]] = {}
    for shape, param, _ in VARIANTS:
        known.setdefault(shape, set()).add(param)
    rows = _all_rows()
    assert len(rows) >= 11 * 4
    for row in rows:
        assert row.params and {k for k, _ in row.params} <= known[row.shape], row.code
        xml.dom.minidom.parseString(_svg(row))
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        assert [w for w in words if re.search(r"\d", w)] == [], row.code


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_styles_of_one_type_that_differ_on_the_axis_draw_differently(ptype: str) -> None:
    rows = _rows(ptype)
    drawn = {_svg(r) for r in rows}
    assert len(drawn) >= len({tuple(sorted(r.params)) for r in rows}) >= 2


def test_a_belted_trench_coat_draws_its_belt_and_a_hooded_one_its_hood() -> None:
    for row in _rows("Trench Coat"):
        belted = _values(row, "belted") == ["Yes"]
        assert belted == ('class="belt"' in _svg(row)), row.code
    for row in _rows("Raincoat") + _rows("Parka"):
        assert ('class="hood' in _svg(row)) == ("None" not in _values(row, "hood_type")), row.code


# --------------------------------------------------------------------------
# Colors: the six main colors across the styles of each type and audience.
# --------------------------------------------------------------------------


def test_every_type_and_audience_offers_the_six_main_colors() -> None:
    assert not set(TYPES) & set(main_colors.EXCEPTIONS)
    groups = main_colors.groups(scale.templates())
    mine = {k: v for k, v in groups.items() if k[0] in TYPES}
    assert {k[0] for k in mine} == set(TYPES)
    lacking = {k: [c for c in main_colors.MAIN_COLORS if c not in main_colors.offered(v)]
               for k, v in mine.items()}  # fmt: skip
    assert {k: c for k, c in lacking.items() if c} == {}


# --------------------------------------------------------------------------
# Text-match decoys (gen#294's rule): the decoy plan of the clothing department covers them.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_carries_its_text_match_decoys(ptype: str) -> None:
    planned = {s.product_type for s in decoy_apparel.types()}
    assert ptype in planned
    spec = _spec(ptype)
    if spec.apparel is not None:
        assert len(spec.apparel.compounds) >= 2, "real class 2 compounds, never an invented one"


def test_the_decoy_table_lists_the_new_types() -> None:
    doc = Path(__file__).resolve().parent.parent / "docs" / "retail-apparel-decoys.md"
    table = doc.read_text()
    assert [p for p in TYPES if p not in table] == []


# --------------------------------------------------------------------------
# Tree and build.
# --------------------------------------------------------------------------


def test_the_new_nodes_sit_in_the_tree_under_the_guards_rules() -> None:
    rows = _all_rows()
    paths = [tuple(r.path) for r in rows]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    assert (
        tree_guard.misplaced_title_findings([(f"BRD-{r.code}", r.title, r.path) for r in rows])
        == []
    )


@pytest.mark.timeout(300)
def test_every_outerwear_style_reaches_the_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    want = {f"BRD-{r.code}" for r in _all_rows()}
    assert want and want <= got
    mine = [d for d in docs if d["product_id"] in want]
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {d["product_type"] for d in mine} == set(TYPES)
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not (want & kept), "templates only: the seeded derivation is what it was"
