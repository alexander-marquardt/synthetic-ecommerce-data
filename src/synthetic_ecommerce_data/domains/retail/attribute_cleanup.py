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
  also puts Petite in the ``size_range``, whose values are title case;
- **split**: an authored key holding two kinds of value goes out as one key per kind (the 10-18
  ruling, "Split"): a watch's ``strap`` is ``strap_material``, any other's ``strap_style``; a
  lampshade's ``fabric`` is ``shade_material`` and a soft toy's ``material``; a neck in a
  ``knit_style`` (:data:`BY_VALUE`) is the ``neckline``, unless the product authors its own
  neckline (a polo's Collared), and every neckline takes one spelling (Crew, V-neck; a roll
  or turtle neck is High, as ``neckline_rows.TITLE_WORDS`` reads it);
  and ``items`` or a ``contents`` that only counts ("3 items", :data:`COUNTED`) is the
  ``piece_count``, a bare number of pieces;
- **folded**: a one-type sub-kind key (:data:`SUB_KINDS`: a BBQ's ``bbq_kind``, a skirt's
  ``skirt_shape``, a whisky's ``spirit_style``) is the product's ``style`` "Style" (the 10-18
  ruling, "Style"). A value naming the product type itself (a Marble Run's ``toy_type`` Marble
  Run) is dropped as above. The well-known facets of their own (``bra_shape``, ``knit_style``,
  ``back_style``, ``leg_fit``, ``fit``, ``cut``, ``collar``, ``closure``) are not folded;
- **value-fixed** (no deliberately wrong data, gen#404): a boolean is published only when
  true, always as ``Yes`` (:data:`TRUE`, :data:`FALSE`), and a :data:`UNIT_IN_VALUE` value's
  unit ("36cm") goes to the unit field.

Across the catalogue, one display name names one key and one key has one name
(``name_guard.catalogue_name_findings``): a Rug's ``rug_shape`` is ``shape``, and so on in
:data:`RENAMES`. A test that reads a document by an authored key asks :func:`published` for the
key to read. A Skirt's ``fit_length`` and a Suit Jacket's ``length`` await a ruling.
"""

from __future__ import annotations

import re
from typing import Any

from synthetic_ecommerce_data.core.entry import canonical, split

#: Review merge #30's one-type sub-kind keys, and the Jelly Shoes' ``jelly_style`` (also shown
#: as "Style"): each names the kind of product within its type, published as ``style``.
SUB_KINDS = frozenset(
    {
        "accessory_type", "airer_type", "bag_shape", "bag_style", "band_type", "bbq_kind",
        "bin_type", "bolero_style", "bookcase_style", "bowl_type", "bracelet_type", "chair_style",
        "chest_style", "cutlery_type", "earring_style", "fixture_type", "furniture_kind",
        "glass_type", "heater_type", "jelly_style", "kettle_type", "knife_type", "ladder_kind",
        "laundry_basket_type", "lid_type", "mattress_type", "mirror_type", "module_type",
        "mop_type", "necklace_type", "pan_type", "parasol_kind", "pinafore_style", "plate_type",
        "pump_type", "purse_type", "ring_type", "shapewear_type", "shorts_style", "skirt_shape",
        "skirt_style", "spirit_style", "storage_type", "table_type", "tent_type", "toy_type",
        "tracker_type", "umbrella_type", "utensil_type", "watch_type",
    }
)  # fmt: skip
#: Keys the review found carrying the product type as their value (#497, "Remove"), and every
#: key folded into ``style`` (a Frying Pan's ``pan_type`` Frying Pan).
RESTATING = frozenset({"type", "style", *SUB_KINDS})

#: Authored key -> the (key, display name) it is published under: one concept written two
#: ways (#497 review merges #15-#27, #31). A target key is listed too, so it carries one name.
LEG = ("leg_length", "Leg length")
GARMENT = ("garment_length", "Garment length")
STRAP_MATERIAL = ("strap_material", "Strap material")
NECKLINE = ("neckline", "Neckline")
PIECES = ("piece_count", "Piece count")
STYLE = ("style", "Style")
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
    "strap": ("strap_style", "Strap style"),
    "neckline": NECKLINE,
    "items": PIECES,
    "piece_count": PIECES,
    # One display name, one key, catalogue-wide (#497's guard, ``name_guard``): a Rug's shape
    # is ``shape``, a Volt Meter's form ``form``, a fan's and a dishwasher's noise one key, a
    # hamper's theme and a tool kit's pieces both its ``contents``; a Water Gun's range is not
    # the brand ``line`` "Range".
    "rug_shape": ("shape", "Shape"),
    "meter_form": ("form", "Form"),
    "noise_db": ("noise_level", "Noise level (dB)"),
    "contents_kind": ("contents", "Contents"),
    "kit_contents": ("contents", "Contents"),
    "water_range": ("water_range", "Water range"),
    **{key: STYLE for key in SUB_KINDS | {"style"}},
}
#: (authored key, product type) -> the (key, name) it is published under on that type alone. A
#: Suit Jacket's Short/Regular/Long ``length`` is a fit with no leg, kept until a ruling. A
#: watch's ``strap`` is what the strap is made of; every other type's is its form (the 10-18
#: ruling, "Split"). A lampshade's and a soft toy's cloth is a material: ``fabric`` is apparel's.
BY_TYPE: dict[tuple[str, str], tuple[str, str]] = {
    ("length", "Jeans"): LEG,
    ("length", "Suit Jacket"): ("length", "Length"),
    ("leg_length", "PE Shorts"): GARMENT,
    ("strap", "Analog Watch"): STRAP_MATERIAL,
    ("strap", "Digital Watch"): STRAP_MATERIAL,
    ("strap", "Fitness Band"): STRAP_MATERIAL,
    ("fabric", "Lampshade"): ("shade_material", "Shade material"),
    ("fabric", "Soft Toy"): ("material", "Material"),
}
#: (authored key, value) -> the (key, name) that value alone is published under: a jumper's
#: ``knit_style`` names its neck beside its construction (review #29), and the neck is its
#: ``neckline``, in that key's vocabulary (``neckline_rows.TITLE_WORDS``). A list that authors
#: that key already keeps its own value and drops the moved one: one neckline per product.
BY_VALUE: dict[tuple[str, str], tuple[str, str]] = {
    ("knit_style", neck): NECKLINE
    for neck in ("Crew Neck", "V Neck", "Roll Neck", "Boat Neck", "Cowl Neck", "Turtle Neck")
}
#: An authored ``contents`` that only counts what is in the box ("3 items") is its piece count
#: (review #6); a ``contents`` that lists the pieces stays.
COUNTED = re.compile(r"(?P<n>\d+) items?")
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
    "filling": {"Hollow Fibre": "Hollowfibre"},
    "leg_length": {"Short/Petite": "Short", PETITE_LEG: "Short"},
    "garment_length": {
        "Knee Length": "Knee",
        "Mid": "Mid Length",
        "Full": "Full Length",
        "Crop": "Cropped",
    },  # fmt: skip
    "size_range": {"petite": "Petite", "regular": "Regular", "tall": "Tall", "plus": "Plus"},
    "neckline": {
        "crew": "Crew", "Crew Neck": "Crew", "v-neck": "V-neck", "V Neck": "V-neck",
        "round": "Round", "boat": "Boat", "Boat Neck": "Boat", "slash": "Slash",
        "square": "Square", "high": "High", "collared": "Collared", "cowl": "Cowl",
        "Cowl Neck": "Cowl", "halter": "Halter", "tie-neck": "Tie-neck",
        "Roll Neck": "High", "Turtle Neck": "High",
    },
}  # fmt: skip
#: A published key whose bare number is in a unit (``export.FACTS`` gives ``piece_count`` C62).
BARE_UNIT = {"piece_count": "C62"}
#: A key whose authored value writes its unit into the text (a boot's calf "36cm", a coat's
#: "5,000 mm" rating): the number is the value and the unit goes to the unit field.
UNIT_IN_VALUE = frozenset({"calf", "waterproof_rating"})
_NUMBER_UNIT = re.compile(r"(?P<n>\d[\d,]*(?:\.\d+)?)\s*(?P<unit>cm|mm)")
_UNIT_CODE = {"cm": "CMT", "mm": "MMT"}
#: A boolean is published only when true, and always as ``Yes`` (#497 value fixes): the
#: authored rows say Yes/No and the record's flags (``online_only``) yes/no.
TRUE, FALSE = frozenset({"yes", "true"}), frozenset({"no", "false"})


def _target(key: str, product_type: str, value: Any = None) -> tuple[str, str] | None:
    if isinstance(value, str):
        if key == "contents" and COUNTED.fullmatch(value):
            return PIECES
        if (key, value) in BY_VALUE:
            return BY_VALUE[(key, value)]
    return BY_TYPE.get((key, product_type)) or RENAMES.get(key)


def published(key: str, product_type: str = "", value: Any = None) -> str:
    """The key an authored ``key`` is published under (on ``product_type``, or with ``value``,
    when it decides)."""
    target = _target(key, product_type, value)
    return key if target is None else target[0]


def published_as(key: str, name: str, product_type: str = "") -> tuple[str, str]:
    """The (key, display name) an authored ``key`` named ``name`` is published under."""
    return _target(key, product_type) or (key, name)


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
    target = _target(entry["key"], product_type, entry["value"])
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
        if target == PIECES:
            value = COUNTED.sub(r"\g<n>", value)
        return {"key": key, "name": name, **split(name, value, BARE_UNIT.get(key))}
    return entry | {"key": key, "name": name}


def withheld(entries: list[dict[str, Any]], product_type: str = "") -> set[str]:
    """The published keys of ``entries`` that publish nothing: every value a false boolean (a
    raincoat that is not ``waterproof``, a tote's ``pocket`` No) or, given ``product_type``,
    one restating it (a plain Bolero's ``bolero_style`` Bolero). A test that wants a type's key
    attributes on its document wants these off it."""
    held: dict[str, bool] = {}
    for e in entries:
        false = isinstance(e["value"], str) and e["value"].casefold() in FALSE
        false = false or restates_the_type(e, product_type)
        key = published(e["key"], product_type)
        held[key] = held.get(key, True) and false
    return {key for key, false in held.items() if false}


def _value_fixed(entry: dict[str, Any]) -> dict[str, Any] | None:
    """``entry`` with a boolean only when true, as ``Yes`` (else None), and a unit written into
    a :data:`UNIT_IN_VALUE` value moved to the unit field."""
    value = entry["value"]
    if not isinstance(value, str) or "unit_code" in entry:
        return entry
    if value.casefold() in FALSE:
        return None
    if value.casefold() in TRUE:
        return entry if value == "Yes" else entry | {"value": "Yes"}
    if entry["key"] in UNIT_IN_VALUE and (m := _NUMBER_UNIT.fullmatch(value)):
        number, unit = m["n"].replace(",", ""), _UNIT_CODE[m["unit"]]
        exact = canonical(number, unit)
        return entry | {"value": number, "unit_code": unit, "value_canonical": exact}
    return entry


def _gives_way(entry: dict[str, Any], authored: set[str]) -> bool:
    """Whether ``entry`` is a value :data:`BY_VALUE` moves onto a key the list already authors
    (a polo's ``knit_style`` Crew Neck beside its ``neckline`` collared)."""
    value = entry["value"]
    return isinstance(value, str) and BY_VALUE.get((entry["key"], value), ("",))[0] in authored


def clean(
    entries: list[dict[str, Any]],
    product_type: str,
    title: str = "",
    *,
    on_product: bool = False,
) -> list[dict[str, Any]]:
    """``entries`` as published: none restating the type, each merged key under its one key
    and name, an origin as its places (a region ``title`` names first), a (key, value) the
    merge repeats dropped, a value moved onto a key the list authors dropped. ``on_product``:
    the product's list, where a Petite leg also puts Petite in the size range (a SKU's list
    does not carry the range)."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    authored = {published(e["key"], product_type) for e in entries}
    for raw in entries:
        if restates_the_type(raw, product_type) or _gives_way(raw, authored):
            continue
        for e in _published(raw, product_type, f"{title} {product_type}", on_product):
            e = _value_fixed(e)
            if e is None:
                continue
            if e is raw or (e["key"], e["value"]) not in seen:
                seen.add((e["key"], e["value"]))
                out.append(e)
    return out
