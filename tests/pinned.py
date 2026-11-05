"""The figures a test pins on one build, read from what the one command writes (#50).

A regeneration (``uv run ecom-generate build --out golden-catalog && uv run python
scripts/measure_pins.py``) moves a type's SKU count, the sizes a defect rewrote, a fit's spread.
A test that typed such a figure went red on a moved seed until it was measured again by hand
(slice 2 of #50, ``scripts/reseed_proof.py``, listed them). It reads the figure here instead:

* :func:`sku_count` and :func:`product_count`: the default build's counts by type, from
  ``golden-catalog/stats.json``, which the build writes;
* :func:`hundred_k_skus`: the 100K build's, from ``measured_builds.json``, which the merge
  script's rebuild writes (gen#85);
* :func:`figure`: what a module of :data:`MODULES` measures with its own
  ``measure_pins(config)`` on the build ``config`` makes, from ``tests/data/golden_pins.json``.

The fixture's diff is the review artifact: a figure that moves for no stated reason is questioned
there. A census band is never a figure here: a test holds the build to the band itself.
"""

from __future__ import annotations

import functools
import json
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data.core.price import BUILDS_FILE

REPO = Path(__file__).resolve().parents[1]
STATS = REPO / "golden-catalog" / "stats.json"
PINS = REPO / "tests" / "data" / "golden_pins.json"

#: The test modules that measure a figure of their own with ``measure_pins(config)``; the
#: fixture's ``figures`` holds each one's under its name.
MODULES = (
    "test_fit_price_model",
    "test_pack_quantity",
    "test_type_cotter_pins",
    "test_type_pillow_block_bearings",
    "test_type_roller_chain",
    "test_type_roller_chain_links",
    "test_type_roller_chain_sprockets",
    "test_type_shackles",
)


@functools.cache
def _stats() -> dict:
    return json.loads(STATS.read_text("utf-8"))


def sku_count(type_key: str) -> int:
    """How many SKUs of ``type_key`` the default build holds."""
    return _stats()["skus_by_type"][type_key]


def product_count(type_key: str) -> int:
    """How many products (lines) of ``type_key`` the default build holds."""
    return _stats()["lines_by_type"][type_key]


def hundred_k_skus(type_key: str) -> int:
    """How many SKUs of ``type_key`` the 100K build holds."""
    return json.loads(BUILDS_FILE.read_text("utf-8"))["hundred_k"]["skus_by_type"][type_key]


def figure(module_file: str, name: str) -> Any:
    """The figure ``name`` that the module at ``module_file`` measured into the fixture.

    Read when a test runs, never at import: ``scripts/measure_pins.py`` imports the module to
    measure it, and a fixture without the module's figures yet must not stop that import.
    """
    module = Path(module_file).stem
    figures = json.loads(PINS.read_text("utf-8")).get("figures", {})
    assert module in figures and name in figures[module], (
        f"tests/data/golden_pins.json holds no figure {module}.{name}: "
        "run uv run python scripts/measure_pins.py"
    )
    return figures[module][name]
