"""Mutant rows for the complexion shades (gen#345), kept out of ``mutation_check.py``.

Each row plants one defect where a complexion product's shade is written and names the tests that
must go red. ``python scripts/mutation_check.py --only "shades:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "shades"

_T = "tests/test_retail_shade_345.py"


def rows() -> list[Row]:
    def row(name, file, old, new, tests, prop):
        return Row(f"{PREFIX}: {name}", file, old, new, tests, prop, root=RETAIL_DRAWINGS)

    return [
        row(
            "a complexion product writes its shade back to color",
            "export.py",
            '    if rec["product_type"] in shades.SOLD_BY_SHADE:\n'
            "        return _shade_entries(authored)",
            "    if False:\n        return _shade_entries(authored)",
            (f"{_T} -k no_color_value_is_a_shade_code", f"{_T} -k has_no_color_at_all"),
            "no color value is a shade code",
        ),
        row(
            "the style's own shade list falls back to color",
            "export.py",
            '        facts += _swatch_entries(rec, c["color"])',
            '        facts += _color_entries(c["color"])',
            f"{_T} -k has_no_color_at_all",
            "the style carries no color either",
        ),
        row(
            "the tinted moisturiser is not sold by shade",
            "shades.py",
            'SOLD_BY_SHADE = frozenset({"Foundation", "Concealer", "Moisturiser"})',
            'SOLD_BY_SHADE = frozenset({"Foundation", "Concealer"})',
            f"{_T} -k no_color_value_is_a_shade_code",
            "every complexion type is sold by shade",
        ),
        row(
            "a shade loses its undertone entry",
            "export.py",
            '        _entry("undertone", "Undertone", None, undertone),\n',
            "",
            f"{_T} -k has_shade_depth_and_undertone",
            "every complexion row has an undertone",
        ),
        row(
            "a shade loses its depth entry",
            "export.py",
            '        _entry("shade_depth", "Shade depth", None, depth),\n',
            "",
            f"{_T} -k has_shade_depth_and_undertone",
            "every complexion row has a depth",
        ),
        row(
            "the medium band starts a depth late",
            "shades.py",
            "_BAND_START = (1, 3, 6, 9, 12)",
            "_BAND_START = (1, 3, 7, 9, 12)",
            f"{_T} -k a_code_derives",
            "6 is medium",
        ),
        row(
            "the light band starts a depth early",
            "shades.py",
            "_BAND_START = (1, 3, 6, 9, 12)",
            "_BAND_START = (1, 2, 6, 9, 12)",
            f"{_T} -k a_code_derives",
            "2 is fair",
        ),
        row(
            "the deep band starts a depth early",
            "shades.py",
            "_BAND_START = (1, 3, 6, 9, 12)",
            "_BAND_START = (1, 3, 6, 9, 11)",
            f"{_T} -k a_code_derives",
            "11 is tan",
        ),
        row(
            "the deep band starts a depth late",
            "shades.py",
            "_BAND_START = (1, 3, 6, 9, 12)",
            "_BAND_START = (1, 3, 6, 9, 13)",
            f"{_T} -k a_code_derives",
            "12 is deep",
        ),
        row(
            "a warm code reads neutral",
            "shades.py",
            '"W": "warm"',
            '"W": "neutral"',
            f"{_T} -k a_code_derives",
            "W is warm",
        ),
        row(
            "a named shade takes the wrong depth",
            "shades.py",
            '"Espresso": ("deep", "neutral")',
            '"Espresso": ("tan", "neutral")',
            f"{_T} -k a_named_shade_states",
            "a named shade states its depth",
        ),
        row(
            "an unknown shade name is guessed instead of refused",
            "shades.py",
            "        if shade not in NAMED:\n            raise KeyError(",
            "        if False:\n            raise KeyError(",
            f"{_T} -k unknown_shade_name",
            "nothing is guessed from a word",
        ),
        row(
            "a named shade is folded into a plain color word",
            "class_rows.py",
            '(shade("Porcelain", "#f1dcc8"), 1)',
            '(cw("Porcelain", "#f1dcc8"), 1)',
            (f"{_T} -k kept_as_authored", f"{_T} -k a_named_shade_states"),
            "a named shade is kept as authored",
        ),
        row(
            "the shade key loses its declaration",
            "export.py",
            '    "shade": ("shade", "Shade", None),\n',
            "",
            f"{_T} -k declared_options",
            "shade is a declared option",
        ),
    ]
