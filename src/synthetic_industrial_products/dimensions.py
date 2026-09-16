"""Parse the dimension strings that industrial catalogs actually publish.

Catalog values are text, not numbers: ``3/8"``, ``1-3/8"``, ``1/2 in``,
``0.411 in``, ``6 mm``, ``#10-32``. Everything downstream draws from these, so
a value this module cannot read must raise rather than fall back to a default.
A drawing produced from a silently-defaulted dimension is a picture that
disagrees with its own record, which is exactly the failure this catalog exists
to avoid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

MM_PER_INCH = 25.4

#: ANSI screw "number" sizes: the major diameter of a #N is 0.060 + 0.013 N inches.
_NUMBER_SIZE_BASE_IN = 0.060
_NUMBER_SIZE_STEP_IN = 0.013

#: Unified/ISO 60-degree thread form: the minor diameter of an external thread
#: sits 1.226869 pitches below the major diameter.
_MINOR_DIA_PITCH_FACTOR = 1.226869


class DimensionParseError(ValueError):
    """A catalog value could not be read as the dimension it is supposed to be."""


@dataclass(frozen=True)
class Length:
    """A length, canonicalised to inches but remembering how it was published."""

    inches: float
    unit: str  # "in" or "mm"
    raw: str

    @property
    def mm(self) -> float:
        return self.inches * MM_PER_INCH

    def display(self) -> str:
        """The value as the catalog published it -- never a reformatted version."""
        return self.raw


@dataclass(frozen=True)
class Thread:
    """A thread designation, reduced to the numbers a drawing needs."""

    designation: str
    major: Length
    pitch_in: float

    @property
    def tpi(self) -> float:
        return 1.0 / self.pitch_in

    @property
    def minor_in(self) -> float:
        """Minor diameter of the external thread, from the 60-degree thread form."""
        return self.major.inches - _MINOR_DIA_PITCH_FACTOR * self.pitch_in


_UNIT_SUFFIXES: tuple[tuple[str, str], ...] = (
    ("millimeters", "mm"),
    ("millimetres", "mm"),
    ("millimeter", "mm"),
    ("millimetre", "mm"),
    ("inches", "in"),
    ("inch", "in"),
    ("in.", "in"),
    ("mm", "mm"),
    ("in", "in"),
    ('"', "in"),
)

_MIXED = re.compile(r"^(?P<whole>\d+)[-\s](?P<num>\d+)/(?P<den>\d+)$")
_FRACTION = re.compile(r"^(?P<num>\d+)/(?P<den>\d+)$")
_DECIMAL = re.compile(r"^(?P<dec>\d+(?:\.\d+)?)$")


def _split_unit(text: str) -> tuple[str, str]:
    low = text.lower()
    for suffix, unit in _UNIT_SUFFIXES:
        if low.endswith(suffix):
            return text[: len(text) - len(suffix)].strip(), unit
    raise DimensionParseError(
        f"{text!r} carries no unit; a bare number is ambiguous and is not accepted"
    )


def _parse_magnitude(text: str, *, original: str) -> float:
    text = text.strip()
    if not text:
        raise DimensionParseError(f"{original!r} has a unit but no magnitude")
    for pattern in (_MIXED, _FRACTION, _DECIMAL):
        m = pattern.match(text)
        if m is None:
            continue
        groups = m.groupdict()
        if "den" in groups:
            den = int(groups["den"])
            if den == 0:
                raise DimensionParseError(f"{original!r} has a zero denominator")
            value = int(groups["num"]) / den
            if "whole" in groups and groups.get("whole") is not None:
                value += int(groups["whole"])
            return value
        return float(groups["dec"])
    raise DimensionParseError(f"{original!r} is not a number, a fraction, or a mixed number")


def parse_length(value: str) -> Length:
    """Read a published length such as ``3/8"``, ``1-3/8"``, ``6 mm``, ``0.411 in``."""
    if not isinstance(value, str):
        raise DimensionParseError(f"expected a catalog string, got {type(value).__name__}")
    original = value
    text = value.strip()
    if not text:
        raise DimensionParseError("empty value")
    body, unit = _split_unit(text)
    magnitude = _parse_magnitude(body, original=original)
    inches = magnitude if unit == "in" else magnitude / MM_PER_INCH
    if inches <= 0:
        raise DimensionParseError(f"{original!r} is not a positive length")
    return Length(inches=inches, unit=unit, raw=original.strip())


def parse_count(value: str) -> int:
    """Read an integer attribute such as ``Number of Flutes``."""
    text = str(value).strip()
    if not re.fullmatch(r"\d+", text):
        raise DimensionParseError(f"{value!r} is not a whole count")
    count = int(text)
    if count <= 0:
        raise DimensionParseError(f"{value!r} is not a positive count")
    return count


def parse_angle_degrees(value: str) -> float:
    """Read ``30 Degrees`` / ``30`` / ``30 deg`` as a number of degrees."""
    text = str(value).strip().lower()
    text = re.sub(r"\s*(degrees|degree|deg\.?|°)$", "", text).strip()
    m = _DECIMAL.match(text)
    if m is None:
        raise DimensionParseError(f"{value!r} is not an angle in degrees")
    angle = float(m.group("dec"))
    if not 0 <= angle < 90:
        raise DimensionParseError(f"{value!r} is not a usable helix angle")
    return angle


_NUMBER_THREAD = re.compile(r"^#(?P<size>\d+)\s*-\s*(?P<tpi>\d+)$")
_INCH_THREAD = re.compile(r"^(?P<dia>[\d/\-.\" ]+?)\s*-\s*(?P<tpi>\d+)$")
_METRIC_THREAD = re.compile(r"^M\s*(?P<dia>\d+(?:\.\d+)?)\s*[x×]\s*(?P<pitch>\d+(?:\.\d+)?)$", re.I)


def parse_thread(value: str) -> Thread:
    """Read a thread designation: ``#10-32``, ``1/4"-20``, ``M6x1``.

    A designation without an explicit pitch (a bare ``M6``) raises: the coarse
    pitch is a table lookup, not something this string carries, and guessing it
    would put a number in the drawing that the record does not contain.
    """
    text = str(value).strip()
    if not text:
        raise DimensionParseError("empty thread designation")

    m = _METRIC_THREAD.match(text)
    if m:
        major_mm = float(m.group("dia"))
        pitch_mm = float(m.group("pitch"))
        if major_mm <= 0 or pitch_mm <= 0:
            raise DimensionParseError(f"{value!r} has a non-positive dimension")
        return Thread(
            designation=text,
            major=Length(inches=major_mm / MM_PER_INCH, unit="mm", raw=f"{m.group('dia')} mm"),
            pitch_in=pitch_mm / MM_PER_INCH,
        )

    m = _NUMBER_THREAD.match(text)
    if m:
        size = int(m.group("size"))
        tpi = int(m.group("tpi"))
        if tpi <= 0:
            raise DimensionParseError(f"{value!r} has a non-positive thread count")
        major_in = _NUMBER_SIZE_BASE_IN + _NUMBER_SIZE_STEP_IN * size
        return Thread(
            designation=text,
            major=Length(inches=major_in, unit="in", raw=f'{major_in:.3f}"'),
            pitch_in=1.0 / tpi,
        )

    m = _INCH_THREAD.match(text)
    if m:
        tpi = int(m.group("tpi"))
        if tpi <= 0:
            raise DimensionParseError(f"{value!r} has a non-positive thread count")
        dia_text = m.group("dia").strip()
        if not dia_text.endswith('"'):
            dia_text += '"'
        major = parse_length(dia_text)
        return Thread(designation=text, major=major, pitch_in=1.0 / tpi)

    raise DimensionParseError(
        f"{value!r} is not a thread designation this renderer can read "
        '(expected forms: #10-32, 1/4"-20, M6x1)'
    )
