"""Garden furniture set (gen#203, a spec by gen#351): bistro, dining, corner lounge and sun lounger.

**Garden > Garden Furniture** holds five styles from five invented brands, in one leaf
(bistro, dining, corner and lounger sets), drawn by :func:`kit_outdoor.garden_furniture`. The
material (rattan-effect, aluminum, wood, steel), the kind and whether cushions come with the set
are structured entries. The SKUs are a color times a seat count: ``seats`` is also a drawing
param, so each SKU's image draws its own number of seats. The six main colors are offered across
the type (gen#275). Not derivable: the department grows by authored rows. The type's text-match
decoys (gen#294) are in :mod:`garden_rows`, with the other machines'.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_outdoor  # noqa: F401 -- registers garden_furniture
from outdoor_helpers import BLACK, BLUE, GREEN, RED, WHITE, YELLOW, H, L, M, V, W, a, axis, row
from type_registry import Option, TypeSpec

_ROOT = ("Garden", "Garden Furniture")
_PT = "Garden Furniture Set"


def _attrs(kind: str, material: str, cushions: bool) -> tuple:
    return (a("furniture_kind", "Furniture kind", kind), a("material", "Material", material),
            a("cushions_included", "Cushions included", "Yes" if cushions else "No"))  # fmt: skip


SPEC = TypeSpec(
    key="garden_furniture_set",
    department="Garden",
    product_type=_PT,
    options=(Option("seats", "seats", "Seats", "C62"),),
    rows=(
        row("GFSBIS", "Steel Bistro Garden Furniture Set", W, (*_ROOT, "Garden Furniture Sets"), _PT, 79.0,
            "garden_furniture", "A round table and two folding chairs in powder-coated steel, "
            "small enough for a balcony or a patio corner.",
            (BLACK, WHITE, GREEN), _attrs("Bistro", "Steel", False), axis((2, 79.0)), "seats",
            (("kind", "bistro"), ("seats", "2"), ("cushions", "no"))),
        row("GFSCRN", "Rattan-Effect Corner Lounge Garden Furniture Set", L, (*_ROOT, "Garden Furniture Sets"), _PT,
            449.0, "garden_furniture", "A weatherproof rattan-effect corner sofa with a low "
            "table, deep seat cushions and covers for the winter.",
            (BLACK, BLUE, RED), _attrs("Corner Lounge", "Rattan-Effect", True),
            axis((4, 449.0), (5, 549.0), (6, 649.0)), "seats",
            (("kind", "corner"), ("seats", "4"), ("cushions", "yes"))),
        row("GFSDIN", "Aluminum Dining Garden Furniture Set", H, (*_ROOT, "Garden Furniture Sets"), _PT, 299.0,
            "garden_furniture", "A rust-proof aluminum table with chairs that tuck under it, "
            "with padded seat cushions, for family meals outdoors.",
            (BLACK, WHITE, BLUE), _attrs("Dining", "Aluminum", True),
            axis((4, 299.0), (6, 399.0), (8, 499.0)), "seats",
            (("kind", "dining"), ("seats", "4"), ("cushions", "yes"))),
        row("GFSWDN", "Wooden Dining Garden Furniture Set", V, (*_ROOT, "Garden Furniture Sets"), _PT, 249.0,
            "garden_furniture", "A treated hardwood table and chairs with a slatted seat, "
            "oiled for the weather and sold without cushions.",
            (GREEN, YELLOW, WHITE), _attrs("Dining", "Wood", False), axis((4, 249.0), (6, 349.0)), "seats",
            (("kind", "dining"), ("seats", "4"), ("cushions", "no"))),
        row("GFSLNG", "Wooden Sun Lounger Garden Furniture Set", M, (*_ROOT, "Garden Furniture Sets"), _PT, 129.0,
            "garden_furniture", "A reclining sun lounger in treated wood with a padded cushion, "
            "sold singly or as a pair.",
            (YELLOW, WHITE, RED, GREEN), _attrs("Sun Lounger", "Wood", True), axis((1, 129.0), (2, 229.0)),
            "seats", (("kind", "lounger"), ("seats", "1"), ("cushions", "yes"))),
    ),
)  # fmt: skip
