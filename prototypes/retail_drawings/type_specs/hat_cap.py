"""Hats and caps (gen#422, a spec by gen#351): five kinds, six colors, three size forms.

The Accessories leaves held bags and umbrellas, so ``red beanie`` and ``white baseball cap`` found
nothing or an unrelated item. This is **Womens > Accessories > Hats & Caps** (gen#248: there is no
top-level Accessories root; a hat is unisex, which the ``audience`` entry says and the path does
not). The kind is the drawing's shape (``kind``), equal to the row's structured ``hat_style`` entry.
The SKU axes are the six main colors (gen#275) and the size (``hat_size``: one size, S/M, L/XL).
Not derivable: the department grows by authored rows. Every name here is invented.

The decoys are same-type hats whose text claims what their structured entries deny (gen#294): an
acrylic beanie that names wool (class 4), a blue label in the description of a black beanie
(class 5), a color word or another category's noun in a range name (two of class 6: "Yellow Marsh Beanie" is black) and another brand's name in the description (class 7). A bottle cap or a pen cap is a
product of another type, which the ranker's category intent keeps below a cap here.
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from kit import INK, LW, LW_DETAIL, Fill, _line, _path, _shade, register
from type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Womens", "Accessories", "Hats & Caps")
_W, _P = "Wrenfield", "Pellbrook"
_ONE, _ADJ = ("One Size",), ("S/M", "L/XL")


def _band(paint: str, d: str) -> str:
    return _path(d, _shade(paint, 0.18), LW_DETAIL)


def _beanie(paint: str) -> list[str]:
    ribs = [
        _line(
            f"M{x},232 L{x},{176 + abs(x - 200) // 3}",
            1.1,
            ' stroke-opacity=".45"',
            _shade(paint, 0.4),
        )
        for x in range(130, 272, 14)
    ]
    return [
        _path("M96,252 C90,146 310,146 304,252 Z", paint, LW),
        *ribs,
        _path("M92,250 L308,250 L312,292 L88,292 Z", _shade(paint, 0.12), LW),
        *[
            _line(f"M{x},252 L{x},290", 1.4, ' stroke-opacity=".5"', _shade(paint, 0.45))
            for x in range(104, 300, 12)
        ],
        f'<circle cx="200" cy="142" r="20" fill="{_shade(paint, 0.1)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
    ]


def _baseball_cap(paint: str) -> list[str]:
    return [
        _path("M106,258 C100,150 270,142 288,256 Z", paint, LW),
        _line("M196,150 C176,190 168,226 170,256", LW_DETAIL),
        _line("M196,150 C226,190 240,226 238,256", LW_DETAIL),
        _path(
            "M104,258 Q216,284 344,256 Q352,282 270,296 Q168,304 104,262 Z", _shade(paint, 0.2), LW
        ),
        _line("M120,264 Q220,286 330,262", LW_DETAIL, ' stroke-dasharray="4 3"'),
        f'<circle cx="196" cy="148" r="8" fill="{_shade(paint, 0.15)}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        *[
            f'<circle cx="{x}" cy="{y}" r="2.6" fill="#ffffff" stroke="{INK}" stroke-width="1"/>'
            for x, y in ((150, 206), (246, 204))
        ],
        _path("M104,258 L288,256 L286,268 Q190,278 104,266 Z", _shade(paint, 0.12), LW_DETAIL),
    ]


def _bucket_hat(paint: str) -> list[str]:
    return [
        _path("M126,252 C116,150 284,150 274,252 Z", paint, LW),
        _path("M64,246 Q200,284 336,246 L322,282 Q200,326 78,282 Z", _shade(paint, 0.1), LW),
        _path(
            "M124,246 Q200,266 276,246 L275,224 Q200,244 125,224 Z", _shade(paint, 0.2), LW_DETAIL
        ),
        *[
            _line(
                f"M{x},262 L{x - 3},{290 - abs(x - 200) // 12}",
                1.1,
                ' stroke-opacity=".5"',
                _shade(paint, 0.4),
            )
            for x in range(100, 310, 22)
        ],
        *[
            f'<circle cx="{x}" cy="196" r="2.6" fill="#ffffff" stroke="{INK}" stroke-width="1"/>'
            for x in (166, 234)
        ],
    ]


def _fedora(paint: str) -> list[str]:
    return [
        _path(
            "M58,252 Q200,298 342,252 Q312,226 200,226 Q88,226 58,252 Z", _shade(paint, 0.06), LW
        ),
        _path(
            "M128,240 C122,170 168,148 200,160 C232,148 278,170 272,240 Q200,262 128,240 Z",
            paint,
            LW,
        ),
        _line("M168,158 Q200,186 232,158", LW_DETAIL),
        _path(
            "M128,238 Q200,260 272,238 L271,218 Q200,238 129,218 Z", _shade(paint, 0.35), LW_DETAIL
        ),
        _line("M255,222 L292,258 M255,222 L268,262", 3.2, "", _shade(paint, 0.35)),
    ]


def _sun_hat(paint: str) -> list[str]:
    weave = [
        _line(
            f"M{x0},{y} Q200,{y + 40} {400 - x0},{y}",
            1.1,
            ' stroke-opacity=".45"',
            _shade(paint, 0.4),
        )
        for x0, y in ((52, 252), (84, 247), (116, 243))
    ]
    return [
        _path("M30,252 Q200,306 370,252 Q300,224 200,224 Q100,224 30,252 Z", paint, LW),
        *weave,
        _path("M130,240 C128,186 272,186 270,240 Q200,256 130,240 Z", paint, LW),
        _path(
            "M130,232 Q200,250 270,232 L270,216 Q200,234 130,216 Z", _shade(paint, 0.3), LW_DETAIL
        ),
        _line("M150,214 Q200,196 250,214", 1.3, ' stroke-opacity=".5"', _shade(paint, 0.4)),
    ]


_KINDS = {
    "beanie": _beanie,
    "baseball cap": _baseball_cap,
    "bucket hat": _bucket_hat,
    "fedora": _fedora,
    "sun hat": _sun_hat,
}


def hat(paint: str, fill: Fill, label: str | None, kind: str = "Beanie") -> list[str]:
    """A hat seen from the front. ``kind`` is a beanie (a ribbed knit with a cuff and a pompom), a
    baseball cap (a six-panel crown and a curved peak), a bucket hat (a sloped brim), a fedora (a
    pinched crown, a band and a brim) or a sun hat (a wide woven brim and a low crown)."""
    return _KINDS.get(kind.lower(), _beanie)(paint)


register({"hat": hat})

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)


def _attrs(kind: str, material: str) -> tuple[tuple[str, str, str], ...]:
    return (
        a("hat_style", "Hat style", kind), a("material", "Material", material),
        a("audience", "Audience", "Unisex"),
    )  # fmt: skip


def _row(code, title, brand, price, kind, material, sizes, desc, colors=_SIX) -> Row:
    return Row(code, title, brand, "Clothing", _PATH, "Hat", price, "hat", desc, colors,
               _attrs(kind, material), tuple((s, price) for s in sizes), size_key="hat_size",
               params=(("kind", kind),))  # fmt: skip


SPEC = TypeSpec(
    key="hat_cap",
    department="Clothing",
    product_type="Hat",
    owners=((_W, "own"), (_P, "third_party")),
    apparel_exempt="an accessory, not a garment: its decoys are authored here (gen#294)",
    rows=(
        _row("HATBNE", "Ribbed Knit Beanie", _W, 8.0, "Beanie", "Acrylic", _ONE,
             "A stretchy ribbed knit beanie with a deep cuff that folds down over the ears, with a soft pompom on top."),
        _row("HATWBN", "Cuffed Wool Beanie", _P, 14.0, "Beanie", "Wool", _ONE,
             "A close-fitting wool beanie with a turn-up cuff, warm on a cold walk and soft against the forehead."),
        _row("HATCAP", "Cotton Baseball Cap", _W, 10.0, "Baseball Cap", "Cotton", _ADJ,
             "A six-panel cotton baseball cap with a curved peak, stitched eyelets and an adjustable strap at the back."),
        _row("HATBKT", "Cotton Bucket Hat", _P, 12.0, "Bucket Hat", "Cotton", _ADJ,
             "A soft cotton bucket hat with a sloped brim that shades the face and packs flat in a bag."),
        _row("HATFED", "Wool Felt Fedora", _W, 24.0, "Fedora", "Wool Felt", _ADJ,
             "A wool felt fedora with a pinched crown, a ribbon band and a medium brim, shaped to keep its dent."),
        _row("HATSUN", "Wide Brim Straw Sun Hat", _P, 16.0, "Sun Hat", "Straw", _ONE,
             "A woven straw sun hat with a wide brim and a low crown, light enough for the beach."),
    ),
    decoys=(
        Decoy(4, "wool beanie", "material facet: a wool query keeps Wool in the material",
              _row("DCHAT1", "Soft Knit Beanie", _W, 6.0, "Beanie", "Acrylic", _ONE,
                   "A knit beanie in the shape and the cuff of our wool beanies, made of acrylic with no wool in the yarn.",
                   (BLACK,))),
        Decoy(5, "blue beanie", "color facet: blue means the hat color, not a word in the text",
              _row("DCHAT2", "Labelled Knit Beanie", _P, 9.0, "Beanie", "Acrylic", _ONE,
                   "A black knit beanie with a small blue label sewn on the cuff.",
                   (BLACK,))),
        Decoy(6, "yellow beanie", "color facet: a color word in a range name is not the hat color",
              _row("DCHAT4", "Yellow Marsh Beanie", _P, 8.0, "Beanie", "Acrylic", _ONE,
                   "A black acrylic beanie from the Marsh range, with a plain cuff.",
                   (BLACK,))),
        Decoy(6, "scarf cap", "type facet: another category's noun in a range name does not make the cap that category",
              _row("DCHAT5", "Scarf Lane Cap", _W, 7.0, "Baseball Cap", "Cotton", _ADJ,
                   "A black cotton twill cap from the Lane range, with a curved peak.",
                   (BLACK,))),
        Decoy(7, "pellbrook cap", "brand facet: a brand named in the text is not the product's brand",
              _row("DCHAT3", "Everyday Cotton Cap", _W, 7.0, "Baseball Cap", "Cotton", _ADJ,
                   "A budget alternative to Pellbrook baseball caps, in a plain black cotton twill.",
                   (BLACK,))),
    ),
)  # fmt: skip
