"""Pet leashes, grooming brushes and small-pet supplies for the retail drawing kit (gen#967, slice 3).

================  ===========================================  ===================================
shape             draws                                        params
================  ===========================================  ===================================
pet_leash         the gear in its color: a leash with its      gear_kind (leash, retractable
                  handle and clip, a retractable leash's       leash, collar, harness), material,
                  case, a buckled collar or a harness          animal
grooming_brush    the brush in its color: a slicker, a pin,    brush_kind (slicker, pin, bristle,
                  a bristle or a deshedding brush, a rubber    deshedding, rubber, glove),
                  curry or a grooming glove                    coat_type, animal
small_pet_supply  a bag or a tub in the pack's color with a    supply_kind (flakes, pellets,
                  window of what it holds, and its animal's    gravel, hay, nuggets, bedding),
                  emblem                                       animal, formula
================  ===========================================  ===================================

What the product says is drawn on it, as on the toys and beds of :mod:`kit_pet_gear`, so two
styles of one leaf and price read apart on a results grid: a leash or collar shows a swatch of its
material (a nylon weave, leather stitching, reflective rays, padded quilting, rope twists); a
brush a tag of the coat it is made for (short strokes, long waves, two layers, curls); a supply
pack its animal's emblem (a fish, a rabbit's long ears, a guinea pig's or a hamster's round ones)
and its formula's band.

Each param's values are the lower-cased attribute values of the spec rows, so a derived style
that changes one draws what it states (gen#512). The drawings are original and drawn by code
(ruling 2026-11-02, gen#102).
"""

# ruff: noqa: E501 -- SVG paths read better whole than wrapped (prototype only).

from __future__ import annotations

from collections.abc import Callable

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
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
from synthetic_ecommerce_data.domains.retail.kit_pets import _flavor_band, _paw, _spare
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: A clip's, a buckle's and a pin's metal, and a brush's bristles.
METAL = "#b9bec6"
BRISTLE = "#8a6a48"
#: What a supply pack's window shows: fish flakes, pellets, gravel, hay, nuggets, bedding.
FLAKE = "#e0a040"
PELLET = "#8a6a3a"
HAY = "#c9b25a"
BEDDING = "#efe6d2"


# --- Leashes and collars -----------------------------------------------------------------------


def _leash(paint: str, fill: Fill) -> list[str]:
    return [_path("M120,96 Q80,60 120,52 Q160,60 120,96", "none", 14, stroke=paint),
            _path("M120,96 Q150,220 250,250 Q300,266 296,316", "none", 14, stroke=paint),
            _line("M120,96 Q150,220 250,250 Q300,266 296,316", LW_DETAIL),
            _rect(284, 312, 24, 30, METAL, 6, LW_DETAIL), _ell(296, 350, 10, 10, "none", 3)]  # fmt: skip


def _retractable(paint: str, fill: Fill) -> list[str]:
    return [_path("M88,140 Q88,92 150,92 L210,92 Q262,92 262,150 Q262,214 196,224 L150,224 Q88,214 88,140 Z", paint),
            _ell(176, 156, 44, 44, _tint(fill.base, 0.3), LW_DETAIL),
            _rect(102, 214, 52, 70, _shade(fill.base, 0.2), 18),
            _line("M262,170 Q300,240 300,320", 2), _rect(288, 316, 24, 30, METAL, 6, LW_DETAIL),
            _highlight("M110,120 Q140,100 190,100", 6, 0.4)]  # fmt: skip


def _collar(paint: str, fill: Fill) -> list[str]:
    return [_ell(200, 210, 120, 82, "none", 26),
            _path("M80,210 Q80,128 200,128 Q320,128 320,210 Q320,292 200,292 Q80,292 80,210 Z", "none", 22, stroke=paint),
            _rect(176, 274, 48, 36, METAL, 6, LW_DETAIL), _line("M200,278 L200,306", 3),
            _ell(200, 132, 16, 12, "none", 4)]  # fmt: skip


def _harness(paint: str, fill: Fill) -> list[str]:
    loop = "M90,170 Q90,114 160,114 Q230,114 230,170 Q230,226 160,226 Q90,226 90,170 Z"
    return [_path(loop, "none", 20), _path(loop, "none", 14, stroke=paint),
            _path("M150,226 L150,320 L250,320 L250,226", "none", 18, stroke=paint),
            _line("M230,170 L320,170 L320,300 L250,300", 14, stroke=paint),
            _rect(186, 300, 28, 30, METAL, 6, LW_DETAIL), _ell(160, 112, 12, 9, METAL, LW_DETAIL)]  # fmt: skip


#: Each gear kind's drawing, by the first word of this table its value holds; a leash by default.
#: ``retract`` comes before ``leash`` so a retractable leash draws its case.
LEASHES: dict[str, Callable[[str, Fill], list[str]]] = {
    "retract": _retractable, "collar": _collar, "harness": _harness, "leash": _leash,
}  # fmt: skip


def _material_swatch(x: float, y: float, material: str, ink: str) -> list[str]:
    """A swatch tag of the gear's material (``x``, ``y`` its top left, 64 square), in ``ink``."""
    out = [_rect(x, y, 64, 64, PAPER, 8, LW_DETAIL)]
    if "nylon" in material:
        out += [
            _line(f"M{x + 6},{y + d} L{x + 58},{y + d}", 1.4, stroke=ink) for d in (14, 26, 38, 50)
        ]
        out += [_line(f"M{x + d},{y + 6} L{x + d},{y + 58}", 1.4, stroke=ink) for d in (20, 44)]
    elif "leather" in material:
        out.append(_rect(x + 8, y + 16, 48, 32, "#8a5a34", 4, 1))
        out += [_line(f"M{x + 12 + i * 8},{y + 20} l4,0", 1.4, stroke=PAPER) for i in range(5)]
    elif "reflect" in material:
        out += [_line(f"M{x + 32},{y + 32} l{dx},{dy}", 2, stroke=ink)
                for dx, dy in ((0, -24), (17, -17), (24, 0), (17, 17), (0, 24), (-17, 17), (-24, 0), (-17, -17))]  # fmt: skip
    elif "pad" in material:
        out += [
            _line(f"M{x + 6},{y + d} q13,-10 26,0 t26,0", 1.6, stroke=ink) for d in (20, 36, 52)
        ]
    elif "rope" in material:
        out += [
            _line(f"M{x + 8 + i * 10},{y + 56} L{x + 18 + i * 10},{y + 8}", 2.4, stroke=ink)
            for i in range(5)
        ]
    elif material:
        out.append(_rect(x + 12, y + 12, 40, 40, _spare(material), 4, 1))
    return out


def pet_leash(
    paint: str, fill: Fill, label: str | None, gear_kind: str = "leash", material: str = "",
    animal: str = "dog",
) -> list[str]:  # fmt: skip
    """The leash, collar or harness in its color, a swatch of its material at the top right, and a
    paw at the bottom left (a dog's paw larger than a cat's)."""
    draw = next((d for w, d in LEASHES.items() if w in gear_kind), _leash)
    out = draw(paint, fill)
    if material:
        out += _material_swatch(310, 40, material, _shade(fill.base, 0.35))
    out += _paw(60, 336, 20 if animal == "dog" else 14, _tint(INK, 0.6))
    return _label(out, label)


# --- Grooming brushes --------------------------------------------------------------------------


def _handle(paint: str) -> list[str]:
    return [_rect(184, 214, 32, 140, paint, 14)]


def _slicker(paint: str, fill: Fill) -> list[str]:
    out = _handle(paint) + [
        _rect(104, 110, 192, 108, paint, 16),
        _rect(118, 124, 164, 80, PAPER, 8, LW_DETAIL),
    ]
    out += [_ell(130 + i * 14, 136 + j * 14, 1.6, 1.6, INK, 1) for i in range(12) for j in range(5)]
    return out


def _pin(paint: str, fill: Fill) -> list[str]:
    out = _handle(paint) + [
        _ell(200, 156, 100, 70, paint),
        _ell(200, 156, 80, 52, _tint(fill.base, 0.5), LW_DETAIL),
    ]
    out += [_ell(150 + i * 20, 126 + j * 20, 4, 4, METAL, 1) for i in range(6) for j in range(4)]
    return out


def _bristle(paint: str, fill: Fill) -> list[str]:
    out = _handle(paint) + [_ell(200, 150, 100, 64, paint)]
    out += [_line(f"M{x},{110 + abs(x - 200) * 0.25} L{x},{190 - abs(x - 200) * 0.25}", 3, stroke=BRISTLE)
            for x in range(130, 280, 12)]  # fmt: skip
    return out


def _deshedding(paint: str, fill: Fill) -> list[str]:
    out = _handle(paint) + [_path("M96,150 Q200,96 304,150 L304,214 L96,214 Z", paint),
                            _rect(90, 208, 220, 16, METAL, 2, LW_DETAIL)]  # fmt: skip
    out += [_line(f"M{x},224 L{x},238", 2) for x in range(96, 306, 10)]
    return out


def _rubber(paint: str, fill: Fill) -> list[str]:
    out = [
        _ell(200, 200, 112, 96, paint),
        _rect(140, 92, 120, 28, _shade(fill.base, 0.2), 12, LW_DETAIL),
    ]
    out += [_ell(200 + dx, 216 + dy, 9, 9, _tint(fill.base, 0.3), LW_DETAIL)
            for dx in (-60, -30, 0, 30, 60) for dy in (-30, 0, 30) if abs(dx) + abs(dy) < 90]  # fmt: skip
    return out


def _glove(paint: str, fill: Fill) -> list[str]:
    out = [_path("M110,330 L110,170 Q110,150 128,150 L128,110 Q128,90 148,90 Q168,90 168,110 L168,96 Q168,76 188,76 "
                 "Q208,76 208,96 L208,104 Q208,84 228,84 Q248,84 248,104 L248,124 Q248,106 268,106 Q288,106 288,126 "
                 "L288,330 Z", paint)]  # fmt: skip
    out += [
        _ell(150 + i * 26, 190 + j * 30, 6, 6, _tint(fill.base, 0.35), LW_DETAIL)
        for i in range(5)
        for j in range(4)
    ]
    return out


#: Each brush kind's drawing, by the first word of this table its value holds; a slicker by default.
BRUSHES: dict[str, Callable[[str, Fill], list[str]]] = {
    "slicker": _slicker, "pin": _pin, "bristle": _bristle, "deshed": _deshedding,
    "rubber": _rubber, "glove": _glove,
}  # fmt: skip


def _coat_tag(x: float, y: float, coat: str, ink: str) -> list[str]:
    """A tag of the coat the brush is for (``x``, ``y`` its top left, 64 square), in ``ink``."""
    out = [_rect(x, y, 64, 64, PAPER, 8, LW_DETAIL)]
    if "short" in coat:
        out += [_line(f"M{x + 10 + i * 9},{y + 44} l3,-14", 2, stroke=ink) for i in range(5)]
    elif "long" in coat:
        out += [
            _line(f"M{x + 12 + i * 12},{y + 8} q-8,14 0,24 t0,24", 2, stroke=ink) for i in range(4)
        ]
    elif "double" in coat:
        out += [_line(f"M{x + 8},{y + d} q12,-8 24,0 t24,0", 2, stroke=ink) for d in (24, 34)]
        out += [_line(f"M{x + 8},{y + d} L{x + 56},{y + d}", 3, stroke=ink) for d in (48,)]
    elif "curl" in coat:
        out += [
            _ell(x + 18 + i * 14, y + 22 + j * 20, 6, 6, "none", 2)
            for i in range(3)
            for j in range(2)
        ]
    elif coat:
        out.append(_rect(x + 12, y + 12, 40, 40, _spare(coat), 4, 1))
    return out


def grooming_brush(
    paint: str, fill: Fill, label: str | None, brush_kind: str = "slicker", coat_type: str = "",
    animal: str = "dog",
) -> list[str]:  # fmt: skip
    """The brush in its color, a tag of its coat at the top right, and a paw at the top left (a
    dog's paw larger than a cat's)."""
    draw = next((d for w, d in BRUSHES.items() if w in brush_kind), _slicker)
    out = draw(paint, fill)
    if coat_type:
        out += _coat_tag(310, 40, coat_type, _shade(fill.base, 0.35))
    out += _paw(60, 72, 20 if animal == "dog" else 14, _tint(INK, 0.6))
    return _label(out, label)


# --- Fish and small-animal supplies ------------------------------------------------------------


def _contents(kind: str) -> list[str]:
    """What the pack's window (x 134-266, y 190-290) shows."""
    if "flake" in kind:
        return [
            _path(f"M{x},{y} l14,-6 l8,10 l-12,8 Z", FLAKE, 1)
            for y in (206, 236, 266)
            for x in (146, 182, 218, 246)
        ]
    if "gravel" in kind:
        return [_ell(x, y, 9 + (x + y) % 5, 7, _tint(PELLET, 0.2 * ((x * y) % 4)), 1)
                for y in (206, 232, 258, 280) for x in (152, 178, 204, 230, 254)]  # fmt: skip
    if "hay" in kind:
        return [
            _line(f"M140,{y} Q200,{y - 18} 262,{y + 6}", 2.4, stroke=HAY)
            for y in range(204, 290, 10)
        ]
    if "nugget" in kind:
        return [
            _rect(x - 10, y - 8, 20, 16, PELLET, 6, 1)
            for y in (210, 240, 270)
            for x in (160, 200, 240)
        ]
    if "bedding" in kind or "shaving" in kind:
        return [
            _path(f"M{x},{y} q10,-12 20,0 q-10,10 -20,0 Z", BEDDING, 1)
            for y in (210, 236, 262, 284)
            for x in (146, 178, 210, 238)
        ]
    return [
        _ell(x, y, 4.5, 4.5, PELLET, 1)
        for y in (204, 222, 240, 258, 276)
        for x in range(150, 260, 16)
    ]


def _emblem(cx: float, cy: float, animal: str, ink: str) -> list[str]:
    """The animal the pack is for: a fish, or a small animal's head by its ears (a rabbit's long,
    a guinea pig's small, a hamster's round and high), in ``ink``."""
    if "fish" in animal:
        return [_path(f"M{cx - 22},{cy} Q{cx},{cy - 16} {cx + 16},{cy} Q{cx},{cy + 16} {cx - 22},{cy} Z", ink, LW_DETAIL),
                _path(f"M{cx + 14},{cy} L{cx + 28},{cy - 10} L{cx + 28},{cy + 10} Z", ink, LW_DETAIL)]  # fmt: skip
    head = [_ell(cx, cy + 6, 18, 15, ink, LW_DETAIL)]
    if "rabbit" in animal:
        return [
            _ell(cx - 8, cy - 20, 5, 16, ink, LW_DETAIL),
            _ell(cx + 8, cy - 20, 5, 16, ink, LW_DETAIL),
            *head,
        ]
    if "hamster" in animal:
        return [
            _ell(cx - 12, cy - 10, 6, 6, ink, LW_DETAIL),
            _ell(cx + 12, cy - 10, 6, 6, ink, LW_DETAIL),
            *head,
        ]
    return [
        _ell(cx - 16, cy - 2, 7, 4, ink, LW_DETAIL),
        _ell(cx + 16, cy - 2, 7, 4, ink, LW_DETAIL),
        *head,
    ]


def small_pet_supply(
    paint: str, fill: Fill, label: str | None, supply_kind: str = "pellets", animal: str = "rabbit",
    formula: str = "",
) -> list[str]:  # fmt: skip
    """A tub (fish food) or a bag (the rest) in the pack's color, a window of its contents, its
    animal's emblem and its formula's band."""
    if "fish" in animal:
        out = [
            _rect(120, 110, 160, 240, paint, 16),
            _rect(112, 84, 176, 34, _shade(fill.base, 0.2), 8),
        ]
    else:
        out = [_path("M112,74 L288,74 Q296,212 300,350 L100,350 Q104,212 112,74 Z", paint),
               _rect(112, 96, 176, 8, _shade(fill.base, 0.2), 3, LW_DETAIL)]  # fmt: skip
    out.append(_rect(134, 186, 132, 108, PAPER, 12, LW_DETAIL))
    out += _contents(supply_kind)
    out += _emblem(200, 150, animal, _tint(fill.base, 0.6))
    if formula:
        out += _flavor_band(120, 306, 160, 20, formula)
    out.append(_highlight("M128,120 L120,330", 6, 0.35))
    return _label(out, label)


SHAPES = {
    "pet_leash": pet_leash,
    "grooming_brush": grooming_brush,
    "small_pet_supply": small_pet_supply,
}
register(SHAPES)
