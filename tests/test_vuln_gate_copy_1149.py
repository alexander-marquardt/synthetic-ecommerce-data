"""This repository runs elastic/prism's vulnerability gate as a standalone copy (#1149).

The copy is rendered by elastic/prism's ``scripts/sister_vuln_gate.py write`` and committed
as is: ``.github/vuln-gate/`` (the gate's scripts, ``verify_pin.py`` and ``PIN.json``) and
``.github/workflows/vuln-gate.yaml``. The allowlist ``.github/vuln-allowlist.json`` is this
repository's own. These tests hold what a change here could break: the pin, the workflow's
triggers, the allowlist's shape, the required check a merge waits for, and ruff leaving the
vendored scripts alone (they are linted in core, under core's Python, and a fix here would break
the pin). Docs: docs/vulnerability-gate.md.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
MIRROR = ROOT / ".github" / "vuln-gate"
WORKFLOW = ROOT / ".github" / "workflows" / "vuln-gate.yaml"
ALLOWLIST = ROOT / ".github" / "vuln-allowlist.json"


def test_the_vendored_copy_matches_its_pin() -> None:
    pin = MIRROR / "verify_pin.py"
    assert pin.is_file(), f"{pin.relative_to(ROOT)} is missing: the copy is not installed"
    done = subprocess.run(
        [sys.executable, str(pin)], cwd=ROOT, capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stdout + done.stderr


def test_the_gate_runs_on_every_pull_request_and_every_push_to_main() -> None:
    assert WORKFLOW.is_file(), "the vuln-gate workflow is missing"
    doc = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    on = doc[True] if True in doc else doc["on"]  # YAML 1.1 reads a bare `on` as True
    assert "pull_request" in on
    assert on["push"]["branches"] == ["main"]
    assert doc["jobs"]["vuln-gate"]["name"] == "vuln-gate"


def test_every_allowlist_entry_names_advisory_package_issue_and_expiry() -> None:
    assert ALLOWLIST.is_file(), "the repository's allowlist is missing"
    entries = json.loads(ALLOWLIST.read_text(encoding="utf-8"))["entries"]
    assert isinstance(entries, list)
    for entry in entries:
        assert set(entry) >= {"advisory", "package", "issue", "expires"}, entry


def test_a_merge_needs_the_gate_green_by_its_check_name() -> None:
    required = json.loads((ROOT / ".github" / "required-checks.json").read_text(encoding="utf-8"))
    job = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["vuln-gate"]
    assert job["name"] in required["required"], "vuln-gate is not a check a merge needs"


def test_merge_pr_local_ci_skips_the_gate_and_still_reads_every_other_workflow() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import local_ci_jobs

    assert WORKFLOW.name in local_ci_jobs.NOT_A_CHECK
    jobs = local_ci_jobs.load_jobs(ROOT / ".github" / "workflows")
    assert "vuln-gate" not in jobs
    assert "lint" in jobs


def test_ruff_leaves_the_vendored_copy_alone() -> None:
    ruff = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["ruff"]
    assert ".github/vuln-gate" in ruff.get("extend-exclude", [])
