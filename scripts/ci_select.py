#!/usr/bin/env python3
"""Which test files a pull request's change reaches (#495).

    ci_select.py --base BASE --head HEAD          # the test files to run, one per line
    ci_select.py --changed PATH...                # the same, for named changed paths
    ci_select.py --base BASE --head HEAD --why    # each selected file and the changed path that reached it

A pull request's CI used to run the whole suite (about 93 job-minutes on the 22 jobs of
one run, against a runner cap near 20 jobs), so runs queued behind each other and the merge
train gave up while a PR's CI was still queued. The trunk model (elastic/prism#12274) runs
only the tests a change can reach before the merge, and the whole suite on every push to
``main`` (``.github/workflows/ci.yaml``: the ``tests`` job has no scope on a push).

The selection is built to over-select, never to drop. A test file is selected when:

* it is itself a changed path, or it is in ``SMOKE``;
* a changed Python file is in its import closure. The closure follows ``import`` and
  ``from ... import`` statements (resolved against every Python file of the repository, by
  every dotted suffix of its path, so the ``sys.path`` inserts of the retail tests need no
  special case), the ``.py`` file names a file's text mentions (a harness that loads
  ``scripts/mutation_check.py`` by path, a mutation row that names the file it plants in),
  the dotted module names it mentions, the console scripts of ``pyproject.toml`` it names
  (``ecom-generate`` runs ``generate_cli``), and, for a module that imports by computed
  name (``import_module``, ``walk_packages``, a ``*.py`` glob), every Python file under its
  own directory;
* a changed file that is not Python (a data file, a golden file, a document) is named in the
  text of any file of its closure: by the shortest unique tail of its path, by its stem, or
  by its directory (a quoted name or a path prefix), so a test that composes
  ``Path("golden-retail") / "stats.json"`` is still reached by its directory.

A change to the workflow, the project file, the lock file, the vendored core or a test
fixture module every test uses (``FULL_RUN``), or a diff that cannot be read, selects every
test. The same holds with no base and head (a push to ``main``).
``tests/test_ci_select_495.py`` pins each rule on a throwaway repository and pins the
real tree: every test that imports a module is selected when that module changes.
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: Test files every pull request runs: the guards of this selection and of the sharding, which
#: are cheap and fail the moment the CI wiring or the selection is wrong.
SMOKE: tuple[str, ...] = (
    "tests/test_ci_select_495.py",
    "tests/test_ci_shards_348.py",
    "tests/test_ci_tests_job_parallel_348.py",
)

#: A change to one of these (path prefix or exact path) selects every test: the CI definition,
#: the dependency set, the vendored core, and the files pytest loads before any test.
FULL_RUN: tuple[str, ...] = (
    ".github/",
    "pyproject.toml",
    "uv.lock",
    "vendor/",
    "tests/conftest.py",
    "tests/ci_shard_split.py",
    "tests/xdist_groups.py",
    "scripts/ci_select.py",
    "scripts/ci_shards.py",
    "scripts/ci_shard_weights.json",
)

#: Test files that name a data file only as a fixture or pin its listing, never its content:
#: a MODIFIED path under one of these prefixes does not select the test. An added or deleted
#: path still does (a pinned listing of the tracked files changes). ``tests/test_merge_pr.py``
#: drives ``scripts/merge_pr.sh`` in a throwaway origin of its own and compares the
#: ``GENERATED`` list with ``git ls-files golden-catalog``, so a regenerated golden file
#: cannot change its result, and it is 76 of the suite's 256 minutes.
CONTENT_INSENSITIVE: dict[str, tuple[str, ...]] = {
    "tests/test_merge_pr.py": ("golden-retail/", "golden-catalog/", "docs/", "README.md"),
    "tests/test_merge_pr_github_ci_348.py": ("golden-retail/", "golden-catalog/", "docs/", "README.md"),
}

#: A document names code and data; it does not change what they do. A changed ``.md`` file
#: selects the tests that name it in their own text (the test files, their helpers under
#: ``tests/``, and the scripts they load), not every test that imports a module whose prose
#: or output names the page.
_DOC_SUFFIXES = (".md",)
_DOC_READERS = ("tests/", "scripts/")

#: A file that imports by a computed name depends on every Python file under its directory.
_DYNAMIC = re.compile(r"\b(import_module|walk_packages|iter_modules|__import__)\b|glob\([^)]*\.py")
_PY_NAME = re.compile(r"[\w.-]+\.py\b")
#: A call that runs or loads what it is given: a ``.py`` file named inside its arguments is
#: executed with its imports. Named anywhere else (``read_text``, a pinned command line, a copy)
#: the file is a dependency by its own text only, and its imports are not followed.
_EXEC_CALLEES = frozenset(
    {
        "spec_from_file_location", "run_path", "exec_module", "import_module", "run", "call",
        "check_call", "check_output", "Popen", "system", "execv", "execvp", "runpy",
    }
)  # fmt: skip
_DOTTED = re.compile(r"\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+\b")
#: A Python file's text is searched for names only up to this size (a data table is not code).
_TEXT_LIMIT = 2_000_000


def tracked_files(root: Path) -> list[str]:
    """Repo-relative posix paths of every tracked or unignored file (every file but .git and
    virtual environments when ``root`` is not a git checkout)."""
    run = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
    )
    if run.returncode == 0:
        found = [p for p in run.stdout.decode().split("\0") if p]
    else:
        found = [
            p.relative_to(root).as_posix()
            for p in root.rglob("*")
            if not {".git", ".venv"} & set(p.relative_to(root).parts)
        ]
    return sorted(p for p in found if (root / p).is_file())


def changed_paths(base: str, head: str, root: Path = REPO) -> tuple[list[str], set[str]] | None:
    """Paths changed from the merge base of ``base`` and ``head`` to ``head`` (a rename is its
    two paths), and which of them were only modified; None when git cannot say."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "diff", "--name-status", "--no-renames", "-z", f"{base}...{head}"],
            capture_output=True,
            check=True,
        ).stdout.decode()
    except (subprocess.CalledProcessError, OSError):
        return None
    fields = [f for f in out.split("\0") if f]
    paths: list[str] = []
    modified: set[str] = set()
    for status, path in zip(fields[0::2], fields[1::2], strict=False):
        paths.append(path)
        if status == "M":
            modified.add(path)
    return paths, modified


class Tree:
    """The import and mention graph of one checkout."""

    def __init__(self, root: Path = REPO) -> None:
        self.root = root
        self.files = tracked_files(root)
        self.py = [p for p in self.files if p.endswith(".py")]
        self.text: dict[str, str] = {}
        for path in self.files:
            if path.endswith(".py") or Path(path).suffix in _TEXT_SUFFIXES:
                try:
                    data = (root / path).read_bytes()[:_TEXT_LIMIT]
                except OSError:
                    continue
                self.text[path] = data.decode("utf-8", "replace")
        self.by_name: dict[str, set[str]] = defaultdict(set)
        for path in self.py:
            parts = list(Path(path).with_suffix("").parts)
            if parts[-1] == "__init__":
                parts = parts[:-1]
            for start in range(len(parts)):
                self.by_name[".".join(parts[start:])].add(path)
        self.by_basename: dict[str, set[str]] = defaultdict(set)
        for path in self.py:
            self.by_basename[Path(path).name].add(path)
        self.scripts = self._console_scripts()
        self.strings: dict[str, str] = {}
        self.aliases: dict[str, set[str]] = defaultdict(set)
        self.trees: dict[str, ast.Module | None] = {}
        for path in self.py:
            try:
                self.trees[path] = ast.parse(self.text.get(path, ""))
            except SyntaxError:
                self.trees[path] = None
        self._collect_aliases()
        self.edges: dict[str, set[str]] = {}
        self.leaves: dict[str, set[str]] = {}
        for path in self.py:
            self.edges[path], self.leaves[path] = self._edges(path)
        self._closure: dict[str, tuple[frozenset[str], frozenset[str]]] = {}

    def _console_scripts(self) -> dict[str, set[str]]:
        """``[project.scripts]`` of pyproject.toml (read as text: tomllib needs Python 3.11)."""
        project = self.root / "pyproject.toml"
        if not project.is_file():
            return {}
        section = re.search(r"^\[project\.scripts\]\n(.*?)(?=^\[|\Z)", project.read_text(), re.S | re.M)
        found: dict[str, set[str]] = {}
        for name, target in re.findall(r'^([\w-]+)\s*=\s*"([^":]+)', section.group(1) if section else "", re.M):
            found[name] = set(self.by_name.get(target, ()))
        return found

    def _resolve(self, name: str) -> set[str]:
        """The Python files an imported dotted name can mean, with each package it passes."""
        found: set[str] = set()
        parts = name.split(".")
        for end in range(1, len(parts) + 1):
            found |= self.by_name.get(".".join(parts[:end]), set())
        return found

    @staticmethod
    def _strings(module: ast.Module) -> list[str]:
        """Every string constant that is not a docstring (a docstring names files in prose)."""
        docstrings: set[int] = set()
        for node in ast.walk(module):
            if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                first = node.body[0] if node.body else None
                if (
                    isinstance(first, ast.Expr)
                    and isinstance(first.value, ast.Constant)
                    and isinstance(first.value.value, str)
                ):
                    docstrings.add(id(first.value))
        return [
            n.value
            for n in ast.walk(module)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings
        ]

    def _collect_aliases(self) -> None:
        """Module-level names bound to an expression that names a ``.py`` file: ``SCRIPT = ROOT / "a.py"``."""
        for module in self.trees.values():
            for node in module.body if module is not None else []:
                if isinstance(node, ast.Assign):
                    named = {
                        n.value
                        for n in ast.walk(node.value)
                        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.endswith(".py")
                    }
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.aliases[target.id] |= named

    def _executed_names(self, module: ast.Module) -> set[str]:
        """The ``.py`` base names a file passes to a call that runs them."""
        found: set[str] = set()
        for node in ast.walk(module):
            if not isinstance(node, ast.Call):
                continue
            callee = node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")
            if callee not in _EXEC_CALLEES:
                continue
            for arg in [*node.args, *(k.value for k in node.keywords)]:
                for inner in ast.walk(arg):
                    if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                        found.update(Path(n).name for n in _PY_NAME.findall(inner.value))
                    elif isinstance(inner, ast.Name):
                        found.update(Path(n).name for n in self.aliases.get(inner.id, ()))
        return found

    def _edges(self, path: str) -> tuple[set[str], set[str]]:
        text = self.text.get(path, "")
        edges: set[str] = set()
        leaves: set[str] = set()
        module = self.trees.get(path)
        here = Path(path).parent
        strings = self._strings(module) if module is not None else []
        self.strings[path] = "\n".join(strings)
        if module is not None:
            for node in ast.walk(module):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        edges |= self._resolve(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.level:
                        base = here
                        for _ in range(node.level - 1):
                            base = base.parent
                        prefix = ".".join(base.parts)
                        name = ".".join(x for x in (prefix, node.module) if x)
                        if node.module:
                            edges |= self._resolve(name)
                        else:  # ``from . import x``: the package and its members
                            edges |= self.by_name.get(prefix, set())
                        for alias in node.names:
                            edges |= self.by_name.get(f"{name}.{alias.name}" if name else alias.name, set())
                    else:
                        edges |= self._resolve(node.module or "")
                        for alias in node.names:
                            edges |= self._resolve(f"{node.module}.{alias.name}")
        # What a file names in a string is a dependency of the file that names it; its prose
        # (comments, docstrings) is not. Product code under src/ takes its dependencies by import.
        if not path.startswith("src/"):
            executed = self._executed_names(module) if module is not None else set()
            for value in strings:
                for name in _PY_NAME.findall(value):
                    # A test file named in a string is named, not run (a row of the mutation
                    # bed, a pinned test id); it is a dependency only when imported.
                    named = {
                        p for p in self.by_basename.get(Path(name).name, set()) if not is_test_file(p)
                    }
                    (edges if Path(name).name in executed else leaves).update(named)
                for dotted in _DOTTED.findall(value):
                    if dotted in self.by_name:
                        edges |= self._resolve(dotted)
                for script, targets in self.scripts.items():
                    if re.search(rf"(?<![\w-]){re.escape(script)}(?![\w-])", value):
                        edges |= targets
        if _DYNAMIC.search(text) and not path.startswith("tests/"):
            prefix = str(here) + "/"
            edges |= {p for p in self.py if p.startswith(prefix)}
            # A package-walk registry (``typespec.discover``) loads every module of the package
            # it is given by name: the package a dotted string of the file names.
            for value in strings:
                for dotted in _DOTTED.findall(value):
                    for init in self.by_name.get(dotted, ()):
                        if init.endswith("/__init__.py"):
                            edges |= {p for p in self.py if p.startswith(init[: -len("__init__.py")])}
        edges.discard(path)
        leaves -= edges
        leaves.discard(path)
        return edges, leaves

    def closure(self, path: str) -> tuple[frozenset[str], frozenset[str]]:
        """The files whose code and text ``path`` depends on, and the files it only reads."""
        if path not in self._closure:
            seen = {path}
            leaves: set[str] = set()
            stack = [path]
            while stack:
                node = stack.pop()
                leaves |= self.leaves.get(node, set())
                for nxt in self.edges.get(node, ()):
                    if nxt not in seen:
                        seen.add(nxt)
                        stack.append(nxt)
            self._closure[path] = (frozenset(seen), frozenset(leaves - seen))
        return self._closure[path]

    def _tokens(self, changed: str) -> tuple[re.Pattern[str], ...]:
        """The patterns that name a changed non-Python file in some text."""
        parts = Path(changed).parts
        others = [Path(p).parts for p in self.files if p != changed]
        tail = 1
        while tail < len(parts) and any(o[-tail:] == parts[-tail:] for o in others):
            tail += 1
        suffix = "/".join(parts[-tail:])
        patterns = [rf"(?<![\w.-]){re.escape(suffix)}(?![\w-])"]
        stem = Path(changed).stem
        if len(stem) >= 8 and re.search(r"[-_\d]", stem):  # a plain word ("stats") is in every text
            patterns.append(rf"(?<![\w-]){re.escape(stem)}(?![\w-])")
        if len(parts) > 1:  # the directory, spelled as a path part or a glob/f-string prefix
            parent = "/".join(parts[:-1])
            patterns.append(rf"[\"']{re.escape(parts[-2])}[\"']")
            patterns.append(rf"(?<![\w-]){re.escape(parent)}/[*{{]")
        return tuple(re.compile(p) for p in patterns)

    def reaches(self, test: str, changed: str) -> bool:
        members, leaves = self.closure(test)
        if changed in members or changed in leaves:
            return True
        if changed.endswith(".py"):
            return False if changed in self.text else self._unresolved_import(members, changed)
        if self._owner_module_in(members, changed):
            return True
        patterns = self._tokens(changed)
        readers = _DOC_READERS if changed.endswith(_DOC_SUFFIXES) else ("",)
        return any(
            any(p.search(self.strings.get(m, "")) for p in patterns)
            for m in members
            if m.startswith(readers)
        )

    def _package_dir(self, changed: str) -> str | None:
        """The directory of the package that owns a non-Python file under ``src/``: the nearest
        ancestor that is a package (holds ``__init__.py``) and holds a module other than its
        ``__init__.py``, so a data directory of a package belongs to the package that reads it."""
        if not changed.startswith("src/"):
            return None
        parent = Path(changed).parent
        while str(parent) not in ("", "."):
            here = parent.as_posix()
            init = f"{here}/__init__.py"
            if init in self.trees and any(
                p.startswith(here + "/") and p.count("/") == here.count("/") + 1 and p != init
                for p in self.py
            ):
                return here
            parent = parent.parent
        return None

    def _owner_module_in(self, members: frozenset[str], changed: str) -> bool:
        """A data file of a package is read by a path built from ``__file__``, which no text
        names: any test whose closure holds a module of the owning package may read it."""
        here = self._package_dir(changed)
        return here is not None and any(m.startswith(here + "/") for m in members)

    def _unresolved_import(self, members: frozenset[str], changed: str) -> bool:
        """A deleted module: a file that still names it by stem is broken, so it is selected."""
        stem = Path(changed).stem
        pattern = re.compile(rf"(?<![\w-]){re.escape(stem)}(?![\w-])")
        return any(pattern.search(self.strings.get(m, "")) for m in members)


_TEXT_SUFFIXES = {
    ".sh", ".txt", ".md", ".yaml", ".yml", ".toml", ".json", ".cfg", ".ini", ".html",
}  # fmt: skip


def is_test_file(path: str) -> bool:
    name = Path(path).name
    return path.startswith("tests/") and (
        (name.startswith("test_") and name.endswith(".py")) or name.endswith("_test.py")
    )


def select(
    changed: list[str],
    tree: Tree | None = None,
    root: Path = REPO,
    modified: set[str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    """The test files to run for the changed paths, and the reason for each."""
    tree = tree or Tree(root)
    tests = sorted(p for p in tree.py if is_test_file(p))
    reasons: dict[str, str] = {}
    for path in changed:
        if any(path == f or (f.endswith("/") and path.startswith(f)) for f in FULL_RUN):
            return tests, {t: f"full run: {path}" for t in tests}
    for test in SMOKE:
        if test in tests:
            reasons[test] = "smoke"
    for path in changed:
        for test in tests:
            if test in reasons:
                continue
            if path in (modified or ()) and path.startswith(CONTENT_INSENSITIVE.get(test, ())):
                continue
            if path == test or tree.reaches(test, path):
                reasons[test] = path
    return sorted(reasons), reasons


def selection_for_range(base: str, head: str, root: Path = REPO) -> list[str] | None:
    """The selected test files for a PR range, or None for 'every test' (no range, unreadable diff)."""
    if not base or not head:
        return None
    found = changed_paths(base, head, root)
    if not found or not found[0]:
        return None
    chosen, _ = select(found[0], Tree(root), modified=found[1])
    return chosen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    parser.add_argument("--changed", nargs="*", default=None)
    parser.add_argument("--why", action="store_true")
    args = parser.parse_args(argv)
    modified: set[str] = set()
    if args.changed is not None:
        changed: list[str] | None = args.changed
    elif args.base and args.head:
        found = changed_paths(args.base, args.head)
        changed, modified = found if found else (None, set())
    else:
        changed = None
    tree = Tree()
    every = sorted(p for p in tree.py if is_test_file(p))
    if not changed:
        # No range, or git cannot read it, or an empty diff: nothing may be dropped.
        print("\n".join(every))
        return 0
    chosen, reasons = select(changed, tree, modified=modified)
    for test in chosen:
        print(f"{test}\t{reasons[test]}" if args.why else test)
    return 0


if __name__ == "__main__":
    sys.exit(main())
