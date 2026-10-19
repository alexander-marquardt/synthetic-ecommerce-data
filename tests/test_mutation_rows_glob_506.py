"""A mutant-row file is found by glob, so a pull request that adds one edits no shared line (#506).

Before this, ``scripts/mutation_check.py`` imported every ``mutation_rows_*.py`` at the top and
wrapped each in a per-file line of the one ``MUTATIONS`` list (and ``mutation_rows_garden_hose.ALL``
did the same for fourteen more), so every pull request that added a row edited the same lines and
conflicted with the next. The row shape is now one :class:`mutation_row.Row`, a file exposes
``PREFIX`` and ``rows()``, and ``mutation_row.discover`` is the one door.
"""

from __future__ import annotations

import ast
import importlib.util
import re
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

sys.path.insert(0, str(SCRIPTS))
import mutation_row  # noqa: E402  (scripts/ is not a package)

_ROWS_FILE = re.compile(r"mutation_rows_\w+(\.py)?")


def _harness():
    spec = importlib.util.spec_from_file_location("mutation_check", SCRIPTS / "mutation_check.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _names_a_rows_file(tree: ast.AST) -> list[str]:
    """Every place a module names a rows file: an import, a bound name, an attribute, a string."""
    docstrings = {
        id(node.body[0].value)
        for node in ast.walk(tree)
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef))
        and node.body
        and isinstance(node.body[0], ast.Expr)
        and isinstance(node.body[0].value, ast.Constant)
    }
    hits: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            hits += [a.name for a in node.names if a.name.startswith("mutation_rows_")]
        elif isinstance(node, ast.ImportFrom) and (node.module or "").startswith("mutation_rows_"):
            hits.append(node.module or "")
        elif isinstance(node, ast.Name) and node.id.startswith("mutation_rows_"):
            hits.append(node.id)
        elif (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and id(node) not in docstrings
            and _ROWS_FILE.fullmatch(node.value)
        ):
            hits.append(node.value)
    return hits


def test_the_scripts_name_no_rows_file() -> None:
    """The guard: no script imports or lists a rows file by name, whatever the shared list is.

    ``mutation_check.py`` once imported thirty-three of them and ``mutation_rows_garden_hose.ALL``
    fourteen more. A new entry in a list like that is the conflict this issue removes."""
    named = {
        path.name: hits
        for path in sorted(SCRIPTS.glob("*.py"))
        if (hits := _names_a_rows_file(ast.parse(path.read_text("utf-8"))))
    }
    assert not named, f"these scripts name a rows file; the glob finds them: {named}"


def test_the_guard_sees_an_import_a_name_and_a_string() -> None:
    tree = ast.parse(
        textwrap.dedent(
            '''
            """mutation_rows_in_a_docstring"""
            import mutation_rows_a
            from mutation_rows_b import ROWS
            x = mutation_rows_c.ROWS
            y = "mutation_rows_d.py"
            z = "no rows file here"
            '''
        )
    )
    assert sorted(_names_a_rows_file(tree)) == [
        "mutation_rows_a",
        "mutation_rows_b",
        "mutation_rows_c",
        "mutation_rows_d.py",
    ]


def test_every_rows_file_is_found_by_the_glob() -> None:
    files = [p.stem for p in SCRIPTS.glob("mutation_rows_*.py")]
    assert len(files) > 40
    found = mutation_row.discover()
    assert len({prefix for prefix, _ in found}) == len(files), (
        "each rows file has its own prefix and every one of them yielded rows"
    )


def test_the_harness_plants_exactly_the_rows_the_glob_finds() -> None:
    harness = _harness()
    planted = {m.name for m in harness.MUTATIONS}
    found = mutation_row.discover()
    assert len(found) > 400
    missing = [
        f"{prefix}: {row.name}" for prefix, row in found if f"{prefix}: {row.name}" not in planted
    ]
    assert not missing, f"the harness leaves out rows the glob finds: {missing[:5]}"


def _rows_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **files: str) -> None:
    """A directory of fabricated rows files, on ``sys.path`` and in ``mutation_row.HERE``."""
    for stem, body in files.items():
        (tmp_path / f"{stem}.py").write_text(textwrap.dedent(body), encoding="utf-8")
    monkeypatch.setattr(mutation_row, "HERE", tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))
    for stem in files:
        monkeypatch.delitem(sys.modules, stem, raising=False)


_GOOD = """
    from mutation_row import Row
    PREFIX = "{prefix}"
    def rows():
        return [Row("a defect", "f.py", "old", "new", "tests/t.py -k x", "a property")]
"""


def test_a_new_rows_file_is_found_with_no_other_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _rows_dir(tmp_path, monkeypatch, mutation_rows_fake_one=_GOOD.format(prefix="fake one"))
    [(prefix, row)] = mutation_row.discover()
    assert (prefix, row.name, row.root, row.direction) == (
        "fake one",
        "a defect",
        "src/synthetic_ecommerce_data",
        "",
    )


@pytest.mark.parametrize(
    ("body", "complaint"),
    [
        ("def rows():\n    return []\n", "no PREFIX"),
        ('PREFIX = "x"\n', "no rows()"),
        ('PREFIX = "x"\ndef rows():\n    return [("a", "b")]\n', "not a Row"),
    ],
    ids=["no-prefix", "no-rows", "a-bare-tuple"],
)
def test_a_rows_file_that_breaks_the_contract_is_named(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str, complaint: str
) -> None:
    _rows_dir(tmp_path, monkeypatch, mutation_rows_fake_bad=body)
    with pytest.raises(ValueError, match=rf"mutation_rows_fake_bad\.py.*{complaint}"):
        mutation_row.discover()


def test_two_rows_files_cannot_share_a_prefix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _rows_dir(
        tmp_path,
        monkeypatch,
        mutation_rows_fake_a=_GOOD.format(prefix="same"),
        mutation_rows_fake_b=_GOOD.format(prefix="same"),
    )
    with pytest.raises(ValueError, match="share the prefix 'same'"):
        mutation_row.discover()
