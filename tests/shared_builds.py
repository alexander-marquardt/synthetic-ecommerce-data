"""The 100K builds the tests read, shared across xdist workers (#140).

STUB for the red commit: every call builds again, in its own process.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any


def cached(
    name: str,
    build: Callable[[], Any],
    *,
    roots: list[Path] | None = None,
    cache_dir: Path | None = None,
) -> Any:
    return build()


def hundred_k_prices() -> tuple[dict, list]:
    """The 100K build's price rows by name, and its kit SKUs."""
    from synthetic_ecommerce_data.core.config import HUNDRED_K_LINES, GeneratorConfig
    from synthetic_ecommerce_data.domains.industrial import price_report
    from synthetic_ecommerce_data.domains.industrial.generate import generate

    catalog = generate(GeneratorConfig(lines=HUNDRED_K_LINES))
    return {row.name: row for row in price_report.price_comparisons(catalog)}, []
