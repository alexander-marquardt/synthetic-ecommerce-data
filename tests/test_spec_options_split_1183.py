"""The spec-options rows are one module per family, not one dict in the gen#413 test (gen#1183).

``tests/test_retail_type_options_413.py`` held ``MOVED`` (spec key -> the options it declares)
as one dict, and every type that added an option appended a row there: 3 PRs conflicted on it in
7 days. ``tests/spec_options/`` holds the rows by family and merges them by walking the package.
"""

from __future__ import annotations

import importlib
import re
from pathlib import Path

import pytest

import spec_options

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "tests" / "spec_options"
TEST_413 = ROOT / "tests" / "test_retail_type_options_413.py"


def test_the_gen413_test_holds_no_spec_row() -> None:
    rows = re.findall(r'^\s+"[a-z][a-z0-9_]*":\s*\[', TEST_413.read_text(encoding="utf-8"), re.M)
    assert rows == []


def test_the_rows_are_in_modules_by_family() -> None:
    families = sorted(p.stem for p in PACKAGE.glob("*.py") if not p.stem.startswith("_"))
    assert len(families) >= 10, "tests/spec_options/<family>.py"
    modules = [importlib.import_module(f"spec_options.{f}") for f in families]
    assert sum(len(m.MOVED) for m in modules) == len(spec_options.MOVED)


def _family_package(tmp_path: Path, name: str, **families: str) -> Path:
    folder = tmp_path / name
    folder.mkdir()
    (folder / "__init__.py").write_text("", encoding="utf-8")
    (folder / "_shared.py").write_text("MOVED = {'ignored': []}\n", encoding="utf-8")
    for family, body in families.items():
        (folder / f"{family}.py").write_text(f"MOVED = {body}\n", encoding="utf-8")
    return folder


def test_the_rows_of_two_families_merge_and_a_private_module_is_no_family(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = _family_package(
        tmp_path, "planted_family_merge_1183", a="{'kite': [1]}", b="{'sled': [2]}"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    assert spec_options._load(folder, "planted_family_merge_1183") == {"kite": [1], "sled": [2]}


def test_a_spec_two_families_declare_raises_and_names_both(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    folder = _family_package(
        tmp_path, "planted_family_twice_1183", a="{'kite': [1]}", b="{'kite': [1]}"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    with pytest.raises(ValueError, match=r"'kite': declared by both a and b"):
        spec_options._load(folder, "planted_family_twice_1183")
