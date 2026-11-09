"""Scarves (gen#422, a spec by gen#351): knitted, woven, silk squares and snoods, six colors.

The Accessories leaves held no scarf, so ``silk scarf`` found a silk tie or a planted cap. This is
**Womens > Accessories > Scarves** (gen#248: there is no top-level Accessories root; a scarf is
unisex, which the ``audience`` entry says and the path does not). The kind is the drawing's shape
(``kind``), equal to the row's structured ``scarf_style`` entry; the material is a second entry and
the length in centimetres a measured one (``item_length``). The SKU axis is the six main colors
(gen#275). Not derivable: the department grows by authored rows. Every name here is invented.

The decoys are same-type scarves whose text claims what their structured entries deny (gen#294): a
polyester scarf that names silk (class 4), a blue fringe in the description of a black scarf
(class 5), a color word or another category's noun in a range name (two of class 6: "Green Fell
Scarf" is black) and another brand's name in the description (class 7).
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import barry_plotter
from synthetic_ecommerce_data.domains.retail.kit import (
    LW,
    LW_DETAIL,
    PAPER,
    Fill,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Womens", "Accessories", "Scarves")
_W, _P = "Wrenfield", "Pellbrook"
#: The folded loop around the neck, and the two tails that hang from it, the right one longer.
_LOOP = "M112,118 Q200,66 288,118 Q306,160 262,186 Q200,216 138,186 Q94,160 112,118 Z"
_NECK = "M148,128 Q200,102 252,128 Q262,146 240,156 Q200,170 160,156 Q138,146 148,128 Z"
_LEFT = "M138,184 L118,312 L188,322 L204,200 Z"
_RIGHT = "M200,202 L206,346 L276,338 L262,186 Z"
#: A silk square laid on its corner, its hem inset, and the knot of a square worn tied.
_SQUARE = "M200,62 L340,202 L200,342 L60,202 Z"
_HEM = "M200,84 L318,202 L200,320 L82,202 Z"


def _fringe(x0: int, x1: int, y0: int, y1: int) -> list[str]:
    """The short threads under a tail's hem, from (x0, y0) to (x1, y1)."""
    return [
        _line(f"M{x0 + (x1 - x0) * n / 10:g},{y0 + (y1 - y0) * n / 10:g} l0,18", 2)
        for n in range(11)
    ]


def _ribs(paint: str, x0: int, x1: int, top: int, bottom: int) -> list[str]:
    return [
        _line(f"M{x},{top} L{x},{bottom}", 1.4, ' stroke-opacity=".5"', _shade(paint, 0.45))
        for x in range(x0, x1, 12)
    ]


def scarf(paint: str, fill: Fill, label: str | None, kind: str = "Knitted") -> list[str]:
    """A scarf as it is sold. ``kind`` is knitted (a loop and two ribbed tails with a fringe), woven
    (the same fall, with a woven check and a fringe), a silk square (a square on its corner with a
    rolled hem) or a snood (a closed ring and no tails)."""
    kind = kind.lower()
    if kind == "silk square":
        out = [_path(_SQUARE, paint, LW)]
        out += [_line(_HEM, LW_DETAIL, ' stroke-dasharray="4 3"')]
        out += [
            _line(
                f"M{x},{y} l34,34 M{x + 34},{y} l-34,34",
                1.3,
                ' stroke-opacity=".5"',
                _shade(paint, 0.4),
            )
            for x, y in ((183, 124), (123, 185), (243, 185), (183, 246))
        ]
        return out
    if kind == "snood":
        out = [
            _path("M92,150 Q200,86 308,150 L308,262 Q200,330 92,262 Z", paint, LW),
            _path(
                "M126,150 Q200,116 274,150 Q290,170 262,184 Q200,206 138,184 Q110,170 126,150 Z",
                PAPER,
                LW_DETAIL,
            ),
        ]
        out += _ribs(paint, 104, 300, 196, 250)
        return out
    out = [_path(_LEFT, paint, LW), _path(_RIGHT, paint, LW), _path(_LOOP, paint, LW)]
    out += [_path(_NECK, PAPER, LW_DETAIL)]
    out += _fringe(118, 188, 312, 322) + _fringe(206, 276, 346, 338)
    if kind == "knitted":
        out += _ribs(paint, 142, 190, 208, 300) + _ribs(paint, 214, 268, 216, 328)
    else:
        for y in (232, 266, 300):
            out.append(
                _line(f"M124,{y - 10} L194,{y}", 2.4, ' stroke-opacity=".6"', _shade(paint, 0.4))
            )
            out.append(
                _line(f"M204,{y + 6} L268,{y - 2}", 2.4, ' stroke-opacity=".6"', _shade(paint, 0.4))
            )
        out += [
            _line(
                "M150,200 L136,312 M170,204 L158,316 M226,210 L232,338 M248,206 L256,338",
                2.4,
                ' stroke-opacity=".6"',
                _shade(paint, 0.4),
            )
        ]
    return out


register({"scarf": scarf})

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)


def _attrs(kind: str, material: str, length: str) -> tuple[tuple[str, ...], ...]:
    return (
        a("scarf_style", "Scarf style", kind), a("material", "Material", material),
        ("item_length", "Item length", length, "CMT", float(length) * 10),
        a("audience", "Audience", "Unisex"),
    )  # fmt: skip


def _row(code, title, brand, price, kind, material, length, desc, colors=_SIX) -> Row:
    return Row(code, title, brand, "Clothing", _PATH, "Scarf", price, "scarf", desc, colors,
               _attrs(kind, material, length), params=(("kind", kind),))  # fmt: skip


SPEC = TypeSpec(
    key="scarf",
    department="Clothing",
    product_type="Scarf",
    owners=((_W, "own"), (_P, "third_party")),
    apparel_exempt="an accessory, not a garment: its decoys are authored here (gen#294)",
    rows=(
        _row("SCFKNT", "Chunky Knitted Scarf", _W, 14.0, "Knitted", "Acrylic", "180",
             "A long ribbed scarf with a fringe at each end, thick enough for the coldest walk to work."),
        _row("SCFWVN", "Woven Wool Scarf", _P, 22.0, "Woven", "Wool", "190",
             "A soft wool scarf in a woven check with a short fringe, warm and light around the neck."),
        _row("SCFCSH", "Cashmere Blend Scarf", _W, 45.0, "Woven", "Cashmere", "170",
             "A fine woven scarf with a brushed finish and a short fringe, soft enough to wear against the skin."),
        _row("SCFSLK", "Silk Square Scarf", _P, 32.0, "Silk Square", "Silk", "90",
             "A smooth silk square with a hand rolled hem, to knot at the neck or tie to a bag handle."),
        _row("SCFSLP", "Silk Neck Scarf", _W, 26.0, "Silk Square", "Silk", "70",
             "A small silk scarf with a rolled hem that folds to a neat band at the neck."),
        _row("SCFSNO", "Ribbed Knit Snood", _W, 16.0, "Snood", "Wool", "60",
             "A closed loop of ribbed wool that pulls over the head and sits close to the neck, with no ends to tie."),
        *barry_plotter.rows_of("Scarf"),  # the Barry Plotter range (gen#925)
    ),
    decoys=(
        Decoy(4, "silk scarf", "material facet: a silk query keeps Silk in the material",
              _row("DCSCF1", "Satin Finish Scarf", _W, 9.0, "Woven", "Polyester", "160",
                   "A polyester scarf with a sheen in a style like our silk scarves, machine washable and easy to fold.",
                   (BLACK,))),
        Decoy(5, "blue scarf", "color facet: blue means the scarf color, not a word in the text",
              _row("DCSCF2", "Fringed Wool Scarf", _P, 15.0, "Woven", "Wool", "180",
                   "A black wool scarf with a blue fringe at each end.",
                   (BLACK,))),
        Decoy(6, "green scarf", "color facet: a color word in a range name is not the scarf color",
              _row("DCSCF4", "Green Fell Scarf", _P, 12.0, "Knitted", "Acrylic", "170",
                   "A black knitted scarf from the Fell range, in a plain rib.",
                   (BLACK,))),
        Decoy(6, "glove scarf", "type facet: another category's noun in a range name does not make the scarf that category",
              _row("DCSCF5", "Glove Lane Scarf", _W, 11.0, "Woven", "Cotton", "180",
                   "A black woven scarf from the Lane range, light enough for spring.",
                   (BLACK,))),
        Decoy(7, "pellbrook scarf", "brand facet: a brand named in the text is not the product's brand",
              _row("DCSCF3", "Everyday Woven Scarf", _W, 8.0, "Woven", "Cotton", "170",
                   "A budget alternative to Pellbrook woven scarves, in a plain black weave.",
                   (BLACK,))),
    ),
)  # fmt: skip
