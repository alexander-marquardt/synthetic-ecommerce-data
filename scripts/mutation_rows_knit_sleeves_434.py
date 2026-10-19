"""Mutation rows for the Womens knitwear sleeve lengths and cowl neck (gen#434, gap 2).

Each row plants one defect in ``knit_sleeves.py`` or ``knitwear_rows.py`` and names the test that
must go red. ``mutation_check.py`` turns them into ``Mutation`` rows named ``knit sleeves: ...``
(``--only "knit sleeves:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_knitwear_sleeves_434.py"
_ROOT = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "no knit is completed",
        "knit_sleeves.py",
        "or _stated(r):",
        "or True:",
        f"{_T} -k 'states_one_sleeve_length'",
        "every Womens knit states a sleeve length",
        _ROOT,
    ),
    (
        "a stated sleeve gets a second one",
        "knit_sleeves.py",
        "or _stated(r):",
        "or False:",
        f"{_T} -k 'states_one_sleeve_length'",
        "a knit that states a sleeve keeps its one",
        _ROOT,
    ),
    (
        "a knit with no drawn sleeve is short sleeved",
        "knit_sleeves.py",
        'STORED.get(drawn, "Long")',
        'STORED.get(drawn, "Short")',
        f"{_T} -k 'stated_none_is_long_sleeved'",
        "the older knits are long sleeved",
        _ROOT,
    ),
    (
        "a long drawn sleeve is stored as short",
        "knit_sleeves.py",
        '"long": "Long",',
        '"long": "Short",',
        f"{_T} -k 'drawing_shows_the_sleeve'",
        "the stored sleeve is the drawn one",
        _ROOT,
    ),
    (
        "a short sleeve knit is drawn long sleeved",
        "knitwear_rows.py",
        '"Short": "short",',
        '"Short": "long",',
        f"{_T} -k 'drawing_shows_the_sleeve'",
        "the drawing shows the stored sleeve",
        _ROOT,
    ),
    (
        "the cowl neck jumper states a crew neck",
        "knitwear_rows.py",
        '_JUMP, "cowl", "cowl", "Long"',
        '_JUMP, "crew", "cowl", "Long"',
        f"{_T} -k 'cowl_neck_products'",
        "a cowl neck knit states a cowl neckline",
        _ROOT,
    ),
    (
        "the three quarter cardigan states long sleeves",
        "knitwear_rows.py",
        '_CARDI, "v-neck", "v_neck", "Three quarter"',
        '_CARDI, "v-neck", "v_neck", "Long"',
        f"{_T} -k 'title_naming_a_sleeve and three'",
        "a title naming three quarter sleeves states them",
        _ROOT,
    ),
    (
        "the short sleeve top states long sleeves",
        "knitwear_rows.py",
        '_TOP, "crew", "crew", "Short"',
        '_TOP, "crew", "crew", "Long"',
        f"{_T} -k 'title_naming_a_sleeve and short'",
        "a title naming short sleeves states them",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "knit sleeves"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
