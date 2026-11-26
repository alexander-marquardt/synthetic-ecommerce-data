"""CI checks the dependency review table against the tree, by a pinned copy of core (#1180).

``docs/internals/appendix/dependency-review-table.md`` is rendered by elastic/prism's
``scripts/dependency_review.py``. Core is private and this repository holds no secret that
reads it, so the ``dependency-review`` job of ``ci.yaml`` runs a copy of the script under
``.github/dependency-review/``, pinned by ``PIN.json`` (the form of ``.github/vuln-gate/``,
#1149). These tests hold the pin, the copy's verdict on this tree and on a planted one, the job's
steps and the required check a merge waits for. Docs: docs/internals/dependency-review.md.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
COPY = ROOT / ".github" / "dependency-review"
SCRIPT = COPY / "scripts" / "dependency_review.py"
CI = ROOT / ".github" / "workflows" / "ci.yaml"
TABLE = "docs/internals/appendix/dependency-review-table.md"
WRITE = "uv run python .github/dependency-review/scripts/dependency_review.py --root . --write"


def _verify_pin():
    spec = importlib.util.spec_from_file_location("verify_pin_1180", COPY / "verify_pin.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _review(root: Path, mode: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), mode],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=120,
    )


def test_the_copy_matches_its_pin() -> None:
    done = subprocess.run(
        [sys.executable, str(COPY / "verify_pin.py")],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    pin = json.loads((COPY / "PIN.json").read_text(encoding="utf-8"))
    assert pin["source"] == "elastic/prism"
    assert set(pin["sha256"]) == set(_verify_pin().FILES)


@pytest.mark.parametrize(
    "change, refusal",
    [
        ("edit", "scripts/dependency_review.py: differs from its pin"),
        ("remove", "prism_engine/strict_yaml.py: gone"),
        ("add", "scripts/extra.py: not in the pin"),
    ],
)
def test_a_copy_edited_by_hand_is_refused_by_name(
    tmp_path: Path, change: str, refusal: str
) -> None:
    here = tmp_path / "dependency-review"
    shutil.copytree(COPY, here, ignore=shutil.ignore_patterns("__pycache__"))
    if change == "edit":
        with (here / "scripts" / "dependency_review.py").open("a", encoding="utf-8") as out:
            out.write("# a local fix\n")
    elif change == "remove":
        (here / "prism_engine" / "strict_yaml.py").unlink()
    else:
        (here / "scripts" / "extra.py").write_text("x = 1\n", encoding="utf-8")
    assert _verify_pin().problems(here) == [refusal]


def test_the_committed_table_matches_this_tree() -> None:
    done = _review(ROOT, "--check")
    assert done.returncode == 0, f"{done.stdout}{done.stderr}\nrun: {WRITE}"


def test_a_dependency_added_without_write_fails_the_check(tmp_path: Path) -> None:
    (tmp_path / "src" / "planted").mkdir(parents=True)
    (tmp_path / "src" / "planted" / "a.py").write_text("import numpy\n", encoding="utf-8")
    manifest = tmp_path / "pyproject.toml"
    manifest.write_text(
        '[project]\nname = "planted"\nversion = "0"\ndependencies = ["numpy"]\n', encoding="utf-8"
    )
    assert _review(tmp_path, "--write").returncode == 0
    assert _review(tmp_path, "--check").returncode == 0
    manifest.write_text(
        manifest.read_text(encoding="utf-8").replace('["numpy"]', '["numpy", "pyyaml"]'),
        encoding="utf-8",
    )
    done = _review(tmp_path, "--check")
    assert done.returncode == 1
    assert f"{TABLE} is stale" in done.stdout


def test_ci_checks_the_pin_installs_the_extras_and_runs_the_check_on_every_event() -> None:
    document = yaml.safe_load(CI.read_text(encoding="utf-8"))
    job = document["jobs"]["dependency-review"]
    assert "if" not in job, "the check runs on pull requests, pushes to main and dispatches alike"
    runs = [step.get("run", "") for step in job["steps"]]
    order = [
        next(i for i, run in enumerate(runs) if needle in run)
        for needle in ("uv sync --dev --locked", "verify_pin.py", "--extras", "--check")
    ]
    assert order == sorted(order), runs
    assert '--extra "$name"' in runs[order[2]]


def test_a_merge_needs_the_check_green() -> None:
    required = json.loads((ROOT / ".github" / "required-checks.json").read_text(encoding="utf-8"))
    assert "dependency-review" in required["required"]
    config = (ROOT / "scripts" / "merge_pr" / "config.sh").read_text(encoding="utf-8")
    line = next(row for row in config.splitlines() if row.startswith("REQUIRED_CI=("))
    assert "dependency-review" in line.removeprefix("REQUIRED_CI=(").rstrip(")").split()


def test_ruff_leaves_the_copied_files_alone() -> None:
    ruff = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["ruff"]
    excluded = ruff.get("extend-exclude", [])
    for directory in _verify_pin().COPIED_DIRS:
        assert f".github/dependency-review/{directory}" in excluded
