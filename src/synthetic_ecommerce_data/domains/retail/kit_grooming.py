"""Oral care and shaving for the retail drawing kit (gen#957): toothbrushes, toothpaste, razors.

==========  ==============================================  =====================================
shape       draws                                           params
==========  ==============================================  =====================================
toothbrush  a toothbrush, upright: a handle in the SKU's    power (manual, electric, sonic,
            color whose body is drawn by ``power`` (a       battery), bristle (soft, medium,
            slim manual stick, a thick electric body with   extra soft, firm)
            a round head, a tall sonic body with a ring,
            a battery body with its end cap), and bristle
            tufts in the ``bristle``'s tone
toothpaste  a toothpaste tube standing on its cap: the      benefit (any word: printed), flavour
            label prints the product word over the          (mint, spearmint, peppermint, cool
            ``benefit``, and the stripe's tone is the       mint, eucalyptus, herbal)
            ``flavour``
razor       a razor, upright: a handle in the SKU's color   blades (2-blade to 6-blade), handle
            drawn by ``handle`` (a ribbed grip, a wide      (rubber grip, weighted, slim,
            weighted bar, a slim stick, a curved            ergonomic)
            ergonomic one) under a head with one line per
            blade
==========  ==============================================  =====================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a toothbrush's ``power``, a toothpaste's ``flavour`` or a razor's ``blades`` draws
what its title states (gen#512).
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
    _word,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The grey of a button, a cap and a blade.
GREY = "#5a5d63"
STEEL = "#b8bec6"
#: A toothbrush's bristle tufts, one tone per bristle.
TUFT = {"soft": "#f4f4f2", "medium": "#7fb8e0", "extra soft": "#f2d4e6", "firm": "#3a6fb0"}
#: A toothpaste tube's stripe, one tone per flavour.
STRIPE = {"mint": "#5fbf9a", "spearmint": "#3f9f6a", "peppermint": "#2f7f9f",
          "cool mint": "#7fc8e0", "eucalyptus": "#6f8f8a", "herbal": "#8aa05a"}  # fmt: skip


def toothbrush(
    paint: str,
    fill: Fill,
    label: str | None,
    power: str = "manual",
    bristle: str = "soft",
) -> list[str]:
    """A toothbrush, upright: the handle by ``power`` and the bristle tufts by ``bristle``."""
    tuft = TUFT.get(bristle, TUFT["soft"])
    if power == "manual":
        out = [
            _path("M190,350 L186,170 Q186,150 194,140 L196,100 L204,100 L206,140 "
                  "Q214,150 214,170 L210,350 Z", paint),  # fmt: skip
            _rect(186, 40, 28, 70, _tint(fill.base, 0.4), 12),
        ]
        out += [_rect(170, y, 16, 9, tuft, 3, 1) for y in range(48, 104, 12)]
        out.append(_highlight("M196,180 L194,330", 4, 0.45))
        return _label(out, label)
    width, top = {"electric": (48, 170), "sonic": (40, 140), "battery": (36, 160)}.get(
        power, (48, 170)
    )  # fmt: skip
    x = 200 - width / 2
    out = [
        _rect(x, top, width, 360 - top, paint, width / 2),
        _rect(194, 70, 12, top - 60, _tint(fill.base, 0.6), 4, LW_DETAIL),
        _ell(200, top + 50, 9, 9, GREY, LW_DETAIL),
    ]
    if power == "electric":
        out += [_ell(200, 62, 22, 22, _tint(fill.base, 0.6))]
        out += [_ell(182 + 9 * (i % 5), 54 + 8 * (i // 5), 3.5, 3.5, tuft, 1) for i in range(15)]
    elif power == "sonic":
        out += [_rect(186, 30, 28, 52, _tint(fill.base, 0.6), 12),
                _rect(x, top + 90, width, 10, STEEL, 2, LW_DETAIL),
                _ell(200, top + 74, 5, 5, GREY, LW_DETAIL)]  # fmt: skip
        out += [_rect(172, y, 14, 7, tuft, 3, 1) for y in range(36, 78, 10)]
    else:  # battery: a manual-style head, an end cap at the foot
        out += [_rect(188, 36, 24, 52, _tint(fill.base, 0.6), 10),
                _rect(x, 330, width, 30, GREY, 6, LW_DETAIL)]  # fmt: skip
        out += [_rect(174, y, 14, 7, tuft, 3, 1) for y in range(42, 84, 10)]
    out.append(_highlight(f"M{x + 8},{top + 20} L{x + 8},{340}", 5, 0.45))
    return _label(out, label)


def toothpaste(
    paint: str,
    fill: Fill,
    label: str | None,
    benefit: str = "",
    flavour: str = "mint",
) -> list[str]:
    """A toothpaste tube standing on its cap: the product word over the ``benefit`` on its
    label, and a stripe in the ``flavour``'s tone."""
    out = [
        _path("M140,40 L260,40 L262,56 L250,300 Q246,316 228,318 L172,318 Q154,316 150,300 "
              "L138,56 Z", paint),  # fmt: skip
        _rect(138, 36, 124, 14, _shade(fill.base, 0.15), 2, LW_DETAIL),
        _rect(170, 318, 60, 40, _shade(fill.base, 0.3), 6),
        _path("M147,96 L253,96 L251,128 L149,128 Z", STRIPE.get(flavour, GREY), LW_DETAIL),
    ]
    out += [_line(f"M{x},38 L{x},48", LW_DETAIL) for x in range(150, 256, 10)]
    if label:
        out.append(_word(label, 200, 180, 92, 20))
    if benefit:
        out.append(_word(benefit.title(), 200, 216, 92, 14, "#5a5f66"))
    out.append(_highlight("M156,70 L164,290", 5, 0.45))
    return out


def _blade_count(blades: str) -> int:
    head = blades.split("-")[0]
    return int(head) if head.isdigit() else 3


def razor(
    paint: str,
    fill: Fill,
    label: str | None,
    blades: str = "3-blade",
    handle: str = "rubber grip",
) -> list[str]:
    """A razor, upright: the handle by ``handle`` and the head's blades by ``blades``."""
    if handle == "weighted":
        out = [_rect(180, 124, 40, 236, paint, 10),
               _rect(180, 200, 40, 50, STEEL, 4, LW_DETAIL)]  # fmt: skip
    elif handle == "slim":
        out = [_rect(190, 120, 20, 240, paint, 10)]
    elif handle == "ergonomic":
        out = [_path("M190,120 Q172,200 186,280 Q194,340 200,360 L214,360 Q212,330 210,280 "
                     "Q222,200 210,120 Z", paint)]  # fmt: skip
    else:  # rubber grip
        out = [_rect(184, 120, 32, 240, paint, 14)]
        out += [_rect(184, y, 32, 8, _shade(fill.base, 0.35), 3, LW_DETAIL)
                for y in range(170, 300, 18)]  # fmt: skip
    n = _blade_count(blades)
    out += [
        _rect(194, 96, 12, 30, _shade(fill.base, 0.2), 3, LW_DETAIL),
        _rect(130, 52, 140, 52, _tint(fill.base, 0.5), 10),
    ]
    out += [_line(f"M140,{60 + i * 36 / n:.1f} L260,{60 + i * 36 / n:.1f}", 2.5, "", STEEL)
            for i in range(n)]  # fmt: skip
    out.append(_highlight("M192,140 L192,340", 4, 0.45))
    return _label(out, label)


SHAPES = {"toothbrush": toothbrush, "toothpaste": toothpaste, "razor": razor}
register(SHAPES)
