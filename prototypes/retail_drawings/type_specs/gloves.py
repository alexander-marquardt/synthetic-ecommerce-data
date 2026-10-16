"""Gloves (gen#422, a spec by gen#351): knitted, leather, touchscreen and mittens, six colors, four sizes.

The Accessories leaves held bags and umbrellas, so ``touchscreen gloves`` and ``leather gloves``
found nothing or a baseball glove. This is **Womens > Accessories > Gloves** (gen#248: there is no
top-level Accessories root; a pair is unisex, which the ``audience`` entry says and the path does
not). The kind is the drawing's shape (``kind``), equal to the row's structured ``glove_style``
entry; the lining is a second entry. The SKU axes are the six main colors (gen#275) and the size
(``glove_size``, S to XL). Not derivable: the department grows by authored rows. Every name here
is invented.

The decoys are same-type pairs whose text claims what their structured entries deny (gen#294): a
knitted pair that names touchscreen fingertips (class 4), a blue lining in the description of a
black pair (class 5) and another brand's name in the description (class 7).
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _line, _path, _shade, register
from type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Womens", "Accessories", "Gloves")
_W, _P = "Wrenfield", "Pellbrook"
_SIZES = ("S", "M", "L", "XL")
#: A right hand seen from the back, the thumb on the left: the cuff, the palm, four fingers, a thumb.
_THUMB = "L132,266 L104,236 Q84,212 98,196 Q112,184 128,200 L140,218"
_FINGERS = "L140,146 Q140,130 156,130 Q172,130 172,146 L172,128 Q172,112 188,112 Q204,112 204,128 L204,142 Q204,126 220,126 Q236,126 236,142 L236,160 Q236,150 250,150 Q264,150 264,166"
_GLOVE = f"M132,330 {_THUMB} {_FINGERS} L264,266 L270,330 Z"
_MITTEN = f"M132,330 {_THUMB} L140,176 Q140,112 202,112 Q264,112 264,176 L264,266 L270,330 Z"
_TIPS = ((156, 138), (188, 120), (220, 134), (250, 158))


def _cuff(paint: str, ribbed: bool) -> list[str]:
    out = [_path("M130,296 L272,296 L272,336 L128,336 Z", _shade(paint, 0.15), LW)]
    if ribbed:
        out += [
            _line(f"M{x},298 L{x},334", 1.4, ' stroke-opacity=".5"', _shade(paint, 0.45))
            for x in range(138, 270, 10)
        ]
    return out


def gloves(paint: str, fill: Fill, label: str | None, kind: str = "Knitted") -> list[str]:
    """One glove seen from the back. ``kind`` is knitted (a ribbed cuff and knit rows), leather
    (seams between the fingers and a wrist strap with a stud), touchscreen (a glove with a pad on
    each fingertip) or mittens (the four fingers in one block, with a ribbed cuff)."""
    kind = kind.lower()
    mitten = kind == "mittens"
    out = [_path(_MITTEN if mitten else _GLOVE, paint, LW)]
    if not mitten:
        out += [
            _line(f"M{x},{y} L{x},262", LW_DETAIL) for x, y in ((172, 146), (204, 142), (236, 160))
        ]
    if kind in ("knitted", "mittens"):
        out += [
            _line(f"M{x},{y} l6,8 l6,-8", 1.2, ' stroke-opacity=".45"', _shade(paint, 0.45))
            for y in range(200, 290, 14)
            for x in range(144, 244, 14)
        ]
        out += _cuff(paint, True)
    elif kind == "leather":
        out += [
            _line(f"M{x},{y} L{x},258", 1.3, ' stroke-dasharray="3 3"', _shade(paint, 0.4))
            for x, y in ((156, 150), (188, 134), (220, 148), (250, 170))
        ]
        out += _cuff(paint, False)
        out += [
            _path("M128,304 L274,304 L274,322 L128,322 Z", _shade(paint, 0.3), LW_DETAIL),
            f'<circle cx="244" cy="313" r="5" fill="#d6b56a" stroke="{INK}" stroke-width="1.2"/>',
        ]
    else:
        out += [
            f'<circle cx="{x}" cy="{y}" r="9" fill="{_shade(paint, 0.35)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
            for x, y in _TIPS
        ]
        out += [
            f'<circle cx="{x}" cy="{y}" r="3.4" fill="#ffffff" fill-opacity=".7"/>'
            for x, y in _TIPS
        ]
        out += _cuff(paint, True)
    return out


register({"gloves": gloves})

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)


def _attrs(kind: str, lining: str) -> tuple[tuple[str, str, str], ...]:
    return (
        a("glove_style", "Glove style", kind), a("lining", "Lining", lining),
        a("audience", "Audience", "Unisex"),
    )  # fmt: skip


def _row(code, title, brand, price, kind, lining, desc, colors=_SIX) -> Row:
    return Row(code, title, brand, "Clothing", _PATH, "Gloves", price, "gloves", desc, colors,
               _attrs(kind, lining), tuple((s, price) for s in _SIZES), size_key="glove_size",
               params=(("kind", kind),))  # fmt: skip


SPEC = TypeSpec(
    key="gloves",
    department="Clothing",
    product_type="Gloves",
    owners=((_W, "own"), (_P, "third_party")),
    apparel_exempt="an accessory, not a garment: its decoys are authored here (gen#294)",
    rows=(
        _row("GLVKNT", "Knitted Gloves", _W, 8.0, "Knitted", "Fleece",
             "Stretchy ribbed knit gloves with a soft fleece lining, warm enough for a winter commute."),
        _row("GLVLTH", "Leather Gloves", _P, 24.0, "Leather", "Wool",
             "Smooth leather gloves with a wool lining, a wrist strap and a snug fit through the fingers."),
        _row("GLVTCH", "Touchscreen Gloves", _W, 12.0, "Touchscreen", "Thermal",
             "Warm gloves with conductive fingertip pads, so you can answer a phone or swipe a screen without taking them off."),
        _row("GLVMIT", "Fleece Lined Mittens", _P, 9.0, "Mittens", "Fleece",
             "Chunky knitted mittens with a soft fleece lining that keeps all four fingers together and warm."),
        _row("GLVDRV", "Leather Driving Gloves", _W, 28.0, "Leather", "Unlined",
             "Unlined leather driving gloves with a thin palm for a firm grip on the wheel and a snap wrist strap."),
        _row("GLVTHM", "Thermal Touchscreen Gloves", _P, 15.0, "Touchscreen", "Thermal",
             "Thermal gloves with a brushed lining and touchscreen fingertip pads, light enough to type in."),
    ),
    decoys=(
        Decoy(4, "touchscreen gloves", "style facet: a touchscreen query keeps the Touchscreen style",
              _row("DCGLV1", "Fashion Knitted Gloves", _W, 6.0, "Knitted", "Unlined",
                   "Knitted gloves in a style like our touchscreen gloves, for looks only: the fingertips are plain knit and do not work on a screen.",
                   (BLACK,))),
        Decoy(5, "blue gloves", "color facet: blue means the glove color, not a word in the text",
              _row("DCGLV2", "Lined Leather Gloves", _P, 13.0, "Leather", "Fleece",
                   "Black leather gloves with a blue fleece lining that shows at the wrist.",
                   (BLACK,))),
        Decoy(7, "pellbrook gloves", "brand facet: a brand named in the text is not the product's brand",
              _row("DCGLV3", "Everyday Knitted Gloves", _W, 5.0, "Knitted", "Unlined",
                   "A budget alternative to Pellbrook knitted gloves, in a plain black knit.",
                   (BLACK,))),
    ),
)  # fmt: skip
