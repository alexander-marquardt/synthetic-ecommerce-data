"""Pet food and litter for the retail drawing kit (gen#967): bags, pouches, trays, tins.

============  ===============================================  =================================
shape         draws                                            params
============  ===============================================  =================================
dry_pet_food  a stand-up bag in the pack's color, its crimped  animal (dog, cat)
              seal, a paw on the front and a window of a bowl
              of kibble: bones for a dog, fish for a cat
wet_pet_food  one item of the pack: by ``pack_format`` a       pack_format (pouches, trays,
              pouch, a peel-lid tray or a ring-pull tin, each  tins), animal (dog, cat)
              with a paw on its label
cat_litter    a bag with a carry handle and a window that      litter_type (clumping clay,
              shows its granules: clay grains, crystals,       non-clumping clay, silica crystal,
              wood pellets, paper pellets or corn grains       wood pellet, recycled paper,
                                                               clumping corn)
============  ===============================================  =================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a pack's format or a litter's type draws what it states (gen#512). The drawings are
original and drawn by code (ruling 2026-11-02, gen#102).
"""

# ruff: noqa: E501 -- SVG paths read better whole than wrapped (prototype only).

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

#: Kibble, a tray's foil and a tin's steel.
KIBBLE = "#9a6a3c"
FOIL = "#c3c7cd"
#: The granules of each litter: (fill, form). A form is how one granule is drawn.
GRAINS = {
    "crystal": ("#cfe6f2", "diamond"),
    "pellet": ("#c9a46a", "rod"),
    "paper": ("#e4e1d8", "rod"),
    "corn": ("#e8c95a", "grain"),
}
CLAY = ("#b9b4ab", "grain")


def _paw(cx: float, cy: float, s: float, ink: str) -> list[str]:
    """A paw print: one pad and four toes, ``s`` across the pad."""
    out = [_ell(cx, cy, s * 0.55, s * 0.45, ink, LW_DETAIL)]
    for dx, dy in ((-0.62, -0.62), (-0.22, -0.95), (0.22, -0.95), (0.62, -0.62)):
        out.append(_ell(cx + dx * s, cy + dy * s, s * 0.18, s * 0.24, ink, LW_DETAIL))
    return out


def _kibble(x: float, y: float, animal: str) -> str:
    """One piece of kibble: a small bone for a dog, a small fish for a cat."""
    if animal == "cat":
        return _path(f"M{x - 9},{y} Q{x - 2},{y - 7} {x + 5},{y} L{x + 10},{y - 5} "
                     f"L{x + 10},{y + 5} L{x + 5},{y} Q{x - 2},{y + 7} {x - 9},{y} Z",
                     KIBBLE, LW_DETAIL)  # fmt: skip
    return _path(f"M{x - 8},{y - 4} L{x + 8},{y - 4} Q{x + 13},{y - 8} {x + 12},{y} "
                 f"Q{x + 13},{y + 8} {x + 8},{y + 4} L{x - 8},{y + 4} Q{x - 13},{y + 8} "
                 f"{x - 12},{y} Q{x - 13},{y - 8} {x - 8},{y - 4} Z", KIBBLE, LW_DETAIL)  # fmt: skip


def dry_pet_food(paint: str, fill: Fill, label: str | None, animal: str = "dog") -> list[str]:
    """A stand-up bag of dry food: the body, a crimped top seal, a paw and a bowl of kibble."""
    out = [
        _path("M112,92 L288,92 L306,352 L94,352 Z", paint),
        _rect(106, 58, 188, 36, _shade(fill.base, 0.2), 4),
    ]
    out += [_line(f"M{x},62 L{x},90", LW_DETAIL) for x in range(116, 290, 12)]
    out.append(_rect(142, 176, 116, 120, PAPER, 10, LW_DETAIL))
    out.append(_path("M158,262 L242,262 Q238,286 200,288 Q162,286 158,262 Z", _tint(fill.base, 0.4)))
    out += [_kibble(x, y, animal) for x, y in ((178, 252), (200, 246), (222, 252), (189, 236), (211, 234))]
    out += _paw(200, 136, 22, _tint(fill.base, 0.65))
    out.append(_highlight("M124,110 L112,330", 6, 0.35))
    return _label(out, label)


def _pouch(paint: str, fill: Fill) -> list[str]:
    out = [
        _path("M132,72 L268,72 L274,344 Q200,356 126,344 Z", paint),
        _rect(132, 72, 136, 22, _shade(fill.base, 0.2), 3, LW_DETAIL),
        _path("M262,104 L274,110 L262,116 Z", PAPER, LW_DETAIL),
    ]
    out.append(_highlight("M144,110 L140,330", 5, 0.4))
    return out


def _tray(paint: str, fill: Fill) -> list[str]:
    return [
        _path("M88,232 L312,232 L292,320 L108,320 Z", FOIL),
        _line("M98,276 L302,276", LW_DETAIL),
        _path("M80,218 L320,218 L312,236 L88,236 Z", paint),
        _path("M300,218 L330,204 L336,214 L314,226 Z", _shade(fill.base, 0.25), LW_DETAIL),
    ]


def _tin(paint: str, fill: Fill) -> list[str]:
    return [
        _path("M118,140 L282,140 L282,318 Q200,342 118,318 Z", FOIL),
        _path("M118,170 L282,170 L282,296 Q200,318 118,296 Z", paint),
        _ell(200, 140, 82, 20, _tint(FOIL, 0.3)),
        _ell(200, 140, 64, 14, FOIL, LW_DETAIL),
        _ell(176, 138, 16, 7, _shade(FOIL, 0.2), LW_DETAIL),
    ]


#: The one item a wet food's pack holds, by its format, and where its label's paw sits.
WET = {"pouches": (_pouch, (200, 220, 26)), "trays": (_tray, (200, 196, 0)),
       "tins": (_tin, (200, 232, 24))}  # fmt: skip


def wet_pet_food(
    paint: str, fill: Fill, label: str | None, pack_format: str = "pouches", animal: str = "dog"
) -> list[str]:
    """One item of a wet food's pack: a pouch, a peel-lid tray or a ring-pull tin."""
    draw, (cx, cy, s) = WET.get(pack_format, WET["pouches"])
    out = draw(paint, fill)
    if s:
        out.append(_ell(cx, cy, s * 1.6, s * 1.6, PAPER, LW_DETAIL))
        out += _paw(cx, cy + 6, s * 0.8, _shade(fill.base, 0.1))
    if animal == "cat" and pack_format == "trays":
        out.append(_kibble(200, 296, animal))
    return _label(out, label)


def _granules(litter_type: str, x0: float, y0: float, x1: float, y1: float) -> list[str]:
    """The granules a litter's window shows, in rows across the window."""
    color, form = next((g for k, g in GRAINS.items() if k in litter_type), CLAY)
    out = []
    for i, y in enumerate(range(int(y0) + 12, int(y1) - 6, 16)):
        for x in range(int(x0) + 12 + (i % 2) * 8, int(x1) - 8, 18):
            if form == "diamond":
                out.append(_path(f"M{x},{y - 6} L{x + 6},{y} L{x},{y + 6} L{x - 6},{y} Z", color, 1))
            elif form == "rod":
                out.append(_rect(x - 7, y - 3, 14, 7, color, 3, 1))
            else:
                out.append(_ell(x, y, 5, 4, color, 1))
    return out


def cat_litter(
    paint: str, fill: Fill, label: str | None, litter_type: str = "clumping clay"
) -> list[str]:
    """A bag of litter: the body, a cut-out carry handle and a window of its granules."""
    out = [
        _rect(100, 62, 200, 290, paint, 14),
        _rect(170, 78, 60, 20, PAPER, 10, LW_DETAIL),
        _rect(132, 196, 136, 124, PAPER, 8, LW_DETAIL),
    ]
    out += _granules(litter_type, 132, 196, 268, 320)
    out += _paw(200, 150, 20, _tint(fill.base, 0.6))
    out.append(_highlight("M114,90 L114,330", 6, 0.35))
    return _label(out, label)


SHAPES = {"dry_pet_food": dry_pet_food, "wet_pet_food": wet_pet_food, "cat_litter": cat_litter}
register(SHAPES)
