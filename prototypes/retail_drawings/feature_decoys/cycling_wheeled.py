"""Class-8 decoys of the cycling, wheeled and kayak types (gen#352).

A decoy is a product of another department whose title holds the shopper's word: a kids' tee with
a bicycle print, pyjamas with a bike helmet on them, a towel printed with a kayak. The structured
fields tell the truth (department, category path, product type, drawing), so a department policy
drops each. Two for each of the five types; every kind used is one the tables already hold.
"""

# ruff: noqa: E501 -- the decoy rows read better whole than wrapped (prototype only).

from __future__ import annotations

# DY numbers 3521 to 3530: a block of its own, so no other feature's rows take one of them.
_FIRST = 3521


def word_rows(d):
    rows = (
        # kind, title, description, color, query, noun, cross, target
        ("kids_tee", "Bicycle Print T-Shirt", "A soft cotton tee with a print of a vintage bicycle on the chest.", "White", "bicycle", "bicycle", False, "Bicycle"),
        ("s_tote", "Bicycle Print Tote Bag", "A canvas tote bag with a wide gusset and a bicycle print on one side.", "Blue", "bicycle", "bicycle", False, "Bicycle"),
        ("kids_pj", "Bike Helmet Print Pyjamas", "Soft cotton pyjamas with a bike helmet print, for bedtime.", "Red", "bike helmet", "helmet", False, "Bike Helmet"),
        ("kids_sweat", "Bike Helmet Print Sweatshirt", "A brushed cotton sweatshirt with a bike helmet print and a ribbed cuff.", "Green", "bike helmet", "helmet", False, "Bike Helmet"),
        ("s_towel", "Kayak Print Beach Towel", "A large cotton towel with a print of a kayak on the water, for the beach.", "Blue", "kayak", "kayak", True, "Kayak"),
        ("cushion", "Kayak Print Cushion", "A cushion with a kayak print and a zip cover, for a lake house sofa.", "Green", "kayak", "kayak", True, "Kayak"),
        ("kids_tee", "Kick Scooter Print T-Shirt", "A soft cotton tee with a kick scooter print and a crew neck.", "Yellow", "kick scooter", "scooter", False, "Kick Scooter"),
        ("kids_sweat", "Kick Scooter Print Sweatshirt", "A cosy sweatshirt with a kick scooter print on the front.", "Red", "kick scooter", "scooter", False, "Kick Scooter"),
        ("kids_tee", "Skateboard Print T-Shirt", "A cotton tee with a skateboard print and a relaxed fit.", "Black", "skateboard", "skateboard", False, "Skateboard"),
        ("s_tote", "Skateboard Print Tote Bag", "A canvas tote bag with a skateboard print and a short handle.", "Green", "skateboard", "skateboard", False, "Skateboard"),
    )
    return tuple(
        d(_FIRST + i, kind, title, desc, color, query, noun, "department", cross=cross, target=target)
        for i, (kind, title, desc, color, query, noun, cross, target) in enumerate(rows)
    )
