"""Mutation rows for the tap's drive square (gen#3), in their own file.

Each row plants one defect where a tap's ``Square Size`` and the ``Shank Dia.`` beside it are
built, or in the table they come from, and names the test of ``tests/test_tap_square_size_3.py``
that must go red. ``mutation_row.discover`` finds this file by glob and the harness names the
rows ``tap square size: ...`` (``--only "tap square size:"`` re-runs them).
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_tap_square_size_3.py"
_I = "domains/industrial"
_TABLE = "core/standards_library/tables/tap_shank_squares.json"
_BUILD = f"{_I}/generate.py"
_SERIES = f"{_I}/series.py"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "a tap build stops publishing the square",
        _BUILD,
        '                self._length("Square Size", square_in, style),\n',
        "",
        f"{_T}::test_the_default_build_carries_square_size_at_its_declared_presence",
        "a tap SKU carries Square Size at its declared presence",
    ),
    (
        "a tap's square is its shank",
        _BUILD,
        'self._length("Square Size", square_in, style)',
        'self._length("Square Size", shank_in, style)',
        f"{_T}::test_a_tap_square_is_the_standards_square_for_its_thread_size",
        "a tap's square is the standard's square for its thread size",
    ),
    (
        "a tap's shank is a fixed ratio of its thread again",
        _BUILD,
        'self._length("Shank Dia.", shank_in, style),\n                self._length("Square',
        'self._length("Shank Dia.", major_in * 0.9, style),\n                self._length("Square',
        f"{_T}::test_a_tap_shank_is_the_same_row_of_the_standard_as_its_square",
        "a tap's shank and square come from one row of the standard",
    ),
    (
        "a metric tap's square is read in millimetres as inches",
        _SERIES,
        'row["shank_mm"] / MM_PER_INCH, row["square_mm"] / MM_PER_INCH',
        'row["shank_mm"] / MM_PER_INCH, row["square_mm"]',
        f"{_T}::test_a_tap_square_is_the_standards_square_for_its_thread_size",
        "a tap's square is the standard's square for its thread size",
    ),
    (
        "an inch tap's shank and square are swapped",
        _SERIES,
        'return row["shank_in"], row["square_in"]',
        'return row["square_in"], row["shank_in"]',
        f"{_T}::test_a_square_always_fits_on_its_shank",
        "a drive square is smaller than the shank it is cut on",
    ),
    (
        "the table's 5/16 square is mistyped",
        _TABLE,
        '"square_in": 0.238',
        '"square_in": 0.328',
        f"{_T}::test_the_table_is_the_published_shank_and_square_pairs",
        "the table is the published shank and square pairs",
    ),
    (
        "the name exception says the square is never emitted again",
        f"{_I}/names.py",
        '"a tap\'s drive square, from the ASME B94.9 and ISO 529 shank tables; the census has"\n'
        '        " no tap square"',
        '"a tap\'s drive square; declared, never emitted (issue #3)"',
        f"{_T}::test_no_name_exception_still_says_the_name_is_never_emitted",
        "no name exception claims a name is never emitted",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "tap square size"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
