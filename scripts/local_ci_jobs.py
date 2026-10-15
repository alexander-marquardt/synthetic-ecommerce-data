#!/usr/bin/env python3
"""Derive the local equivalent of every GitHub Actions job (scripts/merge_pr.sh --local-ci).

GitHub Actions on this repository is billing-blocked, so CI is run locally on
the merged tree instead. This is the one parser that turns the workflow files
into what runs, so the list of local jobs is the workflows' job list and not a
hand-kept copy that drifts.

    local_ci_jobs.py [--workflows DIR] --list
    local_ci_jobs.py [--workflows DIR] --emit JOB --base SHA --head SHA
    local_ci_jobs.py --pytest-options

``--list`` prints one job id per line, in workflow-file then job order.
``--emit`` prints the job's ``run:`` steps as one shell script, to be run with
``bash --noprofile --norc -eo pipefail`` in the tree's root, which is the shell
and the working directory GitHub gives a ``run:`` step.

A job has a local equivalent only if everything in it is understood: the
``uses:`` steps that merely set the machine up (checkout, uv, python) are
dropped because the merged tree and the tools are already here; any other
action, a matrix, a custom shell, or an expression other than the pull
request's base and head shas is an error, never a silent skip. The ``if:`` of
a job is ignored: a pull request's local run executes every job, the
push-only ``main-merged-tree`` included, since it is the same check on the
same tree.

Every emitted step runs with ``PYTEST_ADDOPTS`` carrying ``-n <workers> --dist loadgroup``
(#348): the suite took 47 to 54 minutes on one core and merges are serial, so the suite's
wall time was the rate pull requests landed. The worker count is the cores or, if fewer,
what the memory available allows at ``WORKER_MB`` each (``default_workers``), and never
fewer than two; ``LOCAL_CI_WORKERS`` replaces it (``0`` is one process). The workflow file is not
where this lives: the token that pushes it cannot change ``.github/workflows`` and the
hosted run is billing-blocked, so the local run is the CI that merges.
``tests/test_ci_tests_job_parallel_348.py`` runs the emitted script of the real tests job
and fails if pytest in it gets one worker. ``--pytest-options`` prints the same options
for ``scripts/merge_pr.sh``'s own check step.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

import yaml

#: Actions that only prepare the runner; the local tree and tools stand in.
SETUP_ACTIONS = ("actions/checkout", "astral-sh/setup-uv", "actions/setup-python")

_EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")

#: pytest-xdist options added to every emitted step through ``PYTEST_ADDOPTS`` (#348).
#: ``loadgroup`` keeps a module's tests on one worker (tests/xdist_groups.py).
WORKERS_ENV = "LOCAL_CI_WORKERS"
DIST = "loadgroup"

#: Memory one worker may be budgeted, in MB. Measured on the 88 GB agent VM, whole suite,
#: ``-n 8 --dist loadgroup``: the largest worker ended at 4,311 MB (a worker keeps what
#: each module it ran built), the eight workers and everything they started peaked at
#: 26,814 MB; at ``-n 16`` the tree had reached 38 GB within three minutes, when the probe
#: stopped it. An uncapped ``-n auto`` on this 48-core VM took the host down (10-15
#: 18:27Z), so the count is capped by memory as well as by cores.
WORKER_MB = 4500
#: The share of the memory available at the start that the workers may fill.
MEMORY_SHARE = 0.8
#: One worker is the serial run this issue removes; two fit any machine that runs the suite.
MIN_WORKERS = 2


def memory_available_mb() -> int | None:
    """Memory a new process can use now, in MB: Linux ``MemAvailable``, macOS ``vm_stat``."""
    try:
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError, IndexError):
        pass
    try:
        out = subprocess.run(["vm_stat"], capture_output=True, text=True, check=True).stdout
        size = int(re.search(r"page size of (\d+) bytes", out).group(1))  # type: ignore[union-attr]
        pages = sum(
            int(m.group(1))
            for m in re.finditer(r"^Pages (?:free|inactive|speculative):\s+(\d+)\.", out, re.M)
        )
        return pages * size // (1024 * 1024)
    except (OSError, subprocess.SubprocessError, ValueError, AttributeError):
        return None


def default_workers(cores: int | None = None, available_mb: int | None = None) -> int:
    """Workers for the suite: one per core, fewer when memory is the limit, at least two.

    ``cores`` and ``available_mb`` are read from this machine when not given; memory that
    cannot be read gives the floor, not an unbounded count.
    """
    cores = cores if cores is not None else (os.cpu_count() or MIN_WORKERS)
    available = available_mb if available_mb is not None else memory_available_mb()
    if available is None:
        return MIN_WORKERS
    by_memory = int(available * MEMORY_SHARE // WORKER_MB)
    return max(MIN_WORKERS, min(cores, by_memory))


def pytest_options(
    environ: dict[str, str] | None = None,
    cores: int | None = None,
    available_mb: int | None = None,
) -> str:
    """The options as a string: the worker count from ``LOCAL_CI_WORKERS``, else the machine's."""
    workers = (os.environ if environ is None else environ).get(WORKERS_ENV)
    return f"-n {workers or default_workers(cores, available_mb)} --dist {DIST}"


class NoLocalEquivalent(Exception):
    """A workflow job holds something that cannot be run locally as written."""


def workflow_files(directory: Path) -> list[Path]:
    return sorted([*directory.glob("*.yml"), *directory.glob("*.yaml")])


def load_jobs(directory: Path) -> dict[str, dict]:
    """Every job of every workflow file, by job id (an id used twice is an error)."""
    jobs: dict[str, dict] = {}
    for path in workflow_files(directory):
        document = yaml.safe_load(path.read_text()) or {}
        for key in ("env", "defaults"):
            if key in document:
                raise NoLocalEquivalent(f"{path.name}: workflow {key!r} is not reproduced locally")
        for job_id, job in document.get("jobs", {}).items():
            if job_id in jobs:
                raise NoLocalEquivalent(f"job {job_id!r} is defined twice (in {path.name})")
            jobs[job_id] = job
    return jobs


def _substitute(text: str, values: dict[str, str], where: str) -> str:
    def one(match: re.Match) -> str:
        expression = match.group(1)
        if expression not in values:
            raise NoLocalEquivalent(f"{where}: no local value for ${{{{ {expression} }}}}")
        return values[expression]

    return _EXPR.sub(one, text)


def emit(job_id: str, job: dict, base: str, head: str) -> str:
    """The shell script for one job, or NoLocalEquivalent."""
    values = {
        "github.event.pull_request.base.sha": base,
        "github.event.pull_request.head.sha": head,
    }
    if "strategy" in job or "container" in job or "services" in job:
        raise NoLocalEquivalent(f"{job_id}: a matrix, container or service has no local equivalent")
    for key in ("defaults", "continue-on-error", "needs", "timeout-minutes"):
        if key in job:
            raise NoLocalEquivalent(f"{job_id}: job key {key!r} is not reproduced locally")
    lines = [f"echo {shlex.quote('== job ' + job_id + ' ==')}"]
    # The script is emitted on the machine that runs it, so the count is that machine's own
    # (cores and memory now); LOCAL_CI_WORKERS, read when the script runs, replaces it.
    lines.append(
        'export PYTEST_ADDOPTS="${PYTEST_ADDOPTS:+$PYTEST_ADDOPTS }'
        f'-n ${{{WORKERS_ENV}:-{default_workers()}}} --dist {DIST}"'
    )
    ran = 0
    for number, step in enumerate(job.get("steps", []), 1):
        where = f"{job_id} step {number}"
        for key in ("if", "continue-on-error", "timeout-minutes"):
            if key in step:
                raise NoLocalEquivalent(f"{where}: step key {key!r} is not reproduced locally")
        if "uses" in step:
            if not step["uses"].split("@")[0].startswith(SETUP_ACTIONS):
                raise NoLocalEquivalent(f"{where}: action {step['uses']!r} has no local equivalent")
            continue
        if "run" not in step:
            raise NoLocalEquivalent(f"{where}: neither run nor a known setup action")
        if step.get("shell", "bash") != "bash":
            raise NoLocalEquivalent(f"{where}: shell {step['shell']!r} is not bash")
        if not isinstance(step["run"], str):
            raise NoLocalEquivalent(f"{where}: run is not a string (quote it)")
        env = {**job.get("env", {}), **step.get("env", {})}
        body = _substitute(step["run"], values, where)
        prefix = "".join(
            f"export {key}={shlex.quote(_substitute(str(value), values, where))}\n"
            for key, value in env.items()
        )
        directory = step.get("working-directory")
        title = step.get("name", f"step {number}")
        lines.append(f"echo {shlex.quote('-- ' + title)}")
        cd = f"cd {shlex.quote(directory)}\n" if directory else ""
        lines.append("(\n" + prefix + cd + body + "\n)")
        ran += 1
    if not ran:
        raise NoLocalEquivalent(f"{job_id}: no run step, so nothing to run locally")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--workflows", type=Path, default=Path(".github/workflows"))
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--list", action="store_true")
    action.add_argument("--emit", metavar="JOB")
    action.add_argument("--pytest-options", action="store_true")
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    args = parser.parse_args(argv)
    if args.pytest_options:
        print(pytest_options())
        return 0
    try:
        jobs = load_jobs(args.workflows)
        if not jobs:
            raise NoLocalEquivalent(f"no workflow jobs under {args.workflows}")
        if args.list:
            for job_id, job in jobs.items():
                emit(job_id, job, "BASE", "HEAD")  # refuses a job with no local equivalent
                print(job_id)
            return 0
        if args.emit not in jobs:
            raise NoLocalEquivalent(f"no workflow job {args.emit!r}")
        sys.stdout.write(emit(args.emit, jobs[args.emit], args.base, args.head))
        return 0
    except NoLocalEquivalent as error:
        print(f"local_ci_jobs.py: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
