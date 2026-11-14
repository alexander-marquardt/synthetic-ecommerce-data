"""Hair styling tools for the retail drawing kit (gen#957): dryers, straighteners, hairbrushes.

==================  ============================================  ================================
shape               draws                                         params
==================  ============================================  ================================
hair_dryer          a hair dryer from the side: its body and      technology (ionic, ceramic,
                    nozzle in the SKU's color, a vent grille,     tourmaline, infrared), form
                    a badge by ``technology`` and a handle by     (compact, salon, travel,
                    ``form`` (a folding travel handle is drawn    folding)
                    hinged, a salon dryer long with a cord,
                    a travel dryer with a hanging loop)
hair_straightener   a closed straightener, upright: two arms in   plate (ceramic, titanium,
                    the SKU's color, plates whose tone is the     tourmaline), kind (mini,
                    ``plate`` material, and by ``kind`` a short   salon, cordless, travel)
                    body, a long one with a cord, or a battery
hairbrush           a hairbrush, upright: a handle in the SKU's   head (paddle, round, vent,
                    color, a head by ``head`` and bristle tips    detangling), bristle (boar,
                    by ``bristle``                                nylon, mixed)
==================  ============================================  ================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a dryer's ``form`` or a brush's ``head`` draws what it states (gen#512).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    LW_DETAIL,
    Fill,
    _highlight,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The grey of a vent grille, a hinge and a cord.
GRILLE = "#5a5d63"
CORD = "#3a3a40"
#: The badge on a dryer's body, one tone per technology.
BADGE = {"ionic": "#6fb3d9", "ceramic": "#efe9dc", "tourmaline": "#b25c86", "infrared": "#d9533a"}
#: A straightener's plates, one tone per material.
PLATE = {"ceramic": "#f2ede2", "titanium": "#9aa1a9", "tourmaline": "#6a3a55"}
#: A hairbrush's bristle tips, one tone per bristle.
BRISTLE = {"boar": "#c9a77a", "nylon": "#f4f4f2", "mixed": "#c9a77a"}


def _cord(x: float, y: float) -> str:
    return _line(f"M{x},{y} C{x},{y + 30} {x + 40},{y + 20} {x + 46},{y + 34}", 4, "", CORD)


def hair_dryer(
    paint: str,
    fill: Fill,
    label: str | None,
    technology: str = "ionic",
    form: str = "salon",
) -> list[str]:
    """A hair dryer from the side: the body and nozzle, the vent grille at the back, a badge by
    ``technology`` and a handle by ``form``."""
    scale = 0.82 if form in ("compact", "travel") else 1.0
    x0, x1, cy, r = 90, 90 + 210 * scale, 150, 58 * scale
    out = [
        _rect(x0, cy - r, x1 - x0, 2 * r, paint, r),
        _path(
            f"M{x1 - 8},{cy - r * 0.6} L{x1 + 50 * scale},{cy - r * 0.45} "
            f"L{x1 + 50 * scale},{cy + r * 0.45} L{x1 - 8},{cy + r * 0.6} Z",
            _shade(fill.base, 0.2),
        ),  # fmt: skip
        _ell(x0 + 10, cy, 14, r - 6, GRILLE),
    ]
    out += [_line(f"M{x0 + 3},{y:.1f} L{x0 + 17},{y:.1f}", LW_DETAIL, "", "#ffffff")
            for y in (cy - r * 0.5, cy - r * 0.15, cy + r * 0.2, cy + r * 0.55)]  # fmt: skip
    out.append(_ell(x0 + 70 * scale, cy, 14, 14, BADGE.get(technology, BADGE["ionic"]), LW_DETAIL))
    hx = x0 + 100 * scale
    long = form == "salon"
    hy0, hlen = cy + r - 6, (150 if long else 110) * scale
    if form == "folding":
        out += [
            _ell(hx + 18, hy0 + 6, 9, 9, GRILLE, LW_DETAIL),
            _rect(hx, hy0 + 12, 36, hlen, _shade(fill.base, 0.1), 14),
            _line(f"M{hx},{hy0 + 30} L{hx + 36},{hy0 + 30}", LW_DETAIL),
        ]
    else:
        out.append(_rect(hx, hy0, 36, hlen, _shade(fill.base, 0.1), 14))
    out.append(_rect(hx + 10, hy0 + 30, 16, 26, _tint(fill.base, 0.5), 4, LW_DETAIL))
    if long:
        out.append(_cord(hx + 18, hy0 + hlen))
    elif form == "travel":
        out.append(_ell(hx + 18, hy0 + hlen + 8, 10, 8, "none", LW_DETAIL))
    out.append(_highlight(f"M{x0 + 40},{cy - r + 12} L{x1 - 20},{cy - r + 12}", 6, 0.45))
    return _label(out, label)


def hair_straightener(
    paint: str,
    fill: Fill,
    label: str | None,
    plate: str = "ceramic",
    kind: str = "salon",
) -> list[str]:
    """A closed straightener, upright: two arms, the plates' tone by ``plate`` and the body by
    ``kind`` (a mini is short; a salon tool is long, with a cord; a cordless one has a battery)."""
    top, bottom = (120, 300) if kind == "mini" else (52, 330)
    plates = PLATE.get(plate, PLATE["ceramic"])
    out = [
        _path(
            f"M170,{bottom} L166,{top + 20} Q166,{top} 186,{top} L198,{top} L198,{bottom} Z", paint
        ),  # fmt: skip
        _path(
            f"M230,{bottom} L234,{top + 20} Q234,{top} 214,{top} L202,{top} L202,{bottom} Z",
            _shade(fill.base, 0.12),
        ),  # fmt: skip
        _rect(190, top + 12, 20, (bottom - top) * 0.45, plates, 3, LW_DETAIL),
        _rect(176, bottom - 6, 48, 34, _shade(fill.base, 0.25), 8),
        _ell(200, bottom - 70, 7, 7, "#e8e2d4", LW_DETAIL),
    ]
    if kind == "cordless":
        out.append(_rect(184, bottom + 4, 32, 18, GRILLE, 4, LW_DETAIL))
        out += [_rect(188 + 7 * i, bottom + 9, 5, 8, "#9fd38a", 1, 1) for i in range(3)]
    elif kind == "salon":
        out.append(_cord(200, bottom + 28))
    out.append(_highlight(f"M178,{top + 30} L176,{bottom - 30}", 5, 0.45))
    return _label(out, label)


def hairbrush(
    paint: str,
    fill: Fill,
    label: str | None,
    head: str = "paddle",
    bristle: str = "nylon",
) -> list[str]:
    """A hairbrush, upright: the handle, a head by ``head`` and bristle tips by ``bristle``."""
    tip = BRISTLE.get(bristle, BRISTLE["nylon"])
    out = [_rect(184, 210, 32, 150, paint, 14)]
    if head == "round":
        out.append(_rect(176, 52, 48, 164, _tint(fill.base, 0.35), 24))
        pins = [(x, y) for y in range(64, 206, 14) for x in (162, 238)]
    else:
        wide = 64 if head == "paddle" else 48
        pad = _shade(fill.base, 0.3) if head == "vent" else "#2e2e33"
        out += [
            _rect(200 - wide - 6, 40, 2 * wide + 12, 180, paint, wide),
            _rect(200 - wide, 48, 2 * wide, 164, pad, wide - 6),
        ]
        if head == "vent":
            out += [_rect(194, y, 12, 10, "#ffffff", 3, LW_DETAIL) for y in range(64, 200, 26)]
        step = 20 if head == "detangling" else 14
        xs = range(200 - wide + 14, 200 + wide - 8, step)
        pins = [(x, y) for y in range(66, 200, step) for x in xs
                if head != "vent" or abs(x - 200) > 10]  # fmt: skip
    if bristle == "mixed":
        out += [_ell(x, y, 3.5, 3.5, "#2e2e33" if (x + y) % 28 else tip, 1) for x, y in pins]
    else:
        out += [_ell(x, y, 3.5, 3.5, tip, 1) for x, y in pins]
    out.append(_highlight("M192,226 L192,346", 5, 0.45))
    return _label(out, label)


SHAPES = {"hair_dryer": hair_dryer, "hair_straightener": hair_straightener, "hairbrush": hairbrush}
register(SHAPES)
