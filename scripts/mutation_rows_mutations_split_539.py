"""Mutation rows for the loader of ``scripts/mutations/*.py`` (gen#539).

Each row plants one defect in ``mutation_row.discover_mutations`` or ``all_mutations`` and names
the test of ``tests/test_mutations_split_539.py`` that must go red. Found by
``mutation_row.discover``; ``--only "mutations split:"`` re-runs them.
"""

from __future__ import annotations

from mutation_row import Row

PREFIX = "mutations split"

_T = "tests/test_mutations_split_539.py"
_FILE = "scripts/mutation_row.py"


def _row(name, old, new, test, prop) -> Row:
    return Row(name, _FILE, old, new, f"{_T} -k {test}", prop, ".")


def rows() -> list[Row]:
    return [
        _row(
            "a file with no MUTATIONS list is not refused",
            "        if not isinstance(listed, list):",
            "        if False:",
            "absent",
            "a file with no MUTATIONS list is refused by name",
        ),
        _row(
            "an element that is not a Mutation is not refused",
            "            if not isinstance(mutation, Mutation):",
            "            if False:",
            "wrong-element",
            "an element that is not a Mutation is refused by name",
        ),
        _row(
            "a name two files share is planted twice",
            "            if mutation.name in owner:",
            "            if False:",
            "test_two_mutations_files_cannot_share_a_name",
            "two files cannot share a mutation name",
        ),
        _row(
            "the glob finds only the first file",
            '    return sorted((HERE / "mutations").glob("*.py"))',
            '    return sorted((HERE / "mutations").glob("*.py"))[:1]',
            "test_a_new_mutations_file_is_found_with_no_other_edit",
            "a new mutations file is found with no other edit",
        ),
        _row(
            "the whole bed drops the mutations files",
            "    return [*discover_mutations(), *rows]",
            "    return rows",
            "test_the_whole_bed_is_the_mutations_files_then_the_rows_files",
            "the whole bed holds the mutations files and the rows",
        ),
    ]
