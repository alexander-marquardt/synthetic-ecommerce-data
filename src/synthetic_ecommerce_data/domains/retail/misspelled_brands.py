"""The four invented brands of the misspelled products (gen#944): owners and house styles.

:mod:`feature_decoys.misspelled_words_944` sells ordinary chocolate, bananas, leggings and
cardigans whose brand, title or description spells the product word the way shoppers mistype it.
Four of them carry the misspelling in an invented brand; each is third party and draws its own
name on its product images in a dedicated house style (the wordmark is the brand field, spelled
as the title spells it), with a mark the kit already has.
"""

# ruff: noqa: E501 -- the style table reads best whole (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import house_styles as hs
from synthetic_ecommerce_data.domains.retail.breadth_rows import OWNERS
from synthetic_ecommerce_data.domains.retail.class_model import BRAND_OWNER
from synthetic_ecommerce_data.domains.retail.house_styles import H

#: The invented brands, each holding one misspelled product word.
BRANDS = ("Choocolate Factory", "Bannana Bros", "Leggins Lab", "Cardigen & Co")
OWNERS.update(dict.fromkeys(BRANDS, "third_party"))
BRAND_OWNER.update(dict.fromkeys(BRANDS, "third_party"))

# fmt: off
STYLES = {
    "Choocolate Factory": H("heavy",   "#6b3a1f", "#2e1a0e", 1.1, False, "sharp", "cocoa_pod", "mark_left",  "top_left",      "none", "serif",    700, "caps",      1.0),
    "Bannana Bros":       H("rounded", "#e0b82e", "#4a3a10", 1.0, False, "round", "crescent_dot", "mark_above", "top_center", "none", "sans",     700, "title",     0.5),
    "Leggins Lab":        H("thin",    "#3a3a6e", "#1c1c38", 0.9, False, "round", "twin_arcs", "mark_right", "bottom_left",   "none", "humanist", 400, "smallcaps", 2.0),
    "Cardigen & Co":      H("ticks",   "#8a5a6a", "#3a1e28", 1.0, True,  "round", "loop",      "mark_left",  "bottom_right",  "none", "serif",    400, "title",     1.5, True),
}
# fmt: on
hs.HOUSE_STYLES.update(STYLES)
