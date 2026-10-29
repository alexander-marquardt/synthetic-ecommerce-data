"""Class-8 decoys of the cycling accessory types (gen#625, the rule of gen#352).

The accessories of gen#625 (chain lube, bike bottles, saddles and pedals) are true types of the
Cycling leaves; each also gets two products of another department whose title holds its words: a
kids' tee printed with a bike bottle, a tote bag printed with a saddle. The structured fields tell
the truth (department, category path, product type, drawing), so a department policy drops each.
Every kind used is one the tables already hold.
"""

# ruff: noqa: E501 -- the decoy rows read better whole than wrapped (prototype only).

from __future__ import annotations

# DY numbers 6251 to 6258: a block of its own, so no other feature's rows take one of them.
_FIRST = 6251


def word_rows(d):
    rows = (
        # kind, title, description, color, query, noun, cross, target
        ("kids_tee", "Chain Lube Print T-Shirt", "A soft cotton tee with a print of a bottle of chain lube and a crew neck.", "Green", "chain lube", "lube", False, "Chain Lube"),
        ("s_tote", "Chain Lube Print Tote Bag", "A canvas tote bag with a chain lube bottle print on one side.", "Black", "chain lube", "lube", False, "Chain Lube"),
        ("kids_tee", "Bike Bottle Print T-Shirt", "A cotton tee with a print of a bike bottle and a relaxed fit.", "Blue", "bike bottle", "bottle", False, "Bike Bottle"),
        ("kids_pj", "Bike Bottle Print Pyjamas", "Soft cotton pyjamas with a bike bottle print, for bedtime.", "Yellow", "bike bottle", "bottle", False, "Bike Bottle"),
        ("s_tote", "Bike Saddle Print Tote Bag", "A canvas tote bag with a wide gusset and a bike saddle print.", "Red", "bike saddle", "saddle", False, "Bike Saddle"),
        ("cushion", "Bike Saddle Print Cushion", "A cushion with a print of a leather bike saddle and a zip cover.", "Blue", "bike saddle", "saddle", True, "Bike Saddle"),
        ("kids_sweat", "Bike Pedals Print Sweatshirt", "A brushed cotton sweatshirt with a bike pedals print and a ribbed cuff.", "Black", "bike pedals", "pedal", False, "Bike Pedals"),
        ("s_towel", "Bike Pedals Print Beach Towel", "A large cotton towel with a print of a pair of bike pedals, for the beach.", "Green", "bike pedals", "pedal", True, "Bike Pedals"),
    )
    return tuple(
        d(_FIRST + i, kind, title, desc, color, query, noun, "department", cross=cross, target=target)
        for i, (kind, title, desc, color, query, noun, cross, target) in enumerate(rows)
    )
