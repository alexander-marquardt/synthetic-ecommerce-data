"""Mutation rows for light bulbs and the one color temperature key (gen#498), kept out of
``mutation_check.py``.

Each row plants one defect and names the test that must go red. ``mutation_check.py`` turns
them into ``Mutation`` rows named ``light bulbs: ...`` (``--only "light bulbs:"`` re-runs them).
A row is ``(name, file, old, new, test, property, root)``; ``test`` is a file and the full name
of one test after ``-k``.
"""

from __future__ import annotations

RETAIL = "prototypes/retail_drawings"
SRC = "src/synthetic_ecommerce_data"
BULBS = "tests/test_retail_light_bulbs_498.py"
SPEC = "type_specs/light_bulb.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a bulb states its temperature under a second key",
        SPEC,
        'return ("color_temperature", "Color temperature", str(k), "KEL", float(k))',
        'return ("color_temperature_k", "Color temperature", str(k), "KEL", float(k))',
        f"{BULBS} -k test_every_lighting_temperature_is_the_one_kelvin_key",
        "a bulb's temperature is under the one color_temperature key",
        RETAIL,
    ),
    (
        "a bulb states its temperature under a second name",
        SPEC,
        'return ("color_temperature", "Color temperature", str(k), "KEL", float(k))',
        'return ("color_temperature", "Colour temp", str(k), "KEL", float(k))',
        f"{BULBS} -k test_every_lighting_temperature_is_the_one_kelvin_key",
        "a bulb's temperature is named Color temperature",
        RETAIL,
    ),
    (
        "a bulb's temperature carries the wrong unit",
        SPEC,
        'str(k), "KEL", float(k))',
        'str(k), "WTT", float(k))',
        f"{BULBS} -k test_every_lighting_temperature_is_the_one_kelvin_key",
        "a bulb's temperature is in kelvin",
        RETAIL,
    ),
    (
        "soft white names the 2700K box",
        SPEC,
        '3000: ("Soft White",',
        '3000: ("Warm White",',
        f"{BULBS} -k test_a_bulb_title_carries_the_box_name_and_the_kelvin_it_states",
        "a bulb's title names the box that its kelvin count prints",
        RETAIL,
    ),
    (
        "the B22 bulbs are sold as E27",
        SPEC,
        '("B22", "gls", "GLS",',
        '("E27", "gls", "GLS",',
        f"{BULBS} -k test_bulbs_exist_in_every_fitting_at_every_temperature",
        "bulbs exist in E27, E14, GU10 and B22 at every temperature",
        RETAIL,
    ),
    (
        "a fitting is sold in one wattage",
        SPEC,
        '((8.5, 60, 3.5), (13.0, 100, 4.5))',
        '((8.5, 60, 3.5), (8.5, 60, 3.5))',
        f"{BULBS} -k test_each_fitting_is_sold_in_a_few_wattage_equivalents",
        "each fitting is sold in two wattages",
        RETAIL,
    ),
    (
        "the integrated LED uplighter states no temperature",
        "lighting_rows.py",
        '"Integrated LED"), _temp(3000),',
        '"Integrated LED"),',
        f"{BULBS} -k test_a_light_states_a_temperature_only_where_the_light_source_comes_with_it",
        "a lamp with an integrated LED states its temperature",
        RETAIL,
    ),
    (
        "a pendant that takes an E27 bulb states a temperature",
        "lighting_rows.py",
        '_a("fixture_type", "Fixture type", "Pendant"), _lights(1),',
        '_temp(3000), _a("fixture_type", "Fixture type", "Pendant"), _lights(1),',
        f"{BULBS} -k test_a_light_states_a_temperature_only_where_the_light_source_comes_with_it",
        "a fitting that takes a replaceable bulb states no temperature",
        RETAIL,
    ),
    (
        "a candle decoy is filed under lighting",
        "decoy_rows.py",
        '"candle_gardenia": Kind("Gifts", ("Gifts", "Home Fragrance", "Scented Candles"),',
        '"candle_gardenia": Kind("Home", ("Home", "Lighting", "Light Bulbs"),',
        f"{BULBS} -k test_each_box_name_has_at_least_three_decoys_that_are_not_lighting",
        "a box-name decoy is not a lighting product",
        RETAIL,
    ),
    (
        "the core knows no watt unit",
        "core/entry.py",
        '    "WTT": Fraction(1),',
        '    "WTTX": Fraction(1),',
        f"{BULBS} -k test_every_lighting_temperature_is_the_one_kelvin_key",
        "WTT is a unit code the standard accepts",
        SRC,
    ),
]
