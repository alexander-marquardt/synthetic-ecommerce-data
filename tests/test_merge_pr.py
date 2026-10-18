"""scripts/merge_pr.sh merges only a tree that is green after main is merged in (#54).

Each case builds a throwaway origin from this checkout's HEAD, pushes a PR
branch to it, and runs the script from a clone of that origin. Two stand-ins
go first on ``PATH``:

* ``gh`` plays GitHub. It answers ``pr view``, reports the CI check runs of a
  commit as ``FAKE_GH_CI`` says, and records a ``pr merge`` only when its
  ``--match-head-commit`` is still the branch head, as GitHub does.
* ``uv`` runs the real one, and while the build runs it can move ``main`` or
  the PR head on the origin (``FAKE_UV_MOVE``), write a file the build does
  not (``FAKE_UV_STRAY``), or skip the build (``FAKE_UV_SKIP_BUILD``). That
  is how a case makes something change mid-run. With ``FAKE_UV_DNS_DOWN`` it
  also plays a network whose lookups fail: a build that is not offline
  (``UV_OFFLINE=1``) stops on the error uv printed when that happened (#178).

The script's own checks are narrowed to one test (``MERGE_PR_CHECKS``): what is
under test is the script's order of operations, not the suite.
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

from synthetic_ecommerce_data import generate_cli as cli

REPO = Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "merge_pr.sh"
JOBS_SCRIPT = REPO / "scripts" / "local_ci_jobs.py"
WORKFLOWS = REPO / ".github" / "workflows"

#: Moves ``refs/heads/$1`` on the origin by one empty commit: another PR
#: landing on main, or a builder pushing to the PR branch.
_MOVE = r"""
move() {
  local new
  new=$(git -C "$FAKE_ORIGIN" commit-tree "$1^{tree}" -p "$1" -m "$1 moves on")
  git -C "$FAKE_ORIGIN" update-ref "refs/heads/$1" "$new"
}
"""

_FAKE_GH = (
    "#!/usr/bin/env bash\n"
    + _MOVE
    + r"""
case "$1 $2" in
  "pr view")
    printf 'OPEN\tfalse\t%s\t%s\tmain\n' "${FAKE_GH_BRANCH:-pr-branch}" "$FAKE_GH_HEAD"
    if [ -n "${FAKE_GH_MOVE_ON_VIEW:-}" ]; then move "$FAKE_GH_MOVE_ON_VIEW"; fi
    ;;
  "api "*)
    # repos/<slug>/commits/<sha>/check-runs, answered as the --jq would.
    sha=${2#*/commits/}
    sha=${sha%%/*}
    echo "$sha" >>"$FAKE_GH_CI_LOG"
    mode=${FAKE_GH_CI:-green}
    if [ "$mode" = head-only ]; then
      [ "$sha" = "$FAKE_GH_HEAD" ] || exit 0
      mode=green
    fi
    case "$mode" in
      green) printf 'tests (1)\tcompleted\tsuccess\ntests (2)\tcompleted\tsuccess\n' ;;
      red) printf 'tests (1)\tcompleted\tsuccess\ntests (2)\tcompleted\tfailure\n' ;;
      skipped) printf 'tests (1)\tcompleted\tskipped\n' ;;
      pending) printf 'tests (1)\tin_progress\t\n' ;;
      missing) ;;
    esac
    printf 'lint\tcompleted\tsuccess\n'
    printf 'commit-messages\tcompleted\tsuccess\n'
    printf 'file-size\tcompleted\tsuccess\n'
    printf 'red-commit-proof\tcompleted\tsuccess\n'
    printf 'customer-name-check\tcompleted\tsuccess\n'
    printf 'main-merged-tree\tcompleted\tskipped\n'
    ;;
  "pr merge")
    if [ -n "${FAKE_GH_REFUSE_FIRST_MERGE:-}" ] && [ ! -e "$FAKE_GH_LOG.refused" ]; then
      touch "$FAKE_GH_LOG.refused"
      if [ -n "${FAKE_GH_MOVE_ON_REFUSAL:-}" ]; then move "$FAKE_GH_MOVE_ON_REFUSAL"; fi
      echo "fake gh: not mergeable yet" >&2
      exit 1
    fi
    want="" prev=""
    for arg in "$@"; do
      if [ "$prev" = --match-head-commit ]; then want=$arg; fi
      prev=$arg
    done
    branch=${FAKE_GH_BRANCH:-pr-branch}
    if [ "$want" != "$(git -C "$FAKE_ORIGIN" rev-parse "refs/heads/$branch")" ]; then
      echo "fake gh: the head of $branch is not $want" >&2
      exit 1
    fi
    echo "$*" >>"$FAKE_GH_LOG"
    if [ -n "${FAKE_GH_LAND:-}" ]; then
      # A squash merge: the PR's tree, one commit on main (which the script
      # has already merged into the branch, so the tree is main plus the PR).
      new=$(git -C "$FAKE_ORIGIN" commit-tree "$branch^{tree}" -p refs/heads/main -m "squash")
      git -C "$FAKE_ORIGIN" update-ref refs/heads/main "$new"
    fi
    ;;
  *) echo "fake gh: unexpected $*" >&2; exit 2 ;;
esac
"""
)

_FAKE_UV = (
    "#!/usr/bin/env bash\n"
    + _MOVE
    + r"""
if [[ " $* " == *" build "* ]]; then
  if [ -n "${FAKE_UV_DNS_DOWN:-}" ] && [ "${UV_OFFLINE:-}" != 1 ]; then
    cat >&2 <<'MSG'
  x Failed to build `synthetic-ecommerce-data`
  |-> Failed to resolve requirements from `build-system.requires`
  |-> Failed to fetch: `https://pypi.org/simple/hatchling/`
  |-> dns error: failed to lookup address information: nodename nor servname provided, or not known
MSG
    exit 2
  fi
  if [ -n "${FAKE_UV_MOVE:-}" ] && [ ! -e "$FAKE_GH_LOG.moved" ]; then
    touch "$FAKE_GH_LOG.moved"
    move "$FAKE_UV_MOVE"
  fi
  if [ -n "${FAKE_UV_STRAY:-}" ]; then
    prev=""
    for arg in "$@"; do
      if [ "$prev" = --directory ]; then echo stray >"$arg/$FAKE_UV_STRAY"; fi
      prev=$arg
    done
  fi
  if [ -n "${FAKE_UV_SKIP_BUILD:-}" ]; then exit 0; fi
  if [ -n "${FAKE_UV_SKIP_BUILD_ONCE:-}" ] && [ ! -e "$FAKE_GH_LOG.skipped" ]; then
    touch "$FAKE_GH_LOG.skipped"
    exit 0
  fi
fi
if [[ " $* " == *retail_figures.py* ]]; then
  # The retail rebuild takes about 40 s: only a case about it runs the real one.
  if [ -n "${FAKE_UV_RETAIL_FAIL:-}" ]; then echo "retail build: boom" >&2; exit 3; fi
  if [ -z "${FAKE_UV_RETAIL:-}" ]; then exit 0; fi
fi
exec "$REAL_UV" "$@"
"""
)

#: Each case builds its own throwaway origin (30 to 80 s) and shares no fixture, so the
#: cases spread over the xdist workers instead of sharing one (tests/xdist_groups.py).
XDIST_SPREAD = True

pytestmark = pytest.mark.skipif(shutil.which("uv") is None, reason="the script runs uv")


_IDENTITY = {
    "GIT_AUTHOR_NAME": "t",
    "GIT_AUTHOR_EMAIL": "t@example.invalid",
    "GIT_COMMITTER_NAME": "t",
    "GIT_COMMITTER_EMAIL": "t@example.invalid",
}

_STATS = "golden-catalog/stats.json"
_RETAIL_STATS = "golden-retail/stats.json"

#: Name resolution that fails, as a dropped lookup does (#178). The stand-in uv
#: stops a build that is not offline with the error uv printed then
#: (``FAKE_UV_DNS_DOWN``), and every proxy variable points at a host that
#: cannot resolve (``.invalid`` is reserved for that), so a real uv that does
#: reach for an index fails the same way.
_NO_NAME_RESOLUTION = {
    "FAKE_UV_DNS_DOWN": "1",
    **{
        name: "http://dns-blocked.invalid:3128"
        for name in (
            "HTTP_PROXY",
            "HTTPS_PROXY",
            "ALL_PROXY",
            "http_proxy",
            "https_proxy",
            "all_proxy",
        )
    },
}


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
        env={**os.environ, **_IDENTITY},
    ).stdout.strip()


@pytest.fixture
def world(tmp_path: Path) -> dict:
    env = {**os.environ, **_IDENTITY}
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    # This checkout's HEAD as the origin's main; CI checks out full history so
    # the fetch never starts from a shallow repository.
    quiet = ["-c", "gc.auto=0", "-c", "maintenance.auto=false"]
    quiet += ["-c", "fetch.writeCommitGraph=false"]
    _git(origin, *quiet, "fetch", "-q", str(REPO), "HEAD:refs/heads/main")
    _git(origin, "symbolic-ref", "HEAD", "refs/heads/main")
    checkout = tmp_path / "checkout"
    # --no-local: the objects are transferred, not hardlinked or copied from the origin's
    # directory; on a hosted runner the copy raced with git's own commit-graph writes
    # ("hardlink different from source", "failed to copy file ... commit-graph-chain.lock").
    clone = ["git", *quiet, "clone", "-q", "--no-local", str(origin), str(checkout)]
    subprocess.run(clone, check=True)
    # The script under test is this tree's, not the HEAD commit's.
    shutil.copy2(SCRIPT, checkout / "scripts" / "merge_pr.sh")
    shutil.copy2(JOBS_SCRIPT, checkout / "scripts" / "local_ci_jobs.py")
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    for name, text in (("gh", _FAKE_GH), ("uv", _FAKE_UV)):
        (bin_dir / name).write_text(text)
        (bin_dir / name).chmod(0o755)
    env.update(
        REAL_UV=str(shutil.which("uv")),
        PATH=f"{bin_dir}{os.pathsep}{env['PATH']}",
        FAKE_ORIGIN=str(origin),
        FAKE_GH_LOG=str(tmp_path / "gh.log"),
        FAKE_GH_CI_LOG=str(tmp_path / "ci.log"),
        TMPDIR=str(tmp_path),
        # Every wait is one look: a case decides what CI says up front.
        MERGE_PR_CI_TIMEOUT="0",
        MERGE_PR_CI_POLL="0",
        MERGE_PR_RETRY_SLEEP="0",
        # The narrowed checks are one test: two workers, not one per core (#348).
        LOCAL_CI_WORKERS="2",
        MERGE_PR_LOG_DIR=str(tmp_path),
        # The planted worlds run with name resolution blocked: a red here is
        # the script's, never the network's (#178).
        **_NO_NAME_RESOLUTION,
        # ... and build from uv's cache, the checkout having been synced once.
        UV_OFFLINE="1",
    )
    for name in ("NO_PROXY", "no_proxy"):
        env.pop(name, None)
    # The suite may itself run under GEN_LOCAL_CI=1; a case opts in on its own.
    env.pop("GEN_LOCAL_CI", None)
    return {
        "origin": origin,
        "checkout": checkout,
        "env": env,
        "log": tmp_path / "gh.log",
        "ci_log": tmp_path / "ci.log",
    }


def _commit(checkout: Path, plant: dict[str, str], message: str) -> None:
    for path, text in plant.items():
        (checkout / path).write_text(text)
    _git(checkout, "add", "--", *plant)
    _git(checkout, "commit", "-q", "-m", message)


def _open_pr(
    world: dict, plant: dict[str, str], on_main: dict[str, str] | None = None, main_moves=True
) -> str:
    """A PR branch off main with ``plant``; then, unless told not to, a later
    commit on main (``on_main``, or a line added to the README)."""
    checkout = world["checkout"]
    _git(checkout, "switch", "-q", "-c", "pr-branch")
    _commit(checkout, plant, "planted PR change")
    _git(checkout, "push", "-q", "origin", "pr-branch")
    head = _git(checkout, "rev-parse", "HEAD")
    _git(checkout, "switch", "-q", "main")
    if main_moves:
        later = on_main or {"README.md": (checkout / "README.md").read_text() + "\nlater\n"}
        _commit(checkout, later, "main moves on after the PR's CI run")
        _git(checkout, "push", "-q", "origin", "main")
    return head


def _run(
    world: dict, head: str, checks: str, *flags: str, **env: str
) -> subprocess.CompletedProcess:
    env = {**world["env"], "FAKE_GH_HEAD": head, "MERGE_PR_CHECKS": checks, **env}
    return subprocess.run(
        [str(world["checkout"] / "scripts" / "merge_pr.sh"), *flags, "54"],
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _branch(world: dict, name: str = "pr-branch") -> str:
    return _git(world["origin"], "rev-parse", name)


def _merged(world: dict) -> bool:
    return world["log"].exists()


def _ci_reads(world: dict) -> list[str]:
    return world["ci_log"].read_text().split() if world["ci_log"].exists() else []


_GREEN = {"tests/test_planted_green.py": "def test_ok():\n    pass\n"}
_GREEN_CHECK = "tests/test_planted_green.py"


# -- the merge it exists for -------------------------------------------------


def test_a_stale_golden_is_rebuilt_on_the_merged_tree_pushed_and_merged(world: dict) -> None:
    stats = world["checkout"] / _STATS
    stale = stats.read_text().replace('"lines": ', '"lines": 1', 1)
    head = _open_pr(world, {_STATS: stale})
    result = _run(world, head, "tests/test_catalog_golden.py")
    assert result.returncode == 0, result.stdout + result.stderr
    pushed = _branch(world)
    assert pushed != head, "the merged and rebuilt tree was not pushed"
    assert _git(world["origin"], "merge-base", "--is-ancestor", "main", pushed) == ""
    assert _git(world["origin"], "show", f"{pushed}:{_STATS}") == _git(
        world["origin"], "show", f"main:{_STATS}"
    )
    merged = world["log"].read_text().split()
    assert merged[:3] == ["pr", "merge", "54"]
    assert merged[-3:] == ["--squash", "--match-head-commit", pushed]
    # The CI that gates the merge is the pushed tree's, not the stale head's.
    assert _ci_reads(world) == [pushed]


def test_a_red_merged_tree_is_neither_pushed_nor_merged(world: dict) -> None:
    plant = {"tests/test_planted_red.py": "def test_planted():\n    assert False\n"}
    head = _open_pr(world, plant)
    result = _run(world, head, "tests/test_planted_red.py")
    assert result.returncode != 0
    assert "red on the merged tree; NOT pushed, NOT merged" in result.stderr
    assert _branch(world) == head
    assert not _merged(world)


def test_a_dry_run_pushes_and_merges_nothing(world: dict) -> None:
    stats = world["checkout"] / _STATS
    head = _open_pr(world, {_STATS: stats.read_text() + " "})
    result = _run(world, head, "tests/test_catalog_golden.py", "--dry-run")
    assert result.returncode == 0, result.stdout + result.stderr
    assert "dry run: would push" in result.stdout
    assert _branch(world) == head
    assert not _merged(world)


def test_a_merge_github_refuses_once_is_retried(world: dict) -> None:
    """GitHub refuses a merge until it has recomputed mergeability after a push."""
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_GH_REFUSE_FIRST_MERGE="1")
    assert result.returncode == 0, result.stdout + result.stderr
    assert _merged(world)


_IMAGES = re.compile(r'"images": \d+')


def _with_images(stats: str, count: int) -> str:
    """The stats text with its first images total set to ``count``, whatever the true total is."""
    assert _IMAGES.search(stats), "the retail stats carry no images total"
    return _IMAGES.sub(f'"images": {count}', stats, count=1)


def _conflicting_retail_stats(world: dict) -> tuple[str, str]:
    """A PR and main that edit one total of the retail stats two ways; and the true file."""
    true = (world["checkout"] / _RETAIL_STATS).read_text()
    head = _open_pr(
        world,
        {**_GREEN, _RETAIL_STATS: _with_images(true, 910021)},
        on_main={_RETAIL_STATS: _with_images(true, 910031)},
    )
    return head, true


def test_a_conflict_in_the_retail_stats_is_resolved_by_the_rebuild(world: dict) -> None:
    """gen#343: gen#323, #328 and #335 each stopped here and needed a hand merge."""
    head, true = _conflicting_retail_stats(world)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_RETAIL="1")
    assert result.returncode == 0, result.stdout + result.stderr
    pushed = _branch(world)
    assert _git(world["origin"], "merge-base", "--is-ancestor", "main", pushed) == ""
    # Neither side's total: the retail rebuild's.
    assert _git(world["origin"], "show", f"{pushed}:{_RETAIL_STATS}") + "\n" == true
    assert _merged(world)


def test_a_stale_retail_stats_is_rebuilt_on_the_merged_tree_and_pushed(world: dict) -> None:
    """No conflict, wrong totals: the auto-merge the script exists to catch, for retail."""
    true = (world["checkout"] / _RETAIL_STATS).read_text()
    head = _open_pr(
        world, {**_GREEN, _RETAIL_STATS: _with_images(true, 910021)}
    )
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_RETAIL="1")
    assert result.returncode == 0, result.stdout + result.stderr
    pushed = _branch(world)
    assert pushed != head, "the merged and rebuilt tree was not pushed"
    assert _git(world["origin"], "show", f"{pushed}:{_RETAIL_STATS}") + "\n" == true
    assert _merged(world)


def test_a_retail_stats_the_rebuild_left_conflicted_is_refused(world: dict) -> None:
    head, _ = _conflicting_retail_stats(world)
    result = _run(world, head, _GREEN_CHECK)
    assert result.returncode != 0
    assert "still holds conflict markers" in result.stderr, result.stderr[-800:]
    assert _RETAIL_STATS in result.stderr
    assert _branch(world) == head
    assert not _merged(world)


def test_a_retail_rebuild_that_fails_refuses_the_merge(world: dict) -> None:
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_RETAIL_FAIL="1")
    assert result.returncode != 0
    assert "the retail rebuild refuses the merged tree" in result.stderr, result.stderr[-800:]
    assert _branch(world) == head
    assert not _merged(world)


# -- a check run that is not a green run ------------------------------------


def test_a_check_run_in_which_no_test_passed_is_not_green(world: dict) -> None:
    """Pytest exits 0 when every test is skipped; that run proved nothing."""
    plant = {
        "tests/test_planted_skipped.py": (
            "import pytest\npytestmark = pytest.mark.skip('flaky')\n"
            "def test_planted():\n    assert False\n"
        )
    }
    head = _open_pr(world, plant)
    result = _run(world, head, "tests/test_planted_skipped.py")
    assert result.returncode != 0
    assert "no test passed" in result.stderr, result.stdout[-800:] + result.stderr[-800:]
    assert _branch(world) == head
    assert not _merged(world)


# -- the PR's own CI, on the exact tree that merges --------------------------


@pytest.mark.parametrize(
    "ci, refusal",
    [
        # A test outside the script's checks is red in the PR's own CI.
        ("red", "check tests (2) on {sha} is failure"),
        ("skipped", "check tests (1) on {sha} was skipped"),
        ("missing", "missing: tests"),
        ("pending", "still running: tests"),
        # CI ran on the PR head, never on the merge the script pushed.
        (
            "head-only",
            "missing: lint tests commit-messages file-size red-commit-proof customer-name-check",
        ),
    ],
    ids=["red", "skipped", "missing", "pending", "head-only"],
)
def test_a_merge_waits_for_every_check_on_the_pushed_tree(
    world: dict, ci: str, refusal: str
) -> None:
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_GH_CI=ci)
    pushed = _branch(world)
    assert pushed != head
    assert result.returncode != 0
    assert refusal.format(sha=pushed) in result.stderr, result.stderr[-800:]
    assert "NOT merged" in result.stderr
    assert _ci_reads(world) == [pushed]
    assert not _merged(world)


def test_a_build_the_network_stops_says_so_apart_from_the_build_refusing(world: dict) -> None:
    """Online, a dropped lookup stops the build; the script names the network (#178)."""
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, UV_OFFLINE="0")
    assert result.returncode != 0
    # The word, not the substring: the throwaway path the script names holds this test's name.
    lines = [line for line in result.stderr.splitlines() if re.search(r"\bnetwork\b", line, re.I)]
    assert len(lines) == 1, result.stderr[-800:]
    assert "the build refuses the merged tree" not in lines[0]
    assert "the build refuses the merged tree" in result.stderr
    assert "dns error" in result.stderr, "uv's own message is still printed"
    assert _branch(world) == head
    assert not _merged(world)


def test_with_nothing_to_push_the_heads_own_ci_gates_the_merge(world: dict) -> None:
    head = _open_pr(world, _GREEN, main_moves=False)
    result = _run(world, head, _GREEN_CHECK, FAKE_GH_CI="red")
    assert result.returncode != 0
    # The check is a shard of the sharded tests job (`tests (2)`), or plain `tests`.
    assert re.search(rf"check tests( \(\d+\))? on {head} is failure", result.stderr), (
        result.stderr[-800:]
    )
    assert not _merged(world)


# -- main or the head moving mid-run -----------------------------------------


def test_main_that_moves_during_the_checks_is_not_merged_onto(world: dict) -> None:
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_MOVE="main")
    assert result.returncode != 0
    assert "main moved to" in result.stderr, result.stderr[-800:]
    assert not _merged(world)


def test_main_that_moves_between_merge_attempts_is_not_merged_onto(world: dict) -> None:
    """The first merge is refused (mergeability) and meanwhile another PR lands."""
    head = _open_pr(world, _GREEN)
    result = _run(
        world,
        head,
        _GREEN_CHECK,
        FAKE_GH_REFUSE_FIRST_MERGE="1",
        FAKE_GH_MOVE_ON_REFUSAL="main",
    )
    assert result.returncode != 0
    assert "main moved to" in result.stderr, result.stderr[-800:]
    assert not _merged(world), "merged after main moved past the base the checks ran on"


def test_a_head_that_moves_while_cloning_is_refused(world: dict) -> None:
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_GH_MOVE_ON_VIEW="pr-branch")
    assert result.returncode != 0
    assert "head moved while cloning" in result.stderr, result.stderr[-800:]
    assert not _merged(world)


def test_a_head_that_moves_during_the_checks_is_neither_overwritten_nor_merged(
    world: dict,
) -> None:
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_MOVE="pr-branch")
    assert result.returncode != 0
    assert "the push" in result.stderr and "refused" in result.stderr, result.stderr[-800:]
    moved = _branch(world)
    assert moved != head
    assert _git(world["origin"], "log", "-1", "--format=%s", moved) == "pr-branch moves on"
    assert not _merged(world)


def test_a_head_that_moves_with_nothing_to_push_is_not_merged(world: dict) -> None:
    head = _open_pr(world, _GREEN, main_moves=False)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_MOVE="pr-branch")
    assert result.returncode != 0
    assert "pr-branch moved to" in result.stderr, result.stderr[-800:]
    assert not _merged(world)


# -- conflicts ----------------------------------------------------------------


def test_a_conflict_outside_the_generated_files_is_handed_back(world: dict) -> None:
    readme = (world["checkout"] / "README.md").read_text()
    head = _open_pr(
        world,
        {"README.md": readme + "\nPR side\n"},
        on_main={"README.md": readme + "\nmain side\n"},
    )
    result = _run(world, head, _GREEN_CHECK)
    assert result.returncode != 0
    assert "conflicts outside the generated files" in result.stderr, result.stderr[-800:]
    assert "README.md" in result.stderr
    assert _branch(world) == head
    assert not _merged(world)


def test_a_conflict_in_a_file_the_build_does_not_write_is_handed_back(world: dict) -> None:
    """Under golden-catalog/ but not written by the build: main's edit would be lost."""
    head = _open_pr(
        world,
        {"golden-catalog/NOTES.md": "PR side\n"},
        on_main={"golden-catalog/NOTES.md": "main side: a real edit\n"},
    )
    result = _run(world, head, _GREEN_CHECK)
    assert result.returncode != 0
    assert "conflicts outside the generated files" in result.stderr, result.stderr[-800:]
    assert "golden-catalog/NOTES.md" in result.stderr
    assert _branch(world) == head
    assert not _merged(world)


def _conflicting_stats(world: dict) -> tuple[str, str]:
    """A PR and main that edit one line of stats.json two ways; and the true file."""
    true = (world["checkout"] / _STATS).read_text()
    head = _open_pr(
        world,
        {_STATS: true.replace('"lines": ', '"lines": 1', 1)},
        on_main={_STATS: true.replace('"lines": ', '"lines": 2', 1)},
    )
    return head, true


def test_a_conflict_in_generated_output_is_resolved_by_the_rebuild(world: dict) -> None:
    head, true = _conflicting_stats(world)
    result = _run(world, head, "tests/test_catalog_golden.py")
    assert result.returncode == 0, result.stdout + result.stderr
    pushed = _branch(world)
    assert _git(world["origin"], "merge-base", "--is-ancestor", "main", pushed) == ""
    assert _git(world["origin"], "show", f"{pushed}:{_STATS}") + "\n" == true
    # Neither side's line: the rebuild's.
    assert _merged(world)


def test_a_generated_file_the_rebuild_left_conflicted_is_refused(world: dict) -> None:
    head, _ = _conflicting_stats(world)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_SKIP_BUILD="1")
    assert result.returncode != 0
    assert "still holds conflict markers" in result.stderr, result.stderr[-800:]
    assert _STATS in result.stderr
    assert _branch(world) == head
    assert not _merged(world)


# -- two type PRs, one after the other (#103) ---------------------------------

_BALL_MODULE = Path("src/synthetic_ecommerce_data/domains/industrial/product_types/raw_materials")


def _add_a_type(world: dict, branch: str, key: str, label: str) -> str:
    """A PR branch off main that adds the breadth type ``key`` the way
    docs/adding-a-type.md says: a module declaring its own label, and the
    rebuilt golden.

    The module is the precision-ball one under a new key. Both keys sort
    straight after ``ball_stock_precision``, so were the label a line of a
    shared table, the two branches would edit the same lines of it."""
    checkout = world["checkout"]
    _git(checkout, "switch", "-q", "-c", branch, "main")
    module = (checkout / _BALL_MODULE / "ball_stock_precision.py").read_text()
    module = module.replace(
        '    "ball_stock_precision",\n', f'    "{key}",\n    label="{label}",\n'
    )
    assert f'label="{label}"' in module
    (checkout / _BALL_MODULE / f"{key}.py").write_text(
        module.replace("ball_stock_precision", key).replace("Precision Balls", label + "s")
    )
    built = subprocess.run(
        ["uv", "run", "--locked", "ecom-generate", "build", "--out", "golden-catalog"],
        cwd=checkout,
        env=world["env"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert built.returncode == 0, built.stdout + built.stderr
    _git(checkout, "add", "-A")
    _git(checkout, "commit", "-q", "-m", f"adds {key}")
    _git(checkout, "push", "-q", "origin", branch)
    head = _git(checkout, "rev-parse", "HEAD")
    _git(checkout, "switch", "-q", "main")
    return head


def test_two_prs_that_each_add_a_type_merge_one_after_the_other_by_the_script(
    world: dict,
) -> None:
    """The done-when of #103: no hand merge for the second PR."""
    heads = {
        "pr-a": _add_a_type(world, "pr-a", "ball_stock_ptfe", "Ptfe Ball"),
        "pr-b": _add_a_type(world, "pr-b", "ball_stock_quartz", "Quartz Ball"),
    }
    for branch, head in heads.items():
        result = _run(
            world,
            head,
            "tests/test_catalog_golden.py tests/test_product_type_label_331.py",
            FAKE_GH_BRANCH=branch,
            FAKE_GH_LAND="1",
        )
        assert result.returncode == 0, f"{branch}: {result.stdout}{result.stderr}"
    # The second one met a main that held the first: it was merged and rebuilt.
    assert "conflicts only in generated files" in result.stdout, result.stdout
    flat = _git(world["origin"], "show", "main:golden-catalog/flat.jsonl")
    for key in ("ball_stock_ptfe", "ball_stock_quartz"):
        assert key in flat, key
    assert len(world["log"].read_text().splitlines()) == 2


# -- what the rebuild commits ------------------------------------------------


def _without_dependencies(pyproject: str) -> str:
    """The same project with no dependency at all, so ``uv.lock`` is stale.

    ``uv run --locked`` has to re-resolve before it can call a lock stale, and
    offline that resolve reads registry metadata only from uv's cache. With no
    package left to look up, the resolve needs no registry and the refusal does
    not depend on what the cache holds (#338). Adding a dependency would.
    """
    emptied = re.sub(r"^dependencies = \[.*?^\]", "dependencies = []", pyproject, flags=re.S | re.M)
    emptied = re.sub(r"^dev = \[.*?^\]", "dev = []", emptied, flags=re.S | re.M)
    assert emptied != pyproject and "matplotlib" not in emptied.split("[build-system]")[0]
    return emptied


@pytest.mark.parametrize("cache", ["inherited", "empty"])
def test_a_stale_lock_is_refused_not_relocked_and_committed(
    world: dict, tmp_path: Path, cache: str
) -> None:
    """``uv run`` would re-lock it, and the rebuild commit would carry ``uv.lock``.

    ``empty`` runs the script on a cold uv cache, as a new machine or a CI runner
    has one: the refusal must not depend on what the cache holds (#338).
    """
    pyproject = (world["checkout"] / "pyproject.toml").read_text()
    stale_lock = _without_dependencies(pyproject)
    head = _open_pr(world, {"pyproject.toml": stale_lock})
    if os.environ.get("GITHUB_ACTIONS") == "true":
        # Deciding that the lock is stale re-resolves it, which needs the index; a hosted
        # runner has the network and a cold cache, a developer's machine the warm cache.
        for name in ("UV_OFFLINE", "FAKE_UV_DNS_DOWN", *_NO_NAME_RESOLUTION):
            world["env"].pop(name, None)
    env = {"UV_CACHE_DIR": str(tmp_path / "cold-uv-cache")} if cache == "empty" else {}
    result = _run(world, head, _GREEN_CHECK, **env)
    assert result.returncode != 0
    assert "--locked" in result.stderr, result.stderr[-800:]
    assert _branch(world) == head
    assert not _merged(world)


def test_a_change_the_rebuild_makes_outside_the_generated_files_is_refused(
    world: dict,
) -> None:
    """Only the generated files are committed, and nothing else may be left over."""
    head = _open_pr(world, _GREEN)
    result = _run(world, head, _GREEN_CHECK, FAKE_UV_SKIP_BUILD="1", FAKE_UV_STRAY="stray.txt")
    assert result.returncode != 0
    assert "changes outside the generated files" in result.stderr, result.stderr[-800:]
    assert "stray.txt" in result.stderr
    assert _branch(world) == head
    assert not _merged(world)


def _printed(flag: str) -> list[str]:
    return subprocess.run(
        [str(SCRIPT), flag], capture_output=True, text=True, check=True
    ).stdout.splitlines()


def test_the_generated_files_are_exactly_what_the_build_writes() -> None:
    """Only a file the rebuild rewrites may have a conflict resolved by it."""
    golden = _git(REPO, "ls-files", "golden-catalog").splitlines()
    retail = _git(REPO, "ls-files", "golden-retail").splitlines()
    field_map = cli.field_map_target().relative_to(REPO).as_posix()
    assert sorted(_printed("--print-generated")) == sorted([*golden, *retail, field_map])


def test_the_retail_rebuild_is_the_command_the_retail_figures_name() -> None:
    """One command writes golden-retail/stats.json; the script runs that file, not a copy."""
    figures = (REPO / "prototypes" / "retail_drawings" / "retail_figures.py").read_text()
    named = re.search(r'^REBUILD = "python3 (\S+)"$', figures, re.MULTILINE)
    assert named, "retail_figures.py no longer names its rebuild command"
    assert named.group(1) in SCRIPT.read_text()


def test_the_ci_checks_a_merge_waits_for_are_the_workflows_jobs() -> None:
    """Every job a pull request runs is required; a push-only job is skipped by design."""
    jobs = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yaml").read_text())["jobs"]
    push_only = {key for key, job in jobs.items() if job.get("if") == "github.event_name == 'push'"}
    want = sorted(
        [f"required {key}" for key in jobs if key not in push_only]
        + [f"skipped-by-design {key}" for key in push_only]
    )
    assert sorted(_printed("--print-ci")) == want


# -- the main-merged-tree job ------------------------------------------------


def _job_run(job: str) -> str:
    jobs = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yaml").read_text())["jobs"]
    return jobs[job]["steps"][-1]["run"]


@pytest.mark.parametrize(
    "path, edit",
    [
        (_STATS, lambda t: t.replace('"lines": ', '"lines": 1', 1)),
        (
            "src/prism_synthetic_industrial/data/field_weights/synthetic_industrial_flat.yaml",
            lambda t: t + "\n# hand edit\n",
        ),
    ],
    ids=["stats-auto-merged-wrong", "field-weights-hand-edit"],
)
def test_main_merged_tree_job_is_red_on_a_broken_main(tmp_path: Path, path: str, edit) -> None:
    tree = tmp_path / "main"
    subprocess.run(["git", "clone", "-q", str(REPO), str(tree)], check=True)
    shutil.copy2(REPO / ".github" / "workflows" / "ci.yaml", tree / ".github/workflows/ci.yaml")
    shutil.copy2(SCRIPT, tree / "scripts" / "merge_pr.sh")
    target = tree / path
    target.write_text(edit(target.read_text()))
    # The shell GitHub runs a ``run:`` step with.
    result = subprocess.run(
        ["bash", "--noprofile", "--norc", "-eo", "pipefail", "-c", _job_run("main-merged-tree")],
        cwd=tree,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0, "main-merged-tree is green on a broken main"


# -- --local-ci: the workflows' jobs run here, GitHub is not asked -----------


def _workflow(**commands: str) -> dict[str, str]:
    """A planted workflow whose jobs run ``commands`` (job id -> shell)."""
    jobs = "".join(
        f"  {job}:\n    runs-on: ubuntu-latest\n    steps:\n"
        f"      - uses: actions/checkout@v4\n      - name: run it\n        run: {run!r}\n"
        for job, run in commands.items()
    )
    return {".github/workflows/ci.yaml": f"name: CI\non: [pull_request]\njobs:\n{jobs}"}


_ALL_GREEN = _workflow(
    tests="echo suite",
    lint="echo lint",
    **{
        "commit-messages": "echo msgs",
        "file-size": "echo size",
        "red-commit-proof": "echo red",
        "customer-name-check": "echo names",
        "main-merged-tree": "echo drift",
    },
)


def test_local_ci_runs_every_job_logs_each_and_merges_without_asking_github(world: dict) -> None:
    head = _open_pr(world, {**_GREEN, **_ALL_GREEN})
    done = _run(world, head, _GREEN_CHECK, "--local-ci", "--label", "lbl")
    assert done.returncode == 0, done.stderr
    for job in (
        "tests",
        "commit-messages",
        "file-size",
        "red-commit-proof",
        "customer-name-check",
        "main-merged-tree",
    ):
        assert f"local CI {job}: PASS" in done.stdout
        assert (world["log"].parent / f"lbl-{job}.log").is_file()
    assert "suite" in (world["log"].parent / "lbl-tests.log").read_text()
    assert _ci_reads(world) == [], "GitHub's checks were read"
    assert _merged(world)


def test_a_failing_local_job_refuses_the_merge_but_the_others_still_run(world: dict) -> None:
    plant = _workflow(
        tests="echo suite",
        **{
            "lint": "true",
            "commit-messages": "echo bad >&2; exit 3",
            "file-size": "true",
            "red-commit-proof": "true",
            "customer-name-check": "true",
        },
    )
    head = _open_pr(world, {**_GREEN, **plant})
    done = _run(world, head, _GREEN_CHECK, "--local-ci", "--label", "lbl")
    assert done.returncode != 0
    assert "local CI commit-messages: FAIL" in done.stdout
    assert "local CI tests: PASS" in done.stdout
    assert "bad" in (world["log"].parent / "lbl-commit-messages.log").read_text()
    assert not _merged(world)
    assert _ci_reads(world) == []


def test_a_failing_local_job_fails_a_dry_run_too(world: dict) -> None:
    plant = _workflow(
        tests="exit 1",
        **{
            "lint": "true",
            "commit-messages": "true",
            "file-size": "true",
            "red-commit-proof": "true",
            "customer-name-check": "true",
        },
    )
    head = _open_pr(world, {**_GREEN, **plant})
    done = _run(world, head, _GREEN_CHECK, "--dry-run", "--local-ci")
    assert done.returncode != 0
    assert "local CI tests: FAIL" in done.stdout
    assert not _merged(world)


def test_a_required_check_missing_from_the_workflows_refuses(world: dict) -> None:
    head = _open_pr(world, {**_GREEN, **_workflow(tests="true", lint="true")})
    done = _run(world, head, _GREEN_CHECK, "--local-ci")
    assert done.returncode != 0
    assert "commit-messages is not a job" in done.stderr
    assert not _merged(world)


def test_a_workflow_job_with_no_local_equivalent_refuses(world: dict) -> None:
    odd = {
        ".github/workflows/ci.yaml": "name: CI\non: [pull_request]\njobs:\n"
        "  tests:\n    runs-on: x\n    steps:\n      - uses: some/deploy@v1\n"
    }
    head = _open_pr(world, {**_GREEN, **odd})
    done = _run(world, head, _GREEN_CHECK, "--local-ci")
    assert done.returncode != 0
    assert "no local equivalent" in done.stderr
    assert not _merged(world)


def test_gen_local_ci_makes_it_the_default(world: dict) -> None:
    head = _open_pr(world, {**_GREEN, **_ALL_GREEN})
    done = _run(world, head, _GREEN_CHECK, GEN_LOCAL_CI="1")
    assert done.returncode == 0, done.stderr
    assert "local CI tests: PASS" in done.stdout
    assert _ci_reads(world) == []


def test_without_the_flag_or_the_variable_github_is_still_what_is_waited_for(world: dict) -> None:
    head = _open_pr(world, _GREEN)
    done = _run(world, head, _GREEN_CHECK)
    assert done.returncode == 0, done.stderr
    assert "local CI" not in done.stdout
    assert _ci_reads(world)


# -- a local CI red that is only a stale golden is regenerated, not handed back (#440) --

_FRESH = "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build"
_EXACTLY_FRESH = (
    "tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output"
)
_RETAIL_FRESH = (
    "tests/test_retail_figures_162.py::test_the_committed_figures_are_what_the_build_measures"
)
_FIELD_MAP_FRESH = (
    "tests/test_prism_field_map_drift.py::test_committed_field_map_matches_a_fresh_derivation"
)
_STATS_FRESH = "tests/test_catalog_golden.py::test_stats_reports_the_catalog_that_was_committed"
_ALL_FRESH = [_FRESH, _EXACTLY_FRESH, _RETAIL_FRESH, _FIELD_MAP_FRESH, _STATS_FRESH]

#: A ``tests`` job that is red the way the golden freshness test is: it prints the
#: pytest summary line of that test unless golden-catalog/stats.json is main's.
_STALE_UNLESS_MAINS = (
    "git show origin/main:golden-catalog/stats.json | cmp -s - golden-catalog/stats.json"
    f' || {{ echo "FAILED {_FRESH}[stats.json] - differs"; exit 1; }}'
)
_OTHER_JOBS = {
    "lint": "true",
    "commit-messages": "true",
    "file-size": "true",
    "red-commit-proof": "true",
    "customer-name-check": "true",
}


def _stale_golden_pr(world: dict, tests_job: str) -> str:
    """A PR whose golden is stale and whose first rebuild on the merged tree does
    nothing (``FAKE_UV_SKIP_BUILD_ONCE``): the red the local CI sees is the
    freshness test's, after step 2 had its chance."""
    stats = world["checkout"] / _STATS
    stale = stats.read_text().replace('"lines": ', '"lines": 1', 1)
    plant = {**_GREEN, _STATS: stale, **_workflow(tests=tests_job, **_OTHER_JOBS)}
    return _open_pr(world, plant)


def _subject(world: dict, rev: str) -> str:
    return _git(world["origin"], "log", "-1", "--format=%s", rev)


def test_a_local_ci_red_that_is_only_the_golden_freshness_test_is_regenerated_and_merged(
    world: dict,
) -> None:
    head = _stale_golden_pr(world, _STALE_UNLESS_MAINS)
    done = _run(
        world, head, _GREEN_CHECK, "--local-ci", "--label", "lbl", FAKE_UV_SKIP_BUILD_ONCE="1"
    )
    assert done.returncode == 0, done.stdout + done.stderr
    pushed = _branch(world)
    assert _subject(world, pushed) == "regenerate golden on main"
    changed = _git(world["origin"], "show", "--stat", "--format=", "--name-only", pushed).split()
    assert changed == [_STATS], changed
    assert _git(world["origin"], "show", f"{pushed}:{_STATS}") == _git(
        world["origin"], "show", f"main:{_STATS}"
    )
    assert done.stdout.count("local CI tests: FAIL") == 1
    assert done.stdout.count("local CI tests: PASS") == 1
    # The merge is of the regenerated commit, and the first run's log is kept.
    assert world["log"].read_text().split()[-1] == pushed
    before = world["log"].parent / "lbl-tests.log.before-regenerate"
    assert before.is_file(), "the first run's log was not kept"
    assert "FAILED" in before.read_text()
    assert _ci_reads(world) == []


def _red_on(*ids: str) -> str:
    """A ``tests`` job that is red the way a test runner reports a stale generated file
    (one ``FAILED`` or ``ERROR`` summary line per id) unless the golden is main's."""
    lines = "; ".join(f'echo "{line}"' for line in ids)
    return _STALE_UNLESS_MAINS.replace(
        f'echo "FAILED {_FRESH}[stats.json] - differs"; exit 1', f"{lines}; exit 1"
    )


@pytest.mark.parametrize("node", [_FIELD_MAP_FRESH, _STATS_FRESH])
def test_a_red_on_the_field_map_or_the_stats_freshness_test_is_regenerated(
    world: dict, node: str
) -> None:
    """A stale field-weights YAML reds the drift test, and a stale stats.json the stats
    test: #440 names both, and each is a test of a generated file (the PR review)."""
    head = _stale_golden_pr(world, _red_on(f"FAILED {node}"))
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode == 0, done.stdout + done.stderr
    assert _subject(world, _branch(world)) == "regenerate golden on main"
    assert done.stdout.count("local CI tests: FAIL") == 1
    assert _merged(world)


def test_the_stale_yaml_signature_of_the_incident_is_regenerated(world: dict) -> None:
    """The drift test FAILED beside the golden directory and file tests ERRORed, as the
    runner printed them for a stale field-weights YAML on a merged tree."""
    ids = [
        f"FAILED {_FIELD_MAP_FRESH}",
        f"ERROR {_EXACTLY_FRESH}",
        *(f"ERROR {_FRESH}[{name}]" for name in ("flat.jsonl", "stats.json", "render.jsonl")),
    ]
    head = _stale_golden_pr(world, _red_on(*ids))
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode == 0, done.stdout + done.stderr
    assert _subject(world, _branch(world)) == "regenerate golden on main"
    assert _merged(world)


def test_a_local_ci_red_on_the_golden_freshness_and_another_test_is_not_regenerated(
    world: dict,
) -> None:
    tests_job = _STALE_UNLESS_MAINS.replace(
        "exit 1", "echo FAILED tests/test_other.py::test_x; exit 1"
    )
    head = _stale_golden_pr(world, tests_job)
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode != 0
    assert "local CI is red" in done.stderr
    assert done.stdout.count("local CI tests:") == 1, "the suite was run a second time"
    assert _subject(world, _branch(world)) != "regenerate golden on main"
    assert not _merged(world)


def test_a_local_ci_red_on_another_test_alone_is_not_regenerated(world: dict) -> None:
    head = _stale_golden_pr(world, 'echo "FAILED tests/test_other.py::test_x - boom"; exit 1')
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode != 0
    assert done.stdout.count("local CI tests:") == 1
    assert _subject(world, _branch(world)) != "regenerate golden on main"
    assert not _merged(world)


def test_a_red_with_no_pytest_failure_line_is_not_taken_for_a_stale_golden(world: dict) -> None:
    head = _stale_golden_pr(world, "exit 1")
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode != 0
    assert done.stdout.count("local CI tests:") == 1
    assert not _merged(world)


def test_a_freshness_red_beside_a_red_job_that_is_not_pytest_is_not_regenerated(
    world: dict,
) -> None:
    stats = world["checkout"] / _STATS
    stale = stats.read_text().replace('"lines": ', '"lines": 1', 1)
    jobs = {**_OTHER_JOBS, "file-size": "echo too big; exit 1"}
    plant = {**_GREEN, _STATS: stale, **_workflow(tests=_STALE_UNLESS_MAINS, **jobs)}
    head = _open_pr(world, plant)
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode != 0
    assert "local CI file-size: FAIL" in done.stdout
    assert done.stdout.count("local CI tests:") == 1, "the suite was run a second time"
    assert _subject(world, _branch(world)) != "regenerate golden on main"
    assert not _merged(world)


def test_a_golden_that_is_still_red_after_the_regeneration_is_regenerated_once_only(
    world: dict,
) -> None:
    always = f'echo "FAILED {_FRESH}[stats.json] - differs"; exit 1'
    head = _stale_golden_pr(world, always)
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode != 0
    assert "after the golden regeneration" in done.stderr
    assert done.stdout.count("local CI tests: FAIL") == 2
    assert not _merged(world)
    assert _subject(world, _branch(world)) != "regenerate golden on main", (
        "a regenerated tree that is still red was pushed"
    )


def test_a_freshness_red_a_rebuild_does_not_change_is_not_merged(world: dict) -> None:
    """The generator is nondeterministic, or the test is red for another reason."""
    always = f'echo "FAILED {_FRESH}[stats.json] - differs"; exit 1'
    head = _stale_golden_pr(world, always)
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD="1")
    assert done.returncode != 0
    assert "a rebuild changes nothing" in done.stderr
    assert not _merged(world)


#: A ``tests`` job that is red like the freshness test until the golden is main's and,
#: on the second run, moves the PR branch on the origin as a builder's push does.
_MOVES_THE_HEAD_ON_THE_SECOND_RUN = _STALE_UNLESS_MAINS.replace(
    " || {",
    " && { new=$(git -C $FAKE_ORIGIN commit-tree pr-branch^{tree} -p pr-branch -m moved);"
    " git -C $FAKE_ORIGIN update-ref refs/heads/pr-branch $new; } || {",
    1,
)


def test_a_head_that_moves_during_the_second_run_is_neither_overwritten_nor_merged(
    world: dict,
) -> None:
    """The push of the regenerated commit is not forced, as the first push is not."""
    head = _stale_golden_pr(world, _MOVES_THE_HEAD_ON_THE_SECOND_RUN)
    done = _run(world, head, _GREEN_CHECK, "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode != 0, done.stdout + done.stderr
    assert "the push of the regenerated" in done.stderr and "refused" in done.stderr, done.stderr
    moved = _branch(world)
    assert moved != head
    assert _subject(world, moved) == "moved", "the builder's push was overwritten"
    assert not _merged(world)


def test_a_dry_run_regenerates_the_golden_but_pushes_and_merges_nothing(world: dict) -> None:
    head = _stale_golden_pr(world, _STALE_UNLESS_MAINS)
    done = _run(world, head, _GREEN_CHECK, "--dry-run", "--local-ci", FAKE_UV_SKIP_BUILD_ONCE="1")
    assert done.returncode == 0, done.stdout + done.stderr
    assert done.stdout.count("local CI tests: PASS") == 1
    assert "dry run: would push" in done.stdout
    assert _branch(world) == head
    assert not _merged(world)


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


# -- the one parser: every workflow job has a local equivalent ---------------


def _jobs_cli(*args: str, workflows: Path = WORKFLOWS) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python3", str(JOBS_SCRIPT), "--workflows", str(workflows), *args],
        capture_output=True,
        text=True,
        check=False,
    )


def test_every_job_of_the_real_workflows_has_a_local_equivalent() -> None:
    declared = []
    for path in sorted(WORKFLOWS.glob("*.y*ml")):
        declared += list(yaml.safe_load(path.read_text())["jobs"])
    listed = _jobs_cli("--list")
    assert listed.returncode == 0, listed.stderr
    assert listed.stdout.split() == declared
    for job in declared:
        emitted = _jobs_cli("--emit", job, "--base", "BBB", "--head", "HHH")
        assert emitted.returncode == 0, emitted.stderr
        assert "uv run" in emitted.stdout or "python3" in emitted.stdout
    msgs = _jobs_cli("--emit", "commit-messages", "--base", "BBB", "--head", "HHH")
    assert "BBB..HHH" in msgs.stdout


def test_the_local_jobs_are_the_pull_request_checks_a_merge_requires() -> None:
    required = [line.split()[1] for line in _printed("--print-ci") if line.startswith("required")]
    assert set(required) <= set(_jobs_cli("--list").stdout.split())


def test_a_new_workflow_job_nobody_can_run_locally_fails_the_parser(tmp_path: Path) -> None:
    (tmp_path / "extra.yml").write_text(
        "on: push\njobs:\n  deploy:\n    runs-on: x\n    steps:\n      - uses: some/deploy@v1\n"
    )
    assert _jobs_cli("--list", workflows=tmp_path).returncode != 0
    (tmp_path / "extra.yml").write_text(
        "on: push\njobs:\n  odd:\n    runs-on: x\n    steps:\n"
        "      - run: echo ${{ secrets.TOKEN }}\n"
    )
    assert _jobs_cli("--list", workflows=tmp_path).returncode != 0


def test_a_step_if_and_settings_the_parser_cannot_honour_refuse(tmp_path: Path) -> None:
    plants = [
        "jobs:\n  a:\n    steps:\n      - run: echo x\n        if: false\n",
        "env:\n  X: 1\njobs:\n  a:\n    steps:\n      - run: echo x\n",
        "defaults:\n  run:\n    shell: sh\njobs:\n  a:\n    steps:\n      - run: echo x\n",
        "jobs:\n  a:\n    continue-on-error: true\n    steps:\n      - run: echo x\n",
    ]
    for plant in plants:
        (tmp_path / "w.yml").write_text(plant)
        assert _jobs_cli("--list", workflows=tmp_path).returncode != 0, plant
