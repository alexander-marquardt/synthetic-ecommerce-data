"""Mutation rows for the pack scale (gen#543), kept out of ``mutation_check.py``.

Each row plants one defect in the scaling and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``pack scale: ...``
(``--only "pack scale:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_pack_scale_543.py"
_STYLED = f"{_T}::test_the_styled_render_draws_a_smaller_size_smaller_on_the_same_canvas"
_ROOT = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the styled render ignores the shrink",
        "kit.py",
        "uid), shrink)\n    if shape in OFFSET_Y:\n        inner = f'<g",
        "uid), 1.0)\n    if shape in OFFSET_Y:\n        inner = f'<g",
        _STYLED,
        "the shipped (styled) drawing of a smaller size is drawn smaller",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "pack scale"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
