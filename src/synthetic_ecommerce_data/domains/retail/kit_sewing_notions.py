"""The notions of the sewing and knitting range for the retail drawing kit (gen#1118, cut 3).

==============  =============================================  =============================
shape           draws                                          params
==============  =============================================  =============================
sewing_needles  a needle book in the SKU's color, its felt     needle_kind (sharps,
                page holding a row of steel needles: medium    embroidery, tapestry,
                needles with a round eye (sharps), the same    quilting)
                with a long eye (embroidery), fewer thick
                ones with a large eye (tapestry), or more
                short ones (quilting)
sewing_pins     a pin card with two rows of steel pins, the    head (ball head, glass head,
                heads in the SKU's color: small round heads,   flat head)
                larger round heads that shine (glass), or
                flat discs
embroidery_kit  a wooden hoop holding the fabric, its motif    kit_type (cross stitch,
                worked in the SKU's floss color: a grid of     stamped), motif (floral,
                crosses (cross stitch) or a filled satin       heart)
                stitch shape (stamped); a flower or a heart,
                and two skeins of the floss below
==============  =============================================  =============================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a needle's kind, a pin's head or a kit's motif draws what it states (gen#512).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    PAPER,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sewing_tools import STEEL, _needle
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The light wood of an embroidery hoop.
WOOD = "#d9b382"
#: The linen an embroidery kit's motif is worked on.
LINEN = "#f4efe3"

#: A needle kind's look: how many needles the page holds, their length, thickness and eye length.
KINDS = {
    "sharps": (5, 170, 5.0, 4.0),
    "embroidery": (5, 170, 5.0, 10.0),
    "tapestry": (4, 190, 8.0, 12.0),
    "quilting": (7, 110, 4.0, 3.0),
}


def sewing_needles(
    paint: str, fill: Fill, label: str | None, needle_kind: str = "sharps"
) -> list[str]:
    """A needle book in the SKU's color, open on its felt page, which holds a row of steel
    needles point down. ``needle_kind`` sets the row: five medium needles with a round eye
    (sharps), the same with a long eye (embroidery), four thick, long ones with a large eye
    (tapestry) or seven short ones (quilting)."""
    count, length, width, eye = KINDS.get(needle_kind, KINDS["sharps"])
    out = [
        _rect(60, 40, 280, 320, paint, 14),
        _rect(60, 40, 280, 56, _shade(fill.base, 0.2), 14),
        _rect(88, 112, 224, 222, PAPER, 6, LW_DETAIL),
    ]
    step = 180 / max(count - 1, 1)
    top = 126 if length > 150 else 170
    for i in range(count):
        x = 110 + step * i
        out.append(_needle(x, top, x, top + length, width, STEEL))
        out.append(_ell(x, top + 5 + eye, max(width * 0.22, 1.0), eye, PAPER, LW_DETAIL))
        out.append(_highlight(f"M{x - 1:.1f},{top + 14 + 2 * eye:.1f} L{x - 1:.1f},"
                              f"{top + length - 20:.1f}", 1.2, 0.6))  # fmt: skip
    return _label(out, label)


def sewing_pins(paint: str, fill: Fill, label: str | None, head: str = "ball head") -> list[str]:
    """A pin card holding two rows of steel pins, their heads in the SKU's color: a small round
    head (ball head), a larger round head that shines (glass head) or a flat disc (flat head).
    The card's band is printed in the same color."""
    out = [
        _rect(56, 48, 288, 304, PAPER, 10),
        _rect(56, 296, 288, 56, paint, 10),
    ]
    for row_top in (76, 182):
        for i in range(6):
            x = 92 + 43 * i
            out.append(_line(f"M{x},{row_top} L{x},{row_top + 92}", 2.6, stroke=STEEL))
            if head == "flat head":
                out.append(_ell(x, row_top, 12, 4, paint, LW_DETAIL))
            elif head == "glass head":
                out.append(_ell(x, row_top, 13, 13, paint, LW_DETAIL))
                out.append(_ell(x - 4, row_top - 4, 3.5, 3.5, "#ffffff", 0))
            else:
                out.append(_ell(x, row_top, 8, 8, paint, LW_DETAIL))
    out.append(_rect(56, 140, 288, 22, _tint(fill.base, 0.7), 2, LW_DETAIL))
    out.append(_rect(56, 246, 288, 22, _tint(fill.base, 0.7), 2, LW_DETAIL))
    return _label(out, label)


#: A motif as rows of a cross stitch chart, ``X`` a stitch.
CHARTS = {
    "heart": (
        ".XX...XX.",
        "XXXX.XXXX",
        "XXXXXXXXX",
        "XXXXXXXXX",
        ".XXXXXXX.",
        "..XXXXX..",
        "...XXX...",
        "....X....",
    ),  # fmt: skip
    "floral": (
        "...XXX...",
        "..XXXXX..",
        "XX.XXX.XX",
        "XXXX.XXXX",
        "XX.XXX.XX",
        "..XXXXX..",
        "...XXX...",
        "....X....",
        "....X....",
    ),  # fmt: skip
}


def _cross_stitch(paint: str, motif: str) -> list[str]:
    chart = CHARTS.get(motif, CHARTS["floral"])
    cell, x0, y0 = 18, 119, 172 - 9 * len(chart)
    d = []
    for r, line in enumerate(chart):
        for c, ch in enumerate(line):
            if ch == "X":
                x, y = x0 + c * cell, y0 + r * cell
                d.append(f"M{x + 3},{y + 3} L{x + cell - 3},{y + cell - 3} "
                         f"M{x + cell - 3},{y + 3} L{x + 3},{y + cell - 3}")  # fmt: skip
    return [_line(" ".join(d), 3.4, stroke=paint)]


def _stamped(paint: str, fill: Fill, motif: str) -> list[str]:
    if motif == "heart":
        shape = [
            _path(
                "M200,250 C120,196 104,148 132,120 C156,98 190,108 200,136 C210,108 244,98 "
                "268,120 C296,148 280,196 200,250 Z",
                paint,
                3.0,
            ),  # fmt: skip
        ]
        return shape + [_line(f"M{x},{126 + abs(200 - x) // 4} L{x},{214 - abs(200 - x) // 2}",
                              1.0, stroke=_tint(fill.base, 0.35))
                        for x in range(140, 264, 12)]  # fmt: skip
    out = [_line("M200,190 C196,224 204,250 200,280", 4.0, stroke=_shade(fill.base, 0.35))]
    for cx, cy in ((200, 118), (240, 150), (226, 196), (174, 196), (160, 150)):
        out.append(_ell(cx, cy, 30, 30, paint, LW_DETAIL))
    out.append(_ell(200, 160, 18, 18, _shade(fill.base, 0.3), LW_DETAIL))
    return out


def embroidery_kit(
    paint: str,
    fill: Fill,
    label: str | None,
    kit_type: str = "cross stitch",
    motif: str = "floral",
) -> list[str]:
    """An embroidery kit: a wooden hoop with its brass screw holding the linen, and the motif
    worked on it in the SKU's floss color, a grid of crosses (``cross stitch``) or a satin
    stitched shape (``stamped``); ``motif`` is a flower or a heart. Two skeins of the floss lie
    below the hoop."""
    out = [
        _rect(186, 14, 28, 26, STEEL, 3, LW_DETAIL),
        _ell(200, 180, 156, 156, WOOD),
        _ell(200, 180, 140, 140, LINEN, LW_DETAIL),
    ]
    out += (
        _cross_stitch(paint, motif) if kit_type == "cross stitch" else _stamped(paint, fill, motif)
    )
    for x in (96, 220):
        out.append(_rect(x, 330, 84, 30, paint, 12))
        out.append(_rect(x + 30, 328, 24, 34, PAPER, 3, LW_DETAIL))
    return _label(out, label)


SHAPES = {
    "sewing_needles": sewing_needles,
    "sewing_pins": sewing_pins,
    "embroidery_kit": embroidery_kit,
}
register(SHAPES)
