"""Own-kind shapes for products the shape audit found drawn as a generic stand-in.

The audit of the 179-product preview found rose bouquets drawn as fruit
(``round_produce``), socks, wallets and watches as a ``box``, beds as
``box_wide``. Each kind here has its own flat, parametric drawing in the
kit's house style: outlines in the kit's ink, the record's fill (color and
pattern) on the product's main surface. ``test_shape_honesty.py`` keeps it
so: a generic shape outside its allow-list of categories fails, naming the
row, and every shape below must be used by a sample and paint the record's
fill.

==============  ===============================================  =========================
shape           draws                                            params
==============  ===============================================  =========================
bouquet         paper cone, ``stems`` rose heads in the fill     stems (5-9), foliage, wrap
socks           one pair, or a fanned pack under a count band    pairs
bed_frame       a bed from its foot: headboard, duvet, base      head
watch           round case, dial, two strap halves               strap (mesh, link)
earrings        a pair on a backing card                         kind (stud, hoop), stone
compact         a powder: hinged compact or loose-powder pot     form (pressed, loose)
cardigan        :func:`kit_garments.top` as a buttoned cardigan  neckline, sleeve
bodysuit        a sleeveless top with a popper-fastened brief    neckline, sleeve
wallet          a leather gift set laid in its box               pieces
keyring         split ring, link and a stitched leather fob      ring
trophy          a two-handled cup on a stem, plinth and plate    plinth
charging_pad    a flat disc with a metal rim and a cable         surface
chairbed        an armchair, its foam mattress pulled out        --
mattress        a deep sprung mattress with a quilted top        depth
potted_tree     a small tree in a tied hessian wrap              leaves
pudding         a dome pudding with brandy butter and holly      --
panettone       a tall domed loaf in a paper case                --
==============  ===============================================  =========================

Every params value is a string, as a style row's ``params`` carry it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _mirror,
    _panel,
    _path,
    _shade,
    _tint,
    _word,
    register,
)
from kit_garments import _dark, top

GOLD = "#d6b56a"
BRASS = "#c9a227"
KRAFT = "#c9a77c"
GREEN = "#5a8f4a"
LINEN = "#f7f5ef"
CASE = "#2f2f35"


def _circle(cx: float, cy: float, r: float, fill: str, width: float = LW, extra: str = "") -> str:
    return (
        f'<circle{extra} cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}" '
        f'stroke="{INK}" stroke-width="{width}"/>'
    )


def _spread(n: int, lo: float, hi: float) -> list[float]:
    """``n`` evenly spaced values from ``lo`` to ``hi`` (the middle for one)."""
    return [(lo + hi) / 2] if n == 1 else [lo + (hi - lo) * i / (n - 1) for i in range(n)]


def _leaf(x0: float, y0: float, x1: float, y1: float, width: float, color: str) -> str:
    """A pointed leaf from its base (x0, y0) to its tip (x1, y1)."""
    mx, my = (x0 + x1) / 2, (y0 + y1) / 2
    dx, dy = (y1 - y0) * width, (x0 - x1) * width
    d = f"M{x0:.1f},{y0:.1f} Q{mx + dx:.1f},{my + dy:.1f} {x1:.1f},{y1:.1f} Q{mx - dx:.1f},{my - dy:.1f} {x0:.1f},{y0:.1f} Z"
    return (
        f'<path class="leaf" fill="{color}" d="{d}" stroke="{INK}" stroke-width="{LW_DETAIL}" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )


def _ring(cx: float, cy: float, r: float, color: str, width: float) -> list[str]:
    """A metal ring: an ink outline under the ring's own color."""
    return [
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{INK}" stroke-width="{width + 3:g}"/>',
        f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{color}" stroke-width="{width:g}"/>',
    ]


# --------------------------------------------------------------------------
# Garden and food
# --------------------------------------------------------------------------


def bouquet(
    paint: str, fill: Fill, label: str | None, stems: str = "7", foliage: str = GREEN, wrap: str = KRAFT
) -> list[str]:
    """A hand-tied bouquet in a paper cone: ``stems`` rose heads in the record's fill, leaves in ``foliage``."""
    n = int(stems)
    if not 5 <= n <= 9:
        raise ValueError(f"a bouquet has 5 to 9 stems, not {n}")
    r = 34 - 2 * (n - 5)
    back = [(x, 120.0) for x in _spread(n // 2, 134, 266)]
    front = [(x, 168.0) for x in _spread(n - n // 2, 112, 288)]
    out = [_path("M78,212 L98,118 Q200,150 302,118 L322,212 Z", _tint(wrap, 0.25))]
    out += [_line(f"M{x:.1f},{y + r:.1f} L{200 + (x - 200) * 0.12:.1f},360", 3.0, stroke=_shade(foliage, 0.25)) for x, y in (*back, *front)]
    out += [
        _leaf(108, 176, 62, 120, 0.22, foliage),
        _leaf(292, 176, 338, 120, 0.22, foliage),
        _leaf(150, 120, 120, 62, 0.22, foliage),
        _leaf(250, 120, 280, 62, 0.22, foliage),
        _leaf(200, 112, 200, 48, 0.22, foliage),
    ]
    swirl = _shade(fill.base, 0.35)
    for cx, cy in (*back, *front):
        out += [
            _circle(cx, cy, r, paint, LW, ' class="bloom"'),
            _line(
                f"M{cx - 0.45 * r:.1f},{cy + 0.05 * r:.1f} Q{cx - 0.4 * r:.1f},{cy - 0.55 * r:.1f} {cx + 0.1 * r:.1f},{cy - 0.5 * r:.1f} "
                f"Q{cx + 0.55 * r:.1f},{cy - 0.35 * r:.1f} {cx + 0.45 * r:.1f},{cy + 0.1 * r:.1f} "
                f"Q{cx + 0.3 * r:.1f},{cy + 0.55 * r:.1f} {cx - 0.1 * r:.1f},{cy + 0.45 * r:.1f} "
                f"M{cx - 0.15 * r:.1f},{cy:.1f} Q{cx:.1f},{cy - 0.25 * r:.1f} {cx + 0.15 * r:.1f},{cy:.1f}",
                1.6,
                stroke=swirl,
            ),
        ]
    out += [
        _path("M66,198 Q200,236 334,198 L214,378 L186,378 Z", wrap),
        _line("M134,226 L194,372 M270,224 L210,372", 1.0, ' stroke-opacity=".45"'),
        _path("M129.6,290 L270.4,290 L261.2,306 L138.8,306 Z", GOLD, LW_DETAIL),
        _path("M200,298 Q170,276 166,292 Q170,310 200,298 Z M200,298 Q230,276 234,292 Q230,310 200,298 Z", GOLD, LW_DETAIL),
        _line("M196,302 L184,330 M204,302 L216,330", 2.4, stroke=_shade(GOLD, 0.2)),
    ]
    if label:
        out += _panel(150, 318, 100, 34, label, 20)
    return out


def potted_tree(paint: str, fill: Fill, label: str | None, leaves: str = "#8fa27a") -> list[str]:
    """A young tree, its pot wrapped in hessian (the record's fill) and tied with twine; ``label`` on the tag."""
    out = [
        _path("M194,214 Q186,170 200,140 Q210,116 198,92 L208,90 Q222,118 210,144 Q200,172 208,214 Z", "#7a6a52", LW_DETAIL),
        _path("M200,140 Q176,120 160,124", "none", 4),
    ]
    for cx, cy, rx, ry in ((150, 112, 54, 34), (250, 104, 58, 36), (200, 74, 62, 40), (176, 140, 40, 22), (232, 140, 44, 22)):
        out.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{leaves}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
        )
    out += [
        _line(
            "M120,104 L142,96 M164,118 L184,108 M226,96 L248,88 M262,112 L284,102 M184,66 L206,58 M210,84 L232,76",
            2.2,
            stroke=_shade(leaves, 0.3),
        ),
        *[f'<ellipse cx="{x}" cy="{y}" rx="4" ry="5.5" fill="#3d3a4f"/>' for x, y in ((138, 128), (262, 120), (214, 92))],
        _path("M126,236 L108,204 L146,220 L158,196 L182,220 L200,194 L218,220 L242,196 L254,220 L292,204 L274,236 Z", paint),
        _dark("M126,236 L108,204 L146,220 L158,196 L182,220 L200,194 L218,220 L242,196 L254,220 L292,204 L274,236 Z", 0.12),
        _path("M120,236 Q110,300 126,352 Q200,370 274,352 Q290,300 280,236 Q240,248 200,244 Q160,248 120,236 Z", paint),
        _line(
            " ".join(f"M{x},{250} L{x + 4},{356}" for x in range(136, 268, 16))
            + " "
            + " ".join(f"M{124},{y} L{278},{y}" for y in range(262, 350, 16)),
            0.8,
            ' stroke-opacity=".3"',
        ),
        _line("M120,238 Q200,252 280,238", 4.5, stroke=_shade(fill.accent, 0.05)),
        _line("M200,246 Q184,262 176,274 M200,246 Q216,262 226,272", 3, stroke=_shade(fill.accent, 0.05)),
    ]
    if label:
        out += [_line("M226,272 L240,282", 1.4), *_panel(226, 280, 76, 32, label, 18)]
    return out


def pudding(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A dome pudding on a plate, brandy butter over its crown and a sprig of holly on top."""
    dome = "M86,314 Q84,172 200,162 Q316,172 314,314 Z"
    specks = ((120, 270), (150, 240), (176, 286), (214, 256), (248, 290), (276, 246), (230, 228), (140, 300), (196, 304), (288, 288))
    return [
        '<ellipse cx="200" cy="320" rx="160" ry="30" fill="#ffffff" stroke="#2b3440" stroke-width="3.0"/>',
        _path(dome, paint),
        *[f'<circle cx="{x}" cy="{y}" r="4" fill="{_shade(fill.base, 0.4)}"/>' for x, y in specks],
        *[f'<circle cx="{x + 12}" cy="{y - 10}" r="3" fill="{_tint(fill.base, 0.35)}"/>' for x, y in specks[::2]],
        _path(
            "M114,214 Q150,166 200,164 Q250,166 286,214 Q276,226 268,214 Q256,240 244,216 Q230,234 216,214 Q202,244 188,216 Q174,232 162,214 Q148,240 136,216 Q124,228 114,214 Z",
            "#fbf6ea",
            LW_DETAIL,
        ),
        _leaf(196, 160, 150, 134, 0.3, "#3f7a3a"),
        _leaf(204, 160, 250, 134, 0.3, "#3f7a3a"),
        *[_circle(x, y, 7, "#c0262f", 1.4) for x, y in ((192, 156), (206, 152), (200, 164))],
        _highlight("M116,292 Q108,240 138,206", 6, 0.3),
        *(_panel(140, 244, 120, 48, label, 26) if label else []),
    ]


def panettone(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tall panettone: a domed crown in the record's fill over a pleated paper case."""
    case = "M110,206 L290,206 L290,340 Q200,352 110,340 Z"
    return [
        _path("M100,216 Q94,108 200,94 Q306,108 300,216 Q200,232 100,216 Z", paint),
        _line("M168,118 L232,150 M232,118 L168,150", 2.4, stroke=_shade(fill.base, 0.35)),
        *[f'<circle cx="{x}" cy="{y}" r="4.5" fill="{_shade(fill.base, 0.55)}"/>' for x, y in ((130, 170), (162, 196), (250, 178), (276, 202), (206, 186))],
        _highlight("M120,184 Q124,132 168,110", 6, 0.35),
        _path(case, KRAFT),
        _line(" ".join(f"M{x},{210} L{x},{340}" for x in range(126, 290, 16)), 1.0, ' stroke-opacity=".35"'),
        _path("M110,226 L290,226 L290,242 L110,242 Z", GOLD, LW_DETAIL),
        *(_panel(140, 262, 120, 52, label, 28) if label else []),
    ]


# --------------------------------------------------------------------------
# Clothing and accessories
# --------------------------------------------------------------------------

_SOCK = "M0,0 L60,0 L60,128 Q62,146 80,152 L142,170 Q166,178 162,198 Q156,216 132,212 L30,190 Q0,182 0,150 Z"
_HEEL = "M0,150 Q0,182 30,190 L46,193 Q34,164 0,146 Z"
_TOE = "M132,212 Q156,216 162,198 Q166,178 142,170 Q126,190 132,212 Z"


def _sock(paint: str, transform: str) -> str:
    ribs = " ".join(f"M{x},4 L{x},22" for x in range(8, 60, 8))
    parts = [
        _path(_SOCK, paint),
        _path("M0,0 L60,0 L60,24 L0,24 Z", paint, LW_DETAIL),
        _dark("M0,0 L60,0 L60,24 L0,24 Z", 0.14),
        _line(ribs, 1.0, ' stroke-opacity=".5"'),
        _dark(_HEEL, 0.2),
        _dark(_TOE, 0.2),
        _line("M0,146 Q34,164 46,193 M142,170 Q126,190 132,212", 1.2, ' stroke-opacity=".6"'),
    ]
    return f'<g class="sock" transform="{transform}">{"".join(parts)}</g>'


def socks(paint: str, fill: Fill, label: str | None, pairs: str = "1") -> list[str]:
    """One pair of socks, or a pack of ``pairs`` socks fanned under a band naming the count."""
    n = int(pairs)
    if n < 1:
        raise ValueError(f"a pack holds at least one pair, not {n}")
    if n == 1:
        return [
            _sock(paint, "translate(132 40) scale(1.2)"),
            _sock(paint, "translate(86 74) scale(1.2)"),
        ]
    out = [
        _sock(paint, f"translate(150 72) scale(0.92) rotate({a:.1f} 30 280)")
        for a in _spread(n, -20, 20)
    ]
    return [*out, *_panel(112, 82, 176, 46, f"{n} pairs", 28)]


def cardigan(paint: str, fill: Fill, label: str | None, neckline: str = "v_neck", sleeve: str = "long") -> list[str]:
    """A knitted cardigan: :func:`kit_garments.top`'s buttoned placket, pockets and rib bands."""
    return top(paint, fill, label, neckline=neckline, sleeve=sleeve, kind="cardigan")


def bodysuit(paint: str, fill: Fill, label: str | None, neckline: str = "square", sleeve: str = "sleeveless") -> list[str]:
    """A bodysuit: the top's body above a brief cut high at the leg, poppers at the crotch."""
    brief = "M128,286 L272,286 Q236,300 222,348 L178,348 Q164,300 128,286 Z"
    return [
        _path(brief, paint),
        _line("M136,292 Q166,304 180,340 M264,292 Q234,304 220,340", 1.2, ' stroke-dasharray="4 3"'),
        *[_circle(x, 340, 3.2, _tint(fill.accent, 0.2), 1.2) for x in (192, 200, 208)],
        f'<g transform="translate(40 8) scale(0.8)">{"".join(top(paint, fill, label, neckline=neckline, sleeve=sleeve))}</g>',
    ]


def watch(paint: str, fill: Fill, label: str | None, strap: str = "mesh") -> list[str]:
    """A wristwatch in the record's metal: round case and crown, a dial, a ``mesh`` or ``link`` strap."""
    upper, lower = "M172,36 L228,36 L234,150 L166,150 Z", "M166,250 L234,250 L228,364 L172,364 Z"
    if strap == "mesh":
        texture = _line(
            " ".join(f"M{168 + (y - 36) * 0.05:.1f},{y} L{232 - (y - 36) * 0.05:.1f},{y}" for y in range(42, 150, 6))
            + " "
            + " ".join(f"M{168 + (y - 250) * 0.05:.1f},{y} L{232 - (y - 250) * 0.05:.1f},{y}" for y in range(256, 360, 6)),
            0.8,
            ' stroke-opacity=".45"',
        )
    elif strap == "link":
        texture = _line(
            " ".join(f"M168,{y} L232,{y}" for y in (*range(54, 150, 18), *range(268, 364, 18)))
            + " M188,36 L188,150 M212,36 L212,150 M188,250 L188,364 M212,250 L212,364",
            1.4,
        )
    else:
        raise ValueError(f"unknown strap {strap!r}; mesh or link")
    ticks = []
    for k in range(12):
        a = math.radians(k * 30)
        r0 = 42 if k % 3 else 36
        ticks.append(f"M{200 + r0 * math.sin(a):.1f},{200 - r0 * math.cos(a):.1f} L{200 + 48 * math.sin(a):.1f},{200 - 48 * math.cos(a):.1f}")
    return [
        _path(upper, paint),
        _path(lower, paint),
        texture,
        _path("M176,330 L224,330 L223,346 L177,346 Z", _shade(fill.base, 0.15), LW_DETAIL),
        _path("M266,190 L280,190 L280,210 L266,210 Z", paint, LW_DETAIL),
        _circle(200, 200, 68, paint),
        _circle(200, 200, 56, "#fbf8f2", LW_DETAIL),
        _line(" ".join(ticks), 1.8),
        _line("M200,200 L200,166 M200,200 L230,214", 3.2),
        _circle(200, 200, 4, INK, 1),
        _highlight("M148,168 Q160,144 186,136", 5, 0.5),
    ]


def earrings(paint: str, fill: Fill, label: str | None, kind: str = "stud", stone: str | None = None) -> list[str]:
    """A pair of earrings on a backing card: ``stud`` (a stone in a metal setting) or ``hoop`` (with an optional ``stone`` drop)."""
    out = [
        f'<rect x="110" y="64" width="180" height="280" rx="12" fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        '<ellipse cx="200" cy="84" rx="14" ry="5" fill="#fbfaf6" stroke="#2b3440" stroke-width="1.2"/>',
    ]
    for cx in (156, 244):
        if kind == "stud":
            gem = stone or "#eef6fb"
            out += [
                *[_circle(cx + dx, 190 + dy, 6, paint, 1.4) for dx, dy in ((-18, -18), (18, -18), (-18, 18), (18, 18))],
                _circle(cx, 190, 26, paint),
                _circle(cx, 190, 19, gem, LW_DETAIL),
                _line(f"M{cx - 19},190 L{cx + 19},190 M{cx},{171} L{cx},{209} M{cx - 13},177 L{cx + 13},203 M{cx + 13},177 L{cx - 13},203", 0.8, ' stroke-opacity=".45"'),
                _highlight(f"M{cx - 8},{180} L{cx - 2},{184}", 3, 0.9),
            ]
        elif kind == "hoop":
            out += _ring(cx, 168, 40, paint, 8)
            if stone:
                out += [
                    _line(f"M{cx},208 L{cx},222", 2),
                    _path(f"M{cx},220 Q{cx + 22},252 {cx},272 Q{cx - 22},252 {cx},220 Z", stone, LW_DETAIL),
                    _highlight(f"M{cx - 6},{244} Q{cx - 6},{236} {cx - 2},{232}", 3, 0.7),
                ]
        else:
            raise ValueError(f"unknown earring kind {kind!r}; stud or hoop")
    if label:
        out.append(_word(label, 200, 318, 150, 22))
    return out


def compact(paint: str, fill: Fill, label: str | None, form: str = "pressed") -> list[str]:
    """A face powder in the record's shade: an open hinged ``pressed`` compact, or a ``loose`` powder pot with its sifter."""
    if form == "pressed":
        return [
            _circle(200, 116, 78, CASE),
            _circle(200, 116, 64, "#dfe8ee", LW_DETAIL),
            _highlight("M164,96 L190,70 M176,112 L214,74", 4, 0.8),
            _path("M182,192 L218,192 L218,206 L182,206 Z", CASE, LW_DETAIL),
            _circle(200, 284, 84, CASE),
            _circle(200, 284, 66, paint, LW_DETAIL),
            _line("M160,262 Q200,240 240,262 M150,286 Q200,262 250,286 M160,310 Q200,288 240,310", 1.2, ' stroke-opacity=".35"'),
            _highlight("M156,252 Q170,234 196,228", 5, 0.45),
            *(_panel(150, 356, 100, 30, label, 18) if label else []),
        ]
    if form == "loose":
        holes = [(x, y) for y, xs in ((224, range(150, 260, 18)), (236, range(141, 270, 18))) for x in xs]
        return [
            f'<rect x="196" y="96" width="150" height="54" rx="12" transform="rotate(-14 270 122)" fill="{CASE}" stroke="{INK}" stroke-width="{LW}"/>',
            _path("M110,230 L290,230 L290,326 Q290,344 272,344 L128,344 Q110,344 110,326 Z", "#f4f6f8"),
            _path("M114,262 L286,262 L286,324 Q286,340 270,340 L130,340 Q114,340 114,324 Z", paint, LW_DETAIL),
            f'<ellipse cx="200" cy="230" rx="90" ry="22" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
            f'<ellipse cx="200" cy="230" rx="76" ry="16" fill="none" stroke="{INK}" stroke-width="1.2"/>',
            *[f'<circle cx="{x}" cy="{y}" r="2.2" fill="{_shade(fill.base, 0.45)}"/>' for x, y in holes],
            _highlight("M124,276 L124,326", 4, 0.5),
            '<ellipse cx="300" cy="330" rx="56" ry="20" fill="#f6e9e4" stroke="#2b3440" stroke-width="1.6"/>',
            _line("M286,316 Q300,300 314,316", 2.4),
            *(_panel(150, 282, 100, 40, label, 22) if label else []),
        ]
    raise ValueError(f"unknown compact form {form!r}; pressed or loose")


def _bifold(paint: str, x: float, y: float, w: float, h: float) -> list[str]:
    half = x + w / 2
    slots = [y + h * t for t in (0.26, 0.46, 0.66)]
    return [
        _path(f"M{x},{y} L{x + w},{y} L{x + w},{y + h} L{x},{y + h} Z", paint),
        _dark(f"M{half},{y} L{x + w},{y} L{x + w},{y + h} L{half},{y + h} Z", 0.12),
        _line(f"M{half},{y} L{half},{y + h}", 1.6),
        *[f'<rect x="{half + 8:.1f}" y="{s - 9:.1f}" width="{w / 2 - 16:.1f}" height="9" fill="{c}" stroke="{INK}" stroke-width="1"/>' for s, c in zip(slots, ("#cfd8df", "#e9d8a6", "#c9d9c4"), strict=True)],
        *[_path(f"M{half + 4},{s} Q{half + w / 4},{s + 8} {x + w - 4},{s} L{x + w - 4},{s + 14} L{half + 4},{s + 14} Z", paint, 1.2) for s in slots],
        _line(f"M{x + 6},{y + 6} L{x + w - 6},{y + 6} L{x + w - 6},{y + h - 6} L{x + 6},{y + h - 6} Z", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
    ]


def _card_holder(paint: str, x: float, y: float, w: float, h: float) -> list[str]:
    return [
        f'<rect x="{x + 12:.1f}" y="{y - 14:.1f}" width="{w - 24:.1f}" height="30" rx="3" fill="#cfd8df" stroke="{INK}" stroke-width="1"/>',
        _path(f"M{x},{y} Q{x + w / 2},{y + 20} {x + w},{y} L{x + w},{y + h} L{x},{y + h} Z", paint),
        _line(f"M{x + 4},{y + h * 0.55} Q{x + w / 2},{y + h * 0.55 + 14} {x + w - 4},{y + h * 0.55}", 1.4),
        _line(f"M{x + 6},{y + 10} L{x + 6},{y + h - 6} L{x + w - 6},{y + h - 6} L{x + w - 6},{y + 10}", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
    ]


def _coin_purse(paint: str, x: float, y: float, w: float, h: float) -> list[str]:
    return [
        _path(f"M{x},{y + 12} Q{x},{y} {x + 12},{y} L{x + w - 12},{y} Q{x + w},{y} {x + w},{y + 12} L{x + w},{y + h - 16} Q{x + w},{y + h} {x + w - 16},{y + h} L{x + 16},{y + h} Q{x},{y + h} {x},{y + h - 16} Z", paint),
        _line(f"M{x + 8},{y + 16} L{x + w - 8},{y + 16}", 1.4, ' stroke-dasharray="3 2"'),
        f'<rect x="{x + w - 22:.1f}" y="{y + 12:.1f}" width="10" height="24" rx="3" fill="{GOLD}" stroke="{INK}" stroke-width="1.2"/>',
    ]


_PIECES = {"wallet": _bifold, "card_holder": _card_holder, "coin_purse": _coin_purse}


def wallet(paint: str, fill: Fill, label: str | None, pieces: str = "wallet+card_holder") -> list[str]:
    """A leather gift set in its open box: ``pieces`` is two of wallet, card_holder, coin_purse (``+`` joined)."""
    first, second = pieces.split("+")
    return [
        f'<rect x="48" y="112" width="304" height="224" rx="10" fill="{CASE}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="62" y="126" width="276" height="196" rx="6" fill="#efe8da" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *_PIECES[first](paint, 78, 150, 152, 150),
        *_PIECES[second](paint, 244, 178, 84, 122),
        *(_panel(140, 340, 120, 34, label, 20) if label else []),
    ]


def keyring(paint: str, fill: Fill, label: str | None, ring: str = BRASS) -> list[str]:
    """A keyring: a split ring and link in ``ring`` metal, a stitched leather fob in the record's fill."""
    fob = "M156,176 L244,176 L244,300 Q244,344 200,354 Q156,344 156,300 Z"
    return [
        *_ring(200, 92, 42, ring, 7),
        _line("M232,64 Q240,72 242,82", 1.4),
        f'<rect x="190" y="130" width="20" height="42" rx="8" fill="none" stroke="{INK}" stroke-width="7"/>',
        f'<rect x="190" y="130" width="20" height="42" rx="8" fill="none" stroke="{ring}" stroke-width="4"/>',
        _path(fob, paint),
        _line("M166,186 L234,186 L234,298 Q234,334 200,342 Q166,334 166,298 Z", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
        _circle(200, 196, 8, ring, 1.6),
        _highlight("M170,214 L170,296", 4, 0.35),
        *(_panel(160, 360, 80, 28, label, 16) if label else []),
    ]


def trophy(paint: str, fill: Fill, label: str | None, plinth: str = "#3b2a20") -> list[str]:
    """A two-handled trophy cup in the record's fill on a stem, a ``plinth`` block and its engraving plate."""
    bowl = "M128,92 L272,92 Q272,196 200,214 Q128,196 128,92 Z"
    return [
        _line("M130,108 Q78,108 86,154 Q94,188 146,180", 9),
        _line("M270,108 Q322,108 314,154 Q306,188 254,180", 9),
        _path(bowl, paint),
        _path("M188,212 L212,212 L210,266 L190,266 Z", paint),
        _path("M160,266 L240,266 L250,286 L150,286 Z", paint),
        f'<rect x="134" y="286" width="132" height="70" rx="4" fill="{plinth}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="156" y="304" width="88" height="34" rx="3" fill="#d9c27a" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _highlight("M150,108 Q152,170 190,198", 6, 0.45),
        *(_panel(150, 364, 100, 28, label, 16) if label else []),
    ]


# --------------------------------------------------------------------------
# Home and electricals
# --------------------------------------------------------------------------

_HEADS = ("shaker", "panel", "spindle", "upholstered", "ottoman", "sleigh")


def _headboard(head: str, paint: str, fill: Fill) -> list[str]:
    if head == "shaker":
        slats = [_path(f"M{x - 7:.1f},96 L{x + 7:.1f},96 L{x + 7:.1f},236 L{x - 7:.1f},236 Z", paint, LW_DETAIL) for x in _spread(5, 136, 264)]
        return [
            *slats,
            _path("M92,70 L308,70 L308,96 L92,96 Z", paint),
            _path("M92,64 L112,64 L112,240 L92,240 Z M288,64 L308,64 L308,240 L288,240 Z", paint),
        ]
    if head == "panel":
        insets = [f"M{x},{92} L{x + 52},{92} L{x + 52},{196} L{x},{196} Z" for x in (112, 174, 236)]
        return [
            _path("M92,64 L308,64 L308,240 L92,240 Z", paint),
            *[_path(d, paint, LW_DETAIL) for d in insets],
            *[_dark(d, 0.14) for d in insets],
            _path("M84,56 L316,56 L316,68 L84,68 Z", paint, LW_DETAIL),
        ]
    if head == "spindle":
        bars = " ".join(f"M{x:.1f},92 L{x:.1f},236" for x in _spread(9, 122, 278))
        return [
            _line(bars, 9, stroke=INK),
            _line(bars, 5, stroke=paint),
            _path("M96,84 L304,84 L304,94 L96,94 Z M96,196 L304,196 L304,206 L96,206 Z", paint, LW_DETAIL),
            _path("M92,72 L106,72 L106,240 L92,240 Z M294,72 L308,72 L308,240 L294,240 Z", paint, LW_DETAIL),
            _circle(99, 64, 10, paint, LW_DETAIL),
            _circle(301, 64, 10, paint, LW_DETAIL),
        ]
    if head == "sleigh":
        return [_path("M100,240 L100,96 Q100,66 70,64 Q52,64 56,80 Q62,92 84,86 L84,86 Q120,76 200,76 Q280,76 316,86 Q338,92 344,80 Q348,64 330,64 Q300,66 300,96 L300,240 Z", paint)]
    # upholstered, ottoman: a padded, buttoned headboard
    buttons = [(x, y) for y in (100, 132, 164) for x in _spread(5, 124, 276)]
    return [
        _path("M92,240 L92,104 Q92,68 128,68 L272,68 Q308,68 308,104 L308,240 Z", paint),
        *[_circle(x, y, 3.4, _shade(fill.base, 0.3), 1) for x, y in buttons],
        _line("M100,108 Q100,76 130,76 L270,76 Q300,76 300,108", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'),
    ]


def bed_frame(paint: str, fill: Fill, label: str | None, head: str = "shaker") -> list[str]:
    """A bed seen from its foot: a ``head`` headboard and the base in the record's fill, pillows and duvet in white.

    ``head`` is one of shaker, panel, spindle, upholstered, ottoman (a deep
    lift-up storage base) or sleigh (scrolled head and foot boards).
    """
    if head not in _HEADS:
        raise ValueError(f"unknown head {head!r}; one of {_HEADS}")
    out = _headboard(head, paint, fill)
    out += [
        _path("M110,182 Q108,172 120,172 L190,172 Q200,172 198,184 L196,214 L112,214 Z", "#ffffff", LW_DETAIL),
        _path("M202,184 Q200,172 210,172 L280,172 Q292,172 290,182 L288,214 L204,214 Z", "#ffffff", LW_DETAIL),
        _path("M98,206 L302,206 L332,262 L68,262 Z", LINEN),
        _line("M90,222 L310,222", 1.2, ' stroke-opacity=".5"'),
        _path("M68,262 L332,262 L332,290 L68,290 Z", _shade(LINEN, 0.05), LW_DETAIL),
    ]
    if head == "ottoman":
        out += [
            _path("M60,288 L340,288 L340,340 L60,340 Z", paint),
            _line("M62,302 L338,302", 1.4),
            _path("M188,312 L212,312 L212,326 L188,326 Z", _shade(fill.base, 0.3), 1.2),
        ]
    elif head == "sleigh":
        out.append(_path("M70,262 Q54,262 54,248 Q54,234 70,234 Q86,236 86,252 L314,252 Q314,236 330,234 Q346,234 346,248 Q346,262 330,262 L330,342 L70,342 Z", paint))
    else:
        legs = "M70,320 L88,320 L86,346 L72,346 Z M312,320 L330,320 L328,346 L314,346 Z"
        out += [_path("M62,288 L338,288 L338,322 L62,322 Z", paint), _path(legs, paint, LW_DETAIL)]
        if head == "upholstered":
            out.append(_line("M66,294 L334,294", 1.0, ' stroke-dasharray="4 3" stroke-opacity=".6"'))
        if head == "spindle":
            bars = " ".join(f"M{x:.1f},262 L{x:.1f},318" for x in _spread(11, 92, 308))
            out += [
                _line(bars, 8, stroke=INK),
                _line(bars, 4, stroke=paint),
                _path("M66,256 L334,256 L334,266 L66,266 Z", paint, LW_DETAIL),
                _circle(66, 250, 9, paint, LW_DETAIL),
                _circle(334, 250, 9, paint, LW_DETAIL),
            ]
    return out


def mattress(paint: str, fill: Fill, label: str | None, depth: str = "25cm") -> list[str]:
    """A deep sprung mattress: quilted top, a border with handles and vents, its ``depth`` dimensioned."""
    top_face = "M100,120 L340,120 L304,200 L60,200 Z"
    front = "M60,200 L304,200 L304,300 L60,300 Z"
    side = "M304,200 L340,120 L340,220 L304,300 Z"
    tufts = [(x + (y - 120) * -0.45, y) for y in (140, 160, 180) for x in (124, 164, 204, 244, 284, 324) if x + (y - 120) * -0.45 < 330]
    return [
        _path(top_face, paint),
        _line("M120,128 L82,192 M168,128 L130,192 M216,128 L178,192 M264,128 L226,192 M312,128 L274,192", 1.0, ' stroke-opacity=".35"'),
        *[_circle(x, y, 2.6, _shade(fill.base, 0.25), 0.8) for x, y in tufts],
        _path(front, paint),
        _dark(front, 0.08),
        _path(side, paint),
        _dark(side, 0.22),
        _line("M64,210 L300,210 M64,290 L300,290", 1.2, ' stroke-dasharray="5 3"'),
        _path("M120,240 L170,240 L170,254 L120,254 Z M194,240 L244,240 L244,254 L194,254 Z", _shade(fill.base, 0.15), 1.2),
        *[_circle(x, 272, 4, "#ffffff", 1.2) for x in (90, 280)],
        _line("M40,200 L40,300 M34,200 L46,200 M34,300 L46,300", 1.4),
        f'<text x="40" y="324" font-family="Helvetica, Arial, sans-serif" font-size="14" text-anchor="middle" fill="{INK}">{depth}</text>',
    ]


def chairbed(paint: str, fill: Fill, label: str | None) -> list[str]:
    """An armchair (back, two arms, seat cushion) with its foam mattress half pulled out in front.

    The pulled-out section hangs from the seat's front edge, a seam across it; the full single
    bed it unfolds into is dashed on the floor.
    """
    arm = "M56,176 Q56,148 84,148 Q112,148 112,176 L112,300 L56,300 Z"
    feet = "".join(
        f'<path d="M{x},300 L{x + 14},300 L{x + 12},318 L{x + 2},318 Z" fill="#6b4a2e" stroke="{INK}" stroke-width="{LW_DETAIL}" stroke-linejoin="round"/>'
        for x in (62, 324)
    )
    pulled = "M112,296 L288,296 L308,338 L92,338 Z"
    return [
        _line("M92,338 L44,382 L356,382 L308,338", 1.4, ' stroke-dasharray="6 4" stroke-opacity=".7"'),
        feet,
        _path("M90,98 Q200,84 310,98 L310,236 L90,236 Z", paint),
        _dark("M90,98 Q200,84 310,98 L310,236 L90,236 Z", 0.08),
        _line("M200,92 L200,232", 1.4, ' stroke-opacity=".6"'),
        _path("M104,232 L296,232 L296,296 L104,296 Z", paint),
        _dark("M104,268 L296,268 L296,296 L104,296 Z", 0.14),
        _line("M104,268 L296,268", 1.6),
        _path(pulled, "#f1ede4", LW_DETAIL),
        _line("M100,317 L300,317", 1.4, ' stroke-dasharray="5 3"'),
        _path(arm, paint),
        _path(_mirror(arm), paint),
        _dark("M56,176 Q56,148 84,148 Q112,148 112,176 Z", 0.12),
        _dark(_mirror("M56,176 Q56,148 84,148 Q112,148 112,176 Z"), 0.12),
        _highlight("M70,200 L70,260", 4, 0.4),
    ]


def charging_pad(paint: str, fill: Fill, label: str | None, surface: str = "#3b3f46") -> list[str]:
    """A slim wireless charging pad: a disc on a metal rim in the record's fill, its cable curling off."""
    return [
        _line("M318,206 C368,214 364,292 302,302 C252,312 244,340 272,352", 9, stroke=INK),
        _line("M318,206 C368,214 364,292 302,302 C252,312 244,340 272,352", 5, stroke="#e9e9ea"),
        _path("M262,346 L286,346 L286,362 L262,362 Z", "#d0d3d8", LW_DETAIL),
        _path("M70,196 L70,220 A130,52 0 0 0 330,220 L330,196 Z", paint),
        f'<ellipse cx="200" cy="196" rx="130" ry="52" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<ellipse cx="200" cy="194" rx="118" ry="45" fill="{surface}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *[f'<ellipse cx="200" cy="194" rx="{rx}" ry="{rx * 0.38:.1f}" fill="none" stroke="#ffffff" stroke-opacity=".18" stroke-width="1.4"/>' for rx in (36, 56, 76)],
        _path("M204,176 L190,198 L202,198 L196,214 L212,190 L200,190 Z", "#ffffff", 1),
        _circle(200, 254, 3, "#7fe0a0", 1),
        _highlight("M96,212 Q130,244 190,250", 4, 0.5),
    ]


register(
    {"bouquet": bouquet, "socks": socks, "bed_frame": bed_frame, "watch": watch,
     "earrings": earrings, "compact": compact, "cardigan": cardigan, "bodysuit": bodysuit,
     "wallet": wallet, "keyring": keyring, "trophy": trophy, "charging_pad": charging_pad, "chairbed": chairbed,
     "mattress": mattress, "potted_tree": potted_tree, "pudding": pudding, "panettone": panettone},
    {"cardigan": 6},
)  # fmt: skip
