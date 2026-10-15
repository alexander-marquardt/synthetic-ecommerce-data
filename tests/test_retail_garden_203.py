"""Garden machines, first increment (gen#203): lawn mowers, robot mowers, grass trimmers, barbecues.

:mod:`garden_rows` holds the styles and :mod:`kit_garden` draws them. These checks hold what the
issue asked for: every type has its range (three styles from three brands), each style draws as
its own shape, each key attribute is a structured entry in the export with its unit, a measured
axis is on the SKUs, every type offers the six main colors, every type carries text-match decoys
of five classes, three each, whose structured fields stay true (gen#294), the styles sit in the
tree under the tree guard's rules, and they reach the scaled build.
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

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ALL = garden_rows.ROWS
DECOY_CODES = set(garden_rows.DECOY_TABLE)
ROWS = tuple(r for r in ALL if r.code not in DECOY_CODES)

#: Each type and the key attributes every one of its styles states.
KEYS = {
    "Lawn Mower": {
        "power_source",
        "drive",
        "grass_box_capacity",
        "cutting_heights",
        "cutting_width",
        "color",
    },
    "Robot Mower": {"boundary", "app_control", "max_slope", "lawn_area", "color"},
    "Grass Trimmer": {"power_source", "cutting_head", "telescopic", "cutting_width", "color"},
    "BBQ": {"fuel", "bbq_kind", "lid", "side_shelves", "color"},
}

#: The SKU axis of a type, and what it becomes in the export (key, unit code) when it has a unit.
AXES = {
    "Lawn Mower": ("cutting_width_cm", "cutting_width", "CMT"),
    "Robot Mower": ("lawn_area_m2", "lawn_area", None),
    "Grass Trimmer": ("cutting_width_cm", "cutting_width", "CMT"),
}


def _keys(row) -> set[str]:
    doc = export.standard_document(row.doc())
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


def _svg(row=None, **kw) -> str:
    shape = row.shape if row else kw.pop("shape")
    params = dict(row.params) if row else kw
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_garden_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_garden.SHAPES} == {}
    assert len({r.shape for r in ROWS}) == len(KEYS)
    assert {r.shape for r in ROWS}.isdisjoint({"box", "box_wide"})


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        if KEYS[ptype] - _keys(row):
            missing[row.code] = sorted(KEYS[ptype] - _keys(row))
    assert missing == {}


def test_a_cordless_mower_and_trimmer_state_their_battery_voltage_in_volts() -> None:
    for row in (r for r in ROWS if r.product_type in ("Lawn Mower", "Grass Trimmer")):
        doc = export.standard_document(row.doc())
        volts = [e for e in doc["attributes"] if e["key"] == "battery_voltage"]
        if dict(row.params)["power"] == "cordless":
            assert [e["unit_code"] for e in volts] == ["VLT"], row.code
            assert volts[0]["value_canonical"] in (18.0, 36.0, 40.0), row.code
        else:
            assert volts == [], row.code


@pytest.mark.parametrize("ptype", sorted(AXES))
def test_a_measured_axis_is_on_every_sku(ptype: str) -> None:
    sku_key, export_key, unit = AXES[ptype]
    for row in (r for r in ROWS if r.product_type == ptype):
        assert row.size_key == sku_key, row.code
        assert row.sizes and all(sku_key in s for s in row.skus()), row.code
        doc = export.standard_document(row.doc())
        entries = [e for v in doc["variants"] for e in v["attributes"] if e["key"] == export_key]
        assert len(entries) == len(row.skus()), row.code
        if unit:
            assert {e["unit_code"] for e in entries} == {unit}, row.code


def test_a_barbecue_sells_its_size_or_states_its_burners() -> None:
    for row in (r for r in ROWS if r.product_type == "BBQ"):
        if dict(row.params)["kind"] == "gas":
            burners = [a for a in row.attrs if a[0] == "burners"]
            assert len(burners) == 1 and burners[0][3] == "C62", row.code
            assert str(dict(row.params)["burners"]) == burners[0][2], row.code
        else:
            assert row.size_key in ("diameter_cm", "length_cm") and len(row.sizes) >= 2, row.code
            assert not [a for a in row.attrs if a[0] == "burners"], row.code


def test_the_power_sources_and_fuels_are_the_ones_the_issue_names() -> None:
    values = collections.defaultdict(set)
    for row in ROWS:
        for a in row.attrs:
            if a[0] in ("power_source", "fuel", "bbq_kind", "boundary", "drive"):
                values[(row.product_type, a[0])].add(a[2])
    assert values[("Lawn Mower", "power_source")] == {
        "Cordless Battery",
        "Petrol",
        "Corded Electric",
    }
    assert values[("Lawn Mower", "drive")] == {"Push", "Self-Propelled"}
    assert values[("Robot Mower", "boundary")] == {"Wire", "Wire-Free GPS"}
    assert values[("BBQ", "fuel")] == {"Charcoal", "Gas"}
    assert {"Kettle", "Barrel", "Kamado", "Portable", "Gas"} == values[("BBQ", "bbq_kind")]


# --------------------------------------------------------------------------
# Drawings: each param changes the picture, and what the record states is what is drawn.
# --------------------------------------------------------------------------

VARIANTS = [
    ("lawn_mower", {"power": "cordless"}, {"power": "petrol"}),
    ("lawn_mower", {"power": "cordless"}, {"power": "electric"}),
    ("lawn_mower", {"drive": "push"}, {"drive": "self"}),
    ("robot_mower", {"boundary": "wire"}, {"boundary": "gps"}),
    ("grass_trimmer", {"head": "line"}, {"head": "blade"}),
    ("grass_trimmer", {"power": "cordless"}, {"power": "petrol"}),
    ("bbq", {"kind": "kettle"}, {"kind": "barrel"}),
    ("bbq", {"kind": "kettle"}, {"kind": "kamado"}),
    ("bbq", {"kind": "kettle"}, {"kind": "portable"}),
    ("bbq", {"kind": "kettle"}, {"kind": "gas"}),
]


@pytest.mark.parametrize(("shape", "one", "other"), VARIANTS, ids=lambda v: str(v))
def test_a_param_changes_the_drawing(shape: str, one: dict, other: dict) -> None:
    assert shape in kit_garden.SHAPES
    assert _svg(shape=shape, **one) != _svg(shape=shape, **other)
    assert _svg(shape=shape) == _svg(shape=shape, **one), "the default is the first reading"


@pytest.mark.parametrize("row", ALL, ids=lambda r: r.code)
def test_every_style_draws_well_formed_svg(row) -> None:
    xml.dom.minidom.parseString(_svg(row))


def test_a_mower_draws_the_power_source_its_record_states() -> None:
    marks = {
        "cordless": kit_garden.BATTERY_CLASS,
        "petrol": kit_garden.FUEL_CLASS,
        "electric": kit_garden.CABLE_CLASS,
    }
    for row in (r for r in ALL if r.shape in ("lawn_mower", "grass_trimmer")):
        power = dict(row.params)["power"]
        svg = _svg(row)
        for name, cls in marks.items():
            assert (f'class="{cls}"' in svg) == (name == power), (row.code, name)


def test_a_gas_barbecue_draws_one_knob_per_burner_and_the_others_none() -> None:
    for row in (r for r in ALL if r.shape == "bbq"):
        params = dict(row.params)
        want = int(params["burners"]) if params["kind"] == "gas" else 0
        assert len(re.findall(r'<g class="knob"', _svg(row))) == want, row.code
    assert len(re.findall(r'<g class="knob"', _svg(shape="bbq", kind="gas", burners="5"))) == 5


def test_no_garden_drawing_prints_a_size() -> None:
    """A style's sizes share one image, so a printed width or area is wrong for all but one."""
    printed = {}
    for row in ALL:
        words = re.findall(r"<text[^>]*>([^<]*)</text>", _svg(row))
        sized = [w for w in words if re.search(r"\d", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


# --------------------------------------------------------------------------
# Colors, tree and build.
# --------------------------------------------------------------------------


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_type_offers_the_six_main_colors_with_no_exception(ptype: str) -> None:
    assert ptype not in main_colors.EXCEPTIONS
    offered = {c[0] for r in ROWS if r.product_type == ptype for c in r.colors}
    assert set(main_colors.MAIN_COLORS) <= offered


def test_the_tree_nests_the_types_under_lawn_care_and_barbecues_and_grills() -> None:
    paths = [tuple(r.path) for r in ROWS]
    assert {p[:2] for p in paths} == {("Garden", "Lawn Care"), ("Garden", "Barbecues & Grills")}
    assert {p[-1] for p in paths} >= {
        "Cordless Lawn Mowers",
        "Petrol Lawn Mowers",
        "Robot Mowers",
        "Gas Barbecues",
    }
    rows = [(f"BRD-{r.code}", r.title, r.path) for r in ALL]
    all_paths = [tuple(r.path) for r in ALL]
    assert tree_guard.sibling_head_noun_findings(all_paths) == []
    assert tree_guard.headless_group_findings(all_paths) == []
    assert tree_guard.misplaced_title_findings(rows) == []


# --------------------------------------------------------------------------
# Text-match decoys (gen#294): at least three of each class per type, every field true.
# --------------------------------------------------------------------------

TARGETS = {
    "Lawn Mower": "lawn mower",
    "Robot Mower": "robot mower",
    "Grass Trimmer": "grass trimmer",
    "BBQ": "bbq",
}


def _decoys(ptype: str) -> dict[str, list]:
    out: dict[str, list] = collections.defaultdict(list)
    for r in ALL:
        if r.code in DECOY_CODES and garden_rows.DECOY_TABLE[r.code][2] == ptype:
            out[garden_rows.DECOY_TABLE[r.code][0]].append(r)
    return out


CLASSES = ("type", "absent", "incidental", "secondary", "shade")
MAIN = ("red", "blue", "green", "yellow", "black", "white")


def _color_words(text: str) -> set[str]:
    return {w for w in MAIN if re.search(rf"\b{w}\b", text.lower())}


def _own(row) -> set[str]:
    return {c[0].lower() for c in row.colors}


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_each_type_carries_at_least_three_decoys_of_each_class(ptype: str) -> None:
    got = _decoys(ptype)
    assert set(got) <= set(CLASSES)
    assert {k: len(got[k]) for k in CLASSES if len(got[k]) < 3} == {}


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_a_sibling_or_incidental_decoy_is_not_the_type_and_its_title_holds_the_words(
    ptype: str,
) -> None:
    got = _decoys(ptype)
    for sibling in got["type"]:
        assert sibling.product_type != ptype and TARGETS[ptype] in sibling.title.lower()
    first = TARGETS[ptype].split()[0] if ptype != "BBQ" else "bbq"
    for incidental in got["incidental"]:
        assert len(incidental.title.split()) <= 5, "a short title: the word weighs most"
        assert first in incidental.title.lower() or first in incidental.description.lower()
    real = [r for r in got["incidental"] if r.product_type == ptype]
    assert len(real) >= 2, "a short title on a real product is the stronger lure"
    for r in real:
        assert _color_words(r.title) and not _color_words(r.title) & _own(r)
    assert any(r.product_type != ptype for r in got["incidental"])


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_an_absent_decoy_names_a_power_source_it_lacks_and_is_the_type(ptype: str) -> None:
    word = {
        "Lawn Mower": "petrol",
        "Robot Mower": "gps",
        "Grass Trimmer": "cordless",
        "BBQ": "gas",
    }[ptype]
    for row in _decoys(ptype)["absent"]:
        assert row.product_type == ptype
        assert word in row.title.lower()
        stated = (
            " ".join(a[2].lower() for a in row.attrs) + " " + " ".join(v for _, v in row.params)
        )
        assert word not in stated


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_a_secondary_color_decoy_names_a_part_color_and_keeps_its_own_main_color(
    ptype: str,
) -> None:
    for row in _decoys(ptype)["secondary"]:
        assert row.product_type == ptype and len(row.colors) == 1
        words = _color_words(row.title)
        assert _own(row) <= words and words - _own(row), row.code
        assert " with " in row.title.lower(), "the other color names a part"


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_a_shade_decoy_names_a_color_only_in_its_description(ptype: str) -> None:
    for row in _decoys(ptype)["shade"]:
        assert row.product_type == ptype and len(row.colors) == 1
        assert _color_words(row.title) == set(), row.code
        assert _color_words(row.description) - _own(row), row.code


def test_the_decoys_are_exempt_from_the_text_check_and_left_out_of_the_derivation() -> None:
    assert garden_rows.decoy_ids() <= scale.DECOY_IDS
    assert len(garden_rows.decoy_ids()) == len(DECOY_CODES) >= 3 * len(CLASSES) * len(KEYS)
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert {f"BRD-{r.code}" for r in ALL} == scale.GARDEN_IDS and not (scale.GARDEN_IDS & kept)


def test_a_decoy_keeps_the_one_color_it_was_authored_with() -> None:
    tpls = {d["product_id"]: d for d in scale.templates()}
    for row in ALL:
        if row.code in DECOY_CODES:
            assert [c["color"] for c in tpls[f"BRD-{row.code}"]["color_options"]] == [
                c[0] for c in row.colors
            ], row.code


@pytest.mark.timeout(300)
def test_every_garden_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ALL if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.GARDEN_IDS]
    assert len(mine) == len(ALL)
    assert check_catalog(mine, one_class_per_key=True, text_exempt=scale.DECOY_IDS) == []


# --------------------------------------------------------------------------
# What the record states is what is drawn: shelves, the side burner, the drive lever.
# --------------------------------------------------------------------------


def _attr(row, key: str) -> str | None:
    return next((a[2] for a in row.attrs if a[0] == key), None)


def test_a_barbecue_draws_a_shelf_per_side_exactly_when_its_record_says_yes() -> None:
    rows = [r for r in ALL if r.shape == "bbq"]
    assert {_attr(r, "side_shelves") for r in rows} == {"Yes", "No"}
    for row in rows:
        want = 2 if _attr(row, "side_shelves") == "Yes" else 0
        assert len(re.findall(r'<g class="shelf"', _svg(row))) == want, row.code


def test_a_barbecue_draws_a_side_burner_exactly_when_its_record_says_yes() -> None:
    rows = [r for r in ALL if r.shape == "bbq"]
    assert "Yes" in {_attr(r, "side_burner") for r in rows}
    for row in rows:
        want = 1 if _attr(row, "side_burner") == "Yes" else 0
        assert len(re.findall(r'<g class="side-burner"', _svg(row))) == want, row.code


def test_a_self_drive_mower_draws_its_lever_and_arrow_and_a_push_mower_neither() -> None:
    rows = [r for r in ALL if r.shape == "lawn_mower"]
    assert {dict(r.params)["drive"] for r in rows} == {"push", "self"}
    for row in rows:
        want = 1 if dict(row.params)["drive"] == "self" else 0
        svg = _svg(row)
        assert len(re.findall(r'<g class="drive-lever"', svg)) == want, row.code
        assert len(re.findall(r'<g class="drive-arrow"', svg)) == want, row.code
