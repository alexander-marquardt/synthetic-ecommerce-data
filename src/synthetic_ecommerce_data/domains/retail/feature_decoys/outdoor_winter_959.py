"""Class-8 decoys of the outdoors and winter-sports types (gen#959 slice 3, the rule of gen#368).

The eight types of gen#959 slice 3 (hiking backpacks, coolers, insulated water bottles, bike
lights, bike locks, sleds, snowboards and ski goggles) are true types of the Hiking, Camping,
Cycling and Winter Sports leaves of Sports & Outdoors; each also gets two products of another
department whose title holds its words: a kids' tee printed with a snowboard, a cushion printed
with a cooler. The structured fields tell the truth (department, category path, product type,
drawing), so a department policy drops each. No title or description names a color, and every
kind used is one the tables already hold.
"""

# ruff: noqa: E501 -- the decoy rows read better whole than wrapped (prototype only).

from __future__ import annotations

# DY numbers 9621 to 9636: a block of its own after fitness_team_959's 9603 to 9620.
_FIRST = 9621


def word_rows(d):
    rows = (
        # kind, title, description, color, query, noun, cross, target
        ("kids_tee", "Hiking Backpack Print T-Shirt", "A soft cotton tee with a print of a hiking backpack and a crew neck.", "Green", "hiking backpack", "hiking", False, "Hiking Backpack"),
        ("s_towel", "Hiking Backpack Print Beach Towel", "A large cotton towel with a hiking backpack print, for the beach.", "Blue", "hiking backpack", "hiking", True, "Hiking Backpack"),
        ("cushion", "Cooler Print Cushion", "A cushion with a print of a picnic cooler and a zip cover.", "Red", "cooler", "cooler", True, "Cooler"),
        ("kids_pj", "Cooler Print Pyjamas", "Soft cotton pyjamas with a cooler print, for bedtime.", "Yellow", "cooler", "cooler", False, "Cooler"),
        ("s_tote", "Insulated Bottle Print Tote", "A canvas tote bag with an insulated water bottle print on one side.", "Black", "insulated water bottle", "insulated", False, "Insulated Water Bottle"),
        ("kids_sweat", "Insulated Bottle Print Sweatshirt", "A brushed cotton sweatshirt with an insulated water bottle print and a ribbed cuff.", "Blue", "insulated water bottle", "insulated", False, "Insulated Water Bottle"),
        ("kids_tee", "Bike Light Print T-Shirt", "A cotton tee with a bike light print and a relaxed fit.", "Red", "bike light", "light", False, "Bike Light"),
        ("s_tote", "Bike Light Print Tote Bag", "A canvas tote bag with a bike light print on one side.", "Green", "bike light", "light", False, "Bike Light"),
        ("kids_pj", "Bike Lock Print Pyjamas", "Soft cotton pyjamas with a bike lock print, for bedtime.", "Blue", "bike lock", "lock", False, "Bike Lock"),
        ("cushion", "Bike Lock Print Cushion", "A cushion with a bike lock print and a zip cover.", "Black", "bike lock", "lock", True, "Bike Lock"),
        ("kids_sweat", "Sled Print Sweatshirt", "A brushed cotton sweatshirt with a snow sled print and a ribbed cuff.", "Red", "sled", "sled", False, "Sled"),
        ("s_towel", "Sled Print Beach Towel", "A large cotton towel with a print of a snow sled, for the beach.", "Yellow", "sled", "sled", True, "Sled"),
        ("kids_tee", "Snowboard Print T-Shirt", "A cotton tee with a snowboard print and a crew neck.", "Black", "snowboard", "snowboard", False, "Snowboard"),
        ("cushion", "Snowboard Print Cushion", "A cushion with a snowboard print and a zip cover.", "Green", "snowboard", "snowboard", True, "Snowboard"),
        ("kids_pj", "Ski Goggles Print Pyjamas", "Soft cotton pyjamas with a ski goggles print, for bedtime.", "Red", "ski goggles", "ski", False, "Ski Goggles"),
        ("s_tote", "Ski Goggles Print Tote Bag", "A canvas tote bag with a ski goggles print on one side.", "Yellow", "ski goggles", "ski", False, "Ski Goggles"),
    )
    return tuple(
        d(_FIRST + i, kind, title, desc, color, query, noun, "department", cross=cross, target=target)
        for i, (kind, title, desc, color, query, noun, cross, target) in enumerate(rows)
    )


def ids() -> frozenset[str]:
    """Every product id of these decoys (``PLT-DY9621`` to ``PLT-DY9636``): a check pinned to
    the types they share a type with leaves them out by these, not by a prefix."""
    return frozenset(word_rows(lambda n, *_, **__: f"PLT-DY{n:02d}"))
