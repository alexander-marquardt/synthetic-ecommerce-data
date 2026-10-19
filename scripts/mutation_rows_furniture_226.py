"""Mutation rows for the furniture drawings' color and material (gen#226), kept out of
``mutation_check.py``.

Each row puts one of the fix's lines back (a grey bookcase back, an opaque glass top, no veins,
a table with no top param) and names the test that must go red. ``mutation_check.py`` turns them
into ``Mutation`` rows named ``furniture drawings: ...`` (``--only "furniture drawings:"``
re-runs them). A row is ``(name, file, old, new, tests, property)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_furniture_drawings_226.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "a bookcase back is shaded 30% toward black",
        "kit_furniture.py",
        "_rect(122, 52, 156, 296, _shade(paint, 0.1), LW_DETAIL)",
        "_rect(122, 52, 156, 296, _shade(paint, 0.3), LW_DETAIL)",
        f"{_T}::test_a_white_bookcase_of_every_style_reads_white",
        "a White bookcase reads white",
    ),
    (
        "the nest of tables is shaded 20% toward black",
        "kit_furniture.py",
        "p = _shade(paint, 0.06 * (2 - k))",
        "p = _shade(paint, 0.1 * (2 - k))",
        f"{_T}::test_a_white_furniture_drawing_reads_white",
        "a White nest of tables reads white",
    ),
    (
        "a glass top is drawn opaque",
        "kit_furniture.py",
        """' class="top" fill-opacity=".55"'""",
        """' class="top"'""",
        f"{_T}::test_a_glass_top_is_drawn_translucent_glass_over_the_record_colored_legs",
        "a glass top is translucent",
    ),
    (
        "a glass top is painted in the record color",
        "kit_furniture.py",
        "_path(outline_d, GLASS, LW,",
        "_path(outline_d, paint, LW,",
        f"{_T}::test_a_glass_top_is_drawn_translucent_glass_over_the_record_colored_legs",
        "a glass top is drawn as glass",
    ),
    (
        "a glass top is drawn as timber",
        "kit_furniture.py",
        '    if top == "glass":\n        out +=',
        '    if top == "glassy":\n        out +=',
        f"{_T}::test_a_glass_top_is_drawn_translucent_glass_over_the_record_colored_legs",
        "a glass top draws no wood grain",
    ),
    (
        "a marble-effect top is drawn as timber",
        "kit_furniture.py",
        'elif top == "marble_effect":',
        'elif top == "marble_effecty":',
        f"{_T}::test_a_marble_effect_top_has_veins_and_no_grain",
        "a marble-effect top is drawn with veins, not grain",
    ),
    (
        "a marble-effect top has no veins",
        "kit_furniture.py",
        ", *_veins(cx, cy, rx, ry, fill.base)]",
        "]",
        f"{_T}::test_a_marble_effect_top_has_veins_and_no_grain",
        "a marble-effect top is drawn with veins",
    ),
    (
        "every table top is oak",
        "furniture_rows.py",
        '("top", top.lower().replace("-", "_"))',
        '("top", "oak")',
        f"{_T}::test_top_material_is_a_drawn_param_that_follows_the_attribute",
        "the top param follows the top_material attribute",
    ),
    (
        "an unknown table top is drawn as timber",
        "kit_furniture.py",
        "    if top not in TOPS:",
        "    if False:",
        f"{_T}::test_an_unknown_top_material_is_refused",
        "an unknown top material is refused",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "furniture drawings"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
