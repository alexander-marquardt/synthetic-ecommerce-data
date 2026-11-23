"""Books for the retail drawing kit (gen#1119): a book seen from the front, a little turned.

==========  ===================================================  ==============================
shape       draws                                                params
==========  ===================================================  ==============================
book_cover  a hardback-shaped book: the page block behind, the   layout (0 to 5), genre
            spine in a darker shade, the front cover in the      (cookery, craft, gardening,
            title's cover color with its layout and its genre's  diy, pets, childrens, fiction,
            emblem, and two bars where the title and author      travel)
            are printed
==========  ===================================================  ==============================

A layout is how the cover is laid out: ``0`` a band across the top, ``1`` a band across the
foot, ``2`` an inset frame, ``3`` a diagonal sash, ``4`` a rule above and below the emblem, ``5``
a round medallion behind it. With the ten cover colors of :mod:`books_rows` that is 60 covers,
one per title of a leaf, so no two titles of a leaf share a picture. The drawings are original
and drawn by code (ruling 2026-11-02, gen#102).
"""

# ruff: noqa: E501 -- SVG paths read better whole than wrapped (prototype only).

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
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The cover's box: left, top, width and height.
X, Y, W, H = 122.0, 54.0, 176.0, 292.0
#: The emblem's center.
CX, CY = X + W / 2, 196.0


def _layout(layout: str, ink: str) -> list[str]:
    """The cover's layout, drawn in ``ink`` (a tint or a shade of the cover)."""
    if layout == "1":
        return [_rect(X, Y + H - 78, W, 42, ink, 0, LW_DETAIL)]
    if layout == "2":
        return [_rect(X + 14, Y + 14, W - 28, H - 28, "none", 4, LW_DETAIL),
                _rect(X + 20, Y + 20, W - 40, H - 40, "none", 2, LW_DETAIL)]  # fmt: skip
    if layout == "3":
        return [
            _path(
                f"M{X},{Y + 150} L{X + W},{Y + 60} L{X + W},{Y + 104} L{X},{Y + 194} Z",
                ink,
                LW_DETAIL,
            )
        ]
    if layout == "4":
        return [_line(f"M{X + 24},{CY - 58} L{X + W - 24},{CY - 58}", 4),
                _line(f"M{X + 24},{CY + 58} L{X + W - 24},{CY + 58}", 4)]  # fmt: skip
    if layout == "5":
        return [_ell(CX, CY, 58, 58, ink, LW_DETAIL)]
    return [_rect(X, Y + 30, W, 42, ink, 0, LW_DETAIL)]


def _emblem(genre: str, ink: str) -> list[str]:
    """The genre's emblem at the cover's center: a whisk, a needle and thread, a leaf, a hammer,
    a paw, a star, a quill or a compass."""
    x, y = CX, CY
    if genre == "craft":
        return [_line(f"M{x - 30},{y + 34} L{x + 30},{y - 34}", 5, stroke=ink),
                _ell(x + 24, y - 27, 4, 7, PAPER, LW_DETAIL),
                _line(f"M{x + 24},{y - 27} Q{x + 44},{y} {x + 8},{y + 10} Q{x - 30},{y + 20} {x - 12},{y + 40}", 3, stroke=ink)]  # fmt: skip
    if genre == "gardening":
        return [_path(f"M{x - 34},{y + 34} Q{x - 34},{y - 30} {x + 34},{y - 34} Q{x + 30},{y + 30} {x - 34},{y + 34} Z", ink, LW_DETAIL),
                _line(f"M{x - 34},{y + 34} L{x + 18},{y - 18}", LW_DETAIL)]  # fmt: skip
    if genre == "diy":
        return [_rect(x - 6, y - 16, 12, 56, ink, 3, LW_DETAIL),
                _rect(x - 30, y - 36, 60, 22, ink, 4, LW_DETAIL)]  # fmt: skip
    if genre == "pets":
        out = [_ell(x, y + 14, 20, 16, ink, LW_DETAIL)]
        for dx, dy in ((-24, -12), (-9, -26), (9, -26), (24, -12)):
            out.append(_ell(x + dx, y + dy, 7, 9, ink, LW_DETAIL))
        return out
    if genre == "childrens":
        pts = " ".join(f"{x + dx},{y + dy}" for dx, dy in ((0, -38), (11, -12), (38, -12), (16, 5), (24, 32),
                                                          (0, 16), (-24, 32), (-16, 5), (-38, -12), (-11, -12)))  # fmt: skip
        return [_path(f"M{pts} Z", ink, LW_DETAIL)]
    if genre == "fiction":
        return [_path(f"M{x + 30},{y - 38} Q{x - 10},{y - 20} {x - 22},{y + 30} Q{x + 10},{y + 4} {x + 30},{y - 38} Z", ink, LW_DETAIL),
                _line(f"M{x - 22},{y + 30} L{x - 30},{y + 42}", 3, stroke=ink)]  # fmt: skip
    if genre == "travel":
        return [_ell(x, y, 34, 34, "none", 3),
                _path(f"M{x},{y - 30} L{x + 8},{y} L{x},{y + 30} L{x - 8},{y} Z", ink, LW_DETAIL)]  # fmt: skip
    return [_line(f"M{x},{y + 40} L{x},{y + 4}", 5, stroke=ink),
            _path(f"M{x},{y + 6} Q{x - 24},{y - 20} {x},{y - 40} Q{x + 24},{y - 20} {x},{y + 6} Z", "none", 3),
            _line(f"M{x - 10},{y - 14} Q{x},{y - 4} {x + 10},{y - 14}", LW_DETAIL)]  # fmt: skip


def book_cover(
    paint: str, fill: Fill, label: str | None, layout: str = "0", genre: str = "cookery"
) -> list[str]:
    """A book: its page block, its spine and its front cover with the layout, the genre's emblem
    and the title and author bars."""
    out = [
        _path(
            f"M{X + 8},{Y + 8} L{X + W + 10},{Y + 8} L{X + W + 10},{Y + H + 8} L{X + 8},{Y + H + 8} Z",
            PAPER,
        ),
        _rect(X - 26, Y, 28, H, _shade(fill.base, 0.3), 3),
        _rect(X, Y, W, H, paint, 4),
    ]
    out += [_line(f"M{X + W + 4},{Y + 14 + 6 * k} L{X + W + 4},{Y + H - 6}", 0.8) for k in range(2)]
    out += _layout(layout, _tint(fill.base, 0.45))
    out += _emblem(genre, _tint(fill.base, 0.7))
    out += [_rect(X + 34, Y + H - 66, W - 68, 12, PAPER, 3, LW_DETAIL),
            _rect(X + 54, Y + H - 46, W - 108, 9, PAPER, 3, LW_DETAIL)]  # fmt: skip
    out.append(_highlight(f"M{X - 18},{Y + 12} L{X - 18},{Y + H - 12}", 4, 0.35))
    return _label(out, label)


SHAPES = {"book_cover": book_cover}
register(SHAPES)
