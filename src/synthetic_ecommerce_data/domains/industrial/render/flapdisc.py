"""Dimensioned flap-disc drawing, derived entirely from a product record.

What is drawn and what is not
-----------------------------
* The **disc diameter** and the **arbor hole** are published, and are the two
  dimensions on the drawing.
* There is **no edge view**. A flap disc record publishes ``Flap Disc Shape``
  -- Type 27 flat or Type 29 conical -- but no thickness and no cone angle, so
  an edge view would be a profile drawn to numbers the record does not carry.
  The shape appears in the attribute table, where it is the record's own word
  for itself, and not as a drawn form.
* The **flaps** are a surface indication, not a count. How many flaps a disc
  carries is not an attribute of any record here; what is drawn is the
  overlapping-leaf texture at a fixed spacing, the way drafting indicates a
  knurl or a thread without claiming a pitch. No dimension points at them.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from matplotlib.patches import Circle

from synthetic_ecommerce_data.core.dimensions import Length, parse_length
from synthetic_ecommerce_data.domains.industrial.render import canvas as cv
from synthetic_ecommerce_data.domains.industrial.render.attrs import (
    ImpossibleGeometryError,
    MissingAttributeError,
    provenance_note,
    require,
    spec_table,
)
from synthetic_ecommerce_data.domains.industrial.render.profiles import CARD, Profile

__all__ = [
    "FlapDiscGeometry",
    "ImpossibleGeometryError",
    "MissingAttributeError",
    "build",
    "geometry_from_record",
    "render",
]

FILL_V = 0.86
FILL_H = 0.54

#: Flap indication: how many leaves are drawn, and how far each one leans, as a
#: multiple of the angular step. Constants of this module -- see the docstring.
FLAP_MARKS = 48
FLAP_LEAN = 2.6
#: Where the flaps start, as a fraction of the disc radius.
FLAP_INNER = 0.42

#: Room kept above and below the disc for its two dimension lines, in disc
#: diameters, and counted into the content height so the disc stays centred.
DIM_ZONE = 0.42


@dataclass(frozen=True)
class FlapDiscGeometry:
    """Every number the drawing uses, and nothing else."""

    disc_d: Length
    arbor_d: Length


def geometry_from_record(record: dict) -> FlapDiscGeometry:
    geom = FlapDiscGeometry(
        disc_d=parse_length(require(record, "Diameter")),
        arbor_d=parse_length(require(record, "Arbor Hole")),
    )
    if geom.arbor_d.inches >= geom.disc_d.inches:
        raise ImpossibleGeometryError(
            f"record {record.get('sku', '?')!r}: an arbor hole of {geom.arbor_d.display()} is not "
            f"smaller than the {geom.disc_d.display()} disc it is in"
        )
    return geom


def _draw_face(ax, geom: FlapDiscGeometry) -> None:
    r_out = geom.disc_d.inches / 2
    r_arbor = geom.arbor_d.inches / 2
    r_flap = max(r_out * FLAP_INNER, r_arbor * 1.25)

    ax.add_patch(Circle((0, 0), r_out, fc=cv.BODY_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=2))
    lean = 2 * math.pi * FLAP_LEAN / FLAP_MARKS
    for k in range(FLAP_MARKS):
        theta = 2 * math.pi * k / FLAP_MARKS
        ax.plot(
            [r_flap * math.cos(theta), r_out * math.cos(theta + lean)],
            [r_flap * math.sin(theta), r_out * math.sin(theta + lean)],
            color=cv.FLUTE,
            lw=cv.LW_FLUTE * 0.8,
            zorder=3,
            solid_capstyle="butt",
        )
    ax.add_patch(Circle((0, 0), r_flap, fc=cv.SHANK_FILL, ec=cv.INK, lw=cv.LW_BODY, zorder=4))
    ax.add_patch(Circle((0, 0), r_arbor, fc=cv.PAPER, ec=cv.INK, lw=cv.LW_BODY, zorder=5))
    ax.plot([0], [0], marker="+", color=cv.MUTED, ms=5, mew=cv.LW_FLUTE)


def _dimension(ax, geom: FlapDiscGeometry, frame_w: float, frame_h: float) -> None:
    r_out = geom.disc_d.inches / 2
    r_arbor = geom.arbor_d.inches / 2
    overhang = frame_w * 0.045
    lift = frame_h * 0.010

    # Arbor hole, carried up out of the disc to its own dimension line. Drawn
    # across the hole itself the value would cover the hole, which on a
    # 150-pixel-wide card is the whole feature.
    y_arbor = r_out + DIM_ZONE * geom.disc_d.inches * 0.58
    for sign in (-1, 1):
        cv.extension_line(ax, sign * r_arbor, 0.0, y_arbor)
    cv.centred_diameter_callout(
        ax,
        y_arbor,
        geom.arbor_d.inches,
        f"Ø{geom.arbor_d.display()}",
        "arbor hole",
        overhang=overhang,
        lift=lift,
    )
    # Disc diameter, on its own dimension line clear below the disc.
    cv.centred_diameter_callout(
        ax,
        -r_out - DIM_ZONE * geom.disc_d.inches * 0.48,
        geom.disc_d.inches,
        f"Ø{geom.disc_d.display()}",
        "disc dia.",
        overhang=overhang,
        lift=lift,
    )


def _frame_height(fig, rect, geom: FlapDiscGeometry) -> float:
    box_ratio = cv.frame_width(fig, rect, 1.0)
    content = geom.disc_d.inches * (1.0 + 2 * DIM_ZONE)
    by_height = content / FILL_V
    by_width = (geom.disc_d.inches / FILL_H) / box_ratio
    return max(by_height, by_width)


def _render_card(record: dict, geom: FlapDiscGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.0, 0.0, 1.0, 1.0)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_face(ax, geom)
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


def _render_detail(record: dict, geom: FlapDiscGeometry, profile: Profile):
    fig = cv.new_figure(profile)
    rect = (0.04, 0.05, 0.52, 0.82)
    frame_h = _frame_height(fig, rect, geom)
    ax = cv.frame_axes(fig, rect, frame_h)
    frame_w = cv.frame_width(fig, rect, frame_h)

    _draw_face(ax, geom)
    _dimension(ax, geom, frame_w, frame_h)

    fig.text(
        0.04,
        0.955,
        str(record.get("Item", "Flap Disc")),
        fontsize=cv.FS_TITLE,
        fontweight="bold",
        color=cv.INK,
    )
    fig.text(0.04, 0.925, str(record.get("sku", "")), fontsize=cv.FS_SPEC, color=cv.MUTED)

    y = spec_table(
        fig,
        [
            ("Diameter", geom.disc_d.display()),
            ("Arbor Hole", geom.arbor_d.display()),
            ("Grit", record.get("Grit", "")),
            ("Max. RPM", record.get("Max. RPM", "")),
            ("Abrasive Material", record.get("Abrasive Material", "")),
            ("Backing Material", record.get("Backing Material", "")),
            ("Shape", record.get("Shape", "")),
            ("Mounting Type", record.get("Mounting Type", "")),
        ],
    )
    fig.text(
        0.62,
        y - 0.012,
        "edge profile: no thickness published, not drawn",
        fontsize=cv.FS_FOOT,
        color=cv.MUTED,
        style="italic",
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
