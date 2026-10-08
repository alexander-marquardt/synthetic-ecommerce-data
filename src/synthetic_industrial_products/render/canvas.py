"""Figure setup and the dimensioning primitives shared by every renderer."""

from __future__ import annotations

import io
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

#: Section hatching is line work, drawn at the weight of a thin line. Set here
#: rather than per-patch because matplotlib takes it from the rcParams at draw
#: time, so a per-figure override would be read after the figure was built.
matplotlib.rcParams["hatch.linewidth"] = 0.5

from matplotlib.backends.backend_agg import FigureCanvasAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402

from .profiles import Profile  # noqa: E402

INK = "#1b1b1b"
DIM = "#b03a2e"
FLUTE = "#5d6d7e"
MUTED = "#8b98a5"
#: Section hatching, lighter than the outline it sits inside: the hatch
#: describes what the part is made of and must not bury the part.
HATCH = "#aab4be"
SHANK_FILL = "#eef1f3"
BODY_FILL = "#fbfcfd"
PAPER = "white"

#: Point sizes, chosen for the 50 CSS-pixel-per-inch display scale both
#: profiles share: a 15 pt callout is about 10 CSS pixels tall on the 150 px card.
FS_CALLOUT = 15.0
FS_SUBLABEL = 8.5
FS_TITLE = 12.0
FS_SPEC = 9.0
FS_FOOT = 7.0

#: Dimensions are drawn over the subject, never under it. A round subject has
#: its dimension lines inside its own outline, and a callout that lost a
#: z-order fight with the part it measures is a callout nobody can read.
Z_DIM = 8

LW_BODY = 2.4
LW_DIM = 1.2
LW_FLUTE = 1.6
LW_HIDDEN = 1.0


def new_figure(profile: Profile) -> Figure:
    fig = Figure(figsize=profile.figsize, dpi=profile.dpi, facecolor=PAPER)
    # Attach the raster canvas up front so a caller can read the figure's own
    # pixels without going through a file.
    FigureCanvasAgg(fig)
    return fig


def frame_axes(fig: Figure, rect: tuple[float, float, float, float], frame_height: float):
    """An axes filling ``rect`` whose data limits are centred on the origin.

    The limits are given the same ratio as the axes box, so x and y are at
    equal scale without ``set_aspect`` -- which would shrink the box away from
    the rectangle and put the drawing off centre. Centring the data limits on
    zero is what keeps the subject centred in the frame no matter how much room
    the dimension labels take on one side.
    """
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    fig_w, fig_h = fig.get_size_inches()
    box_ratio = (rect[2] * fig_w) / (rect[3] * fig_h)
    half_h = frame_height / 2.0
    half_w = half_h * box_ratio
    ax.set_xlim(-half_w, half_w)
    ax.set_ylim(-half_h, half_h)
    return ax


def frame_width(fig: Figure, rect: tuple[float, float, float, float], frame_height: float) -> float:
    fig_w, fig_h = fig.get_size_inches()
    return frame_height * (rect[2] * fig_w) / (rect[3] * fig_h)


def _diameter_arrow(ax, y, diameter, overhang, zorder=None):
    """The dimension line across a diameter, with a tick at each extreme."""
    x0, x1 = -diameter / 2, diameter / 2
    extra = {} if zorder is None else {"zorder": zorder}
    ax.annotate(
        "",
        xy=(x0 - overhang, y),
        xytext=(x1 + overhang, y),
        arrowprops=dict(arrowstyle="<->", color=DIM, lw=LW_DIM, shrinkA=0, shrinkB=0),
        **extra,
    )
    for x in (x0, x1):
        ax.plot(
            [x, x], [y - overhang * 0.6, y + overhang * 0.6], color=DIM, lw=LW_DIM * 0.7, **extra
        )
    return x0, x1


def centred_diameter_callout(ax, y, diameter, label, sub, overhang, lift, fontsize=FS_CALLOUT):
    """A diameter dimension with the value centred on its own line.

    This is the ISO placement -- value above the dimension line, centred on it
    -- and it is what a round subject needs. A side-placed label on a disc has
    to clear the disc before it starts, so on a 150-pixel-wide card the two
    labels a washer needs run off both edges; centred, they cannot, whatever
    the value's length. Both texts sit on a paper-colored box so they stay
    legible where they cross the subject.
    """
    _diameter_arrow(ax, y, diameter, overhang, zorder=Z_DIM)
    ax.text(
        0,
        y + lift,
        label,
        ha="center",
        va="bottom",
        color=DIM,
        fontsize=fontsize,
        fontweight="bold",
        zorder=Z_DIM,
    )
    if sub:
        ax.text(
            0,
            y - lift * 0.7,
            sub,
            ha="center",
            va="top",
            color=MUTED,
            fontsize=FS_SUBLABEL,
            zorder=Z_DIM,
        )


def diameter_callout(ax, y, diameter, label, sub, side, overhang, gap, fontsize=FS_CALLOUT):
    """A double-headed arrow across a diameter, labelled off to one side.

    ``side`` is -1 to put the label left of the subject, +1 to put it right.
    """
    x0, x1 = _diameter_arrow(ax, y, diameter, overhang)
    text_x = (x1 + overhang + gap) if side > 0 else (x0 - overhang - gap)
    ha = "left" if side > 0 else "right"
    ax.text(text_x, y, label, ha=ha, va="center", color=DIM, fontsize=fontsize, fontweight="bold")
    if sub:
        # The leading newline reserves the value's own line, so the sub-label
        # lands directly under it without measuring the rendered text.
        ax.text(
            text_x,
            y,
            "\n" + sub,
            ha=ha,
            va="top",
            color=MUTED,
            fontsize=FS_SUBLABEL,
        )


def length_dimension(ax, x, y0, y1, label, fontsize=FS_SPEC):
    """A vertical dimension line beside the subject, with witness lines back to it."""
    ax.annotate(
        "",
        xy=(x, y0),
        xytext=(x, y1),
        arrowprops=dict(arrowstyle="<->", color=DIM, lw=LW_DIM, shrinkA=0, shrinkB=0),
    )
    ax.text(
        x,
        (y0 + y1) / 2,
        label,
        ha="center",
        va="center",
        rotation=90,
        color=DIM,
        fontsize=fontsize,
        fontweight="bold",
        backgroundcolor=PAPER,
    )


def included_angle_callout(ax, apex, half_angle_deg, radius, label, drop, fontsize=FS_SPEC):
    """An angular dimension on the cone meeting at ``apex``, opening upwards.

    The arc is struck inside the cone, where it can only be read against the
    two flanks it spans; the value is set below the apex, which on a tool drawn
    tip-down is the one place near the point with nothing else in it. The
    leader ties the two together so the number is not left floating.
    """
    x0, y0 = apex
    start, end = 90.0 - half_angle_deg, 90.0 + half_angle_deg
    steps = 48
    xs = [
        x0 + radius * math.cos(math.radians(start + (end - start) * k / steps))
        for k in range(steps + 1)
    ]
    ys = [
        y0 + radius * math.sin(math.radians(start + (end - start) * k / steps))
        for k in range(steps + 1)
    ]
    ax.plot(xs, ys, color=DIM, lw=LW_DIM, zorder=7)
    ax.plot([x0, x0], [y0, y0 - drop * 0.8], color=DIM, lw=LW_DIM * 0.7, zorder=7)
    ax.text(
        x0,
        y0 - drop,
        label,
        ha="center",
        va="top",
        color=DIM,
        fontsize=fontsize,
        fontweight="bold",
    )


def witness(ax, x_from, x_to, y):
    ax.plot([x_from, x_to], [y, y], color=DIM, lw=LW_DIM * 0.6, ls=(0, (4, 3)), alpha=0.8)


def extension_line(ax, x, y_from, y_to):
    """A vertical extension line, carrying a feature out to its dimension line."""
    ax.plot(
        [x, x],
        [y_from, y_to],
        color=DIM,
        lw=LW_DIM * 0.6,
        ls=(0, (4, 3)),
        alpha=0.8,
        zorder=Z_DIM,
    )


def to_bytes(fig: Figure, profile: Profile) -> bytes:
    """The PNG the figure makes, at exactly the profile's pixel size.

    ``bbox_inches="tight"`` is deliberately not used: it crops to the ink and
    so returns whatever size the labels happened to need, which is not a size
    the card can rely on. The software metadata is suppressed so the same
    figure makes the same bytes on any machine -- which is what lets a caller
    compare two drawings by comparing two files.
    """
    buffer = io.BytesIO()
    fig.savefig(
        buffer,
        format="png",
        dpi=profile.dpi,
        facecolor=PAPER,
        metadata={"Software": None},
    )
    return buffer.getvalue()


def save(fig: Figure, path: str | Path, profile: Profile) -> Path:
    """Write the PNG at exactly the profile's pixel size, byte-deterministically.

    The bytes come from :func:`to_bytes` rather than from a second call to
    ``savefig``: a caller comparing rendered files and a caller comparing
    rendered buffers must be comparing the same thing.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(to_bytes(fig, profile))
    return path
