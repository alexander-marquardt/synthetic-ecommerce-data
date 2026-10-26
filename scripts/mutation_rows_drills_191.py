"""Mutation rows for the DIY drill family (gen#191).

They are kept out of ``mutation_check.py``. Each row plants one defect in the family's specs,
decoys, house styles or the guard that owes them, and names the test that must go red.
``mutation_row.discover`` finds this file by glob and the harness names the rows ``drills: ...``
(``--only "drills:"`` re-runs them). A row is ``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_drills_191.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the hammer drill's type is a plain Drill",
        "type_specs/hammer_drill.py",
        'product_type="Hammer Drill",',
        'product_type="Drill",',
        f"{_T} -k the_product_type_names_the_tool and hammer_drill",
        "a drill type names its tool and is never a plain Drill",
        _R,
    ),
    (
        "the step ladder draws a stand-in box",
        "type_specs/step_ladder.py",
        '    "step_ladder",\n',
        '    "box",\n',
        f"{_T} -k a_type_draws_a_shape_of_its_own and step_ladder",
        "each type draws a shape of its own, not a box",
        _R,
    ),
    (
        "the candle decoys of the family are dropped",
        "diy_decoy_rows.py",
        "    for row in (_sibling(words, sc, st, kind), _candle(oc, ot, od))",
        "    for row in (_sibling(words, sc, st, kind),)",
        f"{_T} -k a_type_carries_three_text_match_decoys",
        "each type carries an incidental-word decoy besides its category-word one",
        _R,
    ),
    (
        "the corded drill's brands collapse to one",
        "type_specs/corded_drill.py",
        "            d.TOR,\n",
        "            d.BRI,\n",
        f"{_T} -k a_type_has_three_invented_brands and corded_drill",
        "a type has at least three brands",
        _R,
    ),
    (
        "a house style of the family is missing",
        "diy_brand_styles.py",
        '    "Stonemarsh":     H(',
        '    "Stonemarsh ":    H(',
        f"{_T} -k every_image_id_of_a_type_resolves and sds_hammer_drill",
        "every brand of the family draws its house style",
        _R,
    ),
    (
        "a multi-purpose bit set drills into one material only",
        "type_specs/drill_bit_set.py",
        "into = (drills,) if isinstance(drills, str) else drills",
        "into = (drills,) if isinstance(drills, str) else drills[:1]",
        "tests/test_retail_type_specs_351.py -k drill_bit_set",
        "a set that names masonry in its text states masonry as a material",
        _R,
    ),
    (
        "the color-word drills go back to the old type",
        "color_word_brand_rows.py",
        '        "Drill Driver",\n        49.0,',
        '        "Cordless Drill",\n        49.0,',
        f"{_T} -k no_row_of_the_catalog_is_typed_with_the_old_cordless_drill",
        "no row keeps the old Cordless Drill type",
        _R,
    ),
]
