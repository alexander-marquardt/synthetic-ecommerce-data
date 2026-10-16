"""Mutation rows for the Mens suits and tailoring types (gen#215), in their own file.

Each row plants one defect in a rule of ``kit_suits.py`` or ``mens_depth_rows.py`` and names the
test that must go red. ``mutation_rows_garden_hose.ALL`` carries them to ``mutation_check.py`` as
rows named ``suits: ...`` (``--only "suits:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a long trouser is drawn as long as a short one",
        "kit_suits.py",
        '_HEM = {"short": 316, "regular": 340, "long": 366}',
        '_HEM = {"short": 340, "regular": 340, "long": 340}',
        "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
        "the leg length changes the hem, not only the stamp",
        "prototypes/retail_drawings",
    ),
    (
        "slim, tailored and regular jackets share one geometry",
        "kit_suits.py",
        '_JACKET = {"slim": (142, 136), "tailored": (134, 126), "regular": (122, 116)}',
        '_JACKET = {"slim": (122, 116), "tailored": (122, 116), "regular": (122, 116)}',
        "tests/test_retail_suits_215.py -k cut_closer_to_the_body",
        "the fit changes the cut of a jacket, not only the stamp",
        "prototypes/retail_drawings",
    ),
    (
        "slim, tailored and regular trousers share one leg width",
        "kit_suits.py",
        '_LEG_W = {"slim": 17, "tailored": 22, "regular": 28}',
        '_LEG_W = {"slim": 22, "tailored": 22, "regular": 22}',
        "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
        "the fit changes the width of a trouser leg, not only the stamp",
        "prototypes/retail_drawings",
    ),
    (
        "the notch lapel is drawn as the shawl",
        "kit_suits.py",
        '    if lapel == "notch":',
        '    if lapel == "notch" and False:',
        "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
        "the lapel changes the path, not only the stamp",
        "prototypes/retail_drawings",
    ),
    (
        "a waistcoat record of four or six buttons is drawn with five",
        "mens_depth_rows.py",
        '("buttons", _BUTTONS[detail])',
        '("buttons", "5")',
        "tests/test_retail_suits_215.py -k draws_what_its_record_states",
        "a waistcoat draws the button count its record states",
        "prototypes/retail_drawings",
    ),
    (
        "a decoy accessory drops its accessory type",
        "mens_depth_rows.py",
        "            if kind.item:",
        "            if False:",
        "tests/test_retail_suits_215.py -k decoy_accessory_states",
        "a decoy accessory states its accessory type",
        "prototypes/retail_drawings",
    ),
    (
        "a three-button jacket is drawn with two buttons",
        "kit_suits.py",
        '        buttons=3 if buttons == "3" else 2,',
        "        buttons=2,",
        "tests/test_retail_suits_215.py -k draws_as_many_buttons",
        "a jacket draws the button count its record states",
        "prototypes/retail_drawings",
    ),
]
