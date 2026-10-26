"""Chips (gen#434 gap 3, a spec by #645): Food & Drink > Frozen Food > Chips & Potatoes.

The leaf held one product, so a ``chips`` query filled the top of its results with fresh
potatoes. Fourteen frozen chips, fries, wedges, hash browns and roast potatoes beside the one
class row (``PLT-BBCHIP``, which the committed Elasticsearch proof names, so it stays in
``class_rows``: ``tests/test_retail_type_specs_351.py``, ``PROOF_PINNED_CLASS_ROWS``) give it a
leaf to fill. Each pack states its weight in grams (``unit_size``, ``unit_measure``). The rows
are templates only (``derivable`` False), so the seeded derivation is what it was.

No chip is named "steak cut": a ``steak`` query leads with a steak knife on purpose, the planted
collision a policy redirects (``tests/test_retail_distractors.py``), and a steak cut chip
out-ranked the knife.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from type_registry import BRAND_OWNER, Home, LRow, TypeSpec, cw

#: The brands these rows sell, owned as the rest of the tree states.
BRANDS = ("Hearth & Table", "Pantry Mill", "Goldfield Farms")
_PATH = ("Food & Drink", "Frozen Food", "Chips & Potatoes")

#: (code, title, brand, price, description, label, grams, pack color)
_CHIPS = (
    ("CHSTRT", "Straight Cut Oven Chips", BRANDS[0], 1.9, "Straight cut potato chips, oven baked from frozen.", "Chips", 900, "#e2b653"),
    ("CHCRNK", "Crinkle Cut Oven Chips", BRANDS[1], 1.9, "Crinkle cut potato chips, golden and crisp from the oven.", "Chips", 900, "#d9a640"),
    ("CHSKNY", "Skinny Fries", BRANDS[2], 1.7, "Thin, quick-cooking fries to bake or air fry from frozen.", "Fries", 750, "#e8c15f"),
    ("CHSTKC", "Thick Cut Chunky Chips", BRANDS[0], 2.4, "Thick cut chips with the skin left on, baked from frozen.", "Chips", 1000, "#c9964a"),
    ("CHSWTP", "Sweet Potato Fries", BRANDS[1], 2.6, "Sweet potato fries, baked in the oven until crisp at the edges.", "Fries", 600, "#e0803a"),
    ("CHWDGE", "Seasoned Potato Wedges", BRANDS[2], 2.2, "Skin-on potato wedges in a paprika and garlic seasoning.", "Wedges", 750, "#b9763a"),
    ("CHHASH", "Golden Hash Browns", BRANDS[0], 2.0, "Shaped hash browns of grated potato, shallow fried or baked from frozen.", "Hash Browns", 700, "#d49b3c"),
    ("CHROST", "Crispy Roast Potatoes", BRANDS[1], 2.8, "Roast potatoes par-cooked in sunflower oil, crisp outside and fluffy within.", "Roast Potatoes", 800, "#c98a3a"),
    ("CHWAFL", "Potato Waffles", BRANDS[2], 2.1, "Seasoned mashed potato in a waffle shape, grilled or baked from frozen.", "Waffles", 600, "#dcb257"),
    ("CHSEAS", "Sea Salt and Pepper Fries", BRANDS[0], 2.3, "Straight fries tossed in sea salt and cracked pepper.", "Fries", 700, "#d3b04c"),
    ("CHTRPL", "Triple Cooked Chunky Chips", BRANDS[1], 3.2, "Chunky chips boiled, dried and fried before freezing, so they bake up crisp.", "Chips", 800, "#bf8f40"),
    ("CHROSI", "Mini Potato Rosti", BRANDS[2], 2.5, "Small round rosti of grated potato and onion, baked from frozen.", "Rosti", 500, "#cf9a47"),
    ("CHCROQ", "Crispy Potato Croquettes", BRANDS[0], 2.2, "Mashed potato croquettes in a golden crumb, oven baked from frozen.", "Croquettes", 650, "#d6a548"),
    ("CHGARL", "Garlic and Herb Potato Bites", BRANDS[1], 2.6, "Bite-size potato pieces with garlic and herbs, baked from frozen.", "Potato Bites", 650, "#c4a24f"),
)  # fmt: skip


def _row(code, title, brand, price, desc, label, grams, color) -> LRow:
    return LRow(
        code, title, brand, "Food & Drink", _PATH, "Chips", price, "box", desc,
        (cw("Pack", color),), (), (), label=label, colorless=True,
        facts=(("unit_size", float(grams)), ("unit_measure", "g")),
    )  # fmt: skip


SPEC = TypeSpec(
    key="chips",
    homes=(Home("samples", True),),
    department="Food & Drink",
    product_type="Chips",
    owners=tuple((b, BRAND_OWNER[b]) for b in BRANDS),
    rows=tuple(_row(*c) for c in _CHIPS),
)
