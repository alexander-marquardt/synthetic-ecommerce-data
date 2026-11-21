"""The orientation of every retail drawing: the set of angles a product's figure turns by (#849).

Retail draws a product as a shape (:data:`kit.SHAPES`), and many types share one (jeans, chinos
and joggers are all ``trousers``), so the orientation is the shape's: what is drawn is what
looks right or wrong turned. Tilt is opt-in (#1101): a shape is named, in the module of
:mod:`orientations` named after the module that registers it (#1045), only to give it a tilt
or to record why it is level. A shape no module names is ``level`` (:func:`of`), so a new
shape is never turned by accident. This module holds no shape: it walks that package and builds
the table. The sets are :data:`...core.drawing.product_look.ORIENTATIONS`:

* ``any`` (the 24 clock positions): a small thing with no natural up. Gloves (the maintainer's
  ruling on #860), a screw, a ball, round fruit, a snowflake, coiled cables and laces.
* ``slight`` (+-15 degrees): clothing, footwear and what is worn with them (a belt, a scarf, a
  tie, a hat), where a garment turned further reads as falling over (the maintainer's ruling
  on #860).
* ``upright`` (+-36 degrees): a small thing you hold, carry or wear that has a natural up (a
  bottle, a bulb, a kettle, a phone, a doll, a drill).

* ``level`` (0 degrees only, #884), and every shape no module names: a set type drawn as several
  items (cutlery, a dinner set, luggage), which overlap on a slant; and a bicycle, which rests
  on its two wheels and reads as falling or wheelieing on a slant (#1049); and every furniture
  item (a bed, a sofa, a table, a wardrobe: the shapes of the furniture, seating, home and
  storage furniture kits), which stands on the floor and looks wrong turned (the maintainer,
  2026-11-20, #1095), and with it every lamp and light fitting, the lampshade, the coat stand,
  the garden furniture and parasols, and the crib (#1095, slice 2); and each shape that was
  ``upright`` but is not held or worn (#1101, slice 2: the list is
  ``tests/test_level_default_1101.py``). That covers a shape that stands on the floor, one fixed
  to a wall, ceiling, car or plumbing, a mains appliance or screen used where it stands,
  bedding, rugs, mats and curtains, and a vehicle or anything on wheels.

A product any SKU of which is a pack of several items (``pack_copies.count``: its pack size,
units per pack or pack attribute, or "Set of 2" in its title) is drawn level on every SKU
whatever its shape (:func:`of_product`, #884), so a cup set in 2, 4 and 8 packs stands level
while a single cup keeps its tilt. To move a shape, move its line to another tuple of its owner's
module in :mod:`orientations`.

A guard beside the pack rule wins over the shape table (:func:`level_because`, #1101). A product
in a category of :data:`NEVER_TILT` (furniture, large appliances, bikes, kick scooters,
ride-ons) is drawn level, and so is a product whose stated height or length is over
:data:`MAX_TILT_CM` (:func:`stated_cm`). The shape alone used to decide: a shape nobody was sure
of went to ``upright``, so every fridge and washing machine was turned by up to 36 degrees.
"""

from __future__ import annotations

import importlib
import pkgutil
import re
from typing import Any

from synthetic_ecommerce_data.core.drawing import product_look
from synthetic_ecommerce_data.domains.retail import orientations, pack_copies

_SETS: tuple[str, ...] = ("ANY", "SLIGHT", "UPRIGHT", "LEVEL")


def _owned() -> dict[str, dict[str, tuple[str, ...]]]:
    """Each module of :mod:`orientations` by name -> its four tuples (an absent one empty).
    A module that names no shape, or a shape another module (or set) already names, is refused."""
    owned: dict[str, dict[str, tuple[str, ...]]] = {}
    seen: dict[str, str] = {}
    for info in sorted(pkgutil.iter_modules(orientations.__path__), key=lambda i: i.name):
        module = importlib.import_module(f"{orientations.__name__}.{info.name}")
        sets = {name: tuple(getattr(module, name, ())) for name in _SETS}
        if not any(sets.values()):
            raise ValueError(f"orientations/{info.name}.py names no shape in {', '.join(_SETS)}")
        for name, shapes in sets.items():
            for shape in shapes:
                where = f"orientations/{info.name}.py {name}"
                if shape in seen:
                    raise ValueError(f"shape {shape!r} is in {seen[shape]} and {where}")
                seen[shape] = where
        owned[info.name] = sets
    return owned


_OWNED = _owned()

#: Things with no natural up, drawn at any of the 24 clock positions.
ANY: tuple[str, ...] = tuple(s for sets in _OWNED.values() for s in sets["ANY"])

#: Clothing, footwear and what is worn with them: within +-15 degrees.
SLIGHT: tuple[str, ...] = tuple(s for sets in _OWNED.values() for s in sets["SLIGHT"])

#: Small things held, carried or worn that have a natural up: within +-36 degrees (#1101).
UPRIGHT: tuple[str, ...] = tuple(s for sets in _OWNED.values() for s in sets["UPRIGHT"])

#: Set types, drawn as several items (#884), a bicycle on its wheels (#1049), furniture (#1095)
#: and what is not held or worn (#1101): 0 degrees only, as is every shape no module names.
LEVEL: tuple[str, ...] = tuple(s for sets in _OWNED.values() for s in sets["LEVEL"])

#: Shape -> orientation.
ORIENTATION: dict[str, str] = {
    **dict.fromkeys(ANY, "any"),
    **dict.fromkeys(SLIGHT, "slight"),
    **dict.fromkeys(UPRIGHT, "upright"),
    **dict.fromkeys(LEVEL, "level"),
}


def of(shape: str) -> str:
    """The orientation ``shape`` is drawn at: ``level`` for a shape the table does not name, so
    tilt is opt-in (#1101)."""
    return ORIENTATION.get(shape, "level")


#: Category path prefixes whose products stand on the floor or on wheels and are drawn level
#: whatever their shape (#1101): the maintainer, 2026-11-21, "sofas should not be tilted. I
#: think most furniture should not. Neither should mountain bikes."
NEVER_TILT: tuple[tuple[str, ...], ...] = (
    ("Home", "Furniture"),
    ("Garden", "Garden Furniture"),
    ("Kids", "Baby", "Nursery Furniture"),
    ("Home", "Large Appliances"),
    ("Sports & Outdoors", "Cycling", "Bikes"),
    ("Sports & Outdoors", "Yoga & Fitness", "Exercise Bikes"),
    ("Sports & Outdoors", "Wheeled Sports", "Kick Scooters"),
    ("Toys", "Outdoor Toys", "Ride-On Toys"),
)

#: A product with a stated height or length over this many centimetres is drawn level (#1101).
MAX_TILT_CM = 60.0

#: The attributes and SKU fields that state an item's own height or length, in centimetres. A
#: run length in metres (a cable, a hose, bunting) is not one: the item is drawn coiled.
_CM_FIELDS: tuple[str, ...] = ("item_height", "item_length", "height_cm", "length_cm")

_FEET = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*ft\b")
_CM_DIMS = re.compile(r"(\d+(?:\.\d+)?(?:\s*x\s*\d+(?:\.\d+)?)+)\s*cm\b")


def _cm(key: str, value: Any) -> list[float]:
    """The centimetre figures field ``key`` states in ``value``: a number for a
    :data:`_CM_FIELDS` field, a ``"5 ft"`` height, or each side of a ``"60 x 90 cm"``
    ``dimensions`` value (all its sizes, when it lists several)."""
    text = str(value)
    if key in _CM_FIELDS:
        try:
            return [float(text)]
        except ValueError:
            return []
    if key == "height" and (feet := _FEET.match(text)):
        return [float(feet.group(1)) * 30.48]
    if key == "dimensions":
        return [float(n) for dims in _CM_DIMS.findall(text) for n in re.split(r"\s*x\s*", dims)]
    return []


def stated_cm(rec: dict[str, Any]) -> float | None:
    """The largest height or length product ``rec`` states, in centimetres, over its attributes
    and every SKU (``None`` when it states none)."""
    figures = [n for attr in rec.get("attributes", ()) for n in _cm(attr["key"], attr["value"])]
    figures += [n for sku in rec.get("skus", ()) for key, v in sku.items() for n in _cm(key, v)]
    return max(figures, default=None)


def level_because(rec: dict[str, Any]) -> str | None:
    """Why product ``rec`` is drawn level whatever its shape, or ``None``: ``"pack"`` when any of
    its SKUs is a pack of several items (#884), ``"category"`` when its category is under
    :data:`NEVER_TILT`, ``"size"`` when it states a height or length over :data:`MAX_TILT_CM`
    (#1101)."""
    if any(pack_copies.count(rec, sku) > 1 for sku in rec.get("skus", ())):
        return "pack"
    path = tuple(rec.get("category_path", ()))
    if any(path[: len(prefix)] == prefix for prefix in NEVER_TILT):
        return "category"
    cm = stated_cm(rec)
    if cm is not None and cm > MAX_TILT_CM:
        return "size"
    return None


def of_product(rec: dict[str, Any]) -> str:
    """The orientation product ``rec`` is drawn at: its shape's, or ``level`` when
    :func:`level_because` names a reason (a pack, #884; a never-tilt category or a stated size
    over the limit, #1101), so every SKU of it shares the one angle."""
    held = level_because(rec) is not None
    return product_look.product_orientation(of(rec["drawing"]["shape"]), held)
