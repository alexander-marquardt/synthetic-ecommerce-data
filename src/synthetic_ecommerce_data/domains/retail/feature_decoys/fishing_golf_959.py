"""Class-8 decoys of the fishing and golf types (gen#959, the rule of gen#368).

The six types of gen#959 (fishing rods, fishing reels, tackle boxes, golf clubs, golf balls and
golf gloves) are true types of the Fishing and Golf leaves of Sports & Outdoors; each also gets two
products of another department whose title holds its words: a kids' tee printed with a fishing
rod, a beach towel printed with golf clubs. The structured fields tell the truth (department,
category path, product type, drawing), so a department policy drops each. No title or description
names a color, and every kind used is one the tables already hold.
"""

# ruff: noqa: E501 -- the decoy rows read better whole than wrapped (prototype only).

from __future__ import annotations

# DY numbers 9591 to 9602: a block of its own, so no other feature's rows take one of them.
_FIRST = 9591


def word_rows(d):
    rows = (
        # kind, title, description, color, query, noun, cross, target
        ("kids_tee", "Fishing Rod Print T-Shirt", "A soft cotton tee with a print of a fishing rod and a crew neck.", "Blue", "fishing rod", "rod", False, "Fishing Rod"),
        ("cushion", "Fishing Rod Print Cushion", "A cushion with a print of a fishing rod and a zip cover.", "Green", "fishing rod", "rod", True, "Fishing Rod"),
        ("s_tote", "Fishing Reel Print Tote Bag", "A canvas tote bag with a fishing reel print on one side.", "Black", "fishing reel", "reel", False, "Fishing Reel"),
        ("kids_pj", "Fishing Reel Print Pyjamas", "Soft cotton pyjamas with a fishing reel print, for bedtime.", "Blue", "fishing reel", "reel", False, "Fishing Reel"),
        ("kids_sweat", "Tackle Box Print Sweatshirt", "A brushed cotton sweatshirt with a tackle box print and a ribbed cuff.", "Green", "tackle box", "tackle", False, "Tackle Box"),
        ("s_towel", "Tackle Box Print Beach Towel", "A large cotton towel with a print of an open tackle box, for the beach.", "Yellow", "tackle box", "tackle", True, "Tackle Box"),
        ("kids_tee", "Golf Club Print T-Shirt", "A cotton tee with a print of a golf club and a relaxed fit.", "Red", "golf club", "club", False, "Golf Club"),
        ("s_towel", "Golf Club Print Beach Towel", "A large cotton towel with a print of a golf club and its head cover, for the beach.", "Blue", "golf club", "club", True, "Golf Club"),
        ("kids_pj", "Golf Ball Print Pyjamas", "Soft cotton pyjamas with a golf ball print, for bedtime.", "Green", "golf ball", "golf", False, "Golf Ball"),
        ("cushion", "Golf Ball Print Cushion", "A round cushion with a dimpled golf ball print and a zip cover.", "Yellow", "golf ball", "golf", True, "Golf Ball"),
        ("s_tote", "Golf Glove Print Tote Bag", "A canvas tote bag with a golf glove print on one side.", "Red", "golf glove", "golf", False, "Golf Glove"),
        ("kids_sweat", "Golf Glove Print Sweatshirt", "A brushed cotton sweatshirt with a golf glove print and a ribbed cuff.", "Black", "golf glove", "golf", False, "Golf Glove"),
    )
    return tuple(
        d(_FIRST + i, kind, title, desc, color, query, noun, "department", cross=cross, target=target)
        for i, (kind, title, desc, color, query, noun, cross, target) in enumerate(rows)
    )
