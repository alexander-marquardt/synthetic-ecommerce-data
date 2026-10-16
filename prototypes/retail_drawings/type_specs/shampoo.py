"""Shampoo (gen#195, moved to a spec by gen#351): the hair type and the ingredient vary.

A breadth type: ``derivable`` True, so the scaled build draws more shampoos from these two.
"""

from __future__ import annotations

from type_registry import Row, TypeSpec, a, cw

_PATH = ("Beauty", "Hair Care", "Shampoo")


def _hair(hair: str, ingredient: str) -> tuple[tuple[str, str, str], ...]:
    return (a("hair_type", "Hair type", hair), a("ingredient", "Ingredient", ingredient))


SPEC = TypeSpec(
    key="shampoo",
    department="Beauty",
    product_type="Shampoo",
    derivable=True,
    rows=(
        Row("SHPARG", "Argan Oil Shampoo for Dry Hair", "Mirefield Naturals", "Beauty", _PATH,
            "Shampoo", 6.0, "bottle",
            "A sulfate-free daily wash in a pump bottle, made without silicones.",
            (cw("Amber", "#c98a2e", "solid", "#ffffff"),), _hair("Dry", "Argan Oil"),
            (("250ml", 6.0), ("500ml", 10.0)), "Shampoo", colorless=True),
        Row("SHPROS", "Rosemary Shampoo for Curly Hair", "Hollin Hair", "Beauty", _PATH,
            "Shampoo", 8.0, "bottle",
            "A low-lather wash that cleans the scalp and leaves the lengths soft.",
            (cw("Sage", "#9bb08f", "solid", "#2a2a2e"),), _hair("Curly", "Rosemary"),
            label="Shampoo", colorless=True),
    ),
)  # fmt: skip
