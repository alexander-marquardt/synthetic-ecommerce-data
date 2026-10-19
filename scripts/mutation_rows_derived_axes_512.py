"""Mutation rows for a derived shoe's redrawn variant axes (gen#512), kept out of the table.

Each row plants one defect in ``scale.derive``'s call of ``footwear_rows.fit_axes`` or in
``fit_axes`` itself, and names the tests that must go red. ``mutation_row.discover`` finds this
file by glob and names the rows ``derived shoe axes: ...`` (``--only "derived shoe axes:"``
re-runs them). The root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "derived shoe axes"

_T = "tests/test_retail_scale_drawing_params_512.py"
_CLOG = f"{_T}::test_a_derived_clog_draws_the_strap_its_attribute_states"
_SWEEP = f"{_T}::test_every_value_the_scale_can_derive_to_is_one_the_kit_draws"


def rows() -> list[Row]:
    return [
        Row(
            "a derived shoe keeps the axes the swap wrote",
            "scale.py",
            "    footwear_rows.fit_axes(rec)  #",
            "    pass  #",
            (_CLOG, _SWEEP),
            "a derived shoe is drawn with the kit's word for its attributes",
            root=RETAIL_DRAWINGS,
        ),
        Row(
            "a derived shoe is redrawn from the template's attributes, not its own",
            "footwear_rows.py",
            '    e = {a["key"]: a["value"] for a in rec["attributes"]}\n    params |=',
            '    e = {"strap": "None", "material": "EVA"}\n    params |=',
            _CLOG,
            "a derived clog draws the strap its attribute states",
            root=RETAIL_DRAWINGS,
        ),
    ]
