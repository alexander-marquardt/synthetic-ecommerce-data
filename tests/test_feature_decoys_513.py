"""A feature's text-match decoys are a module in ``feature_decoys/``, found by walking it (gen#513).

``decoy_rows.py`` (classes 1 to 7 and 9) and ``decoy_product_words.py`` (class 8) were registries:
each feature appended a row to a ``TABLE`` tuple and a ``Kind`` to a ``KINDS`` dict, so 3 and 4 of
the 18 open PRs on 2026-10-18 edited each. A module under ``prototypes/retail_drawings/
feature_decoys/`` now exposes ``KINDS`` (new kinds), ``decoy_rows(d)`` and ``word_rows(d)`` (rows
built with the table's own row maker) and the two tables read it. The first group of tests plants
a probe module in a throwaway directory that is put on the package path and asserts that the
tables, the ids and the kinds hold it with no edit to a shared file; the second holds the
contract. The first and the third run in a subprocess, so the import-time tables are built fresh.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RETAIL = ROOT / "prototypes" / "retail_drawings"

PROBE = """
from decoy_kind import Kind

KINDS = {
    "zz_cushion": Kind("Home", ("Home", "Soft Furnishings", "Cushions"), "Cushion", "cushion",
                       "Hearth & Table", 12.0),
}


def decoy_rows(d):
    return (
        d("ZZ01", "zz_cushion", "Red Probe Sofa Cushion", "A red cushion.", "Red", 2,
          "red probe", 500),
    )


def word_rows(d):
    return (
        d(901, "zz_cushion", "Probe Dress Cushion", "A cushion.", "Blue", "red dress", "dress",
          "category"),
    )
"""

REPORT = """
import json, sys
sys.path.insert(0, {retail!r})
import feature_decoys
feature_decoys.__path__.append({extra!r})
import decoy_rows, decoy_product_words as dpw
print(json.dumps({{
    "decoy_table": [d.code for d in decoy_rows.TABLE if d.code.startswith("ZZ")],
    "decoy_ids": sorted(i for i in decoy_rows.IDS if "ZZ" in i),
    "decoy_by_id": sorted(i for i in decoy_rows.BY_ID if "ZZ" in i),
    "decoy_docs": sum(1 for doc in decoy_rows.docs() if "Probe" in doc.get("title", "")),
    "word_table": [r.code for r in dpw.TABLE if r.code == "DY901"],
    "word_ids": sorted(i for i in dpw.IDS if i.endswith("DY901")),
    "word_by_id": sorted(i for i in dpw.BY_ID if i.endswith("DY901")),
    "kind_in_both": ["zz_cushion" in decoy_rows.KINDS, "zz_cushion" in dpw.KINDS],
}}))
"""


def _report(tmp_path: Path, modules: dict[str, str]) -> subprocess.CompletedProcess[str]:
    extra = tmp_path / "extra"
    extra.mkdir()
    for name, text in modules.items():
        (extra / f"{name}.py").write_text(text, encoding="utf-8")
    code = REPORT.format(retail=str(RETAIL), extra=str(extra))
    return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)


def test_a_probe_module_reaches_both_tables_with_no_shared_file_edited(tmp_path):
    done = _report(tmp_path, {"zz_probe": PROBE})
    assert done.returncode == 0, done.stderr
    got = json.loads(done.stdout)
    assert got == {
        "decoy_table": ["ZZ01"],
        "decoy_ids": ["PLT-DZZ01"],
        "decoy_by_id": ["PLT-DZZ01"],
        "decoy_docs": 1,
        "word_table": ["DY901"],
        "word_ids": ["PLT-DY901"],
        "word_by_id": ["PLT-DY901"],
        "kind_in_both": [True, True],
    }


def test_two_modules_with_one_row_code_are_refused_naming_the_code(tmp_path):
    done = _report(tmp_path, {"zz_probe": PROBE, "zz_twin": PROBE.replace("zz_cushion", "zz_two")})
    assert done.returncode != 0
    assert "ZZ01" in done.stderr and "twice" in done.stderr


def test_a_module_whose_word_row_reuses_a_code_of_the_word_table_is_refused(tmp_path):
    clash = PROBE.replace("d(901,", "d(43,")
    done = _report(tmp_path, {"zz_probe": clash})
    assert done.returncode != 0
    assert "DY43" in done.stderr and "twice" in done.stderr


def test_a_module_whose_decoy_reuses_a_code_of_the_table_is_refused(tmp_path):
    clash = PROBE.replace('"ZZ01"', '"XS01"')
    done = _report(tmp_path, {"zz_probe": clash})
    assert done.returncode != 0
    assert "XS01" in done.stderr and "twice" in done.stderr


@pytest.fixture
def package(tmp_path, monkeypatch):
    """The package with its path replaced by an empty directory the test fills."""
    monkeypatch.syspath_prepend(str(RETAIL))
    import feature_decoys

    where = tmp_path / "pkg"
    where.mkdir()
    monkeypatch.setattr(feature_decoys, "__path__", [str(where)])
    for name in [n for n in sys.modules if n.startswith("feature_decoys.")]:
        monkeypatch.delitem(sys.modules, name)
    return feature_decoys, where


def _write(where: Path, name: str, text: str) -> None:
    (where / f"{name}.py").write_text(text, encoding="utf-8")


def test_modules_are_found_by_name_in_a_fixed_order(package):
    feature_decoys, where = package
    for name in ("zz_b", "zz_a"):
        _write(where, name, "def word_rows(d):\n    return ()\n")
    assert [m.__name__.rsplit(".", 1)[-1] for m in feature_decoys.modules()] == ["zz_a", "zz_b"]


def test_a_module_that_names_nothing_the_tables_read_is_refused_by_name(package):
    feature_decoys, where = package
    _write(where, "zz_empty", "X = 1\n")
    with pytest.raises(ValueError, match="zz_empty"):
        feature_decoys.modules()


def test_a_kind_declared_twice_is_refused_naming_it(package):
    feature_decoys, where = package
    kind = "KINDS = {'sofa': 1}\n"
    _write(where, "zz_dup", kind)
    with pytest.raises(ValueError, match="sofa"):
        feature_decoys.kinds({"sofa": object()})


def test_a_kind_declared_by_two_modules_is_refused_naming_them(package):
    feature_decoys, where = package
    _write(where, "zz_one", "KINDS = {'zz_k': 1}\n")
    _write(where, "zz_two", "KINDS = {'zz_k': 2}\n")
    with pytest.raises(ValueError, match="zz_k"):
        feature_decoys.kinds({})


def test_the_module_rows_are_built_with_the_maker_the_table_passes(package):
    feature_decoys, where = package
    _write(where, "zz_a", "def word_rows(d):\n    return (d(1), d(2))\n")
    _write(where, "zz_b", "def word_rows(d):\n    return (d(3),)\n")
    assert feature_decoys.word_rows(lambda n: n) == (1, 2, 3)
    assert feature_decoys.decoy_rows(lambda n: n) == ()


def test_a_module_kind_that_the_word_table_already_holds_is_refused_naming_it(tmp_path):
    clash = PROBE.replace("zz_cushion", "s_blockheel")
    done = _report(tmp_path, {"zz_probe": clash})
    assert done.returncode != 0
    assert "s_blockheel" in done.stderr and "NEW_KINDS" in done.stderr
