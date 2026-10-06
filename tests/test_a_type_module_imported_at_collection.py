"""A breadth type module imported at collection, before anything else (#54).

The test a builder writes for their own type starts with
``from ...product_types.<family>.<key> import SPEC``. Named to sort before
every other test file, so a full run collects it before anything has
imported the generator; run alone, it is that builder's own test run.
"""

from __future__ import annotations

from synthetic_industrial_products.product_types.raw_materials.ball_stock_precision import SPEC


def test_the_module_declares_its_own_key() -> None:
    assert SPEC.key == "ball_stock_precision"
