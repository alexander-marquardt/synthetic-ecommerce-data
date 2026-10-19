"""Mutation rows for the truthful grocery, home and garden decoys (gen#449), kept out of
``mutation_check.py``. Each row plants one defect that brings back a lie the believability audit
found (a mushroom punnet of strawberries, a four pack drawn as one pot, a negation as a title, a
description that is a field dump) and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``truthful decoys: ...``
(``--only "truthful decoys:"`` re-runs them). A row is ``(name, file, old, new, test, property)``;
the root is ``prototypes/retail_drawings``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_truthful_decoys_449.py"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str]] = [
    (
        "every punnet holds strawberries again",
        "kit.py",
        "item = PRODUCE[produce]",
        'item = PRODUCE["strawberry"]',
        f"{_T}::test_a_punnet_holds_what_the_title_says",
        "a punnet draws the produce its title names",
    ),
    (
        "every vegetable punnet is asked for tomatoes",
        "grocery.py",
        'marks["produce"] = PUNNET[flavor.name]',
        'marks["produce"] = "tomato"',
        f"{_T}::test_a_punnet_holds_what_the_title_says",
        "the grocery family passes the produce of its own variety",
    ),
    (
        "a multipack of pots is drawn as one pot",
        "kit.py",
        "n = int(count)",
        "n = 1",
        f"{_T}::test_a_four_pack_of_yogurt_is_drawn_as_four_pots",
        "units_per_pack above one draws that many pots",
    ),
    (
        "the lemon sponge's yellow is left out of the color table",
        "decoy_rows.py",
        '"Nude": NUDE, "Yellow": YELLOW,',
        '"Nude": NUDE,',
        f"{_T}::test_no_text_match_decoy_is_drawn_in_the_grey_fallback",
        "every decoy color is in the table: an unknown one is an error, never a grey product",
    ),
    (
        "the mug cake mix is drawn as a celebration cake",
        "decoy_product_words.py",
        '"cake_mix": Kind("Food & Drink", ("Food & Drink", "Bakery", "Cakes"), "Cake", "box",',
        '"cake_mix": Kind("Food & Drink", ("Food & Drink", "Bakery", "Cakes"), "Cake", "cake",',
        f"{_T}::test_a_boxed_mug_cake_mix_is_drawn_as_a_box_not_a_celebration_cake",
        "a boxed mix is drawn as a box",
    ),
    (
        "the mini-me knit top is titled with the audience phrase again",
        "knitwear_rows.py",
        'f"{root} Mini-Me {noun}, Kids\' Version Sold Separately"',
        'f"{root} Mini-Me Kids\' Style {noun}"',
        f"{_T}::test_a_title_states_what_the_product_is_never_what_it_is_not",
        "a title states what the product is, never a bare audience label",
    ),
    (
        "the mens mini-me rows are titled with the audience phrase again",
        "mens_depth_rows.py",
        'add(3, i, f"Mens Mini-Me {noun}, Kids\' Version Sold Separately",',
        'add(3, i, f"Mens Mini-Me Kids\' Style {noun}",',
        f"{_T}::test_a_title_states_what_the_product_is_never_what_it_is_not",
        "a mens Mini-Me title says what it matches, never a bare audience label",
    ),
    (
        "a grocery description drops its pack line",
        "grocery.py",
        "    out.append(_available(packs))\n",
        '    out.append("")\n',
        f"{_T}::test_a_grocery_description_is_a_sentence_then_the_pack_and_storage_line",
        "the pack sizes read as a sentence after the copy",
    ),
    (
        "a grocery description is the field dump again",
        "grocery.py",
        "head = INTRO[fam.product_type].format(name=names[0])",
        'head = f"{names[0]}, in {\', \'.join(p[\'pack_size\'] for p in packs)}."',
        f"{_T}::test_no_grocery_description_is_a_field_dump",
        "no description is the fields read back",
    ),
    (
        "pasta names are a flavor again",
        "grocery_rows.py",
        '           _CUP, 0.03, axis="variety"),',
        "           _CUP, 0.03),",
        f"{_T}::test_a_named_dish_or_pasta_is_a_variety_not_a_flavor",
        "a named product is a variety",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "truthful decoys"


def rows() -> list[Row]:
    return [Row(*r, "prototypes/retail_drawings") for r in ROWS]
