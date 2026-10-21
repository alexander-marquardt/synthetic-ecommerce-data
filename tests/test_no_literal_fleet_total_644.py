"""No test types the retail template fleet total as a literal (#644).

``test_the_pattern_values_add_no_style_and_no_sku`` (gen#408) once asserted
``len(scale.templates()) == 11540`` and a template SKU sum of ``103191``. Every PR that added a
product row moved those two lines, so every pair of product PRs conflicted there and only there,
and the literal went stale the moment main moved. The total is derived from the per-source
counts in ``retail_figures.measure()``; this scan keeps a literal from coming back.

A function that calls ``templates()`` may not compare ``len(...)`` with an integer of four or
more digits, nor a ``sku_count`` sum with an integer of five or more digits, in one assertion.
"""

from __future__ import annotations

import ast
from pathlib import Path

TESTS = Path(__file__).resolve().parent

#: ``len(...) == 1000`` and up is a fleet total; a ``sku_count`` sum of ``10000`` and up is.
MIN_LEN_LITERAL = 1000
MIN_SKU_LITERAL = 10000


def _int_literals(node: ast.expr) -> list[int]:
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and type(n.value) is int]


def _text(node: ast.AST) -> str:
    return ast.unparse(node)


def literal_fleet_totals(source: str) -> list[tuple[int, str]]:
    """The (line, statement) of every assertion of a literal fleet total against ``templates()``."""
    found: list[tuple[int, str]] = []
    for fn in ast.walk(ast.parse(source)):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if "templates(" not in _text(fn):
            continue
        for stmt in ast.walk(fn):
            if not isinstance(stmt, ast.Assert):
                continue
            for cmp_ in (n for n in ast.walk(stmt.test) if isinstance(n, ast.Compare)):
                if not all(isinstance(op, ast.Eq) for op in cmp_.ops):
                    continue
                sides = [cmp_.left, *cmp_.comparators]
                for side in sides:
                    others = [s for s in sides if s is not side]
                    lits = [v for o in others for v in _int_literals(o) if isinstance(o, ast.Constant)]
                    text = _text(side)
                    if any(v >= MIN_LEN_LITERAL for v in lits) and text.startswith("len("):
                        found.append((stmt.lineno, _text(stmt)))
                    if any(v >= MIN_SKU_LITERAL for v in lits) and "sku_count" in text:
                        found.append((stmt.lineno, _text(stmt)))
    return sorted(set(found))


def test_no_test_asserts_a_literal_template_total() -> None:
    bad = {
        path.name: hits
        for path in sorted(TESTS.glob("test_*.py"))
        if path != Path(__file__).resolve()
        for hits in [literal_fleet_totals(path.read_text())]
        if hits
    }
    assert not bad, (
        "a literal fleet total goes stale with every product PR: derive it from "
        f"retail_figures.measure()['templates'] instead: {bad}"
    )


def test_the_scan_sees_both_old_pins_and_passes_a_derived_one() -> None:
    pinned = (
        "def test_x():\n"
        "    tpls = scale.templates()\n"
        "    assert len(tpls) == 11540\n"
        "    assert sum(t['sku_count'] for t in tpls) == 103191\n"
    )
    assert [line for line, _ in literal_fleet_totals(pinned)] == [3, 4]
    derived = (
        "def test_x():\n"
        "    tpls = scale.templates()\n"
        "    assert len(tpls) == sum(p['styles'] for p in parts)\n"
        "    assert len(tpls[:5]) == 5\n"
    )
    assert literal_fleet_totals(derived) == []
    other = "def test_x():\n    assert len(rows) == 11540\n"
    assert literal_fleet_totals(other) == []
