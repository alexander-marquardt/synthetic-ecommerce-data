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
yoga_block      a slab, foam (gloss) or cork (flecks)       material
yoga_strap      a coil and a tail, D-rings or a clip        buckle
resistance_band a flat loop or a tube with two handles      form
lantern         an LED glass body or a concertina           style
roll_mat        a rolled mat or a folded stack              form
bike_pump       a floor pump with a gauge or a hand pump    style
baseball_bat    a bat, wood (grain) or alloy (grip tape)    material
baseball_glove  a glove, infield or deeper outfield web     position
baseball        a ball, leather or synthetic (banded)       cover
batting_helmet  a helmet with one ear flap or two           flaps
swim_goggles    two lenses and a strap, clear or mirrored   lens
swim_cap        a dome, silicone or panelled lycra          material
kickboard       a float, plain or with hand cut-outs        grips
swim_armbands   a pair, two or three chambers each          chambers
football        a ball, classic or modern panels            panels
tennis_racket   a frame and handle, open or dense strings   strings
badminton_set   two or four rackets over a shuttlecock      players
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


# --------------------------------------------------------------------------
# Second increment (gen#368): blocks, straps, bands, lanterns, roll mats, pumps, baseball,
# swimming, team and racket sports.
# --------------------------------------------------------------------------

PAPER2 = "#f4f4ee"
GLOW = "#fff2b8"


def yoga_block(paint: str, fill: Fill, label: str | None, material: str = "foam") -> list[str]:
    """A yoga block: a slab seen from a corner; ``cork`` is flecked, ``foam`` has a gloss line."""
    out = [
        _path("M70,196 L120,152 L350,152 L300,196 Z", _tint(fill.base, 0.3)),
        _path("M300,196 L350,152 L350,262 L300,310 Z", _shade(fill.base, 0.3)),
        _rect(70, 196, 230, 114, paint, 8),
    ]
    if material.lower() == "cork":
        out += [_ell(x, y, 5, 3, "#8a5a32", 1) for x, y in ((110, 230), (170, 262), (220, 224), (260, 276), (140, 288), (250, 242))]
    else:
        out.append(_highlight("M88,214 L282,214", 5, 0.5))
    return _label(out, label)


def yoga_strap(paint: str, fill: Fill, label: str | None, buckle: str = "ring") -> list[str]:
    """A yoga strap: a coil and a tail ending in a ``ring`` (two D-rings) or a ``clip`` buckle."""
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M170,176 L340,176 L340,214 L170,214 Z", paint),
        _ell(130, 200, 84, 84, paint),
        _ell(130, 200, 60, 60, "none", 2),
        _ell(130, 200, 38, 38, dark, 2),
        _ell(130, 200, 14, 14, PAPER2, 2),
    ]
    if buckle.lower() == "clip":
        out += [_rect(330, 168, 44, 54, POLE, 6), _line("M352,168 L352,222", 3)]
    else:
        out += [_rect(330, 164, 36, 62, "none", 12, 6), _rect(348, 164, 36, 62, "none", 12, 6)]
    return _label(out, label)


def resistance_band(paint: str, fill: Fill, label: str | None, form: str = "loop") -> list[str]:
    """A resistance band: a flat ``loop`` or a ``tube`` with a handle at each end."""
    if form.lower() == "tube":
        out = [
            _line("M84,262 Q200,70 316,262", 24, stroke=INK),
            _line("M84,262 Q200,70 316,262", 17, stroke=paint),
            _rect(58, 250, 52, 56, POLE, 10),
            _rect(290, 250, 52, 56, POLE, 10),
        ]
    else:
        out = [_ell(200, 200, 150, 84, paint), _ell(200, 200, 112, 52, PAPER2), _highlight("M96,160 Q150,124 220,122", 5, 0.5)]
    return _label(out, label)


def lantern(paint: str, fill: Fill, label: str | None, style: str = "led") -> list[str]:
    """A camping lantern: an ``led`` glass body with a base and cap, or a ``collapsible`` concertina."""
    dark = _shade(fill.base, 0.35)
    out = [_line("M150,128 Q200,40 250,128", 9, stroke=INK)]
    if style.lower() == "collapsible":
        for i in range(4):
            y = 310 - i * 44
            out.append(_path(f"M{140 - i * 4},{y} L{260 + i * 4},{y} L{250 + i * 4},{y - 44} L{150 - i * 4},{y - 44} Z", paint if i % 2 == 0 else dark, 2.4))
        out.append(_ell(200, 126, 52, 12, GLOW))
    else:
        out += [
            _path("M120,150 L280,150 L262,118 L138,118 Z", dark),
            _rect(134, 150, 132, 170, paint, 16),
            _rect(152, 170, 96, 130, GLOW, 10),
            _line("M200,170 L200,300", 2, ' stroke-opacity=".4"'),
            _rect(124, 320, 152, 24, dark, 6),
        ]
    return _label(out, label)


def roll_mat(paint: str, fill: Fill, label: str | None, form: str = "rolled") -> list[str]:
    """A camping roll mat: ``rolled`` up with two straps, or ``folded`` into a concertina stack."""
    dark = _shade(fill.base, 0.3)
    if form.lower() == "folded":
        out = []
        for i in range(5):
            y = 300 - i * 46
            out.append(_path(f"M70,{y} L330,{y} L330,{y - 36} L70,{y - 36} Z", paint if i % 2 == 0 else dark, 2.4))
        out.append(_highlight("M84,118 L316,118", 4, 0.5))
    else:
        out = [
            _path("M92,150 L292,150 L292,300 L92,300 Z", paint),
            _ell(292, 225, 44, 75, _tint(fill.base, 0.25)),
            _ell(292, 225, 28, 48, "none", 2),
            _ell(292, 225, 10, 16, dark, 2),
            _ell(92, 225, 44, 75, paint),
            _line("M150,150 L150,300 M236,150 L236,300", 7, ' stroke-opacity=".9"', INK),
        ]
    return _label(out, label)


def bike_pump(paint: str, fill: Fill, label: str | None, style: str = "floor") -> list[str]:
    """A bike pump: a ``floor`` pump with a base, gauge and T handle, or a ``hand`` pump."""
    dark = _shade(fill.base, 0.35)
    if style.lower() == "hand":
        return _label([
            _rect(100, 184, 210, 34, paint, 10),
            _rect(300, 180, 40, 42, dark, 8),
            _rect(60, 160, 26, 82, POLE, 7),
            _line("M86,201 L100,201", 10),
            _line("M340,200 Q386,250 340,300", 7, stroke=INK),
            _highlight("M116,194 L290,194", 4, 0.5),
        ], label)
    return _label([
        _rect(100, 318, 200, 24, POLE, 7),
        _rect(184, 140, 32, 180, paint, 8),
        _rect(140, 112, 120, 22, dark, 8),
        _line("M200,134 L200,150", 8),
        _ell(262, 250, 26, 26, PAPER2),
        _line("M262,250 L274,232", 3),
        _line("M216,300 Q300,330 330,300", 6, stroke=INK),
        _highlight("M192,160 L192,300", 4, 0.5),
    ], label)


def _tilted(parts: list[str], angle: float, cx: float = 200, cy: float = 200) -> list[str]:
    return [f'<g transform="rotate({angle:g} {cx:g} {cy:g})">', *parts, "</g>"]


def baseball_bat(paint: str, fill: Fill, label: str | None, material: str = "wood") -> list[str]:
    """A baseball bat on the slant: ``wood`` shows grain, ``alloy`` a grip tape and a flared end."""
    dark = _shade(fill.base, 0.35)
    barrel = "M168,192 Q250,182 304,174 Q344,174 344,200 Q344,226 304,226 Q250,218 168,208 Z"
    parts = [_ell(54, 200, 10, 16, dark, 2.4), _path("M62,192 L170,192 L170,208 L62,208 Z", paint), _path(barrel, paint)]
    if material.lower() == "alloy":
        parts += [_path("M64,193 L130,193 L130,207 L64,207 Z", dark, 2), _line("M310,176 L310,224", 3, ' stroke-opacity=".6"')]
    else:
        parts += [_line("M180,200 L330,200 M72,200 L170,200", 1.6, ' stroke-opacity=".35"'), _highlight("M190,190 L320,186", 4, 0.45)]
    return _label([*_tilted(parts, -32)], label)


def baseball_glove(paint: str, fill: Fill, label: str | None, position: str = "infield") -> list[str]:
    """A baseball glove: four fingers, a thumb and a web; the ``outfield`` glove has a deeper web."""
    dark = _shade(fill.base, 0.35)
    out = [
        _path("M118,336 Q84,250 100,196 L108,112 Q112,92 134,98 L148,172 L162,72 Q168,52 188,58 L192,170 L216,68 Q224,50 242,58 L244,172 L270,102 Q282,86 296,98 Q294,190 304,244 Q314,304 272,340 Z", paint),
        _path("M112,252 Q60,232 48,192 Q54,172 80,192 Z", dark, 2.4),
        _line("M150,200 Q200,250 262,196", 3, ' stroke-dasharray="6 4"', dark),
        _line("M130,310 Q200,336 262,310", 2.4, ' stroke-dasharray="5 4"', dark),
    ]
    if position.lower() == "outfield":
        out += [_path("M150,172 L192,172 L244,172 L222,236 L170,236 Z", dark, 2.4), _line("M170,236 L192,172 M222,236 L192,172", 2)]
    else:
        out.append(_path("M168,172 L220,172 L206,212 L182,212 Z", dark, 2.4))
    return _label(out, label)


def baseball(paint: str, fill: Fill, label: str | None, cover: str = "leather") -> list[str]:
    """A baseball: a ball with two curved seams; a ``synthetic`` cover adds a band round it."""
    stitch = "#c8312e"
    out = [
        _ell(200, 200, 112, 112, paint),
        _line("M138,108 Q184,200 138,292", 3, stroke=stitch),
        _line("M262,108 Q216,200 262,292", 3, stroke=stitch),
        _line("M138,108 Q184,200 138,292", 9, ' stroke-dasharray="2 12" stroke-opacity=".9"', stitch),
        _line("M262,108 Q216,200 262,292", 9, ' stroke-dasharray="2 12" stroke-opacity=".9"', stitch),
        _highlight("M120,160 Q132,130 168,114", 5, 0.5),
    ]
    if cover.lower() == "synthetic":
        out.append(_line("M90,204 Q200,226 310,204", 8, ' stroke-opacity=".55"', _shade(fill.base, 0.4)))
    return _label(out, label)


def batting_helmet(paint: str, fill: Fill, label: str | None, flaps: str = "single") -> list[str]:
    """A batting helmet: a dome with a bill and an ear flap on one side or on ``double`` sides."""
    dark = _shade(fill.base, 0.35)
    out = [
        _path("M70,260 Q70,100 200,100 Q330,100 330,260 L330,282 L70,282 Z", paint),
        _path("M72,252 Q24,262 20,288 L150,288 L150,270 Z", dark, 2.6),
        _path("M236,206 Q338,196 338,262 Q338,322 272,322 Q240,296 236,262 Z", dark),
        _ell(210, 150, 6, 6, INK, 1), _ell(236, 134, 6, 6, INK, 1), _ell(176, 136, 6, 6, INK, 1),
        _highlight("M96,196 Q104,146 160,120", 5, 0.5),
    ]
    if flaps.lower() == "double":
        out.append(_path("M164,206 Q62,196 62,262 Q62,322 128,322 Q160,296 164,262 Z", dark))
    return _label(out, label)


def swim_goggles(paint: str, fill: Fill, label: str | None, lens: str = "clear") -> list[str]:
    """Swimming goggles: two lenses on a nose bridge and a strap; ``mirrored`` lenses are dark."""
    glass = "#4b5d78" if lens.lower() == "mirrored" else "#cfe8f5"
    out = [
        _line("M24,190 Q200,120 376,190", 14, stroke=INK),
        _line("M24,190 Q200,120 376,190", 9, stroke=paint),
        _ell(128, 214, 62, 46, paint),
        _ell(272, 214, 62, 46, paint),
        _ell(128, 214, 46, 32, glass, 2.4),
        _ell(272, 214, 46, 32, glass, 2.4),
        _line("M188,212 L212,212", 8),
        _highlight("M100,200 Q112,188 136,186", 4, 0.6),
        _highlight("M244,200 Q256,188 280,186", 4, 0.6),
    ]
    return _label(out, label)


def swim_cap(paint: str, fill: Fill, label: str | None, material: str = "silicone") -> list[str]:
    """A swim cap: a dome; ``lycra`` shows panel seams, ``silicone`` a smooth gloss."""
    out = [_path("M64,282 Q64,92 200,92 Q336,92 336,282 Q200,318 64,282 Z", paint)]
    if material.lower() == "lycra":
        out += [_line("M200,92 L200,300 M138,100 Q118,200 146,296 M262,100 Q282,200 254,296", 2, ' stroke-opacity=".55"')]
    else:
        out += [_highlight("M104,200 Q108,130 160,110", 6, 0.55), _line("M70,276 Q200,308 330,276", 3, ' stroke-opacity=".5"')]
    return _label(out, label)


def kickboard(paint: str, fill: Fill, label: str | None, grips: str = "none") -> list[str]:
    """A kickboard: a rounded float; ``cutouts`` adds two hand holes near the top."""
    out = [
        _path("M104,336 L104,120 Q104,64 160,64 L240,64 Q296,64 296,120 L296,336 Z", paint),
        _line("M104,300 L296,300 M104,260 L296,260", 1.6, ' stroke-opacity=".3"'),
        _highlight("M122,130 L122,290", 5, 0.5),
    ]
    if grips.lower() == "cutouts":
        out += [_ell(166, 126, 18, 26, PAPER2, 2.4), _ell(234, 126, 18, 26, PAPER2, 2.4)]
    return _label(out, label)


def swim_armbands(paint: str, fill: Fill, label: str | None, chambers: str = "two") -> list[str]:
    """A pair of inflatable armbands, each split into ``two`` or ``three`` chambers."""
    out = []
    for cx in (130, 270):
        out += [_ell(cx, 200, 60, 104, paint), _ell(cx, 200, 24, 46, PAPER2, 2.4)]
        cuts = (200,) if chambers.lower() == "two" else (166, 234)
        out += [_line(f"M{cx - 56},{y} Q{cx},{y + 14} {cx + 56},{y}", 2.4, ' stroke-opacity=".6"') for y in cuts]
    return _label(out, label)


def football(paint: str, fill: Fill, label: str | None, panels: str = "classic") -> list[str]:
    """A football: ``classic`` black pentagon panels, or ``modern`` swirling thermal panels."""
    dark = _shade(fill.base, 0.55)
    out = [_ell(200, 200, 120, 120, paint)]
    if panels.lower() == "modern":
        out += [_line(f"M{x1},{y1} Q200,200 {x2},{y2}", 3, ' stroke-opacity=".7"') for x1, y1, x2, y2 in ((96, 130, 300, 110), (84, 250, 316, 270), (130, 96, 170, 306), (270, 96, 232, 306))]
    else:
        out += [_path("M200,150 L246,184 L228,236 L172,236 L154,184 Z", dark, 2.4)]
        out += [_line(f"M{a},{b} L{c},{d}", 2.4, ' stroke-opacity=".7"') for a, b, c, d in ((200, 150, 200, 88), (246, 184, 304, 164), (228, 236, 266, 292), (172, 236, 134, 292), (154, 184, 96, 164))]
        out += [_path("M200,88 L226,80 L252,98 L238,118 Z", dark, 2), _path("M200,88 L174,80 L148,98 L162,118 Z", dark, 2)]
    out.append(_highlight("M112,150 Q126,118 166,100", 5, 0.5))
    return _label(out, label)


def tennis_racket(paint: str, fill: Fill, label: str | None, strings: str = "open") -> list[str]:
    """A tennis racket: an oval frame, a throat and a handle; the strings are ``open`` or ``dense``."""
    n = 9 if strings.lower() == "dense" else 5
    dark = _shade(fill.base, 0.35)
    out = [_ell(200, 150, 86, 108, paint), _ell(200, 150, 68, 90, PAPER2, 2.4)]
    for k in range(n):
        f = (k + 0.5) / n * 2 - 1
        dx, dy = 68 * f, 90 * f
        hy, hx = 90 * (1 - f * f) ** 0.5, 68 * (1 - f * f) ** 0.5
        out.append(_line(f"M{200 + dx:.1f},{150 - hy:.1f} L{200 + dx:.1f},{150 + hy:.1f}", 1.4, ' stroke-opacity=".6"'))
        out.append(_line(f"M{200 - hx:.1f},{150 + dy:.1f} L{200 + hx:.1f},{150 + dy:.1f}", 1.4, ' stroke-opacity=".6"'))
    out += [_path("M172,250 L200,300 L228,250 Z", paint), _rect(186, 296, 28, 76, dark, 8)]
    return _label(out, label)


def badminton_set(paint: str, fill: Fill, label: str | None, players: str = "2") -> list[str]:
    """A badminton set: two or four rackets fanned out over a shuttlecock."""
    angles = (-34, -11, 11, 34) if players == "4" else (-20, 20)
    out = []
    for a in angles:
        out += _tilted([_ell(200, 130, 40, 54, paint), _ell(200, 130, 28, 40, PAPER2, 2), _line("M200,90 L200,170 M172,130 L228,130", 1.2, ' stroke-opacity=".5"'), _line("M200,184 L200,300", 6), _rect(192, 296, 16, 40, _shade(fill.base, 0.35), 5)], a, 200, 336)
    out += [_path("M176,356 L224,356 L212,334 L188,334 Z", PAPER2, 2), _ell(200, 366, 14, 8, INK, 2)]
    return _label(out, label)


SHAPES = {
    "tent": tent, "sleeping_bag": sleeping_bag, "camp_chair": camp_chair, "yoga_mat": yoga_mat,
    "dumbbell": dumbbell, "kettlebell": kettlebell, "foam_roller": foam_roller,
    "yoga_block": yoga_block, "yoga_strap": yoga_strap, "resistance_band": resistance_band,
    "lantern": lantern, "roll_mat": roll_mat, "bike_pump": bike_pump, "baseball_bat": baseball_bat,
    "baseball_glove": baseball_glove, "baseball": baseball, "batting_helmet": batting_helmet,
    "swim_goggles": swim_goggles, "swim_cap": swim_cap, "kickboard": kickboard,
    "swim_armbands": swim_armbands, "football": football, "tennis_racket": tennis_racket,
    "badminton_set": badminton_set,
}  # fmt: skip
register(SHAPES)
