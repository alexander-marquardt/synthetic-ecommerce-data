"""A plain screw's figure, drawn from the SKU's gauge or thread and its length (#750).

A head, a threaded shank and, on a screw that cuts its own way, a point. A wood screw's top third
is plain shank. The end view beside it shows the drive. The head proportions are a plain screw's
usual ones and no standard's: a published gauge fixes the shank, not the head.
"""

from __future__ import annotations

from synthetic_ecommerce_data.core.dimensions import (
    DimensionParseError,
    parse_gauge,
    parse_length,
    parse_thread,
)
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.domains.industrial.drawing import primitives as P  # noqa: N812
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn, Record

#: The spacing of a gauge screw's coarse thread, as a share of its diameter.
GAUGE_PITCH = 0.5
#: A head's diameter and height, as multiples of the shank's diameter, by the head's first word.
HEADS: dict[str, tuple[float, float]] = {
    "Flat": (1.95, 0.6),
    "Bugle": (1.9, 0.75),
    "Pan": (1.95, 0.7),
    "Round": (1.9, 0.75),
    "Hex": (1.7, 0.8),
}
NOMINAL_MAJOR = 0.164
NOMINAL_LENGTH = 1.0


def _major_and_pitch(record: Record) -> tuple[float, float]:
    """The shank's diameter and the thread's pitch, in inches."""
    gauge = record.get("Gauge")
    if gauge is not None:
        major = parse_gauge(gauge)
        return major, major * GAUGE_PITCH
    thread = parse_thread(record["Thread Size"])
    return thread.major.inches, thread.pitch_in


def _head(fig: Figure, head_type: str, head_d: float, r: float, height: float) -> None:
    if head_type.startswith(("Flat", "Bugle")):
        P.head_flat(fig, head_d, r, height)
    elif head_type.startswith("Pan"):
        P.head_pan(fig, head_d, height)
    elif head_type.startswith("Hex"):
        P.head_hex(fig, head_d, height)
    else:
        P.head_button(fig, head_d, height)


def _drive(fig: Figure, drive: str, cx: float, cy: float, head_d: float) -> None:
    """The recess a drive cuts into the head, seen end on."""
    arm, web = 0.3 * head_d, 0.07 * head_d
    if drive == "Phillips":
        fig.rect(cx - arm, cy - web, cx + arm, cy + web, "dark")
        fig.rect(cx - web, cy - arm, cx + web, cy + arm, "dark")
    elif drive == "Slotted":
        fig.rect(cx - 1.5 * arm, cy - web, cx + 1.5 * arm, cy + web, "dark")
    elif drive == "Square":
        fig.rect(cx - 0.6 * arm, cy - 0.6 * arm, cx + 0.6 * arm, cy + 0.6 * arm, "dark")
    else:
        P.drive_recess(fig, (cx, cy), head_d * 0.4)


def plain_screw(record: Record) -> Drawn:
    """The screw at its published length; a value that does not parse draws nominal."""
    source = "record"
    try:
        major, pitch = _major_and_pitch(record)
    except (DimensionParseError, KeyError):
        major, pitch, source = NOMINAL_MAJOR, NOMINAL_MAJOR * GAUGE_PITCH, "partial"
    try:
        length = parse_length(record["Length"]).inches
    except (DimensionParseError, KeyError):
        length, source = NOMINAL_LENGTH, "partial"
    head_type = record.get("Head Type", "Flat Head")
    across, tall = HEADS[head_type.split()[0]]
    head_d, height = across * major, tall * major
    r = major / 2
    # The published length runs from under a raised head, and over the whole of a countersunk one.
    countersunk = head_type.startswith(("Flat", "Bugle"))
    total = length if countersunk else length + height
    fig = Figure(size_in=total)
    _head(fig, head_type, head_d, r, height)
    pointed = "Gauge" in record
    tip = min(1.2 * major, (total - height) / 2) if pointed else 0.0
    shank_end = height + (total - height) / 3 if head_type == "Flat Head" and pointed else height
    if shank_end > height:
        P.shank(fig, r, height, shank_end)
    P.thread(fig, r, shank_end, total - tip, pitch, 0.0 if pointed else pitch)
    if pointed:
        P.conical_end(fig, r, total - tip, total - tip, total)
    cx, cy = head_d * 1.25, head_d / 2
    if head_type.startswith("Hex"):
        P.hex_face(fig, (cx, cy), head_d / 2)
    else:
        P.round_face(fig, (cx, cy), head_d / 2)
        _drive(fig, record.get("Drive Type", "Phillips"), cx, cy, head_d)
    return Drawn(fig, source)
