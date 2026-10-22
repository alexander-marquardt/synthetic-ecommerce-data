"""Mutation rows for the real cups and the Cup-named bras (gen#620), kept out of
``mutation_check.py``. Each row plants one defect on a changed line and names the test that must go
red. Found by ``mutation_row.discover``; ``--only "cups:"`` re-runs them. The root is
``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "cups"

_T = "tests/test_retail_cups_620.py"


def _row(name, file, old, new, test, prop) -> Row:
    return Row(name, file, old, new, test, prop, RETAIL_DRAWINGS)


def rows() -> list[Row]:
    return [
        _row(
            "the tumbler is drawn as a mug again",
            "class_rows.py",
            '"Tumbler", "tumbler", ((cw("Black", BLACK), 50)',
            '"Tumbler", "mug", ((cw("Black", BLACK), 50)',
            f"{_T} -k drawing_of_its_own",
            "every cup kind has a drawing of its own",
        ),
        _row(
            "the travel cup is drawn as a mug again",
            "class_rows.py",
            '"Travel Cup", "travel_cup",',
            '"Travel Cup", "mug",',
            f"{_T} -k drawing_of_its_own",
            "every cup kind has a drawing of its own",
        ),
        _row(
            "the espresso set title is the short one again",
            "class_rows.py",
            "Set of 4 Porcelain Espresso Cups in Gift Box",
            "Set of 4 Espresso Cups",
            f"{_T} -k six_to_ten_words",
            "a real cup title is six to ten words",
        ),
        _row(
            "the sports tumbler title is the short one again",
            "nike_rows.py",
            '"Insulated Sports Tumbler with Straw Lid for Running"',
            '"Insulated Sports Tumbler"',
            f"{_T} -k six_to_ten_words",
            "a real cup title is six to ten words",
        ),
        _row(
            "the cup bras are no longer bras",
            "feature_decoys/cups_620.py",
            '(*_BRAS, leaf), "Bra", "bra", brand',
            '(*_BRAS, leaf), "Brief", "bra", brand',
            f"{_T} -k are_bras_with_cup",
            "a Cup-named decoy is a bra by product type",
        ),
        _row(
            "the cup bras leave the bra category",
            "feature_decoys/cups_620.py",
            '_BRAS = ("Womens", "Lingerie", "Bras")',
            '_BRAS = ("Womens", "Lingerie", "Briefs")',
            (f"{_T} -k are_bras_with_cup", f"{_T} -k ranks_the_decoys"),
            "a Cup-named decoy sits in the bra category",
        ),
        _row(
            "the full cup bra title drops the word cup",
            "feature_decoys/cups_620.py",
            'cup(620, "cup_bra_full", "Full Cup Bra",',
            'cup(620, "cup_bra_full", "Full Bra",',
            "tests/test_retail_product_word_decoys_326.py -k every_title_is_short",
            "every class-8 title holds its noun",
        ),
    ]
