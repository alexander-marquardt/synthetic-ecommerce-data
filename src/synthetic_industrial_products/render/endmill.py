"""Dimensioned end-mill drawing, derived entirely from a product record.

The tool stands vertically, shank up and cutting end down: that is how the
industry draws one, and it is the only orientation in which a long thin tool
fills a portrait card.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Rectangle

from ..dimensions import Length, parse_angle_degrees, parse_count, parse_length
from . import canvas as cv
from .profiles import CARD, Profile

#: Fraction of the frame height the tool occupies, and the largest fraction of
#: the frame width its widest diameter may take before the tool is scaled down
#: to leave room for the callouts.
FILL_V = 0.78
FILL_H = 0.30


class MissingAttributeError(KeyError):
    """The record does not carry an attribute the drawing needs."""


class ImpossibleGeometryError(ValueError):
    """The record's own dimensions contradict each other."""


@dataclass(frozen=True)
class EndMillGeometry:
    """Every number the drawing uses, and nothing else."""

    cut_d: Length
    shank_d: Length
    loc: Length
    oal: Length
    flutes: int
    helix_deg: float

    @property
    def max_d(self) -> float:
        return max(self.cut_d.inches, self.shank_d.inches)

    @property
    def shoulder(self) -> float:
        """Height of the flute/shank boundary above the cutting tip, in inches."""
        return self.loc.inches

    @property
    def axial_flute_pitch(self) -> float:
        """Axial distance between successive flute edges on the visible face.

        A helix of angle ``h`` on a cylinder of diameter ``d`` advances
        ``pi * d / tan(h)`` per turn; with ``n`` flutes an edge crosses the
        visible face every ``1/n`` of that. Drawing the flutes at any other
        spacing would make helix angle and flute count decorative.
        """
        lead = math.pi * self.cut_d.inches / math.tan(math.radians(self.helix_deg))
        return lead / self.flutes


def _require(record: dict, key: str) -> str:
    try:
        return record[key]
    except KeyError as exc:
        raise MissingAttributeError(
            f"record {record.get('sku', '?')!r} has no {key!r}; the drawing needs it"
        ) from exc


def geometry_from_record(record: dict) -> EndMillGeometry:
    geom = EndMillGeometry(
        cut_d=parse_length(_require(record, "Milling Dia.")),
        shank_d=parse_length(_require(record, "Shank Dia.")),
        loc=parse_length(_require(record, "Length of Cut")),
        oal=parse_length(_require(record, "Overall Length")),
        flutes=parse_count(_require(record, "Number of Flutes")),
        helix_deg=parse_angle_degrees(_require(record, "Helix Angle")),
    )
    if geom.loc.inches >= geom.oal.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: length of cut {geom.loc.display()} is not "
            f"shorter than overall length {geom.oal.display()}; there is no shank to draw"
        )
    return geom


def _draw_body(ax, geom: EndMillGeometry) -> None:
    """Silhouette plus flutes, centred on the origin."""
    cut_d, shank_d = geom.cut_d.inches, geom.shank_d.inches
    oal, loc = geom.oal.inches, geom.loc.inches
    y_tip = -oal / 2.0

    shank = Rectangle(
        (-shank_d / 2, y_tip + loc),
        shank_d,
        oal - loc,
        fc=cv.SHANK_FILL,
        ec=cv.INK,
        lw=cv.LW_BODY,
        joinstyle="miter",
        zorder=2,
    )
    cutting = Rectangle(
        (-cut_d / 2, y_tip),
        cut_d,
        loc,
        fc=cv.BODY_FILL,
        ec=cv.INK,
        lw=cv.LW_BODY,
        joinstyle="miter",
        zorder=2,
    )
    ax.add_patch(shank)
    ax.add_patch(cutting)

    # Flutes: right-hand helix, rising to the right, at the pitch the helix
    # angle and flute count imply. Clipped to the cutting portion -- a flute
    # that ran on into the shank would be drawing a tool that does not exist.
    rise = cut_d / math.tan(math.radians(geom.helix_deg))
    pitch = geom.axial_flute_pitch
    y = y_tip - rise
    while y < y_tip + loc:
        line = ax.plot(
            [-cut_d / 2, cut_d / 2],
            [y, y + rise],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE,
            zorder=3,
            solid_capstyle="butt",
        )[0]
        line.set_clip_path(cutting)
        y += pitch


def _draw_end_view(ax, geom: EndMillGeometry) -> None:
    """The cutting end seen along the axis: both diameters, and the flute count."""
    r_cut = geom.cut_d.inches / 2
    r_shank = geom.shank_d.inches / 2
    ax.add_patch(
        Circle(
            (0, 0),
            r_shank,
            fill=False,
            ec=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (5, 4)),
            zorder=2,
        )
    )
    ax.add_patch(Circle((0, 0), r_cut, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=3))
    for k in range(geom.flutes):
        theta = 2 * math.pi * k / geom.flutes
        ax.plot(
            [0, r_cut * math.cos(theta)],
            [0, r_cut * math.sin(theta)],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE * 1.3,
            zorder=4,
            solid_capstyle="butt",
        )
    ax.plot([0], [0], marker="+", color=cv.MUTED, ms=5, mew=cv.LW_FLUTE)


def _frame_height(fig, rect, geom: EndMillGeometry) -> float:
    by_length = geom.oal.inches / FILL_V
    box_ratio = cv.frame_width(fig, rect, 1.0)
    by_width = (geom.max_d / FILL_H) / box_ratio
    return max(by_length, by_width)


def _render_card(record: dict, geom: EndMillGeometry, profile: Profile):
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
        y_tip + geom.loc.inches * 0.45,
        geom.cut_d.inches,
        f"Ø{geom.cut_d.display()}",
        "milling",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + geom.loc.inches + (geom.oal.inches - geom.loc.inches) * 0.55,
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


def _render_detail(record: dict, geom: EndMillGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.50, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_body(ax, geom)

    oal, loc = geom.oal.inches, geom.loc.inches
    cut_d, shank_d = geom.cut_d.inches, geom.shank_d.inches
    y_tip = -oal / 2
    overhang = frame_w * 0.04
    gap = frame_w * 0.03

    # Both length dimensions stack on the left, shortest nearest the tool, and
    # both diameter callouts go right: no label can land on another dimension.
    x_oal = -frame_w * 0.42
    cv.length_dimension(ax, x_oal, y_tip, y_tip + oal, geom.oal.display())
    cv.witness(ax, x_oal, -shank_d / 2, y_tip + oal)
    cv.witness(ax, x_oal, -cut_d / 2, y_tip)
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

    x_loc = -frame_w * 0.26
    cv.length_dimension(ax, x_loc, y_tip, y_tip + loc, geom.loc.display())
    cv.witness(ax, x_loc, -cut_d / 2, y_tip + loc)
    ax.text(
        x_loc - frame_w * 0.055,
        y_tip + loc / 2,
        "length of cut",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    cv.diameter_callout(
        ax,
        y_tip + loc * 0.5,
        cut_d,
        f"Ø{geom.cut_d.display()}",
        "milling dia.",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + oal - (oal - loc) * 0.35,
        shank_d,
        f"Ø{geom.shank_d.display()}",
        "shank dia.",
        side=1,
        overhang=overhang,
        gap=gap,
    )

    end_rect = (0.62, 0.55, 0.30, 0.30)
    ax_end = cv.frame_axes(fig, end_rect, geom.max_d * 2.2)
    _draw_end_view(ax_end, geom)
    ax_end.text(
        0,
        -geom.max_d * 1.0,
        f"end view · {geom.flutes} flutes",
        ha="center",
        va="top",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    title = f"{record.get('Item', 'End Mill')}"
    fig.text(0.04, 0.955, title, fontsize=cv.FS_TITLE, fontweight="bold", color=cv.INK)
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    specs = [
        ("Milling Dia.", geom.cut_d.display()),
        ("Shank Dia.", geom.shank_d.display()),
        ("Length of Cut", geom.loc.display()),
        ("Overall Length", geom.oal.display()),
        ("Number of Flutes", str(geom.flutes)),
        ("Helix Angle", record.get("Helix Angle", "")),
        ("Finish", record.get("Finish", "")),
    ]
    y = 0.44
    for name, value in specs:
        if not value:
            continue
        fig.text(0.62, y, name, fontsize=cv.FS_SPEC, color=cv.MUTED)
        fig.text(
            0.955, y, str(value), fontsize=cv.FS_SPEC, color=cv.INK, fontweight="bold", ha="right"
        )
        y -= 0.042
    fig.text(
        0.04,
        0.018,
        "drawn from this record's attribute values",
        fontsize=cv.FS_FOOT,
        color=cv.MUTED,
        style="italic",
    )
    return fig, ax


def build(record: dict, profile: Profile = CARD):
    """Build the figure without writing it: ``(figure, elevation axes, geometry)``.

    Exposed so a caller -- a test, or an embedder -- can measure the drawing in
    the figure's own coordinates instead of guessing at pixels.
    """
    geom = geometry_from_record(record)
    builder = _render_detail if profile.verbose else _render_card
    fig, ax = builder(record, geom, profile)
    return fig, ax, geom


def render(record: dict, path: str | Path, profile: Profile = CARD) -> Path:
    """Render ``record`` to ``path`` at ``profile``'s exact pixel size."""
    fig, _, _ = build(record, profile)
    return cv.save(fig, path, profile)
