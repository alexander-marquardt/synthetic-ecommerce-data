"""Mutation rows for the code-built bicycle range (gen#685).

Each row plants one defect in the axes table or the build of ``type_specs/bicycle.py`` and names
the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``bikerange: ...`` (``--only "bikerange:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row's old and new text are source lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

_R = "src/synthetic_ecommerce_data/domains/retail"
_F = "type_specs/bicycle.py"
_T = "tests/test_retail_bicycle_range_685.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "one brand sells the whole range",
        _F,
        "for b, brand in enumerate(BRANDS)\n",
        "for b, brand in enumerate(BRANDS[:1])\n",
        f'{_T} -k "about_twenty_bikes"',
        "the range is about twenty bikes",
        _R,
    ),
    (
        "no brand sells last year's model",
        _F,
        "bmn.MODEL_YEAR - 1 if b == i % len(BRANDS) else bmn.MODEL_YEAR",
        "bmn.MODEL_YEAR",
        f'{_T} -k "both_model_years"',
        "the range carries two model years",
        _R,
    ),
    (
        "the model number ignores the bike's year",
        _F,
        "    return _numbered(row, year)",
        "    return _numbered(row)",
        f'{_T} -k "both_model_years"',
        "last year's bike carries last year's model number and year",
        _R,
    ),
    (
        "last year's model sells at full price",
        _F,
        "        raw *= LAST_YEAR",
        "        raw *= 1",
        f'{_T} -k "price_follows_the_parts"',
        "last year's model costs less",
        _R,
    ),
    (
        "a gear step the markdown rounds away",
        _F,
        "PER_GEAR = 12.0",
        "PER_GEAR = 10.0",
        f'{_T} -k "price_follows_the_parts"',
        "a bike with more of every part costs more",
        _R,
    ),
    (
        "the build ships a repeated bike",
        _F,
        "if key in axes or row.code in codes:",
        "if False:",
        f'{_T} -k "refuses_a_repeated_bike"',
        "no two bikes share brand, kind, gears, wheel and year",
        _R,
    ),
]

PREFIX = "bikerange"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
