"""Mutation rows for the tartan, floral, breton stripe and patchwork patterns (gen#408).

Each row plants one defect in the splitter, in the style rows' wiring or in the swatch words, and
names the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``pattern facet: ...`` (``--only "pattern facet:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; every file is under ``prototypes/retail_drawings``.
"""

# ruff: noqa: E501  -- an anchor is the exact source line, so it cannot be wrapped
from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_pattern_facet_408.py"
_WORDS = '    "Polka Dot", "Gingham", "Breton Stripe", "Stripe", "Check", "Spot", "Print", "Leopard", "Marl",\n    "Lace", "Tartan", "Floral", "Patchwork",\n'

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "tartan is no pattern word",
        "colorwords.py",
        _WORDS,
        _WORDS.replace('"Tartan", ', ""),
        f"{_T} -k split",
        "a Red Tartan colorway is color Red and pattern Tartan",
    ),
    (
        "floral is no pattern word",
        "colorwords.py",
        _WORDS,
        _WORDS.replace('"Floral", ', ""),
        f"{_T} -k split",
        "a Pink Floral colorway is color Pink and pattern Floral",
    ),
    (
        "patchwork is no pattern word",
        "colorwords.py",
        _WORDS,
        _WORDS.replace(', "Patchwork"', ""),
        f"{_T} -k split",
        "a Multi Patchwork colorway is color Multi and pattern Patchwork",
    ),
    (
        "breton stripe is a stripe again",
        "colorwords.py",
        _WORDS,
        _WORDS.replace('"Breton Stripe", ', ""),
        f"{_T} -k split",
        "a Navy Breton Stripe colorway has the pattern Breton Stripe, not Stripe",
    ),
    (
        "the pattern rows are not built",
        "scale.py",
        "*neckline_rows.docs(), *pattern_rows.docs(),",
        "*neckline_rows.docs(),",
        f"{_T} -k six_wanted",
        "the build sells the tartan, floral, breton stripe and patchwork styles",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "pattern facet"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
