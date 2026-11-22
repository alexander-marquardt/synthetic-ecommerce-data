"""A retail module row whose brand has no owner fails in a check, before any ``doc()`` (gen#1039).

``type_registry.validate`` names a spec row whose brand has no owner. A module-level ``Row`` of an
older row module had no such check: its missing owner was a ``KeyError`` from the first
``doc()`` call on whichever CI worker built it. ``owned_rows.check()`` walks every module of
the retail package and names each module-level row whose brand ``brand_owners.table()`` does
not own; ``scale.templates()`` runs it before it builds any document.
"""

from __future__ import annotations

import dataclasses

import pytest

from synthetic_ecommerce_data.domains.retail import electronics_rows, owned_rows, scale
from synthetic_ecommerce_data.domains.retail.breadth_row import Row

#: A brand no module states.
UNOWNED = "Quorrel Unowned"


def test_every_retail_module_row_sells_an_owned_brand() -> None:
    found = {(module, row.code) for module, row in owned_rows.rows()}
    assert ("electronics_rows", electronics_rows.LAPTOPS[0].code) in found
    assert len(found) > 1000, "the walk no longer finds the module rows"
    assert owned_rows.unowned() == []


def test_an_unowned_module_row_fails_in_the_check_and_never_reaches_doc(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bad = dataclasses.replace(electronics_rows.LAPTOPS[0], brand=UNOWNED)
    monkeypatch.setattr(electronics_rows, "INJECTED", (bad,), raising=False)

    def no_doc(self: Row) -> dict:
        raise AssertionError(f"doc() ran for {self.code}: the check must not build documents")

    monkeypatch.setattr(Row, "doc", no_doc)
    try:
        owned_rows.check()
    except owned_rows.UnownedBrand as exc:
        message = str(exc)
    else:
        message = ""
    assert f"electronics_rows {bad.code} sells {UNOWNED!r}" in message
    assert owned_rows.unowned() == [f"electronics_rows {bad.code} sells {UNOWNED!r}"]


class _Checked(Exception):
    pass


class _Built(Exception):
    pass


def test_the_scaled_build_runs_the_check_before_it_builds_a_document(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def checked() -> None:
        raise _Checked

    def built() -> dict:
        raise _Built

    monkeypatch.setattr(owned_rows, "check", checked)
    monkeypatch.setattr(scale, "samples", built)
    first = None
    try:
        scale.templates()
    except (_Checked, _Built) as exc:
        first = type(exc)
    assert first is _Checked
