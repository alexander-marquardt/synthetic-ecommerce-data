"""Pet treats, toys and beds for the retail drawing kit (gen#967, slice 2).

==========  ================================================  ==================================
shape       draws                                             params
==========  ================================================  ==================================
dog_treats  a resealable pouch in the pack's color, a paw     treat_form (dental stick, dental
            and a window of its treats: sticks, twists,       twist, biscuit, training bite),
            bone biscuits or small bites                      flavor, breed_size, life_stage
pet_toy     the toy in its color: a ball, a rope, a ring, a   toy_kind (ball, rope, ring, bone,
            bone, a flying disc, a wand, a mouse or a kicker  flying disc, wand, mouse, kicker),
            with its feature's mark                           play_feature
pet_bed     the bed in its color: a donut, a bolster, an      bed_style (donut, bolster,
            orthopedic mattress, a cushion, a cave or a       orthopedic, cushion, cave,
            radiator hammock, with a swatch of its cover      radiator), cover
==========  ================================================  ==================================

What the product says is drawn on it, as on the food bags of :mod:`kit_pets`, so two styles of
one leaf and price read apart on a results grid: a treat pouch shows its flavor's band, its life
stage's pips and treats sized to the breed; a toy its feature's mark beside it (sound arcs for a
squeaker, waves for a floater, a shield for a tough chew, rays for a glow, a feather, a catnip
leaf, a bell, a crinkle zigzag, two arrows for a tug); a bed a swatch tag of its cover (fur
strokes, corduroy ribs, a quilted lattice, a water drop, a velvet sheen, sherpa curls).

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
from synthetic_ecommerce_data.domains.retail.kit_pets import (
    BREED_SCALE,
    _flavor_band,
    _paw,
    _pips,
    _spare,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect

#: The treats' own inks: a dental stick's green, a baked biscuit's brown, a soft bite's red-brown.
DENTAL = "#7fb89a"
BISCUIT = "#c98a4a"
BITE = "#a8503a"
#: A wand's cane and a radiator hammock's steel frame.
CANE = "#b08a5a"
STEEL = "#c3c7cd"


def _bone(x: float, y: float, k: float, ink: str, width: float = LW_DETAIL) -> str:
    """A bone ``k`` times its unit size, centered on ``(x, y)``: a biscuit or a chew toy."""
    return _path(f"M{x - 20 * k},{y - 8 * k} L{x + 20 * k},{y - 8 * k} Q{x + 30 * k},{y - 22 * k} {x + 32 * k},{y - 6 * k} "
                 f"Q{x + 40 * k},{y} {x + 32 * k},{y + 6 * k} Q{x + 30 * k},{y + 22 * k} {x + 20 * k},{y + 8 * k} "
                 f"L{x - 20 * k},{y + 8 * k} Q{x - 30 * k},{y + 22 * k} {x - 32 * k},{y + 6 * k} "
                 f"Q{x - 40 * k},{y} {x - 32 * k},{y - 6 * k} Q{x - 30 * k},{y - 22 * k} {x - 20 * k},{y - 8 * k} Z",
                 ink, width)  # fmt: skip


def _treats(treat_form: str, k: float) -> list[str]:
    """The treats a pouch's window shows (x 134-266, y 180-290), ``k`` times their size."""
    if "twist" in treat_form:
        return [_path(f"M{150},{y} Q{175},{y - 14 * k} {200},{y} T{250},{y}", "none", 9 * k, stroke=DENTAL)
                for y in (204, 236, 268)]  # fmt: skip
    if "stick" in treat_form:
        out = []
        for y in (200, 232, 264):
            out.append(_rect(200 - 50 * k, y - 8 * k, 100 * k, 16 * k, DENTAL, 6 * k, LW_DETAIL))
            out += [_line(f"M{200 - 44 * k},{y} L{200 + 44 * k},{y}", 1)]
        return out
    if "bite" in treat_form:
        return [_ell(x, y, 7 * k, 7 * k, BITE, LW_DETAIL)
                for y in (204, 230, 256) for x in (160, 186, 212, 238)]  # fmt: skip
    return [_bone(x, y, 0.75 * k, BISCUIT) for x, y in ((172, 214), (228, 230), (186, 262))]


def dog_treats(
    paint: str, fill: Fill, label: str | None, treat_form: str = "biscuit", flavor: str = "",
    breed_size: str = "", life_stage: str = "",
) -> list[str]:  # fmt: skip
    """A resealable pouch of treats: the body, a zip strip, a paw, a window of the treats (sized to
    the breed), the life stage's pips and the flavor's band."""
    k = next((v for w, v in BREED_SCALE.items() if breed_size.startswith(w)), 1.0)
    out = [
        _path("M112,74 L288,74 Q296,212 300,350 L100,350 Q104,212 112,74 Z", paint),
        _rect(112, 96, 176, 8, _shade(fill.base, 0.2), 3, LW_DETAIL),
        _rect(134, 180, 132, 110, PAPER, 12, LW_DETAIL),
    ]
    out += _treats(treat_form, k)
    out += _paw(200, 140, 20, _tint(fill.base, 0.6))
    if life_stage:
        out += _pips(124, 140, life_stage, PAPER)
    if flavor:
        out += _flavor_band(110, 306, 180, 22, flavor)
    out.append(_highlight("M124,112 L114,330", 6, 0.35))
    return _label(out, label)


def _ball(paint: str, fill: Fill) -> list[str]:
    return [_ell(200, 210, 96, 96, paint),
            _line("M124,152 Q176,210 124,268", 4), _line("M276,152 Q224,210 276,268", 4),
            _highlight("M150,150 Q170,130 196,126", 8, 0.45)]  # fmt: skip


def _rope(paint: str, fill: Fill) -> list[str]:
    knot = _shade(fill.base, 0.15)
    out = [_path("M110,210 Q200,150 290,210", "none", 30, stroke=paint),
           _line("M110,210 Q200,150 290,210", LW_DETAIL)]  # fmt: skip
    out += [_line(f"M{x},{y - 12} L{x + 10},{y + 12}", LW_DETAIL)
            for x, y in ((140, 192), (170, 180), (200, 178), (230, 180), (260, 192))]  # fmt: skip
    out += [_ell(96, 214, 26, 26, knot), _ell(304, 214, 26, 26, knot)]
    out += [_line(f"M{x},236 L{x + d},278", LW_DETAIL) for x, d in ((86, -8), (96, 0), (106, 8), (294, -8), (304, 0), (314, 8))]
    return out


def _ring(paint: str, fill: Fill) -> list[str]:
    return [_ell(200, 210, 104, 104, paint), _ell(200, 210, 50, 50, PAPER),
            _highlight("M128,170 Q150,128 196,114", 8, 0.4)]  # fmt: skip


def _bone_toy(paint: str, fill: Fill) -> list[str]:
    return [_bone(200, 210, 3.4, paint, 3.0),
            _highlight("M140,190 L258,190", 6, 0.4)]  # fmt: skip


def _disc(paint: str, fill: Fill) -> list[str]:
    return [_ell(200, 214, 128, 64, paint), _ell(200, 206, 96, 42, _tint(fill.base, 0.25), LW_DETAIL),
            _highlight("M120,196 Q160,170 210,168", 6, 0.4)]  # fmt: skip


def _wand(paint: str, fill: Fill) -> list[str]:
    return [_line("M96,340 L232,110", 9, stroke=CANE), _line("M232,110 Q284,130 266,196", LW_DETAIL),
            _path("M266,196 Q300,232 282,300 Q246,252 266,196 Z", paint),
            _line("M266,198 L282,298", LW_DETAIL)]  # fmt: skip


def _mouse(paint: str, fill: Fill) -> list[str]:
    return [_line("M118,236 Q70,250 82,300", 4), _path("M112,236 Q140,152 248,176 Q300,200 312,236 Q220,272 112,236 Z", paint),
            _ell(250, 168, 20, 20, _tint(fill.base, 0.3)), _ell(290, 216, 5, 5, INK, 1)]  # fmt: skip


def _kicker(paint: str, fill: Fill) -> list[str]:
    out = [_rect(84, 168, 232, 84, paint, 40)]
    out += [_line(f"M{x},172 L{x},248", LW_DETAIL) for x in (144, 200, 256)]
    return out


#: Each toy kind's drawing, by the first word of this table its value holds; a ball by default.
TOYS: dict[str, Callable[[str, Fill], list[str]]] = {
    "ball": _ball, "rope": _rope, "ring": _ring, "bone": _bone_toy, "disc": _disc,
    "wand": _wand, "mouse": _mouse, "kicker": _kicker,
}  # fmt: skip


def _feature_mark(cx: float, cy: float, feature: str) -> list[str]:
    """A toy's feature, drawn beside it in ink."""
    if "squeak" in feature:
        return [_line(f"M{cx + r * 0.5},{cy - r} Q{cx + r},{cy} {cx + r * 0.5},{cy + r}", 2.4) for r in (8, 16, 24)]
    if "float" in feature:
        return [_line(f"M{cx - 24},{cy + d} q8,-8 16,0 t16,0 t16,0", 2.4, stroke="#3a7ab8") for d in (-10, 4, 18)]
    if "chew" in feature or "tough" in feature:
        return [_path(f"M{cx},{cy - 22} L{cx + 18},{cy - 14} Q{cx + 16},{cy + 12} {cx},{cy + 22} "
                      f"Q{cx - 16},{cy + 12} {cx - 18},{cy - 14} Z", "#8a9aa8", LW_DETAIL)]  # fmt: skip
    if "glow" in feature:
        out = [_ell(cx, cy, 9, 9, "#c8f070", LW_DETAIL)]
        return out + [_line(f"M{cx + dx * 13},{cy + dy * 13} L{cx + dx * 22},{cy + dy * 22}", 2.4)
                      for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (0.7, 0.7), (-0.7, -0.7), (0.7, -0.7), (-0.7, 0.7))]  # fmt: skip
    if "feather" in feature:
        return [_path(f"M{cx - 6},{cy + 24} Q{cx - 18},{cy - 6} {cx + 8},{cy - 24} Q{cx + 12},{cy + 4} {cx - 6},{cy + 24} Z",
                      "#e8d8b0", LW_DETAIL), _line(f"M{cx - 6},{cy + 24} L{cx + 6},{cy - 18}", 1)]  # fmt: skip
    if "catnip" in feature:
        return [_path(f"M{cx - 18},{cy + 16} Q{cx - 14},{cy - 18} {cx + 18},{cy - 18} Q{cx + 14},{cy + 16} {cx - 18},{cy + 16} Z",
                      "#5aa04a", LW_DETAIL), _line(f"M{cx - 18},{cy + 16} L{cx + 10},{cy - 10}", 1)]  # fmt: skip
    if "bell" in feature:
        return [_path(f"M{cx - 16},{cy + 12} Q{cx - 14},{cy - 18} {cx},{cy - 18} Q{cx + 14},{cy - 18} {cx + 16},{cy + 12} Z",
                      "#e8c040", LW_DETAIL), _ell(cx, cy + 15, 5, 5, "#e8c040", LW_DETAIL)]  # fmt: skip
    if "crinkle" in feature:
        return [_line(f"M{cx - 24},{cy} l8,-12 l8,24 l8,-24 l8,24 l8,-24 l8,12", 2.4)]
    if "tug" in feature:
        return [_line(f"M{cx - 4},{cy - 8} L{cx - 24},{cy - 8} m8,-8 l-8,8 l8,8", 2.4),
                _line(f"M{cx + 4},{cy + 8} L{cx + 24},{cy + 8} m-8,-8 l8,8 l-8,8", 2.4)]  # fmt: skip
    if not feature:
        return []
    return [_rect(cx - 12, cy - 12, 24, 24, _spare(feature), 4, LW_DETAIL)]


def pet_toy(
    paint: str, fill: Fill, label: str | None, toy_kind: str = "ball", play_feature: str = "",
    animal: str = "dog",
) -> list[str]:  # fmt: skip
    """The toy in its color, its feature's mark at the top right, and a paw at the top left (a
    dog's paw larger than a cat's)."""
    draw = next((d for w, d in TOYS.items() if w in toy_kind), _ball)
    out = draw(paint, fill)
    out += _feature_mark(320, 72, play_feature)
    out += _paw(76, 72, 20 if animal == "dog" else 14, _tint(INK, 0.6))
    return _label(out, label)


def _donut(paint: str, fill: Fill) -> list[str]:
    return [_ell(200, 236, 156, 100, paint), _ell(200, 248, 96, 54, _tint(fill.base, 0.35)),
            _highlight("M80,214 Q120,158 200,146", 8, 0.35)]  # fmt: skip


def _bolster(paint: str, fill: Fill) -> list[str]:
    return [_rect(56, 232, 288, 96, _tint(fill.base, 0.35), 20),
            _path("M56,320 L56,192 Q56,160 92,160 L308,160 Q344,160 344,192 L344,320 L308,320 L308,204 L92,204 L92,320 Z", paint),
            _highlight("M76,300 L76,190", 6, 0.35)]  # fmt: skip


def _orthopedic(paint: str, fill: Fill) -> list[str]:
    out = [_rect(52, 268, 296, 52, PAPER, 8), _rect(52, 196, 296, 76, paint, 14)]
    out += [_path(f"M{x},300 q10,-14 20,0", "none", LW_DETAIL) for x in range(66, 330, 26)]
    return out


def _cushion(paint: str, fill: Fill) -> list[str]:
    return [_rect(52, 196, 296, 120, paint, 44), _rect(66, 210, 268, 92, "none", 36, LW_DETAIL),
            _highlight("M90,228 L300,228", 6, 0.3)]  # fmt: skip


def _cave(paint: str, fill: Fill) -> list[str]:
    return [_path("M72,326 Q72,126 200,118 Q328,126 328,326 Z", paint),
            _path("M128,326 Q132,212 200,206 Q268,212 272,326 Z", _shade(fill.base, 0.45), LW_DETAIL),
            _rect(60, 316, 280, 20, _tint(fill.base, 0.35), 8, LW_DETAIL)]  # fmt: skip


def _radiator(paint: str, fill: Fill) -> list[str]:
    out = [_line("M76,150 L76,322", 6, stroke=STEEL), _line("M324,150 L324,322", 6, stroke=STEEL),
           _line("M70,150 Q70,136 84,136", 4), _line("M330,150 Q330,136 316,136", 4)]  # fmt: skip
    out.append(_path("M76,170 Q200,300 324,170 L324,196 Q200,326 76,196 Z", paint))
    return out


#: Each bed style's drawing, by the first word of this table its value holds; a donut by default.
BEDS: dict[str, Callable[[str, Fill], list[str]]] = {
    "donut": _donut, "bolster": _bolster, "orthopedic": _orthopedic, "cushion": _cushion,
    "cave": _cave, "radiator": _radiator,
}  # fmt: skip


def _cover_swatch(x: float, y: float, cover: str, ink: str) -> list[str]:
    """A swatch tag of the bed's cover (``x``, ``y`` its top left, 64 square), its texture in
    ``ink``."""
    out = [_rect(x, y, 64, 64, PAPER, 8, LW_DETAIL)]
    if "fur" in cover:
        out += [_line(f"M{x + 8 + i * 9},{y + 52} q-3,-14 2,-30", 1.6, stroke=ink) for i in range(6)]
    elif "corduroy" in cover:
        out += [_rect(x + 8 + i * 10, y + 8, 6, 48, ink, 3, 1) for i in range(5)]
    elif "quilt" in cover:
        out += [_line(f"M{x + 4},{y + d} L{x + d},{y + 4}", 1.4, stroke=ink) for d in (20, 36, 52)]
        out += [_line(f"M{x + 60},{y + 64 - d} L{x + 64 - d},{y + 60}", 1.4, stroke=ink) for d in (20, 36, 52)]
        out += [_line(f"M{x + 4},{y + 64 - d} L{x + d},{y + 60}", 1.4, stroke=ink) for d in (20, 36, 52)]
    elif "waterproof" in cover:
        out.append(_path(f"M{x + 32},{y + 10} Q{x + 50},{y + 34} {x + 44},{y + 46} Q{x + 32},{y + 60} {x + 20},{y + 46} "
                         f"Q{x + 14},{y + 34} {x + 32},{y + 10} Z", "#5a9ad0", LW_DETAIL))  # fmt: skip
    elif "velvet" in cover:
        out.append(_path(f"M{x + 8},{y + 56} Q{x + 32},{y + 4} {x + 56},{y + 8} Q{x + 36},{y + 22} {x + 8},{y + 56} Z", ink, 1))
    elif "sherpa" in cover:
        out += [_ell(x + 14 + i * 18, y + 14 + j * 18, 6, 6, "none", 1.4) for i in range(3) for j in range(3)]
    elif cover:
        out.append(_rect(x + 12, y + 12, 40, 40, _spare(cover), 4, 1))
    return out


def pet_bed(
    paint: str, fill: Fill, label: str | None, bed_style: str = "donut", cover: str = "",
    animal: str = "dog",
) -> list[str]:  # fmt: skip
    """The bed in its color, a swatch tag of its cover at the top right, and a paw at the top
    left (a dog's paw larger than a cat's)."""
    draw = next((d for w, d in BEDS.items() if w in bed_style), _donut)
    out = draw(paint, fill)
    if cover:
        out += _cover_swatch(300, 40, cover, _shade(fill.base, 0.35))
    out += _paw(76, 72, 20 if animal == "dog" else 14, _tint(INK, 0.6))
    return _label(out, label)


SHAPES = {"dog_treats": dog_treats, "pet_toy": pet_toy, "pet_bed": pet_bed}
register(SHAPES)
