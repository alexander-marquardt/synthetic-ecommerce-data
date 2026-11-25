"""Every direct dependency is on a checked-in list that only shrinks (#1106).

``.github/scripts/check_dependency_allowlist.py`` is elastic/prism's script byte for byte, and
``.github/workflows/dependency-allowlist.yaml`` runs the check step of core's reusable workflow,
which this public repository cannot call. The refusals are read by running the committed steps on
a throwaway repository, as a pull request's run would. Docs: docs/dependency-allowlist.md.
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "check_dependency_allowlist.py"
RETRY = ROOT / ".github" / "vuln-gate" / ".github" / "scripts" / "retry.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "dependency-allowlist.yaml"
ALLOWLIST = ROOT / ".github" / "dependency_allowlist.json"

#: Where the copy comes from: the elastic/prism commit and the blob id `git ls-tree` prints there.
CORE_COMMIT = "687e078cb60f5c96d2315f9aca043e6ba615bef7"
CORE_BLOB = "2e25f4c2b922661c5802ba716f1f313053bc6128"
#: The SHA-256 of the check step's ``run`` in core's reusable-dependency-gate.yaml there.
STEP_SHA256 = "f13b5f9b9f3260e49b632826003cab43d0a2cb23865786846b43f07f609bd5bb"

PYPROJECT = """\
[project]
name = "fixture"
version = "0"
dependencies = [{runtime}]
"""
LOCK = "version = 1\n" + "".join(f'[[package]]\nname = "p{n}"\n' for n in range(2))


def _installed(path: Path) -> Path:
    assert path.is_file(), f"{path.relative_to(ROOT)} is missing: the gate is not installed"
    return path


def _job() -> dict:
    return yaml.safe_load(_installed(WORKFLOW).read_text(encoding="utf-8"))["jobs"][
        "dependency-allowlist"
    ]


def _check(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(_installed(SCRIPT)), *args],
        capture_output=True,
        text=True,
        check=False,
    )


# -- the copy and this repository's list ----------------------------------------------------


def test_the_script_is_cores_byte_for_byte() -> None:
    data = _installed(SCRIPT).read_bytes()
    blob = hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()
    assert blob == CORE_BLOB, f"not elastic/prism's script at {CORE_COMMIT}: docs, 'Update it'"


def test_the_check_step_is_cores_word_for_word() -> None:
    run = _job()["steps"][-1]["run"]
    assert hashlib.sha256(run.encode()).hexdigest() == STEP_SHA256


def test_the_list_names_every_direct_dependency_of_this_repository() -> None:
    manifests = json.loads(_installed(ALLOWLIST).read_text(encoding="utf-8"))["manifests"]
    assert set(manifests) == {"pyproject.toml"}
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    declared = {
        "build-system.requires": project["build-system"]["requires"],
        "project.dependencies": project["project"]["dependencies"],
        "dependency-groups.dev": project["dependency-groups"]["dev"],
    }
    listed = manifests["pyproject.toml"]
    assert {g: len(names) for g, names in listed.items()} == {
        g: len(names) for g, names in declared.items()
    }
    done = _check("--root", str(ROOT))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "| `uv.lock` |" in done.stdout


# -- the workflow ---------------------------------------------------------------------------


def test_the_gate_runs_on_every_pull_request_on_its_labels_and_on_every_push_to_main() -> None:
    doc = yaml.safe_load(_installed(WORKFLOW).read_text(encoding="utf-8"))
    on = doc[True] if True in doc else doc["on"]  # YAML 1.1 reads a bare `on` as True
    # The approval is a label, so adding or removing it must run the check again.
    assert {"opened", "synchronize", "reopened", "labeled", "unlabeled"} <= set(
        on["pull_request"]["types"]
    )
    assert "paths" not in on["pull_request"]
    assert on["push"]["branches"] == ["main"]
    job = doc["jobs"]["dependency-allowlist"]
    assert job["name"] == "dependency-allowlist"
    assert not {"if", "continue-on-error"} & set(job)
    assert doc["permissions"] == {"contents": "read"}


def test_a_merge_needs_the_gate_green_by_its_check_name() -> None:
    required = json.loads((ROOT / ".github" / "required-checks.json").read_text(encoding="utf-8"))
    name = _job()["name"]
    assert name in required["required"], f"{name} is not a check a merge needs"


def test_merge_pr_local_ci_skips_the_gate() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    import local_ci_jobs

    assert WORKFLOW.name in local_ci_jobs.NOT_A_CHECK


def test_ruff_leaves_the_copy_alone() -> None:
    ruff = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))["tool"]["ruff"]
    assert ".github/scripts/check_dependency_allowlist.py" in ruff["extend-exclude"]


# -- what the committed steps refuse --------------------------------------------------------


def _git(cwd: Path, *args: str) -> str:
    identity = ["-c", "user.name=t", "-c", "user.email=t@example.invalid"]
    return subprocess.run(
        ["git", *identity, *args], cwd=cwd, capture_output=True, text=True, check=True
    ).stdout.strip()


class PullRequest:
    """A repository holding the copied gate, at ``caller/`` of a workspace, and its base commit."""

    def __init__(self, tmp: Path) -> None:
        self.workspace = tmp / "workspace"
        self.temp = tmp / "runner-temp"
        self.temp.mkdir()
        self.caller = self.workspace / "caller"
        for source in (_installed(SCRIPT), RETRY):
            target = self.caller / source.relative_to(ROOT)
            target.parent.mkdir(parents=True)
            shutil.copy(source, target)
        self.depend("numpy")
        self.write("uv.lock", LOCK)
        self.write_list()
        _git(self.caller, "init", "-q")
        _git(self.caller, "add", "-A")
        _git(self.caller, "commit", "-q", "-m", "base")
        self.base = _git(self.caller, "rev-parse", "HEAD")
        # The base fetch reads the repository itself, as a run reads GitHub's.
        _git(self.caller, "remote", "add", "origin", str(self.caller))

    def write(self, rel: str, text: str) -> None:
        (self.caller / rel).write_text(text, encoding="utf-8")

    def depend(self, *names: str) -> None:
        runtime = ", ".join(f'"{name}>=1"' for name in names)
        self.write("pyproject.toml", PYPROJECT.format(runtime=runtime))

    def write_list(self) -> None:
        done = _check("--root", str(self.caller), "--write")
        assert done.returncode == 0, done.stdout + done.stderr

    def run(self, labels: str = "", event: str = "pull_request") -> subprocess.CompletedProcess:
        env = {
            **os.environ,
            "GITHUB_WORKSPACE": str(self.workspace),
            "RUNNER_TEMP": str(self.temp),
            "GITHUB_STEP_SUMMARY": str(self.temp / "summary.md"),
            "GITHUB_EVENT_NAME": event,
            "PR_BASE_SHA": self.base if event == "pull_request" else "",
            "PR_LABELS": labels,
        }
        done = None
        for step in _job()["steps"]:
            if "run" not in step:
                continue
            env["ALLOWLIST"] = step.get("env", {}).get("ALLOWLIST", "")
            cwd = self.workspace / step.get("working-directory", "")
            done = subprocess.run(
                ["bash", "-e", "-o", "pipefail", "-c", step["run"]],
                cwd=cwd,
                env=env,
                capture_output=True,
                text=True,
                check=False,
            )
            if done.returncode != 0:
                break
        assert done is not None, "the job runs no step"
        return done


@pytest.fixture
def pull_request(tmp_path: Path) -> PullRequest:
    return PullRequest(tmp_path)


def test_a_pull_request_that_changes_no_dependency_passes(pull_request: PullRequest) -> None:
    done = pull_request.run()
    assert done.returncode == 0, done.stdout + done.stderr
    assert "| `uv.lock` | 2 |" in (pull_request.temp / "summary.md").read_text()


def test_a_dependency_off_the_list_is_refused_even_with_the_label(
    pull_request: PullRequest,
) -> None:
    pull_request.depend("numpy", "left-pad")
    done = pull_request.run(labels="dependency-approved")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "`left-pad` (pyproject.toml, project.dependencies)" in done.stderr
    # A push has no labels and no base: the list still equals the manifests.
    assert pull_request.run(event="push").returncode == 1


def test_a_new_entry_needs_the_approval_label(pull_request: PullRequest) -> None:
    pull_request.depend("numpy", "left-pad")
    pull_request.write_list()
    refused = pull_request.run(labels="lane:security,dependencies")
    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "`left-pad`" in refused.stderr and "dependency-approved" in refused.stderr
    assert "names 2 direct dependencies, up from the base's 1" in refused.stderr
    approved = pull_request.run(labels="lane:security,dependency-approved")
    assert approved.returncode == 0, approved.stdout + approved.stderr


def test_a_lock_with_more_packages_than_the_base_needs_the_approval_label(
    pull_request: PullRequest,
) -> None:
    pull_request.write("uv.lock", LOCK + '[[package]]\nname = "pulled-in"\n')
    refused = pull_request.run()
    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "lock `uv.lock` rises to 3 packages from the base's 2" in refused.stderr
    assert pull_request.run(labels="dependency-approved").returncode == 0


def test_a_removal_must_lower_the_list_in_the_same_pull_request(
    pull_request: PullRequest,
) -> None:
    pull_request.depend()
    refused = pull_request.run()
    assert refused.returncode == 1, refused.stdout + refused.stderr
    assert "a stale entry" in refused.stderr and "`numpy`" in refused.stderr
    pull_request.write_list()
    lowered = pull_request.run()
    assert lowered.returncode == 0, lowered.stdout + lowered.stderr
    assert "Direct dependencies on the list: 0." in lowered.stdout
