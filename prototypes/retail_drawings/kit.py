"""A parametric SVG kit for retail product drawings (prototype for #125).

A drawing is ``render(shape, fill, label=..., brand=...)``: one flat line
drawing on a 400 x 400 sheet, in the same house style as the industrial
figures (a paper tint, a thin frame, one ink colour, round joins).

* ``shape`` names an entry of :data:`SHAPES` (clothing, footwear or food).
* ``fill`` is a :class:`Fill`: a solid colour or an SVG pattern
  (stripe, gingham, tartan, leopard, polka dot). It paints the product's
  main surface, so the colour and pattern facets can be checked by eye.
* ``label`` is the large product word a food pack carries ("Milk").
* ``brand`` is printed on a small tag in the bottom-left corner.
* ``params`` drive a parametric shape (``kit_garments``, ``kit_home``):
  a trouser's fit and rise, a top's neckline and sleeve, a frame's size.

Standalone on purpose: no import from the package, no dependency beyond the
standard library. It is a sneak peek, not the core's drawing kit.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from dataclasses import dataclass
from html import escape

SIZE = 400
INK = "#2b3440"
PAPER = "#fbfaf6"
LW = 3.0  # outline width
LW_DETAIL = 1.6  # seams, slots, lace marks
FONT = "Helvetica, Arial, sans-serif"
PATTERNS = ("solid", "stripe", "gingham", "tartan", "leopard", "polka")


@dataclass(frozen=True)
class Fill:
    """What the product's main surface is painted with."""

    pattern: str = "solid"
    base: str = "#cccccc"
    accent: str = "#333333"
    third: str = "#f2d14b"  # tartan's thin over-check

    def __post_init__(self) -> None:
        if self.pattern not in PATTERNS:
            raise ValueError(f"unknown pattern {self.pattern!r}; one of {PATTERNS}")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------


def _mix(a: str, b: str, t: float) -> str:
    """``a`` moved ``t`` of the way to ``b`` (both ``#rrggbb``)."""
    ca = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    cb = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(ca, cb, strict=True))


def _shade(c: str, t: float = 0.25) -> str:
    return _mix(c, "#000000", t)


def _tint(c: str, t: float = 0.5) -> str:
    return _mix(c, "#ffffff", t)


def _path(d: str, fill: str, width: float = LW, extra: str = "", stroke: str = INK) -> str:
    return (
        f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" '
        f'stroke-linejoin="round" stroke-linecap="round"{extra}/>'
    )


def _line(d: str, width: float = LW_DETAIL, extra: str = "", stroke: str = INK) -> str:
    return _path(d, "none", width, extra, stroke)


def _highlight(d: str, width: float, opacity: float) -> str:
    """A white gloss stroke (bottle shoulder, fruit skin)."""
    return _line(d, width, f' stroke-opacity="{opacity:g}"', "#ffffff")


def _mirror(d: str) -> str:
    """The path ``d`` reflected about the sheet's vertical centre line.

    Paths here are written as absolute commands with ``x,y`` pairs, so the
    reflection maps every pair's x to ``SIZE - x``.
    """
    out = []
    for tok in d.split():
        if "," in tok:
            head = tok.rstrip(",")
            letter = head[0] if head[0].isalpha() else ""
            x, y = head[len(letter) :].split(",")
            out.append(f"{letter}{SIZE - float(x):g},{y}")
        else:
            out.append(tok)
    return " ".join(out)


def _both(d: str, fill: str, width: float = LW) -> list[str]:
    return [_path(d, fill, width), _path(_mirror(d), fill, width)]


def _word(text: str, cx: float, cy: float, width: float, max_size: float, colour: str = INK) -> str:
    """``text`` centred on (cx, cy), as large as fits ``width``."""
    size = min(max_size, width / (0.62 * max(len(text), 1)))
    return (
        f'<text x="{cx:g}" y="{cy + size * 0.35:.1f}" font-family="{FONT}" '
        f'font-weight="700" font-size="{size:.1f}" text-anchor="middle" '
        f'fill="{colour}">{escape(text)}</text>'
    )


def _panel(
    x: float, y: float, w: float, h: float, text: str | None, max_size: float = 56, rx: float = 6
) -> list[str]:
    """A white label panel carrying the product word."""
    out = [
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{rx:g}" '
        f'fill="#ffffff" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
    ]
    if text:
        out.append(_word(text, x + w / 2, y + h / 2, w - 14, max_size))
    return out


# --------------------------------------------------------------------------
# Fills
# --------------------------------------------------------------------------


def pattern_defs(fill: Fill, pid: str) -> str:
    """The ``<pattern>`` element for ``fill`` (empty for a solid colour)."""
    b, a, t = fill.base, fill.accent, fill.third
    if fill.pattern == "solid":
        return ""
    if fill.pattern == "stripe":
        tile, body = (
            22,
            (
                f'<rect width="22" height="22" fill="{b}"/>'
                f'<rect y="0" width="22" height="9" fill="{a}"/>'
            ),
        )
    elif fill.pattern == "gingham":
        tile, body = (
            24,
            (
                f'<rect width="24" height="24" fill="{b}"/>'
                f'<rect width="24" height="12" fill="{a}" opacity=".5"/>'
                f'<rect width="12" height="24" fill="{a}" opacity=".5"/>'
            ),
        )
    elif fill.pattern == "tartan":
        tile, body = (
            56,
            (
                f'<rect width="56" height="56" fill="{b}"/>'
                f'<rect y="8" width="56" height="18" fill="{a}" opacity=".6"/>'
                f'<rect x="8" width="18" height="56" fill="{a}" opacity=".6"/>'
                f'<rect y="40" width="56" height="3" fill="{t}" opacity=".9"/>'
                f'<rect x="40" width="3" height="56" fill="{t}" opacity=".9"/>'
                f'<rect y="16" width="56" height="2" fill="#000000" opacity=".35"/>'
                f'<rect x="16" width="2" height="56" fill="#000000" opacity=".35"/>'
            ),
        )
    elif fill.pattern == "leopard":
        spots = [
            (12, 12, 8, 6, 20),
            (40, 18, 7, 9, -30),
            (24, 40, 9, 7, 10),
            (52, 50, 6, 7, 40),
            (6, 52, 6, 5, 0),
        ]
        rings = "".join(
            f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" transform="rotate({r} {x} {y})" '
            f'fill="{_shade(b, 0.2)}" stroke="{a}" stroke-width="3.2" stroke-dasharray="9 4"/>'
            for x, y, rx, ry, r in spots
        )
        dots = '<circle cx="31" cy="4" r="2.2"/><circle cx="56" cy="32" r="2"/><circle cx="4" cy="30" r="1.8"/>'
        tile, body = 60, f'<rect width="60" height="60" fill="{b}"/>{rings}<g fill="{a}">{dots}</g>'
    else:  # polka
        tile, body = (
            28,
            (
                f'<rect width="28" height="28" fill="{b}"/>'
                f'<circle cx="7" cy="7" r="4.5" fill="{a}"/><circle cx="21" cy="21" r="4.5" fill="{a}"/>'
            ),
        )
    return f'<pattern id="{pid}" width="{tile}" height="{tile}" patternUnits="userSpaceOnUse">{body}</pattern>'


# --------------------------------------------------------------------------
# Clothing and footwear
# --------------------------------------------------------------------------
# Every shape takes (paint, fill, label) and returns SVG elements. ``paint`` is
# the fill attribute value (a colour or ``url(#id)``); ``fill`` is the Fill, for
# shapes that need a shade of the base colour.


def tshirt(paint: str, fill: Fill, label: str | None) -> list[str]:
    d = (
        "M170,72 Q200,104 230,72 L292,88 L350,145 L316,180 L292,158 "
        "L292,345 L108,345 L108,158 L84,180 L50,145 L108,88 Z"
    )
    return [
        _path(d, paint),
        _line("M170,72 Q200,114 230,72"),
        _line("M108,158 L108,100 M292,158 L292,100", extra=' stroke-dasharray="4 4"'),
    ]


def blouse(paint: str, fill: Fill, label: str | None) -> list[str]:
    sleeve = "M120,82 L80,110 L52,300 L84,308 L112,170 Z"
    body = "M166,62 L200,118 L234,62 L280,82 L290,340 Q200,358 110,340 L120,82 Z"
    collar = "M166,62 L200,118 L176,112 L152,74 Z"
    return [
        *_both(sleeve, paint),
        _path(body, paint),
        *_both(collar, "#ffffff", LW_DETAIL),
        _line("M200,118 L200,348"),
        *[
            f'<circle cx="200" cy="{y}" r="4" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>'
            for y in (150, 195, 240, 285)
        ],
        _line("M52,300 L84,308", 4),
        _line(_mirror("M52,300 L84,308"), 4),
    ]


def dress(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M158,112 Q200,128 242,112 L236,196 Q290,270 334,352 Q200,378 66,352 Q110,270 164,196 Z"
    return [
        _line("M164,114 L172,48 M236,114 L228,48", 5),
        _path(body, paint),
        _line("M164,196 Q200,206 236,196", 2.2),
        _line("M180,206 Q170,290 150,366 M220,206 Q230,290 250,366", 1.2, ' stroke-opacity=".6"'),
    ]


def _jeans(paint: str, fill: Fill, legs: str) -> list[str]:
    return [
        _path(legs, paint),
        _path("M128,52 L272,52 L272,80 L128,80 Z", _shade(fill.base, 0.15)),
        _line("M200,80 L200,150"),
        _line("M200,80 Q214,120 200,150", 1.2),
        _line("M134,88 Q160,96 168,80 M266,88 Q240,96 232,80"),
        f'<circle cx="200" cy="66" r="4" fill="#d6b56a" stroke="{INK}" stroke-width="1.2"/>',
        *[
            f'<rect x="{x - 3}" y="48" width="6" height="36" fill="none" stroke="{INK}" stroke-width="1.2"/>'
            for x in (150, 250)
        ],
    ]


def jeans_straight(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Straight cut: each leg keeps one width from hip to hem."""
    legs = "M128,80 L272,80 L276,360 L210,360 L204,160 L196,160 L190,360 L124,360 Z"
    return [*_jeans(paint, fill, legs), _line("M124,348 L190,348 M210,348 L276,348", 1.2)]


def jeans_bootcut(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Bootcut: narrow through the knee, then flaring out to a wide hem."""
    legs = (
        "M128,80 L272,80 L262,250 L292,362 L206,362 L208,250 L204,160 L196,160 "
        "L192,250 L194,362 L108,362 L138,250 Z"
    )
    return [*_jeans(paint, fill, legs), _line("M110,350 L194,350 M206,350 L290,350", 1.2)]


def shorts(paint: str, fill: Fill, label: str | None) -> list[str]:
    legs = "M122,108 L278,108 L300,272 L212,284 L204,190 L196,190 L188,284 L100,272 Z"
    return [
        _path(legs, paint),
        _path("M122,86 L278,86 L278,108 L122,108 Z", _tint(fill.base, 0.4)),
        _line("M168,97 Q200,104 232,97", 1.2),
        _line("M200,108 L200,180"),
        _line("M102,258 L188,268 M212,268 L298,258", 1.2),
    ]


def skirt(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M138,92 L262,92 L318,330 Q200,350 82,330 Z"
    pleats = " ".join(
        f"M{200 + k * 18:g},100 L{200 + k * 36:g},{338 - abs(k) * 2:g}" for k in range(-3, 4)
    )
    return [
        _path(body, paint),
        _path("M134,66 L266,66 L264,92 L136,92 Z", _shade(fill.base, 0.2)),
        _line(pleats, 1.2, ' stroke-opacity=".7"'),
    ]


def coat(paint: str, fill: Fill, label: str | None) -> list[str]:
    sleeve = "M130,72 L92,96 L64,328 L100,334 L124,170 Z"
    body = "M164,48 L236,48 L272,72 L298,372 L102,372 L128,72 Z"
    lapel = "M164,48 L200,150 L170,140 L140,78 Z"
    belt = "M108,214 L292,214 L294,236 L106,236 Z"
    return [
        *_both(sleeve, paint),
        _path(body, paint),
        *_both(lapel, _shade(fill.base, 0.12), LW_DETAIL),
        _line("M200,150 L214,372"),
        _path(belt, _shade(fill.base, 0.18), LW_DETAIL),
        f'<rect x="188" y="210" width="28" height="30" rx="3" fill="none" stroke="{INK}" stroke-width="2"/>',
        *[
            f'<circle cx="{x}" cy="{y}" r="4.5" fill="{_shade(fill.base, 0.45)}" stroke="{INK}" stroke-width="1"/>'
            for y in (170, 270, 310)
            for x in (180, 238)
        ],
        _line("M64,328 L100,334", 4),
        _line(_mirror("M64,328 L100,334"), 4),
    ]


def trainer(paint: str, fill: Fill, label: str | None) -> list[str]:
    upper = (
        "M62,282 L62,196 Q64,164 104,166 L148,160 Q176,200 214,196 "
        "Q262,214 312,236 Q350,252 350,282 Z"
    )
    sole = "M50,280 L360,280 Q364,316 330,318 L72,318 Q46,316 50,280 Z"
    eyestay = (
        "M146,162 Q176,204 216,198 Q252,210 270,222 L256,236 Q226,224 206,218 Q166,220 140,178 Z"
    )
    laces = " ".join(
        f"M{x:g},{y:g} L{x + 14:g},{y - 20:g}"
        for x, y in ((158, 200), (184, 214), (210, 222), (236, 228))
    )
    toe = "M286,282 Q300,240 322,240 Q350,252 350,282 Z"
    return [
        _path(upper, paint),
        _path(toe, _tint(fill.base, 0.35), LW_DETAIL),
        _path(eyestay, _tint(fill.base, 0.2), LW_DETAIL),
        _line(laces, 6),
        _line(laces, 3, stroke="#ffffff"),
        _path("M62,262 L286,262 Q284,272 286,282 L62,282 Z", _tint(fill.base, 0.55), LW_DETAIL),
        _path("M62,196 Q60,170 84,166 L84,226 Q62,230 62,226 Z", _shade(fill.base, 0.2), LW_DETAIL),
        _path(sole, "#ffffff"),
        _line("M54,298 L356,298", 1.2),
    ]


def sandal(paint: str, fill: Fill, label: str | None) -> list[str]:
    footbed = (
        "M196,44 C258,44 272,118 264,186 C258,244 252,282 258,322 "
        "C262,364 232,382 200,382 C168,382 140,364 144,322 C150,282 142,244 136,186 C128,118 138,44 196,44 Z"
    )
    toe = "M134,104 Q200,74 266,104 L270,140 Q200,112 132,140 Z"
    cross = "M138,196 Q200,166 262,196 L260,232 Q200,204 140,232 Z"
    return [
        _path(footbed, "#e2c9a0"),
        _path(
            footbed,
            "none",
            1.0,
            ' transform="translate(200 213) scale(.9) translate(-200 -213)" stroke-opacity=".5"',
        ),
        _path(toe, paint),
        _path(cross, paint),
        _line("M142,300 Q200,286 258,300", 6),
        f'<rect x="250" y="292" width="14" height="16" rx="2" fill="#d6b56a" stroke="{INK}" stroke-width="1.2"/>',
    ]


def bra(paint: str, fill: Fill, label: str | None) -> list[str]:
    wing = "M112,176 L46,190 L50,228 L140,232 Z"
    cup = "M200,182 C190,142 160,118 114,126 C98,164 104,210 142,230 C172,242 198,228 200,182 Z"
    return [
        _line("M118,130 L140,48 M282,130 L260,48", 4),
        *_both(wing, paint),
        *_both(cup, paint),
        _line("M120,138 Q150,170 196,190", 1.2, ' stroke-opacity=".7"'),
        _line(_mirror("M120,138 Q150,170 196,190"), 1.2, ' stroke-opacity=".7"'),
        f'<circle cx="200" cy="200" r="6" fill="#ffffff" stroke="{INK}" stroke-width="1.4"/>',
    ]


# --------------------------------------------------------------------------
# Food: every container carries the product word in large text
# --------------------------------------------------------------------------


def carton(paint: str, fill: Fill, label: str | None) -> list[str]:
    side = _shade(fill.base, 0.2)
    return [
        _path("M240,150 L300,150 L300,362 L240,362 Z", side),
        _path("M240,150 L300,150 L270,96 Z", _shade(fill.base, 0.3)),
        _path("M100,150 L240,150 L270,96 L130,96 Z", _tint(fill.base, 0.3)),
        _path("M130,96 L270,96 L270,78 L130,78 Z", "#ffffff"),
        _path("M100,150 L240,150 L240,362 L100,362 Z", paint),
        *_panel(108, 214, 124, 86, label, 48),
    ]


def bottle(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M142,366 L142,186 Q142,138 178,116 L180,58 L220,58 L222,116 Q258,138 258,186 L258,366 Q200,374 142,366 Z"
    return [
        _path(body, paint),
        _path("M176,36 L224,36 L224,94 L176,94 Z", _shade(fill.base, 0.35)),
        *_panel(150, 226, 100, 92, label, 44),
        _highlight("M154,206 Q154,164 180,140", 5, 0.5),
    ]


def jar(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        f'<rect x="120" y="140" width="160" height="220" rx="28" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="130" y="96" width="140" height="46" rx="6" fill="{fill.accent}" stroke="{INK}" stroke-width="{LW}"/>',
        _line(
            " ".join(f"M{x},100 L{x},138" for x in range(142, 270, 12)), 1.0, ' stroke-opacity=".5"'
        ),
        *_panel(128, 196, 144, 104, label, 52),
    ]


def tin(paint: str, fill: Fill, label: str | None) -> list[str]:
    metal = "#d9dde0"
    return [
        _path("M112,112 L112,340 A88,20 0 0 0 288,340 L288,112 Z", paint),
        f'<ellipse cx="200" cy="112" rx="88" ry="20" fill="{metal}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<ellipse cx="200" cy="112" rx="72" ry="14" fill="none" stroke="{INK}" stroke-width="1"/>',
        _line("M112,140 A88,20 0 0 0 288,140 M112,316 A88,20 0 0 0 288,316", 1.2),
        *_panel(122, 180, 156, 100, label, 52),
    ]


def box(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M270,74 L304,56 L304,344 L270,362 Z", _shade(fill.base, 0.25)),
        _path("M110,74 L144,56 L304,56 L270,74 Z", _tint(fill.base, 0.25)),
        _path("M110,74 L270,74 L270,362 L110,362 Z", paint),
        *_panel(118, 120, 144, 96, label, 50),
    ]


def box_wide(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M330,150 L360,132 L360,302 L330,320 Z", _shade(fill.base, 0.25)),
        _path("M50,150 L80,132 L360,132 L330,150 Z", _tint(fill.base, 0.25)),
        _path("M50,150 L330,150 L330,320 L50,320 Z", paint),
        *_panel(78, 190, 224, 90, label, 50),
    ]


def crisps_bag(paint: str, fill: Fill, label: str | None) -> list[str]:
    xs = list(range(116, 292, 8))
    top = " ".join(f"L{x},{64 if i % 2 else 72}" for i, x in enumerate(xs))
    bottom = " ".join(f"L{x},{356 if i % 2 else 348}" for i, x in enumerate(reversed(xs)))
    d = f"M110,98 L116,72 {top} L290,98 Q312,210 290,322 L284,348 {bottom} L110,322 Q88,210 110,98 Z"
    return [
        _path(d, paint),
        _line("M110,98 L290,98 M110,322 L290,322", 1.4),
        _line(
            " ".join(f"M{x},74 L{x},96 M{x},324 L{x},346" for x in xs[1::2]),
            1.0,
            ' stroke-opacity=".5"',
        ),
        *_panel(110, 164, 180, 96, label, 48),
    ]


def tray(paint: str, fill: Fill, label: str | None) -> list[str]:
    black = "#3a3d42"
    return [
        _path("M60,186 L340,186 L320,330 L80,330 Z", black),
        f'<rect x="44" y="150" width="312" height="48" rx="14" fill="{_mix(black, "#ffffff", 0.25)}" stroke="{INK}" stroke-width="{LW}"/>',
        _path("M62,206 L338,206 L326,300 L74,300 Z", paint),
        *_panel(96, 214, 208, 78, label, 46),
    ]


def punnet(paint: str, fill: Fill, label: str | None) -> list[str]:
    berry = (
        "M0,-24 C18,-24 24,-8 16,10 C10,22 4,30 0,32 C-4,30 -10,22 -16,10 C-24,-8 -18,-24 0,-24 Z"
    )
    berries = []
    for x, y in (
        (126, 186),
        (166, 176),
        (206, 182),
        (246, 174),
        (282, 188),
        (146, 200),
        (226, 200),
        (266, 204),
    ):
        berries.append(
            f'<g transform="translate({x} {y})">{_path(berry, "#d23a3a", 2)}'
            f"{_path('M-12,-22 L0,-32 L12,-22 L0,-18 Z', '#4c9a3c', 1.4)}"
            f'<g fill="#f6e27a"><circle cx="-6" cy="-6" r="1.6"/><circle cx="6" cy="2" r="1.6"/><circle cx="-2" cy="12" r="1.6"/></g></g>'
        )
    slots = " ".join(f"M{x},236 L{x + (x - 200) * -0.08:.1f},344" for x in range(112, 300, 20))
    return [
        *berries,
        _path("M86,204 L314,204 L288,356 L112,356 Z", "#eef6f8"),
        _line(slots, 1.0, ' stroke-opacity=".5"'),
        _path("M96,224 L304,224 L296,276 L104,276 Z", paint, LW_DETAIL),
        _word(label or "", 200, 250, 186, 40, "#ffffff") if label else "",
    ]


def tub(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M112,118 L288,118 L262,356 Q200,366 138,356 Z", paint),
        f'<ellipse cx="200" cy="114" rx="96" ry="18" fill="#e9edf0" stroke="{INK}" stroke-width="{LW}"/>',
        *_panel(124, 190, 152, 96, label, 50),
    ]


def loaf(paint: str, fill: Fill, label: str | None) -> list[str]:
    d = (
        "M64,336 L64,212 C60,150 116,128 150,150 C172,118 228,118 250,150 "
        "C284,128 340,150 336,212 L336,336 Z"
    )
    return [
        _path(d, paint),
        _line("M110,180 Q124,164 140,170 M186,150 Q200,136 216,146 M262,170 Q276,160 292,178", 3),
        _line("M64,322 L336,322", 1.2, ' stroke-opacity=".5"'),
        *_panel(108, 222, 184, 84, label, 52),
    ]


def cake(paint: str, fill: Fill, label: str | None) -> list[str]:
    drip = " ".join(
        f"Q{x + 10},{252 if i % 2 else 262} {x + 20},248" for i, x in enumerate(range(80, 320, 20))
    )
    return [
        f'<ellipse cx="200" cy="350" rx="150" ry="18" fill="#e6e8ea" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _path("M80,236 L80,340 A120,16 0 0 0 320,340 L320,236 Z", paint),
        f'<ellipse cx="200" cy="236" rx="120" ry="16" fill="#ffffff" stroke="{INK}" stroke-width="{LW}"/>',
        _path(f"M80,236 L80,248 {drip} L320,236 Z", "#ffffff", 1.4),
        _path("M130,160 L130,236 A70,10 0 0 0 270,236 L270,160 Z", paint),
        f'<ellipse cx="200" cy="160" rx="70" ry="10" fill="#ffffff" stroke="{INK}" stroke-width="{LW}"/>',
        _path(
            "M184,150 L184,110 L192,110 L192,150 Z M208,150 L208,110 L216,110 L216,150 Z",
            "#f4f4f4",
            1.4,
        ),
        _path(
            "M188,108 Q182,96 188,86 Q196,98 188,108 Z M212,108 Q206,96 212,86 Q220,98 212,108 Z",
            "#f6b23c",
            1.2,
        ),
        *_panel(116, 266, 168, 62, label, 46),
    ]


def round_produce(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M200,96 Q196,70 206,52", "none", 5),
        _path("M206,72 Q246,46 272,70 Q238,96 206,72 Z", "#5aa24a", 2),
        f'<circle cx="200" cy="222" r="128" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        _highlight("M126,170 Q138,138 170,124", 8, 0.45),
        *_panel(104, 236, 192, 70, label, 46, 35),
    ]


#: Shape name -> drawing function.
SHAPES = {
    "tshirt": tshirt,
    "blouse": blouse,
    "dress": dress,
    "jeans_straight": jeans_straight,
    "jeans_bootcut": jeans_bootcut,
    "shorts": shorts,
    "skirt": skirt,
    "coat": coat,
    "trainer": trainer,
    "sandal": sandal,
    "bra": bra,
    "carton": carton,
    "bottle": bottle,
    "jar": jar,
    "tin": tin,
    "box": box,
    "box_wide": box_wide,
    "crisps_bag": crisps_bag,
    "tray": tray,
    "punnet": punnet,
    "tub": tub,
    "loaf": loaf,
    "cake": cake,
    "round_produce": round_produce,
}


#: Shapes drawn off the sheet's centre, moved down (+) or up (-) to sit on it.
OFFSET_Y = {"bra": 50, "trainer": -24}


def _brand_tag(brand: str) -> list[str]:
    w = 16 + 6.6 * len(brand)
    return [
        f'<rect x="16" y="364" width="{w:.1f}" height="20" rx="4" fill="#ffffff" stroke="{INK}" stroke-width="1"/>',
        f'<circle cx="25" cy="374" r="2.4" fill="none" stroke="{INK}" stroke-width="1"/>',
        f'<text x="32" y="378" font-family="{FONT}" font-size="11" fill="{INK}">{escape(brand)}</text>',
    ]


def register(shapes: dict, offsets: dict | None = None) -> None:
    """Add another module's shapes (and their vertical offsets) to the kit."""
    SHAPES.update(shapes)
    OFFSET_Y.update(offsets or {})


def render(
    shape: str,
    fill: Fill,
    label: str | None = None,
    brand: str | None = None,
    uid: str = "p",
    params: dict | None = None,
) -> str:
    """One product drawing as a standalone SVG document string.

    ``uid`` makes the pattern id unique, so several drawings can be inlined in
    one HTML page without their ``<pattern>`` ids colliding. ``params`` are
    passed to a parametric shape (a trouser's fit and rise, a top's neckline).
    """
    draw = SHAPES[shape]
    pid = f"fill-{uid}"
    defs = pattern_defs(fill, pid)
    paint = fill.base if fill.pattern == "solid" else f"url(#{pid})"
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{SIZE}" height="{SIZE}" viewBox="0 0 {SIZE} {SIZE}">',
        f"<defs>{defs}</defs>" if defs else "",
        f'<rect width="{SIZE}" height="{SIZE}" fill="{PAPER}"/>',
        f'<rect x="6" y="6" width="{SIZE - 12}" height="{SIZE - 12}" fill="none" stroke="{INK}" stroke-width="1"/>',
        f'<g transform="translate(0 {OFFSET_Y[shape]})">' if shape in OFFSET_Y else "",
        *draw(paint, fill, label, **(params or {})),
        "</g>" if shape in OFFSET_Y else "",
        *(_brand_tag(brand) if brand else []),
        "</svg>",
    ]
    return "".join(p for p in parts if p)
