"""Outerwear for the retail drawing kit (gen#211): nine shapes, each its own.

``trench_coat(length, belt, breasted)``, ``raincoat(length, hood)``, ``parka(length, hood)``,
``puffer(length, hood, quilt)``, ``gilet(fill)``, ``peacoat(length, breasted)``,
``utility_jacket(pockets, collar)``, ``shacket(teddy)`` and ``bolero(style, sleeve)``.

Every param is something a shopper filters on, and every count the record states is a count the
drawing marks, so a test reads it back: the length is stamped on the torso (``hem-mid``), a belt is
one ``belt`` group, a hood one ``hood`` group (``fur`` trim, a ``hood-pack`` roll for a packaway
hood), each button a ``button`` circle, each pocket a ``pocket`` group, a quilted fill its
``channel`` or ``diamond`` stitch lines, a teddy fleece its ``pile`` edge. A shape is painted in
the record's fill and prints no size.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW_DETAIL, Fill, _both, _line, _mirror, _path, _shade, _tint, register

#: length name -> the y of the torso's hem on the 400 sheet.
HEMS = {"cropped": 214, "short": 262, "regular": 284, "mid": 316, "long": 372, "longline": 372}


def _g(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _dot(x: float, y: float, r: float, fill: str, cls: str = "button") -> str:
    return f'<circle class="{cls}" cx="{x:.1f}" cy="{y:.1f}" r="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="1"/>'


def _edge(y: float) -> tuple[float, float]:
    """The torso's left and right x at height ``y`` (a gently widening body)."""
    xl = 128 - 26 * (y - 72) / 300
    return xl, 400 - xl


def _torso(paint: str, hem: float, length: str, flare: float = 0.0, neck: float = 36.0) -> str:
    """The body, with its hem stamped as a ``hem-<length>`` group."""
    xl, xr = _edge(hem)
    xl, xr = xl - flare, xr + flare
    d = f"M{200 - neck},48 L{200 + neck},48 L272,72 L{xr:.0f},{hem} L{xl:.0f},{hem} L128,72 Z"
    return _g(f"hem-{length}", [_path(d, paint)])


def _sleeves(paint: str, end: float = 328, puff: float = 0.0) -> list[str]:
    """Both sleeves down to ``end``; ``puff`` widens them (a padded arm)."""
    ox = 92 - 28 * (end - 96) / 232 - puff
    d = f"M130,72 L{92 - puff:.0f},96 L{ox:.0f},{end} L{ox + 36 + puff:.0f},{end + 6} L124,170 Z"
    return _both(d, paint)


def _cuffs(paint: str, fill: Fill, end: float = 328, puff: float = 0.0) -> list[str]:
    ox = 92 - 28 * (end - 96) / 232 - puff
    d = f"M{ox:.0f},{end - 10} L{ox + 36 + puff:.0f},{end - 4} L{ox + 36 + puff:.0f},{end + 6} L{ox:.0f},{end} Z"
    return _both(d, _shade(fill.base, 0.14), LW_DETAIL)


def _rows(hem: float, n: int = 3, top: float = 136) -> list[float]:
    """``n`` button heights spread between the chest and above the hem."""
    return [round(top + k * (hem - 36 - top) / (n - 1)) for k in range(n)]


def _buttons(fill: Fill, xs: list[float], ys: list[float], r: float = 4.5) -> list[str]:
    return [_dot(x, y, r, _shade(fill.base, 0.45)) for y in ys for x in xs]


def _pocket(side: int, x: float, y: float, w: float, h: float, flap: bool = False, slant: bool = False) -> str:
    """One pocket (a ``pocket`` group): a welt, a patch with a flap, or a slash."""
    x0 = x if side == 1 else 400 - x - w
    if slant:
        d = f"M{x0 + (0 if side == 1 else w):.1f},{y} L{x0 + (w if side == 1 else 0):.1f},{y + h}"
        return _g("pocket", [_line(d, 2.4)])
    parts = [f'<rect x="{x0:.1f}" y="{y}" width="{w}" height="{h}" fill="none" stroke="{INK}" stroke-width="1.6"/>']
    if flap:
        parts.append(_line(f"M{x0:.1f},{y + 10} L{x0 + w:.1f},{y + 10}", 1.6))
    return _g("pocket", parts)


def _hood(paint: str, fill: Fill, fur: bool = False, small: bool = False) -> list[str]:
    """A hood behind the neck (one ``hood`` group); fur trims its opening, a packaway hood is
    smaller and shows the roll it folds into."""
    top = 22 if small else 6
    d = f"M152,60 Q150,{top} 200,{top - 4} Q250,{top} 248,60 L228,56 Q200,36 172,56 Z"
    parts = [_path(d, paint), _line(f"M172,56 Q200,{top + 32} 228,56", 1.4, ' stroke-opacity=".6"')]
    if fur:
        scallops = " ".join(f"Q{x + 6},{36 - (k % 2) * 8} {x + 12},{54 - (k % 2) * 4}" for k, x in enumerate(range(168, 232, 12)))
        parts.append(_g("fur", [_path(f"M168,56 {scallops} L228,60 L168,60 Z", _tint(fill.base, 0.7), LW_DETAIL)]))
    if small:
        parts.append(_g("hood-pack", [_line("M176,44 Q200,30 224,44", 2.0), _line("M186,50 Q200,40 214,50", 1.2)]))
    return [_g("hood", parts)]


def _collar(paint: str, fill: Fill, kind: str) -> str:
    if kind == "stand":
        d = "M164,48 L236,48 L238,62 Q200,74 162,62 Z"
        return _path(d, _shade(fill.base, 0.1), LW_DETAIL)
    d = "M164,48 L200,86 L236,48 L246,76 L200,108 L154,76 Z"
    return _path(d, _shade(fill.base, 0.1), LW_DETAIL)


def _lapels(fill: Fill, hem: float, wide: bool = True) -> list[str]:
    tip = 150 if wide else 124
    d = f"M164,48 L200,{tip} L168,{tip - 14} L140,80 Z"
    return _both(d, _shade(fill.base, 0.12), LW_DETAIL) + [_line(f"M200,{tip} L206,{hem}", 1.4, ' stroke-opacity=".5"')]


def _wash(d: str, t: float = 0.08) -> str:
    return f'<path d="{d}" fill="#000000" fill-opacity="{t}" stroke="none"/>'


# --------------------------------------------------------------------------
# Trench coat: belt, epaulettes, storm flap, one or two button columns
# --------------------------------------------------------------------------


def trench_coat(paint: str, fill: Fill, label: str | None, length: str = "mid", belt: str = "yes",
                breasted: str = "double") -> list[str]:  # fmt: skip
    """A raincoat cut: wide lapels, epaulettes, a storm flap across the shoulder, a belt at the
    waist when ``belt`` is yes and two (double) or one (single) columns of buttons."""
    hem = HEMS[length]
    out = [*_sleeves(paint), *_cuffs(paint, fill), _torso(paint, hem, length), *_lapels(fill, hem)]
    out.append(_g("storm-flap", [_path("M132,76 L268,76 L262,98 L138,98 Z", _shade(fill.base, 0.1), LW_DETAIL)]))
    out += [_g("epaulette", [_path(f"M{x},68 L{x + 26 * s},80 L{x + 22 * s},92 L{x - 4 * s},84 Z", _shade(fill.base, 0.2), LW_DETAIL)]) for x, s in ((132, 1), (268, -1))]
    xs = [180, 220] if breasted == "double" else [200]
    out += _buttons(fill, xs, _rows(hem))
    if belt == "yes":
        out.append(_g("belt", [_path("M110,206 L290,206 L292,226 L108,226 Z", _shade(fill.base, 0.18), LW_DETAIL),
                               f'<rect x="188" y="202" width="24" height="28" rx="3" fill="none" stroke="{INK}" stroke-width="2"/>',
                               _line("M212,216 Q232,236 226,262", 3.0)]))  # fmt: skip
    return out


# --------------------------------------------------------------------------
# Raincoat: no lapels, a zip storm placket, a hood that is fixed or packs away
# --------------------------------------------------------------------------


def raincoat(paint: str, fill: Fill, label: str | None, length: str = "mid", hood: str = "none") -> list[str]:
    """A waterproof mac: a straight body, a stand collar, a zip under a storm placket, welt
    pockets, cuff tabs; ``hood`` none draws none, fixed a full hood, packaway a small one with the
    roll it folds into."""
    hem = HEMS[length]
    out: list[str] = []
    if hood != "none":
        out += _hood(paint, fill, small=hood == "packaway")
    out += [*_sleeves(paint), *_cuffs(paint, fill), _torso(paint, hem, length, flare=6, neck=30), _collar(paint, fill, "stand")]
    out += [_line(f"M200,64 L200,{hem}", 2.0), _line(f"M210,64 L210,{hem}", 1.2, ' stroke-opacity=".5"')]
    out += [_pocket(s, 140 - 0, 214, 36, 4) for s in (1, -1)]
    out += [_g("cuff-tab", [_line(f"M{x},316 L{x + 30 * s},322", 3.0)]) for x, s in ((68, 1), (332, -1))]
    return out


# --------------------------------------------------------------------------
# Parka: long, padded, a drawcord waist, flap pockets, a hood (faux fur trimmed or plain)
# --------------------------------------------------------------------------


def parka(paint: str, fill: Fill, label: str | None, length: str = "long", hood: str = "fixed") -> list[str]:
    hem = HEMS[length]
    out = _hood(paint, fill, fur=hood == "faux_fur")
    out += [*_sleeves(paint, puff=6), *_cuffs(paint, fill, puff=6), _torso(paint, hem, length, flare=8, neck=32)]
    out += [_line(f"M200,64 L200,{hem}", 2.0), _line(f"M214,64 L214,{hem}", 1.2, ' stroke-opacity=".5"')]
    out.append(_g("drawcord", [_line("M112,200 Q200,214 288,200", 2.4), _dot(176, 208, 3, "#ffffff", "toggle"), _dot(224, 208, 3, "#ffffff", "toggle")]))
    out += [_pocket(s, 118, hem - 74, 48, 40, flap=True) for s in (1, -1)]
    return out


# --------------------------------------------------------------------------
# Puffer: a boxy body in stitched channels or diamonds, puffed sleeves, a hood or not
# --------------------------------------------------------------------------


def puffer(paint: str, fill: Fill, label: str | None, length: str = "regular", hood: str = "no", quilt: str = "channel") -> list[str]:
    """A padded jacket: ``quilt`` channel draws horizontal baffles, diamond a crossed stitch;
    the torso widens (a boxy cut) and the sleeves are puffed."""
    hem = HEMS[length]
    out: list[str] = []
    if hood == "yes":
        out += _hood(paint, fill)
    out += [*_sleeves(paint, puff=8), *_cuffs(paint, fill, puff=8), _torso(paint, hem, length, flare=10, neck=28)]
    xl, xr = _edge(hem)
    if quilt == "channel":
        for y in range(96, int(hem) - 8, 24):
            out.append(_line(f"M{_edge(y)[0] - 8:.0f},{y} L{_edge(y)[1] + 8:.0f},{y}", 1.6).replace("<path", '<path class="channel"'))
    else:
        for k, y in enumerate(range(96, int(hem) - 8, 30)):
            for x in range(int(xl) - 6 + (k % 2) * 25, int(xr) + 6, 50):
                out.append(_line(f"M{x},{y} L{x + 25},{y + 30} M{x + 25},{y} L{x},{y + 30}", 1.4).replace("<path", '<path class="diamond"'))
    out += [_line(f"M200,60 L200,{hem}", 2.2), _line("M164,48 Q200,70 236,48", 2.0)]
    return out


# --------------------------------------------------------------------------
# Gilet: sleeveless; padded (channels), quilted (diamonds) or fleece (a pile edge)
# --------------------------------------------------------------------------


def gilet(paint: str, fill: Fill, label: str | None, padding: str = "padded") -> list[str]:
    d = "M166,48 L234,48 L260,70 L268,120 L272,288 L128,288 L132,120 L140,70 Z"
    out = [_g("hem-short", [_path(d, paint)]), _line("M140,70 Q150,104 132,134", 3.0), _line("M260,70 Q250,104 268,134", 3.0)]
    out += [_line("M200,52 L200,288", 2.2), _line("M168,48 Q200,64 232,48", 2.0)]
    if padding == "padded":
        out += [_line(f"M132,{y} L268,{y}", 1.6).replace("<path", '<path class="channel"') for y in range(112, 280, 28)]
    elif padding == "quilted":
        for k, y in enumerate(range(96, 276, 30)):
            for x in range(106 + (k % 2) * 25, 290, 50):
                out.append(_line(f"M{x},{y} L{x + 25},{y + 30} M{x + 25},{y} L{x},{y + 30}", 1.4).replace("<path", '<path class="diamond"'))
    else:
        edge = " ".join(f"Q{x + 4},{44 - (k % 2) * 6} {x + 8},50" for k, x in enumerate(range(164, 236, 8)))
        out.append(_g("pile", [_path(f"M164,50 {edge} L236,56 L164,56 Z", _tint(fill.base, 0.6), LW_DETAIL)]))
        out.append(_pocket(1, 138, 190, 40, 36))
    return out


# --------------------------------------------------------------------------
# Peacoat: short wool coat, broad lapels, a double or single row of big buttons, slash pockets
# --------------------------------------------------------------------------


def peacoat(paint: str, fill: Fill, label: str | None, length: str = "short", breasted: str = "double") -> list[str]:
    hem = HEMS[length]
    out = [*_sleeves(paint), *_cuffs(paint, fill), _torso(paint, hem, length, flare=4), *_lapels(fill, hem, wide=False)]
    xs = [178, 222] if breasted == "double" else [204]
    out += _buttons(fill, xs, _rows(hem, top=150), 6)
    out += [_pocket(s, 134, hem - 72, 30, 40, slant=True) for s in (1, -1)]
    out.append(_g("welt", [_line("M238,128 L262,126", 2.0)]))
    return out


# --------------------------------------------------------------------------
# Utility jacket: boxy cotton jacket, patch pockets (2 or 4), a point or stand collar
# --------------------------------------------------------------------------


def utility_jacket(paint: str, fill: Fill, label: str | None, pockets: str = "4", collar: str = "point") -> list[str]:
    hem = HEMS["regular"]
    out = [*_sleeves(paint, puff=4), *_cuffs(paint, fill, puff=4), _torso(paint, hem, "regular", flare=6, neck=34), _collar(paint, fill, collar)]
    out += [_line(f"M200,{86 if collar == 'point' else 64} L200,{hem}", 1.8)]
    out += _buttons(fill, [208], _rows(hem, 4, 120), 3.6)
    out += [_pocket(s, 138, 110, 40, 40, flap=True) for s in (1, -1)]
    if pockets == "4":
        out += [_pocket(s, 134, 214, 44, 46, flap=True) for s in (1, -1)]
    return out


# --------------------------------------------------------------------------
# Shacket: an oversized shirt jacket; a teddy one has a pile edge
# --------------------------------------------------------------------------


def shacket(paint: str, fill: Fill, label: str | None, teddy: str = "no") -> list[str]:
    hem = HEMS["regular"]
    out = [*_sleeves(paint, end=336, puff=10), *_cuffs(paint, fill, end=336, puff=10), _torso(paint, hem, "regular", flare=14, neck=34), _collar(paint, fill, "point")]
    out += [_line(f"M200,86 L200,{hem}", 1.6), _line("M132,92 Q200,112 268,92", 1.2, ' stroke-opacity=".5"')]
    out += _buttons(fill, [208], _rows(hem, 5, 118), 3.8)
    out += [_pocket(s, 136, 140, 42, 40, flap=True) for s in (1, -1)]
    if teddy == "yes":
        hemx = " ".join(f"Q{x + 6},{hem + 12} {x + 12},{hem}" for x in range(100, 296, 12))
        out.append(_g("pile", [_path(f"M100,{hem} {hemx} L300,{hem - 6} L100,{hem - 6} Z", _tint(fill.base, 0.6), LW_DETAIL)]))
    return out


# --------------------------------------------------------------------------
# Bolero, shrug and cape: short toppers that leave the front open
# --------------------------------------------------------------------------


def bolero(paint: str, fill: Fill, label: str | None, style: str = "bolero", sleeve: str = "long") -> list[str]:
    out: list[str] = []
    if style == "cape":
        d = "M168,52 L232,52 L300,96 L330,236 Q200,262 70,236 L100,96 Z"
        out += [_g("cape", [_path(d, paint)]), _line("M200,56 L200,244", 1.6), _g("clasp", [_dot(188, 58, 4, "#d6b56a", "clasp"), _dot(212, 58, 4, "#d6b56a", "clasp"), _line("M188,58 L212,58", 1.6)])]
        return out
    end = {"long": 316, "three_quarter": 250, "short": 172}[sleeve]
    d = f"M130,72 L92,96 L{92 - 28 * (end - 96) / 232:.0f},{end} L{92 - 28 * (end - 96) / 232 + 34:.0f},{end + 5} L124,150 Z"
    out += [_g("sleeve", [_path(d, paint)]), _g("sleeve", [_path(_mirror(d), paint)])]
    if style == "shrug":
        body = "M170,52 L230,52 L270,76 Q300,120 270,168 L200,148 L130,168 Q100,120 130,76 Z"
    else:
        body = "M170,52 L230,52 L272,72 L276,196 Q238,218 214,170 L186,170 Q162,218 124,196 L128,72 Z"
    out += [_g(f"hem-{style}", [_path(body, paint)]), _line("M170,52 Q200,92 230,52", 2.0)]
    return out



SHAPES = {
    "trench_coat": trench_coat, "raincoat": raincoat, "parka": parka, "puffer": puffer,
    "gilet": gilet, "peacoat": peacoat, "utility_jacket": utility_jacket, "shacket": shacket,
    "bolero": bolero,
}  # fmt: skip
register(SHAPES)
