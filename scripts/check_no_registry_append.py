#!/usr/bin/env python3
"""Refuse a pull request that appends a line to a shared registry (gen#513).

    python3 scripts/check_no_registry_append.py --base <sha> --head <sha>   # CI: no-derived-files

On 2026-10-18, 16 of the 21 open PRs conflicted with main. With the derived files out of git
(``check_no_derived_files.py``, gen#536), what conflicted was a set of registries that each
feature appended one entry to: an import and an id set in ``scale.py``, a row and a kind in the
decoy tables, a line in a legacy type list (gone since gen#537).
:data:`REGISTRIES` maps each such file to the shapes of an appended line and to the new-file
form that replaces the line. The check counts, per registry, the lines of those shapes that
``base...head`` adds less the ones it removes, so an edit in place and a migration that shortens
the list pass, and a diff that nets one fails and names the
form.

A registry is in the table in the same PR that gives it a new-file form, so the check never refuses
what has no alternative yet: ``tests/test_registry_append_guard_513.py`` holds every entry to a
form that exists. The one escape, for a change that is not a feature (a helper module the scaled
build needs), is a ``Registry-Append: <reason>`` trailer on a commit of the branch (any non-merge
commit in ``base..head``, so a later commit or a merge of main does not drop it); a trailer with
no reason does not count.

Exit 0: no registry nets an appended line, or a commit of the branch carries the trailer.
Exit 1: the registries, the lines and the files that replace them.
"""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path
from typing import NamedTuple

TRAILER_KEY = "Registry-Append"
RD = "src/synthetic_ecommerce_data/domains/retail"


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
_WORD_ROW = (r"^\s+_[a-z]\(\s*\d+,", r"^\s+_[a-z]\($")
_WORD_KIND = (r"^NEW_KINDS\.update\(", _KIND_ENTRY)

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
        f"{RD}/decoy_rows.py",
        _shapes(r"^\s+_d\(", _KIND_ENTRY, r"^from decoy_\w+_rows import", r"^\s+\*\(_d\("),
        '    _d("XZ01", "sofa", "Title", "Desc", "Red", 1, "red sofa", 720),',
        _DECOY_FORM,
        _DECOY_FILES,
    ),
    Registry(
        f"{RD}/decoy_product_words.py",
        _shapes(*_WORD_ROW, r"^TABLE = \(\*TABLE, \*(?!feature_decoys\.)", *_WORD_KIND),
        '    _s(99, "s_probe", "Title", "Desc", "Brown", "block", "Yoga Block"),',
        _DECOY_FORM,
        _DECOY_FILES,
    ),
    Registry(
        f"{RD}/decoy_word_table.py",
        _shapes(*_WORD_ROW),
        '    _d(99, "s_probe", "Title", "Desc", "Brown", "block", "Yoga Block", _CAT),',
        _DECOY_FORM,
        _DECOY_FILES,
    ),
    Registry(
        f"{RD}/decoy_word_kinds.py",
        _shapes(*_WORD_KIND),
        '    "probe": Kind("Home", ("Home",), "Cushion", "cushion", "B", 1.0),',
        _DECOY_FORM,
        _DECOY_FILES,
    ),
    Registry(
        "docs/retail-prototype.md",
        _shapes(r"^#{1,6}\s"),
        "### Probe feature (gen#999)",
        "write the feature's section as its own page, docs/retail-prototype/<topic>-<issue>.md;"
        " this page gains no heading",
        ("docs/retail-prototype/pack-scale-543.md",),
    ),
    Registry(
        "docs/retail-product-word-decoys.md",
        _shapes(r"^\|", r"^\*\*[^*\n]+\(gen#\d+\)\.\*\*"),
        "| red sofa | sofa | PLT-XZ01 | Sofa Throw | Throw | category |",
        "the table is built, not pasted: scripts/build_derived.py writes"
        " docs/retail-product-word-decoys-table.md from decoy_product_words.TABLE;"
        " write the feature's section as its own page,"
        " docs/retail-product-word-decoys/<topic>-<issue>.md",
        ("scripts/build_derived.py", "docs/retail-product-word-decoys/cups-620.md"),
    ),
    Registry(
        "tests/test_retail_product_word_decoys_326.py",
        _shapes(r'^\s+"[a-z]+": "[^"]+",'),
        '    "probe": "Probes",',
        "add tests/decoy_true_nodes/<topic>.py with a NODES dict (noun -> the node the noun"
        " really names); tests/decoy_true_nodes/__init__.py finds it by walking the package and"
        " nothing is listed here",
        ("tests/decoy_true_nodes/__init__.py",),
    ),
    Registry(
        f"{RD}/line_grammar.py",
        _shapes(
            r'^\s+"[^"]+": "[a-z]+",',
            r"^\s+\*\*dict\.fromkeys\(",
            r"^[A-Z]+_[A-Z_]+\s*=",
            r'^\s+(el)?if fam == "',
            r"^- [a-z][^:]*:",
        ),
        '    "Kettle": "appliance",',
        f"add {RD}/line_grammar_families/<family>.py exposing KINDS, LEADS, SUBS and NUMBERS (see"
        f" {RD}/line_grammar_families/sport.py); line_grammar finds it by walking the package and"
        " gains no FAMILIES row, vocabulary constant, branch or docstring bullet",
        (f"{RD}/line_grammar_families/__init__.py", f"{RD}/line_grammar_families/sport.py"),
    ),
    Registry(
        "tests/test_retail_scale.py",
        _shapes(r"^def test_\w+\("),
        "def test_a_probe_title_is_numbered(ceiling):",
        "add tests/test_retail_scale_<topic>_<issue>.py, a file of its own that takes the ceiling"
        " build from tests/retail_ceiling.py (ceiling_build()); this file gains no test",
        ("tests/retail_ceiling.py", "tests/test_retail_scale_drawing_params_512.py"),
    ),
    Registry(
        "docs/adding-a-type.md",
        _shapes(r"^#{1,6}\s"),
        "## Nuts by the box (#999)",
        "write the feature's section as its own page, docs/industrial-types/<topic>-<issue>.md;"
        " this guide gains no heading",
        ("docs/industrial-types/plain-screws-750.md",),
    ),
    Registry(
        "docs/retail-catalog-batch-1.md",
        _shapes(r"^#{1,6}\s", r"^\|"),
        "| red sofa | 1 color names a part | PLT-DXZ01 | Blue Sofa with Red Piping | decoy |",
        "the table is built, not pasted: scripts/build_derived.py writes"
        " docs/retail-text-match-decoys-table.md from decoy_rows.TABLE; write the feature's section"
        " as its own page, docs/retail-prototype/<topic>-<issue>.md",
        ("scripts/build_derived.py", "docs/retail-prototype/pack-scale-543.md"),
    ),
    Registry(
        "tests/test_retail_apparel_decoys_311.py",
        _shapes(r"^def test_\w+\(", r'^\s+"[A-Z]\w* [^"]*",'),
        '    "Probe Slippers", "Probe Clogs",',
        "add tests/test_retail_apparel_decoys_<topic>_<issue>.py for a test, taking the build from"
        " tests/retail_ceiling.py, and tests/decoy_real_compounds/<topic>.py with a COMPOUNDS"
        " frozenset for a title; both are found with no line here",
        ("tests/retail_ceiling.py", "tests/decoy_real_compounds/__init__.py"),
    ),
    Registry(
        f"{RD}/details.py",
        _shapes(r'^ {4}"\w+":\s*\{'),
        '    "probe_coat": {"hem": TORSO_HEM},',
        "call details.register_parts(<shape>, {...}) in the type's spec file,"
        f" {RD}/type_specs/<key>.py, beside its kit.register; PARTS gains no entry",
        (f"{RD}/type_registry.py",),
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


def escaped(root: Path, base: str, head: str) -> bool:
    """Whether a non-merge commit in ``base..head`` carries ``Registry-Append: <a reason>``.

    The reason is typed once, on the commit that makes the append; a merge of main or a later
    commit on top of it leaves the trailer where ``git log`` keeps it (gen#646). A merge commit's
    own message does not count: it is not where the append is made.
    """
    fmt = f"--format=%(trailers:key={TRAILER_KEY},valueonly)"
    out = _git(root, "log", "--no-merges", fmt, f"{base}..{head}")
    return any(value.strip() for value in out.split("\n"))


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
        "A change that is not a feature (a helper the build needs) says so on a commit",
        "of the branch, the tip or an earlier one (a merge of main does not drop it):",
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
    if not found or escaped(args.root, args.base, args.head):
        return 0
    print(refusal(found))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
