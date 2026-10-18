"""Travel Organizer (gen#209): packing cubes, passport holders, toiletry rolls and adapter cases.

**Womens > Accessories > Travel > Travel Organizers**: four styles from four invented brands, one
for each kind, drawn by :func:`kit_luggage.travel_organizer` (``kind``). The organizer type, the
pieces in the pack and the material are structured entries; a SKU is a color. Authored rows only.
The decoys are real organizers whose title or description holds a word that fools a search: a
packing cube set titled for the suitcase it fits, a red lining, a leather finish that is not
leather.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK,
    BLUE,
    EXEMPT,
    FENMOOR,
    GREEN,
    GREY,
    MARROWGATE,
    NAVY,
    OWNED,
    PELLBROOK,
    RED,
    SKERRY,
    TAN,
    TARNWICK,
    WHITE,
    YELLOW,
    a,
    count,
    luggage_row,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Travel Organizer", "Travel Organizers"
KINDS = {"Packing Cubes": "packing cubes", "Passport Holder": "passport holder",
         "Toiletry Roll": "toiletry roll", "Adapter Case": "adapter case"}  # fmt: skip


def _row(code, title, brand, price, desc, colors, kind, pieces, material, **kw):
    attrs = (a("organizer_type", "Organizer type", kind), count("piece_count", "Piece count", pieces),
             a("material", "Material", material))  # fmt: skip
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "travel_organizer", attrs, (),
                       (("kind", KINDS[kind]),), **kw)  # fmt: skip


_ROWS = (
    _row("TRVCUB", "Packing Cubes, Set of 4", TARNWICK, 16.0,
         "Four zipped packing cubes in small, medium, large and a flat shoe size, with a mesh "
         "panel to see inside. Compresses a week of clothes.",
         (RED, BLUE, GREEN, YELLOW), "Packing Cubes", 4, "Nylon"),
    _row("TRVPSP", "Passport Holder with Card Slots", MARROWGATE, 12.0,
         "A slim passport holder with a boarding pass pocket, four card slots and a pen loop. "
         "Blocks card skimming.", (BLACK, WHITE, TAN), "Passport Holder", 1, "Polyurethane"),
    _row("TRVTLR", "Hanging Toiletry Roll", SKERRY, 14.0,
         "A toiletry roll that unrolls and hangs on a hook, with three zipped pockets and a "
         "wipe-clean lining.", (NAVY, YELLOW, BLUE), "Toiletry Roll", 1, "Polyester"),
    _row("TRVADP", "Travel Adapter Case", FENMOOR, 9.0,
         "A hard-lined zip case that holds a plug adapter, a charger and cables, with a "
         "mesh divider.", (BLACK, GREY, WHITE), "Adapter Case", 1, "Polyester"),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, kind, pieces, material, brand):
    return Decoy(cls, query, policy, _row(code, title, brand, 15.0, desc, (color,), kind, pieces, material))


SPEC = TypeSpec(
    key="travel_organizer",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red passport holder", "color", "TRVDRD", "Passport Holder, Red Lining",
               "A black passport holder with a bright red lining and a red zip pull.", BLACK,
               "Passport Holder", 1, "Polyurethane", MARROWGATE),
        _decoy(6, "suitcase", "category", "TRVDSU", "Suitcase Packing Cubes, Set of 3",
               "Three packing cubes cut to fit a medium suitcase; the cubes pack inside the case "
               "and are not a case.", NAVY, "Packing Cubes", 3, "Nylon", PELLBROOK),
        _decoy(4, "leather passport holder", "generic", "TRVDLK", "Faux Leather Passport Holder",
               "A passport holder in faux leather with two card slots; no leather is used.", TAN,
               "Passport Holder", 1, "Faux Leather", SKERRY),
    ),
)  # fmt: skip
