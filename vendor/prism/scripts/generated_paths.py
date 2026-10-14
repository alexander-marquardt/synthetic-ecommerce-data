"""Which files are generated, and which suffixes mark hand-written source.

The root ``.ignore`` is read by two checks, and this module is the one place
both take their answers from:

* ``tests/test_ignore_covers_generated_10025.py`` (#10025) holds ``.ignore`` to
  every generator's output and keeps it off hand-written source.
* ``scripts/check_file_size.py`` (#10021) exempts a file from the line cap only
  when ``.ignore`` hides it AND :func:`generated_paths` names it.

The generated paths are DERIVED from the generators' own source (the
``_REPO_ROOT / "a" / "b"`` path constructors, ``generated_ts_path("x.ts")``, a
``DOC_PATH = "..."`` constant, the artifact paths in
``generate-contract-artifacts.sh``'s header, and the ``-o`` outputs of the front
end's ``generate:*`` npm scripts), so a generator added later is seen without a
hand-kept list. Standard library only: the size gate runs without an install.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path, PurePosixPath

sys.path.insert(0, str(Path(__file__).resolve().parent))
import working_tree_subject  # noqa: E402  (path is set up just above)

#: Code and prose a reader opens. The size gate measures these; the
#: hidden-source check refuses ``.ignore`` hiding any of them unless generated.
#: Matched case-insensitively (:func:`has_suffix`).
MEASURED_SUFFIXES: frozenset[str] = frozenset(
    {
        ".py",
        ".pyi",
        ".ts",
        ".tsx",
        ".mts",
        ".cts",
        ".js",
        ".jsx",
        ".mjs",
        ".cjs",
        ".sh",
        ".css",
        ".md",
    }
)
#: Hand-written configuration: outside the line budget (it is data), but still
#: source an agent must be able to search, so ``.ignore`` may not hide it.
CONFIG_SUFFIXES: frozenset[str] = frozenset({".yaml", ".yml", ".toml"})
HAND_WRITTEN_SUFFIXES: frozenset[str] = MEASURED_SUFFIXES | CONFIG_SUFFIXES

# Files a generator writes only a marked REGION of: the rest is hand-written
# prose an agent must be able to search, so they are deliberately not ignored.
REGION_ONLY = frozenset(
    {
        "docs/si/reference/api-reference.md",
        "docs/si/reference/cli-reference.md",
        "docs/si/reference/errors.md",
        "docs/si/07-configuration.md",
        "docs/si/25-config-consistency.md",
    }
)
# Named in the script header as an input, never written: the pinned generator,
# and the hand-written registry the process-guard page is rendered from.
READ_ONLY = frozenset({"search-ui/package.json", "scripts/process_guards.json"})
GENERATORS = (
    "scripts/generate_*.py",
    "scripts/emit_inventory.py",
    "scripts/agent_hazards.py",
)
ARTIFACT_SUFFIXES = (".json", ".ts", ".md", ".yaml")
CONTRACT_SCRIPT = "scripts/generate-contract-artifacts.sh"
FRONTEND_PACKAGE = "search-ui/package.json"
#: Hidden by ``.ignore`` although nobody generates it, with the reason.
HIDDEN_ALLOWED = frozenset({"CHANGELOG.md"})  # append-only release log, 1.2 MB

_CHAIN = re.compile(r'REPO_ROOT\s*/\s*((?:"[^"]+"\s*/\s*)*"[^"]+")')
_TS = re.compile(r'generated_ts_path\(\s*"([^"]+)"')
_DOC = re.compile(r'^DOC_PATH\s*=\s*"([^"]+)"', re.M)
_HEADER = re.compile(r"^#\s.*?\b((?:[\w.*-]+/)+[\w.*-]+\.(?:json|ts|md|yaml))\b", re.M)
_NPM_OUTPUT = re.compile(r"(?:^|\s)-o\s+(\S+)")


def has_suffix(path: str, suffixes: frozenset[str] = MEASURED_SUFFIXES) -> bool:
    """Whether ``path`` ends in one of ``suffixes``, whatever its case."""
    return PurePosixPath(path).suffix.lower() in suffixes


def _npm_outputs(root: Path) -> set[str]:
    """The ``-o`` targets of the front end's ``generate:*`` npm scripts."""
    package = root / FRONTEND_PACKAGE
    if not package.is_file():
        return set()
    scripts = json.loads(package.read_text(encoding="utf-8")).get("scripts", {})
    base = PurePosixPath(FRONTEND_PACKAGE).parent
    return {
        str(base / target)
        for name, command in scripts.items()
        if name.startswith("generate")
        for target in _NPM_OUTPUT.findall(command)
    }


def generated_paths(root: Path) -> set[str]:
    """Every whole file a generator writes, as a repository-relative path."""
    out: set[str] = set()
    for pattern in GENERATORS:
        for src in root.glob(pattern):
            text = src.read_text(encoding="utf-8")
            for m in _CHAIN.finditer(text):
                out.add("/".join(re.findall(r'"([^"]+)"', m.group(1))))
            out.update(f"search-ui/src/generated/{n}" for n in _TS.findall(text))
            out.update(_DOC.findall(text))
    sh = root / CONTRACT_SCRIPT
    if sh.is_file():
        header = sh.read_text(encoding="utf-8").split(
            "What this script does NOT write"
        )[0]
        out.update(_HEADER.findall(header))
    out.update(_npm_outputs(root))
    return {
        p
        for p in out
        if "*" not in p
        and p.endswith(ARTIFACT_SUFFIXES)
        and p not in REGION_ONLY | READ_ONLY
    }


def hidden_hand_written(root: Path) -> list[str]:
    """Tracked hand-written files `.ignore` hides: neither generated nor allowed.

    Uses git's own ignore matching (the semantics ripgrep applies), so a pattern
    too wide is seen as ripgrep sees it. No directory is exempt as a whole: a
    file under ``search-ui/src/generated/`` counts as generated only when
    :func:`generated_paths` names it.
    """
    # git's own "tracked and ignored" answer; no byte of a listed path is opened.
    hidden = working_tree_subject.ls_files("-ci", "--exclude-from=.ignore", root=root)
    allowed = generated_paths(root) | HIDDEN_ALLOWED
    return sorted(
        p for p in hidden if has_suffix(p, HAND_WRITTEN_SUFFIXES) and p not in allowed
    )
