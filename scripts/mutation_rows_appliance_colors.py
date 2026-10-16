"""Mutation rows for the appliance colors (gen#243), kept out of ``mutation_check.py``.

Each row sells a stainless steel appliance in Copper again and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``appliance colors: ...``
(``--only "appliance colors:"`` re-runs them). A row is ``(name, file, old, new, test, property)``.
"""

from __future__ import annotations

_TEST = (
    "tests/test_retail_appliances_202.py "
    "-k no_stainless_steel_row_is_sold_in_the_color_of_another_metal"
)

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the stainless steel kettle is sold in Copper",
        "appliance_rows.py",
        '(SILVER, GREY), _kt("Quiet Boil"',
        '(SILVER, COPPER), _kt("Quiet Boil"',
        _TEST,
        "a stainless steel kettle is not sold in the color of another metal",
    ),
    (
        "the stainless steel toaster is sold in Copper",
        "appliance_rows.py",
        '(SILVER, GREY), _ts(False, "Brushed", 7)',
        '(SILVER, COPPER), _ts(False, "Brushed", 7)',
        _TEST,
        "a stainless steel toaster is not sold in the color of another metal",
    ),
]
