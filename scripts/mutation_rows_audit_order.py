"""Mutation rows for the audit-before-write order of ``ecom-generate build`` (gen#253).

Each row writes ``flat.jsonl`` ahead of one audit or check, which a refused build must not do.
``mutation_check.py`` turns them into ``Mutation`` rows named ``audit order: ...`` (``--only
"audit order:"`` re-runs them). A row is ``(name, old, new, tests, property)`` on
``generate_cli.py``.
"""

from __future__ import annotations

from mutation_row import Row


# The build now writes into a staging directory and moves it into ``--out`` after every audit
# (gen#952): a write ahead of an audit goes straight into ``--out``, at the loop's indent (12)
# or the function's (4).
def _early_write(indent: int) -> str:
    pad = " " * indent
    return (
        f"{pad}out.mkdir(parents=True, exist_ok=True)\n"
        f'{pad}(out / "flat.jsonl").write_text("{{}}\\n", encoding="utf-8")\n'
    )


EARLY_WRITE = _early_write(4)
LOOP_WRITE = _early_write(12)
TESTS = "tests/test_build_refusal_writes_nothing.py -k"

ROWS: list[tuple[str, str, str, tuple[str, ...], str]] = [
    (
        "flat.jsonl is written before the image audit",
        "            problems = _image_problems(part)\n",
        LOOP_WRITE + "            problems = _image_problems(part)\n",
        (f'{TESTS} "leaves_no_output and image"', f'{TESTS} "does_not_overwrite and image"'),
        "a refused build leaves --out as it was",
    ),
    (
        "flat.jsonl is written before the image-id form check",
        "            problems = _image_problems(part)\n",
        LOOP_WRITE + "            problems = _image_problems(part)\n",
        (f'{TESTS} "leaves_no_output and idform"', f'{TESTS} "does_not_overwrite and idform"'),
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
        "            audit = _merged_audit(audit, noncopy.audit(part))\n",
        LOOP_WRITE + "            audit = _merged_audit(audit, noncopy.audit(part))\n",
        (f'{TESTS} "leaves_no_output and noncopy"', f'{TESTS} "does_not_overwrite and noncopy"'),
        "a refused build leaves --out as it was",
    ),
]

# Found by ``mutation_row.discover``: the prefix of the rows' names and the rows in one shape.
PREFIX = "audit order"


def rows() -> list[Row]:
    return [Row(n, "generate_cli.py", o, w, t, p) for n, o, w, t, p in ROWS]
