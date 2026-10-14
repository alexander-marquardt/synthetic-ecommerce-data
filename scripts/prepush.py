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
``lint`` and ``file-size`` as the workflow runs them, and ``tree-scans``, the tests that
read every tracked file. ``tests/test_prepush_gate_11677.py`` proves each row's command is
one its named CI job runs. What stays with CI, by name: the whole suite (about 27
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

COMMIT_MESSAGES_COMMAND = "python3 scripts/check_commit_msg.py --range"
LINT_COMMAND = "uv run --locked ruff check ."
FILE_SIZE_COMMAND = "python3 scripts/file_size_gate.py --base"
SCANS_COMMAND = "uv run --locked pytest"


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
    rc, out = run(
        ["python3", "scripts/check_commit_msg.py", "--range", span],
        ctx.root,
    )
    judged = f"{count} commit message(s) in {span[:7]}..{ctx.head[:7]}"
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


def row_lint(ctx: Context) -> Result:
    rc, out = run(["uv", "run", "--locked", "ruff", "check", "."], ctx.root)
    return Result("PASS" if rc == 0 else "FAIL", f"ruff check . on {ctx.head[:7]}", out)


def row_file_size(ctx: Context) -> Result:
    argv = ["python3", "scripts/file_size_gate.py", "--base", BASE_REF]
    if ctx.body_file:
        rc, out = run([*argv, "--pr-body-file", ctx.body_file], ctx.root)
        judged = f"against {BASE_REF}, PR body {ctx.body_file}"
        return Result("PASS" if rc == 0 else "FAIL", judged, out)
    rc, out = run([*argv, "--no-body-is-advisory"], ctx.root)
    if rc == 4:
        # A file over the cap grew and a body line could clear it: only the PR body can say.
        note = (
            out + "file-size: a file over the cap grew; this run read no PR body, so it cannot "
            "say whether a File-Size-Exception line declares it. Re-run with "
            "--pr-body-file <draft body>.\n"
        )
        return Result("WARN", "NOT JUDGED: a growth needs the PR body (--pr-body-file)", note)
    judged = f"against {BASE_REF}, nothing grew past the cap"
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


def row_tree_scans(ctx: Context) -> Result:
    tests = scan_tests()
    rc, out = run(["uv", "run", "--locked", "pytest", "-p", "no:cacheprovider", *tests], ctx.root)
    found = re.search(r"(\d+) passed", out)
    passed = int(found.group(1)) if found else 0
    judged = f"{passed} passed in {' '.join(tests)}"
    if rc == 0 and passed == 0:
        out += "tree-scans: no test ran (all skipped or none collected), which judges nothing.\n"
        return Result("FAIL", judged, out)
    return Result("PASS" if rc == 0 else "FAIL", judged, out)


#: name, the CI job whose command it runs, that command, the row.
ROWS: tuple[tuple[str, str, str, Row], ...] = (
    ("commit-messages", "commit-messages", COMMIT_MESSAGES_COMMAND, row_commit_messages),
    ("lint", "tests", LINT_COMMAND, row_lint),
    ("file-size", "file-size", FILE_SIZE_COMMAND, row_file_size),
    ("tree-scans", "tests", SCANS_COMMAND, row_tree_scans),
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
    for name, _job, _command, row in ROWS:
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
            unjudged.append(f"{name}: {result.judged}")
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
        for name, job, command, _row in ROWS:
            print(f"{name}\t{job}\t{command}")
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
    ctx = Context(root, head, merge_base, body_file)
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
    if args.hook and not wip and to_ref and to_ref != head:
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
