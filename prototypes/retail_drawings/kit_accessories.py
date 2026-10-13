"""Bag, umbrella and jewelry shapes for the retail drawing kit (gen#207).

Each type of :mod:`accessory_rows` has its own flat drawing in the kit's house style:
outlines in the kit's ink, the record's fill (color and pattern) on the product's main
surface, so a shopper tells a crossbody bag from a bucket bag and a pendant from a choker
at thumbnail size. Jewelry is painted in the metal's fill.

==========  =============================================  ===========================
shape       draws                                          params
==========  =============================================  ===========================
handbag     shoulder, crossbody, top handle, clutch or     style, flap, strap
            bucket (drawstring); flap or open top
backpack    school, laptop or roll-top rucksack; front     use, pockets
            pockets (one ``class="pocket"`` group each)
tote_bag    two parallel handles over an open top; the     gusset, pocket
            opening deepens with the gusset
purse       coin purse, card holder or long wallet; card   type, closure, slots
            slots (one ``class="slot"`` group each)
umbrella    an open canopy or a furled one, curved or      state, handle, ribs
            straight handle (one ``class="rib"`` each)
necklace    pendant, plain chain, choker or layered        kind, layers, stone
            (one ``class="chain"`` group per chain)
bracelet    bangle, cuff, chain, beaded or charm (one      kind, charms, stone
            ``class="charm"`` group per charm)
ring        plain band, signet, stone setting, statement   kind, pieces, stone
            or a stack (one ``class="band"`` per band)
==========  =============================================  ===========================

A drawing never prints a size: a style's sizes share one image per colorway. Every param is
a string with a default, so each shape also draws bare. A count the row states (pockets,
card slots, ribs, layers, charms, stacked bands) is drawn as that many marked groups, which
``tests/test_retail_accessories_207.py`` counts.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _panel, _path, _shade, _tint, register

HARDWARE = "#c9a24a"
HARDWARE_DARK = "#8a6a22"
LINING = "#4a4540"
#: A gem's fill by stone name; a stone not listed is drawn in a neutral blue.
STONES = {
    "diamond": "#eaf5ff", "cubic zirconia": "#eef6ff", "clear crystal": "#eaf5ff",
    "ruby": "#c8243a", "garnet": "#8e1f33", "sapphire": "#2f4fa8", "emerald": "#2e8b57",
    "amethyst": "#8a5bb5", "topaz": "#e6a93a", "citrine": "#e8b923", "aquamarine": "#8ad8d8",
    "turquoise": "#3fb8b0", "opal": "#d9e6e8", "moonstone": "#dfe8f2", "rose quartz": "#f2b6c4",
    "pearl": "#f6f0e6", "peridot": "#a8c83f", "onyx": "#2c2c32", "lapis lazuli": "#27408b",
}  # fmt: skip
NEUTRAL_STONE = "#7aa6d8"


def _n(value: str, default: int) -> int:
    try:
        return max(0, int(str(value).split()[0]))
    except (ValueError, IndexError):
        return default


def _group(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _circle(cx: float, cy: float, r: float, fill: str, width: float = LW_DETAIL) -> str:
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _ell(cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW_DETAIL) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _rect(
    x: float, y: float, w: float, h: float, fill: str, r: float = 4, width: float = LW_DETAIL
) -> str:
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" fill="{fill}" stroke="{INK}" stroke-width="{width}"/>'


def _band(d: str, color: str, width: float) -> list[str]:
    """A flat strap or handle: an ink edge under a ``width`` stroke in ``color``."""
    return [_line(d, width + 4, stroke=INK), _line(d, width, stroke=color)]


def _stitch(d: str) -> str:
    return _line(d, 1.2, ' stroke-dasharray="4 3" stroke-opacity=".6"')


def _gem(cx: float, cy: float, r: float, stone: str) -> list[str]:
    """A cut gem in ``stone`` color: a kite with facet lines."""
    c = STONES.get(stone.lower(), NEUTRAL_STONE) if stone else NEUTRAL_STONE
    top, mid, bot = cy - r * 0.8, cy - r * 0.2, cy + r
    d = f"M{cx - r:.1f},{mid:.1f} L{cx - r * 0.55:.1f},{top:.1f} L{cx + r * 0.55:.1f},{top:.1f} L{cx + r:.1f},{mid:.1f} L{cx:.1f},{bot:.1f} Z"
    return [
        _path(d, c, 2),
        _line(
            f"M{cx - r:.1f},{mid:.1f} L{cx + r:.1f},{mid:.1f} M{cx - r * 0.55:.1f},{top:.1f} L{cx - r * 0.3:.1f},{mid:.1f} L{cx:.1f},{bot:.1f} M{cx + r * 0.55:.1f},{top:.1f} L{cx + r * 0.3:.1f},{mid:.1f}",
            1,
            ' stroke-opacity=".55"',
        ),
        _highlight(
            f"M{cx - r * 0.45:.1f},{top + 3:.1f} L{cx - r * 0.2:.1f},{mid - 2:.1f}", 2.4, 0.7
        ),
    ]


# --------------------------------------------------------------------------
# Handbag
# --------------------------------------------------------------------------


def _body(x0: float, y0: float, x1: float, y1: float, t: float, r: float) -> str:
    """A bag body: ``t`` narrower at the top, rounded at the bottom corners."""
    return (f"M{x0 + t},{y0} L{x1 - t},{y0} L{x1},{y1 - r} Q{x1},{y1} {x1 - r},{y1} "
            f"L{x0 + r},{y1} Q{x0},{y1} {x0},{y1 - r} Z")  # fmt: skip


def _handbag_strap(d: str, dark: str, strap: str) -> list[str]:
    if strap == "chain":
        return [_line(d, 9, stroke=INK), _line(d, 5.5, stroke=HARDWARE),
                _line(d, 5.5, ' stroke-dasharray="2 4"', HARDWARE_DARK)]  # fmt: skip
    return _band(d, dark, 11)


def handbag(
    paint: str,
    fill: Fill,
    label: str | None,
    style: str = "shoulder",
    flap: str = "open",
    strap: str = "leather",
) -> list[str]:
    """A handbag: ``shoulder`` (short strap), ``crossbody`` (long strap), ``top handle`` (rigid
    arch), ``clutch`` (no strap) or ``bucket`` (drawstring); ``flap`` is ``flap`` or ``open``."""
    dark = _shade(fill.base, 0.3)
    out: list[str] = []
    s = style.lower()
    if s == "clutch":
        x0, y0, x1, y1, t, r = 56, 150, 344, 300, 0, 16
        out += [_path(_body(x0, y0, x1, y1, t, r), paint)]
        if flap == "flap":
            out += [_path(f"M{x0},{y0 + 8} Q{x0},{y0} {x0 + 12},{y0} L{x1 - 12},{y0} Q{x1},{y0} {x1},{y0 + 8} L{x1},{y0 + 40} L200,{y0 + 116} L{x0},{y0 + 40} Z", paint),
                    _circle(200, y0 + 100, 9, HARDWARE, 1.6)]  # fmt: skip
        else:
            out += [_line(f"M{x0 + 14},{y0 + 22} L{x1 - 14},{y0 + 22}", 2.2, ' stroke-dasharray="7 3"'),
                    _rect(x1 - 62, y0 + 12, 30, 20, HARDWARE, 5, 1.6)]  # fmt: skip
        out += [
            _stitch(f"M{x0 + 10},{y1 - 12} L{x1 - 10},{y1 - 12}"),
            _highlight(f"M{x0 + 14},{y1 - 34} L{x0 + 14},{y0 + 60}", 4, 0.3),
        ]
    elif s == "bucket":
        out += _handbag_strap("M132,168 C112,34 288,34 268,168", dark, strap)
        out += [
            _path("M104,168 Q96,264 112,322 Q200,352 288,322 Q304,264 296,168 Z", paint),
            _path("M104,168 Q128,144 152,170 Q176,146 200,170 Q224,146 248,170 Q272,144 296,168 Q200,192 104,168 Z", _tint(fill.base, 0.25)),
            _line("M200,184 L184,262 M200,184 L218,270", 2.6, stroke=dark),
            _circle(183, 266, 8, HARDWARE, 1.6), _circle(219, 274, 8, HARDWARE, 1.6),
            _highlight("M120,214 Q116,262 124,300", 4, 0.3),
        ]  # fmt: skip
    else:
        if s == "crossbody":
            x0, y0, x1, y1, t, r = 108, 196, 292, 334, 6, 16
            out += _handbag_strap("M126,200 C60,-20 340,-20 274,200", dark, strap)
        elif s == "top handle":
            x0, y0, x1, y1, t, r = 84, 176, 316, 338, 20, 16
            out += [
                _line("M150,182 C146,84 254,84 250,182", 14, stroke=INK),
                _line("M150,182 C146,84 254,84 250,182", 9, stroke=dark),
            ]
        else:
            x0, y0, x1, y1, t, r = 88, 180, 312, 338, 10, 16
            out += _handbag_strap("M140,186 C128,60 272,60 260,186", dark, strap)
        out += [_path(_body(x0, y0, x1, y1, t, r), paint)]
        if flap == "flap":
            fh = 70
            lx, rx = x0 + t * 0.6, x1 - t * 0.6
            out += [_path(f"M{x0 + t},{y0} L{x1 - t},{y0} L{rx},{y0 + fh} Q200,{y0 + fh + 24} {lx},{y0 + fh} Z", paint),
                    _circle(200, y0 + fh + 4, 9, HARDWARE, 1.6)]  # fmt: skip
        else:
            out += [_line(f"M{x0 + t + 10},{y0 + 16} L{x1 - t - 10},{y0 + 16}", 2.2, ' stroke-dasharray="7 3"'),
                    _rect(x1 - t - 54, y0 + 6, 26, 18, HARDWARE, 5, 1.6)]  # fmt: skip
        out += [
            _stitch(f"M{x0 + 10},{y1 - 14} L{x1 - 10},{y1 - 14}"),
            _highlight(f"M{x0 + 16},{y1 - 36} L{x0 + 22},{y0 + 96}", 4, 0.3),
        ]
        if s == "top handle":
            out += [_circle(150, 182, 6, HARDWARE, 1.6), _circle(250, 182, 6, HARDWARE, 1.6)]
    if label:
        out += _panel(150, 350, 100, 30, label, 18)
    return out


# --------------------------------------------------------------------------
# Backpack
# --------------------------------------------------------------------------


def backpack(
    paint: str, fill: Fill, label: str | None, use: str = "school", pockets: str = "1"
) -> list[str]:
    """A backpack: ``school`` (domed top), ``laptop`` (squarer, padded) or ``rucksack`` (roll-top
    with buckled straps). Each of ``pockets`` front pockets is a ``class="pocket"`` group."""
    n = min(max(_n(pockets, 1), 1), 3)
    dark = _shade(fill.base, 0.3)
    u = use.lower()
    out: list[str] = [
        _path("M96,150 Q70,230 92,332 L112,332 L112,170 Z", dark, LW_DETAIL),
        _path("M304,150 Q330,230 308,332 L288,332 L288,170 Z", dark, LW_DETAIL),
        _line("M176,96 C176,56 224,56 224,96", 9, stroke=INK), _line("M176,96 C176,56 224,56 224,96", 5, stroke=dark),
    ]  # fmt: skip
    if u == "laptop":
        out += [_path("M120,82 L280,82 Q298,82 298,100 L298,338 Q298,356 280,356 L120,356 Q102,356 102,338 L102,100 Q102,82 120,82 Z", paint),
                _line("M118,112 L282,112", 2, ' stroke-dasharray="6 3"'), _rect(262, 102, 18, 14, HARDWARE, 3, 1.4),
                _highlight("M116,130 L116,300", 4, 0.3)]  # fmt: skip
    elif u == "rucksack":
        out += [_path("M114,136 L286,136 L296,338 Q296,356 278,356 L122,356 Q104,356 104,338 Z", paint),
                _rect(112, 76, 176, 66, _shade(fill.base, 0.12), 24, LW),
                _line("M148,78 Q142,108 148,140 M200,76 Q194,108 200,142 M252,78 Q246,108 252,140", 1.4, ' stroke-opacity=".5"'),
                _line("M160,138 L160,206 M240,138 L240,206", 9, stroke=INK), _line("M160,138 L160,206 M240,138 L240,206", 5, stroke=dark),
                _rect(150, 196, 20, 16, HARDWARE, 3, 1.4), _rect(230, 196, 20, 16, HARDWARE, 3, 1.4)]  # fmt: skip
    else:
        out += [_path("M112,120 Q112,82 152,82 L248,82 Q288,82 288,120 L298,336 Q298,356 278,356 L122,356 Q102,356 102,336 Z", paint),
                _line("M126,130 Q200,108 274,130", 2, ' stroke-dasharray="6 3"'), _rect(188, 100, 24, 12, HARDWARE, 3, 1.4),
                _highlight("M118,150 L114,300", 4, 0.3)]  # fmt: skip
    hs = (92, 56, 40)[n - 1]
    for i in range(n):
        y1 = 344 - i * (hs + 8)
        y0 = y1 - hs
        out.append(_group("pocket", [
            _path(f"M122,{y1} L122,{y0 + 10} Q122,{y0} 132,{y0} L268,{y0} Q278,{y0} 278,{y0 + 10} L278,{y1} Q278,{y1 + 6} 270,{y1 + 6} L130,{y1 + 6} Q122,{y1 + 6} 122,{y1} Z", _tint(fill.base, 0.12) if fill.pattern == "solid" else paint, 2),
            _line(f"M132,{y0 + 12} L268,{y0 + 12}", 1.6, ' stroke-dasharray="5 3"'), _rect(196, y0 + 6, 12, 12, HARDWARE, 3, 1.2),
        ]))  # fmt: skip
    if label:
        out += _panel(150, 366, 100, 28, label, 16)
    return out


# --------------------------------------------------------------------------
# Tote bag
# --------------------------------------------------------------------------

#: Depth of the open top by gusset, in sheet units.
GUSSET_DEPTH = {"flat": 8, "standard": 20, "wide": 34}


def tote_bag(
    paint: str, fill: Fill, label: str | None, gusset: str = "standard", pocket: str = "no"
) -> list[str]:
    """A tote: two parallel handles (one behind the open top, one in front), the opening
    deepening with the ``gusset`` (flat, standard or wide); ``pocket`` adds a patch pocket (one ``class="pocket"`` group)."""
    g = GUSSET_DEPTH.get(gusset.lower(), 20)
    dark = _shade(fill.base, 0.3)
    top = 178
    out = [
        *_band(f"M146,{top - g + 2} C140,52 260,52 254,{top - g + 2}", _shade(fill.base, 0.45), 12),
        _path(f"M94,{top} L{104 + 4},{top - g} L{296 - 4},{top - g} L306,{top} Z", LINING, LW_DETAIL),
        _path(f"M94,{top} L306,{top} L322,336 Q323,350 308,350 L92,350 Q77,350 78,336 Z", paint),
        *_band(f"M130,{top + 10} C122,70 278,70 270,{top + 10}", dark, 12),
        _line(f"M130,{top + 22} L130,{top + 6} M270,{top + 22} L270,{top + 6}", 2, stroke=INK),
        _stitch(f"M96,{top + 26} L304,{top + 26}"),
        _highlight(f"M96,{top + 60} L88,330", 4, 0.3),
    ]  # fmt: skip
    if pocket.lower() in ("yes", "true", "1"):
        out.append(_group("pocket", [
            _path("M206,252 L286,252 L288,324 Q288,330 282,330 L210,330 Q204,330 204,324 Z", _tint(fill.base, 0.12) if fill.pattern == "solid" else paint, 2),
            _stitch("M210,262 L282,262"),
        ]))  # fmt: skip
    if label:
        out += _panel(150, 360, 100, 28, label, 16)
    return out


# --------------------------------------------------------------------------
# Purse
# --------------------------------------------------------------------------

CARDS = ("#ffffff", "#e5edf6", "#f6e6d0", "#e6f1e3", "#f3e4ec", "#ece7f6")


def _slots(n: int, x0: float, x1: float, y_body: float) -> list[str]:
    """``n`` cards peeking out of the top, each a ``class="slot"`` group, one step higher each."""
    out = []
    for i in range(n):
        y = y_body - 12 * (i + 1)
        out.append(_group("slot", [_rect(x0 + 14 + 6 * (i % 2), y, x1 - x0 - 28 - 6 * (i % 2), 30, CARDS[i % len(CARDS)], 4, 1.6),
                                   _line(f"M{x0 + 26},{y + 6} L{x0 + 60},{y + 6}", 1.2, ' stroke-opacity=".4"')]))  # fmt: skip
    return out[::-1]


def purse(
    paint: str,
    fill: Fill,
    label: str | None,
    type: str = "wallet",
    closure: str = "zip",
    slots: str = "0",
) -> list[str]:  # noqa: A002
    """A small leather good: a ``coin`` purse (rounded pouch), a ``card`` holder (cards peeking
    from a slim case) or a long ``wallet``; ``closure`` is ``zip`` or ``clasp``; each of the
    ``slots`` cards is a ``class="slot"`` group (card and wallet only)."""
    n = min(_n(slots, 0), 6)
    out: list[str] = []
    t = type.lower()
    if t == "coin":
        out += [
            _path(
                "M92,214 Q92,164 200,160 Q308,164 308,214 L308,262 Q308,322 200,322 Q92,322 92,262 Z",
                paint,
            )
        ]
        if closure == "clasp":
            out += [
                _path("M98,196 Q200,170 302,196 L302,212 Q200,190 98,212 Z", HARDWARE, 2),
                _circle(122, 200, 8, HARDWARE, 1.6),
                _circle(278, 200, 8, HARDWARE, 1.6),
            ]
        else:
            out += [_line("M98,200 Q200,176 302,200", 6, ' stroke-dasharray="2 2"'), _line("M98,200 Q200,176 302,200", 2.2, stroke="#ffffff"),
                    _rect(86, 186, 26, 22, HARDWARE, 4, 1.6), _circle(100, 220, 5, HARDWARE, 1.4)]  # fmt: skip
        out += [
            _stitch("M110,300 Q200,326 290,300"),
            _highlight("M106,240 Q106,282 130,302", 4, 0.3),
        ]
    elif t == "card":
        yb = 210
        out += _slots(n, 84, 316, yb)
        out += [_path(f"M84,{yb + 8} Q84,{yb} 92,{yb} L308,{yb} Q316,{yb} 316,{yb + 8} L316,{yb + 108} Q316,{yb + 122} 302,{yb + 122} L98,{yb + 122} Q84,{yb + 122} 84,{yb + 108} Z", paint),
                _stitch(f"M96,{yb + 14} L304,{yb + 14}"), _stitch(f"M96,{yb + 108} L304,{yb + 108}"),
                _highlight(f"M96,{yb + 30} L96,{yb + 96}", 4, 0.3)]  # fmt: skip
    else:
        yb = 190
        out += _slots(n, 52, 348, yb)
        out += [
            _path(
                f"M52,{yb + 10} Q52,{yb} 62,{yb} L338,{yb} Q348,{yb} 348,{yb + 10} L348,{yb + 124} Q348,{yb + 138} 334,{yb + 138} L66,{yb + 138} Q52,{yb + 138} 52,{yb + 124} Z",
                paint,
            )
        ]
        if closure == "clasp":
            out += [_path(f"M52,{yb + 10} Q52,{yb} 62,{yb} L338,{yb} Q348,{yb} 348,{yb + 10} L348,{yb + 50} L200,{yb + 62} L52,{yb + 50} Z", paint, 2),
                    _circle(200, yb + 58, 9, HARDWARE, 1.6)]  # fmt: skip
        else:
            out += [_stitch(f"M64,{yb + 12} L336,{yb + 12} L336,{yb + 126} L64,{yb + 126} Z"),
                    _line(f"M64,{yb + 12} L336,{yb + 12}", 5, ' stroke-dasharray="2 2"'), _line(f"M64,{yb + 12} L336,{yb + 12}", 1.6, stroke="#ffffff"),
                    _rect(322, yb + 2, 22, 22, HARDWARE, 4, 1.6)]  # fmt: skip
        out += [_highlight(f"M66,{yb + 40} L66,{yb + 110}", 4, 0.3)]
    if label:
        out += _panel(150, 350, 100, 28, label, 16)
    return out


# --------------------------------------------------------------------------
# Umbrella
# --------------------------------------------------------------------------


def umbrella(
    paint: str,
    fill: Fill,
    label: str | None,
    state: str = "open",
    handle: str = "curved",
    ribs: str = "8",
) -> list[str]:
    """An umbrella: ``open`` (a dome with a scalloped hem) or ``closed`` (furled and strapped),
    on a ``curved`` or ``straight`` handle. Each of the ``ribs`` is a ``class="rib"`` line."""
    n = min(max(_n(ribs, 8), 2), 24)
    dark = _shade(fill.base, 0.35)
    out: list[str] = []
    if state == "closed":
        xs = [158 + k * (84 / (n - 1)) for k in range(n)]
        out += [
            _line("M200,248 L200,330", 7, stroke=INK),
            _line("M200,248 L200,330", 4, stroke=HARDWARE),
        ]
        out += [
            _path(
                "M200,34 C226,100 248,180 244,250 Q222,268 200,252 Q178,268 156,250 C152,180 174,100 200,34 Z",
                paint,
            )
        ]
        out += [_line(f"M200,44 Q{200 + (x - 200) * 0.9:.1f},150 {x:.1f},{250 + (4 if k in (0, n - 1) else 0) + 10 * math.sin(math.pi * k / (n - 1)):.1f}", 1.1, ' stroke-opacity=".7"', dark)
                for k, x in enumerate(xs)]  # fmt: skip
        out = out[:3] + [_group("rib", [ln]) for ln in out[3:]]
        out += [
            _rect(150, 196, 100, 18, dark, 6, 1.6),
            _circle(200, 205, 5, HARDWARE, 1.2),
            _line("M200,34 L200,16", 4),
        ]
        top = 330
    else:
        xs = [44 + k * (312 / (n - 1)) for k in range(n)]
        sil = "M44,214 C50,116 122,70 200,66 C278,70 350,116 356,214 "
        sil += (
            " ".join(
                f"Q{(xs[k] + xs[k - 1]) / 2:.1f},196 {xs[k - 1]:.1f},214"
                for k in range(n - 1, 0, -1)
            )
            + " Z"
        )
        out += [
            _line("M200,206 L200,330", 8, stroke=INK),
            _line("M200,206 L200,330", 5, stroke=HARDWARE),
        ]
        out += [_path(sil, paint)]
        for k, x in enumerate(xs):
            out.append(
                _group(
                    "rib",
                    [
                        _line(
                            f"M200,68 Q{200 + (x - 200) * 0.78:.1f},100 {x:.1f},{212 if k in (0, n - 1) else 206}",
                            1.6,
                            ' stroke-opacity=".75"',
                            dark,
                        )
                    ],
                )
            )
        out += [
            _line("M200,66 L200,40", 5),
            _circle(200, 38, 5, HARDWARE, 1.4),
            _circle(200, 214, 7, HARDWARE, 1.4),
        ]
        top = 330
    if handle == "straight":
        out += [
            _path(
                f"M188,{top - 16} L212,{top - 16} L212,{top + 44} Q212,{top + 52} 204,{top + 52} L196,{top + 52} Q188,{top + 52} 188,{top + 44} Z",
                _shade(fill.base, 0.2) if fill.pattern == "solid" else dark,
                2.4,
            )
        ]
    else:
        out += [_line(f"M200,{top - 16} L200,{top + 20} C200,{top + 58} 160,{top + 58} 160,{top + 26}", 12, stroke=INK),
                _line(f"M200,{top - 16} L200,{top + 20} C200,{top + 58} 160,{top + 58} 160,{top + 26}", 8, stroke=_shade(fill.base, 0.2) if fill.pattern == "solid" else dark)]  # fmt: skip
    if label:
        out += _panel(264, 346, 100, 28, label, 16)
    return out


# --------------------------------------------------------------------------
# Jewelry
# --------------------------------------------------------------------------


def _chain(d: str, paint: str, width: float = 5.5) -> list[str]:
    """A chain of links along ``d``: an ink edge, the metal, and link gaps."""
    return [_line(d, width + 3, stroke=INK), _line(d, width, stroke=paint),
            _line(d, 1.6, ' stroke-dasharray="1.5 4.5" stroke-opacity=".45"')]  # fmt: skip


def _loop(w: float, yb: float, top: float = 54) -> str:
    return f"M200,{top} C{200 - w},{top} {200 - w + 12},{yb - 24} 200,{yb} C{200 + w - 12},{yb - 24} {200 + w},{top} 200,{top}"


def necklace(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "pendant",
    layers: str = "2",
    stone: str = "",
) -> list[str]:
    """A necklace laid flat: a ``pendant`` on a chain (a gem when ``stone`` is named), a plain
    ``chain``, a short ``choker`` or ``layered`` chains. Each chain is a ``class="chain"`` group."""
    k = kind.lower()
    out: list[str] = []
    if k == "choker":
        d = _loop(120, 214, 96)
        out += [_group("chain", [_line(d, 17, stroke=INK), _line(d, 13, stroke=paint), _line(d, 1.6, ' stroke-dasharray="1.5 4.5" stroke-opacity=".45"')]),
                _circle(200, 96, 7, HARDWARE, 1.4)]  # fmt: skip
        out += [_circle(200, 222, 13, paint, 2.4)]
    elif k == "layered":
        n = min(max(_n(layers, 2), 2), 3)
        for i in range(n):
            out.append(_group("chain", _chain(_loop(120 + 22 * i, 236 + 36 * i), paint, 4.8)))
        out += [_circle(200, 236 + 36 * (n - 1) + 8, 7, paint, 2)]
        out += [_circle(200, 52, 7, HARDWARE, 1.4)]
    else:
        out.append(_group("chain", _chain(_loop(128, 262), paint)))
        out += [_circle(200, 52, 7, HARDWARE, 1.4), _line("M200,46 L200,32", 3, stroke=INK)]
        if k == "pendant":
            out += [_circle(200, 276, 8, paint, 2.4)]
            if stone:
                out += [_circle(200, 322, 34, paint, 3), *_gem(200, 322, 22, stone)]
            else:
                out += [
                    _path("M200,284 C250,320 238,372 200,372 C162,372 150,320 200,284 Z", paint),
                    _highlight("M184,318 Q176,344 186,358", 4, 0.4),
                ]
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


def _ellipse_arc(cx: float, cy: float, rx: float, ry: float, deg: float) -> tuple[float, float]:
    a = math.radians(deg)
    return cx + rx * math.cos(a), cy + ry * math.sin(a)


def _charm_shape(i: int, x: float, y: float, paint: str) -> list[str]:
    j = i % 3
    if j == 0:
        return [
            _path(
                f"M{x},{y + 30} C{x - 30},{y + 8} {x - 14},{y - 10} {x},{y + 4} C{x + 14},{y - 10} {x + 30},{y + 8} {x},{y + 30} Z",
                paint,
                2.2,
            )
        ]
    if j == 1:
        pts = [
            (
                x + math.sin(math.radians(a)) * (16 if a % 72 == 0 else 7),
                y + 14 - math.cos(math.radians(a)) * (16 if a % 72 == 0 else 7),
            )
            for a in range(0, 360, 36)
        ]
        return [_path("M" + " L".join(f"{px:.1f},{py:.1f}" for px, py in pts) + " Z", paint, 2.2)]
    return [_circle(x, y + 14, 13, paint, 2.2), _circle(x, y + 14, 5, "#fbfaf6", 1.4)]


def bracelet(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "bangle",
    charms: str = "3",
    stone: str = "",
) -> list[str]:
    """A bracelet laid flat: a ``bangle`` ring, an open ``cuff``, a ``chain`` with a clasp, a
    ``beaded`` loop or a ``charm`` chain; each of the ``charms`` is a ``class="charm"`` group."""
    k = kind.lower()
    cx, cy, rx, ry = 200, 190, 128, 92
    out: list[str] = []
    if k in ("bangle", "cuff"):
        irx, iry, icy = rx - 20, ry - 22, cy - 8
        if k == "bangle":
            d = (f"M{cx - rx},{cy} A{rx},{ry} 0 1 0 {cx + rx},{cy} A{rx},{ry} 0 1 0 {cx - rx},{cy} Z "
                 f"M{cx - irx},{icy} A{irx},{iry} 0 1 1 {cx + irx},{icy} A{irx},{iry} 0 1 1 {cx - irx},{icy} Z")  # fmt: skip
            out += [_path(d, paint, LW, ' fill-rule="evenodd"')]
        else:
            ox1, oy1 = _ellipse_arc(cx, cy, rx, ry, -32)
            ox2, oy2 = _ellipse_arc(cx, cy, rx, ry, 32)
            ix1, iy1 = _ellipse_arc(cx, icy, irx, iry, -32)
            ix2, iy2 = _ellipse_arc(cx, icy, irx, iry, 32)
            d = f"M{ox1:.1f},{oy1:.1f} A{rx},{ry} 0 1 0 {ox2:.1f},{oy2:.1f} L{ix2:.1f},{iy2:.1f} A{irx},{iry} 0 1 1 {ix1:.1f},{iy1:.1f} Z"
            out += [_path(d, paint)]
        out += [
            _highlight(
                f"M{cx - rx + 18},{cy + 28} Q{cx - rx + 30},{cy + ry - 12} {cx - 40},{cy + ry - 8}",
                4,
                0.5,
            )
        ]
        if stone:
            out += _gem(cx, cy + ry - 12, 17, stone)
    elif k == "beaded":
        beads = 18
        for i in range(beads):
            x, y = _ellipse_arc(cx, cy, rx - 6, ry - 6, 90 + 360 * i / beads)
            out.append(
                _circle(x, y, 17, _tint(fill.base, 0.1) if fill.pattern == "solid" else paint, 2)
            )
        out += [_ell(cx + rx - 6, cy, 8, 8, HARDWARE, 1.6)]
    else:
        d = f"M{cx - rx},{cy} A{rx},{ry} 0 1 0 {cx + rx},{cy} A{rx},{ry} 0 1 0 {cx - rx},{cy}"
        out += _chain(d, paint)
        out += [
            _rect(cx + rx - 14, cy - 12, 34, 24, HARDWARE, 10, 2),
            _circle(cx - rx, cy, 6, HARDWARE, 1.4),
        ]
        if k == "charm":
            n = min(max(_n(charms, 3), 1), 5)
            span = 24 + 14 * n
            for i in range(n):
                ang = 90 - span / 2 + (span / (n - 1) * i if n > 1 else span / 2)
                x, y = _ellipse_arc(cx, cy, rx, ry, ang)
                out.append(
                    _group(
                        "charm",
                        [
                            _line(f"M{x:.1f},{y:.1f} L{x:.1f},{y + 8:.1f}", 2.4),
                            *_charm_shape(i, round(x, 1), round(y + 6, 1), paint),
                        ],
                    )
                )
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


def _annulus(cx: float, cy: float, ro: float, ri: float, paint: str, ry_scale: float = 1.0) -> str:
    rox, roy, rix, riy = ro, ro * ry_scale, ri, ri * ry_scale
    d = (f"M{cx - rox},{cy} A{rox},{roy} 0 1 0 {cx + rox},{cy} A{rox},{roy} 0 1 0 {cx - rox},{cy} Z "
         f"M{cx - rix},{cy} A{rix},{riy} 0 1 1 {cx + rix},{cy} A{rix},{riy} 0 1 1 {cx - rix},{cy} Z")  # fmt: skip
    return _path(d, paint, LW, ' fill-rule="evenodd"')


def ring(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "band",
    pieces: str = "1",
    stone: str = "",
) -> list[str]:
    """A ring: a plain ``band``, a ``signet`` face, a ``stone`` setting on prongs, a ``statement``
    gem with a halo, or a ``stacking`` set (each of the ``pieces`` is a ``class="band"``)."""
    k = kind.lower()
    out: list[str] = []
    if k == "stacking":
        n = min(max(_n(pieces, 3), 1), 4)
        y0 = 190 - 14 * (n - 1)
        for i in range(n):
            y = y0 + 40 * i
            out.append(
                _group(
                    "band",
                    [
                        _annulus(200, y, 100, 84, paint, 0.42),
                        _highlight(f"M120,{y + 4} Q130,{y + 28} 170,{y + 34}", 3, 0.5),
                    ],
                )
            )
    else:
        out += [_annulus(200, 252, 102, 80 if k == "band" else 84, paint)]
        out += [_highlight("M120,262 Q124,318 170,336", 5, 0.5)]
        if k == "signet":
            out += [
                _ell(200, 150, 58, 44, paint, LW),
                _ell(200, 150, 42, 30, "none", 1.4),
                _highlight("M162,136 Q176,118 200,114", 4, 0.6),
            ]
        elif k == "statement":
            out += [_circle(200, 138, 56, paint, LW)]
            for i in range(8):
                x, y = _ellipse_arc(200, 138, 44, 44, i * 45)
                out.append(_circle(x, y, 7, STONES["diamond"], 1.4))
            out += _gem(200, 138, 26, stone or "sapphire")
        elif k == "stone":
            out += [
                _line("M172,196 L168,150 M228,196 L232,150", 6, stroke=INK),
                _line("M172,196 L168,150 M228,196 L232,150", 3.2, stroke=paint),
            ]
            out += _gem(200, 126, 40, stone or "diamond")
            out += [_line("M164,112 L168,150 M236,112 L232,150", 3, stroke=INK)]
    if label:
        out += _panel(264, 350, 100, 28, label, 16)
    return out


SHAPES = {
    "handbag": handbag, "backpack": backpack, "tote_bag": tote_bag, "purse": purse,
    "umbrella": umbrella, "necklace": necklace, "bracelet": bracelet, "ring": ring,
}  # fmt: skip
register(SHAPES)
