"""Drawn forms that more than one renderer needs.

A thread is a thread whether it is cut on a cap screw or on a tap, and two
copies of the same drawing code are two chances to draw the same feature two
ways. The forms here take the numbers they need as arguments rather than a
geometry object, so nothing about one product type leaks into another's
drawing.
"""

from __future__ import annotations

from matplotlib.patches import Rectangle

from . import canvas as cv


def draw_thread(
    ax, *, major_in: float, minor_in: float, pitch_in: float, y_from: float, length: float
) -> None:
    """A 60-degree thread form at the pitch the designation states.

    Both flanks are drawn as one zig-zag each, half a pitch out of phase, and
    clipped to the threaded run: the pitch comes from the thread designation,
    so a drawing at any other pitch would make the designation decorative.
    """
    r_major = major_in / 2
    r_minor = minor_in / 2
    top = y_from + length

    for x_sign, phase in ((-1, 0.0), (1, 0.5)):
        xs: list[float] = []
        ys: list[float] = []
        y = y_from - pitch_in
        while y < top + pitch_in:
            xs.extend([x_sign * r_minor, x_sign * r_major])
            ys.extend([y + phase * pitch_in, y + (phase + 0.5) * pitch_in])
            y += pitch_in
        clip = Rectangle(
            (-r_major * 1.02, y_from),
            r_major * 2.04,
            length,
            transform=ax.transData,
        )
        line = ax.plot(
            xs, ys, color=cv.INK, lw=cv.LW_BODY * 0.55, zorder=4, solid_joinstyle="miter"
        )[0]
        line.set_clip_path(clip)


def thread_roots(ax, *, minor_in: float, y_from: float, length: float) -> None:
    """The thread root lines either side of a threaded run."""
    r_minor = minor_in / 2
    for sign in (-1, 1):
        ax.plot(
            [sign * r_minor, sign * r_minor],
            [y_from, y_from + length],
            color=cv.MUTED,
            lw=cv.LW_HIDDEN,
            zorder=3,
        )
