"""The pre-push gate: this repository's cheap CI jobs, run before review (elastic/prism#11677).

``scripts/prepush.sh`` runs the mechanical rows of ``.github/workflows/ci.yaml`` on
the branch: lint, the commit-message rule, the file-size cap and the scans over
tracked files. The ``prepush-gate`` pre-push hook runs it on every push. Each case
below builds a small repository (the gate's own scripts, the vendored size gate, a
two-test scan set), plants one failure, and runs the gate in it; ``gh`` is a stub
answering the open-pull-request lookup and the Markdown render.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCAN_TESTS = "tests/test_us_spelling.py tests/test_vendored_core_pin_11683.py"
BIG = 1751  # one line over the 1,750 cap: a file the base already holds over it

# Spelled from parts: this file is itself a tracked file the scans read.
BRITISH = "colo" + "u" + "r"
AI_TRAILER = "Co-Authored-By: " + "Cla" + "ude <noreply@example.invalid>"

_GH_STUB = """#!/bin/sh
case "$1" in
  pr) [ "$FAKE_GH_PRS" = fail ] && exit 1; echo "${FAKE_GH_PRS:-0}" ;;
  api) cat "$GH_STUB_HTML" ;;
  *) exit 2 ;;
esac
"""


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        [
            "git",
            "-C",
            str(repo),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@example.invalid",
            "-c",
            "commit.gpgsign=false",
            *args,
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return done.stdout.strip()


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _lines(repo: Path, relative: str, count: int) -> None:
    path = repo / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"line {n}\n" for n in range(count)), encoding="utf-8")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """``origin/main`` is the base commit; the checkout is on branch ``issue-1``."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    for name in (
        "prepush.sh",
        "prepush.py",
        "check_commit_msg.py",
        "file_size_gate.py",
    ):
        (root / "scripts").mkdir(exist_ok=True)
        shutil.copy2(ROOT / "scripts" / name, root / "scripts" / name)
    (root / "scripts" / "file_size_cap.txt").write_text("cap 1750\n", encoding="utf-8")
    shutil.copytree(ROOT / "vendor", root / "vendor")
    for name in ("pyproject.toml", "uv.lock", ".gitignore"):
        shutil.copy2(ROOT / name, root / name)
    (root / ".ignore").write_text("vendor/\n", encoding="utf-8")
    (root / "tests").mkdir()
    for name in SCAN_TESTS.split():
        shutil.copy2(ROOT / name, root / name)
    _lines(root, "docs/big.md", BIG)
    (root / "src").mkdir()
    (root / "src" / "ok.py").write_text("VALUE = 1\n", encoding="utf-8")
    base = _commit(root, "base")
    _git(root, "update-ref", "refs/remotes/origin/main", base)
    _git(root, "switch", "-q", "-c", "issue-1")
    return root


def _gate(repo: Path, *argv: str, **env: str) -> subprocess.CompletedProcess[str]:
    stub = repo.parent / "bin"
    stub.mkdir(exist_ok=True)
    (stub / "gh").write_text(_GH_STUB, encoding="utf-8")
    (stub / "gh").chmod(0o755)
    if not (repo.parent / "body.html").exists():
        (repo.parent / "body.html").write_text("", encoding="utf-8")
    base_env = {
        key: value
        for key, value in os.environ.items()
        if not key.startswith(("PRE_COMMIT_", "PRISM_", "FAKE_GH", "AGENT_TMP", "GITHUB_"))
    }
    base_env.update(
        PATH=f"{stub}{os.pathsep}{base_env['PATH']}",
        GH_STUB_HTML=str(repo.parent / "body.html"),
        # The planted repository reuses this checkout's environment: no sync, no network.
        UV_PROJECT_ENVIRONMENT=str(ROOT / ".venv"),
        UV_NO_SYNC="1",
        UV_OFFLINE="1",
        PREPUSH_SCAN_TESTS=SCAN_TESTS,
    )
    base_env.update(env)
    return subprocess.run(
        ["bash", "scripts/prepush.sh", *argv],
        cwd=repo,
        env=base_env,
        capture_output=True,
        text=True,
        check=False,
    )


def _out(done: subprocess.CompletedProcess[str]) -> str:
    return done.stdout + done.stderr


def _row(out: str, verdict: str, name: str) -> bool:
    return re.search(rf"^    {verdict}  {re.escape(name)}\b", out, re.MULTILINE) is not None


def _hook(branch: str, repo: Path, **env: str) -> dict[str, str]:
    head = _git(repo, "rev-parse", "HEAD")
    return {
        "PRE_COMMIT_REMOTE_BRANCH": f"refs/heads/{branch}",
        "PRE_COMMIT_TO_REF": head,
        "PRE_COMMIT_FROM_REF": "0" * 40,
        **env,
    }


# -- by hand: blocking, with a review packet ---------------------------------


def test_a_clean_branch_passes_every_row_and_prints_a_review_packet(repo: Path) -> None:
    (repo / "src" / "new.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, "feat: a clean change")
    done = _gate(repo)
    out = _out(done)
    assert done.returncode == 0, out
    for name in ("lint", "commit-messages", "file-size", "tree-scans"):
        assert _row(out, "PASS", name), out
    assert "REVIEW PACKET" in out
    assert out.rstrip().splitlines()[-1].startswith("PREPUSH rc=0 failed=none log="), out


def test_the_log_is_saved_under_the_git_directory_and_named_on_the_last_line(repo: Path) -> None:
    _commit(repo, "feat: nothing to see")
    out = _out(_gate(repo))
    last = out.rstrip().splitlines()[-1:] or [""]
    assert "log=" in last[0], out
    log = last[0].split("log=", 1)[1]
    assert Path(log).parent == repo / ".git"
    assert Path(log).is_file()


def test_a_lint_error_fails_the_lint_row_and_the_other_rows_still_run(repo: Path) -> None:
    (repo / "src" / "bad.py").write_text("import os\n", encoding="utf-8")
    _commit(repo, "feat: an unused import")
    done = _gate(repo)
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "lint"), out
    assert _row(out, "PASS", "commit-messages"), out
    assert "REVIEW PACKET" not in out
    assert "failed=lint" in out.rstrip().splitlines()[-1], out


def test_an_ai_trailer_in_a_commit_message_fails_the_commit_message_row(repo: Path) -> None:
    (repo / "src" / "new.py").write_text("VALUE = 2\n", encoding="utf-8")
    _commit(repo, f"feat: a change\n\n{AI_TRAILER}")
    done = _gate(repo)
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "commit-messages"), out
    assert _row(out, "PASS", "lint"), out


def test_a_scan_over_tracked_files_fails_the_tree_scans_row(repo: Path) -> None:
    (repo / "docs" / "note.md").write_text(f"the {BRITISH} of it\n", encoding="utf-8")
    _commit(repo, "docs: a note")
    done = _gate(repo)
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "tree-scans"), out
    assert "test_no_tracked_file_spells_color_the_british_way" in out


def test_a_scan_set_in_which_no_test_ran_fails_the_row(repo: Path) -> None:
    (repo / "tests" / "test_nothing.py").write_text(
        "import pytest\n\n\n@pytest.mark.skip(reason='x')\ndef test_a():\n    pass\n",
        encoding="utf-8",
    )
    _commit(repo, "test: all skipped")
    done = _gate(repo, PREPUSH_SCAN_TESTS="tests/test_nothing.py")
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "tree-scans"), out
    assert "no test ran" in out


# -- the file-size row and the PR body ---------------------------------------


def _grow(repo: Path) -> None:
    _lines(repo, "docs/big.md", BIG + 1)
    _commit(repo, "docs: one line more")


def test_a_growth_with_no_body_is_a_warning_the_packet_does_not_count_as_judged(
    repo: Path,
) -> None:
    _grow(repo)
    done = _gate(repo)
    out = _out(done)
    assert done.returncode == 0, out
    assert _row(out, "WARN", "file-size"), out
    assert "--pr-body-file" in out
    assert "file-size: NOT JUDGED" in out


def test_a_growth_the_body_does_not_declare_fails_the_file_size_row(
    repo: Path, tmp_path: Path
) -> None:
    _grow(repo)
    body = tmp_path / "body.md"
    body.write_text("Refs #1\n", encoding="utf-8")
    done = _gate(repo, "--pr-body-file", str(body))
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "file-size"), out
    assert "docs/big.md" in out


def test_a_growth_the_body_declares_passes_the_file_size_row(repo: Path, tmp_path: Path) -> None:
    _grow(repo)
    body = tmp_path / "body.md"
    body.write_text("File-Size-Exception: `docs/big.md` - one line more\n", encoding="utf-8")
    (tmp_path / "body.html").write_text(
        "<p>File-Size-Exception: <code>docs/big.md</code> - one line more</p>\n",
        encoding="utf-8",
    )
    done = _gate(repo, "--pr-body-file", str(body))
    out = _out(done)
    assert done.returncode == 0, out
    assert _row(out, "PASS", "file-size"), out


# -- a gate that cannot judge never passes -----------------------------------


def test_no_origin_main_is_a_failure_that_names_the_fix(repo: Path) -> None:
    _git(repo, "update-ref", "-d", "refs/remotes/origin/main")
    done = _gate(repo)
    out = _out(done)
    assert done.returncode != 0, out
    assert "git fetch origin main" in out
    assert not _row(out, "PASS", "lint"), out


def test_only_runs_the_one_row_named(repo: Path) -> None:
    done = _gate(repo, "--only", "lint")
    out = _out(done)
    assert done.returncode == 0, out
    assert _row(out, "PASS", "lint"), out
    assert not _row(out, "PASS", "tree-scans"), out


def test_an_unknown_row_name_is_refused(repo: Path) -> None:
    done = _gate(repo, "--only", "nosuchrow")
    assert done.returncode == 2, _out(done)
    assert "nosuchrow" in _out(done)


# -- the hook: blocks only a branch with an open pull request ----------------


def _plant_lint_error(repo: Path) -> None:
    (repo / "src" / "bad.py").write_text("import os\n", encoding="utf-8")
    _commit(repo, "feat: an unused import")


def test_the_hook_blocks_a_red_branch_that_has_an_open_pull_request(repo: Path) -> None:
    _plant_lint_error(repo)
    done = _gate(repo, "--hook", **_hook("issue-1", repo), FAKE_GH_PRS="1")
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "lint"), out


def test_the_hook_lets_a_red_branch_with_no_pull_request_push_and_says_it_is_no_pass(
    repo: Path,
) -> None:
    _plant_lint_error(repo)
    done = _gate(repo, "--hook", **_hook("issue-1", repo), FAKE_GH_PRS="0")
    out = _out(done)
    assert done.returncode == 0, out
    assert _row(out, "FAIL", "lint"), out
    assert "ADVISORY" in out and "NOT A PASS" in out
    assert "REVIEW PACKET" not in out


def test_the_hook_blocks_when_it_cannot_tell_whether_a_pull_request_is_open(repo: Path) -> None:
    _plant_lint_error(repo)
    done = _gate(repo, "--hook", **_hook("issue-1", repo), FAKE_GH_PRS="fail")
    out = _out(done)
    assert done.returncode == 1, out
    assert "pull request" in out


def test_the_hook_blocks_a_push_to_main_without_asking_for_a_pull_request(repo: Path) -> None:
    _plant_lint_error(repo)
    done = _gate(repo, "--hook", **_hook("main", repo), FAKE_GH_PRS="0")
    assert done.returncode == 1, _out(done)


def test_a_wip_push_is_judged_on_the_commit_messages_only(repo: Path) -> None:
    _plant_lint_error(repo)
    done = _gate(repo, "--hook", **_hook("wip/task", repo))
    out = _out(done)
    assert done.returncode == 0, out
    assert _row(out, "PASS", "commit-messages"), out
    assert not _row(out, "FAIL", "lint") and not _row(out, "PASS", "lint"), out
    assert "NOT JUDGED (wip backup)" in out


def test_a_wip_push_with_an_ai_trailer_is_still_refused(repo: Path) -> None:
    _commit(repo, f"wip\n\n{AI_TRAILER}")
    done = _gate(repo, "--hook", **_hook("wip/task", repo))
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "commit-messages"), out


def test_a_push_of_a_commit_other_than_the_checkout_is_not_judged_as_the_checkout(
    repo: Path,
) -> None:
    _plant_lint_error(repo)
    other = _git(repo, "rev-parse", "HEAD~1")
    env = _hook("issue-1", repo, FAKE_GH_PRS="1")
    env["PRE_COMMIT_TO_REF"] = other
    done = _gate(repo, "--hook", **env)
    out = _out(done)
    assert done.returncode == 1, out
    assert _row(out, "FAIL", "pushed-commit"), out


def test_a_branch_delete_is_not_judged(repo: Path) -> None:
    env = _hook("issue-1", repo)
    env["PRE_COMMIT_TO_REF"] = "0" * 40
    done = _gate(repo, "--hook", **env)
    out = _out(done)
    assert done.returncode == 0, out
    assert "NOT JUDGED (branch delete)" in out


# -- one source: the rows are the CI jobs' own commands, the hook is installed


def _ci() -> dict:
    return yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yaml").read_text("utf-8"))


def _job_runs(job: str) -> str:
    return "\n".join(step.get("run", "") for step in _ci()["jobs"][job]["steps"])


def test_every_row_runs_a_command_its_named_ci_job_runs() -> None:
    done = subprocess.run(
        ["python3", str(ROOT / "scripts" / "prepush.py"), "--list"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    rows = [line.split("\t") for line in done.stdout.splitlines() if line.strip()]
    assert [row[0] for row in rows] == ["commit-messages", "lint", "file-size", "tree-scans"]
    for name, job, command in rows:
        assert job in _ci()["jobs"], f"{name}: no CI job {job!r}"
        assert command in _job_runs(job), f"{name}: CI job {job!r} does not run {command!r}"


def test_every_scan_test_the_gate_runs_exists() -> None:
    done = subprocess.run(
        ["python3", str(ROOT / "scripts" / "prepush.py"), "--list-scans"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    scans = done.stdout.split()
    assert scans, "the gate runs no scan"
    assert [name for name in scans if not (ROOT / name).is_file()] == []


def _precommit() -> dict:
    return yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text("utf-8"))


def test_pre_commit_installs_a_pre_push_hook_that_runs_the_gate() -> None:
    config = _precommit()
    assert "pre-push" in config["default_install_hook_types"]
    hooks = {
        hook["id"]: hook for repo in config["repos"] for hook in repo["hooks"]
    }
    gate = hooks.get("prepush-gate", {})
    assert gate.get("entry") == "bash scripts/prepush.sh --hook"
    assert gate.get("stages") == ["pre-push"]
    assert gate.get("always_run") is True


def test_the_other_hooks_stay_at_the_commit_stage() -> None:
    """Without ``default_stages`` every whitespace and lint hook would run again at push."""
    assert _precommit().get("default_stages") == ["pre-commit"]
