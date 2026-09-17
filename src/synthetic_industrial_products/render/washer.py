"""Dimensioned flat-washer drawing, derived entirely from a product record.

A washer is the one product in this catalog whose drawing needs nothing the
record does not carry: ``Inside Dia.``, ``Outside Dia.`` and ``Thickness`` come
from the washer standard the line is built to and are published on every SKU.
So the type drawing is reached here only through a value that cannot be read or
a pair that contradicts itself, never through sparsity.

Two views, because one is not enough: the face view is the only place the bore
is a circle rather than two hidden lines, and the edge view is the only place
the thickness is a length rather than a foreshortened nothing.

Both diameters are dimensioned on the **edge** view, above it and below it, and
neither is dimensioned on the face. On the face they would have to be drawn
across the part, and on a 150-pixel-wide card the value would then sit on top
of the thing it measures. On the edge view each diameter is a horizontal extent
of what is drawn -- the full width for the outside, the two hidden bore lines
for the inside -- so the dimension lines land in clear paper and the face view
is left to show the shape.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Rectangle

from ..dimensions import Length, parse_length
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
    "ImpossibleGeometryError",
    "MissingAttributeError",
    "WasherGeometry",
    "build",
    "geometry_from_record",
    "render",
]

FILL_V = 0.84
FILL_H = 0.54

#: Gap between the face view and the edge view below it, in outside diameters.
#: The inside-diameter dimension line lives in it.
EDGE_VIEW_GAP = 0.52
#: Room kept below the edge view for the outside-diameter dimension line, in
#: outside diameters. Counted into the content height so the stack stays
#: centred on the frame rather than on the two views alone.
DIM_ZONE = 0.40


@dataclass(frozen=True)
class WasherGeometry:
    """Every number the drawing uses, and nothing else."""

    inside_d: Length
    outside_d: Length
    thickness: Length

    @property
    def content_height(self) -> float:
        """Face view, the gap, the edge view, and the dimension line below it."""
        od = self.outside_d.inches
        return od + EDGE_VIEW_GAP * od + self.thickness.inches + DIM_ZONE * od


def geometry_from_record(record: dict) -> WasherGeometry:
    geom = WasherGeometry(
        inside_d=parse_length(require(record, "Inside Dia.")),
        outside_d=parse_length(require(record, "Outside Dia.")),
        thickness=parse_length(require(record, "Thickness")),
    )
    if geom.inside_d.inches >= geom.outside_d.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: inside diameter {geom.inside_d.display()} is not "
            f"smaller than outside diameter {geom.outside_d.display()}; there is no washer left"
        )
    return geom


def _layout(geom: WasherGeometry) -> tuple[float, float]:
    """``(face centre y, edge view top y)``, with the pair centred on the origin."""
    od = geom.outside_d.inches
    top = geom.content_height / 2.0
    face_centre = top - od / 2.0
    edge_top = top - od - EDGE_VIEW_GAP * od
    return face_centre, edge_top


def _draw_views(ax, geom: WasherGeometry) -> None:
    r_out = geom.outside_d.inches / 2
    r_in = geom.inside_d.inches / 2
    thk = geom.thickness.inches
    face_centre, edge_top = _layout(geom)

    ax.add_patch(
        Circle((0, face_centre), r_out, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=2)
    )
    ax.add_patch(Circle((0, face_centre), r_in, fc=cv.PAPER, ec=cv.INK, lw=cv.LW_BODY, zorder=3))
    ax.plot([0], [face_centre], marker="+", color=cv.MUTED, ms=5, mew=cv.LW_FLUTE)

    ax.add_patch(
        Rectangle(
            (-r_out, edge_top - thk),
            r_out * 2,
            thk,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
    )
    # The bore through the edge view: hidden, because it is behind the section
    # the viewer is looking at.
    for sign in (-1, 1):
        ax.plot(
            [sign * r_in, sign * r_in],
            [edge_top - thk, edge_top],
            color=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (4, 3)),
            zorder=3,
        )


def _dimension(ax, geom: WasherGeometry, frame_w: float, frame_h: float) -> None:
    """The two diameters, on both profiles: they are what a washer is."""
    od = geom.outside_d.inches
    r_in = geom.inside_d.inches / 2
    _, edge_top = _layout(geom)
    overhang = frame_w * 0.045
    lift = frame_h * 0.010

    # Inside diameter, in the gap above the edge view, carried up from the two
    # hidden bore lines.
    y_id = edge_top + EDGE_VIEW_GAP * od * 0.30
    for sign in (-1, 1):
        cv.extension_line(ax, sign * r_in, edge_top, y_id)
    cv.centred_diameter_callout(
        ax,
        y_id,
        geom.inside_d.inches,
        f"Ø{geom.inside_d.display()}",
        "inside dia.",
        overhang=overhang,
        lift=lift,
    )
    # Outside diameter, below the edge view, where it is the drawn width.
    cv.centred_diameter_callout(
        ax,
        edge_top - geom.thickness.inches - DIM_ZONE * od * 0.46,
        od,
        f"Ø{geom.outside_d.display()}",
        "outside dia.",
        overhang=overhang,
        lift=lift,
    )


def _frame_height(fig, rect, geom: WasherGeometry) -> float:
    box_ratio = cv.frame_width(fig, rect, 1.0)
    by_height = geom.content_height / FILL_V
    by_width = (geom.outside_d.inches / FILL_H) / box_ratio
    return max(by_height, by_width)


def _render_card(record: dict, geom: WasherGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.0, 0.0, 1.0, 1.0)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_views(ax, geom)
    _dimension(ax, geom, frame_w, frame_h)
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


def _render_detail(record: dict, geom: WasherGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.52, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_views(ax, geom)
    _dimension(ax, geom, frame_w, frame_h)

    # Thickness, which only the edge view can carry, off to the right of it.
    _, edge_top = _layout(geom)
    thk = geom.thickness.inches
    r_out = geom.outside_d.inches / 2
    x_thk = r_out + frame_w * 0.12
    cv.length_dimension(ax, x_thk, edge_top - thk, edge_top, geom.thickness.display())
    cv.witness(ax, r_out, x_thk, edge_top)
    cv.witness(ax, r_out, x_thk, edge_top - thk)
    ax.text(
        x_thk + frame_w * 0.055,
        edge_top - thk / 2,
        "thickness",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    fig.text(
        0.04,
        0.955,
        str(record.get("Item", "Flat Washer")),
        fontsize=cv.FS_TITLE,
        fontweight="bold",
        color=cv.INK,
    )
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    spec_table(
        fig,
        [
            ("Washer Size", record.get("Washer Size", "")),
            ("Inside Dia.", geom.inside_d.display()),
            ("Outside Dia.", geom.outside_d.display()),
            ("Thickness", geom.thickness.display()),
            ("Washer Type", record.get("Washer Type", "")),
            ("Fastener Material", record.get("Fastener Material", "")),
            ("Fastener Finish", record.get("Fastener Finish", "")),
        ],
    )
    provenance_note(fig)
    return fig, ax


def build(record: dict, profile: Profile = CARD):
    """Build the figure without writing it: ``(figure, axes, geometry)``."""
    geom = geometry_from_record(record)
    builder = _render_detail if profile.verbose else _render_card
    fig, ax = builder(record, geom, profile)
    return fig, ax, geom


def render(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    fig, _, _ = build(record, profile)
    return cv.save(fig, path, profile)
