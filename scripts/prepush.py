#!/usr/bin/env python3
"""The pre-push gate: this repository's cheap CI jobs, run before review (elastic/prism#11677).

    scripts/prepush.sh                          # by hand: blocking, prints a review packet
    scripts/prepush.sh --pr-body-file FILE      # judge a draft PR body for the file-size row
    scripts/prepush.sh --only lint              # re-run one row after a fix
    scripts/prepush.sh --hook                   # what the ``prepush-gate`` pre-push hook runs
    python3 scripts/prepush.py --list           # each row, the CI job it mirrors, its command
    python3 scripts/prepush.py --list-scans     # the tests the ``tree-scans`` row runs

Why it exists. Every mechanical red CI would find cost a CI round and a fix round of
an agent's context. The rows are the commands of the jobs in
``.github/workflows/ci.yaml`` that take seconds and need no network: ``commit-messages``,
``customer-names``, ``lint`` and ``file-size``, and ``tree-scans``, the tests that read every
tracked file.
Each row's argv is read from the workflow (``scripts/local_ci_jobs.py``), never copied;
``tests/test_prepush_gate_11677.py`` fails on a workflow job or step that is neither a row
nor in ``LEFT_TO_CI``. What stays with CI, by name: the whole suite (about 27
minutes), the golden catalog and the merged-tree checks (``scripts/merge_pr.sh``).

The shape is elastic/prism's ``scripts/prepush.sh`` (its job list is not copied):

* a row prints ``    PASS|FAIL|WARN  <name>`` and, for a FAIL, the tail of its output;
* a gate that could not run (no ``origin/main``, no ``uv``, a scan set in which no
  test ran) fails, and never reports a pass it did not earn;
* the whole output is saved as ``<git dir>/prepush.log`` and the last line is
  ``PREPUSH rc=N failed=<rows> log=<path>``;
* a blocking pass prints a REVIEW PACKET for the PR body and saves it beside the log.

By hand the gate blocks. As the hook (``--hook``, the ``prepush-gate`` hook in
``.pre-commit-config.yaml``) it judges the checkout at HEAD, with unstaged edits
stashed by pre-commit, and blocks only a branch that has an OPEN pull request, or
``main``. With none, every row still runs and prints, and the run ends
``ADVISORY — NOT A PASS`` with exit 0, so a work-in-progress push is never refused
and nobody learns to bypass the hook. A push to ``wip/<task>`` is a backup: the
commit-message rule only (a trailer is fixed by rewriting history), then
``NOT JUDGED (wip backup)``. A branch delete is not judged. A pull-request lookup that
fails blocks: the gate cannot tell, and says so.

A deliberate skip is ``SKIP=prepush-gate git push``, which pre-commit prints; CI still
runs every job. Untracked scratch files are in reach of ``ruff check .`` as in CI.

Exit status: 0 pass (or advisory), 1 a row failed, 2 usage, 3 the gate could not judge.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess  # noqa: S404  # runs git, gh, uv and the repo's own scripts, argv lists, never a shell
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE_REF = "origin/main"
#: The wording of the base failure: the fix it names is the only one there is.
FETCH_HINT = "git fetch origin main"
ZEROS = "0" * 40
#: Lines of a failed row's output shown under it; the log keeps all of it.
TAIL_LINES = 40
ROW_TIMEOUT_S = 900

#: The scan tests the ``tree-scans`` row runs: tests that read every tracked file, each in
#: seconds. ``PREPUSH_SCAN_TESTS`` (space separated) replaces them, for this gate's own tests.
SCAN_TESTS = (
    "tests/test_us_spelling.py",
    "tests/test_ignore_hides_only_data_10032.py",
    "tests/test_vendored_core_pin_11683.py",
)

#: Where the CI jobs are read from; ``PREPUSH_WORKFLOWS`` replaces it, for this gate's tests.
WORKFLOWS = ROOT / ".github" / "workflows"

#: Each command a row runs, found in the workflow and not copied here: key -> (CI job, the
#: text that picks the command's line out of the job's ``run:`` steps). The argv a row runs IS
#: that line, so a stricter CI flag, or ``--locked``, reaches the gate with no edit here.
CI_COMMANDS: dict[str, tuple[str, str]] = {
    "commit-messages": ("commit-messages", "check_commit_msg.py"),
    "customer-names": ("customer-name-check", "check_customer_names.py"),
    "lint": ("tests", "ruff check"),
    "file-size": ("file-size", "--no-body-is-advisory"),
    "file-size-body": ("file-size", "--pr-body-file"),
    "tree-scans": ("tests", "pytest"),
}

#: What the gate does not run, by CI job id (or ``job/step name``), and why. A job or step of
#: ``ci.yaml`` that is neither claimed by a row nor listed here fails the drift test, so a new
#: cheap job cannot go unnoticed.
LEFT_TO_CI: dict[str, str] = {
    "main-merged-tree": "the merged-tree checks; scripts/merge_pr.sh --local-ci runs them",
}


class CannotJudge(Exception):
    """The workflow cannot be read into commands: the gate says so and exits 3."""


def workflows_dir() -> Path:
    return Path(os.environ.get("PREPUSH_WORKFLOWS") or WORKFLOWS)


def _jobs(workflows: Path) -> dict[str, dict]:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    try:
        import local_ci_jobs  # noqa: PLC0415  # needs pyyaml; imported where it is used
    except ImportError as error:
        raise CannotJudge(f"cannot read the workflows ({error}); use `uv run --locked`") from error
    try:
        return local_ci_jobs.load_jobs(workflows)
    except (local_ci_jobs.NoLocalEquivalent, OSError) as error:
        raise CannotJudge(f"cannot read {workflows}: {error}") from error


def _run_steps(job: dict) -> list[dict]:
    return [step for step in job.get("steps", []) if "run" in step]


def _statement(run: str, needle: str) -> list[str] | None:
    """The first command of ``run`` whose line holds ``needle``, as argv, up to a shell operator."""
    for line in run.replace("\\\n", " ").splitlines():
        if needle in line:
            tokens = shlex.split(line, comments=True)
            for stop, token in enumerate(tokens):
                if token in ("||", "&&", ";", "|", ">"):
                    return tokens[:stop]
            return tokens
    return None


def ci_commands(workflows: Path = WORKFLOWS) -> dict[str, list[str]]:
    """Every ``CI_COMMANDS`` key to the argv its CI job runs (placeholders not yet filled)."""
    jobs = _jobs(workflows)
    found: dict[str, list[str]] = {}
    for key, (job_id, needle) in CI_COMMANDS.items():
        if job_id not in jobs:
            raise CannotJudge(f"{key}: no CI job {job_id!r} in {workflows}")
        for step in _run_steps(jobs[job_id]):
            argv = _statement(step["run"], needle)
            if argv:
                found[key] = argv
                break
        else:
            raise CannotJudge(f"{key}: no step of CI job {job_id!r} runs a line with {needle!r}")
    return found


def unaccounted(workflows: Path = WORKFLOWS) -> list[str]:
    """Jobs and run steps of the workflows that no row claims and ``LEFT_TO_CI`` does not name."""
    jobs = _jobs(workflows)
    row_jobs = {job_id for job_id, _ in CI_COMMANDS.values()}
    out: list[str] = []
    for job_id, job in jobs.items():
        if job_id in LEFT_TO_CI:
            continue
        if job_id not in row_jobs:
            out.append(job_id)
            continue
        needles = [needle for owner, needle in CI_COMMANDS.values() if owner == job_id]
        for step in _run_steps(job):
            name = f"{job_id}/{step.get('name', step['run'].strip()[:40])}"
            claimed = any(_statement(step["run"], needle) for needle in needles)
            if not claimed and name not in LEFT_TO_CI:
                out.append(name)
    return out


_EXPRESSION = re.compile(r"\$\{\{\s*(.*?)\s*\}\}")


def fill(argv: list[str], values: dict[str, str]) -> list[str]:
    """Replace the workflow's ``${{ }}`` expressions and ``$var`` words with this run's values."""

    def one(token: str) -> str:
        if token in values:
            return values[token]
        return _EXPRESSION.sub(lambda m: values.get(m.group(1), m.group(0)), token)

    return [one(token) for token in argv]


@dataclass
class Result:
    """What one row found: ``verdict`` is PASS, FAIL or WARN; ``judged`` feeds the packet."""

    verdict: str
    judged: str
    output: str = ""


@dataclass
class Context:
    root: Path
    head: str
    merge_base: str
    body_file: str | None
    #: ``ci_commands()``: the argv each CI command runs, read from the workflow.
    ci: dict[str, list[str]]

    def argv(self, key: str) -> list[str]:
        values = {
            "github.event.pull_request.base.sha": self.merge_base,
            "github.event.pull_request.head.sha": self.head,
            "$base": BASE_REF,
            "$body": self.body_file or "",
        }
        return fill(self.ci[key], values)


Row = Callable[[Context], Result]


def scan_tests() -> list[str]:
    override = os.environ.get("PREPUSH_SCAN_TESTS", "").split()
    return override or list(SCAN_TESTS)


def run(argv: list[str], root: Path, timeout: int = ROW_TIMEOUT_S) -> tuple[int, str]:
    """Run ``argv`` in ``root``; a command that cannot start is rc 127, said in words."""
    try:
        done = subprocess.run(  # noqa: S603  # argv list, never a shell
            argv, cwd=root, capture_output=True, text=True, check=False, timeout=timeout
        )
    except FileNotFoundError:
        return 127, f"{argv[0]}: command not found, so this row could not run\n"
    except subprocess.TimeoutExpired:
        return 124, f"{' '.join(argv)}: no verdict in {timeout} s\n"
    return done.returncode, done.stdout + done.stderr


def git(root: Path, *args: str) -> tuple[int, str]:
    rc, out = run(["git", "-C", str(root), *args], root)
    return rc, out.strip()


def row_commit_messages(ctx: Context) -> Result:
    span = f"{ctx.merge_base}..{ctx.head}"
    _, count = git(ctx.root, "rev-list", "--count", span)
    rc, out = run(ctx.argv("commit-messages"), ctx.root)
    judged = f"{count} commit message(s) in {span[:7]}..{ctx.head[:7]}"
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


def row_customer_names(ctx: Context) -> Result:
    """CI's command on the branch's range; no PR exists yet, so the draft body stands in for it."""
    argv = ctx.argv("customer-names")
    if "--pr" in argv:
        at = argv.index("--pr")
        argv = argv[:at] + argv[at + 2 :]
    if ctx.body_file:
        argv = [*argv, "--text-file", ctx.body_file]
    rc, out = run(argv, ctx.root)
    judged = f"the tree and the commits {ctx.merge_base[:7]}..{ctx.head[:7]}"
    if ctx.body_file:
        judged += f", PR body {ctx.body_file}"
    else:
        judged += ", not the PR text (no --pr-body-file)"
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


def row_lint(ctx: Context) -> Result:
    rc, out = run(ctx.argv("lint"), ctx.root)
    return Result("PASS" if rc == 0 else "FAIL", f"ruff check . on {ctx.head[:7]}", out)


def row_file_size(ctx: Context) -> Result:
    if ctx.body_file:
        rc, out = run(ctx.argv("file-size-body"), ctx.root)
        judged = f"against {BASE_REF}, PR body {ctx.body_file}"
        return Result("PASS" if rc == 0 else "FAIL", judged, out)
    rc, out = run(ctx.argv("file-size"), ctx.root)
    if rc == 4:
        # A file over the cap grew and a body line could clear it: only the PR body can say.
        note = (
            out + "file-size: a file over the cap grew; this run read no PR body, so it cannot "
            "say whether a File-Size-Exception line declares it. Re-run with "
            "--pr-body-file <draft body>.\n"
        )
        return Result("WARN", "a growth needs the PR body (--pr-body-file)", note)
    judged = f"against {BASE_REF}, nothing grew past the cap"
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


def row_tree_scans(ctx: Context) -> Result:
    tests = scan_tests()
    rc, out = run([*ctx.argv("tree-scans"), "-p", "no:cacheprovider", *tests], ctx.root)
    found = re.search(r"(\d+) passed", out)
    passed = int(found.group(1)) if found else 0
    judged = f"{passed} passed in {' '.join(tests)}"
    if rc == 0 and passed == 0:
        out += "tree-scans: no test ran (all skipped or none collected), which judges nothing.\n"
        return Result("FAIL", judged, out)
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


#: name, the ``CI_COMMANDS`` key whose command it runs, the row.
ROWS: tuple[tuple[str, str, Row], ...] = (
    ("commit-messages", "commit-messages", row_commit_messages),
    ("customer-names", "customer-names", row_customer_names),
    ("lint", "lint", row_lint),
    ("file-size", "file-size", row_file_size),
    ("tree-scans", "tree-scans", row_tree_scans),
)
ROW_NAMES = [name for name, *_ in ROWS]


def open_pull_requests(root: Path, branch: str) -> int | None:
    """How many open pull requests have ``branch`` as head; None when gh cannot say."""
    rc, out = run(
        ["gh", "pr", "list", "--head", branch, "--state", "open", "--json", "number", "--jq",
         "length"],
        root,
        timeout=60,
    )
    if rc != 0 or not out.strip().isdigit():
        return None
    return int(out.strip())


def packet(head: str, merge_base: str, passed: list[tuple[str, str]], unjudged: list[str]) -> str:
    lines = [
        "### Checked before review",
        "",
        f"`scripts/prepush.sh` at `{head[:12]}` against `{BASE_REF}` (`{merge_base[:12]}`):",
        "",
    ]
    lines += [f"- {name}: {judged}" for name, judged in passed]
    lines += [f"- {text}" for text in unjudged]
    lines += [
        "",
        "Left to CI: the whole suite (golden catalog included)"
        + "".join(f"; {key} ({why})" for key, why in LEFT_TO_CI.items()),
        "",
        "Claims, each with the command that showed it: <FILL: claim and command>",
        "Repro commands: <FILL: commands a reviewer can re-run>",
        "Planted mutants: <FILL: mutants and how many were killed>",
        "",
    ]
    return "\n".join(lines)


def judged_rows(
    selected: list[str], ctx: Context, say: Callable[[str], None]
) -> tuple[list[tuple[str, str]], list[str], list[str]]:
    """Run each selected row; return (passed, unjudged notes, failed names)."""
    passed: list[tuple[str, str]] = []
    unjudged: list[str] = []
    failed: list[str] = []
    for name, _key, row in ROWS:
        if name not in selected:
            continue
        result = row(ctx)
        say(f"    {result.verdict}  {name}  ({result.judged})")
        if result.verdict == "FAIL":
            failed.append(name)
            tail = result.output.rstrip().splitlines()[-TAIL_LINES:]
            for line in tail:
                say(f"        {line}")
        elif result.verdict == "WARN":
            unjudged.append(f"{name}: NOT JUDGED, {result.judged}")
            for line in result.output.rstrip().splitlines()[-TAIL_LINES:]:
                say(f"        {line}")
        else:
            passed.append((name, result.judged))
    return passed, unjudged, failed


def parse(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="prepush.sh", description=__doc__.split("\n")[0])
    parser.add_argument("--hook", action="store_true", help="what the pre-push hook runs")
    parser.add_argument("--pr-body-file", help="a draft PR body, read by the file-size row")
    parser.add_argument("--only", action="append", default=[], metavar="ROW", help="run this row")
    parser.add_argument("--list", action="store_true", help="print each row, its CI job, command")
    parser.add_argument("--list-scans", action="store_true", help="print the tree-scans tests")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse(argv)
    if args.list:
        try:
            commands = ci_commands(workflows_dir())
        except CannotJudge as error:
            print(f"prepush: {error}", file=sys.stderr)
            return 3
        for name, key, _row in ROWS:
            print(f"{name}\t{CI_COMMANDS[key][0]}\t{' '.join(commands[key])}")
        for key, why in LEFT_TO_CI.items():
            print(f"(left to CI)\t{key}\t{why}")
        return 0
    if args.list_scans:
        print("\n".join(scan_tests()))
        return 0
    unknown = [name for name in args.only if name not in ROW_NAMES]
    if unknown:
        print(f"prepush: no row named {unknown[0]!r}; the rows are {', '.join(ROW_NAMES)}",
              file=sys.stderr)
        return 2

    root = Path.cwd()
    lines: list[str] = []

    def say(text: str) -> None:
        lines.append(text)
        print(text, flush=True)

    _, gitdir = git(root, "rev-parse", "--absolute-git-dir")
    log = Path(gitdir) / "prepush.log"

    def finish(rc: int, failed: list[str], text: str | None = None) -> int:
        if text:
            say(text)
        say(f"PREPUSH rc={rc} failed={'; '.join(failed) or 'none'} log={log}")
        log.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return rc

    env = os.environ
    branch = env.get("PRE_COMMIT_REMOTE_BRANCH", "").removeprefix("refs/heads/")
    to_ref = env.get("PRE_COMMIT_TO_REF", "")
    if args.hook and to_ref == ZEROS:
        return finish(0, [], "prepush-gate: NOT JUDGED (branch delete)")

    # A wip/ backup sends a snapshot commit that is not the checkout's HEAD (agent_wip_push
    # makes one), and its commit messages are what the rule reads: judge the commit sent.
    wip = args.hook and branch.startswith("wip/")
    subject = to_ref if wip and to_ref else "HEAD"
    _, head = git(root, "rev-parse", subject)
    rc, merge_base = git(root, "merge-base", BASE_REF, subject)
    if rc != 0:
        say(f"prepush-gate: cannot judge: no {BASE_REF} to measure the branch against. "
            f"Run `{FETCH_HINT}`, then push again.")
        return finish(3, ["origin/main"])

    body_file = args.pr_body_file or env.get("PRISM_PR_BODY_FILE") or None
    try:
        ci = ci_commands(workflows_dir())
    except CannotJudge as error:
        say(f"prepush-gate: cannot judge: {error}")
        return finish(3, ["workflows"])
    ctx = Context(root, head, merge_base, body_file, ci)
    selected = args.only or list(ROW_NAMES)
    blocking = True
    reason = ""
    if args.hook:
        if wip:
            selected = ["commit-messages"]
        elif branch != "main":
            count = open_pull_requests(root, branch)
            if count is None:
                reason = (f"could not look up an open pull request for {branch!r}; "
                          "treating the push as one that has a pull request")
                say(f"prepush-gate: {reason}")
            elif count == 0:
                blocking = False
                reason = f"no open pull request for {branch!r}"
    say(f"prepush-gate: judging {branch or 'HEAD'} at {head[:12]} against "
        f"{BASE_REF} ({merge_base[:12]})")

    passed, unjudged, failed = judged_rows(selected, ctx, say)
    if args.hook and to_ref and to_ref != head:
        failed.append("pushed-commit")
        say(f"    FAIL  pushed-commit  (this gate judges the checkout at {head[:12]}, "
            f"but the push sends {to_ref[:12]}; check that commit out, or push the branch "
            "you stand on)")

    if wip:
        if failed:
            return finish(1, failed, "PREPUSH FAIL (wip backup: the commit-message rule blocks)")
        return finish(0, [], "PREPUSH NOT JUDGED (wip backup): only the commit-message rule ran")
    if failed and not blocking:
        return finish(0, failed, "PREPUSH ADVISORY — NOT A PASS: these rows would block once "
                      f"a pull request is open ({reason})")
    if failed:
        return finish(1, failed, "PREPUSH FAIL: fix the rows above, then push again")
    if not blocking:
        return finish(0, [], f"PREPUSH PASS (advisory: {reason}); no review packet")
    if args.only:
        return finish(0, [], f"PREPUSH PASS (only {', '.join(args.only)}); no review packet")
    text = packet(head, merge_base, passed, unjudged)
    (Path(gitdir) / "prepush-packet.md").write_text(text, encoding="utf-8")
    say("PREPUSH PASS")
    say("REVIEW PACKET (for the PR body)")
    say(text)
    return finish(0, [])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
