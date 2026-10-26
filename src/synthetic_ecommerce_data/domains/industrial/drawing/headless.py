"""The headless threaded screw: one kind of geometry a type file names (#72).

A set screw has no head: a threaded body, a point at one end and a hex socket
sunk into the other, drawn beside an end view of that socket. That is a kind
of geometry, so it is code here; a type that is such a screw (a hex socket set
screw, a stainless one, a square-head one) names it in its data file with
``figure: headless_screw`` and gives only the extent, and no figure module is
written for it.

The proportions below were the pilot's own (``set_screws_hex_socket``) and are
moved here unchanged: the digest of every drawing it served is pinned by
``tests/test_type_set_screws_hex_socket.py`` and the golden catalogue.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length, parse_thread
from synthetic_ecommerce_data.core.drawing.model import Figure, regular_polygon
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn


def _value(record: Mapping[str, str], name: str) -> float | None:
    try:
        return parse_length(record[name]).inches
    except (KeyError, DimensionParseError):
        return None


def headless_screw(record: Mapping[str, str], extent: Sequence[float]) -> Drawn:
    """A headless threaded body, its point, and an end view of the hex socket.

    ``extent`` is the sheet the figure is drawn on; a part longer than 95% of its
    height is drawn compressed, with a break.
    """
    try:
        major = parse_thread(record["Dia./Thread Size"]).major.inches
        pitch = parse_thread(record["Dia./Thread Size"]).pitch_in
        read = True
    except (KeyError, DimensionParseError):
        major, pitch, read = 0.25, 0.05, False
    length = _value(record, "Length") or 1.5 * major
    key = _value(record, "Drive Size") or 0.5 * major
    point_dia = _value(record, "Point Dia.") or 0.6 * major
    r = major / 2
    height = extent[1] * 0.95
    knee = 0.8 * height
    drawn = length if length <= knee else knee + 0.15 * height * (1 - math.exp(-(length - knee)))
    fig = Figure(size_in=drawn)
    point = record.get("Point Type", "Cup Point")
    tip = min(drawn / 3, r)
    body_end = drawn - tip
    fig.rect(-r, 0.0, r, body_end, "plain")
    crests = int(body_end / pitch) if pitch > 0 else 0
    fig.lines([((-r, k * pitch), (r, k * pitch + pitch / 2)) for k in range(min(crests, 400))])
    if point == "Cone Point":
        fig.poly([(-r, body_end), (r, body_end), (0.0, drawn)])
    elif point == "Dog Point":
        p = point_dia / 2
        fig.poly([(-r, body_end), (r, body_end), (p, body_end + tip / 3), (-p, body_end + tip / 3)])
        fig.rect(-p, body_end + tip / 3, p, drawn, "plain")
    else:
        p = point_dia / 2
        fig.poly([(-r, body_end), (r, body_end), (p, drawn), (-p, drawn)])
        if point == "Cup Point":
            fig.poly([(-0.6 * p, drawn), (0.6 * p, drawn), (0.0, drawn - tip / 2)], "hole")
    fig.rect(-key / 2, 0.0, key / 2, min(key, body_end / 2), "dark")
    if length > knee:
        cut = drawn * 0.45
        fig.lines([((-1.15 * r, cut + d), (1.15 * r, cut + d + 0.04)) for d in (0.0, 0.08)])
    cx = major * 1.4
    fig.disc((cx, r), r)
    fig.poly(regular_polygon((cx, r), key / math.sqrt(3), 6, 30), "dark")
    source = "record" if read and _value(record, "Length") else ("partial" if read else "nominal")
    return Drawn(fig, source)


@dataclass(frozen=True)
class HeadlessScrewFigure:
    """The figure function of a type: :func:`headless_screw` at the type's ``extent``.

    A value, not a closure, so two loads of the same type file compare equal.
    """

    extent: tuple[float, ...]

    def __call__(self, record: Mapping[str, str]) -> Drawn:
        return headless_screw(record, self.extent)


def headless_screw_figure(extent: Sequence[float]) -> HeadlessScrewFigure:
    """The figure function of a type whose file names ``figure: headless_screw``."""
    return HeadlessScrewFigure(tuple(extent))
