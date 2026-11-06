"""The suite half of #50's planted proof: a moved seed shows each pin still typed by hand.

``scripts/reseed_proof.py`` moves the default seed in a scratch worktree, runs the one command a
regeneration runs and then the tests that read what it rewrote. A test that goes red there pins a
figure the fixture does not carry. The whole run builds three catalogs and runs the suite's catalog
readers, minutes; these tests hold its parts on fixed text:

* the seed moves on the one seed line of ``GeneratorConfig``, and a config without exactly one is
  refused rather than left unmoved (a run on the old seed would be green and prove nothing);
* the rebuild is the merge script's, so the proof restates what a regeneration restates;
* the red tests are read from pytest's summary, each id once.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
CONFIG = REPO / "src" / "synthetic_ecommerce_data" / "core" / "config.py"

sys.path.insert(0, str(REPO / "scripts"))
import reseed_proof  # noqa: E402  (scripts/ is not a package)

SNIPPET = '''class GeneratorConfig:
    """How much catalog to make."""

    #: Deterministic: the same seed produces the same catalog, byte for byte.
    seed: int = 41

    lines: int = 2600
'''


def test_the_seed_moves_by_one_on_its_one_line():
    text, seed = reseed_proof.reseed(SNIPPET)
    assert seed == 42
    assert "    seed: int = 42\n" in text
    assert text.replace("= 42", "= 41") == SNIPPET


def test_a_named_seed_replaces_the_default():
    text, seed = reseed_proof.reseed(SNIPPET, 7)
    assert (seed, "    seed: int = 7\n" in text) == (7, True)


@pytest.mark.parametrize(
    "text",
    [SNIPPET.replace("seed: int = 41", "seed = 41"), SNIPPET + "    seed: int = 41\n"],
    ids=["no seed line", "two seed lines"],
)
def test_a_config_without_exactly_one_seed_line_is_refused(text):
    with pytest.raises(reseed_proof.ProofError, match="seed line"):
        reseed_proof.reseed(text)


def test_the_committed_config_has_the_seed_line():
    text, seed = reseed_proof.reseed(CONFIG.read_text("utf-8"))
    assert text != CONFIG.read_text("utf-8")
    assert seed > 1


def test_the_rebuild_is_the_merge_scripts():
    config = (REPO / "scripts" / "merge_pr" / "config.sh").read_text("utf-8")
    tree = (REPO / "scripts" / "merge_pr" / "tree.sh").read_text("utf-8")
    arrays = {
        name: tuple(re.search(rf"^{name}=\((.*)\)$", config, re.MULTILINE)[1].split())
        for name in ("BUILDS_REBUILD", "PINS_REBUILD")
    }
    assert "ecom-generate build --out golden-catalog" in tree
    rebuild = reseed_proof.REBUILD
    assert rebuild == (
        ("ecom-generate", "build", "--out", "golden-catalog"),
        arrays["BUILDS_REBUILD"],
        arrays["PINS_REBUILD"],
    )


SUMMARY = """\
..F.....E..
=========================== short test summary info ============================
FAILED tests/test_catalog_golden.py::test_lines - AssertionError: assert 2611 == 2603
FAILED tests/test_sku_drawings.py::test_pinned[M6x1 x 10mm, handle-less] - assert False
ERROR tests/test_facet_control_rule.py::test_band - KeyError: 'band'
FAILED tests/test_catalog_golden.py::test_lines - AssertionError: assert 2611 == 2603
FAILED tests/test_whole_file.py
FAILED tests/test_price.py::test_band@test_price
FAILED tests/test_price.py::test_row[p50 (USD): threaded_rod]@test_price
==================== 3 failed, 400 passed, 1 error in 61.20s ====================
"""


def test_the_red_tests_are_read_from_the_summary_each_once():
    assert reseed_proof.red_tests(SUMMARY) == [
        "tests/test_catalog_golden.py::test_lines",
        "tests/test_sku_drawings.py::test_pinned[M6x1 x 10mm, handle-less]",
        "tests/test_facet_control_rule.py::test_band",
        "tests/test_whole_file.py",
        "tests/test_price.py::test_band",
        "tests/test_price.py::test_row[p50 (USD): threaded_rod]",
    ]


def test_a_green_run_has_no_red_test():
    assert reseed_proof.red_tests("....\n==== 4 passed in 1.00s ====\n") == []


def test_the_proof_judges_the_census_bands_at_the_default_seed_only():
    """The 2026-11-06 ruling on #50, option (b): a band row is a property of the default seed,
    so the proof deselects the tests marked ``default_seed_band`` and runs every other one."""
    argv = reseed_proof.pytest_argv(Path("/tree"), "4", ["tests/test_price.py"])
    end = argv.index("--")
    assert argv[end - 2 : end] == ["-m", "not default_seed_band"]
    assert argv[end + 1 :] == ["tests/test_price.py"]


#: The tests that hold a census band or floor on one draw of the default seed, each red on seed
#: 20260918 (``reseed_proof.py --seed 20260918``): the 2026-11-04T23:27 gate's Deliverables 1
#: and 2 on #50, with the brand share floor of ``test_catalog_brands_voice`` that went red since.
#: Multi-seed robustness of these rows is its own issue.
DEFAULT_SEED_BANDS = {
    "tests/test_price.py::test_every_price_row_is_within_its_band_or_pinned_at_the_default_size",
    "tests/test_price.py::test_scaling_every_price_breaks_every_p50_row",
    "tests/test_price.py::test_widening_or_narrowing_each_types_spread_breaks_its_spread_row",
    "tests/test_price.py::test_the_kit_p90_p10_is_in_band_at_100k",
    "tests/test_price.py::test_each_price_row_is_within_its_band_or_its_pin_holds_at_100k",
    "tests/test_set_screw_length_row_in_band_69b.py::test_a_set_screws_size_and_length_rows_are_both_in_band",
    "tests/test_declared_copy_roles_75.py::test_a_set_screw_reads_its_declared_period_for_the_fine_pitch_near_miss",
    "tests/test_pack_quantity.py::test_the_builds_median_pack_is_the_census_median",
    "tests/test_catalog_brands_voice.py::test_each_type_keeps_its_distinct_spec_floor_at_100k",
    "tests/test_catalog_brands_voice.py::test_no_brand_holds_a_tenth_of_100k_or_under_three_in_a_thousand",
}


def _marked(path: Path) -> set[str]:
    """The tests of ``path`` that carry ``@pytest.mark.default_seed_band``, read from its source."""
    tree = ast.parse(path.read_text("utf-8"))
    return {
        f"tests/{path.name}::{node.name}"
        for node in tree.body
        if isinstance(node, ast.FunctionDef)
        and any(
            reseed_proof.DEFAULT_SEED_BAND in ast.unparse(decorator)
            for decorator in node.decorator_list
        )
    }


def test_the_tests_judged_at_the_default_seed_only_are_the_census_bands_and_floors():
    """A band row the proof leaves out is one the ruling names, and each one it names is out:
    a new mark is a reviewed change to this list, never a way to quiet a moved seed."""
    marked = set().union(*(_marked(path) for path in sorted((REPO / "tests").glob("test_*.py"))))
    assert marked == DEFAULT_SEED_BANDS
