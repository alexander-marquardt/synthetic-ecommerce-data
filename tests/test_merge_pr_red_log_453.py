"""``merge_pr.sh --local-ci`` names a red job's failures and keeps its log (#453).

On 2026-10-17 a local CI said "red on 1fd4c7ff (failed: tests); NOT merged" and left the
temp directory for inspection, but the tests job's log was not in it, so nobody could name
the failing test without a full re-run (about an hour). What is pinned, in the same planted
worlds as tests/test_merge_pr.py:

* a red job's FAILED/ERROR summary lines (at most 20) are in the script's own output;
* the job's log is copied into the directory the script keeps for inspection;
* a red job with no summary line prints none, and its log is kept all the same.
"""

from __future__ import annotations

import re
from pathlib import Path

import test_merge_pr
from test_merge_pr import (
    _GREEN,
    _GREEN_CHECK,
    _merged,
    _open_pr,
    _run,
    _workflow,
)

# Each case builds its own origin: spread over the workers (tests/xdist_groups.py).
XDIST_SPREAD = True

# The planted worlds are test_merge_pr's `world` fixture; a name bound here is what pytest finds.
world = test_merge_pr.world

#: The other jobs are green: the one named red is the whole of the refusal.
_OTHERS_GREEN = {
    "lint": "true",
    "commit-messages": "true",
    "file-size": "true",
    "red-commit-proof": "true",
    "customer-name-check": "true",
    "no-derived-files": "true",
}


def _red_tests(world: dict, command: str):
    """Run ``--local-ci`` on a PR whose tests job runs ``command``."""
    head = _open_pr(world, {**_GREEN, **_workflow(tests=command, **_OTHERS_GREEN)})
    return _run(world, head, _GREEN_CHECK, "--local-ci", "--label", "lbl")


def _kept_dir(done) -> Path:
    """The inspection directory the script says it left, from its own stderr."""
    found = re.search(r"merge_pr\.sh: left (\S+) for inspection", done.stderr)
    assert found, done.stderr
    return Path(found.group(1))


def _printed_failures(done) -> list[str]:
    lines = done.stdout.splitlines()
    return [line.strip() for line in lines if re.match(r"\s+(FAILED|ERROR) ", line)]


def test_a_red_local_job_prints_its_failed_line_and_keeps_its_log(world: dict) -> None:
    done = _red_tests(
        world, "echo noise; echo 'FAILED tests/test_x.py::test_a - boom'; echo more; exit 1"
    )
    assert done.returncode != 0
    assert "local CI tests: FAIL" in done.stdout
    assert _printed_failures(done) == ["FAILED tests/test_x.py::test_a - boom"]
    kept = _kept_dir(done)
    logs = list(kept.rglob("lbl-tests.log"))
    assert len(logs) == 1, f"the tests job log is not in {kept}"
    assert "FAILED tests/test_x.py::test_a - boom" in logs[0].read_text()
    assert not _merged(world)


def test_an_error_line_is_printed_beside_the_failed_ones(world: dict) -> None:
    done = _red_tests(
        world,
        "echo 'ERROR tests/test_y.py - ImportError'; echo 'FAILED tests/test_x.py::test_a'; exit 1",
    )
    assert done.returncode != 0
    assert sorted(_printed_failures(done)) == [
        "ERROR tests/test_y.py - ImportError",
        "FAILED tests/test_x.py::test_a",
    ]


def test_at_most_twenty_failed_lines_are_printed_and_the_rest_are_counted(world: dict) -> None:
    done = _red_tests(
        world,
        'for i in $(seq 1 25); do echo "FAILED tests/test_x.py::test_$i - boom"; done; exit 1',
    )
    assert done.returncode != 0
    printed = _printed_failures(done)
    assert printed, done.stdout
    assert printed[0] == "FAILED tests/test_x.py::test_1 - boom"
    assert len(printed) == 20, printed
    assert "5 more" in done.stdout
    assert len(list(_kept_dir(done).rglob("lbl-tests.log"))) == 1


def test_a_red_job_with_no_summary_line_prints_none_but_its_log_is_kept(world: dict) -> None:
    done = _red_tests(world, "echo 'Traceback: the job crashed' >&2; exit 3")
    assert done.returncode != 0
    assert _printed_failures(done) == []
    logs = list(_kept_dir(done).rglob("lbl-tests.log"))
    assert len(logs) == 1
    assert "the job crashed" in logs[0].read_text()
    assert not _merged(world)
