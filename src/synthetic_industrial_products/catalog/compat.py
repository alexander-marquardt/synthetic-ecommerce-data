"""Which products fit which: the cross-references a real catalog's copy carries.

A distributor's hex key says which cap screws it drives, a tap says which
drill makes its hole, a nut says which bolts it fits. Those sentences are what
make a search ambiguous the way a real one is: ``m12 socket cap screws``
text-matches keys, taps and nuts as well as screws, and the facets are what
separate them. Without them every size query narrowed to one product type on
its words alone, and the facets had nothing to do.

So each sentence here is a FACT, read from a table in this module or from the
extracted fastener standards, about the record's own PUBLISHED value -- and it
is written only when that value is exactly a table entry. A value the table
does not have (a 1.5mm key: the extracted ISO 4762 rows start at M3) gets no
sentence rather than an approximate one; a value a modelled defect has
republished in the other unit does not snap to the table and gets none either.

The sentences are TEXT only. They are never published as the other product's
attributes -- a hex key does not acquire a ``Dia./Thread Size`` -- so a text
match brings the key into a screw query and the facets take it out again.

Every table is checked against its own rule and against every sentence in the
catalog by ``tests/test_compatibility_text.py``.
"""

from __future__ import annotations

from fractions import Fraction
from functools import cache

from ..dimensions import DimensionParseError, parse_length
from . import standards
from .standards import MM_PER_INCH

# --- hex key sizes -------------------------------------------------------------

#: The metric hexagon key series (ISO 2936), in millimetres. A socket's
#: published across-flats in the extracted ISO 4762 rows is a toleranced
#: figure (10.07 for the M12 socket); the key that drives it is the nominal
#: member of this series. The keys under 1.5mm drive the smallest set screw
#: sockets this catalog carries (ISO 4026-4029, M1.6-M2.5).
KEY_SERIES_MM: tuple[float, ...] = (
    0.7, 0.9, 1.3, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 10.0, 12.0, 14.0, 17.0, 19.0, 22.0,
)  # fmt: skip

#: The inch hexagon key series (ASME B18.3), in inches. The keys under 0.050"
#: drive the smallest set screw sockets this catalog carries (#0-#2).
KEY_SERIES_IN: tuple[float, ...] = tuple(
    float(f)
    for f in (
        Fraction(28, 1000), Fraction(35, 1000),
        Fraction(50, 1000), Fraction(1, 16), Fraction(5, 64), Fraction(3, 32),
        Fraction(7, 64), Fraction(1, 8), Fraction(9, 64), Fraction(5, 32),
        Fraction(3, 16), Fraction(7, 32), Fraction(1, 4), Fraction(5, 16),
        Fraction(3, 8), Fraction(7, 16), Fraction(1, 2), Fraction(9, 16),
        Fraction(5, 8),
    )
)  # fmt: skip

#: How far a socket's toleranced across-flats may sit from its nominal key.
#: Measured over the extracted rows: the largest metric offset is 0.10mm (the
#: M20 socket head's 17.10), the largest inch one 0.0010" (0.1880 for 3/16).
_KEY_TOLERANCE_MM = 0.2
_KEY_TOLERANCE_IN = 0.002


def nominal_key_in(drive_in: float, metric: bool) -> float:
    """The nominal hex key, in inches, that drives a socket of ``drive_in`` across flats.

    Raises ``ValueError`` when no key of the series is within tolerance: a
    socket no standard key fits is a data error, not something to round.
    """
    if metric:
        mm = drive_in * MM_PER_INCH
        key = min(KEY_SERIES_MM, key=lambda k: abs(k - mm))
        if abs(key - mm) > _KEY_TOLERANCE_MM:
            raise ValueError(f"no ISO 2936 key within {_KEY_TOLERANCE_MM}mm of {mm:.3f}mm")
        return key / MM_PER_INCH
    key = min(KEY_SERIES_IN, key=lambda k: abs(k - drive_in))
    if abs(key - drive_in) > _KEY_TOLERANCE_IN:
        raise ValueError(f'no ASME B18.3 key within {_KEY_TOLERANCE_IN}" of {drive_in:.4f}"')
    return key


@cache
def socket_head_keys() -> dict[str, tuple[float, str]]:
    """Socket head cap screw diameter -> (nominal key in inches, standard).

    Read from the extracted ISO 4762 and ASME B18.3 rows -- the key-to-screw
    table a distributor prints beside its hex keys.
    """
    table: dict[str, tuple[float, str]] = {}
    for standard, metric in (("ISO 4762", True), ("ASME B18.3", False)):
        for size in standards.available_sizes(standard):
            head = standards.socket_head(standard, size)
            assert head.drive_size_in is not None
            table[size] = (nominal_key_in(head.drive_size_in, metric), standard)
    return table


# --- threads -------------------------------------------------------------------

#: ISO 262's selected FINE pitches, by diameter, for the sizes the extracted
#: standards carry. Coarse is each standard's own row; these are the near-miss
#: alternatives a shopper typing ``m12 socket cap screws`` has to choose among.
METRIC_FINE_PITCHES: dict[str, tuple[float, ...]] = {
    "M8": (1.0,),
    "M10": (1.25, 1.0),
    "M12": (1.5, 1.25),
    "M16": (1.5,),
    "M20": (1.5, 2.0),
}

#: Metric tap drills (mm), for a 6H internal thread, as the metric tap-drill
#: chart prints them: the nominal diameter less the pitch, taken to the stocked
#: tenth of a millimetre (M8x1.25's 6.75 is drilled 6.8, M12x1.75's 10.25 is
#: drilled 10.2). Written out rather than computed so the sentence cites a
#: table; ``test_compatibility_text`` checks every row is within 0.05mm of D-P.
TAP_DRILLS_METRIC: dict[str, float] = {
    "M3x0.5": 2.5,
    "M4x0.7": 3.3,
    "M5x0.8": 4.2,
    "M6x1": 5.0,
    "M8x1.25": 6.8,
    "M8x1": 7.0,
    "M10x1.5": 8.5,
    "M10x1.25": 8.8,
    "M10x1": 9.0,
    "M12x1.75": 10.2,
    "M12x1.5": 10.5,
    "M12x1.25": 10.8,
    "M16x2": 14.0,
    "M16x1.5": 14.5,
    "M20x2.5": 17.5,
    "M20x2": 18.0,
    "M20x1.5": 18.5,
}

#: Unified tap drills for 75% thread engagement -- the chart every machinist's
#: reference prints (Machinery's Handbook, "Tap Drill Sizes"). The drill is
#: named as the chart names it: a number, a letter or a fraction; the decimal
#: is the drill's own size.
TAP_DRILLS_INCH: dict[str, tuple[str, float]] = {
    "#6-32": ("#36", 0.1065),
    "#8-32": ("#29", 0.1360),
    "#10-24": ("#25", 0.1495),
    "#10-32": ("#21", 0.1590),
    "1/4-20": ("#7", 0.2010),
    "1/4-28": ("#3", 0.2130),
    "5/16-18": ("F", 0.2570),
    "5/16-24": ("I", 0.2720),
    "3/8-16": ('5/16"', 0.3125),
    "3/8-24": ("Q", 0.3320),
    "7/16-14": ("U", 0.3680),
    "7/16-20": ('25/64"', 0.390625),
    "1/2-13": ('27/64"', 0.421875),
    "1/2-20": ('29/64"', 0.453125),
}


def fine_threads(size: str, metric: bool) -> tuple[str, ...]:
    """The fine-pitch designations of one diameter: ``M12x1.5``, ``1/4-28``."""
    if metric:
        return tuple(f"{size}x{p:g}" for p in METRIC_FINE_PITCHES.get(size, ()))
    tpi = standards.UNF_THREADS_PER_INCH.get(size)
    return () if tpi is None else (f"{size}-{tpi}",)


def diameter_of(designation: str) -> str:
    """``M12x1.75`` -> ``M12``; ``5/16-18`` -> ``5/16``; ``#10-32`` -> ``#10``."""
    return designation.split("x")[0] if designation.startswith("M") else designation.split("-")[0]


# --- the sentences -------------------------------------------------------------


def _inches(value: str | None) -> float | None:
    if not value:
        return None
    try:
        return parse_length(value).inches
    except DimensionParseError:
        return None


def _is_mm(value: str) -> bool:
    return value.strip().endswith("mm")


def _key_text(key_in: float, metric: bool) -> str:
    if metric:
        return f"{key_in * MM_PER_INCH:g}mm"
    frac = Fraction(round(key_in * 64), 64)
    return f'{frac}"' if abs(float(frac) - key_in) < 1e-9 else f'{key_in:.3f}"'


def _diameter_text(size: str) -> str:
    return size if size.startswith(("M", "#")) else f'{size}"'


def _join(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def _published_key(value: str | None) -> tuple[float, bool] | None:
    """A published key or drive size, snapped to its series -- or None if it is off it."""
    size_in = _inches(value)
    if size_in is None or value is None:
        return None
    metric = _is_mm(value)
    try:
        key = nominal_key_in(size_in, metric)
    except ValueError:
        return None
    # The published value has to BE the nominal key, not merely near one: a
    # toleranced socket figure is a drive size, not a key size.
    return (key, metric) if abs(key - size_in) < 1e-4 else None


def hex_key_sentence(size: str | None) -> str | None:
    """``For M12 socket head cap screws (ISO 4762).`` -- from the key-to-screw table."""
    key = _published_key(size)
    if key is None:
        return None
    key_in, metric = key
    fits = [
        (screw, standard)
        for screw, (k, standard) in socket_head_keys().items()
        if abs(k - key_in) < 1e-6 and (standard == "ISO 4762") == metric
    ]
    if not fits:
        return None
    standard = fits[0][1]
    return f"For {_join([_diameter_text(s) for s, _ in fits])} socket head cap screws ({standard})."


def drive_sentence(drive: str | None) -> str | None:
    """``Takes a 10mm hex key.`` -- from the screw's own published drive size."""
    key = _published_key(drive)
    if key is None:
        return None
    return f"Takes a {_key_text(*key)} hex key."


def tap_sentence(thread: str | None) -> str | None:
    """``For M12x1.75 threads; tap drill 10.2mm.``"""
    if not thread:
        return None
    if thread in TAP_DRILLS_METRIC:
        return f"For {thread} threads; tap drill {TAP_DRILLS_METRIC[thread]:g}mm."
    if thread in TAP_DRILLS_INCH:
        return f"For {thread} threads; tap drill {TAP_DRILLS_INCH[thread][0]}."
    return f"For {thread} threads."


def drill_sentence(size: str | None) -> str | None:
    """``Tap drill for M12x1.75 threads.`` -- only when the drill IS a chart entry."""
    size_in = _inches(size)
    if size_in is None or size is None:
        return None
    if _is_mm(size):
        mm = size_in * MM_PER_INCH
        threads = [t for t, d in TAP_DRILLS_METRIC.items() if abs(d - mm) < 1e-6]
    else:
        threads = [t for t, (_, d) in TAP_DRILLS_INCH.items() if abs(d - size_in) < 1e-6]
    return f"Tap drill for {_join(threads)} threads." if threads else None


def nut_sentence(thread: str | None) -> str | None:
    """``Fits M12x1.75 bolts and screws.`` -- a nut fits its own thread."""
    return f"Fits {thread} bolts and screws." if thread else None


def washer_sentence(size: str | None) -> str | None:
    """``For M12 bolts and screws.`` -- an ISO 7089 washer is sized by thread diameter."""
    if not size or size not in standards.available_sizes("ISO 7089"):
        return None
    return f"For {size} bolts and screws."


SOCKET_SCREWS = frozenset(
    ("screw_socket_head", "screw_flat_head", "screw_button_head", "screw_low_head")
)


def sentence_for(type_key: str, published: dict[str, str]) -> str | None:
    """The one cross-reference sentence a record of ``type_key`` carries, if any."""
    if type_key == "hex_key":
        return hex_key_sentence(published.get("Size"))
    if type_key in SOCKET_SCREWS:
        return drive_sentence(published.get("Drive Size"))
    if type_key == "tap_spiral_point":
        return tap_sentence(published.get("Thread Size"))
    if type_key == "drill_jobber":
        return drill_sentence(published.get("Size"))
    if type_key == "nut_hex":
        return nut_sentence(published.get("Thread Size"))
    if type_key == "washer_flat":
        return washer_sentence(published.get("Size"))
    return None
