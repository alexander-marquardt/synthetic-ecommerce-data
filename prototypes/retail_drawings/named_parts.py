"""A title that names a part in a color draws that part in that color (gen#447).

"Navy Bra with Red Stitching" showed a navy bra and nothing red. The text-match decoys built by
:mod:`decoy_apparel` set the named part on their drawing (:mod:`details`); the class-1 rows of the
other modules (:mod:`decoy_rows`, :mod:`mens_depth_rows`, :mod:`knitwear_rows`) did not, and three
of the trims they named ("Stitching", "Piping", "Stripes") are too fine to show at thumbnail size.

* :func:`trim_part` is the part a row names, picked from the parts its shape can show
  (:func:`details.parts_of`), so a title never names one the drawing cannot draw.
* :func:`apply` reads "with <Color> <Part>" off the title of a clothing, footwear or underwear row
  that carries no named part yet and sets ``drawing.detail``; a part the shape cannot show leaves
  it unset, which ``test_shape_honesty.py`` reports.
"""

from __future__ import annotations

import re

import details
from decoy_apparel import DETAIL_HEX

#: ``... with Red Collar`` / ``... with Red Waistband``: the color, then the part.
NAMED = re.compile(r"\bwith (?P<color>Red|Blue|Green|Yellow|Black|White) (?P<part>[A-Za-z]+)\b")
#: The shapes of the families the rule covers (a part of a sofa or a mower is another matter).
CLOTHING_ROOTS = ("Mens", "Womens", "Kids")
#: A polo's drawing is ``top`` (:mod:`leaf_shapes`); the rows that name its trim read ``tshirt``.
_SHAPE_OF = {"tshirt": "top"}


def trim_part(shape: str, i: int) -> str:
    """The ``i``-th trim a row of ``shape`` may name, as a title words it ("Hem", "Waistband")."""
    parts = details.parts_of(_SHAPE_OF.get(shape, shape))
    if not parts:
        raise ValueError(f"{shape!r} shows no part a decoy title can name")
    return parts[i % len(parts)].title()


def named(title: str) -> tuple[str, str] | None:
    """The ``(color, part)`` a title names ("with Red Collar" -> ``("Red", "collar")``)."""
    m = NAMED.search(title)
    return (m["color"], m["part"].lower()) if m else None


def apply(tpls: list[dict]) -> list[dict]:
    """``tpls`` with the named part of every clothing title that can show it drawn."""
    for tpl in tpls:
        drawing = tpl["drawing"]
        if drawing.get("detail") or tpl["category_path"][0] not in CLOTHING_ROOTS:
            continue
        got = named(tpl["title"])
        if got and got[1] in details.parts_of(drawing["shape"]):
            drawing["detail"] = {"part": got[1], "color": DETAIL_HEX[got[0]]}
    return tpls


def violations(tpls: list[dict]) -> list[str]:
    """One line per clothing title that names a color and a part its drawing does not show."""
    out = []
    for tpl in tpls:
        got = named(tpl["title"])
        if not got or tpl["category_path"][0] not in CLOTHING_ROOTS:
            continue
        drawing = tpl["drawing"]
        want = {"part": got[1], "color": DETAIL_HEX[got[0]]}
        if got[1] in details.parts_of(drawing["shape"]) and drawing.get("detail") == want:
            continue
        out.append(
            f"{tpl['product_id']} {tpl['title']!r}: {drawing['shape']} shows "
            f"{details.parts_of(drawing['shape'])}, detail {drawing.get('detail')}"
        )
    return out
