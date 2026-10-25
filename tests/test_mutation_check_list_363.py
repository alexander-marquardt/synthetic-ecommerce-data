"""``mutation_check.py --list`` names the bed without running it; the E501 exemption is gone (#363).

The bed lives in ``scripts/mutations/`` and the ``mutation_rows_*.py`` row files, found by
``mutation_row.all_mutations``; the runner itself is short. What was left of #363 was a way to read
the bed's names without paying for the green pre-check and every mutated run, and the per-file
``E501`` ignore that the runner carried from when it held the mutated source text inline.
"""

from __future__ import annotations

import subprocess
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

sys.path.insert(0, str(SCRIPTS))
import mutation_row  # noqa: E402  (scripts/ is not a package)


def _list(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "mutation_check.py"), "--list", *args],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
        check=False,
    )


def test_list_prints_every_mutation_name_in_bed_order_and_exits_zero() -> None:
    result = _list()
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [m.name for m in mutation_row.all_mutations()]


def test_list_runs_nothing() -> None:
    """Only names come out: no pre-check banner, no per-mutation marker, no summary."""
    result = _list()
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip(), "--list must print the names"
    assert "checking the suite" not in result.stdout
    assert "mutations caught" not in result.stdout


def test_list_with_only_prints_the_filtered_subset() -> None:
    names = [m.name for m in mutation_row.all_mutations()]
    needle = names[0].split(":")[0]
    expected = [n for n in names if needle in n]
    assert 0 < len(expected) < len(names), "the needle must pick a proper subset of the bed"
    result = _list("--only", needle)
    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == expected


def test_list_with_an_unmatched_only_prints_nothing_and_exits_zero() -> None:
    result = _list("--only", "no mutation is named this #363")
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""


def test_the_runner_carries_no_e501_exemption() -> None:
    config = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    ignores = config["tool"]["ruff"]["lint"].get("per-file-ignores", {})
    assert "scripts/mutation_check.py" not in ignores
