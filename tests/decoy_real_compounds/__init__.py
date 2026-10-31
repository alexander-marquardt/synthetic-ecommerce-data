"""Titles a class 2 apparel decoy may use, one module per topic (gen#513).

``REAL_COMPOUNDS`` in ``test_retail_apparel_decoys_311.py`` is the hand list of real retail terms
a class 2 title must come from. A list read from the decoy table would pass any invented term, so
it stays by hand; but it was one literal, so two features that added a term conflicted. A new term
is a ``COMPOUNDS`` frozenset in a module here, found by its file, and nothing is listed.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path


def load(folder: Path = Path(__file__).parent, package: str = __name__) -> frozenset[str]:
    """The ``COMPOUNDS`` of every module in ``folder``; a module that names none is refused."""
    merged: set[str] = set()
    for path in sorted(folder.glob("*.py")):
        if path.name == "__init__.py":
            continue
        spec = importlib.util.spec_from_file_location(f"{package}.{path.stem}", path)
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        compounds = getattr(module, "COMPOUNDS", None)
        if not compounds:
            raise ValueError(f"{path.stem} names no COMPOUNDS: the decoy test would skip it")
        merged |= compounds
    return frozenset(merged)


FEATURE_COMPOUNDS: frozenset[str] = load()
