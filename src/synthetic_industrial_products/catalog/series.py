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
#: 20 offers 25. Their absence made three of the reference distributor's twelve end-mill
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


#: The largest an oversize shank gets, as a multiple of its cutter. 43 of the
#: 46 differing records in 04_shank_dia_vs_milling_dia.json are at or under
#: 3.0, the 2.667 and 3.0 ratios included, so an inch 5/32" cutter on a 5/8"
#: shank (4.0) is not drawn. Two exceptions draw past it: the smallest stocked
#: shank above the cutter when that is already more (see shank_ceiling), and a
#: metric cutter below SMALL_METRIC_SHANK_MM, which sits on 6 mm whatever the
#: ratio -- 1.5 mm on 6 mm is 4.0x and 1 mm on 6 mm is 6.0x.
MAX_SHANK_RATIO = 3.0

#: The shank a metric cutter below it sits on when its shank is oversize.
#: This is a catalog convention the #33 review proposed, not yet confirmed
#: against a standard's diameter table (#87); DIN 6535 also lists 3, 4
#: and 5 mm shanks, which this rule leaves undrawn for an oversize cutter.
SMALL_METRIC_SHANK_MM = 6.0


def shank_ceiling(dia: float, larger: list[float]) -> float:
    """The largest shank a cutter of ``dia`` may carry, given the stocked
    shanks ``larger`` than it: three times the cutter, or the smallest of
    those shanks when that is already more."""
    return max(dia * MAX_SHANK_RATIO, min(larger))


def larger_shank_imperial(dia_in: float, target_in: float) -> Fraction:
    """A reduced/oversize shank that is NOT smaller than the cutting diameter
    and not above :func:`shank_ceiling`: the stocked shank nearest
    ``target_in`` among those, or the cutting diameter's own size when no
    larger shank is stocked. A shank thinner than the flutes it carries is not
    an end mill a maker sells, and neither is one four times the cutter."""
    larger = [s for s in IMPERIAL_SHANKS if float(s) > dia_in + 1e-9]
    if not larger:
        # Above the largest stocked shank (a 1-1/4" or 1-1/2" cutter), the
        # shank is the cutter's own size.
        return Fraction(dia_in).limit_denominator(64)
    ceiling = shank_ceiling(dia_in, [float(s) for s in larger])
    allowed = [s for s in larger if float(s) <= ceiling + 1e-9]
    return min(allowed, key=lambda s: abs(float(s) - target_in))


def larger_shank_metric(dia_mm: float, target_mm: float) -> float:
    """The metric twin of :func:`larger_shank_imperial`, except that a cutter
    below :data:`SMALL_METRIC_SHANK_MM` sits on that shank."""
    larger = [s for s in METRIC_SHANKS if s > dia_mm + 1e-9]
    if not larger:
        return dia_mm
    if dia_mm < SMALL_METRIC_SHANK_MM - 1e-9:
        return SMALL_METRIC_SHANK_MM
    ceiling = shank_ceiling(dia_mm, larger)
    allowed = [s for s in larger if s <= ceiling + 1e-9]
    return min(allowed, key=lambda s: abs(s - target_mm))


#: Jobber drill sizes, as exact inch fractions: the fractional drill series,
#: 1/16" to 1/2" in its own 1/64 progression. (It used to step by 1/32, which
#: left out 25/64, 27/64 and 29/64 -- the tap drills of 7/16-20, 1/2-13 and
#: 1/2-20, and every odd sixty-fourth a distributor stocks.)
DRILL_FRACTIONAL: tuple[Fraction, ...] = tuple(Fraction(n, 64) for n in range(4, 33))

#: Metric jobber drill sizes (DIN 338), in millimetres: the half-millimetre
#: series from 1 to 13mm plus the tap-drill sizes a distributor stocks beside
#: it (3.3, 4.2, 6.8, 8.8, 10.2, 10.8) -- the sizes a metric tap-drill chart
#: names, :data:`.compat.TAP_DRILLS_METRIC`.
DRILL_METRIC_MM: tuple[float, ...] = (
    1.0, 1.5, 2.0, 2.5, 3.0, 3.3, 3.5, 4.0, 4.2, 4.5, 5.0, 5.5, 6.0, 6.5, 6.8, 7.0,
    7.5, 8.0, 8.5, 8.8, 9.0, 9.5, 10.0, 10.2, 10.5, 10.8, 11.0, 11.5, 12.0, 12.5, 13.0,
)  # fmt: skip

#: Tap thread sizes offered, paired with their threads-per-inch or pitch, one
#: table per thread series -- a tap line is one series, and its ``Thread Type``
#: says which. (One inch table used to mix the two, so a line whose Thread
#: Type read UNC offered 1/4-28 and #10-32.) The Unified coarse and fine
#: pitches are ASME B1.1's; see standards.py for where those came from.
TAP_SIZES_UNC: tuple[tuple[str, int], ...] = (
    ("#6-32", 32),
    ("#8-32", 32),
    ("#10-24", 24),
    ("1/4-20", 20),
    ("5/16-18", 18),
    ("3/8-16", 16),
    ("7/16-14", 14),
    ("1/2-13", 13),
)
TAP_SIZES_UNF: tuple[tuple[str, int], ...] = (
    ("#10-32", 32),
    ("1/4-28", 28),
    ("5/16-24", 24),
    ("3/8-24", 24),
    ("7/16-20", 20),
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
#: ISO 262's selected fine pitches over the same diameters
#: (:data:`.compat.METRIC_FINE_PITCHES`).
TAP_SIZES_METRIC_FINE: tuple[tuple[str, float], ...] = (
    ("M8x1", 1.0),
    ("M10x1.25", 1.25),
    ("M10x1", 1.0),
    ("M12x1.5", 1.5),
    ("M12x1.25", 1.25),
)

#: Ball pein hammer head weights, in ounces -- the sizes actually sold.
#: The head weights ball pein hammers are sold in. 2, 6, 10 and 20 oz were
#: added for the 100K catalog's headroom; each is a size makers list.
HAMMER_HEAD_OUNCES: tuple[int, ...] = (2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 40, 48)

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
