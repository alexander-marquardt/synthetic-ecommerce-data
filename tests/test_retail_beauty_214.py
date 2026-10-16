"""Retail beauty depth (gen#214): mascara, primer, setting spray, serum, face mask, eye patches,
body mist, aftershave and talc.

Each type is its own spec under ``type_specs/`` (gen#351) and ``kit_beauty`` draws it. These checks
hold what the issue asked for: every type has three styles from three invented brands, each style
draws as its own shape with the variant axis as a param, each key attribute is a structured entry
in the export, the SKU axes carry their units, each type carries text-match decoys (gen#294's
rule) whose fields tell the truth, and the styles reach the build.
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

import export  # noqa: E402
import house_styles  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: product type -> (spec key, shape, the key attributes every style states).
TYPES = {
    "Mascara": ("mascara", "mascara", {"effect", "waterproof", "color"}),
    "Face Primer": ("face_primer", "primer", {"finish", "skin_type", "net_volume"}),
    "Setting Spray": ("setting_spray", "setting_spray", {"finish", "skin_type", "net_volume"}),
    "Serum": ("serum", "serum", {"active", "skin_concern", "net_volume"}),
    "Face Mask": ("face_mask", "face_mask", {"mask_type", "skin_concern", "units_per_pack"}),
    "Eye Patches": ("eye_patches", "eye_patches", {"patch_type", "skin_concern", "units_per_pack"}),
    "Body Mist": ("body_mist", "body_mist", {"fragrance_family", "fragrance", "net_volume"}),
    "Aftershave": ("aftershave", "aftershave", {"fragrance_family", "concentration", "net_volume"}),
    "Talc": ("talc", "talc", {"fragrance", "net_weight"}),
}  # fmt: skip
#: product type -> the SKU option keys it varies on and each one's unit code in the export.
AXES = {
    "Mascara": {"color": None},
    "Face Primer": {"net_volume": "MLT"},
    "Setting Spray": {"net_volume": "MLT"},
    "Serum": {"net_volume": "MLT"},
    "Face Mask": {"units_per_pack": "C62"},
    "Eye Patches": {"units_per_pack": "C62"},
    "Body Mist": {"fragrance": None, "net_volume": "MLT"},
    "Aftershave": {"net_volume": "MLT"},
    "Talc": {"net_weight": "GRM"},
}
#: product type -> the misleading word its decoys carry (the head of the query they target).
WORDS = {
    "Mascara": "", "Face Primer": "dewy", "Setting Spray": "dewy", "Serum": "vitamin c",
    "Face Mask": "clay", "Eye Patches": "cloth", "Body Mist": "vanilla", "Aftershave": "citrus",
    "Talc": "rose",
}  # fmt: skip
#: shape -> two param readings that must draw differently (the first is the default).
VARIANTS = [
    ("mascara", {"effect": "volume"}, {"effect": "length"}, {"effect": "curl"}),
    ("primer", {"form": "tube"}, {"form": "pump"}, None),
    ("setting_spray", {"nozzle": "mist"}, {"nozzle": "pump"}, None),
    ("serum", {"form": "dropper"}, {"form": "pump"}, None),
    ("face_mask", {"mask": "sheet"}, {"mask": "clay"}, {"mask": "overnight"}),
    ("eye_patches", {"patch": "hydrogel"}, {"patch": "cloth"}, None),
    ("body_mist", {"cap": "dome"}, {"cap": "ring"}, None),
    ("aftershave", {"cap": "stopper"}, {"cap": "spray"}, None),
    ("talc", {"lid": "shaker"}, {"lid": "puff"}, None),
]


def _spec(ptype: str) -> type_registry.TypeSpec:
    spec = type_registry.specs().get(TYPES[ptype][0])
    assert spec is not None, f"{ptype}: no spec type_specs/{TYPES[ptype][0]}.py"
    spec.docs()  # states the spec's brand owners
    return spec


def _rows(ptype: str) -> list:
    return list(_spec(ptype).rows)


def _decoys(ptype: str) -> list:
    return list(_spec(ptype).decoys)


def _all_rows() -> list:
    return [r for p in TYPES for r in _rows(p)]


def _all_decoys() -> list:
    return [d for p in TYPES for d in _decoys(p)]


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


def _seen(ptype: str, key: str) -> set[str]:
    return {str(e["value"]) for r in _rows(ptype) for e in _doc(r)["attributes"] if e["key"] == key}


def test_the_nine_types_are_registered_each_as_its_own_spec() -> None:
    assert [_spec(p).key for p in TYPES] == [k for k, _, _ in TYPES.values()]
    assert {_spec(p).product_type for p in TYPES} == set(TYPES)
    assert not any(_spec(p).derivable for p in TYPES), "the range grows by authored rows"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_has_three_styles_from_three_invented_brands(ptype: str) -> None:
    rows = _rows(ptype)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3
    owners = dict(_spec(ptype).owners)
    assert {r.brand for r in rows} <= set(owners)
    assert set(owners.values()) == {"third_party"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_draws_as_the_types_own_shape(ptype: str) -> None:
    shape = TYPES[ptype][1]
    assert {r.shape for r in _rows(ptype)} == {shape}
    assert shape in kit.SHAPES
    assert shape not in {"box", "box_wide", "bottle", "jar", "tub", "tin"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_type_is_named_and_filed_under_beauty(ptype: str) -> None:
    for row in _rows(ptype):
        assert row.department == "Beauty" and row.path[0] == "Beauty" and len(row.path) >= 3
        assert _doc(row)["product_type"] == ptype
        assert row.path[-1] == _doc(row)["category_leaf"]


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_key_attribute_is_a_structured_entry_not_a_word_in_the_title(ptype: str) -> None:
    want = TYPES[ptype][2]
    missing = {r.code: want - _keys(r) for r in _rows(ptype)}
    assert {c: m for c, m in missing.items() if m} == {}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_sku_axes_are_options_with_their_units(ptype: str) -> None:
    for row in _rows(ptype):
        doc = _doc(row)
        skus = doc["variants"]
        assert len(skus) >= 2, row.code
        for key, unit in AXES[ptype].items():
            entries = [e for v in skus for e in v["attributes"] if e["key"] == key]
            assert entries, (row.code, key)
            if unit:
                assert {e["unit_code"] for e in entries} == {unit}, row.code
        if len(AXES[ptype]) == 2:  # fragrance x size: every fragrance in every size
            pairs = [
                tuple(e["value"] for k in AXES[ptype] for e in v["attributes"] if e["key"] == k)
                for v in skus
            ]
            assert len(set(pairs)) == len(skus) >= 4, row.code
            assert len({p[0] for p in pairs}) >= 2 and len({p[1] for p in pairs}) >= 2, row.code


def test_the_attribute_values_a_shopper_filters_on_are_all_stated() -> None:
    assert _seen("Mascara", "effect") == {"Volume", "Length", "Curl"}
    assert _seen("Mascara", "waterproof") == {"Yes", "No"}
    assert {"Matte", "Dewy"} <= _seen("Face Primer", "finish")
    assert {"Matte", "Dewy"} <= _seen("Setting Spray", "finish")
    assert {"Retinol", "Vitamin C", "Hyaluronic Acid", "Niacinamide"} <= _seen("Serum", "active")
    assert {"Sheet", "Clay", "Overnight"} <= _seen("Face Mask", "mask_type")
    assert "Hydrogel" in _seen("Eye Patches", "patch_type")
    assert len(_seen("Aftershave", "concentration")) >= 2


# --------------------------------------------------------------------------
# Drawings: the variant axis is a param, two readings draw differently.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("variant", VARIANTS, ids=[v[0] for v in VARIANTS])
def test_a_shapes_param_changes_the_drawing(variant: tuple) -> None:
    shape, one, other, third = variant
    assert shape in kit.SHAPES, f"no {shape} shape registered"
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"
    if third:
        both = {_svg(shape=shape, **one), _svg(shape=shape, **other)}
        assert _svg(shape=shape, **third) not in both
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid and "url(#fill-b)" in striped
    xml.dom.minidom.parseString(solid)


def test_every_style_draws_its_param_and_prints_no_size() -> None:
    known = {v[0]: {k for d in v[1:] if d for k in d} for v in VARIANTS}
    rows = [*_all_rows(), *(d.row for d in _all_decoys())]
    assert len(rows) >= 50
    for row in rows:
        assert {k for k, _ in row.params} <= known[row.shape], row.code
        xml.dom.minidom.parseString(_svg(row))
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        assert [w for w in words if re.search(r"\d", w)] == [], row.code


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_styles_of_one_type_that_differ_on_the_axis_draw_differently(ptype: str) -> None:
    assert len({_svg(r) for r in _rows(ptype)}) >= 2


# --------------------------------------------------------------------------
# Colors: a mascara has shades (declared), the rest is sold in its one pack.
# --------------------------------------------------------------------------


def test_mascara_is_a_declared_shade_exception_and_the_rest_carry_no_color() -> None:
    assert "Mascara" in main_colors.EXCEPTIONS
    for ptype in TYPES:
        for row in _rows(ptype):
            assert row.colorless == (ptype != "Mascara"), row.code
    shades = {c[0] for r in _rows("Mascara") for c in r.colors}
    assert {"Black", "Brown", "Blue"} <= shades


# --------------------------------------------------------------------------
# Text-match decoys (gen#294's rule): the words mislead a text search, the fields tell the truth.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_carries_three_decoys_of_three_classes(ptype: str) -> None:
    mine = _decoys(ptype)
    assert len(mine) >= 3
    assert len({d.cls for d in mine}) >= 3
    assert {6, 7} <= {d.cls for d in mine}, "an incidental-word decoy and a brand decoy (gen#294)"


def test_a_decoys_misleading_word_is_in_the_text_and_in_no_field() -> None:
    decoys = _all_decoys()
    assert len(decoys) >= 27
    for d in decoys:
        row = d.row
        word = WORDS[row.product_type] or d.query.split(" ")[0]
        assert d.query.startswith(word), (row.code, d.query)
        text = (row.title + " " + row.description + " " + row.brand).lower()
        assert word in text, (row.code, word)
        if d.cls in (6, 7):  # the word sits in a short title: the range name or the brand
            assert len(row.title.split()) <= 5, row.code
        if d.cls == 7:
            assert word in row.brand.lower(), row.code
        doc = _doc(row)
        fields = " ".join(str(e["value"]).lower() for e in doc["attributes"]) + " ".join(
            str(c[0]).lower() for c in row.colors
        )
        assert not re.search(rf"\b{re.escape(word)}\b", fields), row.code
        assert row.product_type in TYPES, row.code


def test_decoys_are_templates_never_derived_and_never_colored() -> None:
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    ids = {f"BRD-{r.code}" for r in _all_rows()} | {f"BRD-{d.row.code}" for d in _all_decoys()}
    assert len(ids) == len(_all_rows()) + len(_all_decoys())
    assert ids and not (ids & kept)
    assert {f"BRD-{d.row.code}" for d in _all_decoys()} <= type_registry.decoy_ids()


# --------------------------------------------------------------------------
# Tree and build.
# --------------------------------------------------------------------------


def test_the_new_nodes_sit_in_the_tree_under_the_guards_rules() -> None:
    rows = [*_all_rows(), *(d.row for d in _all_decoys())]
    paths = [tuple(r.path) for r in rows]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    assert (
        tree_guard.misplaced_title_findings([(f"BRD-{r.code}", r.title, r.path) for r in rows])
        == []
    )


@pytest.mark.timeout(300)
def test_every_beauty_style_reaches_the_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    want = {f"BRD-{r.code}" for r in _all_rows()} | {f"BRD-{d.row.code}" for d in _all_decoys()}
    assert want and want <= got
    mine = [d for d in docs if d["product_id"] in want]
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.TEXT_EXEMPT) == []
    assert {d["product_type"] for d in mine} == set(TYPES)


def test_each_invented_beauty_brand_has_a_house_style_of_its_own() -> None:
    """A brand's mark and its logo arrangement with wordmark belong to it alone (house_styles)."""
    styles = house_styles.HOUSE_STYLES
    brands = {r.brand for r in _all_rows()} | {d.row.brand for d in _all_decoys()}
    assert brands and brands <= set(styles)
    for brand in sorted(brands):
        others = [s for b, s in styles.items() if b != brand]
        assert styles[brand].mark not in {s.mark for s in others}, brand
        assert house_styles.lockup_key(styles[brand]) not in {
            house_styles.lockup_key(s) for s in others
        }, brand
