"""Underwear and nightwear shapes for the retail drawing kit (gen#208).

Each type of :mod:`underwear_rows` has its own flat drawing in the kit's house style: the
kit's ink outline, the record's fill (color and pattern) on the garment, so a shopper tells
knickers from tights, a camisole from a thermal vest and a dressing gown from a slip at
thumbnail size.

==============  ====================================================  ========================
shape           draws                                                 params
==============  ====================================================  ========================
knickers        full brief, high-waisted, high-leg, bikini, thong or  cut, trim
                shorts, with a waistband and two leg openings
tights          two legs joined at a waistband, sheer to opaque       denier, finish, control
vest            strappy, camisole, crop, sleeveless or thermal        style, trim
slip            a slim dress on thin straps, mini to full length      length, trim
shapewear       bodysuit, bra-friendly bodysuit, shorts or            type, seamless, control
                high-waisted brief
dressing_gown   an open wrap gown with sleeves, optionally belted     length, hood, belt, fabric
                and hooded
boxers          trunks, boxer shorts or Y-front briefs with a fly     fit
==============  ====================================================  ========================

A drawing never prints a size or a pack count: a style's sizes and packs share one image per
colorway, so a number on it would be wrong for all but one. Every param is a string with a
default, so each shape also draws bare. What a row states and the drawing can count is drawn
as that many marked groups, which ``tests/test_retail_underwear_208.py`` counts per record:
``waistband`` and ``leg-opening`` (knickers), ``leg`` and ``control-panel`` (tights),
``strap`` and ``sleeve`` (vests), ``strap`` and ``lace-trim`` (slips), ``strap``,
``seam-panel`` and ``control-band`` (shapewear), ``sleeve``, ``hood`` and ``belt``
(dressing gowns), ``leg`` and ``fly`` (boxers).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register
from kit_garments import _dark

#: Tights: the share of the drawing's ink and paint kept, by denier (a 10 denier is near sheer).
DENIER_OPACITY = {"10": 0.6, "15": 0.6, "20": 0.6, "40": 0.6, "60": 0.6, "100": 0.6}
#: Dressing gown and slip lengths: where the hem falls on the sheet.
GOWN_HEM = {"short": 262, "knee": 308, "full": 356}
SLIP_HEM = {"mini": 322, "midi": 322, "full": 322}


def _g(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _f(v: float) -> str:
    return f"{v:.1f}"


def _scallops(x0: float, x1: float, y: float, n: int, r: float, up: bool = False) -> str:
    """A row of ``n`` lace scallops along y between x0 and x1 (a lace-trim edge)."""
    w = (x1 - x0) / n
    sign = -1 if up else 1
    return " ".join(
        f"M{_f(x0 + i * w)},{_f(y)} q{_f(w / 2)},{_f(sign * 2 * r)} {_f(w)},0" for i in range(n)
    )


def _lace(x0: float, x1: float, y: float, fill: Fill, n: int = 12, up: bool = False) -> list[str]:
    """A lace edge: scallops over the edge in a lighter tone, with eyelets above them."""
    tone = _tint(fill.base, 0.55) if fill.base.startswith("#") else "#ffffff"
    sign = -1 if up else 1
    scallop = _scallops(x0, x1, y, n, 6, up)
    w = (x1 - x0) / n
    dots = " ".join(f"M{_f(x0 + (i + 0.5) * w)},{_f(y + sign * 4)} l0.1,0" for i in range(n))
    return [_path(scallop, tone, LW_DETAIL), _line(dots, 2.2)]


def _band(x0: float, x1: float, y0: float, y1: float, paint: str, dip: float = 0) -> list[str]:
    """An elastic waistband: a strip with its stitch line, one ``waistband`` mark."""
    d = f"M{_f(x0)},{_f(y0)} Q200,{_f(y0 + dip)} {_f(x1)},{_f(y0)} L{_f(x1)},{_f(y1)} Q200,{_f(y1 + dip)} {_f(x0)},{_f(y1)} Z"
    mid = (y0 + y1) / 2
    return [_g("waistband", [
        _path(d, paint, LW_DETAIL + 0.4), _dark(d, 0.1),
        _line(f"M{_f(x0 + 5)},{_f(mid)} Q200,{_f(mid + dip)} {_f(x1 - 5)},{_f(mid)}", 1.1, ' stroke-dasharray="4 3"'),
    ])]  # fmt: skip


def _hi(fill: Fill) -> str:
    """A detail stroke that shows on the fill: the ink on a light one, white on a dark one."""
    if not fill.base.startswith("#"):
        return INK
    r, g, b = (int(fill.base[i : i + 2], 16) for i in (1, 3, 5))
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.4 else "#ffffff"


def _shadow(cy: float = 366, rx: float = 100) -> str:
    return f'<ellipse cx="200" cy="{cy}" rx="{rx}" ry="7" fill="#000000" fill-opacity=".08"/>'


# --------------------------------------------------------------------------
# Knickers
# --------------------------------------------------------------------------

#: cut -> (waist y, waist half-width, hip y, hip half-width, crotch y, crotch half-width,
#:         leg control x, leg control y, band height)
KNICKER_CUTS = {
    "brief": (122, 104, 206, 112, 296, 30, 64, 238, 22),
    "high_waisted": (66, 92, 214, 112, 300, 30, 62, 246, 30),
    "high_leg": (136, 98, 178, 106, 292, 24, 40, 192, 16),
    "bikini": (150, 104, 196, 106, 288, 26, 58, 232, 14),
    # The shapewear brief: high and snug, with a deep waistband.
    "shape_brief": (70, 82, 214, 100, 306, 26, 62, 250, 26),
}


def _knickers_body(paint: str, cut: str) -> list[str]:
    wy, ww, hy, hw, cy, cwid, qx, qy, bh = KNICKER_CUTS[cut]
    mid = (ww + hw) / 2 + 3
    d = (f"M{200 - ww},{wy} L{200 + ww},{wy} Q{200 + mid:.1f},{(wy + hy) / 2:.1f} {200 + hw},{hy} "
         f"Q{200 + qx},{qy} {200 + cwid},{cy} L{200 - cwid},{cy} Q{200 - qx},{qy} {200 - hw},{hy} "
         f"Q{200 - mid:.1f},{(wy + hy) / 2:.1f} {200 - ww},{wy} Z")  # fmt: skip
    stitch = [
        _line(f"M{200 + hw - 7},{hy + 5} Q{200 + qx - 6},{qy - 7} {200 + cwid - 3},{cy - 7}", 1.2, ' stroke-dasharray="4 3"'),
        _line(f"M{200 - hw + 7},{hy + 5} Q{200 - qx + 6},{qy - 7} {200 - cwid + 3},{cy - 7}", 1.2, ' stroke-dasharray="4 3"'),
    ]
    out = [_path(d, paint), _dark(d, 0.04)]
    out.append(_g("leg-opening", [stitch[0]]))
    out.append(_g("leg-opening", [stitch[1]]))
    out.append(_line(f"M{200 - cwid},{cy - 34} L{200 + cwid},{cy - 34}", 1.2, ' stroke-dasharray="4 3"'))
    out += _band(200 - ww, 200 + ww, wy, wy + bh, paint)
    return out


def _knickers_shorts(paint: str) -> list[str]:
    d = ("M96,124 L304,124 Q316,160 318,200 L322,268 L224,268 Q214,242 200,236 Q186,242 176,268 "
         "L78,268 L82,200 Q84,160 96,124 Z")  # fmt: skip
    out = [_path(d, paint), _dark(d, 0.04)]
    out.append(_g("leg-opening", [_line("M82,256 L174,256", 1.3, ' stroke-dasharray="4 3"')]))
    out.append(_g("leg-opening", [_line("M226,256 L318,256", 1.3, ' stroke-dasharray="4 3"')]))
    out.append(_line("M176,268 Q186,242 200,236 Q214,242 224,268", 1.2))
    out += _band(96, 304, 124, 146, paint)
    return out


def _knickers_thong(paint: str) -> list[str]:
    tri = "M148,150 Q200,166 252,150 Q226,214 210,282 Q200,298 190,282 Q174,214 148,150 Z"
    strip = "M72,134 Q200,152 328,134 L328,146 Q200,164 72,146 Z"
    out = [_g("waistband", [_path(strip, paint, LW_DETAIL + 0.4)]), _path(tri, paint), _dark(tri, 0.05)]
    out.append(_g("leg-opening", [_line("M156,164 Q184,222 196,274", 1.3, ' stroke-dasharray="4 3"')]))
    out.append(_g("leg-opening", [_line("M244,164 Q216,222 204,274", 1.3, ' stroke-dasharray="4 3"')]))
    return out


def knickers(paint: str, fill: Fill, label: str | None, cut: str = "brief", trim: str = "plain") -> list[str]:
    """Knickers in one of the cuts: full brief, high-waisted, high-leg, bikini, thong, shorts."""
    cut = cut.replace("-", "_").replace(" ", "_")
    if cut == "shorts":
        body, edge = _knickers_shorts(paint), (96, 304, 146)
    elif cut == "thong":
        body, edge = _knickers_thong(paint), (76, 324, 150)
    else:
        cut = cut if cut in KNICKER_CUTS else "brief"
        wy, ww, _, _, _, _, _, _, bh = KNICKER_CUTS[cut]
        body, edge = _knickers_body(paint, cut), (200 - ww, 200 + ww, wy + bh)
    out = [_shadow(330, 110), *body]
    if trim == "lace":
        out.append(_g("lace-trim", _lace(edge[0] + 2, edge[1] - 2, edge[2], fill, 14)))
    return out


# --------------------------------------------------------------------------
# Tights
# --------------------------------------------------------------------------


def tights(paint: str, fill: Fill, label: str | None, denier: str = "20", finish: str = "sheer", control: str = "no") -> list[str]:
    """Two legs joined at a waistband; a low denier is drawn faded, a high one solid."""
    op = DENIER_OPACITY.get(str(denier), 0.6)
    left = ("M138,92 L200,92 L200,150 Q186,176 176,230 Q170,290 168,326 Q166,342 150,352 "
            "Q120,356 110,344 Q108,332 124,326 Q130,260 126,214 Q124,150 138,92 Z")  # fmt: skip
    legs = []
    for d in (left, _mirror_path(left)):
        legs.append(_g("leg", [_path(d, paint), _dark(d, 0.05)]))
    body = "".join(legs)
    out = [f'<g opacity="{op:g}">{body}</g>']
    out.append(_line("M200,92 L200,150", 1.4))
    for sx in (1, -1):  # toe seams
        x = 200 + sx * (200 - 122)
        out.append(_line(f"M{x - sx * 8},340 Q{x - sx * 12},346 {x - sx * 28},350", 1.0, ' stroke-opacity=".5"'))
    if finish == "fleece":
        for sx in (1, -1):
            for y in range(180, 320, 14):
                x0 = 200 + sx * (200 - 168 + (y - 230) * -0.1)
                out.append(_line(f"M{_f(x0)},{y} l{sx * 12},3", 1.4, ' stroke-opacity=".6" stroke-dasharray="2 4"', _hi(fill)))
    band = "M136,70 L264,70 L264,96 L136,96 Z"
    out += [_g("waistband", [_path(band, paint, LW_DETAIL + 0.4), _dark(band, 0.1),
                              _line("M142,83 L258,83", 1.1, ' stroke-dasharray="4 3"')])]  # fmt: skip
    if control == "yes":
        panel = "M138,96 L262,96 L254,168 Q200,186 146,168 Z"
        out.append(_g("control-panel", [_path(panel, paint, LW_DETAIL), _dark(panel, 0.14),
                                         _line("M150,126 Q200,140 250,126", 1.0, ' stroke-dasharray="3 3"')]))  # fmt: skip
    out.append(_shadow(364, 96))
    return out


def _mirror_path(d: str) -> str:
    from kit import _mirror

    return _mirror(d)


# --------------------------------------------------------------------------
# Vests
# --------------------------------------------------------------------------


def _strap(x0: float, y0: float, x1: float, y1: float, w: float, paint: str) -> str:
    d = f"M{_f(x0)},{_f(y0)} L{_f(x0 + w)},{_f(y0)} L{_f(x1 + w)},{_f(y1)} L{_f(x1)},{_f(y1)} Z"
    return _g("strap", [_path(d, paint, LW_DETAIL + 0.4)])


def vest(paint: str, fill: Fill, label: str | None, style: str = "strappy", trim: str = "plain") -> list[str]:
    """A vest top: thin straps (strappy), camisole with a V, crop, wide-strap sleeveless, or thermal with sleeves."""
    out = [_shadow(350, 96)]
    if style == "thermal":
        for sx in (1, -1):
            sl = f"M{200 + sx * 62},94 L{200 + sx * 104},122 L{200 + sx * 94},176 L{200 + sx * 66},178 Z"
            out.append(_g("sleeve", [_path(sl, paint), _dark(sl, 0.06),
                                      _line(f"M{200 + sx * 98},160 L{200 + sx * 70},164", 1.2, ' stroke-dasharray="4 3"')]))  # fmt: skip
        body = "M156,80 Q200,114 244,80 L262,96 L272,180 L272,332 L128,332 L128,180 L138,96 Z"
        out.append(_path(body, paint))
        out.append(_line("M156,80 Q200,114 244,80", 2.2))
        for y in range(150, 326, 14):
            out.append(_line(f"M132,{y} L268,{y}", 1.0, ' stroke-opacity=".5"', _hi(fill)))
        out.append(_line("M128,318 L272,318", 1.2, ' stroke-dasharray="4 3"'))
        return out
    if style == "sleeveless":
        body = "M148,78 L178,78 Q200,138 222,78 L252,78 Q254,118 268,142 L264,332 L136,332 L132,142 Q146,118 148,78 Z"
        out.append(_path(body, paint))
        for sx in (1, -1):
            st = f"M{200 + sx * 52},78 L{200 + sx * 22},78 Q{200 + sx * 30},112 {200 + sx * 40},124 L{200 + sx * 62},132 Q{200 + sx * 50},112 {200 + sx * 52},78 Z"
            out.append(_g("strap", [_path(st, paint, LW_DETAIL), _dark(st, 0.08)]))
        out.append(_line("M134,320 L266,320", 1.2, ' stroke-dasharray="4 3"'))
        return out
    hem, neck, sw = {
        "strappy": (330, "scoop", 9),
        "camisole": (336, "v", 9),
        "crop": (232, "scoop", 12),
    }.get(style, (330, "scoop", 9))
    top = 120
    wid = 70 if style != "crop" else 62
    flare = 4 if style == "camisole" else 0
    cut_back = (f"M{200 - 48},{top - 6} Q200,{top + 46} {200 + 48},{top - 6}" if neck == "scoop"
                else f"M{200 - 48},{top - 6} L200,{top + 52} L{200 + 48},{top - 6}")  # fmt: skip
    body = (f"M{200 - 48},{top - 6} L{200 - wid},{top + 22} Q{200 - wid - 4},{top + 60} {200 - wid + 2},{top + 98} "
            f"L{200 - wid - flare - 2},{hem} L{200 + wid + flare + 2},{hem} L{200 + wid - 2},{top + 98} "
            f"Q{200 + wid + 4},{top + 60} {200 + wid},{top + 22} L{200 + 48},{top - 6} "
            + (f"Q200,{top + 46} {200 - 48},{top - 6} Z" if neck == "scoop" else f"L200,{top + 52} L{200 - 48},{top - 6} Z"))  # fmt: skip
    out += [_strap(200 - 62, 68, 200 - 52, top - 4, sw, paint), _strap(200 + 53, 68, 200 + 41, top - 4, sw, paint)]
    out.append(_path(body, paint))
    out.append(_line(cut_back, 1.4, ' stroke-dasharray="4 3"'))
    out.append(_line(f"M{200 - wid - flare},{hem - 10} L{200 + wid + flare},{hem - 10}", 1.2, ' stroke-dasharray="4 3"'))
    if trim == "lace" or style == "camisole":
        if neck == "v":
            out.append(_g("lace-trim", [_line(f"M{200 - 48},{top - 6} L200,{top + 52} L{200 + 48},{top - 6}", 4.0, ' stroke-opacity=".35"')]))
        else:
            out.append(_g("lace-trim", _lace(200 - wid + 4, 200 + wid - 4, hem - 2, fill, 12, up=True)))
    return out


# --------------------------------------------------------------------------
# Slip
# --------------------------------------------------------------------------


def slip(paint: str, fill: Fill, label: str | None, length: str = "midi", trim: str = "plain") -> list[str]:
    """A slim slip dress on thin straps, mini to full length, optionally with a lace hem."""
    hem = SLIP_HEM.get(length, SLIP_HEM["midi"])
    flare = {"mini": 6, "midi": 14, "full": 24}.get(length, 14)
    body = ("M150,112 Q200,176 250,112 Q262,150 252,196 Q246,226 250,262 "
            f"L{250 + flare},{hem} L{150 - flare},{hem} L150,262 Q154,226 148,196 Q138,150 150,112 Z")  # fmt: skip
    out = [_shadow(hem + 12, 100)]
    out.append(_g("strap", [_path("M160,44 L168,44 L168,116 L156,118 Z", paint, LW_DETAIL)]))
    out.append(_g("strap", [_path("M232,44 L240,44 L244,118 L232,116 Z", paint, LW_DETAIL)]))
    out.append(_path(body, paint))
    out.append(_dark("M152,196 Q200,206 248,196 L250,206 Q200,216 150,206 Z", 0.08))
    if trim == "lace":
        out.append(_g("lace-trim", _lace(150 - flare + 1, 250 + flare - 1, hem - 4, fill, 12 + flare // 6, up=True)))
    else:
        out.append(_line(f"M{150 - flare + 3},{hem - 8} L{250 + flare - 3},{hem - 8}", 1.2, ' stroke-dasharray="4 3"'))
    return out


# --------------------------------------------------------------------------
# Shapewear
# --------------------------------------------------------------------------


def shapewear(paint: str, fill: Fill, label: str | None, type: str = "bodysuit", seamless: str = "yes", control: str = "medium") -> list[str]:  # noqa: A002
    """Shapewear: a bodysuit, bra-friendly (plunge) bodysuit, thigh shorts or high-waisted brief."""
    kind = type.replace("-", "_").replace(" ", "_")
    out = [_shadow(352, 100)]
    if kind in ("bodysuit", "bra_friendly"):
        plunge = kind == "bra_friendly"
        neck = "L200,184 L224,108" if plunge else "Q200,150 224,108"
        left_x, right_x = (152, 232) if plunge else (168, 218)
        body = ("M150,118 L176,108 " + neck + " L250,118 Q258,170 244,206 Q240,240 250,262 Q236,292 218,312 L214,326 L186,326 L182,312 "
                "Q164,292 150,262 Q160,240 156,206 Q142,170 150,118 Z")  # fmt: skip
        for x in (left_x, right_x):
            out.append(_g("strap", [_path(f"M{x},58 L{x + 14},58 L{x + 14},112 L{x},112 Z", paint, LW_DETAIL + 0.4)]))
        out.append(_path(body, paint))
        out.append(_dark(body, 0.03))
        out.append(_line("M186,316 L214,316", 2.4))  # popper gusset
        seam_x, y0, y1 = [178, 222], 150, 296
    elif kind == "shorts":
        body = "M138,100 L262,100 Q276,150 280,210 L284,300 L214,300 Q208,268 200,262 Q192,268 186,300 L116,300 L120,210 Q124,150 138,100 Z"
        out.append(_path(body, paint))
        out += _band(138, 262, 100, 124, paint)
        seam_x, y0, y1 = [160, 240], 124, 296
    else:  # high-waisted brief
        out += _knickers_body(paint, "shape_brief")
        seam_x, y0, y1 = [168, 232], 100, 290
    if seamless != "yes":
        for x in seam_x:
            out.append(_g("seam-panel", [_line(f"M{x},{y0} Q{x + (6 if x < 200 else -6)},{(y0 + y1) / 2:.0f} {x},{y1}", 1.4, ' stroke-dasharray="5 3"', _hi(fill))]))
    bands = {"light": 0, "medium": 1, "firm": 2}.get(control, 1)
    mid = (y0 + y1) / 2
    for i in range(bands):
        y = mid - 26 + i * 52
        d = f"M156,{y:.0f} Q200,{y + 14:.0f} 244,{y:.0f}" if kind != "shorts" else f"M122,{y:.0f} Q200,{y + 14:.0f} 278,{y:.0f}"
        out.append(_g("control-band", [_line(d, 2.2, ' stroke-opacity=".55"', _hi(fill))]))
    return out


# --------------------------------------------------------------------------
# Dressing gown
# --------------------------------------------------------------------------


def dressing_gown(paint: str, fill: Fill, label: str | None, length: str = "knee", hood: str = "no", belt: str = "yes", fabric: str = "") -> list[str]:
    """An open wrap gown: shawl collar, two long sleeves, optionally a hood and a belt."""
    hem = GOWN_HEM.get(length, GOWN_HEM["knee"])
    out = [_shadow(hem + 10, 118)]
    if hood == "yes":
        h = "M146,84 Q150,18 200,16 Q250,18 254,84 Q200,64 146,84 Z"
        out.append(_g("hood", [_path(h, paint), _dark("M160,70 Q200,52 240,70 Q200,40 160,70 Z", 0.12), _line("M158,76 Q200,58 242,76", 1.4)]))
    for sx in (1, -1):
        sl = f"M{200 + sx * 54},82 L{200 + sx * 108},100 L{200 + sx * 132},212 L{200 + sx * 134},262 L{200 + sx * 84},264 L{200 + sx * 80},200 L{200 + sx * 70},150 Z"
        out.append(_g("sleeve", [_path(sl, paint), _dark(sl, 0.07),
                                  _line(f"M{200 + sx * 84},248 L{200 + sx * 133},246", 1.3, ' stroke-dasharray="4 3"')]))  # fmt: skip
    flare = 22 if length != "short" else 14
    inner = _inside(fill)
    out.append(_path(f"M176,84 L224,84 L212,{hem} L188,{hem} Z", inner, LW_DETAIL))
    # Two front panels cross over the inside; the shawl collar rolls along their edges.
    out.append(_path(f"M150,84 L176,84 L212,{hem} L{150 - flare},{hem} L150,210 Q142,150 150,84 Z", paint))
    out.append(_path(f"M250,84 L224,84 L190,{hem} L{250 + flare},{hem} L250,210 Q258,150 250,84 Z", paint))
    out.append(_dark(f"M224,84 L190,{hem} L{250 + flare},{hem} Z", 0.05))
    c_left = "M150,84 Q164,80 176,84 L214,190 L200,194 Z"
    c_right = "M250,84 Q236,80 224,84 L186,190 L200,194 Z"
    out += [_path(c_left, paint, LW_DETAIL + 0.4), _dark(c_left, 0.12), _path(c_right, paint, LW_DETAIL + 0.4), _dark(c_right, 0.12)]
    if fabric == "waffle":
        for x in range(158, 245, 12):
            out.append(_line(f"M{x},230 L{x},{hem - 14}", 0.8, ' stroke-opacity=".3"'))
        for y in range(236, hem - 10, 12):
            out.append(_line(f"M{150 - 4},{y} L{250 + 4},{y}", 0.8, ' stroke-opacity=".3"'))
    elif fabric == "towelling":
        for y in range(230, hem - 10, 14):
            out.append(_line(" ".join(f"M{x},{y} q4,-6 8,0" for x in range(156, 244, 14)), 0.9, ' stroke-opacity=".4"'))
    elif fabric == "satin":
        out.append(_highlight("M162,120 Q158,200 164,250", 6, 0.35))
    out.append(_line(f"M{150 - flare + 4},{hem - 10} L{250 + flare - 4},{hem - 10}", 1.2, ' stroke-dasharray="4 3"'))
    if belt == "yes":
        b = "M148,186 L252,186 L252,204 L148,204 Z"
        knot = "M196,190 Q200,184 204,190 L206,238 L194,238 Z"
        out.append(_g("belt", [_path(b, paint, LW_DETAIL + 0.4), _dark(b, 0.16), _path(knot, paint, LW_DETAIL),
                               _path("M196,204 L186,244 L198,240 Z", paint, LW_DETAIL), _path("M204,204 L214,244 L202,240 Z", paint, LW_DETAIL)]))  # fmt: skip
    return out


def _inside(fill: Fill) -> str:
    """The garment's inside: a shade of a light color, a tint of a dark one."""
    r, g, b = (int(fill.base[i : i + 2], 16) for i in (1, 3, 5))
    light = (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.4
    return _shade(fill.base, 0.35) if light else _tint(fill.base, 0.4)


# --------------------------------------------------------------------------
# Boxers
# --------------------------------------------------------------------------

#: fit -> (waist half-width, hem y, hem half-width at the leg)
BOXER_FITS = {"trunks": (100, 240, 106), "boxer": (100, 312, 122)}


def boxers(paint: str, fill: Fill, label: str | None, fit: str = "boxer") -> list[str]:
    """Men's pants: short-leg trunks, long-leg boxer shorts (button fly) or Y-front briefs."""
    out = [_shadow(330, 110)]
    if fit == "brief":
        d = "M100,124 L300,124 Q312,168 296,206 Q252,224 226,292 Q200,306 174,292 Q148,224 104,206 Q88,168 100,124 Z"
        out.append(_path(d, paint))
        out.append(_dark(d, 0.04))
        out += _band(100, 300, 124, 146, paint)
        out.append(_g("fly", [_line("M200,146 L200,214 Q200,226 214,230 M200,214 Q200,226 186,230", 1.6, "", _hi(fill)), _line("M186,146 L186,198 Q190,212 200,214", 1.3, ' stroke-dasharray="3 3"', _hi(fill))]))
        out.append(_g("leg", [_line("M108,214 Q150,224 172,288", 1.3, ' stroke-dasharray="4 3"', _hi(fill))]))
        out.append(_g("leg", [_line("M292,214 Q250,224 228,288", 1.3, ' stroke-dasharray="4 3"', _hi(fill))]))
        return out
    ww, hem, hh = BOXER_FITS.get(fit, BOXER_FITS["boxer"])
    d = (f"M{200 - ww},126 L{200 + ww},126 Q{200 + hh + 6},170 {200 + hh},{hem - 40} L{200 + hh + 6},{hem} L{200 + 12},{hem} "
         f"Q206,{hem - 34} 200,{hem - 40} Q194,{hem - 34} {200 - 12},{hem} L{200 - hh - 6},{hem} L{200 - hh},{hem - 40} "
         f"Q{200 - hh - 6},170 {200 - ww},126 Z")  # fmt: skip
    out.append(_path(d, paint))
    out.append(_dark(d, 0.04))
    out += _band(200 - ww, 200 + ww, 126, 148, paint)
    out.append(_g("leg", [_line(f"M{200 - hh - 3},{hem - 10} L{200 - 14},{hem - 10}", 1.3, ' stroke-dasharray="4 3"', _hi(fill))]))
    out.append(_g("leg", [_line(f"M{200 + 14},{hem - 10} L{200 + hh + 3},{hem - 10}", 1.3, ' stroke-dasharray="4 3"', _hi(fill))]))
    if fit == "boxer":
        out.append(_g("fly", [_path("M184,148 L184,200 Q184,210 194,210 L206,210 L206,148 Z", paint, LW_DETAIL), _line("M196,152 L196,206", 1.0, ' stroke-opacity=".5"'),
                              '<circle cx="200" cy="160" r="3.4" fill="#ffffff" stroke="#2b3440" stroke-width="1.2"/>',
                              '<circle cx="200" cy="184" r="3.4" fill="#ffffff" stroke="#2b3440" stroke-width="1.2"/>']))  # fmt: skip
    else:
        out.append(_g("fly", [_line("M200,148 L200,196 Q200,210 212,214", 1.6, "", _hi(fill)), _line("M188,148 L188,190 Q192,204 204,208", 1.3, ' stroke-dasharray="3 3"', _hi(fill))]))
    return out


register(
    {"knickers": knickers, "tights": tights, "vest": vest, "slip": slip, "shapewear": shapewear,
     "dressing_gown": dressing_gown, "boxers": boxers},
)  # fmt: skip

SHAPES = ("knickers", "tights", "vest", "slip", "shapewear", "dressing_gown", "boxers")
