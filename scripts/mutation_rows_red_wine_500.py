"""Mutation rows for the red wine groceries (gen#500), kept out of ``mutation_check.py``. Each row
plants one defect on a changed line of ``decoy_rows.py`` and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``red wine decoys: ...``
(``--only "red wine decoys:"`` re-runs them). A row is ``(name, file, old, new, test, property)``;
the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

_T = "tests/test_red_wine_decoys_500.py"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "the vinegar kind moves to the sauces leaf",
        "decoy_rows.py",
        '"vinegar": _food(("Food Cupboard", "Vinegar")',
        '"vinegar": _food(("Food Cupboard", "Sauces & Condiments")',
        f"{_T}::test_red_wine_vinegar_sits_under_vinegar_in_two_brands_and_two_packs",
        "red wine vinegar sits under Food Cupboard > Vinegar",
    ),
    (
        "both vinegars carry one brand",
        "decoy_rows.py",
        'brand="Copper Hill Preserves"),',
        'brand="Olivar Grove"),',
        f"{_T}::test_red_wine_vinegar_sits_under_vinegar_in_two_brands_and_two_packs",
        "red wine vinegar is sold in at least two brands",
    ),
    (
        "the 250ml vinegar becomes a second 500ml",
        "decoy_rows.py",
        '"Red Wine Vinegar, 250ml"',
        '"Red Wine Vinegar, 500ml"',
        f"{_T}::test_red_wine_vinegar_sits_under_vinegar_in_two_brands_and_two_packs",
        "red wine vinegar is sold in a 250ml and a 500ml pack",
    ),
    (
        "the 500ml vinegar loses its red wine",
        "decoy_rows.py",
        '"Red Wine Vinegar, 500ml"',
        '"Wine Vinegar, 500ml"',
        f"{_T}::test_red_wine_vinegar_sits_under_vinegar_in_two_brands_and_two_packs",
        "both vinegars carry the query's two words in the title",
    ),
    (
        "no decoy sells anything",
        "decoy_rows.py",
        "one(color, self.sold)",
        "one(color, 1)",
        f"{_T}::test_a_plain_red_wine_search_scores_a_vinegar_in_the_top_10",
        "a vinegar's sales put it in the first ten of a plain red wine search",
    ),
    (
        "the gravy is filed under Wine",
        "decoy_rows.py",
        '"gravy": _food(("Food Cupboard", "Sauces & Condiments"), "Sauce", "jar"',
        '"gravy": _food(("Beer, Wine & Spirits", "Wine"), "Sauce", "jar"',
        f"{_T}::test_each_red_wine_grocery_exists_and_is_not_wine",
        "a red wine grocery is never under the Wine category",
    ),
    (
        "the casserole is a class 9 plural decoy",
        "decoy_rows.py",
        '"Red", 10,\n       "red wine", 870',
        '"Red", 9,\n       "red wine", 870',
        f"{_T}::test_every_red_wine_grocery_is_class_10_and_a_decoy_of_the_red_wine_query",
        "every red wine grocery is class 10",
    ),
]
