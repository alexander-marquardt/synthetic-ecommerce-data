"""Mutation rows for Womens sizes above UK 16 (gen#434), kept out of ``mutation_check.py``.

Each row plants one defect in ``plus_sizes.py`` and names the test that must go red.
``mutation_check.py`` turns them into ``Mutation`` rows named ``plus sizes: ...``
(``--only "plus sizes:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_T = "tests/test_retail_plus_sizes_434.py"
_ROOT = "src/synthetic_ecommerce_data/domains/retail"

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
        '{"sku": sku_id(pid, s), **s} for s in added',
        '{"sku": f"{pid}-{n:03d}", **s} for n, s in enumerate(added, 1)',
        "tests/test_retail_stable_ids_626.py -k size_run_extension",
        "a new size's id names its axes, not its place",
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
    (
        "the EU size is one too small, in the build",
        "plus_sizes.py",
        "str(uk + 28)",
        "str(uk + 27)",
        f"{_T} -k 'larger_size_is_a_row'",
        "a new size carries the chart's EU size",
        _ROOT,
    ),
    (
        "the EU size is one too small, in the unit",
        "plus_sizes.py",
        "str(uk + 28)",
        "str(uk + 27)",
        f"{_T} -k 'literal_eu_and_us and Jeans'",
        "a new size carries the chart's EU size",
        _ROOT,
    ),
    (
        "the US size is one too large, in the build",
        "plus_sizes.py",
        "str(uk - 4)",
        "str(uk - 3)",
        f"{_T} -k 'larger_size_is_a_row'",
        "a new size carries the chart's US size",
        _ROOT,
    ),
    (
        "the US size is one too large, in the unit",
        "plus_sizes.py",
        "str(uk - 4)",
        "str(uk - 3)",
        f"{_T} -k 'literal_eu_and_us and Jeans'",
        "a new size carries the chart's US size",
        _ROOT,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "plus sizes"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
