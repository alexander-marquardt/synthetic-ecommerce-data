"""The SKUs-per-product bounds in docs/adding-a-type.md are the build's (#252).

``ecom-generate build`` refuses a type whose product has more SKUs than the
``variants_per_product`` knob's largest count, or whose median passes the count
where the knob's cumulative weight reaches 75%, for a type of at least
``MEDIAN_MIN_PRODUCTS`` products (``product_split.distribution_problems``). A type
author whose draft trips the refusal reads the numbers in the section
"Product-constant and variant attributes". This test reads them from the doc and
holds each to the value the build enforces, so the doc cannot drift from the code.

The enforced values are measured by calling ``distribution_problems`` itself,
not by re-deriving them: a second derivation here would be a second copy.
"""

from __future__ import annotations

import re
from pathlib import Path

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.product_split import (
    MEDIAN_MIN_PRODUCTS,
    distribution_problems,
)

DOC = Path(__file__).resolve().parents[1] / "docs" / "adding-a-type.md"
SECTION = "### Product-constant and variant attributes"


def _section() -> str:
    text = DOC.read_text("utf-8")
    start = text.index(SECTION)
    end = text.find("\n### ", start + len(SECTION))
    return text[start:end]


def _row(products: int, median: int, top: int) -> dict:
    return {"t": {"products": products, "median": median, "max": top, "histogram": {}}}


def _enforced_max(config: GeneratorConfig) -> int:
    """The most SKUs one product may have: the largest count that does not red."""
    return max(n for n in range(1, 50) if not distribution_problems(_row(1, 1, n), config))


def _enforced_median(config: GeneratorConfig) -> int:
    """The largest median a type of ``MEDIAN_MIN_PRODUCTS`` products may have."""
    rows = {n: _row(MEDIAN_MIN_PRODUCTS, n, 1) for n in range(1, 50)}
    return max(n for n, row in rows.items() if not distribution_problems(row, config))


def _claim(pattern: str) -> int:
    match = re.search(pattern, _section())
    assert match, f"{SECTION!r} in {DOC.name} does not state the bound matching {pattern!r}"
    return int(match.group(1))


def test_the_doc_states_the_maximum_skus_per_product() -> None:
    assert _claim(r"at most (\d+) SKUs") == _enforced_max(GeneratorConfig())


def test_the_doc_states_the_median_bound() -> None:
    assert _claim(r"median of at most (\d+)") == _enforced_median(GeneratorConfig())


def test_the_doc_states_the_product_floor_of_the_median_check() -> None:
    assert _claim(r"(\d+) or more products") == MEDIAN_MIN_PRODUCTS
    below = _row(MEDIAN_MIN_PRODUCTS - 1, 49, 1)
    assert distribution_problems(below, GeneratorConfig()) == []


def test_the_doc_names_where_the_bounds_come_from() -> None:
    section = _section()
    for name in ("variants_per_product", "distribution_problems", "MEDIAN_MIN_PRODUCTS"):
        assert f"`{name}`" in section
