"""The Beauty department's bath and shaving shapes (gen#1112, slice 3).

====================  ==========================================  ================================
shape                 draws                                       params
====================  ==========================================  ================================
body_wash_bottle      a tall bottle under a flip cap, or a pump   wash_finish (creamy, foaming,
                      for a foaming wash; a window shows the      exfoliating, silky), scent (any
                      wash (a cream, bubbles, grains, a sheen),   word: printed on the band)
                      and a band prints the scent
razor_cartridge_pack  a card with a clear blister of four         blades (3-blade, 4-blade,
                      cartridges: each head holds its blades and  5-blade), cartridge_strip (aloe,
                      a lubricating strip in the strip's tone     shea, charcoal, cooling)
shave_gel_can         a tall can under its actuator, a band in    scent (any word: printed),
                      the scent's tone that prints the scent,     skin_type (sensitive, normal,
                      and the skin type printed below it          dry: printed with a mark)
====================  ==========================================  ================================

Each param's values are the lower-cased attribute values of the spec rows (``type_specs/
shower_gel.py``, ``razor_cartridges.py`` and ``shave_gel.py``), so a derived style that swaps the
finish, the scent, the blade count, the strip or the skin type draws what it states (gen#512).
The shapes join :data:`kit.SHAPES` when :func:`kit.register_all` imports this module, as every
``kit_*`` module.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

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

#: The grey of a pump, a cap and a printed word, and the steel of a can's shoulder.
GREY = "#5a5d63"
STEEL = "#b8bec6"
#: A cartridge's lubricating strip, one tone per strip.
STRIP = {"aloe": "#7fbf6a", "shea": "#efe2c4", "charcoal": "#3a3a3c", "cooling": "#7fc6e6"}
#: A shave gel's scent band, one tone per scent; another scent takes the pale default.
SCENT_BAND = {"aloe vera": "#7fbf6a", "menthol": "#7fd3c6", "sandalwood": "#a8714a",
              "unscented": "#e8e8e4", "coconut": "#efe8d8"}  # fmt: skip
DARK = frozenset({"sandalwood"})


def _window(finish: str) -> list[str]:
    """The window of a body wash bottle, showing the wash by ``finish``."""
    if finish == "foaming":  # bubbles
        return [_rect(166, 140, 68, 64, "#f4f7fa", 10, LW_DETAIL),
                *(_ell(cx, cy, r, r, "#ffffff", LW_DETAIL)
                  for cx, cy, r in ((184, 160, 9), (212, 156, 7), (196, 184, 11), (220, 186, 6)))]  # fmt: skip
    if finish == "exfoliating":  # a clear gel holding grains
        return [_rect(166, 140, 68, 64, "#e6f0e8", 10, LW_DETAIL),
                *(_ell(cx, cy, 3, 3, "#a8714a", LW_DETAIL)
                  for cx in (178, 194, 210, 226) for cy in (154, 172, 190))]  # fmt: skip
    if finish == "silky":  # a pearly sheen in waves
        return [_rect(166, 140, 68, 64, "#ece6f2", 10, LW_DETAIL),
                _line("M172,158 Q186,148 200,158 T228,158 M172,176 Q186,166 200,176 T228,176 "
                      "M172,194 Q186,184 200,194 T228,194", LW_DETAIL, stroke="#9a8ab6")]  # fmt: skip
    return [_rect(166, 140, 68, 64, "#f4efe6", 10, LW_DETAIL)]  # creamy: an opaque cream


def body_wash_bottle(
    paint: str,
    fill: Fill,
    label: str | None,
    scent: str = "unscented",
    wash_finish: str = "creamy",
) -> list[str]:
    """A body wash bottle: a pump for a foaming wash, a flip cap else, a window by the finish
    and a band that prints the scent."""
    lid = _shade(fill.base, 0.3)
    out = [_path("M150,120 Q150,104 166,104 L234,104 Q250,104 250,120 L256,350 Q256,362 244,362 "
                 "L156,362 Q144,362 144,350 Z", paint)]  # fmt: skip
    if wash_finish == "foaming":  # a pump head on its stem
        out += [_rect(190, 60, 20, 46, GREY, 3), _rect(176, 46, 56, 16, GREY, 5),
                _rect(228, 48, 30, 10, GREY, 3, LW_DETAIL)]  # fmt: skip
    else:  # a flip cap
        out += [_rect(164, 70, 72, 36, lid, 10), _line("M168,82 L232,82", LW_DETAIL)]
    out += _window(wash_finish)
    out += [_rect(150, 226, 100, 30, _tint(fill.base, 0.6), 2, LW_DETAIL),
            _word(scent.title(), 200, 241, 88, 13, GREY)]  # fmt: skip
    out.append(_highlight("M156,130 L158,340", 5, 0.45))
    return _label(out, label)


def _cartridge(cx: float, cy: float, blades: int, strip: str) -> list[str]:
    """One cartridge head seen face on: its blades and its strip on top."""
    out = [_rect(cx - 44, cy - 26, 88, 52, "#3a3d42", 8, LW_DETAIL),
           _rect(cx - 40, cy - 23, 80, 8, STRIP.get(strip, STRIP["aloe"]), 2, LW_DETAIL)]  # fmt: skip
    step = 34 / max(blades, 1)
    out.append(_line(" ".join(f"M{cx - 36:g},{cy - 10 + i * step:.1f} L{cx + 36:g},{cy - 10 + i * step:.1f}"
                              for i in range(blades)), 1.6, stroke="#d0d6dc"))  # fmt: skip
    return out


def razor_cartridge_pack(
    paint: str,
    fill: Fill,
    label: str | None,
    blades: str = "3-blade",
    cartridge_strip: str = "aloe",
) -> list[str]:
    """A blister card of four razor cartridges, each with its blades and strip."""
    count = int(blades.split("-")[0]) if blades[:1].isdigit() else 3
    out = [_rect(110, 56, 180, 306, paint, 14), _ell(200, 78, 16, 6, "#ffffff", LW_DETAIL),
           _rect(124, 104, 152, 214, _tint("#dfe8ee", 0.4), 12, LW_DETAIL)]  # fmt: skip
    for cx, cy in ((158, 150), (242, 150), (158, 266), (242, 266)):
        out += _cartridge(cx, cy, count, cartridge_strip)
    out += [_rect(146, 328, 108, 24, "#ffffff", 4, LW_DETAIL), _word(blades.upper(), 200, 340, 96, 14, GREY)]
    out.append(_highlight("M130,116 L132,306", 4, 0.4))
    return _label(out, label)


def shave_gel_can(
    paint: str,
    fill: Fill,
    label: str | None,
    scent: str = "unscented",
    skin_type: str = "normal",
) -> list[str]:
    """A shave gel can under its actuator: a band in the scent's tone that prints the scent, and
    the skin type printed below it with its mark (a feather, a drop or a circle)."""
    band = SCENT_BAND.get(scent, "#ecebe6")
    lid = _shade(fill.base, 0.3)
    out = [_rect(148, 120, 104, 240, paint, 10),
           _path("M148,128 Q152,96 180,92 L220,92 Q248,96 252,128 Z", STEEL, LW_DETAIL),
           _rect(176, 50, 48, 44, lid, 8), _rect(222, 60, 16, 8, GREY, 2, LW_DETAIL),
           _rect(148, 196, 104, 34, band, 2, LW_DETAIL),
           _word(scent.title(), 200, 213, 92, 13, "#ffffff" if scent in DARK else GREY)]  # fmt: skip
    if skin_type == "sensitive":  # a feather
        out.append(_path("M200,246 Q214,258 204,280 Q196,268 200,246 Z", "#ffffff", LW_DETAIL))
    elif skin_type == "dry":  # a drop
        out.append(_path("M200,246 Q188,264 188,270 A12,12 0 0 0 212,270 Q212,264 200,246 Z", "#7fc6e6", LW_DETAIL))
    else:  # a plain circle
        out.append(_ell(200, 264, 11, 11, "#ffffff", LW_DETAIL))
    out.append(_word(f"{skin_type.title()} Skin", 200, 300, 92, 12, GREY))
    out.append(_highlight("M158,140 L160,346", 5, 0.45))
    return _label(out, label)


SHAPES = {
    "body_wash_bottle": body_wash_bottle,
    "razor_cartridge_pack": razor_cartridge_pack,
    "shave_gel_can": shave_gel_can,
}
register(SHAPES)
