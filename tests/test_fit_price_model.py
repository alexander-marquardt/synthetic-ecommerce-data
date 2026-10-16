"""``scripts/fit_price_model.py`` spreads the bolt's census slopes, pack included (#86)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.config import GeneratorConfig

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "fit_price_model.py"


@pytest.fixture(scope="module")
def fit():
    spec = importlib.util.spec_from_file_location("fit_price_model", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    sys.modules["fit_price_model"] = module
    spec.loader.exec_module(module)
    yield module
    del sys.modules["fit_price_model"]


def test_the_census_slopes_and_the_page_pack_spread_the_default_bolt_build_30x(fit):
    catalog, recorded = fit.record_draws(GeneratorConfig())
    build = fit.type_build("bolt_hex", fit.collect(catalog), recorded)
    slope = price.CENSUS["bolt_hex"].slope
    length = price.LENGTH_CENSUS["bolt_hex"].slope
    with_pack = fit.alone(build, slope, length)
    assert round(with_pack, 2) == 30.47
    # The pack term is in it: the slopes alone spread 22.84x.
    assert round(fit._p90_p10(slope * build.log_key + length * build.log_length), 2) == 22.84  # noqa: SLF001
