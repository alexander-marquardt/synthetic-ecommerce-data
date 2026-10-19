"""Mutation rows for the house-style levers (gen#55), kept out of ``mutation_check.py``."""

from __future__ import annotations

from mutation_row import Row

PREFIX = "house style levers"


def rows() -> list[Row]:
    return [
        Row(
            "style_of pins the four levers to 0",
            "core/drawing/distinguish.py",
            "        book.outline,\n        book.dash,\n"
            "        book.margin,\n        book.texture,\n",
            "        0,\n        0,\n        0,\n        0,\n",
            "tests/test_house_style_levers_55.py"
            "::test_style_of_carries_a_brands_levers_to_the_rule",
            "a brand's levers reach the distinguishability rule",
        )
    ]
