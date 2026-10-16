"""Mutation rows for Womens sizes above UK 16 (gen#434), kept out of ``mutation_check.py``.

Each row plants one defect in ``plus_sizes.py`` and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``plus sizes: ...``
(``--only "plus sizes:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

_T = "tests/test_retail_plus_sizes_434.py"
_ROOT = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the run stops at UK 22",
        "plus_sizes.py",
        "TOP = 24",
        "TOP = 22",
        f"{_T} -k extend_appends",
        "the run reaches UK 24",
        _ROOT,
    ),
    (
        "no style is extended",
        "plus_sizes.py",
        "return zlib.crc32(rec[\"product_id\"].encode()) % SHARE[1] < SHARE[0]",
        "return False",
        f"{_T} -k thirty_womens_dresses",
        "a share of the Womens dresses carries UK 22",
        _ROOT,
    ),
    (
        "a new SKU gets a reused id",
        "plus_sizes.py",
        "enumerate(added, len(skus) + 1)",
        "enumerate(added, 1)",
        f"{_T} -k options_and_the_sku_count",
        "no existing SKU id is reused",
        _ROOT,
    ),
    (
        "a bare number size also gets an EU size",
        "plus_sizes.py",
        "if key == \"size_uk\":",
        "if True:",
        f"{_T} -k bare_number_size",
        "a bare size stays one field",
        _ROOT,
    ),
]
