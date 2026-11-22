"""A row's ``brand_owner`` is the same whatever the interpreter imported first (gen#1039).

``Row.doc()`` read a brand's owner from ``breadth_row.OWNERS``, which about twenty modules fill
when they are imported. So a row's document depended on import order: in a fresh interpreter
``electronics_rows.LAPTOPS[0].doc()`` raised ``KeyError: 'Halvern'``, and gave ``third_party``
once ``type_registry.specs()`` had run. A test passed or failed by which test files shared its
CI worker (``tests (12)`` of synth#1020). Now no module writes the table: each states its brands
in an ``OWNED`` constant, and ``brand_owners.table()`` merges those, every spec's ``owners`` and
the base table, raising when two give one brand different owners. These checks run in fresh
interpreters, one per first import, so nothing an earlier test imported can fill the table.
"""

from __future__ import annotations

import ast
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


#: A line that adds to an ``OWNERS`` table: ``OWNERS.update(``, ``OWNERS.setdefault(`` or
#: ``OWNERS[brand] = ``, also under an alias that ends in ``OWNERS`` (``_BREADTH_OWNERS``).
WRITE = re.compile(r"OWNERS(\.update\(|\.setdefault\(|\[[^]]+\]\s*=[^=])")


def test_no_module_writes_an_owner_when_it_is_imported() -> None:
    """An import-time write makes an owner depend on what was imported first; a module states its
    brands in ``OWNED`` instead (gen#1039)."""
    assert WRITE.search('_BREADTH_OWNERS.setdefault(b, o)\nOWNERS["Knacks"] = "own"\n')
    writes = [
        f"{p.relative_to(RETAIL)}:{n}"
        for p in sorted(RETAIL.rglob("*.py"))
        for n, line in enumerate(p.read_text().splitlines(), 1)
        if WRITE.search(line)
    ]
    assert writes == []


def _states_owned(path: Path) -> bool:
    """True when the module binds ``OWNED`` at its top level."""
    for node in ast.parse(path.read_text()).body:
        targets = node.targets if isinstance(node, ast.Assign) else [getattr(node, "target", None)]
        if any(isinstance(t, ast.Name) and t.id == "OWNED" for t in targets):
            return True
    return False


def test_every_module_that_states_owned_is_a_source_of_the_table() -> None:
    """A module whose ``OWNED`` is not in ``SOURCES`` would make ``table()`` miss its brands, and a
    source without ``OWNED`` would fail when the table is read. Spec modules are walked."""
    stating = {p.stem for p in RETAIL.glob("*.py") if _states_owned(p)}
    assert stating, "no module states OWNED: the check no longer matches how modules state owners"
    assert sorted(stating - set(brand_owners.SOURCES)) == []
    assert sorted(set(brand_owners.SOURCES) - stating) == []


def test_two_sources_that_disagree_on_a_brand_raise_naming_both() -> None:
    """No first-wins rule hides a disagreement: ``beach_towel`` said ``Harbour & Pine`` was third
    party while 33 other sources said own, and the import-time writes dropped it silently."""
    agree = [
        ("a.OWNED", (("Larkmoor", "own"),)),
        ("b.OWNED", (("Larkmoor", "own"), ("Fenmere", "third_party"))),
    ]
    assert brand_owners.merge(agree) == {"Larkmoor": "own", "Fenmere": "third_party"}
    disagree = [*agree, ("type_specs/beach_towel.py", (("Larkmoor", "third_party"),))]
    with pytest.raises(brand_owners.OwnerConflict) as err:
        brand_owners.merge(disagree)
    assert "'Larkmoor'" in str(err.value)
    assert "a.OWNED" in str(err.value) and "type_specs/beach_towel.py" in str(err.value)


def test_every_source_of_the_table_agrees_on_every_brand() -> None:
    """The base table, each ``OWNED`` and each spec's ``owners`` give each brand one owner."""
    names = [name for name, _ in brand_owners.sources()]
    assert "breadth_row.OWNERS" in names and "hair_rows.OWNED" in names
    assert "type_specs/beach_towel.py" in names
    assert brand_owners.merge(brand_owners.sources()) == dict(brand_owners.table())
    assert brand_owners.table()["Harbour & Pine"] == "own"


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
