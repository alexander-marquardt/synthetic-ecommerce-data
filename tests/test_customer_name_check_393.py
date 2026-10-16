"""A customer name cannot come back into this repository unseen (#393).

``scripts/check_customer_names.py`` scans the tracked tree (every file's content
and its path), the commit messages of a range and the title and body of a pull
request, for the names in elastic/prism's ``CUSTOMER_NAME_SPECS``. It reads that
list from the vendored copy of core's ``audit_grep_diff.py``
(``vendor/prism/PIN.txt``), so there is one list.

Each case below builds a small repository, plants a name and runs the script on
it. A check that has never been seen to fail is not evidence: the planted cases
are the evidence, and they were run against a script that scanned nothing
before the real one was written.

THE TEST FILE NAMES NO CUSTOMER. Each sample is spelled in fragments, so this
file is itself clean under the check it tests (``test_the_real_tree_is_clean``
scans it with the rest).
"""

from __future__ import annotations

import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "check_customer_names.py"
VENDORED = ROOT / "vendor" / "prism" / ".github" / "scripts" / "audit_grep_diff.py"
CI = ROOT / ".github" / "workflows" / "ci.yaml"

#: One sample per row of core's list, keyed by the row's label. Spelled in
#: fragments so that no line of this file matches the row it samples.
SAMPLES = {
    "proprietary-retailer": "Mus" + "grave",
    "industrial-retailer": "M" + "SC" + " Direct",
    "industrial-retailer-formal": "M" + "SC" + " Industrial Supply",
    "industrial-retailer-abbr": "M" + "SC",
}
LABELS = sorted(SAMPLES)


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


def _commit(repo: Path, message: str = "a change") -> str:
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A clean repository: prose, code, a lockfile and a data file, one commit."""
    root = tmp_path / "repo"
    (root / "src").mkdir(parents=True)
    _git(root, "init", "-q", "-b", "main")
    (root / "README.md").write_text("# A distributor\n\nIndustrial fasteners.\n")
    (root / "src" / "mod.py").write_text("# a comment\nVALUE = 1\n")
    (root / "uv.lock").write_text('[[package]]\nname = "scrape-reference"\n')
    (root / "data.json").write_text('{"name": "screw"}\n')
    _commit(root, "base")
    return root


def _fake_gh(
    tmp_path: Path,
    payload: dict[str, str] | None,
    rc: int = 0,
    answers_anyway: bool = False,
) -> dict:
    """A ``gh`` on PATH that records its arguments and answers ``pr view`` offline."""
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir(exist_ok=True)
    log = tmp_path / "gh-args.txt"
    answer = tmp_path / "gh-answer.json"
    answer.write_text(json.dumps(payload or {}))
    gh = bin_dir / "gh"
    gh.write_text(
        '#!/bin/sh\necho "$@" >> "'
        + str(log)
        + '"\n'
        + (f"exit {rc}\n" if rc and not answers_anyway else "")
        + ('cat "' + str(answer) + '"\n' if not rc or answers_anyway else "")
        + (f"exit {rc}\n" if rc and answers_anyway else "")
    )
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    return {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "_log": str(log)}


def _run(
    repo: Path, *args: str, env: dict[str, str] | None = None
) -> subprocess.CompletedProcess[str]:
    run_env = {k: v for k, v in os.environ.items() if k != "_log"}
    run_env.update({k: v for k, v in (env or {}).items() if k != "_log"})
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(repo), *args],
        capture_output=True,
        text=True,
        env=run_env,
    )


# --- the list is core's, not a copy ---------------------------------------


def _vendored() -> ModuleType:
    assert VENDORED.is_file(), f"{VENDORED} is not vendored (vendor/prism/PIN.txt)"
    spec = importlib.util.spec_from_file_location("vendored_audit_grep", VENDORED)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["vendored_audit_grep"] = module
    spec.loader.exec_module(module)
    return module


def test_every_row_of_cores_list_has_a_planted_sample() -> None:
    """A row core adds with no sample here is a row nobody has seen fail."""
    core = _vendored()
    assert sorted(label for label, _ in core.CUSTOMER_NAME_SPECS) == LABELS


@pytest.mark.parametrize("label", LABELS)
def test_each_sample_is_caught_by_its_own_row_of_cores_list(label: str) -> None:
    core = _vendored()
    hits = core.scan_text_for_customer_names(SAMPLES[label], "<sample>")
    assert label in {hit.pattern_label for hit in hits}


def test_the_script_reads_the_vendored_list_and_holds_no_pattern_of_its_own() -> None:
    assert SCRIPT.is_file(), f"{SCRIPT} does not exist"
    spec = importlib.util.spec_from_file_location("check_customer_names", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["check_customer_names"] = module
    spec.loader.exec_module(module)
    core = _vendored()
    assert module.SPECS == core.CUSTOMER_NAME_SPECS
    assert module.SPECS, "an empty list scans nothing and reports clean"


# --- the tree --------------------------------------------------------------


def test_a_clean_tree_passes_and_says_what_it_scanned(repo: Path) -> None:
    done = _run(repo)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "4 files" in done.stdout


SURFACES = {
    "a code comment": ("src/mod.py", "# the {t} catalogue\nVALUE = 1\n", 1),
    "a lockfile": ("uv.lock", '[[package]]\nname = "{t}"\n', 2),
    "prose": ("README.md", "# A distributor\n\n{t} fasteners.\n", 3),
    "a data value": ("data.json", '{{"name": "{t}"}}\n', 1),
}


@pytest.mark.parametrize("surface", sorted(SURFACES))
@pytest.mark.parametrize("label", LABELS)
def test_a_name_planted_in_a_tracked_file_is_found_at_its_line(
    repo: Path, label: str, surface: str
) -> None:
    path, template, line = SURFACES[surface]
    (repo / path).write_text(template.format(t=SAMPLES[label]))
    _commit(repo)
    done = _run(repo)
    assert done.returncode == 1, done.stdout + done.stderr
    assert f"{path}:{line}" in done.stdout
    assert label in done.stdout


def test_the_report_names_the_place_and_never_repeats_the_name(repo: Path) -> None:
    (repo / "src" / "mod.py").write_text(f"# {SAMPLES['industrial-retailer']}\n")
    _commit(repo)
    done = _run(repo)
    assert done.returncode == 1
    for sample in SAMPLES.values():
        assert sample.lower() not in (done.stdout + done.stderr).lower()


@pytest.mark.parametrize("label", LABELS)
def test_a_name_in_a_file_path_is_found(repo: Path, label: str) -> None:
    name = SAMPLES[label].replace(" ", "_")
    (repo / "data").mkdir()
    (repo / "data" / f"catalog_{name}_20260925.json").write_text("{}\n")
    _commit(repo)
    done = _run(repo)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "data/catalog_" in done.stdout


def test_a_name_in_a_file_that_holds_a_nul_byte_is_found(repo: Path) -> None:
    """One NUL byte hides a file from a plain grep; it must not hide it here."""
    (repo / "src" / "mod.py").write_bytes(
        b"\0\n# " + SAMPLES["industrial-retailer-abbr"].encode() + b"\n"
    )
    _commit(repo)
    done = _run(repo)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "src/mod.py:2" in done.stdout


def test_a_file_that_is_not_text_is_named_as_not_scanned(repo: Path) -> None:
    (repo / "logo.png").write_bytes(b"\x89PNG\r\n\x1a\n\xff\xfe\x00\x80")
    _commit(repo)
    done = _run(repo)
    assert done.returncode == 0, done.stdout + done.stderr
    assert "logo.png" in done.stdout
    assert "not scanned" in done.stdout


def test_an_untracked_file_is_scanned_too(repo: Path) -> None:
    """The pre-push gate runs before ``git add``; a draft file must not escape it."""
    (repo / "notes.md").write_text(f"{SAMPLES['proprietary-retailer']}\n")
    done = _run(repo)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "notes.md:1" in done.stdout


def test_an_ignored_file_is_not_scanned(repo: Path) -> None:
    (repo / ".gitignore").write_text("scratch.txt\n")
    _commit(repo)
    (repo / "scratch.txt").write_text(f"{SAMPLES['proprietary-retailer']}\n")
    done = _run(repo)
    assert done.returncode == 0, done.stdout + done.stderr


def test_a_name_inside_a_word_is_not_a_hit(repo: Path) -> None:
    """The abbreviation row is letter-bounded: ``emscripten`` is not a customer."""
    (repo / "src" / "mod.py").write_text("# built with emscripten, termscc\n")
    _commit(repo)
    done = _run(repo)
    assert done.returncode == 0, done.stdout + done.stderr


# --- free text: a PR body, a title ----------------------------------------


def test_a_name_in_a_text_file_is_found_at_its_line(repo: Path, tmp_path: Path) -> None:
    body = tmp_path / "body.md"
    body.write_text(f"Fixes a thing.\n\nSeen at {SAMPLES['industrial-retailer']}.\n")
    done = _run(repo, "--text-file", str(body))
    assert done.returncode == 1, done.stdout + done.stderr
    assert "body.md:3" in done.stdout


def test_a_clean_text_file_passes(repo: Path, tmp_path: Path) -> None:
    body = tmp_path / "body.md"
    body.write_text("Fixes a thing.\n")
    done = _run(repo, "--text-file", str(body))
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 text" in done.stdout


def test_a_missing_text_file_is_not_a_pass(repo: Path, tmp_path: Path) -> None:
    done = _run(repo, "--text-file", str(tmp_path / "nope.md"))
    assert done.returncode == 3, done.stdout + done.stderr


# --- the live pull request -------------------------------------------------


@pytest.mark.parametrize("where", ["title", "body"])
def test_a_name_in_the_live_pr_title_or_body_is_found(
    repo: Path, tmp_path: Path, where: str
) -> None:
    payload = {"title": "A fix", "body": "Some text.\n"}
    payload[where] = f"about {SAMPLES['proprietary-retailer']}"
    env = _fake_gh(tmp_path, payload)
    done = _run(repo, "--pr", "17", env=env)
    assert done.returncode == 1, done.stdout + done.stderr
    assert "pull request 17" in done.stdout
    # The text is read from the API when the job runs, not from the event payload.
    assert Path(env["_log"]).read_text().strip() == "pr view 17 --json title,body"


def test_a_clean_live_pr_passes(repo: Path, tmp_path: Path) -> None:
    env = _fake_gh(tmp_path, {"title": "A fix", "body": "Some text.\n"})
    done = _run(repo, "--pr", "17", env=env)
    assert done.returncode == 0, done.stdout + done.stderr


def test_an_empty_pr_number_means_no_pull_request(repo: Path, tmp_path: Path) -> None:
    """A push event has no PR; CI passes the empty string and ``gh`` is not asked."""
    env = _fake_gh(tmp_path, None, rc=9)
    done = _run(repo, "--pr", "", env=env)
    assert done.returncode == 0, done.stdout + done.stderr
    assert not Path(env["_log"]).exists()


def test_a_gh_that_cannot_answer_is_could_not_judge_not_a_pass(
    repo: Path, tmp_path: Path
) -> None:
    env = _fake_gh(tmp_path, None, rc=1)
    done = _run(repo, "--pr", "17", env=env)
    assert done.returncode == 3, done.stdout + done.stderr
    assert "could not judge" in done.stdout + done.stderr


def test_a_gh_that_answers_and_exits_nonzero_is_not_a_pass(
    repo: Path, tmp_path: Path
) -> None:
    """A clean-looking answer from a failed ``gh`` is not evidence the PR is clean."""
    env = _fake_gh(
        tmp_path, {"title": "A fix", "body": "Some text.\n"}, rc=1, answers_anyway=True
    )
    done = _run(repo, "--pr", "17", env=env)
    assert done.returncode == 3, done.stdout + done.stderr
    assert "could not judge" in done.stdout + done.stderr


# --- commit messages -------------------------------------------------------


def test_a_name_in_a_commit_message_of_the_range_is_found(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "src" / "mod.py").write_text("VALUE = 2\n")
    _commit(repo, f"Match the {SAMPLES['industrial-retailer-abbr']} layout")
    done = _run(repo, "--range", f"{base}..HEAD")
    assert done.returncode == 1, done.stdout + done.stderr
    assert "commit " in done.stdout


def test_a_name_in_a_commit_body_line_is_found_at_that_line(repo: Path) -> None:
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "src" / "mod.py").write_text("VALUE = 2\n")
    _commit(repo, f"Tidy\n\nline two\n{SAMPLES['proprietary-retailer']}\n")
    done = _run(repo, "--range", f"{base}..HEAD")
    assert done.returncode == 1, done.stdout + done.stderr
    assert ":4 " in done.stdout


def test_a_name_in_a_commit_before_the_range_is_not_this_ranges_to_judge(
    repo: Path,
) -> None:
    (repo / "src" / "mod.py").write_text("VALUE = 2\n")
    _commit(repo, f"Match the {SAMPLES['industrial-retailer-abbr']} layout")
    base = _git(repo, "rev-parse", "HEAD")
    (repo / "src" / "mod.py").write_text("VALUE = 3\n")
    _commit(repo, "A clean change")
    done = _run(repo, "--range", f"{base}..HEAD")
    assert done.returncode == 0, done.stdout + done.stderr
    assert "1 commit" in done.stdout


def test_a_range_that_is_a_path_is_refused_not_scanned(repo: Path) -> None:
    """A tool handed a path once scanned 63 unrelated commits and reported clean."""
    done = _run(repo, "--range", "src/mod.py")
    assert done.returncode == 2, done.stdout + done.stderr
    assert "range" in done.stderr


def test_a_range_naming_a_missing_commit_is_could_not_judge(repo: Path) -> None:
    done = _run(repo, "--range", "0" * 40 + "..HEAD")
    assert done.returncode == 3, done.stdout + done.stderr


# --- this repository -------------------------------------------------------


def test_the_real_tree_is_clean() -> None:
    done = subprocess.run(
        [sys.executable, str(SCRIPT)], capture_output=True, text=True, cwd=ROOT
    )
    assert done.returncode == 0, done.stdout + done.stderr


def _job() -> dict:
    jobs = yaml.safe_load(CI.read_text())["jobs"]
    assert "customer-name-check" in jobs, "ci.yaml has no customer-name-check job"
    job: dict = jobs["customer-name-check"]
    return job


def _step() -> dict:
    return next(s for s in _job()["steps"] if "check_customer_names" in s.get("run", ""))


def test_the_ci_job_runs_the_script_on_the_pull_requests_range_and_its_live_text() -> None:
    run = " ".join(_step()["run"].replace("\\\n", " ").split())
    assert "python3 scripts/check_customer_names.py" in run
    assert (
        '--range "${{ github.event.pull_request.base.sha }}..'
        '${{ github.event.pull_request.head.sha }}"'
    ) in run
    assert "--pr " in run


def test_the_ci_job_runs_on_pull_requests_with_a_read_only_token() -> None:
    job = _job()
    assert job["if"] == "github.event_name == 'pull_request'"
    assert _step()["env"]["GH_TOKEN"] == "${{ github.token }}"
    assert job["permissions"] == {"contents": "read", "pull-requests": "read"}


def test_the_local_ci_run_of_the_job_emits_its_command_with_the_shas_and_an_empty_token() -> None:
    """``merge_pr.sh --local-ci`` runs every job; the job must have a local equivalent."""
    spec = importlib.util.spec_from_file_location(
        "local_ci_jobs_393", ROOT / "scripts" / "local_ci_jobs.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    script = module.emit("customer-name-check", _job(), "BASESHA", "HEADSHA")
    assert "scripts/check_customer_names.py" in script
    assert "BASESHA..HEADSHA" in script
    assert "export GH_TOKEN=''" in script, "the local run uses the signed-in gh"
