"""Cream furniture and home decoys for the query "face cream" (gen#541).

The failure, seen on public retail sites: a search for ``face cream`` returns cream-colored
sofas, because the color word is matched alone and "face" is dropped or stemmed away. Three
families of rows, all color Cream, class 4 (a color word that is also a product), all for the
one query ``face cream``:

* **Baby Face** furniture ("Cream Baby Face Fabric Sofa" and its siblings). Baby Face is a real
  upholstery fabric (soft, velvety, resists pet hair and stains), so the title holds both words of
  the query and a text-only match puts it at the top. The category (Home > Furniture) and the
  product type read from the query ("Face Cream") keep it out of Best: the category policy for
  face cream drops it.
* **Facing** corner sofas ("Textured Chenille Right-Hand Facing Corner Sofa, Cream", the left-hand
  one, and their 2 Seater, Snuggle Chair and Footstool siblings). "Right-Hand Facing" is real
  furniture naming, and a stemming engine reads "Facing" as "face". Our title tokeniser is not a
  stemmer, so these match ``face cream`` on "cream" alone and stay below the top 10: the baseline
  is already better than a stemming engine, which is why they are kept. They answer the query
  ``face cream``, and there is no policy for them: nothing in the baseline ranking needs fixing,
  and a policy would hide that the baseline starts from a higher bar. The test in
  ``tests/test_face_cream_cream_sofa_541.py`` holds that they do not reach the top 10.
* **Cream only** pieces: no "face" in the title (a boucle sofa, a linen armchair, a chunky knit
  throw). The sofa and the armchair say "Face fabric" (the spec term for the outer fabric) in the
  description, so they match both words only where the description is searched.

A row is a real product of a type the catalogue already has (a sofa, an armchair, a footstool, a
cushion, a throw), drawn as that product. No brand is a real one.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from decoy_kind import Kind

_Q = "face cream"
_FURN = ("Home", "Furniture")
_SOFAS = (*_FURN, "Sofas")
_CORNER = (*_SOFAS, "Corner Sofas")
_CHAIRS = (*_FURN, "Armchairs")
_STOOLS = (*_FURN, "Footstools")
_B = "Brackenmere Home"
_C = "Hearth & Table"
_BABY = (("material", "Material", "Baby Face Fabric"),)
_CHEN = (("material", "Material", "Chenille"),)
_BOUCLE = (("material", "Material", "Boucle"),)
_LINEN = (("material", "Material", "Linen"),)
_SOFA3 = (("seats", "3"), ("arms", "rolled"), ("legs", "walnut"))
_SOFA2 = (("seats", "2"), ("arms", "rolled"), ("legs", "walnut"))
_ROUND = (("style", "accent"), ("legs", "oak"))
_TUB = (("style", "tub"), ("legs", "oak"))
_STOOL = (("form", "rectangular"), ("storage", "no"), ("legs", "oak"))


def _corner(side: str, extra: tuple, price: float) -> Kind:
    params = (("seats", "5"), ("side", side), ("arms", "track"), ("legs", "black_metal"))
    return Kind("Home", _CORNER, "Corner Sofa", "corner_sofa", _B, price, params=params, extra=extra)


def _seat(path, product_type, shape, brand, price, params, extra) -> Kind:
    return Kind("Home", path, product_type, shape, brand, price, params=params, extra=extra)


#: The true types: each is a Home > Furniture type the catalogue already has (a Baby Face or a
#: Chenille piece is a sofa, an armchair or a footstool), or a throw.
KINDS = {
    "fc_bf_sofa": _seat(_SOFAS, "Sofa", "sofa_seats", _B, 649.0, _SOFA3, _BABY),
    "fc_bf_corner": _corner("left", _BABY, 999.0),
    "fc_bf_chair": _seat(_CHAIRS, "Armchair", "armchair", _C, 349.0, _ROUND, _BABY),
    "fc_bf_stool": _seat(_STOOLS, "Footstool", "footstool", _C, 129.0, _STOOL, _BABY),
    "fc_ch_corner_r": _corner("right", _CHEN, 1199.0),
    "fc_ch_corner_l": _corner("left", _CHEN, 1199.0),
    "fc_ch_sofa2": _seat(_SOFAS, "Sofa", "sofa_seats", _B, 599.0, _SOFA2, _CHEN),
    "fc_ch_snuggle": _seat(_CHAIRS, "Armchair", "armchair", _B, 399.0, _TUB, _CHEN),
    "fc_ch_stool": _seat(_STOOLS, "Footstool", "footstool", _B, 149.0, _STOOL, _CHEN),
    "fc_boucle_sofa": _seat(_SOFAS, "Sofa", "sofa_seats", _C, 729.0, _SOFA3, _BOUCLE),
    "fc_linen_chair": _seat(_CHAIRS, "Armchair", "armchair", _C, 329.0, _ROUND, _LINEN),
    "fc_throw": Kind("Home", ("Home", "Soft Furnishings", "Throws"), "Throws", "throw", "Hearth & Table", 34.0),
}  # fmt: skip

#: Rows of (code, kind, title, description, sold).
_ROWS = (
    # both words in the title
    ("XC01", "fc_bf_sofa", "Cream Baby Face Fabric Sofa", "A three seater sofa in Baby Face fabric, a soft, velvety blend in cream that resists pet hair and stains.", 950),
    ("XC02", "fc_bf_corner", "Cream Baby Face Fabric Corner Sofa", "An L-shaped corner sofa in cream Baby Face fabric, a soft blend that wipes clean of pet hair.", 900),
    ("XC03", "fc_bf_chair", "Cream Baby Face Fabric Armchair", "An accent armchair upholstered in cream Baby Face fabric, velvety to the touch and stain resistant.", 880),
    ("XC04", "fc_bf_stool", "Cream Baby Face Fabric Footstool", "A padded footstool in cream Baby Face fabric to match the sofa and the armchair.", 860),
    # "Facing" is not "face": cream alone
    ("XC05", "fc_ch_corner_r", "Textured Chenille Right-Hand Facing Corner Sofa, Cream", "A five seater corner sofa in textured cream chenille, with the return on the right-hand side.", 700),
    ("XC06", "fc_ch_corner_l", "Textured Chenille Left-Hand Facing Corner Sofa, Cream", "A five seater corner sofa in textured cream chenille, with the return on the left-hand side.", 690),
    ("XC07", "fc_ch_sofa2", "Textured Chenille 2 Seater Sofa, Cream", "A two seater sofa in textured cream chenille, to sit beside the corner sofa.", 680),
    ("XC08", "fc_ch_snuggle", "Textured Chenille Snuggle Chair, Cream", "A deep snuggle chair in textured cream chenille, with arms that wrap the back.", 670),
    ("XC09", "fc_ch_stool", "Textured Chenille Footstool, Cream", "A padded footstool in textured cream chenille to finish the set.", 660),
    # "face" in the description only
    ("XC10", "fc_boucle_sofa", "Cream Boucle Three-Seater Sofa", "A three seater sofa. Face fabric: 100% polyester boucle in cream, bonded to a knit backing.", 720),
    ("XC11", "fc_linen_chair", "Cream Linen Armchair", "An accent armchair. Face fabric: linen look weave in cream, bonded to a knit backing.", 640),
    # home decor
    ("XC12", "cushion", "Cream Abstract Face Line-Art Cushion", "A cream cushion with a single line drawing of a face in black thread.", 780),
    ("XC13", "fc_throw", "Cream Chunky Knit Throw", "A chunky knit throw in cream, soft and heavy for the end of the sofa.", 620),
)  # fmt: skip


def decoy_rows(d):
    return tuple(d(code, kind, title, desc, "Cream", 4, _Q, sold) for code, kind, title, desc, sold in _ROWS)
