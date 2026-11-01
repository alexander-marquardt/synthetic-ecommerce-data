"""Wallets (gen#422, a spec by gen#351): bifold, trifold, card holders and coin purses, six colors.

Men's small leather goods had no home, so ``rfid wallet`` found a phone case or a gift set. This is
**Mens > Accessories > Wallets** (gen#248: there is no top-level Accessories root; the purses, which
hold a few card holders of their own, stay under ``Womens > Accessories > Purses & Wallets``). The
kind is the drawing's shape (``kind``), equal to the row's structured ``wallet_style`` entry; the
RFID blocking and the material are two more entries. The SKU axis is the six main colors (gen#275).
Not derivable: the department grows by authored rows. Every name here is invented.

The shape is ``wallet_fold``, not the gift set's ``wallet`` or the purse's ``purse``: each is
another product's drawing, and a kind here must show as a fold, a slim case or a clasped pouch.

The decoys are same-type wallets whose text claims what their structured entries deny (gen#294): a
plain wallet that names RFID blocking (class 4), a blue lining in the description of a black wallet
(class 5), a color word or another category's noun in a range name (two of class 6: "Yellow Ridge
Wallet" is black) and another brand's name in the description (class 7).
"""

# ruff: noqa: E501 -- data rows and SVG path literals read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit import (
    INK,
    LW,
    LW_DETAIL,
    Fill,
    _line,
    _path,
    _shade,
    register,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

GOLD = "#d6b56a"
_PATH = ("Mens", "Accessories", "Wallets")
_W, _P = "Wrenfield", "Pellbrook"


def _stitch(x0: int, y0: int, x1: int, y1: int, paint: str) -> str:
    d = f"M{x0},{y0} L{x1},{y0} L{x1},{y1} L{x0},{y1} Z"
    return _line(d, 1.3, ' stroke-dasharray="4 3"', _shade(paint, 0.45))


def _slots(paint: str, x0: int, x1: int, ys: tuple[int, ...]) -> list[str]:
    """The card pockets of an open panel, each cut on a shallow slant."""
    return [_line(f"M{x0},{y} L{x1},{y + 6}", LW_DETAIL, "", _shade(paint, 0.5)) for y in ys]


def _bifold(paint: str) -> list[str]:
    """Open flat: two panels, one crease, card pockets on the right and a note slot on the left."""
    out = [_path("M72,128 L328,128 L328,280 L72,280 Z", paint, LW)]
    out += [_line("M200,128 L200,280", 2.4, "", _shade(paint, 0.5))]
    out += [_stitch(82, 138, 190, 270, paint), _stitch(210, 138, 318, 270, paint)]
    out += _slots(paint, 214, 314, (172, 204, 236))
    out += [_line("M88,170 L184,170", LW_DETAIL, "", _shade(paint, 0.5))]
    return out


def _trifold(paint: str) -> list[str]:
    """Open flat: three panels, two creases, the outer panel shorter so it folds in over the rest."""
    out = [_path("M48,136 L256,136 L352,146 L352,262 L256,272 L48,272 Z", paint, LW)]
    out += [_line(f"M{x},136 L{x},272", 2.4, "", _shade(paint, 0.5)) for x in (152, 256)]
    out += _slots(paint, 58, 144, (168, 198, 228)) + _slots(paint, 162, 248, (168, 198, 228))
    out += [_line("M272,172 L338,176 M272,206 L338,206", LW_DETAIL, "", _shade(paint, 0.5))]
    return out


def _card_holder(paint: str) -> list[str]:
    """Upright and slim, with a card in the top pocket and two pockets cut on a curve."""
    out = [
        '<rect x="134" y="82" width="132" height="84" rx="6" fill="#f4f1ea" '
        f'stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        _line("M146,102 L222,102 M146,114 L190,114", LW_DETAIL),
    ]
    out += [_path("M116,126 Q200,152 284,126 L284,322 Q200,334 116,322 Z", paint, LW)]
    out += [
        _line("M116,190 Q200,216 284,190 M116,250 Q200,276 284,250", 2.2, "", _shade(paint, 0.5))
    ]
    out += [
        _line(
            "M126,142 L126,312 M274,142 L274,312",
            1.3,
            ' stroke-dasharray="4 3"',
            _shade(paint, 0.45),
        )
    ]
    return out


def _coin_purse(paint: str) -> list[str]:
    """A rounded pouch under a metal frame, closed by two kissing balls."""
    out = [_path("M116,176 Q70,300 200,312 Q330,300 284,176 Z", paint, LW)]
    out += [
        _path("M112,178 Q200,132 288,178 L284,194 Q200,152 116,194 Z", GOLD, LW_DETAIL),
        f'<circle cx="191" cy="142" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
        f'<circle cx="209" cy="142" r="9" fill="{GOLD}" stroke="{INK}" stroke-width="{LW_DETAIL}"/>',
    ]
    out += [_line("M126,214 Q200,180 274,214", 1.3, ' stroke-dasharray="4 3"', _shade(paint, 0.45))]
    return out


_KINDS = {
    "bifold": _bifold,
    "trifold": _trifold,
    "card holder": _card_holder,
    "coin purse": _coin_purse,
}


def wallet_fold(paint: str, fill: Fill, label: str | None, kind: str = "Bifold") -> list[str]:
    """A wallet as a shop lays it out: ``kind`` is a bifold or a trifold (open flat, its panels and
    pockets showing), a card holder (a slim upright case with a card in it) or a coin purse (a
    rounded pouch under a clasped frame)."""
    return _KINDS.get(kind.lower(), _bifold)(paint)


register({"wallet_fold": wallet_fold})

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
_SIX = (BLACK, RED, BLUE, GREEN, YELLOW, WHITE)


def _attrs(kind: str, material: str, rfid: str) -> tuple[tuple[str, str, str], ...]:
    return (
        a("wallet_style", "Wallet style", kind), a("material", "Material", material),
        a("rfid_blocking", "RFID blocking", rfid), a("audience", "Audience", "Mens"),
    )  # fmt: skip


def _row(code, title, brand, price, kind, material, rfid, desc, colors=_SIX) -> Row:
    return Row(code, title, brand, "Clothing", _PATH, "Wallet", price, "wallet_fold", desc, colors,
               _attrs(kind, material, rfid), params=(("kind", kind),))  # fmt: skip


SPEC = TypeSpec(
    key="wallet",
    department="Clothing",
    product_type="Wallet",
    owners=((_W, "own"), (_P, "third_party")),
    apparel_exempt="an accessory, not a garment: its decoys are authored here (gen#294)",
    rows=(
        _row("WLTBFD", "Leather Bifold Wallet", _W, 24.0, "Bifold", "Leather", "No",
             "A smooth leather wallet with six card slots and a full note pocket, slim enough for a back pocket."),
        _row("WLTRFD", "RFID Bifold Wallet", _P, 28.0, "Bifold", "Leather", "Yes",
             "A leather wallet lined with a shielding layer that keeps contactless cards from being read."),
        _row("WLTTFD", "Canvas Trifold Wallet", _P, 14.0, "Trifold", "Canvas", "No",
             "A hard wearing canvas wallet that folds in three, with a note pocket and room for eight cards."),
        _row("WLTTRF", "RFID Trifold Wallet", _W, 19.0, "Trifold", "Faux Leather", "Yes",
             "A stitched faux leather wallet that folds in three, with a shielding layer behind every pocket."),
        _row("WLTCRD", "Slim Card Holder", _P, 13.0, "Card Holder", "Leather", "Yes",
             "A slim leather card holder with four angled pockets, a shielding layer and room for folded notes."),
        _row("WLTCFX", "Card Holder", _W, 9.0, "Card Holder", "Faux Leather", "No",
             "A thin faux leather card holder with two curved pockets, for a travel pass and a bank card."),
        _row("WLTCOI", "Kiss Clasp Coin Purse", _P, 12.0, "Coin Purse", "Leather", "No",
             "A rounded leather pouch for coins under a gold metal frame that snaps shut with a kiss clasp."),
    ),
    decoys=(
        Decoy(4, "rfid wallet", "feature facet: an rfid query keeps the wallets that block it",
              _row("DCWLT1", "Fashion Fold Wallet", _W, 10.0, "Bifold", "Faux Leather", "No",
                   "A faux leather wallet in a style like our RFID wallets, with no shielding layer behind its pockets.",
                   (BLACK,))),
        Decoy(5, "blue wallet", "color facet: blue means the wallet color, not a word in the text",
              _row("DCWLT2", "Lined Bifold Wallet", _P, 18.0, "Bifold", "Leather", "No",
                   "A black leather wallet with a blue lining that shows when it opens.",
                   (BLACK,))),
        Decoy(6, "yellow wallet", "color facet: a color word in a range name is not the wallet color",
              _row("DCWLT4", "Yellow Ridge Wallet", _P, 15.0, "Bifold", "Leather", "No",
                   "A black leather bifold from the Ridge range, with six card slots.",
                   (BLACK,))),
        Decoy(6, "boot wallet", "type facet: another category's noun in a range name does not make the wallet that category",
              _row("DCWLT5", "Boot Hill Wallet", _W, 13.0, "Trifold", "Canvas", "No",
                   "A black canvas trifold from the Hill range, with room for eight cards.",
                   (BLACK,))),
        Decoy(7, "pellbrook wallet", "brand facet: a brand named in the text is not the product's brand",
              _row("DCWLT3", "Everyday Canvas Wallet", _W, 8.0, "Bifold", "Canvas", "No",
                   "A budget alternative to Pellbrook canvas wallets, in a plain black weave.",
                   (BLACK,))),
    ),
)  # fmt: skip
