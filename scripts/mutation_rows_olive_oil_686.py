"""Mutation rows for the olive oil decoys (gen#686), kept out of ``mutation_check.py``. Each row
plants one defect on a changed line and names the test that must go red. Found by
``mutation_row.discover``; ``--only "olive oil:"`` re-runs them. The root is
``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "olive oil"

_F = "feature_decoys/olive_oil.py"
_T = "tests/test_olive_oil_decoys_686.py"


def _row(name, old, new, test, prop) -> Row:
    return Row(name, _F, old, new, test, prop, RETAIL_DRAWINGS)


def rows() -> list[Row]:
    return [
        _row(
            "the sardines are filed as a pickle jar",
            '("Y6862", "tinned",',
            '("Y6862", "pickle",',
            f"{_T} -k filed_typed_and_drawn",
            "each decoy is filed, typed and drawn as what it is",
        ),
        _row(
            "the crisps are filed under Olive Oil",
            '("Food & Drink", "Biscuits & Snacks", "Crisps")',
            '("Food & Drink", "Food Cupboard", "Olive Oil")',
            f"{_T} -k none_is_an_olive_oil",
            "no decoy sits under Olive Oil",
        ),
        _row(
            "the spread title loses olive oil",
            '"Olive Oil Spread", "A soft spread',
            '"Soft Spread", "A soft spread',
            f"{_T} -k holds_olive_oil",
            "every decoy title holds olive oil",
        ),
        _row(
            "the tuna description runs long",
            '"Skipjack tuna chunks in a tin, in olive oil."',
            '"Skipjack tuna chunks in a tin, in olive oil, caught by pole and line at sea."',
            f"{_T} -k are_short",
            "titles and descriptions are short",
        ),
        _row(
            "the rows are class 9, not class 10",
            "d(code, kind, title, desc, color, 10, _Q,",
            "d(code, kind, title, desc, color, 9, _Q,",
            f"{_T} -k class_10_decoy",
            "every row is a class 10 decoy of the olive oil query",
        ),
        _row(
            "the crisps leave the DY686 block",
            '("Y6866", "olive_oil_crisps",',
            '("Y6966", "olive_oil_crisps",',
            f"{_T} -k dy_block",
            "the codes are a DY block of their own",
        ),
    ]
