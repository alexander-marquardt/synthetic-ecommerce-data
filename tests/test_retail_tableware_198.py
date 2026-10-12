"""The tableware and kitchen utensil types (gen#198): each one sells as its own product type,
with its shopper attributes structured, its own drawing, and a drawn kind that follows the row.

Guard: a type that loses a style, a brand, a key attribute or its own shape fails here, by type.
"""

from __future__ import annotations

import inspect
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parents[1] / "prototypes" / "retail_drawings"
sys.path.insert(0, str(HERE))

import export  # noqa: E402
import kit  # noqa: E402
import kit_tableware  # noqa: E402
import scale  # noqa: E402
import tableware_rows  # noqa: E402

#: product type -> its category leaf, its shape, and the keys its shoppers filter on. A key
#: the SKUs carry (a pack size, a blade length) is read from the exported variants too.
TYPES = {
    "Plate": ("Plates", "plate",
              {"plate_type", "diameter", "material", "finish", "dishwasher_safe", "pack_size"}),
    "Bowl": ("Bowls", "bowl", {"bowl_type", "diameter", "capacity", "material"}),
    "Cutlery": ("Cutlery", "cutlery_piece", {"cutlery_type", "material", "handle", "pack_size"}),
    "Kitchen Knife": ("Kitchen Knives", "kitchen_knife",
                      {"knife_type", "blade_length", "blade_steel", "handle_material"}),
    "Glassware": ("Glassware", "drinking_glass",
                  {"glass_type", "capacity", "material", "pack_size"}),
    "Kitchen Utensil": ("Kitchen Utensils", "kitchen_utensil", {"utensil_type", "material"}),
    "Chopping Board": ("Chopping Boards", "chopping_board", {"material", "dimensions"}),
    "Colander": ("Colanders", "colander", {"material", "diameter", "capacity"}),
}  # fmt: skip

#: shape -> the param that names the drawn kind, which two of its rows must differ on.
KIND_PARAM = {
    "plate": "kind", "bowl": "kind", "cutlery_piece": "piece", "kitchen_knife": "kind",
    "drinking_glass": "kind", "kitchen_utensil": "kind", "chopping_board": "material",
    "colander": "material",
}  # fmt: skip

#: (shape, kind) the shape draws in its closing ``else`` (a plastic board's juice groove, a
#: plastic colander's slots), so an unknown kind draws it too: not a fall-through.
LAST_BRANCH = {("chopping_board", "plastic"), ("colander", "plastic")}

DOCS = tableware_rows.docs()


def _of(ptype: str) -> list[dict]:
    return [d for d in DOCS if d["product_type"] == ptype]


#: exported key -> the SKU field it comes from: a row sold in one size (a platter, a block
#: set, a set of boards) has no such axis, so only a row whose SKUs vary on it must state it.
AXES = {"pack_size": "pack_size", "blade_length": "blade_length_cm", "dimensions": "dimensions"}


def _wanted(ptype: str, doc: dict) -> set[str]:
    return {k for k in TYPES[ptype][2] if k not in AXES or any(AXES[k] in s for s in doc["skus"])}


def _keys(doc: dict) -> set[str]:
    std = export.standard_document(doc)
    return {e["key"] for e in std["attributes"]} | {
        e["key"] for v in std["variants"] for e in v.get("attributes") or ()
    }


def test_every_type_has_rows_and_only_these_types() -> None:
    assert set(tableware_rows.TYPES) == {
        "Plate", "Bowl", "Cutlery", "Kitchen Knife", "Glassware", "Kitchen Utensil",
        "Chopping Board", "Colander",
    }  # fmt: skip
    assert {d["product_type"] for d in DOCS} == set(TYPES)


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_sells_three_styles_from_three_brands_under_its_own_leaf(ptype: str) -> None:
    docs = _of(ptype)
    leaf = TYPES[ptype][0]
    assert len(docs) >= 3
    assert len({d["brand"] for d in docs}) >= 3
    assert {tuple(d["category_path"]) for d in docs} == {("Home", "Kitchen & Dining", leaf)}


@pytest.mark.parametrize("ptype", TYPES)
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {d["product_id"]: sorted(_wanted(ptype, d) - _keys(d)) for d in _of(ptype)}
    assert {k: v for k, v in missing.items() if v} == {}


def test_a_knifes_blade_length_is_exported_with_its_unit() -> None:
    for d in _of("Kitchen Knife"):
        std = export.standard_document(d)
        lengths = [e for v in std["variants"] for e in v.get("attributes") or ()
                   if e["key"] == "blade_length"]  # fmt: skip
        if d["skus"] and "blade_length_cm" in d["skus"][0]:
            assert lengths and {e.get("unit_code") for e in lengths} == {"CMT"}, d["product_id"]


@pytest.mark.parametrize("ptype", TYPES)
def test_a_type_draws_with_its_own_shape(ptype: str) -> None:
    shape = TYPES[ptype][1]
    assert shape in kit_tableware.SHAPES
    assert {d["drawing"]["shape"] for d in _of(ptype)} == {shape}


@pytest.mark.parametrize("shape", kit_tableware.SHAPES)
def test_a_tableware_shape_paints_the_records_color_and_pattern(shape: str) -> None:
    assert shape in kit.SHAPES
    solid = kit.render(shape, kit.Fill("solid", "#123456", "#654321"), uid="a")
    striped = kit.render(shape, kit.Fill("stripe", "#abcdef", "#fedcba"), uid="b")
    assert "#123456" in solid
    assert "url(#fill-b)" in striped


@pytest.mark.parametrize("shape", kit_tableware.SHAPES)
def test_two_rows_that_differ_on_the_drawn_kind_draw_differently(shape: str) -> None:
    param = KIND_PARAM[shape]
    by_kind: dict[str, dict] = {}
    for d in DOCS:
        if d["drawing"]["shape"] == shape:
            by_kind.setdefault(d["drawing"]["params"][param], d["drawing"]["params"])
    assert len(by_kind) >= 2, by_kind
    fill = kit.Fill("solid", "#123456", "#654321")
    drawn = {kit.render(shape, fill, uid="k", params=p) for p in by_kind.values()}
    assert len(drawn) == len(by_kind)


def test_the_rows_are_scale_templates_and_the_kind_is_frozen() -> None:
    ids = {r["product_id"] for r in scale.templates()}
    assert {d["product_id"] for d in DOCS} <= ids
    kinds = {"plate_type", "bowl_type", "cutlery_type", "knife_type", "glass_type", "utensil_type"}
    assert kinds <= scale.FROZEN_KEYS


def test_a_pack_size_lists_every_pack_the_skus_sell() -> None:
    for d in DOCS:
        sizes = {str(s["pack_size"]) for s in d["skus"] if "pack_size" in s}
        if sizes:
            (entry,) = [a for a in d["attributes"] if a["key"] == "pack_size"]
            assert set(entry["value"].split(", ")) == sizes, d["product_id"]


def test_every_drawn_kind_is_one_its_shape_knows() -> None:
    """A kind the shape does not know falls through to its default drawing (a utensil set
    drawn as one spoon): each row's drawing differs from its shape's with the kind unknown,
    unless its kind IS the shape's default."""
    fill = kit.Fill("solid", "#123456", "#654321")
    fallen = []
    for d in DOCS:
        shape, params = d["drawing"]["shape"], d["drawing"]["params"]
        sig = inspect.signature(getattr(kit_tableware, shape))
        kind = params[KIND_PARAM[shape]]
        if kind == sig.parameters[KIND_PARAM[shape]].default or (shape, kind) in LAST_BRANCH:
            continue
        unknown = {**params, KIND_PARAM[shape]: "no such kind"}
        if kit.render(shape, fill, uid="k", params=params) == kit.render(
            shape, fill, uid="k", params=unknown
        ):
            fallen.append((d["product_id"], params[KIND_PARAM[shape]]))
    assert fallen == []


def test_a_knifes_image_states_no_blade_length_its_sku_does_not_sell() -> None:
    """One image serves every blade length of a color, so its chip names the length only
    when the style sells one, and otherwise the style's whole range."""
    import re

    fill = kit.Fill("solid", "#123456", "#654321")
    checked = 0
    for d in _of("Kitchen Knife"):
        lengths = sorted({int(s["blade_length_cm"]) for s in d["skus"] if "blade_length_cm" in s})
        if not lengths:
            continue
        svg = kit.render("kitchen_knife", fill, uid="k", params=d["drawing"]["params"])
        chips = re.findall(r">(\d+(?:-\d+)? cm)(?: blade)?<", svg)
        assert len(chips) == 1, (d["product_id"], chips)
        stated = [int(n) for n in chips[0].removesuffix(" cm").split("-")]
        want = [lengths[0]] if len(lengths) == 1 else [lengths[0], lengths[-1]]
        assert stated == want, (d["product_id"], chips, lengths)
        for s in d["skus"]:
            assert int(s["blade_length_cm"]) in range(stated[0], stated[-1] + 1), s["sku_id"]
            checked += 1
    assert checked >= 20
