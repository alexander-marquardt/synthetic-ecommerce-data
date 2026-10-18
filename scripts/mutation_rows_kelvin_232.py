"""Mutation rows for a light's color temperature as a kelvin entry (gen#232), kept out of
``mutation_check.py``.

Each row plants one defect and names the test that must go red. ``mutation_check.py`` turns
them into ``Mutation`` rows named ``kelvin entry: ...`` (``--only "kelvin entry:"`` re-runs
them). A row is ``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

RETAIL = "prototypes/retail_drawings"
SRC = "src/synthetic_ecommerce_data"
TESTS = "tests/test_retail_lighting_197.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the temperature's value carries its unit again",
        "lighting_rows.py",
        'return (key, name, str(kelvin), "KEL", float(kelvin))',
        'return (key, name, f"{kelvin}K", "KEL", float(kelvin))',
        f"{TESTS} -k every_lighting_color_temperature_entry_is_kelvin",
        "no lighting attribute holds a unit inside its value string",
        RETAIL,
    ),
    (
        "the temperature carries no unit code",
        "lighting_rows.py",
        'return (key, name, str(kelvin), "KEL", float(kelvin))',
        'return (key, name, str(kelvin))',
        f"{TESTS} -k every_lighting_color_temperature_entry_is_kelvin",
        "every lighting color temperature entry carries KEL",
        RETAIL,
    ),
    (
        "a tunable lamp's range is stored low end last",
        "lighting_rows.py",
        '"Minimum color temperature", low)',
        '"Minimum color temperature", high)',
        f"{TESTS} -k desk_lamp_has_one_temperature_or_a_min_and_max_range",
        "a tunable lamp's minimum is below its maximum",
        RETAIL,
    ),
    (
        "a tunable lamp's range loses its maximum entry",
        "lighting_rows.py",
        '_kelvin("color_temperature_max", "Maximum color temperature", high))',
        '_kelvin("color_temperature_min", "Maximum color temperature", high))',
        f"{TESTS} -k desk_lamp_has_one_temperature_or_a_min_and_max_range",
        "a tunable lamp has a minimum and a maximum entry",
        RETAIL,
    ),
    (
        "the core knows no kelvin unit",
        "core/entry.py",
        '    "KEL": Fraction(1),',
        '    "KELX": Fraction(1),',
        f"{TESTS} -k every_lighting_color_temperature_entry_is_kelvin",
        "KEL is a unit code the standard accepts",
        SRC,
    ),
    (
        "the core's kelvin canonical is not the count",
        "core/entry.py",
        '    "KEL": Fraction(1),',
        '    "KEL": Fraction(10),',
        f"{TESTS} -k every_lighting_color_temperature_entry_is_kelvin",
        "a kelvin entry's canonical value is its count",
        SRC,
    ),
    (
        "the preview shows a kelvin entry with no unit",
        "build_preview.py",
        '    "KEL": " K",',
        '    "KEL": "",',
        f"{TESTS} -k preview_shows_a_kelvin_entry_with_its_unit",
        "the preview names the unit the stored value omits",
        RETAIL,
    ),
]
