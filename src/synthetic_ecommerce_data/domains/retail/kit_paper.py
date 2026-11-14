"""Household paper goods for the retail drawing kit (gen#962): toilet paper, paper towels, tissues.

=================  ===========================================  ================================
shape              draws                                        params
=================  ===========================================  ================================
toilet_roll        an upright roll of toilet paper: its top     roll_size (regular, double,
                   face with the card core and the plies at     mega), ply (2-ply, 3-ply,
                   its edge, and a sheet hanging down the       4-ply), finish (quilted draws
                   front                                        quilting, recycled a leaf mark)
paper_towel_roll   a tall upright roll of paper towels: its     roll_size (regular, double,
                   perforations, closer for a half sheet, and   triple), sheet (full sheet, half
                   its top face with the card core              sheet), finish (embossed draws
                                                                dots, recycled a leaf mark)
tissue_box         a box of facial tissues in the box's color,  box (cube, flat), ply (2-ply,
                   a tissue rising from its oval opening        3-ply)
=================  ===========================================  ================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a roll's ``roll_size`` or a box's ``box`` draws what it states (gen#512). The paper
of a roll is the SKU's color (the rows' white); a tissue box is painted in its color and the
tissue is always white.
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
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The brown card core of a roll.
CARD = "#b98a5a"
#: The green of a recycled roll's leaf mark.
LEAF = "#5f8f4a"
#: The tissue rising from a box.
TISSUE = "#ffffff"

#: A roll's half width and its height by ``roll_size``: a bigger roll is wider and a little taller.
TOILET_SIZES = {"regular": (62, 120), "double": (76, 128), "mega": (92, 136)}
TOWEL_SIZES = {"regular": (54, 220), "double": (66, 232), "triple": (80, 244)}
#: How many plies each ``ply`` draws at a roll's or a tissue's edge.
PLIES = {"2-ply": 2, "3-ply": 3, "4-ply": 4}


def _leaf(cx: float, cy: float) -> list[str]:
    """A small leaf mark: the recycled roll's sign."""
    return [
        _path(f"M{cx - 14},{cy + 10} Q{cx - 12},{cy - 14} {cx + 14},{cy - 12} "
              f"Q{cx + 12},{cy + 12} {cx - 14},{cy + 10} Z", LEAF, LW_DETAIL),  # fmt: skip
        _line(f"M{cx - 12},{cy + 8} L{cx + 8},{cy - 6}", LW_DETAIL),
    ]


def _quilting(x0: float, y0: float, x1: float, y1: float) -> list[str]:
    """Quilted sheets: a lattice of short diagonal stitches over the face of the roll."""
    out = []
    for y in range(int(y0) + 14, int(y1) - 8, 22):
        for x in range(int(x0) + 12, int(x1) - 12, 22):
            out.append(_line(f"M{x},{y} L{x + 10},{y + 10} M{x + 10},{y} L{x},{y + 10}", 1.0))
    return out


def _emboss(x0: float, y0: float, x1: float, y1: float) -> list[str]:
    """Embossed sheets: a grid of raised dots."""
    return [_ell(x, y, 2.2, 2.2, _shade(PAPER, 0.12), 0)
            for y in range(int(y0) + 12, int(y1) - 6, 16)
            for x in range(int(x0) + 10, int(x1) - 6, 16)]  # fmt: skip


def _top(cx: float, cy: float, rx: float, plies: int, paint: str) -> list[str]:
    """A roll's top face: the paper, the plies as rings at its edge and the card core."""
    out = [_ell(cx, cy, rx, rx * 0.32, paint)]
    out += [_ell(cx, cy, rx - 4 * i, (rx - 4 * i) * 0.32, "none", 1.0) for i in range(1, plies)]
    out += [
        _ell(cx, cy, 20, 7, CARD, LW_DETAIL),
        _ell(cx, cy, 15, 5, _shade(CARD, 0.45), LW_DETAIL),
    ]
    return out


def toilet_roll(paint: str, fill: Fill, label: str | None, roll_size: str = "regular",
                ply: str = "2-ply", finish: str = "ultra soft") -> list[str]:  # fmt: skip
    """An upright roll of toilet paper with a sheet hanging down its front."""
    half, height = TOILET_SIZES[roll_size]
    cx, top = 200, 200 - height // 2 - 10
    x0, x1, bottom = cx - half, cx + half, top + height
    out = [
        _path(f"M{x0},{top} L{x0},{bottom} A{half},{half * 0.32} 0 0 0 {x1},{bottom} "
              f"L{x1},{top} Z", paint),  # fmt: skip
        _line(f"M{x1 - 14},{top + 8} L{x1 - 14},{bottom + 2}", LW_DETAIL),
    ]
    if finish == "quilted":
        out += _quilting(x0, top, x1, bottom)
    out.append(_path(f"M{cx - 30},{bottom + 8} L{cx - 30},{bottom + 66} L{cx + 30},{bottom + 66} "
                     f"L{cx + 30},{bottom + 12}", paint))  # fmt: skip
    tear = ' stroke-dasharray="4 4"'
    out.append(_line(f"M{cx - 30},{bottom + 40} L{cx + 30},{bottom + 40}", 1.0, tear))
    if finish == "recycled":
        out += _leaf(cx, top + height // 2 + 4)
    out += _top(cx, top, half, PLIES[ply], paint)
    out.append(_highlight(f"M{x0 + 12},{top + 14} L{x0 + 12},{bottom - 6}", 5, 0.5))
    return _label(out, label)


def paper_towel_roll(paint: str, fill: Fill, label: str | None, roll_size: str = "regular",
                     sheet: str = "full sheet",
                     finish: str = "extra absorbent") -> list[str]:  # fmt: skip
    """A tall upright roll of paper towels: perforations down its face and the core at its top."""
    half, height = TOWEL_SIZES[roll_size]
    cx, top = 200, 200 - height // 2
    x0, x1, bottom = cx - half, cx + half, top + height
    out = [
        _path(f"M{x0},{top} L{x0},{bottom} A{half},{half * 0.32} 0 0 0 {x1},{bottom} "
              f"L{x1},{top} Z", paint),  # fmt: skip
    ]
    if finish == "embossed":
        out += _emboss(x0, top + 10, x1, bottom)
    step = 28 if sheet == "half sheet" else 56
    out += [_line(f"M{x0},{y} Q{cx},{y + half * 0.32} {x1},{y}", 1.0, ' stroke-dasharray="5 4"')
            for y in range(top + step, bottom - 8, step)]  # fmt: skip
    if finish == "recycled":
        out += _leaf(cx, top + height // 2)
    out += _top(cx, top, half, 1, paint)
    out.append(_highlight(f"M{x0 + 10},{top + 16} L{x0 + 10},{bottom - 8}", 5, 0.5))
    return _label(out, label)


def tissue_box(paint: str, fill: Fill, label: str | None, box: str = "cube",
               ply: str = "2-ply") -> list[str]:  # fmt: skip
    """A box of tissues in the box's color: its front and top, the oval opening and a tissue."""
    if box == "cube":
        x0, x1, y0, y1, depth = 132, 268, 168, 328, 34
    else:
        x0, x1, y0, y1, depth = 76, 324, 214, 312, 40
    cx = (x0 + x1) / 2
    out = [
        _path(f"M{x0},{y0} L{x0 + depth},{y0 - depth} L{x1 + depth},{y0 - depth} L{x1},{y0} Z",
              _shade(fill.base, 0.12) if fill.pattern == "solid" else paint),
        _path(f"M{x1},{y0} L{x1 + depth},{y0 - depth} L{x1 + depth},{y1 - depth} L{x1},{y1} Z",
              _shade(fill.base, 0.28) if fill.pattern == "solid" else paint),
        _rect(x0, y0, x1 - x0, y1 - y0, paint, 2),
        _ell(cx + depth / 2, y0 - depth / 2, (x1 - x0) * 0.28, depth * 0.3, _shade(fill.base, 0.5),
             LW_DETAIL),
    ]
    plies = PLIES[ply]
    tip = y0 - depth / 2 - 70
    for i in range(plies - 1, -1, -1):
        dx = 6 * i
        out.append(_path(
            f"M{cx + depth / 2 - 30 + dx},{y0 - depth / 2} Q{cx - 10 + dx},{tip + 30} "
            f"{cx + depth / 2 - 6 + dx},{tip} Q{cx + depth / 2 + 24 + dx},{tip + 26} "
            f"{cx + depth / 2 + 30 + dx},{y0 - depth / 2} Z", TISSUE, LW_DETAIL))
    out.append(_highlight(f"M{x0 + 12},{y0 + 14} L{x0 + 12},{y1 - 14}", 5, 0.45))
    return _label(out, label)


SHAPES = {
    "toilet_roll": toilet_roll,
    "paper_towel_roll": paper_towel_roll,
    "tissue_box": tissue_box,
}
register(SHAPES)
