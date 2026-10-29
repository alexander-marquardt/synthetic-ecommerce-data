"""Mutation rows for the bicycle model numbers and the cycling accessories (gen#625).

Each row plants one defect in the model-number scheme, a bicycle title, an accessory drawing or a
decoy row and names the test that must go red. ``mutation_check.py`` turns them into ``Mutation``
rows named ``bikecode: ...`` (``--only "bikecode:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

# ruff: noqa: E501 -- a row's old and new text are source lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

_R = "src/synthetic_ecommerce_data/domains/retail"
_T = "tests/test_retail_bicycle_model_numbers_625.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "an adult bike's code may drop its wheel size",
        "bicycle_model_numbers.py",
        'if (wheel is None) != (kind == "Kids"):\n        raise ValueError',
        "if False:\n        raise ValueError",
        f'{_T} -k "only_a_kids_bike_leaves_the_wheel"',
        "only a kids' bike's code has no wheel digits",
        _R,
    ),
    (
        "a kids' code with wheel digits decodes",
        "bicycle_model_numbers.py",
        'if (wheel is None) != (kind == "Kids"):\n            continue',
        "if False:\n            continue",
        f'{_T} -k "no_scheme_builds_decodes_to_nothing"',
        "a code no scheme builds decodes to nothing",
        _R,
    ),
    (
        "decode reads the model year as two digits",
        "bicycle_model_numbers.py",
        '"year": 2000 + int(m["y"])',
        '"year": int(m["y"])',
        f'{_T} -k "builds_its_code_from_kind_wheel_gears_and_year"',
        "a code decodes back to the bike's model year",
        _R,
    ),
    (
        "the title puts the model number before the series",
        "type_specs/bicycle.py",
        'title=f"{row.brand} {series} {code} {bmn.spec',
        'title=f"{row.brand} {code} {series} {bmn.spec',
        f'{_T} -k "title_holds_its_model_number_after_brand_and_series"',
        "a bicycle title reads brand, series, model number",
        _R,
    ),
    (
        "clipless pedals are drawn as flat ones",
        "kit_cycling.py",
        'if style.lower() == "clipless":',
        "if False:",
        f'{_T} -k "draws_every_style and bike_pedals"',
        "each accessory style draws its own picture",
        _R,
    ),
    (
        "a bike pedals print decoy targets the saddle",
        "feature_decoys/cycling_accessories.py",
        '"bike pedals", "pedal", True, "Bike Pedals"',
        '"bike pedals", "pedal", True, "Bike Saddle"',
        'tests/test_retail_sports_decoys_368.py -k "every_live_non_exempt_sports_type_has_at_least_two_decoys"',
        "every sports type carries two class 8 decoys",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "bikecode"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
