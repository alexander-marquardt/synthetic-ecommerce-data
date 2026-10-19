"""A pull request's CI runs the test files its change reaches, and a push to main runs all (#495).

``scripts/ci_select.py`` reads the import and mention graph of a checkout and names the test
files a change can reach; ``scripts/ci_shards.py --plan`` deals that selection to as few
shards as hold it. A test the selection drops is a test that never ran before the merge, and a
green check does not show it, so this file pins:

* each rule of the selection on a throwaway tree (an import, a transitive import, a module run
  by path, a console script, an import by computed name, a package-walk registry, a data file
  read from ``__file__``, a document, a deleted module);
* the real tree: every test that imports a module is selected when that module changes (an
  oracle written here, apart from the selector), and every mutation row's file selects
  ``tests/test_mutation_bed.py``;
* ``plan``: disjoint shards whose union is the selection, no range meaning every file;
* the tables: ``SMOKE``, ``FULL_RUN`` and ``CONTENT_INSENSITIVE`` name files that exist.

It times nothing.
"""

from __future__ import annotations

import ast
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ci_select = _load("ci_select")
ci_shards = _load("ci_shards")


def _write(root: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def _tree(tmp_path: Path, files: dict[str, str]) -> ci_select.Tree:
    _write(tmp_path, files)
    return ci_select.Tree(tmp_path)


def _picked(tree: ci_select.Tree, *changed: str, modified: tuple[str, ...] = ()) -> list[str]:
    return ci_select.select(list(changed), tree, modified=set(modified))[0]


# --- each rule, on a throwaway tree --------------------------------------------------------


def test_a_test_is_selected_by_the_module_it_imports_and_not_by_another(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "src/alpha.py": "X = 1\n",
            "src/beta.py": "Y = 2\n",
            "tests/test_alpha.py": "import alpha\n",
            "tests/test_beta.py": "import beta\n",
        },
    )
    assert _picked(tree, "src/alpha.py") == ["tests/test_alpha.py"]


def test_a_test_is_selected_by_a_module_its_import_chain_reaches(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "src/top.py": "import middle\n",
            "src/middle.py": "from pkg import leaf\n",
            "src/pkg/__init__.py": "",
            "src/pkg/leaf.py": "Z = 3\n",
            "tests/test_top.py": "import top\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/pkg/leaf.py") == ["tests/test_top.py"]


def test_a_relative_import_is_followed(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "src/pkg/__init__.py": "",
            "src/pkg/a.py": "from .b import B\n",
            "src/pkg/b.py": "B = 1\n",
            "tests/test_a.py": "from pkg import a\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/pkg/b.py") == ["tests/test_a.py"]


def test_a_changed_test_file_selects_itself(tmp_path: Path) -> None:
    tree = _tree(tmp_path, {"tests/test_a.py": "x = 1\n", "tests/test_b.py": "y = 2\n"})
    assert _picked(tree, "tests/test_b.py") == ["tests/test_b.py"]


def test_a_script_run_by_path_is_followed_into_its_imports(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "scripts/tool.py": "import helper\n",
            "scripts/helper.py": "H = 1\n",
            "tests/test_tool.py": (
                'import subprocess\nsubprocess.run(["python3", "scripts/tool.py"])\n'
            ),
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "scripts/helper.py") == ["tests/test_tool.py"]


def test_a_script_only_read_as_text_is_a_dependency_but_its_imports_are_not_followed(
    tmp_path: Path,
) -> None:
    tree = _tree(
        tmp_path,
        {
            "scripts/tool.py": "import helper\n",
            "scripts/helper.py": "H = 1\n",
            "tests/test_reads.py": (
                'from pathlib import Path\nPath("scripts/tool.py").read_text()\n'
            ),
        },
    )
    assert _picked(tree, "scripts/tool.py") == ["tests/test_reads.py"]
    assert _picked(tree, "scripts/helper.py") == []


def test_a_console_script_named_in_a_test_reaches_the_module_it_runs(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "pyproject.toml": '[project.scripts]\necom-run = "pkg.cli:main"\n',
            "src/pkg/__init__.py": "",
            "src/pkg/cli.py": "def main(): ...\n",
            "tests/test_cli.py": 'import subprocess\nsubprocess.run(["ecom-run", "--help"])\n',
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/pkg/cli.py") == ["tests/test_cli.py"]


def test_a_module_that_imports_by_computed_name_depends_on_its_whole_directory(
    tmp_path: Path,
) -> None:
    tree = _tree(
        tmp_path,
        {
            "src/plug/__init__.py": "",
            "src/plug/loader.py": (
                "import importlib\n\ndef load(n):\n    return importlib.import_module(n)\n"
            ),
            "src/plug/ext_one.py": "ONE = 1\n",
            "tests/test_loader.py": "from plug import loader\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/plug/ext_one.py") == ["tests/test_loader.py"]


_REGISTRY = {
    "src/core/__init__.py": "",
    "src/core/registry.py": (
        "import importlib\nimport pkgutil\n\n"
        'TYPES_PACKAGE = "family.types"\n\n'
        "def discover(package=TYPES_PACKAGE):\n"
        "    root = importlib.import_module(package)\n"
        "    walk = pkgutil.walk_packages(root.__path__, prefix=package + '.')\n"
        "    return [importlib.import_module(f.name) for f in walk]\n"
    ),
    "src/family/__init__.py": "",
    "src/family/types/__init__.py": "",
    "src/family/types/alpha.py": "KEY = 'alpha'\n",
    "src/family/other/__init__.py": "",
    "src/family/other/beta.py": "KEY = 'beta'\n",
    "tests/test_registry.py": "from core import registry\n",
    "tests/test_other.py": "import json\n",
}


def test_a_type_module_found_by_a_package_walk_selects_a_test_that_imports_the_registry(
    tmp_path: Path,
) -> None:
    """The registry names its package in a string and imports its modules by computed name:
    no import statement joins the test to ``alpha.py``, yet the test runs its code."""
    tree = _tree(tmp_path, _REGISTRY)
    assert _picked(tree, "src/family/types/alpha.py") == ["tests/test_registry.py"]
    assert _picked(tree, "src/family/other/beta.py") == []


def test_a_data_file_of_a_package_selects_a_test_that_imports_a_module_of_that_package(
    tmp_path: Path,
) -> None:
    """``Path(__file__).with_name(...)`` names the file by no string a text search finds."""
    tree = _tree(
        tmp_path,
        {
            "src/pkg/__init__.py": "",
            "src/pkg/loader.py": (
                "from pathlib import Path\n"
                'DATA = Path(__file__).parent.joinpath("da" + "ta", "tab" + "le.json")\n'
            ),
            "src/pkg/data/__init__.py": "",
            "src/pkg/data/table.json": "{}\n",
            "src/other/__init__.py": "",
            "src/other/mod.py": "M = 1\n",
            "tests/test_loader.py": "from pkg import loader\n",
            "tests/test_other.py": "from other import mod\n",
        },
    )
    assert _picked(tree, "src/pkg/data/table.json") == ["tests/test_loader.py"]


def test_a_package_named_whole_in_a_string_of_product_code_is_imported_by_that_call(
    tmp_path: Path,
) -> None:
    """``resources.files("pkg.data")`` imports ``pkg/data/__init__.py``; product code under
    ``src/`` takes its other dependencies by import only, and a lone word is not a package."""
    tree = _tree(
        tmp_path,
        {
            "src/pkg/__init__.py": "",
            "src/pkg/reader.py": (
                "from importlib import resources\n"
                'FILES = resources.files("pkg.data")\nWORD = "data"\n'
            ),
            "src/pkg/data/__init__.py": "MARK = 1\n",
            "src/pkg/word/__init__.py": "MARK = 2\n",
            "tests/test_reader.py": "from pkg import reader\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/pkg/data/__init__.py") == ["tests/test_reader.py"]


def test_a_test_file_named_in_a_string_selects_the_file_that_names_it(tmp_path: Path) -> None:
    """The mutation bed names the test file of a row; a change to that file can break the bed,
    and the bed's importers are not selected for it."""
    tree = _tree(
        tmp_path,
        {
            "scripts/rows.py": 'ROW = "tests/test_planted.py"\n',
            "tests/test_planted.py": "x = 1\n",
            "tests/test_bed.py": "import rows\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "tests/test_planted.py") == ["tests/test_bed.py", "tests/test_planted.py"]


def test_a_test_that_scans_the_tree_is_selected_by_any_change(tmp_path: Path) -> None:
    """A glob or a walk in the test, or in a helper it imports, reads files no import names."""
    tree = _tree(
        tmp_path,
        {
            "src/unrelated.py": "U = 1\n",
            "tests/scanning.py": 'from pathlib import Path\nALL = list(Path(".").rglob("*.py"))\n',
            "tests/test_scan.py": (
                'from pathlib import Path\nFILES = list(Path("src").glob("*.py"))\n'
            ),
            "tests/test_via_helper.py": "import scanning\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/unrelated.py") == ["tests/test_scan.py", "tests/test_via_helper.py"]


def test_a_file_in_a_source_directory_is_not_reached_by_the_directory_s_name(
    tmp_path: Path,
) -> None:
    tree = _tree(
        tmp_path,
        {
            "tests/review_1_mutants.py.txt": "TESTS = []\n",
            "tests/test_names_it.py": 'ROOT = "tests"\n',
        },
    )
    assert _picked(tree, "tests/review_1_mutants.py.txt") == []


def test_a_fixture_file_is_selected_only_by_the_test_that_names_it(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "tests/data/golden_one.jsonl": "{}\n",
            "tests/test_golden.py": 'P = "tests/data/golden_one.jsonl"\n',
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "tests/data/golden_one.jsonl") == ["tests/test_golden.py"]


def test_a_directory_named_in_a_glob_selects_a_test_for_a_file_under_it(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "golden-retail/stats.json": "{}\n",
            "tests/test_gold.py": ('from pathlib import Path\nDIR = Path("golden-retail")\n'),
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "golden-retail/stats.json") == ["tests/test_gold.py"]


def test_a_changed_document_selects_only_the_tests_and_scripts_that_name_it(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "docs/guide.md": "# guide\n",
            "src/mod.py": 'NOTE = "see docs/guide.md"\n',
            "tests/test_mod.py": "import mod\n",
            "tests/test_guide.py": 'P = "docs/guide.md"\n',
        },
    )
    assert _picked(tree, "docs/guide.md") == ["tests/test_guide.py"]


def test_a_deleted_module_still_named_by_a_test_selects_it(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "tests/test_gone.py": 'P = "retired_module"\n',
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/retired_module.py") == ["tests/test_gone.py"]


def test_a_modified_golden_file_does_not_select_a_content_insensitive_test(tmp_path: Path) -> None:
    name = next(iter(ci_select.CONTENT_INSENSITIVE), None)
    assert name is not None, "CONTENT_INSENSITIVE names at least one test"
    tree = _tree(
        tmp_path,
        {
            "golden-retail/stats.json": "{}\n",
            name: 'P = "golden-retail/stats.json"\n',
            "tests/test_reads_it.py": 'P = "golden-retail/stats.json"\n',
        },
    )
    assert _picked(tree, "golden-retail/stats.json", modified=("golden-retail/stats.json",)) == [
        "tests/test_reads_it.py"
    ]
    assert name in _picked(tree, "golden-retail/stats.json"), (
        "an added or deleted file still selects it"
    )


def test_a_change_to_the_workflow_the_lock_or_a_shared_fixture_selects_every_test(
    tmp_path: Path,
) -> None:
    tree = _tree(tmp_path, {"tests/test_a.py": "x = 1\n", "tests/test_b.py": "y = 2\n"})
    every = ["tests/test_a.py", "tests/test_b.py"]
    for path in (".github/workflows/ci.yaml", "pyproject.toml", "uv.lock", "tests/conftest.py"):
        assert _picked(tree, path) == every, path
    assert _picked(tree, "vendor/prism/anything.py") == every


def test_the_smoke_tests_run_with_any_change(tmp_path: Path) -> None:
    assert ci_select.SMOKE, "SMOKE names at least one test"
    smoke = ci_select.SMOKE[0]
    tree = _tree(tmp_path, {smoke: "x = 1\n", "tests/test_b.py": "y = 2\n", "src/m.py": "M = 1\n"})
    assert _picked(tree, "src/m.py") == [smoke]


# --- the real tree --------------------------------------------------------------------------


@pytest.fixture(scope="module")
def real() -> ci_select.Tree:
    return ci_select.Tree(REPO)


def _test_files(tree: ci_select.Tree) -> list[str]:
    return sorted(p for p in tree.py if ci_select.is_test_file(p))


def _repo_file(dotted: str) -> str | None:
    """The repo file a dotted module name means, by the three source roots and the repo root."""
    for root in ("src", "tests", "scripts", ""):
        base = Path(root) / dotted.replace(".", "/") if root else Path(dotted.replace(".", "/"))
        for candidate in (base.with_suffix(".py"), base / "__init__.py"):
            if (REPO / candidate).is_file():
                return candidate.as_posix()
    return None


def _direct_imports(path: str) -> set[str]:
    """Files ``path`` imports, found from its syntax tree only (the oracle: it shares no code
    with the selector)."""
    try:
        module = ast.parse((REPO / path).read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return set()
    names: set[str] = set()
    for node in ast.walk(module):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            names.add(node.module)
            names.update(f"{node.module}.{alias.name}" for alias in node.names)
    found = {_repo_file(n) for n in names}
    for name in list(names):  # the packages a dotted import passes through
        parts = name.split(".")
        found.update(_repo_file(".".join(parts[:end])) for end in range(1, len(parts)))
    return {f for f in found if f and f != path}


def _import_closure(path: str, cache: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    stack = [path]
    while stack:
        node = stack.pop()
        if node not in cache:
            cache[node] = _direct_imports(node)
        for nxt in cache[node]:
            if nxt not in seen:
                seen.add(nxt)
                stack.append(nxt)
    return seen


def test_every_test_that_imports_a_module_is_selected_when_that_module_changes(
    real: ci_select.Tree,
) -> None:
    cache: dict[str, set[str]] = {}
    # One selection per changed module, not per (test, module) pair: ``select`` walks every test,
    # and 7000 pairs name about 100 modules (a 100 s test that hit the 300 s limit on a loaded
    # runner once a PR grew the tree).
    selected: dict[str, list[str]] = {}
    tests = _test_files(real)
    assert len(tests) > 100
    for test in tests:
        for module in sorted(_import_closure(test, cache)):
            if module.startswith(("vendor/", "tests/conftest")) or module == test:
                continue
            if module not in selected:
                selected[module] = ci_select.select([module], real)[0]
            chosen = selected[module]
            assert test in chosen, (
                f"{test} imports {module}, and a change to {module} does not select it"
            )


def _mutation_rows() -> list:
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        spec = importlib.util.spec_from_file_location(
            "mutation_check", REPO / "scripts" / "mutation_check.py"
        )
        assert spec is not None and spec.loader is not None
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(REPO / "scripts"))
    return list(module.MUTATIONS)


def test_every_file_a_mutation_row_plants_in_selects_the_mutation_bed(real: ci_select.Tree) -> None:
    """``tests/test_mutation_bed.py`` checks that each row still plants: it is the one test a
    change to the planted file or to a row file can break without any import joining them."""
    bed = "tests/test_mutation_bed.py"
    rows = _mutation_rows()
    assert len(rows) > 100
    planted = {Path(row.root, row.file).as_posix().removeprefix("./") for row in rows}
    missing = sorted(p for p in planted if bed not in ci_select.select([p], real)[0])
    assert not missing, f"a change to these files does not select {bed}: {missing[:5]}"
    harness = [
        "scripts/mutation_check.py",
        *sorted(p for p in real.py if Path(p).name.startswith("mutation_rows_")),
        *sorted(p for p in real.py if p.startswith("scripts/mutations/")),
    ]
    unselected = [p for p in harness if bed not in ci_select.select([p], real)[0]]
    assert not unselected, f"a change to these does not select {bed}: {unselected}"


def test_the_smoke_tests_are_selected_by_any_change(real: ci_select.Tree) -> None:
    assert set(ci_select.SMOKE) <= set(ci_select.select(["docs/ci-sharding.md"], real)[0])


def test_a_documentation_change_selects_a_small_part_of_the_suite(real: ci_select.Tree) -> None:
    weights = ci_shards.load_weights()
    every = _test_files(real)
    chosen = ci_select.select(["docs/ci-sharding.md"], real)[0]
    share = sum(weights.get(t, 20) for t in chosen) / sum(weights.get(t, 20) for t in every)
    assert share < 0.2, f"a document change selects {share:.0%} of the suite's seconds: {chosen}"


def test_the_tables_name_files_that_exist() -> None:
    for name in ci_select.SMOKE:
        assert (REPO / name).is_file(), f"SMOKE names {name}, which is not a file"
    assert "tests/test_ci_select_495.py" in ci_select.SMOKE, (
        "this file guards the selection: it always runs"
    )
    for name in ci_select.READS_WHOLE_TREE:
        assert (REPO / name).is_file(), f"READS_WHOLE_TREE names {name}, which is not a file"
    for entry in ci_select.FULL_RUN:
        target = REPO / entry
        assert target.is_dir() if entry.endswith("/") else target.is_file(), (
            f"FULL_RUN names {entry}"
        )
    for must in (
        ".github/",
        "pyproject.toml",
        "uv.lock",
        "scripts/ci_select.py",
        "scripts/ci_shards.py",
    ):
        assert must in ci_select.FULL_RUN, f"a change to {must} must run every test"
    for name, prefixes in ci_select.CONTENT_INSENSITIVE.items():
        assert (REPO / name).is_file(), f"CONTENT_INSENSITIVE names {name}"
        assert name in ci_shards.SPLIT_FILES, f"{name} is too heavy to be listed unless it is split"
        assert prefixes, f"{name} lists nothing it is insensitive to"


# --- the plan -------------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> str:
    env = {
        **os.environ,
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_CONFIG_SYSTEM": os.devnull,
        "GIT_AUTHOR_NAME": "t",
        "GIT_AUTHOR_EMAIL": "t@example.com",
        "GIT_COMMITTER_NAME": "t",
        "GIT_COMMITTER_EMAIL": "t@example.com",
    }
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=env)
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


@pytest.fixture
def repo_with_change(tmp_path: Path) -> tuple[Path, str, str]:
    """Six test files, five of which import ``shared``; a second commit changes ``shared``."""
    files = {
        "src/shared.py": "V = 1\n",
        "src/lonely.py": "L = 1\n",
        "tests/test_lonely.py": "import lonely\n",
    }
    files.update({f"tests/test_user_{n}.py": "import shared\n" for n in range(5)})
    _write(tmp_path, files)
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "src/shared.py").write_text("V = 2\n", encoding="utf-8")
    _git(tmp_path, "commit", "-q", "-am", "change")
    return tmp_path, base, _git(tmp_path, "rev-parse", "HEAD")


def test_the_plan_deals_disjoint_shards_whose_union_is_the_selection(
    repo_with_change: tuple[Path, str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    root, base, head = repo_with_change
    monkeypatch.setattr(ci_shards, "SCOPED_SHARD_SECONDS", 30.0)  # 5 files x 20 s: 4 shards
    selection = ci_select.selection_for_range(base, head, root)
    assert selection is not None
    assert "tests/test_lonely.py" not in selection
    assert {f"tests/test_user_{n}.py" for n in range(5)} <= set(selection)
    dealt: list[list[str]] = []
    counts = set()
    for number in range(1, 9):
        shards, files = ci_shards.plan(number, 8, base, head, root)
        counts.add(shards)
        dealt.append(files)
    assert len(counts) == 1, "every shard reads the same shard count"
    (shards,) = counts
    assert 1 < shards < 8, "a selection of a few files runs on fewer shards than the matrix has"
    flat = [name for files in dealt for name in files]
    assert sorted(flat) == sorted(set(flat)), "a test file is in two shards"
    assert set(flat) == set(selection), "the shards do not add up to the selection"
    assert all(not files for files in dealt[shards:]), "a shard past the count has files"
    assert all(files for files in dealt[:shards]), "a counted shard is empty"


def test_a_small_selection_is_one_shard(repo_with_change: tuple[Path, str, str]) -> None:
    root, base, head = repo_with_change
    shards, files = ci_shards.plan(1, 16, base, head, root)
    assert shards == 1
    assert ci_shards.plan(2, 16, base, head, root) == (1, [])
    assert "tests/test_user_0.py" in files


def test_no_range_is_every_test_file_on_every_shard_of_the_matrix(
    repo_with_change: tuple[Path, str, str],
) -> None:
    root, _, _ = repo_with_change
    every = ci_shards.collected_test_files(root)
    dealt = [ci_shards.plan(n, 4, "", "", root) for n in range(1, 5)]
    assert {shards for shards, _ in dealt} == {4}
    flat = [name for _, files in dealt for name in files]
    assert sorted(flat) == every
    assert ci_select.selection_for_range("", "", root) is None


def test_a_range_that_only_modifies_a_golden_file_skips_the_content_insensitive_test(
    tmp_path: Path,
) -> None:
    name = next(iter(ci_select.CONTENT_INSENSITIVE), None)
    assert name is not None, "CONTENT_INSENSITIVE names at least one test"
    _write(
        tmp_path,
        {
            "golden-retail/stats.json": "{}\n",
            "golden-retail/other.json": "{}\n",
            name: 'P = "golden-retail/stats.json"\n',
            "tests/test_reads_it.py": 'P = "golden-retail/stats.json"\n',
        },
    )
    _git(tmp_path, "init", "-q", "-b", "main")
    _git(tmp_path, "add", "-A")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "golden-retail/stats.json").write_text('{"a": 1}\n', encoding="utf-8")
    _git(tmp_path, "commit", "-q", "-am", "regenerate")
    modified_head = _git(tmp_path, "rev-parse", "HEAD")
    assert ci_select.selection_for_range(base, modified_head, tmp_path) == [
        "tests/test_reads_it.py"
    ]
    (tmp_path / "golden-retail/stats.json").unlink()
    _git(tmp_path, "commit", "-q", "-am", "delete")
    selected = ci_select.selection_for_range(
        modified_head, _git(tmp_path, "rev-parse", "HEAD"), tmp_path
    )
    assert selected is not None and name in selected, "a deleted file still selects it"


def test_an_unreadable_range_is_every_test_file(repo_with_change: tuple[Path, str, str]) -> None:
    root, _, head = repo_with_change
    assert ci_select.selection_for_range("0" * 40, head, root) is None
    assert ci_select.selection_for_range(head, head, root) is None, "an empty diff drops nothing"
    shards, files = ci_shards.plan(1, 2, "0" * 40, head, root)
    assert shards == 2 and files


def test_the_plan_line_prints_the_count_then_the_files() -> None:
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--plan", "1", "--of", "3"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert done.returncode == 0, done.stderr
    first, *files = done.stdout.splitlines()
    assert first == "shards=3"
    shard = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--shard", "1", "--of", "3"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert files == shard.stdout.splitlines(), "with no range --plan is the plain shard"


def test_plan_all_prints_every_test_file_for_a_local_run() -> None:
    done = subprocess.run(
        [sys.executable, str(REPO / "scripts" / "ci_shards.py"), "--plan", "all"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert done.returncode == 0, done.stderr
    first, *files = done.stdout.splitlines()
    assert first == "shards=1"
    assert files == ci_shards.collected_test_files()


def test_the_selector_prints_every_test_for_no_change_and_the_reached_ones_for_a_path() -> None:
    def run(*args: str) -> list[str]:
        done = subprocess.run(
            [sys.executable, str(REPO / "scripts" / "ci_select.py"), *args],
            capture_output=True,
            text=True,
            cwd=REPO,
        )
        assert done.returncode == 0, done.stderr
        return done.stdout.splitlines()

    every = run()
    assert every == run("--changed"), "an empty list of changed paths is no scope"
    assert len(every) > 100
    chosen = run("--changed", "tests/test_variant_axes_47.py", "--why")
    assert "tests/test_variant_axes_47.py\ttests/test_variant_axes_47.py" in chosen, chosen
    assert "tests/test_ci_shards_348.py\tsmoke" in chosen, chosen
    assert len(chosen) < 60, "one changed test file does not select the suite"


def test_the_workflow_selects_from_the_range_and_a_push_to_main_has_none() -> None:
    import yaml

    workflow = yaml.safe_load(
        (REPO / ".github" / "workflows" / "ci.yaml").read_text(encoding="utf-8")
    )
    runs = " ".join(step.get("run", "") for step in workflow["jobs"]["tests"]["steps"])
    assert "--base" in runs and "--head" in runs, "the shard must be told the range"
    assert "github.event.pull_request.base.sha" in runs and "inputs.base" in runs
    assert "pull_request" in (workflow.get("on") or workflow.get(True)), (
        "a pull request runs the tests job"
    )
    assert "push" in (workflow.get("on") or workflow.get(True)), "main is run whole after a merge"


# --- the review of the first head: a planner that crashes, and three tests the selection dropped


def test_a_script_loaded_by_a_path_held_in_a_variable_is_followed_into_its_imports(
    tmp_path: Path,
) -> None:
    tree = _tree(
        tmp_path,
        {
            "scripts/tool.py": "import helper\n",
            "scripts/helper.py": "H = 1\n",
            "tests/test_loads.py": (
                "import importlib.util\n"
                "def load():\n"
                '    path = ROOT / "scripts" / "tool.py"\n'
                '    spec = importlib.util.spec_from_file_location("tool", path)\n'
                "    return spec\n"
            ),
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "scripts/helper.py") == ["tests/test_loads.py"]


def test_the_real_price_census_test_is_selected_by_a_module_its_script_imports(
    real: ci_select.Tree,
) -> None:
    chosen = ci_select.select(["src/synthetic_ecommerce_data/core/price.py"], real)[0]
    assert "tests/test_price_census_69.py" in chosen


@pytest.mark.parametrize(
    "name", ["tests/test_readme_split_240.py", "tests/test_customer_name_check_393.py"]
)
def test_a_test_that_reads_the_whole_tree_is_selected_by_any_change(
    name: str, real: ci_select.Tree
) -> None:
    assert name in ci_select.READS_WHOLE_TREE
    assert name in ci_select.select(["docs/ci-sharding.md"], real)[0]


def _tests_job_step(step_id_or_name: str) -> str:
    import yaml

    workflow = yaml.safe_load(
        (REPO / ".github" / "workflows" / "ci.yaml").read_text(encoding="utf-8")
    )
    for step in workflow["jobs"]["tests"]["steps"]:
        if step.get("id") == step_id_or_name or step.get("name") == step_id_or_name:
            return step["run"]
    raise AssertionError(f"no step {step_id_or_name!r} in the tests job")


def _run_step(tmp_path: Path, run: str, planner: str) -> tuple[int, str]:
    """Run a workflow step's script with the expressions filled and ``planner`` as the
    planner script; returns the exit status and what the step wrote to GITHUB_OUTPUT."""
    import re

    _write(tmp_path, {"scripts/ci_shards.py": planner})
    output = tmp_path / "github_output"
    output.write_text("", encoding="utf-8")
    script = re.sub(r"\$\{\{.*?\}\}", "1", run)
    done = subprocess.run(
        ["bash", "-e", "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "GITHUB_OUTPUT": str(output)},
    )
    return done.returncode, output.read_text(encoding="utf-8")


CRASH = "import sys\nsys.stderr.write('boom')\nsys.exit(1)\n"
GARBAGE = "print('Traceback')\n"
NO_FILE = "print('shards=1')\n"
ONE_FILE = "print('shards=1')\nprint('tests/test_a.py')\n"


@pytest.mark.parametrize("step", ["select", "Tests"])
@pytest.mark.parametrize("planner", [CRASH, GARBAGE])
def test_a_planner_that_crashes_or_prints_no_plan_is_a_red_step(
    tmp_path: Path, step: str, planner: str
) -> None:
    status, written = _run_step(tmp_path, _tests_job_step(step), planner)
    assert status != 0, "a planner that fails must not read as no test to run"
    assert "run=false" not in written


def test_the_select_step_says_run_only_when_the_plan_holds_a_file(tmp_path: Path) -> None:
    run = _tests_job_step("select")
    assert _run_step(tmp_path, run, ONE_FILE) == (0, "run=true\n")
    assert _run_step(tmp_path, run, NO_FILE) == (0, "run=false\n")
