"""Round-3 review of #54: mutants of scripts/merge_pr.sh run against tests/test_merge_pr.py.

    uv run python scripts/review_54_r3_mutants.py

All four survive at 8e25c6e: no test moves main mid-run, moves the head, or
makes a conflict, so the refusal paths and the --ours resolution are untested.
"""

import shutil
import subprocess
from pathlib import Path

SCRIPT = Path(__file__).with_name("merge_pr.sh")
MUTANTS = {
    "no base re-check before merge": ('[ "$now_base" = "$base_sha" ] ||\n  die', "true ||\n  die"),
    "every conflict auto-resolved": ("by_hand=$(printf", 'by_hand=""; : $(printf'),
    "no head-moved check after clone": ('[ "$(git -C "$work" rev-parse HEAD)" = "$head_sha" ] ||', "true ||"),
    "generated conflicts take main's side": ("checkout --ours", "checkout --theirs"),
}
original = SCRIPT.read_text()
backup = SCRIPT.with_suffix(".orig")
shutil.copy2(SCRIPT, backup)
try:
    for name, (old, new) in MUTANTS.items():
        assert old in original, name
        SCRIPT.write_text(original.replace(old, new, 1))
        run = subprocess.run(["uv", "run", "-q", "pytest", "-q", "-p", "no:cacheprovider", "tests/test_merge_pr.py"], capture_output=True)
        print(f"{name}: {'caught' if run.returncode else 'SURVIVES'}")
finally:
    shutil.copy2(backup, SCRIPT)
    backup.unlink()
