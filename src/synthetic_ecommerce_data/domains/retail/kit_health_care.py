"""The Health department's eye-care, incontinence and mobility-aid shapes (gen#968, slice 3).

===============  ===============================================  ==============================
shape            draws                                            params
===============  ===============================================  ==============================
eye_drop_bottle  a carton in the box's color and, in front of     pack (dropper bottle,
                 it, a dropper bottle, a strip of single-dose     single-dose vials, eye wash)
                 vials, or a wash bottle with its eye bath
pad_pack         a soft pack with a pad on its front and one      absorbency (light, medium,
                 drop per absorbency step, a moon for overnight   heavy, overnight)
walking_stick    a walking stick on its rubber tip, its handle    handle (crook, derby, offset,
                 drawn by ``handle``                              t-handle)
===============  ===============================================  ==============================

Each param's values are the lower-cased attribute values of the spec rows (``type_specs/
eye_drops.py``, ``incontinence_pads.py`` and ``walking_sticks.py``), so a derived style that
swaps the pack, the absorbency or the handle draws what it states (gen#512). The shapes join
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
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The white of a dropper bottle and a pad, the blue of a drop, the grey of a stick's rubber tip.
BOTTLE = "#f6f6f3"
DROP = "#5aa3d8"
RUBBER = "#3a3d42"
#: How many drops a pack shows for each absorbency step.
DROPS = {"light": 1, "medium": 2, "heavy": 3, "overnight": 4}


def _carton(paint: str, fill: Fill) -> list[str]:
    """A tall carton with its top and side faces and a paper panel on its front."""
    return [
        _path("M80,110 L230,110 L258,88 L108,88 Z", _tint(fill.base, 0.35)),
        _path("M230,110 L258,88 L258,300 L230,322 Z", _shade(fill.base, 0.2)),
        _rect(80, 110, 150, 212, paint, 4),
        _rect(94, 130, 122, 36, PAPER, 4, LW_DETAIL),
    ]


def _drop(cx: float, cy: float, r: float, color: str = DROP) -> str:
    """A falling drop, ``r`` its round foot's radius."""
    return _path(
        f"M{cx:g},{cy - 2.2 * r:g} Q{cx + r * 1.1:g},{cy - 0.4 * r:g} {cx + r:g},{cy + 0.2 * r:g} "
        f"A{r:g},{r:g} 0 0 1 {cx - r:g},{cy + 0.2 * r:g} Q{cx - r * 1.1:g},{cy - 0.4 * r:g} {cx:g},{cy - 2.2 * r:g} Z",
        color,
        LW_DETAIL,
    )


def eye_drop_bottle(
    paint: str, fill: Fill, label: str | None, pack: str = "dropper bottle"
) -> list[str]:
    """A carton of eye care and, in front of it, what the ``pack`` holds."""
    out = _carton(paint, fill)
    if pack == "single-dose vials":  # a strip of five twist-top vials
        for i in range(5):
            x = 150 + i * 38
            out += [
                _rect(x, 236, 30, 96, BOTTLE, 8),
                _path(
                    f"M{x + 8},236 L{x + 8},214 L{x + 22},214 L{x + 22},236",
                    _tint(fill.base, 0.5),
                    LW_DETAIL,
                ),
            ]
        out.append(_line("M150,300 L332,300", LW_DETAIL))
    elif pack == "eye wash":  # a tall wash bottle and its eye bath cup
        out += [
            _path(
                "M236,200 L236,172 L276,172 L276,200 Q300,210 300,236 L300,340 L212,340 L212,236 Q212,210 236,200 Z",
                BOTTLE,
            ),
            _rect(230, 150, 52, 26, paint, 4),
            _rect(222, 254, 68, 50, _tint(fill.base, 0.6), 4, LW_DETAIL),
            _path("M310,300 L356,300 L346,344 L320,344 Z", _tint(DROP, 0.5)),
            _ell(333, 300, 23, 6, _tint(DROP, 0.7), LW_DETAIL),
        ]
    else:  # a squat dropper bottle with a tapered nozzle and a drop falling from it
        out += [
            _path(
                "M228,236 Q228,220 248,216 L292,216 Q312,220 312,236 L312,334 Q312,344 302,344 L238,344 Q228,344 228,334 Z",
                BOTTLE,
            ),
            _rect(246, 186, 48, 32, paint, 4),
            _path("M258,186 L264,150 L276,150 L282,186 Z", BOTTLE, LW_DETAIL),
            _rect(236, 262, 68, 44, _tint(fill.base, 0.6), 4, LW_DETAIL),
            _drop(270, 128, 7),
        ]
    out.append(_highlight("M88,122 L88,310", 5, 0.4))
    return _label(out, label)


def pad_pack(paint: str, fill: Fill, label: str | None, absorbency: str = "light") -> list[str]:
    """A soft pack of pads: a pad on its front and a drop for each absorbency step."""
    out = [
        _path(
            "M70,96 Q70,72 96,72 L304,72 Q330,72 330,96 L336,320 Q336,348 308,348 L92,348 Q64,348 64,320 Z",
            paint,
        ),
        _line("M78,92 L322,92", LW_DETAIL),
        _path(
            "M150,120 Q200,104 250,120 Q262,180 246,226 Q262,272 250,318 Q200,334 150,318 Q138,272 154,226 Q138,180 150,120 Z",
            BOTTLE,
        ),
        _path(
            "M178,150 Q200,142 222,150 Q230,190 220,226 Q230,262 222,302 Q200,310 178,302 Q170,262 180,226 Q170,190 178,150 Z",
            _tint(DROP, 0.8),
            LW_DETAIL,
        ),
    ]
    steps = DROPS.get(absorbency, 1)
    out += [_drop(96, 136 + i * 44, 9) for i in range(steps)]
    if absorbency == "overnight":  # a crescent moon above the drops
        out.append(
            _path("M300,112 A22,22 0 1 0 300,156 A26,26 0 0 1 300,112 Z", "#f2d36b", LW_DETAIL)
        )
    out.append(_highlight("M80,110 L80,320", 5, 0.4))
    return _label(out, label)


def walking_stick(paint: str, fill: Fill, label: str | None, handle: str = "crook") -> list[str]:
    """A walking stick on its rubber tip, with a crook, derby, offset or T handle."""
    grip = _shade(fill.base, 0.3)
    if handle == "derby":  # a shaped handle with a short tail under the hand
        top = [
            _path(
                "M196,110 Q196,74 236,74 L292,74 Q316,74 316,96 Q316,112 300,112 L254,112 Q240,112 232,126 L232,138 L196,138 Z",
                grip,
            )
        ]
    elif handle == "offset":  # the shaft bends out so the grip sits over it
        top = [
            _path(
                "M196,190 L196,160 Q196,130 226,120 L240,116 L240,136 L232,140 Q222,146 222,166 L222,190 Z",
                paint,
            ),
            _rect(226, 100, 104, 26, grip, 13),
        ]
    elif handle == "t-handle":  # a straight grip across the top
        top = [_rect(140, 96, 140, 28, grip, 14), _rect(196, 120, 26, 24, grip, 4, LW_DETAIL)]
    else:  # a crook: the round hook of a classic cane
        top = [
            _path(
                "M196,150 L196,120 A50,50 0 0 1 296,120 L296,150 L270,150 L270,120 A24,24 0 0 0 222,120 L222,150 Z",
                paint,
            )
        ]
    out = [
        *top,
        _rect(196, 136, 26, 196, paint, 6),
        _rect(192, 330, 34, 26, RUBBER, 6),
        _highlight("M203,150 L203,320", 4, 0.45),
    ]
    return _label(out, label)


SHAPES = {
    "eye_drop_bottle": eye_drop_bottle,
    "pad_pack": pad_pack,
    "walking_stick": walking_stick,
}
register(SHAPES)
