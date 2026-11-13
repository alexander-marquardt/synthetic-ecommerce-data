"""Car care shapes for the retail drawing kit (gen#970).

The Automotive department's products that no other shape draws: each is drawn as what it is, so a
wiper blade never reads as a ruler and a wash mitt never reads as a glove. Outlines are the kit's
ink, and the record's fill paints the main surface. Car shampoo, wax and interior cleaners use the
kit's ``bottle``, ``tub`` and ``trigger_spray``.

================  ===========================================  ===============================
shape             draws                                        params
================  ===========================================  ===============================
wiper_blade       a blade on the diagonal: a framed blade      style (conventional, beam,
                  with its bridges, a bare curved beam, a      hybrid, rear)
                  beam under a spoiler cover, or a short rear
                  blade with its own arm
fluid_jug         a jug with a handle, a screw cap and a        none
                  see-through level strip
air_freshener     a scented card on its string, a vent clip,    style (card, vent_clip, gel_can)
                  or a gel can with a vented lid
wash_mitt         a mitt with a cuff: a chenille mitt of        style (chenille, lambswool)
                  rows of noodles, or a fleece of curls
microfiber_towel  a folded towel with a stitched edge, or a     style (folded, stack)
                  stack of three cloths
================  ===========================================  ===============================

A drawing never prints a length, a volume or a scent: a style's SKUs share one image per
colorway. Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _panel,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _label, _rect

#: The rubber of a wiper blade's edge and a cap's plastic.
RUBBER = "#26292e"


def wiper_blade(paint: str, fill: Fill, label: str | None, style: str = "beam") -> list[str]:
    """A wiper blade from the side, on a shallow diagonal, with the hook adapter at its middle."""
    s = style.lower()
    if s == "rear":
        return _label([
            _line("M300,330 L240,210", LW + 7, stroke=INK),
            _line("M300,330 L240,210", LW + 3, stroke=paint),
            f'<circle cx="300" cy="330" r="16" fill="{_shade(fill.base, 0.3)}" stroke="{INK}" stroke-width="{LW}"/>',
            _path("M110,214 Q200,196 290,206 L290,216 Q200,208 110,224 Z", paint),
            _path("M110,224 Q200,208 290,216 L290,226 Q200,220 110,232 Z", RUBBER, LW_DETAIL),
            _rect(226, 196, 28, 18, POLE, 4),
        ], label)
    blade = "M50,260 Q200,206 350,150 L352,160 Q202,218 52,272 Z"
    rubber = "M52,272 Q202,218 352,160 L354,170 Q204,230 54,282 Z"
    out = [_path(rubber, RUBBER, LW_DETAIL)]
    if s == "conventional":
        out += [
            _path(blade, POLE),
            _line("M80,256 L130,200 L270,150 L322,148", LW + 1, stroke=INK),
            _line("M80,256 L130,200 L270,150 L322,148", LW - 1, stroke=paint),
            _line("M130,200 Q200,176 270,150", LW + 1),
        ]
    elif s == "hybrid":
        out += [
            _path(blade, paint),
            _path("M70,252 Q200,196 330,152 L334,140 Q200,184 66,240 Z", _shade(fill.base, 0.3)),
            _line("M110,234 L170,212 M230,190 L290,168", LW_DETAIL),
        ]
    else:
        out += [_path(blade, paint), _highlight("M70,258 Q200,210 330,162", 3, 0.5)]
    out += [
        _rect(186, 190, 34, 22, _tint(fill.base, 0.2) if s == "hybrid" else POLE, 4),
        _line("M196,190 L196,176 Q204,168 214,176", LW_DETAIL),
        _rect(44, 258, 14, 18, RUBBER, 3),
        _rect(344, 146, 14, 18, RUBBER, 3),
    ]
    return _label(out, label)


def fluid_jug(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A fluid jug: a handled body, a screw cap off to one side and a level strip."""
    body = "M120,368 L120,170 Q120,130 160,124 L214,124 L222,96 L262,96 L268,124 Q300,132 300,170 L300,368 Q210,378 120,368 Z"
    return [
        _path(body, paint),
        _path("M230,124 L292,124 Q300,124 300,150 L300,214 L272,214 L272,152 L230,152 Z", _shade(fill.base, 0.2), LW_DETAIL),
        _rect(216, 70, 52, 30, _shade(fill.accent, 0.1), 5),
        _line("M224,78 L224,94 M236,78 L236,94 M248,78 L248,94 M260,78 L260,94", 1.0),
        _rect(134, 180, 10, 170, _tint(fill.base, 0.55), 4, LW_DETAIL),
        *_panel(156, 230, 120, 96, label, 34),
        _highlight("M138,160 Q140,140 160,136", 5, 0.5),
    ]


def air_freshener(paint: str, fill: Fill, label: str | None, style: str = "card") -> list[str]:
    """A car air freshener: a scented ``card`` on its string, a ``vent_clip`` or a ``gel_can``."""
    s = style.lower()
    dark = _shade(fill.base, 0.35)
    if s == "vent_clip":
        return _label([
            _rect(150, 150, 100, 100, paint, 50),
            f'<circle cx="200" cy="200" r="30" fill="{_tint(fill.base, 0.4)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
            _line("M178,200 L222,200 M200,178 L200,222", LW_DETAIL),
            _rect(186, 250, 28, 60, dark, 4),
            _line("M192,310 L192,350 M208,310 L208,350", LW),
        ], label)
    if s == "gel_can":
        return _label([
            _path("M120,330 L120,220 L280,220 L280,330 Q200,346 120,330 Z", paint),
            f'<ellipse cx="200" cy="220" rx="80" ry="18" fill="{dark}" stroke="{INK}" stroke-width="{LW}"/>',
            f'<ellipse cx="200" cy="198" rx="80" ry="18" fill="{_tint(fill.base, 0.3)}" stroke="{INK}" stroke-width="{LW}"/>',
            _line("M150,192 L250,192 M150,204 L250,204", LW_DETAIL),
            _highlight("M134,240 L134,316", 5, 0.5),
        ], label)
    card = "M150,130 L250,130 Q262,130 262,142 L262,320 Q200,346 138,320 L138,142 Q138,130 150,130 Z"
    return _label([
        _line("M200,40 L200,118", LW_DETAIL),
        f'<circle cx="200" cy="124" r="7" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _path(card, paint),
        _line("M200,300 L200,180 M200,250 Q176,232 168,208 M200,226 Q224,210 232,188", LW_DETAIL),
        _highlight("M152,150 L152,300", 4, 0.4),
    ], label)


def wash_mitt(paint: str, fill: Fill, label: str | None, style: str = "chenille") -> list[str]:
    """A wash mitt with a ribbed cuff: rows of ``chenille`` noodles or ``lambswool`` curls."""
    body = "M120,330 L120,170 Q120,80 200,80 Q280,80 280,170 L280,330 Z"
    out = [_path(body, paint)]
    if style.lower() == "lambswool":
        out += [_line(f"M{x},{y} q8,-10 16,0 q8,10 16,0", LW_DETAIL) for y in (130, 175, 220, 265, 305) for x in (138, 186, 234)]
    else:
        out += [_line(f"M{x},110 L{x},322", 8, ' stroke-dasharray="2 14"', _shade(fill.base, 0.3)) for x in range(140, 272, 20)]
    out += [
        _rect(112, 324, 176, 44, _shade(fill.accent, 0.15), 8),
        _line(" ".join(f"M{x},330 L{x},362" for x in range(126, 280, 14)), 1.0),
    ]
    return _label(out, label)


def microfiber_towel(paint: str, fill: Fill, label: str | None, style: str = "folded") -> list[str]:
    """A microfiber towel ``folded`` in thirds, or a ``stack`` of three cloths."""
    edge = _shade(fill.base, 0.25)
    if style.lower() == "stack":
        out = []
        for i, y in enumerate((280, 230, 180)):
            out += [
                _path(f"M{90 + i * 6},{y + 60} L{90 + i * 6},{y} L{310 - i * 6},{y} L{310 - i * 6},{y + 60} Z", paint),
                _line(f"M{96 + i * 6},{y + 6} L{304 - i * 6},{y + 6}", 1.0, ' stroke-dasharray="4 3"', edge),
            ]
        return _label(out, label)
    return _label([
        _path("M90,320 L90,150 Q90,130 110,130 L310,130 L310,320 Z", paint),
        _path("M90,150 Q90,130 110,130 L310,130 L310,180 L110,180 Q90,180 90,160 Z", _tint(fill.base, 0.15)),
        _line("M96,312 L304,312 M96,190 L304,190", 1.0, ' stroke-dasharray="4 3"', edge),
        _line("M90,250 L310,250", LW_DETAIL),
    ], label)


SHAPES = {
    "wiper_blade": wiper_blade,
    "fluid_jug": fluid_jug,
    "air_freshener": air_freshener,
    "wash_mitt": wash_mitt,
    "microfiber_towel": microfiber_towel,
}
register(SHAPES)
