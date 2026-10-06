"""One-off runner for tests/review_58_r3_mutants.py.txt (review round 3 of #58).

Applies one mutant, runs tests/test_price.py (stop at the first failure), and
restores the file. Prints KILLED (a test went red) or SURVIVED per entry,
with the first failing test id.
"""

import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ns: dict = {}
exec((ROOT / "tests/review_58_r3_mutants.py.txt").read_text(), ns)  # noqa: S102
wanted = set(sys.argv[1:])
results = []
for path, old, new, name in ns["MUTANTS"]:
    if wanted and name not in wanted:
        continue
    target = ROOT / path
    text = target.read_text()
    if text.count(old) != 1:
        results.append((name, f"ERROR: pattern found {text.count(old)} times"))
        continue
    target.write_text(text.replace(old, new))
    try:
        env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        run = subprocess.run(  # noqa: S603
            ["uv", "run", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests/test_price.py"],  # noqa: S607
            cwd=ROOT,
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        out = run.stdout
        failed = [line for line in out.splitlines() if line.startswith("FAILED")]
        verdict = f"KILLED by {failed[0][7:120]}" if run.returncode else "SURVIVED"
        results.append((name, verdict))
    finally:
        target.write_text(text)
    print(f"{name}: {results[-1][1]}", flush=True)
killed = sum(r.startswith("KILLED") for _, r in results)
print(f"{killed} of {len(results)} killed")
