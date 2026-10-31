"""The colors and small parts the toy shapes share (:mod:`kit_toys`)."""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import INK, LW, LW_DETAIL, _line, _path

BLACK = "#2f2f35"
WHITE = "#ffffff"
WOOD = "#d9b98a"
SKIN = "#f1c9a5"
HAIR = "#6b4226"
STEEL = "#cfd5da"
#: Paint, bead, pencil and yarn colors a kit holds whatever the box's own color.
RAINBOW = ("#d93b30", "#f08a24", "#f2c94c", "#5f9a4a", "#2f8fc4", "#3f5fb5", "#7b4fa0",
           "#e46aa0", "#8a5a3a", "#2f2f35", "#9a9ca0", "#f4f1ea")  # fmt: skip
#: A range's badge color, by the motif that marks it.
BADGE = {"star": "#f2c94c", "dinosaur": "#5f9a4a", "bird": "#e07a1f", "whale": "#3f6fb5"}


def _n(value: str, default: int) -> int:
    try:
        return max(0, int(str(value).split()[0]))
    except (ValueError, IndexError):
        return default


def _counts(value: str, default: tuple[int, ...]) -> list[int]:
    try:
        return [max(0, int(v)) for v in str(value).split(",")] if value else list(default)
    except ValueError:
        return list(default)


def _ell(
    cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW, extra: str = ""
) -> str:
    return (f'<ellipse{extra} cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>')  # fmt: skip


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    r: float = 4,
    width: float = LW,
    extra: str = "",
) -> str:
    return (f'<rect{extra} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>')  # fmt: skip


def _group(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _shadow(cx: float, cy: float, rx: float) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{rx * 0.08:.1f}" fill="#000000" fill-opacity=".08"/>'


def _badge(character: str, cx: float = 350, cy: float = 50, r: float = 28) -> list[str]:
    """The range's mark: its motif on a round white badge (nothing when there is none)."""
    if not character:
        return []
    from synthetic_ecommerce_data.domains.retail import (
        motifs,  # deferred: motifs draws with this kit's shapes
    )

    return [_group("character", [_ell(cx, cy, r, r, WHITE, 2.4),
                                 motifs.motif_svg(character, BADGE.get(character, INK), cx, cy, r * 2.6)])]  # fmt: skip


def _star(cx: float, cy: float, r: float, fill: str, width: float = LW_DETAIL) -> str:
    pts = []
    for i in range(10):
        a = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append(f"{cx + rr * math.cos(a):.1f},{cy + rr * math.sin(a):.1f}")
    return _path("M" + " L".join(pts) + " Z", fill, width)


def _wheel(
    cx: float, cy: float, r: float, tire: str = BLACK, hub: str = STEEL, spokes: int = 0
) -> str:
    parts = [_ell(cx, cy, r, r, tire), _ell(cx, cy, r * 0.62, r * 0.62, hub, LW_DETAIL)]
    if spokes:
        parts.append(
            _line(
                " ".join(
                    f"M{cx:.1f},{cy:.1f} L{cx + r * 0.62 * math.cos(i * 2 * math.pi / spokes):.1f},{cy + r * 0.62 * math.sin(i * 2 * math.pi / spokes):.1f}"
                    for i in range(spokes)
                ),
                1,
            )
        )
    parts.append(_ell(cx, cy, r * 0.14, r * 0.14, INK, 1))
    return _group("wheel", parts)
