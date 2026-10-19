"""A feature PR adds a file; it never appends a line to a shared registry (gen#513).

On 2026-10-18, 16 of the 21 open PRs conflicted with main. Once the rolled stats files stopped
being committed (#373), what conflicted was a set of registries that each feature appended one
entry to: an import line and an id set in ``scale.py``, a row and a kind in the decoy tables, a
line in ``legacy_types.txt``. ``scripts/check_no_registry_append.py`` (the ``no-derived-files`` job)
refuses a diff that nets a line of one of those shapes and names the new-file form that replaces
it. A registry is in its table only while it has such a form, so the check never refuses what has
no alternative. These tests plant the appended line in a throwaway repository, hold the table to
its own examples, and read the workflow and the guide that name the form.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yaml"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import check_no_registry_append as guard  # noqa: E402

RD = "prototypes/retail_drawings"
SCALE = f"{RD}/scale.py"
DECOY_ROWS = f"{RD}/decoy_rows.py"
WORDS = f"{RD}/decoy_product_words.py"
LEGACY = f"{RD}/type_specs/legacy_types.txt"
HARNESS = "scripts/mutation_check.py"

#: (registry file, the line a feature used to append there, a word of the new-file form refusal)
APPENDS = {
    "harness-import": (HARNESS, "import mutation_rows_probe_513  # noqa: E402", "mutation_rows_"),
    "harness-wrapper": (HARNESS, "    *_wrap(mutation_rows_probe_513.ROWS),", "mutation_rows_"),
    "scale-import": (SCALE, "import probe_rows  # noqa: E402", "type_specs"),
    "scale-ids": (SCALE, "PROBE_IDS = frozenset(r.code for r in probe_rows.ROWS)", "type_specs"),
    "legacy-line": (LEGACY, "Beauty|Probe Cream", "new_type.py"),
    "decoy-row": (
        DECOY_ROWS,
        '    _d("XZ01", "sofa", "Title", "Desc", "Red", 1, "red sofa", 720),',
        "feature_decoys",
    ),
    "decoy-kind": (
        DECOY_ROWS,
        '    "probe": Kind("Home", ("Home", "Soft"), "Cushion", "cushion", "Brand", 1.0),',
        "feature_decoys",
    ),
    "word-row": (
        WORDS,
        '    _s(99, "s_probe", "Title", "Desc", "Brown", "block", "Yoga Block"),',
        "feature_decoys",
    ),
    "decoy-import": (
        DECOY_ROWS, "from decoy_plural_rows import ROWS as PLURAL_ROWS", "feature_decoys"
    ),
    "decoy-splat": (
        DECOY_ROWS,
        "    *(_d(code, kind, title, desc, color, 9, plural, sold, ingredients=ing)",
        "feature_decoys",
    ),
    "word-table": (WORDS, "TABLE = (*TABLE, *_PROBE)", "feature_decoys"),
    "word-kinds": (WORDS, "NEW_KINDS.update(_PROBE_KINDS)", "feature_decoys"),
    "word-kind": (
        WORDS,
        '    "probe": Kind("Home", ("Home",), "Cushion", "cushion", "B", 1.0),',
        "feature_decoys",
    ),
    "word-d-open": (WORDS, "    _d(", "feature_decoys"),
}

#: The registry files as they stand on main, each with a row an edit may change.
BASE = {
    HARNESS: "import argparse\n\nMUTATIONS = []\n",
    SCALE: "import json  # noqa: E402\nimport foo_rows  # noqa: E402\n",
    LEGACY: "# header\nBeauty|Body Cream\n",
    DECOY_ROWS: 'TABLE = (\n    _d("XS01", "sofa", "Sofa", "Desc", "Blue", 1, "red sofa"),\n)\n',
    WORDS: 'TABLE = (\n    _s(43, "s_x", "Block Heel", "Desc", "Brown", "block", "Yoga"),\n)\n',
}


def _git(repo: Path, *args: str) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        capture_output=True,
        text=True,
    )  # fmt: skip
    assert done.returncode == 0, f"git {args}: {done.stderr}"
    return done.stdout.strip()


def _commit(repo: Path, message: str, files: dict[str, str]) -> str:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "--allow-empty", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


@pytest.fixture
def repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q", "-b", "main")
    base = _commit(root, "base", BASE)
    _git(root, "switch", "-q", "-c", "feature")
    return root, base


def _run(root: Path, base: str, capsys) -> tuple[int, str]:
    head = _git(root, "rev-parse", "HEAD")
    code = guard.main(["--root", str(root), "--base", base, "--head", head])
    return code, capsys.readouterr().out


def _append(root: Path, path: str, line: str, message: str = "feature") -> None:
    text = (root / path).read_text(encoding="utf-8")
    _commit(root, message, {path: text + line + "\n"})


@pytest.mark.parametrize("name", APPENDS)
def test_an_appended_registry_line_is_refused_and_names_the_new_file_form(repo, capsys, name):
    root, base = repo
    path, line, word = APPENDS[name]
    _append(root, path, line)
    code, out = _run(root, base, capsys)
    assert code == 1, f"{path}: {line!r} was let by"
    assert path in out
    assert word in out, f"the refusal does not name the new-file form ({word!r}):\n{out}"


def test_a_new_file_and_no_shared_line_is_let_by(repo, capsys):
    root, base = repo
    _commit(root, "feature", {f"{RD}/type_specs/probe.py": "SPEC = 1\n",
                              "scripts/mutation_rows_probe_513.py": "PREFIX = 'p'\n"})  # fmt: skip
    assert _run(root, base, capsys)[0] == 0


def test_the_hook_lines_of_the_new_file_form_are_not_an_append(repo, capsys):
    root, base = repo
    hooks = {
        DECOY_ROWS: [
            "KINDS = feature_decoys.kinds(KINDS)",
            "TABLE = (*TABLE, *feature_decoys.decoy_rows(_d))",
        ],
        WORDS: ["TABLE = (*TABLE, *feature_decoys.word_rows(_d))"],
    }
    _commit(root, "feature", {path: BASE[path] + "\n".join(lines) + "\n"
                              for path, lines in hooks.items()})  # fmt: skip
    code, out = _run(root, base, capsys)
    assert code == 0, out


def test_a_row_edited_in_place_is_not_an_append(repo, capsys):
    root, base = repo
    text = BASE[WORDS].replace("Block Heel", "Block Heel Shoes")
    _commit(root, "feature", {WORDS: text})
    assert _run(root, base, capsys)[0] == 0


def test_a_line_removed_is_not_an_append(repo, capsys):
    root, base = repo
    _commit(root, "migrate", {LEGACY: "# header\n"})
    assert _run(root, base, capsys)[0] == 0


def test_a_registry_line_replaced_by_another_is_not_an_append(repo, capsys):
    root, base = repo
    _commit(root, "migrate", {LEGACY: "# header\nBeauty|Body Lotion\n"})
    assert _run(root, base, capsys)[0] == 0


def test_every_append_in_one_diff_is_named(repo, capsys):
    root, base = repo
    _append(root, SCALE, "import probe_rows  # noqa: E402")
    _append(root, LEGACY, "Beauty|Probe Cream")
    code, out = _run(root, base, capsys)
    assert code == 1
    assert SCALE in out and LEGACY in out


def test_a_reasoned_trailer_on_the_tip_lets_an_append_by(repo, capsys):
    root, base = repo
    _append(root, SCALE, "import probe_rows  # noqa: E402",
            "feature\n\nRegistry-Append: a helper module, not a feature")  # fmt: skip
    assert _run(root, base, capsys)[0] == 0


def test_a_trailer_with_no_reason_does_not_let_an_append_by(repo, capsys):
    root, base = repo
    _append(root, SCALE, "import probe_rows  # noqa: E402", "feature\n\nRegistry-Append:")
    assert _run(root, base, capsys)[0] == 1


def test_a_trailer_on_an_earlier_commit_does_not_let_the_tip_by(repo, capsys):
    root, base = repo
    _append(root, SCALE, "import probe_rows  # noqa: E402",
            "feature\n\nRegistry-Append: first")  # fmt: skip
    _append(root, LEGACY, "Beauty|Probe Cream", "later")
    assert _run(root, base, capsys)[0] == 1


def test_the_table_holds_exactly_the_registries_that_have_a_new_file_form():
    assert {r.path for r in guard.REGISTRIES} == {path for path, _, _ in APPENDS.values()}


def test_every_registry_names_a_form_that_exists_and_matches_its_own_example():
    assert guard.REGISTRIES
    for reg in guard.REGISTRIES:
        assert (ROOT / reg.path).exists(), reg.path
        assert reg.form.strip(), reg.path
        assert reg.exists, f"{reg.path} names no path of its new-file form"
        for form_path in reg.exists:
            assert (ROOT / form_path).exists(), f"{reg.path}: the form {form_path} is not there"
        assert any(shape.search(reg.example) for shape in reg.shapes), (
            f"{reg.path}: the example {reg.example!r} matches none of its shapes"
        )


def test_no_current_registry_line_is_a_dead_shape():
    """A shape that matches no line of the planted appends is a pattern nobody exercises."""
    for reg in guard.REGISTRIES:
        planted = [line for path, line, _ in APPENDS.values() if path == reg.path]
        for shape in reg.shapes:
            assert any(shape.search(line) for line in planted), f"{reg.path}: {shape.pattern}"


def test_the_no_derived_files_job_runs_the_registry_guard():
    jobs = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]
    steps = jobs["no-derived-files"]["steps"]
    runs = " ".join(str(step.get("run", "")) for step in steps)
    assert "scripts/check_no_registry_append.py" in runs
    assert "--base" in runs and "--head" in runs


@pytest.mark.parametrize(
    "doc", ["docs/new-type-quick-path.md", "docs/adding-a-retail-type.md", "docs/adding-a-type.md"]
)
def test_the_guide_names_the_new_file_form_and_not_a_line_to_append(doc):
    text = (ROOT / doc).read_text(encoding="utf-8")
    assert "feature_decoys" in text or "check_no_registry_append" in text, doc
