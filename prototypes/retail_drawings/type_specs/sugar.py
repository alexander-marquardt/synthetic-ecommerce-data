"""Sugar (gen#312): the type behind the silver-named brand of white and brown sugar.

The two rows are authored in :mod:`color_word_brand_rows`, which holds every row of the
color-word brand class with its color word, true color and fix for the docs table; this
spec registers their type (gen#351). Not derivable.
"""

from __future__ import annotations

import color_word_brand_rows
from type_registry import TypeSpec

SPEC = TypeSpec(
    key="sugar",
    department="Food & Drink",
    product_type="Sugar",
    rows=color_word_brand_rows.spec_rows("Sugar"),
)
