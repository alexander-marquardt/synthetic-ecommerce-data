"""Mutation rows for the one spelling of each pattern value (gen#324).

Each row puts one retired spelling (``Striped``, ``Checked``, ``Spotted``) back on an authored row
and names the test that must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named
``pattern spelling: ...`` (``--only "pattern spelling:"`` re-runs them). A row is
``(name, file, old, new, tests, property)``; every file is under ``prototypes/retail_drawings``.
"""

# ruff: noqa: E501  -- an anchor is the exact source line, so it cannot be wrapped
from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_pattern_spelling_324.py -k authored_template"
_STRIPE = '_a("pattern", "Pattern", "Stripe")'
_WALL = 'a("pattern", "Pattern", "{}")'

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the tote bag is Striped",
        "accessory_rows.py",
        '_tb("Medium", "Cotton", "Zip", False, ' + _STRIPE + ")",
        '_tb("Medium", "Cotton", "Zip", False, ' + _STRIPE.replace("Stripe", "Striped") + ")",
        _T,
        "the tote bag's pattern is spelled Stripe, as its colorways are",
    ),
    (
        "the umbrella is Striped",
        "accessory_rows.py",
        '_um("Stick", False, True, False, 16, ' + _STRIPE + ")",
        '_um("Stick", False, True, False, 16, ' + _STRIPE.replace("Stripe", "Striped") + ")",
        _T,
        "the umbrella's pattern is spelled Stripe, as its colorways are",
    ),
    (
        "the melamine plate is Striped",
        "tableware_rows.py",
        _STRIPE,
        _STRIPE.replace("Stripe", "Striped"),
        _T,
        "the melamine plate's pattern is spelled Stripe, as its colorways are",
    ),
    (
        "the wallpaper is Striped",
        "type_specs/wallpaper.py",
        _WALL.format("Stripe"),
        _WALL.format("Striped"),
        _T,
        "the striped wallpaper's pattern is spelled Stripe",
    ),
    (
        "the wallpaper is Checked",
        "type_specs/wallpaper.py",
        _WALL.format("Check"),
        _WALL.format("Checked"),
        _T,
        "the checked wallpaper's pattern is spelled Check, as the colorway split spells it",
    ),
    (
        "the wallpaper is Spotted",
        "type_specs/wallpaper.py",
        _WALL.format("Spot"),
        _WALL.format("Spotted"),
        _T,
        "the spotted wallpaper's pattern is spelled Spot, as the colorway split spells it",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "pattern spelling"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
