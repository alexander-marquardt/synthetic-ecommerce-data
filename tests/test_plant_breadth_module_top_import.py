"""Review plant for #54: the test a builder writes for their own breadth type."""

from __future__ import annotations

from synthetic_industrial_products.product_types.raw_materials.ball_stock_precision import SPEC


def test_the_module_declares_its_own_key() -> None:
    assert SPEC.key == "ball_stock_precision"
