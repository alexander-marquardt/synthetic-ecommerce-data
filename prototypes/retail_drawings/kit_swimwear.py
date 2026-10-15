"""Swimwear shapes for the retail drawing kit (gen#212).

Each type of :mod:`swimwear_rows` has its own flat drawing in the kit's house style: the
kit's ink outline and the record's fill on the garment, so a shopper tells a swimsuit from a
tankini, a bikini top from its bottoms and a changing robe from a kaftan at thumbnail size.

================  ==================================================  ==========================
shape             draws                                               params
================  ==================================================  ==========================
swimsuit          one piece: scoop, plunge, halter or one shoulder    cut, tummy, padded, leg
bikini_top        triangle, bandeau, balcony or underwired top        top_shape
bikini_bottoms    briefs at a high, mid or low rise, tied or not      rise, tie_side
tankini           a swim top: crop, hip or long, three supports       length, support
swim_shorts       trunks: short, mid or long, drawstring or elastic   length, waist
kids_swimsuit     a child's one piece, sleeveless to long sleeved     sleeve, upf, nappy
period_swimwear   briefs with an absorbent gusset of one or two       absorbency, cut
                  layers
cover_up          a kaftan: mini, midi or maxi, with wide sleeves     length
changing_robe     a hooded robe: hip, knee or full, two linings       length, lining, waterproof
================  ==================================================  ==========================

A drawing never prints a size. What a row states and the drawing can count is drawn as that
many marked groups (``tests/test_retail_swimwear_212.py`` counts them per record): ``cup``,
``underwire``, ``strap``, ``tie``, ``ruching``, ``band``, ``waistband``, ``leg-opening``,
``shelf-band``, ``leg``, ``drawstring``, ``elastic``, ``sleeve``, ``upf-badge``, ``leg-band``,
``absorbent-layer``, ``hood``, ``lining``, ``storm-flap``. Every param is a string with a
default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW_DETAIL, Fill, _line, _mirror, _path, register
from kit_garments import _dark
from kit_underwear import _f, _g, _hi, _shadow

Seg = tuple  # ("L", x, y) | ("Q", cx, cy, x, y) | ("C", c1x, c1y, c2x, c2y, x, y)


def _s(segs: list[Seg]) -> str:
    return " ".join(
        s[0] + " ".join(f"{_f(s[i])},{_f(s[i + 1])}" for i in range(1, len(s), 2)) for s in segs
    )


def _d(start: tuple[float, float], segs: list[Seg]) -> str:
    return f"M{_f(start[0])},{_f(start[1])} " + _s(segs)


def _flip(start: tuple[float, float], segs: list[Seg]) -> list[Seg]:
    """The left-hand run ``start`` + ``segs`` walked backwards on the right-hand side, mirrored."""
    pts = [start] + [(s[-2], s[-1]) for s in segs]
    out: list[Seg] = []
    for i in range(len(segs) - 1, -1, -1):
        s, end = segs[i], pts[i]
        ctrl = [(s[j], s[j + 1]) for j in range(1, len(s) - 2, 2)][::-1]
        flat = [v for c in ctrl for v in (400 - c[0], c[1])]
        out.append((s[0], *flat, 400 - end[0], end[1]))
    return out


def _closed(start: tuple[float, float], left: list[Seg]) -> str:
    """A closed outline: the left run from ``start`` (top centre) to the bottom centre, then its
    mirror image walked back to the top."""
    return _d(start, left + _flip(start, left)) + " Z"


def _leg_ctrl(leg: str) -> tuple[float, float]:
    return {"regular": (136, 282), "high": (166, 246)}.get(leg, (136, 282))


# --------------------------------------------------------------------------
# Swimsuit
# --------------------------------------------------------------------------

SWIM_NECK = {
    "scoop": ((200, 120), [("Q", 172, 122, 166, 88), ("L", 164, 60), ("L", 144, 60), ("Q", 140, 100, 134, 138)]),
    "plunge": ((200, 178), [("L", 168, 100), ("L", 166, 60), ("L", 146, 60), ("Q", 140, 100, 134, 138)]),
    "halter": ((200, 132), [("Q", 178, 128, 174, 98), ("L", 198, 46), ("L", 184, 44), ("Q", 152, 96, 134, 138)]),
}


def swimsuit(paint: str, fill: Fill, label: str | None, cut: str = "scoop", tummy: str = "no", padded: str = "no", leg: str = "regular") -> list[str]:
    """A one piece. The cut sets the neckline, the leg its opening; ruching and cups are marked."""
    cut = cut.replace("-", "_")
    cx, cy = _leg_ctrl(leg)
    lower: list[Seg] = [("Q", 140, 196, 136, 230), ("Q", cx, cy, 184, 298), ("L", 200, 298)]
    if cut == "one_shoulder":
        up: list[Seg] = [("L", 166, 98), ("L", 164, 60), ("L", 144, 60), ("Q", 140, 100, 134, 138)]
        d = _d((200, 107), [*up, *lower, *_flip((134, 138), lower), ("L", 266, 124)]) + " Z"
    else:
        start, upper = SWIM_NECK.get(cut, SWIM_NECK["scoop"])
        d = _closed(start, upper + lower)
    out = [_shadow(342, 96), _path(d, paint), _dark(d, 0.05)]
    out.append(_g("leg-opening", [_line(f"M140,232 Q{cx + 6:.0f},{cy - 6:.0f} 182,290", 1.2, ' stroke-dasharray="4 3"', _hi(fill))]))
    out.append(_g("leg-opening", [_line(f"M260,232 Q{400 - cx - 6:.0f},{cy - 6:.0f} 218,290", 1.2, ' stroke-dasharray="4 3"', _hi(fill))]))
    if tummy == "yes":
        out.append(_g("ruching", [_line(f"M156,{y} Q200,{y + 12} 244,{y}", 1.3, "", _hi(fill)) for y in (184, 200, 216)]))
    if padded == "yes":
        out.append(_g("cup", [_path("M160,138 Q170,176 198,150 Q188,128 160,138 Z", paint, LW_DETAIL), _dark("M160,138 Q170,176 198,150 Q188,128 160,138 Z", 0.1)]))
        out.append(_g("cup", [_path("M240,138 Q230,176 202,150 Q212,128 240,138 Z", paint, LW_DETAIL), _dark("M240,138 Q230,176 202,150 Q212,128 240,138 Z", 0.1)]))
    return out


# --------------------------------------------------------------------------
# Bikini top and bottoms
# --------------------------------------------------------------------------


def _cup_tri(side: int, paint: str) -> str:
    d = "M196,124 L108,112 Q130,176 196,170 Z" if side < 0 else _mirror("M196,124 L108,112 Q130,176 196,170 Z")
    return _g("cup", [_path(d, paint), _dark(d, 0.05)])


def bikini_top(paint: str, fill: Fill, label: str | None, top_shape: str = "triangle") -> list[str]:
    """A bikini top: two triangles on ties, a bandeau band, two balcony cups or underwired cups."""
    out = [_shadow(300, 110)]
    if top_shape == "bandeau":
        d = "M82,134 Q200,146 318,134 L322,196 Q200,208 78,196 Z"
        out += [_g("band", [_path(d, paint), _dark(d, 0.05), _line("M92,165 Q200,177 308,165", 1.1, ' stroke-dasharray="4 3"', _hi(fill))])]
        out += [_g("tie", [_line("M82,150 Q60,150 46,168", 3.0)]), _g("tie", [_line("M318,150 Q340,150 354,168", 3.0)])]
        return out
    if top_shape == "triangle":
        out += [_g("strap", [_line("M108,112 Q150,70 200,58", 3.2)]), _g("strap", [_line("M292,112 Q250,70 200,58", 3.2)])]
        out += [_cup_tri(-1, paint), _cup_tri(1, paint), _line("M100,166 Q60,170 36,184", 3.0), _line("M300,166 Q340,170 364,184", 3.0)]
        return out
    cup_l = "M104,126 Q112,198 196,184 L196,130 Q150,140 104,126 Z" if top_shape == "balcony" else "M110,120 Q92,196 160,206 Q200,208 198,150 Q172,106 110,120 Z"
    out += [_g("strap", [_line("M118,126 Q124,90 146,66", 4.0)]), _g("strap", [_line("M282,126 Q276,90 254,66", 4.0)])]
    for d in (cup_l, _mirror(cup_l)):
        out += [_g("cup", [_path(d, paint), _dark(d, 0.05)])]
    if top_shape == "underwired":
        for d in ("M106,190 Q150,222 198,200", _mirror("M106,190 Q150,222 198,200")):
            out += [_g("underwire", [_line(d, 3.0, "", _hi(fill))])]
    return out


BOTTOM_RISE = {"high": 100, "mid": 146, "low": 182}


def bikini_bottoms(paint: str, fill: Fill, label: str | None, rise: str = "mid", tie_side: str = "no") -> list[str]:
    """Bikini bottoms: the waist sits at the rise; a tie-side pair has a cord at each hip."""
    wy = BOTTOM_RISE.get(rise, 146)
    left = [("L", 96, wy), ("Q", 106, (wy + 218) / 2, 114, 218), ("Q", 156, 270, 200, 296)]
    d = _closed((200, wy), left)
    out = [_shadow(330, 110), _path(d, paint), _dark(d, 0.05)]
    out.append(_g("leg-opening", [_line("M116,220 Q150,262 192,286", 1.2, ' stroke-dasharray="4 3"', _hi(fill))]))
    out.append(_g("leg-opening", [_line("M284,220 Q250,262 208,286", 1.2, ' stroke-dasharray="4 3"', _hi(fill))]))
    if tie_side == "yes":
        out += [_g("tie", [_line(f"M96,{wy + 6} Q66,{wy + 4} 52,{wy + 30} M96,{wy + 6} Q70,{wy + 36} 62,{wy + 56}", 3.0)])]
        out += [_g("tie", [_line(f"M304,{wy + 6} Q334,{wy + 4} 348,{wy + 30} M304,{wy + 6} Q330,{wy + 36} 338,{wy + 56}", 3.0)])]
    return out


# --------------------------------------------------------------------------
# Tankini
# --------------------------------------------------------------------------

TANKINI_HEM = {"crop": 214, "hip": 270, "long": 322}


def tankini(paint: str, fill: Fill, label: str | None, length: str = "hip", support: str = "light") -> list[str]:
    """A swim top on two straps: where the hem falls is the length; support adds a shelf band
    (medium) or underwires (underwired)."""
    hem = TANKINI_HEM.get(length, 270)
    left = [("Q", 176, 114, 170, 84), ("L", 168, 56), ("L", 146, 56), ("Q", 140, 100, 128, 140), ("Q", 142, (140 + hem) / 2, 138, hem)]
    d = _closed((200, 118), left + [("Q", 170, hem + 8, 200, hem + 4)])
    out = [_shadow(hem + 36, 96), _path(d, paint), _dark(d, 0.05)]
    out += [_g("strap", [_line("M157,60 L157,96", 2.2, "", _hi(fill))]), _g("strap", [_line("M243,60 L243,96", 2.2, "", _hi(fill))])]
    if support == "medium":
        out += [_g("shelf-band", [_line("M138,184 Q200,200 262,184", 1.6, "", _hi(fill)), _line("M138,194 Q200,210 262,194", 1.2, ' stroke-dasharray="4 3"', _hi(fill))])]
    elif support == "underwired":
        for d2 in ("M146,176 Q172,206 198,184", _mirror("M146,176 Q172,206 198,184")):
            out += [_g("underwire", [_line(d2, 3.0, "", _hi(fill))])]
    out.append(_line(f"M140,{hem - 8} Q200,{hem + 6} 260,{hem - 8}", 1.2, ' stroke-dasharray="4 3"', _hi(fill)))
    return out


# --------------------------------------------------------------------------
# Swim shorts
# --------------------------------------------------------------------------

SHORTS_HEM = {"short": 228, "mid": 276, "long": 328}


def swim_shorts(paint: str, fill: Fill, label: str | None, length: str = "mid", waist: str = "drawstring") -> list[str]:
    """Trunks: two legs from a waistband; a drawstring pair is knotted with two cords, an
    elasticated pair shows stitched elastic."""
    hem = SHORTS_HEM.get(length, 276)
    top = 92
    d = (f"M94,{top} L306,{top} Q316,150 318,{(top + hem) / 2:.0f} L322,{hem} L218,{hem} Q214,{hem - 64:.0f} 200,{top + 118} Q186,{hem - 64:.0f} 182,{hem} L78,{hem} L82,{(top + hem) / 2:.0f} Q84,150 94,{top} Z")
    out = [_shadow(hem + 28, 116), _path(d, paint), _dark(d, 0.05)]
    out += [_g("leg", [_line(f"M82,{hem - 12} L178,{hem - 12}", 1.3, ' stroke-dasharray="4 3"', _hi(fill))]), _g("leg", [_line(f"M222,{hem - 12} L318,{hem - 12}", 1.3, ' stroke-dasharray="4 3"', _hi(fill))])]
    band = f"M94,{top} L306,{top} L308,{top + 26} L92,{top + 26} Z"
    out.append(_g("waistband", [_path(band, paint, LW_DETAIL + 0.4), _dark(band, 0.1)]))
    if waist == "drawstring":
        out.append(_g("drawstring", [_line(f"M200,{top + 14} Q176,{top + 40} 170,{top + 66} M200,{top + 14} Q224,{top + 40} 230,{top + 66}", 2.2, "", _hi(fill)), f'<circle cx="200" cy="{top + 14}" r="4" fill="{_hi(fill)}" stroke="{INK}" stroke-width="1"/>']))
    else:
        out.append(_g("elastic", [_line(f"M100,{top + 13} L300,{top + 13}", 1.2, ' stroke-dasharray="3 3"', _hi(fill))]))
    return out


# --------------------------------------------------------------------------
# Kids' swimsuit
# --------------------------------------------------------------------------

KIDS_SLEEVE = {"short": 108, "long": 74}


def kids_swimsuit(paint: str, fill: Fill, label: str | None, sleeve: str = "none", upf: str = "no", nappy: str = "no") -> list[str]:
    """A child's one piece: sleeveless, short or long sleeved; a UPF style carries a sun badge,
    a nappy-friendly one a double leg band."""
    left = [("Q", 176, 112, 168, 92), ("L", 162, 64), ("L", 140, 64), ("Q", 136, 110, 128, 140), ("Q", 146, 190, 144, 232), ("Q", 150, 268, 172, 280), ("Q", 188, 284, 200, 282)]
    d = _closed((200, 118), left)
    out = [_shadow(318, 90), _path(d, paint), _dark(d, 0.05)]
    if sleeve in KIDS_SLEEVE:
        x = KIDS_SLEEVE[sleeve]
        for sd in (f"M140,70 L{x},{96 if sleeve == 'short' else 214} L{x + 26},{104 if sleeve == 'short' else 220} L134,142 Z",
                   _mirror(f"M140,70 L{x},{96 if sleeve == 'short' else 214} L{x + 26},{104 if sleeve == 'short' else 220} L134,142 Z")):
            out.append(_g("sleeve", [_path(sd, paint), _dark(sd, 0.06)]))
    if upf == "yes":
        out.append(_g("upf-badge", ['<circle cx="200" cy="190" r="16" fill="#ffffff" fill-opacity=".55" stroke="#2b3440" stroke-width="1.2"/>', _line("M200,170 L200,162 M200,210 L200,218 M180,190 L172,190 M220,190 L228,190", 1.6)]))
    if nappy == "yes":
        out.append(_g("leg-band", [_line("M146,244 Q154,270 176,278", 1.3, ' stroke-dasharray="3 3"', _hi(fill)), _line("M154,236 Q162,260 180,268", 1.1, "", _hi(fill))]))
        out.append(_g("leg-band", [_line("M254,244 Q246,270 224,278", 1.3, ' stroke-dasharray="3 3"', _hi(fill)), _line("M246,236 Q238,260 220,268", 1.1, "", _hi(fill))]))
    return out


# --------------------------------------------------------------------------
# Period swimwear
# --------------------------------------------------------------------------


def period_swimwear(paint: str, fill: Fill, label: str | None, absorbency: str = "light", cut: str = "bikini") -> list[str]:
    """Briefs with a gusset: one absorbent layer is light, two are moderate."""
    wy = 112 if cut == "high_waisted" else 150
    left = [("L", 96, wy), ("Q", 104, (wy + 214) / 2, 112, 214), ("Q", 154, 266, 200, 296)]
    d = _closed((200, wy), left)
    out = [_shadow(330, 110), _path(d, paint), _dark(d, 0.05)]
    band = f"M97,{wy} L303,{wy} L304,{wy + 18} L96,{wy + 18} Z"
    out.append(_g("waistband", [_path(band, paint, LW_DETAIL + 0.4), _dark(band, 0.1)]))
    layers = 2 if absorbency == "moderate" else 1
    for i in range(layers):
        g = f"M182,{206 + i * 12} Q200,{198 + i * 12} 218,{206 + i * 12} L214,{268 - i * 6} Q200,{282 - i * 6} 186,{268 - i * 6} Z"
        out.append(_g("absorbent-layer", [_path(g, paint, LW_DETAIL), _dark(g, 0.1 + 0.08 * i)]))
    return out


# --------------------------------------------------------------------------
# Cover-up and changing robe
# --------------------------------------------------------------------------

COVER_HEM = {"mini": 250, "midi": 304, "maxi": 360}
ROBE_HEM = {"hip": 258, "knee": 312, "full": 362}


def cover_up(paint: str, fill: Fill, label: str | None, length: str = "midi") -> list[str]:
    """A kaftan: a V neck, wide sleeves and a flared body; the hem sets the length."""
    hem = COVER_HEM.get(length, 304)
    left = [("L", 168, 56), ("L", 138, 62), ("L", 70, 130), ("L", 82, 170), ("L", 138, 128), ("Q", 134, (130 + hem) / 2, 118, hem)]
    d = _closed((200, 104), left + [("Q", 160, hem + 10, 200, hem + 6)])
    out = [_shadow(hem + 30, 120), _path(d, paint), _dark(d, 0.05)]
    for sd in ("M138,62 L70,130 L82,170 L138,128 Z", _mirror("M138,62 L70,130 L82,170 L138,128 Z")):
        out.append(_g("sleeve", [_line(sd, 1.2, ' stroke-dasharray="4 3"', _hi(fill))]))
    out.append(_line(f"M118,{hem - 12} Q200,{hem + 2} 282,{hem - 12}", 1.2, ' stroke-dasharray="4 3"', _hi(fill)))
    return out


def changing_robe(paint: str, fill: Fill, label: str | None, length: str = "knee", lining: str = "towelling", waterproof: str = "no") -> list[str]:
    """A hooded robe with sleeves: fleece lining is drawn as a wavy pile, towelling as loops; a
    waterproof shell has a storm flap down the front."""
    hem = ROBE_HEM.get(length, 312)
    left = [("Q", 176, 92, 168, 78), ("L", 140, 70), ("L", 108, 112), ("L", 92, (112 + hem) / 2 + 20), ("L", 128, (112 + hem) / 2 + 24), ("L", 134, 130), ("Q", 130, (130 + hem) / 2, 120, hem)]
    d = _closed((200, 100), left + [("Q", 160, hem + 8, 200, hem + 4)])
    out = [_shadow(hem + 28, 120), _path(d, paint), _dark(d, 0.05)]
    hood = "M150,72 Q150,22 200,20 Q250,22 250,72 Q226,92 200,92 Q174,92 150,72 Z"
    out.append(_g("hood", [_path(hood, paint), _dark(hood, 0.05)]))
    rim = "M158,70 Q200,98 242,70" if lining == "fleece" else "M158,70 Q200,98 242,70"
    pile = " ".join(f"M{160 + i * 10},{74 + (i % 2) * 4} q4,-6 8,0" for i in range(8)) if lining == "fleece" else " ".join(f"M{162 + i * 12},{76} m0,0 a4,4 0 1 1 0.1,0" for i in range(7))
    out.append(_g("lining", [_line(rim, 2.0, "", _hi(fill)), _line(pile, 1.3, "", _hi(fill))]))
    for sx in (1, -1):
        sd = f"M{200 + sx * 70},112 L{200 + sx * 108},{(112 + hem) / 2 + 20:.0f} L{200 + sx * 72},{(112 + hem) / 2 + 24:.0f} Z"
        out.append(_g("sleeve", [_line(sd, 1.2, ' stroke-dasharray="4 3"', _hi(fill))]))
    out.append(_line(f"M200,92 L200,{hem}", 1.4, "", INK))
    if waterproof == "yes":
        out.append(_g("storm-flap", [_path(f"M200,96 L214,96 L214,{hem - 6} L200,{hem - 6} Z", paint, LW_DETAIL), _dark(f"M200,96 L214,96 L214,{hem - 6} L200,{hem - 6} Z", 0.1)]))
    return out


register(
    {"swimsuit": swimsuit, "bikini_top": bikini_top, "bikini_bottoms": bikini_bottoms,
     "tankini": tankini, "swim_shorts": swim_shorts, "kids_swimsuit": kids_swimsuit,
     "period_swimwear": period_swimwear, "cover_up": cover_up, "changing_robe": changing_robe},
)  # fmt: skip

SHAPES = ("swimsuit", "bikini_top", "bikini_bottoms", "tankini", "swim_shorts", "kids_swimsuit",
          "period_swimwear", "cover_up", "changing_robe")
