"""Lower-body basics for the retail drawing kit (gen#206): six shapes, each its own.

``leggings(length, rise, pocket)``, ``joggers(fit, cuff, rise, pocket, cargo)``,
``shorts(length, style, pocket)``, ``cycling_shorts(length, rise, pad, pocket)``,
``tracksuit(top, pieces, fit)`` and ``skirt(shape, length)``. Every param is something a
shopper filters on, and every count the record states is a count the drawing marks: a
``pocket`` group per pocket, a ``belt-loop`` group per loop, a ``piece`` group per piece of a
tracksuit, a ``tier`` group per ruffle of a tiered skirt. The rise is stamped on the
waistband (``waistband-high``) and the length on the hem (``hem-knee``), so a test reads
them back. A shape is painted in the record's fill and prints no size.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, SIZE, Fill, _line, _path, register
from kit_garments import Pt, _dark, _f, _x_at, mirror, smooth

GOLD = "#d6b56a"


def _group(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _circle(x: float, y: float, r: float, fill: str = "#ffffff", width: float = 1.2) -> str:
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{width:g}"/>'


def _trunc(pts: list[Pt], hem: float) -> list[Pt]:
    """``pts`` (top to bottom) cut at height ``hem``: the polyline ends exactly there."""
    out: list[Pt] = []
    for a, b in zip(pts, pts[1:], strict=False):
        out.append(a)
        if a[1] < hem <= b[1]:
            t = (hem - a[1]) / (b[1] - a[1])
            out.append((a[0] + (b[0] - a[0]) * t, hem))
            return out
    out.append(pts[-1])
    return out


def _legs(oL: list[Pt], iL: list[Pt]) -> str:
    """The outline of a pair of legs: the left outer seam down, the left inner seam up, then
    the right leg as the mirror image."""
    oR, iR = mirror(oL), mirror(iL)
    return (f"M{_f(oL[0])} {smooth(oL)} L{_f(iL[-1])} {smooth(iL[::-1])} "
            f"L{_f(iR[0])} {smooth(iR)} L{_f(oR[-1])} {smooth(oR[::-1])} Z")  # fmt: skip


def _band(paint: str, bt: float, bb: float, wx: float, cls: str, ribs: bool = True) -> str:
    """A waistband from ``wx`` to its mirror, with vertical rib marks."""
    d = f"M{wx},{bt} L{SIZE - wx},{bt} L{SIZE - wx},{bb} L{wx},{bb} Z"
    parts = [_path(d, paint, LW), _dark(d, 0.16)]
    if ribs:
        xs = range(int(wx) + 7, int(SIZE - wx) - 4, 7)
        parts.append(_line(" ".join(f"M{x},{bt + 4} L{x + 1},{bb - 4}" for x in xs), 1.0, ' stroke-opacity=".5"'))
    return _group(cls, parts)


def _cords(bb: float, cy: float) -> list[str]:
    """A drawstring tied at the centre of the band, the two ends hanging with a knot each."""
    return [
        _line(f"M196,{cy} Q186,{bb + 30} 178,{bb + 52} M204,{cy} Q214,{bb + 30} 222,{bb + 52}", 2.4),
        _circle(178, bb + 54, 3.5), _circle(222, bb + 54, 3.5),
        _circle(190, cy, 2.4, INK, 1), _circle(210, cy, 2.4, INK, 1),
    ]  # fmt: skip


def _slant_pocket(side: int, wx: float, bb: float, outer: list[Pt], depth: float = 46) -> str:
    """A slanted side pocket opening (one ``pocket`` group)."""

    def X(x: float) -> float:
        return x if side == 1 else SIZE - x

    py = bb + depth
    ox = _x_at(outer, py)
    return _group("pocket", [_line(f"M{X(wx + 14):.1f},{bb} Q{X(wx + 8):.1f},{py - 8:.1f} {X(ox + 1):.1f},{py:.1f}", 1.6),
                             _line(f"M{X(wx + 14):.1f},{bb} Q{X(wx + 20):.1f},{py + 6:.1f} {X(ox + 1):.1f},{py:.1f}", 1.0, ' stroke-opacity=".45"')])  # fmt: skip


def _cargo_pocket(side: int, x_edge: float, y0: float, w: float = 32, h: float = 46) -> str:
    """A flapped cargo patch on the outer thigh (one ``cargo-pocket`` group); ``x_edge`` is the
    outer seam's x at its top."""
    x = x_edge + 4 if side == 1 else SIZE - x_edge - 4 - w
    return _group("cargo-pocket", [
        f'<rect x="{x:.1f}" y="{y0:.1f}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="1.6"/>',
        f'<path d="M{x:.1f},{y0:.1f} L{x + w:.1f},{y0:.1f} L{x + w:.1f},{y0 + 12:.1f} L{x + w / 2:.1f},{y0 + 17:.1f} L{x:.1f},{y0 + 12:.1f} Z" fill="#000000" fill-opacity=".14" stroke="{INK}" stroke-width="1.4"/>',
        _circle(x + w / 2, y0 + 12, 2.4, GOLD, 0.8),
    ])  # fmt: skip


def _denim_pocket(side: int, wx: float, bb: float, outer: list[Pt]) -> str:
    """A western scoop pocket (one ``pocket`` group): a curved opening with a topstitch beside
    it and a gold rivet at its lower corner."""

    def X(x: float) -> float:
        return x if side == 1 else SIZE - x

    py = bb + 46
    ox = _x_at(outer, py)
    return _group("pocket", [
        _line(f"M{X(wx + 6):.1f},{bb} Q{X(wx + 12):.1f},{py - 4:.1f} {X(ox + 3):.1f},{py - 6:.1f}", 1.8),
        _line(f"M{X(wx + 11):.1f},{bb + 2} Q{X(wx + 17):.1f},{py + 1:.1f} {X(ox + 8):.1f},{py - 3:.1f}", 1.0, ' stroke-dasharray="3 2" stroke-opacity=".75"'),
        _circle(X(ox + 3), py - 6, 2.6, GOLD, 0.8)])  # fmt: skip


def _hem_line(o: list[Pt], i: list[Pt], y: float) -> str:
    return _line(f"M{_x_at(o, y):.1f},{y:.1f} L{_x_at(i, y):.1f},{y:.1f}", 1.2)


# --------------------------------------------------------------------------
# Leggings
# --------------------------------------------------------------------------

LEG_HEM = {"full": 372, "7_8": 338, "cropped": 294}
RISE_BAND = {"high": (54, 100, 142), "mid": (86, 110, 136)}


def leggings(paint: str, fill: Fill, label: str | None, length: str = "full", rise: str = "high",
             pocket: str = "no") -> list[str]:  # fmt: skip
    """Close-fitting leggings: a tapered leg that stops at the ankle (full), above it (7/8) or
    at mid calf (cropped); a high rise shows a deep waistband; side pockets are drawn."""
    bt, bb, wx = RISE_BAND[rise]
    hem = LEG_HEM[length]
    oL = _trunc([(wx, bb), (134, 156), (137, 215), (148, 280), (156, 332), (160, 372)], hem)
    iL = _trunc([(198, 202), (194, 245), (190, 300), (186, 372)], hem)
    out = [_group(f"hem-{length}", [_path(_legs(oL, iL), paint)])]
    for o, i in ((oL, iL), (mirror(oL), mirror(iL))):
        out.append(_hem_line(o, i, hem - 8))
        dx = 7 if o is oL else -7
        shifted = [(x + dx, y) for x, y in o[1:]]
        out.append(_line(f"M{_f(shifted[0])} {smooth(shifted)}", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".5"'))
    out.append(_line(f"M200,{bb} L200,202", 1.2, ' stroke-opacity=".5"'))
    out.append(_band(paint, bt, bb, wx, f"waistband-{rise}"))
    if rise == "high":
        out.append(_line(f"M{wx + 2},{bt + 14} L{SIZE - wx - 2},{bt + 14}", 1.0, ' stroke-opacity=".5"'))
    if pocket == "yes":
        for side in (1, -1):
            x0 = _x_at(oL, 176) + 7
            x = x0 if side == 1 else SIZE - x0 - 20
            out.append(_group("pocket", [
                f'<path d="M{x:.1f},166 L{x + 20:.1f},166 L{x + 20:.1f},210 Q{x + 10:.1f},218 {x:.1f},210 Z" fill="#000000" fill-opacity=".1" stroke="{INK}" stroke-width="1.4"/>',
                _line(f"M{x:.1f},166 L{x + 20:.1f},166", 2.2)]))  # fmt: skip
    return out


# --------------------------------------------------------------------------
# Joggers
# --------------------------------------------------------------------------

#: fit -> the left leg's outer x at the hip, thigh, knee and calf.
JOG_FIT = {"slim": (127, 124, 129, 135), "regular": (122, 114, 117, 122),
           "relaxed": (116, 105, 104, 107), "oversized": (106, 92, 88, 90)}  # fmt: skip
JOG_RISE = {"high": (44, 76, 136), "mid": (60, 90, 134)}


def joggers(paint: str, fill: Fill, label: str | None, fit: str = "regular", cuff: str = "elastic",
            rise: str = "mid", pocket: str = "yes", cargo: str = "no") -> list[str]:  # fmt: skip
    """Sweat joggers: a drawstring waist, a leg whose width follows ``fit``, and either a ribbed
    elasticated cuff the leg gathers into or an open hem; ``cargo`` adds thigh pockets."""
    bt, bb, wx = JOG_RISE[rise]
    hip, th, kn, ca = JOG_FIT[fit]
    outer: list[Pt] = [(wx, bb), (hip, 150), (th, 215), (kn, 275), (ca, 322)]
    inner: list[Pt] = [(198, 198), (197, 240), (196, 290), (195, 328)]
    if cuff == "elastic":
        # The leg tapers down into a snug rib cuff, narrower than the leg above it.
        oL = [(wx, bb), (hip, 150), (th, 215), (th + (150 - th) * 0.5 + (kn - th) * 0.3, 278), (150, 340)]
        iL = [*inner[:3], (194, 340)]
        hem_y = 340
    else:
        oL = [*outer, (ca - 3, 368)]
        iL = [*inner, (194, 368)]
        hem_y = 368
    out = [_group(f"hem-{cuff}", [_path(_legs(oL, iL), paint)])]
    for o, i in ((oL, iL), (mirror(oL), mirror(iL))):
        if cuff == "elastic":
            x0, x1 = sorted((o[-1][0], i[-1][0]))
            d = f"M{x0:.1f},{hem_y - 3} L{x1:.1f},{hem_y - 3} L{x1 - 1:.1f},{hem_y + 28} L{x0 + 1:.1f},{hem_y + 28} Z"
            ribs = " ".join(f"M{x:.1f},{hem_y} L{x:.1f},{hem_y + 26}" for x in range(int(x0) + 5, int(x1) - 2, 6))
            out += [_path(d, paint, LW_DETAIL + 0.6), _dark(d, 0.18), _line(ribs, 1.0, ' stroke-opacity=".55"')]
        else:
            out.append(_hem_line(o, i, hem_y - 9))
    out += [_band(paint, bt, bb, wx, f"waistband-{rise}"), *_cords(bb, (bt + bb) / 2),
            _line(f"M200,{bb} L200,{198 - 4}", 1.2, ' stroke-opacity=".5"')]  # fmt: skip
    if pocket == "yes":
        out += [_slant_pocket(1, wx, bb, oL, 54), _slant_pocket(-1, wx, bb, oL, 54)]
    if cargo == "yes":
        top = 196
        out += [_cargo_pocket(1, _x_at(oL, top), top), _cargo_pocket(-1, _x_at(oL, top), top)]
    return out


# --------------------------------------------------------------------------
# Shorts
# --------------------------------------------------------------------------

SHORT_HEM = {"mini": 232, "mid": 282, "knee": 332}
SHORT_STYLES = ("denim", "chino", "cargo", "tailored", "bermuda", "sweat")


def shorts(paint: str, fill: Fill, label: str | None, length: str = "mid", style: str = "chino",
           pocket: str = "yes") -> list[str]:  # fmt: skip
    """Shorts at one of three lengths in one of :data:`SHORT_STYLES`: denim (rivets, a curved
    pocket), chino and tailored (belt loops, a fly; tailored adds pleats), cargo (belt loops and
    thigh patch pockets), bermuda (a turned-up knee hem) and sweat (an elastic drawstring waist)."""
    hem = SHORT_HEM[length]
    sweat = style == "sweat"
    bt, bb, wx = (66, 98, 134) if sweat else (74, 98, 134)
    spread = (hem - 232) * 0.08
    oL: list[Pt] = [(wx, bb), (124, 152), (111 - spread, hem)]
    iL: list[Pt] = [(198, 192), (186 - spread * 0.4, hem)]
    out = [_group(f"hem-{length}", [_path(_legs(oL, iL), paint)])]
    turn = style in ("bermuda", "denim")
    for o, i in ((oL, iL), (mirror(oL), mirror(iL))):
        if turn:
            y0 = hem - 22
            d = f"M{_x_at(o, y0):.1f},{y0} L{_x_at(i, y0):.1f},{y0} L{i[-1][0]:.1f},{hem} L{o[-1][0]:.1f},{hem} Z"
            out += [_path(d, paint, LW_DETAIL + 0.4), _dark(d, 0.16)]
        else:
            out.append(_hem_line(o, i, hem - 8))
    out.append(_band(paint, bt, bb, wx, "waistband", ribs=sweat))
    if sweat:
        out += _cords(bb, (bt + bb) / 2)
    else:
        fly = bb + 62
        out += [_line(f"M200,{bb} L200,{fly}"), _line(f"M209,{bb} L209,{fly - 12} Q209,{fly} 200,{fly + 6}", 1.2),
                _circle(200, (bt + bb) / 2, 4.5, GOLD)]  # fmt: skip
        if style in ("chino", "cargo", "tailored", "bermuda"):
            for x in (wx + 8, 168, SIZE - 168, SIZE - wx - 8):
                out.append(_group("belt-loop", [f'<rect x="{x - 3}" y="{bt - 4}" width="6" height="{bb - bt + 9}" fill="none" stroke="{INK}" stroke-width="1.3"/>']))
        if style == "tailored":
            for x in (168, SIZE - 168):
                out.append(_line(f"M{x},{bb} L{x - 1},{bb + 34}", 1.4))
            for o, i in ((oL, iL), (mirror(oL), mirror(iL))):
                out.append(_line(f"M{(o[0][0] + i[0][0]) / 2 + (6 if o is oL else -6):.1f},{bb + 30} L{(o[-1][0] + i[-1][0]) / 2:.1f},{hem - 4}", 1.2, ' stroke-opacity=".5"'))
    if style == "cargo":
        top = max(150, 160 + (hem - 232) * 0.45)
        out += [_cargo_pocket(1, _x_at(oL, top), top, 30, 44), _cargo_pocket(-1, _x_at(oL, top), top, 30, 44)]
    if pocket == "yes" and style != "denim":
        out += [_slant_pocket(1, wx, bb, oL, 50), _slant_pocket(-1, wx, bb, oL, 50)]
    elif pocket == "yes":
        out += [_denim_pocket(1, wx, bb, oL), _denim_pocket(-1, wx, bb, oL)]
    return out


# --------------------------------------------------------------------------
# Cycling shorts
# --------------------------------------------------------------------------


def cycling_shorts(paint: str, fill: Fill, label: str | None, length: str = "mid",
                   rise: str = "high", pad: str = "no", pocket: str = "no") -> list[str]:  # fmt: skip
    """Close-fitting cycling shorts: a tube of a leg with a silicone gripper band at the hem,
    panel seams from the waist down each leg, and, when padded, the chamois pad outlined."""
    hem = SHORT_HEM[length] + 8
    bt, bb, wx = (58, 106, 140) if rise == "high" else (82, 112, 136)
    oL: list[Pt] = [(wx, bb), (132, 160), (134, 220), (136, hem)]
    iL: list[Pt] = [(198, 204), (194, 250), (190, hem)]
    out = [_group(f"hem-{length}", [_path(_legs(oL, iL), paint)])]
    for o, i in ((oL, iL), (mirror(oL), mirror(iL))):
        x0, x1 = sorted((o[-1][0], i[-1][0]))
        d = f"M{x0 - 1.5:.1f},{hem - 18} L{x1 + 1.5:.1f},{hem - 18} L{x1:.1f},{hem} L{x0:.1f},{hem} Z"
        out += [_path(d, paint, LW_DETAIL + 0.4), _dark(d, 0.28),
                _line(f"M{x0 + 2:.1f},{hem - 9} L{x1 - 2:.1f},{hem - 9}", 1.0, ' stroke-dasharray="3 3" stroke-opacity=".7"')]  # fmt: skip
    for k in (0, 1):
        s = (lambda p: p) if k == 0 else mirror
        panel = s([(wx + 18, bb), (146, 190), (150, 258), (152, hem - 18)])
        out.append(_line(f"M{_f(panel[0])} {smooth(panel)}", 1.4))
        seam = s([(193, 206), (176, 250), (170, hem - 18)])
        out.append(_line(f"M{_f(seam[0])} {smooth(seam)}", 1.2, ' stroke-opacity=".55"'))
    out.append(_band(paint, bt, bb, wx, f"waistband-{rise}", ribs=False))
    out.append(_line(f"M{wx + 4},{(bt + bb) / 2:g} L{SIZE - wx - 4},{(bt + bb) / 2:g}", 1.0, ' stroke-opacity=".5"'))
    if pocket == "yes":
        out += [_slant_pocket(1, wx, bb, oL, 44), _slant_pocket(-1, wx, bb, oL, 44)]
    if pad == "yes":
        out.append(_group("pad", [
            f'<path d="M172,166 Q200,146 228,166 L231,218 Q200,246 169,218 Z" fill="#ffffff" fill-opacity=".18" stroke="{INK}" stroke-width="1.6" stroke-dasharray="5 3"/>',
            _line("M180,180 L220,212 M220,180 L180,212 M200,158 L200,232", 1.0, ' stroke-opacity=".4"')]))  # fmt: skip
    return out


# --------------------------------------------------------------------------
# Tracksuit
# --------------------------------------------------------------------------

TRACK_FIT = {"slim": 0, "regular": 6, "relaxed": 14}


def _jacket(paint: str, top: str) -> str:
    """The tracksuit jacket from the front: sleeves with rib cuffs, a rib hem, a zip, and a
    hood, a standing collar with a full zip, or a standing collar with a half zip."""
    parts: list[str] = []
    if top == "hooded":
        hood = "M164,44 Q158,2 200,4 Q242,2 236,44 Z"
        parts += [_path(hood, paint), _dark(hood, 0.2), _path("M178,44 Q180,18 200,18 Q220,18 222,44 Z", INK, LW_DETAIL)]
    sleeve = [(146, 44), (100, 124), (86, 178), (114, 190), (130, 142), (148, 104)]
    for pts in (sleeve, mirror(sleeve)):
        d = "M" + " L".join(_f(p) for p in pts) + " Z"
        parts += [_path(d, paint), _dark(d, 0.1)]
        cuff = [(pts[2][0], pts[2][1] - 10), (pts[3][0], pts[3][1] - 10), pts[3], pts[2]]
        parts += [_path("M" + " L".join(_f(p) for p in cuff) + " Z", paint, LW_DETAIL), _dark("M" + " L".join(_f(p) for p in cuff) + " Z", 0.2)]
    body = "M150,44 Q200,60 250,44 L254,188 L146,188 Z"
    parts += [_path(body, paint), _dark(body, 0.06)]
    hem = "M146,176 L254,176 L254,196 L146,196 Z"
    parts += [_path(hem, paint, LW_DETAIL + 0.4), _dark(hem, 0.2),
              _line(" ".join(f"M{x},179 L{x},193" for x in range(152, 252, 7)), 1.0, ' stroke-opacity=".5"')]  # fmt: skip
    if top == "hooded":
        parts += [_line("M200,52 L200,176", 1.8), _circle(200, 70, 3, GOLD),
                  _line("M186,50 Q184,80 187,98 M214,50 Q216,80 213,98", 2.0), _circle(187, 100, 3), _circle(213, 100, 3)]  # fmt: skip
    elif top == "zip":
        col = "M176,38 L224,38 L224,56 L176,56 Z"
        parts += [_path(col, paint, LW_DETAIL + 0.4), _dark(col, 0.2), _line("M200,38 L200,176", 1.8), _circle(200, 62, 3, GOLD),
                  _line("M160,130 L160,166 M240,130 L240,166", 1.6)]  # fmt: skip
    else:
        col = "M174,36 L226,36 L226,56 L174,56 Z"
        parts += [_path(col, paint, LW_DETAIL + 0.4), _dark(col, 0.2), _line("M200,36 L200,108", 1.8), _circle(200, 60, 3, GOLD),
                  _line("M200,108 L194,116 L206,116 Z", 1.2),
                  _path("M168,130 L232,130 L232,164 L168,164 Z", "none", LW_DETAIL), _line("M168,142 L232,142", 1.0, ' stroke-opacity=".5"')]  # fmt: skip
    return _group("piece", parts)


def _jogger_bottoms(paint: str, spread: float, y0: float = 206) -> str:
    """The matching bottoms, smaller: a drawstring waist and tapered, cuffed legs."""
    wx = 148 - spread * 0.4
    oL: list[Pt] = [(wx, y0 + 20), (140 - spread, y0 + 56), (144 - spread * 0.5, y0 + 100), (151, y0 + 142)]
    iL: list[Pt] = [(198, y0 + 60), (196, y0 + 110), (193, y0 + 142)]
    parts = [_path(_legs(oL, iL), paint)]
    for o, i in ((oL, iL), (mirror(oL), mirror(iL))):
        x0, x1 = sorted((o[-1][0], i[-1][0]))
        d = f"M{x0:.1f},{y0 + 140} L{x1:.1f},{y0 + 140} L{x1:.1f},{y0 + 170} L{x0:.1f},{y0 + 170} Z"
        parts += [_path(d, paint, LW_DETAIL + 0.4), _dark(d, 0.2),
                  _line(" ".join(f"M{x:.1f},{y0 + 142} L{x:.1f},{y0 + 168}" for x in range(int(x0) + 5, int(x1) - 2, 6)), 1.0, ' stroke-opacity=".5"')]  # fmt: skip
    parts += [_band(paint, y0, y0 + 20, wx, "waistband"), *_cords(y0 + 20, y0 + 10)[:1],
              _line(f"M196,{y0 + 10} Q190,{y0 + 34} 186,{y0 + 44} M204,{y0 + 10} Q210,{y0 + 34} 214,{y0 + 44}", 2.2),
              _line(f"M200,{y0 + 20} L200,{y0 + 58}", 1.2, ' stroke-opacity=".5"')]  # fmt: skip
    return _group("piece", parts)


def _tee(paint: str, x: float, y: float) -> str:
    """The third piece, a short-sleeved tee drawn small beside the set."""
    pts = [(0, 14), (22, 0), (32, 8), (46, 8), (56, 0), (78, 14), (66, 36), (56, 30), (56, 92), (22, 92), (22, 30), (12, 36)]
    d = "M" + " L".join(f"{x + a:.1f},{y + b:.1f}" for a, b in pts) + " Z"
    return _group("piece", [_path(d, paint), _dark(d, 0.08), _line(f"M{x + 32},{y + 8} Q{x + 39},{y + 18} {x + 46},{y + 8}", 1.4)])


def tracksuit(paint: str, fill: Fill, label: str | None, top: str = "zip", pieces: str = "2",
              fit: str = "regular") -> list[str]:  # fmt: skip
    """A matching set shown together: the jacket (``top``: hooded, zip or half_zip) over its
    bottoms (``fit`` sets the leg width) and, for three pieces, a tee beside them."""
    inner = [_jacket(paint, top), _jogger_bottoms(paint, TRACK_FIT[fit])]
    if int(pieces) == 3:
        return [f'<g transform="translate(-30 8) scale(.9)">{"".join(inner)}</g>', _tee(paint, 304, 128)]
    return inner


# --------------------------------------------------------------------------
# Skirts
# --------------------------------------------------------------------------

SKIRT_HEM = {"mini": 204, "midi": 300, "maxi": 376}
SKIRT_SHAPES = ("a_line", "pleated", "pencil", "wrap", "tiered", "tennis")


def _skirt_waist(paint: str, bt: float, bb: float, half: float, cls: str = "waistband") -> str:
    return _band(paint, bt, bb, 200 - half, cls, ribs=False)


def _panel(paint: str, top: float, bot: float, half_top: float, half_bot: float, frill: bool) -> str:
    """One skirt tier: a flared panel with a straight or a ruffled hem."""
    xl, xr = 200 - half_top, 200 + half_top
    hl, hr = 200 - half_bot, 200 + half_bot
    if frill:
        waves = 8
        step = (hr - hl) / waves
        hem = "".join(f" Q{hr - (k + 0.5) * step:.1f},{bot + 12:.1f} {hr - (k + 1) * step:.1f},{bot:.1f}" for k in range(waves))
    else:
        hem = f" Q200,{bot + 14:.1f} {hl:.1f},{bot:.1f}"
    return f"M{xl:.1f},{top:.1f} L{xr:.1f},{top:.1f} L{hr:.1f},{bot:.1f}{hem} Z"


def skirt(paint: str, fill: Fill, label: str | None, shape: str = "a_line", length: str = "midi") -> list[str]:
    """A skirt in one of :data:`SKIRT_SHAPES` at mini, midi or maxi length: an A-line flare,
    knife pleats, a straight pencil with a slit, a wrap with an overlap and a tie, three
    ruffled tiers, or a short pleated tennis skirt."""
    hem = SKIRT_HEM["mini" if shape == "tennis" else length]
    bt, bb = 64, 90
    out: list[str] = []
    span = hem - bb
    if shape == "pencil":
        d = f"M152,{bb} L248,{bb} Q252,150 250,{bb + span * 0.45:.1f} L244,{hem} Q200,{hem + 8} 156,{hem} L150,{bb + span * 0.45:.1f} Q148,150 152,{bb} Z"
        out += [_group(f"hem-{length}", [_path(d, paint)]), _dark(d, 0.05)]
        out += [_line(f"M200,{hem - 44} L200,{hem + 4}", 1.4), _line(f"M186,{bb} L188,{bb + 40} M214,{bb} L212,{bb + 40}", 1.2, ' stroke-opacity=".6"')]
        out.append(_skirt_waist(paint, bt, bb, 52))
    elif shape == "tiered":
        n = 3
        gaps = [bb, bb + span * 0.30, bb + span * 0.62, hem]
        halves = [(52, 66), (62, 88), (82, 116)]
        for k in range(n):
            top, bot = gaps[k], gaps[k + 1] + (0 if k == n - 1 else 6)
            d = _panel(paint, top, bot, halves[k][0], halves[k][1], True)
            gathers = " ".join(f"M{200 + dx:.1f},{top + 3:.1f} L{200 + dx * 1.08:.1f},{bot - 8:.1f}" for dx in range(-int(halves[k][0]) + 8, int(halves[k][0]), 14))
            out.append(_group("tier", [_path(d, paint), _dark(d, 0.04 + 0.04 * k), _line(gathers, 1.0, ' stroke-opacity=".4"')]))
        out.append(_skirt_waist(paint, bt, bb, 52))
    else:
        half_hem = {"a_line": 54 + span * 0.30, "pleated": 54 + span * 0.36, "wrap": 54 + span * 0.30, "tennis": 54 + span * 0.55}[shape]
        d = _panel(paint, bb, hem, 52, half_hem, False)
        out.append(_group(f"hem-{length}", [_path(d, paint)]))
        if shape in ("pleated", "tennis"):
            n = 15
            for k in range(1, n):
                t = k / n
                x0, x1 = 148 + 104 * t, 200 - half_hem + 2 * half_hem * t
                out.append(_line(f"M{x0:.1f},{bb + 2} L{x1:.1f},{hem - 3}", 1.0, ' stroke-opacity=".55"'))
                if k % 2:
                    nt = (k + 1) / n
                    shade = f"M{x0:.1f},{bb} L{148 + 104 * nt:.1f},{bb} L{200 - half_hem + 2 * half_hem * nt:.1f},{hem - 2} L{x1:.1f},{hem - 2} Z"
                    out.append(_dark(shade, 0.07))
            if shape == "tennis":
                out.append(_line(f"M{200 - half_hem + 6:.1f},{hem - 14} Q200,{hem} {200 + half_hem - 6:.1f},{hem - 14}", 1.6))
        if shape == "wrap":
            # The overlap's lower edge follows the hem curve (the sub-curve of the hem's own quadratic).
            t = (1 - 0.55) / 2
            tip = f"{200 + half_hem * 0.55:.1f},{hem + 28 * t * (1 - t):.1f}"
            flap = f"M{200 - 52:.1f},{bb} L{200 + 8:.1f},{bb} L{tip} Q{200 - t * half_hem:.1f},{hem + 14 * (1 - t):.1f} {200 - half_hem:.1f},{hem} Z"
            out += [_path(flap, paint, LW), _dark(flap, 0.1), _circle(236, 98, 4, GOLD)]
            out += [_line(f"M{204},{bb + 6} Q198,{bb + 40} 206,{bb + 70}", 1.2, ' stroke-opacity=".5"')]
        if shape == "a_line":
            out.append(_line(f"M200,{bb} L200,{bb + 40}", 1.2, ' stroke-opacity=".5"'))
        out.append(_skirt_waist(paint, bt, bb, 52))
    if shape == "wrap":
        out += [_circle(246, 78, 6, "#ffffff", 1.4), _line("M246,84 Q256,104 250,122 M246,84 Q238,106 240,124", 2.4)]
    if shape == "tennis":
        out.append(_line(f"M{150},{bt + 9} L{250},{bt + 9}", 1.2, ' stroke-opacity=".6"'))
    return out


SHAPES = {"leggings": leggings, "joggers": joggers, "shorts": shorts,
          "cycling_shorts": cycling_shorts, "tracksuit": tracksuit, "skirt": skirt}  # fmt: skip
register(SHAPES)
