"""Outdoors and winter-sports shapes for the retail drawing kit (gen#959, slice 3).

Each product is drawn as what it is, so a cooler never reads as a tackle box and a snowboard never
as a skateboard. Outlines are the kit's ink, and the record's fill (color and pattern) paints the
main surface: a pack's body, a cooler's box, a bottle's wall, a light's housing, a lock's body, a
sled's deck, a board's top sheet and a goggle's frame.

===============  ==========================================  ====================================
shape            draws                                       params
===============  ==========================================  ====================================
hiking_backpack  a pack from the front with its straps       pack_frame (internal frame, external
                                                             frame, frameless)
cooler           a cooler from the front, three-quarter      cooler_type (hard, soft, wheeled)
bottle_insul     a tall bottle and its lid                   bottle_lid (straw lid, chug lid,
                                                             screw cap)
bike_light       a light on its mount, lens to the left      light_position (front, rear,
                                                             twin-pack)
bike_lock        a lock standing on its body                 lock_type (shackle, chain, folding,
                                                             cable)
sled             a sled from above on the slant              sled_type (toboggan, saucer,
                                                             steerable)
snowboard        a board from above, standing, its profile   board_profile (camber, rocker, flat)
                 drawn beside it
ski_goggles      goggles face on with their strap            lens_shape (spherical, cylindrical,
                                                             toric)
===============  ==========================================  ====================================

Each param's values are the lower-cased attribute values of the spec rows, so a derived style that
changes a cooler's ``cooler_type`` or a lock's ``lock_type`` draws what it states (gen#512). A
drawing never prints a capacity, a length or a size: a style's SKUs share one image per colorway.
Every param is a string with a default, so each shape also draws bare.
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
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_sports import POLE, _ell, _label, _rect, _tilted

#: The dark webbing of a strap, a wheel's tyre and a lock's shackle coat.
STRAP = "#33363c"
#: The steel of a lid's hinge, a lock's shackle and a bottle's rim.
STEEL = "#b8bec6"
#: The lens of a light and a goggle's mirrored glass.
LENS = "#dfe7ee"


def hiking_backpack(
    paint: str, fill: Fill, label: str | None, pack_frame: str = "internal frame"
) -> list[str]:
    """A pack from the front: an ``internal frame`` pack shows a hip belt with padded wings, an
    ``external frame`` one its bare frame rails beside the bag, and a ``frameless`` one a slim
    body with a cord grid on its front."""
    kind = pack_frame.lower()
    dark = _shade(fill.base, 0.3)
    out: list[str] = []
    if kind == "external frame":
        out += [
            _rect(118, 50, 12, 300, POLE, 4),
            _rect(270, 50, 12, 300, POLE, 4),
            _line("M124,90 L276,90 M124,330 L276,330", 6, stroke=POLE),
        ]
    out += [
        _path(
            "M140,96 Q140,60 200,58 Q260,60 260,96 L268,318 Q268,340 246,340 L154,340 Q132,340 132,318 Z",
            paint,
        ),
        _path("M146,100 Q150,70 200,68 Q250,70 254,100 Q200,118 146,100 Z", dark),
        _rect(160, 196, 80, 96, _tint(fill.base, 0.2), 14),
        _line("M168,206 L232,206", LW_DETAIL),
    ]
    if kind == "internal frame":
        out += [
            _path("M104,272 L144,262 L144,300 L104,306 Z", STRAP),
            _path("M296,272 L256,262 L256,300 L296,306 Z", STRAP),
            _rect(186, 268, 28, 30, STEEL, 4),
        ]
    elif kind == "frameless":
        out += [
            _line("M164,130 L236,186 M236,130 L164,186", LW_DETAIL, stroke=STRAP),
            _line("M164,130 L236,130 L236,186 L164,186 Z", LW_DETAIL, stroke=STRAP),
        ]
    out.append(_highlight("M150,110 L148,300", 5, 0.4))
    return _label(out, label)


def cooler(paint: str, fill: Fill, label: str | None, cooler_type: str = "hard") -> list[str]:
    """A cooler from the front: a ``hard`` cooler is a box with a lid and latches, a ``soft`` one
    a rounded bag with a zip and a shoulder strap, and a ``wheeled`` one a box with a tow handle
    and two wheels."""
    kind = cooler_type.lower()
    dark = _shade(fill.base, 0.3)
    if kind == "soft":
        return _label(
            [
                _line("M126,150 Q200,40 274,150", 8, stroke=STRAP),
                _path(
                    "M90,160 Q90,140 112,140 L288,140 Q310,140 310,160 L314,310 Q314,330 292,330 L108,330 Q86,330 86,310 Z",
                    paint,
                ),
                _line("M96,176 L304,176", 4, stroke=dark),
                _rect(240, 170, 26, 12, STEEL, 3),
                _rect(140, 220, 120, 70, _tint(fill.base, 0.2), 10),
                _highlight("M104,190 L102,310", 5, 0.4),
            ],
            label,
        )
    out = [
        _path("M80,150 L320,150 L330,320 Q330,334 316,334 L84,334 Q70,334 70,320 Z", paint),
        _rect(70, 120, 260, 40, dark, 8),
        _rect(100, 160, 22, 26, STEEL, 3),
        _rect(278, 160, 22, 26, STEEL, 3),
        _line("M90,300 L310,300", LW_DETAIL),
        _highlight("M90,180 L86,310", 5, 0.4),
    ]
    if kind == "wheeled":
        out += [
            _ell(110, 336, 26, 26, STRAP),
            _ell(110, 336, 8, 8, STEEL),
            _line("M300,150 L340,80 L364,80", 8, stroke=POLE),
        ]
    else:
        out += [_rect(170, 104, 60, 18, STRAP, 6)]
    return _label(out, label)


def bottle_insul(
    paint: str, fill: Fill, label: str | None, bottle_lid: str = "screw cap"
) -> list[str]:
    """A tall bottle: a ``straw lid`` carries a flip straw and a loop, a ``chug lid`` a wide spout
    under a flip cap, and a ``screw cap`` a plain cap with a carry loop."""
    kind = bottle_lid.lower()
    dark = _shade(fill.base, 0.3)
    out = [
        _path(
            "M156,110 L244,110 Q262,130 262,160 L262,330 Q262,350 242,350 L158,350 Q138,350 138,330 L138,160 Q138,130 156,110 Z",
            paint,
        ),
        _rect(150, 96, 100, 18, STEEL, 4),
        _line("M140,320 L260,320", LW_DETAIL, stroke=dark),
        _highlight("M154,160 L154,320", 6, 0.45),
    ]
    if kind == "straw lid":
        out += [
            _rect(152, 60, 96, 40, STRAP, 10),
            _line("M200,60 L214,26", 6, stroke=_tint(STRAP, 0.6)),
            _path("M236,66 Q270,60 262,92", "none", 6, stroke=STRAP),
        ]
    elif kind == "chug lid":
        out += [
            _rect(152, 68, 96, 32, STRAP, 8),
            _path("M180,68 L220,68 L216,48 L184,48 Z", STEEL),
            _path("M224,72 Q256,40 250,80", "none", 6, stroke=STRAP),
        ]
    else:
        out += [
            _rect(156, 64, 88, 36, STRAP, 8),
            _path("M176,64 Q200,24 224,64", "none", 8, stroke=STRAP),
        ]
    return _label(out, label)


def bike_light(
    paint: str, fill: Fill, label: str | None, light_position: str = "front"
) -> list[str]:
    """A light on its strap mount: a ``front`` light is a long housing with a round white lens,
    a ``rear`` one a short housing with a ribbed red lens, and a ``twin-pack`` both."""
    kind = light_position.lower()

    def front(x: float, y: float) -> list[str]:
        return [
            _rect(x, y, 150, 70, paint, 22),
            _ell(x + 24, y + 35, 28, 30, LENS),
            _ell(x + 24, y + 35, 12, 12, "#ffffff", LW_DETAIL),
            _rect(x + 60, y + 70, 50, 26, STRAP, 6),
            _highlight(f"M{x + 60},{y + 12} L{x + 136},{y + 12}", 5, 0.45),
        ]

    def rear(x: float, y: float) -> list[str]:
        return [
            _rect(x, y, 70, 110, paint, 18),
            _rect(x + 10, y + 12, 50, 86, "#d84a3a", 12),
            *[
                _line(
                    f"M{x + 14},{y + 30 + 18 * i} L{x + 56},{y + 30 + 18 * i}",
                    LW_DETAIL,
                    stroke=_shade("#d84a3a", 0.4),
                )
                for i in range(4)
            ],
            _rect(x + 70, y + 40, 22, 30, STRAP, 5),
        ]

    if kind == "rear":
        return _label(rear(150, 130), label)
    if kind == "twin-pack":
        return _label([*front(60, 120), *rear(260, 110)], label)
    return _label(front(125, 150), label)


def bike_lock(paint: str, fill: Fill, label: str | None, lock_type: str = "shackle") -> list[str]:
    """A lock: a ``shackle`` lock is a steel U in a crossbar, a ``chain`` a run of links in a
    sleeve to a padlock, a ``folding`` lock its jointed plates folded in a fan, and a ``cable``
    lock a coil with a lock head."""
    kind = lock_type.lower()
    if kind == "chain":
        links = [_ell(96 + 26 * i, 110 + 22 * i, 18, 12, paint) for i in range(6)]
        return _label(
            [
                *links,
                _rect(250, 230, 70, 80, STEEL, 12),
                _path("M262,232 Q285,190 308,232", "none", 8, stroke=POLE),
                _ell(285, 270, 7, 7, STRAP, LW_DETAIL),
            ],
            label,
        )
    if kind == "folding":
        plates = [
            _rect(100, 196 - 14 * i, 210, 26, paint if i % 2 == 0 else _shade(fill.base, 0.2), 10)
            for i in range(5)
        ]
        return _label(
            [*plates, _rect(270, 220, 70, 60, STEEL, 10), _ell(305, 250, 8, 8, STRAP, LW_DETAIL)],
            label,
        )
    if kind == "cable":
        rings = [
            f"M90,{180 + 12 * i} A90,50 0 1,0 270,{180 + 12 * i} A90,50 0 1,0 90,{180 + 12 * i}"
            for i in range(4)
        ]
        return _label(
            [
                *[_line(d, 14) for d in rings],
                *[_line(d, 9, stroke=paint) for d in rings],
                _rect(250, 240, 80, 56, paint, 10),
                _ell(300, 268, 8, 8, STRAP, LW_DETAIL),
            ],
            label,
        )
    return _label(
        [
            _path(
                "M140,250 L140,140 Q140,60 200,60 Q260,60 260,140 L260,250 L236,250 L236,140 Q236,86 200,86 Q164,86 164,140 L164,250 Z",
                STEEL,
            ),
            _rect(110, 240, 180, 50, paint, 18),
            _ell(250, 265, 9, 9, STRAP, LW_DETAIL),
            _highlight("M124,252 L276,252", 5, 0.45),
        ],
        label,
    )


def sled(paint: str, fill: Fill, label: str | None, sled_type: str = "toboggan") -> list[str]:
    """A sled from above: a ``toboggan`` is a long deck curled at the nose with a pull rope, a
    ``saucer`` a round dish with two handles, and a ``steerable`` sled a deck on two runners with
    a steering bar."""
    kind = sled_type.lower()
    dark = _shade(fill.base, 0.3)
    if kind == "saucer":
        return _label(
            [
                _ell(200, 200, 140, 140, paint),
                _ell(200, 200, 100, 100, _tint(fill.base, 0.2), LW_DETAIL),
                _rect(52, 186, 30, 28, STRAP, 8),
                _rect(318, 186, 30, 28, STRAP, 8),
                _highlight("M110,120 Q150,80 210,72", 6, 0.45),
            ],
            label,
        )
    parts = [
        _path(
            "M120,80 Q120,40 160,40 L240,40 Q280,40 280,80 L280,340 Q280,360 260,360 L140,360 Q120,360 120,340 Z",
            paint,
        ),
        _path("M126,82 Q130,52 160,50 L240,50 Q270,52 274,82 Q200,100 126,82 Z", dark),
    ]
    if kind == "steerable":
        parts = [
            _rect(108, 70, 10, 300, POLE, 4),
            _rect(282, 70, 10, 300, POLE, 4),
            *parts,
            _line("M110,110 L290,110", 8, stroke=STRAP),
        ]
    else:
        parts += [
            _path("M160,40 Q200,0 240,40", "none", 5, stroke=STRAP),
            *[
                _line(f"M140,{140 + 60 * i} L260,{140 + 60 * i}", LW_DETAIL, stroke=dark)
                for i in range(3)
            ],
        ]
    parts.append(_highlight("M136,100 L136,330", 5, 0.4))
    return _label(_tilted(parts, -20), label)


def snowboard(
    paint: str, fill: Fill, label: str | None, board_profile: str = "camber"
) -> list[str]:
    """A board from above, standing, with two bindings; beside it the board's edge from the side:
    ``camber`` arches up between the contact points, ``rocker`` bows down, and ``flat`` lies
    straight."""
    kind = board_profile.lower()
    dark = _shade(fill.base, 0.3)
    out = [
        _path("M150,40 Q200,20 250,40 Q236,200 250,360 Q200,380 150,360 Q164,200 150,40 Z", paint),
        _rect(166, 110, 68, 34, STRAP, 8),
        _rect(166, 250, 68, 34, STRAP, 8),
        _line("M162,190 L238,210", LW_DETAIL, stroke=dark),
        _highlight("M168,60 L172,340", 5, 0.4),
    ]
    edge = {
        "rocker": "M300,40 Q330,200 300,360",
        "flat": "M312,40 Q306,44 306,60 L306,340 Q306,356 312,360",
    }.get(kind, "M318,40 Q296,48 302,70 Q292,200 302,330 Q296,352 318,360")
    out.append(_line(edge, 6, stroke=_shade(fill.base, 0.45)))
    return _label(out, label)


def ski_goggles(
    paint: str, fill: Fill, label: str | None, lens_shape: str = "spherical"
) -> list[str]:
    """Goggles face on: a ``spherical`` lens bulges top and bottom, a ``cylindrical`` lens is flat
    top to bottom with straight edges, and a ``toric`` lens sits between, its corners rounder."""
    kind = lens_shape.lower()
    lens = {
        "cylindrical": "M100,160 L300,160 L300,250 L224,250 Q200,226 176,250 L100,250 Z",
        "toric": "M100,164 Q200,140 300,164 L300,248 L224,252 Q200,230 176,252 L100,248 Z",
    }.get(
        kind,
        "M100,170 Q200,120 300,170 Q306,214 300,252 L224,258 Q200,232 176,258 L100,252 Q94,214 100,170 Z",
    )
    return _label(
        [
            _rect(30, 186, 340, 40, STRAP, 10),
            _path(
                "M84,150 Q200,108 316,150 Q330,210 316,268 L230,272 Q200,244 170,272 L84,268 Q70,210 84,150 Z",
                paint,
            ),
            _path(lens, LENS),
            _highlight("M120,176 Q160,160 200,158", 6, 0.6),
            _line("M120,236 Q160,246 176,244", LW_DETAIL, stroke=_shade(LENS, 0.3)),
        ],
        label,
    )


SHAPES = {
    "hiking_backpack": hiking_backpack,
    "cooler": cooler,
    "bottle_insul": bottle_insul,
    "bike_light": bike_light,
    "bike_lock": bike_lock,
    "sled": sled,
    "snowboard": snowboard,
    "ski_goggles": ski_goggles,
}
register(SHAPES)
