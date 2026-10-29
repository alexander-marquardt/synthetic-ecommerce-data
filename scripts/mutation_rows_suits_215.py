"""Mutation rows for the Mens suits and tailoring types (gen#215), in their own file.

Each row plants one defect in a rule of ``kit_suits.py`` or ``mens_depth_rows.py`` and names the
test that must go red. ``mutation_row.discover`` finds this file by glob and the harness names
them as rows named ``suits: ...`` (``--only "suits:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "a suit trousers style is sold in one leg",
        "mens_depth_rows.py",
        'axis_key="inside_leg", axis=_SUIT_LEGS,',
        'axis_key="inside_leg", axis=_SUIT_LEGS[1:2],',
        "tests/test_retail_suits_215.py -k sell_each_leg",
        "suit trousers are sold in every leg as a SKU (gen#206)",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "no suit trousers style has a leg sold out",
        "mens_depth_rows.py",
        '    return {1: ("Long",), 3: ("Short/Petite",)}.get(i % 4, ())',
        "    return ()",
        "tests/test_retail_suits_215.py -k petite_filter",
        "a petite filter tells suit trousers styles apart",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "a sold-out leg stays in stock",
        "lowerbody_rows.py",
        '"in_stock": s["in_stock"] and v not in self.sold_out}',
        '"in_stock": s["in_stock"]}',
        "tests/test_retail_suits_215.py -k petite_filter",
        "a sold-out leg is out of stock on every SKU",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "a size range counts the legs out of stock",
        "lowerbody_rows.py",
        'served = {LENGTH_RANGE[s[self.axis_key]] for s in self.skus() if s["in_stock"]}',
        "served = {LENGTH_RANGE[s[self.axis_key]] for s in self.skus()}",
        "tests/test_retail_suits_215.py -k size_range_is_derived",
        "a size range is derived from the legs in stock",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "a suit jacket is sold in one length",
        "mens_depth_rows.py",
        'axis_key="length", axis=_JACKET_LENGTHS,',
        'axis_key="length", axis=_JACKET_LENGTHS[:1],',
        "tests/test_retail_suits_215.py -k suit_jacket_sells_each_length",
        "a Mens suit jacket is sold in every length as a SKU",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "slim, tailored and regular jackets share one geometry",
        "kit_suits.py",
        '_JACKET = {"slim": (142, 136), "tailored": (134, 126), "regular": (122, 116)}',
        '_JACKET = {"slim": (122, 116), "tailored": (122, 116), "regular": (122, 116)}',
        "tests/test_retail_suits_215.py -k cut_closer_to_the_body",
        "the fit changes the cut of a jacket, not only the stamp",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "slim, tailored and regular trousers share one leg width",
        "kit_suits.py",
        '_LEG_W = {"slim": 17, "tailored": 22, "regular": 28}',
        '_LEG_W = {"slim": 22, "tailored": 22, "regular": 22}',
        "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
        "the fit changes the width of a trouser leg, not only the stamp",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "the notch lapel is drawn as the shawl",
        "kit_suits.py",
        '    if lapel == "notch":',
        '    if lapel == "notch" and False:',
        "tests/test_retail_suits_215.py -k geometry_not_only_the_stamp",
        "the lapel changes the path, not only the stamp",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "a waistcoat record of four or six buttons is drawn with five",
        "mens_depth_rows.py",
        '("buttons", _BUTTONS[detail])',
        '("buttons", "5")',
        "tests/test_retail_suits_215.py -k draws_what_its_record_states",
        "a waistcoat draws the button count its record states",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "a decoy accessory drops its accessory type",
        "mens_depth_rows.py",
        "            if kind.item:",
        "            if False:",
        "tests/test_retail_suits_215.py -k decoy_accessory_states",
        "a decoy accessory states its accessory type",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        "a three-button jacket is drawn with two buttons",
        "kit_suits.py",
        '        buttons=3 if buttons == "3" else 2,',
        "        buttons=2,",
        "tests/test_retail_suits_215.py -k draws_as_many_buttons",
        "a jacket draws the button count its record states",
        "src/synthetic_ecommerce_data/domains/retail",
    ),
    (
        'a wide trouser leg is drawn as a straight one',
        'kit_suit_sets.py',
        '"wide": 38,',
        '"wide": 24,',
        'tests/test_retail_suit_sets_215.py -k geometry_not_only_the_stamp',
        'the trouser leg fit changes the width of a leg, not only the stamp',
        'src/synthetic_ecommerce_data/domains/retail',
    ),
    (
        'a three piece boys suit is drawn as two pieces',
        'kit_suit_sets.py',
        'n = 3 if pieces == "3" else 2',
        'n = 2 if pieces == "3" else 2',
        'tests/test_retail_suit_sets_215.py -k its_pieces',
        'the pieces param changes the number of pieces drawn',
        'src/synthetic_ecommerce_data/domains/retail',
    ),
    (
        'a double breasted jacket loses its second column of buttons',
        'kit_suit_sets.py',
        'body += [_button(176, 202), _button(176, 250)]',
        'body += []',
        'tests/test_retail_suit_sets_215.py -k second_column_of_buttons',
        'a double breasted jacket draws its second column of buttons',
        'src/synthetic_ecommerce_data/domains/retail',
    ),
    (
        'a collarless jacket is drawn with a lapel',
        'kit_suits.py',
        'if lapel == "none":',
        'if lapel == "never":',
        'tests/test_retail_suit_sets_215.py -k neck_facing_and_no_lapel',
        'a collarless jacket draws its neck facing and no lapel',
        'src/synthetic_ecommerce_data/domains/retail',
    ),
    (
        'the check suit jacket is drawn as a coat again',
        'class_rows.py',
        '"Suit Jacket", "suit_jacket", one(',
        '"Suit Jacket", "coat", one(',
        'tests/test_retail_suit_sets_215.py -k old_suit_jacket_row',
        'the one old Suit Jacket row is drawn as a suit jacket',
        'src/synthetic_ecommerce_data/domains/retail',
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "suits"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
