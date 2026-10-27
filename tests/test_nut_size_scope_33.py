"""A hex nut claims a grade standard only inside that standard's size scope, and
a heavy hex nut exists only at the sizes a real one is made in (#33).

The review of release catalog-2026-09-29f found 55 inch nuts of #6-#10 claiming
SAE J995 (which covers 1/4" to 1-1/2"), 15 M3/M4 nuts claiming ISO 898-2 (which
covers M5 to M39), and 103 heavy hex nuts at #6-#10 and M3-M10, sizes no maker
sells in the heavy series (``#6-32`` heavy hex at 7/16" across flats and 0.120"
high). Each check reads the nut records as published, golden and fresh.
"""

from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path

import pytest

from published import authored_attributes
from synthetic_ecommerce_data.core import emit
from synthetic_ecommerce_data.core.config import GeneratorConfig
from synthetic_ecommerce_data.domains.industrial.generate import generate
from test_catalog_facts import _realistic_only

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"


@pytest.fixture(scope="module")
def golden() -> list[dict]:
    docs = [json.loads(line) for line in (GOLDEN / "flat.jsonl").read_text("utf-8").splitlines()]
    return _realistic_only(docs)


@pytest.fixture(scope="module")
def fresh() -> list[dict]:
    return _realistic_only(list(emit.iter_flat(generate(GeneratorConfig()))))


@pytest.fixture(scope="module", params=["golden", "fresh"])
def docs(request) -> list[dict]:
    return request.getfixturevalue(request.param)


#: SAE J995, mechanical and quality requirements for steel nuts: 1/4" to 1-1/2".
J995_INCH = (Fraction(1, 4), Fraction(3, 2))
#: ISO 898-2 (2022): nuts of nominal diameter 5 mm to 39 mm.
ISO_898_2_MM = (5, 39)
#: A heavy hex nut is made from 1/4" (ASME B18.2.2) and, as the structural
#: series (ISO 7414 / EN 14399-4), from M12.
HEAVY_INCH_FROM = Fraction(1, 4)
HEAVY_MM_FROM = 12


def _nominal(thread: str) -> tuple[bool, Fraction | None]:
    """``(metric, diameter)`` of a thread size: M12x1.75 -> (True, 12); 1/4-20 ->
    (False, 1/4); ``#10-24`` has no inch fraction here, so ``(False, None)``
    is "below every scope", and no nut table row is smaller than a number size."""
    if thread.startswith("M"):
        return True, Fraction(thread[1:].split("x")[0])
    key = thread.split("-")[0]
    return False, None if key.startswith("#") else Fraction(key)


def _nuts(docs: list[dict]) -> list[tuple[dict, dict[str, list[str]]]]:
    out = []
    for doc in docs:
        if doc["product_type"] != "nut_hex":
            continue
        by_name: dict[str, list[str]] = {}
        for attribute in authored_attributes(doc):
            by_name.setdefault(attribute["name"], []).append(attribute["value"])
        out.append((doc, by_name))
    return out


def out_of_scope_claims(docs: list[dict]) -> tuple[list, int]:
    """The nut records claiming SAE J995 or ISO 898-2 outside its scope, and
    how many such claims were checked."""
    wrong, checked = [], 0
    for doc, values in _nuts(docs):
        metric, diameter = _nominal(values["Thread Size"][0])
        for standard in values.get("Standards", ()):
            if standard == "SAE J995":
                low, high = J995_INCH
                ok = not metric and diameter is not None and low <= diameter <= high
            elif standard == "ISO 898-2":
                low, high = ISO_898_2_MM
                ok = metric and diameter is not None and low <= diameter <= high
            else:
                continue
            checked += 1
            if not ok:
                wrong.append((doc["sku"], standard, values["Thread Size"][0]))
    return wrong, checked


def small_heavy_hex(docs: list[dict]) -> tuple[list, int]:
    """The heavy hex nut records below the smallest heavy hex size, and how
    many heavy hex records there are."""
    wrong, checked = [], 0
    for doc, values in _nuts(docs):
        if values.get("Type") != ["Heavy Hex"]:
            continue
        checked += 1
        metric, diameter = _nominal(values["Thread Size"][0])
        floor = HEAVY_MM_FROM if metric else HEAVY_INCH_FROM
        if diameter is None or diameter < floor:
            wrong.append((doc["sku"], values["Thread Size"][0]))
    return wrong, checked


def test_a_nut_claims_a_grade_standard_only_inside_its_size_scope(docs):
    """SAE J995 is 1/4" to 1-1/2"; ISO 898-2 is M5 to M39."""
    wrong, checked = out_of_scope_claims(docs)
    assert wrong == [], (len(wrong), wrong[:10])
    assert checked > 50


def test_a_heavy_hex_nut_is_not_offered_below_the_heavy_series(docs):
    """No #6-#10 or M3-M10 heavy hex nut: inch from 1/4", metric from M12."""
    wrong, checked = small_heavy_hex(docs)
    assert wrong == [], (len(wrong), wrong[:10])
    assert checked > 50


def test_the_heavy_hex_nuts_still_cover_every_size_they_are_made_in(docs):
    """Dropping the small sizes must not thin the rest: each size from the
    floor up is still offered, so a search by size finds a heavy hex nut."""
    seen = {_nominal(v["Thread Size"][0]) for _, v in _nuts(docs) if v.get("Type") == ["Heavy Hex"]}
    inch = {d for metric, d in seen if not metric}
    metric = {d for metric, d in seen if metric}
    assert {Fraction(1, 4), Fraction(1, 2), Fraction(1)} <= inch
    assert {12, 16, 20, 24} <= metric


@pytest.mark.parametrize(
    ("thread", "expected"),
    [("#6-32", (False, None)), ("1/4-20", (False, Fraction(1, 4))), ("M12x1.75", (True, 12))],
)
def test_a_thread_size_reads_to_its_nominal_diameter(thread, expected):
    assert _nominal(thread) == expected
