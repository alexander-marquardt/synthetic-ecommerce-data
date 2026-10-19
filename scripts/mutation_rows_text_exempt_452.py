"""Mutation rows for the text-check exemption derived from the registry (gen#452), kept out of
``mutation_check.py``.

Each row plants one defect in ``scale.py`` or ``type_registry.py`` and names the test that must go
red. ``mutation_row.discover`` finds this file by glob and the harness names them as rows named
``text exempt: ...`` (``--only "text exempt:"`` re-runs them). A row is
``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

from mutation_row import Row

_R = "prototypes/retail_drawings"

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "scale drops the registry's decoys of every department",
        "scale.py",
        "        | type_registry.text_match_decoy_ids()\n",
        "",
        "tests/test_retail_text_exempt_452.py -k joins_the_exemption_without_editing_scale",
        "a registered type's decoy is exempt by registering, with no edit to scale.py",
        _R,
    ),
    (
        "the unfiltered call returns no department",
        "type_registry.py",
        "if department is None or spec.department == department",
        "if spec.department == department",
        "tests/test_retail_text_exempt_452.py -k union_over_every_department",
        "no department means every department",
        _R,
    ),
    (
        "a class-8 decoy joins the exemption",
        "type_registry.py",
        "        if d.cls != 8\n        for i in _ids([d.row])",
        "        for i in _ids([d.row])",
        "tests/test_retail_text_exempt_452.py -k class_8_decoy_is_checked",
        "the product-word decoys are checked like any product",
        _R,
    ),
    (
        "scale drops the declared one-offs",
        "scale.py",
        "        | frozenset(type_registry.ONE_OFF_TEXT_EXEMPT)\n",
        "",
        "tests/test_retail_text_exempt_452.py -k rose_gold_hoop_is_a_declared_one_off",
        "a declared one-off is exempt",
        _R,
    ),
    (
        "an exempt id the catalog no longer builds goes unfound",
        "scale.py",
        "sorted(text_exempt() - built)",
        "sorted(text_exempt() & set())",
        "tests/test_retail_text_exempt_452.py -k one_off_that_is_in_no_catalog",
        "a stale entry is found",
        _R,
    ),
    (
        "a one-off the registry already knows goes unfound",
        "scale.py",
        "if pid in known:",
        "if False:",
        "tests/test_retail_text_exempt_452.py -k one_off_the_registry_already_knows",
        "a redundant one-off is found",
        _R,
    ),
    (
        "a one-off with no reason goes unfound",
        "scale.py",
        "if not reason.strip():",
        "if False:",
        "tests/test_retail_text_exempt_452.py -k one_off_without_a_reason",
        "a declared one-off states its reason",
        _R,
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "text exempt"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
