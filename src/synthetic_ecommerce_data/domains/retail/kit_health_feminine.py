"""The Health department's feminine-care shapes (gen#1112, slice 1).

=================  =============================================  ==================================
shape              draws                                          params
=================  =============================================  ==================================
sanitary_pad_pack  a soft pack with a pad on its front, its       absorbency (light, regular, long,
                   wings out or not, a thin or a thick edge, one   super, overnight), wings (with
                   drop per absorbency step, a moon overnight     wings, without wings), thickness
                                                                  (ultra thin, maxi)
tampon_box         a carton with a tampon in front: in a          absorbency (light, regular, super,
                   plastic or a cardboard applicator, or bare     super plus), applicator (plastic
                   with its cord; one drop per absorbency step    applicator, cardboard applicator,
                                                                  non-applicator)
liner_pack         a flat box with a liner in front, its length   length (regular, long, extra
                   drawn to scale; a sprig for a fresh scent,     long), scent (unscented, fresh
                   an aloe leaf for aloe                          scent, aloe)
=================  =============================================  ==================================

Each param's values are the lower-cased attribute values of the spec rows (``type_specs/
sanitary_pads.py``, ``tampons.py`` and ``panty_liners.py``), so a derived style that swaps the
absorbency, the wings, the applicator or the length draws what it states (gen#512). The shapes join
:data:`kit.SHAPES` when :func:`kit.register_all` imports this module, as every ``kit_*`` module.
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
from synthetic_ecommerce_data.domains.retail.kit_health_care import BOTTLE, DROP, _carton, _drop
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: How many drops a pack shows for each absorbency step.
PAD_DROPS = {"light": 1, "regular": 2, "long": 3, "super": 4, "overnight": 5}
TAMPON_DROPS = {"light": 1, "regular": 2, "super": 3, "super plus": 4}
#: A liner's half-length in the drawing for each length.
LINER_HALF = {"regular": 70, "long": 92, "extra long": 112}
#: The beige of a cardboard applicator and the pink of a tampon's cord.
CARD = "#d8c29a"
CORD = "#c98aa0"
MOON = "#f2d36b"


def sanitary_pad_pack(
    paint: str,
    fill: Fill,
    label: str | None,
    absorbency: str = "regular",
    wings: str = "with wings",
    thickness: str = "ultra thin",
) -> list[str]:
    """A soft pack of sanitary pads: a pad on its front, winged or not, thin or thick."""
    out = [
        _path(
            "M70,96 Q70,72 96,72 L304,72 Q330,72 330,96 L336,320 Q336,348 308,348 L92,348 Q64,348 64,320 Z",
            paint,
        ),
        _line("M78,92 L322,92", LW_DETAIL),
    ]
    if wings == "with wings":  # two tabs that fold round the gusset
        out += [
            _path("M154,196 L112,184 Q100,226 112,268 L154,256 Z", BOTTLE, LW_DETAIL),
            _path("M246,196 L288,184 Q300,226 288,268 L246,256 Z", BOTTLE, LW_DETAIL),
        ]
    edge = 14 if thickness == "maxi" else 5  # the pad's side edge: a thick band or a thin line
    out += [
        _path(
            f"M150,{120 + edge} Q200,{104 + edge} 250,{120 + edge} Q262,{180 + edge} 246,{226 + edge} Q262,{272 + edge} 250,{318 + edge} Q200,{334 + edge} 150,{318 + edge} Q138,{272 + edge} 154,{226 + edge} Q138,{180 + edge} 150,{120 + edge} Z",
            _shade(BOTTLE, 0.12),
            LW_DETAIL,
        ),
        _path(
            "M150,120 Q200,104 250,120 Q262,180 246,226 Q262,272 250,318 Q200,334 150,318 Q138,272 154,226 Q138,180 150,120 Z",
            BOTTLE,
        ),
        _path(
            "M178,150 Q200,142 222,150 Q230,190 220,226 Q230,262 222,302 Q200,310 178,302 Q170,262 180,226 Q170,190 178,150 Z",
            _tint(fill.base, 0.75),
            LW_DETAIL,
        ),
    ]
    out += [_drop(96, 128 + i * 40, 8) for i in range(PAD_DROPS.get(absorbency, 2))]
    if absorbency == "overnight":  # a crescent moon above the drops
        out.append(_path("M300,112 A22,22 0 1 0 300,156 A26,26 0 0 1 300,112 Z", MOON, LW_DETAIL))
    out.append(_highlight("M80,110 L80,320", 5, 0.4))
    return _label(out, label)


def tampon_box(
    paint: str,
    fill: Fill,
    label: str | None,
    absorbency: str = "regular",
    applicator: str = "plastic applicator",
) -> list[str]:
    """A carton of tampons and, in front of it, one tampon as the pack sells it."""
    out = _carton(paint, fill)
    out += [_drop(110 + i * 30, 200, 8) for i in range(TAMPON_DROPS.get(absorbency, 2))]
    if applicator == "non-applicator":  # a bare cotton tampon and its cord
        out += [
            _rect(262, 196, 40, 104, BOTTLE, 18),
            _line("M270,220 L294,220 M270,244 L294,244 M270,268 L294,268", LW_DETAIL),
            _line("M282,300 Q276,326 286,350", 2.4, stroke=CORD),
        ]
    elif applicator == "cardboard applicator":  # two straight card tubes, one in the other
        out += [
            _rect(262, 170, 40, 100, CARD, 4),
            _rect(268, 268, 28, 70, _shade(CARD, 0.12), 3),
            _line("M262,206 L302,206", LW_DETAIL),
            _line("M282,338 L282,356", 2.4, stroke=CORD),
        ]
    else:  # a smooth plastic barrel with a rounded tip, a ringed grip and a plunger
        out += [
            _path("M262,270 L262,186 Q262,164 282,160 Q302,164 302,186 L302,270 Z", _tint(fill.base, 0.55)),
            _rect(266, 268, 32, 30, _tint(fill.base, 0.3), 6),
            _line("M268,276 L296,276 M268,284 L296,284 M268,292 L296,292", LW_DETAIL),
            _rect(274, 296, 16, 46, _tint(fill.base, 0.65), 4),
            _highlight("M270,186 L270,262", 4, 0.5),
        ]
    return _label(out, label)


def liner_pack(
    paint: str,
    fill: Fill,
    label: str | None,
    length: str = "regular",
    scent: str = "unscented",
) -> list[str]:
    """A flat box of panty liners with one liner in front, drawn to its length."""
    half = LINER_HALF.get(length, 70)
    out = [
        _path("M58,138 L314,138 L342,114 L86,114 Z", _tint(fill.base, 0.35)),
        _path("M314,138 L342,114 L342,316 L314,340 Z", _shade(fill.base, 0.2)),
        _rect(58, 138, 256, 202, paint, 6),
        _rect(76, 156, 88, 28, PAPER, 4, LW_DETAIL),
        _ell(186, 240, half, 34, BOTTLE),
        _ell(186, 240, half - 16, 20, _tint(DROP, 0.8), LW_DETAIL),
        _line(f"M{186 - half + 10},240 L{186 + half - 10},240", LW_DETAIL),
    ]
    if scent == "fresh scent":  # a sprig of leaves on the box's corner
        out += [
            _line("M286,320 Q276,290 292,262", 2.4),
            _ell(278, 290, 9, 5, "#6fb37a", LW_DETAIL),
            _ell(296, 278, 9, 5, "#6fb37a", LW_DETAIL),
        ]
    elif scent == "aloe":  # a spiked aloe leaf on the box's corner
        out.append(_path("M282,330 Q270,290 292,248 Q296,292 290,330 Z", "#7fb38a", LW_DETAIL))
    out.append(_highlight("M68,150 L68,326", 5, 0.4))
    return _label(out, label)


SHAPES = {
    "sanitary_pad_pack": sanitary_pad_pack,
    "tampon_box": tampon_box,
    "liner_pack": liner_pack,
}
register(SHAPES)
