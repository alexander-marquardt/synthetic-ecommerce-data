"""Each shared file of gen#513's census has a new-file form that a feature's own file reaches.

The guard (``scripts/check_no_registry_append.py``) refuses the appended line; these tests build
the throwaway form a feature adds instead and assert the shared code finds it with nothing else
edited: a spec's parts, a module of real compounds, a page of a feature.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

import build_derived  # noqa: E402

import decoy_real_compounds  # noqa: E402
from synthetic_ecommerce_data.domains.retail import decoy_rows, details  # noqa: E402

PROBE_SPEC = """
from synthetic_ecommerce_data.domains.retail import details

details.register_parts("zz_probe_coat", {"hem": details.TORSO_HEM})
SPEC = None
"""

REPORT = """
import importlib, json, sys
from synthetic_ecommerce_data.domains.retail import details, type_specs
type_specs.__path__.append({extra!r})
importlib.import_module("synthetic_ecommerce_data.domains.retail.type_specs.zz_probe_coat")
print(json.dumps(details.parts_of("zz_probe_coat")))
"""


def test_a_spec_module_gives_its_shape_parts_with_no_line_in_details(tmp_path: Path) -> None:
    (tmp_path / "zz_probe_coat.py").write_text(PROBE_SPEC, encoding="utf-8")
    code = REPORT.format(extra=str(tmp_path))
    done = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert done.returncode == 0, done.stderr
    assert done.stdout.strip() == '["hem"]'


def test_a_shape_with_parts_is_refused_a_second_table() -> None:
    with pytest.raises(ValueError, match="raincoat"):
        details.register_parts("raincoat", {"hem": details.HEM})
    assert details.parts_of("raincoat") == ("hem",)


def test_a_real_compound_module_is_found_by_its_file(tmp_path: Path) -> None:
    (tmp_path / "zz_probe.py").write_text('COMPOUNDS = frozenset({"Probe Clogs"})\n')
    assert decoy_real_compounds.load(tmp_path, "planted_compounds") == {"Probe Clogs"}


def test_the_compound_modules_reach_the_test_that_reads_them() -> None:
    assert {"Running Tights", "Cycling Tights"} <= decoy_real_compounds.FEATURE_COMPOUNDS


def test_a_compound_module_that_names_none_is_refused_by_name(tmp_path: Path) -> None:
    (tmp_path / "zz_empty.py").write_text("NOTHING = 1\n")
    with pytest.raises(ValueError, match="zz_empty"):
        decoy_real_compounds.load(tmp_path, "planted_empty")


def _pages(root: Path, pages: dict[str, str]) -> None:
    for name, text in pages.items():
        path = root / "docs" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def test_a_new_feature_page_is_in_the_built_index_with_no_shared_file_edited(
    tmp_path: Path,
) -> None:
    _pages(tmp_path, {"retail-prototype/probe-999.md": "# A probe feature (gen#999)\n\nText.\n"})
    index = build_derived.feature_pages(tmp_path)
    assert "[A probe feature (gen#999)](retail-prototype/probe-999.md)" in index


def test_the_index_covers_every_feature_page_directory(tmp_path: Path) -> None:
    pages = {f"{d}/p-1.md": f"# Page of {d}\n" for d in build_derived.FEATURE_PAGE_DIRS}
    _pages(tmp_path, pages)
    index = build_derived.feature_pages(tmp_path)
    assert [name for name in pages if f"({name})" not in index] == []


def test_a_feature_page_with_no_heading_is_refused_by_name(tmp_path: Path) -> None:
    _pages(tmp_path, {"retail-prototype/bare-1.md": "No heading here.\n"})
    with pytest.raises(SystemExit, match="bare-1"):
        build_derived.feature_pages(tmp_path)


def test_the_real_pages_all_reach_the_index() -> None:
    index = build_derived.feature_pages(ROOT)
    for folder in build_derived.FEATURE_PAGE_DIRS:
        pages = sorted((ROOT / "docs" / folder).glob("*.md"))
        assert pages, folder
        assert [p.name for p in pages if f"({folder}/{p.name})" not in index] == []


def test_the_two_built_pages_are_outputs_of_the_derived_build() -> None:
    assert decoy_rows.TABLE_DOC in build_derived.OUTPUTS
    assert build_derived.FEATURE_PAGES in build_derived.OUTPUTS
