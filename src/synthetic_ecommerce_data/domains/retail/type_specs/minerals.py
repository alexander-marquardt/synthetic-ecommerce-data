"""Minerals: tubs of mineral tablets and capsules sold by count, beside the vitamins in Health.

A breadth type (``derivable``): the scaled build draws more tubs by swapping the mineral and the
form the title shows. Over the counter only, and no title or description claims an effect
(see ``docs/retail-health.md``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Health", "Vitamins & Supplements", "Minerals")
_WHITE = cw("White", "#f4f4f2", "solid", "#2a2a2e")
_AMBER = cw("Amber", "#c98a2e", "solid", "#ffffff")
_SAGE = cw("Sage", "#9bb08f", "solid", "#2a2a2e")


def _row(code, title, brand, mineral, form, sizes, desc, color=_WHITE) -> Row:  # noqa: ANN001
    return Row(code, title, brand, "Health", _PATH, "Minerals", sizes[0][1], "tub", desc,
               (color,), (a("mineral", "Mineral", mineral), a("form", "Form", form)), sizes,
               colorless=True, size_key="piece_count")  # fmt: skip


ROWS = (
    _row("MINZNC", "Zinc Tablets", "Velling Apothecary", "Zinc", "Tablets",
         (("30", 3.0), ("90", 7.0)),
         "Small one-a-day tablets in a resealable tub, vegan and free from gelatin."),
    _row("MINMAG", "Magnesium Tablets", "Ledwick Botanics", "Magnesium", "Tablets",
         (("60", 5.5), ("120", 9.5)),
         "Two tablets a day with food, in a resealable tub.", _AMBER),
    _row("MINIRN", "Iron Tablets", "Mirefield Naturals", "Iron", "Tablets",
         (("30", 3.5), ("90", 8.0)),
         "Gentle one-a-day tablets in a resealable tub, taken with water.", _SAGE),
    _row("MINCAL", "Calcium Tablets", "Velling Apothecary", "Calcium", "Tablets",
         (("60", 4.5), ("120", 8.0)),
         "Two tablets a day with a meal, in a resealable tub."),
    _row("MINSEL", "Selenium Capsules", "Ledwick Botanics", "Selenium", "Capsules",
         (("30", 4.0), ("90", 9.0)),
         "Small one-a-day capsules in a resealable tub, suitable for vegans.", _AMBER),
    _row("MINMGC", "Magnesium Capsules", "Mirefield Naturals", "Magnesium", "Capsules",
         (("60", 6.0), ("120", 10.5)),
         "Two capsules a day with food, in a resealable tub.", _SAGE),
    _row("MINPOT", "Potassium Tablets", "Velling Apothecary", "Potassium", "Tablets",
         (("60", 5.0), ("120", 9.0)),
         "Two tablets a day with a meal, in a resealable tub."),
    _row("MINCHR", "Chromium Tablets", "Velling Apothecary", "Chromium", "Tablets",
         (("30", 3.5), ("90", 8.0)),
         "Small one-a-day tablets in a resealable tub, taken with water."),
    _row("MINIOD", "Iodine Tablets", "Ledwick Botanics", "Iodine", "Tablets",
         (("30", 3.0), ("90", 7.0)),
         "One-a-day tablets in a resealable tub, suitable for vegans.", _AMBER),
    _row("MINMNG", "Manganese Tablets", "Mirefield Naturals", "Manganese", "Tablets",
         (("60", 4.5), ("120", 8.0)),
         "One-a-day tablets in a resealable tub, swallowed with water.", _SAGE),
    _row("MINZCP", "Zinc Capsules", "Ledwick Botanics", "Zinc", "Capsules",
         (("30", 3.5), ("90", 8.0)),
         "Small one-a-day capsules in a resealable tub, vegan and free from gelatin."),
    _row("MINBOR", "Boron Tablets", "Mirefield Naturals", "Boron", "Tablets",
         (("60", 4.0), ("120", 7.0)),
         "One-a-day tablets in a resealable tub, swallowed with water.", _SAGE),
    _row("MINMOL", "Molybdenum Tablets", "Velling Apothecary", "Molybdenum", "Tablets",
         (("30", 3.5), ("90", 8.0)),
         "Small one-a-day tablets in a resealable tub, taken with a meal."),
    _row("MINSIL", "Silica Capsules", "Ledwick Botanics", "Silica", "Capsules",
         (("30", 4.5), ("90", 10.0)),
         "One-a-day capsules in a resealable tub, suitable for vegans.", _AMBER),
)

#: Text-match decoys (classes 4 and 6): a title holds the query's mineral, the fields say zinc
#: or magnesium, so only a policy that reads the mineral puts them below the real tubs.
DECOYS = (
    Decoy(4, "iron tablets", "vocabulary",
          Row("MINDY1", "Iron Grey Tub Zinc Tablets", "Velling Apothecary", "Health", _PATH,
              "Minerals", 3.0, "tub", "Zinc tablets in an iron-grey tub.", (_WHITE,),
              (a("mineral", "Mineral", "Zinc"), a("form", "Form", "Tablets")),
              (("30", 3.0), ("90", 7.0)), colorless=True, size_key="piece_count")),
    Decoy(6, "iron tablets", "generic",
          Row("MINDY2", "Iron Gate Magnesium Tablets", "Ledwick Botanics", "Health", _PATH,
              "Minerals", 5.5, "tub", "From the Iron Gate range: magnesium tablets.", (_AMBER,),
              (a("mineral", "Mineral", "Magnesium"), a("form", "Form", "Tablets")),
              (("60", 5.5), ("120", 9.5)), colorless=True, size_key="piece_count")),
    Decoy(4, "calcium tablets", "vocabulary",
          Row("MINDY3", "Calcium White Tub Zinc Tablets", "Mirefield Naturals", "Health", _PATH,
              "Minerals", 3.0, "tub", "Zinc tablets in a calcium-white tub.", (_SAGE,),
              (a("mineral", "Mineral", "Zinc"), a("form", "Form", "Tablets")),
              (("30", 3.0), ("90", 7.0)), colorless=True, size_key="piece_count")),
)  # fmt: skip

SPEC = TypeSpec(
    key="minerals",
    department="Health",
    product_type="Minerals",
    derivable=True,
    owners=(("Velling Apothecary", "third_party"), ("Ledwick Botanics", "third_party"),
            ("Mirefield Naturals", "third_party")),
    rows=ROWS,
    decoys=DECOYS,
)
