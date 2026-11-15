"""The store's departments: the closed list of top levels of every ``category_path`` (gen#125).

Slice 3 of the 2026-10-28 ruling on #125. **The department is the top level of
``category_path``, for every domain; there is no ``department`` field** (gen#281): a second
home for a fact the path already states would be a second source of truth. A department exists
so that a policy can target it, which is why the list is closed and lives here, in core:
:func:`.standard.check_document` refuses a ``category_path`` or a ``category_paths`` entry whose
top level is not on it, whatever domain wrote the document.

A domain files each of its products under one of its own departments: retail's tree starts at
them (``Womens``, ``Food & drink``), and industrial files each of its roots under one by one
table, ``domains/industrial/taxonomy.DEPARTMENT_OF`` (``Milling`` sits in ``Tools``). The
names are the published spelling, sentence case (gen#499, gen#516). Renaming one is a change
here and in the domain that files under it, and every consumer's category vocabulary follows.
"""

from __future__ import annotations

#: The retail store's departments (gen#281).
RETAIL = (
    "Womens",
    "Mens",
    "Kids",
    "Food & drink",
    "Home",
    "Beauty",
    "Cleaning",
    "Toys",
    "Gifts",
    "Garden",
    "Sports & outdoors",
    "Electronics",
    "Health",
    "Office & school",
)

#: The industrial supplier's departments: the maintainer's three (2026-10-13), first kept as
#: ``INDUSTRIAL_DEPARTMENTS`` in the catalogue repository's ``combined_catalog.py``.
INDUSTRIAL = (
    "Hardware",
    "Tools",
    "Workshop & safety",
)

#: Every value the top level of a ``category_path`` may hold.
DEPARTMENTS = frozenset({*RETAIL, *INDUSTRIAL})
