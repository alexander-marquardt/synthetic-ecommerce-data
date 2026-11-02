"""Every industrial ``category_path`` starts at its department (slice 3 of the 2026-10-28 ruling).

The department is the top level of ``category_path`` for every domain (gen#281, #125). Industrial
types file their paths from their root down, and ``taxonomy.DEPARTMENT_OF`` files each root under
one of core's departments (``core/departments.py``). Until this slice the catalogue repository
prefixed the department at load from its own copy of the table; the generator now publishes it.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from synthetic_ecommerce_data.core import departments, emit
from synthetic_ecommerce_data.core.config import SMALL
from synthetic_ecommerce_data.core.letter_case import sentence_case
from synthetic_ecommerce_data.domains.industrial import taxonomy
from synthetic_ecommerce_data.domains.industrial.generate import generate

GOLDEN = Path(__file__).resolve().parents[1] / "golden-catalog"


@pytest.fixture(scope="module")
def nested() -> list[dict]:
    return list(emit.iter_nested(generate(SMALL)))


def test_every_built_document_starts_at_the_department_its_root_is_filed_under(nested):
    wrong = [
        d["category_path"]
        for d in nested
        if taxonomy.DEPARTMENT_OF.get(d["category_path"][1] if len(d["category_path"]) > 1 else "")
        != d["category_path"][0]
    ]
    assert wrong == [], f"{len(wrong)} documents, e.g. {wrong[:3]}"


@pytest.mark.parametrize("name", ["flat.jsonl", "nested.jsonl"])
def test_every_golden_row_sits_under_an_industrial_department(name):
    with (GOLDEN / name).open(encoding="utf-8") as handle:
        tops = {json.loads(line)["category_path"][0] for line in handle}
    assert tops == set(departments.INDUSTRIAL)


def test_a_root_with_no_department_is_refused_not_passed_through():
    try:
        got = taxonomy.rooted(("Widgets", "Sprockets", "Widget Sprockets"))
    except ValueError as exc:
        assert "Widgets" in str(exc)
    else:
        raise AssertionError(f"an unfiled root passed through as {got!r}")


def test_a_path_is_rooted_once_under_its_roots_department():
    assert taxonomy.rooted(("Hand Tools", "Hammers")) == ("Tools", "Hand Tools", "Hammers")


def test_every_authored_root_is_filed_and_every_row_is_a_root_in_use():
    roots = {sentence_case(path[0]) for path in taxonomy.all_paths()}
    assert roots == set(taxonomy.DEPARTMENT_OF)


def test_the_table_files_under_core_departments_only_and_uses_each():
    assert set(taxonomy.DEPARTMENT_OF.values()) == set(departments.INDUSTRIAL)
    assert set(departments.INDUSTRIAL) <= departments.DEPARTMENTS
