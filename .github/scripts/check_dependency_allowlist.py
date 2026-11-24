"""The direct-dependency allowlist gate (#16448): the list only shrinks.

``.github/dependency_allowlist.json`` names every direct dependency of every
``pyproject.toml`` and ``package.json`` in the tree, by manifest and group. This
script derives the same data from the tree and refuses:

- (a) a dependency a manifest declares that the list does not name;
- a stale entry (on the list, in no manifest), so the list always equals the
  manifests;
- with ``--base-root`` (the tree at the PR's base): (b) an entry the base's list
  did not have, and (c) an entry count above the base's, or a ``uv.lock`` or
  ``package-lock.json`` with more packages than the base's, unless ``--labels``
  holds ``dependency-approved``, the maintainer's approval.

A lock's packages are counted from the two trees, never recorded in the list: a
recorded total is right only for the lock it was counted from, so another PR's
merge makes it wrong with no conflict (#16760).

Every refusal names the dependency (or lock) and what to do. ``--write``
rewrites the list from the tree. Standard library only, so the CI job installs
nothing. The rule and how to clear a red: contributing/dependency-allowlist.md.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tomllib
from collections.abc import Iterator, Sequence
from pathlib import Path

ALLOWLIST = ".github/dependency_allowlist.json"
APPROVAL_LABEL = "dependency-approved"
# This script's path in elastic/prism, and in the generator's byte-for-byte copy.
SCRIPT = ".github/scripts/check_dependency_allowlist.py"
WRITE_COMMAND = f"python3 {SCRIPT} --write"


def about(command: str) -> str:
    """The list's ``about`` line, naming the command that regenerates it."""
    return (
        "Every direct dependency of this repo by manifest and group (#16448). CI "
        "refuses a manifest entry not listed here, a stale one, and a new entry or a "
        f"lock with more packages without the PR label {APPROVAL_LABEL}. "
        f"Regenerate: {command}. "
        "Rule: contributing/dependency-allowlist.md."
    )


ABOUT = about(WRITE_COMMAND)


def write_command(root: Path, allowlist: str) -> str:
    """The command that rewrites ``allowlist`` from ``root``'s tree.

    A tree that holds this script (elastic/prism, the generator's copy) runs its
    own; a sister calling the reusable workflow holds none, so it runs core's
    from a checkout of elastic/prism, on its own root.
    """
    flag = "" if allowlist == ALLOWLIST else f" --allowlist {allowlist}"
    if (root / SCRIPT).is_file():
        return f"python3 {SCRIPT}{flag} --write"
    return f"python3 <a checkout of elastic/prism>/{SCRIPT} --root .{flag} --write"


# Tool state, never a manifest of the repo's own: a clone's history, a
# virtualenv, an agent's scratch and installed packages. Every other directory,
# hidden or not (.github, .devcontainer, .tools), is read: CI can install from it.
PRUNED = frozenset({".git", ".venv", ".agent", "node_modules"})
MANIFESTS = frozenset({"pyproject.toml", "package.json"})
LOCKS = frozenset({"uv.lock", "package-lock.json"})
NPM_GROUPS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)
_NAME = re.compile(r"\s*([A-Za-z0-9][A-Za-z0-9._-]*)")

# (manifest, group, name): one entry of the list.
Entry = tuple[str, str, str]


def _files(root: Path) -> Iterator[Path]:
    """Every manifest and lock under ``root``, outside the ``PRUNED`` directories."""
    for here, dirs, names in os.walk(root):
        dirs[:] = sorted(d for d in dirs if d not in PRUNED)
        for name in sorted(names):
            if name in MANIFESTS or name in LOCKS:
                yield Path(here) / name


def _pep503(requirement: str) -> str:
    match = _NAME.match(requirement)
    if match is None:
        raise ValueError(f"cannot read a package name from requirement {requirement!r}")
    return re.sub(r"[-_.]+", "-", match.group(1)).lower()


def _python_groups(data: dict) -> dict[str, list[str]]:
    project = data.get("project", {})
    groups: dict[str, list] = {
        "build-system.requires": data.get("build-system", {}).get("requires", []),
        "project.dependencies": project.get("dependencies", []),
        "tool.uv.dev-dependencies": data.get("tool", {})
        .get("uv", {})
        .get("dev-dependencies", []),
    }
    for extra, requirements in project.get("optional-dependencies", {}).items():
        groups[f"project.optional-dependencies.{extra}"] = requirements
    for group, requirements in data.get("dependency-groups", {}).items():
        groups[f"dependency-groups.{group}"] = requirements
    # A ``{include-group = ...}`` table names another group, not a package.
    return {
        g: sorted({_pep503(r) for r in reqs if isinstance(r, str)})
        for g, reqs in groups.items()
    }


def _npm_groups(data: dict) -> dict[str, list[str]]:
    return {group: sorted(data.get(group, {})) for group in NPM_GROUPS}


def _lock_count(path: Path) -> int:
    if path.name == "uv.lock":
        return len(tomllib.loads(path.read_text()).get("package", []))
    # The "" key of a v2/v3 package-lock is the root project itself.
    return len([key for key in json.loads(path.read_text()).get("packages", {}) if key])


def derive(root: Path, command: str = WRITE_COMMAND) -> dict:
    """The list as the tree has it: only non-empty groups and manifests."""
    manifests: dict[str, dict[str, list[str]]] = {}
    for path in _files(root):
        if path.name in LOCKS:
            continue
        rel = path.relative_to(root).as_posix()
        if path.name == "pyproject.toml":
            groups = _python_groups(tomllib.loads(path.read_text()))
        else:
            groups = _npm_groups(json.loads(path.read_text()))
        kept = {group: names for group, names in sorted(groups.items()) if names}
        if kept:
            manifests[rel] = kept
    return {"about": about(command), "manifests": manifests}


def lock_counts(root: Path) -> dict[str, int]:
    """The packages each lock of the tree holds."""
    return {
        path.relative_to(root).as_posix(): _lock_count(path)
        for path in _files(root)
        if path.name in LOCKS
    }


def entries(allowlist: dict) -> set[Entry]:
    return {
        (manifest, group, name)
        for manifest, groups in allowlist.get("manifests", {}).items()
        for group, names in groups.items()
        for name in names
    }


def _describe(entry: Entry) -> str:
    manifest, group, name = entry
    return f"`{name}` ({manifest}, {group})"


def consistency(
    listed: dict,
    tree: dict,
    allowlist: str = ALLOWLIST,
    command: str = WRITE_COMMAND,
) -> list[str]:
    """Refusals where the list and the tree differ: (a) and stale entries."""
    problems: list[str] = []
    on_list, in_tree = entries(listed), entries(tree)
    for entry in sorted(in_tree - on_list):
        problems.append(
            f"{_describe(entry)} is a direct dependency that {allowlist} does not list. "
            f"Remove it from the manifest, or add it with `{command}` and ask the "
            f"maintainer for the `{APPROVAL_LABEL}` label on this PR."
        )
    for entry in sorted(on_list - in_tree):
        problems.append(
            f"{_describe(entry)} is on {allowlist} but in no manifest: a stale entry. "
            f"Remove it from the list (`{command}`), so the count goes down."
        )
    return problems


def growth(listed: dict, base: dict, allowlist: str = ALLOWLIST) -> list[str]:
    """Refusals of what the list gained over the base's list: (b) and (c)'s entries."""
    problems: list[str] = []
    for entry in sorted(entries(listed) - entries(base)):
        problems.append(
            f"{_describe(entry)} is a new entry on {allowlist}, and this PR has no "
            f"`{APPROVAL_LABEL}` label. Drop the dependency, or ask the maintainer to add the label."
        )
    head_total, base_total = len(entries(listed)), len(entries(base))
    if head_total > base_total:
        problems.append(
            f"{allowlist} names {head_total} direct dependencies, up from the base's {base_total}; "
            f"the count only goes down without the `{APPROVAL_LABEL}` label."
        )
    return problems


def lock_growth(locks: dict[str, int], base_locks: dict[str, int]) -> list[str]:
    """Refusals of a lock that holds more packages than the base's: (c)'s locks."""
    return [
        f"lock `{lock}` rises to {count} packages from the base's {base_locks.get(lock, 0)}; "
        f"cut the dependency that pulls the new packages in, or ask the maintainer for the "
        f"`{APPROVAL_LABEL}` label."
        for lock, count in sorted(locks.items())
        if count > base_locks.get(lock, 0)
    ]


def summary(listed: dict, locks: dict[str, int], compared: bool) -> str:
    lines = [
        "## Direct-dependency allowlist (#16448)",
        "",
        "| lock | packages |",
        "| --- | --- |",
    ]
    lines += [f"| `{lock}` | {count} |" for lock, count in sorted(locks.items())]
    lines += ["", f"Direct dependencies on the list: {len(entries(listed))}."]
    if not compared:
        lines.append(
            "No base tree with a list was given, so new entries and raised counts were not compared "
            "(only a pull_request run, which can read the PR's labels, compares them)."
        )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--base-root", type=Path, help="the tree at the PR's base")
    parser.add_argument("--labels", default="", help="the PR's labels, comma-separated")
    parser.add_argument(
        "--allowlist",
        default=ALLOWLIST,
        help="the list's path under --root (a sister names its own)",
    )
    parser.add_argument(
        "--write", action="store_true", help="rewrite the list from the tree"
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    command = write_command(root, args.allowlist)
    tree = derive(root, command)
    path = root / args.allowlist
    if args.write:
        path.write_text(json.dumps(tree, indent=2) + "\n")
        print(
            f"wrote {args.allowlist}: {len(entries(tree))} entries, locks {lock_counts(root)}"
        )
        return 0
    listed = json.loads(path.read_text())
    problems = consistency(listed, tree, args.allowlist, command)
    locks = lock_counts(root)
    labels = {label.strip() for label in args.labels.split(",")}
    # A base with no list is the PR that adds it: there is nothing to compare.
    compared = (
        args.base_root is not None and (args.base_root / args.allowlist).is_file()
    )
    if compared and APPROVAL_LABEL not in labels:
        base = json.loads((args.base_root / args.allowlist).read_text())
        problems += growth(listed, base, args.allowlist)
        problems += lock_growth(locks, lock_counts(args.base_root))
    print(summary(listed, locks, compared))
    for problem in problems:
        print(f"::error::{problem}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
