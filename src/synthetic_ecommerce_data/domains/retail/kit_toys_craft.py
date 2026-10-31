"""The craft kit and ride-on shapes of the toy kit (:mod:`kit_toys`)."""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    _tint,
)
from synthetic_ecommerce_data.domains.retail.kit_toy_parts import (
    BLACK,
    RAINBOW,
    STEEL,
    WHITE,
    WOOD,
    _badge,
    _counts,
    _ell,
    _group,
    _n,
    _rect,
    _shadow,
    _star,
    _wheel,
)

# --------------------------------------------------------------------------
# Arts and crafts
# --------------------------------------------------------------------------


def _brush(x: float, y: float, turn: float, color: str) -> str:
    return _group("piece", [f'<g transform="rotate({turn:g} {x:.1f} {y:.1f})">',
                            _rect(x, y - 4, 120, 8, "#d93b30", 3, 1.2), _rect(x + 120, y - 5, 18, 10, STEEL, 1, 1.2),
                            _path(f"M{x + 138:.1f},{y - 5:.1f} Q{x + 160:.1f},{y:.1f} {x + 138:.1f},{y + 5:.1f} Z", color, 1.2), "</g>"])  # fmt: skip


def _pencil(x: float, y: float, w: float, h: float, color: str) -> str:
    return _group("piece", [_rect(x, y + w * 1.4, w, h - w * 1.4, color, 1, 1),
                            _path(f"M{x:.1f},{y + w * 1.4:.1f} L{x + w / 2:.1f},{y:.1f} L{x + w:.1f},{y + w * 1.4:.1f} Z", WOOD, 0.8),
                            _path(f"M{x + w * 0.35:.1f},{y + w * 0.5:.1f} L{x + w / 2:.1f},{y:.1f} L{x + w * 0.65:.1f},{y + w * 0.5:.1f} Z", color, 0.6)])  # fmt: skip


def craft_kit(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "painting",
    counts: str = "",
    character: str = "",
) -> list[str]:
    """An opened kit, every piece of ``counts`` drawn (``class="piece"``): a ``painting``
    tin of paint pans with brushes and a water pot; a ``bead`` tray of tubs with cords; a
    ``slime`` kit's tubs, glitter pots and cup; ``knitting`` needles, yarn and booklet; a
    ``coloring`` tin of pencils with a sharpener and a book. The kit's box is in the fill."""
    out = [_shadow(200, 352, 170)]
    if kind == "painting":
        pans, brushes, pots = (_counts(counts, (12, 2, 1)) + [0, 0])[:3]
        rows = 1 if pans <= 6 else 2
        cols = max(1, math.ceil(pans / rows))
        out += [
            _rect(34, 36, 300, 70, paint, 8),
            _rect(34, 112, 300, 140 if rows == 2 else 90, "#3a3f4a", 8),
        ]
        pw = 280 / cols
        for i in range(pans):
            x = 44 + pw * (i % cols)
            y = 124 + 62 * (i // cols)
            out.append(
                _group("piece", [_rect(x, y, pw - 8, 52, RAINBOW[i % len(RAINBOW)], 6, 1.4)])
            )
        for i in range(brushes):
            out.append(_brush(50, 290 + i * 26, -6 + i * 4, RAINBOW[i * 4 % len(RAINBOW)]))
        for _ in range(pots):
            out.append(
                _group(
                    "piece",
                    [
                        _path("M296,270 L360,270 L352,344 L304,344 Z", "#e3eef0"),
                        _path("M300,300 L356,300 L352,344 L304,344 Z", _tint("#2f8fc4", 0.5), 1.2),
                    ],
                )
            )
    elif kind == "bead":
        tubs, cords, trays = (_counts(counts, (8, 4, 1)) + [0, 0])[:3]
        if trays:
            out.append(
                _group(
                    "piece",
                    [
                        _rect(40, 60, 320, 200, paint, 12),
                        _rect(52, 72, 296, 176, _tint(fill.base, 0.5), 8, LW_DETAIL),
                    ],
                )
            )
        cols = max(1, math.ceil(tubs / 2))
        tw = 296 / cols
        for i in range(tubs):
            x, y = 52 + tw * (i % cols), 72 + 88 * (i // cols)
            c = RAINBOW[i % len(RAINBOW)]
            dots = "".join(
                f'<circle cx="{x + 12 + (k % 4) * (tw - 24) / 3:.1f}" cy="{y + 22 + (k // 4) * 18:.1f}" r="6" fill="{c}" stroke="{INK}" stroke-width=".8"/>'
                for k in range(12)
            )
            out.append(_group("piece", [_rect(x + 4, y + 6, tw - 8, 76, WHITE, 8, 1.4), dots]))
        for i in range(cords):
            out.append(
                _group(
                    "piece",
                    [
                        _path(
                            f"M{60 + i * 8:.1f},{280 + i * 16:.1f} Q{150:.1f},{262 + i * 16:.1f} {220:.1f},{290 + i * 16:.1f} T{350 - i * 6:.1f},{284 + i * 14:.1f}",
                            "none",
                            2.6,
                            stroke=RAINBOW[(i * 3 + 1) % len(RAINBOW)],
                        )
                    ],
                )
            )
    elif kind == "slime":
        tubs, glitter, cups = (_counts(counts, (6, 3, 1)) + [0, 0])[:3]
        out.append(_rect(30, 40, 340, 110, paint, 10))
        out.append(_rect(46, 56, 308, 78, _tint(fill.base, 0.6), 6, LW_DETAIL))
        cols = max(1, math.ceil(tubs / 2))
        for i in range(tubs):
            cx, cy = 66 + (i % cols) * 70, 200 + (i // cols) * 80
            c = RAINBOW[(i * 2) % len(RAINBOW)]
            out.append(_group("piece", [_path(f"M{cx - 28:.1f},{cy - 16:.1f} L{cx + 28:.1f},{cy - 16:.1f} L{cx + 24:.1f},{cy + 30:.1f} L{cx - 24:.1f},{cy + 30:.1f} Z", _tint(c, 0.3)),
                                        _rect(cx - 31, cy - 30, 62, 16, c, 4, LW_DETAIL)]))  # fmt: skip
        for i in range(glitter):
            x = 278 + i * 28
            out.append(_group("piece", [_rect(x, 180, 22, 60, "#e3eef0", 4, LW_DETAIL), _rect(x, 172, 22, 12, RAINBOW[(i * 3) % len(RAINBOW)], 2, 1.2),
                                        *(f'<circle cx="{x + 5 + (k % 3) * 6:.1f}" cy="{200 + (k // 3) * 10:.1f}" r="1.8" fill="#f2c94c"/>' for k in range(9))]))  # fmt: skip
        for _ in range(cups):
            out.append(
                _group(
                    "piece",
                    [
                        _path("M282,270 L354,270 L346,340 L290,340 Z", WHITE),
                        _line("M290,290 L346,290", 1),
                    ],
                )
            )
    elif kind == "knitting":
        needles, balls, books = (_counts(counts, (2, 3, 1)) + [0, 0])[:3]
        if books:
            out.append(_group("piece", [_rect(40, 60, 150, 200, paint, 4), _rect(56, 80, 118, 90, WHITE, 3, LW_DETAIL),
                                        _path("M80,150 Q115,90 150,150", "none", 2), _line("M60,196 L170,196 M60,212 L170,212 M60,228 L140,228", 1.2)]))  # fmt: skip
        for i in range(balls):
            cx, cy = (250, 240, 320)[i % 3] + (i // 3) * 20, (150, 280, 270)[i % 3]
            c = _tint(fill.base, 0.1 + 0.25 * i) if fill.pattern == "solid" else RAINBOW[i]
            wraps = " ".join(
                f"M{cx - 44:.1f},{cy - 30 + k * 14:.1f} Q{cx:.1f},{cy - 50 + k * 14:.1f} {cx + 44:.1f},{cy - 26 + k * 14:.1f}"
                for k in range(5)
            )
            out.append(
                _group(
                    "piece", [_ell(cx, cy, 52, 52, c), _line(wraps, 1.2, ' stroke-opacity=".55"')]
                )
            )
        for i in range(needles):
            x0, y0, x1, y1 = (190, 60, 330, 200) if i % 2 == 0 else (330, 60, 200, 210)
            out.append(
                _group(
                    "piece",
                    [
                        _line(f"M{x0},{y0} L{x1},{y1}", 6, stroke=WOOD),
                        _line(f"M{x0},{y0} L{x1},{y1}", 1),
                        _ell(x0, y0, 9, 9, "#d93b30", 1.4),
                    ],
                )
            )
    else:  # coloring
        pencils, sharpeners, books = (_counts(counts, (24, 1, 1)) + [0, 0])[:3]
        out += [
            _rect(30, 60, 340, 180, paint, 8),
            _rect(42, 72, 316, 156, _tint(fill.base, 0.7), 6, LW_DETAIL),
        ]
        pw = 300 / max(pencils, 1)
        for i in range(pencils):
            out.append(_pencil(50 + i * pw, 86, pw - 2, 130, RAINBOW[i % len(RAINBOW)]))
        for _ in range(books):
            out.append(
                _group(
                    "piece",
                    [
                        _rect(40, 262, 200, 90, WHITE, 3),
                        _star(140, 307, 30, "none", 1.6),
                        _line("M40,262 L40,352", 4),
                    ],
                )
            )
        for _ in range(sharpeners):
            out.append(
                _group(
                    "piece",
                    [_rect(280, 290, 54, 40, "#2f8fc4", 4), _ell(307, 310, 8, 8, BLACK, 1.2)],
                )
            )
    return [*out, *_badge(character)]


# --------------------------------------------------------------------------
# Ride-ons
# --------------------------------------------------------------------------


def ride_on(
    paint: str,
    fill: Fill,
    label: str | None,
    kind: str = "balance_bike",
    wheels: str = "2",
    character: str = "",
) -> list[str]:
    """A ``balance_bike`` (no pedals), a ``scooter`` (a deck and a T-bar; two wheels, or
    three with two at the front), a ``trike`` with its push handle, or a ride-on ``car``
    whose far wheels show behind its body; every wheel a ``class="wheel"`` group.
    A bike's wheel sizes are rungs of :mod:`size_ladder`, so each size is its own picture."""
    n = _n(wheels, 2)
    out = [_shadow(200, 350, 170)]
    if kind == "scooter":
        three = n >= 3
        out += [_wheel(306, 312, 28, BLACK, "#e6c46a")]
        if three:
            out += [
                _wheel(116, 306, 28, _shade(BLACK, 0.2), "#e6c46a"),
                _wheel(90, 314, 28, BLACK, "#e6c46a"),
            ]
        else:
            out += [_wheel(96, 312, 28, BLACK, "#e6c46a")]
        out += [_path("M110,292 L300,292 Q320,292 320,304 L110,304 Z", paint), _rect(118, 282, 180, 14, _shade(fill.base, 0.2), 6, LW_DETAIL),
                _path("M98,300 L112,292 L140,70 L128,68 Z", paint, LW_DETAIL), _rect(70, 58, 130, 14, "#2f2f35", 7, LW_DETAIL),
                _rect(62, 56, 28, 18, BLACK, 8, LW_DETAIL), _rect(180, 56, 28, 18, BLACK, 8, LW_DETAIL)]  # fmt: skip
        return [*out, *_badge(character, 350, 120)]
    if kind == "trike":
        out += [_line("M304,290 L330,60", 6, stroke="#2f2f35"), _path("M316,64 Q330,40 356,56", "none", 8, stroke="#2f2f35"),
                _wheel(296, 300, 38, _shade(BLACK, 0.2), STEEL, 6), _wheel(110, 290, 58, BLACK, STEEL, 8),
                _path("M120,180 L140,180 L250,280 L330,300 L330,312 L240,300 L130,200 Z", paint),
                _wheel(330, 306, 38, BLACK, STEEL, 6),
                _line("M244,214 L244,272", 8, stroke="#2f2f35"), _rect(206, 196, 76, 20, "#2f2f35", 9), _path("M206,196 Q200,150 230,150 L246,196 Z", "#2f2f35", LW_DETAIL),
                _line("M110,290 L120,170", 7, stroke=paint if fill.pattern == "solid" else "#9a9ca0"), _rect(86, 160, 72, 12, "#2f2f35", 6, LW_DETAIL),
                _rect(96, 280, 34, 10, "#2f2f35", 3, 1.2)]  # fmt: skip
        return [*out, *_badge(character)]
    if kind == "car":
        out += [_wheel(140, 300, 30, _shade(BLACK, 0.2)), _wheel(310, 300, 30, _shade(BLACK, 0.2)),
                _path("M40,290 Q40,220 100,214 L150,214 Q170,160 220,160 L260,160 Q300,160 316,214 L350,220 Q376,226 370,290 Z", paint),
                _path("M166,214 Q178,174 214,172 L214,214 Z", "#dcebef", LW_DETAIL), _rect(226, 190, 70, 24, "#2f2f35", 8, LW_DETAIL),
                _path("M190,160 L176,128", "none", 4), _ell(176, 126, 18, 7, "#2f2f35", LW_DETAIL),
                _ell(54, 252, 10, 12, "#f2c94c", LW_DETAIL), _ell(360, 256, 6, 10, "#d93b30", LW_DETAIL),
                _wheel(110, 306, 34), _wheel(286, 306, 34)]  # fmt: skip
        return [*out, *_badge(character)]
    # balance bike: two wheels, a frame, a saddle, bars; no pedals
    frame = paint if fill.pattern == "solid" else _shade(fill.base, 0.1)
    out += [_wheel(100, 290, 62, BLACK, STEEL, 10), _wheel(300, 290, 62, BLACK, STEEL, 10),
            _path("M100,290 L170,200 L270,196 L300,290", "none", 14, stroke=INK), _path("M100,290 L170,200 L270,196 L300,290", "none", 9, stroke=frame),
            _line("M270,196 L250,110", 12, stroke=INK), _line("M270,196 L250,110", 7, stroke=frame),
            _line("M170,200 L156,150", 10, stroke="#9a9ca0"), _path("M120,150 Q156,138 196,148 L190,158 Q156,154 124,160 Z", "#2f2f35", LW_DETAIL),
            _rect(214, 98, 76, 12, "#2f2f35", 6, LW_DETAIL), _rect(206, 96, 26, 16, BLACK, 7, 1.2)]  # fmt: skip
    return [*out, *_badge(character)]
