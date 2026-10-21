"""Mutation rows for the Electronics department (gen#332).

Each row plants one defect on a changed line of the department's rows, its real-name list, its
closed department list or its class 8 decoys, and names the test that must go red. Found by
``mutation_row.discover``; ``--only "electronics:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "electronics"

_T = "tests/test_retail_electronics_332.py"


def _row(name, file, old, new, test, prop) -> Row:
    return Row(name, file, old, new, test, prop, RETAIL_DRAWINGS)


def rows() -> list[Row]:
    return [
        _row(
            "iPad is no longer a ruled-in real name",
            "real_brands.py",
            'ALLOWED: tuple[str, ...] = ("Nike", "Apple", "iPhone", "iPad")',
            'ALLOWED: tuple[str, ...] = ("Nike", "Apple", "iPhone")',
            f"{_T}::test_the_only_real_names_are_apple_iphone_and_ipad",
            "Apple, iPhone and iPad are the real names the maintainer ruled in",
        ),
        _row(
            "Electronics leaves the closed department list",
            "departments.py",
            '    "Sports & Outdoors",\n    "Electronics",\n)',
            '    "Sports & Outdoors",\n)',
            f"{_T}::test_the_department_is_on_the_closed_list_and_holds_every_node_of_the_issue",
            "Electronics is a department of the closed list",
        ),
        _row(
            "a phone case title drops the phone it fits",
            "electronics_rows.py",
            '_row(f"ECS{i + 1:03d}", f"{n} for {fits}", b,',
            '_row(f"ECS{i + 1:03d}", f"{n}", b,',
            f"{_T}::test_an_accessory_names_the_phone_it_fits_and_has_an_invented_brand",
            "a case for iPhone 15 names the phone truthfully (the model-word decoy)",
        ),
        _row(
            "a class 8 row forgets the device type it clashes with",
            "feature_decoys/electronics.py",
            "cross=True, device_type=device)",
            'cross=True, device_type="")',
            f"{_T}::test_each_cross_department_word_has_at_least_three_class_8_decoys",
            "each model word has class 8 decoys tied to its device type",
        ),
    ]
