"""Carry bag shapes for the retail drawing kit (gen#1114): belt, messenger and laptop bags.

Each shape reads the style's form from ``bag_shape`` and its surface from ``material``, as
:mod:`kit_bags` does, so a derived style that swaps its material draws the one it states.

=============  ==========================================  ================================
shape          ``bag_shape``                               ``material``
=============  ==========================================  ================================
belt_bag       crescent, box, pouch (on a buckled belt)    leather, faux leather, canvas, nylon
messenger_bag  courier, satchel, utility (wide strap)      leather, faux leather, canvas, nylon
laptop_bag     briefcase, top load, folio                  leather, faux leather, canvas, nylon
=============  ==========================================  ================================

Every param is a string with a default, so each shape also draws bare.
"""

# ruff: noqa: E501 -- SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details
from synthetic_ecommerce_data.domains.retail.kit import (
    Fill,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_accessories import HARDWARE, _band, _circle, _rect
from synthetic_ecommerce_data.domains.retail.kit_bags import _label, _surface

#: The belt of every belt bag form and the strap of every messenger form.
_BELT = "M70,182 C10,64 390,64 330,182"
_STRAP = "M84,176 C44,0 356,0 316,176"
_ZIP = ' stroke-dasharray="7 3"'


def belt_bag(paint: str, fill: Fill, label: str | None, bag_shape: str = "crescent", material: str = "nylon") -> list[str]:  # fmt: skip
    """A small bag on a belt: a zipped half-moon ``crescent``, a ``box`` with a front pocket, or a
    flapped ``pouch``."""
    dark = _shade(fill.base, 0.3)
    out = [*_band(_BELT, dark, 14), _rect(178, 81, 44, 26, HARDWARE, 5, 1.8)]
    if bag_shape == "box":
        out += [_path("M62,190 Q62,176 76,176 L324,176 Q338,176 338,190 L338,322 Q338,336 324,336 L76,336 Q62,336 62,322 Z", paint),
                _line("M76,196 L324,196", 2.4, _ZIP),
                _path("M88,218 L312,218 L312,320 L88,320 Z", _tint(fill.base, 0.18)),
                *_surface(material, fill, 102, 240, 298, 312),
                _line("M88,230 L312,230", 2.2, _ZIP)]  # fmt: skip
    elif bag_shape == "pouch":
        out += [_path("M56,184 L344,184 L336,308 Q332,340 300,340 L100,340 Q68,340 64,308 Z", paint),
                *_surface(material, fill, 100, 282, 300, 332),
                _path("M56,184 L344,184 L338,252 Q200,292 62,252 Z", _tint(fill.base, 0.14)),
                _circle(200, 256, 9, HARDWARE, 1.6)]  # fmt: skip
    else:
        out += [_path("M50,182 Q200,168 350,182 Q360,342 200,342 Q40,342 50,182 Z", paint),
                *_surface(material, fill, 104, 226, 296, 318),
                _line("M62,204 Q200,190 338,204", 2.4, _ZIP),
                _rect(314, 196, 22, 12, HARDWARE, 4, 1.6)]  # fmt: skip
    return _label(out, label)


def messenger_bag(paint: str, fill: Fill, label: str | None, bag_shape: str = "courier", material: str = "canvas") -> list[str]:  # fmt: skip
    """A wide bag on a shoulder strap: a ``courier`` bag whose deep flap clips shut, a ``satchel``
    with one tongue and lock, or a ``utility`` bag with two front pockets."""
    dark = _shade(fill.base, 0.3)
    out = [*_band(_STRAP, dark, 16),
           _path("M52,176 L348,176 L348,330 Q348,346 332,346 L68,346 Q52,346 52,330 Z", paint)]  # fmt: skip
    if bag_shape == "utility":
        out += [*_surface(material, fill, 66, 228, 334, 252),
                _path("M52,176 L348,176 L348,222 L52,222 Z", _tint(fill.base, 0.14)),
                *[p for x in (70, 208) for p in (_path(f"M{x},256 L{x + 122},256 L{x + 122},336 L{x},336 Z", _tint(fill.base, 0.18)),
                                                 _path(f"M{x},256 L{x + 122},256 L{x + 122},282 L{x},282 Z", _shade(fill.base, 0.12)),
                                                 _circle(x + 61, 278, 6, HARDWARE, 1.6))]]  # fmt: skip
    elif bag_shape == "satchel":
        out += [*_surface(material, fill, 66, 290, 334, 338),
                _path("M52,176 L348,176 L348,236 Q340,276 300,276 L100,276 Q60,276 52,236 Z", _shade(fill.base, 0.12)),
                _path("M180,236 L220,236 L220,296 L200,308 L180,296 Z", dark),
                _rect(186, 270, 28, 20, HARDWARE, 3, 1.8)]  # fmt: skip
    else:
        out += [_path("M46,172 L354,172 L354,308 L46,308 Z", _tint(fill.base, 0.1)),
                *_surface(material, fill, 120, 190, 280, 296),
                *[p for x in (74, 296) for p in (_path(f"M{x},262 L{x + 30},262 L{x + 30},332 L{x},332 Z", dark),
                                                 _rect(x - 3, 294, 36, 22, HARDWARE, 4, 1.8))]]  # fmt: skip
    return _label(out, label)


def laptop_bag(paint: str, fill: Fill, label: str | None, bag_shape: str = "briefcase", material: str = "leather") -> list[str]:  # fmt: skip
    """A padded bag for a laptop: a ``briefcase`` with two handles and a front pocket, a ``top load``
    bag with one flat handle and a full flap pocket, or a slim ``folio`` zipped round three sides."""
    dark = _shade(fill.base, 0.3)
    if bag_shape == "folio":
        out = [_path("M54,120 Q54,104 70,104 L330,104 Q346,104 346,120 L346,308 Q346,324 330,324 L70,324 Q54,324 54,308 Z", paint),
               *_surface(material, fill, 88, 138, 312, 290),
               _line("M346,116 L70,116 Q66,116 66,120 L66,308 Q66,312 70,312 L346,312", 2.4, _ZIP),
               _rect(318, 106, 24, 14, HARDWARE, 4, 1.6)]  # fmt: skip
    elif bag_shape == "top load":
        out = [_path("M140,150 L140,112 Q140,100 152,100 L248,100 Q260,100 260,112 L260,150 L242,150 L242,120 L158,120 L158,150 Z", dark),
               _path("M48,160 Q48,146 62,146 L338,146 Q352,146 352,160 L352,328 Q352,342 338,342 L62,342 Q48,342 48,328 Z", paint),
               _line("M60,168 L340,168", 2.4, _ZIP),
               _path("M66,196 L334,196 L334,330 L66,330 Z", _tint(fill.base, 0.12)),
               *_surface(material, fill, 82, 256, 318, 322),
               _path("M66,196 L334,196 L334,240 L66,240 Z", _shade(fill.base, 0.12)),
               _rect(184, 228, 32, 22, HARDWARE, 5, 1.8)]  # fmt: skip
    else:
        out = [*_band("M132,172 C132,72 268,72 268,172", dark, 13),
               _path("M46,164 L354,164 Q360,164 360,172 L352,332 Q351,344 338,344 L62,344 Q49,344 48,332 L40,172 Q40,164 46,164 Z", paint),
               _line("M52,182 L348,182", 2.4, _ZIP),
               _path("M72,222 L328,222 L324,332 L76,332 Z", _tint(fill.base, 0.12)),
               *_surface(material, fill, 92, 246, 308, 322),
               _line("M72,234 L328,234", 2.2, _ZIP),
               *[p for x in (124, 254) for p in (_path(f"M{x},164 L{x + 22},164 L{x + 22},214 L{x},214 Z", dark),
                                                 _circle(x + 11, 198, 6, HARDWARE, 1.6))]]  # fmt: skip
    return _label(out, label)


SHAPES = {"belt_bag": belt_bag, "messenger_bag": messenger_bag, "laptop_bag": laptop_bag}
register(SHAPES)
#: The belt of a belt bag, either side of its buckle, and the strap of a messenger: each is drawn on
#: the very path the shape draws it on, so "with Red Strap" colors all of it.
details.register_parts("belt_bag", {"strap": details.free(("M70,182 C43,128 107,99 180,94", 14.0), ("M330,182 C357,128 293,99 220,94", 14.0))})
details.register_parts("messenger_bag", {"strap": details.free((_STRAP, 16.0))})
