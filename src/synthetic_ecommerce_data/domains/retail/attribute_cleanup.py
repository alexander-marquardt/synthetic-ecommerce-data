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
  again so a unit written into it (a heel drop's "8mm") goes to the unit field;
- **placed**: ``country`` and ``origin`` are one concept, published as ``origin`` "Origin" with
  one entry per level that applies, most specific first (the 10-18 ruling): an adjective is
  its place (:data:`PLACE_OF`: Croatian is Croatia), a place within a country is followed by
  that country (:data:`WITHIN`: Sicily, Italy), and a region the product's own title or type
  names (:data:`NAMED_REGION`: a Rioja Reserva) goes first when it lies in that country, so
  a search for either level finds it. Every published value is in :data:`PLACES`;
- **lengths**: a trouser's leg option is ``leg_length`` "Leg length" (``inside_leg``, a Jeans
  ``length``) and a style length is ``garment_length`` "Garment length" (``skirt_length``, a
  PE Shorts ``leg_length``, every other type's ``length``), in one spelling each. "Petite" is a
  size range, never a length (the 10-18 ruling): a Petite leg is Short, and on the product it
  also puts Petite in the ``size_range``, whose values are title case.

A test that reads a document by an authored key asks :func:`published` for the key to read.
The rest of #497's retail half (a Skirt's ``fit_length`` and a Suit Jacket's ``length``, which
await a ruling; the ``style`` fold, the other value fixes) goes in later slices.
"""

from __future__ import annotations

import re
from typing import Any

from synthetic_ecommerce_data.core.entry import split

#: Keys the review found carrying the product type as their value (#497, "Remove").
RESTATING = frozenset({"storage_type", "tracker_type", "type"})

#: Authored key -> the (key, display name) it is published under: one concept written two
#: ways (#497 review merges #15-#27, #31). A target key is listed too, so it carries one name.
LEG = ("leg_length", "Leg length")
GARMENT = ("garment_length", "Garment length")
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
    "country": ("origin", "Origin"),
    "origin": ("origin", "Origin"),
    "inside_leg": LEG,
    "leg_length": LEG,
    "length": GARMENT,
    "skirt_length": GARMENT,
    "garment_length": GARMENT,
    "size_range": ("size_range", "Size range"),
}
#: (authored key, product type) -> the (key, name) it is published under on that type alone. A
#: Suit Jacket's Short/Regular/Long ``length`` is a fit with no leg, kept until a ruling.
BY_TYPE: dict[tuple[str, str], tuple[str, str]] = {
    ("length", "Jeans"): LEG,
    ("length", "Suit Jacket"): ("length", "Length"),
    ("leg_length", "PE Shorts"): GARMENT,
}
#: The authored keys no type publishes under their own name: a Suit Jacket keeps ``length``.
RETIRED = frozenset(old for old, (key, _) in RENAMES.items() if old != key) - {
    old for (old, _), (key, _) in BY_TYPE.items() if old == key
}
#: An authored leg value the product's ``size_range`` also carries: Petite is a cut, not a length.
PETITE_LEG = "Petite"

#: An authored origin adjective -> the place it names.
PLACE_OF: dict[str, str] = {
    "Brazilian": "Brazil",
    "Colombian": "Colombia",
    "Croatian": "Croatia",
    "Ethiopian": "Ethiopia",
    "Greek": "Greece",
    "Guatemalan": "Guatemala",
    "Italian": "Italy",
    "Portuguese": "Portugal",
    "Sicilian": "Sicily",
    "Spanish": "Spain",
    "Sumatran": "Sumatra",
    "Tunisian": "Tunisia",
}
#: A place -> the country it lies in.
WITHIN: dict[str, str] = {
    "Champagne": "France",
    "Chianti": "Italy",
    "England": "United Kingdom",
    "Rioja": "Spain",
    "Scotland": "United Kingdom",
    "Sicily": "Italy",
    "Sumatra": "Indonesia",
}
#: A word of a product's title or type -> the region it names.
NAMED_REGION: dict[str, str] = {
    "Champagne": "Champagne",
    "Chianti": "Chianti",
    "English": "England",
    "Rioja": "Rioja",
}
#: Every place an ``origin`` entry may hold.
PLACES = frozenset(
    {
        "Argentina", "Australia", "Barbados", "Brazil", "Caribbean", "Chile", "Colombia",
        "Costa Rica", "Croatia", "Dominican Republic", "Ecuador", "Egypt", "Ethiopia", "France",
        "Germany", "Greece", "Guatemala", "Guyana", "Indonesia", "Ireland", "Israel", "Italy",
        "Jamaica", "Mexico", "Morocco", "Netherlands", "New Zealand", "Peru", "Poland",
        "Portugal", "Serbia", "South Africa", "Spain", "Sweden", "Tunisia", "Turkey",
        "United Kingdom", "United States", *WITHIN,
    }
)  # fmt: skip

#: Published key -> {value: its one spelling} (#497 value fixes).
VALUES: dict[str, dict[str, str]] = {
    "power_source": {"Battery": "Battery-Powered"},
    "leg_length": {"Short/Petite": "Short", PETITE_LEG: "Short"},
    "garment_length": {
        "Knee Length": "Knee",
        "Mid": "Mid Length",
        "Full": "Full Length",
        "Crop": "Cropped",
    },  # fmt: skip
    "size_range": {"petite": "Petite", "regular": "Regular", "tall": "Tall", "plus": "Plus"},
}


def _target(key: str, product_type: str) -> tuple[str, str] | None:
    return BY_TYPE.get((key, product_type)) or RENAMES.get(key)


def published(key: str, product_type: str = "") -> str:
    """The key an authored ``key`` is published under (on ``product_type``, when it decides)."""
    target = _target(key, product_type)
    return key if target is None else target[0]


def restates_the_type(entry: dict[str, Any], product_type: str) -> bool:
    """Whether ``entry`` says only what the product type already says."""
    value = entry["value"]
    return (
        entry["key"] in RESTATING
        and isinstance(value, str)
        and value.casefold() == product_type.casefold()
    )


def places(value: str, named: str) -> list[str]:
    """The levels an authored origin ``value`` publishes, most specific first; ``named`` is
    the product's title and type, whose region goes first when it lies in that place."""
    levels = [PLACE_OF.get(value, value)]
    while levels[-1] in WITHIN:
        levels.append(WITHIN[levels[-1]])
    for word in re.findall(r"\w+", named):
        region = NAMED_REGION.get(word)
        if region is not None and region not in levels and WITHIN[region] == levels[0]:
            levels.insert(0, region)
    return levels


def _published(
    entry: dict[str, Any], product_type: str, named: str, on_product: bool
) -> list[dict[str, Any]]:
    """``entry`` as the entries it publishes: one per origin level, a Petite leg with the
    product's Petite size range, else :func:`_merged`."""
    target = _target(entry["key"], product_type)
    if target is not None and target[0] == "origin":
        values = places(entry["value"], named)
        return [{"key": "origin", "name": target[1], "value": p} for p in values]
    out = [_merged(entry, target)]
    if on_product and target == LEG and entry["value"] == PETITE_LEG:
        out.append({"key": "size_range", "name": "Size range", "value": "Petite"})
    return out


def _merged(entry: dict[str, Any], target: tuple[str, str] | None) -> dict[str, Any]:
    """``entry`` under its published key and name, its value in its one spelling."""
    if target is None:
        return entry
    key, name = target
    value = entry["value"]
    if isinstance(value, str) and "unit_code" not in entry:
        value = VALUES.get(key, {}).get(value, value)
        return {"key": key, "name": name, **split(name, value)}
    return entry | {"key": key, "name": name}


def clean(
    entries: list[dict[str, Any]],
    product_type: str,
    title: str = "",
    *,
    on_product: bool = False,
) -> list[dict[str, Any]]:
    """``entries`` as published: none restating the type, each merged key under its one key
    and name, an origin as its places (a region ``title`` names first), a (key, value) the
    merge repeats dropped. ``on_product``: the product's list, where a Petite leg also puts
    Petite in the size range (a SKU's list does not carry the range)."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for raw in entries:
        if restates_the_type(raw, product_type):
            continue
        for e in _published(raw, product_type, f"{title} {product_type}", on_product):
            if e is raw or (e["key"], e["value"]) not in seen:
                seen.add((e["key"], e["value"]))
                out.append(e)
    return out
