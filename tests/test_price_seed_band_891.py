"""A p50 or p90/p10 row's band takes in the build's own sampling error (#891, slice 1).

``price.FITTED`` was fitted on the default seed's one draw, and the default build holds a few
dozen product lines of a type, so on another seed a type's p50 or p90/p10 moves further than its
census band allows. Each level row's band is the census band widened by
:data:`.price_report.CENSUS_SES` bootstrap standard errors over the type's product lines,
at most :data:`.price_report.BUILD_SE_CAP` either side, so a catalog priced x2 or x0.5, or a
spread squared or taken to its fifth root, still leaves it (``tests/test_price.py``'s
mutation-power rows).
"""

from __future__ import annotations

import math

import pytest

from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial import price_report
from synthetic_ecommerce_data.domains.industrial.generate import generate
from synthetic_ecommerce_data.domains.industrial.measure import measure

#: A seed the issue's survey ran (20260917-28) whose build, on main before #891, put six p50 or
#: p90/p10 rows out of their census bands: the combination wrench, rigid caster and socket-head
#: screw p50s, and the carriage bolt, combination wrench and threaded rod spreads.
MOVED_SEED = 20260925

#: The level rows still out of band at :data:`MOVED_SEED` once their bands take in the build's
#: error. Its centre, not its sampling, puts it there: the carriage bolt's spread lands under
#: its band on 9 of the 12 seeds, which a fit over several seeds (#891 slice 2) moves.
STILL_OUT = ["price p90/p10: carriage_bolts"]


def _is_level_row(name: str) -> bool:
    return name.startswith(("price p50 (USD): ", "price p90/p10: "))


@pytest.fixture(scope="module")
def moved_rows() -> list:
    config = GeneratorConfig(seed=MOVED_SEED)
    stats = measure(generate(config), config)
    return [row for row in stats["comparisons"] if row.band is not None]


def test_a_moved_seed_holds_every_level_row_but_the_one_its_centre_puts_out(moved_rows):
    out = sorted(row.name for row in moved_rows if _is_level_row(row.name) and not row.within)
    assert out == STILL_OUT, [
        f"{row.name}: {row.achieved:.4g} outside {row.band}"
        for row in moved_rows
        if row.name in out
    ]


def test_one_line_leaves_the_census_band_as_it_is():
    """One line has no error to resample: its band is the census band."""
    errors = price_report.build_errors("bolt_hex", [[1.0, 2.0, 3.0, 9.0]])
    assert errors == (0.0, 0.0)
    assert price_report.widened((8.0, 12.5), 0.0) == (8.0, 12.5)


def test_lines_that_disagree_widen_the_band_by_three_standard_errors():
    lines = [[10.0, 11.0], [12.0, 12.5], [14.0, 15.0], [11.5, 13.0], [12.0, 14.0]]
    p50_error, spread_error = price_report.build_errors("bolt_hex", lines)
    assert 0.0 < p50_error < 0.1
    assert spread_error > 0.0
    low, high = price_report.widened((8.0, 12.5), p50_error)
    factor = math.exp(price_report.CENSUS_SES * p50_error)
    assert low == pytest.approx(8.0 / factor)
    assert high == pytest.approx(12.5 * factor)


def test_the_bootstrap_is_the_same_on_every_call():
    lines = [[1.0, 4.0], [2.0, 9.0], [3.0, 5.0], [7.0, 8.0]]
    assert price_report.build_errors("hex_key", lines) == price_report.build_errors(
        "hex_key", lines
    )


def test_the_widening_is_capped_so_a_doubled_price_still_leaves_the_p50_band():
    """x2 of a figure at the 0.8 floor is 1.6, past the capped 1.25 x 1.25; x0.5 of one at the
    1.25 ceiling is 0.625, under the capped 0.8 / 1.25."""
    low, high = price_report.widened(price_report.P50_BAND, 5.0)
    assert (low, high) == pytest.approx(
        (
            price_report.P50_BAND[0] / price_report.BUILD_SE_CAP,
            price_report.P50_BAND[1] * price_report.BUILD_SE_CAP,
        )
    )
    assert 2 * price_report.P50_BAND[0] > high
    assert 0.5 * price_report.P50_BAND[1] < low
