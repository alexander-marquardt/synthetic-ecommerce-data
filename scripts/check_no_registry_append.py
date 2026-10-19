#!/usr/bin/env python3
"""Refuse a pull request that appends a line to a shared registry (gen#513).

    python3 scripts/check_no_registry_append.py --base <sha> --head <sha>   # CI, the stats-roll job

On 2026-10-18, 16 of the 21 open PRs conflicted with main. With the rolled stats files out of the
way (``check_no_stats_edit.py``, gen#373), what conflicted was a set of registries that each
feature appended one entry to: an import and an id set in ``scale.py``, a row and a kind in the
decoy tables, a line in ``legacy_types.txt``. :data:`REGISTRIES` maps each such file to the shapes
of an appended line and to the new-file form that replaces the line. The check counts, per
registry, the lines of those shapes that ``base...head`` adds less the ones it removes, so an edit
in place and a migration that shortens the list pass, and a diff that nets one fails and names the
form.

A registry is in the table in the same PR that gives it a new-file form, so the check never refuses
what has no alternative yet: ``tests/test_registry_append_guard_513.py`` holds every entry to a
form that exists. The one escape, for a change that is not a feature (a helper module the scaled
build needs), is a ``Registry-Append: <reason>`` trailer on the tip commit; a trailer with no
reason does not count.

Exit 0: no registry nets an appended line, or the tip carries the trailer. Exit 1: the registries,
the lines and the files that replace them.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import NamedTuple

TRAILER_KEY = "Registry-Append"
RD = "prototypes/retail_drawings"


class Registry(NamedTuple):
    path: str
    #: An added line that matches one of these is an append.
    shapes: tuple[re.Pattern[str], ...]
    #: A line a feature used to append here: it must match a shape.
    example: str
    #: What replaces the line, in the words of the refusal.
    form: str
    #: The files the form names; they must exist.
    exists: tuple[str, ...]


def _shapes(*patterns: str) -> tuple[re.Pattern[str], ...]:
    return tuple(re.compile(p) for p in patterns)


_KIND_ENTRY = r'^\s+"\w+":\s*Kind\('
_DECOY_FORM = (
    f"add {RD}/feature_decoys/<topic>.py exposing KINDS (new kinds), decoy_rows(d) or word_rows(d)"
    " (rows made with the table's own maker d); the tables find it by walking the package"
)
_DECOY_FILES = (f"{RD}/feature_decoys/__init__.py",)

REGISTRIES: tuple[Registry, ...] = (
    Registry(
        "scripts/mutation_check.py",
        _shapes(r"^\s*(import|from)\s+mutation_rows_", r"\bmutation_rows_\w+\."),
        "import mutation_rows_probe_513  # noqa: E402",
        "add scripts/mutation_rows_<topic>.py exposing PREFIX and rows(); scripts/mutation_row.py"
        " finds it by glob and nothing is imported or listed here",
        ("scripts/mutation_row.py",),
    ),
    Registry(
        f"{RD}/scale.py",
        _shapes(r"^import \w+_rows\b", r"^[A-Z][A-Z_]*_IDS\s*="),
        "import probe_rows  # noqa: E402",
        f"declare the type as a spec, {RD}/type_specs/<key>.py (uv run python scripts/new_type.py"
        " <key>); the registry feeds the scaled build, so scale.py gains no import and no id set",
        ("scripts/new_type.py", f"{RD}/type_registry.py"),
    ),
    Registry(
        f"{RD}/type_specs/legacy_types.txt",
        _shapes(r"^[^#\s]"),
        "Beauty|Probe Cream",
        "never add a line: the list only shrinks. scripts/new_type.py <key> writes the spec file"
        " that registers the type",
        ("scripts/new_type.py",),
    ),
    Registry(
        f"{RD}/decoy_rows.py",
        _shapes(r"^\s+_d\(", _KIND_ENTRY, r"^from decoy_\w+_rows import", r"^\s+\*\(_d\("),
        '    _d("XZ01", "sofa", "Title", "Desc", "Red", 1, "red sofa", 720),',
        _DECOY_FORM,
        _DECOY_FILES,
    ),
    Registry(
        f"{RD}/decoy_product_words.py",
        _shapes(
            r"^\s+_[a-z]\(\s*\d+,",
            r"^\s+_[a-z]\($",
            r"^TABLE = \(\*TABLE, \*(?!feature_decoys\.)",
            r"^NEW_KINDS\.update\(",
            _KIND_ENTRY,
        ),
        '    _s(99, "s_probe", "Title", "Desc", "Brown", "block", "Yoga Block"),',
        _DECOY_FORM,
        _DECOY_FILES,
    ),
)


def _git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if done.returncode != 0:
        raise SystemExit(f"check_no_registry_append: git {' '.join(args)}: {done.stderr.strip()}")
    return done.stdout


def _changed_lines(root: Path, base: str, head: str) -> dict[str, tuple[list[str], list[str]]]:
    """Per registry file, the lines ``base...head`` adds and the lines it removes."""
    paths = [reg.path for reg in REGISTRIES]
    span = f"{base}...{head}"
    diff = _git(root, "diff", "-U0", "--no-color", "--no-ext-diff", span, "--", *paths)
    found: dict[str, tuple[list[str], list[str]]] = {}
    current: tuple[list[str], list[str]] | None = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            name = line[4:].removeprefix("b/")
            current = found.setdefault(name, ([], [])) if name in paths else None
        elif line.startswith("--- "):
            continue
        elif current is not None and line[:1] == "+":
            current[0].append(line[1:])
        elif current is not None and line[:1] == "-":
            current[1].append(line[1:])
    return found


def appended(root: Path, base: str, head: str) -> list[tuple[Registry, list[str]]]:
    """The registries whose lines of an append shape grow in ``base...head``, with those lines."""
    changed = _changed_lines(root, base, head)
    out = []
    for reg in REGISTRIES:
        added, removed = changed.get(reg.path, ([], []))
        hits = [ln for ln in added if any(s.search(ln) for s in reg.shapes)]
        gone = [ln for ln in removed if any(s.search(ln) for s in reg.shapes)]
        if len(hits) > len(gone):
            out.append((reg, hits))
    return out


def escaped(root: Path, head: str) -> bool:
    """Whether the tip commit carries ``Registry-Append: <a reason>``."""
    fmt = f"--format=%(trailers:key={TRAILER_KEY},valueonly)"
    return any(value.strip() for value in _git(root, "log", "-1", fmt, head).split("\n"))


def refusal(found: list[tuple[Registry, list[str]]]) -> str:
    lines = [
        "registry-append: this change appends to files every feature PR edits, so the next PR",
        "branched from the same main conflicts with it (gen#513). Each has a new-file form:",
    ]
    for reg, hits in found:
        lines += ["", f"  {reg.path}", *(f"    + {hit.strip()}" for hit in hits[:3])]
        if len(hits) > 3:
            lines.append(f"    + ... {len(hits) - 3} more")
        lines.append(f"    instead: {reg.form}")
    lines += [
        "",
        "A change that is not a feature (a helper the build needs) says so on its tip commit:",
        f"  {TRAILER_KEY}: <why no new file will do>",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    found = appended(args.root, args.base, args.head)
    if not found or escaped(args.root, args.head):
        return 0
    print(refusal(found))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
