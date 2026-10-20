"""Mutation rows for the end mill's drawn cutting ends (gen#9), kept out of ``mutation_check.py``.

Each row breaks one line that carries a published ``Single End/Double End`` through the figure's
fallbacks, and names the tests that must go red. ``mutation_check.py`` turns them into ``Mutation``
rows named ``end ends: ...`` (``--only "end ends:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; the file is relative to the generator package.
"""

from __future__ import annotations

from mutation_row import Row

_TESTS = ("tests/test_end_mill_ends_drawn_9.py",)
_FILE = "domains/industrial/drawing/figures.py"
_FORM = "a fallback takes extents from the nominal shape, never the published form"

ROWS: list[tuple[str, str, str, str, tuple[str, ...], str]] = [
    (
        "the ends are not carried into the keep-the-diameter fallback",
        _FILE,
        "if k not in defaults} | form\n",
        "if k not in defaults}\n",
        _TESTS,
        _FORM,
    ),
    (
        "the ends are not carried into the nominal fallback",
        _FILE,
        'return geometry(nominal | form), "nominal"',
        'return geometry(nominal), "nominal"',
        _TESTS,
        _FORM,
    ),
    (
        "a value naming no number of ends is carried as a form",
        _FILE,
        'if ends.lower() in ("single end", "double end") else {}',
        "if ends else {}",
        _TESTS,
        "only a published number of ends is a form",
    ),
    (
        "a published number of ends is never carried",
        _FILE,
        "form = {ENDS_ATTRIBUTE: ends} if",
        "form = {} if",
        _TESTS,
        "a published double end is drawn double",
    ),
]

PREFIX = "end ends"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
