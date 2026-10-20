"""The shared standards library: each size table sourced once, cited, and reused (#73).

A table is one JSON file in :file:`tables/`, named for what it holds
(``iso_2936_hex_key_mm.json``). Adding a table is adding a file: the library lists the
directory, so no shared list is edited and two family PRs that each add a table do not
collide. A family that needs a table reads it by name::

    from synthetic_ecommerce_data.core import standards_library as library

    library.table("asme_b1_1_unified_threads").select(["#10", "1/4"])

Every file carries a ``_library`` block that the loader requires and checks:

``standards``
    The designations the table is read from (``["ISO 2936"]``).
``edition``
    The edition, table or commit it was read at (``"ISO 2936:2014 Table 1"``).
``source``
    Where a reader can check it: the document, the chart or the repository.
``kind``
    What sort of table it is (``series``, ``rows``, ``extraction``), which names the rule
    ``tests/test_standards_library.py`` holds it to.

The rest of the file is the table: a list of ``values`` (one series) or of ``rows``
(records), plus whatever the table's own columns need. A family that uses only some of a
table's sizes names them with :meth:`Table.select`, which refuses a size the table lacks,
so a family's subset cannot drift from the standard it cites.

This moves SIZE tables. What a type claims to conform to is ``conformance.py``'s (#61).
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path
from typing import Any

#: The packaged tables. A family PR adds its file here.
TABLES_DIR = Path(__file__).resolve().parent / "tables"

#: What every table's ``_library`` block must say.
REQUIRED = ("standards", "edition", "source", "kind")


class StandardsTableError(KeyError):
    """A table is missing, uncited or duplicated."""

    def __str__(self) -> str:  # KeyError would quote the whole message
        return str(self.args[0])


@dataclass(frozen=True)
class Table:
    """One table: its citation, and its data as the file holds it."""

    name: str
    standards: tuple[str, ...]
    edition: str
    source: str
    kind: str
    data: dict[str, Any]

    @property
    def values(self) -> list[Any]:
        """A one-column table: the series itself."""
        return self.data["values"]

    @property
    def rows(self) -> list[Any]:
        """A table of records."""
        return self.data["rows"]

    def select(self, keys: list[str], *, by: str = "size") -> list[dict[str, Any]]:
        """The rows whose ``by`` column is in ``keys``, in the order of ``keys``.

        Raises when the table has no row for a key.
        """
        index = {row[by]: row for row in self.rows}
        missing = [key for key in keys if key not in index]
        if missing:
            raise StandardsTableError(
                f"{self.name} has no {by} {missing[0]!r} (carries {', '.join(map(str, index))})"
            )
        return [index[key] for key in keys]

    def pick(self, items: list[Any]) -> list[Any]:
        """The ``values`` named in ``items``, in the order of ``items``; refuses one the
        series lacks."""
        missing = [item for item in items if item not in self.values]
        if missing:
            raise StandardsTableError(
                f"{self.name} has no value {missing[0]!r} (carries {self.values})"
            )
        return list(items)


def _parse(name: str, path: Path) -> Table:
    data = json.loads(path.read_text("utf-8"))
    block = data.get("_library")
    if not isinstance(block, dict):
        raise StandardsTableError(f"{path.name}: no _library block naming its source")
    for key in REQUIRED:
        if not block.get(key):
            raise StandardsTableError(f"{path.name}: _library block lacks {key!r}")
    standards = block["standards"]
    if not isinstance(standards, list) or not all(isinstance(s, str) and s for s in standards):
        raise StandardsTableError(f"{path.name}: _library 'standards' is a list of designations")
    for key in ("edition", "source", "kind"):
        if not isinstance(block[key], str) or not block[key].strip():
            raise StandardsTableError(f"{path.name}: _library {key!r} is a non-empty string")
    return Table(name, tuple(standards), block["edition"], block["source"], block["kind"], data)


class Library:
    """The packaged tables, plus the tables of any extra directory handed in."""

    def __init__(self, *extra_roots: Path) -> None:
        self.roots = (TABLES_DIR, *map(Path, extra_roots))

    @cached_property
    def _paths(self) -> dict[str, Path]:
        paths: dict[str, Path] = {}
        for root in self.roots:
            for path in sorted(root.glob("*.json")):
                if path.stem in paths:
                    raise StandardsTableError(
                        f"two files are named {path.stem!r}: {paths[path.stem]} and {path}"
                    )
                paths[path.stem] = path
        return paths

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._paths))

    @cached_property
    def _tables(self) -> dict[str, Table]:
        return {}

    def table(self, name: str) -> Table:
        if name not in self._tables:
            if name not in self._paths:
                raise StandardsTableError(f"no table {name!r}; the library has {self.names()}")
            self._tables[name] = _parse(name, self._paths[name])
        return self._tables[name]


#: The packaged library every family reads.
DEFAULT = Library()


def names() -> tuple[str, ...]:
    return DEFAULT.names()


def table(name: str) -> Table:
    return DEFAULT.table(name)
