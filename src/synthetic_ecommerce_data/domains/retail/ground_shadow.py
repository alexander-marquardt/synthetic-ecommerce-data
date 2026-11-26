"""The one shadow a product stands on, flat on the ground, level or turned (gen#1182).

A kit draws its shadow in its figure, and draws it by :func:`ellipse`, which labels it
``class="ground"``. Turning the drawing turned that shadow with it, and a tilted pile looked as if
it sat on a slope. :func:`turned` takes those ellipses out of the drawing and draws one in their
place, outside the turn: a soft ellipse, horizontal, its center line at the lowest point of the
turned drawing and its width that of the part of the drawing near the ground. A level picture,
in a house style or on the plain sheet, stands on the same one (an empty turn), so every
picture's shadow is drawn here and falls away from the one :data:`LIGHT`.

The drawing is measured by :func:`.sheet_extent.reaches`, which gives a box per lean and reads
the drawing once for all of them. Leaning the drawing a little each way and reading how low it
reaches gives the lines that hug its underside (:func:`_span`), so the footprint of a path is read
without a rasteriser.
"""

from __future__ import annotations

import functools
import math
import re

from synthetic_ecommerce_data.domains.retail import sheet_extent

#: The direction to the light, in sheet units (y grows downward): up and to the left, where the
#: produce kit's gloss has its highlight.
LIGHT = (-0.5, -1.0)
#: The share of the turned drawing's height, from its lowest point up, that casts the shadow.
BAND = 0.12
#: Sheet units the soft edge reaches past the footprint, each side.
PAD = 8.0
#: The shadow's height per unit of its width, and the least and most it is tall (half-heights).
FLATNESS, MIN_RY, MAX_RY = 0.075, 5.0, 12.0
#: The kit's sheet, in its units: a level drawing's shadow stays on it.
SHEET = 400.0
#: The black of the shadow's middle; its edge is clear.
OPACITY = 0.3
#: The leans, in degrees, the underside is measured at (each way): a product is turned by a multiple
#: of 12 or 15, so these hold the straight sides of most boxes exactly.
LEANS = (3, 12, 15, 24, 30, 36, 45, 54, 66, 90)

#: The shadow a kit draws in its figure.
GROUND = re.compile(r'<ellipse class="ground"[^>]*/>')
_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg"><defs>{0}</defs>'
    '<g transform="rotate({1})">{2}</g></svg>'
)


def ellipse(
    cx: float, cy: float, rx: float, ry: float, ink: str = "#000000", opacity: float = 0.08
) -> str:
    """The shadow a kit draws under its figure, labelled so :func:`turned` finds it and draws the
    flat one in its place. A kit marks its shadow by this, never by an unlabelled ellipse."""
    return (
        f'<ellipse class="ground" cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
        f'fill="{ink}" fill-opacity="{opacity:g}"/>'
    )


def turned(drawing: str, defs: str, transform: str, uid: str) -> tuple[str, str]:
    """(shadow, figure): ``drawing``'s figure without the shadow its kit drew, and the flat one
    to draw before it, outside ``transform`` (the product's turn). A drawing with no shadow
    gets none, and one that draws nothing to stand on it loses its shadow."""
    figure, shadows = GROUND.subn("", drawing)
    if not shadows:
        return "", drawing
    return _flat(figure, defs, transform, uid), figure


def turned_all(drawings: list[str], defs: str, transform: str, uid: str) -> tuple[list[str], str]:
    """(measured, product): each of ``drawings`` turned by ``transform`` with its shadow flat before
    it, for measuring, and the last of them, the SKU's own, in the group its picture draws. An
    empty ``transform`` is a level picture: the same shadow, and no turn group."""
    lifted = [turned(d, defs, transform, uid) for d in drawings]
    if not transform:
        return [shadow + figure for shadow, figure in lifted], "".join(lifted[-1])
    measured = [f'{shadow}<g transform="{transform}">{figure}</g>' for shadow, figure in lifted]
    shadow, figure = lifted[-1]
    return measured, f'{shadow}<g class="turn" transform="{transform}">{figure}</g>'


@functools.lru_cache(maxsize=256)  # every size rung of one colorway measures the same drawing
def _flat(figure: str, defs: str, transform: str, uid: str) -> str:
    body = f'<g transform="{transform}">{figure}</g>' if transform else figure
    foot = _footprint(defs, body)
    if foot is None:
        return ""
    left, right, low = foot
    rx = (right - left) / 2 + PAD
    ry = min(MAX_RY, max(MIN_RY, rx * FLATNESS))
    cx = (left + right) / 2 + ry * LIGHT[0] / LIGHT[1]
    if not transform:  # a level drawing is on its kit's own sheet, and its shadow keeps to it
        rx, ry = min(rx, cx, SHEET - cx), min(ry, SHEET - low)
    gid = f"ground-{uid}"
    return (
        f'<radialGradient id="{gid}">'
        f'<stop offset=".5" stop-color="#000000" stop-opacity="{OPACITY}"/>'
        f'<stop offset="1" stop-color="#000000" stop-opacity="0"/></radialGradient>'
        f'<ellipse class="ground" cx="{cx:.2f}" cy="{low:.2f}" rx="{rx:.2f}" '
        f'ry="{ry:.2f}" fill="url(#{gid})"/>'
    )


def _footprint(defs: str, body: str) -> tuple[float, float, float] | None:
    """(left, right, lowest y) of the part of ``body`` near the ground, or ``None`` when it draws
    nothing :func:`.sheet_extent.reach` measures."""
    angles = [a for lean in LEANS for a in (lean, -lean)]
    flat, *leaned = sheet_extent.reaches(_SVG.format(defs, 0, body), [0, *angles])
    if flat is None:
        return None
    low = flat[3]
    # How low the drawing reaches leaned each way: the line that hugs its underside there.
    lines = []
    for a, box in zip(angles, leaned, strict=True):
        assert box is not None
        lines.append((math.radians(a), box[3]))
    spans = [_span(lines, y) for y in (low, low - BAND * (low - flat[1]))]
    return min(s[0] for s in spans), max(s[1] for s in spans), low


def _span(lines: list[tuple[float, float]], y: float) -> tuple[float, float]:
    """The left and right of the drawing at height ``y``, between the ``lines`` (a lean, the lowest
    it reaches leaned) that hug its underside: every point keeps x sin(a) + y cos(a) under it."""
    at = {a: (h - y * math.cos(a)) / math.sin(a) for a, h in lines}
    return max(x for a, x in at.items() if a < 0), min(x for a, x in at.items() if a > 0)
