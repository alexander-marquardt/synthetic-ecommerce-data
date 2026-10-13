"""Refuse a pull request that changes served code and says nothing about its docs.

This script is the docs-impact gate of issue #9914, run as a step of the
REQUIRED ``audit-grep`` job (``.github/workflows/audit-grep.yaml``), so a red
here blocks the merge. It sits in that job rather than a workflow of its own for
the reason the review-verdict gate and the coverage floor do: a new job binds
nothing until branch protection is edited. The rule it is a forcing function for
lives in ``CONTRIBUTING.md`` -> "Docs travel with the code — same PR, or an
explicit Docs-Impact line"; this docstring states what the CHECK does and what
it cannot see, and does not restate the rule.

Why this exists
---------------
Docs drift from the code one pull request at a time, and nothing reds when they
do. An integrator cannot ask us, so a stale sentence in ``docs/`` becomes a wrong
integration. The 2026-10-01 docs audit (#8483) found dozens of stale or false
passages, and the maintainer ruled (2026-10-01) that every change to code or
behaviour updates its docs IN THE SAME PR, with "no docs affected" allowed only
as an explicit, reviewable statement.

The decision, in full
---------------------
1. The changed paths are read from git over the PR's range (``--diff-range``,
   renames split into a deletion and an addition so a file moved OUT of a
   served path still counts as a served change).
2. A changed path is a **served-path change** when it matches
   :data:`SERVED_PATH_GLOBS` and none of :data:`SERVED_PATH_TEST_GLOBS`, or
   when it is an executable a ``docs/`` page or an integrator-facing README
   names (:func:`executables_named_by_docs`).
3. A changed path is a **docs-surface change** when it matches
   :data:`DOCS_SURFACE_GLOBS`.
4. No served-path change -> exit 0. The body is not read.
5. A served-path change AND a docs-surface change -> exit 0. The body is not
   read.
6. A served-path change and NO docs-surface change -> the PR body must carry a
   declaration line ``Docs-Impact: none — <reason>`` (:data:`DECLARATION_RE`)
   whose reason contains a letter or a digit. Present and well-formed -> exit 0,
   quoting the reason. Absent, or any ``Docs-Impact:`` line malformed -> exit 1.

The body is read the way GitHub RENDERS it
------------------------------------------
The declaration is found in the HTML ``POST /markdown`` (``mode=gfm``) returns,
through the renderer and HTML tree :mod:`check_review_verdict` already owns
(imported, not copied). That module's docstring records why: three rounds of
approximating CommonMark in Python were wrong three different ways. What that
buys here, measured against the live renderer on 2026-10-01 and pinned in
``tests/data/docs_impact_rendered_bodies.json``:

* a declaration inside an HTML comment does not render, so the pull-request
  template's guidance cannot satisfy the check on an author's behalf;
* a declaration inside a code fence or an inline code span is an EXAMPLE, not a
  declaration, and is not read;
* the template placeholder ``<reason>`` is stripped by GitHub's sanitiser, so a
  body that copied the form without filling it in renders an EMPTY reason and
  reds;
* a line inside a blockquote or a ``<details>`` block is not read at all
  (:data:`UNREAD_TAGS`, #9921): a quoted line is another pull request's
  declaration, not this one's, and a collapsed one hides from the reviewer who
  judges its reason. Neither satisfies the check, and neither can malform it.

A declaration is a line that OPENS with ``Docs-Impact:`` inside a rendered
paragraph or list item. A sentence that merely mentions the label mid-line is
not one.

What this check CANNOT see -- the forcing function, not the truth check
-----------------------------------------------------------------------
* **WHICH doc should have changed.** Any change under a docs surface satisfies
  it: a one-word edit to an unrelated chapter turns it green.
* **Whether the changed doc is now TRUE.** It reads paths, never content. Truth
  stays a review obligation (``CONTRIBUTING_REVIEW.md``), and the #8483
  validation -- executable examples, generated reference -- is what makes parts
  of it mechanical.
* **Whether a ``Docs-Impact: none`` reason is true.** The reason is a claim a
  reviewer judges; the check only refuses an absent or empty one.
* **What changed INSIDE a served file.** A docstring-only or comment-only edit
  under ``packages/*/src`` is a served-path change by path; such a PR says so in
  its declaration. A regenerated customization schema or API reference page
  (``docs/si/reference/api-reference.md``) is a docs surface (the ruling names
  generated reference as docs), so it satisfies the check on its own --
  whether the hand-written chapter describing the same behaviour also needed
  to move is the reviewer's question. The OpenAPI documents are not committed
  (#10455), so they are not in the docs surface: they never appear in a diff.
* **Paths outside the served globs.** Tests, compose files, Dockerfiles, and
  any script -- operator tool, agent tool or CI gate alike -- that no docs
  surface names are not gated. The RULE still covers them; the check does not
  force it there. Conversely, a CI gate or internal tool that a docs surface
  DOES name is in the served set, because a change to it can falsify that text.
* **A script a doc SHOULD name but does not.** The named-script set is derived
  from what the docs surfaces name, so a new script nobody has documented yet
  is outside it -- which is itself the gap the rule is about.
* **A body edited after the run.** ``audit-grep`` fetches the body LIVE when
  the run executes (never the frozen event payload, #5242), so a re-run sees
  the current text; an edit made after a run finished is seen only by a later
  run. The job's ``edited`` trigger starts one automatically.

Bot pull requests are NOT exempted, because none needs to be: Dependabot is
configured (``.github/dependabot.yml``) for npm in ``/search-ui``, GitHub
Actions and the uv workspace, and each writes only manifests, lockfiles and
workflow pins -- no path in :data:`SERVED_PATH_GLOBS`. An exemption nothing
reaches would be dead code.

Exit status
-----------
* 0 -- nothing owed, docs touched, or a well-formed declaration. Every success
  line names how many changed paths were read and which branch decided it.
* 1 -- a served-path change with no docs-surface change and no well-formed
  declaration, or a malformed ``Docs-Impact:`` line. Each is named with its
  remedy.
* 3 -- the check could not judge, and this is never reported as clean
  (``CONTRIBUTING.md`` -> "A check that COULD NOT judge must not return the
  value that means 'judged, and fine'"): the diff range did not resolve, a
  docs page could not be read, the body file is missing, or the renderer was
  unreachable.
"""

from __future__ import annotations

import argparse
import posixpath
import re
import subprocess
import sys
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from pathlib import Path

# Sibling scripts, not an installed package -- same shape as
# ``check_review_verdict`` importing ``check_closing_keywords``.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_review_verdict import (  # noqa: E402  (path is set up just above)
    Renderer,
    Unrenderable,
    _Element,
    _run_gh,
    gh_renderer,
    parse_html,
    render_when_labelled,
)

REPO_ROOT = Path(__file__).resolve().parents[2]

#: Paths whose change alters what a deployed system does: the three Python
#: packages' runtime source (Engine, Studio, analytics -- the customization
#: config schema's source, ``prism_engine/customization_schema.py``, is under
#: here too) and the search UI's source. Issue #9914 names these as the trigger.
SERVED_PATH_GLOBS: tuple[str, ...] = (
    "packages/*/src/**",
    "search-ui/src/**",
)

#: Test code that lives INSIDE a served glob. The Python packages keep their
#: tests under the root ``tests/``, so only the UI's colocated tests and helpers
#: need this (``features/search/testing/`` holds fixtures no production module
#: imports).
SERVED_PATH_TEST_GLOBS: tuple[str, ...] = (
    "search-ui/src/**/__tests__/**",
    "search-ui/src/**/*.test.*",
    "search-ui/src/**/*.spec.*",
    "search-ui/src/test-utils/**",
    "search-ui/src/**/testing/**",
    "search-ui/src/test-setup.ts",
)

#: The surfaces the 2026-10-01 ruling names as docs: ``docs/``,
#: ``contributing/``, ``CONTRIBUTING`` (and its review checklist), the
#: integrator-facing READMEs, and the committed generated reference -- the
#: OpenAPI snapshots and the customization schema, which are what the
#: docstrings and API/schema descriptions in source feed. ``specs/`` is
#: deliberately absent: a spec is the internal design record, and shipped
#: behaviour gets its ``docs/`` page (CONTRIBUTING.md -> "Implementation specs
#: live in specs/"). ``CHANGELOG.md`` is absent too: it records that something
#: changed, not how it now behaves.
#: The integrator-facing documents outside ``docs/``. Part of the docs
#: surfaces below, and -- with ``docs/`` -- what the named-script set is read
#: from (:func:`executables_named_by_docs`).
INTEGRATOR_DOC_GLOBS: tuple[str, ...] = (
    "README.md",
    "docker-compose.README.md",
    "MIGRATION-v1.md",
    "packages/*/README.md",
    "search-ui/README.md",
    "scripts/README.md",
)

DOCS_SURFACE_GLOBS: tuple[str, ...] = (
    "docs/**",
    "contributing/**",
    "CONTRIBUTING.md",
    "CONTRIBUTING_REVIEW.md",
    *INTEGRATOR_DOC_GLOBS,
    "packages/prism-engine/customization.schema.json",
)

#: Where the named-script set is read from: every page under ``docs/``, plus
#: :data:`INTEGRATOR_DOC_GLOBS` (a script that only ``scripts/README.md`` names
#: -- a migration retained for SIs, say -- is named by a docs surface just the
#: same).
DOCS_ROOT = "docs"

#: A repository path to an executable, as a doc writes it -- optionally behind
#: ``./`` or ``../`` hops, which are stripped. The left guard stops a match from
#: starting mid-token (``prism_engine/x.py`` inside a longer dotted path).
_NAMED_EXECUTABLE_RE = re.compile(
    r"(?<![\w./-])((?:\.\.?/)*(?:[\w.-]+/)*[\w.-]+\.(?:sh|py))\b"
)

#: A rendered line that OPENS with the label is a declaration attempt. The
#: label is matched case-insensitively so a capitalisation slip is judged (and
#: refused if malformed) rather than silently ignored.
_LABEL_RE = re.compile(r"^\s*docs-impact\s*:(?P<rest>.*)$", re.IGNORECASE)
#: The label's name anywhere in the body as written; a body without it is not
#: rendered, so a spent REST quota cannot refuse a body that declares nothing (#11059).
_RAW_LABEL_RE = re.compile(r"docs-impact", re.IGNORECASE)

#: The one well-formed declaration: ``none``, a dash, a reason. The dash may be
#: an em dash (the documented form), an en dash, or one or two ASCII hyphens --
#: the same separator set ``check_review_verdict`` accepts after FILE/BLOCKING.
DECLARATION_RE = re.compile(
    r"^\s*none\s*(?:—|–|--?)\s*(?P<reason>.*?)\s*$", re.IGNORECASE
)

#: A reason must carry at least one letter or digit: punctuation alone is the
#: empty reason with decoration.
_HAS_CONTENT_RE = re.compile(r"[^\W_]")

#: Elements whose text is never a declaration: an example in a code span or
#: block is quoted, not declared. (A fenced block renders as ``<pre><code>``
#: with no paragraph inside, so skipping ``code`` inside a block covers both.)
_CODE_TAGS = frozenset({"code", "pre"})

#: Elements whose text is not read for a declaration at all, wherever they sit
#: (#9921): a blockquote quotes someone else's line, and ``<details>`` renders
#: collapsed, out of the sight of the reviewer who judges the reason.
UNREAD_TAGS = frozenset({"blockquote", "details"})

#: Elements whose own lines are read for a declaration.
_BLOCK_TAGS = frozenset({"p", "li"})

GitRunner = Callable[[list[str]], tuple[int, str, str]]


class CouldNotJudge(Exception):
    """The inputs could not be read; the verdict is UNKNOWN, never clean."""


@dataclass(frozen=True)
class Declaration:
    """One rendered line opening with ``Docs-Impact:``."""

    line: str
    reason: str | None  # None when the line does not parse

    @property
    def well_formed(self) -> bool:
        return self.reason is not None


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


def _glob_regex(pattern: str) -> re.Pattern[str]:
    """Translate a path glob: ``**`` crosses ``/``, ``*`` and ``?`` do not."""
    out: list[str] = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            # Zero or more whole directories, so ``a/**/b`` matches ``a/b``.
            out.append("(?:.*/)?")
            index += 3
        elif pattern.startswith("**", index):
            out.append(".*")
            index += 2
        elif pattern[index] == "*":
            out.append("[^/]*")
            index += 1
        elif pattern[index] == "?":
            out.append("[^/]")
            index += 1
        else:
            out.append(re.escape(pattern[index]))
            index += 1
    return re.compile("".join(out) + r"\Z")


def matches_any(path: str, globs: Iterable[str]) -> bool:
    return any(_glob_regex(glob).match(path) for glob in globs)


def _naming_pages(root: Path) -> list[Path]:
    pages = sorted((root / DOCS_ROOT).rglob("*.md"))
    for glob in INTEGRATOR_DOC_GLOBS:
        pages.extend(sorted(root.glob(glob)))
    return pages


def _resolve_named(root: Path, page_dir: str, token: str) -> str | None:
    """The repo-relative path a page means by ``token``, or None for prose.

    Tried in order: relative to the page's own directory (``migrate.py`` in
    ``scripts/README.md`` is ``scripts/migrate.py``), then repo-relative with
    leading ``./`` / ``../`` hops stripped (how ``docs/`` pages write
    ``scripts/prism.sh``). The first that is a real file wins. When neither
    exists, a token with a directory in it is kept repo-relative, so DELETING a
    script a page still names is a served change too; a bare name is dropped,
    because ``app.py`` in prose names a module, not a path.
    """
    stripped = re.sub(r"^(?:\.\.?/)+", "", token)
    candidates = []
    local = posixpath.normpath(posixpath.join(page_dir, token))
    if not local.startswith(".."):
        candidates.append(local)
    candidates.append(stripped)
    for candidate in candidates:
        if (root / candidate).is_file():
            return candidate
    return stripped if "/" in stripped else None


def executables_named_by_docs(root: Path) -> frozenset[str]:
    """Every ``.sh`` / ``.py`` path a docs surface names, repo-relative.

    Read from every ``docs/`` page and every integrator-facing document
    (:data:`INTEGRATOR_DOC_GLOBS`). Derived rather than listed: a script is in
    the served set because a docs surface names it, so a change to it can
    falsify that text -- whether it is an operator script, an agent tool or a
    CI gate. Paths under ``tests/`` are dropped -- a doc citing a test is
    citing evidence, not an instruction to run something.
    """
    named: set[str] = set()
    for page in _naming_pages(root):
        text = page.read_text(encoding="utf-8", errors="replace")
        page_dir = page.parent.relative_to(root).as_posix()
        for match in _NAMED_EXECUTABLE_RE.finditer(text):
            path = _resolve_named(root, page_dir, match.group(1))
            if path is None or path.startswith("tests/"):
                continue
            named.add(path)
    return frozenset(named)


@dataclass(frozen=True)
class Classified:
    served: tuple[str, ...]
    docs: tuple[str, ...]
    total: int


def classify(paths: Iterable[str], named_by_docs: frozenset[str]) -> Classified:
    all_paths = sorted(set(paths))
    served = tuple(
        path
        for path in all_paths
        if (
            matches_any(path, SERVED_PATH_GLOBS)
            and not matches_any(path, SERVED_PATH_TEST_GLOBS)
        )
        or path in named_by_docs
    )
    docs = tuple(path for path in all_paths if matches_any(path, DOCS_SURFACE_GLOBS))
    return Classified(served=served, docs=docs, total=len(all_paths))


# ---------------------------------------------------------------------------
# Reading the body
# ---------------------------------------------------------------------------


def _text_lines(node: _Element, skip: frozenset[str] = frozenset()) -> list[str]:
    """The rendered lines of a block, skipping code, nested blocks and ``skip``.

    Nested ``p``/``li``/lists are read as blocks of their own, so they are
    excluded here; code is excluded because it is quoted, not declared.
    """
    parts: list[str] = []

    def walk(element: _Element) -> None:
        for child in element.children:
            if isinstance(child, str):
                parts.append(child)
            elif (
                child.tag in _CODE_TAGS
                or child.tag in {"ul", "ol", "p", "li"}
                or child.tag in skip
            ):
                continue
            else:
                walk(child)

    walk(node)
    return "".join(parts).splitlines()


def _blocks(node: _Element, skip: frozenset[str] = frozenset()) -> Iterable[_Element]:
    for child in node.children:
        if isinstance(child, str) or child.tag in skip:
            continue
        if child.tag in _BLOCK_TAGS:
            yield child
        yield from _blocks(child, skip)


def labelled_lines(
    html: str, label: re.Pattern[str], skip: frozenset[str] = frozenset()
) -> list[tuple[str, str]]:
    """Every rendered line, outside code, that ``label`` matches: ``(line, rest)``.

    ``label`` must define a ``rest`` group: the text after the label. Shared with
    the import-layer gate's ``Layer-Exception:`` line (#10048), which is read
    the same way for the same reasons.

    ``skip`` names further tags whose text is not read at all, wherever they
    sit: a gate that treats quoted or struck-through text as not declared
    passes ``blockquote`` and ``del``. The default reads everything outside
    code; the docs-impact gate passes :data:`UNREAD_TAGS`.
    """
    found: list[tuple[str, str]] = []
    for block in _blocks(parse_html(html), skip):
        for raw in _text_lines(block, skip):
            matched = label.match(raw)
            if matched is not None:
                found.append((raw.strip(), matched.group("rest")))
    return found


def read_declarations(html: str) -> list[Declaration]:
    """Every rendered line that opens with ``Docs-Impact:``, parsed."""
    found: list[Declaration] = []
    for line, rest in labelled_lines(html, _LABEL_RE, UNREAD_TAGS):
        parsed = DECLARATION_RE.match(rest)
        if (
            parsed is None
            or not _HAS_CONTENT_RE.search(parsed.group("reason"))
            or has_reason_placeholder(parsed.group("reason"))
        ):
            found.append(Declaration(line=line, reason=None))
        else:
            found.append(Declaration(line=line, reason=parsed.group("reason")))
    return found


# ---------------------------------------------------------------------------
# Transports (injected by the tests)
# ---------------------------------------------------------------------------


def _run(argv: list[str]) -> tuple[int, str, str]:  # pragma: no cover - I/O
    completed = subprocess.run(  # noqa: S603  # argv is only the "git" "diff" list changed_paths builds, whose rev_range is refused when it opens with a dash; no PR text is ever on a command line
        argv, capture_output=True, text=True, check=False, cwd=REPO_ROOT
    )
    return completed.returncode, completed.stdout, completed.stderr


def changed_paths(rev_range: str, run: GitRunner) -> list[str]:
    if not rev_range or rev_range.startswith("-"):
        # A leading dash would reach git as an OPTION, not a range.
        raise CouldNotJudge(f"{rev_range!r} is not a revision range")
    code, stdout, stderr = run(
        ["git", "diff", "--name-only", "--no-renames", "-z", rev_range]
    )
    if code != 0:
        raise CouldNotJudge(
            f"git diff over {rev_range!r} failed ({stderr.strip() or f'exit {code}'})"
        )
    return [path for path in stdout.split("\0") if path]


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


#: The placeholder every printed judgment-line example carries in place of the
#: reason (#10049). The gates refuse any reason containing it, whatever GitHub's
#: markdown does to ``<...>`` (it strips some, escapes others): the refusal does
#: not depend on rendering. Defined once; File-Size-Exception and Process-Guard
#: ``none`` import it.
REASON_PLACEHOLDER = "<WRITE-THE-REASON-HERE>"
REASON_PLACEHOLDER_CORE = "WRITE-THE-REASON-HERE"


def has_reason_placeholder(text: str) -> bool:
    """Whether *text* still holds the printed example's placeholder (any markup)."""
    return REASON_PLACEHOLDER_CORE in text


def example_line(served_path: str) -> str:
    """The declaration's shape, with a placeholder reason the gate REFUSES (#10049).

    The reason is a claim the author states: a ready-made one would be pasted
    blind. The gate refuses :data:`REASON_PLACEHOLDER` itself; any real
    sentence in its place passes. The path is not in the line, so no ``/``
    changes how a renderer treats the placeholder.
    """
    del served_path
    return f"Docs-Impact: none — {REASON_PLACEHOLDER}"


#: The exit of a run that judged nothing: neither a pass nor a refusal.
COULD_NOT_JUDGE_EXIT_STATUS = 3


def could_not_judge(gate: str, reason: str) -> int:
    """Say that ``gate`` judged nothing, and return the status that means so.

    Shared with the process-guard gate, which reads the same range and body.
    """
    sys.stderr.write(
        f"{gate}: NOTHING WAS JUDGED -- {reason}. This is not a verdict on "
        "the pull request; re-run once the input is readable.\n"
    )
    return COULD_NOT_JUDGE_EXIT_STATUS


def range_and_body_args(description: str, argv: list[str] | None) -> argparse.Namespace:
    """Parse the two inputs every body-reading diff gate takes."""
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument(
        "--diff-range",
        required=True,
        help="The PR's range, three-dot form, e.g. origin/main...HEAD.",
    )
    parser.add_argument(
        "--pr-body-file",
        required=True,
        help=(
            "File holding the PR body. In CI, audit-grep's live fetch (never the "
            "frozen event payload); by hand, a draft body."
        ),
    )
    return parser.parse_args(argv)


def _unknown(reason: str) -> int:
    return could_not_judge("docs-impact", reason)


def read_gate_inputs(
    gate: str,
    description: str,
    argv: list[str] | None,
    run: GitRunner | None,
    root: Path | None,
) -> tuple[argparse.Namespace, GitRunner, Path, list[str]] | int:
    """Parse the range and body arguments and read the changed paths.

    Returns the exit code instead when the range cannot be read, so a body-reading
    diff gate reports "could not judge" the same way.
    """
    args = range_and_body_args(description, argv)
    runner = run if run is not None else _run
    tree = root if root is not None else REPO_ROOT
    try:
        paths = changed_paths(args.diff_range, runner)
    except CouldNotJudge as error:
        return could_not_judge(gate, str(error))
    return args, runner, tree, paths


def main(
    argv: list[str] | None = None,
    *,
    run: GitRunner | None = None,
    render: Renderer | None = None,
    root: Path | None = None,
) -> int:
    inputs = read_gate_inputs(
        "docs-impact",
        "Fail a pull request that changes served code with no docs change "
        "and no 'Docs-Impact: none — <reason>' line (issue #9914).",
        argv,
        run,
        root,
    )
    if isinstance(inputs, int):
        return inputs
    args, runner, tree, paths = inputs

    try:
        named = executables_named_by_docs(tree)
    except OSError as error:
        return _unknown(f"a docs page could not be read ({error})")
    verdict = classify(paths, named)
    read = f"read {verdict.total} changed path(s) over {args.diff_range}"

    if not verdict.served:
        print(
            f"docs-impact: no served-path change ({read}), so nothing is owed. "
            "The rule still applies to every change; this check only forces it "
            "on the served globs."
        )
        return 0
    if verdict.docs:
        print(
            f"docs-impact: {len(verdict.served)} served-path change(s) travel "
            f"with {len(verdict.docs)} docs-surface change(s) ({read}): "
            f"{', '.join(verdict.docs[:5])}"
            f"{' …' if len(verdict.docs) > 5 else ''}. This green says a doc "
            "MOVED, not which doc should have or that it is now true -- that "
            "is the review's question."
        )
        return 0

    try:
        body_path = Path(args.pr_body_file)
        if not body_path.is_file():
            raise CouldNotJudge(f"the body file {body_path} does not exist")
        body = body_path.read_text(encoding="utf-8", errors="replace")
        renderer = render if render is not None else gh_renderer(_run_gh)
        html = render_when_labelled(renderer, body, _RAW_LABEL_RE)
    except CouldNotJudge as error:
        return _unknown(str(error))
    except Unrenderable as error:
        return _unknown(
            f"the body could not be rendered ({error}); the declaration is read "
            "from what GitHub renders, and this check will not guess it"
        )

    declarations = read_declarations(html)
    malformed = [d for d in declarations if not d.well_formed]
    served_list = ", ".join(verdict.served[:8]) + (
        " …" if len(verdict.served) > 8 else ""
    )
    if malformed or not declarations:
        sys.stderr.write(
            "docs-impact (#9914): this pull request changes served code and no "
            f"docs surface ({read}).\n  served-path changes: {served_list}\n"
        )
        for declaration in malformed:
            sys.stderr.write(
                f"  malformed declaration: {declaration.line!r} -- the only "
                "accepted form is 'Docs-Impact: none — <reason>', with a "
                "non-empty reason, on its own line outside code; replace "
                f"{REASON_PLACEHOLDER} with your own reason.\n"
            )
        sys.stderr.write(
            "  remedy: update the docs that describe this behaviour in this PR "
            "(docs/, contributing/, CONTRIBUTING.md, an integrator README, or "
            "the generated reference), OR add a line to the PR body, outside "
            "code, a blockquote and a <details> block, reading "
            "'Docs-Impact: none — <why no doc describes this change>'. The "
            "reason is reviewed as a claim. Editing the body re-runs this "
            f"check.\n  shape (state your own reason): {example_line(verdict.served[0])}\n  rule: CONTRIBUTING.md -> 'Docs travel with the code'.\n"
        )
        return 1

    reasons = "; ".join(repr(d.reason) for d in declarations)
    print(
        f"docs-impact: {len(verdict.served)} served-path change(s) and no docs "
        f"change ({read}); the PR body declares no docs impact: {reasons}. "
        "That reason is a claim for the reviewer to judge -- this check only "
        "refused an absent or empty one."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    sys.exit(main())
