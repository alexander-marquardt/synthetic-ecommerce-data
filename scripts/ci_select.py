#!/usr/bin/env python3
"""Which test files a pull request's change reaches (#495).

    ci_select.py --base BASE --head HEAD          # the test files to run, one per line
    ci_select.py --changed PATH...                # the same, for named changed paths
    ci_select.py --base BASE --head HEAD --why    # each selected file and the path that reached it

A pull request's CI used to run the whole suite (about 93 job-minutes on the 22 jobs of
one run, against a runner cap near 20 jobs), so runs queued behind each other and the merge
train gave up while a PR's CI was still queued. The trunk model (elastic/prism#12274) runs
only the tests a change can reach before the merge, and the whole suite on every push to
``main`` (``.github/workflows/ci.yaml``: the ``tests`` job has no scope on a push).

The selection is built to over-select, never to drop. A test file is selected when:

* it is itself a changed path, or it is in ``SMOKE``;
* a changed Python file is in its import closure. The closure follows ``import`` and
  ``from ... import`` statements (resolved against every Python file of the repository, by
  every dotted suffix of its path, so a package import and a bare one off ``sys.path`` both
  resolve), the ``.py`` file names a file's text mentions (a harness that loads
  ``scripts/mutation_check.py`` by path, a mutation row that names the file it plants in),
  the dotted module names it mentions, the console scripts of ``pyproject.toml`` it names
  (``ecom-generate`` runs ``generate_cli``), and, for a module that imports by computed
  name (``import_module``, ``walk_packages``, a ``*.py`` glob), every Python file under its
  own directory;
* a changed file that is not Python (a data file, a golden file, a document) is named in the
  text of any file of its closure: by the shortest unique tail of its path, by its stem, or
  by its directory (a quoted name or a path prefix), so a test that composes
  ``Path("golden-retail") / "stats.json"`` is still reached by its directory, and a data
  file under ``src/`` is reached by any test whose closure holds a module of the package that
  owns it (it is read from ``__file__``, which no text names);
* a package-walk registry (``typespec.discover``) pulls in every module of the package its
  file names by dotted string, and ``resources.files("pkg.data")`` imports that package;
* it scans the tree (a glob, a walk, ``ls-files``, in itself or a ``tests/`` helper it
  imports) and a changed path can be read by that scan: the scan's literal pattern
  (``rglob("*.py")``) matches a part of the path, or ``SCAN_SCOPES`` places the scan over it.
  A scan neither places, and a test of ``READS_WHOLE_TREE``, is selected by any change.

Two edges are not followed, because nothing runs them (#1035): ``import pickle`` is the standard
library's module, not a product module of that name, and an import inside a subcommand's branch
(``if argv[0] == "compose":``) runs only for a closure that holds the subcommand's word.

A change to the workflow, the project file, the lock file, the vendored core or a test
fixture module every test uses (``FULL_RUN``), or a diff that cannot be read, selects every
test. The same holds with no base and head (a push to ``main``). A test file of
``SELECTED_ONLY_BY`` (the tests of ``scripts/merge_pr.sh``) is selected by a change to one of
its listed paths and by no other rule (#1035).
``tests/test_ci_select_495.py`` pins each rule on a throwaway repository and pins the
real tree: every test that imports a module is selected when that module changes.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import re
import subprocess
import sys
from collections import defaultdict
from collections.abc import Collection
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

#: The directories whose ``test_*.py`` files pytest collects (``testpaths`` of pyproject.toml,
#: ``ci_shards.TEST_DIRS``).
_TEST_ROOTS = ("tests/",)

#: Test files every pull request runs: the guards of this selection and of the sharding, which
#: are cheap and fail the moment the CI wiring or the selection is wrong.
SMOKE: tuple[str, ...] = (
    "tests/test_ci_select_495.py",
    "tests/test_ci_shards_348.py",
    "tests/test_ci_tests_job_parallel_348.py",
    # These read the list of test files, so a new one can break them: 1.3 s together (#1035).
    "tests/test_ci_run_order_348.py",
    "tests/test_ci_shard_budget_704.py",
    "tests/test_ci_workers_790.py",
)

#: A change to one of these (path prefix or exact path) selects every test: the CI definition,
#: the dependency set, the vendored core, and the files pytest loads before any test.
FULL_RUN: tuple[str, ...] = (
    ".github/",
    "pyproject.toml",
    "uv.lock",
    "vendor/",
    "tests/conftest.py",
    "tests/templates_memo.py",
    "tests/ci_shard_split.py",
    "tests/xdist_groups.py",
    "scripts/ci_select.py",
    "scripts/ci_shards.py",
    "scripts/ci_shard_weights.json",
)

#: What ``scripts/merge_pr.sh`` is made of and runs: its parts, the scripts and the module it
#: calls, the tests whose ids it names, and the test files that drive it (#1035).
_MERGE_PATH: tuple[str, ...] = (
    "scripts/merge_pr.sh",
    "scripts/merge_pr/",
    "scripts/local_ci_guard.py",
    "scripts/local_ci_jobs.py",
    "scripts/measure_pins.py",
    "scripts/golden_pins.py",
    "src/synthetic_ecommerce_data/domains/industrial/measured_builds.py",
    "tests/pinned.py",
    "tests/test_catalog_golden.py",
    "tests/test_prism_field_map_drift.py",
    "tests/test_product_type_label_331.py",
    "tests/test_readme_split_240.py",
    "tests/test_merge_pr.py",
    "tests/test_merge_pr_github_ci_348.py",
)

#: Test files selected only by a change to one of their paths (an exact path, or a prefix
#: ending in ``/``), never by an import, a mention, ``SMOKE`` or a tree scan. The tests of
#: ``scripts/merge_pr.sh`` each build a throwaway origin and run a real catalogue build, 76 of
#: the suite's 257 minutes. Their closure holds nearly all of ``src/`` because the script
#: builds the catalogue, so every product PR selected them, though what they test is the
#: script's order of operations (#1035). The pins that hold the script to the product (the
#: generated files, the rebuild command, the freshness test ids, the blocks of the types the
#: two-PR case adds) are in ``tests/test_merge_pr_product_pins_1035.py``, which the usual rules
#: select. A ``FULL_RUN`` change and a push to ``main`` still run these files.
SELECTED_ONLY_BY: dict[str, tuple[str, ...]] = {
    "tests/test_merge_pr.py": _MERGE_PATH,
    "tests/test_merge_pr_github_ci_348.py": _MERGE_PATH,
}

#: Test files that read the repository whole through no import and no name: a gate that checks
#: every tracked file, a wheel build. Any change selects them. A test that globs or walks the
#: tree is found by ``_SCANS`` in its own text and in the helpers under ``tests/`` it imports.
READS_WHOLE_TREE: tuple[str, ...] = (
    "tests/test_file_size_gate_11683.py",
    "tests/test_wheel_builds.py",
    # Both read the repository's files by a walk the text scan cannot see (#495 review).
    "tests/test_readme_split_240.py",
    "tests/test_customer_name_check_393.py",
)
_SCANS = re.compile(r"\.r?glob\(|ls-files|os\.walk|\.iterdir\(")
#: A glob of a plain literal (no f-string, no escape): what it finds, it finds by that pattern.
_LITERAL_GLOB = re.compile(r"""\.r?glob\(\s*(["'])([^"'\\]+)\1\s*\)""")

#: The scans whose pattern does not say what they read: the scan's source line (stripped), and
#: the repository paths it can read (a path, or a prefix ending in ``/``; ``()`` is none: it
#: lists what the run itself wrote). A scan with no literal pattern and no row here selects its
#: test on any change, so a new or edited scan is never dropped (#1035).
SCAN_SCOPES: dict[str, dict[str, tuple[str, ...]]] = {
    "tests/shared_builds.py": {
        # the key of the build cache: what a build runs is in the closure of its test
        'files = [root] if root.is_file() else sorted(root.rglob("*"))': (),
        'for old in path.parent.glob(f"{name}-*.pickle"):': (),
    },
    "tests/test_build_refusal_writes_nothing.py": {
        'for p in sorted(root.rglob("*"))': (),
    },
    "tests/test_build_streams_by_type_952.py": {
        'assert [p.name for p in tmp_path.iterdir()] == ["catalog"]': (),
        'for p in sorted(root.rglob("*"))': (),
        "return {path.name: path.read_bytes() for path in sorted(root.iterdir())}": (),
    },
    "tests/test_catalog_golden.py": {
        "committed = {path.name for path in GOLDEN_DIR.iterdir()}": ("golden-catalog/",),
        "written = {path.name for path in fresh_build.iterdir()}": (),
    },
    "tests/test_ceiling_artifact_539.py": {
        '["git", "ls-files", "tests/*.py"], cwd=REPO, capture_output=True, text=True, check=True': (
            "tests/",
        ),
    },
    "tests/test_merge_pr_product_pins_1035.py": {
        'golden = _git(REPO, "ls-files", "golden-catalog").splitlines()': ("golden-catalog/",),
    },
    "tests/test_picture_products_1022.py": {
        'names = sorted(f.name for f in (tmp_path / "images").iterdir())': (),
    },
    "tests/test_prism_field_map_drift.py": {
        "assert [path.name for path in target.parent.iterdir()] == [FIELD_MAP_PATH.name], (": (),
    },
    "tests/test_red_commit_proof_11680.py": {
        # the installed packages of the interpreter
        "for entry in home.iterdir():": (),
    },
    "tests/test_retail_type_specs_351.py": {
        'assert not list(out.iterdir()), "the scaffold wrote a file for a refused code"': (),
        'assert not list(tmp_path.iterdir()), "the scaffold wrote a file for a bad key"': (),
    },
    "tests/test_shoppers_1131.py": {
        'names = sorted(p.name for p in (first / "users").iterdir())': (),
    },
    "tests/test_stress_catalog_948.py": {
        "return {path.name: path.read_bytes() for path in sorted(directory.iterdir())}": (),
    },
}

#: One scan: the globs its literal pattern is, or the paths its row names.
Scan = tuple[str, tuple[str, ...]]
_ANYTHING: Scan = ("name", ("*",))

#: A document names code and data; it does not change what they do. A changed ``.md`` file
#: selects the tests that name it in their own text (the test files, their helpers under
#: ``tests/``, and the scripts they load), not every test that imports a module whose prose
#: or output names the page. A picture under ``docs/`` is the same: its directory's name
#: (``images``) is a word of the product code, which reads no page (#1035).
_DOC_SUFFIXES = (".md",)
_DOC_DIR = "docs/"
_DOC_READERS = ("tests/", "scripts/")

#: A file that imports by a computed name depends on every Python file under its directory.
#: Read from the text of a product file: the docstring of a walked package's ``__init__`` says
#: that its modules are walked, and is the one place that does (``product_types``).
_DYNAMIC = re.compile(r"\b(import_module|walk_packages|iter_modules|__import__)\b|glob\([^)]*\.py")
#: Read from a script's code, not its comments and docstrings: a sentence about ``import_module``
#: imports nothing, and the pattern above made this file, and each test that reads it, depend on
#: every script and so on the retail package (#1035). A string that holds such a call is code
#: another interpreter may run.
_DYNAMIC_NAMES = frozenset({"import_module", "walk_packages", "iter_modules", "__import__"})
_GLOBS = frozenset({"glob", "rglob", "iglob"})
_PY_GLOB = re.compile(r"\.py(?!\w)")
_DYNAMIC_STRING = re.compile(
    r"\b(import_module|walk_packages|iter_modules|__import__)\s*\(|glob\([^)]*\.py(?!\w)"
)
_GENERIC_DIRS = frozenset({"tests", "scripts", "src", "docs"})
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
#: A file that calls one of these loads a script by a path it builds in a variable
#: (``path = ROOT / "scripts" / "x.py"; spec_from_file_location(name, path)``): every ``.py``
#: it names is executed, and its imports are followed.
_LOADERS = frozenset({"spec_from_file_location", "run_path", "exec_module"})
_DOTTED = re.compile(r"\b[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)+\b")
#: A Python file's text is searched for names only up to this size (a data table is not code).
_TEXT_LIMIT = 2_000_000


def _callee(node: ast.Call) -> str:
    return node.func.attr if isinstance(node.func, ast.Attribute) else getattr(node.func, "id", "")


#: A file that imports by a computed name, and the file whose strings are the names: it depends on
#: the modules so named, not on its own directory (#1035). ``golden_pins.measure_figures`` imports
#: each test module of ``pinned.MODULES``; the directory rule gave it every script instead, and so
#: gave the five industrial tests that import it the whole retail package.
IMPORTS_NAMED_BY: dict[str, str] = {"scripts/golden_pins.py": "tests/pinned.py"}


def _imports_by_name(nodes: list[ast.AST], strings: list[str]) -> bool:
    """Whether a script imports by a computed name, or globs Python files (``_DYNAMIC_NAMES``)."""
    for node in nodes:
        if isinstance(node, ast.Name):
            named = node.id
        elif isinstance(node, ast.Attribute):
            named = node.attr
        elif isinstance(node, ast.alias):
            named = node.name
        elif isinstance(node, ast.Call) and _callee(node) in _GLOBS:
            for arg in [*node.args, *(k.value for k in node.keywords)]:
                for inner in ast.walk(arg):
                    if isinstance(inner, ast.Constant) and _PY_GLOB.search(str(inner.value)):
                        return True
            continue
        else:
            continue
        if named in _DYNAMIC_NAMES:
            return True
    return any(_DYNAMIC_STRING.search(value) for value in strings)


def _listed(path: str, entries: Collection[str]) -> bool:
    """Whether ``path`` is one of ``entries``: an exact path, or under a prefix ending in ``/``."""
    return any(path == f or (f.endswith("/") and path.startswith(f)) for f in entries)


def _import_roots(dotted: str) -> set[str]:
    """Where a bare ``import dotted`` finds a repository file: a directory of ``sys.path``."""
    rel = dotted.replace(".", "/")
    return {
        f"{root}{rel}{tail}"
        for root in ("", "src/", "tests/", "scripts/")
        for tail in (".py", "/__init__.py")
    }


def _subcommand(node: ast.If) -> str | None:
    """The word of ``if argv and argv[0] == "word":``, or None."""
    tests = node.test.values if isinstance(node.test, ast.BoolOp) else [node.test]
    if isinstance(node.test, ast.BoolOp) and not isinstance(node.test.op, ast.And):
        return None
    for test in tests:
        if (
            isinstance(test, ast.Compare)
            and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq)
            and ast.unparse(test.left) == "argv[0]"
            and isinstance(test.comparators[0], ast.Constant)
            and isinstance(test.comparators[0].value, str)
        ):
            return test.comparators[0].value
    return None


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


def changed_paths(base: str, head: str, root: Path = REPO) -> list[str] | None:
    """Paths changed from the merge base of ``base`` and ``head`` to ``head`` (a rename is its
    two paths); None when git cannot say."""
    try:
        out = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "diff",
                "--name-only",
                "--no-renames",
                "-z",
                f"{base}...{head}",
            ],
            capture_output=True,
            check=True,
        ).stdout.decode()
    except (subprocess.CalledProcessError, OSError):
        return None
    return [f for f in out.split("\0") if f]


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
        #: file -> subcommand word -> what only that subcommand's branch imports
        self.gated: dict[str, dict[str, set[str]]] = {}
        self._scans: dict[str, frozenset[Scan]] = {}
        for path in self.py:
            self.edges[path], self.leaves[path] = self._edges(path)
        self._closure: dict[str, tuple[frozenset[str], frozenset[str]]] = {}

    def _console_scripts(self) -> dict[str, set[str]]:
        """``[project.scripts]`` of pyproject.toml (read as text: tomllib needs Python 3.11)."""
        project = self.root / "pyproject.toml"
        if not project.is_file():
            return {}
        section = re.search(
            r"^\[project\.scripts\]\n(.*?)(?=^\[|\Z)", project.read_text(), re.S | re.M
        )
        found: dict[str, set[str]] = {}
        for name, target in re.findall(
            r'^([\w-]+)\s*=\s*"([^":]+)', section.group(1) if section else "", re.M
        ):
            found[name] = set(self.by_name.get(target, ()))
        return found

    def _resolve(self, name: str) -> set[str]:
        """The Python files an imported dotted name can mean, with each package it passes."""
        found: set[str] = set()
        parts = name.split(".")
        for end in range(1, len(parts) + 1):
            found |= self.by_name.get(".".join(parts[:end]), set())
        return found

    def _resolve_import(self, name: str) -> set[str]:
        """``_resolve`` for an absolute import: a name of the standard library is the standard
        library's unless a directory of ``sys.path`` holds a file of that name."""
        found = self._resolve(name)
        if name.split(".")[0] not in sys.stdlib_module_names:
            return found
        parts = name.split(".")
        here: set[str] = set()
        for end in range(1, len(parts) + 1):
            here |= _import_roots(".".join(parts[:end]))
        return found & here

    @staticmethod
    def _strings(nodes: list[ast.AST]) -> list[str]:
        """Every string constant that is not a docstring (a docstring names files in prose)."""
        docstrings: set[int] = set()
        for node in nodes:
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
            for n in nodes
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docstrings
        ]

    def _collect_aliases(self) -> None:
        """Module-level names bound to an expression naming a ``.py`` file (``S = d / "a.py"``)."""
        for module in self.trees.values():
            for node in module.body if module is not None else []:
                if isinstance(node, ast.Assign):
                    named = {
                        n.value
                        for n in ast.walk(node.value)
                        if isinstance(n, ast.Constant)
                        and isinstance(n.value, str)
                        and n.value.endswith(".py")
                    }
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            self.aliases[target.id] |= named

    def _executed_names(self, nodes: list[ast.AST]) -> set[str]:
        """The ``.py`` base names a file passes to a call that runs them."""
        found: set[str] = set()
        calls = [n for n in nodes if isinstance(n, ast.Call)]
        if any(_callee(n) in _LOADERS for n in calls):
            for node in nodes:
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    found.update(Path(n).name for n in _PY_NAME.findall(node.value))
        for node in calls:
            callee = _callee(node)
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
        # One walk of the file, read by every rule below: a plan parses 2000 files (#1035).
        nodes = list(ast.walk(module)) if module is not None else []
        strings = self._strings(nodes)
        self.strings[path] = "\n".join(strings)
        if module is not None:
            branches = {
                id(inner): word
                for node in nodes
                if isinstance(node, ast.If) and (word := _subcommand(node)) is not None
                for statement in node.body
                for inner in ast.walk(statement)
            }
            always = edges
            gated: dict[str, set[str]] = defaultdict(set)
            for node in nodes:
                word = branches.get(id(node))
                edges = always if word is None else gated[word]
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        edges |= self._resolve_import(alias.name)
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
                            edges |= self.by_name.get(
                                f"{name}.{alias.name}" if name else alias.name, set()
                            )
                    else:
                        edges |= self._resolve_import(node.module or "")
                        for alias in node.names:
                            edges |= self._resolve_import(f"{node.module}.{alias.name}")
            edges = always
            self.gated[path] = {w: found - always for w, found in gated.items() if found - always}
        # A package a file names whole in a string (``resources.files("pkg.data")``) is imported
        # by that call, in product code too.
        for value in strings:
            if "." in value and _DOTTED.fullmatch(value.strip()):
                edges |= {
                    i for i in self.by_name.get(value.strip(), ()) if i.endswith("/__init__.py")
                }
        # What a file names in a string is a dependency of the file that names it; its prose
        # (comments, docstrings) is not. Product code under src/ takes its dependencies by import.
        if not path.startswith("src/"):
            executed = self._executed_names(nodes)
            for value in strings:
                for name in _PY_NAME.findall(value):
                    # A test file named in a string is named, not run (a row of the mutation
                    # bed, a pinned test id): the file that names it reads it, so a change to
                    # it selects that file, but its imports are not followed.
                    named = self.by_basename.get(Path(name).name, set())
                    leaves.update(named)
                    if Path(name).name in executed:
                        edges.update(p for p in named if not is_test_file(p))
                for dotted in _DOTTED.findall(value):
                    if dotted in self.by_name:
                        edges |= self._resolve(dotted)
                for script, targets in self.scripts.items():
                    if re.search(rf"(?<![\w-]){re.escape(script)}(?![\w-])", value):
                        edges |= targets
        if path.startswith("scripts/") and module is not None:
            dynamic = _imports_by_name(nodes, strings)
        else:
            dynamic = _DYNAMIC.search(text) is not None
        if dynamic and path in IMPORTS_NAMED_BY:
            named_by = self.trees.get(IMPORTS_NAMED_BY[path])
            for value in self._strings(list(ast.walk(named_by))) if named_by else []:
                edges |= self.by_name.get(value, set())
        elif dynamic and not path.startswith("tests/"):
            prefix = str(here) + "/"
            edges |= {p for p in self.py if p.startswith(prefix)}
            # A package-walk registry (``typespec.discover``) loads every module of the package
            # it is given by name: the package a dotted string of the file names.
            for value in strings:
                for dotted in _DOTTED.findall(value):
                    for init in self.by_name.get(dotted, ()):
                        if init.endswith("/__init__.py"):
                            edges |= {
                                p for p in self.py if p.startswith(init[: -len("__init__.py")])
                            }
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
                while stack:
                    node = stack.pop()
                    leaves |= self.leaves.get(node, set())
                    for nxt in self.edges.get(node, ()):
                        if nxt not in seen:
                            seen.add(nxt)
                            stack.append(nxt)
                # What a subcommand imports, once a file besides its own holds the word.
                for node in [n for n in seen if self.gated.get(n)]:
                    for word, targets in self.gated[node].items():
                        new = targets - seen
                        if new and self._says(word, seen - {node}):
                            seen |= new
                            stack.extend(new)
            self._closure[path] = (frozenset(seen), frozenset(leaves - seen))
        return self._closure[path]

    def _says(self, word: str, members: Collection[str]) -> bool:
        """Whether a string of ``members`` outside product code holds ``word``: the tests and
        scripts name the subcommand they run."""
        pattern = re.compile(rf"(?<![\w-]){re.escape(word)}(?![\w-])")
        return any(
            pattern.search(self.strings.get(m, "")) for m in members if not m.startswith("src/")
        )

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
        # The directory, spelled as a path part or a glob/f-string prefix. A source directory
        # is named in a thousand strings and says nothing: a test that globs one is found by
        # ``reads_whole_tree``.
        if len(parts) > 1 and parts[-2] not in _GENERIC_DIRS:
            parent = "/".join(parts[:-1])
            patterns.append(rf"[\"']{re.escape(parts[-2])}[\"']")
            # a string that is the directory's name
            patterns.append(rf"(?m)^{re.escape(parts[-2])}$")
            patterns.append(rf"(?<![\w-]){re.escape(parent)}/[*{{]")
        return tuple(re.compile(p) for p in patterns)

    def scans(self, path: str) -> frozenset[Scan]:
        """What each scan in the text of one file can read."""
        if path not in self._scans:
            text = self.text.get(path, "")
            rows = SCAN_SCOPES.get(path, {})
            found: set[Scan] = set()
            for hit in _SCANS.finditer(text):
                start = text.rfind("\n", 0, hit.start()) + 1
                line = text[start:].split("\n", 1)[0].strip()
                literal = _LITERAL_GLOB.match(text, hit.start())
                if line in rows:
                    found.add(("paths", rows[line]))
                elif literal:
                    # The last part: a directory it matches is walked by what follows it.
                    found.add(("name", (literal.group(2).rsplit("/", 1)[-1] or "*",)))
                else:
                    found.add(_ANYTHING)
            self._scans[path] = frozenset(found)
        return self._scans[path]

    def scan_reads(self, test: str, changed: str) -> bool:
        """Whether a scan of ``test`` (its own, or one of a helper under ``tests/`` it imports)
        can read ``changed``; a listed gate reads every file. A test of ``SELECTED_ONLY_BY`` is
        governed by that table alone."""
        if test in SELECTED_ONLY_BY:
            return False
        if test in READS_WHOLE_TREE:
            return True
        members, _ = self.closure(test)
        parts = Path(changed).parts
        for member in members:
            if not member.startswith("tests/"):
                continue
            for kind, entries in self.scans(member):
                if kind == "paths":
                    if _listed(changed, entries):
                        return True
                elif any(fnmatch.fnmatchcase(part, entries[0]) for part in parts):
                    return True
        return False

    def reaches(self, test: str, changed: str) -> bool:
        members, leaves = self.closure(test)
        if changed in members or changed in leaves:
            return True
        if changed.endswith(".py"):
            return False if changed in self.text else self._unresolved_import(members, changed)
        if self._owner_module_in(members, changed):
            return True
        patterns = self._tokens(changed)
        document = changed.endswith(_DOC_SUFFIXES) or changed.startswith(_DOC_DIR)
        readers = _DOC_READERS if document else ("",)
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
    return path.startswith(_TEST_ROOTS) and (
        (name.startswith("test_") and name.endswith(".py")) or name.endswith("_test.py")
    )


def select(
    changed: list[str],
    tree: Tree | None = None,
    root: Path = REPO,
    among: Collection[str] | None = None,
) -> tuple[list[str], dict[str, str]]:
    """The test files to run for the changed paths, and the reason for each.

    ``among`` asks about those test files only: each one is selected or not as it is in the
    whole selection, and a question about one file skips the other 400 (#790)."""
    tree = tree or Tree(root)
    tests = sorted(p for p in tree.py if is_test_file(p) and (among is None or p in among))
    reasons: dict[str, str] = {}
    for path in changed:
        if _listed(path, FULL_RUN):
            return tests, {t: f"full run: {path}" for t in tests}
    held = [t for t in tests if t in SELECTED_ONLY_BY]
    for test in held:
        hit = [p for p in changed if _listed(p, SELECTED_ONLY_BY[test])]
        if hit:
            reasons[test] = hit[0]
    for test in SMOKE:
        if test in tests and test not in held:
            reasons[test] = "smoke"
    for test in tests:
        if test in reasons or test in held:
            continue
        hit = [p for p in changed if tree.scan_reads(test, p)]
        if hit:
            reasons[test] = f"its scan reads {hit[0]}"
    for path in changed:
        for test in tests:
            if test in reasons or test in held:
                continue
            if path == test or tree.reaches(test, path):
                reasons[test] = path
    return sorted(reasons), reasons


def selection_for_range(base: str, head: str, root: Path = REPO) -> list[str] | None:
    """The selected test files for a PR range; None for every test (no range, unreadable diff)."""
    if not base or not head:
        return None
    found = changed_paths(base, head, root)
    if not found:
        return None
    chosen, _ = select(found, Tree(root))
    return chosen


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="")
    parser.add_argument("--head", default="")
    parser.add_argument("--changed", nargs="*", default=None)
    parser.add_argument("--why", action="store_true")
    args = parser.parse_args(argv)
    if args.changed is not None:
        changed: list[str] | None = args.changed
    elif args.base and args.head:
        changed = changed_paths(args.base, args.head)
    else:
        changed = None
    tree = Tree()
    every = sorted(p for p in tree.py if is_test_file(p))
    if not changed:
        # No range, or git cannot read it, or an empty diff: nothing may be dropped.
        print("\n".join(every))
        return 0
    chosen, reasons = select(changed, tree)
    for test in chosen:
        print(f"{test}\t{reasons[test]}" if args.why else test)
    return 0


if __name__ == "__main__":
    sys.exit(main())
