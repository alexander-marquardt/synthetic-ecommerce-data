"""Mutation rows for the furniture fill floor (gen#1214), kept out of ``mutation_check.py``.

Each row puts one of the redraw's lines back (the shared size ladder, a small round mirror, a
bookcase or a chair with no light and shade, a long sofa seen as a short one, a sofa with no
shadow) and names the test that must go red. A row is
``(name, file, old, new, tests, property)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_furniture_fill_1214.py"
_FILL = f"{_T}::test_every_sku_fills_its_floor_with_a_highlight_and_a_shadow"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "a mirror is on the shared size ladder",
        "size_ladder.py",
        '"mirror": 0.84',
        '"mirror": 0.55',
        f"{_T}::test_a_size_of_furniture_is_drawn_smaller_but_not_under_the_floor[mirror]",
        "a mirror's smallest size keeps most of its largest one's area",
    ),
    (
        "a dining table is on the shared size ladder",
        "size_ladder.py",
        '"dining_table": 0.84',
        '"dining_table": 0.55',
        f"{_FILL}[dining_table]",
        "a dining table's smallest size fills half of the product area",
    ),
    (
        "a round mirror is small",
        "kit_furniture.py",
        "w = h = 320.0",
        "w = h = 220.0",
        f"{_FILL}[mirror]",
        "a round mirror fills half of the product area",
    ),
    (
        "a ladder bookcase is narrow",
        "kit_furniture.py",
        "rails = ((104, 52), (296, 348))\n        out += [_bar(x, 40",
        "n = 2\n        rails = ((104, 52), (296, 348))\n        out += [_bar(x, 40",
        f"{_FILL}[bookcase]",
        "a ladder bookcase's shelves fill it",
    ),
    (
        "an upright front has no shade",
        "kit_furniture.py",
        "(x + w * 0.6, y + h - 2)), 0.08)]",
        "(x + w * 0.6, y + h - 2)), 0.0)]",
        f"{_FILL}[wardrobe]",
        "a wardrobe has a shadow",
    ),
    (
        "a sofa bed is on the shared size ladder",
        "size_ladder.py",
        '"sofa_bed": 0.84',
        '"sofa_bed": 0.55',
        f"{_T}::test_a_size_of_furniture_is_drawn_smaller_but_not_under_the_floor[sofa_bed]",
        "a sofa bed's smallest size keeps most of its largest one's area",
    ),
    (
        "a long sofa is seen as a short one",
        "kit_seating.py",
        "return LONG if across >= LONG_RUN else SOFA",
        "return SOFA",
        f"{_FILL}[sofa_seats]",
        "a sofa of four seats or more fills half of the product area",
    ),
    (
        "a sofa stands on no shadow",
        "kit_seating.py",
        "out = [_ground(sheet, boxes)] if view.ground else []",
        "out = []",
        f"{_T} -k a_sofa_stands_on_a_ground_shadow",
        "a sofa stands on a ground shadow",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "furniture fill"


def rows() -> list[Row]:
    return [Row(*r, "src/synthetic_ecommerce_data/domains/retail") for r in ROWS]
