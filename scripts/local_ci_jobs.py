#!/usr/bin/env python3
"""Derive the local equivalent of every GitHub Actions job (scripts/merge_pr.sh --local-ci).

GitHub Actions on this repository is billing-blocked, so CI is run locally on
the merged tree instead. This is the one parser that turns the workflow files
into what runs, so the list of local jobs is the workflows' job list and not a
hand-kept copy that drifts.

    local_ci_jobs.py [--workflows DIR] --list
    local_ci_jobs.py [--workflows DIR] --emit JOB --base SHA --head SHA

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
"""

from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path

import yaml

#: Actions that only prepare the runner; the local tree and tools stand in.
SETUP_ACTIONS = ("actions/checkout", "astral-sh/setup-uv", "actions/setup-python")

_EXPR = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")


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
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    args = parser.parse_args(argv)
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
