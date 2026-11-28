"""A retail ``size`` is written under the key of its size system (gen#125, the 2026-11-20 ruling).

The build's rows say ``size`` for many kinds of value: a letter (``M``), an age (``3-4 Yrs``), a UK
dress or bra size (``12``, ``32B``), a towel (``Bath Sheet``), a picture's ``5 x 7 in``, a pack's
``150g``, a jar's ``0.5 L``, a plant's ``60 cm``. One key for all of them is two kinds of value
under one name, and industrial's ``size`` is a measured one. The ruling ("The generator should
write the final shape") moves the rule elastic/prism-retail-and-industrial's
``combined_catalog.retail_size_key`` applied downstream into the generator: :func:`renamed` gives
each bare ``size`` entry its key, and :func:`size_key` raises on a value no row names, so a new
shape is a chosen row here, never a guess.

The keys and names are the ones that repository writes: ``size_letter`` "Size (letter)",
``size_age`` "Size (age)", ``size_uk`` "Size (UK)", ``size_towel`` "Size (towel)", and for the
values that are no size system ``dimensions``, ``pack_size`` and ``capacity_volume``. A measured
length in centimetres is one place this generator differs: it goes under ``item_height`` or
``item_width``, the keys gen#227 chose for an item's size (:mod:`.key_guard`; that repository
writes ``height`` and ``width``), or ``diameter``. A lone ``size_uk`` is no core chart's row,
so the standard's three-key rule leaves it alone (:func:`..core.size_charts.problems`).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable, Mapping
from decimal import Decimal
from typing import Any

from synthetic_ecommerce_data.core.entry import canonical

#: The bare key the build's rows write.
SIZE = "size"

#: Each size system's key and its display name.
SYSTEM_NAMES = {
    "size_letter": "Size (letter)",
    "size_age": "Size (age)",
    "size_uk": "Size (UK)",
    "size_towel": "Size (towel)",
}

#: The display names of the keys a value that is no size system takes.
OTHER_NAMES = {
    "dimensions": "Dimensions",
    "pack_size": "Pack size",
    "capacity_volume": "Capacity (volume)",
    "item_height": "Item height",
    "item_width": "Item width",
    "diameter": "Diameter",
}

#: Every key a bare ``size`` can become.
KEYS = frozenset(SYSTEM_NAMES) | frozenset(OTHER_NAMES)

#: The keys of a measured length, written in centimetres.
_LENGTH_KEYS = frozenset({"item_height", "item_width", "diameter"})

#: Value shapes, in order, and the size system each is. A value matching none goes on to the
#: shapes that are no size system (:func:`size_key`).
SYSTEMS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"^(XXS|XS|S|M|L|XL|XXL|XXXL|Small|Medium|Large)$"), "size_letter"),
    # A tights or socks size spanning two letter sizes; only these three, so ``S/XL`` refuses.
    (re.compile(r"^(S/M|M/L|L/XL)$"), "size_letter"),
    (re.compile(r"^\d{1,2}(-\d{1,2})? Yrs$"), "size_age"),
    # A baby's age in months is the same age system as the years.
    (re.compile(r"^(Newborn|\d{1,2}-\d{1,2} Mths)$"), "size_age"),
    # A UK dress size (6-16) or a UK bra size, band then cup (32B, 34DD).
    (re.compile(r"^(\d{1,2}|\d{2}[A-K]{1,2})$"), "size_uk"),
    (re.compile(r"^(Hand Towel|Bath Towel|Bath Sheet)$"), "size_towel"),
)

#: A width by a height (``18 x 23 cm``, ``45 x 45cm``, ``5 x 7 in``).
_DIMENSIONS = re.compile(r"^\d+(\.\d+)? x \d+(\.\d+)? ?(cm|in)$")
#: An amount of mass or volume, optionally a multipack (``6 x 25g``).
_AMOUNT = re.compile(r"^(\d+ x )?\d+(\.\d+)? ?(g|kg|ml|L)$")
_VOLUME = re.compile(r"^\d+(\.\d+)? ?(ml|L)$")
#: Departments where an amount is what the pack holds; elsewhere a volume is what the item holds.
#: Departments are compared casefolded: a build row says ``Food & Drink``, core ``Food & drink``.
_PACK_DEPARTMENTS = frozenset({"food & drink", "beauty"})
#: A length label (a plant's ``60 cm``, ``1.2 m``).
_LENGTH = re.compile(r"^(?P<number>\d+(\.\d+)?) ?(?P<unit>cm|m)$")
_CENTIMETRES_PER = {"cm": Decimal(1), "m": Decimal(100)}
#: Only a Garden length is a plant's height.
_HEIGHT_DEPARTMENTS = frozenset({"garden"})
#: What a Home furniture length measures, keyed by the row's ``item_*`` keys equal to it and its
#: ``shape`` (a round table's width is its diameter). A Home length matching no row is refused.
_HOME_LENGTH_KEYS: dict[tuple[frozenset[str], str | None], str] = {
    (frozenset({"item_height"}), None): "item_height",
    (frozenset({"item_width", "item_length"}), "Square"): "item_width",
    (frozenset({"item_width", "item_length"}), "Round"): "diameter",
    (frozenset({"item_width", "item_height"}), "Round"): "diameter",
    (frozenset({"item_width", "item_height"}), "Sunburst"): "diameter",
}
#: The attributes a Home length is read against.
SIBLING_KEYS = ("shape", "item_height", "item_width", "item_length")


def _decimal(text: str) -> Decimal | None:
    try:
        return Decimal(text)
    except ArithmeticError:
        return None


def _centimetres(value: str) -> Decimal:
    match = _LENGTH.match(value)
    assert match is not None, value
    return Decimal(match["number"]) * _CENTIMETRES_PER[match["unit"]]


def _home_length_key(value: str, siblings: Mapping[str, str]) -> str | None:
    cm = _centimetres(value)
    equal = frozenset(
        key
        for key in ("item_height", "item_width", "item_length")
        if key in siblings and _decimal(siblings[key]) == cm
    )
    shape = siblings.get("shape")
    return _HOME_LENGTH_KEYS.get((equal, shape)) or _HOME_LENGTH_KEYS.get((equal, None))


def size_key(value: str, department: str, siblings: Mapping[str, str] | None = None) -> str:
    """The key a bare ``size`` *value* is written under, in *department*.

    *siblings* is the row's :data:`SIBLING_KEYS` values: a Home length needs them to say what it
    measures. A value matching no shape raises."""
    folded = department.casefold()
    for pattern, key in SYSTEMS:
        if pattern.match(value):
            return key
    if _DIMENSIONS.match(value):
        return "dimensions"
    if _LENGTH.match(value):
        if folded in _HEIGHT_DEPARTMENTS:
            return "item_height"
        if folded == "home":
            home = _home_length_key(value, siblings or {})
            if home is not None:
                return home
        raise ValueError(
            f"size {value!r} is a length in department {department!r}, which is not "
            f"{sorted(_HEIGHT_DEPARTMENTS)}, and no Home furniture row (_HOME_LENGTH_KEYS) says "
            "what it measures; add its key rather than guess"
        )
    if _AMOUNT.match(value):
        if folded in _PACK_DEPARTMENTS:
            return "pack_size"
        if _VOLUME.match(value):
            return "capacity_volume"
        raise ValueError(
            f"size {value!r} is an amount outside a packed department ({department!r}) and not a "
            "volume; add its key rather than guess"
        )
    raise ValueError(f"size {value!r} matches no size system; add its shape and key")


def entry(value: str, department: str, siblings: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The attribute entry a bare ``size`` *value* becomes: its key, its name, and for a length its
    measure in centimetres (``unit_code`` CMT), as every measured length is written."""
    key = size_key(value, department, siblings)
    if key in _LENGTH_KEYS:
        cm = format(_centimetres(value).normalize(), "f")
        return {
            "key": key,
            "name": OTHER_NAMES[key],
            "value": cm,
            "unit_code": "CMT",
            "value_canonical": canonical(cm, "CMT"),
        }
    return {"key": key, "name": SYSTEM_NAMES.get(key) or OTHER_NAMES[key], "value": value}


def siblings_of(entries: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """The :data:`SIBLING_KEYS` values of *entries*, the later entry winning."""
    return {e["key"]: str(e["value"]) for e in entries if e["key"] in SIBLING_KEYS}


def renamed(
    entries: list[dict[str, Any]],
    department: str,
    siblings: Callable[[str], Mapping[str, str]],
) -> list[dict[str, Any]]:
    """*entries* with each bare ``size`` entry under its key (:func:`entry`), a repeat dropped.

    ``siblings(value)`` is the row a size value is read against (a style's list of sizes reads
    each against the SKU that states it). A renamed entry that lands on a key and value the list
    already states is that entry once."""
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, Any]] = set()
    for e in entries:
        if e["key"] == SIZE:
            value = str(e["value"])
            e = entry(value, department, siblings(value))
        if (e["key"], e["value"]) not in seen:
            seen.add((e["key"], e["value"]))
            out.append(e)
    return out
