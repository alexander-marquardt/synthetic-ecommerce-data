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

import decoy_product_words  # noqa: E402
import distractors  # noqa: E402
import export  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402
from breadth_rows import Row  # noqa: E402
from variants import cw  # noqa: E402

from synthetic_ecommerce_data.core.standard import check_catalog  # noqa: E402

TRACKSUIT_IDS = {f"BRD-TST{c}" for c in ("MFL", "MSH", "MHZ", "WFL", "WVL", "W3P", "BHD", "G3P")}
SHAMPOO_IDS = {"BRD-SHPARG", "BRD-SHPROS"}


# Example types the tests below use for a type that is NOT registered. A real type added in its own
# spec file must never take one of these names, or it reds tests its writer did not touch.
SPECIMEN_KAFTAN = ("Clothing", "Specimen Kaftan")
SPECIMEN_ANORAK = ("Clothing", "Specimen Anorak")
SPECIMEN_SERUM = ("Beauty", "Specimen Serum")
SPECIMENS = (SPECIMEN_KAFTAN, SPECIMEN_ANORAK, SPECIMEN_SERUM)


def _types(records: list[dict]) -> set[tuple[str, str]]:
    return {(str(r["department"][0]), str(r["product_type"])) for r in records}


def _scaffold(tmp_path: Path, kind: str, key: str, ptype: str = "Sample Thing"):
    out = tmp_path / kind
    out.mkdir(exist_ok=True)
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "new_type.py"), key, "--kind", kind,
         "--product-type", ptype, "--out", str(out)],
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
    assert type_registry.registration_problems(built) == []


def _outside_spec(templates: list[dict]) -> tuple[dict[str, list[str]], set[str]]:
    """Per spec key the rows registered outside it, and the decoy rows that sit outside one."""
    decoys = {f"PLT-{r.code}" for r in decoy_product_words.TABLE}  # the decoy rows, not the floor
    # the jeans belt (gen#422): a distractor that is a Belt on purpose, beside the Belt spec
    jeans = {d.doc["product_id"] for d in distractors.JEANS}
    stray: dict[str, list[str]] = {}
    out_of_spec: set[str] = set()
    for spec in type_registry.specs().values():
        own = type_registry.ids_of(spec)
        mine = [
            r["product_id"] for r in templates
            if (r["department"][0], r["product_type"]) == (spec.department, spec.product_type)
            and r["product_id"] not in own
            and r["product_id"] not in scale.DECOY_IDS  # gen#311 clones every apparel type
        ]  # fmt: skip
        # a class-8 product-word decoy (gen#326) is another type's title on purpose,
        # e.g. the black bike pump that stands in for "black pumps" (gen#368)
        out_of_spec |= {i for i in mine if i in decoys}
        stray[spec.key] = [i for i in mine if i not in decoys and i not in jeans]
    return stray, out_of_spec


def test_a_spec_type_has_no_row_outside_its_spec_file() -> None:
    stray, out_of_spec = _outside_spec(scale.templates(baseline=False))
    assert not any(stray.values()), f"rows registered outside their spec: {stray}"
    # the one decoy that shares a spec type's name: the black bike pump stands in for "black pumps"
    assert out_of_spec == {"PLT-DY37"}, out_of_spec


def test_a_floor_row_added_to_a_spec_type_is_a_stray_row() -> None:
    """The exemption is the decoy rows alone: an ordinary floor product is not one."""
    templates = scale.templates(baseline=False)
    pump = next(r for r in templates if r["product_id"] == "PLT-DY37")
    floor = next(r for r in decoy_product_words.FLOOR)
    planted = {**pump, "product_id": f"PLT-{floor.code}"}
    stray, _ = _outside_spec([*templates, planted])
    assert planted["product_id"] in sum(stray.values(), [])


@pytest.mark.parametrize("key", sorted(type_registry.specs()))
def test_a_spec_file_is_named_for_its_key_and_its_documents_meet_the_standard(key: str) -> None:
    spec = type_registry.specs()[key]
    assert spec.key == key
    assert (RETAIL / "type_specs" / f"{key}.py").is_file()
    docs = spec.docs()
    assert len(docs) == len(spec.rows) + len(spec.decoys)
    exempt = type_registry.text_match_decoy_ids(spec.department)  # classes 1 to 7 lack on purpose
    problems = check_catalog(
        [export.standard_document(d) for d in docs], one_class_per_key=True, text_exempt=exempt
    )
    assert problems == []


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
            good, decoys=(type_registry.Decoy(9, "q", "p", replace(row, code="DCYZZ")),)),
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
    exempt = type_registry.decoy_ids_of(spec)  # a decoy names a value of its own filter
    standard = [export.standard_document(d) for d in docs]
    assert check_catalog(standard, one_class_per_key=True, text_exempt=exempt) == []
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


# -- a real type enters the live registry (the review of #358, blocking 1) -----------------------


def _census():
    """The gen#311 census tests, loaded by path: their functions are called on a patched build."""
    path = ROOT / "tests" / "test_retail_apparel_decoys_311.py"
    mod_spec = importlib.util.spec_from_file_location("census_311", path)
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return mod


def _real_types(tmp_path: Path) -> dict[str, type_registry.TypeSpec]:
    """A scaffolded clothing type (a specimen Kaftan, in a leaf of its own) and a scaffolded
    beauty type, as the quick path writes them and a writer edits only the leaf."""
    _, kaftan = _scaffold(tmp_path, "clothing", "specimen_kaftan", "Specimen Kaftan")
    row = replace(kaftan.rows[0], path=("Womens", "Tops", "Specimen Kaftans"))
    kaftan = replace(kaftan, rows=(row,))
    _, beauty = _scaffold(tmp_path, "beauty", "serum_specimen", SPECIMEN_SERUM[1])
    return {"specimen_kaftan": kaftan, "serum_specimen": beauty}


def _register(monkeypatch: pytest.MonkeyPatch, added: dict[str, type_registry.TypeSpec]) -> None:
    """Put ``added`` into the live registry: the specs of the tree plus these."""
    live = type_registry.specs()
    monkeypatch.setattr(type_registry, "specs", lambda: dict(sorted({**live, **added}.items())))


def test_a_real_scaffolded_clothing_and_beauty_type_pass_the_apparel_census(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The done-when of gen#351: a clothing type is ONE file. The type enters the live registry
    (a patched ``specs()``) and the census of gen#311 runs on the build that results."""
    census = _census()
    added = _real_types(tmp_path)
    _register(monkeypatch, added)
    import decoy_apparel as da

    plain = scale.templates(baseline=False)
    full = scale.templates()
    census.test_every_clothing_footwear_and_lingerie_type_is_planned(plain)
    rows = da.build([d for d in plain if d["product_id"] not in da.IDS])
    by_id = {d["product_id"]: d for d in plain}
    census.test_every_type_has_three_decoys_per_class_in_the_built_catalog(rows, by_id)
    census.test_each_decoys_fields_contradict_its_misleading_word(rows, by_id)
    mine = {r.pid for r in rows if r.product_type == "Specimen Kaftan"}
    assert len(mine) >= 21 and mine <= da.IDS
    assert not any(r.product_type == SPECIMEN_SERUM[1] for r in rows)
    table = da.table_markdown(rows)
    assert all(pid in table for pid in mine)
    now = {d["product_id"]: d for d in full}
    assert all(now[i] == by_id[i] for i in da.IDS), "a decoy was color-completed"
    ids = [d["product_id"] for d in full]
    assert len(ids) == len(set(ids))


def test_a_clothing_spec_with_no_apparel_plan_or_exemption_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import decoy_apparel as da

    _, kaftan = _scaffold(tmp_path, "clothing", "specimen_kaftan", "Specimen Kaftan")
    bare = replace(kaftan, apparel=None, apparel_exempt="")
    _register(monkeypatch, {"specimen_kaftan": bare})
    with pytest.raises(type_registry.SpecError, match="apparel"):
        _ = da.TYPES


def test_an_exempt_clothing_spec_carries_a_reason_and_no_decoys(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import decoy_apparel as da

    _, kaftan = _scaffold(tmp_path, "clothing", "specimen_kaftan", "Specimen Kaftan")
    exempt = replace(kaftan, apparel=None, apparel_exempt="a costume, not a garment")
    _register(monkeypatch, {"specimen_kaftan": exempt})
    assert da.EXEMPT.get("Specimen Kaftan") == "a costume, not a garment"
    assert "Specimen Kaftan" not in {t.product_type for t in da.TYPES}


def test_adding_a_spec_type_moves_no_other_decoy_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A spec type is numbered by its key, never by its place in the plan: adding one that sorts
    before another moves no decoy id."""
    import decoy_apparel as da

    before = da.IDS
    added = _real_types(tmp_path)
    _register(monkeypatch, added)
    with_kaftan = da.IDS
    assert before < with_kaftan
    by_key = "PLT-DSSPECIMEN_KAFTAN"
    assert any(i.startswith(by_key) for i in with_kaftan), "a spec type is numbered by its key"
    _, anorak = _scaffold(tmp_path, "clothing", "specimen_anorak", "Specimen Anorak")
    _register(monkeypatch, {"specimen_anorak": anorak})
    assert with_kaftan < da.IDS, "adding a type that sorts first moved a decoy id"
    assert {i for i in da.IDS if i.startswith(by_key)} == {
        i for i in with_kaftan if i.startswith(by_key)
    }


def test_a_type_planned_twice_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """Tracksuit is planned in ``decoy_apparel``; its spec cannot plan it a second time."""
    import decoy_apparel as da

    twice = replace(type_registry.specs()["tracksuit"], apparel=type_registry.ApparelPlan())
    _register(monkeypatch, {"tracksuit": twice})
    with pytest.raises(type_registry.SpecError, match="already planned"):
        _ = da.TYPES


@pytest.mark.parametrize("kind", ["clothing", "beauty"])
def test_the_scaffold_output_passes_ruff(tmp_path: Path, kind: str) -> None:
    path, _ = _scaffold(tmp_path, kind, f"sample_{kind}")
    run = subprocess.run(
        [sys.executable, "-m", "ruff", "check", "--config", str(ROOT / "pyproject.toml"),
         str(path)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stdout + run.stderr


@pytest.mark.parametrize("kind", ["clothing", "beauty"])
def test_the_scaffold_output_is_formatted(tmp_path: Path, kind: str) -> None:
    path, _ = _scaffold(tmp_path, kind, f"sample_{kind}")
    run = subprocess.run(
        [sys.executable, "-m", "ruff", "format", "--check", "--config",
         str(ROOT / "pyproject.toml"), str(path)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stdout + run.stderr


_PLAN = type_registry.ApparelPlan
_APPAREL_BAD = {  # name -> (the department of the base spec, the fields it declares)
    "a plan and an exemption": ("Clothing", dict(apparel=_PLAN(), apparel_exempt="a costume")),
    "a plan on a beauty type": ("Beauty", dict(apparel=_PLAN())),
    "an exemption on a beauty type": ("Beauty", dict(apparel_exempt="why")),
    "fewer than three decoys per class": ("Clothing", dict(apparel=_PLAN(per_class=2))),
    "an unknown word family": ("Clothing", dict(apparel=_PLAN(family="z"))),
}


def _base(department: str) -> type_registry.TypeSpec:
    good = _good()
    if department == "Beauty":
        return good
    row = replace(
        good.rows[0], department="Clothing", product_type="Specimen Kaftan", brand="Larkmoor",
        path=("Womens", "Tops", "Specimen Kaftans"),
    )  # fmt: skip
    return replace(good, department="Clothing", product_type="Specimen Kaftan", rows=(row,))


@pytest.mark.parametrize("name", sorted(_APPAREL_BAD))
def test_validate_refuses_a_malformed_apparel_declaration(name: str) -> None:
    department, fields = _APPAREL_BAD[name]
    with pytest.raises(type_registry.SpecError, match="apparel"):
        type_registry.validate(replace(_base(department), **fields))


def test_no_specimen_type_name_is_a_registered_or_built_type() -> None:
    """A specimen name is an example of an unregistered type; a real type with that name would red
    the tests that patch it in (the review of #358, Hair Serum). Held against the live registry
    and the live build, so a new type's own spec file cannot collide."""
    registered = {(sp.department, sp.product_type) for sp in type_registry.specs().values()}
    built = _types(scale.templates(baseline=False))
    taken = [x for x in SPECIMENS if x in registered or x in built]
    assert not taken, f"a real type takes a specimen name, rename the specimen: {taken}"
    # the literal "Specimen" prefix keeps a catalog type from taking one by accident
    assert all(name.startswith("Specimen ") for _, name in SPECIMENS)


# -- the guard is pinned (the review of #358, blocking 3) ----------------------------------------


def test_a_type_registered_outside_a_spec_file_is_a_problem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    built = _types(scale.templates(baseline=False)) | {SPECIMEN_SERUM}
    problems = type_registry.registration_problems(built)
    assert len(problems) == 1 and SPECIMEN_SERUM[1] in problems[0], problems


def test_a_legacy_line_appended_for_a_new_type_is_a_problem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The bypass of the review: the type is built and its line is appended to the legacy list."""
    built = _types(scale.templates(baseline=False)) | {SPECIMEN_SERUM}
    legacy = type_registry.legacy_types() | {SPECIMEN_SERUM}
    monkeypatch.setattr(type_registry, "legacy_types", lambda: legacy)
    problems = type_registry.registration_problems(built)
    assert len(problems) == 1 and "ceiling" in problems[0], problems


def test_a_migrated_type_left_on_the_legacy_list_is_a_problem(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    built = _types(scale.templates(baseline=False))
    legacy = type_registry.legacy_types() | {("Beauty", "Shampoo")}
    monkeypatch.setattr(type_registry, "legacy_types", lambda: legacy)
    problems = type_registry.registration_problems(built)
    assert any("Shampoo" in p and "both" in p for p in problems), problems


def test_a_legacy_type_no_longer_built_is_a_problem() -> None:
    built = _types(scale.templates(baseline=False)) - {sorted(type_registry.legacy_types())[0]}
    problems = type_registry.registration_problems(built)
    assert any("no longer built" in p for p in problems), problems


def test_a_migration_lowers_the_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    """The ceiling is exact: a list shorter than it leaves room to append the difference."""
    built = _types(scale.templates(baseline=False))
    legacy = type_registry.legacy_types() - {sorted(type_registry.legacy_types())[0]}
    monkeypatch.setattr(type_registry, "legacy_types", lambda: legacy)
    problems = type_registry.registration_problems(built)
    assert any("lower LEGACY_CEILING" in p for p in problems), problems


# -- one product id belongs to one spec (the beauty half of the review of #358, blocking 1) ------


def _new_type_module():
    mod_spec = importlib.util.spec_from_file_location("new_type", ROOT / "scripts" / "new_type.py")
    mod = importlib.util.module_from_spec(mod_spec)
    mod_spec.loader.exec_module(mod)
    return mod


def test_the_registry_refuses_two_specs_that_build_one_product_id(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Scaffolds of specimen_kaftan and specimen_serum both cut their code to SPECIM: the build
    then held two BRD-SPECIM styles and failed far away, in main_colors, on a missing key."""
    files = {
        "specimen_kaftan": _scaffold_source("specimen_kaftan", "Specimen Kaftan"),
        "specimen_serum": _scaffold_source("specimen_serum", "Specimen Serum"),
    }
    match = "specimen_kaftan and specimen_serum both build BRD-SPECIM"
    with pytest.raises(type_registry.SpecError, match=match):
        _discover(tmp_path, monkeypatch, files)


def test_the_build_refuses_a_spec_id_that_a_legacy_row_already_uses(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A spec cannot see the rows still outside the registry: the build names the clash."""
    mine = {s.product_type for s in type_registry.specs().values()}
    taken = next(
        d["product_id"]
        for d in scale.templates(baseline=False)
        if d["product_type"] not in mine and d["product_id"].startswith("BRD-")
    )
    _, beauty = _scaffold(tmp_path, "beauty", "specimen_serum", "Specimen Serum")
    beauty = replace(beauty, rows=(replace(beauty.rows[0], code=taken.removeprefix("BRD-")),))
    _register(monkeypatch, {"serum_specimen": beauty})
    with pytest.raises(type_registry.SpecError, match=taken):
        scale.templates()


def test_the_scaffold_picks_a_code_no_registered_spec_uses() -> None:
    new_type = _new_type_module()
    taken = {"BRD-SAMPLE", "BRD-SAMPL2"}
    code = new_type.pick_code("sample_b", taken)
    assert f"BRD-{code}" not in taken and len(code) <= 6 and code.startswith("SAMPL"), code
    assert new_type.pick_code("sample_b", set()) == "SAMPLE"


def test_the_scaffold_of_a_key_that_cuts_to_a_live_code_writes_another(tmp_path: Path) -> None:
    live = sorted(type_registry.ids_of(type_registry.specs()["tracksuit"]))[0].removeprefix("BRD-")
    _, spec = _scaffold(tmp_path, "clothing", live.lower() + "_two", "Tracksuit Two")
    code = spec.rows[0].code
    used = {i for s in type_registry.specs().values() for i in type_registry.ids_of(s)}
    assert code != live and f"BRD-{code}" not in used, code


def test_the_scaffold_takes_the_code_it_is_given(tmp_path: Path) -> None:
    out = tmp_path / "coded"
    out.mkdir()
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "new_type.py"), "sample_c", "--kind", "beauty",
         "--product-type", "Sample C", "--code", "ABCXYZ", "--out", str(out)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 0, run.stdout + run.stderr
    assert 'code="ABCXYZ"' in (out / "sample_c.py").read_text(encoding="utf-8")


@pytest.mark.parametrize(
    ("code", "why"), [("abcxyz", "capitals"), ("AB", "too short"), ("TSTMFL", "in use")]
)
def test_the_scaffold_refuses_a_code_that_is_malformed_or_in_use(
    tmp_path: Path, code: str, why: str
) -> None:
    out = tmp_path / "refused"
    out.mkdir()
    run = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "new_type.py"), "sample_d", "--kind", "beauty",
         "--product-type", "Sample D", "--code", code, "--out", str(out)],
        capture_output=True, text=True, check=False, cwd=ROOT,
    )  # fmt: skip
    assert run.returncode == 2 and "new_type:" in run.stdout, (why, run.stdout + run.stderr)
    assert not list(out.iterdir()), "the scaffold wrote a file for a refused code"
