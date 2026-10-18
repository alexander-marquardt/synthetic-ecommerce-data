"""Tracksuits (gen#206, moved to a spec by gen#351): a matching set, sold as the set or as
either piece. :mod:`kit_lowerbody` draws them; the styles are templates only (``derivable``
False), so the seeded derivation is what it was.
"""

from __future__ import annotations

from class_model import KIDS_WAISTS
from lowerbody_rows import BLACK, BURGUNDY, GREEN, GREY_MARL, LILAC, NAVY, PINK, RED
from type_registry import BRAND_OWNER, LRow, Option, TypeSpec, a, count, sizes

#: The brands these rows sell, owned as the rest of the clothing tree states.
BRANDS = ("Stridewell", "Hollinwray Knits", "Harbour & Pine", "Wrenfield", "Larkmoor")
SW, HK = "Stridewell", "Hollinwray Knits"
ADULT = ("XS", "S", "M", "L", "XL")
#: How a tracksuit is sold: ``(value, price factor)`` on the ``sold_as`` SKU axis.
_SOLD = (("Set", 1.0), ("Jacket Only", 0.58), ("Bottoms Only", 0.5))


def _set(top: str, fit: str, fabric: str, pieces: int) -> tuple:
    return (a("top_style", "Top style", top), a("leg_fit", "Leg fit", fit),
            a("fabric", "Fabric", fabric), count("piece_count", "Piece count", pieces),
            a("waist_type", "Waist type", "Drawstring"))  # fmt: skip


def _drawn(top: str, pieces: int, fit: str) -> tuple[tuple[str, str], ...]:
    """The drawing's params: the marks the record states."""
    return (("top", top), ("pieces", str(pieces)), ("fit", fit))


def _row(code, title, brand, path, price, desc, colors, attrs, params, size_list=None) -> LRow:
    return LRow(code, title, brand, "Clothing", path, "Tracksuit", price, "tracksuit", desc,
                colors, attrs, size_list or sizes(price, ADULT), params=params,
                axis_key="sold_as", axis=_SOLD, facts=(("pattern", "plain"),))  # fmt: skip


_WT, _MT = ("Womens", "Tracksuits"), ("Mens", "Tracksuits")
_BT, _GT = ("Kids", "Boys", "Tracksuits"), ("Kids", "Girls", "Tracksuits")

SPEC = TypeSpec(
    options=(
        Option("sold_as", "sold_as", "Sold as"),
    ),
    key="tracksuit",
    department="Clothing",
    product_type="Tracksuit",
    owners=tuple((b, BRAND_OWNER[b]) for b in BRANDS),
    rows=(
        _row("TSTMFL", "Hooded Fleece Tracksuit", SW, _MT, 48.0,
              "A two-piece fleece set: a hooded zip jacket and cuffed joggers.",
              (GREY_MARL, NAVY, BLACK), _set("Hooded", "Regular", "Fleece", 2),
              _drawn("hooded", 2, "regular")),
        _row("TSTMSH", "Shell Suit Tracksuit with Zip Jacket", SW, _MT, 55.0,
              "A lightweight shell tracksuit with a full zip jacket and elasticated bottoms.",
              (NAVY, BLACK, RED), _set("Zip", "Relaxed", "Shell", 2), _drawn("zip", 2, "relaxed")),
        _row("TSTMHZ", "Half-Zip Cotton Tracksuit", "Harbour & Pine", _MT, 52.0,
              "A cotton jersey set with a half-zip sweat top and slim joggers.",
              (GREY_MARL, BLACK), _set("Half-Zip", "Slim", "Cotton", 2),
              _drawn("half_zip", 2, "slim")),
        _row("TSTWFL", "Women's Hooded Fleece Tracksuit", HK, _WT, 46.0,
              "A soft two-piece fleece set: a hooded zip jacket and relaxed joggers.",
              (GREY_MARL, PINK, BLACK), _set("Hooded", "Relaxed", "Fleece", 2),
              _drawn("hooded", 2, "relaxed")),
        _row("TSTWVL", "Velour Tracksuit with Zip Jacket", "Wrenfield", _WT, 58.0,
              "A velour set in a soft pile, with a zip jacket and slim joggers.",
              (BURGUNDY, BLACK, NAVY),
              _set("Zip", "Slim", "Velour", 2), _drawn("zip", 2, "slim")),
        _row("TSTW3P", "3 Piece Half-Zip Tracksuit Set with Tee", "Larkmoor", _WT, 62.0,
              "Three matching pieces: a half-zip top, joggers and a fitted tee.",
              (GREY_MARL, LILAC), _set("Half-Zip", "Regular", "Fleece", 3),
              _drawn("half_zip", 3, "regular")),
        _row("TSTBHD", "Boys Hooded Fleece Tracksuit", "Harbour & Pine", _BT, 30.0,
              "A hooded zip jacket and joggers in warm fleece, for school mornings and weekends.",
              (NAVY, GREY_MARL, GREEN), _set("Hooded", "Regular", "Fleece", 2),
              _drawn("hooded", 2, "regular"), tuple((n, 30.0) for n in KIDS_WAISTS)),
        _row("TSTG3P", "Girls 3 Piece Velour Tracksuit Set", "Wrenfield", _GT, 34.0,
              "A zip velour jacket, joggers and a matching tee.",
              (PINK, LILAC), _set("Zip", "Regular", "Velour", 3), _drawn("zip", 3, "regular"),
              tuple((n, 34.0) for n in KIDS_WAISTS)),
    ),
)  # fmt: skip
