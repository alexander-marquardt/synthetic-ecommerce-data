"""Breadth templates for the scaled retail catalog (gen#125): data only.

:func:`scale.templates` builds these after :mod:`scale_rows`. The authored styles and
the deep-SKU rows left a general-retail catalog thin outside clothing and lingerie: at
the ceiling, toys, garden, gifts and cleaning held under 1% of the styles each, and
food and beauty under 5%. These rows give each thin department leaves of its own, so
that every department holds at least :data:`DEPARTMENT_FLOOR` styles at the ceiling
(``tests/test_retail_scale.py`` pins it).

A row adds capacity through a title-visible value its leaf varies (:func:`scale.value_pools`):
a fabric, a fragrance, a variety, an occasion. Every value of a leaf's pool fits every
template of that leaf, so a derived style stays coherent: a knitted whale and a corduroy
cat are both soft toys, and a variety is a variety of the leaf's one plant. The drawing
shows what never varies (the animal, the bottle, the tree).
"""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_34 import (
    BREADTH_34,
    Contents,  # noqa: F401 -- read through this module
    _a1,  # noqa: F401 -- read through this module
    _in,  # noqa: F401 -- read through this module
    _volts,  # noqa: F401 -- read through this module
)
from synthetic_ecommerce_data.domains.retail.breadth_beauty import BEAUTY
from synthetic_ecommerce_data.domains.retail.breadth_cleaning import _CJ, CLEANING
from synthetic_ecommerce_data.domains.retail.breadth_food import _FD, FOOD
from synthetic_ecommerce_data.domains.retail.breadth_garden import GARDEN
from synthetic_ecommerce_data.domains.retail.breadth_gifts import GIFTS
from synthetic_ecommerce_data.domains.retail.breadth_home import HOME
from synthetic_ecommerce_data.domains.retail.breadth_row import (
    OWNERS,  # noqa: F401 -- read through this module
    Row,  # noqa: F401 -- read through this module
    paint_range,  # noqa: F401 -- read through this module
)
from synthetic_ecommerce_data.domains.retail.breadth_toys import TOYS

#: The fewest derivable styles any department holds at the ceiling build (gen#220). It is a
#: count of the department's own, not a share of the total: a batch that grows one department
#: (the Home types of gen#196-#217) moves no other department's standing, so it needs no
#: filler rows elsewhere. The smallest department at the ceiling holds 212 (Beauty);
#: dropping half of any thin department's rows here leaves it with 64 to 116.
DEPARTMENT_FLOOR = 150


#: Every breadth row, by department.
DEPARTMENTS = {
    "Toys": TOYS, "Garden": GARDEN, "Gifts": GIFTS, _CJ: CLEANING, _FD: FOOD, "Beauty": BEAUTY,
    "Home": HOME,
}  # fmt: skip


def docs() -> list[dict]:
    """Every breadth row's catalog document, department by department, then the tableware
    and kitchen utensil rows (:mod:`tableware_rows`, gen#198), then the furniture
    (:mod:`furniture_rows`, gen#199); both build on :class:`Row`, so each is imported here
    (deferred: a top-level import would be a cycle)."""
    from synthetic_ecommerce_data.domains.retail import furniture_rows, tableware_rows

    rows = (*(r for rows in DEPARTMENTS.values() for r in rows), *BREADTH_34, *tableware_rows.ROWS)
    return [*(r.doc() for r in rows), *furniture_rows.docs()]
