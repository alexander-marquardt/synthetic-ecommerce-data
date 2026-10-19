"""Mutation rows for the audit-before-write order of ``ecom-generate build`` (gen#253).

Each row writes ``flat.jsonl`` ahead of one audit, which a refused build must not do.
``mutation_check.py`` turns them into ``Mutation`` rows named ``audit order: ...`` (``--only
"audit order:"`` re-runs them). A row is ``(name, old, new, tests, property)`` on
``generate_cli.py``.
"""

from __future__ import annotations

from mutation_row import Row

EARLY_WRITE = '    emit.write_jsonl(emit.iter_flat(catalog, base_url), out / "flat.jsonl")\n'
TESTS = "tests/test_build_refusal_writes_nothing.py -k"

ROWS: list[tuple[str, str, str, tuple[str, ...], str]] = [
    (
        "flat.jsonl is written before the image audit",
        "    referenced = emit.referenced_image_ids(catalog)\n",
        EARLY_WRITE + "    referenced = emit.referenced_image_ids(catalog)\n",
        (f'{TESTS} "leaves_no_output and image"', f'{TESTS} "does_not_overwrite and image"'),
        "a refused build leaves --out as it was",
    ),
    (
        "flat.jsonl is written before the product audit",
        "    split_problems = distribution_problems(",
        EARLY_WRITE + "    split_problems = distribution_problems(",
        (f'{TESTS} "leaves_no_output and product"', f'{TESTS} "does_not_overwrite and product"'),
        "a refused build leaves --out as it was",
    ),
    (
        "flat.jsonl is written before the non-copying audit",
        "    audit = noncopy.audit(catalog)\n",
        EARLY_WRITE + "    audit = noncopy.audit(catalog)\n",
        (f'{TESTS} "leaves_no_output and noncopy"', f'{TESTS} "does_not_overwrite and noncopy"'),
        "a refused build leaves --out as it was",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "audit order"


def rows() -> list[Row]:
    return [Row(n, "generate_cli.py", o, w, t, p) for n, o, w, t, p in ROWS]
