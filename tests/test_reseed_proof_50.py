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
