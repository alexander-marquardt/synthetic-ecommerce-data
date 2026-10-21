"""A title that names a part in a color draws that part in that color (gen#447).

"Navy Bra with Red Stitching" showed a navy bra and nothing red. The text-match decoys built by
:mod:`decoy_apparel` set the named part on their drawing (:mod:`details`); the class-1 rows of the
other modules (:mod:`decoy_rows`, :mod:`mens_depth_rows`, :mod:`knitwear_rows`) did not, and three
of the trims they named ("Stitching", "Piping", "Stripes") are too fine to show at thumbnail size.

* :func:`trim_part` is the part a row names, picked from the parts its shape can show
  (:func:`details.parts_of`), so a title never names one the drawing cannot draw.
* :func:`apply` reads "with <Color> <Part>" off the title of an apparel row that carries no named
  part yet and draws it (``drawing.detail``; a shoe's laces are its ``lace`` parameter).
* :func:`violations` is the check ``test_shape_honesty.py`` runs: a title that names a part the
  drawing does not show, or a trim word too fine to draw.
"""

from __future__ import annotations

import re

import details
import leaf_shapes
from decoy_apparel import DEPARTMENTS, DETAIL_HEX, ROOTS

#: ``... with Red Collar`` / ``... with Red Waistband``: the color, then the part.
NAMED = re.compile(r"\bwith (?P<color>Red|Blue|Green|Yellow|Black|White) (?P<part>[A-Za-z]+)\b")
#: A trim too fine to read at thumbnail size: no title of a garment names one.
TOO_FINE = re.compile(r"\b(Stitching|Piping)\b")
#: Parts that come in a pair or a row, which a title words without an article.
_PLURAL = {"cuffs", "straps", "buttons", "laces", "cups", "stripes"}


def trim_part(ptype: str, shape: str, i: int) -> str:
    """The ``i``-th trim a row of ``ptype`` drawn as ``shape`` may name ("Hem", "Waistband").

    The shape is the one the row will be drawn with: a leaf rule (:mod:`leaf_shapes`) may replace
    the authored one, so a polo is asked for its ``top`` parts, not a tee's."""
    shape = leaf_shapes.shape_of(ptype, shape)
    parts = details.parts_of(shape)
    if not parts:
        raise ValueError(f"{shape!r} shows no part a decoy title can name")
    return parts[i % len(parts)].title()


def with_part(color: str, part: str) -> str:
    """"a red hem", "red cuffs": the part a description says a garment is finished with."""
    word = part.lower()
    return f"{color.lower()} {word}" if word in _PLURAL else f"a {color.lower()} {word}"


def named(title: str) -> tuple[str, str] | None:
    """The ``(color, part)`` a title names ("with Red Collar" -> ``("Red", "collar")``)."""
    m = NAMED.search(title)
    return (m["color"], m["part"].lower()) if m else None


def _apparel(tpl: dict) -> bool:
    """Clothing and footwear: the travel goods filed under a women's root (a holdall, a cabin
    case) have handles and zips, not the garment parts of :mod:`details`."""
    return (tpl["category_path"][0] in ROOTS and tpl["department"][0] in DEPARTMENTS
            and tpl["category_path"][1:3] != ["Accessories", "Travel"])


def apply(tpls: list[dict]) -> list[dict]:
    """``tpls`` with the named part of every apparel title that can show it drawn."""
    for tpl in tpls:
        got = named(tpl["title"]) if _apparel(tpl) else None
        if not got:
            continue
        drawing, hex_ = tpl["drawing"], DETAIL_HEX[got[0]]
        if got[1] == "laces" and drawing["shape"] == "shoe":
            drawing["params"] = {**(drawing.get("params") or {}), "lace": hex_}
        elif not drawing.get("detail") and got[1] in details.parts_of(drawing["shape"]):
            drawing["detail"] = {"part": got[1], "color": hex_}
    return tpls


def violations(tpls: list[dict]) -> list[str]:
    """One line per apparel template whose title names a part its drawing does not show."""
    out = []
    for tpl in tpls:
        if not _apparel(tpl):
            continue
        title, drawing = tpl["title"], tpl["drawing"]
        if TOO_FINE.search(title):
            out.append(f"{tpl['product_id']} {title!r}: a trim too fine to see at thumbnail size")
        got = named(title)
        if not got:
            continue
        color, part = got
        hex_ = DETAIL_HEX[color]
        if part == "laces":
            ok = (drawing.get("params") or {}).get("lace") == hex_
        elif part == "stripes":  # a tie's stripes are its pattern, in the named color
            ok = drawing.get("pattern") == "stripe" and drawing.get("accent") == hex_
        else:
            ok = drawing.get("detail") == {"part": part, "color": hex_}
        if not ok:
            out.append(f"{tpl['product_id']} {title!r}: {part} is not drawn in {hex_}")
    return out
