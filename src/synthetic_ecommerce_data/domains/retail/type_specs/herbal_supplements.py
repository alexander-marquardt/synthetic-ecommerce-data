"""Herbal supplements: bottles of herb tablets, capsules, softgels and gummies sold by count (gen#968,
slice 4).

A breadth type (``derivable``) beside the vitamins and minerals: the scaled build draws more
bottles by swapping the herb and the form the title shows. Over the counter only, and no title or
description claims an effect (see ``docs/retail-health.md``): a description says what is in the
bottle and how many to take, never what it does.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health,  # noqa: F401 -- registers supplement_bottle
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Health", "Vitamins & Supplements", "Herbal Supplements")
_SHAPE = "supplement_bottle"
_WHITE = cw("White", "#f4f4f2", "solid", "#2a2a2e")
_AMBER = cw("Amber", "#c98a2e", "solid", "#ffffff")
_SAGE = cw("Sage", "#9bb08f", "solid", "#2a2a2e")
_VELLING, _LEDWICK, _MIREFIELD = "Velling Apothecary", "Ledwick Botanics", "Mirefield Naturals"


def _row(code, title, brand, herb, form, sizes, desc, color=_WHITE) -> Row:  # noqa: ANN001
    return Row(code, title, brand, "Health", _PATH, "Herbal Supplements", sizes[0][1], _SHAPE,
               desc, (color,), (a("herb", "Herb", herb), a("form", "Form", form)), sizes,
               colorless=True, size_key="piece_count",
               params=(("nutrient", herb), ("form", form)))  # fmt: skip


ROWS = (
    _row("HRBTUR", "Turmeric Capsules", _LEDWICK, "Turmeric", "Capsules",
         (("60", 7.0), ("120", 12.0), ("180", 16.5)),
         "Two capsules a day with food, in a resealable bottle, vegan and free from gelatin.", _AMBER),
    _row("HRBECH", "Echinacea Tablets", _MIREFIELD, "Echinacea", "Tablets",
         (("30", 5.0), ("60", 8.5), ("120", 14.5)),
         "One-a-day tablets in a resealable bottle, swallowed with water.", _SAGE),
    _row("HRBGIN", "Ginseng Capsules", _VELLING, "Ginseng", "Capsules",
         (("30", 6.5), ("90", 15.0), ("180", 26.0)),
         "One-a-day capsules in a resealable bottle, taken with a meal."),
    _row("HRBGKG", "Ginkgo Tablets", _LEDWICK, "Ginkgo", "Tablets",
         (("60", 6.0), ("120", 10.5), ("240", 18.0)),
         "Small one-a-day tablets in a resealable bottle, suitable for vegans."),
    _row("HRBMLK", "Milk Thistle Capsules", _MIREFIELD, "Milk Thistle", "Capsules",
         (("60", 7.5), ("120", 13.0), ("180", 17.5)),
         "One capsule twice a day with water, in a resealable bottle.", _SAGE),
    _row("HRBGAR", "Garlic Softgels", _VELLING, "Garlic", "Softgels",
         (("60", 4.5), ("120", 7.5), ("240", 13.0)),
         "Odorless one-a-day softgels in a resealable bottle, taken with a meal.", _AMBER),
    _row("HRBELD", "Elderberry Gummies", _MIREFIELD, "Elderberry", "Gummies",
         (("30", 6.0), ("60", 10.0), ("120", 17.0)),
         "Berry-flavored chewable gummies in a resealable bottle, two a day.", _SAGE),
    _row("HRBGNG", "Ginger Capsules", _LEDWICK, "Ginger", "Capsules",
         (("60", 5.5), ("120", 9.5), ("180", 13.0)),
         "Two capsules a day with food, in a resealable bottle, vegan and free from gelatin."),
    _row("HRBASH", "Ashwagandha Capsules", _VELLING, "Ashwagandha", "Capsules",
         (("60", 8.0), ("120", 14.0), ("180", 19.0)),
         "Two capsules a day with water, in a resealable bottle.", _AMBER),
    _row("HRBVAL", "Valerian Tablets", _LEDWICK, "Valerian", "Tablets",
         (("30", 5.0), ("60", 8.5), ("120", 14.0)),
         "One tablet in the evening, in a resealable bottle, swallowed with water.", _SAGE),
    _row("HRBRHO", "Rhodiola Capsules", _MIREFIELD, "Rhodiola", "Capsules",
         (("30", 7.0), ("60", 12.0), ("120", 20.5)),
         "One-a-day capsules in a resealable bottle, taken in the morning."),
    _row("HRBCRN", "Cranberry Capsules", _VELLING, "Cranberry", "Capsules",
         (("60", 6.5), ("120", 11.0), ("180", 15.0)),
         "One-a-day capsules in a resealable bottle, suitable for vegans.", _AMBER),
    _row("HRBTRG", "Turmeric Gummies", _VELLING, "Turmeric", "Gummies",
         (("60", 8.0), ("120", 14.0)),
         "Orange-flavored chewable gummies in a resealable bottle, two a day."),
    _row("HRBASG", "Ashwagandha Gummies", _LEDWICK, "Ashwagandha", "Gummies",
         (("60", 9.0), ("120", 15.5)),
         "Strawberry-flavored chewable gummies in a resealable bottle, two a day.", _AMBER),
)  # fmt: skip

#: Text-match decoys (classes 4 and 6): a title holds the query's herb as a range or bottle word,
#: the fields say another herb, so only a policy that reads ``herb`` puts the real bottles first.
DECOYS = (
    Decoy(6, "garlic capsules", "generic",
          _row("HRBDY1", "Garlic Lane Turmeric Capsules", _LEDWICK, "Turmeric", "Capsules",
               (("60", 7.0), ("120", 12.0)),
               "From the Garlic Lane range: turmeric capsules in a resealable bottle.", _AMBER)),
    Decoy(4, "ginger tablets", "vocabulary",
          _row("HRBDY2", "Ginger Cap Bottle Echinacea Tablets", _MIREFIELD, "Echinacea",
               "Tablets", (("30", 5.0), ("60", 8.5)),
               "Echinacea tablets in a bottle with a ginger-colored cap.", _SAGE)),
)  # fmt: skip

SPEC = TypeSpec(
    key="herbal_supplements",
    department="Health",
    product_type="Herbal Supplements",
    derivable=True,
    owners=((_VELLING, "third_party"), (_LEDWICK, "third_party"),
            (_MIREFIELD, "third_party")),
    rows=ROWS,
    decoys=DECOYS,
)
