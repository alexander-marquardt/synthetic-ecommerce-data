"""Appliance types (gen#202): fans, heaters, kettles and toasters.

:mod:`appliance_rows` holds the styles and :mod:`kit_appliances` draws them. These checks
hold what the issue asked for: every type has its range (three styles, three brands), each
style draws as its own appliance shape, each key attribute the issue lists is a structured
entry in the export, a count the record states is the count the drawing shows (per SKU where
the SKU carries it), and the styles reach the scaled build.
"""

from __future__ import annotations

import collections
import re
import sys
from pathlib import Path

import pytest

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import appliance_rows  # noqa: E402
import export  # noqa: E402
import image_release  # noqa: E402
import kit_appliances  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

ROWS = appliance_rows.ROWS

#: Each type and the key attributes the issue's table lists for it (product or SKU entries).
KEYS = {
    "Desk Fan": {"blade_size", "power", "speed_settings", "oscillating", "noise_level", "color",
                 "blade_count", "wattage"},
    "Pedestal Fan": {"blade_size", "min_height", "max_height", "remote_control", "timer",
                     "speed_settings", "wattage", "color"},
    "Tower Fan": {"item_height", "oscillating", "remote_control", "timer", "mode", "bladeless",
                  "color"},
    "Ceiling Fan": {"blade_span", "blade_count", "light_kit", "reversible", "remote_control",
                    "pull_cord", "finish"},
    "Handheld Fan": {"power", "foldable", "neck_fan", "color"},
    "Heater": {"heater_type", "wattage", "thermostat", "timer"},
    "Kettle": {"capacity", "kettle_type", "material", "finish", "color"},
    "Toaster": {"slots", "long_slot", "finish", "browning_settings", "defrost", "reheat",
                "color"},
}  # fmt: skip

#: The marked group each counted drawing repeats, in the order the checks run.
MARKS = ("blade", "fin", "tube", "slot")


def _attr(row: appliance_rows.Row, key: str) -> list[str]:
    return [a[2] for a in row.attrs if a[0] == key]


def _drawn(row: appliance_rows.Row, sku: dict) -> dict[str, int]:
    """How many of each counted mark the SKU's own image draws."""
    svg = image_release.render(row.doc(), sku).decode()
    return {m: len(re.findall(rf'class="{m}"', svg)) for m in MARKS}


def _stated(row: appliance_rows.Row, sku: dict) -> dict[str, int]:
    """The counts the record states for this SKU: blades, fins, tubes and slots."""
    blades = _attr(row, "blade_count")
    kind = dict(row.params).get("kind", "")
    return {
        "blade": int(blades[0]) if blades else 0,
        "fin": int(sku["fin_count"]) if "fin_count" in sku else 0,
        "tube": int(_attr(row, "heat_settings")[0]) if kind == "halogen" else 0,
        "slot": int(sku["slots"]) if "slots" in sku else 0,
    }


def _sku_cases() -> list:
    return [pytest.param(r, s, id=f"{r.code}-{i}") for r in ROWS for i, s in enumerate(r.skus())]


def test_every_type_has_three_styles_from_three_brands() -> None:
    styles: dict[str, list[appliance_rows.Row]] = collections.defaultdict(list)
    for row in ROWS:
        styles[row.product_type].append(row)
    assert set(styles) == set(KEYS)
    thin = {t: (len(rs), len({r.brand for r in rs})) for t, rs in styles.items()}
    assert {t: n for t, n in thin.items() if min(n) < 3} == {}


def test_every_style_draws_as_its_own_appliance_shape() -> None:
    assert {r.code: r.shape for r in ROWS if r.shape not in kit_appliances.SHAPES} == {}


@pytest.mark.parametrize("ptype", sorted(KEYS))
def test_every_key_attribute_is_a_structured_entry_in_the_export(ptype: str) -> None:
    missing = {}
    for row in (r for r in ROWS if r.product_type == ptype):
        doc = export.standard_document(row.doc())
        keys = {e["key"] for e in doc["attributes"]}
        keys |= {e["key"] for v in doc["variants"] for e in v["attributes"]}
        if KEYS[ptype] - keys:
            missing[row.code] = sorted(KEYS[ptype] - keys)
    assert missing == {}


def test_each_size_axis_the_issue_names_is_carried_by_every_sku() -> None:
    """Every SKU states its blade size, blade span, capacity, slots or wattage, and each type
    has a style whose SKUs differ on it (a single-size style, such as a travel kettle, is
    allowed, but the axis is a real choice somewhere in the type)."""
    axes = {"Desk Fan": "blade_size_in", "Ceiling Fan": "blade_span_cm", "Kettle": "capacity_l",
            "Toaster": "slots", "Heater": "wattage"}  # fmt: skip
    absent = {r.code for r in ROWS if r.product_type in axes
              and any(axes[r.product_type] not in s for s in r.skus())}  # fmt: skip
    assert absent == set()
    varied = {r.product_type for r in ROWS if r.product_type in axes
              and len({s[axes[r.product_type]] for s in r.skus()}) > 1}  # fmt: skip
    assert varied == set(axes)


@pytest.mark.parametrize(("row", "sku"), _sku_cases())
def test_the_drawing_shows_the_count_its_record_states(row: appliance_rows.Row, sku: dict) -> None:
    """Fan blades, radiator fins, halogen tubes and toaster slots: the SKU's own image draws
    as many of each mark as the record states, and none of a mark it does not count."""
    assert _drawn(row, sku) == _stated(row, sku)


def test_the_counted_marks_cover_a_count_above_one_for_every_mark() -> None:
    """The drawn-count test reads a real count for each mark, not only zeros and ones."""
    big = {m for r in ROWS for s in r.skus() for m, n in _stated(r, s).items() if n > 1}
    assert big == set(MARKS)


def test_a_toasters_slots_and_a_radiators_fins_differ_between_its_skus() -> None:
    """Those counts are per SKU, so the SKUs' images are different images."""
    toast = next(r for r in ROWS if r.shape == "toaster")
    fins = next(r for r in ROWS if r.shape == "heater" and any("fin_count" in s for s in r.skus()))
    for row in (toast, fins):
        first = row.skus()[0].get("color")
        ids = {export.image_id(row.doc(), s) for s in row.skus() if s.get("color") == first}
        assert len(ids) > 1


def test_no_appliance_drawing_prints_a_size() -> None:
    """A style's sizes share one drawing, so a printed size would be wrong for most."""
    printed = {}
    for row in ROWS:
        svg = image_release.render(row.doc(), row.skus()[0]).decode()
        words = re.findall(r"<text[^>]*>([^<]*)</text>", svg)
        sized = [w for w in words if re.search(r"\d\s*(cm|mm|in|l|L|W|dB|ltr|litre)\b", w)]
        if sized:
            printed[row.code] = sized
    assert printed == {}


@pytest.mark.timeout(300)
def test_every_appliance_style_reaches_the_100k_build_and_meets_the_standard() -> None:
    docs = scale.documents(scale.build(100_000))
    got = {d["product_id"] for d in docs}
    assert sorted(f"BRD-{r.code}" for r in ROWS if f"BRD-{r.code}" not in got) == []
    mine = [d for d in docs if d["product_id"] in scale.APPLIANCE_IDS]
    assert len(mine) == len(ROWS)
    assert check_catalog(mine, one_class_per_key=True) == []
