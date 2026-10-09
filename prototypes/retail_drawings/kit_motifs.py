"""Printable motifs for the retail drawing kit (gen#125, motif prints).

Small flat drawings that a print repeats on a surface (see :mod:`motifs`):
fruit, vegetables, animals, dinosaurs and vehicles, flowers, stars, seasonal
figures, food treats and tools. Each is an ordinary kit shape, so it also
draws as a product (a dinosaur toy, an orange) and every other kit shape is
a motif too.

Same house style as :mod:`kit`: one ink outline, round joins, the motif's
body painted with ``paint`` (the print's motif color). Tool figures are
simple stand-ins in the kit's style; the shared core's industrial figures
replace them once retail draws from the core.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register

LEAF = "#5aa24a"
STEM = "#7a5a3a"
WOOD = "#c8955a"
METAL = "#cfd5da"
YOLK = "#f2c14b"


def _circle(cx: float, cy: float, r: float, fill: str, width: float = LW, extra: str = "") -> str:
    return (
        f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{fill}" stroke="{INK}" '
        f'stroke-width="{width:g}"{extra}/>'
    )


def _star_points(cx: float, cy: float, outer: float, inner: float, n: int = 5) -> str:
    pts = []
    for k in range(2 * n):
        r = outer if k % 2 == 0 else inner
        a = math.pi * k / n - math.pi / 2
        pts.append(f"{cx + r * math.cos(a):.1f},{cy + r * math.sin(a):.1f}")
    return "M" + " L".join(pts) + " Z"


# --------------------------------------------------------------------------
# Fruit
# --------------------------------------------------------------------------


def orange(paint: str, fill: Fill, label: str | None) -> list[str]:
    dimples = ((150, 200), (182, 262), (236, 196), (256, 270), (208, 312), (130, 260), (280, 220))
    return [
        _path("M200,110 Q198,94 204,80", "none", 4),
        _path("M204,94 Q240,64 270,86 Q238,114 204,94 Z", LEAF, 2),
        _circle(200, 220, 112, paint),
        *[f'<circle cx="{x}" cy="{y}" r="2.6" fill="{_shade(fill.base, 0.2)}"/>' for x, y in dimples],
        _highlight("M132,182 Q142,146 176,130", 9, 0.45),
    ]


def lemon(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M64,222 Q84,206 106,160 Q200,96 294,160 Q316,206 336,222 Q316,238 294,284 Q200,348 106,284 Q84,238 64,222 Z"
    return [
        _path("M262,128 Q300,84 340,100 Q312,142 262,128 Z", LEAF, 2),
        _path(body, paint),
        _line("M268,130 Q300,108 330,104", 1.2),
        _highlight("M120,186 Q150,146 204,138", 9, 0.45),
    ]


def apple(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M200,140 C160,108 88,122 88,206 C88,288 150,346 200,322 C250,346 312,288 312,206 C312,122 240,108 200,140 Z"
    return [
        _path(body, paint),
        _path("M200,142 Q196,104 210,80", "none", 5, stroke=STEM),
        _path("M206,108 Q240,76 272,96 Q240,126 206,108 Z", LEAF, 2),
        _highlight("M120,190 Q126,160 152,146", 9, 0.45),
    ]


def strawberry(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M200,336 C128,296 86,212 110,164 C132,122 268,122 290,164 C314,212 272,296 200,336 Z"
    seeds = ((150, 180), (200, 172), (250, 180), (130, 222), (176, 220), (224, 220), (270, 222), (154, 262), (200, 264), (246, 262), (178, 300), (222, 300))
    calyx = "M200,150 L176,112 L200,128 L214,96 L222,130 L258,116 L236,148 L200,160 L164,148 L142,118 Z"
    return [
        _path(body, paint),
        *[
            f'<ellipse cx="{x}" cy="{y}" rx="3.4" ry="5.4" fill="{YOLK}" stroke="{INK}" stroke-width="0.8"/>'
            for x, y in seeds
        ],
        _path(calyx, LEAF, 2),
        _highlight("M128,180 Q138,154 162,144", 8, 0.4),
    ]


def cherries(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M150,250 Q170,150 222,96 M254,262 Q244,170 222,96", "none", 4, stroke=STEM),
        _path("M222,96 Q262,70 294,92 Q258,118 222,96 Z", LEAF, 2),
        _circle(150, 282, 58, paint),
        _circle(254, 292, 58, paint),
        _highlight("M118,262 Q124,240 144,232", 7, 0.45),
        _highlight("M222,272 Q228,250 248,242", 7, 0.45),
    ]


# --------------------------------------------------------------------------
# Vegetables
# --------------------------------------------------------------------------


def carrot(paint: str, fill: Fill, label: str | None) -> list[str]:
    root = "M150,128 Q200,108 250,128 Q238,220 206,344 Q200,352 194,344 Q162,220 150,128 Z"
    fronds = "M200,124 Q178,82 150,62 M200,124 Q200,76 206,48 M200,124 Q224,84 256,66"
    return [
        _path(fronds, "none", 7, stroke=LEAF),
        _path(root, paint),
        _line("M164,170 L184,172 M220,200 L238,198 M176,240 L194,242 M206,280 L220,278", 1.6),
    ]


def mushroom(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M164,222 L158,322 Q200,338 242,322 L236,222 Z", "#f4ecdc"),
        _path("M80,226 Q88,104 200,96 Q312,104 320,226 Q200,248 80,226 Z", paint),
        *[_circle(x, y, r, "#ffffff", 1.4) for x, y, r in ((150, 160, 16), (226, 140, 20), (270, 196, 12), (118, 206, 10), (200, 196, 13))],
    ]


# --------------------------------------------------------------------------
# Animals, dinosaurs and vehicles
# --------------------------------------------------------------------------


def cat(paint: str, fill: Fill, label: str | None) -> list[str]:
    head = "M136,170 L128,86 L176,124 Q200,116 224,124 L272,86 L264,170 Q264,226 200,228 Q136,226 136,170 Z"
    return [
        _path("M262,316 Q340,310 326,236 Q320,212 300,222", "none", 10, stroke=_shade(fill.base, 0.15)),
        _path("M126,330 Q118,240 168,218 L232,218 Q282,240 274,330 Z", paint),
        _path(head, paint),
        f'<ellipse cx="176" cy="166" rx="7" ry="10" fill="{INK}"/>',
        f'<ellipse cx="224" cy="166" rx="7" ry="10" fill="{INK}"/>',
        _path("M192,190 L208,190 L200,200 Z", "#e88a9a", 1.2),
        _line("M150,196 L110,190 M150,204 L112,212 M250,196 L290,190 M250,204 L288,212", 1.2),
    ]


def bird(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M96,240 L52,206 L60,262 Z", _shade(fill.base, 0.15), 2),
        _path("M90,236 Q120,150 220,150 Q300,150 304,226 Q300,300 200,306 Q120,306 90,236 Z", paint),
        _path("M296,190 L344,206 L298,220 Z", YOLK, 2),
        _path("M150,226 Q200,196 240,236 Q200,270 150,226 Z", _shade(fill.base, 0.15), 2),
        _circle(266, 196, 8, INK, 1),
        _line("M180,306 L170,342 M220,306 L228,342", 3),
    ]


def whale(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M70,226 Q80,146 200,146 Q290,146 316,212 L350,176 L362,252 L316,236 Q290,292 200,292 Q80,292 70,226 Z"
    return [
        _line("M168,128 Q160,96 140,86 M168,128 Q170,92 168,72 M168,128 Q178,96 196,86", 3, stroke="#5b9bd5"),
        _path(body, paint),
        _path("M80,246 Q200,284 300,240 Q290,288 200,290 Q100,290 80,246 Z", _tint(fill.base, 0.5), 1.4),
        _circle(124, 214, 7, INK, 1),
        _line("M108,240 Q124,250 140,240", 1.6),
    ]


def dinosaur(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = (
        "M52,258 Q116,240 130,222 Q160,184 222,182 Q262,182 276,170 Q284,140 290,110 "
        "Q296,86 322,86 Q348,88 344,108 Q328,118 312,120 Q306,162 302,204 Q302,252 282,264 "
        "L282,326 L254,326 L250,274 L172,274 L168,326 L140,326 L138,264 Q104,266 52,258 Z"
    )
    return [
        _path(body, paint),
        *[_circle(x, y, r, _shade(fill.base, 0.2), 1.2) for x, y, r in ((176, 214, 12), (220, 226, 9), (250, 204, 8), (150, 240, 7))],
        _circle(324, 100, 5, INK, 1),
        _line("M330,112 L344,108", 1.4),
    ]


def car(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M64,268 L64,228 Q66,212 86,210 L128,206 L160,166 Q170,156 190,156 L262,156 Q280,156 292,172 L318,206 L342,212 Q354,216 354,230 L354,268 Z"
    return [
        _path(body, paint),
        _path("M170,174 L196,174 L196,206 L144,206 Z", "#dbe9f4", LW_DETAIL),
        _path("M212,174 L260,174 Q270,174 278,184 L292,206 L212,206 Z", "#dbe9f4", LW_DETAIL),
        *[_circle(x, 270, 28, "#3a3f47") for x in (124, 294)],
        *[_circle(x, 270, 10, METAL, 1.2) for x in (124, 294)],
        f'<rect x="334" y="222" width="14" height="10" rx="3" fill="{YOLK}" stroke="{INK}" stroke-width="1"/>',
    ]


# --------------------------------------------------------------------------
# Flowers, stars and seasonal figures
# --------------------------------------------------------------------------


def daisy(paint: str, fill: Fill, label: str | None) -> list[str]:
    petals = [
        f'<ellipse cx="200" cy="128" rx="24" ry="62" transform="rotate({a} 200 200)" fill="{paint}" stroke="{INK}" stroke-width="2"/>'
        for a in range(0, 360, 36)
    ]
    return [*petals, _circle(200, 200, 42, YOLK)]


def tulip(paint: str, fill: Fill, label: str | None) -> list[str]:
    cup = "M146,110 L174,154 L200,100 L226,154 L254,110 Q268,206 200,234 Q132,206 146,110 Z"
    return [
        _path("M200,232 Q196,290 200,350", "none", 6, stroke=LEAF),
        _path("M198,320 Q140,300 128,240 Q182,256 198,300 Z", LEAF, 2),
        _path(cup, paint),
    ]


def star(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path(_star_points(200, 212, 140, 58), paint),
        _highlight("M170,150 L186,112", 6, 0.45),
    ]


def christmas_tree(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        f'<rect x="184" y="300" width="32" height="44" fill="{STEM}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _path("M200,150 L310,304 L90,304 Z", paint),
        _path("M200,108 L286,232 L114,232 Z", paint),
        _path("M200,70 L262,166 L138,166 Z", paint),
        _path(_star_points(200, 66, 22, 9), YOLK, 1.6),
        *[_circle(x, y, 8, c, 1.2) for x, y, c in ((160, 270, "#d23b3b"), (236, 252, YOLK), (196, 200, "#d23b3b"), (230, 150, YOLK))],
    ]


def pumpkin(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M200,140 Q196,110 212,88", "none", 9, stroke=STEM),
        f'<ellipse cx="146" cy="232" rx="70" ry="94" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<ellipse cx="254" cy="232" rx="70" ry="94" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<ellipse cx="200" cy="232" rx="62" ry="100" fill="{_shade(fill.base, 0.06)}" stroke="{INK}" stroke-width="{LW}"/>',
    ]


def snowflake(paint: str, fill: Fill, label: str | None) -> list[str]:
    arm = "M200,200 L200,70 M200,110 L176,88 M200,110 L224,88 M200,150 L170,126 M200,150 L230,126"
    out = []
    for a in range(0, 360, 60):
        g = f' transform="rotate({a} 200 200)"'
        out += [_path(arm, "none", 16, g), _path(arm, "none", 9, g, stroke=paint)]
    return out


# --------------------------------------------------------------------------
# Food treats
# --------------------------------------------------------------------------


def cupcake(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M118,226 L282,226 L258,336 L142,336 Z", "#f2d9b0"),
        _line("M150,230 L162,334 M184,230 L190,334 M216,230 L210,334 M250,230 L238,334", 1.4),
        _path("M108,230 Q96,186 140,180 Q140,128 200,130 Q260,128 260,180 Q304,186 292,230 Z", paint),
        _circle(200, 112, 18, "#d23b3b", 2),
    ]


def ice_cream(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        _path("M142,212 L258,212 L200,352 Z", "#e2b26a"),
        _line("M160,232 L230,300 M196,224 L248,262 M240,232 L170,300 M204,224 L152,262", 1.2),
        _path("M126,214 Q118,150 170,140 Q190,96 236,112 Q290,128 276,184 Q290,214 270,216 Z", paint),
    ]


def doughnut(paint: str, fill: Fill, label: str | None) -> list[str]:
    ring = "M90,210 A110,110 0 1,0 310,210 A110,110 0 1,0 90,210 Z M164,210 A36,36 0 1,1 236,210 A36,36 0 1,1 164,210 Z"
    icing = "M104,200 Q110,120 200,112 Q290,120 296,200 Q290,250 270,244 Q250,280 220,262 Q190,300 160,264 Q120,282 110,240 Q96,230 104,200 Z M168,206 A32,32 0 1,1 232,206 A32,32 0 1,1 168,206 Z"
    sprinkles = ((150, 150, 20), (240, 146, -30), (270, 200, 60), (130, 210, -50), (200, 136, 0), (250, 240, 30))
    return [
        _path(ring, "#e2b26a", extra=' fill-rule="evenodd"'),
        _path(icing, paint, 2, ' fill-rule="evenodd"'),
        *[
            f'<rect x="{x - 8}" y="{y - 2.5}" width="16" height="5" rx="2.5" fill="{c}" transform="rotate({r} {x} {y})"/>'
            for (x, y, r), c in zip(sprinkles, ("#ffffff", YOLK, "#5b9bd5", "#ffffff", LEAF, YOLK), strict=True)
        ],
    ]


# --------------------------------------------------------------------------
# Tools (novelty and gift ranges only; stand-ins for the core's figures)
# --------------------------------------------------------------------------


def hammer(paint: str, fill: Fill, label: str | None) -> list[str]:
    head = "M112,104 L262,104 Q300,96 318,70 L330,82 Q318,122 290,136 L262,136 L112,136 Q100,120 112,104 Z"
    return [
        f'<g transform="rotate(-30 200 200)">'
        f'<rect x="186" y="128" width="30" height="228" rx="10" fill="{WOOD}" stroke="{INK}" stroke-width="{LW}"/>'
        + _line("M194,300 L208,300 M194,316 L208,316 M194,332 L208,332", 1.2)
        + _path(head, paint)
        + _highlight("M122,112 L250,112", 4, 0.45)
        + "</g>"
    ]


def wrench(paint: str, fill: Fill, label: str | None) -> list[str]:
    jaw = "M170,58 L170,92 Q170,130 200,130 Q230,130 230,92 L230,58 L254,70 Q268,100 256,132 Q240,164 222,166 L178,166 Q160,164 144,132 Q132,100 146,70 Z"
    ring = "M150,322 A50,50 0 1,0 250,322 A50,50 0 1,0 150,322 Z M178,322 A22,22 0 1,1 222,322 A22,22 0 1,1 178,322 Z"
    return [
        f'<g transform="rotate(35 200 210)">'
        f'<rect x="182" y="150" width="36" height="140" fill="{paint}" stroke="{INK}" stroke-width="{LW}"/>'
        + _path(jaw, paint)
        + _path(ring, paint, extra=' fill-rule="evenodd"')
        + _highlight("M192,170 L192,276", 4, 0.45)
        + "</g>"
    ]


def screwdriver(paint: str, fill: Fill, label: str | None) -> list[str]:
    return [
        f'<g transform="rotate(40 200 200)">'
        f'<rect x="192" y="52" width="16" height="170" fill="{METAL}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
        + _path("M192,52 L208,52 L204,36 L196,36 Z", METAL, LW_DETAIL)
        + _path("M168,222 Q168,208 184,208 L216,208 Q232,208 232,222 L236,330 Q236,352 214,352 L186,352 Q164,352 164,330 Z", paint)
        + _line("M186,236 L186,330 M200,236 L200,330 M214,236 L214,330", 1.4)
        + "</g>"
    ]


def drill(paint: str, fill: Fill, label: str | None) -> list[str]:
    body = "M84,140 Q84,116 108,116 L268,116 Q292,116 292,140 L292,188 Q292,204 276,204 L214,204 L236,318 L176,318 L156,204 L108,204 Q84,204 84,180 Z"
    return [
        f'<rect x="292" y="146" width="32" height="28" fill="{_shade(METAL, 0.1)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _path("M324,154 L366,158 L366,162 L324,166 Z", METAL, LW_DETAIL),
        _line("M330,158 L362,160", 1.0),
        _path(body, paint),
        f'<rect x="160" y="300" width="94" height="40" rx="8" fill="{_shade(fill.base, 0.35)}" stroke="{INK}" stroke-width="{LW}"/>',
        _path("M176,212 L188,212 L196,248 L184,248 Z", "#3a3f47", 1.2),
        _line("M108,140 L262,140", 1.4, ' stroke-dasharray="6 4"'),
        _highlight("M100,128 L250,128", 4, 0.45),
    ]


def screw(paint: str, fill: Fill, label: str | None) -> list[str]:
    threads = " ".join(f"M178,{y} L222,{y + 10}" for y in range(150, 316, 18))
    return [
        _path("M178,140 L222,140 L222,316 L200,352 L178,316 Z", paint),
        _line(threads, 1.6),
        f'<ellipse cx="200" cy="120" rx="62" ry="22" fill="{_tint(fill.base, 0.2)}" stroke="{INK}" stroke-width="{LW}"/>',
        _path("M138,120 L138,132 Q200,162 262,132 L262,120", paint),
        f'<ellipse cx="200" cy="120" rx="62" ry="22" fill="{_tint(fill.base, 0.2)}" stroke="{INK}" stroke-width="{LW}"/>',
        _line("M176,114 L224,126 M176,126 L224,114", 3),
    ]


#: Printable motif -> its category (:mod:`motifs` reads it; any other kit shape is a "product").
CATEGORY = {
    "orange": "fruit", "lemon": "fruit", "apple": "fruit", "strawberry": "fruit", "cherries": "fruit",
    "carrot": "vegetables", "mushroom": "vegetables",
    "cat": "animals", "bird": "animals", "whale": "animals",
    "dinosaur": "dinosaurs and vehicles", "car": "dinosaurs and vehicles",
    "daisy": "flowers", "tulip": "flowers",
    "star": "stars",
    "christmas_tree": "seasonal", "pumpkin": "seasonal", "snowflake": "seasonal",
    "cupcake": "food treats", "ice_cream": "food treats", "doughnut": "food treats",
    "hammer": "tools", "wrench": "tools", "screwdriver": "tools", "drill": "tools", "screw": "tools",
}  # fmt: skip

register({name: globals()[name] for name in CATEGORY})
