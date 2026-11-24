"""The one shadow a turned product stands on, flat on the ground (gen#1182).

A kit draws its shadow in its figure (an ellipse with ``class="ground"``), so turning the drawing
turned the shadow with it and a tilted pile looked as if it sat on a slope. :func:`turned` takes
those ellipses out of the drawing and draws one in their place, outside the turn: a soft ellipse,
horizontal, its center line at the lowest point of the turned drawing and its width that of the
part of the drawing near the ground. Every picture's shadow falls away from the one :data:`LIGHT`.

The drawing is measured by :func:`.sheet_extent.reach`, which gives a box. Leaning the drawing a
little each way and reading how low it reaches gives the lines that hug its underside
(:func:`_span`), so the footprint of a path is read without a rasteriser.
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


def turned(drawing: str, defs: str, transform: str, uid: str) -> tuple[str, str]:
    """(shadow, figure): ``drawing``'s figure without the shadow its kit drew, and the flat one
    to draw before it, outside ``transform`` (the product's turn). A drawing with no shadow
    gets none, and one that draws nothing to stand on it loses its shadow."""
    figure, shadows = GROUND.subn("", drawing)
    if not shadows:
        return "", drawing
    return _flat(figure, defs, transform, uid), figure


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
    flat = sheet_extent.reach(_SVG.format(defs, 0, body))
    if flat is None:
        return None
    low = flat[3]
    # How low the drawing reaches leaned each way: the line that hugs its underside there.
    lines = []
    for lean in LEANS:
        for a in (lean, -lean):
            box = sheet_extent.reach(_SVG.format(defs, a, body))
            assert box is not None
            lines.append((math.radians(a), box[3]))
    spans = [_span(lines, y) for y in (low, low - BAND * (low - flat[1]))]
    return min(s[0] for s in spans), max(s[1] for s in spans), low


def _span(lines: list[tuple[float, float]], y: float) -> tuple[float, float]:
    """The left and right of the drawing at height ``y``, between the ``lines`` (a lean, the lowest
    it reaches leaned) that hug its underside: every point keeps x sin(a) + y cos(a) under it."""
    at = {a: (h - y * math.cos(a)) / math.sin(a) for a, h in lines}
    return max(x for a, x in at.items() if a < 0), min(x for a, x in at.items() if a > 0)
