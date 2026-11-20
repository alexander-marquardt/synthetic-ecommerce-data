"""Facial cleansers, deodorants and nail polish for the retail drawing kit (gen#957).

===============  ===========================================  =====================================
shape            draws                                        params
===============  ===========================================  =====================================
facial_cleanser  a cleanser's pack, upright, in the pack's    texture (foaming, gel, oil, micellar,
                 color: the ``texture`` draws the pack (a     balm, clay), skin_type (any word:
                 foam pump bottle, a tube on its flip cap,    printed)
                 a slim oil pump bottle, a tall bottle with
                 a flip cap, a low jar, a tall jar with
                 grains), and the label prints the product
                 word over the ``skin_type``
deodorant        a deodorant, upright, in the pack's color:   applicator (roll-on, stick, spray,
                 the ``applicator`` draws the pack (a domed   gel), scent (unscented, citrus,
                 roll-on, an oval stick on its twist base, a  sandalwood, aloe vera, sea breeze,
                 can under its actuator, a clear gel stick    cedarwood)
                 with a window), with a band in the
                 ``scent``'s tone that prints the scent
nail_polish      a nail polish bottle, upright, the polish    finish (gloss, matte, shimmer,
                 in the SKU's color: the ``finish`` draws     glitter, metallic, gel effect), wear
                 the glass's sheen (a gloss streak, a flat    (quick dry, long wear, chip
                 coat, a few sparkles, many glitter flecks,   resistant, strengthening)
                 bright metal bands, a domed gel top), and
                 the ``wear`` draws the cap (a short wide
                 cap, a tall slim one, a ribbed one, one
                 with a ring)
===============  ===========================================  =====================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a cleanser's ``texture``, a deodorant's ``applicator`` or a polish's ``finish``
draws what its title states (gen#512).
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

#: The grey of a pump, a cap and a printed word.
GREY = "#5a5d63"
STEEL = "#b8bec6"
#: A deodorant's band, one tone per scent.
BAND = {"unscented": "#e8e8e4", "citrus": "#f2b53a", "sandalwood": "#a8714a",
        "aloe vera": "#7fbf6a", "sea breeze": "#5fa8d0", "cedarwood": "#7a5a3a"}  # fmt: skip
#: The bands dark enough that the scent is printed on them in white.
DARK_BANDS = frozenset({"sandalwood", "cedarwood"})


def _pump(x: float, top: float, nozzle: float) -> list[str]:
    """A pump on a bottle whose shoulder is at ``top``: a collar, a stem and a nozzle
    ``nozzle`` wide reaching right."""
    return [
        _rect(x - 20, top - 26, 40, 28, GREY, 4, LW_DETAIL),
        _rect(x - 6, top - 56, 12, 32, STEEL, 2, LW_DETAIL),
        _rect(x - 24, top - 72, 48 + nozzle, 16, GREY, 4, LW_DETAIL),
    ]


def facial_cleanser(
    paint: str,
    fill: Fill,
    label: str | None,
    texture: str = "foaming",
    skin_type: str = "",
) -> list[str]:
    """A facial cleanser's pack, upright: its form by ``texture``, its label printing the
    product word over the ``skin_type``."""
    lid = _shade(fill.base, 0.3)
    if texture == "gel":  # a squeeze tube standing on its flip cap
        out = [
            _path("M146,44 L254,44 L246,300 Q244,312 230,314 L170,314 Q156,312 154,300 Z", paint),
            _rect(144, 36, 112, 14, _shade(fill.base, 0.15), 2, LW_DETAIL),
            _rect(166, 314, 68, 44, lid, 10),
        ]
        out += [_line(f"M{x},38 L{x},48", LW_DETAIL) for x in range(154, 250, 12)]
        text = (180, 92)
    elif texture == "oil":  # a slim bottle under a long-nozzled pump
        out = [_rect(162, 140, 76, 220, paint, 14),
               _rect(184, 118, 32, 24, _tint(fill.base, 0.4), 4)]  # fmt: skip
        out += _pump(200, 120, 30)
        text = (240, 64)
    elif texture == "micellar":  # a tall bottle under a flip cap
        out = [
            _rect(146, 100, 108, 260, paint, 24),
            _rect(162, 62, 76, 42, lid, 8),
            _rect(170, 56, 30, 8, GREY, 2, LW_DETAIL),
        ]
        text = (230, 92)
    elif texture == "balm":  # a low jar under its lid
        out = [_rect(110, 230, 180, 130, paint, 16), _rect(104, 190, 192, 46, lid, 10)]
        text = (290, 150)
    elif texture == "clay":  # a tall jar, its lid, the grains of the clay at the rim
        out = [_rect(124, 170, 152, 190, paint, 14), _rect(118, 128, 164, 46, lid, 10)]
        out += [_ell(134 + 13 * i, 182 + 6 * (i % 2), 3, 3, GREY, 1) for i in range(11)]
        text = (270, 128)
    else:  # foaming: a round-shouldered bottle under a foam pump
        out = [_rect(148, 130, 104, 230, paint, 22)]
        out += _pump(200, 132, 18)
        text = (240, 88)
    cy, width = text
    if label:
        out.append(_word(label, 200, cy, width, 18))
    if skin_type:
        out.append(_word(f"{skin_type.title()} Skin", 200, cy + 30, width, 13, GREY))
    x = 120 if texture == "balm" else 160
    out.append(_highlight(f"M{x},{cy - 60} L{x + 6},{cy + 50}", 5, 0.45))
    return out


def deodorant(
    paint: str,
    fill: Fill,
    label: str | None,
    applicator: str = "roll-on",
    scent: str = "unscented",
) -> list[str]:
    """A deodorant, upright: its pack by ``applicator`` and a band in the ``scent``'s tone."""
    band = BAND.get(scent, BAND["unscented"])
    lid = _shade(fill.base, 0.3)
    if applicator == "stick":  # an oval stick on its twist base
        x, w, top = 146, 108, 100
        out = [_rect(x, top, w, 250, paint, 20), _rect(x, 64, w, 44, lid, 16),
               _ell(200, 352, 46, 9, GREY, LW_DETAIL)]  # fmt: skip
    elif applicator == "spray":  # a can under its actuator
        x, w, top = 156, 88, 120
        out = [_rect(x, top, w, 240, paint, 10),
               _path("M156,128 Q160,98 186,94 L214,94 Q240,98 244,128 Z", STEEL, LW_DETAIL),
               _rect(172, 50, 56, 46, lid, 8),
               _rect(222, 62, 12, 8, GREY, 2, LW_DETAIL)]  # fmt: skip
    elif applicator == "gel":  # a clear stick, the gel seen through a window
        x, w, top = 150, 100, 110
        out = [_rect(x, top, w, 250, paint, 12), _rect(x, 70, w, 44, lid, 10),
               _rect(176, 130, 48, 70, _tint("#9fd4e8", 0.3), 8, LW_DETAIL)]  # fmt: skip
    else:  # roll-on: a bottle under a tall domed cap
        x, w, top = 160, 80, 170
        out = [_rect(x, top, w, 190, paint, 30), _rect(x - 4, 60, w + 8, 116, lid, 40),
               _ell(200, 176, 30, 6, STEEL, LW_DETAIL)]  # fmt: skip
    out.append(_rect(x, 238, w, 34, band, 2, LW_DETAIL))
    ink = "#ffffff" if scent in DARK_BANDS else GREY
    out.append(_word(scent.title(), 200, 255, w - 12, 13, ink))
    if label:
        out.append(_word(label, 200, 300, w - 12, 15))
    out.append(_highlight(f"M{x + 10},{top + 20} L{x + 10},340", 5, 0.45))
    return out


def nail_polish(
    paint: str,
    fill: Fill,
    label: str | None,
    finish: str = "gloss",
    wear: str = "long wear",
) -> list[str]:
    """A nail polish bottle, upright: the glass's sheen by ``finish``, the cap by ``wear``."""
    out = [_rect(140, 196, 120, 160, paint, 22), _rect(176, 176, 48, 24, _tint(fill.base, 0.5), 4)]
    if wear == "quick dry":
        out.append(_rect(160, 120, 80, 58, GREY, 10))
    elif wear == "chip resistant":
        out.append(_rect(172, 70, 56, 108, GREY, 8))
        out += [_line(f"M{x},76 L{x},172", LW_DETAIL, "", STEEL) for x in range(182, 224, 9)]
    elif wear == "strengthening":
        out += [_rect(174, 80, 52, 98, GREY, 8), _rect(170, 150, 60, 12, STEEL, 3, LW_DETAIL)]
    else:  # long wear: a tall slim cap
        out.append(_rect(180, 52, 40, 126, GREY, 10))
    if finish == "matte":
        out.append(_rect(148, 206, 104, 140, _shade(fill.base, 0.12), 18, 0))
    elif finish == "shimmer":
        out += [_ell(166 + 17 * i, 236 + 22 * (i % 3), 3, 3, "#ffffff", 0.5) for i in range(5)]
    elif finish == "glitter":
        tones = ("#ffffff", "#f2d24a", "#c0c6ce")
        out += [_ell(152 + 9 * (i % 11), 216 + 11 * (i // 11) * 3 + 4 * (i % 3), 2.2, 2.2,
                     tones[i % 3], 0.4) for i in range(33)]  # fmt: skip
    elif finish == "metallic":
        out += [_rect(140, y, 120, 10, _tint(fill.base, 0.55), 2, 0) for y in (226, 266, 306)]
    elif finish == "gel effect":
        out += [_ell(200, 206, 58, 14, _tint(fill.base, 0.35), LW_DETAIL),
                _highlight("M154,226 Q200,214 246,226", 6, 0.7)]  # fmt: skip
    if finish not in ("matte",):
        out.append(_highlight("M154,218 L156,336", 5, 0.5))
    return _label(out, label)


SHAPES = {"facial_cleanser": facial_cleanser, "deodorant": deodorant, "nail_polish": nail_polish}
register(SHAPES)
