#!/usr/bin/env python3
"""Run a list of mutants one at a time against the tests named to kill each (#10512).

Every agent with a mutant step used to write its own runner, and hand-written
runners fail silently: in #10421 a pattern matched two places, so one mutant
never ran and nobody saw it. This is the one runner, and its input file is the
receipt a reviewer re-runs (#10111), so "N of M killed" is checked, not trusted.

    uv run python scripts/mutant_run.py <mutants file> [--root DIR] [--only NAME]...
        [--tests-only NODE...]
    uv run python scripts/mutant_run.py <mutants file> --check   # validate, run nothing

Under the host-wide heavy lock, with a cap that fits the whole run::

    cd <clone> && agent_heavy "mutants <label>" --max-secs 1800 -- uv run --directory <clone> python <clone>/scripts/mutant_run.py <file>

Run it from the clone: the root defaults to the cwd (#11446).

The mutants file
----------------
A Python file, usually ``tests/review_<N>_mutants.py.txt``, that is READ, never
executed. Three module-level assignments matter; every other statement is
ignored, so an old hand-written runner converts by reshaping its list::

    TESTS = ["tests/test_x.py"]          # node ids for a mutant that names none
    BASELINE_RED = ["tests/test_p.py::test_pin"]   # optional; red by design, deselected
    PYTEST_ARGS = ["--noconftest"]       # optional; default: -q -p no:cacheprovider
    MUTANTS = [
        (path, old, new, name),                       # killed by TESTS
        (path, old, new, name, ["tests/test_x.py::test_y"]),
    ]

``--only NAME`` runs just that row (its own baseline, then the mutant: two pytest
runs for a one-row change). ``--tests-only NODE...`` replaces every row's tests for
this run, so "survives the PR's suites, killed by the review pins" is one file and
two invocations, not a scratch copy. ``BASELINE_RED`` names node ids that fail with
no mutant on purpose (a review plant pinning a fix not made yet): every run, the
baseline included, deselects them and the run prints an ``EXCLUDED`` line for each,
so the baseline stops the run only for a test that should be green. List a plant
there only when it is red by design; a green one named there is silently not run.

A search-ui (Studio) mutant names vitest files instead (#11541)::

    TESTS = ["search-ui/src/components/Widget.test.tsx"]
    MUTANTS = [("search-ui/src/components/Widget.tsx", old, new, name)]

A row whose tests are all ``search-ui/**/*.test.ts(x)`` runs
``search-ui/node_modules/.bin/vitest run --maxWorkers=2 <files>`` from
``search-ui/``, the clone's own vitest and never one ``npx`` finds elsewhere,
in its own process group, so a timeout stops its workers too. It runs ``npm ci``
there first when ``node_modules`` is missing, and stops before any mutant when
``node_modules`` is there without an executable ``.bin/vitest``. It is judged
from vitest's JSON report under the same verdicts. A vitest test is a whole file: a row that names one with ``::``,
mixes vitest files and pytest node ids, or lists one in ``BASELINE_RED`` is a
usage error; ``PYTEST_ARGS`` does not apply to it.

``path`` is relative to ``--root`` (default: the current directory, which must
be a git checkout). Values are literals; a name bound earlier to a literal
(``ARM = "scripts/arm_pr.py"``) and ``+`` between strings or lists are allowed.

What it guarantees
------------------
* A mutant whose ``old`` occurs zero times, or more than once, in its file is
  REFUSED, never applied: that silent no-op is the measured failure. Overlapping
  occurrences count (``aa`` occurs twice in ``aaa``).
* One mutant at a time; its tests run with ``PYTHONDONTWRITEBYTECODE=1``, so no
  bytecode of a mutant is cached for a later run to import.
* The file is restored in a ``finally`` (bytes and mtime) and compared byte for
  byte with the original. A mismatch stops the run and names the file.
* Before a mutant is written, the original and a hash of the mutant are journaled
  under the checkout's git directory. SIGTERM, SIGINT and SIGHUP stop the run
  after the restore; a run that was killed outright (SIGKILL, OOM) leaves the
  journal. The next run restores the file from it only while the file still
  holds that mutant, then says so and stops; a file someone has edited since is
  never overwritten: the run names it, keeps the journal and stops.
  ``agent_heavy`` SIGTERMs at ``--max-secs``, and a mutant was once left on
  disk and committed that way; ``agent_commit`` refuses while the journal exists.
* One run per checkout: a second run while one holds the lock stops at once.
* It never commits. The tracked tree (HEAD, and the status, bytes and staged
  blob of every tracked file that differs from HEAD) is read before the run and
  after every test run; any change stops the run and names the paths.
* Each mutant's own test set first runs with no mutant applied. A baseline that
  does not pass stops the run, since every mutant would read as KILLED against
  it; a set run alone, as its mutant runs it, can fail where the same tests pass
  in a larger session.

Verdicts, one line per mutant, then ``N of M killed``:

* ``KILLED``   a test failed on an assertion (``AssertionError`` or ``pytest.fail``)
  that the test itself raised, in the test body or in a helper it calls from a
  ``test_*.py`` module (#10670), not a fixture, a hook, a guard or the code under
  test (``mutant_run_plugin.py`` says how that is judged). For vitest: an
  ``AssertionError`` (``expect``, ``assert``) or a Testing Library
  ``TestingLibraryElementError`` whose first stack frame outside
  ``node_modules`` is in a ``*.test.ts(x)`` file; a file that failed to load is
  ``NOT-TESTED``.
* ``SURVIVED`` every test passed.
* ``ERROR``    no assertion failed, and something else did: a test raised another
  exception, or the run timed out. A crash is not a detection; a mutant that
  only breaks its tests' input is replaced by one that narrows
  (contributing/testing-discipline.md, the per-mutation record).
* ``NOT-TESTED`` no test ran to judge the mutant: a test module failed to
  collect or import, every test skipped, or pytest stopped first (#10961). A
  pytest exit status of 1 or 2 there is not a kill. With no mutant applied it
  is ``BASELINE NOT-TESTED`` and nothing is mutated.
* ``REFUSED``  the mutant was never applied (see above).

Exit status: 0 when every mutant was KILLED or SURVIVED; 1 when any was REFUSED,
ERROR or NOT-TESTED, or the baseline failed; 2 for a mutants file that cannot be read or a
usage error; 3 when a file could not be restored, the tracked tree changed, a
killed run's journal was found, or another run holds the checkout; 128+N when
stopped by signal N (after the restore).
"""

from __future__ import annotations

import argparse
import ast
import base64
import fcntl
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from types import FrameType

from bounded_process import _end_watcher, _start_watcher, stop_group

PLUGIN_SOURCE = Path(__file__).resolve().parent / "mutant_run_plugin.py"
PLUGIN_MODULE = "prism_mutant_run_plugin"
REPORT_ENV = "PRISM_MUTANT_RUN_REPORT"
#: The ``detail`` the plugin records for a module that failed to collect or
#: import. The plugin runs as a copy outside the tree, so it spells it itself.
COLLECTION = "collection failed"
DEFAULT_PYTEST_ARGS = ("-q", "-p", "no:cacheprovider")
JOURNAL_NAME = "prism-mutant-run-journal.json"
LOCK_NAME = "prism-mutant-run.lock"
STOP_SIGNALS = (signal.SIGTERM, signal.SIGINT, signal.SIGHUP)
DEFAULT_TIMEOUT_SECS = 600
#: How many lines of a broken run's output are shown under its verdict.
TAIL_LINES = 8
#: The front end whose vitest files a mutant may name (#11541). A test there is a
#: whole file, run from this directory: vitest addresses no test by ``::``.
VITEST_DIR = "search-ui"
VITEST_SUFFIXES = (".test.ts", ".test.tsx")
VITEST_ARGS = ("--maxWorkers=2",)
#: A failure a vitest test file raised that is a detection, not a crash: an
#: ``expect``, ``assert`` or ``expect.fail``, and a Testing Library ``getBy*``
#: that found no element (a query that asserts presence by design).
VITEST_ASSERTIONS = ("AssertionError", "TestingLibraryElementError")
#: A stack frame's file: ``at fn (/abs/x.ts:4:10)`` or ``at /abs/x.ts:4:10``.
_FRAME_RE = re.compile(
    r"^\s*at (?:.*? \()?(?:file://)?(?P<path>/[^\s()]+?):\d+:\d+\)?\s*$"
)

EXIT_OK = 0
EXIT_FINDINGS = 1
EXIT_USAGE = 2
EXIT_TREE = 3


class FormatError(Exception):
    """The mutants file cannot be read as a mutant list."""


class TreeError(Exception):
    """The checkout is not in the state the run left it in: a hard stop."""


@dataclass(frozen=True)
class Mutant:
    path: str
    old: str
    new: str
    name: str
    tests: tuple[str, ...]


@dataclass(frozen=True)
class MutantFile:
    mutants: tuple[Mutant, ...]
    pytest_args: tuple[str, ...]
    baseline_red: tuple[str, ...] = ()
    tests_only: tuple[str, ...] = ()


@dataclass(frozen=True)
class Outcome:
    verdict: str
    detail: str
    tail: tuple[str, ...] = ()


# --------------------------------------------------------------------------- input


def _literal(node: ast.expr, names: dict[str, object]) -> object:
    if isinstance(node, ast.Constant) and isinstance(node.value, str | int):
        return node.value
    if isinstance(node, ast.Tuple | ast.List):
        items = [_literal(element, names) for element in node.elts]
        return tuple(items) if isinstance(node, ast.Tuple) else items
    if isinstance(node, ast.Name) and node.id in names:
        return names[node.id]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left, right = _literal(node.left, names), _literal(node.right, names)
        if isinstance(left, str) and isinstance(right, str):
            return left + right
        if isinstance(left, list | tuple) and isinstance(right, list | tuple):
            return [*left, *right]
    raise FormatError(
        f"line {node.lineno}: not a literal the runner reads ({ast.unparse(node)[:60]})"
    )


def _assignments(source: str, filename: str) -> dict[str, object]:
    try:
        tree = ast.parse(source, filename=filename)
    except SyntaxError as error:
        raise FormatError(f"line {error.lineno}: {error.msg}") from error
    names: dict[str, object] = {}
    for statement in tree.body:
        if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
            target, value = statement.targets[0], statement.value
        elif isinstance(statement, ast.AnnAssign) and statement.value is not None:
            target, value = statement.target, statement.value
        else:
            continue
        if not isinstance(target, ast.Name):
            continue
        try:
            names[target.id] = _literal(value, names)
        except FormatError:
            if target.id in ("MUTANTS", "TESTS", "PYTEST_ARGS"):
                raise
    return names


def _strings(value: object, what: str) -> tuple[str, ...]:
    if not isinstance(value, list | tuple) or not all(
        isinstance(item, str) for item in value
    ):
        raise FormatError(f"{what} must be a list of strings")
    return tuple(value)


def is_vitest(test: str) -> bool:
    """Whether ``test`` names a search-ui vitest file (``::`` and all), not a pytest node."""
    path = test.partition("::")[0]
    return path.startswith(f"{VITEST_DIR}/") and path.endswith(VITEST_SUFFIXES)


def _runner_problem(tests: Sequence[str]) -> str | None:
    """Why one runner cannot run ``tests`` as written, or None."""
    vitest = [test for test in tests if is_vitest(test)]
    if not vitest:
        return None
    if len(vitest) != len(tests):
        return "names vitest files and pytest node ids together: one runner per mutant"
    if any("::" in test for test in vitest):
        return "names a test inside a vitest file: name the file, vitest runs it whole"
    return None


def load_mutants(path: Path, tests_only: Sequence[str] = ()) -> MutantFile:
    """Read the mutant list from ``path`` without executing it.

    ``tests_only`` replaces every mutant's tests, the file's ``TESTS`` and a row's
    own list alike.
    """
    names = _assignments(path.read_text(encoding="utf-8"), str(path))
    if "MUTANTS" not in names:
        raise FormatError("no MUTANTS = [...] assignment")
    default_tests = _strings(names["TESTS"], "TESTS") if "TESTS" in names else ()
    baseline_red = _strings(names.get("BASELINE_RED", ()), "BASELINE_RED")
    pytest_args = _strings(names.get("PYTEST_ARGS", DEFAULT_PYTEST_ARGS), "PYTEST_ARGS")
    entries = names["MUTANTS"]
    if not isinstance(entries, list | tuple) or not entries:
        raise FormatError("MUTANTS must be a non-empty list")
    mutants: list[Mutant] = []
    for index, entry in enumerate(entries):
        where = f"MUTANTS[{index}]"
        if not isinstance(entry, list | tuple) or len(entry) not in (4, 5):
            raise FormatError(
                f"{where} must be (path, old, new, name) or (path, old, new, name, tests)"
            )
        fields = entry[:4]
        if not all(isinstance(field, str) for field in fields):
            raise FormatError(f"{where}: path, old, new and name must be strings")
        file_path, old, new, name = (str(field) for field in fields)
        tests = (
            tuple(tests_only)
            if tests_only
            else _strings(entry[4], f"{where} tests")
            if len(entry) == 5
            else default_tests
        )
        if not tests:
            raise FormatError(
                f"{where} ({name}) names no tests, and there is no TESTS default"
            )
        if problem := _runner_problem(tests):
            raise FormatError(f"{where} ({name}) {problem}")
        if not old:
            raise FormatError(f"{where} ({name}): old is empty")
        mutants.append(Mutant(file_path, old, new, name, tests))
    if any(is_vitest(node) for node in baseline_red):
        raise FormatError(
            "BASELINE_RED names a vitest file: vitest deselects no file, so a "
            "red-by-design vitest test cannot be excluded"
        )
    seen: set[str] = set()
    for mutant in mutants:
        if mutant.name in seen:
            raise FormatError(f"two mutants are named {mutant.name!r}")
        seen.add(mutant.name)
    return MutantFile(tuple(mutants), pytest_args, baseline_red, tuple(tests_only))


# ---------------------------------------------------------------------- the checkout


def _git_raw(root: Path, *args: str) -> str:
    done = subprocess.run(  # noqa: S603  # argv is "git", the checkout path and literal subcommands; no shell
        ["git", "-C", str(root), *args],  # noqa: S607  # "git" on PATH runs "rev-parse" and "status" here, which only read
        capture_output=True,
        text=True,
        check=False,
    )
    return done.stdout if done.returncode == 0 else ""


def _git(root: Path, *args: str) -> str:
    return _git_raw(root, *args).strip()


def resolve_target(root: Path, mutant: Mutant) -> Path:
    target = (root / mutant.path).resolve()
    if not target.is_relative_to(root):
        raise FormatError(f"{mutant.path} is outside {root}")
    return target


def refusal(root: Path, mutant: Mutant) -> str | None:
    """Why ``mutant`` cannot be applied, or None when its ``old`` occurs exactly once."""
    try:
        target = resolve_target(root, mutant)
    except FormatError as error:
        return str(error)
    if not target.is_file():
        return f"{mutant.path} is not a file"
    if mutant.old == mutant.new:
        return "new is the same as old, so the mutant changes nothing"
    count = occurrences(target.read_bytes(), mutant.old.encode("utf-8"))
    if count != 1:
        return f"old occurs {count} times in {mutant.path}, not exactly once"
    return None


def occurrences(data: bytes, pattern: bytes) -> int:
    """How many offsets ``pattern`` starts at, overlaps included.

    ``bytes.count`` skips past each match, so ``aa`` counts once in ``aaa``
    though it sits at two offsets and the mutant's target is a guess.
    """
    count, start = 0, data.find(pattern)
    while start != -1:
        count += 1
        start = data.find(pattern, start + 1)
    return count


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _git_dir(root: Path) -> Path:
    git_dir = _git(root, "rev-parse", "--absolute-git-dir")
    if not git_dir:
        raise FormatError(f"{root} is not a git checkout")
    return Path(git_dir)


class Journal:
    """The original bytes of the one file a mutant is on, and a hash of the
    mutant, kept where a killed run's successor finds them: the checkout's git
    directory, which no tree scan walks and no commit includes."""

    def __init__(self, root: Path) -> None:
        self.path = _git_dir(root) / JOURNAL_NAME

    def write(
        self, target: Path, original: bytes, mutated: bytes, mtime_ns: int, name: str
    ) -> None:
        record = {
            "path": str(target),
            "name": name,
            "mtime_ns": mtime_ns,
            "original": base64.b64encode(original).decode("ascii"),
            "mutant_sha256": _digest(mutated),
        }
        scratch = self.path.with_suffix(".tmp")
        scratch.write_text(json.dumps(record), encoding="utf-8")
        os.replace(scratch, self.path)

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)

    def recover(self) -> str | None:
        """Undo what a killed run left; describe a restore, or None.

        The journaled original is written back only while the file still holds
        the mutant. A file that already holds the original (a kill between the
        restore and the clear) only needs the journal cleared. Anything else
        is an edit made since the kill, and writing the stale original over it
        would lose that work, so it is a TreeError and nothing is written.
        """
        if not self.path.exists():
            return None
        record = json.loads(self.path.read_text(encoding="utf-8"))
        target = Path(record["path"])
        original = base64.b64decode(record["original"])
        try:
            current: str | None = _digest(target.read_bytes())
        except OSError:
            current = None
        if current == _digest(original):
            self.clear()
            return None
        if current != record["mutant_sha256"]:
            raise TreeError(
                f"{target} holds neither mutant {record['name']!r} nor its original: "
                f"it was edited after a run was killed, so it was left as it is. "
                f"The journal {self.path} holds its original bytes (base64, key "
                f"'original'): write them beside the file to inspect them with "
                f'python3 -c "import base64,json,sys; sys.stdout.buffer.write('
                f"base64.b64decode(json.load(open(sys.argv[1]))['original']))\" "
                f"{self.path} > {target}.orig"
            )
        restore(target, original, int(record["mtime_ns"]))
        self.clear()
        return f"{target} (mutant {record['name']!r})"


def restore(target: Path, original: bytes, mtime_ns: int) -> None:
    target.write_bytes(original)
    os.utime(target, ns=(mtime_ns, mtime_ns))
    if target.read_bytes() != original:
        raise TreeError(
            f"{target} is not byte-identical to its original after the restore"
        )


@dataclass(frozen=True)
class TreeState:
    """What a test run must leave as it found it: HEAD, and for every tracked
    file that differs from HEAD, its status, its bytes and its staged blob.

    A clean tracked file is not listed; one a test writes or stages appears in
    the status, so it is caught without hashing the whole tree. The staged blob
    catches a test that restages a file whose status and bytes end as they were.
    """

    head: str
    changed: tuple[tuple[str, str], ...]

    def differences(self, after: TreeState) -> list[str]:
        named = []
        if after.head != self.head:
            named.append(f"HEAD ({self.head or '<no commit>'} -> {after.head})")
        before, now = dict(self.changed), dict(after.changed)
        named.extend(
            path
            for path in sorted(before.keys() | now.keys())
            if before.get(path) != now.get(path)
        )
        return named


def tree_state(root: Path) -> TreeState:
    # --no-optional-locks: reading the status must not rewrite the index stat cache.
    status = _git_raw(
        root,
        "--no-optional-locks",
        "status",
        "--porcelain=v1",
        "-z",
        "--untracked-files=no",
    )
    tokens = iter(status.split("\0"))
    changed: dict[str, str] = {}
    for token in tokens:
        if len(token) < 4:
            continue
        code, path = token[:2], token[3:]
        if code[0] in "RC":
            next(tokens, None)  # a rename's source path follows it
        try:
            content = _digest((root / path).read_bytes())
        except OSError:
            content = "<unreadable>"
        staged = _git(root, "rev-parse", "-q", "--verify", f":{path}")
        changed[path] = f"{code} disk={content} staged={staged or '<none>'}"
    return TreeState(
        head=_git(root, "rev-parse", "-q", "--verify", "HEAD"),
        changed=tuple(sorted(changed.items())),
    )


class CheckoutLock:
    """One run per checkout: a second run would read the first's journal as a
    killed run's and restore the live mutant under it."""

    def __init__(self, root: Path) -> None:
        self.path = _git_dir(root) / LOCK_NAME
        self._handle: int | None = None

    def acquire(self) -> bool:
        handle = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            os.close(handle)
            return False
        self._handle = handle
        return True

    def release(self) -> None:
        if self._handle is not None:
            os.close(self._handle)
            self._handle = None


# --------------------------------------------------------------------------- running


class Runner:
    def __init__(
        self, root: Path, spec: MutantFile, timeout_secs: int, scratch: Path
    ) -> None:
        self.root = root
        self.spec = spec
        self.timeout_secs = timeout_secs
        self.scratch = scratch
        self.stop_signal: int | None = None
        self.journal = Journal(root)
        shutil.copyfile(PLUGIN_SOURCE, scratch / f"{PLUGIN_MODULE}.py")

    def on_signal(self, signum: int, _frame: FrameType | None) -> None:
        # Only a flag: raising here could land inside the restore. The loops
        # below look at it between every step and stop the test run.
        self.stop_signal = signum

    def run_tests(
        self, tests: Sequence[str], label: str, *, deselect: bool = True
    ) -> Outcome:
        if is_vitest(tests[0]):
            return self._run_vitest(tests, label)
        report = self.scratch / f"{label}.jsonl"
        log = self.scratch / f"{label}.log"
        report.unlink(missing_ok=True)
        env = dict(os.environ)
        env["PYTHONDONTWRITEBYTECODE"] = "1"
        env[REPORT_ENV] = str(report)
        env["PYTHONPATH"] = os.pathsep.join(
            filter(None, [str(self.scratch), env.get("PYTHONPATH", "")])
        )
        command = [
            sys.executable,
            "-m",
            "pytest",
            *self.spec.pytest_args,
            "-p",
            PLUGIN_MODULE,
            *(
                f"--deselect={node}"
                for node in (self.spec.baseline_red if deselect else ())
            ),
            *tests,
        ]
        done = self._wait(command, self.root, env, log)
        if not isinstance(done, int):
            return done
        return classify(done, _read_report(report), _tail(log))

    def _run_vitest(self, tests: Sequence[str], label: str) -> Outcome:
        report = self.scratch / f"{label}.json"
        log = self.scratch / f"{label}.log"
        report.unlink(missing_ok=True)
        command = [
            str(self.vitest),  # search-ui's own, never one npx resolves elsewhere
            "run",
            "--reporter=default",
            "--reporter=json",
            f"--outputFile.json={report}",
            *VITEST_ARGS,
            *(test.removeprefix(f"{VITEST_DIR}/") for test in tests),
        ]
        done = self._wait(command, self.root / VITEST_DIR, dict(os.environ), log)
        if not isinstance(done, int):
            return done
        return classify(done, vitest_events(report, self.root), _tail(log), "vitest")

    @property
    def vitest(self) -> Path:
        """search-ui's own vitest: the version its lock file pins, and no other."""
        return self.root / VITEST_DIR / "node_modules" / ".bin" / "vitest"

    def prepare_vitest(self) -> str | None:
        """Make search-ui runnable: why it is not, or None.

        ``npm ci`` runs first when ``node_modules`` is missing (a clone made
        without the npm dependencies), under the same cap and signals as a test
        run. That is a choice, kept over refusing as ``agent_prepush`` does: a
        mutant run is long and unattended, and ``npm ci`` is the whole install
        vitest needs, because vitest's ``globalSetup`` (``search-ui/vite.config.ts``)
        renders ``src/generated`` before any test file loads (#10837). A
        ``node_modules`` that is there without ``.bin/vitest`` (an interrupted
        install) is not reinstalled: the run stops and says so.
        """
        ui = self.root / VITEST_DIR
        if (ui / "node_modules").is_dir():
            return self._vitest_problem()
        if shutil.which("npm") is None:
            return f"{ui} has no node_modules and npm is not on PATH to install it"
        _print(f"NPM CI   {ui} has no node_modules: running npm ci there first")
        log = self.scratch / "npm-ci.log"
        done = self._wait(
            [shutil.which("npm") or "npm", "ci", "--no-audit", "--no-fund"],
            ui,
            dict(os.environ),
            log,
        )
        if isinstance(done, Outcome):
            return f"npm ci in {ui}: {done.detail}"
        if done != 0:
            return f"npm ci in {ui} exited {done}: " + " / ".join(_tail(log)[-3:])
        return self._vitest_problem()

    def _vitest_problem(self) -> str | None:
        if os.access(self.vitest, os.X_OK):
            return None
        return (
            f"{self.vitest} is missing or not executable (a partial install?); "
            f'reinstall with: agent_heavy "npm ci" -- npm ci --prefix {self.vitest.parents[2]}'
        )

    def _wait(
        self, command: list[str], cwd: Path, env: dict[str, str], log: Path
    ) -> int | Outcome:
        """Run ``command`` to its end: its exit status, or why it was stopped."""
        timed_out = False
        with log.open("wb") as output:
            # Its own process group, so a timeout or a signal stops the whole
            # run (vitest's fork workers sit below its first process) and not
            # only the direct child. The watcher stops that group if this
            # runner dies first, a SIGKILL from agent_heavy included (#11598).
            child = subprocess.Popen(  # noqa: S603  # command is the pytest, search-ui vitest or "npm" ci argv the Runner built, with tests from the operator's own mutants file; no shell
                command,
                cwd=cwd,
                env=env,
                stdout=output,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            watcher = _start_watcher(child.pid)
            try:
                deadline = time.monotonic() + self.timeout_secs
                while child.poll() is None:
                    if self.stop_signal is not None:
                        break
                    if time.monotonic() > deadline:
                        timed_out = True
                        break
                    time.sleep(0.1)
            finally:
                stop_group(child)
                _end_watcher(watcher)
        if self.stop_signal is not None:
            return Outcome("STOPPED", f"signal {self.stop_signal}")
        if timed_out:
            return Outcome("ERROR", f"timed out after {self.timeout_secs}s", _tail(log))
        return child.returncode

    def run_mutant(self, mutant: Mutant, index: int) -> Outcome:
        why = refusal(self.root, mutant)
        if why is not None:
            return Outcome("REFUSED", why)
        target = resolve_target(self.root, mutant)
        original = target.read_bytes()
        mtime_ns = target.stat().st_mtime_ns
        mutated = original.replace(
            mutant.old.encode("utf-8"), mutant.new.encode("utf-8"), 1
        )
        self.journal.write(target, original, mutated, mtime_ns, mutant.name)
        try:
            target.write_bytes(mutated)
            if self.stop_signal is not None:
                return Outcome("STOPPED", f"signal {self.stop_signal}")
            return self.run_tests(mutant.tests, f"mutant-{index}")
        finally:
            restore(target, original, mtime_ns)
            self.journal.clear()


def _tail(log: Path) -> tuple[str, ...]:
    text = log.read_text(encoding="utf-8", errors="replace")
    return tuple(text.splitlines()[-TAIL_LINES:])


def _relative(path: str, root: Path) -> str:
    try:
        return Path(path).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path


def _vitest_failure(messages: Sequence[str], root: Path) -> tuple[str, str]:
    """``(outcome, detail)`` for one failed vitest test, from its first error.

    It is an ``assertion`` only when the error is one of
    :data:`VITEST_ASSERTIONS` and the first stack frame outside
    ``node_modules`` is in a test file: the same assert raised in the code under
    test did not notice the mutant from the test's side.
    """
    text = messages[0] if messages else ""
    head = text.splitlines()[0] if text else "failed with no error message"
    if not head.startswith(VITEST_ASSERTIONS):
        return "error", head
    frames = (_FRAME_RE.match(line) for line in text.splitlines()[1:])
    where = next(
        (
            frame["path"]
            for frame in frames
            if frame and "/node_modules/" not in frame["path"]
        ),
        None,
    )
    if where is None:
        return "error", f"{head}, with no stack frame outside node_modules"
    if not where.endswith(VITEST_SUFFIXES):
        return (
            "error",
            f"{head}, raised in {_relative(where, root)}, not in a test file",
        )
    return "assertion", head


def vitest_events(report: Path, root: Path) -> list[dict[str, str]]:
    """The events :func:`classify` reads, from vitest's JSON report (#11541).

    A test file that failed with no test in it did not load: a ``collection
    failed`` error. One that failed with every test green failed in a hook.
    """
    try:
        data = json.loads(report.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    events = []
    for suite in data.get("testResults", []):
        file = _relative(suite.get("name", ""), root)
        cases = suite.get("assertionResults", [])
        for case in cases:
            nodeid = f"{file}::" + " > ".join(
                [*case.get("ancestorTitles", []), case.get("title", "")]
            )
            if case.get("status") == "passed":
                events.append({"outcome": "passed", "nodeid": nodeid, "detail": ""})
            elif case.get("status") == "failed":
                outcome, detail = _vitest_failure(case.get("failureMessages", []), root)
                events.append({"outcome": outcome, "nodeid": nodeid, "detail": detail})
        if suite.get("status") == "failed" and not any(
            case.get("status") == "failed" for case in cases
        ):
            message = (suite.get("message") or "").splitlines()
            detail = message[0] if cases and message else COLLECTION
            events.append({"outcome": "error", "nodeid": file, "detail": detail})
    return events


def _read_report(report: Path) -> list[dict[str, str]]:
    if not report.exists():
        return []
    events = []
    for line in report.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def classify(
    returncode: int,
    events: list[dict[str, str]],
    tail: tuple[str, ...] = (),
    tool: str = "pytest",
) -> Outcome:
    """The verdict on one test run, from what the plugin (or vitest's JSON
    report) recorded and the ``tool``'s exit status."""
    assertions = sorted(
        {event["nodeid"] for event in events if event["outcome"] == "assertion"}
    )
    errors = [event for event in events if event["outcome"] == "error"]
    passed = sum(1 for event in events if event["outcome"] == "passed")
    if assertions:
        shown = ", ".join(assertions[:3]) + (
            f" and {len(assertions) - 3} more" if len(assertions) > 3 else ""
        )
        return Outcome("KILLED", f"failed on an assertion: {shown}")
    if returncode == 0 and passed and not errors:
        return Outcome("SURVIVED", f"{passed} passed")
    # Nothing below ran a test that could have judged the mutant (#10961).
    uncollected = [event["nodeid"] for event in errors if event["detail"] == COLLECTION]
    if uncollected:
        more = f" (+{len(uncollected) - 1} more)" if len(uncollected) > 1 else ""
        return Outcome(
            "NOT-TESTED",
            f"{uncollected[0]}: {COLLECTION}{more}, so no test judged the mutant",
            tail,
        )
    if errors:
        first = errors[0]
        more = f" (+{len(errors) - 1} more)" if len(errors) > 1 else ""
        return Outcome(
            "ERROR",
            f"{first['nodeid']}: {first['detail']}{more}, no assertion failed",
            tail,
        )
    if passed:
        return Outcome(
            "ERROR", f"{tool} exited {returncode} and no assertion failed", tail
        )
    if returncode == 0:
        return Outcome(
            "NOT-TESTED", "no test passed, so nothing judged the mutant", tail
        )
    return Outcome("NOT-TESTED", f"{tool} exited {returncode} and ran no test", tail)


def _print(line: str) -> None:
    print(line, flush=True)


def _print_outcome(name: str, outcome: Outcome) -> None:
    _print(f"{outcome.verdict:<8} {name}: {outcome.detail}")
    for line in outcome.tail:
        _print(f"    | {line}")


def check(root: Path, spec: MutantFile, only: Sequence[str]) -> int:
    refused = 0
    for mutant in _selected(spec, only):
        why = refusal(root, mutant)
        refused += why is not None
        _print(
            f"{'REFUSED' if why else 'OK':<8} {mutant.name}"
            + (f": {why}" if why else "")
        )
    return EXIT_FINDINGS if refused else EXIT_OK


def _selected(spec: MutantFile, only: Sequence[str]) -> list[Mutant]:
    if not only:
        return list(spec.mutants)
    known = {mutant.name for mutant in spec.mutants}
    unknown = [name for name in only if name not in known]
    if unknown:
        raise FormatError(f"--only names no mutant: {', '.join(unknown)}")
    return [mutant for mutant in spec.mutants if mutant.name in only]


def run(root: Path, spec: MutantFile, only: Sequence[str], timeout_secs: int) -> int:
    mutants = _selected(spec, only)
    lock = CheckoutLock(root)
    if not lock.acquire():
        _print(
            f"BUSY     another mutant_run holds {lock.path}: one run per checkout, so "
            "neither restores the other's mutant"
        )
        return EXIT_TREE
    try:
        with tempfile.TemporaryDirectory(prefix="mutant-run-") as scratch:
            runner = Runner(root, spec, timeout_secs, Path(scratch))
            try:
                recovered = runner.journal.recover()
            except TreeError as error:
                _print(f"NOT RESTORED {error}")
                return EXIT_TREE
            if recovered:
                _print(
                    f"RESTORED {recovered}: a previous run was killed with this mutant on disk. Run again."
                )
                return EXIT_TREE
            previous = {
                signum: signal.signal(signum, runner.on_signal)
                for signum in STOP_SIGNALS
            }
            try:
                return _run_all(runner, mutants)
            finally:
                for signum, handler in previous.items():
                    signal.signal(signum, handler)
    finally:
        lock.release()


def _tree_moved(runner: Runner, before: TreeState, after_what: str) -> bool:
    """Print and return True when the tracked tree is not as the run found it."""
    after = tree_state(runner.root)
    named = before.differences(after)
    if not named:
        return False
    if after.head != before.head:
        _print(
            f"HEAD MOVED from {before.head or '<no commit>'} to {after.head}: "
            "check that commit for a mutant"
        )
    _print(
        f"TREE CHANGED after {after_what}: {', '.join(named)}. The runner restores only "
        "the file it mutated, so a test wrote these; nothing else ran"
    )
    return True


def _run_all(runner: Runner, mutants: list[Mutant]) -> int:
    before = tree_state(runner.root)
    _print(
        f"mutant_run @ {before.head or '<no commit>'}: {len(mutants)} mutants in {runner.root}"
    )
    if runner.spec.tests_only:
        _print(f"TESTS-ONLY {' '.join(runner.spec.tests_only)}")
    # Each mutant runs only its own tests, so each distinct set is the baseline
    # that mutant is judged against: a test that passes in a larger session
    # (one that sets state another reads) can fail alone, whatever the mutant.
    for node in runner.spec.baseline_red:
        _print(f"EXCLUDED {node}: named BASELINE_RED, deselected from every run")
    green = []
    for index, node in enumerate(runner.spec.baseline_red):
        probe = runner.run_tests((node,), f"red-{index}", deselect=False)
        if probe.verdict == "STOPPED":
            return _stopped(runner)
        if probe.verdict == "SURVIVED":
            green.append(node)
    if green:
        for node in green:
            _print(f"BASELINE_RED {node}: passes, so it is not red by design")
        _print(
            "refusing the run: a BASELINE_RED test that passes is deselected from "
            "every run and could have killed a mutant; remove it from the list"
        )
        return EXIT_FINDINGS
    vitest = any(is_vitest(mutant.tests[0]) for mutant in mutants)
    if vitest and (problem := runner.prepare_vitest()):
        if runner.stop_signal is not None:
            return _stopped(runner)
        _print(f"NOT-TESTED vitest: {problem}; nothing was mutated")
        return EXIT_FINDINGS
    test_sets = list(dict.fromkeys(mutant.tests for mutant in mutants))
    for index, tests in enumerate(test_sets):
        baseline = runner.run_tests(tests, f"baseline-{index}")
        if baseline.verdict == "STOPPED":
            return _stopped(runner)
        if _tree_moved(runner, before, "the baseline"):
            return EXIT_TREE
        if baseline.verdict != "SURVIVED":
            _print_outcome(
                "NOT-TESTED" if baseline.verdict == "NOT-TESTED" else "FAILED",
                Outcome(
                    "BASELINE",
                    f"{baseline.detail} [tests: {' '.join(tests)}]",
                    baseline.tail,
                ),
            )
            _print(
                "the tests must pass with no mutant applied, or every mutant reads as KILLED; nothing was mutated"
            )
            return EXIT_FINDINGS
        _print(f"BASELINE ok: {baseline.detail} [tests: {' '.join(tests)}]")
    counts = {"KILLED": 0, "SURVIVED": 0, "ERROR": 0, "NOT-TESTED": 0, "REFUSED": 0}
    for index, mutant in enumerate(mutants):
        if runner.stop_signal is not None:
            return _stopped(runner)
        try:
            outcome = runner.run_mutant(mutant, index)
        except TreeError as error:
            _print(f"RESTORE FAILED {mutant.name}: {error}")
            return EXIT_TREE
        if outcome.verdict == "STOPPED":
            return _stopped(runner)
        counts[outcome.verdict] += 1
        _print_outcome(mutant.name, outcome)
        if _tree_moved(runner, before, f"mutant {mutant.name!r}"):
            return EXIT_TREE
    _print(
        f"{counts['KILLED']} of {len(mutants)} killed "
        f"({counts['SURVIVED']} survived, {counts['ERROR']} error, "
        f"{counts['NOT-TESTED']} not tested, {counts['REFUSED']} refused)"
    )
    findings = counts["ERROR"] + counts["NOT-TESTED"] + counts["REFUSED"]
    return EXIT_FINDINGS if findings else EXIT_OK


def _stopped(runner: Runner) -> int:
    signum = runner.stop_signal or signal.SIGTERM
    _print(
        f"STOPPED by signal {signum}: the file under mutation was restored; nothing else ran"
    )
    return 128 + signum


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__.split("\n\n")[0] if __doc__ else None
    )
    parser.add_argument(
        "mutants", type=Path, help="the mutants file (read, never executed)"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="the checkout the paths are relative to",
    )
    parser.add_argument(
        "--only",
        action="append",
        default=[],
        metavar="NAME",
        help="run only this mutant",
    )
    parser.add_argument(
        "--tests-only",
        nargs="+",
        default=[],
        metavar="NODE",
        help="run these test node ids for every mutant, instead of the file's lists",
    )
    parser.add_argument(
        "--check", action="store_true", help="validate every mutant; run no test"
    )
    parser.add_argument(
        "--timeout-secs",
        type=int,
        default=DEFAULT_TIMEOUT_SECS,
        help="cap on one test run",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        spec = load_mutants(args.mutants, args.tests_only)
        if args.check:
            return check(root, spec, args.only)
        return run(root, spec, args.only, args.timeout_secs)
    except FormatError as error:
        print(f"mutant_run: {args.mutants}: {error}", file=sys.stderr)
        return EXIT_USAGE
    except TreeError as error:
        print(f"mutant_run: RESTORE FAILED: {error}", file=sys.stderr)
        return EXIT_TREE


if __name__ == "__main__":
    sys.exit(main())
