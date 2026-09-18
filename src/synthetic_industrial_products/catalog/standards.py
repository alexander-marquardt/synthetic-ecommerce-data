"""Fastener dimensions, from published standards rather than from invention.

This is the opposite case to :mod:`.series`. An end mill has no open
dimensional source, so its numbers are generated and claim nothing. A cap
screw does: ``ASME B18.3.2`` fixes the head of a ``#10`` flat head socket cap
screw at 0.411" across and 0.127" high, and any catalog that publishes
anything else is publishing a screw that is not to standard. So the fastener
dimensions here are *extracted*, and every generated fastener carries the
standard designation its dimensions came from.

That is also why the non-copying guarantee is stated over the **full attribute
tuple** and not field by field. A generated ``#10-32`` cap screw shares
``Head Dia. = 0.411 in`` with every real one in the world, including the
reference record ``26LD37`` bundled in :mod:`..records`. That agreement is
what standards compliance *means*; it is not evidence of copying. What would
be copying is reproducing a compilation -- which is what the full-tuple test
in :mod:`.noncopy` actually checks.

Provenance
----------
:file:`../data/fastener_standards.json` is the extraction, unmodified, and
carries its own ``_provenance`` block naming every upstream repository, its
licence and the commit it was read at:

* **FreeCAD FastenersWB** (``GPL-2.0-or-later``) -- the primary source for
  every standard here.
* **BOLTS** (fastener collections, ``LGPL-2.1+``) -- corroboration only, and
  the sole source for DIN 912 because FastenersWB carries no DIN 912 table.
  It was deliberately NOT consulted for ISO 10642 (it conflates that standard
  with DIN 7991) nor for washer inner diameter or thickness (it is wrong at
  M10 and at M42 and above).

The values are dimensions fixed by public standards. Reproducing a handful of
them is reproducing facts about the physical world; the upstream compilations
are not redistributed.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from importlib import resources

from ..dimensions import parse_length

MM_PER_INCH = 25.4

#: Unified fine-thread pitches, transcribed by hand for the sizes this catalog
#: offers. The coarse (UNC) pitches come out of the ASME B18.3 extraction --
#: its derived threads-per-inch lands on 32 / 32 / 24 / 20 / 18 / 16 / 13 / 11
#: across the eight inch sizes, which is the published coarse series exactly --
#: but the FINE series appears in no open dimensional dataset. These few rows
#: are transcribed from the Unified Thread Standard table on Wikipedia
#: (CC BY-SA 4.0); the standard itself is ASME B1.1. Each entry is really just
#: its own designation: "#10-32" states 32 threads per inch in the name.
UNF_THREADS_PER_INCH: dict[str, int] = {
    "#6": 40,
    "#8": 36,
    "#10": 32,
    "1/4": 28,
    "5/16": 24,
    "3/8": 24,
    "7/16": 20,
    "1/2": 20,
    "5/8": 18,
}

#: Nominal major diameter of the inch sizes, in inches. The numbered sizes
#: follow the ANSI rule already encoded in :mod:`..dimensions`
#: (0.060 + 0.013 N); the fractional sizes are their own names.
INCH_MAJOR_DIA: dict[str, float] = {
    "#6": 0.138,
    "#8": 0.164,
    "#10": 0.190,
    "1/4": 0.250,
    "5/16": 0.3125,
    "3/8": 0.375,
    "7/16": 0.4375,
    "1/2": 0.500,
    "5/8": 0.625,
}


class StandardsDataError(KeyError):
    """The standards extraction does not carry the row that was asked for."""


@lru_cache(maxsize=1)
def _load(name: str = "fastener_standards.json") -> dict:
    text = resources.files("synthetic_industrial_products.data").joinpath(name).read_text("utf-8")
    return json.loads(text)


@lru_cache(maxsize=1)
def _load_lengths() -> dict:
    text = (
        resources.files("synthetic_industrial_products.data")
        .joinpath("fastener_offered_lengths.json")
        .read_text("utf-8")
    )
    return json.loads(text)


def provenance() -> dict:
    return _load()["_provenance"]


def rows(standard: str) -> list[dict]:
    """Every extracted row for ``standard``, including the ones marked absent."""
    data = _load()
    if standard not in data:
        raise StandardsDataError(f"no extraction for {standard!r}")
    return list(data[standard]["rows"])


def available_sizes(standard: str) -> tuple[str, ...]:
    """The sizes the source actually carries.

    A size the standard does not define is recorded in the extraction with
    ``present_in_source: false`` rather than filled in -- ASME B18.2.1 hex head
    screws begin at 1/4", so there is no ``#10`` hex bolt and this catalog does
    not invent one.
    """
    return tuple(row["size"] for row in rows(standard) if row.get("present_in_source"))


def row_for(standard: str, size: str) -> dict:
    for row in rows(standard):
        if row["size"] == size:
            if not row.get("present_in_source"):
                raise StandardsDataError(
                    f"{standard} does not define size {size!r}: {row.get('note', '')}"
                )
            return row
    raise StandardsDataError(f"{standard} has no row for size {size!r}")


def offered_lengths_in(standard: str, size: str) -> tuple[float, ...]:
    """Lengths the standard actually offers in this size, in inches.

    These are the source's own lists -- the nominal lengths filtered to the
    per-size range, exactly as the upstream workbench computes them -- not an
    arithmetic series invented to fill the gap.
    """
    data = _load_lengths()
    if standard not in data:
        return ()
    sizes = data[standard].get("sizes", {})
    entry = sizes.get(size)
    if not entry:
        return ()
    values = entry.get("offered_lengths_mm")
    if values:
        return tuple(float(v) / MM_PER_INCH for v in values)
    values = entry.get("offered_lengths_in")
    if values:
        # The inch tables publish these as strings in the standard's own
        # spelling -- "1/2in", "1 1/4in". They are read with the repository's
        # own dimension parser rather than a second number-reader written
        # here, so there is exactly one place that decides what "1 1/4in"
        # means.
        return tuple(parse_length(str(v)).inches for v in values)
    return ()


@dataclass(frozen=True)
class FastenerHead:
    """The head dimensions of one size under one standard, in inches.

    ``published_unit`` is the unit the standard itself publishes in, because
    that decides how the catalog writes the value: a metric standard's screw
    is published in millimetres and an inch standard's in inches, and writing
    either in the other unit is how the measurement-system contradictions in
    the reference corpus arise.
    """

    standard: str
    size: str
    published_unit: str  # "mm" or "in"
    head_dia_in: float
    head_height_in: float
    threads_per_inch: float | None
    pitch_mm: float | None
    drive_size_in: float | None
    major_dia_in: float

    @property
    def thread_designation(self) -> str:
        """``M6x1`` or ``#10-32`` -- the form :func:`..dimensions.parse_thread` reads."""
        if self.published_unit == "mm":
            pitch = self.pitch_mm
            if pitch is None:
                raise StandardsDataError(f"{self.standard} {self.size} carries no pitch")
            text = f"{pitch:g}"
            return f"{self.size}x{text}"
        if self.threads_per_inch is None:
            raise StandardsDataError(f"{self.standard} {self.size} carries no thread count")
        return f"{self.size}-{round(self.threads_per_inch)}"


def _metric_major_dia_in(size: str) -> float:
    return float(size.lstrip("M")) / MM_PER_INCH


def socket_head(standard: str, size: str) -> FastenerHead:
    """A hexagon socket head cap screw -- ISO 4762 (metric) or ASME B18.3 (inch)."""
    row = row_for(standard, size)
    if standard == "ISO 4762":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="mm",
            head_dia_in=row["head_diameter_mm"] / MM_PER_INCH,
            head_height_in=row["head_height_mm"] / MM_PER_INCH,
            threads_per_inch=None,
            pitch_mm=row["thread_pitch_coarse_mm"],
            drive_size_in=row["socket_across_flats_mm"] / MM_PER_INCH,
            major_dia_in=_metric_major_dia_in(size),
        )
    if standard == "ASME B18.3":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="in",
            head_dia_in=row["head_diameter_in"],
            head_height_in=row["head_height_in"],
            threads_per_inch=row["threads_per_inch"],
            pitch_mm=None,
            drive_size_in=row["hex_socket_across_flats_in"],
            major_dia_in=INCH_MAJOR_DIA[size],
        )
    raise StandardsDataError(f"{standard!r} is not a socket head cap screw standard")


def flat_head(standard: str, size: str) -> FastenerHead:
    """A flat countersunk socket head cap screw -- ISO 10642 or ASME B18.3.2."""
    row = row_for(standard, size)
    if standard == "ISO 10642":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="mm",
            # The theoretical sharp-corner head diameter, matching the column
            # ASME B18.3.2 is read from, so the two countersunk standards are
            # described by the same measurement rather than by two different
            # ones that happen to share a field name.
            head_dia_in=row["head_diameter_theoretical_mm"] / MM_PER_INCH,
            head_height_in=row["head_height_mm"] / MM_PER_INCH,
            threads_per_inch=None,
            pitch_mm=row["thread_pitch_coarse_mm"],
            drive_size_in=row["socket_across_flats_mm"] / MM_PER_INCH,
            major_dia_in=_metric_major_dia_in(size),
        )
    if standard == "ASME B18.3.2":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="in",
            # dk_theo, the theoretical sharp-corner head diameter: this is the
            # 0.411" that the published #10 row states.
            head_dia_in=row["head_diameter_in"],
            head_height_in=row["head_height_in"],
            threads_per_inch=row["threads_per_inch"],
            pitch_mm=None,
            drive_size_in=row["hex_socket_across_flats_in"],
            major_dia_in=INCH_MAJOR_DIA[size],
        )
    raise StandardsDataError(f"{standard!r} is not a flat head cap screw standard")


def button_head(standard: str, size: str) -> FastenerHead:
    """A hexagon socket button head screw -- ISO 7380-1 or ASME B18.3.3A.

    A button head is a shallow dome, so its head diameter and head height
    describe a different shape from the cylinder a socket head cap screw's do.
    The two numbers are the ones the drawing needs -- the dome's chord and its
    rise -- and nothing else about the dome is extracted, because nothing else
    about it is published.
    """
    row = row_for(standard, size)
    if standard == "ISO 7380-1":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="mm",
            head_dia_in=row["head_diameter_mm"] / MM_PER_INCH,
            head_height_in=row["head_height_mm"] / MM_PER_INCH,
            threads_per_inch=None,
            pitch_mm=row["thread_pitch_coarse_mm"],
            drive_size_in=row["socket_across_flats_mm"] / MM_PER_INCH,
            major_dia_in=_metric_major_dia_in(size),
        )
    if standard == "ASME B18.3.3A":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="in",
            head_dia_in=row["head_diameter_in"],
            head_height_in=row["head_height_in"],
            threads_per_inch=row["threads_per_inch"],
            pitch_mm=None,
            drive_size_in=row["hex_socket_across_flats_in"],
            major_dia_in=INCH_MAJOR_DIA[size],
        )
    raise StandardsDataError(f"{standard!r} is not a button head cap screw standard")


def low_head(standard: str, size: str) -> FastenerHead:
    """A low head socket cap screw -- DIN 7984 or ASME B18.3.1G.

    The same cylindrical head as a socket head cap screw, and a different
    product: the head is about half as tall, because the screw exists for
    joints with no room for a full head. It is not wider for it -- DIN 7984's
    head diameter equals ISO 4762's at every size here, and ASME B18.3.1G's is
    a few thousandths under ASME B18.3's -- so what the two published numbers
    describe is a full head's diameter at half its height. That difference is
    entirely in those two numbers, which is why no separate head SHAPE is
    derived for it: a drawing built from these dimensions is already the squat
    head the standard describes.
    """
    row = row_for(standard, size)
    if standard == "DIN 7984":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="mm",
            head_dia_in=row["head_diameter_mm"] / MM_PER_INCH,
            head_height_in=row["head_height_mm"] / MM_PER_INCH,
            threads_per_inch=None,
            pitch_mm=row["thread_pitch_coarse_mm"],
            drive_size_in=row["socket_across_flats_mm"] / MM_PER_INCH,
            major_dia_in=_metric_major_dia_in(size),
        )
    if standard == "ASME B18.3.1G":
        return FastenerHead(
            standard=standard,
            size=size,
            published_unit="in",
            head_dia_in=row["head_diameter_in"],
            head_height_in=row["head_height_in"],
            threads_per_inch=row["threads_per_inch"],
            pitch_mm=None,
            drive_size_in=row["hex_socket_across_flats_in"],
            major_dia_in=INCH_MAJOR_DIA[size],
        )
    raise StandardsDataError(f"{standard!r} is not a low head cap screw standard")


@dataclass(frozen=True)
class HexBoltHead:
    standard: str
    size: str
    published_unit: str
    width_across_flats_in: float
    width_across_corners_in: float
    head_height_in: float
    threads_per_inch: float | None
    pitch_mm: float | None
    major_dia_in: float

    @property
    def thread_designation(self) -> str:
        if self.published_unit == "mm":
            return f"{self.size}x{self.pitch_mm:g}"
        return f"{self.size}-{round(self.threads_per_inch or 0)}"


def hex_bolt(standard: str, size: str) -> HexBoltHead:
    """A hex head screw.

    ISO 4017 and DIN 933 describe the same product and disagree: the width
    across flats is 16 vs 17 mm at M10 and 18 vs 19 mm at M12. Both upstream
    sources reproduce that split identically, so it is a real difference
    between the standards and not a transcription error -- and it is exactly
    the kind of thing a catalog carries, since which standard a line is built
    to is a property of the line.
    """
    row = row_for(standard, size)
    if standard in ("ISO 4014", "ISO 4017", "DIN 933"):
        return HexBoltHead(
            standard=standard,
            size=size,
            published_unit="mm",
            width_across_flats_in=row["width_across_flats_mm"] / MM_PER_INCH,
            width_across_corners_in=row["width_across_corners_mm"] / MM_PER_INCH,
            head_height_in=row["head_height_mm"] / MM_PER_INCH,
            threads_per_inch=None,
            pitch_mm=row["thread_pitch_coarse_mm"],
            major_dia_in=_metric_major_dia_in(size),
        )
    if standard == "ASME B18.2.1":
        return HexBoltHead(
            standard=standard,
            size=size,
            published_unit="in",
            width_across_flats_in=row["width_across_flats_in"],
            width_across_corners_in=row.get("width_across_corners_in")
            or row["width_across_flats_in"],
            head_height_in=row["head_height_in"],
            threads_per_inch=row["threads_per_inch"],
            pitch_mm=None,
            major_dia_in=INCH_MAJOR_DIA[size],
        )
    raise StandardsDataError(f"{standard!r} is not a hex bolt standard")


@dataclass(frozen=True)
class Washer:
    standard: str
    size: str
    published_unit: str
    inside_dia_in: float
    outside_dia_in: float
    thickness_in: float


def washer(standard: str, size: str) -> Washer:
    """A plain washer. ISO 7089 only: DIN 125 A is absent from the source.

    The extraction records DIN 125 A as carrying no rows rather than filling
    it from the corroborating repository, because that repository's washer
    inner diameter and thickness are known wrong. An empty table is the
    honest result and this catalog publishes no DIN 125 A washer.
    """
    row = row_for(standard, size)
    if standard != "ISO 7089":
        raise StandardsDataError(f"{standard!r} is not an extracted washer standard")
    return Washer(
        standard=standard,
        size=size,
        published_unit="mm",
        inside_dia_in=row["inner_diameter_mm"] / MM_PER_INCH,
        outside_dia_in=row["outer_diameter_mm"] / MM_PER_INCH,
        thickness_in=row["thickness_mm"] / MM_PER_INCH,
    )


def thread_designation_inch(size: str, *, fine: bool, coarse_tpi: float | None) -> str:
    """``#10-32`` for the fine series, ``#10-24`` for the coarse."""
    if fine:
        return f"{size}-{UNF_THREADS_PER_INCH[size]}"
    if coarse_tpi is None:
        raise StandardsDataError(f"no coarse thread count known for {size!r}")
    return f"{size}-{round(coarse_tpi)}"
