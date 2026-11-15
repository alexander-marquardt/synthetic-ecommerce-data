"""Pet food and litter for the retail drawing kit (gen#967): bags, pouches, trays, tins.

============  ===============================================  =================================
shape         draws                                            params
============  ===============================================  =================================
dry_pet_food  a stand-up bag in the pack's color, its crimped  animal (dog, cat), life_stage,
              seal, a paw on the front and a window of a bowl  flavor, breed_size (a dog's),
              of kibble: bones for a dog, fish for a cat       special_need (a cat's)
wet_pet_food  one item of the pack: by ``pack_format`` a       pack_format (pouches, trays,
              pouch, a peel-lid tray or a ring-pull tin, each  tins), animal (dog, cat),
              with a paw on its label                          life_stage, flavor
cat_litter    a bag with a carry handle and a window that      litter_type (clumping clay,
              shows its granules: clay grains, crystals,       non-clumping clay, silica crystal,
              wood pellets, paper pellets or corn grains       wood pellet, recycled paper,
                                                               clumping corn), scent
============  ===============================================  =================================

What the pack says is drawn on it (gen#967), so two styles of one leaf and price read apart on a
results grid: the ``life_stage`` as a row of pips (one for a puppy or a kitten, two for an adult,
three for a senior), the ``flavor`` as a band in its meat's and its side's inks, a dog's
``breed_size`` as the size of the kibble, a cat's ``special_need`` as an emblem beside the paw,
and a litter's ``scent`` as a sprig in the scent's ink (none when it is unscented).

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes a pack's format or a litter's type draws what it states (gen#512). The drawings are
original and drawn by code (ruling 2026-11-02, gen#102).
"""

# ruff: noqa: E501 -- SVG paths read better whole than wrapped (prototype only).

from __future__ import annotations

import zlib

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
#: A flavor's first ink: the meat or the fish it names, by the first word of this table it holds.
MEAT_INKS = {
    "chicken": "#e0a43a", "turkey": "#a8643a", "duck": "#6b7a3a", "lamb": "#d8b8a0",
    "beef": "#8a2a2a", "salmon": "#f08a6a", "tuna": "#5a7a9a", "fish": "#b8c8d8",
    "rabbit": "#9a8a7a", "venison": "#6a3a2a", "pork": "#e8a0a0", "trout": "#c87a5a",
    "cod": "#dcdcd0", "sardine": "#7a8aa0", "prawn": "#f0a080", "ocean": "#3a6a9a",
}  # fmt: skip
#: A flavor's second ink: the side it names, or its gravy, jelly or loaf.
SIDE_INKS = {
    "sweet potato": "#d9772f", "potato": "#d9b56a", "rice": "#f2ead8", "pea": "#7ab34a",
    "vegetable": "#4f9a3a", "gravy": "#6a3a1a", "jelly": "#c9a0c0", "loaf": "#a07a5a",
    "pumpkin": "#e8902a", "carrot": "#f07a2a", "oat": "#e0d0a0", "barley": "#c8b070",
    "sauce": "#b04a3a", "pate": "#c89a8a",
}  # fmt: skip
#: Inks a flavor this table does not name takes, by a stable hash of its words.
SPARE_INKS = ("#5a9a8a", "#b0507a", "#8a7ab0", "#c8a03a", "#4a7a4a", "#a05a3a")
#: The pips of each life stage; a stage this table does not name draws two.
STAGE_PIPS = {"puppy": 1, "kitten": 1, "junior": 1, "adult": 2, "senior": 3, "mature": 3,
              "all life stages": 4}  # fmt: skip
#: A dog's kibble size by its breed size's first word.
BREED_SCALE = {"toy": 0.6, "small": 0.75, "medium": 1.0, "large": 1.25, "giant": 1.4}
#: A litter's scent and its sprig's ink; ``unscented`` draws no sprig.
SCENT_INKS = {
    "lavender": "#8a6ab8", "pine": "#2f6b45", "linen": "#9ac0e0", "powder": "#f0b8c8",
    "citrus": "#f0c030", "lemon": "#f0d040", "rose": "#d0607a", "eucalyptus": "#6aa08a",
    "apple": "#8ac040", "cotton": "#e8e8f0", "vanilla": "#f0e0b0", "aloe": "#7ab07a",
}  # fmt: skip


def _ink(value: str, table: dict[str, str]) -> str | None:
    """The ink of the first word of ``table`` that ``value`` holds, or ``None``."""
    return next((ink for k, ink in table.items() if k in value), None)


def _spare(value: str) -> str:
    """A stable spare ink for a value no table names."""
    return SPARE_INKS[zlib.crc32(value.encode()) % len(SPARE_INKS)]


def _flavor_band(x: float, y: float, w: float, h: float, flavor: str) -> list[str]:
    """The flavor's band: its meat's ink, then its side's (or the meat's again when it has none)."""
    meat = _ink(flavor, MEAT_INKS) or _spare(flavor)
    side = _ink(flavor, SIDE_INKS) or meat
    return [
        _rect(x, y, w / 2, h, meat, 2, LW_DETAIL),
        _rect(x + w / 2, y, w / 2, h, side, 2, LW_DETAIL),
    ]


def _pips(x: float, y: float, life_stage: str, ink: str) -> list[str]:
    """The life stage's pips in a row from ``x``: one, two, three or four."""
    n = next((v for k, v in STAGE_PIPS.items() if k in life_stage), 2)
    return [_ell(x + i * 13, y, 4.5, 4.5, ink, LW_DETAIL) for i in range(n)]


def _need_emblem(cx: float, cy: float, need: str, ink: str) -> list[str]:
    """A cat's special need beside the paw: a house for indoor, a heart for sterilized, a coil for
    hairball control, a leaf for sensitive, a feather for weight, a tooth for dental."""
    if "indoor" in need:
        return [_path(f"M{cx - 10},{cy + 9} L{cx - 10},{cy - 2} L{cx},{cy - 11} L{cx + 10},{cy - 2} "
                      f"L{cx + 10},{cy + 9} Z", ink, LW_DETAIL)]  # fmt: skip
    if "steril" in need or "neuter" in need:
        return [_path(f"M{cx},{cy + 10} L{cx - 10},{cy - 1} Q{cx - 10},{cy - 10} {cx},{cy - 4} "
                      f"Q{cx + 10},{cy - 10} {cx + 10},{cy - 1} Z", ink, LW_DETAIL)]  # fmt: skip
    if "hairball" in need:
        return [_ell(cx, cy, 10, 10, ink, LW_DETAIL), _ell(cx, cy, 5, 5, PAPER, LW_DETAIL)]
    if "sensitive" in need:
        return [_path(f"M{cx - 10},{cy + 8} Q{cx - 8},{cy - 10} {cx + 10},{cy - 10} "
                      f"Q{cx + 8},{cy + 8} {cx - 10},{cy + 8} Z", ink, LW_DETAIL)]  # fmt: skip
    if "weight" in need or "light" in need:
        return [_path(f"M{cx - 3},{cy + 11} Q{cx - 9},{cy - 2} {cx + 6},{cy - 11} "
                      f"Q{cx + 6},{cy + 2} {cx - 3},{cy + 11} Z", ink, LW_DETAIL)]  # fmt: skip
    if "dental" in need or "teeth" in need:
        return [_path(f"M{cx - 8},{cy - 9} L{cx + 8},{cy - 9} L{cx + 6},{cy + 10} L{cx},{cy + 4} "
                      f"L{cx - 6},{cy + 10} Z", ink, LW_DETAIL)]  # fmt: skip
    if not need:
        return []
    return [_rect(cx - 8, cy - 8, 16, 16, _spare(need), 3, LW_DETAIL)]


def _paw(cx: float, cy: float, s: float, ink: str) -> list[str]:
    """A paw print: one pad and four toes, ``s`` across the pad."""
    out = [_ell(cx, cy, s * 0.55, s * 0.45, ink, LW_DETAIL)]
    for dx, dy in ((-0.62, -0.62), (-0.22, -0.95), (0.22, -0.95), (0.62, -0.62)):
        out.append(_ell(cx + dx * s, cy + dy * s, s * 0.18, s * 0.24, ink, LW_DETAIL))
    return out


def _kibble(x: float, y: float, animal: str, k: float = 1.0) -> str:
    """One piece of kibble, ``k`` times its usual size: a small bone for a dog, a fish for a cat."""
    if animal == "cat":
        return _path(f"M{x - 9 * k},{y} Q{x - 2 * k},{y - 7 * k} {x + 5 * k},{y} L{x + 10 * k},{y - 5 * k} "
                     f"L{x + 10 * k},{y + 5 * k} L{x + 5 * k},{y} Q{x - 2 * k},{y + 7 * k} {x - 9 * k},{y} Z",
                     KIBBLE, LW_DETAIL)  # fmt: skip
    return _path(f"M{x - 8 * k},{y - 4 * k} L{x + 8 * k},{y - 4 * k} Q{x + 13 * k},{y - 8 * k} {x + 12 * k},{y} "
                 f"Q{x + 13 * k},{y + 8 * k} {x + 8 * k},{y + 4 * k} L{x - 8 * k},{y + 4 * k} Q{x - 13 * k},{y + 8 * k} "
                 f"{x - 12 * k},{y} Q{x - 13 * k},{y - 8 * k} {x - 8 * k},{y - 4 * k} Z", KIBBLE, LW_DETAIL)  # fmt: skip


def dry_pet_food(
    paint: str, fill: Fill, label: str | None, animal: str = "dog", life_stage: str = "",
    flavor: str = "", breed_size: str = "", special_need: str = "",
) -> list[str]:  # fmt: skip
    """A stand-up bag of dry food: the body, a crimped top seal, a paw and a bowl of kibble, with
    the life stage's pips, the need's emblem and the flavor's band."""
    k = next((v for w, v in BREED_SCALE.items() if breed_size.startswith(w)), 1.0)
    out = [
        _path("M112,92 L288,92 L306,352 L94,352 Z", paint),
        _rect(106, 58, 188, 36, _shade(fill.base, 0.2), 4),
    ]
    out += [_line(f"M{x},62 L{x},90", LW_DETAIL) for x in range(116, 290, 12)]
    out.append(_rect(142, 176, 116, 120, PAPER, 10, LW_DETAIL))
    out.append(
        _path("M158,262 L242,262 Q238,286 200,288 Q162,286 158,262 Z", _tint(fill.base, 0.4))
    )
    out += [
        _kibble(x, y, animal, k)
        for x, y in ((178, 252), (200, 246), (222, 252), (189, 236), (211, 234))
    ]
    out += _paw(200, 136, 22, _tint(fill.base, 0.65))
    if life_stage:
        out += _pips(124, 136, life_stage, PAPER)
    out += _need_emblem(262, 136, special_need, PAPER)
    if flavor:
        out += _flavor_band(110, 308, 180, 22, flavor)
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
#: Where each format draws its life stage's pips ``(x, y)`` and its flavor's band ``(x, y, w, h)``.
WET_MARKS = {"pouches": ((174, 120), (140, 300, 120, 20)), "trays": ((174, 254), (122, 290, 156, 18)),
             "tins": ((174, 184), (130, 274, 140, 16))}  # fmt: skip


def wet_pet_food(
    paint: str, fill: Fill, label: str | None, pack_format: str = "pouches", animal: str = "dog",
    life_stage: str = "", flavor: str = "",
) -> list[str]:  # fmt: skip
    """One item of a wet food's pack: a pouch, a peel-lid tray or a ring-pull tin, with the life
    stage's pips and the flavor's band."""
    draw, (cx, cy, s) = WET.get(pack_format, WET["pouches"])
    (px, py), band = WET_MARKS.get(pack_format, WET_MARKS["pouches"])
    out = draw(paint, fill)
    if s:
        out.append(_ell(cx, cy, s * 1.6, s * 1.6, PAPER, LW_DETAIL))
        out += _paw(cx, cy + 6, s * 0.8, _shade(fill.base, 0.1))
    if animal == "cat" and pack_format == "trays":
        out.append(_kibble(200, 296, animal))
    if life_stage:
        out += _pips(px, py, life_stage, PAPER)
    if flavor:
        out += _flavor_band(*band, flavor)
    return _label(out, label)


def _granules(litter_type: str, x0: float, y0: float, x1: float, y1: float) -> list[str]:
    """The granules a litter's window shows, in rows across the window."""
    color, form = next((g for k, g in GRAINS.items() if k in litter_type), CLAY)
    out = []
    for i, y in enumerate(range(int(y0) + 12, int(y1) - 6, 16)):
        for x in range(int(x0) + 12 + (i % 2) * 8, int(x1) - 8, 18):
            if form == "diamond":
                out.append(
                    _path(f"M{x},{y - 6} L{x + 6},{y} L{x},{y + 6} L{x - 6},{y} Z", color, 1)
                )
            elif form == "rod":
                out.append(_rect(x - 7, y - 3, 14, 7, color, 3, 1))
            else:
                out.append(_ell(x, y, 5, 4, color, 1))
    return out


def cat_litter(
    paint: str, fill: Fill, label: str | None, litter_type: str = "clumping clay", scent: str = ""
) -> list[str]:
    """A bag of litter: the body, a cut-out carry handle, a window of its granules and its scent's
    sprig: a stem and three leaves in the scent's ink, none when it is unscented."""
    out = [
        _rect(100, 62, 200, 290, paint, 14),
        _rect(170, 78, 60, 20, PAPER, 10, LW_DETAIL),
        _rect(132, 196, 136, 124, PAPER, 8, LW_DETAIL),
    ]
    out += _granules(litter_type, 132, 196, 268, 320)
    out += _paw(200, 150, 20, _tint(fill.base, 0.6))
    if scent and "unscented" not in scent:
        ink = _ink(scent, SCENT_INKS) or _spare(scent)
        out.append(_line("M258,176 L258,132", LW_DETAIL))
        out += [
            _ell(258 + dx, y, 7, 4, ink, LW_DETAIL)
            for dx, y in ((-7, 168), (7, 156), (-7, 144), (0, 132))
        ]
    out.append(_highlight("M114,90 L114,330", 6, 0.35))
    return _label(out, label)


SHAPES = {"dry_pet_food": dry_pet_food, "wet_pet_food": wet_pet_food, "cat_litter": cat_litter}
register(SHAPES)
