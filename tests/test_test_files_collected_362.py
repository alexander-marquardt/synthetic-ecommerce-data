"""Every test file in the repository is a file CI collects (gen#362).

``prototypes/retail_drawings/test_*.py`` sat outside ``testpaths = ["tests"]``, so neither the
CI shards nor ``merge_pr.sh --local-ci`` ran them, and they went red on main without anyone
seeing it (history: the red tests were fixed on main by #548). This guard fails when a tracked
``test_*.py`` or ``*_test.py`` file is outside the paths pytest collects (``pyproject.toml``),
and when the planner, the selection or the shard plan does not reach a collected one.
"""

from __future__ import annotations

import importlib.util
import sys
import tomllib
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
RETAIL = "src/synthetic_ecommerce_data/domains/retail"
#: The drawing tests that sat beside the prototype, under ``tests/`` since the move (#125).
DRAWING_TESTS = (
    "tests/test_cups.py",
    "tests/test_footwear.py",
    "tests/test_house_styles.py",
    "tests/test_mattress_topper.py",
    "tests/test_motifs.py",
    "tests/test_real_classes.py",
    "tests/test_shape_honesty.py",
    "tests/test_signals_and_paths.py",
    "tests/test_styles.py",
    "tests/test_variants.py",
)


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules.setdefault(name, module)
    spec.loader.exec_module(module)
    return module


ci_select = _load("ci_select")
ci_shards = _load("ci_shards")


def _is_test_file(path: str) -> bool:
    name = Path(path).name
    return path.endswith(".py") and (name.startswith("test_") or name.endswith("_test.py"))


def _testpaths() -> list[str]:
    config = tomllib.loads((REPO / "pyproject.toml").read_text(encoding="utf-8"))
    return list(config["tool"]["pytest"]["ini_options"]["testpaths"])


def test_no_test_file_sits_outside_the_paths_pytest_collects() -> None:
    paths = _testpaths()
    outside = [
        p
        for p in ci_select.tracked_files(REPO)
        if _is_test_file(p) and not any(p.startswith(f"{root.rstrip('/')}/") for root in paths)
    ]
    assert outside == [], (
        "these test files are outside testpaths, so CI never runs them; move them under a "
        f"collected path or add their directory to testpaths in pyproject.toml: {outside}"
    )


def test_the_planner_deals_every_retail_drawing_test_file() -> None:
    assert not sorted((REPO / RETAIL).rglob("test_*.py")), "a test file sits in the package"
    assert set(DRAWING_TESTS) <= set(ci_shards.collected_test_files())


def test_a_change_to_a_drawing_module_selects_the_drawing_test_that_imports_it() -> None:
    chosen, reasons = ci_select.select([f"{RETAIL}/house_styles.py"], ci_select.Tree(REPO))
    assert "tests/test_house_styles.py" in chosen, reasons


def test_a_drawing_test_file_is_a_test_file_of_the_selection() -> None:
    assert ci_select.is_test_file("tests/test_house_styles.py")
    assert not ci_select.is_test_file(f"{RETAIL}/house_styles.py")


def test_no_doc_says_pytest_collects_only_tests_and_no_second_drawing_runner_exists() -> None:
    stale = [
        p.relative_to(REPO).as_posix()
        for p in sorted((REPO / "docs").glob("*.md"))
        if "collects only `tests/`" in p.read_text(encoding="utf-8")
        or "does not collect `prototypes/`" in p.read_text(encoding="utf-8")
    ]
    assert not stale, stale
    assert not (REPO / "tests" / "test_prototype_tests_collected_486.py").exists()
