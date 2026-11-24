"""What a shard's plan costs, and the edges of an import by computed name (#1035).

* A run plans once: the ``ceiling-catalogue`` job writes every shard's plan, and a shard reads its
  own before it checks out, so a shard with no file costs seconds.
* A selection searches each text once for a changed file.
* A script imports by a computed name when its code does. A comment, a docstring or a pattern that
  says ``import_module`` imports nothing, and made a retail change select 127 s of merge tests.
* ``IMPORTS_NAMED_BY``: ``golden_pins`` imports the modules ``tests/pinned.py`` names, not its own
  directory.
"""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

import pytest
import yaml

import pinned
from test_ci_select_495 import _picked, _tests_job_step, _tree, _write, ci_select, ci_shards

REPO = Path(__file__).resolve().parent.parent

# --- a plan is made once a run --------------------------------------------------------------

PLANNER = """
import sys
from pathlib import Path
if "--plan" in sys.argv:
    made = Path("plans")
    made.write_text(made.read_text() + "x" if made.is_file() else "x")
    print("shards=3")
    print("tests/test_a.py")
"""
RUNNER = "import sys\nopen('ran', 'w').write(' '.join(sys.argv[1:]))\n"
CI = yaml.safe_load((REPO / ".github" / "workflows" / "ci.yaml").read_text(encoding="utf-8"))
SHARDS = CI["jobs"]["tests"]["strategy"]["matrix"]["shard"]


def _steps(tmp_path: Path, saved: str | None, shard: str, *steps: str) -> tuple[int, str]:
    """Run the named steps of shard ``shard``, in order, on a runner whose plan artifact holds
    ``saved`` as shard 1's plan. The last step's exit status and what GITHUB_OUTPUT holds."""
    _write(tmp_path, {"scripts/ci_shards.py": PLANNER, "scripts/ci_run_pytest.py": RUNNER})
    output = tmp_path / "output"
    output.write_text("")
    plans = tmp_path / "temp" / "test-plans"
    plans.mkdir(parents=True)
    if saved is not None:
        (plans / "test-plan-1.txt").write_text(saved)
    # A local run started on a runner has that runner's RUNNER_TEMP too.
    env = {**os.environ, "GITHUB_OUTPUT": str(output), "RUNNER_TEMP": str(plans.parent)}
    status = 0
    for step in steps:
        script = re.sub(r"\$\{\{.*?\}\}", shard, _tests_job_step(step))
        status = subprocess.run(["bash", "-e", "-c", script], cwd=tmp_path, env=env).returncode
        if status:
            break
    return status, output.read_text()


def test_a_shard_runs_the_plan_the_run_made(tmp_path: Path) -> None:
    done = _steps(tmp_path, "shards=3\ntests/test_a.py\n", "1", "select", "Tests")
    assert done == (0, "run=true\n")
    assert (tmp_path / "ran").read_text() == "-- uv run --locked pytest tests/test_a.py"
    assert not (tmp_path / "plans").exists(), "the shard planned again"


def test_a_shard_with_no_file_plans_nothing_and_runs_no_test(tmp_path: Path) -> None:
    done = _steps(tmp_path, "shards=3\n", "1", "select", "Tests")
    assert done == (0, "run=false\n")
    assert not (tmp_path / "ran").exists()
    assert not (tmp_path / "plans").exists(), "the shard planned again"


@pytest.mark.parametrize("saved", [None, "", "Traceback\n"], ids=["absent", "empty", "garbage"])
def test_a_shard_whose_plan_is_absent_or_no_plan_is_red(tmp_path: Path, saved: str | None) -> None:
    """Never an empty plan: a hosted shard that plans for itself hides a run with no plan."""
    status, written = _steps(tmp_path, saved, "1", "select")
    assert status != 0
    assert "run=" not in written
    assert not (tmp_path / "plans").exists(), "the shard planned for itself"


def test_a_local_run_makes_its_own_plan(tmp_path: Path) -> None:
    """``merge_pr.sh --local-ci`` runs the steps as the shard ``all``, and reads no other plan."""
    assert _steps(tmp_path, "shards=3\ntests/test_b.py\n", "all", "select", "Tests") == (
        0,
        "run=true\n",
    )
    assert (tmp_path / "ran").read_text() == "-- uv run --locked pytest tests/test_a.py"


def test_a_shard_reads_its_plan_before_it_checks_out_and_checks_out_only_with_a_file() -> None:
    """A shard with no file cost 0.6 to 1.0 runner-minutes, most of it the checkout of the whole
    history; a retail change left about 15 of the 20 shards with none (#1035)."""
    steps = CI["jobs"]["tests"]["steps"]
    select = next(i for i, s in enumerate(steps) if s.get("id") == "select")
    checkouts = [i for i, s in enumerate(steps) if s.get("uses", "").startswith("actions/checkout")]
    assert len(checkouts) == 1
    assert checkouts[0] > select, "every shard checks out before it knows it has a file"
    assert steps[checkouts[0]].get("if") == "steps.select.outputs.run == 'true'"
    plans = [s for s in steps[:select] if "uses" in s]
    assert [s["with"]["name"] for s in plans] == ["test-plans"]
    assert plans[0]["with"]["path"] == "${{ runner.temp }}/test-plans"


def test_the_run_plans_every_shard_of_the_matrix_once_where_the_shards_read_it() -> None:
    job = CI["jobs"]["ceiling-catalogue"]
    assert CI["jobs"]["tests"]["needs"] == "ceiling-catalogue"
    planned = [s["run"] for s in job["steps"] if "--plans-out" in s.get("run", "")]
    assert len(planned) == 1, "the plan is not made in the job the shards wait for"
    assert re.search(r"--of (\d+)", planned[0])[1] == str(len(SHARDS)), "not the matrix's count"
    for name in ("github.event.pull_request.base.sha || inputs.base", "head.sha || inputs.head"):
        assert name in planned[0]
    upload = next(s for s in job["steps"] if s.get("with", {}).get("name") == "test-plans")
    assert upload["with"]["path"] == "${{ runner.temp }}/test-plans"
    assert upload["with"]["if-no-files-found"] == "error"
    checkout = next(s for s in job["steps"] if s.get("uses", "").startswith("actions/checkout"))
    assert "'0'" in str(checkout.get("with", {}).get("fetch-depth")), "the base is not reachable"


def _main(*args: str) -> int:
    """``ci_shards.main``'s exit status, argparse's refusal included."""
    try:
        return ci_shards.main(list(args))
    except SystemExit as refused:
        return int(refused.code or 0)


def test_the_plans_written_are_the_plans_a_shard_makes_and_the_change_is_read_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    reads: list[str] = []
    chosen = ci_shards.collected_test_files()[:40]

    def selection(base: str, head: str, root: Path) -> list[str]:
        reads.append(base)
        return list(chosen)

    monkeypatch.setattr(ci_select, "selection_for_range", selection)
    # not the base and head of any other test: a selection may be kept per range
    ends = ["--base", f"b{tmp_path}", "--head", f"h{tmp_path}"]
    assert _main("--plans-out", str(tmp_path / "out"), "--of", "5", *ends) == 0
    assert len(reads) == 1, "each shard's plan read the change again"
    capsys.readouterr()
    for number in range(1, 6):
        assert _main("--plan", str(number), "--of", "5", *ends) == 0
        expected = capsys.readouterr().out
        assert (tmp_path / "out" / f"test-plan-{number}.txt").read_text() == expected
    assert len(list((tmp_path / "out").iterdir())) == 5


def test_a_selection_searches_a_text_for_a_changed_file_once(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Every test that reaches a module searched that module's text again: a change to one JSON
    file took 8 to 32 s to select for, most of it the same two million searches (#1035)."""
    files = {"tests/helper.py": "X = 1\n", "data/some_rows_1.json": "{}\n"}
    files |= {f"tests/test_{n}.py": "import helper\n" for n in "abc"}
    tree = _tree(tmp_path, files)
    asked: list[str] = []
    real = tree._tokens
    monkeypatch.setattr(tree, "_tokens", lambda changed: asked.append(changed) or real(changed))
    searched: list[str] = []

    class Texts(dict):
        def get(self, name, default=None):
            searched.append(name)
            return super().get(name, default)

    monkeypatch.setattr(tree, "strings", Texts(tree.strings))
    assert _picked(tree, "data/some_rows_1.json") == []
    assert asked == ["data/some_rows_1.json"]
    assert searched.count("tests/helper.py") == 1
    _write(tmp_path, {"tests/helper.py": 'X = "some_rows_1.json"\n'})
    assert len(_picked(ci_select.Tree(tmp_path), "data/some_rows_1.json")) == 3


# --- an import by computed name -------------------------------------------------------------


def _reaches_the_directory(tmp_path: Path, tool: str) -> bool:
    tree = _tree(
        tmp_path,
        {
            "scripts/tool.py": tool,
            "scripts/helper.py": "H = 1\n",
            "tests/test_tool.py": "import tool\n",
        },
    )
    return _picked(tree, "scripts/helper.py") == ["tests/test_tool.py"]


@pytest.mark.parametrize(
    "tool",
    [
        '"""It says import_module and glob("*.py")."""\n',
        "# importlib.import_module(name)\n",
        'NAMES = frozenset({"import_module", "walk_packages"})\n',
        'PATTERN = r"\\b(import_module|iter_modules|__import__)\\b"\n',
        'def clear(cached):\n    return list(cached.glob("*.pyc"))\n',
    ],
)
def test_a_script_that_only_names_a_computed_import_does_not_depend_on_its_directory(
    tmp_path: Path, tool: str
) -> None:
    assert not _reaches_the_directory(tmp_path, tool)


@pytest.mark.parametrize(
    "tool",
    [
        "import importlib\n\ndef load(n):\n    return importlib.import_module(n)\n",
        "from importlib import import_module as load\n",
        "import importlib\n\nload = importlib.import_module\n",
        "def load(n):\n    return __import__(n)\n",
        "import pkgutil\n\nFOUND = list(pkgutil.iter_modules([]))\n",
        'def found(here):\n    return sorted(here.glob("kit_*.py"))\n',
        'def found(here, stem):\n    return sorted(here.rglob(f"{stem}*.py"))\n',
        'import glob\n\nFOUND = glob.glob(pathname="*.py")\n',
        'CODE = "import importlib; importlib.import_module(name)"\n',
        "CODE = 'sorted(here.glob(\"*.py\"))'\n",
        # a file this Python cannot parse is read as text
        'def broken(:\n    return here.glob("*.py")\n',
    ],
)
def test_a_file_that_imports_by_a_computed_name_depends_on_its_directory(
    tmp_path: Path, tool: str
) -> None:
    assert _reaches_the_directory(tmp_path, tool)


def test_a_walked_package_whose_docstring_says_so_still_depends_on_its_modules(
    tmp_path: Path,
) -> None:
    """``product_types/__init__`` holds no walk: its docstring is the edge to each type module."""
    tree = _tree(
        tmp_path,
        {
            "src/pkg/__init__.py": '"""Walked by ``pkgutil.iter_modules``."""\n',
            "src/pkg/leaf.py": "L = 1\n",
            "tests/test_pkg.py": "import pkg\n",
            "tests/test_other.py": "import json\n",
        },
    )
    assert _picked(tree, "src/pkg/leaf.py") == ["tests/test_pkg.py"]


def test_a_file_of_imports_named_by_depends_on_the_named_modules(tmp_path: Path) -> None:
    tree = _tree(
        tmp_path,
        {
            "scripts/golden_pins.py": (
                "import importlib\n\ndef load(n):\n    return importlib.import_module(n)\n"
            ),
            "scripts/helper.py": "H = 1\n",
            "src/leaf.py": "L = 1\n",
            "tests/pinned.py": 'MODULES = ("test_measured",)\n',
            "tests/test_measured.py": "import leaf\n",
            "tests/test_other.py": "import json\n",
            "tests/test_pins.py": "import golden_pins\n",
        },
    )
    assert _picked(tree, "scripts/helper.py") == []
    both = ["tests/test_measured.py", "tests/test_pins.py"]
    assert _picked(tree, "tests/test_measured.py") == both
    assert _picked(tree, "src/leaf.py") == both


@pytest.fixture(scope="module")
def real() -> ci_select.Tree:
    return ci_select.Tree()


def test_every_module_golden_pins_measures_is_reached_from_its_tests(real: ci_select.Tree) -> None:
    table = getattr(ci_select, "IMPORTS_NAMED_BY", {})
    assert table == {"scripts/golden_pins.py": "tests/pinned.py"}
    closure = real.closure("scripts/golden_pins.py")[0]
    assert [m for m in pinned.MODULES if f"tests/{m}.py" not in closure] == []


def test_a_retail_row_selects_no_test_through_a_script_s_prose(real: ci_select.Tree) -> None:
    row = "src/synthetic_ecommerce_data/domains/retail/color_word_brand_rows.py"
    chosen = ci_select.select([row], real)[0]
    assert "tests/test_retail_scale.py" in chosen
    industrial = ("test_merge_pr_shape_539", "test_type_roller_chain", "test_golden_pins_reseed_50")
    assert [n for n in industrial if f"tests/{n}.py" in chosen] == []


def test_a_new_test_file_selects_the_guards_that_read_the_list_of_test_files(
    real: ci_select.Tree,
) -> None:
    chosen = ci_select.select(["tests/test_not_there_yet.py"], real)[0]
    guards = ("test_ci_run_order_348", "test_ci_shard_budget_704", "test_ci_workers_790")
    assert [g for g in guards if f"tests/{g}.py" not in chosen] == []
