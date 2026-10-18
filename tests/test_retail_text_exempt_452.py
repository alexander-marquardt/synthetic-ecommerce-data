"""The text-check exemption of the retail build is derived from the type registry (gen#452).

``scale.TEXT_EXEMPT`` used to be a union written in ``scale.py``, naming the one department
(``Toys``) whose spec decoys were exempt, so each new department had to remember to add itself.
It is now computed from :func:`type_registry.text_match_decoy_ids` over every department, plus the
declared one-offs of :data:`type_registry.ONE_OFF_TEXT_EXEMPT`, and :func:`scale.exempt_problems`
finds an id that no longer belongs.
"""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RETAIL = ROOT / "prototypes" / "retail_drawings"
if str(RETAIL) not in sys.path:
    sys.path.insert(0, str(RETAIL))

import scale  # noqa: E402
import type_registry  # noqa: E402
from breadth_rows import Row  # noqa: E402
from variants import cw  # noqa: E402


def _planted(cls: int, department: str = "Planted Department") -> type_registry.TypeSpec:
    """A registered type of a department no list names, with one decoy of class ``cls``."""
    row = Row(
        "PLNTRW", "Planted Item", "Mirefield Naturals", department,
        (department, "Planted", "Planted Item"), "Planted Item", 6.0, "each", "A planted item.",
        (cw("Amber", "#c98a2e"),),
        sizes=(("one size", 6.0),), colorless=True,
    )  # fmt: skip
    decoy = replace(row, code="PLNTDC", title="Planted Item With Red Trim")
    return type_registry.TypeSpec(
        "planted_item", department, "Planted Item", rows=(row,),
        decoys=(type_registry.Decoy(cls, "red planted item", "color", decoy),),
    )  # fmt: skip


def _with(monkeypatch: pytest.MonkeyPatch, spec: type_registry.TypeSpec) -> None:
    real = type_registry.specs()
    monkeypatch.setattr(type_registry, "specs", lambda: {**real, spec.key: spec})


def test_a_registered_decoy_of_any_department_joins_the_exemption_without_editing_scale(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert "BRD-PLNTDC" not in scale.text_exempt()
    _with(monkeypatch, _planted(1))
    assert "BRD-PLNTDC" in type_registry.text_match_decoy_ids()
    assert "BRD-PLNTDC" in scale.text_exempt()
    assert "BRD-PLNTRW" not in scale.text_exempt()  # a row of the type is checked like any product


def test_a_class_8_decoy_is_checked_like_any_product(monkeypatch: pytest.MonkeyPatch) -> None:
    _with(monkeypatch, _planted(8))
    assert "BRD-PLNTDC" not in scale.text_exempt()


def test_the_unfiltered_ids_are_the_union_over_every_department() -> None:
    departments = {s.department for s in type_registry.specs().values()}
    assert len(departments) > 1
    union = frozenset().union(*(type_registry.text_match_decoy_ids(d) for d in departments))
    assert union
    assert type_registry.text_match_decoy_ids() == union
    assert union <= scale.TEXT_EXEMPT


def test_the_live_exemption_has_no_stale_id() -> None:
    assert scale.exempt_problems() == []


def test_the_rose_gold_hoop_is_a_declared_one_off_with_its_reason() -> None:
    reason = type_registry.ONE_OFF_TEXT_EXEMPT.get("PLT-RQHOOP", "")
    assert len(reason.split()) >= 5, reason
    assert "PLT-RQHOOP" in scale.TEXT_EXEMPT
    assert "PLT-RQHOOP" not in type_registry.text_match_decoy_ids()  # no spec owns it


def test_a_declared_one_off_that_is_in_no_catalog_is_found(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(type_registry.ONE_OFF_TEXT_EXEMPT, "PLT-GONE", "a row since removed")
    problems = scale.exempt_problems()
    assert [p for p in problems if "PLT-GONE" in p], problems


def test_a_one_off_the_registry_already_knows_is_found(monkeypatch: pytest.MonkeyPatch) -> None:
    known = sorted(type_registry.text_match_decoy_ids("Toys"))[0]
    monkeypatch.setitem(type_registry.ONE_OFF_TEXT_EXEMPT, known, "already a registered decoy")
    problems = scale.exempt_problems()
    assert [p for p in problems if known in p], problems


def test_a_declared_one_off_without_a_reason_is_found(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(type_registry.ONE_OFF_TEXT_EXEMPT, "PLT-RQHOOP", "")
    problems = scale.exempt_problems()
    assert [p for p in problems if "PLT-RQHOOP" in p], problems
