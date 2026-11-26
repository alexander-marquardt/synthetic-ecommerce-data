"""Spec key -> the SKU options that spec declares, one module per family (gen#1183).

``tests/test_retail_type_options_413.py`` checks each spec declares the options listed here. The
rows were one ``MOVED`` dict in that test, so every type that added a SKU option appended a row to
it and any two such PRs conflicted (3 in 7 days). Each family is now a module of this package with
a ``MOVED`` dict; a new family is a new file, found here by its name, and nothing is listed. Options
more than one family uses are in ``_shared.py`` (a leading ``_`` is not a family). A spec key two
families both declare raises and names both.
"""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path

from synthetic_ecommerce_data.domains.retail.type_registry import Option


def _load(folder: Path = Path(__file__).parent, package: str = __name__) -> dict[str, list[Option]]:
    merged: dict[str, list[Option]] = {}
    owner: dict[str, str] = {}
    for info in sorted(pkgutil.iter_modules([str(folder)]), key=lambda i: i.name):
        if info.name.startswith("_"):
            continue
        for key, options in importlib.import_module(f"{package}.{info.name}").MOVED.items():
            if key in owner:
                raise ValueError(f"{key!r}: declared by both {owner[key]} and {info.name}")
            owner[key] = info.name
            merged[key] = options
    return merged


#: The options only spec types carry, by the spec that declares each: spec key -> options.
MOVED: dict[str, list[Option]] = _load()
