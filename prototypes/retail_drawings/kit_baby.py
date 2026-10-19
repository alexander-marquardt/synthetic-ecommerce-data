"""Babywear and nursery shapes for the retail drawing kit (gen#213).

Each type of :mod:`babywear_rows` has its own flat drawing in the kit's house style: the kit's
ink outline and the record's fill (color and pattern) on the product, so a shopper tells a
sleepsuit from a bodysuit, a snowsuit from a puddlesuit and a blanket from a changing mat at
thumbnail size. The variant axis that changes how the product looks is a shape param.

==================  ===================================================  ===========================
shape               draws                                                params
==================  ===================================================  ===========================
sleepsuit           a baby grow: footed or footless, long or short       feet, sleeve, fastening
                    sleeves, a row of poppers or a zip
baby_bodysuit       a vest with a popper crotch, short or long sleeves,  sleeve, neck
                    an envelope (overlapping) or a crew neck
snowsuit            a padded pramsuit: quilted, hood, fold-over mitts    hood, mitts, feet
                    and feet
puddlesuit          a waterproof all-in-one with taped seams and         hood, lining
                    elastic cuffs, optionally fleece-lined and hooded
all_in_one          a loose hooded onesie with a pocket and a zip, in    hood, fabric
                    fleece, teddy or jersey
baby_blanket        a cellular weave, a fleece, a knit or a swaddle      type, size
                    wrap, pram or cot sized
changing_mat        a wipe-clean mat with raised edges, or a quilted     wipe_clean, compartments
                    one, with side pockets
nappy_caddy         an open carry tote with dividers and a handle        compartments
nursery_storage     a fabric basket, a cube bin or a hanging organizer   kind
==================  ===================================================  ===========================

A drawing never prints a size or a pack count: a style's sizes and packs share one image per
colorway. Every param is a string with a default, so each shape also draws bare. What a row
states and the drawing can count is drawn as that many marked groups, which
``tests/test_retail_babywear_213.py`` counts per record: ``sleeve``, ``foot``, ``ankle-cuff``,
``poppers`` and ``zip`` (sleepsuits), ``sleeve``, ``envelope-neck``, ``crew-neck`` and
``popper-strip`` (bodysuits), ``hood``, ``mitt``, ``foot`` and ``quilting`` (snowsuits),
``hood``, ``taped-seam`` and ``fleece-lining`` (puddlesuits), ``hood``, ``teddy-loops``,
``fleece-pile`` and ``rib`` (all-in-ones), ``cell-weave``, ``fleece-edge``, ``knit-stitch`` and
``swaddle-wrap`` (blankets), ``sheen``, ``quilt-stitch`` and ``compartment`` (mats and caddies),
``compartment`` (caddies) and ``pocket`` (a hanging organizer).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW_DETAIL, Fill, _both, _line, _mirror, _path, _shade, _tint, register
from kit_garments import _dark


def _g(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _twin(cls: str, d: str, paint: str, width: float = 3.0) -> list[str]:
    """The path ``d`` and its mirror, each in its own marked group (one mark per side)."""
    return [_g(cls, [_path(d, paint, width)]), _g(cls, [_path(_mirror(d), paint, width)])]


def scallop(x0: float, x1: float, y: float) -> str:
    """A row of six fleece scallops from ``x0`` to ``x1`` at height ``y``."""
    return " ".join(
        f"M{x0 + i * (x1 - x0) / 6:.0f},{y} q{(x1 - x0) / 12:.0f},-9 {(x1 - x0) / 6:.0f},0"
        for i in range(6)
    )


def _hi(fill: Fill) -> str:
    """A detail stroke that shows on the fill: the ink on a light one, white on a dark one."""
    if not fill.base.startswith("#"):
        return INK
    r, g, b = (int(fill.base[i : i + 2], 16) for i in (1, 3, 5))
    return INK if (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.4 else "#ffffff"


def _dots(points: list[tuple[float, float]], r: float, fill: Fill) -> list[str]:
    stroke = _hi(fill)
    return [
        f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{_tint(fill.accent, 0.3) if fill.accent.startswith("#") else "#ffffff"}" stroke="{stroke}" stroke-width="1.3"/>'
        for x, y in points
    ]


def _shadow(cy: float = 372, rx: float = 110) -> str:
    return f'<ellipse cx="200" cy="{cy}" rx="{rx}" ry="7" fill="#000000" fill-opacity=".08"/>'


def _hood(paint: str, fill: Fill, cy: float = 66, rx: float = 64, ry: float = 54) -> list[str]:
    """A hood behind the head: a rounded cap with its face opening, one ``hood`` mark."""
    cap = f"M{200 - rx},{cy + 14} Q{200 - rx},{cy - ry} 200,{cy - ry} Q{200 + rx},{cy - ry} {200 + rx},{cy + 14} Q{200 + rx - 6},{cy + 40} 200,{cy + 44} Q{200 - rx + 6},{cy + 40} {200 - rx},{cy + 14} Z"
    face = f"M{200 - rx + 20},{cy + 14} Q{200 - rx + 22},{cy - ry + 18} 200,{cy - ry + 16} Q{200 + rx - 22},{cy - ry + 18} {200 + rx - 20},{cy + 14} Q{200 + rx - 28},{cy + 32} 200,{cy + 34} Q{200 - rx + 28},{cy + 32} {200 - rx + 20},{cy + 14} Z"
    return [
        _g(
            "hood",
            [
                _path(cap, paint),
                _dark(cap, 0.05),
                _path(
                    face,
                    _shade(fill.base, 0.35) if fill.base.startswith("#") else "#e8e4d8",
                    LW_DETAIL + 0.4,
                ),
            ],
        )
    ]


# --------------------------------------------------------------------------
# Sleepsuit
# --------------------------------------------------------------------------


def sleepsuit(
    paint: str,
    fill: Fill,
    label: str | None,
    feet: str = "footed",
    sleeve: str = "long",
    fastening: str = "poppers",
) -> list[str]:
    """A baby grow: ``footed`` (a foot on each leg) or ``footless`` (an ankle cuff), ``long`` or
    ``short`` sleeves, ``poppers`` or a ``zip`` down the front."""
    ay = 312 if feet == "footed" else 330
    half = (
        f"M200,78 L244,88 Q258,97 260,134 L263,220 Q268,268 266,{ay} L210,{ay} Q207,288 200,264 Z"
    )
    out = [_shadow(), *_both(half, paint), _dark(half, 0.04)]
    out.append(_line("M176,80 Q200,102 224,80", 2.0))
    arm = (
        "M246,90 L328,210 L304,234 L254,150 Z"
        if sleeve == "long"
        else "M246,90 L292,128 L272,152 L254,130 Z"
    )
    out += _twin("sleeve", arm, paint)
    if feet == "footed":
        foot = f"M210,{ay - 4} L266,{ay - 4} Q298,{ay + 6} 294,{ay + 26} Q290,{ay + 38} 262,{ay + 38} L216,{ay + 38} Q202,{ay + 34} 208,{ay + 10} Z"
        out += _twin("foot", foot, paint)
        out.append(
            _line(f"M222,{ay + 28} L262,{ay + 28}", 1.2, ' stroke-dasharray="4 3"', _hi(fill))
        )
        out.append(
            _line(f"M178,{ay + 28} L138,{ay + 28}", 1.2, ' stroke-dasharray="4 3"', _hi(fill))
        )
    else:
        cuff = f"M210,{ay - 16} L266,{ay - 16} L266,{ay + 2} L210,{ay + 2} Z"
        out += _twin("ankle-cuff", cuff, paint, LW_DETAIL + 0.6)
    if fastening == "zip":
        out.append(
            _g(
                "zip",
                [
                    _line("M200,92 L200,262", 1.6, ' stroke-dasharray="3 2"', _hi(fill)),
                    _path(
                        "M195,92 L205,92 L205,108 L195,108 Z",
                        _tint(fill.accent, 0.4) if fill.accent.startswith("#") else "#dddddd",
                        LW_DETAIL,
                    ),
                ],
            )
        )
    else:
        out.append(_g("poppers", _dots([(200, 110 + 26 * k) for k in range(6)], 3.8, fill)))
    return out


# --------------------------------------------------------------------------
# Baby bodysuit
# --------------------------------------------------------------------------


def baby_bodysuit(
    paint: str, fill: Fill, label: str | None, sleeve: str = "short", neck: str = "envelope"
) -> list[str]:
    """A baby vest: ``short`` or ``long`` sleeves, an ``envelope`` (overlapping shoulders) or a
    ``crew`` neck, leg openings and a popper strip at the crotch."""
    half = "M200,100 L226,82 L248,92 L256,130 L262,226 Q262,268 238,280 L214,276 Q204,270 200,270 Z"
    out = [_shadow(330, 100), *_both(half, paint), _dark(half, 0.04)]
    arm = (
        "M236,84 L298,114 L286,152 L252,128 Z"
        if sleeve == "short"
        else "M236,84 L318,196 L292,218 L252,136 Z"
    )
    out += _twin("sleeve", arm, paint)
    if neck == "envelope":
        flap_r = "M200,98 L232,80 L240,108 L200,124 Z"
        flap_l = "M168,80 L200,98 L200,124 L160,108 Z"
        out.append(
            _g(
                "envelope-neck",
                [
                    _path(flap_r, paint, LW_DETAIL + 0.6),
                    _dark(flap_r, 0.08),
                    _path(flap_l, paint, LW_DETAIL + 0.6),
                ],
            )
        )
    else:
        out.append(
            _g(
                "crew-neck",
                [
                    _line("M168,86 Q200,128 232,86", 5.0),
                    _line("M172,88 Q200,122 228,88", 1.2, ' stroke-dasharray="3 3"', _hi(fill)),
                ],
            )
        )
    out.append(
        _g(
            "popper-strip",
            [
                _path("M176,266 L224,266 L224,296 L176,296 Z", paint, LW_DETAIL + 0.6),
                *_dots([(188, 281), (200, 281), (212, 281)], 3.6, fill),
            ],
        )
    )
    out.append(
        _line(
            "M258,236 Q246,262 222,272 M142,236 Q154,262 178,272",
            1.2,
            ' stroke-dasharray="4 3"',
            _hi(fill),
        )
    )
    return out


# --------------------------------------------------------------------------
# Snowsuit
# --------------------------------------------------------------------------


def snowsuit(
    paint: str,
    fill: Fill,
    label: str | None,
    hood: str = "yes",
    mitts: str = "yes",
    feet: str = "yes",
) -> list[str]:
    """A padded pramsuit: quilted body, a ``hood``, fold-over ``mitts`` and fold-over ``feet``."""
    out = [_shadow(376, 120)]
    if hood == "yes":
        out += _hood(paint, fill, 70, 62, 52)
    half = "M200,98 L246,100 Q276,112 280,166 L282,250 Q290,300 284,322 L212,322 Q208,296 200,274 Z"
    out += [*_both(half, paint), _dark(half, 0.04)]
    quilt = " ".join(
        f"M{x0},{y} Q200,{y + 8} {400 - x0},{y}"
        for x0, y in ((124, 142), (118, 182), (118, 222), (122, 262), (136, 302))
    )
    out.append(_g("quilting", [_line(quilt, 1.3, ' stroke-dasharray="6 3"', _hi(fill))]))
    arm = "M250,110 L336,214 L312,244 L254,176 Z"
    out += _twin("sleeve", arm, paint)
    if mitts == "yes":
        out += [
            _g(
                "mitt",
                [_path("M318,214 Q352,206 350,236 Q344,262 318,256 Q304,238 318,214 Z", paint)],
            ),
            _g(
                "mitt",
                [
                    _path(
                        _mirror("M318,214 Q352,206 350,236 Q344,262 318,256 Q304,238 318,214 Z"),
                        paint,
                    )
                ],
            ),
        ]
    if feet == "yes":
        foot = "M212,318 L284,318 Q316,326 312,346 Q306,360 280,360 L216,360 Q202,356 208,332 Z"
        out += _twin("foot", foot, paint)
    out.append(_line("M200,104 L200,274", 1.8, ' stroke-dasharray="3 2"', _hi(fill)))
    out.append(
        _path(
            "M194,104 L206,104 L206,122 L194,122 Z",
            _tint(fill.accent, 0.4) if fill.accent.startswith("#") else "#dddddd",
            LW_DETAIL,
        )
    )
    return out


# --------------------------------------------------------------------------
# Puddlesuit
# --------------------------------------------------------------------------


def puddlesuit(
    paint: str, fill: Fill, label: str | None, hood: str = "yes", lining: str = "none"
) -> list[str]:
    """A waterproof all-in-one: a smooth cut with taped seams and elastic cuffs; ``lining`` is
    ``fleece`` (a scalloped fleece edge at the hood, wrists and ankles) or ``none``."""
    out = [_shadow(372, 116)]
    if hood == "yes":
        out += _hood(paint, fill, 70, 58, 50)
    half = "M200,96 L250,100 Q266,110 268,150 L270,236 Q274,290 270,334 L208,334 Q206,296 200,270 Z"
    out += [*_both(half, paint), _dark(half, 0.04)]
    arm = "M250,106 L322,222 L296,244 L256,172 Z"
    out += _twin("sleeve", arm, paint)
    out += _twin("elastic-cuff", "M296,224 L322,222 L330,240 L304,246 Z", paint, LW_DETAIL + 0.6)
    out += _twin("elastic-cuff", "M208,320 L270,320 L272,338 L208,338 Z", paint, LW_DETAIL + 0.6)
    seams = "M252,104 L322,222 M256,172 L262,300 M232,102 L226,236 M300,230 L322,222"
    out.append(
        _g(
            "taped-seam",
            [
                _line(seams, 1.3, ' stroke-dasharray="2 3"', _hi(fill)),
                _line(_mirror(seams), 1.3, ' stroke-dasharray="2 3"', _hi(fill)),
            ],
        )
    )
    out.append(_line("M200,100 L200,270", 1.8, ' stroke-dasharray="3 2"', _hi(fill)))
    if lining == "fleece":
        edges = [
            scallop(150, 250, 126) if hood == "yes" else scallop(160, 240, 98),
            scallop(300, 336, 246),
            scallop(64, 100, 246),
            scallop(210, 268, 318),
            scallop(132, 190, 318),
        ]
        out.append(
            _g(
                "fleece-lining",
                [
                    _line(
                        " ".join(edges),
                        3.4,
                        "",
                        _tint(fill.base, 0.55) if fill.base.startswith("#") else "#f2efe6",
                    )
                ],
            )
        )
    return out


# --------------------------------------------------------------------------
# All-in-one
# --------------------------------------------------------------------------


def all_in_one(
    paint: str, fill: Fill, label: str | None, hood: str = "yes", fabric: str = "fleece"
) -> list[str]:
    """A loose onesie with a front zip and a pocket, ribbed cuffs, a ``hood`` or none; the
    ``fabric`` shows as a pile (fleece), loops (teddy) or ribbing (jersey)."""
    out = [_shadow(376, 124)]
    if hood == "yes":
        out += _hood(paint, fill, 62, 70, 50)
    half = "M200,92 L252,98 Q272,108 274,150 L276,238 Q286,300 284,350 L208,350 Q206,306 200,282 Z"
    out += [*_both(half, paint), _dark(half, 0.04)]
    arm = "M254,106 L338,236 L310,258 L258,172 Z"
    out += _twin("sleeve", arm, paint)
    out += _twin("rib", "M310,238 L338,236 L346,254 L318,262 Z", paint, LW_DETAIL + 0.6)
    out += _twin("rib", "M208,334 L284,334 L286,352 L208,352 Z", paint, LW_DETAIL + 0.6)
    out.append(_line("M200,98 L200,282", 1.8, ' stroke-dasharray="3 2"', _hi(fill)))
    pocket = "M232,206 L268,206 L266,246 L234,246 Z"
    out.append(_path(pocket, paint, LW_DETAIL + 0.4))
    texture = _hi(fill)
    if fabric == "teddy":
        curls = " ".join(
            f"M{x},{y} q4,-7 8,0 q4,7 8,0"
            for x, y in (
                (150, 140),
                (176, 170),
                (216, 150),
                (144, 220),
                (170, 252),
                (146, 292),
                (238, 296),
                (222, 330),
                (170, 326),
            )
        )
        out.append(_g("teddy-loops", [_line(curls, 1.4, "", texture)]))
    elif fabric == "fleece":
        pile = " ".join(
            f"M{x},{y} l0,7"
            for x, y in (
                (150, 150),
                (166, 168),
                (150, 200),
                (174, 222),
                (152, 262),
                (170, 300),
                (240, 290),
                (230, 320),
                (156, 330),
            )
        )
        out.append(_g("fleece-pile", [_line(pile, 1.6, "", texture)]))
    return out


# --------------------------------------------------------------------------
# Baby blanket
# --------------------------------------------------------------------------

#: size -> (half width, half height) of the blanket on the sheet.
BLANKET_SIZES = {"pram": (86, 112), "cot": (124, 148)}


def baby_blanket(
    paint: str, fill: Fill, label: str | None, type: str = "cellular", size: str = "pram"
) -> list[str]:
    """A blanket in its weave: ``cellular`` (a grid of open cells), ``fleece`` (soft, with a
    scalloped edge), ``knit`` (rows of stitches) or ``swaddle`` (a wrap folded over a bundle);
    ``size`` is ``pram`` or ``cot``, the cot blanket larger on the sheet."""
    hw, hh = BLANKET_SIZES.get(size, BLANKET_SIZES["pram"])
    x0, x1, y0, y1 = 200 - hw, 200 + hw, 200 - hh, 200 + hh
    out = [_shadow(y1 + 14, hw + 14)]
    if type == "swaddle":
        wrap = f"M200,{y0} L{x1},{200 - hh // 3} L{x1 - 14},{y1} L{x0 + 14},{y1} L{x0},{200 - hh // 3} Z"
        out += [_path(wrap, paint), _dark(wrap, 0.04)]
        fold = f"M{x0},{200 - hh // 3} L{x1 - 30},{y1 - 20} L{x1 - 14},{y1} L{x0 + 14},{y1} Z"
        out.append(
            _g(
                "swaddle-wrap",
                [
                    _path(fold, paint, LW_DETAIL + 0.8),
                    _dark(fold, 0.1),
                    _line(
                        f"M{x0 + 10},{200 - hh // 3 + 14} L{x1 - 40},{y1 - 14}",
                        1.2,
                        ' stroke-dasharray="4 3"',
                        _hi(fill),
                    ),
                ],
            )
        )
        return out
    body = f"M{x0 + 8},{y0} L{x1 - 8},{y0} Q{x1},{y0} {x1},{y0 + 8} L{x1},{y1 - 8} Q{x1},{y1} {x1 - 8},{y1} L{x0 + 8},{y1} Q{x0},{y1} {x0},{y1 - 8} L{x0},{y0 + 8} Q{x0},{y0} {x0 + 8},{y0} Z"
    out += [_path(body, paint), _dark(body, 0.04)]
    tone = _hi(fill)
    if type == "cellular":
        cells = []
        for yy in range(y0 + 22, y1 - 12, 22):
            for xx in range(x0 + 22, x1 - 12, 22):
                cells.append(f"M{xx - 7},{yy} L{xx},{yy - 7} L{xx + 7},{yy} L{xx},{yy + 7} Z")
        out.append(_g("cell-weave", [_line(" ".join(cells), 1.2, "", tone)]))
    elif type == "fleece":
        n = (x1 - x0) // 14
        edge = " ".join(
            f"M{x0 + i * (x1 - x0) / n:.0f},{y1 - 8} q{(x1 - x0) / n / 2:.0f},10 {(x1 - x0) / n:.0f},0"
            for i in range(n)
        )
        out.append(
            _g(
                "fleece-edge",
                [
                    _line(edge, 2.2, "", tone),
                    _line(
                        f"M{x0 + 10},{y0 + 18} L{x1 - 10},{y0 + 18}",
                        1.2,
                        ' stroke-dasharray="5 4"',
                        tone,
                    ),
                ],
            )
        )
    elif type == "knit":
        rows = " ".join(
            f"M{x0 + 12},{yy} q6,-8 12,0 q6,8 12,0"
            + " q6,-8 12,0 q6,8 12,0" * ((x1 - x0 - 24) // 24 - 1)
            for yy in range(y0 + 22, y1 - 10, 18)
        )
        out.append(_g("knit-stitch", [_line(rows, 1.3, "", tone)]))
    return out


# --------------------------------------------------------------------------
# Changing mat
# --------------------------------------------------------------------------


def changing_mat(
    paint: str, fill: Fill, label: str | None, wipe_clean: str = "yes", compartments: str = "0"
) -> list[str]:
    """A changing mat: a flat pad inside raised edges with a head cushion; ``wipe_clean`` is a
    glossy surface (sheen streaks) or a quilted fabric one (stitched diamonds); ``compartments``
    pockets sit on the front edge."""
    n = int(compartments)
    out = [_shadow(330, 150)]
    outer = "M60,130 Q60,112 80,112 L320,112 Q340,112 340,130 L340,288 Q340,308 320,308 L80,308 Q60,308 60,288 Z"
    inner = "M86,152 L314,152 L314,268 L86,268 Z"
    out += [
        _path(outer, paint),
        _dark(outer, 0.05),
        _path(inner, paint, LW_DETAIL + 0.6),
        _dark(inner, 0.08),
    ]
    out.append(
        _path("M110,112 Q200,96 290,112 L290,134 Q200,120 110,134 Z", paint, LW_DETAIL + 0.6)
    )
    if wipe_clean == "yes":
        out.append(
            _g(
                "sheen",
                [
                    _highlight_stroke("M104,176 L168,176 M104,192 L140,192"),
                    _highlight_stroke("M256,236 L296,236"),
                ],
            )
        )
    else:
        lines = []
        for x0 in range(86 - 76, 314, 38):
            for a, b in (((x0, 152), (x0 + 76, 268)), ((x0 + 76, 152), (x0, 268))):
                seg = _clip_x(a, b, 86, 314)
                if seg:
                    lines.append("M{:g},{:g} L{:g},{:g}".format(*seg))
        diamonds = " ".join(lines)
        out.append(_g("quilt-stitch", [_line(diamonds, 1.1, ' stroke-dasharray="4 3"', _hi(fill))]))
    for i in range(n):
        x = 98 + i * (216 // max(n, 1))
        w = 216 // max(n, 1) - 12
        out.append(
            _g(
                "compartment",
                [
                    _path(
                        f"M{x},{274} L{x + w},{274} L{x + w},{300} L{x},{300} Z",
                        paint,
                        LW_DETAIL + 0.6,
                    ),
                    _line(
                        f"M{x + 4},{280} L{x + w - 4},{280}",
                        1.0,
                        ' stroke-dasharray="3 3"',
                        _hi(fill),
                    ),
                ],
            )
        )
    return out


def _clip_x(a: tuple[float, float], b: tuple[float, float], lo: float, hi: float):
    """The part of the segment ``a`` to ``b`` with x between ``lo`` and ``hi`` (None if none)."""
    (x1, y1), (x2, y2) = a, b
    if x1 == x2:
        return (x1, y1, x2, y2) if lo <= x1 <= hi else None
    t0, t1 = sorted(((lo - x1) / (x2 - x1), (hi - x1) / (x2 - x1)))
    t0, t1 = max(t0, 0.0), min(t1, 1.0)
    if t0 >= t1:
        return None
    return (x1 + t0 * (x2 - x1), y1 + t0 * (y2 - y1), x1 + t1 * (x2 - x1), y1 + t1 * (y2 - y1))


def _highlight_stroke(d: str) -> str:
    return _line(d, 3.0, ' stroke-opacity=".7"', "#ffffff")


# --------------------------------------------------------------------------
# Nappy caddy
# --------------------------------------------------------------------------


def nappy_caddy(paint: str, fill: Fill, label: str | None, compartments: str = "3") -> list[str]:
    """An open carry tote for nappies and wipes: ``compartments`` sections divided inside, with
    a handle across the top."""
    n = max(2, int(compartments))
    out = [_shadow(338, 130)]
    out.append(
        _g(
            "handle",
            [
                _line("M96,176 Q200,34 304,176", 7.0),
                _line("M96,176 Q200,34 304,176", 3.0, "", paint),
            ],
        )
    )
    tub = "M62,170 L338,170 L318,320 Q316,334 300,334 L100,334 Q84,334 82,320 Z"
    out += [_path(tub, paint), _dark(tub, 0.05)]
    rim = "M62,170 Q200,194 338,170 L338,186 Q200,210 62,186 Z"
    out.append(_path(rim, paint, LW_DETAIL + 0.6))
    width = 236 / n
    for i in range(n):
        x = 90 + i * width
        pocket = f"M{x:.0f},206 L{x + width - 6:.0f},206 L{x + width - 6:.0f},322 L{x:.0f},322 Z"
        out.append(
            _g(
                "compartment",
                [
                    _path(pocket, paint, LW_DETAIL + 0.6),
                    _dark(pocket, 0.07),
                    _line(
                        f"M{x + 6:.0f},228 L{x + width - 12:.0f},228",
                        1.0,
                        ' stroke-dasharray="4 3"',
                        _hi(fill),
                    ),
                ],
            )
        )
    return out


# --------------------------------------------------------------------------
# Nursery storage
# --------------------------------------------------------------------------


def nursery_storage(paint: str, fill: Fill, label: str | None, kind: str = "basket") -> list[str]:
    """Nursery storage: a ``basket`` (a round fabric tub with handle cut-outs), a ``cube`` (a
    square bin with a fabric drawer) or a ``hanging`` organizer (tiers of pockets on a rail)."""
    if kind == "hanging":
        out = [_line("M110,42 L290,42", 6.0), _line("M130,42 L130,56 M270,42 L270,56", 3.0)]
        panel = "M120,56 L280,56 L280,352 L120,352 Z"
        out += [_path(panel, paint), _dark(panel, 0.04)]
        for k in range(4):
            y = 74 + k * 70
            out.append(
                _g(
                    "pocket",
                    [
                        _path(
                            f"M132,{y} L268,{y} L268,{y + 56} L132,{y + 56} Z",
                            paint,
                            LW_DETAIL + 0.6,
                        ),
                        _dark(f"M132,{y} L268,{y} L268,{y + 14} L132,{y + 14} Z", 0.08),
                        _line(
                            f"M140,{y + 40} L260,{y + 40}",
                            1.0,
                            ' stroke-dasharray="4 3"',
                            _hi(fill),
                        ),
                    ],
                )
            )
        return out
    if kind == "cube":
        out = [_shadow(356, 126)]
        frame = "M76,76 L324,76 L324,340 L76,340 Z"
        out += [_path(frame, paint), _dark(frame, 0.05)]
        out.append(_path("M104,104 L296,104 L296,312 L104,312 Z", paint, LW_DETAIL + 0.8))
        out.append(
            _g(
                "bin",
                [
                    _path("M122,176 L278,176 L278,296 L122,296 Z", paint),
                    _dark("M122,176 L278,176 L278,296 L122,296 Z", 0.08),
                    _path("M178,200 L222,200 L222,216 L178,216 Z", "#ffffff", LW_DETAIL),
                ],
            )
        )
        return out
    out = [_shadow(350, 124)]
    tub = "M84,120 L316,120 L296,332 Q294,344 280,344 L120,344 Q106,344 104,332 Z"
    out += [_path(tub, paint), _dark(tub, 0.05)]
    out.append(_path("M84,120 Q200,150 316,120 Q200,98 84,120 Z", paint, LW_DETAIL + 0.6))
    out += _twin(
        "handle",
        "M96,170 Q96,152 114,152 L134,152 Q148,152 148,170 Q148,186 134,186 L114,186 Q96,186 96,170 Z",
        paint,
        LW_DETAIL + 0.8,
    )
    out.append(_line("M118,300 L282,300", 1.2, ' stroke-dasharray="5 4"', _hi(fill)))
    return out


register(
    {
        "sleepsuit": sleepsuit, "baby_bodysuit": baby_bodysuit, "snowsuit": snowsuit,
        "puddlesuit": puddlesuit, "all_in_one": all_in_one, "baby_blanket": baby_blanket,
        "changing_mat": changing_mat, "nappy_caddy": nappy_caddy,
        "nursery_storage": nursery_storage,
    },
)  # fmt: skip

SHAPES = (
    "sleepsuit", "baby_bodysuit", "snowsuit", "puddlesuit", "all_in_one", "baby_blanket",
    "changing_mat", "nappy_caddy", "nursery_storage",
)  # fmt: skip
