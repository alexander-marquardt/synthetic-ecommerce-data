"""Decoys that hold the phrase "face cream" for the query ``face cream`` (gen#874).

With interpretation off, the served search multiplies a product's text score by 3 for each typed
word its title holds, and by 2.5 more when the title holds the typed phrase itself (prism#14050).
Every real face cream says "Face Cream". The decoys of gen#541 and gen#294 say "Cream Face Towel"
or "Cream Baby Face Fabric Sofa": both words, never the phrase. They trailed the 23 real creams at
about 40% of their score, so the top 24 showed one decoy and the demo had no "before" picture.

Each row here is a short title that holds the phrase and names a product a shopper really meets:

* **Baby Face Cream**: a sofa range sells its fabric and colour as one name, so "Baby Face" (the
  upholstery fabric of gen#541) in Cream is "Baby Face Cream". A sofa and a matching cushion.
* **Empty containers**: travel jars and sample pots that a face cream is decanted into, sold
  empty in Beauty > Travel & Minis.

Their structured fields tell the truth: each is a Sofa, a Cushion or a Travel Set outside the Face
Creams node, so the Face Creams route of class 12 leaves them below every real face cream when
interpretation is on. ``tests/test_face_cream_decoys_874.py`` holds the ranking.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

_Q = "face cream"
_BABY = (("material", "Material", "Baby Face Fabric"),)
_TRAVEL = ("Beauty", "Travel & Minis", "Travel Sets")

#: The true types: a sofa and a cushion the catalogue already sells, and the Travel Set type.
KINDS = {
    "fc874_sofa": Kind("Home", ("Home", "Furniture", "Sofas"), "Sofa", "sofa_seats", "Brackenmere Home", 599.0,
                       params=(("seats", "2"), ("arms", "rolled"), ("legs", "walnut")), extra=_BABY),
    "fc874_cushion": Kind("Home", ("Home", "Soft Furnishings", "Cushions"), "Cushion", "cushion", "Hearth & Table", 24.0,
                          extra=(("fabric", "Fabric", "Baby Face Fabric"),)),
    "fc874_jars": Kind("Beauty", _TRAVEL, "Travel Set", "moisturiser_jar", "Velling Apothecary", 6.0, colorless=True),
}  # fmt: skip

#: Rows of (code, kind, title, description, color, class, sold).
_ROWS = (
    ("XC14", "fc874_sofa", "Baby Face Cream Sofa", "A two seater sofa in Baby Face Cream, a soft, velvety fabric that resists pet hair and stains.", "Cream", 4, 940),
    ("XC15", "fc874_cushion", "Baby Face Cream Cushion", "A square scatter cushion in Baby Face Cream fabric, made to match the sofa.", "Cream", 4, 900),
    ("XC16", "fc874_jars", "Face Cream Travel Jars", "Three empty 30 ml jars with screw lids, to decant a face cream for a trip.", "Clear", 2, 920),
    ("XC17", "fc874_jars", "Face Cream Sample Pots", "Ten empty 5 ml pots with lids, to share a face cream or take a sample of one.", "Clear", 2, 860),
)  # fmt: skip


def decoy_rows(d):
    return tuple(
        d(code, kind, title, desc, color, cls, _Q, sold)
        for code, kind, title, desc, color, cls, sold in _ROWS
    )
