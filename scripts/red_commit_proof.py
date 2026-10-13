"""CI proves each declared red commit is red on an assertion (elastic/prism#11680).

    python3 scripts/red_commit_proof.py --range <base>..<head>     # a pull request's commits
    python3 scripts/red_commit_proof.py --range origin/main..HEAD  # the same, before you push

A commit with a ``Red-Test: <test id> ...`` trailer claims those tests fail at
that commit, on an assertion: the red commit of the red-commit-first rule
(elastic/prism's "A test is proven by a red commit before its fix", lever
#10028). Without a check the claim is only prose, and a test that cannot fail
merges as coverage. For each such commit this checks the commit's tree out in a
throwaway worktree, runs ONLY the named tests there, and passes the commit when
every named test failed in its own call phase on an ``AssertionError`` (or
``pytest.fail``). It refuses, naming the id, a named test that:

* passes, so it is not red;
* fails on anything else: a collection or import error, a fixture or teardown
  error, another exception, a timeout;
* matches no test that ran (a typo, a skip, a missing file);

and a trailer token that is not a ``path.py::name`` test id (prose, a sha). A
parametrized case is named by its own id, ``tests/test_a.py::t[x, y]``.

A commit with no trailer, or ``Red-Test: none - <reason>`` (a refactor, a docs
change, the fix after its red commit), runs nothing: the proof costs a handful
of named tests per red commit, never the suite.

The verdict on each test is the one ``mutant_run.py`` gives a mutant, from the
same pytest plugin (``vendor/prism/scripts/mutant_run_plugin.py``, core's, byte
for byte): it also refuses an assertion raised in the code under test or in a
fixture, which is not the test noticing anything.

Exit: 0 every declared red commit is proven (or none is declared); 1 a refusal;
2 a usage error (an empty or unresolvable range); 3 a commit could not be judged
(pytest wrote no outcomes, or timed out) and none was refused.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDORED = REPO_ROOT / "vendor" / "prism" / "scripts"

sys.path.insert(0, str(VENDORED))
import mutant_run as runner  # noqa: E402  (the vendored path is set up just above)

#: How long one commit's named tests may run before the commit is "not judged".
TIMEOUT_SECS = 900
TEST_ID = re.compile(r"^[\w./-]+\.py::\S.*$")
NONE_VALUE = re.compile(r"^none(?![\w])", re.IGNORECASE)


def _tokens(value: str) -> list[str]:
    """Split on commas and blanks outside square brackets, so ``t[x, y]`` stays whole."""
    tokens, current, depth = [], "", 0
    for char in value:
        if char == "[":
            depth += 1
        elif char == "]":
            depth = max(0, depth - 1)
        if depth == 0 and (char.isspace() or char == ","):
            if current:
                tokens.append(current)
            current = ""
        else:
            current += char
    if current:
        tokens.append(current)
    return tokens


def declared_tests(values: Sequence[str]) -> list[str]:
    """The tokens of a commit's ``Red-Test:`` values; ``none ...`` values name nothing."""
    names: list[str] = []
    for value in values:
        if NONE_VALUE.match(value.strip()):
            continue
        names.extend(_tokens(value))
    return names


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args], capture_output=True, text=True, check=check
    )


def trailer_values(repo: Path, sha: str) -> list[str]:
    shown = _git(repo, "show", "-s", "--format=%(trailers:key=Red-Test,valueonly,unfold)", sha)
    return [line for line in shown.stdout.splitlines() if line.strip()]


def _events(report: Path) -> list[dict[str, str]]:
    if not report.exists():
        return []
    events = []
    for line in report.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def run_named(
    tree: Path, ids: list[str], scratch: Path
) -> tuple[int | None, list[dict[str, str]], str]:
    """Run only ``ids`` in ``tree``: (pytest's status or None on a timeout, outcomes, output)."""
    shutil.copyfile(runner.PLUGIN_SOURCE, scratch / f"{runner.PLUGIN_MODULE}.py")
    report = scratch / "outcomes.jsonl"
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env[runner.REPORT_ENV] = str(report)
    # The tree's own packages first: the editable install points at the checkout
    # that started this script, not at the commit being judged.
    path = [str(scratch)]
    if (tree / "src").is_dir():
        path.append(str(tree / "src"))
    env["PYTHONPATH"] = os.pathsep.join(filter(None, [*path, env.get("PYTHONPATH", "")]))
    try:
        done = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-p",
                "no:cacheprovider",
                "-p",
                runner.PLUGIN_MODULE,
                *ids,
            ],
            cwd=tree,
            env=env,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECS,
        )
    except subprocess.TimeoutExpired:
        return None, _events(report), ""
    return done.returncode, _events(report), done.stdout + done.stderr


def refusals(ids: list[str], events: list[dict[str, str]]) -> list[str]:
    """One ``<id>: <why>`` per named test that is not red on an assertion."""
    problems = []
    for name in ids:
        mine = [event for event in events if event["nodeid"] == name]
        if any(event["outcome"] == "error" for event in mine):
            detail = next(e["detail"] for e in mine if e["outcome"] == "error")
            problems.append(f"{name}: fails, but not on an assertion ({detail})")
        elif any(event["outcome"] == "passed" for event in mine):
            problems.append(f"{name}: passes, so it is not red at this commit")
        elif not any(event["outcome"] == "assertion" for event in mine):
            problems.append(f"{name}: matches no test that ran (a typo, a skip, a missing file)")
    named = set(ids)
    for event in events:
        if event["outcome"] == "error" and event["nodeid"] not in named:
            problems.append(f"{event['nodeid']}: {event['detail']}, outside the named tests")
    return problems


def judge_commit(repo: Path, sha: str, ids: list[str]) -> tuple[str, list[str]]:
    """``("proven" | "refused" | "not-judged", lines)`` for one declared red commit."""
    prose = [name for name in ids if not TEST_ID.match(name)]
    if not ids or prose:
        shown = ", ".join(prose) or "no test id"
        return "refused", [
            f"the Red-Test trailer must name tests as path.py::name; it names {shown}"
        ]
    scratch = Path(tempfile.mkdtemp(prefix="red-proof-"))
    tree = scratch / "tree"
    try:
        _git(repo, "worktree", "add", "--detach", str(tree), sha)
        status, events, output = run_named(tree, ids, scratch)
    finally:
        _git(repo, "worktree", "remove", "--force", str(scratch / "tree"), check=False)
        shutil.rmtree(scratch, ignore_errors=True)
    if status is None:
        return "not-judged", [f"pytest ran longer than {TIMEOUT_SECS} s"]
    if not events and status == 4 and "not found" in output:
        # pytest's usage error for an id that selects nothing: the trailer's typo.
        missing = [
            line.strip().replace(f"{tree}/", "")
            for line in output.splitlines()
            if "not found" in line
        ]
        return "refused", [f"{line} (matches no test)" for line in missing]
    if not events:
        return "not-judged", [f"pytest exited {status} and wrote no outcomes"]
    problems = refusals(ids, events)
    return ("refused", problems) if problems else ("proven", [])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--range", required=True, dest="spec", help="<base>..<head>")
    parser.add_argument("--repo", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)
    listed = _git(args.repo, "rev-list", "--reverse", "--no-merges", args.spec, check=False)
    shas = listed.stdout.split()
    if listed.returncode != 0 or not shas:
        print(
            f"red_commit_proof: {args.spec!r} resolves to no commits; nothing was checked",
            file=sys.stderr,
        )
        return 2
    refused = unjudged = declared = 0
    for sha in shas:
        values = trailer_values(args.repo, sha)
        ids = declared_tests(values)
        if not values or (not ids and all(NONE_VALUE.match(v.strip()) for v in values)):
            continue
        declared += 1
        verdict, lines = judge_commit(args.repo, sha, ids)
        label = sha[:9]
        if verdict == "proven":
            print(f"PROVEN   {label}: red on an assertion: {', '.join(ids)}")
        elif verdict == "refused":
            refused += 1
            print(f"REFUSED  {label}")
            for line in lines:
                print(f"    {line}")
        else:
            unjudged += 1
            print(f"NOT JUDGED  {label}: {lines[0]}")
    print(f"red-commit proof: {len(shas)} commit(s), {declared} declare a red test")
    return 1 if refused else 3 if unjudged else 0


if __name__ == "__main__":
    sys.exit(main())
