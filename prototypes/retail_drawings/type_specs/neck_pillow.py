"""Neck Pillow (gen#209): memory foam, microbead and inflatable travel pillows.

**Womens > Accessories > Travel > Neck Pillows**: three styles from three invented brands, drawn
by :func:`kit_luggage.neck_pillow` (``hood``). The fill, the cover and the hood are structured
entries, so ``memory foam neck pillow`` reads the fill. A SKU is a color. Authored rows only. The
decoys are real neck pillows whose title or description holds a word that fools a search (red
piping, a suitcase strap, a fill that only feels like memory foam).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from luggage_common import (
    BLACK, BLUE, EXEMPT, FENMOOR, GREEN, GREY, NAVY, OWNED, PELLBROOK, RED, SKERRY, WHITE, WRENFIELD,
    YELLOW, a, luggage_row,
)  # fmt: skip
from type_registry import Decoy, TypeSpec

PT, LEAF = "Neck Pillow", "Neck Pillows"


def _row(code, title, brand, price, desc, colors, fill, cover, hood, **kw):
    attrs = (a("fill", "Fill", fill), a("cover", "Cover", cover), a("hood", "Hood", "Yes" if hood else "No"))
    return luggage_row(code, title, brand, price, desc, colors, PT, LEAF, "neck_pillow", attrs, (),
                       (("hood", "yes" if hood else "no"),), **kw)  # fmt: skip


_ROWS = (
    _row("NCKMEM", "Memory Foam Neck Pillow", PELLBROOK, 14.0,
         "A contoured memory foam neck pillow with a soft velour cover that unzips to wash, and a "
         "clip to hold it on a bag.", (GREY, BLACK, BLUE), "Memory Foam", "Velour", False),
    _row("NCKMIC", "Microbead Neck Pillow with Hood", FENMOOR, 12.0,
         "A squashy microbead neck pillow with a hood that pulls up for sleep on long flights.",
         (GREEN, YELLOW, RED), "Microbead", "Cotton", True),
    _row("NCKINF", "Inflatable Neck Pillow", SKERRY, 7.0,
         "A neck pillow that inflates in a few breaths and packs flat into a pouch, with a soft "
         "flocked cover.", (WHITE, BLUE, NAVY), "Inflatable", "Flocked", False),
)  # fmt: skip


def _decoy(cls, query, policy, code, title, desc, color, fill, cover, brand):
    return Decoy(cls, query, policy, _row(code, title, brand, 10.0, desc, (color,), fill, cover, False))


SPEC = TypeSpec(
    key="neck_pillow",
    department="Clothing",
    product_type=PT,
    rows=_ROWS,
    owners=OWNED,
    apparel_exempt=EXEMPT,
    decoys=(
        _decoy(1, "red neck pillow", "color", "NCKDRD", "Neck Pillow, Red Piping",
               "A grey microbead neck pillow with red piping round the seam.", GREY, "Microbead",
               "Cotton", FENMOOR),
        _decoy(6, "suitcase", "category", "NCKDSU", "Neck Pillow with Suitcase Strap",
               "A neck pillow with an elastic strap that slips over a suitcase handle; it is a "
               "pillow, not a case.", BLACK, "Memory Foam", "Velour", WRENFIELD),
        _decoy(4, "memory foam neck pillow", "generic", "NCKDLK", "Soft Touch Neck Pillow",
               "A polyester filled neck pillow that feels like memory foam; it has no memory foam "
               "in it.", NAVY, "Polyester", "Velour", PELLBROOK),
    ),
)  # fmt: skip
