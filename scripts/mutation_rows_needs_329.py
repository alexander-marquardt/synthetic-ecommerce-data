"""Mutation rows for the medical bras, period pants and lamp shades (gen#329).

Each row plants one defect and names the test that must go red. ``mutation_check.py`` turns them
into rows named ``needs 329: ...`` (``--only "needs 329:"`` re-runs them). A row is
``(name, file, old, new, test, property)``; every row's root is ``prototypes/retail_drawings``.
"""

# ruff: noqa: E501  (a row quotes the whole line it breaks)

from __future__ import annotations

from mutation_row import Row

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "the medical bras are no longer left out of the derivation",
        "needs_rows.py",
        ', *(f"BRA-{s.code}" for s in BRAS)])',
        "])",
        "tests/test_retail_elasticated_waist_329.py -k test_every_row_is_a_template_no_derived_style_copies",
        "the medical bras are no longer left out of the derivation",
    ),
    (
        "Mastectomy Bras is not a purpose node under Bras",
        "facet_leaves.py",
        '"Post-Surgery Bras", "Mastectomy Bras")',
        '"Post-Surgery Bras")',
        "tests/test_retail_needs_329.py -k test_mastectomy_bras_are_a_purpose_node_that_stays_under_bras",
        "Mastectomy Bras is not a purpose node under Bras",
    ),
    (
        "the Mastectomy leaf holds three products, below its floor of four",
        "needs_rows.py",
        'Bra("KILDALE", "Kildale", "Bramblewood", "Mastectomy"',
        'Bra("KILDALE", "Kildale", "Bramblewood", "Post-Surgery"',
        "tests/test_retail_needs_329.py -k test_a_purpose_bra_leaf_holds_a_floor_of_real_products",
        "the Mastectomy leaf holds three products, below its floor of four",
    ),
    (
        "a mastectomy bra without pocketed cups",
        "needs_rows.py",
        "a front hook and eye fastening and pocketed cups for a breast form",
        "a front hook and eye fastening and soft cups",
        "tests/test_retail_needs_329.py -k test_every_mastectomy_bra_says_so_in_its_title_and_has_pocketed_cups",
        "a mastectomy bra without pocketed cups",
    ),
    (
        "every period pants states the Light absorbency",
        "type_specs/period_pants.py",
        'a("absorbency", "Absorbency", level)',
        'a("absorbency", "Absorbency", "Light")',
        "tests/test_retail_needs_329.py -k test_period_pants_state_an_absorbency_and_cover_every_level",
        "every period pants states the Light absorbency",
    ),
    (
        "a Lamp Shade row states no fitting",
        "lighting_rows.py",
        '"floor lamp.",\n        (NATURAL, SAGE, BLUSH),\n        (_a("shape", "Shape", "Empire"), _a("fitting", "Fitting", "Lamp"),',
        '"floor lamp.",\n        (NATURAL, SAGE, BLUSH),\n        (_a("shape", "Shape", "Empire"), _a("mount", "Mount", "Lamp"),',
        "tests/test_retail_needs_329.py -k test_the_two_word_lamp_shades_are_sold_in_distinct_forms",
        "a Lamp Shade row states no fitting",
    ),
    (
        "a mastectomy bra sold as wired",
        "needs_rows.py",
        'Bra("MARSKE", "Marske", "Saltmarsh", "Mastectomy", (32, 46), ("A", "G"),\n        (cw("Soft Grey", "#b9bbbe"), _NUDE, _BLACK), 26.0, wired=False',
        'Bra("MARSKE", "Marske", "Saltmarsh", "Mastectomy", (32, 46), ("A", "G"),\n        (cw("Soft Grey", "#b9bbbe"), _NUDE, _BLACK), 26.0, wired=True',
        "tests/test_retail_needs_329.py -k test_a_medical_bra_is_non_wired",
        "a mastectomy bra sold as wired",
    ),
    (
        "a Bikini period pants drawn with the high-leg cut",
        "type_specs/period_pants.py",
        'CUTS = {"Bikini": "bikini"',
        'CUTS = {"Bikini": "high_leg"',
        "tests/test_retail_needs_329.py -k test_each_period_pants_drawing_shows_the_cut_its_attribute_states",
        "a Bikini period pants drawn with the high-leg cut",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "needs 329"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
