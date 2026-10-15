"""One declarative spec per retail product type (gen#351).

A type is one file under ``prototypes/retail_drawings/type_specs/``; :mod:`type_registry`
discovers it, and the scaled build, the figures and the tests read the registry, so adding a type
edits no wiring. These checks hold the registry's rules, the guard that no type is registered
anywhere else, the two migrated types (``tracksuit``, ``shampoo``) and the scaffold
(``scripts/new_type.py``) that writes a spec.
"""

from __future__ import annotations

import importlib.util
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402
from breadth_rows import Row  # noqa: E402
from variants import cw  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

TRACKSUIT_IDS = {f"BRD-TST{c}" for c in ("MFL", "MSH", "MHZ", "WFL", "WVL", "W3P", "BHD", "G3P")}
SHAMPOO_IDS = {"BRD-SHPARG", "BRD-SHPROS"}


def _types(records: list[dict]) -> set[tuple[str, str]]:
    return {(str(r["department"][0]), str(r["product_type"])) for r in records}


def _scaffold(tmp_path: Path, kind: str, key: str):
    out = tmp_path / kind
    out.mkdir()
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "new_type.py"), key, "--kind", kind,
         "--product-type", "Sample Thing", "--out", str(out)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stdout + run.stderr
    path = out / f"{key}.py"
    assert path.is_file(), run.stdout
    mod_spec = importlib.util.spec_from_file_location(f"scaffold_{key}", path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return path, mod.SPEC


def test_the_two_migrated_types_register_through_specs() -> None:
    specs = type_registry.specs()
    assert set(specs) >= {"tracksuit", "shampoo"}
    assert {f"BRD-{r.code}" for r in specs["tracksuit"].rows} == TRACKSUIT_IDS
    assert {f"BRD-{r.code}" for r in specs["shampoo"].rows} == SHAMPOO_IDS


def test_the_scaled_build_holds_each_spec_row_once() -> None:
    ids = [r["product_id"] for r in scale.templates()]
    assert len(ids) == len(set(ids))
    assert set(ids) >= (TRACKSUIT_IDS | SHAMPOO_IDS)


def test_a_spec_decides_whether_the_build_may_derive_from_its_rows() -> None:
    derivable = {r["product_id"] for r in scale.derivable(scale.templates())}
    assert not TRACKSUIT_IDS & derivable
    assert derivable >= SHAMPOO_IDS


def test_every_type_is_registered_through_a_spec_or_the_legacy_list() -> None:
    """The guard: a type in no spec file must be on the legacy list, which only shrinks."""
    built = _types(scale.templates(baseline=False))
    through_specs = {(s.department, s.product_type) for s in type_registry.specs().values()}
    legacy = type_registry.legacy_types()
    elsewhere = sorted(built - through_specs - legacy)
    assert not elsewhere, f"registered outside a spec file (use scripts/new_type.py): {elsewhere}"
    both = legacy & through_specs
    assert not both, f"migrated but still on the legacy list: {sorted(both)}"
    assert not legacy - built, f"on the legacy list but no longer built: {sorted(legacy - built)}"
    assert through_specs <= built


def test_a_spec_type_has_no_row_outside_its_spec_file() -> None:
    for spec in type_registry.specs().values():
        own = type_registry.ids_of(spec)
        stray = [
            r["product_id"] for r in scale.templates(baseline=False)
            if (r["department"][0], r["product_type"]) == (spec.department, spec.product_type)
            and r["product_id"] not in own
            and r["product_id"] not in scale.DECOY_IDS  # gen#311 clones every apparel type
        ]  # fmt: skip
        assert not stray, f"{spec.key}: rows registered outside its spec: {stray}"


@pytest.mark.parametrize("key", sorted(type_registry.specs()))
def test_a_spec_file_is_named_for_its_key_and_its_documents_meet_the_standard(key: str) -> None:
    spec = type_registry.specs()[key]
    assert spec.key == key
    assert (RETAIL / "type_specs" / f"{key}.py").is_file()
    docs = spec.docs()
    assert len(docs) == len(spec.rows) + len(spec.decoys)
    assert check_catalog([export.standard_document(d) for d in docs], one_class_per_key=True) == []


def _good() -> type_registry.TypeSpec:
    row = Row(
        "SHPTST", "Test Shampoo", "Mirefield Naturals", "Beauty",
        ("Beauty", "Hair Care", "Shampoo"), "Shampoo", 6.0, "bottle", "A test shampoo.",
        (cw("Amber", "#c98a2e"),),
        sizes=(("250ml", 6.0),), colorless=True,
    )  # fmt: skip
    return type_registry.TypeSpec("shampoo_test", "Beauty", "Shampoo", rows=(row,))


def _bad_specs() -> dict[str, type_registry.TypeSpec]:
    good = _good()
    row = good.rows[0]
    return {
        "key with a capital": replace(good, key="Shampoo"),
        "no rows": replace(good, rows=()),
        "row of another product type": replace(good, rows=(replace(row, product_type="Soap"),)),
        "row of another department": replace(good, rows=(replace(row, department="Home"),)),
        "duplicate row code": replace(good, rows=(row, row)),
        "brand with no owner": replace(good, rows=(replace(row, brand="Nobody & Sons"),)),
        "decoy of an unknown class": replace(
            good, decoys=(type_registry.Decoy(8, "q", "p", replace(row, code="DCYZZ")),)),
        "decoy sharing a row code": replace(
            good, decoys=(type_registry.Decoy(1, "q", "p", row),)),
    }  # fmt: skip


BAD = (
    "key with a capital",
    "no rows",
    "row of another product type",
    "row of another department",
    "duplicate row code",
    "brand with no owner",
    "decoy of an unknown class",
    "decoy sharing a row code",
)


@pytest.mark.parametrize("name", BAD)
def test_validate_refuses_a_malformed_spec(name: str) -> None:
    with pytest.raises(type_registry.SpecError):
        type_registry.validate(_bad_specs()[name])


def test_validate_accepts_the_registered_specs() -> None:
    for spec in type_registry.specs().values():
        type_registry.validate(spec)


def test_a_decoy_row_is_never_derivable_and_is_listed_for_the_color_skip() -> None:
    good = _good()
    decoy = type_registry.Decoy(1, "red shampoo", "color", replace(good.rows[0], code="DCYSHP"))
    spec = replace(good, decoys=(decoy,))
    assert "BRD-DCYSHP" in type_registry.decoy_ids_of(spec)
    assert "BRD-DCYSHP" in type_registry.ids_of(spec)
    assert [d["product_id"] for d in spec.docs()][-1] == "BRD-DCYSHP"


@pytest.mark.parametrize("kind", ["clothing", "beauty"])
def test_the_scaffold_writes_a_spec_that_validates_and_builds(tmp_path: Path, kind: str) -> None:
    path, spec = _scaffold(tmp_path, kind, f"sample_{kind}")
    assert spec.key == f"sample_{kind}"
    type_registry.validate(spec)
    docs = spec.docs()
    assert docs
    assert check_catalog([export.standard_document(d) for d in docs], one_class_per_key=True) == []
    again = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "new_type.py"), spec.key, "--kind", kind,
         "--product-type", "Sample Thing", "--out", str(path.parent)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert again.returncode != 0, "the scaffold overwrote an existing spec"


def test_the_scaffold_refuses_a_bad_key(tmp_path: Path) -> None:
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "new_type.py"), "Bad-Key", "--kind", "beauty",
         "--product-type", "Sample Thing", "--out", str(tmp_path)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 2
    assert not list(tmp_path.iterdir()), "the scaffold wrote a file for a bad key"


def _discover(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, files: dict[str, str]) -> dict:
    """Run the discovery over a package holding only ``files`` (module name -> source)."""
    for name, source in files.items():
        (tmp_path / f"{name}.py").write_text(source, encoding="utf-8")
    monkeypatch.setattr(type_registry.type_specs, "__path__", [str(tmp_path)])
    for name in files:
        monkeypatch.delitem(sys.modules, f"type_specs.{name}", raising=False)
    try:
        return type_registry.specs.__wrapped__()
    finally:
        for name in files:
            sys.modules.pop(f"type_specs.{name}", None)


def _scaffold_source(key: str, product_type: str) -> str:
    mod_spec = importlib.util.spec_from_file_location("new_type", ROOT / "scripts" / "new_type.py")
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return mod.render(key, "beauty", product_type)


def test_the_registry_refuses_a_spec_file_whose_key_is_not_its_name(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(type_registry.SpecError, match="name the file"):
        _discover(tmp_path, monkeypatch, {"other_name": _scaffold_source("sample_a", "Sample A")})


def test_the_registry_refuses_a_module_without_a_spec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    with pytest.raises(type_registry.SpecError, match="declares no SPEC"):
        _discover(tmp_path, monkeypatch, {"empty_one": "X = 1\n"})


def test_the_registry_refuses_two_specs_for_one_product_type(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    files = {
        "sample_a": _scaffold_source("sample_a", "Sample Thing"),
        "sample_b": _scaffold_source("sample_b", "Sample Thing").replace("SAMPLE", "OTHERB"),
    }
    with pytest.raises(type_registry.SpecError, match="both declare"):
        _discover(tmp_path, monkeypatch, files)


def test_a_derivable_spec_leaves_only_its_decoys_out_of_the_derivation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    good = _good()
    decoy = type_registry.Decoy(1, "red shampoo", "color", replace(good.rows[0], code="DCYSHP"))
    spec = replace(good, derivable=True, decoys=(decoy,))
    monkeypatch.setattr(type_registry, "specs", lambda: {spec.key: spec})
    assert type_registry.left_out_ids() == {"BRD-DCYSHP"}
    assert type_registry.decoy_ids() == {"BRD-DCYSHP"}
    assert type_registry.left_out_ids() == type_registry.decoy_ids_of(spec)
