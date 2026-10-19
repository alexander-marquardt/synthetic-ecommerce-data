"""The DIY drill family (gen#191): power drills that name their kind, and the comment's five types.

The Retail catalog held four power drills, all one brand and all typed "Cordless Drill". Nine
type specs (Drill Driver, Combi Drill, Hammer Drill, Corded Drill, Impact Driver, SDS Hammer
Drill, Drill Bit Set, Tool Kit, Step Ladder) now hold the range, each drawn as a shape of its own
(:mod:`kit_drills`). These checks hold what the issue and its comment asked for: a product type
that names the tool and is never a plain "Drill", at least three invented brands and three styles
a type, a drawing of its own that a style's parameter changes, each key attribute as a structured
entry in the export, the six main colors, three text-match decoys a type, and an image that
resolves for every SKU.
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

import diy_decoy_rows  # noqa: E402
import export  # noqa: E402
import image_release  # noqa: E402
import kit  # noqa: E402
import main_colors  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402

#: key -> (product type, the shape it draws, a param and two values that change the drawing,
#: the attribute keys it states).
TYPES = {
    "drill_driver": (
        "Drill Driver",
        "drill_driver",
        ("pack", "compact", "large"),
        {"power_source", "voltage_v", "battery_type"},
    ),
    "combi_drill": (
        "Combi Drill",
        "combi_drill",
        ("pack", "compact", "large"),
        {"power_source", "voltage_v", "modes"},
    ),
    "hammer_drill": (
        "Hammer Drill",
        "hammer_drill",
        ("power", "cordless", "corded"),
        {"power_source", "motor_type"},
    ),
    "corded_drill": (
        "Corded Drill",
        "corded_drill",
        ("handle", "pistol", "side"),
        {"power_source", "wattage", "chuck_type"},
    ),
    "impact_driver": (
        "Impact Driver",
        "impact_driver",
        ("batteries", "0", "2"),
        {"power_source", "voltage_v", "torque_nm", "bit_holder", "battery_kit"},
    ),
    "sds_hammer_drill": (
        "SDS Hammer Drill",
        "sds_drill",
        ("power", "corded", "cordless"),
        {"power_source", "impact_energy_j", "modes"},
    ),
    "drill_bit_set": (
        "Drill Bit Set",
        "drill_bit_set",
        ("shank", "round", "hex"),
        {"drills_into", "piece_count", "shank", "case"},
    ),
    "tool_kit": (
        "Tool Kit",
        "tool_kit",
        ("case", "bag", "case"),
        {"piece_count", "kit_contents", "case"},
    ),
    "step_ladder": (
        "Step Ladder",
        "step_ladder",
        ("steps", "2", "5"),
        {"steps", "material", "max_load_kg", "platform_height_m", "ladder_kind"},
    ),
}
KEYS = sorted(TYPES)


def _spec(key: str) -> type_registry.TypeSpec:
    specs = type_registry.specs()
    assert key in specs, f"no type spec {key!r}"
    return specs[key]


def _svg(shape: str, **params: str) -> str:
    return kit.render(shape, kit.Fill("solid", "#123456", "#654321"), params=params)


def _doc_attr_keys(doc: dict) -> set[str]:
    keys = {e["key"] for e in doc["attributes"]}
    return keys | {e["key"] for v in doc["variants"] for e in v["attributes"]}


@pytest.mark.parametrize("key", KEYS)
def test_the_product_type_names_the_tool_and_is_never_a_plain_drill(key: str) -> None:
    ptype = TYPES[key][0]
    spec = _spec(key)
    assert spec.product_type == ptype and ptype != "Drill"
    assert {r.product_type for r in spec.rows} == {ptype}
    assert ptype.split()[-1] != "Drill" or len(ptype.split()) > 1


def test_no_row_of_the_catalog_is_typed_with_the_old_cordless_drill() -> None:
    types = {d["product_type"] for d in scale.templates()}
    assert "Cordless Drill" not in types
    assert "Drill" not in types


@pytest.mark.parametrize("key", KEYS)
def test_a_type_has_three_invented_brands_and_three_styles(key: str) -> None:
    rows = _spec(key).rows
    assert len(rows) >= 3
    assert len({r.brand for r in rows}) >= 3
    real = {"Apple", "iPhone", "iPad"}
    assert not real & {r.brand for r in rows}


@pytest.mark.parametrize("key", KEYS)
def test_a_type_draws_a_shape_of_its_own_and_a_param_changes_it(key: str) -> None:
    _, shape, (param, one, two), _ = TYPES[key]
    rows = _spec(key).rows
    assert {r.shape for r in rows} == {shape}
    assert shape not in {"box", "box_wide", "drill"}
    assert _svg(shape, **{param: one}) != _svg(shape, **{param: two})


def test_the_nine_types_draw_nine_different_shapes() -> None:
    assert len({v[1] for v in TYPES.values()}) == len(TYPES)
    drawn = {_svg(v[1]) for v in TYPES.values()}
    assert len(drawn) == len(TYPES)


@pytest.mark.parametrize("key", KEYS)
def test_every_style_draws_well_formed_svg(key: str) -> None:
    for row in _spec(key).rows:
        xml.dom.minidom.parseString(_svg(row.shape, **dict(row.params)))


@pytest.mark.parametrize("key", KEYS)
def test_each_key_attribute_is_a_structured_entry_in_the_export(key: str) -> None:
    wanted = TYPES[key][3]
    docs = _spec(key).docs()
    own = [d for d in docs if d["product_id"] in {f"BRD-{r.code}" for r in _spec(key).rows}]
    assert own
    seen = set()
    for doc in own:
        seen |= _doc_attr_keys(export.standard_document(doc))
    assert sorted(wanted - seen) == []


@pytest.mark.parametrize("key", KEYS)
def test_a_type_offers_the_six_main_colors_with_no_exception(key: str) -> None:
    ptype = TYPES[key][0]
    assert ptype not in main_colors.EXCEPTIONS
    offered = {c[0] for r in _spec(key).rows for c in r.colors}
    assert set(main_colors.MAIN_COLORS) <= offered


def test_a_cordless_type_states_its_voltage_and_a_corded_one_its_wattage() -> None:
    def values(key: str, attr: str) -> set[float]:
        return {
            float(a[2]) for r in _spec(key).rows for a in r.attrs if a[0] == attr and len(a) >= 3
        }

    assert {12, 18, 20} <= values("drill_driver", "voltage_v")
    assert {18, 40} <= values("hammer_drill", "voltage_v")
    assert values("hammer_drill", "wattage") and min(values("hammer_drill", "wattage")) >= 550
    assert max(values("hammer_drill", "wattage")) <= 1100
    assert 450 <= min(values("corded_drill", "wattage"))
    assert max(values("corded_drill", "wattage")) <= 710
    assert {12, 18, 20} <= values("impact_driver", "voltage_v")


def test_a_corded_and_a_cordless_hammer_drill_state_their_power_source() -> None:
    sources = {
        a[2] for r in _spec("hammer_drill").rows for a in r.attrs if a[0] == "power_source"
    }
    assert sources == {"Cordless", "Corded"}


QUERIES = (
    ("drill_driver", r"\b18 V\b.*drill driver"),
    ("impact_driver", r"\b20 V\b.*impact driver"),
    ("sds_hammer_drill", r"\b1100 W\b.*sds hammer drill"),
    ("corded_drill", r"\b710 W\b.*corded drill"),
    ("drill_bit_set", r"masonry drill bit set, \d+ piece"),
    ("tool_kit", r"tool kit, 61 piece"),
    ("step_ladder", r"\b4 step\b.*step ladder"),
    ("step_ladder", r"step stool"),
)


@pytest.mark.parametrize(("key", "pattern"), QUERIES)
def test_the_commented_query_shapes_find_a_title(key: str, pattern: str) -> None:
    assert any(re.search(pattern, r.title, re.IGNORECASE) for r in _spec(key).rows)


@pytest.mark.parametrize("key", KEYS)
def test_a_type_carries_three_text_match_decoys_that_tell_the_truth(key: str) -> None:
    ptype, phrase = TYPES[key][0], TYPES[key][0].lower()
    spec = _spec(key)
    assert [d.cls for d in spec.decoys] == [4]
    crossing = [r for r in diy_decoy_rows.ROWS if phrase in r.title.lower() + r.description.lower()]
    assert len(crossing) >= 1
    # the cross-department pair: a category-word one (class 2) and an incidental-word one (class 6)
    words = set(phrase.split())
    incidental = [
        r
        for r in diy_decoy_rows.ROWS
        if r.product_type == "Scented Candle"
        and words & set(re.findall(r"[a-z]+", r.title.lower()))
        and words & set(re.findall(r"[a-z]+", r.description.lower()))
    ]
    category = [
        r
        for r in diy_decoy_rows.ROWS
        if r.product_type in {"Cushion", "Apron"} and phrase in r.title.lower()
    ]
    assert category and incidental
    for row in [*category, *incidental, *(d.row for d in spec.decoys)]:
        assert row.product_type != "Drill" and row.code
    assert {r.product_type for r in [*category, *incidental]}.isdisjoint({ptype})


def test_every_decoy_is_a_template_the_build_leaves_as_authored() -> None:
    ids = diy_decoy_rows.product_ids()
    assert len(ids) == 2 * len(TYPES)
    kept = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not ids & kept


@pytest.mark.parametrize("key", KEYS)
def test_every_image_id_of_a_type_resolves_to_a_drawing(key: str) -> None:
    docs = _spec(key).docs()
    wanted = {export.image_id(d, s) for d in docs for s in d["skus"]}
    files = dict(image_release.image_files(docs))
    paths = {image_release.member_path(i) for i in wanted}
    assert paths and paths <= set(files)
    assert all(b.startswith(b"<svg") or b"<svg" in b[:200] for b in files.values())


@pytest.mark.parametrize("key", KEYS)
def test_a_type_sits_under_diy_and_tools_with_a_leaf_of_its_own(key: str) -> None:
    paths = {tuple(r.path) for r in _spec(key).rows}
    assert len(paths) == 1
    (path,) = paths
    assert path[:2] == ("Home", "DIY & Tools") and len(path) == 4
