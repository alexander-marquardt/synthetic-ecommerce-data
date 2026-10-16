"""Mutation rows for the generated measured builds (gen#85), kept out of ``mutation_check.py``.

Each row plants one defect and names the test that must go red. ``mutation_row.discover`` finds
this file by glob and turns the rows into ``Mutation`` rows named ``measured builds: ...``
(``--only "measured builds:"`` re-runs them). A row is ``(name, file, old, new, test, prop, root)``;
``file`` is relative to ``root``.
"""

from __future__ import annotations

from mutation_row import Row

_PRICE_TESTS = "tests/test_price.py"
_FILE = "src/synthetic_ecommerce_data/core/data/measured_builds.json"
_BUILDER = "src/synthetic_ecommerce_data/domains/industrial/measured_builds.py"
_PRICE = "src/synthetic_ecommerce_data/core/price.py"
_MERGE = "tests/test_merge_pr.py"
_ROOT = "."

ROWS: list[tuple[str, str, str, str, str, str, str]] = [
    (
        "the kit pin's 100K figure is loosened in the file",
        _FILE,
        '"price p90/p10: kit_assortment": 3.917',
        '"price p90/p10: kit_assortment": 3.5',
        f"{_PRICE_TESTS} -k measured_builds_file_is_what_the_rebuild_writes",
        "a figure the build moved or a hand loosened is red",
        _ROOT,
    ),
    (
        "the wheel pin's default figure is loosened in the file",
        _FILE,
        '"price brand spread, same spec (median max/min): wheel_depressed_center": 4.303',
        '"price brand spread, same spec (median max/min): wheel_depressed_center": 4.9',
        f"{_PRICE_TESTS} -k each_recorded_figure_is_the_figure_its_build_produces",
        "a pin holds the figure its build produces",
        _ROOT,
    ),
    (
        "a 100K size in the file is left stale",
        _FILE,
        '"wheel_depressed_center": 12435',
        '"wheel_depressed_center": 12000',
        f"{_PRICE_TESTS} -k measured_builds_file_is_what_the_rebuild_writes",
        "a stale size is red until the rebuild is committed",
        _ROOT,
    ),
    (
        "PINNED_FIGURES reads the default figure at 100K",
        _PRICE,
        "(default[name], hundred_k[name])",
        "(default[name], default[name])",
        f"{_PRICE_TESTS} -k pinned_figures_are_the_committed_files",
        "each build reads its own figure from the file",
        _ROOT,
    ),
    (
        "the rebuild rounds a pin to one place",
        _BUILDER,
        "round(rows[name].achieved, price_report.recorded_digits(name))",
        "round(rows[name].achieved, 1)",
        f"{_PRICE_TESTS} -k measured_builds_file_is_what_the_rebuild_writes",
        "a figure is written to the precision it is recorded at",
        _ROOT,
    ),
    (
        "the rebuild leaves a pinned row out of the file",
        _BUILDER,
        "        for name in sorted(price.PINNED_SHORTFALLS)\n",
        "        for name in sorted(price.PINNED_SHORTFALLS)[:1]\n",
        f"{_PRICE_TESTS} -k measured_builds_file_is_what_the_rebuild_writes",
        "every pinned row has a generated figure",
        _ROOT,
    ),
    (
        "the merge script does not list the file as generated",
        "scripts/merge_pr.sh",
        "  src/synthetic_ecommerce_data/core/data/measured_builds.json\n",
        "",
        f"{_MERGE} -k generated_files_are_exactly_what_the_build_writes",
        "a conflict in the file is resolved by the rebuild",
        _ROOT,
    ),
    (
        "the merge script does not rebuild the file",
        "scripts/merge_pr.sh",
        '--directory "$work" "${BUILDS_REBUILD[@]}"',
        '--directory "$work" python -c pass',
        f"{_MERGE} -k conflict_in_the_measured_builds_is_resolved_by_the_rebuild",
        "a conflict in the file is resolved by the rebuild",
        _ROOT,
    ),
    (
        "the breadth-type count may be typed in a doc again",
        "tests/test_measured_figures.py",
        "\\s+\\[?breadth\\s+(?:categor|types)",
        "\\s+\\[?breadth\\s+categor",
        "tests/test_measured_figures.py -k planted_restatement",
        "a typed type count is refused",
        _ROOT,
    ),
    (
        "a 100K per-type size may be typed in a doc again",
        "tests/test_measured_figures.py",
        "if count >= 1000:",
        "if count >= 10**9:",
        "tests/test_measured_figures.py -k planted_restatement",
        "a typed per-type size is refused",
        _ROOT,
    ),
]

PREFIX = "measured builds"


def rows() -> list[Row]:
    return [Row(*r) for r in ROWS]
