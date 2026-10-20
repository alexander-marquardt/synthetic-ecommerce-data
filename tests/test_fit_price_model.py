"""``scripts/fit_price_model.py`` spreads the bolt's census slopes, pack included (#86),
and fits a kit on the part models the same run fitted (#94)."""

from __future__ import annotations

import importlib.util
import math
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
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


@pytest.fixture(scope="module")
def default_build(fit):
    catalog, recorded = fit.record_draws(GeneratorConfig())
    return fit.collect(catalog), recorded


def _doubled_parts() -> dict[str, price.PriceModel]:
    """Every part type a kit holds, refitted to twice its anchor."""
    return {
        part: replace(price.MODELS[part], anchor=price.MODELS[part].anchor * 2)
        for part in set(price.KIT_PARTS.values())
    }


def _kits(collected) -> list[str]:
    return [sku for sku, t in collected.type_of.items() if t == "kit_assortment"]


def test_rekeying_reads_each_kit_on_the_refitted_part_models(fit, default_build):
    collected, recorded = default_build
    rekeyed = fit.rekey_contents(recorded, _doubled_parts())
    kits = _kits(collected)
    assert kits
    for sku in kits:
        assert rekeyed[sku].log_key - recorded[sku].log_key == pytest.approx(math.log(2), abs=1e-9)
    # A type priced from one dimension has nothing to recompute.
    kit_set = set(kits)
    assert all(rekeyed[sku] is recorded[sku] for sku in recorded if sku not in kit_set)


def test_rekeying_leaves_the_draw_terms_a_kit_was_built_with(fit, default_build):
    collected, recorded = default_build
    old = fit.type_build("kit_assortment", collected, recorded)
    rekeyed = fit.rekey_contents(recorded, _doubled_parts())
    new = fit.type_build("kit_assortment", collected, rekeyed)
    assert np.allclose(new.rest, old.rest)
    assert np.allclose(new.log_key - old.log_key, math.log(2))


def test_a_kit_is_shown_at_the_price_of_the_refitted_parts_it_holds(fit, default_build):
    collected, recorded = default_build
    parts = _doubled_parts()
    fitted = {**parts, "kit_assortment": price.MODELS["kit_assortment"]}
    before = fit._shown_prices(collected, recorded, fitted)  # noqa: SLF001
    after = fit._shown_prices(collected, fit.rekey_contents(recorded, parts), fitted)  # noqa: SLF001
    kits = _kits(collected)
    assert sum(after[s] for s in kits) / sum(before[s] for s in kits) == pytest.approx(2, rel=0.03)


def test_one_run_fits_the_kit_on_the_parts_it_just_fitted(fit, default_build, monkeypatch):
    collected, recorded = default_build
    parts = set(price.KIT_PARTS.values())
    seen: dict[str, np.ndarray] = {}

    def refit_the_parts(type_key, builds):
        seen[type_key] = builds[0].log_key
        model = price.MODELS[type_key]
        return fit.TypeFit(
            anchor=model.anchor * (2 if type_key in parts else 1),
            slope=model.slope,
            length_slope=model.length_slope,
            group=model.group_sigma,
            sku=model.sku_sigma,
            step=model.price_step,
            size=model.size_sigma,
            spreads={},
            unreachable=set(),
        )

    monkeypatch.setattr(fit, "fit_type", refit_the_parts)
    fit.fit_all({"default": (collected, recorded)})
    old = fit.type_build("kit_assortment", collected, recorded).log_key
    assert seen["kit_assortment"] - old == pytest.approx(math.log(2), abs=0.01)
