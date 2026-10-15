"""Retail beauty depth (gen#214): mascara, primer, setting spray, serum, face mask, eye patches,
body mist, aftershave, talc and sun cream.

:mod:`beauty_rows` holds the styles and their text-match decoys, :mod:`kit_beauty` draws them.
These checks hold what the issue asked for: every type has three styles from three invented
brands, each style draws as its own shape with the variant axis as a param, each key attribute is
a structured entry in the export, the SKU axes carry their units, each type carries decoys of
three classes (gen#294's rule) whose fields tell the truth, and the styles reach the build.
"""

from __future__ import annotations

import collections
import re
import sys
import xml.dom.minidom
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import beauty_rows  # noqa: E402
import export  # noqa: E402
import kit  # noqa: E402
import kit_beauty  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = beauty_rows.ROWS
DECOYS = beauty_rows.DECOYS
#: product type -> (shape, the key attributes every style states).
TYPES = {
    "Mascara": ("mascara", {"effect", "waterproof", "color"}),
    "Face Primer": ("primer", {"finish", "skin_type", "net_volume"}),
    "Setting Spray": ("setting_spray", {"finish", "skin_type", "net_volume"}),
    "Serum": ("serum", {"active", "skin_concern", "net_volume"}),
    "Face Mask": ("face_mask", {"mask_type", "skin_concern", "units_per_pack"}),
    "Eye Patches": ("eye_patches", {"patch_type", "skin_concern", "units_per_pack"}),
    "Body Mist": ("body_mist", {"fragrance_family", "fragrance", "net_volume"}),
    "Aftershave": ("aftershave", {"fragrance_family", "concentration", "net_volume"}),
    "Talc": ("talc", {"fragrance", "net_weight"}),
    "Sun Cream": ("sun_cream", {"area", "spf", "net_volume"}),
}
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
    "Sun Cream": {"spf": None, "net_volume": "MLT"},
}
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
    ("sun_cream", {"form": "tube"}, {"form": "spray"}, None),
]


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


def _of(ptype: str, rows=ROWS) -> list:
    return [r for r in rows if r.product_type == ptype]


def test_the_ten_types_are_all_here() -> None:
    assert {r.product_type for r in ROWS} == set(TYPES)


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_has_three_styles_from_three_invented_brands(ptype: str) -> None:
    rows = _of(ptype)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3
    assert {r.brand for r in rows} <= set(beauty_rows.BRANDS)


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_draws_as_the_types_own_shape(ptype: str) -> None:
    shape = TYPES[ptype][0]
    assert {r.shape for r in _of(ptype)} == {shape}
    assert kit.SHAPES[shape] is kit_beauty.SHAPES[shape]
    assert shape not in {"box", "box_wide", "bottle", "jar", "tub", "tin"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_type_is_named_and_filed_under_beauty(ptype: str) -> None:
    for row in _of(ptype):
        assert row.department == "Beauty" and row.path[0] == "Beauty" and len(row.path) >= 3
        assert _doc(row)["product_type"] == ptype
        assert row.path[-1] == _doc(row)["category_leaf"]


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {r.code: sorted(TYPES[ptype][1] - _keys(r)) for r in _of(ptype)}
    assert {c: m for c, m in missing.items() if m} == {}


@pytest.mark.parametrize("ptype", sorted(AXES))
def test_the_variant_axes_are_on_the_skus_with_their_units(ptype: str) -> None:
    assert _of(ptype)
    for row in _of(ptype):
        skus = _doc(row)["variants"]
        assert len(skus) >= 3, row.code
        for key, unit in AXES[ptype].items():
            entries = [e for v in skus for e in v["attributes"] if e["key"] == key]
            assert entries, (row.code, key)
            if unit:
                assert {e["unit_code"] for e in entries} == {unit}, row.code


def test_a_sun_cream_and_a_body_mist_are_sold_across_two_axes() -> None:
    pairs_of = (("Sun Cream", "spf", "net_volume"), ("Body Mist", "fragrance", "net_volume"))
    for ptype, a, b in pairs_of:
        assert _of(ptype)
        for row in _of(ptype):
            skus = _doc(row)["variants"]
            pairs = {
                (next(e["value"] for e in v["attributes"] if e["key"] == a),
                 next(e["value"] for e in v["attributes"] if e["key"] == b))
                for v in skus
            }
            assert len(pairs) == len(skus) >= 4, row.code
            assert len({p[0] for p in pairs}) >= 2 and len({p[1] for p in pairs}) >= 2, row.code


def test_the_filter_values_the_issue_names_are_all_offered() -> None:
    def seen(ptype: str, key: str) -> set[str]:
        return {a[2] for r in _of(ptype) for a in r.attrs if a[0] == key}

    assert seen("Mascara", "effect") == {"Volume", "Length", "Curl"}
    assert seen("Mascara", "waterproof") == {"Yes", "No"}
    assert {"Matte", "Dewy"} <= seen("Face Primer", "finish")
    assert {"Matte", "Dewy"} <= seen("Setting Spray", "finish")
    assert {"Retinol", "Vitamin C", "Hyaluronic Acid", "Niacinamide"} <= seen("Serum", "active")
    assert {"Sheet", "Clay", "Overnight"} <= seen("Face Mask", "mask_type")
    assert "Hydrogel" in seen("Eye Patches", "patch_type")
    assert {"Face", "Body"} == seen("Sun Cream", "area")
    assert len(seen("Aftershave", "concentration")) >= 2


# --------------------------------------------------------------------------
# Drawings: the variant axis is a param that changes the picture.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("variant", VARIANTS, ids=[v[0] for v in VARIANTS])
def test_a_param_changes_the_drawing(variant: tuple) -> None:
    shape, one, other, third = variant
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"
    if third:
        both = {_svg(shape=shape, **one), _svg(shape=shape, **other)}
        assert _svg(shape=shape, **third) not in both


@pytest.mark.parametrize("variant", VARIANTS, ids=[v[0] for v in VARIANTS])
def test_a_shape_paints_the_records_fill_and_is_well_formed(variant: tuple) -> None:
    shape = variant[0]
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid and "url(#fill-b)" in striped
    xml.dom.minidom.parseString(solid)


def test_every_style_draws_its_param_and_prints_no_size() -> None:
    known = {v[0]: {k for d in v[1:] if d for k in d} for v in VARIANTS}
    assert ROWS and DECOYS
    for row in (*ROWS, *DECOYS):
        assert {k for k, _ in row.params} <= known[row.shape], row.code
        xml.dom.minidom.parseString(_svg(row))
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        printed = [w for w in words if re.search(r"\d", w)]
        assert printed == [], row.code


def test_styles_of_one_type_that_differ_on_the_axis_draw_differently() -> None:
    for ptype in TYPES:
        drawn = {(_svg(r)) for r in _of(ptype)}
        assert len(drawn) >= 2, ptype


# --------------------------------------------------------------------------
# Colors: a mascara has shades (declared), the rest is sold in its one pack.
# --------------------------------------------------------------------------


def test_mascara_is_a_declared_shade_exception_and_the_rest_carry_no_color() -> None:
    assert "Mascara" in main_colors.EXCEPTIONS
    for row in ROWS:
        assert row.colorless == (row.product_type != "Mascara"), row.code
    shades = {c[0] for r in _of("Mascara") for c in r.colors}
    assert {"Black", "Brown", "Blue"} <= shades


# --------------------------------------------------------------------------
# Text-match decoys (gen#294's rule): the words mislead a text search, the fields tell the truth.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_type_carries_decoys_of_three_classes(ptype: str) -> None:
    mine = _of(ptype, DECOYS)
    assert {d.cls for d in mine} >= {1, 2, 3}, ptype
    assert len(mine) >= 3


def test_a_decoys_misleading_word_is_in_the_text_and_in_no_field() -> None:
    assert DECOYS
    for d in DECOYS:
        doc = _doc(d)
        assert d.word.lower() in d.title.lower() + " " + d.description.lower(), d.code
        if d.cls in (2, 3):  # the word sits in a short title: the range name or the brand
            assert len(d.title.split()) <= 5, d.code
        if d.cls == 3:
            assert d.word.lower() in d.brand.lower(), d.code
        fields = " ".join(
            str(e["value"]).lower() for e in doc["attributes"]
        ) + " ".join(str(c[0]).lower() for c in d.colors)
        assert not re.search(rf"\b{re.escape(d.word.lower())}\b", fields), d.code
        assert d.product_type in TYPES, d.code


def test_decoys_are_templates_never_derived_and_exempt_from_the_text_check_by_id() -> None:
    tpls = scale.templates()
    kept = {r["product_id"] for r in scale.derivable(tpls)}
    assert scale.BEAUTY_IDS and not (scale.BEAUTY_IDS & kept)
    assert scale.BEAUTY_DECOY_IDS == {f"BRD-{d.code}" for d in DECOYS} <= scale.DECOY_IDS
    assert not scale.BEAUTY_DECOY_IDS & {f"BRD-{r.code}" for r in ROWS}


def test_the_shade_word_queries_find_a_decoy_in_the_text_and_a_real_style() -> None:
    """``red mascara``-like queries: a decoy's title names a shade the real mascaras may lack."""
    words = {d.word.lower() for d in _of("Mascara", DECOYS)}
    assert words & {"red", "pink", "purple", "blue", "green", "white", "yellow"}


# --------------------------------------------------------------------------
# Tree and build.
# --------------------------------------------------------------------------


def test_the_new_nodes_sit_in_the_tree_under_the_guards_rules() -> None:
    paths = [tuple(r.path) for r in (*ROWS, *DECOYS)]
    assert paths
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in (*ROWS, *DECOYS)]
    assert tree_guard.misplaced_title_findings(rows) == []


@pytest.mark.timeout(300)
def test_every_beauty_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    want = {f"BRD-{r.code}" for r in (*ROWS, *DECOYS)}
    assert want and want <= got
    mine = [d for d in docs if d["product_id"] in want]
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.DECOY_IDS) == []
    assert len({d["product_type"] for d in mine}) >= len(TYPES)


@pytest.mark.timeout(300)
def test_every_brand_has_exactly_one_owner() -> None:
    records = scale.build(100_000).records
    owners: dict[str, set[str]] = collections.defaultdict(set)
    for rec in [*scale.templates(), *records]:
        if "brand_owner" in rec:
            owners[rec["brand"]].add(rec["brand_owner"])
    mine = {r.brand for r in (*ROWS, *DECOYS)}
    assert mine and mine <= set(owners)
    assert {b: sorted(o) for b, o in owners.items() if b in mine and len(o) != 1} == {}
