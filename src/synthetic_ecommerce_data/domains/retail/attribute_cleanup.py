"""One concept, one published attribute: the retail document's attribute clean-up (gen#497).

The authored rows keep the keys they were written with: the drawing params, the scaler's value
pools and ``FROZEN_KEYS`` read them. What a shopper and a downstream catalogue see is the
published document, so :func:`clean` (called by ``export._product_attributes`` and
``export._variant``) rewrites each entry list once:

- **dropped**: an entry a retailer would not print because the title and the category already
  say it, a key in :data:`RESTATING` whose value is the product type itself (``storage_type``
  "Storage Box" on a Storage Box, ``tracker_type`` "Fitness band" on a Fitness Band, a ``type``
  equal to the type). A real sub-kind of the same key (a nursery storage's Basket) stays;
- **merged**: a key in :data:`RENAMES` is the same concept as another key and goes out under
  that key and its one display name (``seats`` is ``seat_count`` "Seat count", ``range`` and
  ``suit_set`` are ``line`` "Range"); a (key, value) the merge repeats is published once;
- **respelt**: :data:`VALUES` gives a merged key's value its one spelling, and the value is split
  again so a unit written into it (a heel drop's "8mm") goes to the unit field.

A test that reads a document by an authored key asks :func:`published` for the key to read.
The rest of #497's retail half (the length cluster, the ``style`` fold, ``origin``, the other
value fixes) goes in later slices.
"""

from __future__ import annotations

from typing import Any

from synthetic_ecommerce_data.core.entry import split

#: Keys the review found carrying the product type as their value (#497, "Remove").
RESTATING = frozenset({"storage_type", "tracker_type", "type"})

#: Authored key -> the (key, display name) it is published under: one concept written two
#: ways (#497 review merges #15-#27, #31). A target key is listed too, so it carries one name.
RENAMES: dict[str, tuple[str, str]] = {
    "fill": ("filling", "Filling"),
    "seats": ("seat_count", "Seat count"),
    "max_weight_kg": ("max_load_kg", "Maximum load"),
    "voltage_v": ("battery_voltage", "Battery voltage"),
    "power": ("power_source", "Power source"),
    "range": ("line", "Range"),
    "suit_set": ("line", "Range"),
    "line": ("line", "Range"),
    "pocket": ("pockets", "Pockets"),
    "arm": ("arm_style", "Arm style"),
    "blade_size": ("blade_span", "Blade span"),
    "finished_size": ("dimensions", "Dimensions"),
    "charms": ("charm_count", "Charm count"),
    "drop": ("heel_drop", "Heel drop"),
}

#: Published key -> {value: its one spelling} (#497 value fixes).
VALUES: dict[str, dict[str, str]] = {
    "power_source": {"Battery": "Battery-Powered"},
}


def published(key: str) -> str:
    """The key an authored ``key`` is published under."""
    return RENAMES.get(key, (key,))[0]


def restates_the_type(entry: dict[str, Any], product_type: str) -> bool:
    """Whether ``entry`` says only what the product type already says."""
    value = entry["value"]
    return (
        entry["key"] in RESTATING
        and isinstance(value, str)
        and value.casefold() == product_type.casefold()
    )


def _merged(entry: dict[str, Any]) -> dict[str, Any]:
    """``entry`` under its published key and name, its value in its one spelling."""
    if entry["key"] not in RENAMES:
        return entry
    key, name = RENAMES[entry["key"]]
    value = entry["value"]
    if isinstance(value, str) and "unit_code" not in entry:
        value = VALUES.get(key, {}).get(value, value)
        return {"key": key, "name": name, **split(name, value)}
    return entry | {"key": key, "name": name}


def clean(entries: list[dict[str, Any]], product_type: str) -> list[dict[str, Any]]:
    """``entries`` as published: none restating the type, each merged key under its one key
    and name, a (key, value) the merge repeats dropped."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for raw in entries:
        if restates_the_type(raw, product_type):
            continue
        e = _merged(raw)
        if e is raw or (e["key"], e["value"]) not in seen:
            seen.add((e["key"], e["value"]))
            out.append(e)
    return out
