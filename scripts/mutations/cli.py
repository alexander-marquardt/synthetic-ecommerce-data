"""Mutations that plant a defect in the generator's command-line entry points and name the test that must go red.

``mutation_row.discover_mutations`` finds this file by glob and the harness plants each
entry of ``MUTATIONS`` in turn (``--only`` filters by a substring of the name). Moved out of
``scripts/mutation_check.py`` unchanged (gen#539).
"""

# ruff: noqa: E501  (a mutation quotes the whole line it plants in)
from __future__ import annotations

from mutation_row import Mutation

MUTATIONS: list[Mutation] = [
    # ---- the batch driver keeps going (issue #2) -------------------------
    Mutation(
        "abort the batch on the first record it cannot draw",
        "cli.py",
        "                if not keep_going:\n                    raise",
        "                raise",
        "tests/test_cli.py",
        "",
        "a batch skips what it cannot draw and reports it",
    ),
    Mutation(
        "count a refusal as a failure, so a normal catalog run reports failure",
        "cli.py",
        "                bucket = report.refused if isinstance(exc, DECLINED) else report.failed",
        "                bucket = report.failed",
        "tests/test_cli.py",
        "",
        "a refusal is not a failure",
    ),
    Mutation(
        "type seam: ecom-generate block finds no owner of a taken block",
        "generate_cli.py",
        "    owners = sorted(other for other, block in used.items() if block == derived)\n",
        "    owners: list[str] = []\n",
        "tests/test_type_seam.py::test_the_block_command_names_the_owner_and_a_really_free_block",
        "",
        "ecom-generate block names a block no type uses",
    ),
    Mutation(
        "write the committed field map in place, not by replacement (#440)",
        "generate_cli.py",
        '        staged.write_text(render(emit.iter_flat(catalog)), encoding="utf-8")\n        os.replace(staged, target)',
        '        target.write_text(render(emit.iter_flat(catalog)), encoding="utf-8")',
        "tests/test_prism_field_map_drift.py::test_the_field_map_is_replaced_not_rewritten_in_place",
        "",
        "a reader never sees the committed field map cut short",
    ),
    Mutation(
        "emit an eighth file the build does not commit",
        "generate_cli.py",
        '    (out / "mapping.flat.json").write_text(',
        '    (out / "mapping.extra.json").write_text("{}\\n", encoding="utf-8")\n'
        '    (out / "mapping.flat.json").write_text(',
        "tests/test_catalog_golden.py::test_golden_directory_holds_exactly_the_build_output",
        "B",
        "the committed catalog is byte-identical to a fresh build",
    ),
    # ---- figures: the measured figures are build output (#103) -----------
    # A figure the build miscounts reds the rebuild comparison; a doc that
    # quotes one again reds the docs scan.
    Mutation(
        "figures: brands counted as product types",
        "generate_cli.py",
        '"brands": len({doc["brand"] for doc in flat}),',
        '"brands": len({doc["product_type"] for doc in flat}),',
        "tests/test_catalog_golden.py::test_committed_file_matches_a_fresh_build",
        "",
        "the measured figures are the committed catalog's",
    ),
]
