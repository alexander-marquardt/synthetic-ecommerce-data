"""Own-kind shapes for the décor types the kit could not draw (gen#1022, slice 6).

Wall art, decorative objects, garden statues, faux florals and fountains, each a flat front
drawing in the kit's house style with the record's fill on the product itself, drawn from the
attributes a record states, as slices 1, 2 and 4's shapes (:mod:`kit_home_furniture`,
:mod:`kit_storage_furniture`, :mod:`kit_bath_kitchen`) are: the variant axis that changes how the
piece looks is a param, the drawn count of panels, pieces and basins is the stated count, and the
material shows as a texture of its own (stone speckled, metal and resin with a sheen, a glaze, wood
grain, see-through glass).

=============  ============================================  ====================================
shape          draws                                         params
=============  ============================================  ====================================
wall_art       one or more panels hung side by side, each    panels, subject, frame
               a picture (abstract, landscape, botanical
               or geometric) on a canvas wrap or in a thin
               frame, or a wide frame with a mat
decor_object   a row of tabletop pieces, largest first: a    form, material, pieces
               sculpture, a bowl, a lantern or a lidded box
garden_statue  an animal, a figure, a sphere or an obelisk   form, base, material
               on its footing, on a plinth or not
faux_floral    an arrangement in a low pot, a wreath with a  form, bloom
               bow, a topiary or a potted tree, in leaf, in
               flower or with berries
fountain       a tiered fountain on its column, a wall       form, basins, material
               fountain on its back panel or a tabletop one
               in its tray, its basins spilling water
=============  ============================================  ====================================

:data:`PARAMS` is each shape's table of params and the values it draws; any other value is refused
with a ``ValueError`` naming the param. A White piece reads white (gen#226): a picture's subject is
drawn in the kit's book colors, leaves and water in their own, and what the product is drawn
against (a mat, a shelf, the ground) stays light. The kit's own ``ornament`` and ``stems`` shapes
(:mod:`kit_decor`) are unchanged, so no product drawn with them changes picture.

``drawings.render`` (:mod:`synthetic_ecommerce_data.drawings`) is the public call that draws
these shapes in a finish; no generator product uses them yet.
"""

# ruff: noqa: E501 -- param tables and SVG path literals read better whole than wrapped.

from __future__ import annotations

import math

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_bath_kitchen import _cls
from synthetic_ecommerce_data.domains.retail.kit_furniture import BOOKS, GLASS, METAL, _grain, _rect
from synthetic_ecommerce_data.domains.retail.kit_home_furniture import FLOOR

#: Each shape's params and the values it draws, in the order a picker would list them.
PARAMS: dict[str, dict[str, tuple[str, ...]]] = {
    "wall_art": {"panels": ("1", "2", "3"), "subject": ("abstract", "landscape", "botanical", "geometric"), "frame": ("canvas", "thin", "wide")},
    "decor_object": {"form": ("sculpture", "bowl", "lantern", "box"), "material": ("ceramic", "metal", "wood", "glass"), "pieces": ("1", "2", "3")},
    "garden_statue": {"form": ("animal", "figure", "sphere", "obelisk"), "base": ("none", "plinth"), "material": ("stone", "metal", "resin")},
    "faux_floral": {"form": ("arrangement", "wreath", "topiary", "tree"), "bloom": ("leaf", "flower", "berry")},
    "fountain": {"form": ("tiered", "wall", "tabletop"), "basins": ("1", "2", "3"), "material": ("stone", "metal", "resin")},
}  # fmt: skip

#: Fixed colors: what the product is drawn against stays light, so a White piece still reads white.
MAT = "#f6f5f1"
SHELF = "#ece9e4"
GROUND = "#e3dfd6"
LEAF = "#5f7f4a"
LEAF_LIGHT = "#86a46a"
TRUNK = "#8a7a5a"
WATER = "#9cc3d6"
WHITE = "#ffffff"


def _valid(kind: str, /, **given: str) -> None:
    """Refuse a value the shape does not draw, naming the param."""
    for key, value in given.items():
        if value not in PARAMS[kind][key]:
            raise ValueError(f"unknown {kind} {key} {value!r}; one of {PARAMS[kind][key]}")


def _ellipse(
    cx: float,
    cy: float,
    rx: float,
    ry: float,
    fill: str,
    width: float = LW_DETAIL,
    rot: float = 0,
    cls: str = "",
) -> str:
    c = f' class="{cls}"' if cls else ""
    t = f' transform="rotate({rot:.0f} {cx:.1f} {cy:.1f})"' if rot else ""
    return f'<ellipse{c} cx="{cx:.1f}" cy="{cy:.1f}" rx="{rx:.1f}" ry="{ry:.1f}" fill="{fill}" stroke="{INK}" stroke-width="{width}"{t}/>'


def _dot(cx: float, cy: float, r: float, fill: str, cls: str = "", width: float = 0) -> str:
    c = f' class="{cls}"' if cls else ""
    stroke = f' stroke="{INK}" stroke-width="{width}"' if width else ""
    return f'<circle{c} cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="{fill}"{stroke}/>'


def _texture(material: str, x: float, y: float, w: float, h: float, base: str) -> list[str]:
    """The material over a body's box: ``stone`` speckled (``class="speckle"``), ``metal`` two
    upright sheens and a dark edge, ``resin`` one soft curved sheen, ``ceramic`` a glaze line,
    ``wood`` its grain; ``glass`` is drawn see-through by its body, so it adds one highlight."""
    if material == "stone":
        return [
            _dot(
                x + w * (0.15 + 0.7 * ((k * 0.37) % 1)),
                y + h * (0.12 + 0.76 * ((k * 0.61) % 1)),
                1.8,
                _shade(base, 0.35),
                "speckle",
            )
            for k in range(1, 10)
        ]
    if material == "metal":
        return [
            _line(
                f"M{x + w * 0.22:.1f},{y + h * 0.12:.1f} L{x + w * 0.22:.1f},{y + h * 0.85:.1f}",
                3,
                ' class="sheen" stroke-opacity=".7"',
                WHITE,
            ),
            _line(
                f"M{x + w * 0.32:.1f},{y + h * 0.2:.1f} L{x + w * 0.32:.1f},{y + h * 0.6:.1f}",
                1.5,
                ' class="sheen" stroke-opacity=".6"',
                WHITE,
            ),
            _line(
                f"M{x + w * 0.85:.1f},{y + h * 0.1:.1f} L{x + w * 0.85:.1f},{y + h * 0.9:.1f}",
                2,
                ' stroke-opacity=".5"',
                _shade(base, 0.4),
            ),
        ]
    if material == "resin":
        return [
            _line(
                f"M{x + w * 0.2:.1f},{y + h * 0.7:.1f} Q{x + w * 0.18:.1f},{y + h * 0.25:.1f} {x + w * 0.45:.1f},{y + h * 0.15:.1f}",
                3.5,
                ' class="sheen" stroke-opacity=".75"',
                WHITE,
            )
        ]
    if material == "ceramic":
        return [
            _line(
                f"M{x + w * 0.15:.1f},{y + h * 0.3:.1f} L{x + w * 0.45:.1f},{y + h * 0.3:.1f}",
                3,
                ' class="glaze" stroke-opacity=".8"',
                WHITE,
            )
        ]
    if material == "wood":
        return [_grain(x, y, w, h, base)]
    return [
        _line(
            f"M{x + w * 0.75:.1f},{y + h * 0.2:.1f} L{x + w * 0.75:.1f},{y + h * 0.7:.1f}",
            2.5,
            ' class="highlight" stroke-opacity=".9"',
            WHITE,
        )
    ]


# --------------------------------------------------------------------------- wall art


def _subject(subject: str, x: float, y: float, w: float, h: float, i: int) -> list[str]:
    """A picture's subject inside its (x, y, w, h) area, in the kit's book colors; the ``i``-th
    panel of a set carries on where the one before it left off."""
    cx, cy = x + w / 2, y + h / 2
    if subject == "abstract":
        return [
            _ellipse(
                x + w * 0.35, y + h * 0.4, w * 0.25, h * 0.18, BOOKS[i % len(BOOKS)], LW_DETAIL
            ),
            _ellipse(
                x + w * 0.62,
                y + h * 0.58,
                w * 0.2,
                h * 0.22,
                BOOKS[(i + 2) % len(BOOKS)],
                LW_DETAIL,
            ),
            _dot(
                x + w * 0.3,
                y + h * 0.75,
                min(w, h) * 0.08,
                BOOKS[(i + 4) % len(BOOKS)],
                width=LW_DETAIL,
            ),
            _line(
                f"M{x + w * 0.1:.1f},{y + h * 0.2:.1f} Q{cx:.1f},{y + h * 0.05:.1f} {x + w * 0.9:.1f},{y + h * 0.3:.1f}",
                3,
                "",
                BOOKS[(i + 1) % len(BOOKS)],
            ),
            _line(
                f"M{x + w * 0.15:.1f},{y + h * 0.9:.1f} Q{cx:.1f},{y + h * 0.7:.1f} {x + w * 0.85:.1f},{y + h * 0.88:.1f}",
                2,
                "",
                BOOKS[(i + 3) % len(BOOKS)],
            ),
        ]
    if subject == "landscape":
        hz = y + h * 0.62
        return [
            _dot(x + w * (0.7 - 0.2 * i), y + h * 0.28, min(w, h) * 0.1, BOOKS[2], width=LW_DETAIL),
            _path(
                f"M{x:.1f},{hz:.1f} Q{x + w * 0.3:.1f},{hz - h * 0.25:.1f} {x + w * 0.6:.1f},{hz:.1f} Q{x + w * 0.8:.1f},{hz - h * 0.15:.1f} {x + w:.1f},{hz - h * 0.05:.1f} L{x + w:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Q{x:.1f},{hz + h * 0.1:.1f} {x:.1f},{hz:.1f} Z",
                BOOKS[3],
                LW_DETAIL,
            ),
            _path(
                f"M{x:.1f},{y + h * 0.8:.1f} Q{cx:.1f},{y + h * 0.7:.1f} {x + w:.1f},{y + h * 0.82:.1f} L{x + w:.1f},{y + h:.1f} L{x:.1f},{y + h:.1f} Q{x:.1f},{y + h * 0.9:.1f} {x:.1f},{y + h * 0.8:.1f} Z",
                BOOKS[1],
                LW_DETAIL,
            ),
            _line(
                f"M{x + w * 0.15:.1f},{y + h * 0.18:.1f} Q{x + w * 0.2:.1f},{y + h * 0.14:.1f} {x + w * 0.25:.1f},{y + h * 0.18:.1f}",
                1.5,
            ),
        ]
    if subject == "botanical":
        out = [
            _line(
                f"M{cx:.1f},{y + h * 0.92:.1f} Q{cx - w * 0.1:.1f},{cy:.1f} {cx + w * 0.05:.1f},{y + h * 0.1:.1f}",
                2,
                "",
                BOOKS[3],
            )
        ]
        for k in range(4):
            ly = y + h * (0.25 + 0.17 * k)
            side = 1 if (k + i) % 2 else -1
            out.append(
                _ellipse(cx + side * w * 0.14, ly, w * 0.14, h * 0.05, BOOKS[3], 1.2, rot=side * 25)
            )
        return out
    # geometric: straight-edged blocks and a triangle, in the book colors
    return [
        _rect(x + w * 0.1, y + h * 0.1, w * 0.35, h * 0.35, BOOKS[(i + 1) % len(BOOKS)], LW_DETAIL),
        _rect(
            x + w * 0.52, y + h * 0.2, w * 0.38, h * 0.22, BOOKS[(i + 2) % len(BOOKS)], LW_DETAIL
        ),
        _path(
            f"M{x + w * 0.15:.1f},{y + h * 0.9:.1f} L{cx:.1f},{y + h * 0.5:.1f} L{x + w * 0.85:.1f},{y + h * 0.9:.1f} Z",
            BOOKS[(i + 4) % len(BOOKS)],
            LW_DETAIL,
        ),
        _line(f"M{x + w * 0.1:.1f},{y + h * 0.48:.1f} L{x + w * 0.9:.1f},{y + h * 0.48:.1f}", 2),
    ]


def wall_art(
    paint: str,
    fill: Fill,
    label: str | None,
    panels: str = "1",
    subject: str = "abstract",
    frame: str = "canvas",
) -> list[str]:
    """Exactly ``panels`` pieces (``class="panel"``) hung side by side on wires, each a picture of
    its ``subject`` on the record's ground: a ``canvas`` wrapped round its stretcher (its edge
    shows), a ``thin`` black frame, or a ``wide`` one (``class="frame"``, one a panel) round a mat
    (``class="mat"``)."""
    _valid("wall_art", panels=panels, subject=subject, frame=frame)
    n = int(panels)
    gap, top, h = 18.0, 82.0, 236.0
    pw = (312 - (n - 1) * gap) / n
    out: list[str] = []
    for i in range(n):
        x = 44 + i * (pw + gap)
        mid = x + pw / 2
        out.append(
            _line(
                f"M{mid - pw * 0.3:.1f},{top + 10:.1f} L{mid:.1f},{top - 26:.1f} L{mid + pw * 0.3:.1f},{top + 10:.1f}",
                1.4,
            )
        )
        if frame == "canvas":
            out.append(
                _path(
                    f"M{x + pw:.1f},{top:.1f} L{x + pw + 6:.1f},{top + 6:.1f} L{x + pw + 6:.1f},{top + h + 6:.1f} L{x + pw:.1f},{top + h:.1f} Z",
                    _shade(fill.base, 0.2),
                    LW_DETAIL,
                )
            )
            out.append(
                _path(
                    f"M{x:.1f},{top + h:.1f} L{x + pw:.1f},{top + h:.1f} L{x + pw + 6:.1f},{top + h + 6:.1f} L{x + 6:.1f},{top + h + 6:.1f} Z",
                    _shade(fill.base, 0.2),
                    LW_DETAIL,
                )
            )
            ix, iy, iw, ih = x, top, pw, h
        else:
            band = 6.0 if frame == "thin" else 14.0
            out.append(_rect(x, top, pw, h, METAL, LW, cls="frame"))
            ix, iy, iw, ih = x + band, top + band, pw - 2 * band, h - 2 * band
            if frame == "wide":
                out.append(_rect(ix, iy, iw, ih, MAT, LW_DETAIL, cls="mat"))
                ix, iy, iw, ih = ix + 12, iy + 12, iw - 24, ih - 24
        out.append(
            _rect(ix, iy, iw, ih, paint, LW if frame == "canvas" else LW_DETAIL, cls="panel")
        )
        out += _subject(subject, ix, iy, iw, ih, i)
    return out


# --------------------------------------------------------------------------- decorative objects


def _piece(
    form: str, material: str, x: float, bottom: float, w: float, h: float, paint: str, fill: Fill
) -> list[str]:
    """One tabletop piece standing on ``bottom``, its body ``class="piece"``."""
    top = bottom - h
    glass = ' fill-opacity=".35"' if material == "glass" else ""
    out: list[str] = [
        _ellipse(x + w / 2, bottom, w * 0.48, 4, GROUND, 1.0)
    ]  # its shadow on the shelf
    if form == "sculpture":  # an open loop on a block
        bh = h * 0.16
        out.append(_rect(x + w * 0.25, bottom - bh, w * 0.5, bh, paint, LW_DETAIL))
        cx, cy, r = x + w / 2, top + (h - bh) / 2, min(w, h - bh) / 2
        d = f"M{cx:.1f},{bottom - bh:.1f} C{cx - r * 1.4:.1f},{cy + r:.1f} {cx - r * 1.2:.1f},{top:.1f} {cx:.1f},{top:.1f} C{cx + r * 1.2:.1f},{top:.1f} {cx + r * 1.4:.1f},{cy + r:.1f} {cx:.1f},{bottom - bh:.1f} Z"
        out.append(_cls(_path(d, paint, LW, glass), "piece"))
        out.append(_ellipse(cx, cy, r * 0.32, r * 0.42, WHITE, LW_DETAIL))
        out.append(
            _line(
                f"M{x + w * 0.25:.1f},{bottom - bh * 0.5:.1f} L{x + w * 0.75:.1f},{bottom - bh * 0.5:.1f}",
                1.0,
            )
        )
        box = (cx - r, top, 2 * r, h - bh)
    elif form == "bowl":
        rim = top + h * 0.35
        d = f"M{x:.1f},{rim:.1f} L{x + w:.1f},{rim:.1f} Q{x + w * 0.95:.1f},{bottom - 4:.1f} {x + w / 2:.1f},{bottom - 4:.1f} Q{x + w * 0.05:.1f},{bottom - 4:.1f} {x:.1f},{rim:.1f} Z"
        out.append(_cls(_path(d, paint, LW, glass), "piece"))
        out.append(_ellipse(x + w / 2, rim, w / 2, h * 0.06, _shade(fill.base, 0.15), LW_DETAIL))
        out.append(_rect(x + w * 0.38, bottom - 6, w * 0.24, 6, paint, LW_DETAIL))
        box = (x, rim, w, bottom - rim)
    elif form == "lantern":
        roof = h * 0.18
        out.append(_dot(x + w / 2, top + 4, 7, "none", width=LW_DETAIL))
        out.append(
            _path(
                f"M{x + w * 0.1:.1f},{top + roof:.1f} L{x + w / 2:.1f},{top + 10:.1f} L{x + w * 0.9:.1f},{top + roof:.1f} Z",
                paint,
                LW_DETAIL,
            )
        )
        out.append(
            _cls(
                _rect(x + w * 0.12, top + roof, w * 0.76, h - roof - 8, paint, LW).replace(
                    "<rect", f"<rect{glass}", 1
                ),
                "piece",
            )
        )
        out.append(_rect(x + w * 0.22, top + roof + 8, w * 0.56, h - roof - 24, GLASS, LW_DETAIL))
        out.append(_rect(x + w * 0.4, bottom - h * 0.32, w * 0.2, h * 0.22, MAT, 1.2))
        out.append(_ellipse(x + w / 2, bottom - h * 0.38, w * 0.05, h * 0.06, BOOKS[2], 1.0))
        out.append(_rect(x + w * 0.06, bottom - 8, w * 0.88, 8, paint, LW_DETAIL))
        box = (x + w * 0.12, top + roof, w * 0.76, h - roof - 8)
    else:  # box: a lidded box
        lid = h * 0.2
        out.append(
            _cls(
                _rect(x + w * 0.05, top + lid, w * 0.9, h - lid, paint, LW).replace(
                    "<rect", f"<rect{glass}", 1
                ),
                "piece",
            )
        )
        out.append(_rect(x, top + 4, w, lid, paint, LW_DETAIL))
        out.append(_dot(x + w / 2, top, 5, paint, width=LW_DETAIL))
        box = (x + w * 0.05, top + lid, w * 0.9, h - lid)
    return out + _texture(material, *box, fill.base)


def decor_object(
    paint: str,
    fill: Fill,
    label: str | None,
    form: str = "sculpture",
    material: str = "ceramic",
    pieces: str = "1",
) -> list[str]:
    """Exactly ``pieces`` tabletop pieces (``class="piece"``) in a row on a shelf, largest first:
    a ``sculpture`` (an open loop on a block), a ``bowl``, a ``lantern`` with its candle or a lidded
    ``box``, in ``ceramic``, ``metal``, ``wood`` or see-through ``glass``."""
    _valid("decor_object", form=form, material=material, pieces=pieces)
    n = int(pieces)
    scales = (1.0, 0.78, 0.6)[:n]
    unit, gap = 300 / (sum(scales) + 0.15 * (n - 1)), 0.15
    unit = min(unit, 170.0)
    x = 200 - (sum(scales) + gap * (n - 1)) * unit / 2
    bottom = FLOOR - 24
    out = [_rect(30, bottom, 340, 14, SHELF, LW_DETAIL)]
    for s in scales:
        w = unit * s
        out += _piece(form, material, x, bottom, w, min(250.0, w * 1.4), paint, fill)
        x += w + gap * unit
    return out


# --------------------------------------------------------------------------- garden statues


def _statue(
    form: str, ground: float, h: float, paint: str
) -> tuple[list[str], tuple[float, float, float, float]]:
    """The statue standing on ``ground``, ``h`` tall, and the box its texture covers."""
    cx, top = 200.0, ground - h
    if form == "animal":  # a sitting hare
        body = _ellipse(cx - 10, ground - h * 0.3, h * 0.32, h * 0.3, paint, LW)
        head = _ellipse(cx + h * 0.16, ground - h * 0.66, h * 0.15, h * 0.13, paint, LW)
        ears = [
            _ellipse(
                cx + h * (0.12 + 0.08 * k),
                top + h * 0.17,
                h * 0.05,
                h * 0.17,
                paint,
                LW_DETAIL,
                rot=-12 + 18 * k,
            )
            for k in range(2)
        ]
        parts = [_ellipse(cx - h * 0.38, ground - h * 0.22, h * 0.07, h * 0.07, paint, LW_DETAIL), body, *ears, head,
                 _ellipse(cx + h * 0.08, ground - h * 0.06, h * 0.12, h * 0.05, paint, LW_DETAIL), _dot(cx + h * 0.22, ground - h * 0.68, 3, INK)]  # fmt: skip
        return parts, (cx - h * 0.42, top + h * 0.3, h * 0.84, h * 0.66)
    if form == "figure":  # a standing robed figure, hands folded
        hw = h * 0.2
        robe = f"M{cx - hw * 0.5:.1f},{top + h * 0.2:.1f} Q{cx - hw * 1.1:.1f},{top + h * 0.6:.1f} {cx - hw:.1f},{ground:.1f} L{cx + hw:.1f},{ground:.1f} Q{cx + hw * 1.1:.1f},{top + h * 0.6:.1f} {cx + hw * 0.5:.1f},{top + h * 0.2:.1f} Z"
        parts = [_path(robe, paint, LW), _dot(cx, top + h * 0.1, h * 0.1, paint, width=LW),
                 _line(f"M{cx - hw * 0.6:.1f},{top + h * 0.42:.1f} Q{cx:.1f},{top + h * 0.5:.1f} {cx + hw * 0.6:.1f},{top + h * 0.42:.1f}", LW_DETAIL),
                 _line(f"M{cx - hw * 0.3:.1f},{top + h * 0.6:.1f} L{cx - hw * 0.4:.1f},{ground - 6:.1f} M{cx + hw * 0.3:.1f},{top + h * 0.6:.1f} L{cx + hw * 0.4:.1f},{ground - 6:.1f}", 1.2)]  # fmt: skip
        return parts, (cx - hw, top + h * 0.2, 2 * hw, h * 0.8)
    if form == "sphere":  # a globe on a collar
        r = min(h * 0.42, 110.0)
        cy = ground - 18 - r
        parts = [_rect(cx - r * 0.35, ground - 18, r * 0.7, 18, paint, LW_DETAIL), _dot(cx, cy, r, paint, width=LW),
                 _ellipse(cx, cy, r, r * 0.3, "none", LW_DETAIL), _ellipse(cx, cy, r * 0.3, r, "none", LW_DETAIL)]  # fmt: skip
        return parts, (cx - r, cy - r, 2 * r, 2 * r)
    # obelisk: a tapering shaft with a pointed tip and two carved bands
    bw, tw = h * 0.16, h * 0.1
    tip = top + h * 0.12
    parts = [_path(f"M{cx - bw:.1f},{ground:.1f} L{cx + bw:.1f},{ground:.1f} L{cx + tw:.1f},{tip:.1f} L{cx - tw:.1f},{tip:.1f} Z", paint, LW),
             _path(f"M{cx - tw:.1f},{tip:.1f} L{cx + tw:.1f},{tip:.1f} L{cx:.1f},{top:.1f} Z", paint, LW_DETAIL)]  # fmt: skip
    for t in (0.35, 0.75):
        y = tip + (ground - tip) * t
        half = tw + (bw - tw) * t
        parts.append(_line(f"M{cx - half:.1f},{y:.1f} L{cx + half:.1f},{y:.1f}", 1.2))
    return parts, (cx - tw, tip, 2 * tw, ground - tip)


def garden_statue(
    paint: str,
    fill: Fill,
    label: str | None,
    form: str = "animal",
    base: str = "none",
    material: str = "stone",
) -> list[str]:
    """A garden statue on its cast footing on the ground: an ``animal`` (a sitting hare), a
    robed ``figure``, a ``sphere`` on a collar or an ``obelisk``, on a ``plinth``
    (``class="plinth"``) or not, in ``stone`` (``class="speckle"``), ``metal`` or ``resin``."""
    _valid("garden_statue", form=form, base=base, material=material)
    ground = float(FLOOR)
    out = [_ellipse(200, ground, 150, 12, GROUND, 1.0)]
    if base == "plinth":
        out += [
            _cls(_rect(140, ground - 84, 120, 84, paint, LW), "plinth"),
            _rect(130, ground - 96, 140, 12, paint, LW_DETAIL),
        ]
        ground -= 96
    out.append(_rect(150, ground - 12, 100, 12, paint, LW_DETAIL))
    ground -= 12
    parts, box = _statue(form, ground, ground - 40, paint)
    return out + parts + _texture(material, *box, fill.base)


# --------------------------------------------------------------------------- faux florals


def _sprig(cx: float, cy: float, r: float, bloom: str, paint: str, k: int) -> list[str]:
    """What sits at one stem tip: a leaf pair, a five-petal ``class="flower"`` or a cluster of
    three ``class="berry"``."""
    if bloom == "flower":
        petals = [
            _dot(
                cx + r * 0.6 * math.cos(math.radians(72 * p + 15 * k)),
                cy + r * 0.6 * math.sin(math.radians(72 * p + 15 * k)),
                r * 0.5,
                paint,
                width=1.0,
            )
            for p in range(5)
        ]
        return ['<g class="flower">', *petals, _dot(cx, cy, r * 0.35, BOOKS[2], width=1.0), "</g>"]
    if bloom == "berry":
        return [
            '<g class="berry">',
            *[
                _dot(cx + r * 0.5 * dx, cy + r * 0.5 * dy, r * 0.42, paint, width=1.0)
                for dx, dy in ((-1, 0), (1, 0), (0, -1.2))
            ],
            "</g>",
        ]
    return [
        _ellipse(cx - r * 0.6, cy, r * 0.9, r * 0.35, LEAF_LIGHT, 1.0, rot=-30),
        _ellipse(cx + r * 0.6, cy, r * 0.9, r * 0.35, LEAF_LIGHT, 1.0, rot=30),
    ]


def _pot(x: float, top: float, w: float, h: float, paint: str) -> list[str]:
    return [_cls(_path(f"M{x:.1f},{top:.1f} L{x + w:.1f},{top:.1f} L{x + w * 0.88:.1f},{top + h:.1f} L{x + w * 0.12:.1f},{top + h:.1f} Z", paint, LW), "pot"),
            _rect(x - 4, top - 8, w + 8, 10, paint, LW_DETAIL)]  # fmt: skip


def faux_floral(
    paint: str, fill: Fill, label: str | None, form: str = "arrangement", bloom: str = "flower"
) -> list[str]:
    """Artificial greenery: an ``arrangement`` of stems in a low pot, a ``wreath`` hung by a bow
    (``class="bow"``), a clipped ``topiary`` ball or a potted ``tree``; ``leaf`` only, in
    ``flower`` (``class="flower"``) or with ``berry`` clusters (``class="berry"``). The pot or the
    bow, and the flowers and berries, take the record's color."""
    _valid("faux_floral", form=form, bloom=bloom)
    out: list[str] = []
    if form == "wreath":
        cx, cy, r = 200.0, 190.0, 112.0
        out.append(
            f'<circle class="ring" cx="{cx:.1f}" cy="{cy:.1f}" r="{r:.1f}" fill="none" stroke="{LEAF}" stroke-width="10"/>'
        )
        for k in range(16):
            a = math.radians(22.5 * k)
            out.append(
                _ellipse(
                    cx + r * math.cos(a),
                    cy + r * math.sin(a),
                    20,
                    8,
                    LEAF,
                    1.0,
                    rot=math.degrees(a) + 90,
                )
            )
        for k in range(6):
            a = math.radians(60 * k - 60)
            out += _sprig(cx + r * math.cos(a), cy + r * math.sin(a), 14, bloom, paint, k)
        by = cy + r
        out += [_path(f"M{cx:.1f},{by:.1f} L{cx - 36:.1f},{by - 18:.1f} L{cx - 36:.1f},{by + 18:.1f} Z", paint, LW_DETAIL),
                _path(f"M{cx:.1f},{by:.1f} L{cx + 36:.1f},{by - 18:.1f} L{cx + 36:.1f},{by + 18:.1f} Z", paint, LW_DETAIL),
                _cls(_rect(cx - 8, by - 8, 16, 16, paint, LW_DETAIL), "bow"),
                _path(f"M{cx - 6:.1f},{by + 8:.1f} L{cx - 18:.1f},{by + 44:.1f} L{cx - 8:.1f},{by + 40:.1f} Z", paint, LW_DETAIL),
                _path(f"M{cx + 6:.1f},{by + 8:.1f} L{cx + 18:.1f},{by + 44:.1f} L{cx + 8:.1f},{by + 40:.1f} Z", paint, LW_DETAIL)]  # fmt: skip
        return out
    if form == "arrangement":
        pot_top, pot_h, pot_w = FLOOR - 70.0, 70.0, 150.0
        tips = [
            (200 + 120 * math.sin(math.radians(a)), pot_top - 150 * math.cos(math.radians(a)) + 20)
            for a in (-60, -35, -12, 12, 35, 60, 0)
        ]
    elif form == "topiary":
        pot_top, pot_h, pot_w = FLOOR - 80.0, 80.0, 110.0
        out.append(_rect(194, pot_top - 120, 12, 120, TRUNK, LW_DETAIL))
        out.append(_dot(200, pot_top - 180, 80, LEAF, width=LW))
        tips = [
            (200 + 52 * math.cos(math.radians(a)), pot_top - 180 + 52 * math.sin(math.radians(a)))
            for a in range(0, 360, 60)
        ] + [(200, pot_top - 180)]
    else:  # tree: a trunk and a canopy of large leaves
        pot_top, pot_h, pot_w = FLOOR - 90.0, 90.0, 120.0
        out.append(
            _path(
                f"M196,{pot_top:.1f} L204,{pot_top:.1f} L206,{pot_top - 170:.1f} L198,{pot_top - 170:.1f} Z",
                TRUNK,
                LW_DETAIL,
            )
        )
        for k in range(9):
            a = math.radians(-90 + (k - 4) * 34)
            lx, ly = (
                202 + 78 * math.cos(a) * (0.7 + 0.3 * (k % 2)),
                pot_top - 170 + 78 * math.sin(a) * (0.7 + 0.3 * (k % 2)) + 30,
            )
            out.append(_ellipse(lx, ly, 34, 16, LEAF, 1.2, rot=math.degrees(a) + 90))
        for k in range(5):  # an inner ring, so the canopy reads full
            a = math.radians(-90 + (k - 2) * 45)
            out.append(
                _ellipse(
                    202 + 36 * math.cos(a),
                    pot_top - 130 + 36 * math.sin(a),
                    28,
                    13,
                    LEAF_LIGHT,
                    1.2,
                    rot=math.degrees(a) + 90,
                )
            )
        tips = [
            (202 + 60 * math.cos(math.radians(a)), pot_top - 160 + 60 * math.sin(math.radians(a)))
            for a in (-150, -110, -70, -30)
        ]
    for k, (tx, ty) in enumerate(tips):
        if form == "arrangement":
            out.append(
                _line(
                    f"M200,{pot_top:.1f} Q{(200 + tx) / 2:.1f},{(pot_top + ty) / 2 + 20:.1f} {tx:.1f},{ty:.1f}",
                    2,
                    "",
                    LEAF,
                )
            )
            out.append(
                _ellipse(
                    (200 + tx) / 2,
                    (pot_top + ty) / 2 + 12,
                    14,
                    6,
                    LEAF,
                    1.0,
                    rot=35 if tx > 200 else -35,
                )
            )
        out += _sprig(tx, ty, 16 if form == "arrangement" else 12, bloom, paint, k)
    return out + _pot(200 - pot_w / 2, pot_top, pot_w, pot_h, paint)


# --------------------------------------------------------------------------- fountains


def _basin(cx: float, rim: float, half: float, depth: float, paint: str) -> list[str]:
    """One bowl (``class="basin"``) with water standing in it."""
    d = f"M{cx - half:.1f},{rim:.1f} L{cx + half:.1f},{rim:.1f} Q{cx + half * 0.8:.1f},{rim + depth * 1.6:.1f} {cx:.1f},{rim + depth * 1.6:.1f} Q{cx - half * 0.8:.1f},{rim + depth * 1.6:.1f} {cx - half:.1f},{rim:.1f} Z"
    return [
        _cls(_path(d, paint, LW), "basin"),
        _ellipse(cx, rim, half - 4, max(3.0, depth * 0.18), GLASS, 1.0),
    ]


def _spill(x: float, y0: float, y1: float, side: int) -> str:
    """Water falling from a basin's lip at (x, y0) down to y1."""
    return _line(
        f"M{x:.1f},{y0:.1f} Q{x + side * 14:.1f},{y0 + 6:.1f} {x + side * 16:.1f},{y1:.1f}",
        2.2,
        ' class="water"',
        WATER,
    )


def fountain(
    paint: str,
    fill: Fill,
    label: str | None,
    form: str = "tiered",
    basins: str = "1",
    material: str = "stone",
) -> list[str]:
    """A fountain with exactly ``basins`` basins (``class="basin"``), water spilling from each: a
    ``tiered`` one with its basins up a column over a pool, a ``wall`` one with its basins
    stepping down a back panel, or a ``tabletop`` one with its bowls in a tray; in ``stone``
    (``class="speckle"``), ``metal`` or ``resin``."""
    _valid("fountain", form=form, basins=basins, material=material)
    n = int(basins)
    out: list[str] = []
    if form == "tiered":
        ground = float(FLOOR)
        top = ground - 70 - 80 * n
        out.append(_rect(30, ground - 24, 340, 24, paint, LW_DETAIL))
        out.append(_rect(188, top, 24, ground - 24 - top, paint, LW))
        out.append(_dot(200, top - 10, 12, paint, width=LW_DETAIL))
        for k in range(n):
            half, rim = 150 - 40 * k, ground - 70 - 80 * k
            out += _basin(200, rim, half, 18 - 3 * k, paint)
            out += [_spill(200 - half, rim, rim + 50, -1), _spill(200 + half, rim, rim + 50, 1)]
        out.append(
            _line(
                f"M200,{top - 22:.1f} Q190,{top - 50:.1f} 176,{top - 30:.1f} M200,{top - 22:.1f} Q210,{top - 50:.1f} 224,{top - 30:.1f}",
                2.2,
                ' class="water"',
                WATER,
            )
        )
        box = (188.0, top, 24.0, ground - 24 - top)
    elif form == "wall":
        out.append(_rect(110, 50, 180, FLOOR - 50, paint, LW))
        out.append(_path("M100,50 L300,50 L292,36 L108,36 Z", paint, LW_DETAIL))
        out.append(_rect(190, 70, 20, 24, METAL, LW_DETAIL))
        step = (FLOOR - 150) / n
        for k in range(n):
            rim = 120 + step * k
            out += _basin(200, rim, 70 + 12 * k, 20, paint)
        out.append(_line(f"M200,94 L200,{120 - 4:.1f}", 3, ' class="water"', WATER))
        out += [
            _spill(200 + 70 + 12 * k, 120 + step * k, 120 + step * (k + 1) - 8, 1)
            for k in range(n - 1)
        ]
        box = (110.0, 50.0, 180.0, FLOOR - 50.0)
    else:  # tabletop: small bowls cascading into a tray of pebbles
        tray = FLOOR - 40.0
        out.append(
            _path(f"M50,{tray:.1f} L350,{tray:.1f} L330,{FLOOR:.1f} L70,{FLOOR:.1f} Z", paint, LW)
        )
        out += [_dot(90 + 34 * k, tray - 4, 9, TRUNK, width=1.0) for k in range(7)]
        for k in range(n):
            cx, rim = 140 + 60 * k, tray - 170 + 50 * k
            out.append(_rect(cx - 10, rim + 24, 20, tray - rim - 24, paint, LW_DETAIL))
            out += _basin(cx, rim, 46, 14, paint)
            out.append(_spill(cx + 46, rim, rim + 40, 1))
        box = (50.0, tray, 300.0, FLOOR - tray)
    return out + _texture(material, *box, fill.base)


register(
    {"wall_art": wall_art, "decor_object": decor_object, "garden_statue": garden_statue,
     "faux_floral": faux_floral, "fountain": fountain},
)  # fmt: skip
