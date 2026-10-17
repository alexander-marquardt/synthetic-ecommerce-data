#!/usr/bin/env python3
"""No customer name in this repository: the tree, the commits, the pull request (#393).

    uv run python scripts/check_customer_names.py                          # the tree
    uv run python scripts/check_customer_names.py --range origin/main..HEAD  # + commit messages
    uv run python scripts/check_customer_names.py --pr 17    # + the live PR title and body
    uv run python scripts/check_customer_names.py --text-file body.md  # + a draft PR body

``--pr`` takes a pull request number or a head branch, as ``gh pr view`` does.

The tree is every tracked file and every untracked one ``.gitignore`` does not
hide: the file's PATH, and its CONTENT when it is text. A file that is not text
(it does not decode as UTF-8 and holds a NUL byte, such as an image) is scanned
by its path only, and the run NAMES it. A file that decodes and holds a NUL byte
is text and is scanned: one NUL byte hides a whole file from a plain ``grep``,
and must not hide it here.

This is the generator half of elastic/prism-industrial-products#88, whose script
it copies: change one, change the other.

THE LIST IS CORE'S, NOT A COPY. The names are ``CUSTOMER_NAME_SPECS`` in
elastic/prism's ``.github/scripts/audit_grep_diff.py``, vendored byte for byte
under ``vendor/prism/`` (``vendor/prism/PIN.txt``; ``docs/customer-name-check.md``
has the resync). This file holds no pattern. A content hit is reported as the
place and the row, never the line, so the log of a failed run does not carry the
name it exists to keep out; a path hit has to show the path.

Exit status: 0 clean, 1 a hit, 2 a usage error, 3 could not judge (a ``gh`` that
did not answer, a range git cannot resolve, a file that cannot be read). A run
that could not judge is never a pass.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from functools import partial
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
VENDOR = REPO_ROOT / "vendor" / "prism"

sys.path.insert(0, str(VENDOR / ".github" / "scripts"))
import audit_grep_diff as core  # noqa: E402  (the vendored path is set up just above)

#: Core's list, as ``(label, obfuscated regex)`` rows. Read, never copied.
SPECS = core.CUSTOMER_NAME_SPECS

EXIT_CLEAN, EXIT_HIT, EXIT_USAGE, EXIT_UNJUDGED = 0, 1, 2, 3

#: ``<rev>..<rev>`` and nothing else: a path, a bare rev and ``a...b`` are refused.
_RANGE = re.compile(r"([^\s.\-][^\s]*?)\.\.([^\s.\-][^\s]*)")


class CouldNotJudge(Exception):
    """A surface could not be read; the run is not a pass."""


@dataclass(frozen=True)
class Found:
    where: str
    label: str


@dataclass
class Scan:
    hits: list[Found]
    files: int = 0
    commits: int = 0
    texts: int = 0
    binary: list[str] | None = None

    def __post_init__(self) -> None:
        if self.binary is None:
            self.binary = []


def labels_in(line: str) -> list[str]:
    """The rows of core's list that match one line of text, in list order."""
    seen: list[str] = []
    for hit in core.scan_text_for_customer_names(line, "<line>"):
        if hit.pattern_label not in seen:
            seen.append(hit.pattern_label)
    return seen


def scan_lines(text: str, where: str) -> list[Found]:
    """Every row of the list that matches a line of ``text``, at ``where:line``."""
    found: list[Found] = []
    for number, line in enumerate(text.split("\n"), start=1):
        found.extend(Found(f"{where}:{number}", label) for label in labels_in(line))
    return found


def _git(root: Path, *args: str) -> bytes:
    try:
        done = subprocess.run(
            ["git", "-C", str(root), *args], capture_output=True, check=False
        )
    except OSError as err:
        raise CouldNotJudge(f"git did not run: {err}") from err
    if done.returncode != 0:
        detail = done.stderr.decode("utf-8", "replace").strip()
        raise CouldNotJudge(f"`git {' '.join(args)}` failed: {detail}")
    return done.stdout


def tree_paths(root: Path) -> list[str]:
    """Tracked files plus untracked ones that are not ignored, that exist on disk."""
    raw = _git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard")
    names = sorted(
        {p.decode("utf-8", "surrogateescape") for p in raw.split(b"\0") if p}
    )
    return [n for n in names if (root / n).is_file() or (root / n).is_symlink()]


def read_text(path: Path) -> str | None:
    """The file's text, or ``None`` for a file that is not text (see the module doc)."""
    try:
        data = path.read_bytes()
    except OSError as err:
        raise CouldNotJudge(f"cannot read {path}: {err}") from err
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        if b"\0" in data:
            return None
        return data.decode("utf-8", "replace")


def scan_tree(root: Path, scan: Scan) -> None:
    for name in tree_paths(root):
        shown = name.encode("utf-8", "replace").decode("utf-8")
        scan.hits.extend(
            Found(f"{shown} (file name)", label) for label in labels_in(shown)
        )
        path = root / name
        if path.is_symlink():
            continue
        scan.files += 1
        text = read_text(path)
        if text is None:
            assert scan.binary is not None
            scan.binary.append(shown)
            continue
        scan.hits.extend(scan_lines(text, shown))


def check_range(spec: str) -> tuple[str, str]:
    match = _RANGE.fullmatch(spec)
    if match is None:
        raise ValueError(
            f"--range takes a git range `<rev>..<rev>`, not {spec!r}: a path or a "
            "bare rev is not a range, and a tool handed one scanned the wrong commits"
        )
    return match.group(1), match.group(2)


def scan_commits(root: Path, spec: str, scan: Scan) -> None:
    for rev in check_range(spec):
        _git(root, "rev-parse", "--verify", "--quiet", f"{rev}^{{commit}}")
    raw = _git(root, "log", "--format=%H%x1f%B%x1e", spec).decode("utf-8", "replace")
    for record in raw.split("\x1e"):
        if not record.strip():
            continue
        sha, _, message = record.strip("\n").partition("\x1f")
        scan.commits += 1
        scan.hits.extend(scan_lines(message.strip("\n"), f"commit {sha.strip()[:12]}"))


def live_pull_request(number: str) -> dict[str, str]:
    """The PR's title and body, read from the API now, not from the event payload."""
    try:
        done = subprocess.run(
            ["gh", "pr", "view", number, "--json", "title,body"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as err:
        raise CouldNotJudge(
            f"gh did not answer for pull request {number}: {err}"
        ) from err
    if done.returncode != 0:
        raise CouldNotJudge(
            f"gh pr view {number} failed ({done.returncode}): {done.stderr.strip()}"
        )
    try:
        payload = json.loads(done.stdout)
        return {
            "title": str(payload["title"] or ""),
            "body": str(payload["body"] or ""),
        }
    except (ValueError, KeyError, TypeError) as err:
        raise CouldNotJudge(
            f"gh pr view {number} gave no title and body: {err}"
        ) from err


def scan_pull_request(number: str, scan: Scan) -> None:
    payload = live_pull_request(number)
    for part in ("title", "body"):
        scan.texts += 1
        scan.hits.extend(scan_lines(payload[part], f"pull request {number} {part}"))


def scan_text_file(path: str, scan: Scan) -> None:
    text = read_text(Path(path))
    if text is None:
        raise CouldNotJudge(f"{path} is not text")
    scan.texts += 1
    scan.hits.extend(scan_lines(text, path))


def _n(count: int, noun: str) -> str:
    return f"{count} {noun}" if count == 1 else f"{count} {noun}s"


def render(scan: Scan) -> str:
    out: list[str] = []
    for hit in scan.hits:
        out.append(f"customer-name-check: HIT {hit.where} [{hit.label}]")
    if scan.binary:
        out.append(
            "customer-name-check: not scanned for content (not text; the file name was "
            f"scanned): {', '.join(scan.binary)}"
        )
    counted = (
        f"{_n(scan.files, 'file')}, {_n(scan.commits, 'commit')}, "
        f"{_n(scan.texts, 'text')} scanned"
    )
    if scan.hits:
        out.append(
            f"customer-name-check: FAIL {_n(len(scan.hits), 'hit')} ({counted}). "
            "Reword it to the neutral term the tree uses; a commit message is "
            "reworded with a rebase, a PR "
            "title or body with an edit and a re-run. Row labels name the row of "
            "elastic/prism's CUSTOMER_NAME_SPECS, in vendor/prism/.github/scripts/"
            "audit_grep_diff.py."
        )
    else:
        out.append(f"customer-name-check: OK - {counted}")
    return "\n".join(out) + "\n"


def parse(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    parser.add_argument("--range", dest="rev_range", default="")
    parser.add_argument(
        "--pr",
        default="",
        help="a pull request number or head branch, as `gh pr view` takes it; empty means none",
    )
    parser.add_argument("--text-file", action="append", default=[])
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse(argv)
    scan = Scan(hits=[])
    try:
        if args.rev_range:
            check_range(args.rev_range)
    except ValueError as err:
        sys.stderr.write(f"check_customer_names: {err}\n")
        return EXIT_USAGE
    unjudged: list[str] = []

    def attempt(surface: str, step: Callable[[], None]) -> None:
        try:
            step()
        except CouldNotJudge as err:
            unjudged.append(f"{surface}: {err}")

    attempt("the tree", lambda: scan_tree(args.root, scan))
    if args.rev_range:
        attempt(
            "the commit messages",
            lambda: scan_commits(args.root, args.rev_range, scan),
        )
    if args.pr:
        attempt("the pull request", lambda: scan_pull_request(args.pr, scan))
    for path in args.text_file:
        attempt(f"the text file {path}", partial(scan_text_file, path, scan))
    sys.stdout.write(render(scan))
    for reason in unjudged:
        sys.stderr.write(f"customer-name-check: could not judge {reason}\n")
    if scan.hits:
        return EXIT_HIT
    return EXIT_UNJUDGED if unjudged else EXIT_CLEAN


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
