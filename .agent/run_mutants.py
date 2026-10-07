"""One-off mutant loop for the review of PR 104 (the repo has no mutant_run.py).

Applies each tuple of tests/review_104_r1_mutants.py.txt in turn, runs the
table tests twice (every test; then without the byte-parity tests, which red
on any change to a build), and restores the file.
"""

from __future__ import annotations

import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MUTANTS = ROOT / "tests" / "review_104_r1_mutants.py.txt"
TESTS = [
    "tests/test_tabletype.py",
    "tests/test_type_cotter_pins.py",
    "tests/test_type_retaining_rings_external.py",
    *sys.argv[1:],
]
#: Byte-parity tests: they red on any change to what a type builds.
PARITY = (
    "not golden and not declared_count and not byte_identical"
    " and not builds_as_the_committed and not carries_exactly"
)


def run(extra: list[str]) -> tuple[bool, str]:
    result = subprocess.run(  # noqa: S603 -- "uv" runs this repo's own tests
        ["uv", "run", "--locked", "pytest", "-x", "-p", "no:cacheprovider", *TESTS, *extra],
        cwd=ROOT,
        capture_output=True,
        text=True,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        check=False,
    )
    failed = [line for line in result.stdout.splitlines() if line.startswith("FAILED")]
    return result.returncode != 0, (failed[0][:150] if failed else result.stdout[-200:])


def main() -> int:
    mutants = ast.literal_eval(MUTANTS.read_text(encoding="utf-8"))
    killed = behavioural = 0
    for path, old, new, name in mutants:
        target = ROOT / path
        original = target.read_text(encoding="utf-8")
        if original.count(old) != 1:
            print(f"REFUSED {name}: pattern found {original.count(old)} times")
            continue
        target.write_text(original.replace(old, new), encoding="utf-8")
        try:
            any_red, first = run([])
            behaviour_red, first_behaviour = run(["-k", PARITY])
        finally:
            target.write_text(original, encoding="utf-8")
        killed += any_red
        behavioural += behaviour_red
        print(f"{'KILLED  ' if any_red else 'SURVIVED'} {name}")
        print(f"    any test:        {first if any_red else 'green'}")
        print(f"    behavioural only: {first_behaviour if behaviour_red else 'green'}")
    print(
        f"{killed} of {len(mutants)} killed by any test;"
        f" {behavioural} of {len(mutants)} by a behavioural test"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
