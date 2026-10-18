"""Sun Cream (gen#214): the area (face or body) is an attribute and a leaf, the SPF and the size in
ml are the SKUs.

See :mod:`beauty_depth` for the ten types, the colors and the decoy classes; :mod:`kit_beauty`
draws them. The one-style sun cream of ``class_rows`` (``PLT-SPFFCE``) stays beside this range: it
is the near-type distractor of the "face cream" demo (class 12), whose committed Elasticsearch proof
names its id (``tests/test_retail_type_specs_351.py``, ``PROOF_PINNED_CLASS_ROWS``).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from functools import partial

from beauty_depth import PACK_ROSE, PACK_SAND, PACK_SKY, decoy, row
from type_registry import Decoy, Option, TypeSpec, a

_SPF = ("15", "30", "50")
_FACE = partial(row, path=("Beauty", "Suncare", "Face Sun Cream"), ptype="Sun Cream", option=("spf", _SPF))
_BODY = partial(row, path=("Beauty", "Suncare", "Body Sun Cream"), ptype="Sun Cream", option=("spf", _SPF))

ROWS = (
    _FACE("SNCFMN", "Sheer Mineral Face Sun Cream", "Thornlea Skin", 12.0, "sun_cream",
        "A light mineral face sun cream that leaves no white cast and is kind to sensitive skin.",
        (a("area", "Area", "Face"),),
        (("30", 8.0), ("50", 12.0), ("100", 19.0)), "net_volume_ml", (("form", "tube"),), (PACK_SAND,)),
    _BODY("SNCBSP", "Sport Body Sun Cream Spray", "Aldermist", 11.0, "sun_cream",
        "A quick drying body sun cream in a spray that is water resistant for 80 minutes.",
        (a("area", "Area", "Body"),),
        (("150", 11.0), ("200", 14.0), ("300", 19.0)), "net_volume_ml", (("form", "spray"),), (PACK_SKY,)),
    _BODY("SNCBHY", "Hydrating Body Sun Cream", "Sorrel & Salt", 9.0, "sun_cream",
        "A smooth, moisturizing body sun cream in a pump bottle, for the whole family.",
        (a("area", "Area", "Body"),),
        (("100", 6.0), ("200", 9.0), ("400", 15.0)), "net_volume_ml", (("form", "pump"),), (PACK_ROSE,)),
)  # fmt: skip

SPEC = TypeSpec(
    key="sun_cream",
    department="Beauty",
    product_type="Sun Cream",
    options=(Option("spf", "spf", "SPF"),),
    rows=ROWS,
    decoys=(
        Decoy(4, "coconut sun cream", "vocabulary", decoy("SND1", "Fragrance Free Mineral Face Sun Cream", "A mineral face sun cream with no perfume, free from coconut and nut oils.", ROWS[0])),
        Decoy(6, "coconut sun cream", "generic", decoy("SND2", "Coconut Bay Face Sun Cream", "From the Coconut Bay range: a mineral face sun cream.", ROWS[0])),
        Decoy(7, "coconut sun cream", "generic", decoy("SND3", "Mineral Face Sun Cream", "A light mineral face sun cream.", ROWS[0], brand="Coconut Plover")),
    ),
    owners=(("Aldermist", "third_party"), ("Coconut Plover", "third_party"), ("Sorrel & Salt", "third_party"), ("Thornlea Skin", "third_party"),),
)  # fmt: skip
