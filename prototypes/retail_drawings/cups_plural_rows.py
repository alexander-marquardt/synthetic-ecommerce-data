"""Lingerie that names its cups in the plural (gen#508): data only.

One word, a sense in two departments (:mod:`class_rows`, class 15): in Home a cup is drinkware,
in Lingerie it is the cup of a bra. A real retail site answers a bare ``cups`` with bras, because
bralettes, sports bras and T-shirt bras are titled "... with Removable Cups" or "... with Moulded
Cups" and sell hard, while drinkware is titled "Mug" or "Tumbler" more often than "Cup". The
catalogue's bras said "Cup" in the singular only ("Full Cup Bra"), so they met ``cups`` through
the stemmed sub-field at a third of the title weight and never reached page one.

Thirteen bras are here, each a short title that ends in the plural, with sales above the drinkware
they compete with. Eight swimsuits and bikini tops are in :mod:`swimwear_rows`, in their own type
specs, with "Padded Cups" in the title. Every title is true to the product:

- "Removable Cups" is the bra's ``padding`` value ``Removable Cups``, read from the title by
  :func:`facet_leaves.stated_bra_facets`; "Moulded Cups" and "Padded Cups" are the ``Moulded``
  and ``Padded`` values it already read;
- a swimsuit or bikini top titled "Padded Cups" states ``padded`` Yes and is drawn with cups.

No title or description here names a mug, a saucer or an espresso cup, so the sibling queries
(``mugs``, ``espresso cups``) still lead with drinkware. The rows are templates only:
:func:`scale.derivable` leaves them out (``scale.CUPS_PLURAL_IDS``).
"""

# ruff: noqa: E501 -- one style's row reads better whole than wrapped (data only).

from __future__ import annotations

from class_model import Style
from variants import cw

LINGERIE = "Lingerie & Nightwear"
BRAS = ("Womens", "Lingerie", "Bras")
LETTERS = ("XS", "S", "M", "L", "XL")
BLACK, WHITE = cw("Black", "#2a2a2e"), cw("White", "#ffffff")
NUDE, IVORY = cw("Champagne", "#e8d3b0"), cw("Ecru", "#efe8d8")


def bra_sizes(cups: str) -> tuple[str, ...]:
    """Band x cup, 32 to 38 in every cup letter of ``cups``."""
    return tuple(f"{band}{cup}" for band in (32, 34, 36, 38) for cup in cups)


def _bra(code, title, brand, leaf, price, desc, colors, sizes, wiring=None):
    """A bra style at the ``leaf`` of Bras; a title that states its wiring states it as an attribute."""
    extra = (("wiring", "Wiring", wiring),) if wiring else ()
    return Style(
        f"CP{code}", title, brand, LINGERIE, (*BRAS, leaf), price, desc, "Bra", "bra", colors,
        pattern="plain", sizes=sizes, extra=extra,
    )  # fmt: skip


_TW, _BM, _SM, _WF = "Thistle & Wren", "Bramblewood", "Saltmarsh", "Wrenfield"
_B = "Bralette Bras"
_S = "Sports Bras"
_T = "T-Shirt Bras"
_CARAMEL, _PINK, _SAGE, _NAVY = cw("Caramel", "#b07a45"), cw("Pink", "#f3c6cf"), cw("Sage", "#9bb08f"), cw("Navy", "#26365c")

STYLES: tuple[Style, ...] = (
    # -- bralettes: soft, non-wired, in letter sizes
    _bra("BRA1", "Lace Bralette with Removable Cups", _TW, _B, 16.0,
         "A non-wired lace bralette with soft removable cups and adjustable straps.",
         ((BLACK, 860), (IVORY, 640), (_PINK, 410)), LETTERS),
    _bra("BRA2", "Seamless Bralette with Removable Cups", _BM, _B, 14.0,
         "A seamless pull-on bralette with removable cups and a soft stretch band.",
         ((NUDE, 820), (BLACK, 700)), LETTERS),
    _bra("BRA3", "Cotton Bralette with Padded Cups", _SM, _B, 15.0,
         "A cotton jersey bralette with lightly padded cups and a wide elastic band.",
         ((WHITE, 780), (BLACK, 650), (_SAGE, 330)), LETTERS),
    _bra("BRA4", "Ribbed Bralette with Removable Cups", _TW, _B, 13.0,
         "A ribbed stretch bralette with removable cups and a racer cut at the back.",
         ((BLACK, 760), (_CARAMEL, 520)), LETTERS),
    _bra("BRA5", "Satin Bralette with Removable Cups", _BM, _B, 17.0,
         "A satin bralette with removable cups and thin adjustable straps.",
         ((IVORY, 740), (BLACK, 610), (_NAVY, 380)), LETTERS),
    # -- sports bras: the purpose node stays under Bras
    _bra("SPB1", "Racerback Sports Bra with Removable Cups", _SM, _S, 24.0,
         "A medium support sports bra with removable cups, a racerback and a wide underband.",
         ((BLACK, 900), (cw("Blue", "#2f6db5"), 560)), LETTERS),
    _bra("SPB2", "High Impact Sports Bra with Removable Cups", _WF, _S, 28.0,
         "A high impact sports bra with removable cups, adjustable straps and a hook and eye back.",
         ((BLACK, 840), (cw("Red", "#c8322b"), 520)), LETTERS),
    _bra("SPB3", "Zip Front Sports Bra with Padded Cups", _SM, _S, 26.0,
         "A zip front sports bra with padded cups and a wide supportive band.",
         ((_NAVY, 720), (BLACK, 690)), LETTERS),
    _bra("SPB4", "Seamless Sports Bra with Removable Cups", _WF, _S, 22.0,
         "A seamless sports bra with removable cups, made for yoga and low impact training.",
         ((_PINK, 700), (BLACK, 680), (WHITE, 430)), LETTERS),
    # -- T-shirt bras: moulded or removable cups under a smooth top
    _bra("TSB1", "T-Shirt Bra with Moulded Cups", _TW, _T, 18.0,
         "A smooth t-shirt bra with moulded cups and adjustable straps.",
         ((NUDE, 880), (BLACK, 830)), bra_sizes("ABCDE")),
    _bra("TSB2", "Underwired T-Shirt Bra with Moulded Cups", _BM, _T, 22.0,
         "An underwired t-shirt bra with seamless moulded cups for a smooth line under knitwear.",
         ((BLACK, 850), (WHITE, 610), (NUDE, 600)), bra_sizes("BCDEF"), "Underwired"),
    _bra("TSB3", "Seamless T-Shirt Bra with Moulded Cups", _SM, _T, 20.0,
         "A seamless t-shirt bra with moulded cups and a smooth, bonded edge.",
         ((NUDE, 800), (_CARAMEL, 470)), bra_sizes("ABCDE")),
    _bra("TSB4", "Non-Wired T-Shirt Bra with Removable Cups", _TW, _T, 19.0,
         "A non-wired t-shirt bra with removable cups, a soft band and adjustable straps.",
         ((BLACK, 790), (NUDE, 720)), bra_sizes("BCDE"), "Non-Wired"),
)  # fmt: skip


def docs() -> list[dict]:
    """Every style's catalog document."""
    return [s.doc() for s in STYLES]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"PLT-{s.code}" for s in STYLES)
