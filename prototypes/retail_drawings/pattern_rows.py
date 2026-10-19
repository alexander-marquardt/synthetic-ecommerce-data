"""Tartan, floral, breton stripe and patchwork as a ``pattern`` value (gen#408).

The coverage review of gen#188 asked for the patterns a shopper types before a category
("tartan skirt", "floral dress", "breton stripe top", "patchwork cushion"). The build held
leopard and polka dot but none of these four. Each style below is sold in colorways that
carry the pattern ("Red Tartan"); :func:`colorwords.split` takes the color ("Red") and the
pattern ("Tartan") apart, so the ``pattern`` facet holds the pattern and the ``color`` facet
only a color (the gen#188 guard).

No title or description names a color, so the text never states one the style does not carry.
These rows are templates only: :func:`scale.derivable` leaves them out, as it does the
color-group rows, so the seeded derivation is what it was.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from seasonal_rows import SRow
from variants import cw

_C, _H = "Clothing", "Home"
_SIZES = ("XS", "S", "M", "L", "XL")
_SKIRT = ("Womens", "Skirts", "Mini Skirts")
_DRESS = ("Womens", "Dresses", "Midi Dresses")
_BLOUSE = ("Womens", "Shirts & Blouses", "Blouses")
_TOP = ("Womens", "Tops", "Long Sleeve Tops")
_CUSHION = ("Home", "Soft Furnishings", "Cushions")

#: The drawing fields of a flower print, scattered all over the garment (as :mod:`seasonal_rows`).
_FLOWERS = (("motif", "flowers"), ("placement", "all-over"), ("scale", 0.1), ("spacing", 96),
            ("count", 2))  # fmt: skip


def _row(code: str, title: str, brand: str, dept: str, path: tuple[str, ...], ptype: str,
         shape: str, price: float, description: str, colors: tuple, material: str,
         sizes: tuple[tuple[str, float], ...], **kw: object) -> SRow:
    return SRow(code, title, brand, dept, path, ptype, price, shape, description, colors,
                (("material", "Material", material),), sizes, **kw)  # type: ignore[arg-type]


def _clothing(price: float) -> tuple[tuple[str, float], ...]:
    return tuple((s, price) for s in _SIZES)


ROWS = (
    _row("PTSKRT", "Tartan Pleated Mini Skirt", "Wrenfield", _C, _SKIRT, "Skirt", "skirt", 32.0,
         "A pleated mini skirt in brushed twill, with a buckled waist tab.",
         (cw("Red Tartan", "#a3262a", "tartan", "#1f4f3a"),
          cw("Green Tartan", "#2f6b3c", "tartan", "#1f2f5a"),
          cw("Navy Tartan", "#1f2f5a", "tartan", "#a3262a")),
         "Brushed Twill", _clothing(32.0)),
    _row("PTDRSS", "Floral Tea Dress", "Larkmoor", _C, _DRESS, "Dress", "dress", 38.0,
         "A tiered midi dress with a smocked bodice and short puff sleeves.",
         (cw("Pink Floral", "#f3c6cf", "print", "#c8312e"),
          cw("Blue Floral", "#b9d0ea", "print", "#26365c"),
          cw("Navy Floral", "#26365c", "print", "#f3c6cf")),
         "Viscose", _clothing(38.0), motif_print=_FLOWERS),
    _row("PTBLSE", "Floral Print Tie Neck Blouse", "Harbour & Pine", _C, _BLOUSE, "Blouse", "blouse", 30.0,
         "A soft blouse with a tie neck and gathered cuffs, easy under a cardigan.",
         (cw("Cream Floral", "#efe4cf", "print", "#a3262a"),
          cw("Green Floral", "#cfe0cc", "print", "#2f6b3c")),
         "Polyester", _clothing(30.0), motif_print=_FLOWERS),
    _row("PTTOPB", "Breton Stripe Long Sleeve Top", "Harbour & Pine", _C, _TOP, "Top", "top", 20.0,
         "A boat neck top in cotton jersey with long sleeves and a relaxed fit.",
         (cw("Navy Breton Stripe", "#ffffff", "stripe", "#26365c"),
          cw("Red Breton Stripe", "#ffffff", "stripe", "#c8312e"),
          cw("Black Breton Stripe", "#ffffff", "stripe", "#2a2a2e")),
         "Cotton", _clothing(20.0)),
    _row("PTCUSH", "Patchwork Cushion", "Hearth & Table", _H, _CUSHION, "Cushion", "cushion", 20.0,
         "A square cushion pieced from squares of cotton, with a feather pad. Zip opening.",
         (cw("Multi Patchwork", "#c46a4a", "print", "#26365c"),
          cw("Blue Patchwork", "#5b84b8", "print", "#f3ecd9")),
         "Cotton", (("45 x 45cm", 20.0), ("55 x 55cm", 26.0))),
)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]


def product_ids() -> frozenset[str]:
    """The product ids the module adds, for :func:`scale.derivable` to leave out."""
    return frozenset(f"BRD-{r.code}" for r in ROWS)
