#!/usr/bin/env python3
"""Refuse a source or docs file that grows past the line cap (issue #10021).

Every file the gate measures (:data:`SCOPE`, ``MEASURED_SUFFIXES``) may hold
at most the cap's number of lines. The cap is the one number checked in, in
``scripts/file_size_cap.txt``. Why it is that number, and what the gate cannot
see, are documented once in ``contributing/file-size-budget.md``; this
docstring states what the CHECK does.

The one rule
------------
A measured file that is over the cap may not have more lines than it had at
the merge base of ``--base`` and ``HEAD``. A file that is new counts as zero
there, so a new file over the cap and a file the change pushed across the cap
are both growth. A file that was over the cap at the merge base and did not
grow passes: the base already held it.

Growth is allowed only when the pull-request body carries
``File-Size-Exception: `<path>` - <reason>`` for that file. A cap higher than
the merge base's needs ``File-Size-Exception: cap - <reason>``. The body is
read as GitHub RENDERS it, through the reader of the docs-impact gate
(``.github/scripts/check_docs_impact.py``), so a line in an HTML comment or a
fenced block is not a declaration. It is rendered only when something grew
and the body holds the label at all (a spent REST quota refuses the render, #11059).
With no ``--pr-body-file`` a growth is refused: nothing declared it.

No per-file number is checked in (#10271). A list that every growing or
shrinking change edited made two queued pull requests conflict on neighbouring
lines; the merge base already records each file's size, and a second change
is measured from the main the first one grew.

A rename (``git diff -M`` from the merge base) is the same file: it is
measured from the old path's size there.

The CLAUDE.md byte cap (#10596)
-------------------------------
When the cap file carries ``root-guide-bytes <n>``, a ``CLAUDE.md`` over n bytes
that holds more bytes than at the merge base is refused. Every session loads
that file before its first message, so its size is paid on every call. No
path exception clears it: the cap is raised, with
``File-Size-Exception: root-guide-bytes - <reason>``, or the text moves out.
Raising or dropping the line needs that exception, as a raised ``cap`` does;
lowering it needs nothing. An ``@path`` import in that file is refused whatever
the cap: the cap measures the file, while the import loads another file into
every session.

The hub byte cap (#10104)
-------------------------
``hub-bytes <n>`` holds ``CONTRIBUTING.md`` to the same rule: over n bytes and
larger than at the merge base is refused, no path exception clears it, and
raising or dropping the line needs ``File-Size-Exception: hub-bytes - <reason>``.
Each chapter that moves out of the hub into ``contributing/`` lowers n to the
size it leaves, so the text cannot grow back.

``audit-grep`` passes the event's base: under ``pull_request`` the first
parent of GitHub's merge commit (``HEAD^1``, the main the merge was built on),
and under ``merge_group`` the ``merge_group`` base SHA, the queue candidate's
parent. ``tests/test_file_size_ratchet.py`` runs the check over the repository
on the ES-free lane with ``--base HEAD``, since that checkout is shallow.

``--list`` prints every measured file over the cap with its size, largest
first, and gates nothing.

A generated file is exempt when the root ``.ignore`` hides it AND
``scripts/generated_paths.py`` derives it from a generator's own output list.
Hiding a hand-written file in ``.ignore`` exempts nothing: it is still
measured. The ``.ignore`` match is git's own
(``git ls-files -i --exclude-from=.ignore``), the same gitignore semantics
ripgrep applies to that file. The suffix list and the generated paths live in
that module because the ``.ignore`` coverage test (#10025) reads the same ones.

Untracked files that ``.gitignore`` does not hide are measured too, so a new
file reds before it is committed.

Reported, not gated (#10020)
----------------------------
Each run prints the line count of ``CONTRIBUTING.md``, its BYTE size against
its size at the merge base (bytes/4 is the token proxy; the 10-02 ruling on
#10020 freezes the hub while it is cut into topic files), and the total of
the hand-written files under ``contributing/``. A hub that grew is printed as
a finding; no number is checked in for it, the merge base records it. When
the cap file carries ``prose-line-cap <n>``, an ADDED or EDITED markdown prose
line over n characters in :data:`PROSE_SCOPE` is a finding too; a table row,
a fenced code line, a line the change removed elsewhere (a verbatim move) and
an edit of a line that was already over the cap are exempt.

Both PRINT their findings under ``REPORT-ONLY`` and never change the exit
status; #10203 decides when they gate. A report that cannot be computed (git
fails on the docs diff, a file cannot be read) prints one line saying so, and
the run goes on to the verdict on the line cap. Raising the prose cap, or dropping its
line, is judged like a raised ``cap``: it needs
``File-Size-Exception: prose-line-cap - <reason>``. ``--list`` reads no merge
base, and says so instead of printing a base size.

Exit status
-----------
* 0 -- no over-cap file grew and the cap was not raised, or each such growth
  has its exception line.
* 1 -- an over-cap file grew, or the cap was raised, with no well-formed
  exception line for it; or ``CLAUDE.md`` grew past its byte cap; or the tree
  holds the retired per-file list.
* 4 -- only with ``--no-body-is-advisory`` and no ``--pr-body-file``: growth
  that an exception line could clear, and no body to read one from. The
  pre-push gate reports it as a warning before the pull request exists
  (#10422). The retired list and ``CLAUDE.md`` over its byte cap are still 1,
  and a body, when given, is judged as without the flag.
* 3 -- the check could not judge: the cap file or ``.ignore`` is missing or
  malformed, git could not list the tree, the base had no merge base with
  ``HEAD``, the body file did not resolve, or the renderer was unreachable.
  Never reported as clean.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# The rendered-body reader lives with the docs-impact gate; imported, not copied.
_GITHUB_SCRIPTS = REPO_ROOT / ".github" / "scripts"
if str(_GITHUB_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_GITHUB_SCRIPTS))

from check_docs_impact import (  # noqa: E402  (path is set up just above)
    _blocks,
    _Element,
)
from check_review_verdict import (  # noqa: E402
    Renderer,
    Unrenderable,
    _run_gh,
    gh_renderer,
    parse_html,
    render_when_labelled,
)
from efficiency_ratchet import (  # noqa: E402  (path is set up just above)
    BASELINES_RELATIVE,
    METRICS,
    Unreadable,
    raised_baselines,
)

# Which files are generated, and the measured suffixes: shared with the .ignore
# coverage test, so the two can never disagree (#10021, #10025).
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pr_body_draft  # noqa: E402  (path is set up just above)
from generated_paths import (  # noqa: E402  (path is set up just above)
    MEASURED_SUFFIXES,
    generated_paths,
    has_suffix,
)
from working_tree_subject import (  # noqa: E402  (path is set up just above)
    ls_files,
    read_bytes_if_present,
    read_if_present,
    working_tree_files,
)

CAP_RELATIVE = "scripts/file_size_cap.txt"
IGNORE_RELATIVE = ".ignore"

#: The per-file list this gate read before #10271. A branch that edited it meets
#: a conflict when it merges main, and keeping the file resolves that conflict
#: while bringing back the list two queued changes collide on, so a tree that
#: holds it is refused.
RETIRED_RELATIVE = "scripts/file_size_ratchet.txt"

#: The exception target that declares a raised cap.
CAP_TARGET = "cap"
#: The exception target that declares a raised or dropped prose-line cap (#10020).
PROSE_CAP_TARGET = "prose-line-cap"
#: The exception target that declares a raised or dropped CLAUDE.md byte cap (#10596).
#: It names the file's role, the repository's root guide, rather than the file:
#: a PR body that names the token must not need a vendor-name justification.
ROOT_GUIDE_CAP_TARGET = "root-guide-bytes"
#: The exception target that declares a raised or dropped hub byte cap (#10104).
HUB_CAP_TARGET = "hub-bytes"
#: The file every session loads before its first message; held to a byte cap (#10596).
CLAUDE_MD = "CLAUDE.md"
#: The agent definitions together, held to a shrink-only byte cap like
#: CLAUDE.md's (#10361): an agent loads its definition on every call.
AGENT_GUIDES_CAP_TARGET = "agent-guide-bytes"
AGENT_GUIDES_DIR = ".claude/agents"
#: Where an ADDED or EDITED prose line is held to the prose-line cap: the
#: markdown the rulebook and the docs are written in (#10020). A table row is
#: exempt, because grep returns whole lines and a row cannot be wrapped; so is a
#: fenced code line, and a line the same change removed elsewhere (a verbatim move).
PROSE_SCOPE: tuple[str, ...] = (
    "CONTRIBUTING.md",
    "CLAUDE.md",
    ":(glob)contributing/**/*.md",
    ":(glob)docs/**/*.md",
)

#: The same slot and the same value as ``audit_grep_diff.ADVISORY_EXIT_STATUS``:
#: the run judged the tree, and what it found is for the author to act on rather
#: than a refusal. Only ``--no-body-is-advisory`` with no body can produce it.
ADVISORY_EXIT_STATUS = 4

#: Where the gate measures, as git pathspecs: the package sources, the scripts,
#: the front end's source (its tests included: they are read like any source),
#: and the docs and contributor guides. ``tests/`` is outside it for now.
SCOPE: tuple[str, ...] = (
    ":(glob)packages/*/src/**",
    ":(glob)scripts/**",
    ":(glob).github/scripts/**",
    ":(glob)search-ui/src/**",
    ":(glob)docs/**",
    ":(glob)contributing/**",
)

#: Printed every run, never gated: the hub's lines and bytes (#10020), the dir's lines.
REPORTED_FILE = "CONTRIBUTING.md"
REPORTED_DIR = "contributing/"

_CAP_RE = re.compile(r"^cap (?P<cap>[1-9]\d*)$")
_PROSE_CAP_RE = re.compile(r"^prose-line-cap (?P<cap>[1-9]\d*)$")
#: One parsing path for every ``<name>-bytes <n>`` line (#10596, #10104, #10361).
_BYTE_CAP_RE = re.compile(
    rf"^(?P<target>{ROOT_GUIDE_CAP_TARGET}|{AGENT_GUIDES_CAP_TARGET}|{HUB_CAP_TARGET})"
    r" (?P<cap>[1-9]\d*)$"
)
_FENCE_RE = re.compile(r"^\s*(?:```|~~~)")
#: An ``@path`` import in CLAUDE.md: an ``@`` opening a token, then a non-space.
_IMPORT_RE = re.compile(r"(?:^|(?<=\s))@(?=\S)")
_CODE_SPAN_RE = re.compile(r"(`+).*?\1")
_HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(?P<start>\d+)(?:,(?P<count>\d+))? @@")
_LABEL_RE = re.compile(r"^\s*file-size-exception\s*:(?P<rest>.*)$", re.IGNORECASE)
#: The label's name anywhere in the body as written, colon or no colon (``**label**:``
#: renders to a line that reads). A body without it is not rendered
#: (:func:`render_when_labelled`): the Markdown API spends the shared REST quota.
_RAW_LABEL_RE = re.compile(r"file-size-exception", re.IGNORECASE)
_EXCEPTION_RE = re.compile(r"^\s*(?P<target>\S+)\s+(?:—|–|--?)\s*(?P<reason>.*?)\s*$")
_HAS_CONTENT_RE = re.compile(r"[^\W_]")


class CouldNotJudge(Exception):
    """The inputs could not be read; the verdict is UNKNOWN, never clean."""


#: What a report-only computation may raise and still not reach the exit status:
#: this script's own refusal, the file system, a decode or parse, a lookup, git.
REPORT_FAILURES: tuple[type[Exception], ...] = (
    CouldNotJudge,
    OSError,
    ValueError,
    LookupError,
    subprocess.SubprocessError,
)


@dataclass(frozen=True)
class Caps:
    """What the cap file holds: the line cap, and the prose-line cap when set."""

    lines: int
    #: Characters an ADDED or EDITED prose line may hold; ``None``: not reported.
    prose: int | None = None
    #: Bytes :data:`CLAUDE_MD` may hold; ``None``: not capped.
    root_guide: int | None = None
    #: Bytes the agent definitions may hold together (#10361); ``None``: not capped.
    agent_guides: int | None = None
    #: Bytes :data:`REPORTED_FILE`, the hub, may hold; ``None``: not capped (#10104).
    hub: int | None = None

    def byte_caps(self) -> dict[str, int | None]:
        """``{target: bytes}`` for each byte-capped file set (see :func:`byte_sums`)."""
        return {
            ROOT_GUIDE_CAP_TARGET: self.root_guide,
            AGENT_GUIDES_CAP_TARGET: self.agent_guides,
        }

    def raisable(self) -> dict[str, int | None]:
        """Each byte cap a change may raise or drop only with its own exception line."""
        return {**self.byte_caps(), HUB_CAP_TARGET: self.hub}


#: A byte cap's field on :class:`Caps`.
_BYTE_CAP_FIELDS = {
    ROOT_GUIDE_CAP_TARGET: "root_guide",
    AGENT_GUIDES_CAP_TARGET: "agent_guides",
    HUB_CAP_TARGET: "hub",
}


def parse_cap(text: str) -> Caps:
    """The caps from the cap file: comments and blank lines, one ``cap <n>``, and
    at most one each of ``prose-line-cap <n>`` and the three byte caps
    (``root-guide-bytes``, ``agent-guide-bytes``, ``hub-bytes``); any other line
    is malformed."""
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    cap: int | None = None
    prose: int | None = None
    byte_caps: dict[str, int] = {}
    for line in lines:
        as_cap = _CAP_RE.match(line)
        if as_cap is not None and cap is None:
            cap = int(as_cap.group("cap"))
            continue
        as_prose = _PROSE_CAP_RE.match(line)
        if as_prose is not None and prose is None:
            prose = int(as_prose.group("cap"))
            continue
        as_bytes = _BYTE_CAP_RE.match(line)
        if as_bytes is not None and as_bytes.group("target") not in byte_caps:
            byte_caps[as_bytes.group("target")] = int(as_bytes.group("cap"))
            continue
        cap = None
        break
    if cap is None:
        raise CouldNotJudge(
            f"{CAP_RELATIVE} must hold exactly one 'cap <lines>' line, and at most "
            "one 'prose-line-cap <characters>' line and one each of the "
            "'root-guide-bytes', 'agent-guide-bytes' and 'hub-bytes' lines, besides "
            "comments"
        )
    return Caps(
        lines=cap,
        prose=prose,
        **{_BYTE_CAP_FIELDS[target]: n for target, n in byte_caps.items()},
    )


# ---------------------------------------------------------------------------
# Measuring the tree
# ---------------------------------------------------------------------------


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(  # noqa: S603  # argv is the literal "git" "-C", then root (the repository Path main resolved) and args: the ls-files, ls-tree, show and merge-base literals plus SCOPE and a revision merge_base refuses when it opens with a dash
        ["git", "-C", str(root), *args],  # noqa: S607  # the literal "git" is resolved on PATH, as audit-grep runs it; root and args are named on the S603 line above
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CouldNotJudge(
            f"git {' '.join(args[:2])} failed ({completed.stderr.strip() or completed.returncode})"
        )
    return completed.stdout


def _git_content(root: Path, *args: str) -> str:
    """git's output for a call that returns FILE CONTENT, decoded leniently.

    :func:`_git` decodes strictly and reads a lone CR as a line end. That suits
    the revisions and path names its callers read, and not a diff: a docs line
    may hold any byte, and git ends a line at LF only.
    """
    completed = subprocess.run(  # noqa: S603  # argv is the literal "git" "-C", then root (the repository Path main resolved) and args: the diff literals, the commit merge_base resolved and PROSE_SCOPE
        ["git", "-C", str(root), *args],  # noqa: S607  # the literal "git" is resolved on PATH; root and args are named on the S603 line above
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CouldNotJudge(f"git {' '.join(args[:3])} failed ({completed.returncode})")
    return completed.stdout.decode("utf-8", errors="replace")


def _listed(root: Path, *args: str, present: bool = False) -> set[str]:
    # The shared enumerator (#8040) takes the options ahead of the pathspec
    # separator, so -c/-o/-i and --exclude-from reach git unchanged.
    try:
        enumerate_paths = working_tree_files if present else ls_files
        paths = enumerate_paths(*args, "--", *SCOPE, root=root)
    except subprocess.CalledProcessError as error:
        raise CouldNotJudge(
            f"listing the tree failed ({error.stderr or error.returncode})"
        ) from error
    return {path for path in paths if has_suffix(path, MEASURED_SUFFIXES)}


def exempt_files(root: Path) -> set[str]:
    """The files in scope that ``.ignore`` hides AND a generator writes."""
    ignore = root / IGNORE_RELATIVE
    if not ignore.is_file():
        raise CouldNotJudge(
            f"{IGNORE_RELATIVE} is missing; it is the generated-file list"
        )
    hidden = _listed(root, "-c", "-o", "-i", f"--exclude-from={ignore}")
    return hidden & generated_paths(root)


def renamed_from(root: Path, base: str, head: str | None = None) -> dict[str, str]:
    """``{new path: old path}`` for each file renamed from ``base`` to ``head``.

    ``head`` ``None`` compares with the working tree. Rename detection is git's
    own (``-M``, 50% similarity), so a renamed file that also changed is still
    the same file.

    Only a rename from a path the gate measured counts. The old path's size was
    held to the cap only if it sat in ``SCOPE`` with a measured suffix; a file
    moved in from anywhere else is new, or the move would bring an over-cap file
    in with nothing said. ``SCOPE`` limits the diff, so git pairs no path
    outside it, and the suffix is checked here.
    """
    out = _git(
        root,
        "diff",
        "-M",
        "--name-status",
        "-z",
        "--diff-filter=R",
        base,
        *([head] if head is not None else []),
        "--",
        *SCOPE,
    )
    fields = out.split("\0")
    renames: dict[str, str] = {}
    at = 0
    while at + 2 < len(fields) and fields[at]:
        if has_suffix(fields[at + 1], MEASURED_SUFFIXES):
            renames[fields[at + 2]] = fields[at + 1]
        at += 3
    return renames


def merge_base(root: Path, base: str) -> str:
    """The commit the change is measured from: the merge base of ``base`` and HEAD.

    In CI that is the event's base itself, because the checked-out commit
    descends from it; locally it is where the branch left ``origin/main``.
    """
    if base.startswith("-"):
        raise CouldNotJudge(f"{base!r} is not a revision")
    try:
        return _git(root, "merge-base", base, "HEAD").strip()
    except CouldNotJudge as error:
        raise CouldNotJudge(
            f"{error}; pass --base with a revision HEAD shares history with"
        ) from error


def sizes_at(
    root: Path,
    revision: str,
    paths: set[str],
    count: Callable[[bytes], int] | None = None,
) -> dict[str, int]:
    """``{path: count(blob)}`` at ``revision`` for each of ``paths`` that is a file
    there: lines by default, bytes with ``count=len`` (the hub's reported size, #10020).

    One ``cat-file --batch`` for every path, rather than a ``git show`` each:
    the tree holds over a hundred files past the cap.
    """
    wanted = sorted(paths)
    request = "".join(f"{revision}:{path}\n" for path in wanted).encode()
    completed = subprocess.run(  # noqa: S603  # argv is the literal "git" "-C", then root and the cat-file literals; the revision merge_base resolved and the tree's paths go in on stdin
        ["git", "-C", str(root), "cat-file", "--batch"],  # noqa: S607  # the literal "git" is resolved on PATH; root is named on the S603 line above
        input=request,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise CouldNotJudge(f"git cat-file --batch failed ({completed.returncode})")
    out, at, sizes = completed.stdout, 0, {}
    for path in wanted:
        end = out.index(b"\n", at)
        header = out[at:end].split()
        at = end + 1
        if len(header) == 3 and header[1] in (b"blob", b"tree", b"commit", b"tag"):
            length = int(header[2])
            if header[1] == b"blob":
                sizes[path] = (count or count_lines)(out[at : at + length])
            at += length + 1
    return sizes


def count_lines(data: bytes) -> int:
    """Lines as ``splitlines`` counts them: LF, CRLF and a lone CR each end one.

    A CR-only file is source Python runs, so ``wc -l`` (which sees one line in
    it) is not the measure. ``bytes.splitlines`` honours exactly those three
    endings, not a form feed, and a last line with no ending still counts.
    """
    return len(data.splitlines())


def measure(root: Path, exempt: set[str]) -> dict[str, int]:
    """``{path: lines}`` for every tracked or untracked-unignored file in scope."""
    sizes: dict[str, int] = {}
    listed = _listed(root, "-c", "-o", "--exclude-standard", present=True)
    for path in sorted(listed - exempt):
        data = read_bytes_if_present(path, root=root)
        if data is not None:
            sizes[path] = count_lines(data)
    return sizes


# A code span's text is fenced in these marks, so the target alone may sit in one.
_SPAN_OPEN, _SPAN_CLOSE = "\x02", "\x03"
_SPAN_TARGET_RE = re.compile(
    rf"^\s*{_SPAN_OPEN}(?P<target>[^{_SPAN_OPEN}{_SPAN_CLOSE}\s]+){_SPAN_CLOSE}"
    r"\s+(?:—|–|--?)\s*(?P<reason>.*?)\s*$"
)


def _lines_with_spans(node: _Element) -> list[str]:
    """Like ``_text_lines``, but an inline code span is kept, fenced in marks.

    GitHub renders a bare ``__init__`` as bold, so a path with a dunder can only
    be written in backticks. A fenced block (``pre``) and a line that opens in a
    span stay unread: the line's label no longer starts the line (#10091, F1).
    """
    parts: list[str] = []

    def walk(element: _Element) -> None:
        for child in element.children:
            if isinstance(child, str):
                parts.append(child)
            elif child.tag == "code":
                parts.append(_SPAN_OPEN + "".join(_all_text(child)) + _SPAN_CLOSE)
            elif child.tag in {"pre", "ul", "ol", "p", "li"}:
                continue
            else:
                walk(child)

    walk(node)
    return "".join(parts).splitlines()


def _all_text(node: _Element) -> list[str]:
    return [
        part if isinstance(part, str) else "".join(_all_text(part))
        for part in node.children
    ]


#: The words the printed exception line ends in, for the agent to replace (#10966).
#: A reason that still holds them explains nothing, so it declares nothing.
WHY_PLACEHOLDER = "(say why)"


def declared_targets(html: str) -> set[str]:
    """The targets of every well-formed ``File-Size-Exception:`` line.

    The target is plain text or one code span; the rest of the line must be plain.
    """
    targets: set[str] = set()
    for block in _blocks(parse_html(html)):
        for raw in _lines_with_spans(block):
            label = _LABEL_RE.match(raw)
            if not label:
                continue
            rest = label.group("rest")
            parsed = _SPAN_TARGET_RE.match(rest) or _EXCEPTION_RE.match(rest)
            if (
                parsed
                and _HAS_CONTENT_RE.search(parsed.group("reason"))
                and WHY_PLACEHOLDER not in parsed.group("reason")
            ):
                targets.add(parsed.group("target"))
    return targets


# ---------------------------------------------------------------------------
# The rule
# ---------------------------------------------------------------------------


def text_at(root: Path, revision: str, relative: str) -> str | None:
    """The file's text at ``revision``, or ``None`` when it is not there."""
    # `cat-file -e` is a membership test, not an enumeration: no path list comes
    # back to be read. An unknown revision is refused by the rev-parse beside it,
    # so a bad revision cannot pass as "the file did not exist there".
    present = subprocess.run(  # noqa: S603  # argv is the literal "git" "-C", then root and the commit merge_base resolved, plus the cat-file literals and a relative path this module names
        ["git", "-C", str(root), "cat-file", "-e", f"{revision}:{relative}"],  # noqa: S607  # the literal "git" is resolved on PATH; root and revision are named on the S603 line above
        capture_output=True,
        check=False,
    )
    if present.returncode != 0:
        _git(root, "rev-parse", "--verify", "--quiet", f"{revision}^{{commit}}")
        return None
    return _git(root, "show", f"{revision}:{relative}")


def cap_at(root: Path, revision: str) -> Caps | None:
    """The caps at ``revision``, or ``None`` when the cap file is not there."""
    text = text_at(root, revision, CAP_RELATIVE)
    return None if text is None else parse_cap(text)


def check_tree(
    sizes: dict[str, int],
    before: dict[str, int],
    cap: int,
    renamed: dict[str, str] | None = None,
) -> dict[str, str]:
    """``{path: what it did}`` for each over-cap file the change grew.

    ``sizes`` is the tree now; ``before`` holds sizes at the merge base, keyed
    by the path there, and ``renamed`` maps a path now to its path there. A
    file absent from ``before`` is new. A file over the cap that is no larger
    than it was is what main already held, and a red for it would be a red for
    every change behind the one that grew it.
    """
    origin = renamed or {}
    grew: dict[str, str] = {}
    for path, lines in sorted(sizes.items()):
        if lines <= cap:
            continue
        old = origin.get(path, path)
        was = before.get(old)
        if was is None:
            grew[path] = f"new at {lines} lines, over the cap of {cap}"
        elif lines > was:
            source = f" (renamed from {old})" if old != path else ""
            grew[path] = (
                f"grew from {was} to {lines} lines{source}, over the cap of {cap}"
            )
    return grew


def byte_cap_refusal(
    target: str, cap: int | None, now: int | None, before: int | None
) -> str | None:
    """Why a byte-capped file set is refused, or ``None`` (#10596, #10361).

    It is refused when it is over its byte cap and holds more bytes than at the
    merge base (absent there counts as zero), as a file over the line cap is.
    A path exception does not clear it: the cap is raised, with its own
    exception line, or the text is cut.
    """
    if cap is None or now is None or now <= cap or now <= (before or 0):
        return None
    what, why = _BYTE_CAPPED[target]
    return (
        f"{what}: {now} bytes, over the {target} cap of {cap}"
        f" (it was {before if before is not None else 'absent'} at the merge base)."
        f" {why}, so move the text to the topic file it belongs in"
        " and leave a pointer, or raise the cap with 'File-Size-Exception:"
        f" {target} - <reason>' (contributing/file-size-budget.md)."
    )


#: Each byte cap: what it measures, and why its size is paid on every call.
_BYTE_CAPPED = {
    ROOT_GUIDE_CAP_TARGET: (CLAUDE_MD, "Every session loads it"),
    AGENT_GUIDES_CAP_TARGET: (
        f"{AGENT_GUIDES_DIR}/*.md together",
        "Each dispatched agent loads its definition",
    ),
}


def byte_capped_paths(root: Path, revision: str | None) -> set[str]:
    """The files one byte cap sums, for every target: in the tree, or at ``revision``.

    The agent definitions are the ``*.md`` files directly in
    :data:`AGENT_GUIDES_DIR`; the tree side lists the disk, as the line cap
    measures untracked files too, and the revision side asks git.
    """
    if revision is None:
        agents = {
            f"{AGENT_GUIDES_DIR}/{path.name}"
            for path in (root / AGENT_GUIDES_DIR).glob("*.md")
            if path.is_file()
        }
    else:
        listed = _git(
            root, "ls-tree", "--name-only", "-z", revision, f"{AGENT_GUIDES_DIR}/"
        )
        agents = {p for p in listed.split("\0") if p.endswith(".md")}
    return {CLAUDE_MD} | agents


def _byte_target(path: str) -> str:
    return ROOT_GUIDE_CAP_TARGET if path == CLAUDE_MD else AGENT_GUIDES_CAP_TARGET


def byte_sums(sizes: dict[str, int]) -> dict[str, int | None]:
    """``{target: bytes}`` from per-path sizes; ``None`` when no file of it exists."""
    sums: dict[str, int | None] = dict.fromkeys(_BYTE_CAPPED)
    for path, size in sizes.items():
        target = _byte_target(path)
        sums[target] = (sums[target] or 0) + size
    return sums


def hub_refusal(caps: Caps, now: int | None, before: int | None) -> str | None:
    """Why the hub is refused, or ``None`` (#10104).

    As :func:`byte_cap_refusal` for :data:`REPORTED_FILE`: over its byte cap
    and holding more bytes than at the merge base. A path exception does not
    clear it: the chapter's text goes to a ``contributing/`` topic file with a
    pointer left in the hub, or the cap is raised with its own exception line.
    """
    cap = caps.hub
    if cap is None or now is None or now <= cap or now <= (before or 0):
        return None
    return (
        f"{REPORTED_FILE}: {now} bytes, over the {HUB_CAP_TARGET} cap of {cap}"
        f" (it was {before if before is not None else 'absent'} at the merge base)."
        " The hub is the table of contents (#10104): put the new text in the"
        " contributing/ topic file it belongs in and leave a pointer, or raise the"
        f" cap with 'File-Size-Exception: {HUB_CAP_TARGET} - <reason>'"
        " (contributing/file-size-budget.md)."
    )


def root_guide_import_refusal(text: str) -> str | None:
    """Why :data:`CLAUDE_MD` is refused for an ``@path`` import, or ``None`` (#10596).

    The harness expands an ``@path`` token in this file into every session's
    context, so a file that shrank under the byte cap could still load any
    amount: the cap measures the file, not what it loads. No exception clears
    it; the file links its detail instead.

    An import is an ``@`` that opens a whitespace-separated token, anywhere on
    the line, outside a code span or a fenced block, where the harness does not
    expand one; so an address like ``a@b.c`` and a lone ``@`` pass.
    """
    found: list[int] = []
    fenced = False
    for number, line in enumerate(text.splitlines(), start=1):
        if _FENCE_RE.match(line):
            fenced = not fenced
            continue
        if not fenced and _IMPORT_RE.search(_CODE_SPAN_RE.sub("", line)):
            found.append(number)
    if not found:
        return None
    where = ", ".join(str(number) for number in found)
    one = len(found) == 1
    return (
        f"{CLAUDE_MD}: {'line' if one else 'lines'} {where} "
        f"{'holds' if one else 'hold'} an '@path' import, which loads the named"
        " file into every session past the"
        f" {ROOT_GUIDE_CAP_TARGET} cap. Link the file instead ([name](path));"
        " no exception clears this (contributing/file-size-budget.md)."
    )


def hub_bytes(root: Path) -> int | None:
    """The hub's size in bytes now, or ``None`` when it is not in the tree."""
    data = read_bytes_if_present(root / REPORTED_FILE)
    return None if data is None else len(data)


def hub_bytes_at(root: Path, base_commit: str) -> tuple[int | None, bool]:
    """The hub's bytes at the merge base, and whether that read worked.

    The size feeds the report only, so a read that fails is reported as a base
    that was not read and never becomes the run's exit status.
    """
    try:
        sizes = sizes_at(root, base_commit, {REPORTED_FILE}, count=len)
    except REPORT_FAILURES:
        return None, False
    return sizes.get(REPORTED_FILE), True


def hub_phrase(now: int | None, before: int | None, *, base_read: bool) -> str:
    """The hub's bytes against the merge base, for the report line (#10020).

    ``before`` is its size at the merge base, ``None`` when it was not there.
    When no base was read (``--list``), the phrase says so rather than naming
    a size the run did not measure.
    """
    if now is None:
        return "no bytes (it is not in the tree)"
    phrase = f"{now} bytes (about {now // 4} tokens; "
    if not base_read:
        return phrase + "the merge base was not read)"
    if before is None:
        return phrase + "none at the merge base)"
    return phrase + f"was {before} at the merge base)"


def report(root: Path, sizes: dict[str, int], cap: int, hub: str) -> str:
    rulebook_bytes = read_bytes_if_present(root / REPORTED_FILE)
    rulebook_lines = count_lines(rulebook_bytes) if rulebook_bytes is not None else 0
    guides = sum(n for path, n in sizes.items() if path.startswith(REPORTED_DIR))
    over = sum(1 for lines in sizes.values() if lines > cap)
    return (
        f"file-size: measured {len(sizes)} files against a cap of {cap} lines; "
        f"{over} over it. Reported, not gated: {REPORTED_FILE} "
        f"{rulebook_lines} lines and {hub}, hand-written {REPORTED_DIR} {guides} lines."
    )


# ---------------------------------------------------------------------------
# Reported, not gated: the hub's bytes and the prose-line cap (#10020, R-C14)
# ---------------------------------------------------------------------------


def lf_lines(text: str) -> list[str]:
    """The lines of ``text`` as git numbers them: ended by LF, and by nothing else.

    ``str.splitlines`` also ends a line at U+2028, a form feed and a lone CR, so
    its line numbers drift from the diff's in a file that holds one. The CR of a
    CRLF ending is dropped: it is not part of the line a reader sees.
    """
    return [line.removesuffix("\r") for line in text.split("\n")]


def prose_mask(text: str) -> list[bool]:
    """For each line of a markdown text: is it PROSE (not a table row, not fenced code)?"""
    mask: list[bool] = []
    fenced = False
    for line in lf_lines(text):
        if _FENCE_RE.match(line):
            fenced = not fenced
            mask.append(False)
            continue
        mask.append(not fenced and not line.lstrip().startswith("|"))
    return mask


def long_added_lines(
    added: dict[str, list[int]],
    removed: set[str],
    texts: dict[str, str],
    cap: int,
    preimage: dict[str, dict[int, str]] | None = None,
) -> list[str]:
    """Each ADDED or EDITED prose line over ``cap`` characters, as a finding.

    ``added`` maps a path to its added line numbers (1-based, in ``texts``);
    ``removed`` holds every line the same change removed, so a verbatim move of
    an existing long line is not an addition. ``preimage`` maps an added line to
    the removed line it replaces, paired by position within its hunk; an edit of
    a line that was ALREADY over the cap is exempt, so a one-word fix in one of
    the existing long lines does not force a rewrap (touched-only).
    """
    problems: list[str] = []
    before = preimage or {}
    for path in sorted(added):
        lines = lf_lines(texts.get(path, ""))
        mask = prose_mask(texts.get(path, ""))
        for number in added[path]:
            if number > len(lines) or not mask[number - 1]:
                continue
            text = lines[number - 1]
            was = before.get(path, {}).get(number)
            if len(text) > cap and text not in removed and not (was and len(was) > cap):
                problems.append(
                    f"{path}:{number}: an added or edited prose line of {len(text)} "
                    f"characters, over the {PROSE_CAP_TARGET} of {cap}. Break it into "
                    "sentences or list items; a table row is exempt."
                )
    return problems


def added_prose(
    root: Path, base_commit: str, exempt: set[str]
) -> tuple[dict[str, list[int]], set[str], dict[str, str], dict[str, dict[int, str]]]:
    """What the change added to and removed from :data:`PROSE_SCOPE`, from the merge
    base, and each added line's pre-image: the removed line at the same position
    in the same hunk.

    A path git still quotes with ``core.quotePath`` off (one holding a quote, a
    backslash or a control character) is not read.
    """
    diff = _git_content(
        root,
        "-c",
        "core.quotePath=false",
        "diff",
        "-U0",
        "--no-color",
        "--no-ext-diff",
        "--no-renames",
        "--src-prefix=a/",
        "--dst-prefix=b/",
        base_commit,
        "--",
        *PROSE_SCOPE,
    )
    added: dict[str, list[int]] = {}
    removed: set[str] = set()
    preimage: dict[str, dict[int, str]] = {}
    path: str | None = None
    hunk_removed: list[str] = []
    start, count = 0, 0
    # A file's "---" and "+++" lines are read only ahead of its first hunk: past
    # it, an added line that opens with "++ " reads "+++ " too.
    in_header = False
    for raw in diff.split("\n"):
        if raw.startswith("diff --git "):
            path, in_header, count = None, True, 0
        elif raw.startswith("@@"):
            in_header = False
            hunk = _HUNK_RE.match(raw)
            if hunk is not None and path is not None:
                start, count = int(hunk.group("start")), int(hunk.group("count") or 1)
                added.setdefault(path, []).extend(range(start, start + count))
                hunk_removed = []
        elif in_header:
            if raw.startswith("+++ b/"):
                # git ends the name with a tab when it holds a space.
                path = raw[6:].removesuffix("\t")
        elif raw.startswith("-"):
            line = raw[1:].removesuffix("\r")
            removed.add(line)
            if path is not None:
                hunk_removed.append(line)
                # -U0: the n-th removed line of a hunk pairs with its n-th added
                # line; a removed line past the hunk's added count pairs with none.
                if len(hunk_removed) <= count:
                    preimage.setdefault(path, {})[start + len(hunk_removed) - 1] = line
    untracked = {
        name
        for name in _git(
            root, "ls-files", "-z", "-o", "--exclude-standard", "--", *PROSE_SCOPE
        ).split("\0")
        if name
    }
    texts: dict[str, str] = {}
    for name in sorted(set(added) | untracked):
        data = read_bytes_if_present(name, root=root)
        if name in exempt or data is None:
            added.pop(name, None)
            continue
        texts[name] = data.decode("utf-8", errors="replace")
        if name in untracked:
            added[name] = list(range(1, len(lf_lines(texts[name])) + 1))
    return added, removed, texts, preimage


def reported_findings(
    root: Path,
    base_commit: str,
    caps: Caps,
    exempt: set[str],
    hub_now: int | None,
    hub_before: int | None,
) -> tuple[list[str], str | None]:
    """The REPORT-ONLY findings: the hub grew in bytes, and each long prose line.

    The second value is why the prose lines could not be read, ``None`` when
    they were. It is returned, not raised: nothing here reaches the exit status.
    """
    findings: list[str] = []
    failure: str | None = None
    if hub_now is not None and hub_before is not None and hub_now > hub_before:
        findings.append(
            f"{REPORTED_FILE}: grew from {hub_before} to {hub_now} bytes; the #10020 "
            "ruling freezes the hub while it is cut into topic files."
        )
    if caps.prose is not None:
        try:
            added, removed, texts, preimage = added_prose(root, base_commit, exempt)
            findings += long_added_lines(added, removed, texts, caps.prose, preimage)
        except REPORT_FAILURES as error:
            failure = f"{type(error).__name__}: {' '.join(str(error).split())}"
    return findings, failure


def _declared(body_file: str | None, render: Renderer | None) -> set[str] | None:
    """The body's exception targets; ``None`` when no body was given."""
    if body_file is None:
        return None
    body = Path(body_file)
    if not body.is_file():
        raise CouldNotJudge(f"the body file {body} does not exist")
    renderer = render if render is not None else gh_renderer(_run_gh)
    try:
        html = render_when_labelled(
            renderer,
            body.read_text(encoding="utf-8", errors="replace"),
            _RAW_LABEL_RE,
        )
    except Unrenderable as error:
        raise CouldNotJudge(
            f"the body could not be rendered ({error}): a body is rendered through gh, "
            "so check that gh is reachable and authenticated (gh auth status) and "
            "run this again"
        ) from error
    except FileNotFoundError as error:
        if error.filename != "gh":
            raise
        raise CouldNotJudge(
            "the body could not be rendered: gh is not installed, and the body "
            "is rendered through it"
        ) from error
    return declared_targets(html)


def _measured(root: Path) -> tuple[Caps, set[str], dict[str, int]]:
    cap_file = root / CAP_RELATIVE
    if not cap_file.is_file():
        raise CouldNotJudge(f"{CAP_RELATIVE} is missing")
    caps = parse_cap(cap_file.read_text(encoding="utf-8"))
    exempt = exempt_files(root)
    return caps, exempt, measure(root, exempt)


def list_main(root: Path) -> int:
    caps, _exempt, sizes = _measured(root)
    cap = caps.lines
    print(report(root, sizes, cap, hub_phrase(hub_bytes(root), None, base_read=False)))
    for path, lines in sorted(sizes.items(), key=lambda item: (-item[1], item[0])):
        if lines > cap:
            print(f"{lines:>6} {path}")
    return 0


#: The last line of every growth refusal: the cap exists to cut the context a task
#: reads, so a split that leaves every part to be read in turn gains nothing (#10021).
SPLIT_HINT = (
    "split it into chapters, not pages: an overview plus self-contained parts "
    "(contributing/file-size-budget.md#how-to-split-chapters-not-pages)"
)


def exception_line(target: str, what: str) -> str:
    """The ``File-Size-Exception`` line one growth needs, accepted pasted as is (#10966).

    The reason starts with the measured size and the cap, and asks for the why
    in plain words. No angle brackets: the body is read as GitHub renders it,
    where ``<reason>`` is an HTML tag and renders to nothing, so a line printed
    that way declared nothing and the next refusal repeated this one.
    """
    return f"File-Size-Exception: `{target}` - {what}; the split waits because {WHY_PLACEHOLDER}"


def print_unread_lines(body_file: str, targets: set[str]) -> None:
    """Name each body line labelled for a *target* that the gate did not read.

    *targets* are the growths the body does not declare. A line that names one
    of them is there, so the agent pasted it and the gate read no reason or no
    target from it: say so, or the next refusal reads the same as the last.
    """
    try:
        text = Path(body_file).read_text(encoding="utf-8", errors="replace")
    except OSError:
        return
    for raw in text.splitlines():
        label = _LABEL_RE.match(raw)
        if not label:
            continue
        for target in sorted(targets):
            if target in label.group("rest") and WHY_PLACEHOLDER in raw:
                print(
                    f"file-size: {body_file} has a line for `{target}` whose reason is "
                    f"still the placeholder: replace {WHY_PLACEHOLDER} with the real "
                    f"reason: {raw.strip()}"
                )
            elif target in label.group("rest"):
                print(
                    f"file-size: {body_file} has a line for `{target}` that the gate "
                    f"does not read: {raw.strip()}. The body is read as GitHub renders "
                    "it: a word in angle brackets such as <reason> is an HTML tag and "
                    "renders to nothing, and the path is plain text or one code span. "
                    "Replace that line with the one printed for it."
                )


def check_main(
    root: Path,
    base: str,
    body_file: str | None,
    render: Renderer | None,
    no_body_is_advisory: bool = False,
) -> int:
    if (root / RETIRED_RELATIVE).is_symlink() or (root / RETIRED_RELATIVE).exists():
        print(
            f"file-size: {RETIRED_RELATIVE} is retired and this tree holds it "
            f"(#10271). Run `git rm {RETIRED_RELATIVE}`: if merging main stopped "
            "on it, that is the resolution. A file your change grew past the cap "
            "takes a 'File-Size-Exception: `<path>` - <reason>' line in the PR "
            "body instead of a line in that list."
        )
        return 1
    caps, exempt, sizes, base_commit, grew = _growth(root, base)
    cap = caps.lines
    core_now = read_bytes_if_present(root / CLAUDE_MD)
    core_refusals: list[str] = []
    capped = {t: n for t, n in caps.byte_caps().items() if n is not None}
    if capped:
        now_sizes = {
            path: len(data)
            for path in byte_capped_paths(root, None)
            if (data := read_bytes_if_present(root / path)) is not None
        }
        before_sizes = sizes_at(
            root, base_commit, byte_capped_paths(root, base_commit), count=len
        )
        now_sums, before_sums = byte_sums(now_sizes), byte_sums(before_sizes)
        for target, limit in capped.items():
            size_refusal = byte_cap_refusal(
                target, limit, now_sums[target], before_sums[target]
            )
            if size_refusal is not None:
                core_refusals.append(size_refusal)
    # Not tied to the byte cap: dropping the cap line must not admit an import.
    if core_now is not None:
        import_refusal = root_guide_import_refusal(
            core_now.decode("utf-8", errors="replace")
        )
        if import_refusal is not None:
            core_refusals.append(import_refusal)
    now = hub_bytes(root)
    was, base_read = hub_bytes_at(root, base_commit)
    if caps.hub is not None:
        if not base_read and now is not None and now > caps.hub:
            raise CouldNotJudge(
                f"{REPORTED_FILE} is over the {HUB_CAP_TARGET} cap and its size at the"
                " merge base could not be read, so whether it grew is unknown"
            )
        hub_size_refusal = hub_refusal(caps, now, was)
        if hub_size_refusal is not None:
            core_refusals.append(hub_size_refusal)
    print(report(root, sizes, cap, hub_phrase(now, was, base_read=base_read)))
    print(f"file-size: the change is measured from {base_commit[:12]} ({base}).")
    # REPORT-ONLY: printed, never in the exit status; #10203 decides when these gate.
    reported, failure = reported_findings(root, base_commit, caps, exempt, now, was)
    if failure is not None:
        print(
            "file-size: REPORT-ONLY, not gated: the prose-line report could not be "
            f"computed ({failure}). The verdict on the line cap is unaffected."
        )
    if reported:
        print(
            f"file-size: REPORT-ONLY, not gated (#10203 decides when): {len(reported)} "
            "byte or prose-line finding(s)."
        )
        for finding in reported:
            print(f"  {finding}")
    # No exception line clears this one, so it is 1 with or without a body.
    for refusal in core_refusals:
        print(f"file-size: {refusal}")
    hard = 1 if core_refusals else 0
    if not grew:
        return hard
    declared = _declared(body_file, render)
    missing = {
        target: what
        for target, what in grew.items()
        if declared is None or target not in declared
    }
    for target in sorted(set(grew) - set(missing)):
        print(f"  {target}: {grew[target]}; explained by its File-Size-Exception line.")
    for target, what in missing.items():
        print(f"  {target}: {what}.")
    if not missing:
        return hard
    where = (
        "the PR body"
        if declared is not None
        else "the PR body (none was given: pass --pr-body-file)"
    )
    if body_file is not None:
        print_unread_lines(body_file, set(missing))
    print(
        f"file-size: {len(missing)} undeclared growth(s). Split the file along a real "
        f"seam, or add to {where}, for each one, this line (finish its reason):"
    )
    for target, what in sorted(missing.items()):
        print(f"  {exception_line(target, what)}")
    print(SPLIT_HINT)
    # Every entry of ``missing`` is one an exception line clears, and with no
    # body none could have been read; the retired list returned above, and the
    # CLAUDE.md refusal no line clears keeps the status at 1.
    advisory = no_body_is_advisory and declared is None and not hard
    return ADVISORY_EXIT_STATUS if advisory else 1


def _growth(
    root: Path, base: str
) -> tuple[Caps, set[str], dict[str, int], str, dict[str, str]]:
    """The measured tree, the merge base, and what grew from it: target -> how."""
    caps, exempt, sizes = _measured(root)
    cap = caps.lines
    base_commit = merge_base(root, base)
    over = {path for path, lines in sizes.items() if lines > cap}
    renamed = renamed_from(root, base_commit)
    before = sizes_at(root, base_commit, {renamed.get(path, path) for path in over})
    grew = check_tree(sizes, before, cap, renamed)
    # A change that first checks the cap file in raises nothing: no cap preceded it.
    caps_before = cap_at(root, base_commit)
    if caps_before is not None and cap > caps_before.lines:
        grew[CAP_TARGET] = f"raised from {caps_before.lines} to {cap} lines"
    # No prose cap is no limit, so adding one tightens and dropping one loosens.
    if caps_before is not None and caps_before.prose is not None:
        if caps.prose is None:
            grew[PROSE_CAP_TARGET] = f"dropped; it was {caps_before.prose} characters"
        elif caps.prose > caps_before.prose:
            grew[PROSE_CAP_TARGET] = (
                f"raised from {caps_before.prose} to {caps.prose} characters"
            )
    # The same for each byte cap (#10596, #10104, #10361): no line is no limit.
    if caps_before is not None:
        now_caps = caps.raisable()
        for target, was in caps_before.raisable().items():
            if was is None:
                continue
            if now_caps[target] is None:
                grew[target] = f"dropped; it was {was} bytes"
            elif (now_caps[target] or 0) > was:
                grew[target] = f"raised from {was} to {now_caps[target]} bytes"
    # A raised efficiency baseline (#10361) is declared the same way, by metric.
    try:
        grew.update(
            raised_baselines(
                text_at(root, base_commit, BASELINES_RELATIVE),
                read_if_present(root / BASELINES_RELATIVE),
            )
        )
    except Unreadable as error:
        raise CouldNotJudge(str(error)) from error
    return caps, exempt, sizes, base_commit, grew


#: The variable the push gate reads the PR body from; at commit time too (#10892).
BODY_ENV = "PRISM_PR_BODY_FILE"


def commit_body_file(
    given: str | None, environ: Mapping[str, str], root: Path
) -> str | None:
    """The PR body the commit-time step reads (#11464).

    ``--pr-body-file``, else ``PRISM_PR_BODY_FILE``, else the draft in *root*,
    the tree being measured, that ``scripts/pr_open.py`` posts
    (:mod:`pr_body_draft`, its older place included), when that file exists.
    A commit runs with no way to name a body (the hook's arguments are fixed),
    so the draft that justifies a growth is read at commit time as the push
    gate reads it, rather than refused there.
    """
    if given or environ.get(BODY_ENV):
        return given or environ.get(BODY_ENV)
    draft = pr_body_draft.draft_body_file(root)
    return str(draft) if draft.is_file() else None


def _carried(root: Path, base_commit: str) -> set[str]:
    """The targets this commit or its branch carries: staged, or changed since the base.

    The tree is measured with untracked files in it, and pre-commit does not
    stash those. An untracked over-cap file is not part of the commit, so it
    may only warn (#10892 review). The cap targets ride on the cap file.
    """
    paths = set(_git(root, "diff", "--cached", "--name-only", "-z").split("\0"))
    paths |= set(
        _git(root, "diff", "--name-only", "-z", base_commit, "HEAD").split("\0")
    )
    paths.discard("")
    if CAP_RELATIVE in paths:
        paths |= {CAP_TARGET, PROSE_CAP_TARGET, *_BYTE_CAP_FIELDS}
    if BASELINES_RELATIVE in paths:
        paths |= set(METRICS)
    return paths


def _merged_in(root: Path) -> set[str]:
    """The paths a merge in progress stages exactly as the merged branch has them.

    A conflicted merge of main is finished by ``git commit``, so this hook runs
    while ``HEAD`` is still the branch's old tip: the merge base is the old one,
    and a file main grew looks like the branch's growth. A staged blob equal to
    ``MERGE_HEAD``'s is main's, and the push gate, measuring from the merge's
    new base, does not count it (#10892 review). No merge in progress: empty.
    """
    merge_head = root / _git(root, "rev-parse", "--git-path", "MERGE_HEAD").strip()
    if not merge_head.is_file():
        return set()
    staged: dict[str, str] = {}
    for entry in _git(root, "ls-files", "-s", "-z").split("\0"):
        meta, _, path = entry.partition("\t")
        fields = meta.split()
        if len(fields) == 3 and fields[2] == "0":
            staged[path] = fields[1]
    merged: set[str] = set()
    for entry in _git(root, "ls-tree", "-r", "-z", "MERGE_HEAD").split("\0"):
        meta, _, path = entry.partition("\t")
        fields = meta.split()
        if len(fields) == 3 and staged.get(path) == fields[2]:
            merged.add(path)
    return merged


def warn_at_commit(
    root: Path,
    base: str,
    body_file: str | None = None,
    *,
    agent: bool = False,
    render: Renderer | None = None,
) -> int:
    """The commit-time hook (#10559, #10892): name each exception line growth needs.

    With nothing grown it prints nothing and reads no body (pre-commit's own
    hook-id and duration lines still show under ``verbose``). When something
    grew, the same growth the push gate judges:

    * *body_file* given (:func:`commit_body_file`): the body is judged as the
      push gate judges it. A growth it does not declare refuses the commit
      (exit 1). The push gate would refuse the same body after its full run,
      about 10 minutes (#10892).
    * no body, *agent* (``AGENT_TMP`` is set, as in every agent commit): exit 1.
      An agent commits an over-cap growth with the body that declares it.
      A body file named but not written yet is no body here (#11472).
    * no body, not an agent: a warning and exit 0, because the PR body may not
      exist yet.

    A check that could not judge, a body that could not be rendered included,
    is left to the push hook: one line, and the warning in place of a refusal.
    Even an error this module did not foresee never fails a commit. The whole
    tree is measured from the merge base, so a branch that already grew a file
    is judged again on every later commit. Only a growth the commit carries
    (staged, or changed on the branch since the base) is refused; an untracked
    file pre-commit did not stash only warns. A file that a merge in progress
    stages exactly as ``MERGE_HEAD`` has it is the merged branch's growth, not
    this one's, and is not reported (:func:`_merged_in`).
    """
    try:
        _caps, _exempt, _sizes, base_commit, grew = _growth(root, base)
        if grew:
            merged = _merged_in(root)
            grew = {t: what for t, what in grew.items() if t not in merged}
    except Exception as error:  # noqa: BLE001 - a check that could not judge must never fail a commit
        print(
            f"file-size warning skipped: {type(error).__name__}: {error}".splitlines()[
                0
            ]
        )
        return 0
    if not grew:
        return 0
    missing = grew
    refuse = agent
    absent = None
    if agent and body_file and not Path(body_file).is_file():
        # A brief names the body file on every commit, before an impl agent
        # drafts it: a file not written yet is no body (#11472).
        absent, body_file = body_file, None
    if body_file:
        try:
            declared = _declared(body_file, render) or set()
        except Exception as error:  # noqa: BLE001 - a body that could not be read is the push gate's to judge
            print(
                f"file-size: the body {body_file} could not be read, so the push gate "
                f"judges it: {type(error).__name__}: {error}".splitlines()[0]
            )
            refuse = False
        else:
            missing = {t: what for t, what in grew.items() if t not in declared}
            refuse = True
            for target in sorted(set(grew) - set(missing)):
                print(f"file-size: {target}: {grew[target]}; declared in {body_file}.")
    if not missing:
        return 0
    warned: dict[str, str] = {}
    if refuse:
        try:
            carried = _carried(root, base_commit)
        except Exception as error:  # noqa: BLE001 - a commit this check could not scope is the push gate's to judge
            print(
                "file-size: the commit's files could not be listed, so the push gate "
                f"judges them: {type(error).__name__}: {error}".splitlines()[0]
            )
            carried = set()
        warned = {t: what for t, what in missing.items() if t not in carried}
        missing = {t: what for t, what in missing.items() if t in carried}
    else:
        warned, missing = missing, {}
    if warned:
        print(
            f"file-size WARNING (#10559): {len(warned)} file(s) grew past the line cap "
            f"from {base_commit[:12]} ({base}). The push is refused unless the PR body "
            "carries, for each one:"
        )
        for target, what in sorted(warned.items()):
            print(f"  {exception_line(target, what)}")
    if not missing:
        print(SPLIT_HINT)
        return 0
    if body_file:
        print_unread_lines(body_file, set(missing))
        print(
            f"file-size REFUSED (#10892): {len(missing)} file(s) grew past the line cap "
            f"from {base_commit[:12]} ({base}), and {BODY_ENV} ({body_file}) does not "
            "declare them; the push gate would refuse that body after its full run. "
            "Add to the body, for each one, then commit again:"
        )
    elif absent:
        print(
            f"file-size REFUSED (#10892): {len(missing)} file(s) grew past the line cap "
            f"from {base_commit[:12]} ({base}), and {BODY_ENV} names {absent}, which "
            "does not exist (#11472). Write the body there with, for each one, the "
            "line below, then commit again:"
        )
    else:
        print(
            f"file-size REFUSED (#10892): {len(missing)} file(s) grew past the line cap "
            f"from {base_commit[:12]} ({base}), and this agent commit (AGENT_TMP is set) "
            "names no PR body. Write, for each one, into the body file, then commit "
            f"again with {BODY_ENV}=<that file> (a WIP backup too: the guard "
            "refuses an agent's SKIP= on a commit, #11209):"
        )
    for target, what in sorted(missing.items()):
        print(f"  {exception_line(target, what)}")
    print(SPLIT_HINT)
    return 1


def main(
    argv: list[str] | None = None,
    *,
    root: Path | None = None,
    render: Renderer | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--base",
        default="origin/main",
        help="Measure the change from the merge base of this revision and HEAD.",
    )
    parser.add_argument(
        "--pr-body-file",
        help="The PR body, read for File-Size-Exception lines when something grew.",
    )
    parser.add_argument(
        "--no-body-is-advisory",
        action="store_true",
        help=(
            "With no --pr-body-file, exit 4 rather than 1 when every refusal is "
            "one a File-Size-Exception line could clear. For a run before the PR "
            "exists; a body, when given, is judged as without this flag."
        ),
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Print every measured file over the cap with its size; gates nothing.",
    )
    parser.add_argument(
        "--warn-at-commit",
        action="store_true",
        help=(
            "The commit-time hook: name each File-Size-Exception line the PR body "
            "will need, and print nothing when nothing grew. Exit 1 when the body "
            "(--pr-body-file, else PRISM_PR_BODY_FILE, else <clone>/.agent/pr-body.md) lacks "
            "one, or when AGENT_TMP "
            "is set and no body is given; otherwise a warning and exit 0."
        ),
    )
    args = parser.parse_args(argv)
    tree = root if root is not None else REPO_ROOT
    try:
        if args.list:
            return list_main(tree)
        if args.warn_at_commit:
            return warn_at_commit(
                tree,
                args.base,
                commit_body_file(args.pr_body_file, os.environ, tree),
                agent=bool(os.environ.get("AGENT_TMP")),
                render=render,
            )
        return check_main(
            tree, args.base, args.pr_body_file, render, args.no_body_is_advisory
        )
    except CouldNotJudge as error:
        sys.stderr.write(f"file-size: NOTHING WAS JUDGED -- {error}.\n")
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
