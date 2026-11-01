"""Men's pants (gen#780): everyday briefs and hipsters in their own leaf under Mens Underwear.

In British English underwear is called pants, and a demo search for ``pants`` should find it for
men too: ``Mens/Underwear`` held boxers and vests and no pants. The type is sold by cut (briefs,
low-rise briefs, hipsters) and fabric, at about the size of the women's pants (:mod:`.pants`).
It has its own drawing, ``mens_pants``: a contoured pouch and no fly, so a shopper tells it from
the boxers' Y-front at thumbnail size. The cut a row states is the cut it is drawn in. The styles
are templates only (``derivable`` False). The text-match decoys come from the apparel plan
(gen#311): three of each class, cloned from these rows.
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import details
from synthetic_ecommerce_data.domains.retail.kit import Fill, _line, _path, register
from synthetic_ecommerce_data.domains.retail.kit_garments import _dark
from synthetic_ecommerce_data.domains.retail.kit_underwear import _band, _g, _hi, _shadow
from synthetic_ecommerce_data.domains.retail.type_registry import (
    ApparelPlan,
    Row,
    TypeSpec,
    a,
    cw,
    sizes,
)

# --------------------------------------------------------------------------
# The drawing
# --------------------------------------------------------------------------

#: cut -> (waist y, waist half-width, hip y, hip half-width, crotch y, crotch half-width,
#:         leg control x, leg control y, band height)
BRIEF_CUTS = {
    "brief": (124, 100, 182, 106, 292, 32, 54, 224, 22),
    "low_rise": (150, 104, 194, 108, 290, 32, 58, 232, 16),
}
_STITCH = ' stroke-dasharray="4 3"'


def _brief_body(paint: str, fill: Fill, cut: str) -> tuple[list[str], float, float]:
    """A brief's outline cut high at the leg; returns the parts, the band's foot and the crotch y."""
    wy, ww, hy, hw, cy, cwid, qx, qy, bh = BRIEF_CUTS[cut]
    mid = (ww + hw) / 2 + 3
    d = (f"M{200 - ww},{wy} L{200 + ww},{wy} Q{200 + mid:.1f},{(wy + hy) / 2:.1f} {200 + hw},{hy} "
         f"Q{200 + qx},{qy} {200 + cwid},{cy} L{200 - cwid},{cy} Q{200 - qx},{qy} {200 - hw},{hy} "
         f"Q{200 - mid:.1f},{(wy + hy) / 2:.1f} {200 - ww},{wy} Z")  # fmt: skip
    out = [_path(d, paint), _dark(d, 0.04)]
    out.append(_g("leg-opening", [_line(f"M{200 + hw - 7},{hy + 5} Q{200 + qx - 6},{qy - 7} {200 + cwid - 3},{cy - 7}", 1.2, _STITCH, _hi(fill))]))
    out.append(_g("leg-opening", [_line(f"M{200 - hw + 7},{hy + 5} Q{200 - qx + 6},{qy - 7} {200 - cwid + 3},{cy - 7}", 1.2, _STITCH, _hi(fill))]))
    out += _band(200 - ww, 200 + ww, wy, wy + bh, paint)
    return out, wy + bh, cy


def _hipster_body(paint: str, fill: Fill) -> tuple[list[str], float, float]:
    """A hipster: a low waist and a short square leg, cut straight across."""
    d = ("M96,148 L304,148 Q312,190 312,248 L230,256 Q214,236 200,232 Q186,236 170,256 "
         "L88,248 Q88,190 96,148 Z")  # fmt: skip
    out = [_path(d, paint), _dark(d, 0.04)]
    out.append(_g("leg-opening", [_line("M94,238 L168,244", 1.3, _STITCH, _hi(fill))]))
    out.append(_g("leg-opening", [_line("M232,244 L306,238", 1.3, _STITCH, _hi(fill))]))
    out.append(_line("M170,256 Q186,236 200,232 Q214,236 230,256", 1.2))
    out += _band(96, 304, 148, 166, paint)
    return out, 166, 232


def mens_pants(paint: str, fill: Fill, label: str | None, cut: str = "brief") -> list[str]:
    """Men's pants: a brief, a low-rise brief or a hipster, each with a contoured pouch (one
    ``pouch`` mark), a waistband and two leg openings; no fly."""
    cut = cut.replace("-", "_").replace(" ", "_")
    if cut == "hipster":
        body, top, foot = _hipster_body(paint, fill)
    else:
        body, top, foot = _brief_body(paint, fill, cut if cut in BRIEF_CUTS else "brief")
    pouch = f"M176,{top} Q166,{(top + foot) / 2 + 6:.1f} 200,{foot - 22} Q234,{(top + foot) / 2 + 6:.1f} 224,{top}"
    out = [_shadow(330, 110), *body]
    out.append(_g("pouch", [_dark(pouch + " Z", 0.06), _line(pouch, 1.3, _STITCH, _hi(fill))]))
    return out


register({"mens_pants": mens_pants})
details.register_parts("mens_pants", {"waistband": details.WAIST})

# --------------------------------------------------------------------------
# The rows
# --------------------------------------------------------------------------

_LING = "Lingerie & Nightwear"
PATH = ("Mens", "Underwear", "Pants")
SIZES = ("S", "M", "L", "XL", "XXL")
_HB, _WF, _TW, _QS, _HP, _LM = (
    "Harbour & Pine", "Wrenfield", "Thistle & Wren", "Quillon Sleep", "Hollinwray Knits", "Larkmoor",
)  # fmt: skip
BLACK, WHITE = cw("Black", "#2f2f35", "solid", "#8f989f"), cw("White", "#f4f1ea", "solid", "#b9b4a6")
NAVY, GREY = cw("Navy", "#2c3a5e", "solid", "#d8dce8"), cw("Grey", "#9a9ca0", "solid", "#55575c")
CHARCOAL = cw("Charcoal", "#4a4d52", "solid", "#c8cbd0")
BLUE, RED = cw("Blue", "#2f6db5", "solid", "#e4eefa"), cw("Red", "#b3263a", "solid", "#f4d8dc")
GREEN = cw("Green", "#3c6e4f", "solid", "#d8e6dc")
YELLOW = cw("Yellow", "#e6c34a", "solid", "#6a5412")
CUTS = {"Briefs": "brief", "Low-Rise Briefs": "low_rise", "Hipster": "hipster"}


def _row(code, title, brand, cut, fabric, price, desc, colors):
    """One style: its cut and fabric are attributes, and the cut is what the drawing shows."""
    return Row(
        code, title, brand, _LING, PATH, "Mens Pants", price, "mens_pants", f"{desc} Machine washable.",
        colors, (a("cut", "Cut", cut), a("fabric", "Fabric", fabric)),
        sizes(price, SIZES), params=(("cut", CUTS[cut]),),
    )  # fmt: skip


ROWS = (
    _row("MPBRCT", "Mens Cotton Brief Pants", _HB, "Briefs", "Cotton", 7.0,
         "Classic men's brief pants in soft stretch cotton with a covered waistband.",
         (BLACK, WHITE, NAVY, GREY, BLUE)),
    _row("MPBRMD", "Mens Modal Brief Pants", _WF, "Briefs", "Modal", 9.0,
         "Smooth modal brief pants for men, light and soft against the skin.",
         (BLACK, NAVY, CHARCOAL, GREY)),
    _row("MPLRCT", "Mens Low-Rise Pants", _TW, "Low-Rise Briefs", "Cotton", 7.5,
         "Low-rise men's pants in stretch cotton that sit on the hip.",
         (BLACK, WHITE, RED, BLUE, GREY)),
    _row("MPLRMF", "Mens Microfiber Low-Rise Pants", _HP, "Low-Rise Briefs", "Microfiber", 9.0,
         "Low-rise men's pants in light microfiber with flat seams, for the gym and every day.",
         (BLACK, NAVY, GREEN, CHARCOAL)),
    _row("MPHPCT", "Mens Cotton Hipster Pants", _QS, "Hipster", "Cotton", 8.0,
         "Men's hipster pants in soft cotton with a short square leg.",
         (BLACK, GREY, NAVY, WHITE, GREEN)),
    _row("MPHPBM", "Mens Bamboo Hipster Pants", _LM, "Hipster", "Bamboo", 10.0,
         "Breathable bamboo hipster pants for men with a soft wide waistband.",
         (BLACK, NAVY, GREY, BLUE)),
    _row("MPBRSP", "Mens Sports Brief Pants", _HP, "Briefs", "Microfiber", 9.5,
         "Quick-dry men's brief pants with a supportive cut, for running and training.",
         (BLACK, BLUE, RED, YELLOW, CHARCOAL)),
    _row("MPHPST", "Mens Stretch Hipster Pants", _TW, "Hipster", "Cotton Stretch", 8.5,
         "Men's hipster pants in cotton stretch that keep their shape wash after wash.",
         (BLACK, NAVY, RED, GREY)),
    _row("MPLRBM", "Mens Bamboo Low-Rise Pants", _WF, "Low-Rise Briefs", "Bamboo", 9.5,
         "Low-rise men's pants in soft bamboo with a smooth leg line.",
         (BLACK, WHITE, CHARCOAL, GREEN)),
    _row("MPBRES", "Mens Everyday Brief Pants", _QS, "Briefs", "Cotton", 6.0,
         "Everyday men's brief pants in breathable cotton with a soft flat waistband.",
         (WHITE, BLACK, GREY, YELLOW, BLUE)),
)  # fmt: skip

SPEC = TypeSpec(
    key="mens_pants",
    department=_LING,
    product_type="Mens Pants",
    rows=ROWS,
    derivable=False,
    apparel=ApparelPlan(
        family="u",
        compounds=(
            ("boxer", "Boxer Brief Pants"),
            ("hipster", "Hipster Pants"),
            ("swim", "Swim Brief Pants"),
        ),
    ),
)
