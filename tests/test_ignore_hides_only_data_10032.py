"""The root ``.ignore`` hides bulk data from ripgrep and the agent Grep tool, and nothing else.

elastic/prism#10025 put a ``.ignore`` in the core repository so that a search
never floods an agent's context with catalog or golden lines; elastic/prism#10032
ports it here. Two ways it rots, each a test below: a pattern that no longer
hides any tracked file reads as coverage and is not, and a pattern drawn too
wide hides hand-written code an agent must see.

Git's own matcher reads the file. ``.ignore`` has gitignore syntax, the syntax
ripgrep applies to it, so nothing here re-implements the matching.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IGNORE = ROOT / ".ignore"
# Hand-written files an agent edits: hiding one from a search is never right.
CODE_SUFFIXES = (".py", ".sh", ".md", ".toml")


def _hidden(*exclude: str) -> list[str]:
    """Tracked files the given ``--exclude``/``--exclude-from`` arguments hide."""
    argv = [shutil.which("git") or "git", "-C", str(ROOT), "ls-files", "-ci", *exclude]
    done = subprocess.run(argv, capture_output=True, text=True, check=True)
    return done.stdout.splitlines()


def _patterns() -> list[str]:
    lines = (ln.strip() for ln in IGNORE.read_text(encoding="utf-8").splitlines())
    return [ln for ln in lines if ln and not ln.startswith("#")]


def test_every_pattern_hides_a_tracked_file() -> None:
    stale = [pat for pat in _patterns() if not _hidden(f"--exclude={pat}")]
    assert stale == [], f".ignore patterns that hide no tracked file: {stale}"


def test_no_hand_written_code_is_hidden() -> None:
    hidden = _hidden(f"--exclude-from={IGNORE}")
    code = [path for path in hidden if path.endswith(CODE_SUFFIXES)]
    assert code == [], f".ignore hides hand-written files a search must see: {code}"
