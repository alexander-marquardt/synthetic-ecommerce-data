"""Omega oils: bottles of fish, krill and plant oil softgels, capsules and gummies sold by count
(gen#968, slice 4).

A breadth type (``derivable``) beside the vitamins and minerals: the scaled build draws more
bottles by swapping the oil and the form the title shows. Over the counter only, and no title or
description claims an effect (see ``docs/retail-health.md``). No description names an oil, so a
derived style that swaps the oil says nothing its fields do not.
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import (
    kit_health,  # noqa: F401 -- registers supplement_bottle
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Row, TypeSpec, a, cw

_PATH = ("Health", "Vitamins & Supplements", "Omega Oils")
_SHAPE = "supplement_bottle"
_WHITE = cw("White", "#f4f4f2", "solid", "#2a2a2e")
_AMBER = cw("Amber", "#c98a2e", "solid", "#ffffff")
_SAGE = cw("Sage", "#9bb08f", "solid", "#2a2a2e")
_VELLING, _LEDWICK, _MIREFIELD = "Velling Apothecary", "Ledwick Botanics", "Mirefield Naturals"


def _row(code, title, brand, oil, form, sizes, desc, color=_WHITE) -> Row:  # noqa: ANN001
    return Row(code, title, brand, "Health", _PATH, "Omega Oils", sizes[0][1], _SHAPE, desc,
               (color,), (a("supplement_oil", "Oil type", oil), a("form", "Form", form)), sizes,
               colorless=True, size_key="piece_count",
               params=(("nutrient", oil), ("form", form)))  # fmt: skip


ROWS = (
    _row("OMGFSH", "Fish Oil Softgels", _VELLING, "Fish Oil", "Softgels",
         (("60", 5.0), ("120", 8.5), ("240", 15.0), ("365", 21.0)),
         "One-a-day softgels in a resealable bottle, taken with a meal.", _AMBER),
    _row("OMGCOD", "Cod Liver Oil Capsules", _LEDWICK, "Cod Liver Oil", "Capsules",
         (("30", 3.5), ("90", 8.5), ("180", 15.0)),
         "One-a-day capsules in a resealable bottle, swallowed with water."),
    _row("OMGKRL", "Krill Oil Softgels", _MIREFIELD, "Krill Oil", "Softgels",
         (("30", 9.0), ("60", 16.0), ("120", 28.0)),
         "Small one-a-day softgels in a resealable bottle, taken with a meal.", _SAGE),
    _row("OMGFLX", "Flaxseed Oil Capsules", _MIREFIELD, "Flaxseed Oil", "Capsules",
         (("60", 6.0), ("120", 10.5), ("180", 14.5)),
         "Two capsules a day with food, in a resealable bottle.", _SAGE),
    _row("OMGEPO", "Evening Primrose Oil Softgels", _LEDWICK, "Evening Primrose Oil", "Softgels",
         (("60", 6.5), ("120", 11.0), ("240", 19.0)),
         "One softgel twice a day with water, in a resealable bottle.", _AMBER),
    _row("OMGALG", "Algae Oil Capsules", _VELLING, "Algae Oil", "Capsules",
         (("30", 9.5), ("60", 17.0), ("120", 30.0)),
         "Plant-based one-a-day capsules in a resealable bottle, suitable for vegans."),
    _row("OMGFGM", "Fish Oil Gummies", _MIREFIELD, "Fish Oil", "Gummies",
         (("60", 8.0), ("120", 14.0)),
         "Lemon-flavored chewable gummies in a resealable bottle, two a day.", _SAGE),
    _row("OMGCDS", "Cod Liver Oil Softgels", _VELLING, "Cod Liver Oil", "Softgels",
         (("60", 4.5), ("120", 7.5), ("240", 13.5)),
         "Small one-a-day softgels in a resealable bottle, taken with a meal.", _AMBER),
)  # fmt: skip

#: Text-match decoys (class 6): the title names a range holding the query's oil, the fields say
#: another, so only a policy that reads ``supplement_oil`` puts the real bottles first.
DECOYS = (
    Decoy(6, "krill oil softgels", "generic",
          _row("OMGDY1", "Krill Bay Fish Oil Softgels", _LEDWICK, "Fish Oil", "Softgels",
               (("60", 5.0), ("120", 8.5)),
               "From the Krill Bay range: one-a-day softgels in a resealable bottle.", _AMBER)),
    Decoy(6, "flaxseed oil capsules", "generic",
          _row("OMGDY2", "Flaxseed Fields Cod Liver Oil Capsules", _VELLING, "Cod Liver Oil",
               "Capsules", (("30", 3.5), ("90", 8.5)),
               "From the Flaxseed Fields range: one-a-day capsules in a resealable bottle.")),
)  # fmt: skip

SPEC = TypeSpec(
    key="omega_oils",
    department="Health",
    product_type="Omega Oils",
    derivable=True,
    owners=((_VELLING, "third_party"), (_LEDWICK, "third_party"),
            (_MIREFIELD, "third_party")),
    rows=ROWS,
    decoys=DECOYS,
)
