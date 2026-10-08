"""The industrial brands' marks: fifteen machine-shop motifs, each in three enclosures.

A brand's mark is a function of the brand alone (synthetic-ecommerce-data#132):
the brand book declares its ``motif`` and ``enclosure``
(:data:`...core.brands.BRAND_BOOK`), :func:`mark_of` builds it from the shapes
below with the shared core's :func:`...core.drawing.brand_mark.enclose`, and
the sheet sets it beside the brand's name in the plate under the figure
(:mod:`...core.drawing.sheet`).

THE DISTINGUISHABILITY RULE (#55, made a test in
``tests/test_brand_marks.py``): any two brands' marks, rasterised at
:data:`TILE_MARK_PX` -- the size the Studio grid tile shows them -- differ in
at least :data:`MIN_DIFFERING_PIXELS` pixels. Fifteen motifs in three
enclosures give 45 marks, one per brand; a new brand needs a new motif that
passes the same test, which buys room for three.

Every motif is drawn in the unit box (-1 to 1, y down) from a few bold
shapes: at 19 px across, a hairline or a small gap does not survive.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing.brand_mark import (
    Disc,
    Mark,
    Poly,
    Ring,
    Stroke,
    enclose,
    regular,
    star,
)

#: The mark's side at the Studio grid tile, in pixels: the sheet's 32-unit
#: mark (:data:`...core.drawing.sheet.PLATE_MARK`) at the tile's 0.6 px a unit
#: (180 px for the sheet's 300 units) is 19.2 px, rounded down to whole pixels.
TILE_MARK_PX = 19
#: The fewest pixels, of the :data:`TILE_MARK_PX` square, in which any two
#: brands' marks may differ. The closest pair measured 25 (arrow in a ring
#: against twin discs in a ring); ``test_any_two_brands_marks_differ_visibly``
#: names the closest pair when it fails.
MIN_DIFFERING_PIXELS = 24


def _gear() -> Mark:
    teeth = []
    for k in range(8):
        a0 = k * 45 - 9
        for r, a in ((1.0, a0), (1.0, a0 + 18), (0.72, a0 + 27), (0.72, a0 + 36)):
            teeth.extend(regular(1, r, a))
    return (Poly(tuple(teeth)), Disc(0, 0, 0.32, cut=True))


MOTIFS: dict[str, Mark] = {
    "gear": _gear(),
    "hex_nut": (Poly(regular(6, 1.0, 0)), Disc(0, 0, 0.45, cut=True)),
    "bolt_circle": tuple(Disc(*p, 0.26) for p in regular(6, 0.72)) + (Disc(0, 0, 0.3),),
    "chevrons": (
        Stroke(((-0.75, -0.15), (0, -0.75), (0.75, -0.15)), 0.32),
        Stroke(((-0.75, 0.6), (0, 0), (0.75, 0.6)), 0.32),
    ),
    "crosshair": (
        Ring(0, 0, 0.6, 0.22),
        Stroke(((0, -1), (0, 1)), 0.2),
        Stroke(((-1, 0), (1, 0)), 0.2),
    ),
    "torx": (Poly(star(6, 1.0, 0.62)), Disc(0, 0, 0.3, cut=True)),
    "ibeam": (
        Poly(((-0.85, -0.9), (0.85, -0.9), (0.85, -0.55), (0.22, -0.55), (0.22, 0.55),
              (0.85, 0.55), (0.85, 0.9), (-0.85, 0.9), (-0.85, 0.55), (-0.22, 0.55),
              (-0.22, -0.55), (-0.85, -0.55))),
    ),  # fmt: skip
    "arrow": (
        Poly(((-0.95, -0.28), (0.1, -0.28), (0.1, -0.8), (0.95, 0), (0.1, 0.8), (0.1, 0.28),
              (-0.95, 0.28))),
    ),  # fmt: skip
    "delta": (Poly(regular(3, 1.0, -90, cy=0.15)), Poly(regular(3, 0.42, 90, cy=0.15), cut=True)),
    "twin_discs": (Disc(-0.5, 0, 0.45), Disc(0.5, 0, 0.45)),
    "spark": (Poly(star(4, 1.0, 0.28)),),
    "slant_bars": tuple(
        Poly(((x - 0.2, 0.85), (x + 0.3, -0.85), (x + 0.62, -0.85), (x + 0.12, 0.85)))
        for x in (-0.95, -0.3, 0.35)
    ),
    "plus": (
        Poly(((-0.3, -0.95), (0.3, -0.95), (0.3, -0.3), (0.95, -0.3), (0.95, 0.3), (0.3, 0.3),
              (0.3, 0.95), (-0.3, 0.95), (-0.3, 0.3), (-0.95, 0.3), (-0.95, -0.3), (-0.3, -0.3))),
    ),  # fmt: skip
    "checker": (
        Poly(((-0.9, -0.9), (0, -0.9), (0, 0), (-0.9, 0))),
        Poly(((0, 0), (0.9, 0), (0.9, 0.9), (0, 0.9))),
    ),
    "speed_bars": tuple(
        Poly(((-0.9 + s, y - 0.17), (0.9, y - 0.17), (0.9, y + 0.17), (-0.9 + s, y + 0.17)))
        for s, y in ((0, -0.62), (0.45, 0), (0.9, 0.62))
    ),
}


def mark_of(brand: str) -> Mark:
    """``brand``'s mark: its declared motif in its declared enclosure."""
    return enclose(MOTIFS[brands.motif_of(brand)], brands.enclosure_of(brand))
