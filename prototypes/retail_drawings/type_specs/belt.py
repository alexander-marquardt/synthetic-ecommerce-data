"""Belts (gen#422, a spec by gen#351): four materials, three buckles, six colors and six waists.

The Accessories leaves held bags and umbrellas, so ``black leather belt`` and ``mens belt 34 inch``
found nothing or the jeans-belt distractor. This is **Mens > Accessories > Belts** (gen#248: there
is no top-level Accessories root; the leaf is the one the distractor ``JNSBLT`` already sits in).
The material and the buckle are the drawing's params (``material``, ``buckle``), equal to the
row's structured entries. The SKU axes are the six main colors (gen#275) and the waist in inches
(``waist_in``, which the export states with its unit), so ``34 inch`` is a measured value.
Not derivable: the department grows by authored rows. Every name here is invented.

The decoys are same-type belts whose text claims what their structured entries deny (gen#294): a
pin-buckle belt that names the automatic buckle (class 4), a blue lining in the description of a
black belt (class 5) and another brand's name in the description (class 7). The text-match for
the word itself is the ranker's: a sander belt in Tools never outranks a leather belt.
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _line, _path, _shade, register
from type_registry import Decoy, Row, TypeSpec, a, cw

GOLD = "#d6b56a"
_PATH = ("Mens", "Accessories", "Belts")
_W, _P = "Wrenfield", "Pellbrook"
_WAISTS = ("30", "32", "34", "36", "38", "40")  # inches
_Y0, _Y1 = 186, 218  # the strap's top and bottom edge


def _studs(x: float, y: float) -> str:
    return (
        f'<circle cx="{x:g}" cy="{y:g}" r="3.4" fill="#ffffff" stroke="{INK}" stroke-width="1.2"/>'
    )


def _strap(material: str, paint: str) -> list[str]:
    """The strap from the keeper to the tail, with the weave or the stitching of its material."""
    pointed = material in ("leather", "faux leather")
    tail = "L352,186 L372,202 L352,218" if pointed else "L360,186 L360,218"
    out = [_path(f"M118,{_Y0} {tail} L118,{_Y1} Z", paint, LW)]
    if material == "webbing":
        out += [
            _line(f"M118,{y} L360,{y}", 1.2, ' stroke-opacity=".55"', _shade(paint, 0.35))
            for y in (193, 200, 207, 211)
        ]
        out += [
            _line(f"M118,{_Y0 + 3} L360,{_Y0 + 3}", 2, "", "#f4f1ea"),
            _line(f"M118,{_Y1 - 3} L360,{_Y1 - 3}", 2, "", "#f4f1ea"),
        ]
    elif material == "canvas":
        out += [
            _line(f"M{x},{_Y1} L{x + 18},{_Y0}", 1.1, ' stroke-opacity=".4"', _shade(paint, 0.4))
            for x in range(124, 350, 12)
        ]
        out += [
            _line(
                f"M124,{_Y0 + 4} L346,{_Y0 + 4}",
                LW_DETAIL,
                ' stroke-dasharray="5 3"',
                _shade(paint, 0.4),
            )
        ]
    else:
        out += [
            _line(
                f"M124,{_Y0 + 5} L{346 if pointed else 356},{_Y0 + 5} M124,{_Y1 - 5} L{346 if pointed else 356},{_Y1 - 5}",
                LW_DETAIL,
                ' stroke-dasharray="5 3"',
                _shade(paint, 0.4),
            )
        ]
        if material == "faux leather":
            out += [
                f'<circle cx="{x}" cy="{y}" r="1.1" fill="{_shade(paint, 0.3)}" fill-opacity=".7"/>'
                for x in range(140, 340, 20)
                for y in (196, 208)
            ]
    return out


def _buckle(kind: str) -> list[str]:
    """The buckle at the left end: a pin frame with a prong, a flat plate or an automatic slide."""
    if kind == "pin":
        return [
            f'<rect x="58" y="166" width="62" height="72" rx="14" fill="none" stroke="{GOLD}" stroke-width="10"/>',
            f'<rect x="53" y="161" width="72" height="82" rx="17" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
            f'<rect x="63" y="171" width="52" height="62" rx="9" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
            _line("M88,172 L88,232", 6, stroke=GOLD),
            _line("M88,202 L136,202", 4.5, stroke=GOLD),
            _line("M88,202 L136,202", 1.2),
        ]
    if kind == "plate":
        return [
            f'<rect x="52" y="168" width="70" height="68" rx="9" fill="{GOLD}" stroke="{INK}" stroke-width="{LW}"/>',
            f'<rect x="62" y="178" width="50" height="48" rx="5" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
            f'<rect x="72" y="190" width="30" height="24" rx="3" fill="#ffffff" fill-opacity=".35" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        ]
    return [
        f'<rect x="48" y="172" width="82" height="60" rx="8" fill="{GOLD}" stroke="{INK}" stroke-width="{LW}"/>',
        f'<rect x="58" y="182" width="62" height="40" rx="4" fill="none" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<rect x="74" y="160" width="30" height="16" rx="4" fill="{_shade(GOLD, 0.15)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *[_line(f"M{x},{_Y1 + 3} L{x},{_Y1 + 11}", 2.4) for x in range(150, 350, 14)],
    ]


def belt_buckled(
    paint: str, fill: Fill, label: str | None, material: str = "Leather", buckle: str = "Pin"
) -> list[str]:
    """A belt laid flat, buckle on the left. ``material`` is leather, faux leather (stitched and
    grained), canvas (a woven twill) or webbing (flat ribs between two pale edges); ``buckle``
    is a pin (a frame and a prong, with punched holes), a plate (a flat gold plate, a slide) or an
    automatic (a ratchet slide, with teeth under the strap and no holes)."""
    material, buckle = material.lower(), buckle.lower()
    out = _strap(material, paint)
    if buckle == "pin":
        out += [_studs(x, 202) for x in (200, 228, 256, 284, 312)]
    out += [
        f'<rect x="146" y="{_Y0 - 5}" width="14" height="{_Y1 - _Y0 + 10}" rx="3" fill="{_shade(paint, 0.12)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>'
    ]
    return [
        '<g transform="translate(-24 -24.2) scale(1.12)">'
        + "".join([*out, *_buckle(buckle)])
        + "</g>"
    ]


register({"belt_buckled": belt_buckled})

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)


def _attrs(material: str, buckle: str, width: str) -> tuple[tuple[str, ...], ...]:
    return (
        a("material", "Material", material), a("buckle", "Buckle", buckle),
        ("belt_width", "Belt width", width, "CMT", float(width) * 10), a("audience", "Audience", "Mens"),
    )  # fmt: skip


def _row(code, title, brand, price, material, buckle, width, desc, colors=_SIX) -> Row:
    sizes = tuple((n, price) for n in _WAISTS)
    return Row(code, title, brand, "Clothing", _PATH, "Belt", price, "belt_buckled", desc, colors,
               _attrs(material, buckle, width), sizes, size_key="waist_in",
               params=(("material", material), ("buckle", buckle)))  # fmt: skip


SPEC = TypeSpec(
    key="belt",
    department="Clothing",
    product_type="Belt",
    owners=((_W, "own"), (_P, "third_party")),
    rows=(
        _row("BLTLTH", "Leather Dress Belt", _W, 16.0, "Leather", "Pin", "3",
             "A smooth full-grain belt with a polished pin buckle and five punched holes, cut to wear with trousers."),
        _row("BLTFXL", "Faux Leather Plate Buckle Belt", _P, 11.0, "Faux Leather", "Plate", "3.5",
             "A stitched faux leather belt with a flat plate buckle that slides to size, with a grained finish."),
        _row("BLTCNV", "Canvas Casual Belt", _W, 9.0, "Canvas", "Pin", "3.8",
             "A woven canvas belt with a pin buckle and a pale stitched edge, for chinos and shorts."),
        _row("BLTWEB", "Webbing Belt", _P, 10.0, "Webbing", "Plate", "3.2",
             "A flat woven webbing belt with a plate buckle that grips anywhere along the strap, so it fits every waist."),
        _row("BLTAUT", "Automatic Leather Belt", _W, 19.0, "Leather", "Automatic", "3.5",
             "A leather belt with a ratchet slide under the strap that clicks to a fit in small steps, with no holes to punch."),
    ),
    decoys=(
        Decoy(4, "automatic belt", "buckle facet: an automatic query keeps the Automatic buckle",
              _row("DCBLT1", "Fashion Pin Belt", _W, 8.0, "Faux Leather", "Pin", "3",
                   "A pin buckle belt in a style like our automatic ratchet belts, with five fixed holes and no ratchet slide.",
                   (BLACK,))),
        Decoy(5, "blue belt", "color facet: blue means the belt color, not a word in the text",
              _row("DCBLT2", "Lined Dress Belt", _P, 12.0, "Leather", "Pin", "3",
                   "A black leather belt with a blue lining stitched along its inner edge, with a pin buckle.",
                   (BLACK,))),
        Decoy(7, "pellbrook belt", "brand facet: a brand named in the text is not the product's brand",
              _row("DCBLT3", "Everyday Casual Belt", _W, 7.0, "Canvas", "Plate", "3.2",
                   "A budget alternative to Pellbrook canvas belts, in a plain black weave with a plate buckle.",
                   (BLACK,))),
    ),
)  # fmt: skip
