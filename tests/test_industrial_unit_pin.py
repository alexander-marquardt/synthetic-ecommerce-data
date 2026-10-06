"""The pinned unit declaration is the industrial deployment's own.

``tests/data/industrial_canonical_units.yaml`` is a copy, and a copy drifts. The
contract test takes every unit's kind and size from it, so a copy that no longer
matches the deployment would certify a catalog the deployment reads
differently. This compares the two.

The source is a PRIVATE repository that this repository's CI token cannot read.
The comparison runs wherever the source can be read: from a file named by
``INDUSTRIAL_CUSTOMIZATION_YAML``, or through an authenticated ``gh``. Where
neither works it is SKIPPED, naming why, and never passed.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from fractions import Fraction
from pathlib import Path

import pytest

from industrial_units import PIN, Unit, load_block, parse, pinned

SOURCE_REPO = "elastic/prism-industrial-products"
SOURCE_PATH = "src/prism_industrial_products/data/customization.yaml"


def _source_text() -> str | None:
    path = os.environ.get("INDUSTRIAL_CUSTOMIZATION_YAML")
    if path:
        return Path(path).read_text(encoding="utf-8")
    if shutil.which("gh") is None:
        return None
    result = subprocess.run(
        [
            "gh",
            "api",
            "-H",
            "Accept: application/vnd.github.raw",
            f"repos/{SOURCE_REPO}/contents/{SOURCE_PATH}",
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    return result.stdout if result.returncode == 0 else None


def test_the_pin_matches_the_deployments_declaration():
    source = _source_text()
    if source is None:
        pytest.skip(
            f"{SOURCE_REPO} is not readable here: set INDUSTRIAL_CUSTOMIZATION_YAML "
            "or authenticate gh to compare the pin with its source"
        )
    assert load_block(PIN.read_text(encoding="utf-8")) == load_block(source), (
        f"{PIN.name} no longer matches {SOURCE_REPO}/{SOURCE_PATH}: copy the "
        "canonical_units block again and update its commit and blob"
    )


def test_the_parser_reads_a_reciprocal_as_a_count_per_size():
    """``{reciprocal: <size>}`` divides; a plain size multiplies."""
    units = parse({"k": {"code": "A", "units": {"A": "1", "B": "3", "C": {"reciprocal": "6"}}}})
    assert units["B"] == Unit("k", Fraction(3))
    assert units["C"] == Unit("k", Fraction(6), reciprocal=True)
    assert units["B"].canonical(Fraction(4)) == 12
    assert units["C"].canonical(Fraction(4)) == Fraction(3, 2)


def test_the_pin_parses():
    assert pinned(), "the pinned block declares no unit"
