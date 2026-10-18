"""A feature PR never edits the golden stats files; the release step rolls them (gen#373).

``golden-retail/stats.json`` and ``golden-catalog/stats.json`` are build output that
moves with every type or grocery PR. Committed by each PR, they were the one file 16 of
the 21 open PRs shared on 10-18, so every merge conflicted the rest.

Now a PR commits neither. CI rewrites both from the PR's own build before the tests read
them (``scripts/roll_stats.py``), ``scripts/merge_pr.sh`` is the release step that commits
the rebuilt files when the PR merges (its commit carries ``Rolled-By: scripts/merge_pr.sh``),
and ``scripts/check_no_stats_edit.py`` refuses a PR whose range edits either file without
that trailer on its tip. These tests hold the four ends.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yaml"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import roll_stats  # noqa: E402

RETAIL = "golden-retail/stats.json"
CATALOG = "golden-catalog/stats.json"
BOTH = (RETAIL, CATALOG)
TRAILER = "Rolled-By: scripts/merge_pr.sh"


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def _commit(repo: Path, message: str, files: dict[str, str]) -> str:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """``main`` holds both stats files; the checkout is on a feature branch."""
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    _commit(
        root,
        "base",
        {RETAIL: '{"a": 1}\n', CATALOG: '{"b": 1}\n', "golden-catalog/flat.jsonl": "{}\n"},
    )
    _git(root, "switch", "-q", "-c", "feature")
    return root


def _edit(repo: Path, message: str, path: str) -> str:
    target = repo / path
    target.write_text(target.read_text(encoding="utf-8") + "\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


def _lint(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / "check_no_stats_edit.py"), "--root", str(repo),
         "--base", "main", "--head", "HEAD"],
        capture_output=True,
        text=True,
    )


def test_the_rolled_files_are_the_two_golden_stats() -> None:
    assert roll_stats.ROLLED == BOTH


@pytest.mark.parametrize("path", BOTH)
def test_a_pr_that_edits_a_rolled_file_by_hand_is_refused(repo: Path, path: str) -> None:
    _edit(repo, "feat: a type", path)
    done = _lint(repo)
    assert done.returncode == 1, done.stdout + done.stderr
    out = done.stdout + done.stderr
    assert path in out
    assert f"git checkout main -- {path}" in out
    assert "scripts/merge_pr.sh" in out


def test_the_refusal_names_every_edited_file_and_the_command_that_shows_the_figures(
    repo: Path,
) -> None:
    _edit(repo, "feat: a type", RETAIL)
    _edit(repo, "feat: more", CATALOG)
    out = (lambda d: d.stdout + d.stderr)(_lint(repo))
    assert f"git checkout main -- {RETAIL}" in out and f"git checkout main -- {CATALOG}" in out
    assert "scripts/roll_stats.py" in out


def test_a_pr_that_edits_other_golden_files_and_sources_passes(repo: Path) -> None:
    _edit(repo, "feat: a type", "golden-catalog/flat.jsonl")
    _commit(repo, "feat: source", {"src/x.py": "x = 1\n"})
    done = _lint(repo)
    assert done.returncode == 0, done.stdout + done.stderr


def test_an_edit_that_a_later_commit_takes_back_is_no_edit(repo: Path) -> None:
    _edit(repo, "feat: a type", RETAIL)
    _git(repo, "checkout", "main", "--", RETAIL)
    _git(repo, "commit", "-q", "-m", "drop the stats edit")
    done = _lint(repo)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_main_that_moved_on_its_own_stats_is_not_the_prs_edit(repo: Path) -> None:
    """The range is ``base...head``: main rolled the stats after the PR branched."""
    _git(repo, "switch", "-q", "main")
    _edit(repo, f"Rebuild\n\n{TRAILER}", RETAIL)
    _git(repo, "switch", "-q", "feature")
    _edit(repo, "feat: a type", "golden-catalog/flat.jsonl")
    done = subprocess.run(
        [sys.executable, str(SCRIPTS / "check_no_stats_edit.py"), "--root", str(repo),
         "--base", "main", "--head", "feature"],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_tip_commit_with_the_release_trailer_passes(repo: Path) -> None:
    _edit(repo, "feat: a type", RETAIL)
    _edit(repo, f"Rebuild golden-catalog on the merge\n\n{TRAILER}", CATALOG)
    done = _lint(repo)
    assert done.returncode == 0, done.stdout + done.stderr


def test_the_trailer_must_be_a_trailer_not_a_line_in_the_prose(repo: Path) -> None:
    _edit(repo, f"feat: a type, {TRAILER}\n\nmore words", RETAIL)
    assert _lint(repo).returncode == 1
    _edit(repo, f"feat: more\n\n{TRAILER}\n\nand a closing paragraph", CATALOG)
    assert _lint(repo).returncode == 1


def test_a_trailer_naming_another_step_is_no_release(repo: Path) -> None:
    _edit(repo, "feat: a type\n\nRolled-By: me", RETAIL)
    assert _lint(repo).returncode == 1


def test_the_release_trailer_on_an_earlier_commit_does_not_cover_a_later_edit(
    repo: Path,
) -> None:
    _edit(repo, f"Rebuild\n\n{TRAILER}", RETAIL)
    _edit(repo, "feat: and then a hand edit", CATALOG)
    assert _lint(repo).returncode == 1


def test_roll_writes_both_files_through_the_two_builders(tmp_path: Path) -> None:
    made: list[str] = []

    def retail(root: Path) -> None:
        made.append("retail")
        (root / RETAIL).parent.mkdir(parents=True, exist_ok=True)
        (root / RETAIL).write_text("{}\n", encoding="utf-8")

    def catalog(root: Path) -> None:
        made.append("catalog")
        (root / CATALOG).parent.mkdir(parents=True, exist_ok=True)
        (root / CATALOG).write_text("{}\n", encoding="utf-8")

    rolled = roll_stats.roll(tmp_path, retail=retail, catalog=catalog)
    assert sorted(made) == ["catalog", "retail"]
    assert rolled == list(BOTH)


def test_roll_refuses_a_builder_that_leaves_a_rolled_file_unwritten(tmp_path: Path) -> None:
    with pytest.raises(SystemExit):
        roll_stats.roll(tmp_path, retail=lambda root: None, catalog=lambda root: None)


def _fake_root(tmp_path: Path, body: str) -> Path:
    script = tmp_path / "prototypes" / "retail_drawings" / "retail_figures.py"
    script.parent.mkdir(parents=True)
    script.write_text(body, encoding="utf-8")
    return tmp_path


def test_the_retail_builder_runs_the_roots_own_measurement(tmp_path: Path) -> None:
    root = _fake_root(
        tmp_path,
        "from pathlib import Path\n"
        "out = Path(__file__).resolve().parents[2] / 'golden-retail' / 'stats.json'\n"
        "out.parent.mkdir(exist_ok=True)\n"
        "out.write_text('{}')\n",
    )
    roll_stats.build_retail(root)
    assert (root / RETAIL).read_text(encoding="utf-8") == "{}"


def test_a_failing_retail_measurement_is_refused_with_its_output(tmp_path: Path) -> None:
    root = _fake_root(tmp_path, "import sys\nprint('boom')\nsys.exit(3)\n")
    with pytest.raises(SystemExit) as refused:
        roll_stats.build_retail(root)
    assert "boom" in str(refused.value)


def test_the_cli_lists_the_files_it_rolls() -> None:
    done = subprocess.run(
        [sys.executable, str(SCRIPTS / "roll_stats.py"), "--list"], capture_output=True, text=True
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.split() == list(BOTH)


def _jobs() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]


def _run_text(job: dict) -> str:
    return "\n".join(step.get("run", "") for step in job["steps"])


def test_ci_has_a_stats_roll_job_that_runs_the_lint_on_the_pr_range() -> None:
    job = _jobs().get("stats-roll")
    assert job is not None, "ci.yaml has no stats-roll job"
    assert "pull_request" in job["if"] and "workflow_dispatch" in job["if"]
    checkout = [s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout")][0]
    assert checkout["with"]["fetch-depth"] == 0, "the lint reads the range's history"
    text = _run_text(job)
    assert "scripts/check_no_stats_edit.py" in text
    assert "--base" in text and "--head" in text


def test_the_tests_job_rolls_the_stats_before_pytest_except_on_a_push() -> None:
    text = _run_text(_jobs()["tests"])
    assert "scripts/roll_stats.py" in text, "the tests job never rewrites the stats"
    assert text.index("scripts/roll_stats.py") < text.index("pytest "), "it must run first"
    roll_line = [line for line in text.splitlines() if "scripts/roll_stats.py" in line][0]
    assert "push" in roll_line, "a push to main must read the committed files, not rewrite them"


def test_the_merge_waits_for_the_stats_roll_check() -> None:
    done = subprocess.run(
        ["bash", str(SCRIPTS / "merge_pr.sh"), "--print-ci"], capture_output=True, text=True
    )
    assert done.returncode == 0, done.stderr
    assert "stats-roll" in done.stdout.split()


def test_every_commit_the_merge_script_makes_of_generated_files_carries_the_trailer() -> None:
    lines = [
        line
        for line in (SCRIPTS / "merge_pr.sh").read_text(encoding="utf-8").splitlines()
        if 'commit -q -m "' in line and "$work" in line
    ]
    assert len(lines) == 3, lines
    assert all('-m "$ROLLED_BY"' in line for line in lines), lines
    assert f'ROLLED_BY="{TRAILER}"' in (SCRIPTS / "merge_pr.sh").read_text(encoding="utf-8")
