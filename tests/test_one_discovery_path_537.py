"""One discovery path for product types (gen#537).

A type is one ``type_specs/<key>.py`` and the registry walk finds it: no legacy list, no ceiling,
and no id set in ``scale.py`` that a person types. The 293 types that once sat on
``legacy_types.txt`` are specs too, each naming the shared row modules that still hold its rows
(:class:`type_registry.Home`); ``scale.derivable`` reads which of them it leaves out from those
homes. The byte-identity of the ceiling build against the base is the migration's oracle and is
shown in the pull request; these checks hold the result.
"""

from __future__ import annotations

import ast
import importlib
import re
import sys
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "prototypes" / "retail_drawings"
for _p in (str(RETAIL), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import check_no_registry_append as guard  # noqa: E402
import scale  # noqa: E402
import type_registry  # noqa: E402
import type_specs  # noqa: E402

PLANTED_KEY = "zz_planted_537"
PLANTED = textwrap.dedent(
    """
    from type_registry import Row, TypeSpec, a, cw

    SPEC = TypeSpec(
        key="zz_planted_537",
        department="Beauty",
        product_type="Planted Specimen Tonic",
        derivable={derivable},
        rows=(
            Row("ZZPL01", "Planted Specimen Tonic", "Mirefield Naturals", "Beauty",
                ("Beauty", "Hair Care", "Planted Specimen Tonic"), "Planted Specimen Tonic",
                6.0, "bottle", "A tonic planted by the test of gen#537.",
                (cw("Amber", "#c98a2e", "solid", "#ffffff"),),
                (a("hair_type", "Hair type", "Dry"),), (), "Tonic", colorless=True),
        ),
    )
    """
)


def _problem(spec: type_registry.TypeSpec) -> str | None:
    try:
        type_registry.validate(spec)
    except type_registry.SpecError as exc:
        return str(exc)
    return None


def _built_types() -> set[tuple[str, str]]:
    return {(str(r["department"][0]), str(r["product_type"])) for r in scale.templates(False)}


def test_no_legacy_list_or_ceiling_remains() -> None:
    """Done when: ``legacy_types.txt`` and ``LEGACY_CEILING`` are gone."""
    assert not (RETAIL / "type_specs" / "legacy_types.txt").exists()
    assert not hasattr(type_registry, "LEGACY_CEILING")
    assert not hasattr(type_registry, "legacy_types")
    assert not hasattr(type_registry, "LEGACY_FILE")


def test_every_built_type_is_a_spec() -> None:
    """Every ``(department, product type)`` of the ceiling templates is a spec's."""
    through = {(s.department, s.product_type) for s in type_registry.specs().values()}
    assert sorted(_built_types() - through) == []
    assert type_registry.registration_problems(_built_types()) == []


def test_a_built_type_no_spec_declares_is_a_problem() -> None:
    problems = type_registry.registration_problems(_built_types() | {("Beauty", "Probe Cream")})
    assert any("Probe Cream" in p and "spec" in p for p in problems), problems


def test_a_spec_type_that_is_not_built_is_a_problem() -> None:
    problems = type_registry.registration_problems(set())
    assert any("not built" in p for p in problems), problems


def test_scale_holds_no_id_set_that_a_person_types() -> None:
    """The 27 hand-imported sets are derived: ``scale.py`` assigns no ``*_IDS`` but the text
    exemption, which unions module-level decoy sets."""
    tree = ast.parse((RETAIL / "scale.py").read_text(encoding="utf-8"))
    names = {
        t.id
        for node in tree.body
        if isinstance(node, ast.Assign)
        for t in node.targets
        if isinstance(t, ast.Name) and t.id.endswith("_IDS")
    }
    assert names <= {"DECOY_IDS"}, sorted(names)


def test_a_home_must_be_a_source_the_build_reads() -> None:
    spec = type_registry.TypeSpec(
        "probe", "Beauty", "Probe Cream", rows=(),
        homes=(type_registry.Home("no_such_rows", False),),
    )  # fmt: skip
    problem = _problem(spec)
    assert problem is not None and "no_such_rows" in problem and "source" in problem, problem


def test_a_spec_may_hold_homes_in_place_of_rows() -> None:
    home = type_registry.Home("breadth_rows", True)
    spec = type_registry.TypeSpec("probe", "Beauty", "Probe Cream", rows=(), homes=(home,))
    assert _problem(spec) is None
    assert spec.docs() == [] and type_registry.ids_of(spec) == frozenset()
    bare = type_registry.TypeSpec("probe", "Beauty", "Probe Cream", rows=())
    assert _problem(bare) is not None  # no rows and no home: nothing to build


def _source_docs(name: str) -> list[dict]:
    if name == "samples":
        return [d for recs in scale.samples().values() for d in recs]
    if name == "grocery":
        return scale.grocery.build()
    return importlib.import_module(name).docs()


def test_every_row_of_a_shared_source_is_homed_by_a_spec() -> None:
    """A row appended to a shared row module for a type no spec names fails here, so a type
    cannot be registered anywhere but a spec; and a home names a source that holds the type."""
    assert type_registry.HOME_SOURCES, "no source is declared"
    owned = {i for s in type_registry.specs().values() for i in type_registry.ids_of(s)}
    homed = {
        (h.source, s.department, s.product_type)
        for s in type_registry.specs().values()
        for h in s.homes
    }
    held = set()
    for name in type_registry.HOME_SOURCES:
        for d in _source_docs(name):
            if d["product_id"] not in owned:
                held.add((name, str(d["department"][0]), str(d["product_type"])))
    assert sorted(held - homed) == [], "a row of a type that has no home"
    assert sorted(homed - held) == [], "a home that holds no row"


def test_the_sources_are_the_ones_the_templates_read() -> None:
    """The names ``HOME_SOURCES`` lists are the names ``scale.source_docs`` can read."""
    assert type_registry.HOME_SOURCES
    for name in type_registry.HOME_SOURCES:
        assert scale.source_docs(name) is not None


def _plant(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, derivable: bool) -> None:
    (tmp_path / f"{PLANTED_KEY}.py").write_text(
        PLANTED.format(derivable=derivable), encoding="utf-8"
    )
    monkeypatch.setattr(type_specs, "__path__", [*type_specs.__path__, str(tmp_path)])
    monkeypatch.delitem(sys.modules, f"type_specs.{PLANTED_KEY}", raising=False)
    type_registry.specs.cache_clear()
    left_out = getattr(scale, "left_out", None)
    if left_out is not None:
        left_out.cache_clear()


@pytest.fixture(autouse=True)
def _forget_the_planted_spec():
    yield
    sys.modules.pop(f"type_specs.{PLANTED_KEY}", None)
    type_registry.specs.cache_clear()
    left_out = getattr(scale, "left_out", None)
    if left_out is not None:
        left_out.cache_clear()


@pytest.mark.parametrize("derivable", [False, True])
def test_a_spec_file_alone_is_built_and_registered(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, derivable: bool
) -> None:
    """The #72 case: one new file under ``type_specs/``, no other edit. The registry finds it, the
    templates build it, ``registration_problems`` is clear, and ``derivable`` honors its flag."""
    _plant(tmp_path, monkeypatch, derivable)
    assert PLANTED_KEY in type_registry.specs()
    tpls = scale.templates(False)
    ids = {r["product_id"] for r in tpls if r["product_type"] == "Planted Specimen Tonic"}
    assert "BRD-ZZPL01" in ids
    drawn = {r["product_id"] for r in scale.derivable(tpls)}
    assert ("BRD-ZZPL01" in drawn) is derivable
    assert type_registry.registration_problems(_built_types()) == []


def _table_paths() -> set[str]:
    text = (ROOT / "docs" / "new-type-quick-path.md").read_text(encoding="utf-8")
    section = text.split("## Shared files: add a file, never a line", 1)[1].split("\n## ", 1)[0]
    rows = [ln for ln in section.splitlines() if ln.startswith("| `")]
    return {m.group(1) for ln in rows if (m := re.match(r"\| `([^`]+)`", ln))}


def test_the_no_append_check_covers_the_whole_513_table() -> None:
    """Every shared file the page lists is checked, but the one the page says needs nothing (its
    pin is derived), and the check lists no file that is gone."""
    text = (ROOT / "docs" / "new-type-quick-path.md").read_text(encoding="utf-8")
    covered = {reg.path for reg in guard.REGISTRIES}
    nothing = {
        m.group(1)
        for ln in text.splitlines()
        if (m := re.match(r"\| `([^`]+)` \|.*\| nothing:", ln))
    }
    listed = {p.removeprefix("prototypes/retail_drawings/") for p in _table_paths()}
    wanted = {p for p in listed if p not in nothing}
    short = {p.removeprefix("prototypes/retail_drawings/") for p in covered}
    assert sorted(wanted - short) == []
    assert sorted(p for p in covered if not (ROOT / p).exists()) == []
    assert not any(p.endswith("legacy_types.txt") for p in covered)
    assert "type_specs/legacy_types.txt" not in listed
