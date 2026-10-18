"""Retail lighting (gen#197): floor, table, desk, ceiling and wall lights, and lampshades.

Each type is a leaf of its own under ``Home/Lighting`` with at least three styles from at
least three brands; its key attributes are structured entries in the exported document; a
SKU's second axis (a finish, a shade color, a diameter) is drawn in that SKU's own image;
and a derived style that changes a drawn attribute redraws it.
"""

from __future__ import annotations

import collections
import hashlib
import json
import random
import re
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
                   {"style", "item_height", "shade_material", "switch", "bulb_fitting"}, "finish"),
    "Table Lamp": ("Table Lamps", "table_lamp",
                   {"style", "item_height", "base_material", "power"}, "shade_color"),
    "Desk Lamp": ("Desk Lamps", "desk_lamp", {"arm"}, None),
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
        generic = {"Lamps": "Lamps", "Lights": "Lights"}.get(leaf.split()[-1])  # gen#283
        want = ("Home", "Lighting", *([generic] if generic else []), leaf)
        assert {tuple(r["category_path"]) for r in recs} == {want}, ptype
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


def _legacy_image_id(rec: dict, sku: dict) -> str:
    """The image id before SKU params existed: the digest of the drawing and swatch alone."""
    swatch = next((c for c in rec.get("color_options", ()) if c["color"] == sku.get("color")), None)
    blob = json.dumps(
        {"drawing": rec["drawing"], "swatch": swatch}, sort_keys=True, ensure_ascii=False
    )
    digest = hashlib.sha256(blob.encode()).hexdigest()[:12]
    return f"{export._slug(rec['product_type'])}/{rec['product_id']}/{digest}"


def test_a_sku_that_carries_no_drawing_param_keeps_its_image_id() -> None:
    """The rule: a SKU whose product's drawing params it carries none of, in any template
    (whether or not that template's drawing declares params), has a spec with no ``params``
    and the image id it had before SKU params existed. A template that declares params
    (a heater's ``fin_count``) is held to it on its param-less SKUs."""
    checked = 0
    for t in scale.templates():
        declared = t["drawing"].get("params") or {}
        for s in t["skus"]:
            if any(k in s for k in declared):
                continue
            checked += 1
            assert "params" not in export.drawing_spec(t, s), s["sku"]
            assert export.image_id(t, s) == _legacy_image_id(t, s), s["sku"]
    assert checked


def test_a_lighting_sku_stripped_of_its_param_values_keeps_the_legacy_image_id() -> None:
    for rec in (d for d in DOCS if d["product_id"] in IDS):
        declared = rec["drawing"].get("params") or {}
        for s in rec["skus"]:
            bare = {k: v for k, v in s.items() if k not in declared}
            assert export.image_id(rec, bare) == _legacy_image_id(rec, bare), s["sku"]


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

#: A phrase a lighting description may carry only while its style holds the attribute value
#: it implies: phrase -> the ``(key, value)`` pairs that make it true (one of them must
#: hold). ``scale.derive`` rewrites the attribute word itself ("tripod" -> "arc"), but not
#: the phrases that only that value explains, so a derived style must not keep one.
FORM_BOUND_PHRASES = {
    r"\bsplayed legs?\b|\blegs\b": (("style", "Tripod"),),
    r"\bcurved arms?\b|\bcandle bulb\b|\bhang it at the height\b": (
        ("fixture_type", "Chandelier"),),
    r"\bwashes the ceiling\b|\blights the ceiling\b": (("style", "Uplighter"),),
    r"\btilting\b|\bonto a book\b": (("style", "Task"),),
    r"\breading light on its own arm\b|\beach with its own switch\b": (
        ("style", "Mother-and-Child"),),
    r"\btap the base\b|\bbrightness levels\b": (("style", "Touch"),),
    r"\bsits tight to the ceiling\b|\blow ceiling\b": (("fixture_type", "Flush"),),
    r"\bshort rods\b|\bclose to the ceiling\b": (("fixture_type", "Semi-Flush"),),
    r"\bsprung\b|\bjointed arm\b": (("arm", "Adjustable"),),
    r"\bbends\b": (("arm", "Gooseneck"),),
    r"\bgrips\b|\bshelf edge\b": (("arm", "Clamp-On"),),
    r"\bheads that each tilt\b|\bworktop\b": (("fixture_type", "Spotlight Bar"),),
    r"\bcharged? by usb\b|\bno socket\b|\bruns on a battery\b|\bno wiring\b|\bbetween charges\b": (
        ("power", "Rechargeable"),),
    r"\bplugs into\b|\bno electrician\b": (("power", "Plug-In"),),
    r"\b(?:two|three|four|five)\b": tuple(
        ("light_count", str(n)) for n in (2, 3, 4, 5)
    ),
}  # fmt: skip

#: A switch word that opens a sentence ("Inline the shade to dim it", from "Touch the shade
#: to dim it" after the switch value changed) has lost its grammar.
SWITCH_WORD_OPENING = (
    r"(?:^|[.;:] )(?:Inline|Foot|Dimmer|Touch|Wall Switch) (?:the|to|a|an) "
)


def _contradictions(rec: dict) -> list[str]:
    """The form-bound phrases (and broken sentences) of a lighting style's description that
    its own attributes do not support."""
    held = {(a["key"], str(a["value"])) for a in rec["attributes"]}
    text = rec["description"]
    bad = [
        m.group(0)
        for pattern, supports in FORM_BOUND_PHRASES.items()
        for m in re.finditer(pattern, text, flags=re.IGNORECASE)
        if not held & set(supports)
    ]
    bad += [m.group(0) for m in re.finditer(SWITCH_WORD_OPENING, text)]
    return bad


@pytest.fixture(scope="module")
def derived_lighting() -> list[dict]:
    built = scale.build(10**6)
    ids = {d["product_id"] for d in DOCS}
    return [
        r for r in built.records
        if built.template_of.get(r["product_id"]) in ids and r["product_type"] != "Lampshade"
    ]  # fmt: skip


def test_the_ceiling_derives_lighting_styles_to_check(derived_lighting: list[dict]) -> None:
    assert len(derived_lighting) > 300


def test_no_derived_lighting_description_says_what_its_attributes_contradict(
    derived_lighting: list[dict],
) -> None:
    """Guard: a form-bound phrase in a lighting row that ``scale.derive`` cannot rewrite
    fails here. Metric: how many of the derived styles carry one, in the message."""
    wrong = {r["product_id"]: _contradictions(r) for r in derived_lighting}
    wrong = {k: v for k, v in wrong.items() if v}
    assert not wrong, f"{len(wrong)} of {len(derived_lighting)}: {list(wrong.items())[:5]}"


@pytest.mark.parametrize(
    ("description", "attributes"),
    [
        ("A task floor lamp on three splayed legs.", [("style", "Task")]),
        ("A pendant with five curved arms.", [("fixture_type", "Pendant"), ("light_count", "1")]),
        ("It charges by USB, so it has no socket near it.", [("power", "Plug-In")]),
        ("A pendant that sits tight to the ceiling.", [("fixture_type", "Pendant")]),
        ("A swing arm that runs on a battery, with no wiring. Inline the shade to dim it.",
         [("power", "Hardwired")]),
    ],
)  # fmt: skip
def test_the_phrase_table_catches_the_reviewed_contradictions(
    description: str, attributes: list[tuple[str, str]]
) -> None:
    rec = {
        "description": description,
        "attributes": [{"key": k, "value": v} for k, v in attributes],
    }
    assert _contradictions(rec)


def test_a_description_its_attributes_support_passes() -> None:
    rec = {
        "description": "A tripod floor lamp on splayed legs.",
        "attributes": [{"key": "style", "value": "Tripod"}],
    }
    assert _contradictions(rec) == []


def _task_lamp_svg(style: str) -> str:
    import kit_lighting

    return "".join(kit_lighting.floor_lamp("#2f2f33", None, None, style=style))


def _highest_joint(style: str) -> float:
    """The smallest ``cy`` of the joints a floor lamp of ``style`` draws: its head's height."""
    svg = _task_lamp_svg(style)
    return min(float(y) for y in re.findall(r'<circle cx="[\d.]+" cy="([\d.]+)"', svg))


def _highest_pole_point(style: str) -> float:
    """The smallest y any pole, arm or cord path (an unfilled ``<path>``) of ``style`` reaches."""
    svg = _task_lamp_svg(style)
    ds = re.findall(r'<path d="([^"]+)" fill="none"', svg)
    return min(float(y) for d in ds for y in re.findall(r"[\d.]+,([\d.]+)", d))


def test_a_task_floor_lamp_reaches_as_high_as_an_arc_one_not_a_desk_lamp() -> None:
    """The task lamp's head sat at y 118, a desk lamp's height, so its thumbnail read as one
    in a floor-lamp grid. Guard: its head must sit above y 100 of the 400 px sheet (a desk
    lamp's sits near 150), and so must the top of its pole (gen#238): a change that moved
    only the pole path left the joints at the new height and passed a joints-only check."""
    assert _highest_joint("task") < 100
    assert _highest_pole_point("task") < 100


def test_a_task_floor_lamp_pole_ends_at_its_head_joint() -> None:
    """The pole's top and the head joint are one point: a pole that stops short, or runs past
    the joint, leaves a gap or a stub in the thumbnail (gen#238)."""
    assert _highest_pole_point("task") == _highest_joint("task")


def test_a_picture_light_offers_only_the_finishes_its_brass_hood_can_show() -> None:
    """The hood is drawn in the record fill (Brass), so a Chrome SKU would show a brass hood
    under a chrome label. Guard: the picture light lists no Chrome finish."""
    pic = next(d for d in DOCS if d["product_id"] == "BRD-LTWPIC")
    finishes = {s["finish"] for s in pic["skus"]}
    assert finishes == {"Antique Brass", "Brass"}


# --- gen#232: a color temperature is a Kelvin count, never "3000K" in the value ---------------

_UNIT_IN_VALUE = re.compile(r"^[0-9][0-9.,/-]*\s*[A-Za-z%\u00b0]+$")


def _temperature_entries(doc: dict) -> dict[str, dict]:
    return {e["key"]: e for e in doc["attributes"] if e["key"].startswith("color_temperature")}


def test_every_lighting_color_temperature_entry_is_kelvin_and_none_holds_a_unit_in_its_value():
    from synthetic_ecommerce_data.core.entry import CANONICAL_PER_UNIT

    assert "KEL" in CANONICAL_PER_UNIT
    seen = 0
    standard = [export.standard_document(d) for d in DOCS]
    assert check_catalog(standard) == []
    for doc in standard:
        for entry in _temperature_entries(doc).values():
            seen += 1
            assert entry["unit_code"] == "KEL", (doc["product_id"], entry)
            assert entry["value"].isdigit(), (doc["product_id"], entry)
            assert entry["value_canonical"] == float(entry["value"]), (doc["product_id"], entry)
        for entry in doc["attributes"] + [e for v in doc["variants"] for e in v["attributes"]]:
            if "unit_code" not in entry:
                assert not _UNIT_IN_VALUE.match(entry["value"]), (doc["product_id"], entry)
    assert seen


def test_a_desk_lamp_has_one_temperature_or_a_two_ended_range_under_the_one_key():
    """gen#498: one fact has one key, so a tunable lamp holds both ends under color_temperature."""
    shapes = {}
    for doc in (export.standard_document(d) for d in DOCS if d["product_type"] == "Desk Lamp"):
        entries = [e for e in doc["attributes"] if e["key"].startswith("color_temperature")]
        assert {e["key"] for e in entries} == {"color_temperature"}, doc["product_id"]
        shapes[doc["product_id"]] = sorted(int(e["value"]) for e in entries)
    assert len({len(v) for v in shapes.values()}) == 2
    assert {k: shapes[k] for k in ("BRD-LTDGNK", "BRD-LTDCLP")} == {
        "BRD-LTDGNK": [3000],
        "BRD-LTDCLP": [5000],
    }
    assert shapes["BRD-LTDADJ"] == shapes["BRD-LTDWCP"] == [2700, 6500]


def test_the_preview_shows_a_kelvin_entry_with_its_unit() -> None:
    """The unit is not in the stored value, so the page that shows the attribute adds it."""
    import build_preview

    desk = [d for d in DOCS if d["product_type"] == "Desk Lamp"]
    shown = {d["product_id"]: build_preview._attr_rows(d) for d in desk}
    assert "<td>3000 K</td>" in shown["BRD-LTDGNK"]
    assert "<th>Color temperature</th><td>2700 K, 6500 K</td>" in shown["BRD-LTDADJ"]
