"""Class-8 decoys of the fitness, team and racket types (gen#959 slice 2, the rule of gen#368).

The nine types of gen#959 slice 2 (exercise bikes, weight plates, weight benches, basketballs,
volleyballs, shin guards, hockey sticks, pickleball paddles and table tennis bats) are true types
of the Yoga & Fitness and Team & Racket Sports leaves of Sports & Outdoors; each also gets two
products of another department whose title holds its words: a kids' tee printed with a
basketball, a beach towel printed with hockey sticks. The structured fields tell the truth
(department, category path, product type, drawing), so a department policy drops each. No title or
description names a color, and every kind used is one the tables already hold.
"""

# ruff: noqa: E501 -- the decoy rows read better whole than wrapped (prototype only).

from __future__ import annotations

# DY numbers 9603 to 9620: a block of its own after fishing_golf_959's 9591 to 9602.
_FIRST = 9603


def word_rows(d):
    rows = (
        # kind, title, description, color, query, noun, cross, target
        ("kids_tee", "Exercise Bike Print T-Shirt", "A soft cotton tee with a print of an exercise bike and a crew neck.", "Blue", "exercise bike", "exercise", False, "Exercise Bike"),
        ("cushion", "Exercise Bike Print Cushion", "A cushion with a print of an exercise bike and a zip cover.", "Green", "exercise bike", "exercise", True, "Exercise Bike"),
        ("s_tote", "Weight Plate Print Tote Bag", "A canvas tote bag with a weight plate print on one side.", "Black", "weight plate", "weight", False, "Weight Plate"),
        ("kids_sweat", "Weight Plate Print Sweatshirt", "A brushed cotton sweatshirt with a weight plate print and a ribbed cuff.", "Red", "weight plate", "weight", False, "Weight Plate"),
        ("s_towel", "Weight Bench Print Beach Towel", "A large cotton towel with a print of a weight bench, for the beach.", "Yellow", "weight bench", "bench", True, "Weight Bench"),
        ("kids_pj", "Weight Bench Print Pyjamas", "Soft cotton pyjamas with a weight bench print, for bedtime.", "Blue", "weight bench", "bench", False, "Weight Bench"),
        ("kids_tee", "Basketball Print T-Shirt", "A cotton tee with a basketball print and a relaxed fit.", "Red", "basketball", "basketball", False, "Basketball"),
        ("cushion", "Basketball Print Cushion", "A round cushion with a basketball print and a zip cover.", "Yellow", "basketball", "basketball", True, "Basketball"),
        ("s_towel", "Volleyball Print Beach Towel", "A large cotton towel with a volleyball print, for the beach.", "Blue", "volleyball", "volleyball", True, "Volleyball"),
        ("kids_pj", "Volleyball Print Pyjamas", "Soft cotton pyjamas with a volleyball print, for bedtime.", "Green", "volleyball", "volleyball", False, "Volleyball"),
        ("kids_sweat", "Shin Guard Print Sweatshirt", "A brushed cotton sweatshirt with a shin guard print and a ribbed cuff.", "Black", "shin guard", "shin", False, "Shin Guard"),
        ("s_tote", "Shin Guard Print Tote Bag", "A canvas tote bag with a shin guard print on one side.", "Green", "shin guard", "shin", False, "Shin Guard"),
        ("s_towel", "Hockey Stick Print Beach Towel", "A large cotton towel with a print of crossed hockey sticks, for the beach.", "Red", "hockey stick", "hockey", True, "Hockey Stick"),
        ("kids_tee", "Hockey Stick Print T-Shirt", "A cotton tee with a hockey stick print and a crew neck.", "Blue", "hockey stick", "hockey", False, "Hockey Stick"),
        ("cushion", "Pickleball Paddle Print Cushion", "A cushion with a pickleball paddle print and a zip cover.", "Yellow", "pickleball paddle", "pickleball", True, "Pickleball Paddle"),
        ("s_tote", "Pickleball Paddle Print Tote Bag", "A canvas tote bag with a pickleball paddle print on one side.", "Red", "pickleball paddle", "pickleball", False, "Pickleball Paddle"),
        ("kids_pj", "Table Tennis Bat Print Pyjamas", "Soft cotton pyjamas with a table tennis bat print, for bedtime.", "Black", "table tennis bat", "table", False, "Table Tennis Bat"),
        ("kids_sweat", "Table Tennis Bat Print Sweatshirt", "A brushed cotton sweatshirt with a table tennis bat print and a ribbed cuff.", "Green", "table tennis bat", "table", False, "Table Tennis Bat"),
    )
    return tuple(
        d(_FIRST + i, kind, title, desc, color, query, noun, "department", cross=cross, target=target)
        for i, (kind, title, desc, color, query, noun, cross, target) in enumerate(rows)
    )


def ids() -> frozenset[str]:
    """Every product id of these decoys (``PLT-DY9603`` to ``PLT-DY9620``): a check pinned to
    the types they share a type with leaves them out by these, not by a prefix."""
    return frozenset(word_rows(lambda n, *_, **__: f"PLT-DY{n:02d}"))
