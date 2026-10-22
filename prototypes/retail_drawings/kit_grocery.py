"""Pack shapes the grocery build draws that the kit lacked (gen#154).

==============  ===================================================  ======
shape           draws                                                params
==============  ===================================================  ======
bar             a wrapped bar: crimped ends, the wrapper torn back    --
                at one corner to show the segments
bag             a stand-up bag: a zip seal across the top, a          --
                rounded gusset at the foot
butter_block    a foil-wrapped block of butter, the foil folded       --
                at the end and peeled back to show the butter
lidded_tub      a tapering tub with a snap-on lid and a thumb         --
                tab (ice cream, a spread)
steak_tray      a black tray under film holding one cut of meat:      --
                a fat rim, marbling and a label on the tray (a steak)
pizza           a round pizza on a card base under film, seen at a    flavor,
                slight angle: toppings by flavour, diameter by inches  pack_size
==============  ===================================================  ======

Each paints the record's fill on the pack's main surface and carries the product
word on a white label panel, as the kit's other packs do (``kit.box``, ``kit.jar``).
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from kit import INK, LW, LW_DETAIL, Fill, _line, _mix, _panel, _path, _shade, register


def bar(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A wrapped bar, the wrapper peeled back at the top right to show the segments."""
    crimp_l = " ".join(f"L{52 if i % 2 else 60},{132 + i * 12}" for i in range(12))
    crimp_r = " ".join(f"L{348 if i % 2 else 340},{264 - i * 12}" for i in range(12))
    body = "M60,132 L300,132 L340,170 L340,276 L60,276 Z"
    segment = _mix(fill.base, "#3b2416", 0.75)
    return [
        _path(f"M60,128 {crimp_l} L60,280 Z", paint, 1.6),
        _path(f"M340,166 {crimp_r} L340,280 Z", paint, 1.6),
        _path(body, paint),
        _path("M300,132 L340,132 L340,170 Z", segment),
        _line("M306,140 L332,140 M318,132 L318,162", 1.2, ' stroke-opacity=".6"'),
        _path("M300,132 L340,170 L318,176 Z", _mix(fill.base, "#ffffff", 0.35), 1.6),
        *_panel(110, 172, 180, 64, label, 40),
    ]


def bag(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A stand-up bag with a zip seal and a rounded gusset."""
    return [
        _path("M112,70 L288,70 L300,330 Q300,352 278,352 L122,352 Q100,352 100,330 Z", paint),
        _line("M110,98 L290,98", 2.4),
        _line("M110,106 L290,106", 1.0, ' stroke-dasharray="4 4"'),
        _line("M104,316 Q200,300 296,316", 1.4, ' stroke-opacity=".6"'),
        *_panel(122, 160, 156, 96, label, 44),
    ]


def butter_block(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A foil-wrapped butter block, seen from above-left, the foil peeled back at one end."""
    return [
        _path("M70,196 L130,150 L350,150 L290,196 Z", _mix(fill.base, "#ffffff", 0.45)),
        _path("M290,196 L350,150 L350,262 L290,310 Z", _mix(fill.base, "#000000", 0.2)),
        _path("M70,196 L290,196 L290,310 L70,310 Z", paint),
        _line("M290,226 L350,182 M290,262 L350,218", 1.2, ' stroke-opacity=".55"'),
        _line("M80,204 L282,204", 1.2, ' stroke-opacity=".5"'),
        _path("M70,196 L130,150 L150,170 L96,206 Z", "#f6dc7a", 1.6),
        _line("M94,300 L270,300", 1.4, ' stroke-opacity=".5"'),
        *_panel(84, 214, 190, 80, label, 44),
    ]


def lidded_tub(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A tapering tub with a snap-on lid, its rim and a thumb tab."""
    lid = _mix(fill.base, "#ffffff", 0.7)
    return [
        _path("M116,156 L284,156 L266,350 Q200,364 134,350 Z", paint),
        f'<rect x="104" y="118" width="192" height="42" rx="12" fill="{lid}" stroke="{INK}" stroke-width="{LW}"/>',
        _line("M116,132 L284,132", 1.2, ' stroke-opacity=".5"'),
        _path("M284,136 L312,142 L312,152 L284,150 Z", lid, 1.6),
        *_panel(128, 186, 144, 106, label, 48),
    ]


def steak_tray(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A black tray under film holding one steak: its fat rim, marbling and a label panel.

    The meat is the record's fill; the rim is a lighter tone of it and the marbling a pale
    streak, so a sirloin, a ribeye and a minute steak differ by color and by their label."""
    fat = _mix(fill.base, "#fff4e6", 0.7)
    meat = "M92,246 C88,214 138,198 192,202 C250,196 312,210 310,248 C308,284 252,298 196,294 C140,296 96,282 92,246 Z"
    return [
        _path("M52,190 L348,190 L328,326 L72,326 Z", "#3a3d42"),
        f'<rect x="38" y="156" width="324" height="44" rx="14" fill="{_mix("#3a3d42", "#ffffff", 0.25)}" stroke="{INK}" stroke-width="{LW}"/>',
        _path("M62,206 L338,206 L324,316 L76,316 Z", _mix("#f4efe6", "#ffffff", 0.4), 1.4),
        _path(meat, fat, extra=' class="steak"'),
        _path("M104,246 C102,222 142,210 192,214 C246,208 298,220 296,248 C294,276 248,286 196,282 C146,284 106,272 104,246 Z", paint, 1.4, ' class="lean"'),
        _line("M134,238 Q160,226 188,236 M214,230 Q246,222 272,238 M150,262 Q184,252 214,262 M232,258 Q256,252 276,262", 2.2, ' stroke-opacity=".55"', _mix(fill.base, "#fff4e6", 0.8)),
        _line("M72,170 L340,170", 1.2, ' stroke-opacity=".5"', "#ffffff"),
        *_panel(206, 268, 130, 46, label, 30),
    ]


# ---------------------------------------------------------------------------
# The chilled pizza (gen#604)
# ---------------------------------------------------------------------------

#: The pie is seen from above at a slight angle: its depth is this share of its width.
TILT = 0.6
#: The drawn radius of a 12 inch pizza; a smaller one is in proportion (10 inch is 5/6 of it).
PIZZA_RADIUS = 160.0
PIZZA_BASE_Y = 262.0  # the card's lowest edge: every size sits on one baseline
#: Each flavour's toppings, cycled over a spiral of positions, and how many of them.
TOPPINGS = {
    "Margherita": (("mozzarella", "basil"), 14),
    "Pepperoni": (("pepperoni",), 13),
    "Vegan Garden": (("green_pepper", "red_pepper", "aubergine", "courgette"), 16),
    "Four Cheese": ((), 0),  # four wedges, drawn whole
    "Ham & Pineapple": (("ham", "pineapple"), 16),
}
CHEESES = ("#f7edd2", "#f0a43c", "#f6d36a", "#d7dfec")  # mozzarella, cheddar, edam, blue-veined


def _ell(cls: str, cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW,
         extra: str = "") -> str:  # fmt: skip
    return (f'<ellipse class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"{extra}/>')  # fmt: skip


def _bit(kind: str, x: float, y: float, k: float) -> list[str]:
    """One topping at (x, y), ``k`` times its 12 inch size, squashed by the view's tilt."""
    r = 17 * k
    flat = r * TILT
    d = LW_DETAIL * 0.7
    if kind == "pepperoni":
        return [_ell("pep", x, y, r * 1.1, flat * 1.1, "#a8322b", d),
                f'<circle cx="{x - r * .4:.1f}" cy="{y - flat * .2:.1f}" r="{1.6 * k:.1f}" fill="#7a2018"/>',
                f'<circle cx="{x + r * .4:.1f}" cy="{y + flat * .3:.1f}" r="{1.4 * k:.1f}" fill="#7a2018"/>']  # fmt: skip
    if kind == "mozzarella":
        return [_ell("moz", x, y, r * 1.2, flat * 1.2, "#fbf6e6", d)]
    if kind == "basil":
        return [_ell("basil", x, y, r * 0.9, flat * 0.55, "#3f8a3a", d, f' transform="rotate(-25 {x:.1f} {y:.1f})"')]
    if kind == "green_pepper":
        return [_ell("gp", x, y, r, flat, "#6dae3c", d), _ell("gp", x, y, r * .45, flat * .45, "#f1cf6a", 0.8)]
    if kind == "red_pepper":
        return [_ell("rp", x, y, r * 1.1, flat * .5, "#d23a2c", d, f' transform="rotate(20 {x:.1f} {y:.1f})"')]
    if kind == "aubergine":
        return [_ell("aub", x, y, r, flat, "#6a3f7a", d), _ell("aub", x, y, r * .55, flat * .55, "#e8dcb4", 0.8)]
    if kind == "courgette":
        return [_ell("cou", x, y, r * .95, flat * .95, "#a9cf6a", d), _ell("cou", x, y, r * .6, flat * .6, "#d9efb0", 0.8)]
    if kind == "ham":
        return [_ell("ham", x, y, r * 1.15, flat * .85, "#e9a0a0", d, f' transform="rotate(-15 {x:.1f} {y:.1f})"')]
    if kind == "pineapple":
        w, h = r * .9, flat * .9
        tri = f"M{x - w:.1f},{y + h:.1f} L{x:.1f},{y - h:.1f} L{x + w:.1f},{y + h:.1f} Z"
        return [_path(tri, "#f4d03f", d)]
    raise ValueError(f"no topping {kind!r}")  # pragma: no cover


def _four_cheeses(cx: float, cy: float, rx: float, ry: float) -> list[str]:
    """Four wedges of cheese, one per quarter: pale mozzarella, orange cheddar, yellow edam
    with a red rind dot, and blue-veined emmental."""
    out = []
    for i, tone in enumerate(CHEESES):
        pts = [(cx + rx, cy), (cx, cy + ry), (cx - rx, cy), (cx, cy - ry), (cx + rx, cy)]
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        out.append(_path(f"M{cx:.1f},{cy:.1f} L{ax:.1f},{ay:.1f} A{rx:.1f},{ry:.1f} 0 0 1 {bx:.1f},{by:.1f} Z", tone, LW_DETAIL * 0.7))
        mx, my = (ax + bx) / 2 * 0.62 + cx * 0.38, (ay + by) / 2 * 0.62 + cy * 0.38
        dot = ("#c23a2e", "#d98a1c", "#c23a2e", "#4a6fb0")[i]
        out.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="{rx * 0.05:.1f}" fill="{dot}"/>')
    return out


def pizza(paint: str, fill: Fill, label: str | None, flavor: str = "Margherita",
          pack_size: str = "12 inch") -> list[str]:  # fmt: skip
    """A round pizza on a card base under film, seen from above at a slight angle.

    ``flavor`` picks the toppings and ``pack_size`` ("10 inch", "12 inch") the diameter, both
    the SKU's own values (per-SKU drawing params), so each flavour and size is its own picture.
    The card is tinted by the record's fill and the label panel below carries the range name
    and the band of the style's flavour colors."""
    if flavor not in TOPPINGS:
        raise ValueError(f"no pizza flavour {flavor!r}; known: {sorted(TOPPINGS)}")
    inches = float(pack_size.split()[0])
    if not 6 <= inches <= 12:
        raise ValueError(f"a pizza of {pack_size!r} does not fit the sheet")
    r = PIZZA_RADIUS * inches / 12
    k = r / PIZZA_RADIUS
    ry = r * TILT
    cx, cy = 200.0, PIZZA_BASE_Y - 26 - ry  # the card's foot (26 below the crust's middle line) on the baseline
    kinds, n = TOPPINGS[flavor]
    bits: list[str] = []
    for i in range(n):
        rad = math.sqrt((i + 0.6) / n) * 0.72
        ang = i * 2.39996
        bits += _bit(kinds[i % len(kinds)], cx + rad * r * math.cos(ang), cy + rad * ry * math.sin(ang), k)
    if flavor == "Four Cheese":
        bits = _four_cheeses(cx, cy, r * 0.8, ry * 0.8)
    card = _mix(paint, "#e8dcc0", 0.55)
    return [
        _ell("card", cx, cy + 12, r + 18, ry + 14, _shade(card, 0.15), LW),
        _ell("card", cx, cy + 6, r + 18, ry + 14, card, LW),
        _ell("crust", cx, cy, r, ry, "#d9a05b"),
        _ell("sauce", cx, cy, r * 0.88, ry * 0.88, "#c4402e", LW_DETAIL),
        _ell("cheese", cx, cy, r * 0.82, ry * 0.82, "#f3d27a", 0.8),
        f'<g class="toppings">{"".join(bits)}</g>',
        _ell("film", cx, cy + 2, r + 12, ry + 10, "#ffffff", 1.2, ' fill-opacity=".16" stroke-opacity=".55"'),
        _line(f"M{cx - r * .7:.1f},{cy - ry * .55:.1f} Q{cx - r * .35:.1f},{cy - ry * .95:.1f} {cx + r * .1:.1f},{cy - ry * 1.02:.1f}",
              3.0, ' stroke-opacity=".6"', "#ffffff"),
        *_panel(100, 292, 200, 62, label, 36),
    ]  # fmt: skip


register({"bar": bar, "bag": bag, "butter_block": butter_block, "lidded_tub": lidded_tub,
          "steak_tray": steak_tray, "pizza": pizza})
