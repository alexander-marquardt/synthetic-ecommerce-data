"""Weekend Bag (gen#209): rounded duffels in canvas, leather-look and nylon.

**Womens > Accessories > Travel > Weekend Bags**: three styles from three invented brands, drawn
by :func:`kit_luggage.weekend_bag` (``compartments``, ``sleeve``). The material, the compartments,
the trolley sleeve and the capacity in litres are structured entries; a SKU is a color. Authored
rows only. The decoys are real weekend bags whose title or description holds a word that fools a
search (a red lining, a wash bag that comes with it, a leather look that is not leather).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK, BLUE, BURGUNDY, EXEMPT, FENMOOR, GREEN, NAVY, OWNED, RED, SKERRY, TAN, WHITE, WRENFIELD,
    YELLOW, a, count, litres, luggage_row,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Weekend Bag", "Weekend Bags"


def _row(code, title, brand, price, desc, colors, material, rooms, sleeve, litre, **kw):
    attrs = (a("material", "Material", material), count("compartments", "Compartments", rooms),
             a("trolley_sleeve", "Trolley sleeve", "Yes" if sleeve else "No"), litres("capacity", "Capacity", litre))  # fmt: skip
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "weekend_bag", attrs, (),
                       (("compartments", str(rooms)), ("sleeve", "yes" if sleeve else "no")), **kw)  # fmt: skip


_ROWS = (
    _row("WKBCNV", "Canvas Weekend Bag", SKERRY, 34.0,
         "A roomy canvas weekend bag with two top handles, a zip and a cotton lining, big enough "
         "for two nights away.", (GREEN, BLUE, WHITE), "Canvas", 1, False, 35),
    _row("WKBLTH", "Leather-Look Weekend Bag", FENMOOR, 49.0,
         "A smart weekend bag in polyurethane with a leather finish, a zipped end pocket and "
         "a detachable shoulder strap.", (BLACK, TAN, BURGUNDY), "Leather-Look", 2, False, 40),
    _row("WKBNYL", "Nylon Weekend Bag with Trolley Sleeve", WRENFIELD, 39.0,
         "A light nylon weekend bag with a trolley sleeve that slides over a suitcase handle, two "
         "end pockets and a shoulder strap.", (RED, YELLOW, NAVY), "Nylon", 3, True, 45),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, material, brand):
    return Decoy(cls, query, policy, _row(code, title, brand, 36.0, desc, (color,), material, 1, False, 38))


SPEC = TypeSpec(
    key="weekend_bag",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red weekend bag", "color", "WKBDRD", "Weekend Bag, Red Lining",
               "A navy canvas weekend bag with a bright red lining and red handles.", NAVY, "Canvas", SKERRY),
        _decoy(6, "wash bag", "category", "WKBDWB", "Weekend Bag with Wash Bag",
               "A black canvas weekend bag sold with a small wash bag clipped inside; the bag itself "
               "is a duffel.", BLACK, "Canvas", FENMOOR),
        _decoy(4, "leather weekend bag", "generic", "WKBDLK", "Faux Leather Weekend Bag",
               "A weekend bag in faux leather with a zip top; no leather is used.", TAN,
               "Faux Leather", WRENFIELD),
    ),
)  # fmt: skip
