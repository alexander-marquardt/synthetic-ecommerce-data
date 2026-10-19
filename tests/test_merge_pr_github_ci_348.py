"""scripts/merge_pr.sh --github-ci runs the CI workflow on GitHub-hosted runners (#348).

Same worlds as tests/test_merge_pr.py (a throwaway origin, a PR branch, stand-in ``gh`` and
``uv``). The stand-in ``gh`` here also plays GitHub Actions: ``workflow run`` is accepted
only for a branch of the origin whose head is the sha named in ``-f head=``, and the run it
answers for is green, or red the way ``FAKE_GH_RUN`` says. With ``stale-aware`` the run is
red on the golden freshness test unless the tree's ``golden-catalog/stats.json`` is main's,
which is how a real run reds on a stale golden.

What is pinned: the tree is dispatched from a throwaway branch and that branch is deleted
on every exit; nothing lands on the PR branch until the run is green; a red run prints the
failing job, its URL and its FAILED lines; a green run merges and prints
``gen-merge-minutes``; the golden-freshness regeneration works through a run.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import test_merge_pr
from test_merge_pr import (
    _ALL_GREEN,
    _FRESH,
    _GREEN,
    _GREEN_CHECK,
    _STATS,
    _branch,
    _ci_reads,
    _git,
    _merged,
    _open_pr,
    _run,
    _subject,
)

# The `actions` fixture below builds on test_merge_pr's `world` fixture: a name bound here
# is what pytest finds (a fixture is not shared between modules by import alone).
world = test_merge_pr.world

REPO = Path(__file__).resolve().parent.parent

#: Each case builds its own origin: spread over the workers (tests/xdist_groups.py).
XDIST_SPREAD = True

_FAKE_ACTIONS_GH = r"""#!/usr/bin/env bash
base_gh="$(dirname "$0")/gh-base"
RUN_URL=https://github.com/o/r/actions/runs/777
verdict() {
  # Prints the run's jobs as the --jq of the script would: id, name, status, conclusion, url.
  local mode=${FAKE_GH_RUN:-green} head sha
  head=$(cat "$FAKE_GH_LOG.dispatched")
  if [ "$mode" = stale-aware ]; then
    if git -C "$FAKE_ORIGIN" show "$head:golden-catalog/stats.json" 2>/dev/null |
      cmp -s - <(git -C "$FAKE_ORIGIN" show main:golden-catalog/stats.json); then
      mode=green
    else
      mode=stale
    fi
  fi
  j() { printf '%s\t%s\tcompleted\t%s\t%s/job/%s\n' "$1" "$2" "$3" "$RUN_URL" "$1"; }
  j 1 lint success
  case "$mode" in
    red) j 2 "tests (1)" success; j 3 "tests (2)" failure ;;
    stale) j 2 "tests (1)" failure; j 3 "tests (2)" success ;;
    *) j 2 "tests (1)" success; j 3 "tests (2)" success ;;
  esac
  j 4 commit-messages success
  if [ "$mode" != no-file-size ]; then j 5 file-size success; fi
  j 6 red-commit-proof success
  j 7 customer-name-check success
  j 9 no-derived-files success
  printf '8\tmain-merged-tree\tcompleted\tskipped\t%s/job/8\n' "$RUN_URL"
}
if [ "$1 $2" = "workflow run" ]; then
  echo "$*" >>"$FAKE_GH_LOG.dispatch"
  [ -z "${FAKE_GH_REFUSE_DISPATCH:-}" ] || { echo "fake gh: HTTP 403" >&2; exit 1; }
  ref="" head="" prev=""
  for arg in "$@"; do
    if [ "$prev" = --ref ]; then ref=$arg; fi
    case "$arg" in head=*) head=${arg#head=} ;; esac
    prev=$arg
  done
  [ "$(git -C "$FAKE_ORIGIN" rev-parse "refs/heads/$ref" 2>/dev/null)" = "$head" ] ||
    { echo "fake gh: $ref is not at $head on the origin" >&2; exit 1; }
  echo "$head" >"$FAKE_GH_LOG.dispatched"
  if [ -n "${FAKE_GH_MOVE_ON_DISPATCH:-}" ]; then
    new=$(git -C "$FAKE_ORIGIN" commit-tree "$FAKE_GH_MOVE_ON_DISPATCH^{tree}" \
      -p "$FAKE_GH_MOVE_ON_DISPATCH" -m "moves on")
    git -C "$FAKE_ORIGIN" update-ref "refs/heads/$FAKE_GH_MOVE_ON_DISPATCH" "$new"
  fi
  if [ -z "${FAKE_GH_NO_URL:-}" ]; then echo "$RUN_URL"; fi
  exit 0
fi
if [ "$1 $2" = "run list" ]; then
  [ -f "$FAKE_GH_LOG.dispatched" ] && echo 777
  exit 0
fi
if [ "$1 $2" = "run view" ]; then
  case "$*" in
    *"--json status"*)
      if [ "${FAKE_GH_RUN:-}" = pending ]; then printf 'in_progress\t-\n'; exit 0; fi
      if verdict | awk -F'\t' '$4 == "failure" { bad = 1 } END { exit !bad }'; then
        printf 'completed\tfailure\n'
      else
        printf 'completed\tsuccess\n'
      fi ;;
    *"--json jobs"*) verdict ;;
  esac
  exit 0
fi
logs_path=""
if [ "$1" = api ]; then
  # merge_pr.sh passes `--allow-escape-sequences` before the path: take it wherever it is.
  for arg in "$@"; do
    case "$arg" in */actions/jobs/*/logs) logs_path=$arg ;; esac
  done
fi
if [ -n "$logs_path" ]; then
  job=${logs_path#*/actions/jobs/}
  job=${job%%/*}
  ts=2026-10-17T10:00:00.0000000Z
  echo "$ts ##[group]Run pytest"
  if [ "$FAKE_GH_RUN" = stale-aware ] || [ "$FAKE_GH_RUN" = stale ]; then
    echo "$ts FAILED $FAKE_FRESH_ID[stats.json] - differs"
  else
    echo "$ts FAILED tests/test_planted.py::test_planted - assert False"
  fi
  exit 0
fi
exec "$base_gh" "$@"
"""


@pytest.fixture
def actions(world: dict) -> dict:
    """The world, with a ``gh`` that also plays Actions (the original stays as ``gh-base``)."""
    bin_dir = Path(world["env"]["PATH"].split(":")[0])
    (bin_dir / "gh").rename(bin_dir / "gh-base")
    (bin_dir / "gh").write_text(_FAKE_ACTIONS_GH)
    (bin_dir / "gh").chmod(0o755)
    world["env"]["FAKE_FRESH_ID"] = _FRESH
    return world


def _dispatches(world: dict) -> list[str]:
    path = Path(str(world["log"]) + ".dispatch")
    return path.read_text().splitlines() if path.exists() else []


def _throwaway_gone(world: dict) -> bool:
    return not _git(world["origin"], "branch", "--list", "ci/merge-54")


def test_a_green_run_on_the_throwaway_branch_merges_and_the_branch_is_deleted(
    actions: dict,
) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_RUN="green")
    assert done.returncode == 0, done.stdout + done.stderr
    pushed = _branch(actions)
    assert pushed != head, "the merged tree is pushed to the PR branch once the run is green"
    (dispatch,) = _dispatches(actions)
    main = _git(actions["origin"], "rev-parse", "main")
    for want in ("--ref ci/merge-54", f"base={main}", f"head={pushed}", "pr=54", "ci.yaml"):
        assert want in dispatch, (want, dispatch)
    assert _throwaway_gone(actions), "the throwaway branch was left on the origin"
    assert _ci_reads(actions) == [], "the PR's own check runs were read, not the dispatched run"
    assert actions["log"].read_text().split()[-1] == pushed
    assert "3. skipped" in done.stdout
    assert "GitHub CI run https://github.com/o/r/actions/runs/777" in done.stdout
    assert "gen-merge-minutes: " in done.stdout and "github-ci" in done.stdout


def test_nothing_lands_on_the_pr_branch_before_the_run_is_green(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_RUN="red")
    assert done.returncode != 0
    assert _branch(actions) == head, "a red tree was pushed to the PR branch"
    assert not _merged(actions)
    assert _throwaway_gone(actions)


def test_a_red_run_names_the_failing_job_its_url_and_its_failed_lines(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", "--label", "lbl", FAKE_GH_RUN="red")
    assert done.returncode != 0
    assert "GitHub CI tests (2): failure https://github.com/o/r/actions/runs/777/job/3" in (
        done.stdout
    )
    assert "FAILED tests/test_planted.py::test_planted - assert False" in done.stdout
    assert "GitHub CI is red" in done.stderr and "NOT merged" in done.stderr
    assert "tests__2_" in done.stderr, "the failed job is named in the refusal"
    log = actions["log"].parent / "lbl-tests__2_.log"
    assert "FAILED tests/test_planted.py" in log.read_text()
    assert "2026-10-17T10:00" not in log.read_text(), "the runner's timestamps are stripped"


def test_a_required_job_missing_from_a_green_run_is_not_a_green_run(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_RUN="no-file-size")
    assert done.returncode != 0
    assert "required check file-size did not pass" in done.stderr
    assert not _merged(actions) and _branch(actions) == head and _throwaway_gone(actions)


def test_a_dispatch_github_refuses_is_reported_and_leaves_nothing_behind(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_REFUSE_DISPATCH="1")
    assert done.returncode != 0
    assert "could not dispatch the CI workflow on ci/merge-54" in done.stderr
    assert not _merged(actions) and _branch(actions) == head and _throwaway_gone(actions)


def test_a_run_that_does_not_finish_in_time_is_not_merged(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_RUN="pending")
    assert done.returncode != 0
    assert "has not finished after 0s" in done.stderr
    assert not _merged(actions) and _branch(actions) == head and _throwaway_gone(actions)


def test_a_gh_that_prints_no_run_url_is_asked_for_the_run_by_branch_and_sha(
    actions: dict,
) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_NO_URL="1")
    assert done.returncode == 0, done.stdout + done.stderr
    assert _merged(actions)


def test_a_pr_head_that_moves_during_the_run_is_neither_overwritten_nor_merged(
    actions: dict,
) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_MOVE_ON_DISPATCH="pr-branch")
    assert done.returncode != 0
    assert "was refused (has the PR head moved?)" in done.stderr
    assert not _merged(actions) and _branch(actions) != head and _throwaway_gone(actions)


def test_a_dry_run_dispatches_but_pushes_and_merges_nothing(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--dry-run", "--github-ci")
    assert done.returncode == 0, done.stdout + done.stderr
    assert len(_dispatches(actions)) == 1
    assert "5. every GitHub CI job is green" in done.stdout
    assert not _merged(actions) and _branch(actions) == head and _throwaway_gone(actions)


def test_gen_github_ci_makes_it_the_default(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, GEN_GITHUB_CI="1")
    assert done.returncode == 0, done.stdout + done.stderr
    assert len(_dispatches(actions)) == 1 and _ci_reads(actions) == []


def test_the_last_of_the_two_ci_flags_wins(actions: dict) -> None:
    head = _open_pr(actions, {**_GREEN, **_ALL_GREEN})
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", "--local-ci", "--label", "lbl")
    assert done.returncode == 0, done.stdout + done.stderr
    assert _dispatches(actions) == [] and "local CI tests: PASS" in done.stdout


def test_a_run_red_only_on_the_golden_freshness_test_is_regenerated_and_run_again(
    actions: dict,
) -> None:
    stats = actions["checkout"] / _STATS
    stale = stats.read_text().replace('"lines": ', '"lines": 1', 1)
    head = _open_pr(actions, {**_GREEN, _STATS: stale})
    done = _run(
        actions,
        head,
        _GREEN_CHECK,
        "--github-ci",
        "--label",
        "lbl",
        FAKE_GH_RUN="stale-aware",
        FAKE_UV_SKIP_BUILD_ONCE="1",
    )
    assert done.returncode == 0, done.stdout + done.stderr
    pushed = _branch(actions)
    assert _subject(actions, pushed) == "regenerate golden on main"
    assert len(_dispatches(actions)) == 2, "the regenerated tree gets its own run"
    assert f"head={pushed}" in _dispatches(actions)[1]
    assert done.stdout.count("GitHub CI tests (1): failure") == 1
    assert (actions["log"].parent / "lbl-tests__1_.log.before-regenerate").is_file()
    assert actions["log"].read_text().split()[-1] == pushed
    assert _throwaway_gone(actions)


def test_a_golden_that_stays_red_after_the_regeneration_is_regenerated_once_only(
    actions: dict,
) -> None:
    stats = actions["checkout"] / _STATS
    stale = stats.read_text().replace('"lines": ', '"lines": 1', 1)
    head = _open_pr(actions, {**_GREEN, _STATS: stale})
    done = _run(
        actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_RUN="stale", FAKE_UV_SKIP_BUILD_ONCE="1"
    )
    assert done.returncode != 0
    assert len(_dispatches(actions)) == 2, "one regeneration, one more run, then it stops"
    assert "after the golden regeneration" in done.stderr
    assert not _merged(actions) and _branch(actions) == head and _throwaway_gone(actions)


def test_a_red_that_is_not_a_freshness_test_is_not_regenerated(actions: dict) -> None:
    head = _open_pr(actions, _GREEN)
    done = _run(actions, head, _GREEN_CHECK, "--github-ci", FAKE_GH_RUN="red")
    assert len(_dispatches(actions)) == 1
    assert "rebuilding it on the merged tree" not in done.stdout


# -- the shard matrix in the local run ----------------------------------------------------

_JOBS = REPO / "scripts" / "local_ci_jobs.py"


def _emit(workflow: str, tmp_path: Path, job: str = "t") -> subprocess.CompletedProcess:
    (tmp_path / "w.yml").write_text(workflow, encoding="utf-8")
    return subprocess.run(
        [sys.executable, str(_JOBS), "--workflows", str(tmp_path), "--emit", job]
        + ["--base", "BBB", "--head", "HHH"],
        capture_output=True,
        text=True,
        check=False,
    )


_SHARDED = """\
on: push
jobs:
  t:
    strategy:
      fail-fast: false
      matrix:
        shard: [1, 2, 3]
    env:
      PYTEST_ADDOPTS: "-n auto --dist loadgroup"
    steps:
      - uses: actions/checkout@v4
      - run: echo shard=${{ matrix.shard }} of=${{ strategy.job-total }}
      - uses: actions/upload-artifact@v4
        if: always()
        with: {name: x, path: y}
"""


def test_a_shard_matrix_runs_once_locally_as_the_all_shard_with_the_local_worker_count(
    tmp_path: Path,
) -> None:
    done = _emit(_SHARDED, tmp_path)
    assert done.returncode == 0, done.stderr
    assert "echo shard=all of=1" in done.stdout
    assert done.stdout.count("export PYTEST_ADDOPTS=") == 1, "the hosted -n auto must not win"
    assert "-n auto" not in done.stdout


@pytest.mark.parametrize(
    "edit",
    [
        ("shard: [1, 2, 3]", "shard: [1, 2, 3]\n        os: [a, b]"),
        ("fail-fast: false", "fail-fast: false\n      max-parallel: 2"),
    ],
    ids=["a second matrix key", "a strategy key the local run cannot honour"],
)
def test_a_matrix_of_another_shape_has_no_local_equivalent(
    tmp_path: Path, edit: tuple[str, str]
) -> None:
    assert _emit(_SHARDED.replace(*edit), tmp_path).returncode != 0


def test_an_or_expression_takes_the_first_value_that_is_not_empty(tmp_path: Path) -> None:
    workflow = (
        "on: push\njobs:\n  t:\n    steps:\n"
        "      - run: echo ${{ github.event.pull_request.base.sha || inputs.base }}"
        " ${{ inputs.pr || github.event.pull_request.head.sha }}\n"
    )
    done = _emit(workflow, tmp_path)
    assert done.returncode == 0, done.stderr
    assert "echo BBB HHH" in done.stdout


def test_the_real_workflow_s_pr_jobs_can_be_dispatched_with_the_range_as_inputs() -> None:
    import yaml

    document = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yaml").read_text())
    inputs = document[True]["workflow_dispatch"]["inputs"]  # YAML reads `on` as True
    assert set(inputs) == {"base", "head", "pr"}
    jobs = ("commit-messages", "file-size", "red-commit-proof", "customer-name-check", "no-derived-files")
    for job in jobs:
        condition = document["jobs"][job]["if"]
        assert "workflow_dispatch" in condition and "inputs.head" in condition, job
