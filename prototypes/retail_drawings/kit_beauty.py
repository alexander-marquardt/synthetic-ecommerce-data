"""Beauty shapes for the retail drawing kit (gen#214).

Each of the ten types of :mod:`beauty_depth` has its own flat drawing in the kit's house style:
outlines in the kit's ink, the record's fill on the product's main surface. The variant axis that changes how
the product looks is a param; every param is a string with a default, so each shape draws bare.

==============  ==========================================  =====================
shape           draws                                       params
==============  ==========================================  =====================
mascara         a tube beside its wand: a fat, a long       effect (volume,
                or a curved brush                           length, curl)
primer          a squeeze tube standing on its cap, or a    form (tube, pump)
                pump bottle
setting_spray   a tall bottle under a fine-mist atomizer    nozzle (mist, pump)
                or a long pump head
serum           a glass bottle with a rubber dropper, or    form (dropper, pump)
                a pump head
face_mask       a foil sachet with a face, a clay tub with  mask (sheet, clay,
                a spatula, or a wide sleeping-mask pot      overnight)
eye_patches     a jar with a pair of crescent gel patches   patch (hydrogel,
                or of cloth strips                          cloth)
body_mist       a slim spray bottle, a dome or a ringed     cap (dome, ring)
                cap
aftershave      a square-shouldered bottle, stoppered or    cap (stopper, spray)
                with a spray head
talc            a round tin with a shaker lid, or with a    lid (shaker, puff)
                powder puff on top
sun_cream       a squeeze bottle with a flip cap, a pump    form (tube, pump,
                bottle or a trigger spray, a sun on each    spray)
==============  ==========================================  =====================

A drawing never prints a size or a count. A smaller size of a style is the same shape drawn
smaller (:mod:`pack_scale`, gen#543), so the SKUs of one size share one image per colorway.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, Fill, _highlight, _line, _panel, _path, _shade, _tint, register

CAP = "#3a3f46"
GLASS = "#e9eef2"


def _ell(cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _rect(
    x: float, y: float, w: float, h: float, fill: str, r: float = 6, width: float = LW
) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _label(out: list[str], label: str | None) -> list[str]:
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


def mascara(paint: str, fill: Fill, label: str | None, effect: str = "volume") -> list[str]:
    """A mascara: a tube with a cap band, and its wand laid beside it: ``volume`` (a fat oval
    brush), ``length`` (a long slim brush) or ``curl`` (a brush bent into a curve)."""
    out = [
        _rect(100, 190, 76, 150, paint, 10),
        _rect(106, 120, 64, 78, CAP, 8),
        _line("M100,236 L176,236", 2.4),
        _highlight("M114,214 L114,320", 5, 0.5),
        _line("M290,330 L290,250", 8, stroke=INK),
        _line("M290,330 L290,250", 4, stroke="#8d949c"),
    ]
    e = effect.lower()
    if e == "length":
        out += [
            _rect(278, 70, 24, 186, _shade(fill.base, 0.35), 12),
            _line(
                "M278,96 L302,96 M278,124 L302,124 M278,152 L302,152 M278,180 L302,180 M278,208 L302,208",
                1.6,
            ),
        ]
    elif e == "curl":
        out += [
            _path(
                "M270,252 Q262,170 292,120 Q308,92 332,90 Q320,128 316,172 Q312,214 306,252 Z",
                _shade(fill.base, 0.35),
            ),
            _line("M278,222 Q276,170 296,128 M292,236 Q292,180 314,134", 1.6),
        ]
    else:
        out += [
            _ell(290, 160, 40, 92, _shade(fill.base, 0.35)),
            _line("M258,120 L322,120 M254,150 L326,150 M254,180 L326,180 M258,210 L322,210", 1.6),
        ]
    return _label(out, label)


def primer(paint: str, fill: Fill, label: str | None, form: str = "tube") -> list[str]:
    """A face primer: a ``tube`` standing on its flat cap, or a ``pump`` bottle."""
    if form.lower() == "pump":
        out = [
            _rect(150, 150, 100, 190, paint, 16),
            _rect(186, 104, 28, 50, CAP, 4),
            _path("M176,104 L224,104 Q240,104 240,90 L240,80 L176,80 Z", CAP, 2.6),
            _line("M224,92 L262,92", 6, stroke=INK),
            _highlight("M166,176 L166,314", 5, 0.5),
        ]
    else:
        out = [
            _path("M130,330 L130,150 Q130,120 170,112 L230,112 Q270,120 270,150 L270,330 Z", paint),
            _rect(118, 330, 164, 34, CAP, 8),
            _path("M130,112 L270,112 L262,92 L138,92 Z", _tint(fill.base, 0.4), 2.6),
            _line("M146,104 L254,104", 1.6),
            _highlight("M150,168 L150,314", 5, 0.5),
        ]
    return _label(out, label)


def setting_spray(paint: str, fill: Fill, label: str | None, nozzle: str = "mist") -> list[str]:
    """A setting spray: a tall bottle under a ``mist`` atomizer (a small round head) or a ``pump``
    (a long pump head with a spout)."""
    out = [_rect(138, 140, 124, 204, paint, 22), _highlight("M156,176 L156,318", 5, 0.5)]
    if nozzle.lower() == "pump":
        out += [
            _rect(186, 96, 28, 46, CAP, 4),
            _path("M172,96 L228,96 Q236,76 276,70 L276,92 L246,100 L244,110 Z", CAP, 2.6),
        ]
    else:
        out += [
            _rect(168, 112, 64, 32, CAP, 8),
            _ell(200, 100, 24, 14, CAP),
            _line("M170,60 L158,46 M200,56 L200,38 M230,60 L242,46", 2.4),
        ]
    return _label(out, label)


def serum(paint: str, fill: Fill, label: str | None, form: str = "dropper") -> list[str]:
    """A serum: a glass bottle with a rubber ``dropper`` bulb, or with a ``pump`` head."""
    out = [
        _rect(146, 164, 108, 176, _tint(fill.base, 0.55), 20),
        _rect(158, 232, 84, 96, paint, 10),
        _highlight("M162,190 L162,318", 5, 0.5),
    ]
    if form.lower() == "pump":
        out += [
            _rect(178, 138, 44, 30, CAP, 4),
            _rect(188, 104, 24, 36, CAP, 4),
            _path("M180,104 L220,104 Q236,104 242,88 L196,88 Z", CAP, 2.6),
        ]
    else:
        out += [
            _rect(170, 142, 60, 26, CAP, 4),
            _path("M178,142 L178,110 Q178,70 200,70 Q222,70 222,110 L222,142 Z", "#7c4a3e"),
            _line("M200,232 L200,196", 3),
        ]
    return _label(out, label)


def face_mask(paint: str, fill: Fill, label: str | None, mask: str = "sheet") -> list[str]:
    """A face mask: a ``sheet`` mask's foil sachet with a face and eye holes, a ``clay`` mask's tub
    with its spatula, or an ``overnight`` mask's wide shallow pot."""
    m = mask.lower()
    if m == "clay":
        out = [
            _path("M96,170 L304,170 L292,320 Q290,336 270,336 L130,336 Q110,336 108,320 Z", paint),
            _rect(88, 130, 224, 44, CAP, 10),
            _line("M300,128 L352,44", 10, stroke=INK),
            _line("M300,128 L352,44", 5, stroke="#d9c3a0"),
            _highlight("M122,196 L130,300", 5, 0.5),
        ]
    elif m == "overnight":
        out = [
            _path("M70,230 L330,230 L318,320 Q316,338 296,338 L104,338 Q84,338 82,320 Z", paint),
            _rect(60, 192, 280, 44, CAP, 12),
            _ell(200, 192, 110, 12, _tint(fill.base, 0.4), 2.4),
            _highlight("M96,256 L102,314", 5, 0.5),
        ]
    else:
        out = [
            _rect(116, 70, 168, 268, paint, 6),
            _line("M116,92 L284,92 M116,316 L284,316", 2.4, ' stroke-dasharray="5 4"'),
            _path(
                "M200,126 Q146,126 146,200 Q146,282 200,296 Q254,282 254,200 Q254,126 200,126 Z",
                _tint(fill.base, 0.5),
                2.6,
            ),
            _ell(176, 192, 12, 7, "#ffffff", 2.4),
            _ell(224, 192, 12, 7, "#ffffff", 2.4),
            _line("M200,206 L200,236 M182,262 Q200,274 218,262", 2.4),
        ]
    return _label(out, label)


def eye_patches(paint: str, fill: Fill, label: str | None, patch: str = "hydrogel") -> list[str]:
    """Eye patches: a round jar with its lid, and a pair laid in front, ``hydrogel`` (crescent gel
    patches) or ``cloth`` (rounded cloth strips)."""
    out = [
        _path("M96,160 L304,160 L296,316 Q294,332 276,332 L124,332 Q106,332 104,316 Z", paint),
        _rect(88, 112, 224, 52, CAP, 12),
        _highlight("M120,186 L126,300", 5, 0.5),
    ]
    if patch.lower() == "cloth":
        out += [
            _rect(112, 236, 80, 36, "#ffffff", 14, 2.6),
            _rect(208, 236, 80, 36, "#ffffff", 14, 2.6),
            _line("M126,254 L178,254 M222,254 L274,254", 1.6),
        ]
    else:
        out += [
            _path("M112,240 Q152,296 194,240 Q152,268 112,240 Z", _tint(fill.base, 0.35), 2.6),
            _path("M206,240 Q248,296 288,240 Q248,268 206,240 Z", _tint(fill.base, 0.35), 2.6),
        ]
    return _label(out, label)


def body_mist(paint: str, fill: Fill, label: str | None, cap: str = "dome") -> list[str]:
    """A body mist: a slim, tall spray bottle with a ``dome`` cap or a ``ring`` collar and pump."""
    out = [_rect(150, 128, 100, 214, paint, 30), _highlight("M168,172 L168,320", 5, 0.5)]
    if cap.lower() == "ring":
        out += [
            _rect(158, 112, 84, 20, CAP, 4),
            _rect(186, 78, 28, 36, CAP, 4),
            _path("M178,78 L222,78 Q232,66 252,64 L252,82 L232,90 Z", CAP, 2.6),
        ]
    else:
        out += [
            _path("M158,128 L158,86 Q158,40 200,40 Q242,40 242,86 L242,128 Z", CAP),
            _highlight("M172,84 Q172,60 192,54", 4, 0.45),
        ]
    return _label(out, label)


def aftershave(paint: str, fill: Fill, label: str | None, cap: str = "stopper") -> list[str]:
    """An aftershave: a heavy square-shouldered glass bottle with a ``stopper`` or a ``spray`` head."""
    out = [
        _path("M110,170 L290,170 L290,318 Q290,342 266,342 L134,342 Q110,342 110,318 Z", paint),
        _path("M110,170 L290,170 L290,196 L110,196 Z", _tint(fill.base, 0.45), 2.4),
        _highlight("M128,214 L128,320", 5, 0.5),
    ]
    if cap.lower() == "spray":
        out += [
            _rect(172, 134, 56, 38, CAP, 4),
            _rect(186, 98, 28, 38, CAP, 4),
            _path("M178,98 L222,98 Q234,86 260,84 L260,102 L236,108 Z", CAP, 2.6),
        ]
    else:
        out += [
            _rect(176, 150, 48, 22, CAP, 3),
            _path("M164,150 L164,92 Q164,66 200,66 Q236,66 236,92 L236,150 Z", CAP),
        ]
    return _label(out, label)


def talc(paint: str, fill: Fill, label: str | None, lid: str = "shaker") -> list[str]:
    """A talc: a round tin with a ``shaker`` lid (a ring of sprinkle holes) or a powder ``puff`` on top."""
    out = [
        _path("M110,170 L290,170 L290,320 Q290,342 268,342 L132,342 Q110,342 110,320 Z", paint),
        _line("M110,214 L290,214 M110,296 L290,296", 2.4),
        _highlight("M126,232 L126,284", 5, 0.5),
    ]
    if lid.lower() == "puff":
        out += [
            _rect(104, 140, 192, 34, CAP, 10),
            _ell(200, 112, 62, 34, "#f7f1e6"),
            _line("M162,112 Q200,92 238,112 M170,128 Q200,116 230,128", 1.6),
        ]
    else:
        out += [
            _rect(104, 132, 192, 42, CAP, 10),
            _ell(200, 132, 96, 14, _tint(fill.base, 0.2), 2.4),
        ]
        out += [_ell(x, 132, 4.5, 2.6, INK, 1) for x in (140, 170, 200, 230, 260)]
    return _label(out, label)


def _sun(cx: float, cy: float, r: float) -> list[str]:
    """The sun printed on a sun cream bottle: a disc and eight short rays."""
    rays = " ".join(
        f"M{cx + 1.35 * r * dx:.1f},{cy + 1.35 * r * dy:.1f} L{cx + 1.8 * r * dx:.1f},{cy + 1.8 * r * dy:.1f}"
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, 0.7), (0.7, -0.7), (-0.7, -0.7))
    )
    return [_ell(cx, cy, r, r, "#f4c542", 2.6), _line(rays, 2.6)]


def sun_cream(paint: str, fill: Fill, label: str | None, form: str = "tube") -> list[str]:
    """A sun cream: a squat ``tube`` (a squeeze bottle under a wide flip cap), a ``pump`` bottle or
    a ``spray`` bottle under a trigger head, each with a sun printed on its front."""
    kind = form.lower()
    if kind == "pump":
        out = [
            _rect(130, 150, 140, 196, paint, 22),
            _rect(186, 108, 28, 44, CAP, 4),
            _path("M170,108 L230,108 Q246,108 250,92 L250,80 L170,80 Z", CAP, 2.6),
            _line("M236,92 L276,92", 6),
        ]
        sun = _sun(200, 250, 26)
    elif kind == "spray":
        out = [
            _rect(146, 150, 108, 196, paint, 18),
            _rect(176, 122, 48, 30, CAP, 4),
            _path("M166,122 L166,86 Q166,72 180,72 L250,72 L250,100 L228,100 L228,122 Z", CAP, 2.6),
            _line("M214,126 Q196,136 202,156", 3),
        ]
        sun = _sun(200, 250, 24)
    else:
        out = [
            _path("M120,330 L120,172 Q120,140 152,134 L248,134 Q280,140 280,172 L280,330 Q280,346 264,346 L136,346 Q120,346 120,330 Z", paint),
            _rect(150, 90, 100, 46, CAP, 12),
            _line("M150,112 L250,112", 1.6),
        ]
        sun = _sun(200, 246, 28)
    out += [_highlight("M138,180 L138,318", 5, 0.5), *sun]
    return _label(out, label)


SHAPES = {
    "mascara": mascara, "primer": primer, "setting_spray": setting_spray, "serum": serum,
    "face_mask": face_mask, "eye_patches": eye_patches, "body_mist": body_mist,
    "aftershave": aftershave, "talc": talc, "sun_cream": sun_cream,
}  # fmt: skip
register(SHAPES)
