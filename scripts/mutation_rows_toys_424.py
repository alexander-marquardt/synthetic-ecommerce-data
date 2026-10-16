"""Mutation rows for the six toy types of gen#424, in their own file.

Each row plants one defect in a spec, a drawing or a decoy row of gen#424 and names the test that
must go red. ``mutation_rows_garden_hose.ALL`` carries them to ``mutation_check.py`` as rows
named ``toys depth: ...`` (``--only "toys depth:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

_R = "prototypes/retail_drawings"
_T = "tests/test_retail_toys_depth_424.py"
_D = "tests/test_retail_product_word_decoys_326.py"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the kite loses Black and White",
        "type_specs/kite.py",
        "        EIGHT,\n",
        "        EIGHT[:4],\n",
        f"{_T} -k six_main_colors",
        "a kite offers the six main colors",
        _R,
    ),
    (
        "the water gun's tank loses its unit",
        "type_specs/water_gun.py",
        'measured("tank_capacity", "Tank capacity", ml, "MLT")',
        'measured("tank_capacity", "Tank capacity", ml, "LTR")',
        f"{_T} -k structured_entry_with_its_unit",
        "a water gun's tank capacity is in millilitres",
        _R,
    ),
    (
        "the card game loses its Deluxe edition",
        "type_specs/card_game.py",
        ', ("Deluxe", price + 6.0)',
        "",
        f"{_T} -k at_least_150_skus",
        "the six toy types build 150 SKUs or more",
        _R,
    ),
    (
        "the blaster is drawn as the pistol",
        "kit_toys_play.py",
        '    elif k == "blaster":',
        '    elif k == "never":',
        f"{_T} -k param_changes_the_drawing",
        "a water gun's kind changes the drawing",
        _R,
    ),
    (
        "the dolls' house SKU axis is not exported",
        "export.py",
        '    "house_style": ("style", "Style", None),\n',
        "",
        f"{_T} -k sku_axis",
        "a dolls' house is sold by its style",
        _R,
    ),
    (
        "the glue gun's title drops the word gun",
        "decoy_product_words.py",
        '_t(5, "t_glue", "Hot Glue Gun",',
        '_t(5, "t_glue", "Hot Glue Tool",',
        f"{_D} -k every_title_is_short_and_holds_the_noun",
        "a class-8 decoy holds the shopper's noun",
        _R,
    ),
    (
        "the kitchen scales sit in the play kitchen's leaf",
        "decoy_product_words.py",
        '"t_scales": Kind("Home", ("Home", "Kitchen & Dining", "Kitchen Scales")',
        '"t_scales": Kind("Home", ("Home", "Kitchen & Dining", "Play Kitchens")',
        f"{_D} -k fields_say_the_product_is_not_what_the_noun_names",
        "a class-8 decoy never sits in the node of the product its noun names",
        _R,
    ),
]
