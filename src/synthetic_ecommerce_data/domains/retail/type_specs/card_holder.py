"""Card Holder (gen#1114): slim, zip and bifold card cases, a leaf of their own.

**Womens > Accessories > Purses & Wallets > Card Holders**, a breadth type: the scaled build derives
styles that swap the material; the form (``holder_style``), the closure, the card slots and the RFID
blocking stay the template's. One size, so a SKU is a color. The two Purse styles whose ``purse_type``
is Card Holder and the two men's Wallet card holders stay where they are, as the Handbags kept
their crossbody styles.

The drawing ``card_holder`` reads the form from ``holder_style`` and the surface from ``material``,
as the bag shapes of :mod:`kit_bags` do, so a derived style draws the material it states:

==========  ==========================================================
form        drawn as
==========  ==========================================================
slim        an upright case, a card in its top pocket, two curved pockets
zip         a square case zipped round three sides, a pull and a ring
bifold      open flat: two panels, a crease, angled slots and a snap tab
==========  ==========================================================
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import bags_common as bc
from synthetic_ecommerce_data.domains.retail.accessory_rows import ARow, _a, _count, _who
from synthetic_ecommerce_data.domains.retail.audience import WOMENS
from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    _tint,
    register,
)
from synthetic_ecommerce_data.domains.retail.kit_accessories import HARDWARE, _band, _circle, _rect
from synthetic_ecommerce_data.domains.retail.kit_bags import _label, _surface
from synthetic_ecommerce_data.domains.retail.type_registry import TypeSpec

PT = "Card Holder"
PATH = ("Womens", "Accessories", "Purses & Wallets", "Card Holders")
_ZIP = ' stroke-dasharray="7 3"'


def _slots(fill: Fill, x0: int, x1: int, ys: tuple[int, ...]) -> list[str]:
    """Card pockets cut on a shallow slant across a panel."""
    return [_line(f"M{x0},{y} L{x1},{y + 8}", 2.2, "", _shade(fill.base, 0.4)) for y in ys]


def card_holder(paint: str, fill: Fill, label: str | None, holder_style: str = "slim", material: str = "leather") -> list[str]:  # fmt: skip
    """A card holder as a shop lays it out: a ``slim`` upright case with a card in it, a square
    ``zip`` case with a pull and a key ring, or a ``bifold`` case open flat with a snap tab."""
    if holder_style == "zip":
        out = [_path("M76,92 Q76,72 96,72 L304,72 Q324,72 324,92 L324,316 Q324,336 304,336 L96,336 Q76,336 76,316 Z", paint),
               *_surface(material, fill, 104, 118, 296, 310),
               _line("M88,336 L88,96 Q88,84 100,84 L300,84 Q312,84 312,96 L312,336", 2.6, _ZIP),
               _rect(298, 116, 28, 16, HARDWARE, 4, 1.6),
               *_band("M48,318 A22,22 0 1,1 92,318 A22,22 0 1,1 48,318", HARDWARE, 5)]  # fmt: skip
    elif holder_style == "bifold":
        out = [_path("M44,104 L356,104 L356,312 L44,312 Z", paint),
               *_surface(material, fill, 58, 118, 186, 298),
               _line("M200,104 L200,312", 2.6, "", _shade(fill.base, 0.45)),
               _path("M212,120 L344,120 L344,300 L212,300 Z", _tint(fill.base, 0.14)),
               *_slots(fill, 214, 342, (150, 190, 230, 270)),
               _path("M356,168 L384,168 Q392,168 392,176 L392,240 Q392,248 384,248 L356,248 Z", _shade(fill.base, 0.2)),
               _circle(376, 208, 9, HARDWARE, 1.6)]  # fmt: skip
    else:
        out = ['<rect x="128" y="58" width="144" height="92" rx="7" fill="#f4f1ea" '
               f'stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
               _line("M142,80 L226,80 M142,94 L190,94", LW_DETAIL),
               _path("M104,108 Q200,136 296,108 L296,330 Q200,344 104,330 Z", paint),
               *_surface(material, fill, 120, 210, 280, 322),
               _line("M104,176 Q200,204 296,176 M104,246 Q200,274 296,246", 2.4, "", _shade(fill.base, 0.45))]  # fmt: skip
    return _label(out, label)


register({"card_holder": card_holder})


def _row(code, title, brand, price, desc, colors, form, material, closure, slots, rfid) -> ARow:
    attrs = (_a("holder_style", "Holder style", form), _a("material", "Material", material),
             _a("closure", "Closure", closure), _count("card_slots", "Card slots", slots),
             _a("rfid_blocking", "RFID blocking", rfid))  # fmt: skip
    return ARow(code, title, brand, bc.DEPARTMENT, PATH, PT, price, "card_holder", desc, colors,
                _who(attrs, WOMENS), params=(("holder_style", form.lower()), ("material", material.lower())))  # fmt: skip


_ROWS = (
    _row("CHDSLL", "Leather Slim Card Holder", bc.CALDERBY, 18.0,
         "A slim leather card holder with four angled pockets and a middle pocket for folded notes.",
         bc.CLASSIC, "Slim", "Leather", "Open", 4, "No"),
    _row("CHDSLC", "Canvas Slim Card Holder", bc.WRENFIELD, 9.0,
         "A thin canvas card holder with three pockets, for a travel pass and two bank cards.",
         bc.SOFT, "Slim", "Canvas", "Open", 3, "No"),
    _row("CHDZPF", "Faux Leather Zip Card Holder", bc.THISTLE, 14.0,
         "A faux leather card holder that zips round three sides, with six card slots, a key ring and a shielding layer against contactless reads.",
         bc.BRIGHT, "Zip", "Faux Leather", "Zip", 6, "Yes"),
    _row("CHDBFS", "Suede Bifold Card Holder", bc.HARBOUR, 22.0,
         "A suede card holder that folds in two and closes with a snap tab, with eight card slots.",
         bc.EARTH, "Bifold", "Suede", "Snap", 8, "No"),
    _row("CHDBFL", "Leather Bifold Card Holder", bc.CALDERBY, 26.0,
         "A leather card holder that folds in two and closes with a snap tab, with eight card slots and a shielding layer against contactless reads.",
         bc.SOFT, "Bifold", "Leather", "Snap", 8, "Yes"),
)  # fmt: skip

SPEC = TypeSpec(
    key="card_holder",
    department=bc.DEPARTMENT,
    product_type=PT,
    rows=_ROWS,
    derivable=True,
    apparel_exempt=bc.APPAREL_EXEMPT,
    decoys=(
        bc.decoy(1, "red card holder", "color", _row(
            "CHDDRD", "Contrast Lining Card Holder", bc.WRENFIELD, 15.0,
            "A black faux leather card holder that zips shut over a red lining.", (bc.BLACK,), "Zip", "Faux Leather", "Zip", 6, "No")),
        bc.decoy(4, "leather card holder", "generic", _row(
            "CHDDLK", "Faux Leather Slim Card Holder", bc.THISTLE, 8.0,
            "A slim faux leather card holder with four pockets; there is no leather in it.", (bc.TAN,), "Slim", "Faux Leather", "Open", 4, "No")),
        bc.decoy(6, "green card holder", "color", _row(
            "CHDDGN", "Green Park Card Holder", bc.HARBOUR, 20.0,
            "From the Green Park range: a card holder that folds in two and closes with a snap tab.", (bc.NAVY,), "Bifold", "Leather", "Snap", 8, "No")),
    ),
)  # fmt: skip
