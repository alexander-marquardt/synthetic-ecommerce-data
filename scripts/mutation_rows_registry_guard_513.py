"""Mutation rows for the shared-registry guard and the feature decoy modules (gen#513).

Each row plants one defect on a changed line of ``check_no_registry_append.py``, of
``feature_decoys/__init__.py``, of the two decoy tables that read it or of the workflow, and names
the test that must go red. Found by ``mutation_row.discover``; ``--only "registry guard:"`` re-runs
them.
"""

from __future__ import annotations

from mutation_row import RETAIL_DRAWINGS, Row

PREFIX = "registry guard"

_G = "tests/test_registry_append_guard_513.py"
_F = "tests/test_feature_decoys_513.py"
_APPEND = f"{_G}::test_an_appended_registry_line_is_refused_and_names_the_new_file_form"
_GUARD = "check_no_registry_append.py"
_PKG = "feature_decoys/__init__.py"


def _row(name, root, file, old, new, test, prop) -> Row:
    return Row(name, file, old, new, test, prop, root)


def rows() -> list[Row]:
    return [
        _row(
            "an edit in place counts as an append",
            "scripts",
            _GUARD,
            "if len(hits) > len(gone):",
            "if len(hits) > 0:",
            f"{_G}::test_a_row_edited_in_place_is_not_an_append",
            "a line replaced by a line is no append",
        ),
        _row(
            "only the first registry is read",
            "scripts",
            _GUARD,
            "    for reg in REGISTRIES:\n        added, removed",
            "    for reg in REGISTRIES[:1]:\n        added, removed",
            f"{_G}::test_every_append_in_one_diff_is_named",
            "every registry the diff appends to is named",
        ),
        _row(
            "a trailer with no reason lets an append by",
            "scripts",
            _GUARD,
            "any(value.strip() for value in",
            "any(True for value in",
            f"{_G}::test_a_trailer_with_no_reason_does_not_let_an_append_by",
            "the escape needs a reason",
        ),
        _row(
            "the refusal does not name the form",
            "scripts",
            _GUARD,
            '        lines.append(f"    instead: {reg.form}")',
            '        lines.append("")',
            f"{_APPEND}[decoy-row]",
            "the refusal names the file that replaces the line",
        ),
        _row(
            "a legacy list line is not a shape",
            "scripts",
            _GUARD,
            '_shapes(r"^[^#\\s]"),',
            '_shapes(r"^[^#\\s]{99}"),',
            f"{_APPEND}[legacy-line]",
            "a line appended to the legacy list is refused",
        ),
        _row(
            "the guard step names another script",
            ".",
            ".github/workflows/ci.yaml",
            "python3 scripts/check_no_registry_append.py",
            "python3 scripts/check_no_stats_edit.py",
            f"{_G}::test_the_stats_roll_job_runs_the_registry_guard",
            "the stats-roll job runs the registry guard",
        ),
        _row(
            "a kind declared twice is merged",
            RETAIL_DRAWINGS,
            _PKG,
            "            if key in merged:",
            "            if False:",
            f"{_F}::test_a_kind_declared_by_two_modules_is_refused_naming_them",
            "a kind key has one owner",
        ),
        _row(
            "a row code held twice is let by",
            RETAIL_DRAWINGS,
            _PKG,
            "        if code in seen:",
            "        if False:",
            f"{_F}::test_a_module_whose_decoy_reuses_a_code_of_the_table_is_refused",
            "a row code is one id",
        ),
        _row(
            "a module that names nothing is skipped",
            RETAIL_DRAWINGS,
            _PKG,
            "        if not reads:",
            "        if False:",
            f"{_F}::test_a_module_that_names_nothing_the_tables_read_is_refused_by_name",
            "a file the tables would skip is refused",
        ),
        _row(
            "the decoy table ignores the modules",
            RETAIL_DRAWINGS,
            "decoy_rows.py",
            "TABLE = (*TABLE, *feature_decoys.decoy_rows(_d))",
            "TABLE = (*TABLE,)",
            f"{_F}::test_a_probe_module_reaches_both_tables_with_no_shared_file_edited",
            "a module's decoys reach decoy_rows.TABLE",
        ),
        _row(
            "the decoy kinds ignore the modules",
            RETAIL_DRAWINGS,
            "decoy_rows.py",
            "KINDS = feature_decoys.kinds(KINDS)",
            "KINDS = dict(KINDS)",
            f"{_F}::test_a_probe_module_reaches_both_tables_with_no_shared_file_edited",
            "a module's kinds reach decoy_rows.KINDS",
        ),
        _row(
            "the class-8 table ignores the modules",
            RETAIL_DRAWINGS,
            "decoy_product_words.py",
            "TABLE = (*TABLE, *feature_decoys.word_rows(_d))",
            "TABLE = (*TABLE,)",
            f"{_F}::test_a_probe_module_reaches_both_tables_with_no_shared_file_edited",
            "a module's decoys reach decoy_product_words.TABLE",
        ),
    ]
