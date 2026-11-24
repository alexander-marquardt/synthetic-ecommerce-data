"""What a shard's plan costs, and the edges of an import by computed name (#1035).

* A shard plans once: the ``select`` step saves its plan and the ``Tests`` step reads it.
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

import pinned
from test_ci_select_495 import _picked, _tests_job_step, _tree, _write, ci_select

# --- a plan is made once a shard ------------------------------------------------------------

PLANNER = """
import sys
from pathlib import Path
if "--plan" in sys.argv:
    made = Path("plans")
    made.write_text(made.read_text() + "x" if made.is_file() else "x")
    print("shards=3")
    print("tests/test_a.py")
"""
NO_FILE_PLANNER = PLANNER.replace('    print("tests/test_a.py")\n', "")
RUNNER = "import sys\nopen('ran', 'w').write(' '.join(sys.argv[1:]))\n"


def _steps(tmp_path: Path, planner: str, runner_temp: Path | None, *steps: str) -> None:
    """Run the named steps of the tests job, in order, with ``planner`` as the planner script."""
    _write(tmp_path, {"scripts/ci_shards.py": planner, "scripts/ci_run_pytest.py": RUNNER})
    env = {k: v for k, v in os.environ.items() if k not in ("RUNNER_TEMP", "GITHUB_OUTPUT")}
    if runner_temp is not None:
        runner_temp.mkdir()
        env["RUNNER_TEMP"] = str(runner_temp)
    for step in steps:
        script = re.sub(r"\$\{\{.*?\}\}", "1", _tests_job_step(step))
        done = subprocess.run(
            ["bash", "-e", "-c", script], cwd=tmp_path, capture_output=True, text=True, env=env
        )
        assert done.returncode == 0, f"{step}: {done.stdout}{done.stderr}"


def test_the_tests_step_reads_the_plan_the_select_step_made(tmp_path: Path) -> None:
    _steps(tmp_path, PLANNER, tmp_path / "temp", "select", "Tests")
    assert (tmp_path / "ran").read_text() == "-- uv run --locked pytest tests/test_a.py"
    assert (tmp_path / "plans").read_text() == "x", "the shard planned twice"


def test_a_saved_plan_that_holds_no_file_runs_no_test(tmp_path: Path) -> None:
    _steps(tmp_path, NO_FILE_PLANNER, tmp_path / "temp", "select", "Tests")
    assert not (tmp_path / "ran").exists()
    assert (tmp_path / "plans").read_text() == "x", "the shard planned twice"


def test_a_tests_step_with_no_saved_plan_makes_its_own(tmp_path: Path) -> None:
    """``merge_pr.sh --local-ci`` runs the steps with no RUNNER_TEMP."""
    _steps(tmp_path, PLANNER, None, "select", "Tests")
    assert (tmp_path / "plans").read_text() == "xx"
    assert (tmp_path / "ran").read_text() == "-- uv run --locked pytest tests/test_a.py"
    (tmp_path / "ran").unlink()
    _steps(tmp_path, PLANNER, tmp_path / "temp", "Tests")
    assert (tmp_path / "ran").exists()


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
