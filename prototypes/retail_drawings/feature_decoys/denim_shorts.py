"""Text-match decoys of "denim shorts" (gen#603, the rule of #294).

A shopper who types ``denim shorts`` and gets the real denim shorts first has not been tested: the
words and the products agree. These rows make them disagree, in three ways. Each keeps its
structured fields true (category, product type, drawing, the ``fabric`` attribute), so only the
text misleads and only an interpreting search can tell them from the real thing.

(a) Shorts that are not denim. "denim" is their colour or their look, and the fabric is the
    truth: Linen, Jersey, Cotton.
(b) Shorts sold with a denim item, or worn with one: a denim belt bag, a denim jacket.
(c) Denim items that are not shorts but say "shorts": a jacket to wear with shorts, and a hanger
    for them (Home > Storage).

The real denim shorts (``lowerbody_rows.SHORTS``) carry a longer title that names the cut, the
rise or the length, and the decoy titles are about as long, so the title-length normalisation of
a search cannot tell them apart. ``tests/test_retail_denim_shorts_decoys_603.py`` pins all of it.
"""

from __future__ import annotations

from decoy_kind import Kind

_SIZES = ("XS", "S", "M", "L", "XL")


def _shorts(style: str, length: str, fabric: str, waist: str) -> tuple[tuple[str, str, str], ...]:
    """The true attributes of a pair of shorts, in the form the real shorts carry them."""
    return (
        ("shorts_style", "Style", style),
        ("garment_length", "Length", length),
        ("fabric", "Fabric", fabric),
        ("waist_type", "Waist type", waist),
        ("pockets", "Pockets", "Yes"),
    )


_WS = ("Womens", "Shorts")

#: The true type of each row: three fabrics of shorts, a denim jacket, and a hanger.
KINDS = {
    "dn_linen": Kind("Clothing", _WS, "Shorts", "shorts", "Wrenfield", 21.0, sizes=_SIZES,
                     params=(("length", "mid"), ("style", "chino"), ("pocket", "yes")),
                     extra=_shorts("Chino", "Mid Length", "Linen", "Drawstring")),
    "dn_jersey": Kind("Clothing", _WS, "Shorts", "shorts", "Larkmoor", 14.0, sizes=_SIZES,
                      params=(("length", "mini"), ("style", "sweat"), ("pocket", "yes")),
                      extra=_shorts("Sweat", "Mini", "Jersey", "Elastic")),
    "dn_cotton": Kind("Clothing", _WS, "Shorts", "shorts", "Harbour & Pine", 24.0, sizes=_SIZES,
                      params=(("length", "knee"), ("style", "bermuda"), ("pocket", "yes")),
                      extra=_shorts("Bermuda", "Knee Length", "Cotton", "Belted")),
    "dn_sweat": Kind("Clothing", _WS, "Shorts", "shorts", "Wrenfield", 16.0, sizes=_SIZES,
                     params=(("length", "mid"), ("style", "sweat"), ("pocket", "yes")),
                     extra=_shorts("Sweat", "Mid Length", "Cotton Jersey", "Elastic")),
    "dn_jacket": Kind("Clothing", ("Womens", "Coats & Jackets", "Denim Jackets"), "Denim Jacket",
                      "coat", "Harbour & Pine", 42.0, sizes=_SIZES),
    "dn_hanger": Kind("Home", ("Home", "Storage", "Hangers"), "Hanger", "hanger",
                      "Brackenmere Home", 6.0, extra=(("pack_size", "Pack size", "3 pack"),)),
}  # fmt: skip

#: Rows of (code, kind, title, description, color, class, sold).
_ROWS = (
    # (a) not denim: the colour or the look is denim, the fabric is not.
    ("DS01", "dn_linen", "Denim Blue Linen Shorts with Drawstring Waist",
     "Light linen shorts in a denim blue, with an elastic back and a drawstring.", "Blue", 4, 700),
    ("DS02", "dn_jersey", "Denim-Look Jersey Shorts with Elastic Waist",
     "Soft jersey shorts printed to look like denim; they hold no denim.", "Blue", 4, 680),
    ("DS03", "dn_cotton", "Chambray Cotton Shorts, Denim Wash, Knee Length",
     "Knee length cotton chambray shorts in a denim wash, with belt loops.", "Blue", 4, 640),
    ("DS04", "dn_cotton", "Denim Blue Cotton Bermuda Shorts, Belted Waist",
     "Cotton bermuda shorts in a denim blue, sold with a woven belt.", "Blue", 4, 600),
    # (b) shorts sold with, or worn with, a denim item.
    ("DS05", "dn_jersey", "Jersey Shorts with Denim Belt Bag",
     "Mini jersey shorts sold with a small denim belt bag to wear at the hip.", "Grey", 2, 660),
    ("DS06", "dn_sweat", "Sweat Shorts, Wear with a Denim Jacket",
     "Mid length jersey sweat shorts, easy to wear with a denim jacket.", "Navy", 2, 620),
    # (c) denim items that are not shorts but say shorts.
    ("DS07", "dn_jacket", "Denim Jacket to Wear with Shorts",
     "A cropped denim jacket that sits well over a pair of shorts.", "Blue", 2, 760),
    ("DS08", "dn_hanger", "Denim Shorts Hanger, Set of 3",
     "Three clip hangers that hold a pair of denim shorts by the waistband.", "Blue", 2, 560),
)  # fmt: skip


def decoy_rows(d):
    return tuple(
        d(code, kind, title, desc, color, cls, "denim shorts", sold)
        for code, kind, title, desc, color, cls, sold in _ROWS
    )
