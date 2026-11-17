"""Drawings of the figures, dolls and building sets of gen#960 (slice 2). Each is its own shape,
registers itself with the kit, and prints the style's character or theme on a name panel, as
its title shows it, so two derived styles of one kind never share a results tile.

=============  ==========================================  ============================
shape          what it draws                               params
=============  ==========================================  ============================
action_figure  a figure in a blister bubble on a card,     kind (superhero, space,
               in the suit's color: a cape for a           adventure), character
               superhero, a helmet and an air pack for a
               space figure, a hat and a satchel for an
               adventure figure
doll_box       a window box with the doll inside it        kind (fashion, baby, rag),
               (:func:`kit_toys.doll`), in the outfit's    theme
               color
brick_box      a building set's box (:func:`kit_toys.      kind (vehicle, tower,
               building_set`), its theme's art when the    creature), theme
               kit has one, and the kind's model on the
               front: a wheel, a stack of bricks or a
               creature's head
=============  ==========================================  ============================

A kind may be the toy type's own words ("space action figure"); its last words are dropped.
No drawing prints a number: a style's sizes share one image.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import kit_toys
from synthetic_ecommerce_data.domains.retail.kit import Fill, _panel, _path, _shade, _tint, register
from synthetic_ecommerce_data.domains.retail.kit_sports import _ell, _label, _rect
from synthetic_ecommerce_data.domains.retail.kit_toy_parts import SKIN, _shadow, _star

GLASS, BROWN, STEEL = "#e4eef4", "#8a5a3a", "#cfd5da"
#: The themes :func:`kit_toys.building_set` has box art for.
BOX_ART = ("space", "castle", "city", "dinosaurs", "farm")


def _kind(value: str, suffix: str) -> str:
    return value.lower().removesuffix(suffix).strip()


def action_figure(
    paint: str, fill: Fill, label: str | None, kind: str = "superhero", character: str = ""
) -> list[str]:
    """An action figure in a blister bubble on its card, the suit in ``paint``; the kind adds a
    cape (superhero), a helmet and an air pack (space) or a hat and a satchel (adventure)."""
    kind = _kind(kind, " action figure")
    dark = _shade(fill.base, 0.35)
    out = [_shadow(200, 362, 140), _rect(70, 30, 260, 326, _tint(fill.base, 0.72), 14)]
    out += _panel(88, 44, 224, 46, character.title() or None, 26)
    out.append(_rect(112, 104, 176, 236, GLASS, 40))
    if kind == "superhero":
        out.append(_path("M176,176 L150,318 L250,318 L224,176 Z", dark))
    elif kind == "space":
        out.append(_rect(168, 176, 64, 74, STEEL, 8))
    out += [
        _rect(178, 248, 18, 70, dark, 4),
        _rect(204, 248, 18, 70, dark, 4),
        _rect(174, 170, 52, 84, paint, 10),
        _rect(150, 176, 22, 66, paint, 8),
        _rect(228, 176, 22, 66, paint, 8),
        _ell(200, 148, 22, 24, SKIN),
    ]
    if kind == "superhero":
        out.append(_star(200, 206, 13, "#f2c94c"))
    elif kind == "space":
        out.append(_ell(200, 148, 32, 34, GLASS, 2, ' fill-opacity="0.55"'))
    else:
        out += [_ell(200, 128, 38, 8, BROWN), _rect(184, 104, 32, 26, BROWN, 6)]
        out += [_path("M176,172 L224,236", "none", 4), _rect(214, 226, 26, 20, BROWN, 4)]
    return _label(out, label)


def doll_box(
    paint: str, fill: Fill, label: str | None, kind: str = "fashion", theme: str = ""
) -> list[str]:
    """A doll in a window box: the theme on the box's panel, the doll (a fashion, baby or rag
    doll, :func:`kit_toys.doll`) behind the window in the outfit's color."""
    kind = _kind(kind, " doll")
    out = [_shadow(200, 360, 150), _rect(76, 30, 248, 326, _tint(fill.base, 0.55), 12)]
    out += _panel(94, 44, 212, 46, theme.title() or None, 26)
    out.append(_rect(98, 104, 204, 236, GLASS, 8))
    inner = kit_toys.doll(paint, fill, None, kind=kind)
    out.append('<g transform="translate(108 112) scale(0.46)">' + "".join(inner) + "</g>")
    return _label(out, label)


def brick_box(
    paint: str, fill: Fill, label: str | None, kind: str = "vehicle", theme: str = ""
) -> list[str]:
    """A building set's box (:func:`kit_toys.building_set`) with the theme's art when the kit
    draws one, the theme on a panel across the front, and the kind's model in its corner."""
    kind = _kind(kind, " building set")
    art = theme.lower() if theme.lower() in BOX_ART else ""
    out = kit_toys.building_set(paint, fill, None, theme=art)
    out += _panel(68, 270, 168, 40, theme.title() or None, 22)
    if kind == "tower":
        out += [_rect(250, 250 - 22 * i, 30, 22, paint, 3) for i in range(4)]
    elif kind == "creature":
        out += [_ell(262, 236, 26, 22, paint), _ell(254, 230, 5, 5, "#ffffff", 2)]
        out.append(_path("M240,218 L246,198 L256,214 Z", _shade(fill.base, 0.35)))
    else:
        out += [_ell(250, 250, 16, 16, "#2f2f35"), _ell(250, 250, 6, 6, STEEL, 2)]
    return out


SHAPES = {"action_figure": action_figure, "doll_box": doll_box, "brick_box": brick_box}
register(SHAPES)
