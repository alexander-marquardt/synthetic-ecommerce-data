"""Round 4 shapes for the planted distractors: belt, hanger, outfit set, trigger spray,
gift bag and zipped pouch.

Same kit conventions as :mod:`kit`: flat outlines in the kit's ink, the
product's main surface painted with the record's fill. ``hanger`` and
``outfit_set`` reuse the trouser and top drawings of :mod:`kit_garments`,
scaled into place, so a "jeans hanger" visibly holds jeans.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _panel, _path, _shade, _tint, register
from kit_garments import top, trousers

GOLD = "#d6b56a"
DENIM = "#4a6a94"


def _bezier(p0, p1, p2, p3, t: float) -> tuple[float, float]:
    u = 1 - t
    return tuple(  # type: ignore[return-value]
        u**3 * a + 3 * u * u * t * b + 3 * u * t * t * c + t**3 * d
        for a, b, c, d in zip(p0, p1, p2, p3, strict=True)
    )


def belt(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A belt laid in a shallow S: roller buckle and keeper on the left, holes and tip on the right."""
    strap = "M84,190 C164,150 252,240 326,196 L358,212 L326,230 C252,274 164,184 84,224 Z"
    centre = ((84, 207), (164, 167), (252, 257), (326, 213))
    holes = [_bezier(*centre, t) for t in (0.66, 0.72, 0.78, 0.84, 0.90)]
    return [
        _path(strap, paint),
        _line(
            "M90,197 C168,158 252,248 326,203 M90,217 C168,177 252,266 326,223",
            1.0,
            ' stroke-dasharray="4 3" stroke-opacity=".6"',
        ),
        f'<rect x="108" y="183" width="14" height="44" rx="2" fill="{_shade(fill.base, 0.2)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *[
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>'
            for x, y in holes
        ],
        f'<rect x="40" y="176" width="52" height="62" rx="12" fill="none" stroke="{GOLD}" stroke-width="10"/>',
        f'<rect x="35" y="171" width="62" height="72" rx="15" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect x="45" y="181" width="42" height="52" rx="8" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line("M66,207 L104,207", 4, stroke=GOLD),
        _line("M66,207 L104,207", 1.2),
    ]


def hanger(paint: str, fill: Fill, label: str | None, holds: str = DENIM) -> list[str]:
    """A clip hanger holding a pair of jeans by the waistband; ``paint`` is the hanger."""
    jeans = trousers(holds, Fill("solid", holds), None, fit="straight", rise="mid")
    return [
        f'<g transform="translate(90 128) scale(.55)">{"".join(jeans)}</g>',
        _line("M200,104 L200,74 C200,44 236,44 236,68 C236,82 222,86 214,80", LW + 1),
        _path(
            "M70,104 L330,104 Q338,104 338,112 L338,118 Q338,126 330,126 L70,126 Q62,126 62,118 L62,112 Q62,104 70,104 Z",
            paint,
        ),
        *[
            _path(
                f"M{x - 16},126 L{x + 16},126 L{x + 14},166 L{x - 14},166 Z",
                _shade(fill.base, 0.25),
                LW_DETAIL,
            )
            for x in (150, 250)
        ],
        *[_line(f"M{x - 10},160 L{x + 10},160", 1.2) for x in (150, 250)],
        _highlight("M80,110 L320,110", 3, 0.4),
    ]


def outfit_set(paint: str, fill: Fill, label: str | None, tee: str = "#ffffff") -> list[str]:
    """A two-piece set: a tee in ``tee`` beside jeans painted with the record's fill."""
    shirt = top(tee, Fill("solid", tee), None, neckline="crew", sleeve="short")
    legs = trousers(paint, fill, None, fit="slim", rise="mid")
    return [
        f'<g transform="translate(-12 86) scale(.6)">{"".join(shirt)}</g>',
        f'<g transform="translate(150 72) scale(.65)">{"".join(legs)}</g>',
    ]


def trigger_spray(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A trigger spray bottle of cleaner; ``label`` goes on its front panel."""
    body = "M146,368 L146,214 Q146,184 172,170 L176,150 L236,150 L240,170 Q266,184 266,214 L266,368 Q206,376 146,368 Z"
    head = "M168,150 L168,104 Q168,92 180,92 L272,92 L298,110 L272,124 L244,124 L244,150 Z"
    trigger = "M232,124 Q236,162 214,176 L206,166 Q220,152 218,124 Z"
    return [
        _path(body, paint),
        _path(head, _shade(fill.accent, 0.0)),
        _path(trigger, _shade(fill.accent, 0.15), LW_DETAIL),
        f'<rect x="296" y="102" width="12" height="16" rx="2" fill="{_shade(fill.accent, 0.3)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *_panel(160, 236, 92, 96, label, 30),
        _highlight("M158,226 Q158,196 178,184", 5, 0.5),
    ]


def gift_bag(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A paper gift bag: rope handles, a side gusset and a turned top; ``label`` goes on its tag."""
    return [
        _line("M150,140 C150,70 214,70 214,134", LW + 2, stroke=_shade(fill.accent, 0.1)),
        _line("M186,134 C186,64 250,64 250,140", LW + 2, stroke=_shade(fill.accent, 0.1)),
        _path("M270,140 L312,126 L312,346 L270,360 Z", _shade(fill.base, 0.25)),
        _path("M110,140 L270,140 L270,360 L110,360 Z", paint),
        _path("M110,140 L152,126 L312,126 L270,140 Z", _tint(fill.base, 0.3)),
        _line("M110,160 L270,160", 1.0, ' stroke-opacity=".5"'),
        _line("M214,134 L224,226", 1.0),
        *_panel(160, 226, 112, 56, label, 26, rx=10),
        _highlight("M120,172 L120,340", 4, 0.35),
    ]


def pouch(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A zipped wash or cosmetic pouch; ``label`` goes on a sewn-on patch."""
    body = "M92,176 Q92,150 118,150 L282,150 Q308,150 308,176 L318,326 Q320,352 294,352 L106,352 Q80,352 82,326 Z"
    return [
        _path(body, paint),
        _path("M104,152 L296,152 L296,174 L104,174 Z", _shade(fill.base, 0.2), LW_DETAIL),
        _line("M108,163 L292,163", 1.4, ' stroke-dasharray="3 3"'),
        f'<rect x="270" y="156" width="14" height="36" rx="4" fill="{_shade(fill.accent, 0.1)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *_panel(140, 234, 120, 64, label, 28),
        _highlight("M104,196 Q100,260 108,320", 5, 0.4),
    ]


register(
    {"belt": belt, "hanger": hanger, "outfit_set": outfit_set, "trigger_spray": trigger_spray,
     "gift_bag": gift_bag, "pouch": pouch},
)  # fmt: skip
