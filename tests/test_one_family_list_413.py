"""The scaled build reads its row families from one list (gen#413, slice 4).

``scale.templates`` called each shared row module's ``docs()`` by name, ``retail_figures.measure``
imported and called the same 28 modules again, and ``type_registry.HOME_SOURCES`` named them a
third time: a new family edited three lists in three files, and each was a line two pull
requests could both append to. :data:`type_registry.BUILD_SOURCES` is now the one list, in build
order, with the specs' place in it; both files walk it, and ``HOME_SOURCES`` is that list less
the specs. Reading the families from the list never changes what is generated: the byte-identical
oracle diff (``scripts/build_oracle.py``) of the pull request shows it.
"""

from __future__ import annotations

import ast
from pathlib import Path

from synthetic_ecommerce_data.domains.retail import scale, type_registry

RETAIL = Path(__file__).resolve().parents[1] / "src" / "synthetic_ecommerce_data" / "domains"
RETAIL = RETAIL / "retail"
READERS = ("scale.py", "retail_figures.py")


def _tree(name: str) -> ast.Module:
    return ast.parse((RETAIL / name).read_text(encoding="utf-8"))


def _family_calls(tree: ast.Module) -> list[str]:
    """Every ``<x>_rows.docs()`` call: a family the file names by hand."""
    return sorted(
        node.func.value.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "docs"
        and isinstance(node.func.value, ast.Name)
        and node.func.value.id.endswith("_rows")
    )


def test_no_reader_calls_a_row_family_by_name() -> None:
    assert {name: _family_calls(_tree(name)) for name in READERS} == {n: [] for n in READERS}


def test_the_figures_import_no_row_family() -> None:
    imported = [
        alias.name
        for node in ast.walk(_tree("retail_figures.py"))
        if isinstance(node, ast.ImportFrom | ast.Import)
        for alias in node.names
        if alias.name.endswith("_rows")
    ]
    assert imported == []


def test_the_home_sources_are_the_build_sources_less_the_specs() -> None:
    sources = type_registry.BUILD_SOURCES
    assert sources[0] == "samples" and sources[-1] == "grocery"
    assert sources.count(type_registry.SPEC_SOURCE) == 1
    assert len(set(sources)) == len(sources)
    homes = tuple(s for s in sources if s != type_registry.SPEC_SOURCE)
    assert homes == type_registry.HOME_SOURCES


def test_every_family_the_build_lists_is_read_by_name() -> None:
    """``scale.family_docs`` reads each row module of the list, and the specs at their place."""
    names = [s for s in type_registry.BUILD_SOURCES if s not in ("samples", "grocery")]
    got = scale.family_docs(frozenset())
    want = [
        d
        for name in names
        for d in (
            type_registry.docs(skip=frozenset())
            if name == type_registry.SPEC_SOURCE
            else scale.source_docs(name)
        )
    ]
    assert [d["product_id"] for d in got] == [d["product_id"] for d in want]
