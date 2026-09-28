"""Dimensioned jobber-drill drawing, derived entirely from a product record.

The drill stands vertically, shank up and point down, for the same reason the
end mill does: it is how the industry draws one, and it is the only orientation
in which a long thin tool fills a portrait card.

What is drawn and what is not
-----------------------------
* The **point** is drawn to the included angle the record publishes as
  ``Point Angle``, and the angular dimension on the detail profile restates
  that published value. A record whose point angle is absent -- or whose angle
  attribute carries a length unit, which this catalog reproduces at a measured
  rate -- is refused rather than drawn to a conventional 118 degrees.
* The **shank** needs ``Shank Dia.``. A jobber drill's shank is usually the
  nominal diameter, but "usually" is a convention, not this record, and drawing
  the shank at the drill size would put a diameter in the picture the record
  does not carry. Only 46% of the generated catalog publishes it; the rest get
  the undimensioned type drawing.
* The **flutes** are drawn in the conventional way drafting draws a thread or a
  knurl: at a fixed spacing, stating that the surface is fluted without stating
  a helix. No attribute on a drill record carries a helix angle or a flute
  count, so there is nothing to derive one from -- and nothing on the drawing
  points a dimension at them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Polygon, Rectangle

from ..dimensions import Length, parse_included_angle_degrees, parse_length
from . import canvas as cv
from .attrs import (
    ImpossibleGeometryError,
    MissingAttributeError,
    provenance_note,
    require,
    spec_table,
)
from .profiles import CARD, Profile

__all__ = [
    "DrillGeometry",
    "ImpossibleGeometryError",
    "MissingAttributeError",
    "build",
    "geometry_from_record",
    "render",
]

FILL_V = 0.78
FILL_H = 0.26

#: Flute spacing and slant, as fractions of the drawn diameter. Conventional
#: representation: see the module docstring.
FLUTE_PITCH = 1.15
FLUTE_RISE = 1.55


@dataclass(frozen=True)
class DrillGeometry:
    """Every number the drawing uses, and nothing else."""

    dia: Length
    shank_d: Length
    flute_len: Length
    oal: Length
    point_deg: float

    @property
    def max_d(self) -> float:
        return max(self.dia.inches, self.shank_d.inches)

    @property
    def point_height(self) -> float:
        """Axial height of the point cone, from its included angle and the diameter."""
        half = math.radians(self.point_deg / 2.0)
        return (self.dia.inches / 2.0) / math.tan(half)


def geometry_from_record(record: dict) -> DrillGeometry:
    geom = DrillGeometry(
        dia=parse_length(require(record, "Size")),
        shank_d=parse_length(require(record, "Shank Dia.")),
        flute_len=parse_length(require(record, "Flute Length")),
        oal=parse_length(require(record, "Overall Length")),
        point_deg=parse_included_angle_degrees(require(record, "Point Angle")),
    )
    if geom.flute_len.inches >= geom.oal.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: flute length {geom.flute_len.display()} is not "
            f"shorter than overall length {geom.oal.display()}; there is no shank to draw"
        )
    if geom.point_height >= geom.flute_len.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a {geom.point_deg:g} degree point on "
            f"{geom.dia.display()} is taller than the flute length {geom.flute_len.display()}"
        )
    return geom


def _draw_body(ax, geom: DrillGeometry) -> None:
    dia, shank_d = geom.dia.inches, geom.shank_d.inches
    oal, flute_len = geom.oal.inches, geom.flute_len.inches
    y_tip = -oal / 2.0
    cone = geom.point_height

    ax.add_patch(
        Rectangle(
            (-shank_d / 2, y_tip + flute_len),
            shank_d,
            oal - flute_len,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
    )
    fluted = Rectangle(
        (-dia / 2, y_tip + cone),
        dia,
        flute_len - cone,
        fc=cv.BODY_FILL,
        ec=cv.INK,
        lw=cv.LW_BODY,
        joinstyle="miter",
        zorder=2,
    )
    ax.add_patch(fluted)
    ax.add_patch(
        Polygon(
            [(-dia / 2, y_tip + cone), (0.0, y_tip), (dia / 2, y_tip + cone)],
            closed=True,
            fc=cv.BODY_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
    )

    rise = dia * FLUTE_RISE
    pitch = dia * FLUTE_PITCH
    y = y_tip + cone - rise
    while y < y_tip + flute_len:
        line = ax.plot(
            [-dia / 2, dia / 2],
            [y, y + rise],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE,
            zorder=3,
            solid_capstyle="butt",
        )[0]
        line.set_clip_path(fluted)
        y += pitch


def _draw_end_view(ax, geom: DrillGeometry) -> None:
    """The drill seen along the axis: the two diameters, and nothing invented.

    The lips and the chisel edge are not drawn. Their shape follows from a web
    thickness and a point grind, and a drill record publishes neither.
    """
    ax.add_patch(
        Circle(
            (0, 0),
            geom.shank_d.inches / 2,
            fill=False,
            ec=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (5, 4)),
            zorder=2,
        )
    )
    ax.add_patch(
        Circle((0, 0), geom.dia.inches / 2, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=3)
    )
    ax.plot([0], [0], marker="+", color=cv.MUTED, ms=5, mew=cv.LW_FLUTE)


def _frame_height(fig, rect, geom: DrillGeometry) -> float:
    by_length = geom.oal.inches / FILL_V
    box_ratio = cv.frame_width(fig, rect, 1.0)
    by_width = (geom.max_d / FILL_H) / box_ratio
    return max(by_length, by_width)


def _render_card(record: dict, geom: DrillGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.0, 0.0, 1.0, 1.0)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_body(ax, geom)

    y_tip = -geom.oal.inches / 2
    overhang = frame_w * 0.05
    gap = frame_w * 0.035
    cv.diameter_callout(
        ax,
        y_tip + geom.flute_len.inches * 0.45,
        geom.dia.inches,
        f"Ø{geom.dia.display()}",
        "drill size",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + geom.flute_len.inches + (geom.oal.inches - geom.flute_len.inches) * 0.55,
        geom.shank_d.inches,
        f"Ø{geom.shank_d.display()}",
        "shank",
        side=-1,
        overhang=overhang,
        gap=gap,
    )
    ax.text(
        0,
        -frame_h * 0.47,
        str(record.get("sku", "")),
        ha="center",
        va="bottom",
        color=cv.MUTED,
        fontsize=cv.FS_FOOT,
    )
    return fig, ax


def _render_detail(record: dict, geom: DrillGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.50, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_body(ax, geom)

    oal, flute_len = geom.oal.inches, geom.flute_len.inches
    dia, shank_d = geom.dia.inches, geom.shank_d.inches
    y_tip = -oal / 2
    overhang = frame_w * 0.04
    gap = frame_w * 0.03

    x_oal = -frame_w * 0.42
    cv.length_dimension(ax, x_oal, y_tip, y_tip + oal, geom.oal.display())
    cv.witness(ax, x_oal, -shank_d / 2, y_tip + oal)
    cv.witness(ax, x_oal, 0.0, y_tip)
    ax.text(
        x_oal - frame_w * 0.055,
        0,
        "overall length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    x_flute = -frame_w * 0.26
    cv.length_dimension(ax, x_flute, y_tip, y_tip + flute_len, geom.flute_len.display())
    cv.witness(ax, x_flute, -dia / 2, y_tip + flute_len)
    ax.text(
        x_flute - frame_w * 0.055,
        y_tip + flute_len / 2,
        "flute length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    cv.diameter_callout(
        ax,
        y_tip + flute_len * 0.55,
        dia,
        f"Ø{geom.dia.display()}",
        "drill size",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + oal - (oal - flute_len) * 0.35,
        shank_d,
        f"Ø{geom.shank_d.display()}",
        "shank dia.",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.included_angle_callout(
        ax,
        (0.0, y_tip),
        geom.point_deg / 2.0,
        geom.point_height * 0.72,
        str(record.get("Point Angle", "")),
        drop=frame_h * 0.055,
    )

    end_rect = (0.62, 0.55, 0.30, 0.30)
    ax_end = cv.frame_axes(fig, end_rect, geom.max_d * 2.2)
    _draw_end_view(ax_end, geom)
    ax_end.text(
        0,
        -geom.max_d * 1.0,
        "end view",
        ha="center",
        va="top",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    fig.text(
        0.04,
        0.955,
        str(record.get("Item", "Drill Bit")),
        fontsize=cv.FS_TITLE,
        fontweight="bold",
        color=cv.INK,
    )
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    spec_table(
        fig,
        [
            ("Size", geom.dia.display()),
            ("Decimal Equivalent", record.get("Decimal Equivalent", "")),
            ("Shank Dia.", geom.shank_d.display()),
            ("Flute Length", geom.flute_len.display()),
            ("Overall Length", geom.oal.display()),
            ("Point Angle", record.get("Point Angle", "")),
            ("Point Type", record.get("Point Type", "")),
            ("Shank Type", record.get("Shank Type", "")),
            ("Material", record.get("Material", "")),
            ("Finish", record.get("Finish", "")),
            ("Cutting Direction", record.get("Cutting Direction", "")),
        ],
    )
    provenance_note(fig)
    return fig, ax


def build(record: dict, profile: Profile = CARD):
    """Build the figure without writing it: ``(figure, elevation axes, geometry)``."""
    geom = geometry_from_record(record)
    builder = _render_detail if profile.verbose else _render_card
    fig, ax = builder(record, geom, profile)
    return fig, ax, geom


def render(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    fig, _, _ = build(record, profile)
    return cv.save(fig, path, profile)
