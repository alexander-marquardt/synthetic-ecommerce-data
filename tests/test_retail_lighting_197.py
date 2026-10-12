"""Retail lighting (gen#197): floor, table, desk, ceiling and wall lights, and lampshades.

Each type is a leaf of its own under ``Home/Lighting`` with at least three styles from at
least three brands; its key attributes are structured entries in the exported document; a
SKU's second axis (a finish, a shade color, a diameter) is drawn in that SKU's own image;
and a derived style that changes a drawn attribute redraws it.
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import image_release  # noqa: E402
import kit  # noqa: E402
import lighting_rows  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

DOCS = lighting_rows.docs()
IDS = {d["product_id"] for d in DOCS}

#: product type -> (leaf, shape, the key attributes every style of it carries as entries,
#: the SKU axis beside color, or None)
TYPES = {
    "Floor Lamp": ("Floor Lamps", "floor_lamp",
                   {"style", "height", "shade_material", "switch", "bulb_fitting"}, "finish"),
    "Table Lamp": ("Table Lamps", "table_lamp",
                   {"style", "height", "base_material", "power"}, "shade_color"),
    "Desk Lamp": ("Desk Lamps", "desk_lamp", {"arm", "color_temperature"}, None),
    "Ceiling Light": ("Ceiling Lights", "ceiling_light",
                      {"fixture_type", "light_count", "shade_material", "bulb_fitting"},
                      "finish"),
    "Wall Light": ("Wall Lights", "wall_light",
                   {"fixture_type", "power", "switch", "ip_rating"}, "finish"),
    "Lampshade": ("Lampshades", "lampshade", {"shape", "fitting", "fabric", "pattern"},
                  "diameter"),
}  # fmt: skip


def _by_type() -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = collections.defaultdict(list)
    for d in DOCS:
        out[d["product_type"]].append(d)
    return out


def test_every_type_has_three_styles_from_three_brands_in_its_own_leaf() -> None:
    by_type = _by_type()
    assert sorted(by_type) == sorted(TYPES)
    for ptype, recs in by_type.items():
        leaf, shape, _, _ = TYPES[ptype]
        assert len(recs) >= 3, ptype
        assert len({r["brand"] for r in recs}) >= 3, ptype
        assert {tuple(r["category_path"]) for r in recs} == {("Home", "Lighting", leaf)}, ptype
        assert {r["drawing"]["shape"] for r in recs} == {shape}, ptype
        assert all(shape in kit.SHAPES for r in recs)


def test_key_attributes_are_structured_entries_and_the_sku_axis_is_a_variant_entry() -> None:
    standard = [export.standard_document(d) for d in DOCS]
    assert check_catalog(standard) == []
    for doc in standard:
        keys, axis = TYPES[doc["product_type"]][2], TYPES[doc["product_type"]][3]
        assert keys <= {e["key"] for e in doc["attributes"]}, doc["product_id"]
        if axis is not None:
            assert all(
                any(e["key"] == axis for e in v["attributes"]) for v in doc["variants"]
            ), doc["product_id"]
            assert axis in doc["variant_axes"], doc["product_id"]


def test_a_lampshade_diameter_is_a_measured_variant_entry() -> None:
    shade = next(d for d in DOCS if d["product_type"] == "Lampshade")
    entries = [
        e for v in export.standard_document(shade)["variants"] for e in v["attributes"]
        if e["key"] == "diameter"
    ]  # fmt: skip
    assert entries and all(e["unit_code"] == "CMT" for e in entries)
    assert {e["value_canonical"] for e in entries} == {
        float(s["diameter_cm"]) * 10 for s in shade["skus"]
    }


@pytest.mark.parametrize("pid", sorted(IDS))
def test_each_sku_draws_its_own_second_axis_and_gets_its_own_image(pid: str) -> None:
    rec = next(d for d in DOCS if d["product_id"] == pid)
    params = rec["drawing"].get("params", {})
    for sku in rec["skus"]:
        drawn = image_release.colorway_drawing(rec, sku)["params"]
        for key in params:
            if key in sku:
                assert drawn[key] == str(sku[key]), (sku["sku"], key)
    ids = {export.image_id(rec, s) for s in rec["skus"]}
    assert len(ids) == len(rec["skus"]), pid
    assert len(image_release.image_files([rec])) == len(rec["skus"])


def test_a_sku_that_carries_no_drawing_param_keeps_its_image_id() -> None:
    """The SKU's own param values join the image spec only when it carries one, so no other
    template's image id moves."""
    others = [t for t in scale.templates() if t["product_id"] not in IDS]
    for t in others:
        for s in t["skus"]:
            assert "params" not in export.drawing_spec(t, s), s["sku"]


def test_lighting_styles_are_templates_a_derived_style_may_come_from() -> None:
    derivable = {t["product_id"] for t in scale.derivable(scale.templates())}
    assert derivable >= IDS


@pytest.mark.parametrize(
    ("pid", "key", "new", "param"),
    [
        ("BRD-LTFARC", "style", "Tripod", "style"),
        ("BRD-LTCPND", "fixture_type", "Flush", "kind"),
        ("BRD-LTDGNK", "arm", "Clamp-On", "arm"),
        ("BRD-LTSDRM", "shape", "Pleated", "form"),
        ("BRD-LTWSWG", "power", "Rechargeable", "power"),
    ],
)
def test_a_derived_style_that_changes_a_drawn_attribute_redraws_it(
    pid: str, key: str, new: str, param: str
) -> None:
    tpl = next(d for d in DOCS if d["product_id"] == pid)
    colors = [tpl["color_options"][0]["color"]]
    rec = scale.derive(
        tpl, "BRD-TEST", "Ashcombe", tpl["brand"], {key: new}, colors,
        {tpl["brand"]: "own"}, random.Random(0),
    )  # fmt: skip
    assert rec["drawing"]["params"][param] == new.lower()
    image_release.render(rec, rec["skus"][0])


def test_a_safety_rating_and_a_shade_fitting_never_vary() -> None:
    pools = scale.value_pools(scale.derivable(scale.templates()))
    for d in DOCS:
        variable = scale.variable_keys(d, pools)
        assert "ip_rating" not in variable and "fitting" not in variable, d["product_id"]
