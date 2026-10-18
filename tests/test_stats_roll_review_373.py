"""The review round of the stats roll (gen#373): the apparel decoy table is rolled too, and the
steps the roll adds to CI are run, not read.

The first round pinned the roll by its text. The review found four gaps this file closes:

* ``scripts/roll_stats.py`` rewrites ``docs/retail-apparel-decoys.md`` (``retail_figures.py`` ends
  with ``decoy_apparel.write_doc()``), so a PR that forgot the table was green in CI and refused
  at the merge. The table is now a rolled file like the two stats: no PR commits it;
* the ``tests`` job's roll step and the ``stats-roll`` job's command are RUN here with a stub for
  ``uv`` and for the lint, so the ``push`` branch, ``--locked`` and the base and head values
  are pinned by what they do, not by a substring;
* the lint compares the trailer for equality, and the catalog half of the roll takes the build's
  ``stats.json``, not the committed one.
"""

from __future__ import annotations

import os
import re
import shutil
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

TABLE = "docs/retail-apparel-decoys.md"
STATS = "golden-retail/stats.json"


def _run_steps(job: str) -> list[dict]:
    jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
    return [step for step in jobs[job]["steps"] if "run" in step]


def _fill(run: str) -> str:
    """The step's script with the pull request's base and head values written in."""
    run = re.sub(
        r"\$\{\{\s*github\.event\.pull_request\.base\.sha \|\| inputs\.base\s*\}\}", "BASESHA", run
    )
    run = re.sub(
        r"\$\{\{\s*github\.event\.pull_request\.head\.sha \|\| inputs\.head\s*\}\}", "HEADSHA", run
    )
    return re.sub(r"\$\{\{.*?\}\}", "1", run)


# ---- the table is a rolled file ----------------------------------------------------------


def test_the_merge_script_regenerates_every_rolled_file() -> None:
    """``stage_generated`` dies on a file the rebuild rewrote that GENERATED does not list."""
    done = subprocess.run(
        ["bash", str(SCRIPTS / "merge_pr.sh"), "--print-generated"],
        capture_output=True,
        text=True,
        check=True,
    )
    listed = set(done.stdout.split())
    assert set(roll_stats.ROLLED) <= listed, set(roll_stats.ROLLED) - listed


def test_the_table_is_what_the_roll_writes_and_a_stale_one_does_not_survive_it(
    tmp_path: Path,
) -> None:
    """Run the real retail measurement in a copy: it rewrites the table and the stats."""
    shutil.copytree(
        ROOT / "prototypes" / "retail_drawings",
        tmp_path / "prototypes" / "retail_drawings",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "retail-apparel-decoys.md").write_text("STALE-MARKER\n", encoding="utf-8")
    roll_stats.build_retail(tmp_path)
    table = (tmp_path / TABLE).read_text(encoding="utf-8")
    assert "STALE-MARKER" not in table
    assert table.startswith("# Text-match decoys")
    assert (tmp_path / STATS).read_text(encoding="utf-8").startswith("{")
    assert set(roll_stats.ROLLED) == {STATS, "golden-catalog/stats.json", TABLE}


@pytest.mark.parametrize(
    "doc", ["README.md", "docs/adding-a-retail-type.md", "docs/new-type-quick-path.md"]
)
def test_the_docs_never_tell_a_builder_to_commit_the_table(doc: str) -> None:
    text = " ".join((ROOT / doc).read_text(encoding="utf-8").split())
    assert "commit the table" not in text, "the table is rolled; no PR commits it"
    assert "goes in the commit even when your type" not in text
    assert TABLE in text, f"{doc} must name the rolled table"


def test_the_readme_names_the_one_escape_and_who_may_write_it() -> None:
    text = " ".join((ROOT / "README.md").read_text(encoding="utf-8").split())
    assert "the one escape" in text
    assert "only `scripts/merge_pr.sh` writes" in text


# ---- the CI steps are run ---------------------------------------------------------------


def _tests_step(tmp_path: Path, event: str) -> list[str]:
    """Run the Tests step on a one-file plan with a ``uv`` that records its arguments."""
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "ci_shards.py").write_text(
        "print('shards=1')\nprint('tests/test_a.py')\n", encoding="utf-8"
    )
    log = tmp_path / "uv.log"
    stub = tmp_path / "bin" / "uv"
    stub.parent.mkdir()
    stub.write_text(f'#!/bin/bash\necho "$@" >> "{log}"\n', encoding="utf-8")
    stub.chmod(0o755)
    step = next(s for s in _run_steps("tests") if s.get("name") == "Tests")
    env = {**os.environ, "PATH": f"{stub.parent}{os.pathsep}{os.environ['PATH']}"}
    env["GITHUB_EVENT_NAME"] = event
    done = subprocess.run(
        ["bash", "-e", "-c", _fill(step["run"])],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        env=env,
    )
    assert done.returncode == 0, done.stdout + done.stderr
    return log.read_text(encoding="utf-8").splitlines()


def test_a_pull_request_rolls_the_files_locked_and_then_runs_pytest(tmp_path: Path) -> None:
    assert _tests_step(tmp_path, "pull_request") == [
        "run --locked python scripts/roll_stats.py",
        "run --locked pytest tests/test_a.py",
    ]


def test_a_push_to_main_reads_the_committed_files_and_rolls_nothing(tmp_path: Path) -> None:
    assert _tests_step(tmp_path, "push") == ["run --locked pytest tests/test_a.py"]


def test_the_stats_roll_job_hands_the_lint_the_pull_requests_base_and_head(
    tmp_path: Path,
) -> None:
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "check_no_stats_edit.py").write_text(
        "import sys\nprint(' '.join(sys.argv[1:]))\n", encoding="utf-8"
    )
    step = next(s for s in _run_steps("stats-roll") if "check_no_stats_edit" in s["run"])
    done = subprocess.run(
        ["bash", "-e", "-c", _fill(step["run"])], cwd=tmp_path, capture_output=True, text=True
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout.split() == ["--base", "BASESHA", "--head", "HEADSHA"]


# ---- the trailer and the catalog half ---------------------------------------------------


def test_a_trailer_that_only_starts_like_the_release_step_is_no_release(tmp_path: Path) -> None:
    def git(*args: str) -> None:
        subprocess.run(
            [
                "git",
                "-C",
                str(tmp_path),
                "-c",
                "user.name=t",
                "-c",
                "user.email=t@e.invalid",
                "-c",
                "commit.gpgsign=false",
                *args,
            ],
            check=True,
            capture_output=True,
        )

    git("init", "-q", "-b", "main")
    (tmp_path / STATS).parent.mkdir()
    (tmp_path / STATS).write_text("{}\n", encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "base")
    git("switch", "-q", "-c", "feature")
    (tmp_path / STATS).write_text('{"a": 1}\n', encoding="utf-8")
    git("add", "-A")
    git("commit", "-q", "-m", "feat: a type\n\nRolled-By: scripts/merge_pr.sh-x")
    done = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "check_no_stats_edit.py"),
            "--root",
            str(tmp_path),
            "--base",
            "main",
            "--head",
            "HEAD",
        ],
        capture_output=True,
        text=True,
    )
    assert done.returncode == 1, done.stdout + done.stderr


def test_the_catalog_half_takes_the_fresh_build_not_the_committed_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from synthetic_ecommerce_data import generate_cli as cli

    committed = tmp_path / "golden-catalog" / "stats.json"
    committed.parent.mkdir()
    committed.write_text('{"stale": 1}\n', encoding="utf-8")

    def fake_main(argv: list[str]) -> int:
        out = Path(argv[argv.index("--out") + 1])
        out.mkdir(parents=True)
        (out / "stats.json").write_text('{"fresh": 1}\n', encoding="utf-8")
        return 0

    monkeypatch.setattr(cli, "main", fake_main)
    roll_stats.build_catalog(tmp_path)
    assert committed.read_text(encoding="utf-8") == '{"fresh": 1}\n'
