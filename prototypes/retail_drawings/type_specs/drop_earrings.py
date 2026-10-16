"""Drop Earrings (gen#423): a new Womens jewellery type beside the legacy ``Earrings``.

Each style is a pair of posts with a hanging drop (pearl, teardrop or bar), in one to three
metals. ``drop`` and ``gem`` are drawn by :mod:`kit_jewellery`. The two decoys carry the word
"drop" in their text and are not a hanging drop by their fields.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from jewellery_rows import (
    ALL_METALS,
    GOLD,
    LARKMOOR,
    OWNED,
    ROSE_GOLD,
    SILVER,
    SKERRY,
    TIDEWELL,
    WRENFIELD,
    a,
    earrings_row,
)
from type_registry import Decoy, TypeSpec

LEAF, PTYPE = "Drop Earrings", "Drop Earrings"
STYLE = a("earring_style", "Earring style", "Drop")


def _row(code, title, brand, price, desc, drop, **kw):
    gem = kw.pop("gem", None)
    params = (("drop", drop), *((("gem", gem),) if gem else ()))
    return earrings_row(code, title, brand, price, desc, "drop_earrings", LEAF, PTYPE, STYLE, params, **kw)


SPEC = TypeSpec(
    key="drop_earrings",
    department="Clothing",
    product_type=PTYPE,
    owners=OWNED,
    apparel_exempt="jewellery: the color is the metal finish, not a printed or dyed color; it carries its own decoys (gen#423)",
    rows=(
        _row("DREPRL", "Freshwater Pearl Drop Earrings", WRENFIELD, 18.0,
             "Drop earrings with a single freshwater pearl hanging from a polished post.", "pearl", stone="Pearl"),
        _row("DRETRD", "Teardrop Drop Earrings", LARKMOOR, 15.0,
             "Polished teardrop earrings on a short chain, light and easy to wear.", "teardrop"),
        _row("DREBAR", "Bar Drop Earrings", SKERRY, 13.0,
             "Slim bar drop earrings that hang straight from a flat post.", "bar", colors=(GOLD, SILVER)),
        _row("DRERBY", "Ruby Teardrop Earrings", TIDEWELL, 29.0,
             "Teardrop earrings with a faceted ruby stone that hangs below a polished cap.", "teardrop",
             gem="#b3202e", stone="Ruby", colors=(GOLD, ROSE_GOLD)),
        _row("DREPAV", "Crystal Drop Earrings", SKERRY, 22.0,
             "Drop earrings with a clear crystal that hangs from a fine chain, in stainless steel for sensitive ears.", "teardrop",
             gem="#e8f1f7", stone="Crystal", steel=True, colors=ALL_METALS),
    ),
    decoys=(
        Decoy(4, "pearl drop earrings", "category",
              _row("DREDSH", "Dainty Pearl Earrings", WRENFIELD, 12.0,
                   "Delicate earrings with a pearl that hangs only a short drop from a silver post.", "pearl",
                   stone="Pearl", colors=(SILVER,))),
        Decoy(6, "drop earrings", "category",
              _row("DREDCR", "Teardrop Crystal Studs", LARKMOOR, 11.0,
                   "Small crystal earrings cut in a teardrop shape that sit flat on the lobe.", "teardrop",
                   gem="#e8f1f7", stone="Crystal", colors=(SILVER,))),
    ),
)  # fmt: skip
