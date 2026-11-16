"""Drawings of the craft kits, remote-control vehicles and learning toys of gen#960 (slice 3).
Each is its own shape, registers itself with the kit, and prints the style's theme on a name
panel, as its title shows it, so two derived styles of one kind never share a results tile.

==============  =========================================  ===========================
shape           what it draws                              params
==============  =========================================  ===========================
craft_tub       a craft kit's open box: beads, mosaic      kind (bead, mosaic, gem
                tiles, gems or pom-poms in its trays       art, pom-pom), theme
rc_vehicle      a remote-control car, truck, boat or       kind (car, truck, boat,
                helicopter in the body's color, with its   helicopter), theme
                handset and aerial beside it
learning_toy    an activity cube, a shape sorter, a        kind (activity cube, shape
                learning tablet or a counting abacus in    sorter, learning tablet,
                the toy's color                            counting abacus), theme
==============  =========================================  ===========================

A kind may be the toy type's own words ("bead kit", "remote-control car"); the words the type
adds are dropped. No drawing prints a number: a style's sizes share one image.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import Fill, _panel, _path, _shade, _tint, register
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect
from synthetic_ecommerce_data.domains.retail.kit_toy_parts import _shadow, _star

DARK, STEEL, GLASS, WATER = "#2f2f35", "#cfd5da", "#e4eef4", "#9cc9e6"
#: The bright colors of the beads, tiles and pom-poms, whatever the kit's color.
MIX = ("#c8312e", "#3f6fb5", "#5f9a4a", "#f2c94c", "#e07a1f", "#f2a1b8")


def _kind(value: str, prefix: str = "", suffix: str = "") -> str:
    return value.lower().removeprefix(prefix).removesuffix(suffix).strip()


def craft_tub(
    paint: str, fill: Fill, label: str | None, kind: str = "bead kit", theme: str = ""
) -> list[str]:
    """A craft kit's open box: the theme on the lid, four trays of the kind's pieces below."""
    kind = _kind(kind, suffix=" kit")
    out = [_shadow(200, 362, 150), _rect(60, 36, 280, 120, _tint(fill.base, 0.45), 12)]
    out += _panel(80, 66, 240, 50, theme.title() or None, 26)
    out.append(_rect(60, 170, 280, 180, _tint(fill.base, 0.75), 12))
    for i in range(4):
        x, y = 76 + (i % 2) * 130, 186 + (i // 2) * 80
        out.append(_rect(x, y, 118, 68, "#ffffff", 8))
        for j in range(3):
            color = MIX[(i + j) % len(MIX)]
            cx, cy = x + 22 + j * 37, y + 34
            if kind == "mosaic":
                out.append(_rect(cx - 13, cy - 13, 26, 26, color, 3))
            elif kind == "gem art":
                out.append(
                    _path(
                        f"M{cx},{cy - 16} L{cx + 14},{cy} L{cx},{cy + 16} L{cx - 14},{cy} Z", color
                    )
                )
            elif kind == "pom-pom":
                out.append(_ell(cx, cy, 15, 15, color))
            else:
                out += [_ell(cx, cy, 11, 11, color), _ell(cx, cy, 3, 3, "#ffffff", 1)]
    return _label(out, label)


def _wheel(cx: float, cy: float, r: float) -> list[str]:
    return [_ell(cx, cy, r, r, DARK), _ell(cx, cy, r * 0.4, r * 0.4, STEEL, 2)]


def rc_vehicle(
    paint: str, fill: Fill, label: str | None, kind: str = "car", theme: str = ""
) -> list[str]:
    """A remote-control vehicle of the kind in ``paint``, the handset and its aerial beside it."""
    kind = _kind(kind, prefix="remote-control ")
    dark = _shade(fill.base, 0.35)
    out = [_shadow(200, 360, 160)]
    out += _panel(70, 30, 260, 46, theme.title() or None, 26)
    if kind == "truck":
        out += [_rect(70, 196, 230, 70, paint, 12), _rect(196, 150, 84, 56, paint, 10)]
        out.append(_rect(210, 160, 56, 32, GLASS, 6))
        out += _wheel(112, 290, 40) + _wheel(258, 290, 40)
    elif kind == "boat":
        out.append(_path("M40,236 L320,236 L292,300 L72,300 Z", paint))
        out += [_rect(150, 190, 100, 48, dark, 8), _rect(164, 198, 72, 24, GLASS, 4)]
        out.append(_path("M30,318 Q90,300 150,318 T270,318 T340,318", "none", 4, stroke=WATER))
    elif kind == "helicopter":
        out += [_ell(176, 230, 86, 52, paint), _rect(250, 218, 96, 20, paint, 8)]
        out += [_ell(150, 222, 38, 30, GLASS), _rect(90, 160, 180, 10, DARK, 4)]
        out += [_rect(172, 168, 12, 14, DARK, 2), _rect(110, 292, 140, 8, DARK, 3)]
    else:
        out.append(_path("M60,260 L80,206 L150,190 L236,190 L290,214 L320,260 Z", paint))
        out.append(_path("M156,198 L230,198 L262,216 L144,216 Z", GLASS))
        out += _wheel(116, 270, 30) + _wheel(266, 270, 30)
    out += [_rect(300, 96, 64, 52, dark, 10), _rect(330, 52, 4, 46, DARK, 2)]
    out += [_ell(318, 122, 9, 9, STEEL, 2), _ell(346, 122, 9, 9, STEEL, 2)]
    return _label(out, label)


def learning_toy(
    paint: str, fill: Fill, label: str | None, kind: str = "activity cube", theme: str = ""
) -> list[str]:
    """A learning toy of the kind in ``paint``: an activity cube with a bead maze on top, a
    shape sorter with its shapes, a tablet with letter keys, or an abacus of colored beads."""
    kind = _kind(kind)
    dark = _shade(fill.base, 0.35)
    out = [_shadow(200, 362, 150)]
    out += _panel(70, 30, 260, 46, theme.title() or None, 26)
    if kind == "shape sorter":
        out += [_rect(80, 160, 240, 170, paint, 14), _rect(80, 140, 240, 30, dark, 10)]
        out += [_ell(130, 220, 22, 22, DARK), _rect(178, 198, 44, 44, DARK, 2)]
        out += [_path("M270,196 L294,242 L246,242 Z", DARK), _star(200, 290, 20, MIX[3])]
    elif kind == "learning tablet":
        out += [_rect(70, 100, 260, 240, paint, 22), _rect(96, 122, 208, 110, GLASS, 8)]
        out += [_ell(120 + 40 * i, 280, 14, 14, MIX[i]) for i in range(5)]
        out.append(_star(200, 176, 26, MIX[3]))
    elif kind == "counting abacus":
        out += [_rect(70, 100, 16, 240, dark, 4), _rect(314, 100, 16, 240, dark, 4)]
        out.append(_rect(60, 330, 280, 20, paint, 6))
        for row in range(5):
            y = 130 + row * 42
            out.append(_rect(86, y - 2, 228, 4, STEEL, 2))
            out += [_ell(110 + 24 * b, y, 11, 14, MIX[row]) for b in range(4)]
    else:
        out += [_rect(100, 180, 200, 160, paint, 12), _rect(120, 200, 70, 60, GLASS, 6)]
        out += [_ell(250, 230, 26, 26, MIX[0]), _rect(214, 280, 66, 40, MIX[3], 6)]
        out.append(_path("M120,180 L120,120 Q200,90 280,120 L280,180", "none", 5, stroke=dark))
        out += [_ell(150 + 50 * i, 118 - (i % 2) * 14, 12, 12, MIX[i + 1]) for i in range(3)]
    return _label(out, label)


SHAPES = {"craft_tub": craft_tub, "rc_vehicle": rc_vehicle, "learning_toy": learning_toy}
register(SHAPES)
