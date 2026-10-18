"""Holdall (gen#209): soft gym and travel holdalls, with and without wheels.

**Womens > Accessories > Travel > Holdalls**: three styles from three invented brands, drawn by
:func:`kit_luggage.holdall` (``wheels``, ``strap``). The use (gym or travel), the material, the
shoulder strap and the wheels are structured entries; a SKU is a color times a capacity in
litres. Authored rows only. The decoys are real holdalls whose title or description holds a word
that fools a search (red handles, the word suitcase, a leather look that is not leather).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK,
    BLUE,
    EXEMPT,
    FENMOOR,
    GREEN,
    KHAKI,
    MARROWGATE,
    NAVY,
    OWNED,
    PELLBROOK,
    RED,
    TARNWICK,
    WHITE,
    YELLOW,
    a,
    luggage_row,
    num,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Holdall", "Holdalls"


def _row(code, title, brand, price, desc, colors, use, material, wheels, caps, **kw):
    attrs = (a("use", "Use", use), a("material", "Material", material), a("shoulder_strap", "Shoulder strap", "Yes"),
             a("wheels", "Wheels", "2 Wheel" if wheels == "yes" else "No Wheels"))  # fmt: skip
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "holdall", attrs, num(*caps),
                       (("wheels", wheels), ("strap", "yes")), **kw)  # fmt: skip


_ROWS = (
    _row("HLDGYM", "Gym Holdall with Shoe Compartment", MARROWGATE, 22.0,
         "A padded gym holdall with a ventilated shoe compartment, a wet pocket and a shoulder "
         "strap. Two zipped end pockets for a towel and a water bottle.",
         (BLACK, RED, BLUE), "Gym", "Polyester", "no", ((30, 22.0), (45, 28.0))),
    _row("HLDWHL", "Wheeled Travel Holdall", TARNWICK, 46.0,
         "A large soft holdall on two wheels with a telescopic handle, a shoulder strap and "
         "a zipped lid pocket. Packs away flat when empty.",
         (NAVY, GREEN, YELLOW), "Travel", "Polyester", "yes", ((60, 46.0), (85, 56.0))),
    _row("HLDCNV", "Canvas Holdall with Shoulder Strap", PELLBROOK, 38.0,
         "A hardwearing canvas holdall with leather-look handles, a detachable shoulder strap and "
         "a lined main compartment.",
         (KHAKI, WHITE, BLACK), "Travel", "Canvas", "no", ((40, 38.0), (60, 46.0))),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, material, brand, wheels="no"):
    return Decoy(cls, query, policy, _row(code, title, brand, 30.0, desc, (color,), "Travel", material, wheels, ((40, 30.0), (55, 36.0))))


SPEC = TypeSpec(
    key="holdall",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red holdall", "color", "HLDDRD", "Holdall with Red Handles",
               "A black polyester holdall with red handles and a red zip pull.", BLACK, "Polyester", MARROWGATE),
        _decoy(6, "wheeled suitcase", "category", "HLDDSU", "Suitcase Style Wheeled Holdall",
               "A soft holdall that packs like a suitcase, with a telescopic handle; it has no hard "
               "shell and is a holdall.", GREEN, "Polyester", FENMOOR, "yes"),
        _decoy(4, "leather holdall", "generic", "HLDDLK", "Leather-Look Holdall",
               "A smart holdall in polyurethane with a leather finish; there is no leather in it.",
               NAVY, "Polyurethane", PELLBROOK),
    ),
)  # fmt: skip
