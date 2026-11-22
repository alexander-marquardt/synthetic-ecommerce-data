"""Every module-level retail row sells an owned brand, checked before any ``doc()`` (gen#1039).

``type_registry.validate`` names a spec row whose brand has no owner. A module-level
:class:`~synthetic_ecommerce_data.domains.retail.breadth_row.Row` of an older row module had no
such check: its missing owner was a ``KeyError`` from the first ``doc()`` call, on whichever CI
worker built that row. :func:`check` imports every module of the retail package itself, so its
answer does not depend on what the interpreter imported first, and names every module-level row
(bare, or in a tuple, list, set or dict) whose brand :func:`brand_owners.table` does not own.
``scale.templates()`` runs it before it builds any document. ``tests/test_owned_rows_1039.py``.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Iterator

from synthetic_ecommerce_data.domains.retail import brand_owners
from synthetic_ecommerce_data.domains.retail.breadth_row import Row

_PACKAGE = __name__.rpartition(".")[0]

#: How deep a module-level value's containers are searched for rows: a tuple of rows is depth 1,
#: a dict of tuples of rows depth 2.
_DEPTH = 3


class UnownedBrand(ValueError):
    """A module-level row sells a brand :func:`brand_owners.table` does not own."""


def _found(value: object, depth: int) -> Iterator[Row]:
    if isinstance(value, Row):
        yield value
        return
    if depth == 0:
        return
    if isinstance(value, dict):
        value = value.values()
    if isinstance(value, (tuple, list, set, frozenset, type({}.values()))):
        for item in value:
            yield from _found(item, depth - 1)


def rows() -> Iterator[tuple[str, Row]]:
    """``(module, row)`` for every module-level row of every retail module, the module named
    relative to the retail package (``type_specs.granola``)."""
    package = importlib.import_module(_PACKAGE)
    for info in pkgutil.walk_packages(package.__path__, f"{_PACKAGE}."):
        module = importlib.import_module(info.name)
        name = info.name.removeprefix(f"{_PACKAGE}.")
        for value in vars(module).values():
            for row in _found(value, _DEPTH):
                yield name, row


def unowned() -> list[str]:
    """``"<module> <code> sells '<brand>'"`` for each module-level row whose brand has no owner."""
    owners = brand_owners.table()
    return sorted(
        {f"{module} {row.code} sells {row.brand!r}" for module, row in rows()
         if row.brand not in owners}
    )  # fmt: skip


def check() -> None:
    """Raise :class:`UnownedBrand` naming every module-level row whose brand has no owner."""
    if problems := unowned():
        raise UnownedBrand("a row sells a brand with no owner: " + "; ".join(problems))
