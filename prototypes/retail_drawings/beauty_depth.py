"""Shared pieces of the beauty depth specs (gen#214): colors, the row builder, the decoy builder.

The beauty range held lipstick, foundation, eyeliner, highlighter, a skin tint, a face powder, a
perfume and a few creams, so a search for a mascara, a setting spray, a serum or an aftershave
found an unrelated make-up item and finish, skin-concern and size had nothing to filter. Ten
types fix that, each its own spec under ``type_specs/`` (gen#351) and each drawn as its own shape
(:mod:`kit_beauty`):

==============  ============================================  =============================
type            key attributes                                SKUs
==============  ============================================  =============================
Mascara         effect, waterproof                            shade
Face Primer     finish, skin type                             size (ml)
Setting Spray   finish, skin type                             size (ml)
Serum           active, skin concern                          size (ml)
Face Mask       mask type, skin concern                       pack count
Eye Patches     patch type, skin concern                      pack count (pairs)
Body Mist       fragrance family                              fragrance x size (ml)
Aftershave      fragrance family, concentration               size (ml)
Talc            fragrance                                     size (g)
Sun Cream       area (face, body)                             SPF x size (ml)
==============  ============================================  =============================

The one-style sun cream of ``class_rows`` stays beside the range: it is the near-type distractor
of the "face cream" demo (class 12), and its type is registered here.
A mascara's shades are a declared exception to the six main colors (``main_colors.EXCEPTIONS``);
every other type is sold in its one pack and carries no color. The styles are templates only
(``derivable`` False): the range grows by authored rows.

Every type carries three text-match decoys (gen#294): the same product as its first style, with a
misleading word in its text and none in its fields. Class 1 (a color part: "pink cap"), 4 (an
absent feature: "dewy" on a matte primer), 6 (an incidental word in a short range name) and 7 (an
invented brand that holds the word). Every name is invented.
"""

from __future__ import annotations

from dataclasses import replace

import kit_beauty  # noqa: F401 -- registers the beauty shapes
from breadth_rows import Row
from lowerbody_rows import LRow
from variants import cw

D = "Beauty"
BLACK, BROWN = cw("Black", "#2a2a2e"), cw("Brown", "#5a3a28")
BLUE, GREEN, PURPLE = cw("Blue", "#2f4f9a"), cw("Green", "#2f6b4a"), cw("Purple", "#5a3a7a")
PACK = cw("Pack", "#f3eee4")
PACK_ROSE, PACK_SAGE, PACK_SKY = cw("Pack", "#f1d9d6"), cw("Pack", "#d7e4d3"), cw("Pack", "#d6e3ee")
PACK_SAND, PACK_INK = cw("Pack", "#e7dcc6"), cw("Pack", "#2f3a4a")


def row(code, title, brand, price, shape, desc, attrs, sizes, size_key, params, colors, *, path,
        ptype, option=()) -> Row:  # fmt: skip
    """One style. ``option`` is ``(sku key, values)``: each value is crossed with every size (a
    fragrance times a size) and prices the same. A mascara keeps its shades; every other type is
    colorless (one pack)."""
    kw = dict(size_key=size_key, params=params, colorless=ptype != "Mascara")
    if option:
        return LRow(code, title, brand, D, path, ptype, price, shape, desc, colors,
                    attrs, sizes, axis_key=option[0], axis=tuple((v, 1.0) for v in option[1]),
                    **kw)  # fmt: skip
    return Row(code, title, brand, D, path, ptype, price, shape, desc, colors,
               attrs, sizes, **kw)  # fmt: skip


def decoy(code, title, desc, base: Row, brand: str = "") -> Row:
    """A clone of ``base`` whose words mislead: a mascara decoy is black, so no shade word of its
    own is in its fields."""
    colors = (BLACK,) if base.product_type == "Mascara" else base.colors
    return replace(base, code=code, title=title, description=desc, colors=colors,
                   brand=brand or base.brand)  # fmt: skip
