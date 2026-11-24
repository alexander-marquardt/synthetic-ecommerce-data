"""``scale.templates()`` is computed once per worker, and the copy is the computation (#1035).

``tests/templates_memo.py`` keeps the templates a test process computes and gives each caller a
list of its own. The tests that compare two ``scale.templates()`` results to prove the build
deterministic now compare two copies, so the claim is held here against another process, under
another hash seed.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest

import templates_memo
from synthetic_ecommerce_data.domains.retail import scale

REPO = Path(__file__).resolve().parent.parent

_COMPUTE = """
import json, sys
from synthetic_ecommerce_data.domains.retail import scale
for baseline in (True, False):
    print(json.dumps(scale.templates(baseline)))
"""


class _Source:
    """A stand-in for ``scale.templates``: one shared list per ``baseline``, and its calls."""

    def __init__(self) -> None:
        self.calls: list[bool] = []
        self.lists = {True: [{"title": "plain"}, {"title": "row"}], False: [{"title": "row"}]}

    def __call__(self, baseline: bool = True) -> list[dict]:
        self.calls.append(baseline)
        return self.lists[baseline]


def _memo(source: _Source):
    def templates(baseline: bool = True) -> list[dict]:
        return source(baseline)

    return templates_memo.memo(templates)


def test_the_memo_is_what_a_test_calls() -> None:
    """The guard of the saving: no edit is held in a plain test, and the memo is installed."""
    assert not templates_memo.patched()
    assert getattr(scale.templates, "is_memo", False), "conftest does not install the memo"


def test_the_copy_is_what_another_process_computes_under_another_hash_seed() -> None:
    seed = "1" if os.environ.get("PYTHONHASHSEED") != "1" else "2"
    done = subprocess.run(
        [sys.executable, "-c", _COMPUTE],
        capture_output=True,
        text=True,
        check=True,
        cwd=REPO,
        env={**os.environ, "PYTHONHASHSEED": seed},
    )
    plain, authored = done.stdout.splitlines()
    assert getattr(scale.templates, "is_memo", False)
    for _ in range(2):  # the computed list, then a copy of it
        assert json.dumps(scale.templates()) == plain
        assert json.dumps(scale.templates(baseline=False)) == authored


def test_each_baseline_is_computed_once() -> None:
    source = _Source()
    templates = _memo(source)
    for _ in range(3):
        assert len(templates()) == 2
        assert len(templates(baseline=False)) == 1
    assert source.calls == [True, False]


def test_an_edit_of_one_copy_is_not_seen_by_the_next() -> None:
    templates = _memo(_Source())
    for _ in range(2):  # the first call returns a copy too, not the list that is kept
        taken = templates()
        taken[0]["title"] = "edited"
        taken.append({"title": "added"})
    assert templates() == [{"title": "plain"}, {"title": "row"}]


class _Target:
    attribute = "kept"


def _edit(patch: pytest.MonkeyPatch, kind: str) -> None:
    if kind == "setattr":
        patch.setattr(_Target, "attribute", "edited")
    elif kind == "delattr":
        patch.delattr(_Target, "attribute")
    elif kind == "setitem":
        patch.setitem({"a": 1}, "a", 2)
    elif kind == "delitem":
        patch.delitem({"a": 1}, "a")
    else:
        patch.setenv("TEMPLATES_MEMO_1035", "1")


@pytest.mark.parametrize("kind", ["setattr", "delattr", "setitem", "delitem", "setenv"])
def test_an_edit_held_by_a_monkeypatch_computes_and_keeps_nothing(kind: str) -> None:
    source = _Source()
    templates = _memo(source)
    patch = pytest.MonkeyPatch()
    _edit(patch, kind)
    try:
        assert templates_memo.patched()
        source.lists[True] = [{"title": "patched"}]
        assert templates() == templates() == [{"title": "patched"}]
        assert source.calls == [True, True]
        source.lists[True] = [{"title": "plain"}]
    finally:
        patch.undo()
    assert not templates_memo.patched()
    assert templates() == templates() == [{"title": "plain"}]
    assert source.calls == [True, True, True]


def test_an_edit_outlives_the_undo_of_another_monkeypatch() -> None:
    first, second = pytest.MonkeyPatch(), pytest.MonkeyPatch()
    _edit(first, "setattr")
    _edit(second, "setitem")
    try:
        second.undo()
        assert templates_memo.patched(), "the first edit is still held"
    finally:
        first.undo()
        second.undo()
    assert not templates_memo.patched()


def test_an_edit_of_pytest_s_own_config_does_not_disable_the_memo(
    pytestconfig: pytest.Config,
) -> None:
    """The tmp_path plugin holds a Config edit for the whole session."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(pytestconfig, "_templates_memo_1035", 1, raising=False)
        assert pytestconfig._templates_memo_1035 == 1
        assert not templates_memo.patched()
        patch.setattr(_Target, "attribute", "edited")
        assert templates_memo.patched()


def test_the_memo_is_not_installed_over_a_patched_function_or_twice(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    real = getattr(scale.templates, "__wrapped__", None)
    assert real is not None and not getattr(real, "is_memo", False)
    installed = scale.templates
    templates_memo.install()
    assert scale.templates is installed, "a second install wraps the memo again"

    def stub(baseline: bool = True) -> list[dict]:
        return []

    monkeypatch.setattr(scale, "templates", stub)
    templates_memo.install()
    assert scale.templates is stub


def test_a_change_to_the_memo_selects_every_test() -> None:
    sys.path.insert(0, str(REPO / "scripts"))
    try:
        import ci_select  # noqa: PLC0415
    finally:
        sys.path.remove(str(REPO / "scripts"))
    assert "tests/templates_memo.py" in ci_select.FULL_RUN


def test_no_module_binds_the_function_past_the_memo() -> None:
    """``from ...scale import templates`` binds the function before the memo is installed."""
    name = re.compile(r"^\s*from\s+[\w.]*\bscale\s+import\b[^\n]*\btemplates\b", re.M)
    grouped = re.compile(r"^\s*from\s+[\w.]*\bscale\s+import\s*\([^)]*\btemplates\b", re.M)
    assert name.search("from synthetic_ecommerce_data.domains.retail.scale import templates")
    assert grouped.search("from .scale import (\n    build,\n    templates,\n)")
    found = [
        path.relative_to(REPO).as_posix()
        for top in ("src", "tests", "scripts")
        for path in sorted((REPO / top).rglob("*.py"))
        if name.search(text := path.read_text(encoding="utf-8")) or grouped.search(text)
    ]
    assert found == []
