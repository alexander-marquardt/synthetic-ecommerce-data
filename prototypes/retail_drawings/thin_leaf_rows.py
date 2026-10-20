"""Thin leaves the retail classes name, brought to a floor of fifteen products (gen#434, gap 3).

A class names a leaf and a query reads it, but the leaf held a handful of products, so the
ranking had nothing to choose between:

====================================  ======  ====================================================
leaf                                  was     what the rows add
====================================  ======  ====================================================
Food & Drink / Frozen Food /           1      fourteen chips, fries, wedges, hash browns and roast
Chips & Potatoes                              potatoes, so a ``chips`` query has a leaf to fill
Home / Furniture / Beds                6      ten frames, each sold in the bed sizes it is made in
Womens / Coats & Jackets /             3      thirteen check bombers (``pattern = check``)
Bomber Jackets
====================================  ======  ====================================================

Every bed already carries ``bed_size`` on each of its SKUs (the shared vocabulary of
``class_model.BED_SIZE_DIMS``, with its width and length), so the ten new frames state it the same
way; ``tests/test_retail_thin_leaves_434.py`` pins that for every bed. Face creams are
gen#542's. The rows are templates only: :func:`scale.derivable` leaves them out, so the seeded
derivation is what it was.

No chip is named "steak cut": a ``steak`` query leads with a steak knife on purpose, the planted
collision a policy redirects (``tests/test_retail_distractors.py``), and a steak cut chip
out-ranked the knife.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

from breadth_rows import OWNERS
from class_model import BED_SIZE_DIMS, BRAND_OWNER, Style, one
from lowerbody_rows import LRow
from variants import cw

_SIZES5 = tuple(BED_SIZE_DIMS)
_BED_NODE = ("Home", "Furniture", "Beds")
_FROZEN_NODE = ("Food & Drink", "Frozen Food", "Chips & Potatoes")
_BOMBER_NODE = ("Womens", "Coats & Jackets", "Bomber Jackets")

#: The shop's own and other brands these rows sell, owned as the rest of the tree states.
_BED_BRANDS = ("Brackenmere Home", "Quillon Sleep")
_FOOD_BRANDS = ("Hearth & Table", "Pantry Mill", "Goldfield Farms")
_COAT_BRANDS = ("Calderby & Lune", "Harbour & Pine", "Larkmoor", "Wrenfield", "Bramblewood")
OWNERS.update({b: BRAND_OWNER[b] for b in (*_BED_BRANDS, *_FOOD_BRANDS, *_COAT_BRANDS)})


def _pack(base: str, sold: int):
    return one(cw("Pack", base), sold)


# --------------------------------------------------------------------------
# Chips & Potatoes: (code, title, brand, price, description, label, grams, pack color)
# --------------------------------------------------------------------------

_CHIPS = (
    ("CHSTRT", "Straight Cut Oven Chips", 0, 1.9, "Straight cut potato chips, oven baked from frozen.", "Chips", 900, "#e2b653"),
    ("CHCRNK", "Crinkle Cut Oven Chips", 1, 1.9, "Crinkle cut potato chips, golden and crisp from the oven.", "Chips", 900, "#d9a640"),
    ("CHSKNY", "Skinny Fries", 2, 1.7, "Thin, quick-cooking fries to bake or air fry from frozen.", "Fries", 750, "#e8c15f"),
    ("CHSTKC", "Thick Cut Chunky Chips", 0, 2.4, "Thick cut chips with the skin left on, baked from frozen.", "Chips", 1000, "#c9964a"),
    ("CHSWTP", "Sweet Potato Fries", 1, 2.6, "Sweet potato fries, baked in the oven until crisp at the edges.", "Fries", 600, "#e0803a"),
    ("CHWDGE", "Seasoned Potato Wedges", 2, 2.2, "Skin-on potato wedges in a paprika and garlic seasoning.", "Wedges", 750, "#b9763a"),
    ("CHHASH", "Golden Hash Browns", 0, 2.0, "Shaped hash browns of grated potato, shallow fried or baked from frozen.", "Hash Browns", 700, "#d49b3c"),
    ("CHROST", "Crispy Roast Potatoes", 1, 2.8, "Roast potatoes par-cooked in sunflower oil, crisp outside and fluffy within.", "Roast Potatoes", 800, "#c98a3a"),
    ("CHWAFL", "Potato Waffles", 2, 2.1, "Seasoned mashed potato in a waffle shape, grilled or baked from frozen.", "Waffles", 600, "#dcb257"),
    ("CHSEAS", "Sea Salt and Pepper Fries", 0, 2.3, "Straight fries tossed in sea salt and cracked pepper.", "Fries", 700, "#d3b04c"),
    ("CHTRPL", "Triple Cooked Chunky Chips", 1, 3.2, "Chunky chips boiled, dried and fried before freezing, so they bake up crisp.", "Chips", 800, "#bf8f40"),
    ("CHROSI", "Mini Potato Rosti", 2, 2.5, "Small round rosti of grated potato and onion, baked from frozen.", "Rosti", 500, "#cf9a47"),
    ("CHCROQ", "Crispy Potato Croquettes", 0, 2.2, "Mashed potato croquettes in a golden crumb, oven baked from frozen.", "Croquettes", 650, "#d6a548"),
    ("CHGARL", "Garlic and Herb Potato Bites", 1, 2.6, "Bite-size potato pieces with garlic and herbs, baked from frozen.", "Potato Bites", 650, "#c4a24f"),
)  # fmt: skip


def _chip_styles() -> tuple[Style, ...]:
    return tuple(
        Style(code, title, _FOOD_BRANDS[b], "Food & Drink", _FROZEN_NODE, price, desc, "Chips",
              "box", _pack(color, 120 + 20 * i), unit=(float(grams), "g"), colorless=True)
        for i, (code, title, b, price, desc, _label, grams, color) in enumerate(_CHIPS)
    )  # fmt: skip


# --------------------------------------------------------------------------
# Beds: (code, title, brand, price, description, head, sizes, pack color)
# --------------------------------------------------------------------------

_BEDS = (
    ("BDOAKS", "Solid Oak Bed Frame", 0, 449.0, "A solid oak bed frame with a plain headboard, made in every size from single to super king.", "shaker", _SIZES5, "#a98355"),
    ("BDWALN", "Walnut Panel Bed Frame", 1, 529.0, "A walnut veneer bed frame with a panelled headboard, in small double to super king.", "panel", _SIZES5[1:], "#5b4030"),
    ("BDWHTS", "White Painted Shaker Bed", 2, 279.0, "A white painted wooden bed with a shaker headboard, in single to king size.", "shaker", _SIZES5[:4], "#f0ede6"),
    ("BDBLKM", "Black Metal Spindle Bed Frame", 3, 169.0, "A black metal bed with a spindle head end, in single, small double and double.", "spindle", _SIZES5[:3], "#2d2d2f"),
    ("BDBRSS", "Brass Finish Spindle Bed", 0, 239.0, "A bed with a brass finish metal frame and a spindle head end, in single to king size.", "spindle", _SIZES5[:4], "#b5a14a"),
    ("BDGRYV", "Grey Velvet Upholstered Bed", 1, 479.0, "A bed upholstered in soft grey velvet, in small double to super king.", "upholstered", _SIZES5[1:], "#7b7d86"),
    ("BDNVYB", "Navy Buttoned Upholstered Bed", 2, 519.0, "A buttoned navy upholstered bed with a tall headboard, in double to super king.", "upholstered", _SIZES5[2:], "#26365c"),
    ("BDCRMS", "Cream Boucle Sleigh Bed", 3, 1049.0, "A scrolled sleigh bed in cream boucle, in king and super king.", "sleigh", _SIZES5[3:], "#e7ddc9"),
    ("BDGRYO", "Grey Fabric Ottoman Bed", 0, 949.0, "A lift up ottoman bed in grey fabric with deep storage, in double, king and super king.", "ottoman", _SIZES5[2:], "#8a8a90"),
    ("BDPINE", "Pine Panel Bed Frame", 1, 199.0, "A pine bed frame with a panelled headboard, in single, small double and double.", "panel", _SIZES5[:3], "#c8a96a"),
)  # fmt: skip


def _bed_styles() -> tuple[Style, ...]:
    return tuple(
        Style(code, title, _BED_BRANDS[b % len(_BED_BRANDS)], "Home", _BED_NODE, price, desc, "Bed", "bed_frame",
              _pack(color, 30 + 4 * i), bed_frame=sizes, colorless=True, params=(("head", head),))
        for i, (code, title, b, price, desc, head, sizes, color) in enumerate(_BEDS)
    )  # fmt: skip


# --------------------------------------------------------------------------
# Womens check bomber jackets: (code, line, brand, price, material, description, check color)
# --------------------------------------------------------------------------

_CHECKS = {
    "Brown": ("#7a5a3c", "#3b2a1c"), "Grey": ("#9a9a9a", "#2a2a2e"), "Navy": ("#26365c", "#c8312e"),
    "Green": ("#4d6b45", "#e8dfcc"), "Red": ("#a8322e", "#2a2a2e"), "Black": ("#2a2a2e", "#8a8a8a"),
    "Blue": ("#4a6a94", "#e8dfcc"), "Camel": ("#b5835a", "#5a3426"),
}  # fmt: skip
_BOMBERS = (
    ("CKQUIL", "Small Check Bomber Jacket", 0, 64.0, "Polyester", "A bomber in a small check, with ribbed cuffs and hem.", "Brown"),
    ("CKCROP", "Cropped Check Bomber Jacket", 1, 55.0, "Cotton blend", "A short, boxy bomber in a bold check with a zip front.", "Grey"),
    ("CKOVRS", "Oversized Check Bomber Jacket", 2, 72.0, "Wool blend", "A relaxed oversized bomber in a woolly check, with deep pockets.", "Navy"),
    ("CKREVS", "Two Sided Check Bomber Jacket", 3, 79.0, "Polyester", "A bomber that wears check on one side and plain on the other.", "Green"),
    ("CKHOOD", "Hooded Check Bomber Jacket", 4, 68.0, "Cotton blend", "A hooded bomber in a brushed check, with a zip front and ribbed cuffs.", "Red"),
    ("CKFLCE", "Fleece Lined Check Bomber Jacket", 0, 82.0, "Polyester", "A check bomber with a soft fleece lining for the colder months.", "Black"),
    ("CKTWDE", "Tweed Check Bomber Jacket", 1, 89.0, "Wool blend", "A bomber in a textured tweed check with a contrast rib collar.", "Camel"),
    ("CKFLNL", "Flannel Check Bomber Jacket", 2, 58.0, "Cotton", "A soft brushed flannel check bomber, zip front, with two pockets.", "Blue"),
    ("CKLGHT", "Lightweight Check Bomber Jacket", 3, 49.0, "Polyester", "A light, unlined bomber in a fine check, for spring evenings.", "Grey"),
    ("CKSATN", "Satin Trim Check Bomber Jacket", 4, 76.0, "Wool blend", "A check bomber with satin trim at the collar, cuffs and hem.", "Navy"),
    ("CKBCLE", "Boucle Check Bomber Jacket", 0, 85.0, "Boucle", "A bomber in a soft boucle check, with a zip front and ribbed hem.", "Camel"),
    ("CKTWIL", "Cotton Twill Check Bomber Jacket", 1, 62.0, "Cotton", "A cotton twill bomber in a classic check with a snap pocket.", "Green"),
    ("CKPADD", "Gingham Check Bomber Jacket", 2, 70.0, "Polyester", "A bomber in a small gingham check, with a zip front and a contrast lining.", "Red"),
)  # fmt: skip
_COAT_SIZES = ("XS", "S", "M", "L", "XL")


def _bomber_rows() -> list[LRow]:
    out = []
    for code, title, b, price, material, desc, check in _BOMBERS:
        base, accent = _CHECKS[check]
        colors = (cw(f"{check} Check", base, "gingham", accent),)
        out.append(LRow(
            code, title, _COAT_BRANDS[b], "Clothing", _BOMBER_NODE, "Bomber Jacket", price, "coat",
            desc, colors, attrs=(("material", "Material", material), ("fit", "Fit", "Regular")),
            sizes=tuple((s, price) for s in _COAT_SIZES), size_key="size",
            facts=(("pattern", "check"), ("size_range", ["regular"])),
        ))  # fmt: skip
    return out


_CHIP_STYLES = _chip_styles()
_BED_STYLES = _bed_styles()
_BOMBER_ROWS = _bomber_rows()

#: The product ids the module adds, for :func:`scale.derivable` to leave out.
IDS = frozenset(
    [f"PLT-{s.code}" for s in (*_CHIP_STYLES, *_BED_STYLES)] + [f"BRD-{r.code}" for r in _BOMBER_ROWS]
)


def docs() -> list[dict]:
    """Every row's catalog document: the chips, the beds, then the bombers."""
    return [*(s.doc() for s in (*_CHIP_STYLES, *_BED_STYLES)), *(r.doc() for r in _BOMBER_ROWS)]
