"""Mutation rows for the repeated (name, value) pair on a parent (gen#1).

Kept out of ``mutation_check.py``.

Each row plants one defect in how a parent comes to publish one ``Standards`` value twice, or in
how the report reads it, and names the test that must go red. ``mutation_check.py`` turns them
into ``Mutation`` rows named ``repeated pair: ...`` (``--only "repeated pair:"`` re-runs them).
A row is ``(name, file, old, new, test, property, root)``.
"""

from __future__ import annotations

SRC = "src/synthetic_ecommerce_data"
TESTS = "tests/test_repeated_pair_1.py"

ROWS: list[tuple[str, str, str, str, str | tuple[str, ...], str, str]] = [
    (
        "no parent publishes one",
        "domains/industrial/finishing.py",
        "        if draws.random() >= self.config.scaled_defect(self.config.defect_repeated_pair):\n            return line_attrs",  # noqa: E501
        "        if True:\n            return line_attrs",
        (
            f"{TESTS}::test_some_parents_repeat_a_pair_and_it_is_the_multivalued_attribute",
            f"{TESTS}::test_the_report_row_counts_what_the_documents_publish",
        ),
        "some parents publish a (name, value) pair twice",
        SRC,
    ),
    (
        "the defect knob does not reach it",
        "domains/industrial/finishing.py",
        "        if draws.random() >= self.config.scaled_defect(self.config.defect_repeated_pair):",
        "        if draws.random() >= self.config.defect_repeated_pair * 10:",
        f"{TESTS}::test_defects_at_zero_publish_no_repeated_pair",
        "--defects 0 publishes no repeated pair",
        SRC,
    ),
    (
        "a repeated value counts as a second value",
        "domains/industrial/measure.py",
        "                    if len(set(values)) > 1:  # distinct values: a repeat is not multi-valued",  # noqa: E501
        "                    if len(values) > 1:",
        f"{TESTS}::test_a_repeated_value_is_not_counted_as_a_second_value",
        "a repeated value is not a second value",
        SRC,
    ),
]
