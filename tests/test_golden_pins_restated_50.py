"""A moved seed restates every figure a test pins on one build, through the one command (#50).

Slice 2's ``scripts/reseed_proof.py`` moved the default seed, ran the one command and listed what
went red: the golden slices of ``tests/data/golden_slices/``, which only each type test's own
``__main__`` rewrote, and figures a test typed after measuring them on one build (a type's SKU
count, the sizes a defect rewrote, the pack census counts...). These tests hold the restatement:

* the one command rewrites every golden slice, and a fixture written elsewhere (``--out``, slice 1's
  proof on a reseeded catalog) rewrites none;
* the fixture carries the figures of each module :data:`pinned.MODULES` names, and no test types
  one of them again.

A census band is not a pin: a test holds the build to the census's band, never to a copied figure.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

import type_gates

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import golden_pins  # noqa: E402  (scripts/ is not a package)
import measure_pins  # noqa: E402

KEY = "shackles"


@pytest.fixture
def stale(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A slices directory whose one slice is stale, and a fixture of one cheap measure."""
    slices = tmp_path / "golden_slices"
    slices.mkdir()
    (slices / f"{KEY}.jsonl").write_text("stale\n", "utf-8")
    monkeypatch.setattr(golden_pins, "SLICES", slices)
    monkeypatch.setattr(golden_pins, "MEASURES", {"x": lambda *_: {"n": 1}})
    monkeypatch.setattr(golden_pins, "PINS_PATH", tmp_path / "golden_pins.json")
    return slices / f"{KEY}.jsonl"


def test_the_one_command_rewrites_every_golden_slice(stale: Path) -> None:
    assert measure_pins.main([]) == 0
    written = stale.read_text("utf-8").splitlines()
    assert written == type_gates.default_records(KEY), (
        f"{stale.name} is not the default build of {KEY}: the one command left it stale"
    )


def test_a_fixture_written_elsewhere_rewrites_no_slice(stale: Path, tmp_path: Path) -> None:
    assert measure_pins.main(["--out", str(tmp_path / "elsewhere.json")]) == 0
    assert stale.read_text("utf-8") == "stale\n"


def test_the_fixture_carries_the_figures_of_one_build() -> None:
    pins = json.loads(golden_pins.PINS_PATH.read_text("utf-8"))
    assert "figures" in pins, f"no figure of one build is pinned; run {golden_pins.REGENERATE}"


#: Where a figure of one build used to be typed: the file and a pattern that matches it typed.
TYPED = {
    "shackles": (
        "tests/test_type_shackles.py",
        r"^(?:DEFAULT|LARGE)_(?:SKUS|PRODUCTS) = \d|rewritten == \[",
    ),
    "turnbuckles": ("tests/test_type_turnbuckles.py", r"^DEFAULT_\w+ = \d"),
    "cotter-pins": ("tests/test_type_cotter_pins.py", r"^DEFAULT_\w+ = \d|len\(rewritten\) == \d"),
    "retaining-rings": ("tests/test_type_retaining_rings_external.py", r"^DEFAULT_\w+ = \d"),
    "sprockets": (
        "tests/test_type_roller_chain_sprockets.py",
        r"^(?:DEFAULT_SKUS|MILLIMETRE_PITCHES) = \d|len\(units\) == \d|not in sizes\]\) == \d",
    ),
    "links": ("tests/test_type_roller_chain_links.py", r"^DEFAULT_\w+ = \d|== \(\d+, \d+\)"),
    "pillow-blocks": (
        "tests/test_type_pillow_block_bearings.py",
        r'^(?:DEFAULT|LARGE)_(?:SKUS|PRODUCTS) = \d|doc\["price_usd"\] == \d',
    ),
    "strand-sets": ("tests/test_type_roller_chain.py", r"^STRAND_SETS = \{"),
    "kit-counts": ("tests/test_price.py", r'\("default", \d+\), \("100K", \d+\)'),
    "pack-counts": ("tests/test_pack_quantity.py", r"^PUBLISHED = \{|\) == \(100\.0, \d"),
    "fit-spread": ("tests/test_fit_price_model.py", r"\), 2\) == \d"),
    "mutation-seed": ("scripts/mutations/core.py", r'"    seed: int = \d+"'),
}


@pytest.mark.parametrize("pin", TYPED)
def test_no_figure_of_one_build_is_typed(pin: str) -> None:
    path, pattern = TYPED[pin]
    text = (REPO / path).read_text("utf-8")
    found = [m.group(0) for m in re.finditer(pattern, text, re.MULTILINE)]
    assert found == [], (
        f"{path} types a figure of one build ({found[:3]}): a moved seed leaves it stale; "
        "read it from tests/pinned.py"
    )
