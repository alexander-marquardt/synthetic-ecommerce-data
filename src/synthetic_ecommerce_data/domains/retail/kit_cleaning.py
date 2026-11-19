"""Own-kind shapes for the cleaning packs, which were drawn as a tub (a yellow cup) or a plain bottle.

==============  ===============================================  ==========
shape           what it draws                                    params
==============  ===============================================  ==========
rim_block       a hanging cage clipped on a rim, a block in it   units
angled_bottle   a bottle with a bent neck, to reach under a rim  --
jug             a laundry jug: a grip hole, a cap in the accent  --
squeeze_bottle  a waisted dish-soap bottle under a flip cap      --
==============  ===============================================  ==========

``jug`` and ``squeeze_bottle`` are gen#1028's (slice 2): liquid laundry detergent and fabric
softener, and dish soap, drew the plain ``bottle``, and their tablets, wipes and beads the
cup-like ``tub``. The bottle is the fill's base, the cap its accent.

A ``units`` param of ``"2"`` (a twin pack) draws two cages side by side. Every params
value is a string, as a style row's ``params`` carry it.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    PAPER,
    Fill,
    _highlight,
    _panel,
    _path,
    _shade,
    _word,
    register,
)


def _cage(
    cx: float, top: float, paint: str, label: str | None, size: float, base: str
) -> list[str]:
    """One rim block: a wire hook over a rim, the cage under it, the block inside."""
    half = size / 2
    height = size * 1.7
    left, right, bottom = cx - half, cx + half, top + height
    out = [
        # the hook that clips over the bowl rim
        _path(
            f"M{cx - 14:g},{top + 40:g} L{cx - 14:g},{top:g} Q{cx - 14:g},{top - 22:g} {cx:g},{top - 22:g} Q{cx + 14:g},{top - 22:g} {cx + 14:g},{top:g} L{cx + 14:g},{top + 40:g}",
            "none",
        ),
        # the cage: a rounded frame, bars across it
        f'<rect x="{left:g}" y="{top + 30:g}" width="{size:g}" height="{height - 30:g}" rx="10" fill="#f4f1ea" stroke="{INK}" stroke-width="{LW}"/>',
        *(
            f'<path d="M{left + 8:g},{top + 30 + k * (height - 30) / 5:g} L{right - 8:g},{top + 30 + k * (height - 30) / 5:g}" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            for k in (1, 2, 3, 4)
        ),
        # the block, in the product's color, showing through the bars
        _path(
            f"M{left + 12:g},{top + 52:g} L{right - 12:g},{top + 52:g} L{right - 12:g},{bottom - 14:g} L{left + 12:g},{bottom - 14:g} Z",
            paint,
        ),
    ]
    if label:
        out.append(_word(label, cx, top + 30 + (height - 30) / 2, size - 28, 26, "#ffffff"))
    out.append(_highlight(f"M{left + 20:g},{top + 62:g} L{left + 20:g},{bottom - 24:g}", 4, 0.4))
    return out


def rim_block(paint: str, fill: Fill, label: str | None, units: str = "1") -> list[str]:
    if int(units) == 2:
        return [
            *_cage(112, 120, paint, label, 120, fill.base),
            *_cage(288, 120, paint, label, 120, fill.base),
        ]
    return _cage(200, 110, paint, label, 150, fill.base)


def angled_bottle(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A bottle with a neck bent to one side, so the nozzle reaches under the bowl rim."""
    body = "M120,366 L120,196 Q120,160 150,138 L206,96 Q214,60 232,48 L262,60 Q268,78 252,96 L238,126 Q282,152 282,196 L282,366 Q200,376 120,366 Z"
    return [
        _path(body, paint),
        _path("M222,40 L276,58 L268,84 L214,66 Z", _shade(fill.base, 0.35)),
        *_panel(134, 226, 134, 96, label, 44),
        _highlight("M136,206 Q136,176 160,156", 5, 0.5),
    ]


def jug(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A laundry jug: a wide body, a grip hole cut through its upper right, a ribbed cap on the
    neck at its upper left."""
    body = "M112,366 L112,172 Q112,138 142,126 L142,94 L198,94 L198,118 L264,118 Q292,122 292,152 L292,366 Q202,376 112,366 Z"
    cap = _shade(fill.accent, 0.0)
    return [
        _path(body, paint, extra=' class="jug"'),
        f'<rect class="handle" x="236" y="140" width="38" height="88" rx="17" fill="{PAPER}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect class="cap" x="134" y="58" width="72" height="38" rx="7" fill="{cap}" stroke="{INK}" stroke-width="{LW}"/>',
        _path(" ".join(f"M{x},64 L{x},90" for x in range(146, 200, 10)), "none", LW_DETAIL),
        *_panel(124, 244, 156, 98, label, 44),
        _highlight("M126,206 Q126,162 152,146", 5, 0.5),
    ]


def squeeze_bottle(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A dish-soap squeeze bottle: tall, pinched at the waist for the grip, under a flip cap
    whose spout is folded down."""
    body = "M152,366 L148,272 Q140,232 154,200 Q166,172 166,140 L176,118 L224,118 L234,140 Q234,172 246,200 Q260,232 252,272 L248,366 Q200,374 152,366 Z"
    cap = _shade(fill.accent, 0.0)
    return [
        _path(body, paint, extra=' class="bottle"'),
        f'<rect class="cap" x="172" y="82" width="56" height="38" rx="9" fill="{cap}" stroke="{INK}" stroke-width="{LW}"/>',
        _path(
            "M186,82 L190,62 L210,62 L214,82 Z",
            _shade(fill.accent, 0.2),
            LW_DETAIL,
            ' class="flip"',
        ),
        _path("M172,96 L228,96", "none", LW_DETAIL),
        *_panel(156, 250, 88, 96, label, 26),
        _highlight("M160,300 Q156,252 166,218", 5, 0.5),
    ]


register(
    {
        "rim_block": rim_block,
        "angled_bottle": angled_bottle,
        "jug": jug,
        "squeeze_bottle": squeeze_bottle,
    }
)
