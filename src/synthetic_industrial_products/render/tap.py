"""Dimensioned spiral-point-tap drawing, derived entirely from a product record.

What is drawn and what is not
-----------------------------
* The **thread** is drawn to the 60-degree form at the pitch the designation
  states, by the same code the cap-screw renderer uses. ``Thread Size`` is the
  only place a tap record carries a diameter for its threaded end, so a record
  whose designation cannot be read is refused.
* The **drive square** is not drawn on the elevation. A machine tap has one,
  but neither its across-flats nor its length follows from any attribute on the
  record -- ``Square Size`` exists in the vocabulary and no record generated so
  far carries it -- and a square drawn to a guessed width is a dimension the
  data cannot defend. Where the record *does* publish ``Square Size``, it
  appears in the end view at its true across-flats, which is exactly how the
  cap-screw renderer treats a socket drive whose depth is unpublished.
* The **chamfer** at the entering end is not drawn. ``Chamfer Style`` says
  plug, bottoming or taper; how many threads that is, is a table this record
  does not carry.
* The **flutes** appear in the end view when ``Number of Flutes`` is published,
  at that count, and nowhere else. Their width is not published, so they are
  drawn as edges.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle, Polygon, Rectangle

from ..dimensions import Length, Thread, parse_count, parse_length, parse_thread
from . import canvas as cv
from . import forms
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
    "TapGeometry",
    "build",
    "geometry_from_record",
    "render",
]

FILL_V = 0.78
FILL_H = 0.26


@dataclass(frozen=True)
class TapGeometry:
    """Every number the drawing uses, and nothing else."""

    thread: Thread
    shank_d: Length
    thread_len: Length
    oal: Length
    #: Present only when the record publishes it; the elevation never uses it.
    square: Length | None
    #: Present only when the record publishes it; the end view uses it.
    flutes: int | None

    @property
    def max_d(self) -> float:
        return max(self.thread.major.inches, self.shank_d.inches)


def _optional_length(record: dict, key: str) -> Length | None:
    raw = record.get(key)
    return parse_length(raw) if raw else None


def geometry_from_record(record: dict) -> TapGeometry:
    flutes_raw = record.get("Number of Flutes")
    geom = TapGeometry(
        thread=parse_thread(require(record, "Thread Size")),
        shank_d=parse_length(require(record, "Shank Dia.")),
        thread_len=parse_length(require(record, "Thread Length")),
        oal=parse_length(require(record, "Overall Length")),
        square=_optional_length(record, "Square Size"),
        flutes=parse_count(flutes_raw) if flutes_raw else None,
    )
    if geom.thread_len.inches >= geom.oal.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: thread length {geom.thread_len.display()} is not "
            f"shorter than overall length {geom.oal.display()}; there is no shank to draw"
        )
    if geom.square is not None and geom.square.inches > geom.shank_d.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: a {geom.square.display()} square will not fit "
            f"on a {geom.shank_d.display()} shank"
        )
    return geom


def _draw_body(ax, geom: TapGeometry) -> None:
    major = geom.thread.major.inches
    shank_d = geom.shank_d.inches
    oal, thread_len = geom.oal.inches, geom.thread_len.inches
    y_tip = -oal / 2.0

    ax.add_patch(
        Rectangle(
            (-shank_d / 2, y_tip + thread_len),
            shank_d,
            oal - thread_len,
            fc=cv.SHANK_FILL,
            ec=cv.INK,
            lw=cv.LW_BODY,
            joinstyle="miter",
            zorder=2,
        )
    )
    ax.add_patch(
        Rectangle(
            (-major / 2, y_tip),
            major,
            thread_len,
            fc=cv.BODY_FILL,
            ec="none",
            zorder=1,
        )
    )
    for sign in (-1, 1):
        ax.plot(
            [sign * major / 2, sign * major / 2],
            [y_tip, y_tip + thread_len],
            color=cv.INK,
            lw=cv.LW_BODY,
            zorder=3,
        )
    ax.plot([-major / 2, major / 2], [y_tip, y_tip], color=cv.INK, lw=cv.LW_BODY, zorder=3)
    forms.thread_roots(ax, minor_in=geom.thread.minor_in, y_from=y_tip, length=thread_len)
    forms.draw_thread(
        ax,
        major_in=major,
        minor_in=geom.thread.minor_in,
        pitch_in=geom.thread.pitch_in,
        y_from=y_tip,
        length=thread_len,
    )


def _draw_end_view(ax, geom: TapGeometry) -> None:
    """Looking down the shank: the shank circle, the square when published, the flutes."""
    r_shank = geom.shank_d.inches / 2
    ax.add_patch(Circle((0, 0), r_shank, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=3))
    ax.add_patch(
        Circle(
            (0, 0),
            geom.thread.major.inches / 2,
            fill=False,
            ec=cv.MUTED,
            lw=cv.LW_HIDDEN,
            ls=(0, (5, 4)),
            zorder=4,
        )
    )
    if geom.square is not None:
        half = geom.square.inches / 2
        ax.add_patch(
            Polygon(
                [(-half, -half), (-half, half), (half, half), (half, -half)],
                closed=True,
                fc=cv.SHANK_FILL,
                ec=cv.INK,
                lw=cv.LW_BODY * 0.8,
                zorder=5,
            )
        )
    if geom.flutes:
        for k in range(geom.flutes):
            theta = 2 * math.pi * k / geom.flutes
            ax.plot(
                [0, r_shank * math.cos(theta)],
                [0, r_shank * math.sin(theta)],
                color=cv.FLUTE,
                lw=cv.LW_FLUTE * 1.3,
                zorder=6,
                solid_capstyle="butt",
            )


def _frame_height(fig, rect, geom: TapGeometry) -> float:
    by_length = geom.oal.inches / FILL_V
    box_ratio = cv.frame_width(fig, rect, 1.0)
    return max(by_length, (geom.max_d / FILL_H) / box_ratio)


def _render_card(record: dict, geom: TapGeometry, profile: Profile):
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
        y_tip + geom.thread_len.inches * 0.45,
        geom.thread.major.inches,
        geom.thread.designation,
        "thread",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + geom.thread_len.inches + (geom.oal.inches - geom.thread_len.inches) * 0.55,
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


def _render_detail(record: dict, geom: TapGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.50, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_body(ax, geom)

    oal, thread_len = geom.oal.inches, geom.thread_len.inches
    major, shank_d = geom.thread.major.inches, geom.shank_d.inches
    y_tip = -oal / 2
    overhang = frame_w * 0.04
    gap = frame_w * 0.03

    x_oal = -frame_w * 0.42
    cv.length_dimension(ax, x_oal, y_tip, y_tip + oal, geom.oal.display())
    cv.witness(ax, x_oal, -shank_d / 2, y_tip + oal)
    cv.witness(ax, x_oal, -major / 2, y_tip)
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

    x_thr = -frame_w * 0.26
    cv.length_dimension(ax, x_thr, y_tip, y_tip + thread_len, geom.thread_len.display())
    cv.witness(ax, x_thr, -major / 2, y_tip + thread_len)
    ax.text(
        x_thr - frame_w * 0.055,
        y_tip + thread_len / 2,
        "thread length",
        rotation=90,
        ha="center",
        va="center",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    cv.diameter_callout(
        ax,
        y_tip + thread_len * 0.5,
        major,
        geom.thread.designation,
        "thread",
        side=1,
        overhang=overhang,
        gap=gap,
    )
    cv.diameter_callout(
        ax,
        y_tip + oal - (oal - thread_len) * 0.35,
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
    label = "end view" if not geom.flutes else f"end view · {geom.flutes} flutes"
    ax_end.text(
        0,
        -geom.max_d * 1.0,
        label,
        ha="center",
        va="top",
        color=cv.MUTED,
        fontsize=cv.FS_SUBLABEL,
    )

    fig.text(
        0.04,
        0.955,
        str(record.get("Item", "Tap")),
        fontsize=cv.FS_TITLE,
        fontweight="bold",
        color=cv.INK,
    )
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    y = spec_table(
        fig,
        [
            ("Thread Size", geom.thread.designation),
            ("Pitch", record.get("Pitch", "")),
            ("Overall Length", geom.oal.display()),
            ("Thread Length", geom.thread_len.display()),
            ("Shank Dia.", geom.shank_d.display()),
            ("Square Size", geom.square.display() if geom.square else ""),
            ("Number of Flutes", str(geom.flutes) if geom.flutes else ""),
            ("Tap Chamfer", record.get("Tap Chamfer", "")),
            ("Tap Style", record.get("Tap Style", "")),
            ("Material", record.get("Material", "")),
            ("Finish", record.get("Finish", "")),
            ("Thread Type", record.get("Thread Type", "")),
            ("Thread Direction", record.get("Thread Direction", "")),
        ],
    )
    if geom.square is None:
        fig.text(
            0.62,
            y - 0.012,
            "drive square: not published, not drawn",
            fontsize=cv.FS_FOOT,
            color=cv.MUTED,
            style="italic",
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
