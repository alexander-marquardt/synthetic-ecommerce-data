"""scripts/hooks.py runs the hook set .pre-commit-config.yaml held, without pre-commit (#1108)."""

from __future__ import annotations

import importlib.util
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("hooks", ROOT / "scripts" / "hooks.py")
assert _spec is not None and _spec.loader is not None
hooks = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hooks)

#: Each hook id of the deleted .pre-commit-config.yaml, and the stage it ran at.
OLD_CONFIG = {
    "end-of-file-fixer": "pre-commit",
    "trailing-whitespace": "pre-commit",
    "check-yaml": "pre-commit",
    "ruff-check": "pre-commit",
    "no-ai-attribution": "commit-msg",
    "file-size-warning": "pre-commit",
    "prepush-gate": "pre-push",
}
CI_LINT = "uv run --locked python scripts/hooks.py run pre-commit --all-files"


def test_every_hook_of_the_old_config_has_its_counterpart_at_its_stage() -> None:
    assert hooks.HOOKS == OLD_CONFIG


def test_the_pre_commit_config_is_gone_and_nothing_installs_pre_commit() -> None:
    assert not (ROOT / ".pre-commit-config.yaml").exists()
    names = subprocess.run(["git", "-C", str(ROOT), "ls-files", "-z"], capture_output=True,
                           text=True, check=True).stdout.split("\0")
    installs = ("pre-commit install", "pre-commit run", "pre-commit/action",
                "install pre-commit", 'name = "pre-commit"', '"pre-commit>')
    hits = []
    for name in names:
        path = ROOT / name
        if not name or name.startswith("vendor/") or name == "tests/test_hooks_1108.py":
            continue
        if not path.is_file() or not hooks.is_text(path):
            continue
        text = path.read_text("utf-8", errors="replace")
        hits += [f"{name}: {needle}" for needle in installs if needle in text]
    assert hits == []


def test_ci_lint_job_runs_the_hook_script_over_every_file() -> None:
    ci = yaml.safe_load((ROOT / ".github" / "workflows" / "ci.yaml").read_text("utf-8"))
    runs = [step.get("run", "").strip() for step in ci["jobs"]["lint"]["steps"]]
    assert CI_LINT in runs


def test_end_of_file_fixer_ends_a_file_in_one_newline_and_fails(tmp_path: Path) -> None:
    cases = {b"x": b"x\n", b"x\n\n\n": b"x\n", b"\n\n": b"", b"x\r\n\r\n": b"x\r\n"}
    for before, after in cases.items():
        path = tmp_path / "a.txt"
        path.write_bytes(before)
        ok, out = hooks.end_of_file([path])
        assert (ok, path.read_bytes()) == (False, after), before
        assert "Fixing" in out
        assert hooks.end_of_file([path])[0] is True
    for good in (b"", b"x\n", b"x\r\n"):
        path.write_bytes(good)
        assert hooks.end_of_file([path]) == (True, "")


def test_trailing_whitespace_strips_line_ends_and_fails(tmp_path: Path) -> None:
    path = tmp_path / "a.md"
    path.write_bytes(b"a  \nb\t\r\nc \n  d")
    ok, _ = hooks.trailing_whitespace([path])
    assert (ok, path.read_bytes()) == (False, b"a\nb\r\nc\n  d")
    assert hooks.trailing_whitespace([path]) == (True, "")


def test_check_yaml_fails_a_file_that_does_not_parse(tmp_path: Path) -> None:
    bad, good = tmp_path / "bad.yaml", tmp_path / "good.yml"
    bad.write_text("a: [1,\n", encoding="utf-8")
    good.write_text("a: [1, 2]\n", encoding="utf-8")
    ok, out = hooks.check_yaml([bad, good])
    assert not ok and "bad.yaml" in out and "good.yml" not in out
    assert hooks.check_yaml([good]) == (True, "")


def test_ruff_check_fails_an_unused_import(tmp_path: Path) -> None:
    bad, good = tmp_path / "bad.py", tmp_path / "good.py"
    bad.write_text("import os\n", encoding="utf-8")
    good.write_text("VALUE = 1\n", encoding="utf-8")
    ok, out = hooks.ruff_check([bad])
    assert not ok and "F401" in out
    assert hooks.ruff_check([good])[0] is True


def test_the_fixers_leave_the_pinned_trees_alone_and_each_check_picks_its_files() -> None:
    assert not hooks.unpinned_text("golden-catalog/catalog.jsonl")
    assert not hooks.unpinned_text("vendor/prism/PIN.txt")
    assert hooks.unpinned_text("docs/golden-catalog/x.md")
    assert hooks.yaml_file(".github/workflows/ci.yaml") and not hooks.yaml_file("a.json")
    assert hooks.python_file("src/a.py") and not hooks.python_file("a.pyc")


def test_the_command_hooks_run_the_scripts_the_config_named() -> None:
    argv = {name: (stage, list(cmd[1:]) if cmd[0] == sys.executable else list(cmd))
            for name, (stage, cmd) in hooks.COMMAND_HOOKS.items()}
    assert argv == {
        "file-size-warning": ("pre-commit", ["scripts/file_size_gate.py", "--base", "origin/main",
                                             "--warn-at-commit"]),
        "no-ai-attribution": ("commit-msg", ["scripts/check_commit_msg.py"]),
        "prepush-gate": ("pre-push", ["bash", "scripts/prepush.sh", "--hook"]),
    }


def test_push_env_names_the_first_ref_that_is_not_a_delete() -> None:
    zeros, sha, old = hooks.ZEROS, "a" * 40, "b" * 40
    stdin = (f"(delete) {zeros} refs/heads/gone {old}\n"
             f"refs/heads/issue-1 {sha} refs/heads/issue-1 {zeros}\n")
    assert hooks.push_env(stdin, "origin") == {
        "PRE_COMMIT_LOCAL_BRANCH": "refs/heads/issue-1", "PRE_COMMIT_TO_REF": sha,
        "PRE_COMMIT_REMOTE_BRANCH": "refs/heads/issue-1", "PRE_COMMIT_FROM_REF": zeros,
        "PRE_COMMIT_REMOTE_NAME": "origin",
    }
    only_delete = hooks.push_env(f"(delete) {zeros} refs/heads/gone {old}\n", "origin")
    assert only_delete["PRE_COMMIT_TO_REF"] == zeros
    assert hooks.push_env("", "origin") == {}


# -- a planted repository: the installed hooks and CI's command ----------------------------

_FAKE_SIZE_GATE = "import sys\n\nprint('size gate', *sys.argv[1:])\n"
_FAKE_PREPUSH = ('#!/usr/bin/env bash\necho "gate $* to=$PRE_COMMIT_TO_REF '
                 'branch=$PRE_COMMIT_REMOTE_BRANCH"\nexit "${FAKE_GATE_RC:-0}"\n')


def _env() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("GIT_") and key not in ("SKIP", "HOOKS_UV")}
    # The hook's python3 is this test's (pyyaml, and the locked ruff beside it).
    env["PATH"] = f"{Path(sys.executable).parent}{os.pathsep}{env.get('PATH', '')}"
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    return env


def _git(repo: Path, *args: str, **env: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.com", *args],
        capture_output=True, text=True, check=False, env={**_env(), **env})


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    (root / "scripts").mkdir(parents=True)
    for name in ("hooks.py", "check_commit_msg.py"):
        shutil.copy2(ROOT / "scripts" / name, root / "scripts" / name)
    (root / "scripts" / "file_size_gate.py").write_text(_FAKE_SIZE_GATE, encoding="utf-8")
    (root / "scripts" / "prepush.sh").write_text(_FAKE_PREPUSH, encoding="utf-8")
    shutil.copy2(ROOT / "pyproject.toml", root / "pyproject.toml")  # this repo's ruff rules
    assert _git(tmp_path, "init", "-q", "-b", "main", str(root)).returncode == 0
    done = subprocess.run([sys.executable, "scripts/hooks.py", "install"], cwd=root,
                          capture_output=True, text=True, check=False, env=_env())
    assert done.returncode == 0, done.stdout + done.stderr
    return root


def _out(done: subprocess.CompletedProcess[str]) -> str:
    return done.stdout + done.stderr


def test_install_writes_the_three_hooks_and_keeps_a_hook_that_is_not_ours(repo: Path) -> None:
    hook_dir = repo / ".git" / "hooks"
    for stage in ("pre-commit", "commit-msg", "pre-push"):
        text = (hook_dir / stage).read_text("utf-8")
        assert hooks.MARK in text and f"run {stage}" in text
        assert os.access(hook_dir / stage, os.X_OK)
    (hook_dir / "pre-push").write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
    done = subprocess.run([sys.executable, "scripts/hooks.py", "install"], cwd=repo,
                          capture_output=True, text=True, check=False, env=_env())
    assert done.returncode == 1 and "--force" in _out(done)
    assert "mine" in (hook_dir / "pre-push").read_text("utf-8")


def test_a_planted_lint_failure_fails_the_commit_hook_and_the_ci_command(repo: Path) -> None:
    (repo / "bad.py").write_text("import os\n", encoding="utf-8")
    _git(repo, "add", "-A")
    done = _git(repo, "commit", "-q", "-m", "feat: an unused import")
    assert done.returncode != 0, _out(done)
    assert "ruff-check" in _out(done) and "F401" in _out(done)
    assert _git(repo, "rev-parse", "-q", "--verify", "HEAD").returncode != 0  # nothing committed

    (repo / "bad.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    done = _git(repo, "commit", "-q", "-m", "feat: a clean module")
    assert done.returncode == 0, _out(done)
    assert "size gate --base origin/main --warn-at-commit" in _out(done)

    ci = [sys.executable, "scripts/hooks.py", "run", "pre-commit", "--all-files"]
    clean = subprocess.run(ci, cwd=repo, capture_output=True, text=True, check=False, env=_env())
    assert clean.returncode == 0, _out(clean)
    (repo / "bad.py").write_text("import os\n", encoding="utf-8")
    red = subprocess.run(ci, cwd=repo, capture_output=True, text=True, check=False, env=_env())
    assert red.returncode == 1, _out(red)
    assert "F401" in _out(red) and "size gate" not in _out(red)


def test_the_commit_hook_judges_the_staged_text_and_puts_unstaged_edits_back(
    repo: Path,
) -> None:
    (repo / "mod.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(repo, "add", "-A")
    (repo / "mod.py").write_text("import os\n", encoding="utf-8")  # unstaged, and red
    done = _git(repo, "commit", "-q", "-m", "feat: the staged module")
    assert done.returncode == 0, _out(done)
    assert (repo / "mod.py").read_text("utf-8") == "import os\n"
    assert _git(repo, "show", "HEAD:mod.py").stdout == "VALUE = 1\n"


def test_the_commit_msg_hook_refuses_an_ai_trailer(repo: Path) -> None:
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "-A")
    trailer = "Co-Authored-By: " + "Cla" + "ude <noreply@example.com>"
    done = _git(repo, "commit", "-q", "-m", f"feat: a\n\n{trailer}")
    assert done.returncode != 0 and "no-ai-attribution" in _out(done), _out(done)
    assert _git(repo, "commit", "-q", "-m", "feat: a").returncode == 0


def test_the_pre_push_hook_runs_the_gate_with_the_pushed_refs(repo: Path, tmp_path: Path) -> None:
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    _git(repo, "add", "-A")
    assert _git(repo, "commit", "-q", "-m", "feat: a").returncode == 0
    head = _git(repo, "rev-parse", "HEAD").stdout.strip()
    remote = tmp_path / "remote.git"
    assert _git(tmp_path, "init", "-q", "--bare", str(remote)).returncode == 0
    done = _git(repo, "push", str(remote), "main:issue-1")
    assert done.returncode == 0, _out(done)
    assert f"gate --hook to={head} branch=refs/heads/issue-1" in _out(done)
    _git(repo, "commit", "-q", "--allow-empty", "-m", "feat: b")
    red = _git(repo, "push", str(remote), "main:issue-1", FAKE_GATE_RC="1")
    assert red.returncode != 0 and "prepush-gate" in _out(red)
    skipped = _git(repo, "push", str(remote), "main:issue-1", FAKE_GATE_RC="1",
                   SKIP="prepush-gate")
    assert skipped.returncode == 0, _out(skipped)
