"""Mutation rows for the one paper and the per-product angle (#849).

Each row plants one defect and names the test that must go red (``--only "one paper:"`` re-runs
them). A row is ``(name, file, old, new, test, property)``; ``file`` hangs off the generator
package.
"""

# ruff: noqa: E501 -- a row's old and new text are source lines, quoted whole.

from __future__ import annotations

from mutation_row import Row

L = "core/drawing/product_look.py"
I = "core/drawing/__init__.py"  # noqa: E741
H = "domains/retail/house_styles.py"
T = "tests/test_one_paper_one_angle_849.py"

ROWS: list[tuple[str, str, str, str, str, str]] = [
    (
        "an industrial brand draws on its own tint again",
        "core/drawing/style.py",
        "        paper=PAPER,",
        '        paper="#edf6ec",',
        f'{T} -k "every_industrial_brand_draws_on_the_one_paper and Vellinhorst"',
        "every industrial brand draws on the one paper",
    ),
    (
        "a retail sheet draws on a tint",
        H,
        """    sheet = [f'<rect width="{SIZE}" height="{SIZE}" fill="{PAPER}"/>']""",
        """    sheet = [f'<rect width="{SIZE}" height="{SIZE}" fill="#edf0f3"/>']""",
        f"{T}::test_every_retail_brand_draws_on_the_one_paper_with_no_texture",
        "every retail brand draws on the one paper",
    ),
    (
        "every product is upright",
        L,
        '    return ANGLES[int.from_bytes(digest[:8], "big") % len(ANGLES)]',
        "    return 0",
        f"{T}::test_the_angles_spread_over_the_set_and_most_products_are_turned",
        "the angles spread over the set",
    ),
    (
        "a product's SKUs are drawn upright, whatever its angle",
        I,
        "        _draw(product_type, brand, record, scale * ratio, angle)",
        "        _draw(product_type, brand, record, scale * ratio, 0)",
        (
            f"{T}::test_every_sku_of_a_product_is_drawn_at_its_products_angle",
            f"{T}::test_two_products_of_one_type_at_two_angles_draw_two_pictures",
        ),
        "every SKU of a product is drawn at its product's angle",
    ),
    (
        "the industrial type scale ignores the turn",
        I,
        "    return type_scale(product_look.turned(*extent, angle))",
        "    return type_scale(extent)",
        f"{T} -k turned_industrial_figure_stays_inside",
        "a turned industrial figure stays inside the figure area",
    ),
    (
        "a turned retail product is never shrunk to fit",
        H,
        "    k = min(\n        1.0,",
        "    k = 1.0 or min(\n        1.0,",
        f"{T}::test_a_turned_retail_product_stays_inside_the_room_its_logo_leaves",
        "a turned retail product stays inside the room its logo leaves",
    ),
]

PREFIX = "one paper"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
