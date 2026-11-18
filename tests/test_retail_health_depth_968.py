"""Health's depth: the release ceiling build holds at least 4,750 Health SKUs (gen#968, slice 4).

Slices 1 to 3 put nine over-the-counter types under ``Health`` (vitamins, minerals, first aid,
monitors, eye care, incontinence and mobility aids), 565 SKUs at the ceiling. The 500K mix
(``docs/catalogue-mix-837.md``) plans 5,000, and the issue's Done-when asks for 95% of it at the
build ``release.yaml`` runs (``--skus ceiling``). Slice 4 widens the values a title shows (more
nutrients, minerals and forms), the Health-wide brands of ``department_rates/health.py`` and the
real pack counts a style is sold in, and adds two bottle types under ``Vitamins & Supplements``
(herbal supplements and omega oils), so the build draws more distinct products
(``docs/retail-health.md``).

Each type's four per-type gates stay in its own slice's file
(``tests/test_retail_health_vitamins_968.py``, which also holds slice 4's two types,
``..._first_aid_968.py``, ``..._care_968.py``).
"""

from __future__ import annotations

import collections

import pytest

from retail_ceiling import ceiling_build
from synthetic_ecommerce_data.domains.retail import department_rates, scale

ROOT = "Health"
#: 95% of the mix's 5,000 (the issue's Done-when).
TARGET = 4_750
#: The nine Health types of slices 1 to 3 and slice 4's two.
TYPES = (
    "Vitamins", "Minerals", "Herbal Supplements", "Omega Oils", "Plasters", "First Aid Kits",
    "Thermometers", "Blood Pressure Monitors", "Eye Drops", "Incontinence Pads", "Walking Sticks",
)  # fmt: skip


@pytest.fixture(scope="module")
def ceiling():
    return ceiling_build()


def _health(ceiling) -> list[dict]:
    return [r for r in ceiling.records if r["category_path"][0] == ROOT]


def test_the_release_ceiling_build_holds_at_least_4750_health_skus(ceiling) -> None:
    assert sum(r["sku_count"] for r in _health(ceiling)) >= TARGET


def test_every_health_type_grows_past_its_templates_at_the_ceiling(ceiling) -> None:
    """Depth is spread over the types, not one type standing in for the department."""
    styles = collections.Counter(r["product_type"] for r in _health(ceiling))
    derived = collections.Counter(
        r["product_type"] for r in _health(ceiling) if r["product_id"] in ceiling.template_of
    )
    assert sorted(styles) == sorted(TYPES)
    assert [t for t in TYPES if derived[t] == 0] == []


def test_health_draws_at_a_rate_of_its_own_with_health_wide_brands() -> None:
    """The extra templates and brands would draw Health at the default rate past its share of a
    sub-ceiling build; the department's module holds its own rate and brands (gen#1044)."""
    assert ROOT in department_rates.rates()
    assert scale.DEPARTMENT_RATE[ROOT] != scale.DEFAULT_RATE
    assert len(scale.EXTRA_BRANDS[ROOT]) >= 2
