"""Hedge trimmers, garden furniture sets and parasols (gen#203, the part #353 left open).

The Garden department held lawn mowers, trimmers, barbecues and hoses (#353, #293) and no hedge
trimmer, garden furniture set or parasol. Each is a spec file (gen#351) drawn by
:mod:`kit_outdoor`; their text-match decoys sit with the other machines' in :mod:`garden_rows`
and are held by ``tests/test_retail_garden_203.py``. These checks hold what the issue asked for:
at least three styles from three invented brands, the key attributes as structured entries, a
measured SKU axis with its unit, the six main colors, a shape of its own whose params change the
picture, and a drawing that states what the record states.
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

import export  # noqa: E402
import garden_rows  # noqa: E402
import kit  # noqa: E402
import kit_garden  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import tree_guard  # noqa: E402
import type_registry  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

#: product type -> (spec key, shape, key attributes every style states, SKU axis (key, export
#: key, unit code), the tree leaf's parent).
TYPES = {
    "Hedge Trimmer": (
        "hedge_trimmer",
        "hedge_trimmer",
        {"power_source", "tooth_gap", "blade_length", "color"},
        ("blade_length_cm", "blade_length", "CMT"),
        ("Garden", "Lawn Care"),
    ),
    "Garden Furniture Set": (
        "garden_furniture_set",
        "garden_furniture",
        {"furniture_kind", "material", "cushions_included", "seats", "color"},
        ("seats", "seats", "C62"),
        ("Garden", "Garden Furniture"),
    ),
    "Parasol": (
        "parasol",
        "parasol",
        {"parasol_kind", "tilt", "base_included", "canopy_diameter", "color"},
        ("canopy_m", "canopy_diameter", "MTR"),
        ("Garden", "Garden Furniture"),
    ),
}


def _rows(ptype: str) -> tuple:
    spec = type_registry.specs().get(TYPES[ptype][0])
    assert spec is not None, f"type_specs/{TYPES[ptype][0]}.py is not registered"
    return spec.rows


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _attr(row, key: str) -> str | None:
    return next((a[2] for a in row.attrs if a[0] == key), None)


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_type_has_three_styles_from_three_invented_brands(ptype: str) -> None:
    rows = _rows(ptype)
    assert len(rows) >= 3 and len({r.brand for r in rows}) >= 3
    assert {r.product_type for r in rows} == {ptype} and {r.department for r in rows} == {"Garden"}


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_type_draws_as_a_shape_of_its_own(ptype: str) -> None:
    rows = _rows(ptype)
    shape = TYPES[ptype][1]
    assert {r.shape for r in rows} == {shape}
    assert shape in kit.SHAPES
    assert shape not in ("box", "box_wide")


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    need = TYPES[ptype][2]
    for row in _rows(ptype):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        assert need <= keys, (row.code, sorted(need - keys))


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_the_measured_axis_is_on_every_sku_with_its_unit(ptype: str) -> None:
    sku_key, export_key, unit = TYPES[ptype][3]
    for row in _rows(ptype):
        assert row.size_key == sku_key and row.sizes, row.code
        doc = export.standard_document(row.doc())
        entries = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == export_key]
        assert len(entries) == len(row.skus()), row.code
        assert {e["unit_code"] for e in entries} == {unit}, row.code


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_each_type_offers_the_six_main_colors_with_no_exception(ptype: str) -> None:
    assert ptype not in main_colors.EXCEPTIONS
    offered = {c[0] for r in _rows(ptype) for c in r.colors}
    assert set(main_colors.MAIN_COLORS) <= offered


def test_the_power_sources_kinds_and_materials_are_the_ones_the_issue_names() -> None:
    values: dict[str, set[str]] = collections.defaultdict(set)
    for ptype in TYPES:
        for row in _rows(ptype):
            for a in row.attrs:
                values[a[0]].add(a[2])
    assert values["power_source"] == {"Cordless Battery", "Corded Electric", "Petrol"}
    assert {"Bistro", "Dining", "Corner Lounge", "Sun Lounger"} == values["furniture_kind"]
    assert {"Rattan-Effect", "Aluminum", "Wood", "Steel"} == values["material"]
    assert values["parasol_kind"] == {"Center Pole", "Cantilever"}


def test_a_cordless_hedge_trimmer_states_its_battery_voltage_in_volts() -> None:
    for row in _rows("Hedge Trimmer"):
        doc = export.standard_document(row.doc())
        volts = [e for e in doc["attributes"] if e["key"] == "battery_voltage"]
        assert [e["unit_code"] for e in volts] == (
            ["VLT"] if _attr(row, "power_source") == "Cordless Battery" else []
        ), row.code
        gap = [e for e in doc["attributes"] if e["key"] == "tooth_gap"]
        assert [e["unit_code"] for e in gap] == ["MMT"], row.code


# --------------------------------------------------------------------------
# Drawings: each param changes the picture, and what the record states is what is drawn.
# --------------------------------------------------------------------------

VARIANTS = [
    ("hedge_trimmer", {"power": "cordless"}, {"power": "petrol"}),
    ("hedge_trimmer", {"power": "cordless"}, {"power": "electric"}),
    ("garden_furniture", {"kind": "dining"}, {"kind": "bistro"}),
    ("garden_furniture", {"kind": "dining"}, {"kind": "corner"}),
    ("garden_furniture", {"kind": "dining"}, {"kind": "lounger"}),
    ("garden_furniture", {"seats": "4"}, {"seats": "6"}),
    ("garden_furniture", {"cushions": "yes"}, {"cushions": "no"}),
    ("parasol", {"kind": "center"}, {"kind": "cantilever"}),
    ("parasol", {"tilt": "no"}, {"tilt": "yes"}),
    ("parasol", {"base": "no"}, {"base": "yes"}),
]


@pytest.mark.parametrize(("shape", "one", "other"), VARIANTS, ids=lambda v: str(v))
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    type_registry.specs()
    assert shape in kit.SHAPES, shape
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_every_style_draws_well_formed_svg(ptype: str) -> None:
    for row in _rows(ptype):
        xml.dom.minidom.parseString(_svg(row))


def test_a_hedge_trimmer_draws_the_power_source_its_record_states() -> None:
    marks = {
        "cordless": kit_garden.BATTERY_CLASS,
        "petrol": kit_garden.FUEL_CLASS,
        "electric": kit_garden.CABLE_CLASS,
    }
    rows = _rows("Hedge Trimmer")
    assert {dict(r.params)["power"] for r in rows} == set(marks)
    for row in rows:
        for name, cls in marks.items():
            assert (f'class="{cls}"' in _svg(row)) == (name == dict(row.params)["power"]), (
                row.code,
                name,
            )


def test_a_furniture_set_draws_one_seat_per_seat_it_sells_on_every_sku() -> None:
    for row in _rows("Garden Furniture Set"):
        for sku in row.skus():
            svg = kit.render(
                row.shape,
                kit.Fill("solid", "#123456", "#654321"),
                params={**dict(row.params), "seats": sku["seats"]},
            )
            drawn = len(re.findall(r'<g class="seat"', svg))
            assert drawn == int(sku["seats"]), (row.code, sku["seats"])


def test_a_furniture_set_draws_cushions_exactly_when_its_record_says_yes() -> None:
    rows = _rows("Garden Furniture Set")
    assert {_attr(r, "cushions_included") for r in rows} == {"Yes", "No"}
    for row in rows:
        assert ('class="cushion"' in _svg(row)) == (_attr(row, "cushions_included") == "Yes"), (
            row.code
        )


def test_a_parasol_draws_its_tilt_and_base_exactly_when_its_record_says_yes() -> None:
    rows = _rows("Parasol")
    for key, cls in (("tilt", "tilt"), ("base_included", "base")):
        assert {_attr(r, key) for r in rows} == {"Yes", "No"}, key
        for row in rows:
            assert (f'class="{cls}"' in _svg(row)) == (_attr(row, key) == "Yes"), (row.code, key)


@pytest.mark.parametrize("ptype", sorted(TYPES))
def test_no_outdoor_drawing_prints_a_size(ptype: str) -> None:
    for row in _rows(ptype):
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        assert [w for w in words if re.search(r"\d", w)] == [], row.code


# --------------------------------------------------------------------------
# Tree and build.
# --------------------------------------------------------------------------


def test_the_tree_places_each_type_under_its_group_and_passes_the_guard() -> None:
    for ptype, (_k, _s, _a, _x, parent) in TYPES.items():
        assert {tuple(r.path[:2]) for r in _rows(ptype)} == {parent}, ptype
    paths = [tuple(r.path) for ptype in TYPES for r in _rows(ptype)]
    paths += [tuple(r.path) for r in garden_rows.ROWS]
    assert tree_guard.sibling_head_noun_findings(paths) == []
    assert tree_guard.headless_group_findings(paths) == []
    titles = [(f"BRD-{r.code}", r.title, r.path) for ptype in TYPES for r in _rows(ptype)]
    assert tree_guard.misplaced_title_findings(titles) == []


@pytest.mark.timeout(300)
def test_every_outdoor_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    ids = {f"BRD-{r.code}" for ptype in TYPES for r in _rows(ptype)}
    docs = scale.documents(scale.build(100_000))
    mine = [d for d in docs if d["product_id"] in ids]
    assert len(mine) == len(ids)
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.DECOY_IDS) == []
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not (ids & kept)
