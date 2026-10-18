"""One concept, one attribute: the retail document's attribute clean-up (gen#497).

The authored rows keep the keys they were written with: the drawing params, the scaler's value
pools and ``FROZEN_KEYS`` read them. What a shopper and a downstream catalogue see is the
published document, so :func:`clean` (called by ``export._product_attributes`` and
``export._variant``) rewrites each entry list once:

- **removed**: :data:`REMOVED` repeats another field (``storage_type`` "Storage Box" on a Storage
  Box) or is back-office (``brand_owner`` stays a document field for ranking, ``pack_size`` is
  restated by ``units_per_pack`` and the net content);
- **merged**: :data:`RENAMES` and :data:`STYLE_KEYS` (one key, one display name), the leg and
  garment lengths, ``strap``, ``fabric`` on a lampshade or toy, the neck values of ``knit_style``,
  ``origin`` (one multi-valued key, most specific place first);
- **value fixes** (no deliberately wrong data, gen#404): one spelling per value, units in the unit
  field, a boolean only when true and always ``Yes``.

``tests/test_retail_attribute_cleanup_497.py`` holds the guards.
"""

from __future__ import annotations

import re
from typing import Any

from synthetic_ecommerce_data.core.entry import split

#: Keys the published document does not carry.
REMOVED = frozenset({"storage_type", "tracker_type", "brand_owner", "pack_size"})

#: Old key -> (key, name): the same concept written two ways (reviews #15-#29, #31).
RENAMES: dict[str, tuple[str, str]] = {
    "fill": ("filling", "Filling"),
    "seats": ("seat_count", "Seat count"),
    "max_weight_kg": ("max_load_kg", "Maximum load"),
    "voltage_v": ("battery_voltage", "Battery voltage"),
    "power": ("power_source", "Power source"),
    "fragrance": ("scent", "Scent"),
    "range": ("line", "Range"),
    "suit_set": ("line", "Range"),
    "pocket": ("pockets", "Pockets"),
    "arm": ("arm_style", "Arm style"),
    "blade_size": ("blade_span", "Blade span"),
    "finished_size": ("dimensions", "Dimensions"),
    "charms": ("charm_count", "Charm count"),
    "drop": ("heel_drop", "Heel drop"),
    "number_of_pieces": ("piece_count", "Piece count"),
    "items": ("piece_count", "Piece count"),
    "contents": ("piece_count", "Piece count"),
    "skirt_length": ("garment_length", "Garment length"),
    "garment_length": ("garment_length", "Garment length"),
    "inside_leg": ("leg_length", "Leg length"),
    "fit_length": ("leg_length", "Leg length"),
    "country": ("origin", "Origin"),
    "line": ("line", "Range"),
}

#: The one-type retail sub-kind keys that fold into ``style`` (review #30). Kept apart because
#: each is a well-known filter of its own: ``bra_shape``, ``back_style``, ``leg_fit``, ``fit``,
#: ``cut``, ``collar``, ``closure``, ``knit_style``.
STYLE_KEYS = frozenset(
    """accessory_type airer_type bag_shape bag_style band_type bbq_kind bin_type bookcase_style
    bowl_type bracelet_type chair_style chest_style cutlery_type earring_style fixture_type
    furniture_kind glass_type heater_type jelly_style kettle_type knife_type laundry_basket_type
    lid_type mattress_type mirror_type module_type mop_type necklace_type pan_type parasol_kind
    pinafore_style plate_type pump_type purse_type ring_type shapewear_type shorts_style
    skirt_shape skirt_style spirit_style table_type tent_type toy_type umbrella_type
    utensil_type watch_type""".split()
)

#: A leg length is Short, Regular or Long; "Petite" is a size range (review #2, ruling 10-18).
LEG_LENGTH = {"Short/Petite": "Short", "Petite": "Short"}
#: ``knit_style``'s neck values are ``neckline``'s, in its spelling.
NECKS = {"Crew Neck": "crew", "V Neck": "v-neck", "Roll Neck": "high", "Boat Neck": "boat"}
#: Strap values that are a material; the rest of ``strap`` is a form (Adjustable, Thin, Back strap).
STRAP_MATERIALS = frozenset({"Leather", "Fabric", "Stainless Steel Mesh", "Silicone", "Chain"})
#: An origin written as an adjective, as place names, most specific first.
PLACES = {
    "Brazilian": ["Brazil"], "Colombian": ["Colombia"], "Croatian": ["Croatia"],
    "Ethiopian": ["Ethiopia"], "Greek": ["Greece"], "Guatemalan": ["Guatemala"],
    "Italian": ["Italy"], "Portuguese": ["Portugal"], "Spanish": ["Spain"],
    "Tunisian": ["Tunisia"], "Sicilian": ["Sicily", "Italy"], "Sumatran": ["Sumatra", "Indonesia"],
}  # fmt: skip
#: Value spellings, by published key.
VALUES: dict[str, dict[str, str]] = {
    "garment_length": {"Knee Length": "Knee", "Full Length": "Full"},
    "filling": {"Hollow Fibre": "Hollowfibre"},
    "power_source": {"Battery": "Battery-powered", "Battery-Powered": "Battery-powered",
                     "USB-Powered": "USB-powered"},
}  # fmt: skip
#: Keys whose value is a number with its unit written in it ("36cm"): the unit field takes it.
UNIT_IN_VALUE = frozenset({"calf", "heel_drop", "mattress_depth"})
_NUMBER_UNIT = re.compile(r"^(\d+(?:\.\d+)?)\s*(cm|mm)$")
_COUNT = re.compile(r"^(\d+)(?: items)?$")


def _entry(key: str, name: str, value: Any, unit: str | None = None) -> dict[str, Any]:
    return {"key": key, "name": name, **split(name, str(value), bare_unit=unit)}


def _as(e: dict[str, Any], key: str, name: str, value: Any = None) -> dict[str, Any]:
    """``e`` published as ``key``/``name``; a changed value is re-split, so units stay in the unit field."""
    if value is None or value == e["value"]:
        return e | {"key": key, "name": name}
    return _entry(key, name, value)


def _one(e: dict[str, Any], product_type: str) -> list[dict[str, Any]]:
    key, value = e["key"], e["value"]
    if key in REMOVED:
        return []
    if key == "type" and value == product_type:
        return []
    if key in STYLE_KEYS:
        return [_as(e, "style", "Style")]
    if key == "inside_leg" or key == "fit_length" or (key == "length" and product_type == "Jeans"):
        return [_as(e, "leg_length", "Leg length", LEG_LENGTH.get(value, value))]
    if key == "length":  # a dressing gown's or slip's style length
        return [_as(e, "garment_length", "Garment length")]
    if key == "strap":
        if value in STRAP_MATERIALS:
            return [_as(e, "strap_material", "Strap material")]
        return [_as(e, "strap_style", "Strap style")]
    if key == "fabric" and product_type == "Lampshade":
        return [_as(e, "shade_material", "Shade material")]
    if key == "fabric" and product_type == "Soft Toy":
        return [_as(e, "material", "Material")]
    if key == "knit_style" and value in NECKS:
        return [_as(e, "neckline", "Neckline", NECKS[value])]
    if key in ("country", "origin") and value in PLACES:
        return [_as(e, "origin", "Origin", place) for place in PLACES[value]]
    if key in ("contents", "items", "number_of_pieces"):
        count = _COUNT.match(str(value))
        return [_entry("piece_count", "Piece count", count.group(1), "C62")] if count else [e]
    if key == "depth" and product_type == "Sofa Bed":
        return [_as(e, "mattress_depth", "Mattress depth")]
    if key in RENAMES and (RENAMES[key][0] != key or e["name"] != RENAMES[key][1]):
        return [_as(e, *RENAMES[key])]
    return [e]


def _tidy(e: dict[str, Any]) -> dict[str, Any] | None:
    """A value fix: a spelling, a unit out of the value, a boolean only when true, as ``Yes``."""
    value = e["value"]
    value = VALUES.get(e["key"], {}).get(value, value) if isinstance(value, str) else value
    if isinstance(value, str) and value.lower() in ("yes", "no", "true", "false"):
        return None if value.lower() in ("no", "false") else e | {"value": "Yes"}
    if e["key"] in UNIT_IN_VALUE and isinstance(value, str) and (m := _NUMBER_UNIT.match(value)):
        return _entry(e["key"], e["name"], f"{m.group(1)} {m.group(2)}")
    return e if value == e["value"] else _as(e, e["key"], e["name"], value)


def clean(entries: list[dict[str, Any]], product_type: str) -> list[dict[str, Any]]:
    """``entries`` as published: removed keys gone, merged keys under one key and name, values
    fixed, a repeat of a (key, value) dropped (so ``origin`` lists each place once)."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for raw in entries:
        for e in _one(raw, product_type):
            fixed = _tidy(e)
            if fixed is not None and (fixed["key"], fixed["value"]) not in seen:
                seen.add((fixed["key"], fixed["value"]))
                out.append(fixed)
    return out
