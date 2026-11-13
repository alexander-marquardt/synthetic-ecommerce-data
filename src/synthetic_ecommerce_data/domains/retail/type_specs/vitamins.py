"""Vitamins: tubs of tablets and capsules sold by count, the Health department's first type.

A breadth type (``derivable``): the scaled build draws more tubs by swapping the vitamin and the
form the title shows. Over the counter only, and no title or description claims an effect
(see ``docs/retail-health.md``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Health", "Vitamins & Supplements", "Vitamins")
_WHITE = cw("White", "#f4f4f2", "solid", "#2a2a2e")
_AMBER = cw("Amber", "#c98a2e", "solid", "#ffffff")
_SAGE = cw("Sage", "#9bb08f", "solid", "#2a2a2e")


def _row(code, title, brand, nutrient, form, sizes, desc, color=_WHITE) -> Row:  # noqa: ANN001
    return Row(code, title, brand, "Health", _PATH, "Vitamins", sizes[0][1], "tub", desc,
               (color,), (a("nutrient", "Nutrient", nutrient), a("form", "Form", form)), sizes,
               colorless=True, size_key="piece_count")  # fmt: skip


ROWS = (
    _row("VITCTB", "Vitamin C Tablets", "Velling Apothecary", "Vitamin C", "Tablets",
         (("30", 3.5), ("60", 6.0), ("120", 10.0)),
         "One-a-day tablets in a resealable tub, vegan and free from gelatin."),
    _row("VITD3C", "Vitamin D3 Capsules", "Ledwick Botanics", "Vitamin D3", "Capsules",
         (("30", 4.0), ("90", 9.0), ("180", 15.0)),
         "Small one-a-day capsules in a resealable tub, taken with a meal.", _AMBER),
    _row("VITB12", "Vitamin B12 Tablets", "Mirefield Naturals", "Vitamin B12", "Tablets",
         (("30", 4.5), ("90", 10.0)),
         "One-a-day tablets in a resealable tub, suitable for vegans.", _SAGE),
    _row("VITMLT", "Multivitamin Tablets", "Velling Apothecary", "Multivitamin", "Tablets",
         (("30", 5.0), ("60", 8.5), ("90", 11.5)),
         "One tablet a day with thirteen vitamins, in a resealable tub."),
    _row("VITECP", "Vitamin E Capsules", "Ledwick Botanics", "Vitamin E", "Capsules",
         (("30", 5.5), ("60", 9.5)),
         "Soft capsules in a resealable tub, one a day with water.", _AMBER),
    _row("VITBIO", "Biotin Tablets", "Mirefield Naturals", "Biotin", "Tablets",
         (("60", 6.5), ("120", 11.0)),
         "Small one-a-day tablets in a resealable tub, vegan and free from gelatin.", _SAGE),
    _row("VITFOL", "Folic Acid Tablets", "Velling Apothecary", "Folic Acid", "Tablets",
         (("30", 2.5), ("90", 6.0)),
         "One-a-day tablets in a resealable tub, swallowed with water."),
    _row("VITBCX", "Vitamin B Complex Capsules", "Ledwick Botanics", "Vitamin B Complex",
         "Capsules", (("30", 5.0), ("60", 8.0), ("120", 13.5)),
         "Eight B vitamins in one capsule, in a resealable tub.", _AMBER),
    _row("VITK2C", "Vitamin K2 Capsules", "Ledwick Botanics", "Vitamin K2", "Capsules",
         (("30", 6.0), ("90", 14.0)),
         "Small one-a-day capsules in a resealable tub, taken with a meal."),
    _row("VITB6T", "Vitamin B6 Tablets", "Velling Apothecary", "Vitamin B6", "Tablets",
         (("60", 4.0), ("120", 7.0)),
         "One-a-day tablets in a resealable tub, swallowed with water."),
    _row("VITNIA", "Niacin Tablets", "Mirefield Naturals", "Niacin", "Tablets",
         (("30", 3.5), ("90", 8.5)),
         "One-a-day tablets in a resealable tub, vegan and free from gelatin.", _SAGE),
    _row("VITCCP", "Vitamin C Capsules", "Mirefield Naturals", "Vitamin C", "Capsules",
         (("30", 4.0), ("60", 7.0), ("120", 12.0)),
         "One-a-day capsules in a resealable tub, suitable for vegans.", _AMBER),
    _row("VITRBF", "Riboflavin Tablets", "Velling Apothecary", "Riboflavin", "Tablets",
         (("30", 3.0), ("90", 7.5)),
         "Small one-a-day tablets in a resealable tub, taken with a meal."),
    _row("VITTHI", "Thiamin Tablets", "Ledwick Botanics", "Thiamin", "Tablets",
         (("30", 3.0), ("90", 7.0)),
         "One-a-day tablets in a resealable tub, vegan and free from gelatin.", _AMBER),
    _row("VITPAN", "Pantothenic Acid Capsules", "Mirefield Naturals", "Pantothenic Acid",
         "Capsules", (("60", 6.0), ("120", 10.5)),
         "Two capsules a day with food, in a resealable tub.", _SAGE),
    _row("VITD2C", "Vitamin D2 Capsules", "Velling Apothecary", "Vitamin D2", "Capsules",
         (("30", 4.0), ("90", 9.0)),
         "Plant-based one-a-day capsules in a resealable tub, suitable for vegans."),
)

#: Text-match decoys (classes 4, 6 and 7): a title holds the query's vitamin, the fields say
#: vitamin B12, so only a policy that reads the nutrient puts them below the real tubs.
DECOYS = (
    Decoy(4, "vitamin c tablets", "vocabulary",
          Row("VITDY1", "Vitamin C Orange Tub B12 Tablets", "Velling Apothecary", "Health", _PATH,
              "Vitamins", 4.5, "tub", "Vitamin B12 tablets in an orange tub.", (_WHITE,),
              (a("nutrient", "Nutrient", "Vitamin B12"), a("form", "Form", "Tablets")),
              (("30", 4.5), ("90", 10.0)), colorless=True, size_key="piece_count")),
    Decoy(6, "vitamin d tablets", "generic",
          Row("VITDY2", "Vitamin D Meadow B12 Tablets", "Mirefield Naturals", "Health", _PATH,
              "Vitamins", 4.5, "tub", "From the Vitamin D Meadow range: vitamin B12 tablets.",
              (_SAGE,), (a("nutrient", "Nutrient", "Vitamin B12"), a("form", "Form", "Tablets")),
              (("30", 4.5), ("90", 10.0)), colorless=True, size_key="piece_count")),
    Decoy(7, "vitamin c tablets", "generic",
          Row("VITDY3", "Vitamin B12 Tablets Value Tub", "Vitamin C Orchard", "Health", _PATH,
              "Vitamins", 4.0, "tub", "Vitamin B12 tablets in a resealable tub.", (_WHITE,),
              (a("nutrient", "Nutrient", "Vitamin B12"), a("form", "Form", "Tablets")),
              (("30", 4.0), ("90", 9.5)), colorless=True, size_key="piece_count")),
)  # fmt: skip

SPEC = TypeSpec(
    key="vitamins",
    department="Health",
    product_type="Vitamins",
    derivable=True,
    owners=(("Velling Apothecary", "third_party"), ("Ledwick Botanics", "third_party"),
            ("Mirefield Naturals", "third_party"),
            ("Vitamin C Orchard", "third_party")),
    rows=ROWS,
    decoys=DECOYS,
)
