"""Prove the new tests bite, by breaking the code they guard.

    python scripts/mutation_check.py

A test that passes tells you nothing on its own: it might be asserting
something that cannot fail. So each mutation below plants a specific, plausible
defect in the source and checks that a named test goes red. Where a property
has two directions -- a rate that could be too high or too low, a guarantee
that could be too strict or too lax -- both are planted, because a test that
only catches one direction leaves the other unguarded.

**A mutation that reds nothing is reported as a zero.** It means the test does
not cover that defect, and hiding it would make this whole exercise
decorative.
"""

from __future__ import annotations

import argparse
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mutation_row  # noqa: E402  (the glob that finds the mutant-row files)
from mutation_row import Mutation  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
SRC = REPO / "src" / "synthetic_ecommerce_data"


#: Every planted defect: the rows of every ``scripts/mutation_rows_*.py``, read here by glob
#: (``mutation_row.discover``). No rows file is named in this module, so a pull request that adds
#: rows adds a file and edits no line of it (#506), and the table is not in this file (#363).
MUTATIONS: list[Mutation] = [
    mutation_row.as_mutation(prefix, row) for prefix, row in mutation_row.discover()
]


def _drop_bytecode() -> None:
    """Remove every cached .pyc under the package.

    Python validates a cached .pyc on (mtime, size). A mutation that swaps two
    values of the SAME total length, written back within the same second,
    produces a file the interpreter considers unchanged -- so it runs the stale
    bytecode. That is not hypothetical: the flute-weight mutation below swaps
    0.42 and 0.375 between two lines, which is length-preserving, and the
    restore silently did not take effect. The suite stayed red with a clean
    `git diff`, which is a genuinely confusing state to debug.

    The failure mode that matters is the quiet one: a mutation that does not
    take effect reports GREEN, and GREEN reads as "the test does not cover
    this" when the truth is "the mutation never ran".
    """
    for cached in SRC.rglob("__pycache__"):
        for pyc in cached.glob("*.pyc"):
            pyc.unlink()


class AmbiguousSelector(ValueError):
    """A selector carries two ``-k`` filters, so pytest silently uses one.

    ``a.py -k one b.py -k two`` looks like "these two filters, one per file"
    and is really "the second filter, applied to both" -- which ran a file
    with a filter that matched nothing in it and reported the mutation as not
    caught. Found by a mutation that came back green for the wrong reason, so
    the shape is refused rather than documented.
    """


class DisjunctiveSelector(ValueError):
    """A selector's ``-k`` filter names two tests with ``or``.

    This harness's verdict is "pytest went red", so a selector matching two
    tests is caught the moment EITHER of them fails -- and the other one is
    printed ``[ok]`` on its back without ever having been shown to bite.

    Measured: ``-k 'mid_word or sheds'`` reported one mutation caught while
    only the segment-level test was doing the catching; the string-level test
    could have been deleted and the row would have stayed green.

    THE FIX IS TWO ENTRIES, NOT A WIDER FILTER. One mutation may legitimately
    be expected to red two tests; write it as two ``Mutation`` rows with one
    selector each, and the table then says which test caught what. ``and`` is
    not refused -- narrowing to a single test is the point of this rule.
    """


def _selector_names_one_test(selector: str) -> None:
    """Refuse a ``-k`` filter that can be satisfied by either of two tests."""
    argv = shlex.split(selector)
    if "-k" not in argv:
        return
    expression = argv[argv.index("-k") + 1]
    if re.search(r"\bor\b", expression):
        raise DisjunctiveSelector(
            f"{selector!r} is satisfied by EITHER test, so one of them is "
            "never proven to bite. Split it into two Mutation rows with one "
            "selector each."
        )


def run(selector: str) -> bool:
    """True when the selector is GREEN."""
    # ``shlex`` rather than ``str.split``: a filter is written
    # ``-k "x or y"`` and splitting on whitespace hands pytest four arguments,
    # one of which is a stray quote. That fails the run for a reason that has
    # nothing to do with the mutation, and reports as "not caught".
    argv = shlex.split(selector)
    if argv.count("-k") > 1:
        raise AmbiguousSelector(
            f"{selector!r} has two -k filters; pytest keeps the last one. Write "
            "one filter, or -- better here -- one Mutation row per test."
        )
    _selector_names_one_test(selector)
    _drop_bytecode()
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-x", "-q", "--no-header", *argv],
        cwd=REPO,
        capture_output=True,
        text=True,
        env=env,
    )
    return result.returncode == 0


def _mutation_is_live(path: Path, mutation: Mutation) -> bool:
    """Confirm the file on disk really carries the mutation.

    A GREEN result is only evidence about the test if the mutation was
    actually present. This is the cheap half of that check; dropping the
    bytecode cache is the other half.
    """
    return mutation.new in path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", help="substring filter on the mutation name")
    parser.add_argument("--list", action="store_true", help="print the mutation names and stop")
    args = parser.parse_args(argv)

    mutations = [m for m in MUTATIONS if not args.only or args.only in m.name]

    if args.list:
        for mutation in mutations:
            print(mutation.name)
        return 0

    print("checking the suite is green before mutating ...")
    for selector in sorted({s for m in mutations for s in m.selectors}):
        if not run(selector):
            print(f"  {selector} is ALREADY RED -- fix that before mutating")
            return 2
    print("  green\n")

    rows: list[tuple[Mutation, bool, str]] = []
    for mutation in mutations:
        path = REPO / mutation.root / mutation.file
        original = path.read_text(encoding="utf-8")
        if mutation.old not in original:
            rows.append((mutation, False, "MUTATION DID NOT APPLY"))
            print(f"[!!] {mutation.name}: the text to mutate was not found")
            continue
        if original.count(mutation.old) != 1:
            rows.append((mutation, False, "MUTATION TEXT IS AMBIGUOUS"))
            print(f"[!!] {mutation.name}: matches {original.count(mutation.old)} places")
            continue
        path.write_text(original.replace(mutation.old, mutation.new), encoding="utf-8")
        try:
            # EVERY selector is judged on its own. A row naming two tests is
            # only FULLY proven when both red, so one of them can never be
            # carried by the other -- see ``Mutation.tests``.
            survivors = [s for s in mutation.selectors if run(s)]
            if survivors and not _mutation_is_live(path, mutation):
                rows.append((mutation, False, "MUTATION DID NOT REACH THE INTERPRETER"))
                print(f"[!!] {mutation.name}: source changed but the import did not")
                continue
        finally:
            path.write_text(original, encoding="utf-8")
        # THREE STATES, NOT TWO. "Nothing red" is a defect that would ship;
        # "something red, but a named test did not bite" is a defect that is
        # caught by a test other than the one the row credits. Reporting both
        # as one verdict is what the disjunctive selectors used to do.
        caught = not survivors
        if caught:
            note = "red"
        elif len(survivors) < len(mutation.selectors):
            note = "caught, but NOT by " + ", ".join(survivors)
        else:
            note = "GREEN -- NOT CAUGHT"
        rows.append((mutation, caught, note))
        marker = "ok" if caught else ("~ " if len(survivors) < len(mutation.selectors) else "  ")
        print(f"[{marker}] {mutation.name}: {note}")

    print("\nre-checking the suite is green after restoring ...")
    ok = all(run(selector) for selector in sorted({s for m in mutations for s in m.selectors}))
    print("  green" if ok else "  STILL RED -- a mutation was not reverted")

    caught = sum(1 for _, c, _ in rows if c)
    print(f"\n{caught} of {len(rows)} mutations caught by EVERY test they name")
    ships_green = [(m, n) for m, c, n in rows if not c and n.startswith("GREEN")]
    partial = [(m, n) for m, c, n in rows if not c and n.startswith("caught, but")]
    if ships_green:
        print("\nNOT CAUGHT -- these defects would ship green:")
        for mutation, note in ships_green:
            print(f"  - {mutation.name} ({mutation.property_name}): {note}")
    if partial:
        print(
            "\nCAUGHT, BUT BY ANOTHER TEST -- the defect is guarded; the test "
            "named here is not proven to bite by this mutation:"
        )
        for mutation, note in partial:
            print(f"  - {mutation.name}: {note}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
