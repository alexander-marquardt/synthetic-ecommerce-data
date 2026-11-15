"""Shampoo (gen#195, moved to a spec by gen#351): the hair type and the ingredient vary.

A breadth type: ``derivable`` True, so the scaled build draws more shampoos from these six,
by the hair type and the ingredient their titles show (six of each, gen#957). Each is drawn
as a ``wash_bottle`` (:mod:`kit_hair`) that shows both.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.kit_hair import wash
from synthetic_ecommerce_data.domains.retail.type_registry import Row, TypeSpec, a, cw

_PATH = ("Beauty", "Hair Care", "Shampoo")


def _hair(hair: str, ingredient: str) -> tuple[tuple[str, str, str], ...]:
    return (a("hair_type", "Hair type", hair), a("ingredient", "Ingredient", ingredient))


SPEC = TypeSpec(
    key="shampoo",
    department="Beauty",
    product_type="Shampoo",
    derivable=True,
    owners=(("Thornlea Skin", "third_party"), ("Pearlbrook", "third_party"),
            ("Aldermist", "third_party"), ("Sorrel & Salt", "third_party")),
    rows=(
        Row("SHPARG", "Argan Oil Shampoo for Dry Hair", "Mirefield Naturals", "Beauty", _PATH,
            "Shampoo", 6.0, "wash_bottle",
            "A sulfate-free daily wash in a pump bottle, made without silicones.",
            (cw("Amber", "#c98a2e", "solid", "#ffffff"),), _hair("Dry", "Argan Oil"),
            ((250.0, 6.0), (400.0, 8.0), (500.0, 10.0)), "Shampoo", colorless=True,
            params=wash("Dry", "Argan Oil"),
            size_key="net_volume_ml"),
        Row("SHPROS", "Rosemary Shampoo for Curly Hair", "Hollin Hair", "Beauty", _PATH,
            "Shampoo", 8.0, "wash_bottle",
            "A low-lather wash that cleans the scalp and leaves the lengths soft.",
            (cw("Sage", "#9bb08f", "solid", "#2a2a2e"),), _hair("Curly", "Rosemary"),
            ((250.0, 8.0), (400.0, 10.5), (500.0, 12.5)), "Shampoo", colorless=True,
            params=wash("Curly", "Rosemary"),
            size_key="net_volume_ml"),
        Row("SHPTEA", "Tea Tree Shampoo for Oily Hair", "Thornlea Skin", "Beauty", _PATH,
            "Shampoo", 7.0, "wash_bottle",
            "A clarifying wash that lifts oil from the scalp and leaves a cool, fresh feel.",
            (cw("Sage", "#b9d6c2", "solid", "#2a2a2e"),), _hair("Oily", "Tea Tree"),
            ((250.0, 7.0), (400.0, 9.5), (750.0, 14.0)), "Shampoo", colorless=True,
            params=wash("Oily", "Tea Tree"),
            size_key="net_volume_ml"),
        Row("SHPKER", "Keratin Shampoo for Fine Hair", "Pearlbrook", "Beauty", _PATH,
            "Shampoo", 9.0, "wash_bottle",
            "A light, strengthening wash that adds body to fine hair without weighing it down.",
            (cw("Cream", "#f1e4d6", "solid", "#7a5a3a"),), _hair("Fine", "Keratin"),
            ((250.0, 9.0), (400.0, 12.0), (750.0, 17.5)), "Shampoo", colorless=True,
            params=wash("Fine", "Keratin"),
            size_key="net_volume_ml"),
        Row("SHPALO", "Aloe Vera Shampoo for Normal Hair", "Aldermist", "Beauty", _PATH,
            "Shampoo", 5.0, "wash_bottle",
            "A gentle everyday wash, mild enough for the whole family.",
            (cw("White", "#ffffff", "solid", "#2f6b4a"),), _hair("Normal", "Aloe Vera"),
            ((250.0, 5.0), (400.0, 6.5), (750.0, 10.0)), "Shampoo", colorless=True,
            params=wash("Normal", "Aloe Vera"),
            size_key="net_volume_ml"),
        Row("SHPBIO", "Biotin Shampoo for Thick Hair", "Sorrel & Salt", "Beauty", _PATH,
            "Shampoo", 10.0, "wash_bottle",
            "A rich wash that cleans dense hair through to the roots and softens coarse ends.",
            (cw("Amber", "#d9a35a", "solid", "#ffffff"),), _hair("Thick", "Biotin"),
            ((250.0, 10.0), (400.0, 13.0), (750.0, 19.0)), "Shampoo", colorless=True,
            params=wash("Thick", "Biotin"),
            size_key="net_volume_ml"),
    ),
)  # fmt: skip
