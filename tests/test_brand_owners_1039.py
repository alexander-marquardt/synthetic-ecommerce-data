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
import re
import subprocess
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.domains.retail import brand_owners

RETAIL = Path(brand_owners.__file__).parent

#: The row modules whose rows raised ``KeyError`` when imported alone on main (gen#1039).
ROW_MODULES = ("automotive_rows", "electronics_rows", "knacks_rows", "outerwear_rows")

#: Imports ``FIRST`` alone, then prints the ``brand_owner`` (or the error) of every module-level
#: row of ``ROW_MODULES`` and of every spec, and the whole owner table.
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
table = dict(importlib.import_module(P + ".brand_owners").table())
print(json.dumps({"rows": out, "table": table}, sort_keys=True))
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


@pytest.mark.parametrize("first", [*brand_owners.SOURCES, *ROW_MODULES, "type_registry"])
def test_brand_owner_is_the_same_whatever_was_imported_first(first: str) -> None:
    got = _probe(first)
    assert got["rows"] == baseline()["rows"]
    assert got["table"] == baseline()["table"]


#: A line that adds to the breadth ``OWNERS`` dict: ``OWNERS.update(``, ``OWNERS.setdefault(``
#: or ``OWNERS[brand] = ``.
WRITE = re.compile(r"\bOWNERS(\.update\(|\.setdefault\(|\[[^]]+\]\s*=[^=])")

#: A module-level ``OWNED = ...`` (or ``OWNED: ... = ...``): the brands a module states.
STATES = re.compile(r"^OWNED\b\s*(:[^=]+)?=", re.M)


def test_no_module_writes_the_owner_table() -> None:
    """A write at import time makes the table hold only what this interpreter imported, and a
    first-wins or last-wins write hides two modules that disagree on an owner (gen#1039)."""
    src = RETAIL.parents[1]
    writes = [
        f"{p.relative_to(src)}:{n}"
        for p in sorted(src.rglob("*.py"))
        for n, line in enumerate(p.read_text().splitlines(), 1)
        if WRITE.search(line)
    ]
    assert writes == []


def test_every_module_that_states_owners_is_a_source_of_the_table() -> None:
    """A module whose ``OWNED`` is not in ``SOURCES`` would leave its brands out of ``table()``,
    and a source with no ``OWNED`` names nothing. Spec modules are walked for ``SPEC.owners``."""
    stating = {p.stem for p in RETAIL.glob("*.py") if STATES.search(p.read_text())}
    assert stating, "the pattern found no module: it no longer matches how modules state owners"
    assert sorted(stating - set(brand_owners.SOURCES)) == []
    assert sorted(set(brand_owners.SOURCES) - stating) == []


def test_two_sources_that_disagree_on_a_brand_raise_naming_both() -> None:
    """A brand two sources give different owners is an error, never a silent first or last win:
    ``beach_towel`` stated ``Harbour & Pine`` as third party while every other source said own."""
    sources = (
        ("breadth_row", (("Harbour & Pine", "own"), ("Larkmoor", "own"))),
        ("spec:beach_towel", (("Harbour & Pine", "third_party"),)),
    )
    try:
        brand_owners.merge(sources)
    except brand_owners.OwnerConflict as exc:
        said = str(exc)
    else:
        said = "no error"
    assert "Harbour & Pine" in said
    assert "breadth_row" in said
    assert "spec:beach_towel" in said


def test_two_sources_that_agree_on_a_brand_merge() -> None:
    sources = (
        ("a", (("Larkmoor", "own"),)),
        ("b", (("Larkmoor", "own"), ("Soapwell", "third_party"))),
    )
    assert brand_owners.merge(sources) == {"Larkmoor": "own", "Soapwell": "third_party"}


#: Validates a copy of the ``plasters`` spec whose one row sells ``Tallow Street``, a brand only
#: ``knacks_rows`` states and which nothing the registry imports has stated yet.
VALIDATE = """
import dataclasses, importlib
from synthetic_ecommerce_data.domains.retail import type_registry
from synthetic_ecommerce_data.domains.retail.breadth_row import OWNERS
spec = importlib.import_module("synthetic_ecommerce_data.domains.retail.type_specs.plasters").SPEC
assert "Tallow Street" not in OWNERS, "pick a brand no imported module states yet"
row = dataclasses.replace(spec.rows[0], brand="Tallow Street")
type_registry.validate(dataclasses.replace(spec, rows=(row,), decoys=(), owners=()))
print("ok")
"""


def test_validate_knows_a_brand_whose_module_was_not_imported_yet() -> None:
    """``type_registry.validate`` checks a spec's brands against every owner module, so whether a
    spec passes does not depend on which modules ran before it (gen#1039)."""
    done = subprocess.run(
        [sys.executable, "-c", VALIDATE], capture_output=True, text=True, timeout=300, check=False
    )
    assert done.returncode == 0, done.stderr[-2000:]
    assert done.stdout.strip() == "ok"


def test_the_table_imports_every_source_itself() -> None:
    """Today the specs import most sources, and the brands the others state are stated elsewhere
    too, so a table built from fewer sources looks the same. A new source with brands of its own
    would not: ``table()`` must import each one itself."""
    probe = (
        "import sys\n"
        "from synthetic_ecommerce_data.domains.retail import brand_owners as b\n"
        "b.table()\n"
        "print(sorted(s for s in b.SOURCES if f'{b._PACKAGE}.{s}' not in sys.modules))\n"
    )
    done = subprocess.run(
        [sys.executable, "-c", probe], capture_output=True, text=True, timeout=300, check=False
    )
    assert done.returncode == 0, done.stderr[-2000:]
    assert done.stdout.strip() == "[]"
