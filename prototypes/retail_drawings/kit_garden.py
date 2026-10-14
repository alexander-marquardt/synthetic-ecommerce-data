"""Drawings of the garden products (gen#292).

The garden hose has a drawing of its own in the kit's house style: an outline in ink, the
color of the style in the hose, a brass fitting at the end. A hose is a tube, so each run of
it is two strokes of one path: a wide one in ink and a narrower one in the style's color on
top. The drawing carries no length: a style's lengths share one image.
"""

from __future__ import annotations

from kit import INK, Fill, _highlight, _line, _panel, _shade, _tint, register

BRASS = "#c9a24a"
#: The three loops of a coiled hose, as (x radius, y radius); the widest is drawn first.
COIL_LOOPS = ((128, 92), (98, 68), (68, 44))


def _tube(d: str, paint: str, width: float) -> str:
    """One run of hose: an ink stroke, then the style's color narrower on top."""
    ink = _line(d, width + 5, stroke=INK)
    return ink + _line(d, width, stroke=paint)


def _fitting(x: float, y: float, w: float, h: float) -> str:
    """A brass connector: a block with a ridge, centred on ``x, y``."""
    return (
        f'<rect x="{x - w / 2:.1f}" y="{y - h / 2:.1f}" width="{w:.1f}" height="{h:.1f}" rx="3" '
        f'fill="{BRASS}" stroke="{INK}" stroke-width="2.4"/>'
        + _line(f"M{x:.1f},{y - h / 2:.1f} L{x:.1f},{y + h / 2:.1f}", 2, ' stroke-opacity=".6"')
    )


def _ellipse_d(cx: float, cy: float, rx: float, ry: float) -> str:
    return (
        f"M{cx - rx:.1f},{cy:.1f} A{rx:.1f},{ry:.1f} 0 1,1 {cx + rx:.1f},{cy:.1f} "
        f"A{rx:.1f},{ry:.1f} 0 1,1 {cx - rx:.1f},{cy:.1f} Z"
    )


def garden_hose(paint: str, fill: Fill, label: str | None, style: str = "coiled") -> list[str]:
    """A garden hose: ``coiled`` (three loops of a plain hose, one free end with a brass
    connector) or ``expandable`` (a thin ribbed hose laid in an S with a connector at each end)."""
    if style.lower() == "expandable":
        run = "M70,310 C70,230 330,260 330,190 C330,130 120,150 120,100"
        out = [
            _tube(run, paint, 14),
            _line(run, 14, ' stroke-dasharray="2 9" stroke-opacity=".55"', _shade(fill.base, 0.4)),
            _fitting(70, 322, 30, 26),
            _fitting(120, 88, 26, 24),
            _highlight("M334,200 C340,150 250,150 200,146", 3, 0.5),
        ]
    else:
        out = []
        for rx, ry in COIL_LOOPS:
            out.append(_tube(_ellipse_d(190, 190, rx, ry), paint, 20))
        out += [
            _tube("M62,190 C40,250 70,320 150,330 L300,336", paint, 20),
            _fitting(318, 336, 28, 30),
            _line("M334,326 L366,318 M334,346 L366,354", 3),
            _highlight("M80,160 C100,110 150,92 190,98", 4, 0.5),
            _line(_ellipse_d(190, 190, 28, 18), 2, ' stroke-opacity=".4"', _tint(fill.base, 0.2)),
        ]
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


SHAPES = {"garden_hose": garden_hose}
register(SHAPES)
