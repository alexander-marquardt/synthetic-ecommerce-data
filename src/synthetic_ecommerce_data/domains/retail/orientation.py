"""The orientation of every retail drawing: the set of angles a product's figure turns by (#849).

Retail draws a product as a shape (:data:`kit.SHAPES`), and many types share one (jeans, chinos
and joggers are all ``trousers``), so the orientation is the shape's: what is drawn is what
looks right or wrong turned. Every registered shape names one, in the module of
:mod:`orientations` named after the module that registers it (#1045), and
``tests/test_one_paper_one_angle_849.py`` refuses a shape missing from this table, so a new
shape cannot forget it. This module holds no shape: it walks that package and builds the
table. The sets are :data:`...core.drawing.product_look.ORIENTATIONS`:

* ``any`` (the 24 clock positions): a thing with no natural up. Gloves (the maintainer's ruling
  on #860), a screw, a ball, round fruit, a snowflake, coiled cables and laces.
* ``slight`` (+-15 degrees): clothing, footwear and what is worn with them (a belt, a scarf, a
  tie, a hat), where a garment turned further reads as falling over (the maintainer's ruling
  on #860).
* ``upright`` (+-36 degrees): everything with a natural up (a bottle, a sofa, a lamp, a fridge,
  a toy), and every shape nobody was sure of.

* ``level`` (0 degrees only, #884): a set type drawn as several items (cutlery, a dinner set,
  luggage), which overlap on a slant; and a bicycle, which rests on its two wheels and reads as
  falling or wheelieing on a slant (#1049).

A product any SKU of which is a pack of several items (``pack_copies.count``: its pack size,
units per pack or pack attribute, or "Set of 2" in its title) is drawn level on every SKU
whatever its shape (:func:`of_product`, #884), so a cup set in 2, 4 and 8 packs stands level
while a single cup keeps its tilt. To move a shape, move its line to another tuple of its owner's
module in :mod:`orientations`.
"""

from __future__ import annotations

import importlib
import pkgutil
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

#: Everything with a natural up, and every shape nobody was sure of: within +-36 degrees.
UPRIGHT: tuple[str, ...] = tuple(s for sets in _OWNED.values() for s in sets["UPRIGHT"])

#: Set types, drawn as several items (#884), and a bicycle on its wheels (#1049): 0 degrees only.
LEVEL: tuple[str, ...] = tuple(s for sets in _OWNED.values() for s in sets["LEVEL"])

#: Shape -> orientation.
ORIENTATION: dict[str, str] = {
    **dict.fromkeys(ANY, "any"),
    **dict.fromkeys(SLIGHT, "slight"),
    **dict.fromkeys(UPRIGHT, "upright"),
    **dict.fromkeys(LEVEL, "level"),
}


def of(shape: str) -> str:
    """The orientation ``shape`` is drawn at. ``KeyError`` for a shape the table does not name."""
    return ORIENTATION[shape]


def of_product(rec: dict[str, Any]) -> str:
    """The orientation product ``rec`` is drawn at: its shape's, or ``level`` when any of its
    SKUs is a pack of several items (#884), so every SKU of it shares the one angle."""
    packed = any(pack_copies.count(rec, sku) > 1 for sku in rec.get("skus", ()))
    return product_look.product_orientation(of(rec["drawing"]["shape"]), packed)
