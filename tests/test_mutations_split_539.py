"""The mutation bed is a directory of files found by glob, not one list (gen#539).

``scripts/mutation_check.py`` held 477 mutations in one list literal over 4,500 lines, so every
pull request that planted a defect edited the same file and an agent that wanted one row read
thousands of lines. The mutations now sit in ``scripts/mutations/<area>.py``, each exposing
``MUTATIONS``, and ``mutation_row.discover_mutations`` is the one door, beside the one that finds
the rows files (#506).
"""

from __future__ import annotations

import ast
import sys
import textwrap
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts"

sys.path.insert(0, str(SCRIPTS))
import mutation_row  # noqa: E402  (scripts/ is not a package)

#: The mutations that were inline in ``mutation_check.py`` when it was split. The bed may grow
#: and a row may be retired by editing its file; losing one in the move would drop this below it.
#: 477 less the five golden-catalog rows main moved to mutation_rows_golden_anchors_50.py (#50).
INLINE_BEFORE_THE_SPLIT = 472


def _mutations_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, **files: str) -> None:
    """A directory of fabricated mutation files, as ``mutation_row.HERE / "mutations"``."""
    folder = tmp_path / "mutations"
    folder.mkdir()
    for stem, body in files.items():
        (folder / f"{stem}.py").write_text(textwrap.dedent(body), encoding="utf-8")
    monkeypatch.setattr(mutation_row, "HERE", tmp_path)


_GOOD = """
    from mutation_row import Mutation
    MUTATIONS = [Mutation("{name}", "f.py", "old", "new", "tests/t.py -k x", "", "a property")]
"""


def test_a_new_mutations_file_is_found_with_no_other_edit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _mutations_dir(tmp_path, monkeypatch, one=_GOOD.format(name="a"), two=_GOOD.format(name="b"))
    found = mutation_row.discover_mutations()
    assert [m.name for m in found] == ["a", "b"]
    assert found[0].root == "src/synthetic_ecommerce_data"


@pytest.mark.parametrize(
    ("body", "complaint"),
    [
        ("X = 1\n", "no MUTATIONS list"),
        ("MUTATIONS = 3\n", "no MUTATIONS list"),
        ("MUTATIONS = [('a', 'f.py')]\n", "not a Mutation"),
    ],
    ids=["absent", "not-a-list", "wrong-element"],
)
def test_a_malformed_mutations_file_is_refused_by_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, body: str, complaint: str
) -> None:
    _mutations_dir(tmp_path, monkeypatch, bad=body)
    with pytest.raises(ValueError, match=rf"bad\.py.*{complaint}"):
        mutation_row.discover_mutations()


def test_two_mutations_files_cannot_share_a_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _mutations_dir(
        tmp_path, monkeypatch, one=_GOOD.format(name="same"), two=_GOOD.format(name="same")
    )
    with pytest.raises(ValueError, match="share the name 'same'"):
        mutation_row.discover_mutations()


def test_the_glob_finds_every_mutation_the_harness_used_to_list() -> None:
    found = mutation_row.discover_mutations()
    assert len(found) >= INLINE_BEFORE_THE_SPLIT
    files = sorted((SCRIPTS / "mutations").glob("*.py"))
    assert len(files) >= 5, "the bed is split by area, not parked in one file"


def test_the_harness_lists_no_mutation_itself() -> None:
    """``mutation_check.py`` builds nothing by hand: no ``Mutation(...)`` call stays in it."""
    tree = ast.parse((SCRIPTS / "mutation_check.py").read_text("utf-8"))
    calls = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "Mutation"
    ]
    assert not calls, f"mutation_check.py still builds mutations at lines {calls[:5]}"


def test_the_harness_is_small_enough_to_read() -> None:
    lines = (SCRIPTS / "mutation_check.py").read_text("utf-8").count("\n")
    assert lines < 400, f"mutation_check.py is {lines} lines; the mutations belong in mutations/"


def test_the_whole_bed_is_the_mutations_files_then_the_rows_files() -> None:
    whole = mutation_row.all_mutations()
    own = mutation_row.discover_mutations()
    rows = mutation_row.discover()
    assert len(whole) == len(own) + len(rows)
    assert [m.name for m in whole[: len(own)]] == [m.name for m in own]
    assert whole[len(own)].name == f"{rows[0][0]}: {rows[0][1].name}"
