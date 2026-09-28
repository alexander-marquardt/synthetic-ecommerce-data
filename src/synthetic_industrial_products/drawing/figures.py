"""One figure per product kind, drawn from a SKU's own attribute values.

Each function reads the record the catalog publishes -- name to value, the
product's attributes and the SKU's together -- and draws the product to scale
in inches. The drawing reflects the specifications VISUALLY only: a longer
length of cut is drawn longer, a finer thread is drawn with more crests, a
flat head is a cone and a button head a dome. There is no text on any of it.

Parsing and the consistency checks are not re-implemented: each kind reads its
geometry through the same ``geometry_from_record`` the dimensioned renderers in
:mod:`..render` use, so the two can never disagree about what a record says.

A record the geometry cannot be read from as published -- an attribute absent,
a value that does not parse, a pair that contradicts itself -- is drawn with
its kind's NOMINAL proportions for the missing or conflicting values, and the
figure says so in :attr:`Drawn.source` (``record``, ``partial`` or
``nominal``). The share is reported per type in the image manifest rather than
hidden. A drawing with no text states no number, so a nominal proportion can
never contradict a published value; what it must not do is contradict one that
IS published, which is why a consistent published value always wins.
"""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass

from ..dimensions import DimensionParseError, parse_length
from ..render import drill as drill_geom
from ..render import endmill as endmill_geom
from ..render import fastener as fastener_geom
from ..render import flapdisc as flapdisc_geom
from ..render import tap as tap_geom
from ..render import washer as washer_geom
from ..render.attrs import REFUSALS
from .model import Figure, arc, regular_polygon

Record = dict[str, str]


@dataclass(frozen=True)
class Drawn:
    figure: Figure
    #: ``record`` when every drawn value is the record's own, ``partial`` when
    #: some were absent or inconsistent and took nominal proportions,
    #: ``nominal`` when the record's primary dimension itself could not be read.
    source: str


def _inches(value: float) -> str:
    return f"{value:.4f} in"


def _read(
    record: Record,
    geometry: Callable[[Record], object],
    defaults: dict[str, Callable[[Record], str]],
    nominal: Record,
    primary: str | None = None,
):
    """The geometry, from the record as published, else completed, else nominal."""
    try:
        return geometry(record), "record"
    except REFUSALS:
        pass
    completed = dict(record)
    for name, default in defaults.items():
        if name not in completed:
            try:
                completed[name] = default(completed)
            except REFUSALS:
                break
    try:
        return geometry(completed), "partial"
    except REFUSALS:
        pass
    # Something PUBLISHED contradicts: keep the primary, rebuild the rest.
    rebuilt = {k: v for k, v in record.items() if k not in defaults}
    for name, default in defaults.items():
        try:
            rebuilt[name] = default(rebuilt)
        except REFUSALS:
            rebuilt = {}
            break
    if rebuilt:
        try:
            return geometry(rebuilt), "partial"
        except REFUSALS:
            pass
    # Something ELSE published contradicts (a ball nose with a corner radius):
    # keep only the primary dimension, so siblings of different sizes still
    # draw different sizes, and take every other value from the nominal shape.
    if primary is not None and primary in record:
        core = {k: v for k, v in nominal.items() if k not in defaults}
        core[primary] = record[primary]
        for name, default in defaults.items():
            try:
                core[name] = default(core)
            except REFUSALS:
                core = {}
                break
        if core:
            try:
                return geometry(core), "partial"
            except REFUSALS:
                pass
    return geometry(nominal), "nominal"


def _len(record: Record, name: str) -> float:
    return parse_length(record[name]).inches


# --- rotary cutting tools --------------------------------------------------


def _helix_lines(x_half, y_from, y_to, pitch, slant, hand):
    """Flute edges across a body: slanted segments every ``pitch``, inside [y_from, y_to]."""
    segments = []
    if pitch <= 0:
        return segments
    y = y_from - slant
    while y < y_to:
        a = (-x_half * hand, y)
        b = (x_half * hand, y + slant)
        if a[1] >= y_from and b[1] <= y_to:
            segments.append((a, b))
        y += pitch
    return segments


def _end_view(fig: Figure, centre, radius, flutes, hand=1):
    fig.disc(centre, radius, "plain")
    cx, cy = centre
    segments = []
    for k in range(flutes):
        angle = 2 * math.pi * k / flutes
        tip = (cx + radius * math.cos(angle), cy + radius * math.sin(angle))
        bend = angle + hand * 0.6
        mid = (cx + 0.45 * radius * math.cos(bend), cy + 0.45 * radius * math.sin(bend))
        segments.append(((cx, cy), mid))
        segments.append((mid, tip))
    fig.lines(segments)


END_MILL_DEFAULTS = {
    "Shank Dia.": lambda r: r["Milling Dia."],
    "Length of Cut": lambda r: _inches(2.5 * _len(r, "Milling Dia.")),
    "Overall Length": lambda r: _inches(
        2.5 * _len(r, "Milling Dia.") + 3.0 * _len(r, "Shank Dia.") + 1.0
    ),
    "Number of Flutes": lambda r: "4",
    "Helix Angle": lambda r: "30 Degrees",
}
END_MILL_NOMINAL = {
    "End Mill Style": "Square",
    "Milling Dia.": '1/2"',
    "Shank Dia.": '1/2"',
    "Length of Cut": '1-1/4"',
    "Overall Length": '3"',
    "Number of Flutes": "4",
    "Helix Angle": "30 Degrees",
}


def end_mill(record: Record) -> Drawn:
    rec = dict(record)
    rec.setdefault("End Mill Style", END_MILL_NOMINAL["End Mill Style"])
    nominal = {**END_MILL_NOMINAL, "End Mill Style": rec["End Mill Style"]}
    geom, source = _read(
        rec, endmill_geom.geometry_from_record, END_MILL_DEFAULTS, nominal, "Milling Dia."
    )
    d, s = geom.cut_d.inches, geom.shank_d.inches
    loc, oal = geom.loc.inches, geom.oal.inches
    r = d / 2
    fig = Figure(size_in=oal)
    body_top = oal - loc
    shank_bottom = loc if geom.double_end else 0.0
    fig.rect(-s / 2, shank_bottom, s / 2, body_top, "plain")
    if geom.double_end:
        fig.rect(-r, 0.0, r, loc, "part")
    # The cutting end.
    if geom.style == "ball":
        outline = [(-r, body_top), (r, body_top)] + arc((0, oal - r), r, 0, 180, 16)
    elif geom.corner_radius is not None and geom.corner_radius.inches > 0:
        cr = geom.corner_radius.inches
        outline = (
            [(-r, body_top), (r, body_top)]
            + arc((r - cr, oal - cr), cr, 0, 90, 6)
            + arc((-r + cr, oal - cr), cr, 90, 180, 6)
        )
    else:
        outline = [(-r, body_top), (r, body_top), (r, oal), (-r, oal)]
    fig.poly(outline, "part")
    lead = math.pi * d / math.tan(math.radians(max(geom.helix_deg, 5.0)))
    pitch = lead / geom.flutes
    fig.lines(
        _helix_lines(
            r, body_top, oal - (r if geom.style == "ball" else 0), pitch, d * 0.55, geom.hand
        )
    )
    _end_view(fig, (max(r, s / 2) + 1.3 * r, body_top * 0.25 + r), r, geom.flutes, geom.hand)
    return Drawn(fig, source)


DRILL_DEFAULTS = {
    "Shank Dia.": lambda r: r["Size"],
    "Flute Length": lambda r: _inches(max(0.75, 11.0 * _len(r, "Size"))),
    "Overall Length": lambda r: _inches(max(0.75, 11.0 * _len(r, "Size")) * 1.55),
    "Point Angle": lambda r: "118 Degrees",
}
DRILL_NOMINAL = {
    "Size": '1/4"',
    "Shank Dia.": '1/4"',
    "Flute Length": '2-3/4"',
    "Overall Length": '4"',
    "Point Angle": "118 Degrees",
}


def drill(record: Record) -> Drawn:
    geom, source = _read(
        record, drill_geom.geometry_from_record, DRILL_DEFAULTS, DRILL_NOMINAL, "Size"
    )
    d, s = geom.dia.inches, geom.shank_d.inches
    flute, oal = geom.flute_len.inches, geom.oal.inches
    r = d / 2
    point = geom.point_height
    fig = Figure(size_in=oal)
    fig.rect(-s / 2, 0.0, s / 2, oal - flute, "plain")
    fig.poly([(-r, oal - flute), (r, oal - flute), (r, oal - point), (0, oal), (-r, oal - point)])
    lead = math.pi * d / math.tan(math.radians(30))
    fig.lines(_helix_lines(r, oal - flute, oal - point, lead / 2, d * 0.55, 1))
    return Drawn(fig, source)


TAP_DEFAULTS = {
    "Shank Dia.": lambda r: _inches(0.8 * _thread_major(r)),
    "Thread Length": lambda r: _inches(2.0 * _thread_major(r)),
    "Overall Length": lambda r: _inches(2.0 * _thread_major(r) + 1.8 + 2 * _thread_major(r)),
}
TAP_NOMINAL = {
    "Thread Size": "1/4-20",
    "Shank Dia.": '0.2550"',
    "Thread Length": '1"',
    "Overall Length": '2-1/2"',
}


def _thread_major(record: Record) -> float:
    from ..dimensions import parse_thread

    for name in ("Thread Size", "Dia./Thread Size"):
        if name in record:
            return parse_thread(record[name]).major.inches
    raise DimensionParseError("no thread size")


def _thread_crests(x_half, y_from, y_to, pitch):
    count = int((y_to - y_from) / pitch)
    return [
        ((-x_half, y_from + k * pitch), (x_half, y_from + k * pitch + pitch / 2))
        for k in range(count)
    ]


def tap(record: Record) -> Drawn:
    geom, source = _read(
        record, tap_geom.geometry_from_record, TAP_DEFAULTS, TAP_NOMINAL, "Thread Size"
    )
    major = geom.thread.major.inches
    s, oal, tl = geom.shank_d.inches, geom.oal.inches, geom.thread_len.inches
    r = major / 2
    pitch = geom.thread.pitch_in
    fig = Figure(size_in=oal)
    square = geom.square.inches if geom.square is not None else 0.8 * s
    fig.rect(-square / 2, 0.0, square / 2, 1.2 * square, "dark")
    fig.rect(-s / 2, 1.2 * square, s / 2, oal - tl, "plain")
    chamfer = min(3 * pitch, tl / 3)
    fig.poly(
        [
            (-r, oal - tl),
            (r, oal - tl),
            (r, oal - chamfer),
            (0.7 * r, oal),
            (-0.7 * r, oal),
            (-r, oal - chamfer),
        ]
    )
    fig.lines(_thread_crests(r, oal - tl, oal - chamfer, pitch))
    return Drawn(fig, source)


# --- fasteners ---------------------------------------------------------------

FASTENER_DEFAULTS = {
    "Length": lambda r: _inches(4.0 * _thread_major(r)),
    "Thread Length": lambda r: r["Length"],
    "Head Dia.": lambda r: _inches(1.5 * _thread_major(r)),
    "Head Height": lambda r: _inches(1.0 * _thread_major(r)),
}
FASTENER_NOMINAL = {
    "Dia./Thread Size": "1/4-20",
    "Length": '1"',
    "Thread Length": '1"',
    "Head Dia.": '0.3750"',
    "Head Height": '0.2500"',
}


def fastener(record: Record) -> Drawn:
    rec = dict(record)
    if "Head Type" not in rec and "Screw Head Type" not in rec:
        rec["Head Type"] = "Socket"
    nominal = {**FASTENER_NOMINAL, "Head Type": rec.get("Head Type", rec.get("Screw Head Type"))}
    geom, source = _read(
        rec, fastener_geom.geometry_from_record, FASTENER_DEFAULTS, nominal, "Dia./Thread Size"
    )
    major = geom.thread.major.inches
    r = major / 2
    hh = geom.head_height.inches
    total = geom.total_height
    hd = geom.head_dia.inches
    fig = Figure(size_in=total)
    # Head, top at y = 0.
    if geom.countersunk:
        fig.poly([(-hd / 2, 0.0), (hd / 2, 0.0), (r, hh), (-r, hh)])
    elif geom.domed:
        dome = [(x, hh - y) for x, y in fastener_geom.dome_profile(hd / 2, hh, 0.0)]
        fig.poly(dome + [(hd / 2, hh), (-hd / 2, hh)])
    elif geom.hex_headed:
        across_corners = geom.across_flats * 2 / math.sqrt(3)
        fig.rect(-across_corners / 2, 0.0, across_corners / 2, hh)
        fig.lines(
            [
                ((-across_corners / 4, 0.0), (-across_corners / 4, hh)),
                ((across_corners / 4, 0.0), (across_corners / 4, hh)),
            ]
        )
    else:
        fig.rect(-hd / 2, 0.0, hd / 2, hh)
    # Shank: plain above the thread, threaded below.
    shank_top = hh
    thread_top = total - geom.threaded_length
    if thread_top > shank_top:
        fig.rect(-r, shank_top, r, thread_top, "plain")
    chamfer = min(geom.thread.pitch_in, geom.threaded_length / 4)
    fig.poly(
        [
            (-r, thread_top),
            (r, thread_top),
            (r, total - chamfer),
            (r - chamfer, total),
            (-r + chamfer, total),
            (-r, total - chamfer),
        ]
    )
    fig.lines(_thread_crests(r, thread_top, total - chamfer, geom.thread.pitch_in))
    # End view of the head, beside it: the drive a shopper would see.
    cx = max(hd, major) * 1.25
    cy = hd / 2
    if geom.hex_headed:
        fig.poly(regular_polygon((cx, cy), geom.across_flats / math.sqrt(3), 6, 30))
    else:
        fig.disc((cx, cy), hd / 2)
        if geom.drive_size is not None:
            fig.poly(
                regular_polygon((cx, cy), geom.drive_size.inches / math.sqrt(3), 6, 30), "dark"
            )
    return Drawn(fig, source)


WASHER_NOMINAL = {"Inside Dia.": '0.2810"', "Outside Dia.": '0.6250"', "Thickness": '0.0650"'}


def washer(record: Record) -> Drawn:
    geom, source = _read(record, washer_geom.geometry_from_record, {}, WASHER_NOMINAL)
    od, i_d, t = geom.outside_d.inches, geom.inside_d.inches, geom.thickness.inches
    fig = Figure(size_in=od)
    fig.disc((0.0, 0.0), od / 2)
    fig.disc((0.0, 0.0), i_d / 2, "hole")
    edge = od / 2 + 0.35 * od
    fig.rect(-od / 2, edge, -i_d / 2, edge + t, "plain")
    fig.rect(i_d / 2, edge, od / 2, edge + t, "plain")
    return Drawn(fig, source)


# --- abrasives ---------------------------------------------------------------

FLAP_DISC_DEFAULTS = {"Arbor Hole": lambda r: '7/8"'}
FLAP_DISC_NOMINAL = {"Diameter": '4-1/2"', "Arbor Hole": '7/8"'}


def _grit(record: Record) -> int | None:
    try:
        return int(str(record.get("Grit", "")).strip())
    except ValueError:
        return None


def flap_disc(record: Record) -> Drawn:
    geom, source = _read(
        record, flapdisc_geom.geometry_from_record, FLAP_DISC_DEFAULTS, FLAP_DISC_NOMINAL
    )
    big, small = geom.disc_d.inches / 2, geom.arbor_d.inches / 2
    fig = Figure(size_in=geom.disc_d.inches)
    fig.disc((0.0, 0.0), big)
    inner = max(0.42 * big, 1.3 * small)
    flaps = 28
    fig.lines(
        (
            (inner * math.cos(a), inner * math.sin(a)),
            (big * math.cos(a + 0.25), big * math.sin(a + 0.25)),
        )
        for a in (2 * math.pi * k / flaps for k in range(flaps))
    )
    if "conical" in str(record.get("Shape", "")).lower():
        fig.disc((0.0, 0.0), inner, "plain")
    grit = _grit(record)
    if grit:
        # Coarse grit reads coarse: fewer, larger marks on the flaps. The count
        # is the grit number itself, over a fixed area, so 40 and 80 differ.
        golden = math.pi * (3 - math.sqrt(5))
        marks = max(8, min(120, grit))
        centres = []
        for k in range(marks):
            rr = inner + (big - inner) * (0.1 + 0.8 * ((k + 0.5) / marks) ** 0.5)
            a = k * golden
            centres.append((rr * math.cos(a), rr * math.sin(a)))
        fig.dots(centres, big * 0.2 / math.sqrt(grit))
    fig.disc((0.0, 0.0), small, "hole")
    return Drawn(fig, source)


# --- hand tools --------------------------------------------------------------

HANDLE_FILL = {"Hickory": "#c89a5b", "Ash": "#dcc08e", "Fiberglass": "#e2c64a", "Steel": "#9aa3aa"}
GRIP_FILL = {"Rubber": "#3d3d3d", "Vinyl": "#51638a"}


def hammer(record: Record) -> Drawn:
    """No geometry function exists for a hammer, and the reason is kept.

    A head WEIGHT is not a shape: drawing the head from it would mean assuming
    a density and a form. So the head is drawn from the published face
    diameter at a nominal pein proportion, and the handle from the published
    handle (or overall) length. Weight is not drawn.
    """
    source = "record"

    def length(name, fallback):
        nonlocal source
        try:
            return parse_length(record[name]).inches
        except (KeyError, DimensionParseError):
            source = "partial"
            return fallback

    face = length("Face Dia.", 1.0)
    oal = length("Overall Length", 13.0)
    handle = length("Handle Length", 0.88 * oal)
    if handle >= oal:
        handle, source = 0.88 * oal, "partial"
    fig = Figure(size_in=oal)
    head_len = 3.6 * face
    head_top = 0.0
    fig.rect(-head_len / 2, head_top, head_len / 2 - 0.45 * face, head_top + face)
    fig.disc((head_len / 2 - 0.45 * face, head_top + face / 2), 0.45 * face)
    width = 0.55 * face
    handle_fill = HANDLE_FILL.get(str(record.get("Handle Material", "")), "#c89a5b")
    fig.rect(-width / 2, head_top + face, width / 2, oal, "handle", handle_fill)
    grip = GRIP_FILL.get(str(record.get("Handle Grip Material", "")))
    if grip:
        fig.rect(-width / 2 - 0.05, oal - 0.35 * handle, width / 2 + 0.05, oal, "grip", grip)
    return Drawn(fig, source)


#: Which figure each product type is drawn with, and the type's largest DRAWN
#: extent in inches, ``(width, height)`` of any product's bounding box, with a
#: little headroom. The sheet's scale for the type is derived from it and is
#: therefore ONE constant per type (:mod:`.sheet`);
#: ``tests/test_sku_drawings.py`` asserts no product's drawing exceeds it, so
#: a regeneration that grows past it is red instead of silently fitted.
#:
#: The five screw and bolt extents were raised for the 100K catalog, which
#: reaches further along each size's OFFERED lengths
#: (``data/fastener_offered_lengths.json``) than the 10K one did: measured on
#: ``sip-generate build --lines 25850``, the longest drawn part is 14.62" (a
#: socket head cap screw), 14.49" (hex bolt), 12.31" (low head), 12.00" (flat
#: head) and 5.34" (button head). Each extent is that maximum plus ~3%.
FIGURES: dict[str, tuple[Callable[[Record], Drawn], tuple[float, float]]] = {
    "end_mill_square": (end_mill, (3.3, 9.5)),
    "end_mill_ball": (end_mill, (3.3, 9.5)),
    "drill_jobber": (drill, (0.52, 8.8)),
    "tap_spiral_point": (tap, (0.52, 4.15)),
    "screw_socket_head": (fastener, (2.75, 15.05)),
    "screw_flat_head": (fastener, (3.7, 12.4)),
    "screw_button_head": (fastener, (2.56, 5.5)),
    "screw_low_head": (fastener, (2.75, 12.7)),
    "bolt_hex": (fastener, (2.85, 14.95)),
    "washer_flat": (washer, (1.5, 2.15)),
    "hammer_ball_pein": (hammer, (5.8, 18.25)),
    "abrasive_flap_disc": (flap_disc, (7.25, 7.25)),
}


# --- the types added by elastic/prism-industrial-products#103 ------------------


def _length_or(record: Record, name: str, fallback: float) -> tuple[float, bool]:
    try:
        return parse_length(record[name]).inches, True
    except (KeyError, DimensionParseError):
        return fallback, False


def hex_nut(record: Record) -> Drawn:
    """A nut's face (hexagon across its flats, the threaded hole) and its edge."""
    try:
        major = _thread_major(record)
        read = True
    except (KeyError, DimensionParseError):
        major, read = 0.25, False
    flats, ok_f = _length_or(record, "Width Across Flats", 1.6 * major)
    height, ok_h = _length_or(record, "Height", 0.85 * major)
    if flats <= major:
        flats, ok_f = 1.6 * major, False
    source = "record" if read and ok_f and ok_h else ("partial" if read else "nominal")
    corners = flats * 2 / math.sqrt(3)
    fig = Figure(size_in=flats)
    fig.poly(regular_polygon((0.0, 0.0), corners / 2, 6, 30))
    fig.disc((0.0, 0.0), major / 2, "hole")
    fig.lines(
        (
            ((major / 2) * 0.82 * math.cos(a), (major / 2) * 0.82 * math.sin(a)),
            ((major / 2) * 0.82 * math.cos(a + 0.9), (major / 2) * 0.82 * math.sin(a + 0.9)),
        )
        for a in (2 * math.pi * k / 3 for k in range(3))
    )
    edge = corners / 2 + 0.3 * corners
    fig.rect(-corners / 2, edge, corners / 2, edge + height, "plain")
    fig.lines(
        [
            ((-corners / 4, edge), (-corners / 4, edge + height)),
            ((corners / 4, edge), (corners / 4, edge + height)),
        ]
    )
    return Drawn(fig, source)


#: How a closure is painted over the ball track: open shows the balls.
_CLOSURE_ROLE = {"Double Shield": "plain", "Double Seal": "dark"}


def bearing(record: Record) -> Drawn:
    """Face view -- rings, and the balls or the shield or the seal -- and the edge."""
    bore, ok_b = _length_or(record, "Bore", 0.5)
    od, ok_o = _length_or(record, "Outside Dia.", 2.4 * bore)
    width, ok_w = _length_or(record, "Width", 0.3 * od)
    if od <= bore:
        od, ok_o = 2.4 * bore, False
    source = "record" if ok_b and ok_o and ok_w else ("partial" if ok_b else "nominal")
    r_out, r_in = od / 2, bore / 2
    section = r_out - r_in
    ring = 0.28 * section
    pitch_r = (r_out + r_in) / 2
    ball_r = 0.3 * section
    fig = Figure(size_in=od)
    fig.disc((0.0, 0.0), r_out)
    fig.disc((0.0, 0.0), r_out - ring, "plain")
    closure = str(record.get("Closure Type", "Open"))
    role = _CLOSURE_ROLE.get(closure)
    if role is None:
        balls = max(6, int(2 * math.pi * pitch_r / (2.3 * ball_r)))
        for k in range(balls):
            a = 2 * math.pi * k / balls
            fig.disc((pitch_r * math.cos(a), pitch_r * math.sin(a)), ball_r)
    else:
        fig.disc((0.0, 0.0), r_out - ring * 1.15, role)
    fig.disc((0.0, 0.0), r_in + ring)
    fig.disc((0.0, 0.0), r_in, "hole")
    edge = r_out + 0.3 * od
    fig.rect(-r_out, edge, r_out, edge + width, "plain")
    fig.lines(
        [
            ((-r_out + ring, edge), (-r_out + ring, edge + width)),
            ((r_out - ring, edge), (r_out - ring, edge + width)),
            ((-r_in - ring, edge), (-r_in - ring, edge + width)),
            ((r_in + ring, edge), (r_in + ring, edge + width)),
        ]
    )
    return Drawn(fig, source)


def depressed_wheel(record: Record) -> Drawn:
    """Face with its grit, and the edge profile: the depressed hub, to thickness."""
    dia, ok_d = _length_or(record, "Diameter", 4.5)
    thick, ok_t = _length_or(record, "Thickness", 0.25)
    arbor, ok_a = _length_or(record, "Arbor Hole", 0.875)
    if arbor >= dia:
        arbor, ok_a = 0.875, False
    source = "record" if ok_d and ok_t and ok_a else ("partial" if ok_d else "nominal")
    big, small = dia / 2, arbor / 2
    fig = Figure(size_in=dia)
    fig.disc((0.0, 0.0), big)
    hub = max(1.9 * small, 0.3 * big)
    fig.disc((0.0, 0.0), hub, "plain")
    grit = _grit(record)
    if grit:
        golden = math.pi * (3 - math.sqrt(5))
        marks = max(8, min(140, grit))
        centres = []
        for k in range(marks):
            rr = hub + (big - hub) * (0.08 + 0.84 * ((k + 0.5) / marks) ** 0.5)
            a = k * golden
            centres.append((rr * math.cos(a), rr * math.sin(a)))
        fig.dots(centres, big * 0.18 / math.sqrt(grit))
    fig.disc((0.0, 0.0), small, "hole")
    # Edge profile, below: a flat rim and a hub set down by the wheel's own
    # thickness (Type 27), or a dished saucer (Type 28).
    top = big + 0.35 * dia
    drop = thick * (1.6 if "28" in str(record.get("Type", "")) else 1.0)
    fig.poly(
        [
            (-big, top),
            (-hub, top),
            (-hub, top + drop),
            (-small, top + drop),
            (-small, top + drop + thick),
            (-hub - thick, top + drop + thick),
            (-hub - thick, top + thick),
            (-big, top + thick),
        ]
    )
    fig.poly(
        [
            (big, top),
            (hub, top),
            (hub, top + drop),
            (small, top + drop),
            (small, top + drop + thick),
            (hub + thick, top + drop + thick),
            (hub + thick, top + thick),
            (big, top + thick),
        ]
    )
    return Drawn(fig, source)


def hex_key(record: Record) -> Drawn:
    """An L of hex bar: the long arm, the short arm, and a ball tip when there is one."""
    size, ok_s = _length_or(record, "Size", 0.125)
    oal, ok_l = _length_or(record, "Overall Length", 1.2 + 9 * size)
    width, ok_w = _length_or(record, "Overall Width", 0.45 + 3 * size)
    if oal <= 2 * size or width <= 2 * size:
        oal, width, ok_l = 1.2 + 9 * size, 0.45 + 3 * size, False
    source = "record" if ok_s and ok_l and ok_w else ("partial" if ok_s else "nominal")
    fig = Figure(size_in=oal)
    fig.poly(
        [
            (0.0, 0.0),
            (width, 0.0),
            (width, size),
            (size, size),
            (size, oal),
            (0.0, oal),
        ]
    )
    if "ball" in str(record.get("Tip Style", "")).lower():
        fig.rect(0.18 * size, oal, 0.82 * size, oal + 0.35 * size, "plain")
        fig.disc((size / 2, oal + 0.35 * size + 0.55 * size), 0.6 * size)
    fig.poly(regular_polygon((width + 1.2 * size, oal * 0.3), size / math.sqrt(3), 6, 30))
    return Drawn(fig, source)


FIGURES.update(
    {
        "nut_hex": (hex_nut, (1.95, 3.5)),
        "bearing_radial_ball": (bearing, (3.25, 4.95)),
        "wheel_depressed_center": (depressed_wheel, (9.3, 13.2)),
        "hex_key": (hex_key, (2.95, 9.85)),
    }
)
