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

import pytest

ROOT = Path(__file__).resolve().parent.parent
IGNORE = ROOT / ".ignore"
# Hand-written files an agent edits: hiding one from a search is never right.
# YAML is here because policies, vocabularies and customization are YAML.
CODE_SUFFIXES = (".py", ".sh", ".md", ".toml", ".yaml", ".yml")
# Protected files hidden on purpose, each with its reason.
ALLOWED_HIDDEN: dict[str, str] = {}


def _hidden(*exclude: str, root: Path = ROOT) -> list[str]:
    """Tracked files the given ``--exclude``/``--exclude-from`` arguments hide.

    A directory pattern hides every tracked file under it, so one that covers a
    protected file fails whether or not a README sits there.
    """
    argv = [shutil.which("git") or "git", "-C", str(root), "ls-files", "-ci", *exclude]
    done = subprocess.run(argv, capture_output=True, text=True, check=True)
    return done.stdout.splitlines()


def _patterns() -> list[str]:
    lines = (ln.strip() for ln in IGNORE.read_text(encoding="utf-8").splitlines())
    return [ln for ln in lines if ln and not ln.startswith("#")]


def test_every_pattern_hides_a_tracked_file() -> None:
    stale = [pat for pat in _patterns() if not _hidden(f"--exclude={pat}")]
    assert stale == [], f".ignore patterns that hide no tracked file: {stale}"


def _hand_written(hidden: list[str]) -> list[str]:
    protected = (path for path in hidden if path.lower().endswith(CODE_SUFFIXES))
    return [path for path in protected if path not in ALLOWED_HIDDEN]


def test_no_hand_written_code_is_hidden() -> None:
    code = _hand_written(_hidden(f"--exclude-from={IGNORE}"))
    assert code == [], f".ignore hides hand-written files a search must see: {code}"


def test_every_allowed_hidden_file_is_still_hidden() -> None:
    hidden = set(_hidden(f"--exclude-from={IGNORE}"))
    stale = [path for path in ALLOWED_HIDDEN if path not in hidden]
    assert stale == [], f"ALLOWED_HIDDEN rows the .ignore no longer hides: {stale}"


PLANTED = {
    "data/vocab/color.yaml": "a: 1\n",
    "customization.yaml": "a: 1\n",
    "data/policies/p.yml": "a: 1\n",
    "data/notes.txt": "x\n",
    "src/pkg/data/mod.py": "x = 1\n",
    "src/pkg/data/LOUD.YAML": "a: 1\n",
}


def _planted_repo(tmp_path: Path) -> Path:
    git = shutil.which("git") or "git"
    subprocess.run([git, "init", "-q", str(tmp_path)], check=True)
    for rel, text in PLANTED.items():
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(text)
    subprocess.run([git, "-C", str(tmp_path), "add", "-f", "."], check=True)
    return tmp_path


@pytest.mark.parametrize(
    ("pattern", "expected"),
    [
        ("data/vocab/*.yaml", ["data/vocab/color.yaml"]),
        ("customization.yaml", ["customization.yaml"]),
        ("*.yaml", ["customization.yaml", "data/vocab/color.yaml"]),
        ("data/policies/", ["data/policies/p.yml"]),
        ("src/pkg/data/", ["src/pkg/data/LOUD.YAML", "src/pkg/data/mod.py"]),
    ],
)
def test_a_pattern_that_hides_yaml_or_code_goes_red(
    tmp_path: Path, pattern: str, expected: list[str]
) -> None:
    repo = _planted_repo(tmp_path)
    hidden = _hand_written(_hidden(f"--exclude={pattern}", root=repo))
    assert set(expected) <= set(hidden)


def test_a_pattern_that_hides_only_data_stays_green(tmp_path: Path) -> None:
    repo = _planted_repo(tmp_path)
    assert _hand_written(_hidden("--exclude=data/*.txt", root=repo)) == []
