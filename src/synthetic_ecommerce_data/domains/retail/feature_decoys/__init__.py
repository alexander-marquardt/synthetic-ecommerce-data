"""One module per feature's text-match decoys, found by walking this package (gen#513).

``decoy_rows.py`` (classes 1 to 7, 9 and 10) and ``decoy_product_words.py`` (class 8) were
registries: every feature appended a row to a ``TABLE`` tuple and a ``Kind`` to a ``KINDS`` dict,
so 3 and 4 of the 18 open PRs on 2026-10-18 edited each, and two of them branched from one main
conflicted. A feature's decoys are now a module here, named for the feature
(``feature_decoys/<topic>.py``), which exposes any of:

``KINDS``
    ``{key: decoy_kind.Kind}``: the true types its rows need that no table has yet. A key already
    declared, by the base table or by another module, is refused. A type the build lacks outright
    is a type spec (``docs/new-type-quick-path.md``), not a kind here.
``decoy_rows(d)``
    The class 1 to 10 rows of :mod:`decoy_rows`, made with ``d``, that module's own row maker
    (``d(code, kind, title, desc, color, cls, query, sold=500, **kw)``).
``word_rows(d)``
    The class-8 rows of :mod:`decoy_product_words`, made with its row maker
    (``d(n, kind, title, desc, color, query, noun, policy, **kw)``).

``d`` is passed in, not imported, so a module here imports :mod:`decoy_kind` and nothing of the
tables it feeds (the tables import this package while they are being built). Modules are read in
the order of their names; a row code that a table already holds, or that two modules share, is
refused by :func:`check_unique`. A file here that names none of the three is refused too: a file
the tables would skip is a defect nobody sees. ``tests/test_feature_decoys_513.py`` holds the
contract, and ``scripts/check_no_registry_append.py`` refuses a line appended to the tables.
"""

from __future__ import annotations

import importlib
import pkgutil
from collections.abc import Callable, Iterable, Mapping
from types import ModuleType
from typing import Any

__all__ = ["check_unique", "decoy_rows", "kinds", "modules", "word_rows"]


def modules() -> list[ModuleType]:
    """Every module of the package, in the order of their names."""
    found = []
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda i: i.name):
        module = importlib.import_module(f"{__name__}.{info.name}")
        reads = (
            hasattr(module, "KINDS")
            or callable(getattr(module, "decoy_rows", None))
            or callable(getattr(module, "word_rows", None))
        )
        if not reads:
            raise ValueError(
                f"{module.__name__} defines none of KINDS, decoy_rows(d) and word_rows(d): "
                "the decoy tables would skip it"
            )
        found.append(module)
    return found


def kinds(base: Mapping[str, Any]) -> dict[str, Any]:
    """``base`` and the ``KINDS`` of every module; a key declared twice is refused."""
    merged = dict(base)
    owner: dict[str, str] = {}
    for module in modules():
        for key, kind in getattr(module, "KINDS", {}).items():
            if key in merged:
                where = owner.get(key, "the base table")
                raise ValueError(f"kind {key!r} of {module.__name__} is also in {where}")
            merged[key] = kind
            owner[key] = module.__name__
    return merged


def _rows(attribute: str, make: Callable[..., Any]) -> tuple[Any, ...]:
    out: list[Any] = []
    for module in modules():
        build = getattr(module, attribute, None)
        if callable(build):
            out.extend(build(make))
    return tuple(out)


def decoy_rows(make: Callable[..., Any]) -> tuple[Any, ...]:
    """The rows of :mod:`decoy_rows` that the modules declare, in module order."""
    return _rows("decoy_rows", make)


def word_rows(make: Callable[..., Any]) -> tuple[Any, ...]:
    """The class-8 rows of :mod:`decoy_product_words` that the modules declare, in module order."""
    return _rows("word_rows", make)


def check_unique(codes: Iterable[str], table: str) -> None:
    """Refuse a row code that ``table`` holds twice: the id of a row is its code."""
    seen: set[str] = set()
    for code in codes:
        if code in seen:
            raise ValueError(f"{table}: the row code {code} appears twice")
        seen.add(code)
