"""Camping and fitness shapes for the retail drawing kit (gen#265).

Each type of :mod:`sports_rows` has its own flat drawing in the kit's house style: outlines in
the kit's ink, the record's fill (color and pattern) on the product's main surface.

==============  ==========================================  =====================
shape           draws                                       params
==============  ==========================================  =====================
tent            a dome (a half-round shell) or a tunnel     style
                (a long arch), door flap and poles
sleeping_bag    a tapered mummy bag with a hood or a        style
                rectangular bag with a zip
camp_chair      a folding chair, with or without arms       arms
yoga_mat        a mat laid flat or rolled up                state
dumbbell        a bar with hexagonal or rounded heads       style
kettlebell      a round body under a flat-topped handle     (none)
foam_roller     a cylinder, smooth or with a grid of        texture
                raised bumps (one ``class="bump"`` each)
==============  ==========================================  =====================

A drawing never prints a size, a berth, a thickness or a weight: a style's SKUs share one image
per colorway. Every param is a string with a default, so each shape also draws bare. The foam
roller's bumps are drawn as that many marked groups, which ``tests/test_retail_sports_265.py``
counts against the record.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, Fill, _highlight, _line, _panel, _path, _shade, _tint, register

#: The raised bumps a ``grid`` foam roller draws, as columns x rows.
BUMP_COLUMNS, BUMP_ROWS = 4, 3
POLE = "#8d949c"
FABRIC_DARK = "#3a3f46"


def _ell(cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _rect(x: float, y: float, w: float, h: float, fill: str, r: float = 6, width: float = LW) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _label(out: list[str], label: str | None) -> list[str]:
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


def tent(paint: str, fill: Fill, label: str | None, style: str = "dome") -> list[str]:
    """A tent: ``dome`` (a half-round shell on crossed poles) or ``tunnel`` (a long arch)."""
    dark = _shade(fill.base, 0.35)
    out = [_line("M30,312 L370,312", 4)]
    if style.lower() == "tunnel":
        out += [
            _path("M40,312 L40,248 Q40,170 120,170 L280,170 Q360,170 360,248 L360,312 Z", paint),
            _path("M150,312 L150,230 Q150,196 200,196 Q250,196 250,230 L250,312 Z", dark, 2.4),
            _line("M120,170 Q120,240 120,312 M280,170 Q280,240 280,312", 2.4, ' stroke-opacity=".55"'),
            _line("M40,312 L16,334 M360,312 L384,334", 2.4),
            _highlight("M64,214 Q74,186 112,180", 4, 0.5),
        ]
    else:
        out += [
            _path("M50,312 Q50,128 200,128 Q350,128 350,312 Z", paint),
            _line("M200,128 L200,312", 2.4, ' stroke-opacity=".5"'),
            _line("M96,312 Q112,176 200,128 M304,312 Q288,176 200,128", 2.4, stroke=POLE),
            _path("M158,312 Q158,222 200,206 Q242,222 242,312 Z", dark, 2.4),
            _line("M200,206 L200,312", 2, ' stroke-opacity=".6"'),
            _line("M50,312 L26,334 M350,312 L374,334", 2.4),
            _highlight("M84,236 Q96,176 144,148", 4, 0.5),
        ]
    return _label(out, label)


def sleeping_bag(paint: str, fill: Fill, label: str | None, style: str = "mummy") -> list[str]:
    """A sleeping bag: a tapered ``mummy`` with a hood, or a ``rectangular`` bag; both have a zip."""
    lining = _tint(fill.base, 0.55)
    if style.lower() == "rectangular":
        out = [
            _path("M96,86 L304,86 Q320,86 320,102 L320,318 Q320,334 304,334 L96,334 Q80,334 80,318 L80,102 Q80,86 96,86 Z", paint),
            _path("M96,86 L304,86 Q320,86 320,102 L320,132 L80,132 L80,102 Q80,86 96,86 Z", lining, 2.4),
            _line("M200,132 L200,334", 2.4, ' stroke-dasharray="6 5"'),
            _line("M120,176 L280,176 M120,230 L280,230 M120,284 L280,284", 1.6, ' stroke-opacity=".4"'),
        ]
    else:
        out = [
            _path("M200,60 Q262,60 270,118 Q292,180 280,250 Q272,326 238,344 L162,344 Q128,326 120,250 Q108,180 130,118 Q138,60 200,60 Z", paint),
            _path("M200,60 Q262,60 270,118 Q236,138 200,138 Q164,138 130,118 Q138,60 200,60 Z", lining, 2.4),
            _line("M200,138 L200,344", 2.4, ' stroke-dasharray="6 5"'),
            _line("M150,190 L250,190 M146,246 L254,246 M156,300 L244,300", 1.6, ' stroke-opacity=".4"'),
        ]
    return _label(out, label)


def camp_chair(paint: str, fill: Fill, label: str | None, arms: str = "no") -> list[str]:
    """A folding camping chair: a fabric seat and back on crossed legs; ``yes`` adds arms and a cup holder."""
    dark = _shade(fill.base, 0.3)
    out = [
        _line("M110,230 L90,340 M290,230 L310,340", 9, stroke=INK),
        _line("M110,230 L90,340 M290,230 L310,340", 5, stroke=POLE),
        _line("M120,340 L280,250 M280,340 L120,250", 9, stroke=INK),
        _line("M120,340 L280,250 M280,340 L120,250", 5, stroke=POLE),
        _path("M98,92 Q200,76 302,92 L296,208 Q200,222 104,208 Z", paint),
        _path("M96,214 Q200,232 304,214 L318,262 Q200,282 82,262 Z", dark),
        _line("M130,110 L128,196 M200,104 L200,204 M270,110 L272,196", 1.6, ' stroke-opacity=".4"'),
    ]
    if arms.lower() == "yes":
        out += [
            _rect(68, 170, 52, 16, dark, 7),
            _rect(280, 170, 52, 16, dark, 7),
            _line("M94,186 L100,236 M306,186 L300,236", 6, stroke=INK),
            _ell(306, 160, 14, 5, "none", 2),
        ]
    return _label(out, label)


def yoga_mat(paint: str, fill: Fill, label: str | None, state: str = "flat") -> list[str]:
    """A yoga mat: laid ``flat`` (a slanted slab) or ``rolled`` up with a spiral end."""
    dark = _shade(fill.base, 0.3)
    if state.lower() == "rolled":
        out = [
            _path("M92,150 L292,150 L292,300 L92,300 Z", paint),
            _ell(292, 225, 44, 75, paint),
            _ell(292, 225, 30, 52, "none", 2),
            _ell(292, 225, 17, 29, "none", 2),
            _ell(292, 225, 6, 10, dark, 2),
            _ell(92, 225, 44, 75, _tint(fill.base, 0.25)),
            _line("M100,176 L284,176 M100,274 L284,274", 1.6, ' stroke-opacity=".35"'),
            _line("M150,150 Q146,225 150,300 M236,150 Q232,225 236,300", 5, ' stroke-opacity=".8"', dark),
        ]
    else:
        out = [
            _path("M96,136 L336,136 L304,314 L40,314 Z", paint),
            _path("M40,314 L304,314 L304,330 L40,330 Z", dark, 2.4),
            _line("M110,176 L318,176 M96,226 L312,226 M80,276 L306,276", 1.6, ' stroke-opacity=".3"'),
            _highlight("M120,152 L300,152", 4, 0.5),
        ]
    return _label(out, label)


def _hex_head(cx: float, cy: float, r: float, paint: str) -> str:
    pts = [(cx - r, cy - r * 0.5), (cx, cy - r), (cx + r, cy - r * 0.5), (cx + r, cy + r * 0.5), (cx, cy + r), (cx - r, cy + r * 0.5)]
    return _path("M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in pts) + " Z", paint)


def dumbbell(paint: str, fill: Fill, label: str | None, style: str = "hex") -> list[str]:
    """A dumbbell: a steel bar between two heads, ``hex`` (six-sided) or ``round`` (neoprene)."""
    bar = [_line("M120,200 L280,200", 16, stroke=INK), _line("M120,200 L280,200", 10, stroke=POLE)]
    if style.lower() == "round":
        heads = [_ell(100, 200, 52, 64, paint), _ell(300, 200, 52, 64, paint), _highlight("M70,166 Q80,148 104,142", 4, 0.5), _highlight("M270,166 Q280,148 304,142", 4, 0.5)]
    else:
        heads = [_hex_head(100, 200, 64, paint), _hex_head(300, 200, 64, paint), _highlight("M64,176 L90,150", 4, 0.5), _highlight("M264,176 L290,150", 4, 0.5)]
    return _label([*bar, *heads], label)


def kettlebell(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A kettlebell: a round cast body under a flat-topped handle."""
    out = [
        _path("M142,150 Q142,100 200,100 Q258,100 258,150 L258,176 L240,176 L240,150 Q240,120 200,120 Q160,120 160,150 L160,176 L142,176 Z", _shade(fill.base, 0.35)),
        _path("M200,164 Q300,164 300,246 Q300,330 200,330 Q100,330 100,246 Q100,164 200,164 Z", paint),
        _ell(200, 322, 44, 8, _shade(fill.base, 0.3), 2),
        _highlight("M126,228 Q130,196 160,184", 5, 0.5),
    ]
    return _label(out, label)


def foam_roller(paint: str, fill: Fill, label: str | None, texture: str = "smooth") -> list[str]:
    """A foam roller: a cylinder lying on its side, ``smooth`` or a ``grid`` of raised bumps
    (:data:`BUMP_COLUMNS` x :data:`BUMP_ROWS`, one ``class="bump"`` group each)."""
    out = [
        _path("M96,120 L304,120 L304,280 L96,280 Z", paint),
        _ell(304, 200, 40, 80, _tint(fill.base, 0.2)),
        _ell(304, 200, 14, 28, "none", 2),
        _ell(96, 200, 40, 80, paint),
    ]
    if texture.lower() == "grid":
        for col in range(BUMP_COLUMNS):
            for row in range(BUMP_ROWS):
                x, y = 130 + col * 50, 150 + row * 50
                out.append(f'<g class="bump">{_ell(x, y, 11, 11, _shade(fill.base, 0.2), 1.6)}</g>')
    else:
        out += [_highlight("M110,138 L290,138", 5, 0.5)]
    return _label(out, label)


SHAPES = {
    "tent": tent, "sleeping_bag": sleeping_bag, "camp_chair": camp_chair, "yoga_mat": yoga_mat,
    "dumbbell": dumbbell, "kettlebell": kettlebell, "foam_roller": foam_roller,
}  # fmt: skip
register(SHAPES)
