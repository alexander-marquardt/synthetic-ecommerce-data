"""Conventional tool series, and the geometry rules that relate them.

**These values are generated, not standards-derived.** There is no open
dimensional source for end mills the way there is for fasteners, so what this
module encodes is the conventional series a tool catalog offers -- the shank
diameters that fit a standard collet, the flute counts that exist, the
length-of-cut multiples a stub / regular / long tool is built to -- and the
rule that relates them. No product generated from this module carries a
standard designation as the provenance of its dimensions, because none of
these numbers came from one. Fasteners are the opposite case and are handled
in :mod:`.standards`.

The geometry rule matters more than the individual numbers. Sampling cutting
diameter, length of cut, overall length and shank diameter independently
produces tools that cannot exist -- a 1/8" cutter with a 4" length of cut on a
2" body. The reference statistics say so outright
(:file:`02_joint_combinations.json`: *"A generator MUST sample whole tuples
[...]; sampling the four fields independently produces geometrically
impossible tools"*). This module therefore derives the whole tuple from one
choice of cutting diameter plus a length class, so the four fields are
coherent by construction rather than by luck.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

MM_PER_INCH = 25.4

#: Imperial cutting diameters, as exact fractions of an inch.
IMPERIAL_CUTTING_DIAS: tuple[Fraction, ...] = (
    Fraction(1, 16),
    Fraction(3, 32),
    Fraction(1, 8),
    Fraction(5, 32),
    Fraction(3, 16),
    Fraction(7, 32),
    Fraction(1, 4),
    Fraction(9, 32),
    Fraction(5, 16),
    Fraction(3, 8),
    Fraction(7, 16),
    Fraction(1, 2),
    Fraction(5, 8),
    Fraction(3, 4),
    Fraction(7, 8),
    Fraction(1, 1),
    Fraction(5, 4),
    Fraction(3, 2),
)

#: Imperial shank diameters. A shank must fit a holder, so the offered set is
#: much coarser than the cutting-diameter set.
IMPERIAL_SHANKS: tuple[Fraction, ...] = (
    Fraction(1, 8),
    Fraction(3, 16),
    Fraction(1, 4),
    Fraction(5, 16),
    Fraction(3, 8),
    Fraction(1, 2),
    Fraction(5, 8),
    Fraction(3, 4),
    Fraction(1, 1),
)

#: Metric cutting diameters, in millimetres.
#:
#: 11, 15 and 25 are ordinary stocked sizes and were missing, which is an
#: artifact of how this list was first written rather than a statement about
#: the market: a catalog that offers 10 and 12 offers 11, and one that offers
#: 20 offers 25. Their absence made three of the customer's twelve end-mill
#: patterns unanswerable -- ``11 mm end mills``, ``15 mm ball end mills`` and
#: ``25mm end mill``, the last of which is the demo's own headline case.
#:
#: 11 and 15 are deliberately NOT added to :data:`METRIC_SHANKS`. A shank has
#: to fit a holder and the collet series really does stop at the round even
#: sizes, so an 11 mm cutter is a reduced- or oversize-shank tool. 25 already
#: is an offered shank, so a 25 mm cutter can be either.
METRIC_CUTTING_DIAS: tuple[float, ...] = (
    1.0,
    1.5,
    2.0,
    2.5,
    3.0,
    4.0,
    5.0,
    6.0,
    8.0,
    10.0,
    11.0,
    12.0,
    15.0,
    16.0,
    20.0,
    25.0,
)

#: Metric shank diameters, in millimetres. 3.175, 6.35 and 12.7 are 1/8", 1/4"
#: and 1/2" -- inch shanks sold into a metric series, which is exactly how the
#: unit mixing in the reference corpus arises.
METRIC_SHANKS: tuple[float, ...] = (
    3.0,
    3.175,
    4.0,
    6.0,
    6.35,
    8.0,
    10.0,
    12.0,
    12.7,
    16.0,
    20.0,
    25.0,
)

#: Flute counts, with the weights measured in 03_flutes_by_milling_dia.json
#: (marginal distribution over 131 records: 4 -> 55, 2 -> 49, 6 -> 15,
#: 3 -> 10). The two singleton counts there, 5 and 8, are not reproduced.
FLUTE_WEIGHTS: tuple[tuple[int, float], ...] = (
    (4, 0.42),
    (2, 0.375),
    (6, 0.115),
    (3, 0.09),
)

#: Helix angles offered by the conventional series.
HELIX_ANGLES: tuple[float, ...] = (30.0, 35.0, 38.0, 45.0)

#: Length-of-cut classes, as multiples of the cutting diameter.
LENGTH_CLASSES: tuple[tuple[str, float], ...] = (
    ("Stub", 1.5),
    ("Regular", 3.0),
    ("Long", 4.0),
)

#: Ratios of shank to cutting diameter observed when the two differ, from
#: 04_shank_dia_vs_milling_dia.json. Reduced-shank tools (ratio < 1) and
#: oversize-shank tools (ratio > 1) both occur; the oversize case dominates
#: because a small cutter on a standard shank is the common product.
OBSERVED_SHANK_RATIOS: tuple[tuple[float, int], ...] = (
    (0.833, 7),
    (2.0, 6),
    (1.333, 4),
    (1.5, 3),
    (1.2, 3),
    (1.143, 3),
    (3.0, 2),
    (2.667, 2),
    (0.75, 2),
    (1.905, 1),
    (1.587, 1),
    (1.191, 1),
    (1.27, 1),
    (1.155, 1),
    (1.111, 1),
    (1.058, 1),
    (1.026, 1),
    (4.0, 1),
    (0.6, 1),
    (0.429, 1),
    (0.375, 1),
)


class GeometryError(ValueError):
    """The requested tool geometry does not describe a tool that can exist."""


def snap_imperial(inches: float, denominator: int = 16) -> Fraction:
    """Round to the nearest 1/``denominator`` inch, the grid a catalog prints on."""
    return Fraction(round(inches * denominator), denominator)


def snap_metric(mm: float, step: float = 0.5) -> float:
    return round(round(mm / step) * step, 3)


@dataclass(frozen=True)
class ToolGeometry:
    """A coherent (cutting dia, length of cut, overall length, shank) tuple.

    Constructed as a whole, never field by field: ``length_of_cut`` follows
    from the cutting diameter and the length class, and ``overall_length``
    follows from the length of cut and the shank. That is the only way the
    four stay physically consistent.
    """

    system: str  # "in" or "mm"
    cutting_dia_in: float
    length_of_cut_in: float
    overall_length_in: float
    shank_dia_in: float
    length_class: str

    def __post_init__(self) -> None:
        if self.cutting_dia_in <= 0 or self.shank_dia_in <= 0:
            raise GeometryError("a tool has positive diameters")
        if self.length_of_cut_in >= self.overall_length_in:
            raise GeometryError(
                f"length of cut {self.length_of_cut_in} is not shorter than overall length "
                f"{self.overall_length_in}; there would be no shank"
            )

    @property
    def shank_equals_cutting(self) -> bool:
        return abs(self.shank_dia_in - self.cutting_dia_in) < 1e-4


def build_imperial(
    cutting_dia: Fraction, length_class: str, multiple: float, shank: Fraction
) -> ToolGeometry:
    """Derive the whole tuple for an inch tool from its diameter and class."""
    loc = snap_imperial(float(cutting_dia) * multiple, 16)
    if loc <= 0:
        loc = Fraction(1, 16)
    # Body long enough to hold the flutes plus enough shank to clamp. 2.5
    # shank diameters of grip is the conventional minimum, and a tool is never
    # shorter than about 1-1/2".
    oal = snap_imperial(max(float(loc) + 2.5 * float(shank), 1.5), 16)
    if oal <= loc:
        oal = loc + Fraction(1, 2)
    return ToolGeometry(
        system="in",
        cutting_dia_in=float(cutting_dia),
        length_of_cut_in=float(loc),
        overall_length_in=float(oal),
        shank_dia_in=float(shank),
        length_class=length_class,
    )


def build_metric(
    cutting_dia_mm: float, length_class: str, multiple: float, shank_mm: float
) -> ToolGeometry:
    loc_mm = snap_metric(cutting_dia_mm * multiple, 0.5)
    if loc_mm <= 0:
        loc_mm = 0.5
    oal_mm = snap_metric(max(loc_mm + 2.5 * shank_mm, 38.0), 1.0)
    if oal_mm <= loc_mm:
        oal_mm = loc_mm + 10.0
    return ToolGeometry(
        system="mm",
        cutting_dia_in=cutting_dia_mm / MM_PER_INCH,
        length_of_cut_in=loc_mm / MM_PER_INCH,
        overall_length_in=oal_mm / MM_PER_INCH,
        shank_dia_in=shank_mm / MM_PER_INCH,
        length_class=length_class,
    )


def nearest_shank_imperial(target_in: float) -> Fraction:
    """The offered shank closest to ``target_in``."""
    return min(IMPERIAL_SHANKS, key=lambda s: abs(float(s) - target_in))


def nearest_shank_metric(target_mm: float) -> float:
    return min(METRIC_SHANKS, key=lambda s: abs(s - target_mm))


#: Jobber drill sizes, as exact inch fractions. Generated series, not a
#: standard: the fractional drill series is the conventional 1/64 progression.
DRILL_FRACTIONAL: tuple[Fraction, ...] = tuple(
    Fraction(n, 64)
    for n in range(4, 33, 2)  # 1/16" to 1/2" in 1/32 steps
)

#: Tap thread sizes offered, paired with their threads-per-inch or pitch. The
#: inch pitches here are the Unified coarse/fine series; see standards.py for
#: where those came from and under what licence.
TAP_SIZES_INCH: tuple[tuple[str, int], ...] = (
    ("#6-32", 32),
    ("#8-32", 32),
    ("#10-24", 24),
    ("#10-32", 32),
    ("1/4-20", 20),
    ("1/4-28", 28),
    ("5/16-18", 18),
    ("5/16-24", 24),
    ("3/8-16", 16),
    ("3/8-24", 24),
    ("1/2-13", 13),
    ("1/2-20", 20),
)

TAP_SIZES_METRIC: tuple[tuple[str, float], ...] = (
    ("M3x0.5", 0.5),
    ("M4x0.7", 0.7),
    ("M5x0.8", 0.8),
    ("M6x1", 1.0),
    ("M8x1.25", 1.25),
    ("M10x1.5", 1.5),
    ("M12x1.75", 1.75),
)

#: Ball pein hammer head weights, in ounces -- the sizes actually sold.
HAMMER_HEAD_OUNCES: tuple[int, ...] = (4, 8, 12, 16, 24, 32, 40, 48)

#: Flap disc diameters in inches, and the grits offered.
FLAP_DISC_DIAS_IN: tuple[Fraction, ...] = (
    Fraction(9, 2),
    Fraction(5, 1),
    Fraction(11, 2),
    Fraction(7, 1),
)
FLAP_DISC_GRITS: tuple[int, ...] = (36, 40, 60, 80, 100, 120)
#: Arbor hole sizes, in inches.
FLAP_DISC_ARBORS: tuple[Fraction, ...] = (Fraction(5, 8), Fraction(7, 8))
