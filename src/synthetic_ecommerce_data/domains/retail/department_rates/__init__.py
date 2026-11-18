"""One module per department's derived-style figures, found by walking this package (gen#1044).

The figures were three tables in ``scale.py`` (``DEPARTMENT_RATE``, ``DEPARTMENT_SHARE`` and
``EXTRA_BRANDS``), and each PR that adds product types recomputes one department's rate there, so
8 PRs in 7 days conflicted on it (gen#1044). A department's figures are now a module here, named
for the department (``department_rates/<department>.py``), which exposes:

``DEPARTMENT``
    The department's name, as a template's ``department`` holds it (``"Food & Drink"``).
``RATE``
    The rate at which each of its templates draws a derived style, before its leaf's weight
    (``scale.rate``): a positive number.
``SHARE`` (optional)
    Its fixed share of derived styles (``scale.department_targets``): a number above 0 and below
    1. The departments with no ``SHARE`` split what the others leave by template count, so the
    shares together stay below 1.
``EXTRA_BRANDS`` (optional)
    Invented brands its derived styles may carry beside its template brands (``scale.brand_pools``):
    a non-empty tuple of non-empty names.

:func:`rates`, :func:`shares` and :func:`extra_brands` build ``scale.DEPARTMENT_RATE``,
``scale.DEPARTMENT_SHARE`` and ``scale.EXTRA_BRANDS`` from the modules, so a new department is one
file here and ``scale.py`` does not change.

Its docstring holds the department's calibration note: why the rate is what it is, and the PR
that last recomputed it. A rate depends on its department and leaf alone, never on how many
templates there are, so adding one adds its styles and moves no other (gen#626). The figures are
``scale.DEPARTMENT_SHARE`` (the rest by template count) divided by the department's summed leaf
weights at the templates of gen#626; ``tests/test_retail_stable_ids_626.py`` fails when the shares
they give drift more than 10 points, which is the signal to recompute one, in its module here.

A module that lacks either name, whose rate is not a positive number, or that names a department
another module names is refused by :func:`rates`; a malformed ``SHARE`` or ``EXTRA_BRANDS``, or
shares that together reach 1, by :func:`shares` and :func:`extra_brands`.
``tests/test_department_rates_1044.py`` holds the contract. A department with no module draws at
``scale.DEFAULT_RATE``. A rate line added back to ``scale.py`` is refused by
``scripts/check_no_registry_append.py``, which names this package.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType

__all__ = ["extra_brands", "modules", "rates", "shares"]


def modules() -> list[ModuleType]:
    """Every module of the package, in the order of their names."""
    return [
        importlib.import_module(f"{__name__}.{info.name}")
        for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name)
    ]


def rates() -> dict[str, float]:
    """Department -> rate, one entry per module; a malformed or repeated one is refused."""
    out: dict[str, float] = {}
    owner: dict[str, str] = {}
    for module in modules():
        department = getattr(module, "DEPARTMENT", None)
        rate = getattr(module, "RATE", None)
        if not isinstance(department, str) or not department:
            raise ValueError(f"{module.__name__} has no DEPARTMENT name")
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not rate > 0:
            raise ValueError(f"{module.__name__} RATE {rate!r} is not a positive number")
        if department in out:
            raise ValueError(
                f"department {department!r} of {module.__name__} is also in {owner[department]}"
            )
        out[department] = float(rate)
        owner[department] = module.__name__
    return out


def shares() -> dict[str, float]:
    """Department -> fixed share, one entry per module with a ``SHARE``; the departments are the
    ones :func:`rates` accepts, and a share outside (0, 1), or shares summing to 1 or more, are
    refused."""
    rates()  # the departments are well formed and named once
    out: dict[str, float] = {}
    for module in modules():
        if not hasattr(module, "SHARE"):
            continue
        share = module.SHARE
        if isinstance(share, bool) or not isinstance(share, (int, float)) or not 0 < share < 1:
            raise ValueError(f"{module.__name__} SHARE {share!r} is not a number in (0, 1)")
        out[module.DEPARTMENT] = float(share)
    if out and not sum(out.values()) < 1:
        raise ValueError(f"the shares sum to {sum(out.values()):g}, leaving nothing to split")
    return out


def extra_brands() -> dict[str, tuple[str, ...]]:
    """Department -> its invented brands, one entry per module with ``EXTRA_BRANDS``; one that
    is not a non-empty tuple of non-empty names is refused."""
    rates()  # the departments are well formed and named once
    out: dict[str, tuple[str, ...]] = {}
    for module in modules():
        if not hasattr(module, "EXTRA_BRANDS"):
            continue
        brands = module.EXTRA_BRANDS
        if (
            not isinstance(brands, tuple)
            or not brands
            or not all(isinstance(b, str) and b for b in brands)
        ):
            raise ValueError(
                f"{module.__name__} EXTRA_BRANDS {brands!r} is not a tuple of brand names"
            )
        out[module.DEPARTMENT] = brands
    return out
