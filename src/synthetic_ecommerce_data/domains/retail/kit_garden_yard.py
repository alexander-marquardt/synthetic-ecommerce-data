"""Garden table, grill accessory and garden storage shapes for the retail drawing kit (gen#961, slice 3).

Each type of the slice has its own flat drawing in the kit's house style (the outlines in the kit's
ink, the record's fill on the product's main surface), and each param is the lower-cased value of
the attribute it draws, so a derived style that swaps a value is drawn true (gen#512).

===============  =========================================  ======================================
shape            draws                                      params
===============  =========================================  ======================================
garden_table     a top on legs with feet, and a rim along   style (bistro, dining, side, folding),
                 the front edge                             material (acacia, steel, aluminum)
grill_accessory  a set of grill tools, a brush or tongs     kind (tool set, brush, tongs, kettle,
                 with painted handles, or a cover over a    cabinet), material (stainless steel,
                 kettle or a cabinet grill                  bamboo, polyester, canvas)
garden_storage   a deck box, a storage bench, a tall        style (deck box, storage bench, tall
                 cabinet or a shed, with a lid (or roof),   cabinet, apex, pent), material (resin,
                 a handle and hinges                        wood, steel)
===============  =========================================  ======================================

A decoy title that names a part's color ("with Red Legs") passes ``part`` and ``part_color``; the
parts each shape can name are :data:`PARTS`, added to :data:`kit_garden.PARTS`, which the Garden
decoys read. Every style draws every part, so a decoy may copy any style. A drawing never prints a
size: a style's widths and capacities share one image.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    PAPER,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_garden import GREASE, _Part
from synthetic_ecommerce_data.domains.retail.kit_garden import PARTS as GARDEN_PARTS
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _ell, _label, _rect

#: shape -> the parts a decoy can name, the first being the one a short-title decoy draws in its color.
PARTS = {
    "garden_table": ("legs", "rim", "feet"),
    "grill_accessory": ("trim", "strap", "tag"),
    "garden_storage": ("lid", "handle", "hinges"),
}
GARDEN_PARTS.update(PARTS)

MATERIAL_CLASS = "material"
CX = 200
GROUND = "M20,338 L380,338"


# --------------------------------------------------------------------------
# Garden table
# --------------------------------------------------------------------------

#: style -> the top (x, y, w, h) and the legs' x positions (a pedestal is one leg at the middle).
_TABLE = {
    "bistro": ((110.0, 150.0, 180.0, 22.0), (CX,)),
    "dining": ((40.0, 150.0, 320.0, 22.0), (60.0, 330.0)),
    "side": ((130.0, 210.0, 140.0, 20.0), (142.0, 248.0)),
    "folding": ((80.0, 170.0, 240.0, 18.0), ()),
}


def _table_marks(material: str, x: float, y: float, w: float, h: float) -> str:
    """What tells one table material from another, in a ``material`` group."""
    if material == "steel":  # a perforated top
        body = "".join(_ell(x + f * w, y + h / 2, 2.5, 2.5, PAPER, 1) for f in (0.15, 0.3, 0.45, 0.6, 0.75, 0.9))
    elif material == "aluminum":  # a brushed sheen
        body = _highlight(f"M{x + 14},{y + 6} L{x + w * 0.6:.1f},{y + 6}", 4, 0.7)
    else:  # acacia: slats across the top
        body = _line(" ".join(f"M{x + f * w:.1f},{y + 2} L{x + f * w:.1f},{y + h - 2}" for f in (0.2, 0.4, 0.6, 0.8)), 1.6, ' stroke-opacity=".55"')
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def garden_table(paint: str, fill: Fill, label: str | None, style: str = "bistro", material: str = "acacia",
                 part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A garden table seen from the front: a small round ``bistro`` table on a pedestal, a long
    ``dining`` table, a low ``side`` table, or a ``folding`` table on crossed legs; each has a rim
    along the front of its top and feet on the ground, and the ``material`` adds its marks (slats,
    perforations, a brushed sheen)."""
    pt = _Part("garden_table", part, part_color)
    style, material = style.lower(), material.lower()
    (x, y, w, h), legs = _TABLE.get(style, _TABLE["bistro"])
    leg = pt.fill("legs", _shade(fill.base, 0.3))
    rim = pt.fill("rim", _shade(fill.base, 0.2))
    feet = pt.fill("feet", GREASE)
    top_y = y + h
    out = [_line(GROUND, 4)]
    if style == "folding":
        right = x + w
        out.append(pt.mark("legs", _path(f"M{x + 20},{top_y} L{x + 34},{top_y} L{right - 20},330 L{right - 34},330 Z", leg)))
        out.append(pt.mark("legs", _path(f"M{right - 34},{top_y} L{right - 20},{top_y} L{x + 34},330 L{x + 20},330 Z", leg)))
        feet_at = (x + 27, x + w - 27)
    elif style == "bistro":
        out.append(pt.mark("legs", _rect(CX - 8, top_y, 16, 316 - top_y, leg, 3)))
        feet_at = (CX,)
    else:
        for lx in legs:
            out.append(pt.mark("legs", _rect(lx - 7, top_y, 14, 322 - top_y, leg, 3)))
        feet_at = legs
    for fx in feet_at:
        wide = 46 if style == "bistro" else 12
        out.append(pt.mark("feet", _rect(fx - wide, 322, 2 * wide, 12, feet, 4)))
    if style == "bistro":
        out.append(_ell(CX, y + h / 2, w / 2, h, paint))
    else:
        out.append(_rect(x, y, w, h, paint, 4))
    out.append(pt.mark("rim", _rect(x + 6, top_y - 6, w - 12, 8, rim, 3)))
    out.append(_table_marks(material, x, y, w, h))
    return _label(out, label)


# --------------------------------------------------------------------------
# Grill accessory
# --------------------------------------------------------------------------


def _accessory_marks(material: str, x: float, y: float, w: float, h: float) -> str:
    """What tells one accessory material from another, in a ``material`` group."""
    if material == "bamboo":  # the nodes of the cane
        body = _line(" ".join(f"M{x + 2},{y + f * h:.1f} L{x + w - 2},{y + f * h:.1f}" for f in (0.3, 0.65)), 2.4, stroke=_shade(PAPER, 0.5))
    elif material == "polyester":  # a woven hatch
        body = _line(" ".join(f"M{x + i},{y + 4} L{x + i - 30},{y + 34}" for i in range(40, int(w), 40)), 1.2, ' stroke-opacity=".45"')
    elif material == "canvas":  # a stitched seam
        body = _line(f"M{x + 10},{y + h * 0.5:.1f} L{x + w - 10},{y + h * 0.5:.1f}", 1.6, ' stroke-dasharray="6 5"')
    else:  # stainless steel: a polish that shines
        body = _highlight(f"M{x + 6},{y + 10} L{x + 6},{y + h - 10}", 4, 0.75)
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def _cover(kind: str, paint: str, fill: Fill, pt: _Part) -> tuple[list[str], tuple[float, float, float, float]]:
    """A fitted cover over a round ``kettle`` grill or a wide ``cabinet`` one."""
    if kind == "kettle":
        x, y, w, h = 110.0, 120.0, 180.0, 200.0
        body = _path(f"M{x},{y + h} L{x},{y + 80} Q{CX},{y - 60} {x + w},{y + 80} L{x + w},{y + h} Z", paint)
    else:
        x, y, w, h = 60.0, 130.0, 280.0, 190.0
        body = _path(f"M{x},{y + h} L{x},{y + 40} Q{x},{y} {x + 40},{y} L{x + w - 40},{y} Q{x + w},{y} {x + w},{y + 40} L{x + w},{y + h} Z", paint)
    out = [
        body,
        pt.mark("trim", _rect(x, y + h - 18, w, 18, pt.fill("trim", _shade(fill.base, 0.3)), 2)),
        pt.mark("strap", _rect(x + 24, y + h - 70, 16, 70, pt.fill("strap", GREASE), 3)),
        pt.mark("tag", _rect(x + w - 70, y + 60, 40, 24, pt.fill("tag", PAPER), 3)),
    ]
    return out, (x, y, w, h)


def _tools(kind: str, paint: str, fill: Fill, pt: _Part) -> tuple[list[str], tuple[float, float, float, float]]:
    """A ``tool set`` (a spatula, a fork and tongs), a ``brush`` or a pair of ``tongs``, each on a
    painted handle with a grip band (the trim), a hang strap and a tag."""
    xs = (120.0, CX, 280.0) if kind == "tool set" else (CX,)
    hx, hy, hw, hh = xs[0] - 14, 220.0, 28.0, 100.0
    out: list[str] = []
    for i, cx in enumerate(xs):
        head = kind if kind != "tool set" else ("spatula", "fork", "tongs")[i]
        if head == "spatula":
            out.append(_line(f"M{cx},{hy} L{cx},120", 6, stroke=POLE))
            out.append(_rect(cx - 30, 60, 60, 64, POLE, 6))
        elif head == "fork":
            out.append(_line(f"M{cx},{hy} L{cx},120 M{cx - 14},60 L{cx - 14},120 L{cx + 14},120 L{cx + 14},60", 6, stroke=POLE))
        elif head == "brush":
            out.append(_line(f"M{cx},{hy} L{cx},150", 6, stroke=POLE))
            out.append(_rect(cx - 50, 80, 100, 70, _tint(fill.base, 0.5), 8))
            out.append(_line(" ".join(f"M{cx - 44 + i * 11},80 L{cx - 44 + i * 11},64" for i in range(9)), 2, stroke=POLE))
        else:  # tongs
            out.append(_line(f"M{cx - 6},{hy} L{cx - 26},60 M{cx + 6},{hy} L{cx + 26},60", 6, stroke=POLE))
        out.append(_rect(cx - 14, hy, 28, hh, paint, 8))
        out.append(pt.mark("trim", _rect(cx - 16, hy + 30, 32, 14, pt.fill("trim", _shade(fill.base, 0.35)), 3)))
        out.append(pt.mark("strap", _ell(cx, hy + hh + 10, 9, 9, pt.fill("strap", GREASE))))
    out.append(pt.mark("tag", _rect(xs[-1] + 18, hy + 10, 30, 20, pt.fill("tag", PAPER), 3)))
    return out, (hx, hy, hw, hh)


def grill_accessory(paint: str, fill: Fill, label: str | None, kind: str = "tool set", material: str = "stainless steel",
                    part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """A grill accessory: a ``tool set``, a ``brush`` or ``tongs`` on painted handles, or a cover
    over a ``kettle`` or a ``cabinet`` grill; each has a trim (a handle's grip band or a cover's
    hem), a strap and a tag, and the ``material`` adds its marks (a polish, cane nodes, a woven
    hatch, a stitched seam)."""
    pt = _Part("grill_accessory", part, part_color)
    kind, material = kind.lower(), material.lower()
    if kind in ("kettle", "cabinet"):
        body, box = _cover(kind, paint, fill, pt)
    else:
        body, box = _tools(kind if kind in ("brush", "tongs") else "tool set", paint, fill, pt)
    out = [_line(GROUND, 4), *body, _accessory_marks(material, *box)]
    return _label(out, label)


# --------------------------------------------------------------------------
# Garden storage
# --------------------------------------------------------------------------

#: style -> the body (x, y, w, h).
_STORE = {
    "deck box": (60.0, 190.0, 280.0, 140.0),
    "storage bench": (70.0, 210.0, 260.0, 120.0),
    "tall cabinet": (120.0, 70.0, 160.0, 260.0),
    "apex": (80.0, 150.0, 240.0, 180.0),
    "pent": (80.0, 140.0, 240.0, 190.0),
}


def _store_marks(material: str, x: float, y: float, w: float, h: float) -> str:
    """What tells one storage material from another, in a ``material`` group."""
    if material == "wood":  # shiplap boards
        body = _line(" ".join(f"M{x + 4},{y + f * h:.1f} L{x + w - 4},{y + f * h:.1f}" for f in (0.25, 0.5, 0.75)), 1.6, ' stroke-opacity=".55"')
    elif material == "steel":  # corrugated ribs
        body = _line(" ".join(f"M{x + f * w:.1f},{y + 6} L{x + f * w:.1f},{y + h - 6}" for f in (0.12, 0.24, 0.36, 0.64, 0.76, 0.88)), 2.2, stroke=_shade(PAPER, 0.35))
    else:  # resin: a moulded panel
        body = _rect(x + w * 0.15, y + h * 0.25, w * 0.7, h * 0.5, "none", 10, 1.6)
    return f'<g class="{MATERIAL_CLASS}">{body}</g>'


def garden_storage(paint: str, fill: Fill, label: str | None, style: str = "deck box", material: str = "resin",
                   part: str = "", part_color: str = "") -> list[str]:  # fmt: skip
    """Garden storage seen from the front: a low ``deck box``, a ``storage bench`` with a back, a
    ``tall cabinet`` with two doors, or a shed with an ``apex`` or a ``pent`` roof; each has a lid
    (a shed's roof), a handle and hinges, and the ``material`` adds its marks (a moulded panel,
    boards, ribs)."""
    pt = _Part("garden_storage", part, part_color)
    style, material = style.lower(), material.lower()
    x, y, w, h = _STORE.get(style, _STORE["deck box"])
    right = x + w
    lid = pt.fill("lid", _shade(fill.base, 0.25))
    handle = pt.fill("handle", GREASE)
    hinge = pt.fill("hinges", POLE)
    out = [_line(GROUND, 4)]
    if style == "storage bench":
        out.append(_rect(x, y - 90, w, 70, _shade(fill.base, 0.1), 6))
    out.append(_rect(x, y, w, h, paint, 6))
    if style == "apex":
        out.append(pt.mark("lid", _path(f"M{x - 16},{y + 4} L{CX},{y - 80} L{right + 16},{y + 4} Z", lid)))
    elif style == "pent":
        out.append(pt.mark("lid", _path(f"M{x - 16},{y + 4} L{x - 16},{y - 50} L{right + 16},{y - 10} L{right + 16},{y + 4} Z", lid)))
    else:
        out.append(pt.mark("lid", _rect(x - 8, y - 18, w + 2 * 8, 22, lid, 5)))
    if style in ("apex", "pent", "tall cabinet"):  # two doors
        out.append(_line(f"M{CX},{y + 12} L{CX},{y + h - 4}", 2.4))
        out.append(pt.mark("handle", _rect(CX - 18, y + h * 0.45, 8, 30, handle, 3)))
        out.append(pt.mark("hinges", _rect(x + 4, y + 30, 10, 20, hinge, 2)))
        out.append(pt.mark("hinges", _rect(right - 14, y + 30, 10, 20, hinge, 2)))
    else:
        out.append(pt.mark("handle", _rect(CX - 30, y + 14, 60, 12, handle, 5)))
        out.append(pt.mark("hinges", _rect(x + 30, y - 6, 24, 10, hinge, 2)))
        out.append(pt.mark("hinges", _rect(right - 54, y - 6, 24, 10, hinge, 2)))
    out.append(_store_marks(material, x, y, w, h))
    return _label(out, label)


SHAPES = {"garden_table": garden_table, "grill_accessory": grill_accessory, "garden_storage": garden_storage}
register(SHAPES)
