"""Household shapes for the retail drawing kit (gen#200): cookware, bins, storage, laundry.

Each type of :mod:`household_rows` has its own flat drawing in the kit's house style:
outlines in the kit's ink, the record's fill (color and pattern) on the product's main
surface, so a shopper tells a saucepan from a skillet, a pedal bin from a recycling bin
and a spin mop from a mop bucket at thumbnail size.

==============  ==================================================  ========================
shape           draws                                               params
==============  ==================================================  ========================
saucepan        one pan from the side, or a set's pans in a row     count, lid
                (one ``class="pan"`` group per piece)
frying_pan      a pan in three-quarter view: frying, skillet, wok,  kind, coating
                griddle (ridged) or crepe (shallow)
casserole       a lidded pot with two loop handles; glass is clear  form, material
kitchen_bin     a tall bin: a pedal, a touch-top button, a sensor   kind, compartments
                panel, or a lid split per compartment
storage_box     a lidded or open box; clear plastic shows inside    form, lid, clear, material
laundry_basket  a basket, hamper, folding or two-compartment one    kind, material
mop             a spin mop, flat mop, sponge mop or a mop bucket    kind
clothes_airer   a folding, tower, heated or wall-mounted airer      kind, tiers
==============  ==================================================  ========================

A drawing never prints a size: a style's sizes share one image per colorway, so a number
on it would be wrong for every size but one. Every param is a string with a default, so
each shape also draws bare. A count the row states (pans in a set, compartments, tiers)
is drawn as that many marked groups, which ``tests/test_retail_household_200.py`` counts.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, _tint, register

STEEL = "#cfd5da"
STEEL_DARK = "#8f989f"
BLACK = "#2f2f35"
GLASS = "#dcebef"
WOOD = "#b8875a"
#: A pan's cooking surface by coating.
COATINGS = {"non-stick": "#3a3a40", "ceramic": "#efe6d2", "pre-seasoned": "#2b2b2e",
            "uncoated": "#6f6f72", "enamel": "#e9e2d0"}  # fmt: skip
WOVEN = frozenset({"wicker", "seagrass", "rattan", "water hyacinth"})


def _n(value: str, default: int) -> int:
    try:
        return max(1, int(str(value).split()[0]))
    except (ValueError, IndexError):
        return default


def _ell(
    cx: float, cy: float, rx: float, ry: float, fill: str, width: float = LW, extra: str = ""
) -> str:
    return (f'<ellipse{extra} cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>')  # fmt: skip


def _rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str,
    r: float = 4,
    width: float = LW,
    extra: str = "",
) -> str:
    return (f'<rect{extra} x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{r:g}" '
            f'fill="{fill}" stroke="{INK}" stroke-width="{width}"/>')  # fmt: skip


def _group(cls: str, parts: list[str]) -> str:
    return f'<g class="{cls}">' + "".join(parts) + "</g>"


def _shadow(cx: float, cy: float, rx: float) -> str:
    return f'<ellipse cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{rx * 0.08:.1f}" fill="#000000" fill-opacity=".08"/>'


def _weave(x0: float, y0: float, x1: float, y1: float, step: float = 14) -> list[str]:
    """A basket weave over a box: rows of short alternating strokes."""
    out, row, y = [], 0, y0 + step / 2
    while y < y1 - 2:
        d = " ".join(f"M{x:.1f},{y - 4:.1f} L{x + step * 0.6:.1f},{y + 4:.1f}" if row % 2 else
                     f"M{x:.1f},{y + 4:.1f} L{x + step * 0.6:.1f},{y - 4:.1f}"
                     for x in _steps(x0 + 3, x1 - step * 0.6 - 2, step))  # fmt: skip
        out.append(_line(d, 1.2, ' stroke-opacity=".55"'))
        y, row = y + step, row + 1
    return out


def _steps(a: float, b: float, step: float) -> list[float]:
    out, x = [], a
    while x <= b:
        out.append(x)
        x += step
    return out


# --------------------------------------------------------------------------
# Cookware
# --------------------------------------------------------------------------


def _pan(cx: float, base: float, w: float, paint: str, fill: Fill, lid: str, handle: bool) -> str:
    """One saucepan from the side: a straight-walled body, its rim, a long handle, a lid."""
    h = w * 0.62
    top = base - h
    body = (f"M{cx - w / 2:.1f},{top:.1f} L{cx - w / 2:.1f},{base - 12:.1f} Q{cx - w / 2:.1f},{base:.1f} {cx - w / 2 + 12:.1f},{base:.1f} "
            f"L{cx + w / 2 - 12:.1f},{base:.1f} Q{cx + w / 2:.1f},{base:.1f} {cx + w / 2:.1f},{base - 12:.1f} L{cx + w / 2:.1f},{top:.1f} Z")  # fmt: skip
    parts = []
    if handle:
        hx = cx + w / 2
        parts.append(
            _path(
                f"M{hx:.1f},{top + 8:.1f} L{hx + w * 0.72:.1f},{top - 6:.1f} L{hx + w * 0.74:.1f},{top + 6:.1f} L{hx:.1f},{top + 22:.1f} Z",
                STEEL_DARK,
            )
        )
    parts += [_path(body, paint), _line(f"M{cx - w / 2 + 6:.1f},{top + 16:.1f} L{cx + w / 2 - 6:.1f},{top + 16:.1f}", 1.2, ' stroke-opacity=".5"'),
              _ell(cx, top, w / 2 + 2, w * 0.07, _shade(fill.base, 0.25), LW_DETAIL)]  # fmt: skip
    if lid != "none":
        glass = lid == "glass"
        dome = f"M{cx - w / 2 - 3:.1f},{top:.1f} Q{cx:.1f},{top - w * 0.36:.1f} {cx + w / 2 + 3:.1f},{top:.1f} Z"
        parts.append(
            _path(dome, GLASS if glass else STEEL, LW, ' fill-opacity=".75"' if glass else "")
        )
        parts.append(
            _rect(
                cx - 10, top - w * 0.18 - 12, 20, 12, BLACK if glass else STEEL_DARK, 3, LW_DETAIL
            )
        )
        if glass:
            parts.append(
                _highlight(
                    f"M{cx - w * 0.3:.1f},{top - 6:.1f} Q{cx - w * 0.15:.1f},{top - w * 0.15:.1f} {cx:.1f},{top - w * 0.17:.1f}",
                    3,
                    0.7,
                )
            )
    return _group("pan", parts)


def saucepan(
    paint: str, fill: Fill, label: str | None, count: str = "1", lid: str = "glass"
) -> list[str]:
    """One saucepan with its handle, or a set's ``count`` pans in a row, largest first.

    A set's handles tuck behind the next pan, so each pan is drawn left to right."""
    n = _n(count, 1)
    if n == 1:
        return [_shadow(160, 318, 120), _pan(160, 312, 190, paint, fill, lid, True)]
    raw = [1 - 0.1 * i for i in range(n)]
    gap = 10.0
    widths = [r * (300 - gap * (n - 1)) / sum(raw) for r in raw]  # the last handle fits too
    xs, x = [], 12.0
    for w in widths:
        xs.append(x + w / 2)
        x += w + gap
    out = [_shadow(200, 318, 180)]
    for cx, w in zip(xs, widths, strict=True):
        out.append(_pan(cx, 312, w, paint, fill, lid, True))
    return out


def frying_pan(
    paint: str, fill: Fill, label: str | None, kind: str = "frying", coating: str = "non-stick"
) -> list[str]:
    """A pan seen from above at an angle: the outside in the fill, the cooking surface in its
    coating's color. A skillet has pour spouts and a helper handle, a wok a deep bowl, a
    griddle ridges, a crepe pan a shallow wall."""
    surface = COATINGS.get(coating, COATINGS["non-stick"])
    cx, cy, rx, ry = 170.0, 200.0, 125.0, 72.0
    wall = {"crepe": 8, "wok": 0, "skillet": 30, "griddle": 24}.get(kind, 22)
    out = [_shadow(cx, cy + ry + wall + 16, rx)]
    if kind == "wok":
        out.append(
            _path(
                f"M{cx + rx - 4},{cy - 4} L{cx + rx + 110},{cy - 44} L{cx + rx + 116},{cy - 30} L{cx + rx},{cy + 14} Z",
                WOOD,
            )
        )
        out.append(
            _path(
                f"M{cx - rx:.1f},{cy:.1f} Q{cx - rx + 20:.1f},{cy + ry + 70:.1f} {cx:.1f},{cy + ry + 74:.1f} Q{cx + rx - 20:.1f},{cy + ry + 70:.1f} {cx + rx:.1f},{cy:.1f} Z",
                paint,
            )
        )
        out.append(
            _line(
                f"M{cx - rx - 2},{cy - 6} Q{cx - rx - 34},{cy - 4} {cx - rx - 6},{cy + 16}",
                5,
                stroke=STEEL_DARK,
            )
        )
        out += [
            _ell(cx, cy, rx, ry, surface),
            _ell(cx, cy + 6, rx * 0.55, ry * 0.5, _shade(surface, 0.15), LW_DETAIL),
        ]
        return out
    out.append(_path(f"M{cx + rx - 6},{cy - 6} L{cx + rx + 118},{cy - 34} Q{cx + rx + 130},{cy - 26} {cx + rx + 120},{cy - 16} L{cx + rx - 2},{cy + 14} Z",
                     BLACK if kind != "skillet" else paint))  # fmt: skip
    if kind == "skillet":
        out.append(
            _path(
                f"M{cx - rx + 4},{cy - 14} Q{cx - rx - 34},{cy - 4} {cx - rx + 6},{cy + 18} Z",
                paint,
            )
        )
    out.append(
        _path(
            f"M{cx - rx:.1f},{cy:.1f} L{cx - rx + 6:.1f},{cy + wall:.1f} A{rx - 6:.1f},{ry - 4:.1f} 0 0 0 {cx + rx - 6:.1f},{cy + wall:.1f} L{cx + rx:.1f},{cy:.1f} Z",
            paint,
        )
    )
    out.append(_ell(cx, cy, rx, ry, paint))
    inner = 0.95 if kind == "crepe" else 0.86
    out.append(_ell(cx, cy + 3, rx * inner, ry * inner, surface, LW_DETAIL))
    if kind == "skillet":
        out += [_path(f"M{cx - 14},{cy - ry + 1} L{cx},{cy - ry - 9} L{cx + 14},{cy - ry + 1} Z", paint, LW_DETAIL),
                _path(f"M{cx - 14},{cy + ry - 1} L{cx},{cy + ry + 9} L{cx + 14},{cy + ry - 1} Z", paint, LW_DETAIL)]  # fmt: skip
    if kind == "griddle":
        for i in range(-5, 6):
            x = cx + i * rx * 0.15
            dy = ry * 0.84 * (max(0.0, 1 - ((x - cx) / (rx * 0.86)) ** 2)) ** 0.5
            out.append(
                _line(
                    f"M{x:.1f},{cy + 3 - dy:.1f} L{x:.1f},{cy + 3 + dy:.1f}",
                    3,
                    stroke=_tint(surface, 0.3),
                )
            )
    out.append(
        _highlight(
            f"M{cx - rx * 0.6:.1f},{cy - ry * 0.35:.1f} Q{cx - rx * 0.3:.1f},{cy - ry * 0.65:.1f} {cx:.1f},{cy - ry * 0.68:.1f}",
            4,
            0.35,
        )
    )
    return out


def casserole(
    paint: str, fill: Fill, label: str | None, form: str = "round", material: str = "cast iron"
) -> list[str]:
    """A lidded casserole from the side with two loop handles; an oval one is longer and
    lower. A glass dish is clear: the fill shows faintly, and the inside shows through."""
    oval = form == "oval"
    w, h = (290.0, 112.0) if oval else (226.0, 132.0)
    cx, base = 200.0, 320.0
    top = base - h
    glass = material == "glass"
    body = f"M{cx - w / 2:.1f},{top:.1f} L{cx - w / 2 + 4:.1f},{base - 18:.1f} Q{cx - w / 2 + 8:.1f},{base:.1f} {cx - w / 2 + 30:.1f},{base:.1f} L{cx + w / 2 - 30:.1f},{base:.1f} Q{cx + w / 2 - 8:.1f},{base:.1f} {cx + w / 2 - 4:.1f},{base - 18:.1f} L{cx + w / 2:.1f},{top:.1f} Z"
    op = ' fill-opacity=".45"' if glass else ""
    out = [_shadow(cx, base + 6, w * 0.55)]
    for side in (-1, 1):
        x = cx + side * w / 2
        out.append(
            _path(
                f"M{x:.1f},{top + 18:.1f} Q{x + side * 34:.1f},{top + 24:.1f} {x:.1f},{top + 50:.1f}",
                "none",
                7,
                stroke=INK,
            )
        )
        out.append(
            _path(
                f"M{x:.1f},{top + 18:.1f} Q{x + side * 34:.1f},{top + 24:.1f} {x:.1f},{top + 50:.1f}",
                "none",
                4,
                stroke=_tint(fill.base, 0.2) if not glass else GLASS,
            )
        )
    out.append(_path(body, paint, LW, op))
    if glass:
        out.append(
            _line(
                f"M{cx - w / 2 + 14:.1f},{base - 40:.1f} Q{cx:.1f},{base - 22:.1f} {cx + w / 2 - 14:.1f},{base - 40:.1f}",
                1.6,
                ' stroke-opacity=".5"',
            )
        )
    else:
        out.append(
            _path(
                f"M{cx - w / 2 + 2:.1f},{top + 26:.1f} L{cx + w / 2 - 2:.1f},{top + 26:.1f}",
                "none",
                1.4,
                ' stroke-opacity=".45"',
            )
        )
    out.append(_ell(cx, top, w / 2 + 6, 13, paint, LW, op))
    out.append(
        _path(
            f"M{cx - w / 2 + 2:.1f},{top - 4:.1f} Q{cx:.1f},{top - (52 if not oval else 44):.1f} {cx + w / 2 - 2:.1f},{top - 4:.1f} Z",
            paint,
            LW,
            op,
        )
    )
    out.append(
        _rect(
            cx - 22,
            top - (44 if not oval else 37) - 14,
            44,
            16,
            STEEL if not glass else GLASS,
            6,
            LW_DETAIL,
        )
    )
    out.append(
        _highlight(
            f"M{cx - w * 0.36:.1f},{top + 40:.1f} L{cx - w * 0.36:.1f},{base - 30:.1f}", 6, 0.35
        )
    )
    return out


# --------------------------------------------------------------------------
# Bins and storage
# --------------------------------------------------------------------------

#: Lid tab colors of a recycling bin's compartments, left to right.
RECYCLE_TABS = ("#3f8f4a", "#3f6fb5", "#c8312e", "#d4a32a")


def kitchen_bin(
    paint: str, fill: Fill, label: str | None, kind: str = "pedal", compartments: str = "1"
) -> list[str]:
    """A tall bin with a lid. A pedal bin has a foot pedal, a touch-top bin a button on the
    lid, a sensor bin a dark sensor window, a recycling bin one lid per compartment, each
    with its colored tab (``class="lid-segment"``)."""
    x0, x1, top, base = 118.0, 282.0, 112.0, 352.0
    recycling = kind == "recycling"
    n = _n(compartments, 2) if recycling else 1
    if recycling:
        x0, x1 = 200 - 52 * n - 30, 200 + 52 * n + 30
    out = [
        _shadow(200, base + 4, (x1 - x0) * 0.6),
        _path(
            f"M{x0},{top} L{x0 + 6},{base - 8} Q{x0 + 6},{base} {x0 + 14},{base} L{x1 - 14},{base} Q{x1 - 6},{base} {x1 - 6},{base - 8} L{x1},{top} Z",
            paint,
        ),  # fmt: skip
        _highlight(f"M{x0 + 22},{top + 24} L{x0 + 26},{base - 26}", 7, 0.3),
    ]
    if kind == "pedal":
        out += [
            _path(
                f"M{184},{base - 6} L{216},{base - 6} L{224},{base + 14} L{176},{base + 14} Z",
                BLACK,
                LW_DETAIL,
            )
        ]
    if recycling:
        seg = (x1 - x0 + 8) / n
        for i in range(n):
            a = x0 - 4 + i * seg
            out.append(_group("lid-segment", [
                _path(f"M{a + 2:.1f},{top} L{a + 6:.1f},{top - 20} L{a + seg - 6:.1f},{top - 20} L{a + seg - 2:.1f},{top} Z", _shade(fill.base, 0.12)),
                _rect(a + seg / 2 - 16, top - 30, 32, 10, RECYCLE_TABS[i % len(RECYCLE_TABS)], 3, LW_DETAIL)]))  # fmt: skip
            if i:
                out.append(
                    _line(f"M{a:.1f},{top} L{a + 2:.1f},{base - 4}", 1.6, ' stroke-opacity=".6"')
                )
        return out
    out.append(
        _path(
            f"M{x0 - 4},{top + 2} Q{x0 - 2},{top - 34} 200,{top - 38} Q{x1 + 2},{top - 34} {x1 + 4},{top + 2} Z",
            _shade(fill.base, 0.1),
        )
    )
    if kind == "touch-top":
        out += [
            _ell(200, top - 22, 26, 9, _tint(fill.base, 0.3), LW_DETAIL),
            _ell(200, top - 23, 14, 5, STEEL_DARK, LW_DETAIL),
        ]
    elif kind == "sensor":
        out += [
            _rect(170, top - 22, 60, 14, BLACK, 7, LW_DETAIL),
            f'<circle cx="214" cy="{top - 15}" r="2.5" fill="#7fe0a0"/>',
        ]
    return out


def storage_box(paint: str, fill: Fill, label: str | None, form: str = "box", lid: str = "yes",
                clear: str = "no", material: str = "plastic") -> list[str]:  # fmt: skip
    """A box in three-quarter view. ``form`` sets its proportions (a low ``underbed`` box on
    wheels, a slatted ``crate``, a ``round`` basket); a lid sits on top as its own slab, else
    the open top shows the inside. A ``clear`` body is see-through with folded things inside;
    a woven material draws a weave, and fabric or felt loop handles."""
    w, h, d = {"underbed": (300, 74, 40), "crate": (220, 130, 50)}.get(form, (230, 170, 52))
    x0, base = 200 - w / 2 - d / 4, 330
    y0 = base - h
    clr = clear == "yes"
    op = ' fill-opacity=".38"' if clr else ""
    if form == "round":
        out = [
            _shadow(200, base + 4, 140),
            _path(f"M80,{y0} L92,{base - 8} Q200,{base + 30} 308,{base - 8} L320,{y0} Z", paint),
        ]
        out += _weave(84, y0 + 16, 316, base - 4) if material in WOVEN else []
        out += [
            _ell(200, y0, 120, 26, _shade(fill.base, 0.3)),
            _ell(200, y0 + 3, 104, 19, _shade(fill.base, 0.5), LW_DETAIL),
        ]
        out += [
            _rect(70, y0 + 18, 26, 10, _tint(fill.base, 0.2), 4, LW_DETAIL),
            _rect(304, y0 + 18, 26, 10, _tint(fill.base, 0.2), 4, LW_DETAIL),
        ]
        return out
    fx0, fx1, top = x0, x0 + w, y0
    back = [(fx0 + d, top - d * 0.55), (fx1 + d, top - d * 0.55)]
    out = [_shadow(200, base + 6, w * 0.6)]
    if clr:  # the far walls and what is inside, seen through the front
        out += [_rect(fx0 + 30, base - h * 0.62, w * 0.36, h * 0.5, _tint(fill.base, 0.1) if fill.base != "#e3eef0" else "#c9a46a", 3, LW_DETAIL),
                _rect(fx0 + 34 + w * 0.38, base - h * 0.48, w * 0.4, h * 0.36, "#9bb0c8", 3, LW_DETAIL)]  # fmt: skip
    out.append(
        _path(
            f"M{fx1},{top} L{back[1][0]},{back[1][1]} L{back[1][0]},{base - d * 0.55} L{fx1},{base} Z",
            _shade(fill.base, 0.22),
            LW,
            op,
        )
    )
    out.append(_path(f"M{fx0},{top} L{fx1},{top} L{fx1},{base} L{fx0},{base} Z", paint, LW, op))
    if form == "crate":
        for i in range(1, 4):
            y = top + i * h / 4
            out.append(_line(f"M{fx0},{y:.1f} L{fx1},{y:.1f} L{back[1][0]},{y - d * 0.55:.1f}", 2))
        out.append(_rect(200 - d / 4 - 26, top + 12, 52, 16, _shade(fill.base, 0.5), 8, LW_DETAIL))
    elif material in WOVEN:
        out += _weave(fx0, top + 4, fx1, base - 2)
    elif material in ("fabric", "felt"):
        out += [_line(f"M{fx0 + 8},{top + 8} L{fx1 - 8},{top + 8} L{fx1 - 8},{base - 8} L{fx0 + 8},{base - 8} Z", 1.2, ' stroke-dasharray="5 4"'),
                _rect(200 - d / 4 - 24, top + 22, 48, 12, _shade(fill.base, 0.35), 6, LW_DETAIL)]  # fmt: skip
    if form == "underbed":
        out += [
            _ell(fx0 + 30, base + 8, 10, 10, BLACK, LW_DETAIL),
            _ell(fx1 - 30, base + 8, 10, 10, BLACK, LW_DETAIL),
        ]
    if lid == "yes":
        lip = 12
        out.append(
            _path(
                f"M{fx0 - 6},{top} L{fx0 - 6 + d},{top - d * 0.55} L{fx1 + 6 + d},{top - d * 0.55} L{fx1 + 6},{top} Z",
                _tint(fill.base, 0.2),
                LW,
                op,
            )
        )
        out.append(
            _path(
                f"M{fx0 - 6},{top} L{fx1 + 6},{top} L{fx1 + 6},{top + lip} L{fx0 - 6},{top + lip} Z",
                _shade(fill.base, 0.1),
                LW,
                op,
            )
        )
        if material == "plastic":
            out += [
                _rect(fx0 + 14, top + 4, 18, 22, _shade(fill.base, 0.3), 3, LW_DETAIL),
                _rect(fx1 - 32, top + 4, 18, 22, _shade(fill.base, 0.3), 3, LW_DETAIL),
            ]
    else:
        out.append(
            _path(
                f"M{fx0},{top} L{fx0 + d},{top - d * 0.55} L{fx1 + d},{top - d * 0.55} L{fx1},{top} Z",
                _shade(fill.base, 0.45),
            )
        )
    if clr:
        out.append(_highlight(f"M{fx0 + 14},{top + 24} L{fx0 + 14},{base - 14}", 5, 0.6))
    return out


# --------------------------------------------------------------------------
# Laundry and cleaning
# --------------------------------------------------------------------------


def laundry_basket(
    paint: str, fill: Fill, label: str | None, kind: str = "basket", material: str = "plastic"
) -> list[str]:
    """A ``basket`` is an open oval tub with hand holes and air holes; a ``hamper`` is tall
    with a lid; a ``folding`` one is soft fabric on a wire rim; a ``two-compartment``
    hamper shows two openings (``class="compartment"``) on one frame."""
    woven = material in WOVEN
    if kind == "basket":
        out = [_shadow(200, 324, 160), _path("M50,170 L82,312 Q200,332 318,312 L350,170 Z", paint)]
        if woven:
            out += _weave(70, 186, 330, 306)
        else:
            out += [f'<circle cx="{x}" cy="{y}" r="5" fill="{_shade(fill.base, 0.45)}" stroke="{INK}" stroke-width="1"/>'
                    for y in (220, 252, 284) for x in range(100, 310, 26)]  # fmt: skip
        out += [
            _ell(200, 170, 150, 34, _shade(fill.base, 0.35)),
            _rect(64, 180, 40, 14, _shade(fill.base, 0.5), 7, LW_DETAIL),
            _rect(296, 180, 40, 14, _shade(fill.base, 0.5), 7, LW_DETAIL),
        ]
        return out
    if kind == "two-compartment":
        out = [_shadow(200, 352, 170), _path("M50,140 L60,346 L340,346 L350,140 Z", paint)]
        out += (
            _weave(56, 150, 344, 342)
            if woven
            else [_line("M66,150 L72,336 L328,336 L334,150", 1.2, ' stroke-dasharray="5 4"')]
        )
        out.append(_line("M200,140 L200,346", LW))
        for x in (125, 275):
            out.append(
                _group(
                    "compartment",
                    [
                        _ell(x, 140, 73, 16, _shade(fill.base, 0.45)),
                        _rect(x - 20, 112, 40, 14, _tint(fill.base, 0.25), 6, LW_DETAIL),
                    ],
                )
            )
        return out
    if kind == "folding":
        out = [_shadow(200, 344, 140), _path("M78,120 Q90,230 96,334 L304,334 Q310,230 322,120 Q260,138 200,124 Q140,138 78,120 Z", paint),
               _line("M110,180 Q200,196 290,180 M104,256 Q200,272 296,256", 1.4, ' stroke-opacity=".45"'),
               _line("M78,120 Q140,138 200,124 Q260,138 322,120", 4, stroke=STEEL_DARK),
               _line("M150,128 Q160,84 186,92 M214,92 Q240,84 250,128", 6, stroke=_shade(fill.base, 0.4))]  # fmt: skip
        return out
    # hamper
    out = [_shadow(200, 352, 120), _path("M104,110 L118,346 L282,346 L296,110 Z", paint)]
    out += (
        _weave(110, 120, 290, 342)
        if woven
        else [_line("M116,124 L128,334 M284,124 L272,334", 1.2, ' stroke-dasharray="5 4"')]
    )
    out += [_path("M96,112 Q200,70 304,112 L304,124 Q200,92 96,124 Z", _shade(fill.base, 0.15)),
            _rect(184, 74, 32, 12, _shade(fill.base, 0.45), 6, LW_DETAIL),
            _rect(96, 170, 14, 34, _shade(fill.base, 0.45), 6, LW_DETAIL), _rect(290, 170, 14, 34, _shade(fill.base, 0.45), 6, LW_DETAIL)]  # fmt: skip
    return out


def mop(paint: str, fill: Fill, label: str | None, kind: str = "spin") -> list[str]:
    """A ``spin`` mop stands in its round bucket with a spinner basket; a ``flat`` mop has a
    rectangular pad; a ``sponge`` mop a sponge roller and lever; a ``bucket`` is a wheeled
    janitorial bucket with a wringer."""
    if kind == "bucket":
        return [_shadow(200, 352, 150), _path("M70,190 L90,330 L310,330 L330,190 Z", paint),
                _line("M84,232 L316,232", 1.4, ' stroke-opacity=".5"'),
                *[_ell(x, 342, 12, 12, BLACK, LW_DETAIL) for x in (104, 296)],
                _path("M220,100 L310,100 L320,196 L210,196 Z", _shade(fill.base, 0.35)),
                _line("M232,120 L300,120 M230,140 L302,140 M228,160 L304,160", 1.6),
                _line("M300,100 L344,40", 9, stroke=BLACK),
                _path("M70,190 Q200,150 330,190", "none", 4, stroke=STEEL_DARK)]  # fmt: skip
    if kind == "flat":
        return [_shadow(200, 340, 150), _line("M268,52 L208,300", 10, stroke=paint if fill.pattern == "solid" else STEEL),
                _line("M268,52 L208,300", 2, stroke=INK), _rect(256, 40, 26, 30, BLACK, 6, LW_DETAIL),
                _path("M70,304 L330,304 L340,330 L60,330 Z", paint), _line("M70,322 L330,322", 1.2, ' stroke-dasharray="3 3"')]  # fmt: skip
    if kind == "sponge":
        return [_shadow(200, 340, 120), _line("M240,44 L200,276", 10, stroke=STEEL), _line("M240,44 L200,276", 2, stroke=INK),
                _rect(230, 34, 22, 30, BLACK, 6, LW_DETAIL), _line("M214,190 L244,120 L262,126", 5, stroke=paint),
                _path("M110,276 L290,276 L290,300 L110,300 Z", STEEL_DARK), _rect(116, 298, 168, 36, paint, 10)]  # fmt: skip
    # spin
    return [_shadow(200, 352, 140), _line("M228,40 L206,250", 9, stroke=STEEL), _line("M228,40 L206,250", 2, stroke=INK),
            _rect(218, 30, 22, 28, paint, 6, LW_DETAIL),
            _path("M80,200 L102,340 L298,340 L320,200 Z", paint), _ell(200, 200, 120, 28, _shade(fill.base, 0.35)),
            _ell(170, 214, 58, 16, STEEL, LW_DETAIL), _line("M130,214 L210,214 M140,222 L200,222", 1, ' stroke-opacity=".6"'),
            *[_line(f"M{206 + dx},{250} Q{206 + dx * 1.6},{262} {206 + dx * 2},{276}", 4, stroke="#f1ede4") for dx in range(-24, 25, 8)],
            _rect(260, 324, 40, 14, BLACK, 4, LW_DETAIL)]  # fmt: skip


def clothes_airer(
    paint: str, fill: Fill, label: str | None, kind: str = "folding", tiers: str = "1"
) -> list[str]:
    """A ``folding`` wing airer on crossed legs, a ``tower`` of ``tiers`` racks on posts and
    wheels, a ``heated`` one with its plug lead, a ``wall-mounted`` one on its wall plate.
    Each rack is a ``class="tier"`` group, so the drawing shows the row's tier count."""
    n = _n(tiers, 1)

    def rack(x0: float, x1: float, y: float, depth: float, bars: int) -> str:
        parts = [_path(f"M{x0},{y} L{x1},{y} L{x1 + depth},{y - depth * 0.5} L{x0 + depth},{y - depth * 0.5} Z", "none", 5, stroke=paint),
                 _path(f"M{x0},{y} L{x1},{y} L{x1 + depth},{y - depth * 0.5} L{x0 + depth},{y - depth * 0.5} Z", "none", 1.2, stroke=INK)]  # fmt: skip
        for i in range(1, bars):
            t = i / bars
            parts.append(
                _line(
                    f"M{x0 + depth * t:.1f},{y - depth * 0.5 * t:.1f} L{x1 + depth * t:.1f},{y - depth * 0.5 * t:.1f}",
                    2.4,
                    stroke=_shade(fill.base, 0.45),
                )
            )
        return _group("tier", parts)

    if kind == "wall-mounted":
        return [_rect(40, 80, 30, 240, "#e6e2da", 3, LW_DETAIL), rack(70, 330, 200, 0, 1).replace('class="tier"', 'class="tier" data-wall="1"'),
                *[_line(f"M70,{y} L330,{y}", 5, stroke=paint) for y in (150, 175, 200, 225)],
                *[_line(f"M70,{y} L330,{y}", 1, stroke=INK) for y in (150, 175, 200, 225)],
                _line("M70,250 L330,225 M70,130 L330,150", 3, stroke=_shade(fill.base, 0.3))]  # fmt: skip
    if kind == "tower":
        top, base = 70.0, 330.0
        out = [_shadow(200, base + 12, 140)]
        for x in (90, 290):
            out += [
                _line(f"M{x},{top} L{x},{base}", 6, stroke=paint),
                _line(f"M{x},{top} L{x},{base}", 1.2),
                _ell(x, base + 6, 9, 9, BLACK, LW_DETAIL),
            ]
        step = (base - top - 20) / n
        out += [rack(80, 290, top + 30 + i * step, 40, 6) for i in range(n)]
        return out
    # folding and heated: a wing airer seen from one end, so its gull-wing profile shows:
    # a flat middle, two wings raised on hinges, and the drying bars running back from the
    # front profile to the back one. Crossed legs hold it up; each further tier is a flat
    # rack between the legs, and the heated one is plugged in.
    dx, dy = 14.0, -40.0
    front = [(40.0, 125.0), (125.0, 200.0), (245.0, 200.0), (320.0, 125.0)]
    back = [(x + dx, y + dy) for x, y in front]
    bar = _shade(fill.base, 0.45)
    out = [_shadow(200, 344, 150)]
    for (x0, y0), (x1, y1) in (((125, 200), (245, 330)), ((245, 200), (125, 330))):
        out += [_line(f"M{x0 + dx},{y0 + dy} L{x1 + dx},{y1 + dy}", 5, stroke=_shade(fill.base, 0.2)),
                _line(f"M{x0 + dx},{y0 + dy} L{x1 + dx},{y1 + dy}", 1)]  # fmt: skip
    wing = []
    for (ax, ay), (bx, by), bars in zip(front[:-1], front[1:], (5, 6, 5), strict=True):
        for i in range(bars + 1):
            t = i / bars
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            wing.append(_line(f"M{x:.1f},{y:.1f} L{x + dx:.1f},{y + dy:.1f}", 2.4, stroke=bar))
    for prof in (back, front):
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in prof)
        wing += [_path(d, "none", 5, stroke=paint), _path(d, "none", 1.2, stroke=INK)]
    out.append(_group("tier", wing))
    for x0, y0, x1, y1 in ((125, 200, 245, 330), (245, 200, 125, 330)):
        out += [_line(f"M{x0},{y0} L{x1},{y1}", 6, stroke=paint), _line(f"M{x0},{y0} L{x1},{y1}", 1.2),
                _ell(x1, y1 + 4, 10, 5, BLACK, LW_DETAIL)]  # fmt: skip
    for i in range(1, n):
        out.append(rack(105, 265, 200 + i * 110 / n, 40, 6))
    if kind == "heated":
        out += [_line("M320,125 Q360,240 340,350", 3, stroke=BLACK), _rect(330, 346, 22, 16, "#ffffff", 3, LW_DETAIL),
                _ell(60, 143, 5, 5, "#e0533a", 1)]  # fmt: skip
    return out


SHAPES = {"saucepan": saucepan, "frying_pan": frying_pan, "casserole": casserole,
          "kitchen_bin": kitchen_bin, "storage_box": storage_box, "laundry_basket": laundry_basket,
          "mop": mop, "clothes_airer": clothes_airer}  # fmt: skip
register(SHAPES)
