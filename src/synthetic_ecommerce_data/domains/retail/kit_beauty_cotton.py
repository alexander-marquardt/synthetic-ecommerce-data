"""The Beauty department's cotton shapes (gen#1112, slice 2).

===============  ============================================  ====================================
shape            draws                                         params
===============  ============================================  ====================================
cotton_pad_pack  a clear bag with a stack of pads seen through  pad_shape (round, oval, square),
                 its front: round, oval or square, quilted     pad_texture (quilted, smooth,
                 with a grid, smooth, or dotted to exfoliate   exfoliating)
cotton_bud_tub   a round tub with buds standing out of it: a   bud_stem (paper, bamboo), bud_tip
                 white paper stem or a ringed bamboo one, a    (standard, precision, safety)
                 rounded, a pointed or a bulb tip
cotton_wool_bag  a soft bag holding balls, a folded pleat or   wool_form (balls, pleat, roll),
                 a rolled sheet; a leaf mark for organic       cotton_grade (pure, organic)
===============  ============================================  ====================================

Each param's values are the lower-cased attribute values of the spec rows (``type_specs/
cotton_pads.py``, ``cotton_buds.py`` and ``cotton_wool.py``), so a derived style that swaps the
shape, the texture, the stem, the tip, the form or the grade draws what it states (gen#512). The
shapes join :data:`kit.SHAPES` when :func:`kit.register_all` imports this module, as every
``kit_*`` module.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

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

#: The white of cotton, the tan of a bamboo stem and the green of an organic leaf.
COTTON = "#fbfbf8"
BAMBOO = "#c9a46a"
LEAF = "#6fa86f"


def _pad(cx: float, cy: float, shape: str, texture: str) -> list[str]:
    """One cotton pad seen face on, its outline by ``shape`` and its face by ``texture``."""
    if shape == "square":
        out = [_rect(cx - 46, cy - 46, 92, 92, COTTON, 12)]
    elif shape == "oval":
        out = [_ell(cx, cy, 58, 38, COTTON)]
    else:
        out = [_ell(cx, cy, 48, 48, COTTON)]
    half_w, half_h = {"square": (40, 40), "oval": (50, 30)}.get(shape, (40, 40))
    if texture == "quilted":  # a diamond grid stitched into the face
        out.append(
            _line(
                " ".join(
                    f"M{cx + d - half_w / 2:g},{cy - half_h / 2:g} L{cx + d + half_w / 2:g},{cy + half_h / 2:g} "
                    f"M{cx + d + half_w / 2:g},{cy - half_h / 2:g} L{cx + d - half_w / 2:g},{cy + half_h / 2:g}"
                    for d in (-half_w / 2, 0, half_w / 2)
                ),
                LW_DETAIL,
                stroke="#c9c6bc",
            )
        )
    elif texture == "exfoliating":  # a raised dotted face
        out += [_ell(cx + dx, cy + dy, 3, 3, "#d9d5ca", LW_DETAIL)
                for dx in (-24, 0, 24) for dy in (-16, 0, 16)]  # fmt: skip
    return out


def cotton_pad_pack(
    paint: str,
    fill: Fill,
    label: str | None,
    pad_shape: str = "round",
    pad_texture: str = "quilted",
) -> list[str]:
    """A clear bag of cotton pads: a paper band in the pack's color and a stack seen through."""
    out = [
        _path(
            "M80,92 Q80,70 104,70 L296,70 Q320,70 320,92 L328,330 Q328,352 304,352 L96,352 Q72,352 72,330 Z",
            _tint(fill.base, 0.85),
        ),
        _rect(72, 100, 256, 52, paint, 4),
        _rect(150, 112, 100, 28, PAPER, 4, LW_DETAIL),
    ]
    for i, cy in enumerate((300, 286, 272)):  # the stack's edges below the front pad
        out.append(_line(f"M130,{cy} L270,{cy}", LW_DETAIL, stroke=_shade(COTTON, 0.15 + i * 0.05)))
    out += _pad(200, 222, pad_shape, pad_texture)
    out.append(_highlight("M90,170 L92,320", 5, 0.5))
    return _label(out, label)


def _bud(x: float, top: float, stem: str, tip: str) -> list[str]:
    """One bud standing up from the tub: its stem from ``top`` down, a tip at each end."""
    color = BAMBOO if stem == "bamboo" else COTTON
    out = [_rect(x - 3, top, 6, 120, color, 2, LW_DETAIL)]
    if stem == "bamboo":  # the nodes of a bamboo stem
        out.append(
            _line(
                f"M{x - 3},{top + 40} L{x + 3},{top + 40} M{x - 3},{top + 80} L{x + 3},{top + 80}",
                LW_DETAIL,
            )
        )
    if tip == "precision":  # a pointed tip for make-up
        out.append(
            _path(f"M{x - 8},{top + 4} Q{x},{top - 30} {x + 8},{top + 4} Z", COTTON, LW_DETAIL)
        )
    elif tip == "safety":  # a wide bulb that stops short of a baby's ear
        out.append(_ell(x, top - 4, 13, 16, COTTON, LW_DETAIL))
    else:
        out.append(_ell(x, top - 2, 8, 13, COTTON, LW_DETAIL))
    return out


def cotton_bud_tub(
    paint: str,
    fill: Fill,
    label: str | None,
    bud_stem: str = "paper",
    bud_tip: str = "standard",
) -> list[str]:
    """A round tub of cotton buds, a fan of buds standing out of its open top."""
    out: list[str] = []
    for i, x in enumerate((140, 170, 200, 230, 260)):
        out += _bud(x, 120 + abs(i - 2) * 14, bud_stem, bud_tip)
    out += [
        _path("M104,200 L296,200 L284,346 Q200,360 116,346 Z", paint),
        _ell(200, 200, 96, 18, _shade(fill.base, 0.2)),
        _rect(140, 250, 120, 40, PAPER, 4, LW_DETAIL),
        _highlight("M120,222 L130,334", 5, 0.4),
    ]
    return _label(out, label)


def cotton_wool_bag(
    paint: str,
    fill: Fill,
    label: str | None,
    wool_form: str = "balls",
    cotton_grade: str = "pure",
) -> list[str]:
    """A soft bag of cotton wool: balls, a folded pleat or a rolled sheet in its window."""
    out = [
        _path(
            "M92,96 Q92,74 116,74 L284,74 Q308,74 308,96 L318,332 Q318,354 294,354 L106,354 Q82,354 82,332 Z",
            paint,
        ),
        _rect(112, 140, 176, 180, _tint(fill.base, 0.85), 14, LW_DETAIL),
        _rect(140, 96, 120, 28, PAPER, 4, LW_DETAIL),
    ]
    if wool_form == "pleat":  # a long strip folded back and forth
        out.append(
            _path(
                "M128,170 L272,170 L262,200 L272,230 L262,260 L272,290 L128,290 L138,260 L128,230 L138,200 Z",
                COTTON,
                LW_DETAIL,
            )
        )
        out.append(
            _line(
                "M138,200 L262,200 M128,230 L272,230 M138,260 L262,260", LW_DETAIL, stroke="#c9c6bc"
            )
        )
    elif wool_form == "roll":  # a sheet rolled on itself, its spiral end on show
        out += [
            _rect(132, 196, 120, 80, COTTON, 10, LW_DETAIL),
            _ell(252, 236, 22, 40, COTTON, LW_DETAIL),
            _path(
                "M252,236 m-4,0 a4,6 0 1 1 8,0 a9,14 0 1 1 -18,0 a14,22 0 1 1 28,0",
                "none",
                LW_DETAIL,
            ),
        ]
    else:  # a heap of balls
        out += [_ell(cx, cy, 22, 20, COTTON, LW_DETAIL)
                for cx, cy in ((150, 290), (196, 292), (242, 290), (172, 254), (220, 254), (196, 218))]  # fmt: skip
    if cotton_grade == "organic":  # a leaf on the band
        out.append(_path("M268,98 Q290,94 292,116 Q270,122 268,98 Z", LEAF, LW_DETAIL))
    out.append(_highlight("M100,110 L104,330", 5, 0.4))
    return _label(out, label)


SHAPES = {
    "cotton_pad_pack": cotton_pad_pack,
    "cotton_bud_tub": cotton_bud_tub,
    "cotton_wool_bag": cotton_wool_bag,
}
register(SHAPES)
