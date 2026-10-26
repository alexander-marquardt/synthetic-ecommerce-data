"""Mutation rows for the end mill's drawn cutting ends (gen#9), kept out of ``mutation_check.py``.

Each row breaks one line that carries a published ``Single End/Double End`` through the figure's
fallbacks, and names the tests that must go red. ``mutation_check.py`` turns them into ``Mutation``
rows named ``end ends: ...`` (``--only "end ends:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; the file is relative to the generator package.
"""

from __future__ import annotations

from mutation_row import Row

_TESTS = ("tests/test_end_mill_ends_drawn_9.py",)
# gen#10: the flute count and the hand are carried the way the ends are.
_TESTS_10 = ("tests/test_sku_channels_10.py",)
# The pinned end mill digests are what reach the rungs the sweeps do not (the records they draw).
_PINNED = (
    "tests/test_drawing_primitives_74.py::test_the_moved_figures_draw_the_same_svg_bytes_as_before",
)
_FILE = "domains/industrial/drawing/figures.py"
_FORM = "a fallback takes extents from the nominal shape, never the published form"

ROWS: list[tuple[str, str, str, str, tuple[str, ...], str]] = [
    (
        "the ends are not carried into the keep-the-diameter fallback",
        _FILE,
        "record.items() if k not in defaults} | form\n",
        "record.items() if k not in defaults}\n",
        _PINNED,
        _FORM,
    ),
    (
        "the form is not carried into the nominal-core fallback (gen#10)",
        _FILE,
        "nominal.items() if k not in defaults} | form\n",
        "nominal.items() if k not in defaults}\n",
        _PINNED,
        _FORM,
    ),
    (
        "a default replaces a form value in the keep-the-diameter fallback (gen#10)",
        _FILE,
        "        if name in form:\n            continue\n        try:\n            rebuilt[name]",
        "        try:\n            rebuilt[name]",
        _TESTS_10,
        _FORM,
    ),
    (
        "a default replaces a form value in the nominal-core fallback (gen#10)",
        _FILE,
        "            if name in form:\n                continue\n"
        "            try:\n                core[name]",
        "            try:\n                core[name]",
        _TESTS_10,
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
        'if ends.lower() in ("single end", "double end"):',
        "if ends:",
        _TESTS,
        "only a published number of ends is a form",
    ),
    (
        "a published number of ends is never carried",
        _FILE,
        "form[ENDS_ATTRIBUTE] = ends",
        "pass",
        _TESTS,
        "a published double end is drawn double",
    ),
    (
        "a published flute count is never carried (gen#10)",
        _FILE,
        "form[FLUTES_ATTRIBUTE] = flutes",
        "pass",
        _TESTS_10,
        "a fallback keeps the flute count the record publishes",
    ),
    (
        "a published hand is never carried (gen#10)",
        _FILE,
        "form[HAND_ATTRIBUTE] = hand",
        "pass",
        _TESTS_10,
        "a fallback keeps the hand the record publishes",
    ),
]

PREFIX = "end ends"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
