"""Minerals: bottles of mineral tablets and capsules sold by count, beside the vitamins in Health.

A breadth type (``derivable``): the scaled build draws more bottles by swapping the mineral and the
form the title shows. Over the counter only, and no title or description claims an effect
(see ``docs/retail-health.md``).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health,  # noqa: F401 -- registers supplement_bottle
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Health", "Vitamins & Supplements", "Minerals")
#: The capped bottle of kit_health (gen#1028), not the retail tub, which drew a cup.
_SHAPE = "supplement_bottle"
_WHITE = cw("White", "#f4f4f2", "solid", "#2a2a2e")
_AMBER = cw("Amber", "#c98a2e", "solid", "#ffffff")
_SAGE = cw("Sage", "#9bb08f", "solid", "#2a2a2e")
#: The "Iron Grey Bottle" decoy's own color: its title names it.
_GREY = cw("Grey", "#8d9399", "solid", "#ffffff")


def _drawn(mineral: str, form: str) -> tuple[tuple[str, str], ...]:
    """The bottle's params: its label names the mineral and draws the form (gen#1028)."""
    return (("nutrient", mineral), ("form", form))


def _row(code, title, brand, mineral, form, sizes, desc, color=_WHITE) -> Row:  # noqa: ANN001
    return Row(code, title, brand, "Health", _PATH, "Minerals", sizes[0][1], _SHAPE, desc,
               (color,), (a("mineral", "Mineral", mineral), a("form", "Form", form)), sizes,
               colorless=True, size_key="piece_count", params=_drawn(mineral, form))  # fmt: skip


ROWS = (
    _row("MINZNC", "Zinc Tablets", "Velling Apothecary", "Zinc", "Tablets",
         (("30", 3.0), ("90", 7.0)),
         "Small one-a-day tablets in a resealable bottle, vegan and free from gelatin."),
    _row("MINMAG", "Magnesium Tablets", "Ledwick Botanics", "Magnesium", "Tablets",
         (("60", 5.5), ("120", 9.5)),
         "Two tablets a day with food, in a resealable bottle.", _AMBER),
    _row("MINIRN", "Iron Tablets", "Mirefield Naturals", "Iron", "Tablets",
         (("30", 3.5), ("90", 8.0)),
         "Gentle one-a-day tablets in a resealable bottle, taken with water.", _SAGE),
    _row("MINCAL", "Calcium Tablets", "Velling Apothecary", "Calcium", "Tablets",
         (("60", 4.5), ("120", 8.0)),
         "Two tablets a day with a meal, in a resealable bottle."),
    _row("MINSEL", "Selenium Capsules", "Ledwick Botanics", "Selenium", "Capsules",
         (("30", 4.0), ("90", 9.0)),
         "Small one-a-day capsules in a resealable bottle, suitable for vegans.", _AMBER),
    _row("MINMGC", "Magnesium Capsules", "Mirefield Naturals", "Magnesium", "Capsules",
         (("60", 6.0), ("120", 10.5)),
         "Two capsules a day with food, in a resealable bottle.", _SAGE),
    _row("MINPOT", "Potassium Tablets", "Velling Apothecary", "Potassium", "Tablets",
         (("60", 5.0), ("120", 9.0)),
         "Two tablets a day with a meal, in a resealable bottle."),
    _row("MINCHR", "Chromium Tablets", "Velling Apothecary", "Chromium", "Tablets",
         (("30", 3.5), ("90", 8.0)),
         "Small one-a-day tablets in a resealable bottle, taken with water."),
    _row("MINIOD", "Iodine Tablets", "Ledwick Botanics", "Iodine", "Tablets",
         (("30", 3.0), ("90", 7.0)),
         "One-a-day tablets in a resealable bottle, suitable for vegans.", _AMBER),
    _row("MINMNG", "Manganese Tablets", "Mirefield Naturals", "Manganese", "Tablets",
         (("60", 4.5), ("120", 8.0)),
         "One-a-day tablets in a resealable bottle, swallowed with water.", _SAGE),
    _row("MINZCP", "Zinc Capsules", "Ledwick Botanics", "Zinc", "Capsules",
         (("30", 3.5), ("90", 8.0)),
         "Small one-a-day capsules in a resealable bottle, vegan and free from gelatin."),
    _row("MINBOR", "Boron Tablets", "Mirefield Naturals", "Boron", "Tablets",
         (("60", 4.0), ("120", 7.0)),
         "One-a-day tablets in a resealable bottle, swallowed with water.", _SAGE),
    _row("MINMOL", "Molybdenum Tablets", "Velling Apothecary", "Molybdenum", "Tablets",
         (("30", 3.5), ("90", 8.0)),
         "Small one-a-day tablets in a resealable bottle, taken with a meal."),
    _row("MINSIL", "Silica Capsules", "Ledwick Botanics", "Silica", "Capsules",
         (("30", 4.5), ("90", 10.0)),
         "One-a-day capsules in a resealable bottle, suitable for vegans.", _AMBER),
)

#: Text-match decoys (classes 4 and 6): a title holds the query's mineral, the fields say zinc
#: or magnesium, so only a policy that reads the mineral puts them below the real bottles.
DECOYS = (
    Decoy(4, "iron tablets", "vocabulary",
          Row("MINDY1", "Iron Grey Bottle Zinc Tablets", "Velling Apothecary", "Health", _PATH,
              "Minerals", 3.0, _SHAPE, "Zinc tablets in an iron-grey bottle.", (_GREY,),
              (a("mineral", "Mineral", "Zinc"), a("form", "Form", "Tablets")),
              (("30", 3.0), ("90", 7.0)), colorless=True, size_key="piece_count",
              params=_drawn("Zinc", "Tablets"))),
    Decoy(6, "iron tablets", "generic",
          Row("MINDY2", "Iron Gate Magnesium Tablets", "Ledwick Botanics", "Health", _PATH,
              "Minerals", 5.5, _SHAPE, "From the Iron Gate range: magnesium tablets.", (_SAGE,),
              (a("mineral", "Mineral", "Magnesium"), a("form", "Form", "Tablets")),
              (("60", 5.5), ("120", 9.5)), colorless=True, size_key="piece_count",
              params=_drawn("Magnesium", "Tablets"))),
    Decoy(4, "calcium tablets", "vocabulary",
          Row("MINDY3", "Calcium White Bottle Zinc Tablets", "Mirefield Naturals", "Health", _PATH,
              "Minerals", 3.0, _SHAPE, "Zinc tablets in a calcium-white bottle.", (_WHITE,),
              (a("mineral", "Mineral", "Zinc"), a("form", "Form", "Tablets")),
              (("30", 3.0), ("90", 7.0)), colorless=True, size_key="piece_count",
              params=_drawn("Zinc", "Tablets"))),
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
