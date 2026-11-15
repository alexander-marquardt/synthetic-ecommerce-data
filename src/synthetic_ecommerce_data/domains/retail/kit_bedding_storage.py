"""Sheet set and food storage container shapes for the retail drawing kit (gen#963, slice 2).

=============  ==================================================  ==============================
shape          draws                                               params
=============  ==================================================  ==============================
sheet_set      a folded sheet set on its paper band: crisp folds   kind (cotton percale, cotton
               for percale, a sheen for sateen, a check for        sateen, microfiber, bamboo,
               flannel, slub lines for linen, a soft ripple for    linen, flannel)
               bamboo and rounded edges for microfiber
food_storage   two containers stacked on a third, each with its    kind (glass, plastic,
               lid: clear glass with food inside, frosted          stainless steel, silicone)
               plastic, brushed steel, or silicone that folds
               flat in pleats
bed_pillow     a bed pillow in its cover, seen from the front: a   kind (down alternative, memory
               quilted down alternative, a solid memory foam       foam, shredded memory foam,
               block with air holes, a gel layer on foam, a        cooling gel, feather); support
               zipped cover of shredded foam, a piped feather      (plush, soft, medium, firm,
               pillow; the support sets how far it bulges and      extra firm)
               how deep its side stands
=============  ==================================================  ==============================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes its material draws what it states (gen#512). The sheets and the lids carry the
record's fill; glass, plastic and steel do not. No drawing prints a size or a piece count: one
image serves every size its color sells. The drawings are original and drawn by code (ruling
2026-11-02, gen#102).
"""

# ruff: noqa: E501 -- SVG paths read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_appliances import (
    GLASS,
    PAPER,
    STEEL,
    STEEL_DARK,
    _rect,
    _shadow,
)

#: Frosted plastic, and the food a clear container shows.
FROSTED = "#eef0ec"
FOOD = "#e9a34a"
GREENS = "#7fae58"


def _layer(y: float, h: float, inset: float, paint: str, round_edge: bool) -> str:
    """One folded layer of the stack, ``inset`` in from each side; a soft fabric rounds its
    front edge."""
    x0, x1 = 70 + inset, 330 - inset
    if round_edge:
        d = f"M{x0},{y} L{x1},{y} Q{x1 + 14},{y + h / 2} {x1},{y + h} L{x0},{y + h} Q{x0 - 14},{y + h / 2} {x0},{y} Z"
    else:
        d = f"M{x0},{y} L{x1},{y} L{x1 + 4},{y + h} L{x0 - 4},{y + h} Z"
    return _path(d, paint)


def sheet_set(paint: str, fill: Fill, label: str | None, kind: str = "cotton percale") -> list[str]:
    """A sheet set folded in a stack of three (the flat sheet, the fitted sheet and the
    pillowcases), held by a paper band; ``kind`` is the material, which sets the texture."""
    soft = kind in ("microfiber", "bamboo", "flannel")
    layers = ((236, 92, 0), (172, 64, 14), (120, 52, 30))
    out = [_shadow(200, 334, 150)]
    for y, h, inset in layers:
        out.append(_layer(y, h, inset, paint, soft))
    for y, h, inset in layers:
        x0, x1 = 74 + inset, 326 - inset
        if kind == "cotton percale":
            out.append(_line(f"M{x0},{y + h / 2} L{x1},{y + h / 2}", 1.2, ' stroke-opacity=".6"'))
        elif kind == "cotton sateen":
            out.append(_highlight(f"M{x0 + 10},{y + 10} Q{(x0 + x1) / 2},{y + 4} {x1 - 10},{y + 10}", 6, 0.55))
        elif kind == "flannel":
            for x in range(int(x0) + 24, int(x1), 36):
                out.append(_line(f"M{x},{y + 4} L{x},{y + h - 4}", 3, ' stroke-opacity=".25"', _shade("#ffffff", 0.6)))
            out.append(_line(f"M{x0},{y + h / 2} L{x1},{y + h / 2}", 3, ' stroke-opacity=".25"', _shade("#ffffff", 0.6)))
        elif kind == "linen":
            for k in (0.3, 0.55, 0.8):
                out.append(_line(f"M{x0 + 8},{y + h * k} L{x1 - 8},{y + h * k + 1}", 0.9, ' stroke-opacity=".45" stroke-dasharray="14 3 4 3"'))
        elif kind == "bamboo":
            mid = y + h / 2
            out.append(_line(f"M{x0},{mid} Q{x0 + 40},{mid - 8} {x0 + 80},{mid} T{x0 + 160},{mid} T{x0 + 240},{mid}", 1.2, ' stroke-opacity=".5"'))
        else:  # microfiber: a brushed surface, no weave
            out.append(_highlight(f"M{x0 + 16},{y + h - 10} L{x1 - 16},{y + h - 10}", 3, 0.35))
    out.append(_rect(150, 112, 100, 218, PAPER, 2, LW_DETAIL))
    out.append(_line("M162,150 L238,150 M162,166 L226,166", 2, ' stroke-opacity=".5"'))
    return out


def _container(x: float, y: float, w: float, h: float, paint: str, kind: str) -> list[str]:
    """One container with its lid on top; the lid carries the record's fill."""
    out: list[str] = []
    body = f"M{x},{y} L{x + w},{y} L{x + w - 6},{y + h} L{x + 6},{y + h} Z"
    if kind == "glass":
        out.append(_path(body, GLASS, LW_DETAIL, ' fill-opacity=".9"'))
        out.append(_path(f"M{x + 10},{y + h * 0.45} L{x + w - 10},{y + h * 0.45} L{x + w - 12},{y + h - 6} L{x + 12},{y + h - 6} Z", FOOD, 1.0))
        out.append(_path(f"M{x + 18},{y + h * 0.45} Q{x + w / 2},{y + h * 0.3} {x + w - 18},{y + h * 0.45} Z", GREENS, 1.0))
        out.append(_highlight(f"M{x + 8},{y + 8} L{x + 12},{y + h - 10}", 4, 0.6))
    elif kind == "stainless steel":
        out.append(_path(body, STEEL, LW_DETAIL))
        for k in (0.3, 0.55, 0.8):
            out.append(_line(f"M{x + 6},{y + h * k} L{x + w - 6},{y + h * k}", 0.8, ' stroke-opacity=".35"', STEEL_DARK))
        out.append(_highlight(f"M{x + 12},{y + 8} L{x + 16},{y + h - 8}", 5, 0.7))
    elif kind == "silicone":
        out.append(_path(body, _shade(paint, 0.1) if paint.startswith("#") else paint, LW_DETAIL))
        for k in (0.33, 0.66):
            out.append(_line(f"M{x + 4},{y + h * k} L{x + w - 4},{y + h * k}", 2.2))
    else:  # plastic: frosted, the food a shadow through it
        out.append(_path(body, FROSTED, LW_DETAIL))
        out.append(_path(f"M{x + 12},{y + h * 0.5} L{x + w - 12},{y + h * 0.5} L{x + w - 14},{y + h - 8} L{x + 14},{y + h - 8} Z", FOOD, 1.0, ' fill-opacity=".35"'))
    out.append(_rect(x - 6, y - 14, w + 12, 18, paint, 5))
    out.append(_line(f"M{x + 4},{y - 5} L{x + w - 4},{y - 5}", 1.2, ' stroke-opacity=".5"'))
    return out


def food_storage(paint: str, fill: Fill, label: str | None, kind: str = "plastic") -> list[str]:
    """A set of food storage containers: two small ones on a large one, each with its lid;
    ``kind`` is the material of the boxes (the lids carry the fill)."""
    out = [_shadow(200, 340, 150)]
    out += _container(70, 236, 260, 100, paint, kind)
    out += _container(84, 150, 110, 66, paint, kind)
    out += _container(206, 150, 110, 66, paint, kind)
    return out


#: Each support: how far a pillow's sides bulge and how deep its side stands. A plush pillow is
#: full and round; an extra firm one keeps square edges and a deep side.
SUPPORT = {"plush": (30, 10), "soft": (24, 14), "medium": (18, 18), "firm": (12, 22),
           "extra firm": (6, 26)}  # fmt: skip
GEL = "#8cc8ee"
ZIP = "#8f989f"


def bed_pillow(paint: str, fill: Fill, label: str | None, kind: str = "down alternative",
               support: str = "medium") -> list[str]:  # fmt: skip
    """A bed pillow from the front: ``kind`` is the fill, which sets the cover's make, and
    ``support`` how far the sides bulge and how deep the side below the face stands."""
    bulge, side = SUPPORT[support]
    x0, x1, y0, y1 = 82, 318, 120, 296 - side
    if kind in ("memory foam", "cooling gel"):  # a solid block: straight sides, round corners
        face = f"M{x0 + 18},{y0} L{x1 - 18},{y0} Q{x1},{y0} {x1},{y0 + 18} L{x1},{y1 - 18} Q{x1},{y1} {x1 - 18},{y1} L{x0 + 18},{y1} Q{x0},{y1} {x0},{y1 - 18} L{x0},{y0 + 18} Q{x0},{y0} {x0 + 18},{y0} Z"
    else:
        mid = (y0 + y1) / 2
        face = f"M{x0},{y0} Q200,{y0 - bulge} {x1},{y0} Q{x1 + bulge},{mid} {x1},{y1} Q200,{y1 + bulge} {x0},{y1} Q{x0 - bulge},{mid} {x0},{y0} Z"
    out = ['<ellipse cx="200" cy="340" rx="130" ry="10" fill="#000000" fill-opacity=".08"/>']
    out.append(_path(f"M{x0 + 4},{y1 - 6} L{x1 - 4},{y1 - 6} L{x1 - 10},{y1 + side} L{x0 + 10},{y1 + side} Z", _shade(paint, 0.12) if paint.startswith("#") else paint))
    out.append(_path(face, paint))
    if kind == "down alternative":  # a quilted cover
        for x in range(x0 + 40, x1 - 20, 48):
            out.append(_line(f"M{x},{y0 + 12} L{x + 30},{y1 - 12}", 1.0, ' stroke-opacity=".45" stroke-dasharray="5 4"'))
            out.append(_line(f"M{x + 30},{y0 + 12} L{x},{y1 - 12}", 1.0, ' stroke-opacity=".45" stroke-dasharray="5 4"'))
    elif kind == "memory foam":  # air holes in the foam
        for row, y in enumerate(range(y0 + 34, y1 - 20, 30)):
            for x in range(x0 + 36 + 15 * (row % 2), x1 - 24, 30):
                out.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#000000" fill-opacity=".14"/>')
    elif kind == "cooling gel":  # a gel layer across the top of the foam
        out.append(_path(f"M{x0 + 14},{y0 + 10} L{x1 - 14},{y0 + 10} L{x1 - 14},{y0 + 46} Q200,{y0 + 60} {x0 + 14},{y0 + 46} Z", GEL, 1.0, ' fill-opacity=".85"'))
        out.append(_highlight(f"M{x0 + 40},{y0 + 26} Q150,{y0 + 18} 200,{y0 + 26} T{x1 - 40},{y0 + 26}", 4, 0.6))
    elif kind == "shredded memory foam":  # a zip along the foot, the shredded fill in lumps
        out.append(_line(f"M{x0 + 30},{y1 - 14} L{x1 - 30},{y1 - 14}", 3, "", ZIP))
        for x in range(x0 + 34, x1 - 30, 8):
            out.append(_line(f"M{x},{y1 - 18} L{x},{y1 - 10}", 1.0, "", ZIP))
        for cx, cy in ((140, y0 + 50), (210, y0 + 70), (260, y0 + 44), (176, y0 + 96)):
            out.append(_line(f"M{cx - 14},{cy} q7,-9 14,0 t14,0", 1.2, ' stroke-opacity=".4"'))
    else:  # feather: a piped edge and pointed corners
        out.append(_path(face, "none", 1.2, ' transform="translate(200 208) scale(.92) translate(-200 -208)"'))
        for (x, y), (dx, dy) in (((x0, y0), (-10, -8)), ((x1, y0), (10, -8)), ((x0, y1), (-10, 8)), ((x1, y1), (10, 8))):
            out.append(_line(f"M{x},{y} L{x + dx},{y + dy}", 2.0))
    out.append(_highlight(f"M{x0 + 30},{y0 + 26} Q150,{y0 + 10} 200,{y0 + 10}", 6, 0.3))
    return out


SHAPES = {"sheet_set": sheet_set, "food_storage": food_storage, "bed_pillow": bed_pillow}
register(SHAPES)
