"""A row's ``brand_owner`` is the same whatever the interpreter imported first (gen#1039).

``Row.doc()`` read a brand's owner from ``breadth_row.OWNERS``, which about twenty modules fill
when they are imported. So a row's document depended on import order: in a fresh interpreter
``electronics_rows.LAPTOPS[0].doc()`` raised ``KeyError: 'Halvern'``, and gave ``third_party``
once ``type_registry.specs()`` had run. A test passed or failed by which test files shared its
CI worker (``tests (12)`` of synth#1020). ``brand_owners.table()`` imports every module that
states owners before it answers. These checks run in fresh interpreters, one per first import,
so nothing an earlier test imported can fill the table for them.
"""

from __future__ import annotations

import functools
import json
import subprocess
import sys

#: The row modules whose rows raised ``KeyError`` when imported alone on main (gen#1039).
ROW_MODULES = ("automotive_rows", "electronics_rows", "knacks_rows", "outerwear_rows")

#: Imports ``FIRST`` alone, then prints the ``brand_owner`` (or the error) of every module-level
#: row of ``ROW_MODULES`` and of every spec.
PROBE = """
import importlib, json, sys
P = "synthetic_ecommerce_data.domains.retail"
importlib.import_module(P + "." + sys.argv[1])
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail import type_registry

def rows(mod):
    for val in vars(mod).values():
        items = val.values() if isinstance(val, dict) else val
        items = items if isinstance(items, (list, tuple, type({}.values()))) else [val]
        yield from (r for r in items if isinstance(r, Row))

def owner(row):
    try:
        return row.doc()["brand_owner"]
    except Exception as exc:
        return f"{type(exc).__name__}: {exc}"

out = {}
for name in json.loads(sys.argv[2]):
    for r in rows(importlib.import_module(P + "." + name)):
        out[f"{name} {r.code}"] = owner(r)
for key, spec in type_registry.specs().items():
    for r in [*spec.rows, *(d.row for d in spec.decoys)]:
        out[f"{key} {r.code}"] = owner(r)
print(json.dumps({"rows": out}, sort_keys=True))
"""


def _probe(first: str) -> dict:
    done = subprocess.run(
        [sys.executable, "-c", PROBE, first, json.dumps(ROW_MODULES)],
        capture_output=True, text=True, timeout=300, check=False,
    )  # fmt: skip
    assert done.returncode == 0, done.stderr[-2000:]
    return json.loads(done.stdout)


@functools.cache
def baseline() -> dict:
    """The answer after importing the base table first: the order nothing else fills."""
    return _probe("breadth_row")


def test_no_row_of_the_import_order_modules_or_any_spec_raises() -> None:
    failed = {k: v for k, v in baseline()["rows"].items() if v not in ("own", "third_party")}
    assert failed == {}
    assert {k.split()[0] for k in baseline()["rows"]} >= set(ROW_MODULES)
