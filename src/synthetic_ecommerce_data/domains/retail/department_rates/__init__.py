"""One module per department's derived-style rate, found by walking this package (gen#1044).

The rates were one ``DEPARTMENT_RATE`` table in ``scale.py``, and each PR that adds product types
recomputes one department's rate there, so 8 PRs in 7 days conflicted on it (gen#1044). A
department's rate is now a module here, named for the department
(``department_rates/<department>.py``), which exposes:

``DEPARTMENT``
    The department's name, as a template's ``department`` holds it (``"Food & Drink"``).
``RATE``
    The rate at which each of its templates draws a derived style, before its leaf's weight
    (``scale.rate``): a positive number.

Its docstring holds the department's calibration note: why the rate is what it is, and the PR
that last recomputed it. A rate depends on its department and leaf alone, never on how many
templates there are, so adding one adds its styles and moves no other (gen#626). The figures are
``scale.DEPARTMENT_SHARE`` (the rest by template count) divided by the department's summed leaf
weights at the templates of gen#626; ``tests/test_retail_stable_ids_626.py`` fails when the shares
they give drift more than 10 points, which is the signal to recompute one, in its module here.

A module that lacks either name, whose rate is not a positive number, or that names a department
another module names is refused by :func:`rates`. ``tests/test_department_rates_1044.py`` holds
the contract. A department with no module draws at ``scale.DEFAULT_RATE``.
"""

from __future__ import annotations

import importlib
import pkgutil
from types import ModuleType

__all__ = ["modules", "rates"]


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
