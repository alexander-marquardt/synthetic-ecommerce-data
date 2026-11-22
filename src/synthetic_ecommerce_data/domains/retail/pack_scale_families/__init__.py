"""One module per family of shapes that :mod:`pack_scale` sizes on its own terms (#1151).

``pack_scale.py`` kept one set of the shapes that draw their own size and one table of the
shapes with their own floor, each with a docstring bullet per family: every feature that taught
a shape to draw its own size added a line to the set and a bullet there, so three PRs of one
week (#1140, #1141, #1148) conflicted on the file. A family is now a module here,
``pack_scale_families/<family>.py``, named as its ``orientations`` module is, which exposes one
or both of:

``SELF_SIZED``
    The shapes whose drawing shows its own size, which take no factor
    (:data:`pack_scale.SELF_SIZED`).
``FLOORS``
    Shape -> its own smallest factor, over :data:`pack_scale.FLOOR`
    (:data:`pack_scale.SHAPE_FLOORS`).

Its docstring says why the family takes no factor or its own floor. Modules are read in the
order of their names. A file here that defines neither is refused, because a file the scale
would skip is a defect nobody sees; so is a shape two modules claim, in either table.
``tests/test_pack_scale_families_1151.py`` holds the contract.
"""

from __future__ import annotations

import importlib
import pkgutil

__all__ = ["tables"]


def tables() -> tuple[frozenset[str], dict[str, float]]:
    """Every family's self-sized shapes and shape floors, read in the order of the module names."""
    self_sized: set[str] = set()
    floors: dict[str, float] = {}
    owner: dict[str, str] = {}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        module = importlib.import_module(f"{__name__}.{info.name}")
        if not hasattr(module, "SELF_SIZED") and not hasattr(module, "FLOORS"):
            raise ValueError(
                f"{module.__name__} defines no SELF_SIZED and no FLOORS: the pack scale would"
                " skip it"
            )
        shapes = [*getattr(module, "SELF_SIZED", ()), *getattr(module, "FLOORS", {})]
        for shape in shapes:
            if shape in owner:
                raise ValueError(f"shape {shape!r} of {module.__name__} is also in {owner[shape]}")
            owner[shape] = module.__name__
        self_sized.update(getattr(module, "SELF_SIZED", ()))
        floors.update(getattr(module, "FLOORS", {}))
    return frozenset(self_sized), floors
