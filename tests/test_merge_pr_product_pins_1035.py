"""The pins that hold ``scripts/merge_pr.sh`` to the product (#1035).

``tests/test_merge_pr.py`` and ``tests/test_merge_pr_github_ci_348.py`` drive the script in
throwaway origins, 76 of the suite's 257 minutes, and a pull request runs them only when it
changes the script or what the script runs (``SELECTED_ONLY_BY`` in ``scripts/ci_select.py``).
The product can still break the script without touching it: a rebuild that writes a file the
``GENERATED`` list lacks, a renamed rebuild module or freshness test, a real type that takes a
block the two-PR merge case derives. These checks run in seconds and are selected by the usual
rules, so a product change runs them.
"""

from __future__ import annotations

import subprocess
import sys

from synthetic_ecommerce_data import generate_cli as cli
from synthetic_ecommerce_data.core import price
from test_merge_pr import (
    _ADDED_TYPES,
    _ALL_FRESH,
    _PINS,
    REPO,
    SCRIPT,
    SCRIPT_PARTS,
    _git,
    _printed,
)


def test_no_real_type_takes_a_block_the_merge_test_s_added_types_derive() -> None:
    """The two-PR merge test adds keys whose derived blocks must stay free of real types.

    chain_lubricants (#462) declared block 7423, the block ball_stock_quartz derives, and the
    merge test's build stopped on the collision."""
    from synthetic_ecommerce_data.core import typespec
    from synthetic_ecommerce_data.domains.industrial import generate as industrial

    real = {key: typespec.block_of(key) for key in industrial.all_type_keys()}
    for key in _ADDED_TYPES:
        owners = [k for k, block in real.items() if block == typespec.part_number_block(key)]
        assert owners == [], (
            f"{key} derives block {typespec.part_number_block(key)}, held by {owners}"
        )


def test_the_generated_files_are_exactly_what_the_build_writes() -> None:
    """Only a file the rebuild rewrites may have a conflict resolved by it."""
    golden = _git(REPO, "ls-files", "golden-catalog").splitlines()
    field_map = cli.field_map_target().relative_to(REPO).as_posix()
    builds = price.BUILDS_FILE.relative_to(REPO).as_posix()
    want = sorted([*golden, field_map, builds, _PINS])
    assert sorted(_printed("--print-generated")) == want


def test_the_builds_rebuild_is_the_command_the_builds_module_names() -> None:
    """One module writes the pinned figures and the 100K sizes; the script runs it (#85)."""
    from synthetic_ecommerce_data.domains.industrial import measured_builds  # noqa: PLC0415

    assert price.BUILDS_FILE.is_file()
    assert f"python -m {measured_builds.__name__}" in measured_builds.REBUILD
    assert measured_builds.__name__ in (SCRIPT_PARTS / "config.sh").read_text()


def test_the_freshness_tests_are_real_tests_of_the_golden_files() -> None:
    """A renamed freshness test would silently turn the regeneration off."""
    printed = subprocess.run(
        [str(SCRIPT), "--print-freshness"], capture_output=True, text=True, check=False
    )
    assert printed.returncode == 0, printed.stderr
    named = printed.stdout.splitlines()
    assert sorted(named) == sorted(_ALL_FRESH), named
    collected = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-o",
            "addopts=",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            "-n",
            "0",
            *named,
        ],
        cwd=REPO,
        capture_output=True,
        text=True,
        check=False,
    )
    assert collected.returncode == 0, collected.stdout + collected.stderr
    for node in named:
        assert node in collected.stdout or f"{node}[" in collected.stdout, (
            f"{node} is not collected"
        )
