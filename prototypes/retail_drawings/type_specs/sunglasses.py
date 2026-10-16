"""Sunglasses (gen#422, a spec by gen#351): five frames, three lenses, UV400, in six colors.

The Accessories leaves held bags and umbrellas, so ``polarised sunglasses`` and ``aviator
sunglasses`` found nothing or an unrelated item. This is **Womens > Accessories > Sunglasses**
(gen#248: there is no top-level Accessories root; a pair is unisex, which the ``audience`` entry
says and the path does not). A frame is the drawing's shape (``frame``), the lens its tint
(``lens``), both equal to the row's structured ``frame_shape`` and ``lens_type`` entries. The SKU
axis is the frame color alone, so the six main colors are offered across the type (gen#275).
Not derivable: the department grows by authored rows. Every name here is invented.

The decoys are same-type pairs whose text claims what their structured entries deny (gen#294):
a pair that names UV400 and has no UV protection (class 4), a blue tint in the description of a
black frame (class 5), a color word or another category's noun in a range name (two of class 6: "White Marsh Sunglasses" is black) and another brand's name in the description (class 7).
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _highlight, _line, _path, _shade, register
from type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Womens", "Accessories", "Sunglasses")
_W, _P = "Wrenfield", "Pellbrook"

#: Frame -> (left lens outline, its centre, the rim's inner scale, the lens's drop in the rim).
#: A wayfarer's rim is thick on top, so its lens sits lower; the sport frame is one wide lens.
_FRAMES = {
    "aviator": ("M48,168 Q112,154 176,168 Q184,226 150,252 Q112,276 78,246 Q42,214 48,168 Z", (112, 210), 0.84, 0),
    "wayfarer": ("M44,170 L178,162 L174,224 Q170,250 142,252 L84,252 Q56,250 52,224 Z", (112, 208), 0.8, 5),
    "round": ("M50,200 C50,166 78,138 112,138 C146,138 174,166 174,200 C174,234 146,262 112,262 C78,262 50,234 50,200 Z", (112, 200), 0.84, 0),
    "cat-eye": ("M44,214 Q38,176 60,158 Q120,148 180,178 Q178,236 138,252 Q84,264 44,214 Z", (112, 208), 0.82, 0),
    "sport": ("M40,184 Q200,146 360,184 Q358,252 300,258 Q252,260 232,228 Q200,214 168,228 Q148,260 100,258 Q42,252 40,184 Z", (200, 208), 0.88, 0),
}  # fmt: skip
_TEMPLES = {"round": "M52,184 L22,170", "sport": "M42,186 L20,172"}
_DEFAULT_TEMPLE = "M48,174 L22,160"
_LENS = {"polarised": "#2b333c", "mirrored": "#9db4c6"}
_GRADIENT = "sunglasses-lens-gradient"


def _lens(d: str, cx: float, cy: float, scale: float, drop: float, lens: str) -> list[str]:
    """One lens set in its rim: the lens outline shrunk toward its centre, then the tint's marks."""
    fill = f"url(#{_GRADIENT})" if lens == "gradient" else _LENS.get(lens, _LENS["polarised"])
    inner = [_path(d, fill, LW_DETAIL)]
    if lens == "mirrored":
        inner += [
            _highlight(f"M{cx - 30:g},{cy + 4:g} L{cx - 4:g},{cy - 22:g}", 5, 0.75),
            _highlight(f"M{cx - 14:g},{cy + 18:g} L{cx + 16:g},{cy - 12:g}", 3, 0.6),
            _line(f"M{cx - 38:g},{cy + 22:g} L{cx + 34:g},{cy + 22:g}", 1.6, ' stroke-opacity=".5"', "#4a6a82"),
        ]
    elif lens == "gradient":
        inner += [_highlight(f"M{cx - 24:g},{cy - 22:g} L{cx - 6:g},{cy - 28:g}", 3, 0.45)]
    else:
        inner += [_highlight(f"M{cx - 26:g},{cy - 16:g} L{cx - 10:g},{cy - 26:g}", 4, 0.55)]
    return [f'<g transform="translate({cx:g} {cy + drop:g}) scale({scale:g}) translate({-cx:g} {-cy:g})">' + "".join(inner) + "</g>"]


def sunglasses(paint: str, fill: Fill, label: str | None, frame: str = "aviator", lens: str = "gradient") -> list[str]:
    """A pair of sunglasses seen from the front. ``frame`` is aviator (teardrop lenses), wayfarer
    (squared, a heavy top rim), round, cat-eye (upswept outer corners) or sport (one wide wrap
    lens); ``lens`` is polarised (a dark lens), gradient (dark at the top, clear below) or
    mirrored (a pale reflective lens with streaks). The frame takes the style's color."""
    frame, lens = frame.lower(), lens.lower()
    d, (cx, cy), scale, drop = _FRAMES.get(frame, _FRAMES["aviator"])
    temple = _TEMPLES.get(frame, _DEFAULT_TEMPLE)
    out = [
        f'<defs><linearGradient id="{_GRADIENT}" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#2b333c"/><stop offset="1" stop-color="#c9d3db"/></linearGradient></defs>',
        _line(temple, 9, stroke=INK),
        _line(temple, 5.5, stroke=paint),
        f'<g transform="translate(400 0) scale(-1 1)">{_line(temple, 9, stroke=INK)}{_line(temple, 5.5, stroke=paint)}</g>',
    ]
    if frame == "sport":
        out += [_path(d, paint, LW)]
        out += _lens(d, cx, cy, scale, drop, lens)
        out += [_line("M184,232 Q200,244 216,232", 5, stroke=_shade(fill.base, 0.3))]
        return out
    out += [_line("M176,190 Q200,170 224,190", 9, stroke=INK), _line("M176,190 Q200,170 224,190", 5.5, stroke=paint)]
    for mirrored in (False, True):
        side = [_path(d, paint, LW), *_lens(d, cx, cy, scale, drop, lens)]
        out.append(f'<g transform="translate(400 0) scale(-1 1)">{"".join(side)}</g>' if mirrored else "".join(side))
    return out


register({"sunglasses": sunglasses})

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)


def _attrs(frame: str, lens: str, material: str, uv: str = "Yes") -> tuple[tuple[str, str, str], ...]:
    return (
        a("frame_shape", "Frame shape", frame), a("lens_type", "Lens type", lens),
        a("uv400", "UV400", uv), a("frame_material", "Frame material", material),
        a("audience", "Audience", "Unisex"),
    )  # fmt: skip


def _row(code, title, brand, price, frame, lens, material, desc, colors=_SIX, uv="Yes") -> Row:
    return Row(code, title, brand, "Clothing", _PATH, "Sunglasses", price, "sunglasses", desc, colors,
               _attrs(frame, lens, material, uv), params=(("frame", frame), ("lens", lens)))  # fmt: skip


SPEC = TypeSpec(
    key="sunglasses",
    department="Clothing",
    product_type="Sunglasses",
    owners=((_W, "own"), (_P, "third_party")),
    apparel_exempt="an accessory, not a garment: its decoys are authored here (gen#294)",
    rows=(
        _row("SGLAVI", "Aviator Sunglasses", _W, 14.0, "Aviator", "Gradient", "Metal",
             "Classic teardrop aviator sunglasses with a thin metal frame and gradient lenses that fade from dark to clear, with UV400 protection."),
        _row("SGLWAY", "Polarised Wayfarer Sunglasses", _P, 18.0, "Wayfarer", "Polarised", "Acetate",
             "Squared wayfarer sunglasses with a heavy acetate frame and polarised lenses that cut glare off water and roads, with UV400 protection."),
        _row("SGLRND", "Round Mirrored Sunglasses", _W, 16.0, "Round", "Mirrored", "Metal",
             "Round sunglasses with slim metal rims and mirrored lenses, with UV400 protection."),
        _row("SGLCAT", "Cat-Eye Sunglasses", _P, 15.0, "Cat-Eye", "Gradient", "Acetate",
             "Cat-eye sunglasses with upswept corners, a glossy acetate frame and gradient lenses, with UV400 protection."),
        _row("SGLSPT", "Polarised Sport Sunglasses", _W, 22.0, "Sport", "Polarised", "Plastic",
             "Wraparound sport sunglasses with one wide polarised lens and a light plastic frame that stays put when you run or ride, with UV400 protection."),
    ),
    decoys=(
        Decoy(4, "uv400 sunglasses", "UV400 facet: a UV400 query keeps UV400 Yes",
              _row("DCSGL1", "Retro Fashion Sunglasses", _W, 9.0, "Wayfarer", "Gradient", "Plastic",
                   "Retro fashion sunglasses in a frame styled like our UV400 pairs, for looks only: the tinted lens gives no UV protection.",
                   (BLACK,), uv="No")),
        Decoy(5, "blue sunglasses", "color facet: blue means the frame color, not a word in the text",
              _row("DCSGL2", "Tinted Lens Sunglasses", _P, 11.0, "Round", "Mirrored", "Metal",
                   "A black metal frame with lenses that flash a blue tint in the sun, with UV400 protection.",
                   (BLACK,))),
        Decoy(6, "white sunglasses", "color facet: a color word in a range name is not the frame color",
              _row("DCSGL4", "White Marsh Sunglasses", _P, 9.0, "Round", "Gradient", "Metal",
                   "A black metal frame from the Marsh range, with a gradient lens and UV400 protection.",
                   (BLACK,))),
        Decoy(6, "watch sunglasses", "type facet: another category's noun in a range name does not make the sunglasses that category",
              _row("DCSGL5", "Watch Point Sunglasses", _W, 8.0, "Wayfarer", "Polarised", "Plastic",
                   "A black plastic frame from the Point range, with a polarised lens.",
                   (BLACK,))),
        Decoy(7, "pellbrook sunglasses", "brand facet: a brand named in the text is not the product's brand",
              _row("DCSGL3", "Everyday Wayfarer Sunglasses", _W, 8.0, "Wayfarer", "Polarised", "Plastic",
                   "A budget alternative to Pellbrook wayfarer sunglasses, in a plain black plastic frame.",
                   (BLACK,))),
    ),
)  # fmt: skip
