"""The pinned unit declaration is the industrial deployment's own, untouched.

``tests/data/industrial_canonical_units.yaml`` is a copy of the deployment's
``canonical_units:`` block, and the contract test takes every unit's kind and
size from it. Two things can make it lie, and they are checked in two places:

* A HAND EDIT. The pin records the sha256 of its own block, written by
  ``scripts/check_industrial_unit_pin.py --refresh``. Checked here, on every
  run, with no network: an edited block no longer matches its digest.
* DRIFT from the source, a PRIVATE repository this repository's CI cannot read.
  A pytest that needs it could only skip in CI, a gate that never bites where
  merges are decided, so that comparison is the script's, run by hand (see the
  README's "The pinned unit declaration"). Its decision logic is tested here
  offline, against sources built from the pin itself.
"""

from __future__ import annotations

import hashlib
import importlib.util
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

import yaml

from industrial_units import PIN, Unit, parse, pinned

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "check_industrial_unit_pin.py"


def _script():
    spec = importlib.util.spec_from_file_location("check_industrial_unit_pin", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PIN_TEXT = PIN.read_text(encoding="utf-8")
BLOCK = PIN_TEXT[PIN_TEXT.index("\ncanonical_units:") + 1 :]


def _source(block: str, after: str = "unit_vocabulary:\n  x: 1\n") -> str:
    """A customization file holding ``block`` between other top-level keys."""
    return f"# header\nsearch_config: queries/x.json\n\n{block}\n# next\n{after}"


# --- the pin's own digest: runs everywhere ----------------------------------


def test_the_pins_digest_matches_its_block():
    recorded = (yaml.safe_load(PIN_TEXT).get("pin") or {}).get("sha256")
    # computed here, not by the script, so a wrong digest function cannot agree with itself
    assert recorded == hashlib.sha256(BLOCK.encode("utf-8")).hexdigest(), (
        f"{PIN.name} was edited by hand: refresh it with "
        "scripts/check_industrial_unit_pin.py --refresh"
    )
    assert _script().hash_problems(PIN_TEXT) == []


def test_a_planted_edit_to_the_pin_is_red():
    edited = PIN_TEXT.replace('TPI: { reciprocal: "127/5" }', 'TPI: { reciprocal: "1" }')
    assert edited != PIN_TEXT, "the plant did not apply"
    assert _script().hash_problems(edited), "an edited unit size passed the digest check"


def test_a_planted_edit_to_a_comment_is_red():
    edited = PIN_TEXT.replace("# MILLIMETRES", "# MILLIMETERS", 1)
    assert edited != PIN_TEXT, "the plant did not apply"
    assert _script().hash_problems(edited), "the pin is verbatim, comments included"


def test_a_planted_stale_digest_is_red():
    recorded = yaml.safe_load(PIN_TEXT)["pin"]["sha256"]
    older = hashlib.sha256(BLOCK.replace('C78: "1"', 'C78: "2"').encode()).hexdigest()
    stale = PIN_TEXT.replace(recorded, older)
    assert stale != PIN_TEXT, "the plant did not apply"
    assert _script().hash_problems(stale), "a digest of an older block passed"


def test_a_pin_without_a_digest_is_red():
    recorded = yaml.safe_load(PIN_TEXT)["pin"]["sha256"]
    bare = PIN_TEXT.replace(f"  sha256: {recorded}\n", "")
    assert bare != PIN_TEXT, "the plant did not apply"
    assert _script().hash_problems(bare), "a pin with no digest passed"


# --- the script's comparison with the source, offline ------------------------


def test_the_script_renders_the_pin_it_checks():
    """``--refresh`` writes exactly this file, so a refresh is the only way to make one."""
    script, provenance = _script(), yaml.safe_load(PIN_TEXT)["pin"]
    assert script.render(provenance["commit"], provenance["blob"], BLOCK) == PIN_TEXT


def test_the_block_is_cut_out_of_a_source_verbatim():
    script = _script()
    assert script.block_of(_source(BLOCK)) == BLOCK
    # a column-0 comment after the block introduces the NEXT key, not this one
    assert "# next" not in script.block_of(_source(BLOCK))


def _compare(source_at_pin: str, source_now: str, blob: str | None = None) -> list[str]:
    provenance = yaml.safe_load(PIN_TEXT)["pin"]
    return _script().compare(
        PIN_TEXT,
        source_at_pin=source_at_pin,
        blob_at_pin=blob or provenance["blob"],
        source_now=source_now,
    )


def test_a_source_that_matches_is_green():
    assert _compare(_source(BLOCK), _source(BLOCK)) == []


def test_a_change_outside_the_block_is_green():
    assert _compare(_source(BLOCK), _source(BLOCK, after="unit_vocabulary:\n  y: 2\n")) == []


def test_a_source_whose_block_moved_on_is_red():
    moved = BLOCK.replace('MMT: "1", TPI', 'MMT: "1", CMT: "10", TPI')
    assert moved != BLOCK, "the plant did not apply"
    problems = _compare(_source(BLOCK), _source(moved))
    assert problems and "--refresh" in " ".join(problems)


def test_a_source_whose_block_changed_only_a_comment_is_red():
    moved = BLOCK.replace("# MILLIMETRES", "# MILLIMETERS", 1)
    assert _compare(_source(BLOCK), _source(moved))


def test_a_pin_that_misnames_its_commit_is_red():
    """The block at the recorded commit must be the pin's, and so must the blob."""
    elsewhere = BLOCK.replace('C78: "1"', 'C78: "2"')
    assert _compare(_source(elsewhere), _source(BLOCK))
    assert _compare(_source(BLOCK), _source(BLOCK), blob="0" * 40)


def test_an_unreadable_source_fails_loudly(tmp_path):
    """No ``gh`` on the PATH: the script exits non-zero and says so, never passes."""
    env = {**os.environ, "PATH": str(tmp_path)}
    done = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, env=env, check=False
    )
    assert done.returncode == 2, done.stdout + done.stderr
    assert "cannot read" in done.stderr, done.stderr


# --- the parser the contract test reads the pin with --------------------------


def test_the_parser_reads_a_reciprocal_as_a_count_per_size():
    """``{reciprocal: <size>}`` divides; a plain size multiplies."""
    units = parse({"k": {"code": "A", "units": {"A": "1", "B": "3", "C": {"reciprocal": "6"}}}})
    assert units["B"] == Unit("k", Fraction(3))
    assert units["C"] == Unit("k", Fraction(6), reciprocal=True)
    assert units["B"].canonical(Fraction(4)) == 12
    assert units["C"].canonical(Fraction(4)) == Fraction(3, 2)


def test_the_pin_parses():
    assert pinned(), "the pinned block declares no unit"
