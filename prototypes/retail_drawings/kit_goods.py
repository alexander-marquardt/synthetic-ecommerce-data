"""Small goods whose names borrow a clothing noun (gen#326): shapes for the class-8 decoys.

Shoe laces, a suit carrier, a coat stand, sofa cover and throw, a wash bag, cable ties, jumper
cables, a bike pump: each is the real product, drawn as itself, so a decoy's tile never shows
the garment its title names. Every shape takes the record's fill as its main color.
"""

# ruff: noqa: E501 -- SVG path data, as the other kit files
from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _line, _path, _shade, _tint, register

METAL = "#c9ced3"


def shoe_laces(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Two pairs of flat laces, coiled, each with a metal tip."""
    out = []
    for dy in (0, 88):
        d = f"M92,{140 + dy} C150,{96 + dy} 250,{190 + dy} 306,{140 + dy}"
        out += [_line(d, 13), _line(d, 9, "", paint)]
        out += [
            _path(f"M306,{136 + dy} l22,-6 l0,18 l-22,-6 Z", METAL, LW_DETAIL),
            _path(f"M92,{136 + dy} l-22,-6 l0,18 l22,-6 Z", METAL, LW_DETAIL),
        ]
    return out


def cable_ties(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A bundle of cable ties, ratchet heads at the top, held by a band."""
    out = []
    for i in range(7):
        x = 128 + 24 * i
        out += [
            _path(f"M{x},96 L{x + 12},96 L{x + 12},330 L{x},330 Z", paint, 2),
            _path(
                f"M{x - 2},84 L{x + 14},84 L{x + 14},108 L{x - 2},108 Z", _shade(fill.base, 0.2), 2
            ),
        ]
    out.append(_path("M112,214 L296,214 L296,244 L112,244 Z", "#f4f1ea", LW_DETAIL))
    return out


def jumper_cables(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A pair of jump leads: two heavy cables, a red-and-black clamp at each end."""
    out = [
        _line("M104,150 C170,300 250,300 296,150", 10),
        _line("M104,150 C170,300 250,300 296,150", 6, "", paint),
        _line("M104,170 C170,330 250,330 296,170", 10),
        _line("M104,170 C170,330 250,330 296,170", 6, "", _shade(fill.base, 0.3)),
    ]
    for x in (104, 296):
        out += [
            _path(f"M{x - 26},96 L{x + 26},96 L{x + 18},176 L{x - 18},176 Z", paint, LW),
            _path(f"M{x - 20},82 L{x + 20},82 L{x + 22},98 L{x - 22},98 Z", METAL, LW_DETAIL),
            _line(
                f"M{x - 12},110 L{x + 12},110 M{x - 12},126 L{x + 12},126 M{x - 12},142 L{x + 12},142",
                2,
            ),
        ]
    return out


def pump(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A hand pump: barrel, T handle, hose and foot-peg."""
    return [
        _path("M176,128 L224,128 L224,318 L176,318 Z", paint),
        _path("M170,318 L230,318 L230,336 L170,336 Z", _shade(fill.base, 0.3)),
        _line("M200,128 L200,64 M150,64 L250,64", 10),
        _line("M200,128 L200,64 M150,64 L250,64", 6, "", _tint(fill.base, 0.3)),
        _line("M224,300 C300,300 300,220 270,200", 6),
        _path("M262,192 L284,206 L270,226 L250,212 Z", METAL, LW_DETAIL),
        _line("M176,164 L224,164 M176,176 L224,176", 2),
    ]


def hook_rail(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A wall rail with four coat hooks."""
    out = [_path("M70,130 L330,130 L330,166 L70,166 Z", paint)]
    for x in (110, 170, 230, 290):
        out += [
            _line(f"M{x},166 L{x},214 Q{x},246 {x + 24},238", 9),
            _line(f"M{x},166 L{x},214 Q{x},246 {x + 24},238", 5, "", _tint(fill.base, 0.35)),
        ]
    out.append(_line("M82,148 L90,148 M310,148 L318,148", 4))
    return out


def coat_stand(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A free-standing pole on a tripod foot, with arms and pegs near the top."""
    out = [
        _line("M200,70 L200,320", 11),
        _line("M200,70 L200,320", 7, "", paint),
        _line("M200,320 L130,356 M200,320 L270,356 M200,320 L200,358", 8),
    ]
    for dx in (-56, 56):
        out += [
            _line(f"M200,96 Q{200 + dx},96 {200 + dx},128", 8),
            _line(f"M200,150 Q{200 + dx},150 {200 + dx},182", 8),
        ]
    out.append(
        f'<circle cx="200" cy="62" r="11" fill="{_shade(fill.base, 0.2)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
    )
    return out


def hangers(paint: str, fill: Fill, label: str | None) -> list[str]:
    """Three empty coat hangers, nested."""
    out = []
    for dy, dx in ((0, 0), (22, 8), (44, 16)):
        d = f"M{60 + dx},{214 + dy} L200,{138 + dy} L{340 - dx},{214 + dy} Z"
        out += [
            _path(d, "none", 7, "", INK),
            _path(d, "none", 4, "", paint),
            _line(
                f"M200,{138 + dy} L200,{116 + dy} C200,{92 + dy} 226,{92 + dy} 226,{108 + dy}", 5
            ),
        ]
    return out


def garment_bag(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A long zipped suit carrier with a hanging hook and a clear window."""
    return [
        _path("M110,96 Q200,76 290,96 L304,334 Q200,352 96,334 Z", paint),
        _line("M200,84 L200,52 C200,30 228,30 228,46", 6),
        _line("M200,96 L200,338", 3, ' stroke-dasharray="6 4"'),
        f'<rect x="132" y="150" width="56" height="90" rx="6" fill="#eef3f6" fill-opacity=".8" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect x="196" y="190" width="8" height="26" rx="3" fill="{METAL}" stroke="{INK}" stroke-width="1"/>',
    ]


def mesh_bag(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A zipped mesh wash bag, a diamond weave over its body."""
    body = "M104,120 L296,120 L316,334 Q200,352 84,334 Z"
    weave = " ".join(f"M{90 + 20 * i},{128} L{70 + 20 * i},{340}" for i in range(14))
    weave += " " + " ".join(f"M{84},{150 + 24 * j} L{316},{150 + 24 * j}" for j in range(8))
    return [
        _path(body, _tint(fill.base, 0.55) if fill.base.startswith("#") else paint),
        _line(weave, 1.2, ' stroke-opacity=".5"', _shade(fill.base, 0.2)),
        _path("M104,120 L296,120 L296,146 L104,146 Z", paint, LW_DETAIL),
        f'<rect x="268" y="124" width="14" height="30" rx="4" fill="{METAL}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
    ]


def sofa_cover(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A stretch cover fitted over a sofa: back, arms and a gathered skirt along the hem."""
    skirt = "M70,272 Q86,300 102,272 Q118,300 134,272 Q150,300 166,272 Q182,300 198,272 Q214,300 230,272 Q246,300 262,272 Q278,300 294,272 Q310,300 326,272"
    return [
        _path("M92,110 Q200,92 308,110 L314,226 L86,226 Z", paint),
        _path("M52,176 Q52,150 78,150 L96,150 L96,282 L52,282 Z", _shade(fill.base, 0.12)),
        _path("M348,176 Q348,150 322,150 L304,150 L304,282 L348,282 Z", _shade(fill.base, 0.12)),
        _path("M96,226 L304,226 L304,282 L96,282 Z", paint),
        _line(skirt, 3),
        _line("M200,226 L200,282", 1.4, ' stroke-dasharray="4 3"'),
    ]


def throw(paint: str, fill: Fill, label: str | None) -> list[str]:
    """A woven throw laid flat, banded at each end, with a tassel fringe."""
    out = [_path("M64,116 L336,116 L336,296 L64,296 Z", paint)]
    for y in (140, 272):
        out.append(
            f'<rect x="64" y="{y}" width="272" height="12" fill="{_shade(fill.base, 0.25)}" stroke="{INK}" stroke-width="1"/>'
        )
    fringe = (
        " ".join(f"M{x},296 L{x - 2},{322}" for x in range(72, 336, 12))
        + " "
        + " ".join(f"M{x},116 L{x - 2},{92}" for x in range(72, 336, 12))
    )
    out.append(_line(fringe, 2.4, "", _shade(fill.base, 0.1)))
    return out


SHAPES = {
    "shoe_laces": shoe_laces,
    "cable_ties": cable_ties,
    "jumper_cables": jumper_cables,
    "pump": pump,
    "hook_rail": hook_rail,
    "coat_stand": coat_stand,
    "hangers": hangers,
    "garment_bag": garment_bag,
    "mesh_bag": mesh_bag,
    "sofa_cover": sofa_cover,
    "throw": throw,
}
register(SHAPES)
