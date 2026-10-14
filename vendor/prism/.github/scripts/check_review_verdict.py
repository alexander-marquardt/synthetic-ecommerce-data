"""Refuse a pull request whose review verdict FILES a finding it never filed.

This script implements the checkable half of issue #7622, and is run from the
``audit-grep`` job in ``.github/workflows/audit-grep.yaml``.

Why this exists
---------------
A review verdict used to be a single yes/no over everything it found, so a
false sentence in a docstring blocked a merge exactly as hard as a wrong number
on a shopper's screen. ``CONTRIBUTING.md`` -> "The merge gate and the
perfection gate are different gates" now splits the verdict in two: findings
whose text reaches a published artifact, or whose subject is code, BLOCK;
everything else is FILED as an issue and the pull request merges without it.

That split is only worth having if the FILE half is real. The failure mode it
invites is precise and this repository has already shipped it once: a pull
request stated that its residues were "recorded on" issues where **nothing had
been posted**. A promise reads exactly like a filing, and no reviewer re-checks
a sentence that sounds like it already happened.

So the artifact is what gets checked, never the intention. Every FILE entry in
the pull-request body must name an issue reference, and every reference named
is RESOLVED against the GitHub API before the merge. A finding that was only
promised has no number to resolve, and a number invented to satisfy the rule
does not resolve either.

The verdict is read from the RENDERED body
------------------------------------------
The body is sent to GitHub's own renderer (``POST /markdown``, ``mode=gfm``)
and the verdict is read out of the HTML that comes back -- the headings and the
list items GitHub produced, not a markdown parse of the source.

This is the design, not an implementation detail, and it replaced three rounds
of the alternative. Approximating CommonMark in Python to decide which text is
"really" a verdict was wrong three times for three different reasons -- a
fenced illustration outranking the real section; an unclosed fence blanked
wider than the renderer ends it; a fence detected inside a raw-HTML block where
GitHub sees no fence at all. Each fix closed one construct and asserted a fresh
universal about the constructs it had not tested. The surface is a block
grammar with containers, raw-HTML blocks, setext headings and info strings, and
a merge gate re-deriving it has **no oracle**.

The renderer IS the oracle, because it is definitionally what the reader sees.
Reading its output makes "the gate's reading and the reader's are identical" a
property of the mechanism rather than a claim to be defended construct by
construct, and it retired every one of those defects at once -- including two
that were still open (a setext heading, which no ATX pattern matched, and a
verdict inside ``<pre>``, which rendered as literal text and was being read as
a verdict).

⚠️ The claim this file is entitled to make is narrow and is the only one it
makes: **the gate reads the headings and list items out of the HTML GitHub
produced for this body.** It is not a claim about CommonMark. What is left to
get wrong is the HTML walk, which is small, and every case in
``tests/data/review_verdict_rendered_bodies.json`` is HTML the live renderer
actually returned rather than a shape inferred from reading this code.

The intent model
----------------
The pull-request body is the declaration surface, for the same reason
``check_closing_keywords.py`` uses it: it is what a reviewer reads and what
GitHub renders. The gate reads one section of it -- the rendered heading whose
text opens with ``Review verdict`` -- and judges only the FILE half.

Four properties, and nothing else:

1. **A verdict section that exists states its FILE half.** A section carrying
   only a BLOCKING line has aggregated, which is the behaviour the rule exists
   to end.
2. **The FILE half is not blank.** The default pull-request template ships both
   halves empty, so this is the state an author reaches by answering neither.
   It reds, which is what stops "no answer" from being the cheapest answer.
3. **Every FILE entry either declares the empty set or names an issue.** The
   sentinel spellings for the empty set are ``none`` and ``nothing`` and they
   are only valid as the sole entry. Any other entry text is a finding, and a
   finding with no issue reference in it is a promise.
4. **Every issue named resolves, and resolves to an ISSUE.** ``/issues/<n>``
   resolves pull requests too, so a body citing its own number would otherwise
   pass; a pull request is not the durable artifact a backlog view surfaces.

THE LEAVES ARE THE ENTRIES. A FILE item with a nested list under it is a
header, whatever it says, and each leaf beneath it is judged on its own --
otherwise one filed issue would license every unfiled sibling beside it.

What this gate does NOT do
--------------------------
* It does not judge the CLASSIFICATION. Whether a finding belongs in BLOCKING
  or in FILE is the reviewer's call against the artifact boundary in
  ``CONTRIBUTING.md``; no gate can read a finding and know which side it is on.
  What the gate removes is the possibility of the FILE side being free.
* It does not require the BLOCKING half to name anything. A blocking finding is
  fixed in the pull request, so it leaves its artifact in the diff.
* It does not check that the named issue CONTAINS the finding. Resolution
  proves the artifact exists and is reachable from the body; whether its text
  is faithful is a review judgement, exactly as the body's own text is.
* **It does not classify.** A code blocker declared under FILE with a real
  issue number exits 0, and that is not a hole to be patched. The success line
  says so in its own words, because a green ``audit-grep`` is otherwise read as
  "the verdict was checked", and what was checked is only that the FILE half
  named issues that exist.
* It does not red a body with no RENDERED verdict section. It reports the
  absence in words, loudly, and exits 0 -- see "The absence case" below.

The absence case
----------------
A missing section is reported as a NOTE and not as a failure, deliberately and
temporarily. Making absence red would red every pull request already open on
the day this lands, for a body heading none of their authors could have known
to write -- the false-red class this repository has spent several rounds
eliminating. The obligation to declare a verdict is carried by
``CONTRIBUTING_REVIEW.md`` and by the default pull-request template until every
open pull request carries the section; **hardening absence into a red is filed
as #7636**, not left as an intention here, which is the same discipline this
gate enforces on everyone else.

Behaviour
---------
* exit 0 -- clean. The success line NAMES the number of FILE entries scanned
  and the number of issue references looked up, so a gate that judged nothing
  cannot print a line that reads as "scanned and clean"
  (``contributing/ci-and-merge-process.md`` -> "A gate that exits 0 must name
  what it scanned").
* exit 1 -- at least one FILE entry is a promise, or names something that is
  not a resolvable issue. Every one is named, with its remedy.
* exit 3 -- the gate could not judge, and this is never reported as clean
  (``CONTRIBUTING.md`` -> "A check that COULD NOT judge must not return the
  value that means 'judged, and fine'"). Four causes: a body file that does not
  exist; the renderer could not be reached, so what the reader sees is unknown;
  an issue lookup that failed for any reason other than the issue being absent
  (a rate limit, a network error, a token without ``issues: read``); and a body
  that renders MORE THAN ONE verdict heading, where which one is the verdict is
  not something this gate may guess.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path

# ``check_closing_keywords`` is a sibling script, not an installed package, so
# its directory has to be on the path before the import below. Same shape as
# ``merge_group_dequeue_notice`` importing ``merged_over_red_gate``.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_closing_keywords import (  # noqa: E402  (path is set up just above)
    REFERENCE_PATTERN,
)

#: Rendered heading text that opens the verdict section. Matched against the
#: heading's TEXT at any level, so a setext heading (``===`` underline, which
#: renders ``<h1>``) is found by the same rule as an ATX one -- the renderer
#: has already resolved which spellings are headings.
#: Applied with ``.match``, which anchors at the start on its own -- so a
#: heading that merely CONTAINS the phrase ("Superseded: Review verdict") is
#: not a verdict heading. A leading ``^`` here would be redundant with that,
#: and a redundant guard cannot be mutation-tested: whichever of the two is
#: broken, the other still passes.
VERDICT_HEADING_RE = re.compile(r"review[ \t]+verdict\b", re.IGNORECASE)

#: One half of the verdict, matched against a rendered item's OWN text. The
#: emphasis around ``**FILE**`` is gone by this point (it is a ``<strong>``),
#: so what is left is the label, an optional separator, and the rest.
_HALF_RE = re.compile(
    r"^(?P<label>FILE|BLOCKING)\b[ \t]*(?:[:—–-][ \t]*)?(?P<rest>.*)$",
    re.IGNORECASE | re.DOTALL,
)

#: An issue reference: bare ``#N``, cross-repo ``owner/repo#N``, or the issue
#: URL form. Not restated here -- IMPORTED from ``check_closing_keywords``, which
#: is the one home for the grammar, so an author does not have to hold two
#: reference syntaxes and the two gates cannot resolve one PR body to two
#: different issues (#7985; until then this file's copy rejected ``..`` and that
#: one's did not, so ``Closes ../..#5`` named two different issues depending on
#: which gate read it).
#:
#: The traversal guard is load-bearing HERE specifically: the slug is
#: interpolated into ``repos/<owner>/<repo>/issues/<n>``, so a segment pattern
#: admitting ``..`` would let a body steer the lookup off that path and answer
#: for a different resource. The shared segment rejects exactly the all-dot
#: segments, which is the traversal class -- one notch narrower than the "must
#: open with an alphanumeric" rule this file used to carry, which also excluded
#: real repository names like ``.github``.
#: ``tests/test_issue_reference_grammar_single_source_7985.py`` pins both halves.
ISSUE_REFERENCE_RE = re.compile(REFERENCE_PATTERN)

#: Spellings that DECLARE the empty set, and they must OPEN the entry. Kept to
#: two, both unambiguous: a longer list is a place for "n/a"-shaped text to
#: hide a verdict nobody made. Anchored at the start for two reasons pulling in
#: opposite directions -- "none (the four findings all blocked)" is a real
#: answer and must not red, while "#7641 -- none of this blocks the merge"
#: carries a reference and must be judged as the finding it is.
_EMPTY_SET_RE = re.compile(r"[*_\s]*(?:none|nothing)\b", re.IGNORECASE)

_HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
_LIST_TAGS = {"ul", "ol"}

DEFAULT_REPO_SLUG = "elastic/prism"


@dataclass(frozen=True)
class IssueReference:
    """One issue reference found in a FILE entry."""

    slug: str
    number: int
    matched_text: str

    @property
    def canonical(self) -> str:
        return f"{self.slug}#{self.number}"


@dataclass(frozen=True)
class FileEntry:
    """One FILE-half entry, as rendered, and where it came from in the source.

    ``line_number`` is best-effort: the rendered text is matched back against
    the raw body, and a line is reported only when exactly one line carries it.
    It is a convenience for the human reading the failure, never something the
    verdict depends on -- which is why it is allowed to be ``None``.
    """

    text: str
    line_number: int | None = None

    @property
    def declares_empty_set(self) -> bool:
        return _EMPTY_SET_RE.match(self.text) is not None

    @property
    def references(self) -> list[IssueReference]:
        return issue_references(self.text)


@dataclass(frozen=True)
class Verdict:
    """What the RENDERED body's verdict section says."""

    present: bool
    has_file_half: bool
    entries: tuple[FileEntry, ...]


@dataclass(frozen=True)
class Resolution:
    """What the GitHub API says a reference points at."""

    kind: str
    """``issue`` / ``pull_request`` / ``absent`` / ``unreadable``."""
    detail: str = ""
    state: str = ""
    """The API's ``state`` (``open`` / ``closed``) when it answered; else empty."""


@dataclass(frozen=True)
class Violation:
    """A FILE entry that is a promise rather than a filing."""

    entry_text: str
    reason: str
    remedy: str
    line_number: int | None = None

    @property
    def where(self) -> str:
        if self.line_number is not None:
            return f"body line {self.line_number}"
        return "the verdict section"


Resolver = Callable[[IssueReference], Resolution]
Renderer = Callable[[str], str]


class Unreadable(Exception):
    """A reference could not be looked up. Never a content verdict."""


class Unrenderable(Exception):
    """The body could not be rendered, so what the reader sees is unknown."""


class Ambiguous(Exception):
    """The body renders more than one verdict section. Never a content verdict."""


# ---------------------------------------------------------------------------
# Reading the rendered body
# ---------------------------------------------------------------------------


@dataclass
class _Element:
    """One rendered element. Children are elements or literal strings."""

    tag: str
    children: list[_Element | str] = field(default_factory=list)


class _TreeBuilder(HTMLParser):
    """Build a minimal element tree from the renderer's HTML.

    Deliberately forgiving: an end tag with no open counterpart is dropped
    rather than raising, because the renderer passes raw HTML from the body
    through verbatim and a pull-request body may contain unbalanced markup.
    Nothing downstream depends on the nesting being well-formed -- headings are
    found by walking every element, and an entry's own text is read from its
    own subtree.
    """

    #: Elements that never have an end tag; pushing them would swallow their
    #: siblings into a subtree that GitHub never nested.
    VOID = frozenset(
        [
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        ]
    )

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.root = _Element("#document")
        self._stack: list[_Element] = [self.root]

    def handle_starttag(self, tag: str, attrs: object) -> None:
        if tag in self.VOID:
            return
        element = _Element(tag)
        self._stack[-1].children.append(element)
        self._stack.append(element)

    def handle_startendtag(self, tag: str, attrs: object) -> None:
        return

    def handle_endtag(self, tag: str) -> None:
        # Close the nearest OPEN element of this tag, and nothing if there is
        # none. Popping unconditionally would let a stray ``</div>`` in a body
        # close the list around it and re-parent every following item.
        for index in range(len(self._stack) - 1, 0, -1):
            if self._stack[index].tag == tag:
                del self._stack[index:]
                return

    def handle_data(self, data: str) -> None:
        self._stack[-1].children.append(data)


def parse_html(html: str) -> _Element:
    """The renderer's HTML as an element tree."""
    builder = _TreeBuilder()
    builder.feed(html)
    builder.close()
    return builder.root


def _elements(node: _Element) -> Iterator[_Element]:
    """Every element under ``node``, in document order."""
    for child in node.children:
        if isinstance(child, _Element):
            yield child
            yield from _elements(child)


def _own_text(node: _Element) -> str:
    """An element's text, EXCLUDING any nested list.

    Excluding the nested list is what makes a header distinguishable from an
    entry: ``- **FILE**`` with items under it renders as an ``<li>`` whose own
    text is just the label, and whose leaves are the findings.
    """
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, str):
            parts.append(child)
        elif child.tag not in _LIST_TAGS:
            parts.append(_own_text(child))
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def _sub_items(node: _Element) -> list[_Element]:
    """The list items of a list nested directly under ``node``."""
    items: list[_Element] = []
    for child in node.children:
        if isinstance(child, _Element) and child.tag in _LIST_TAGS:
            items.extend(
                grandchild
                for grandchild in child.children
                if isinstance(grandchild, _Element) and grandchild.tag == "li"
            )
    return items


def _leaves(item: _Element) -> list[_Element]:
    """``item`` itself if it has no nested list, else its leaves."""
    children = _sub_items(item)
    if not children:
        return [item]
    return [leaf for child in children for leaf in _leaves(child)]


def _heading_level(tag: str) -> int:
    return int(tag[1])


def _locate(source: str | None, text: str) -> int | None:
    """The 1-based line of ``source`` carrying ``text``, when exactly one does.

    Best-effort by construction: the rendered text has lost its markup, so this
    matches on the collapsed-whitespace form and reports nothing when the match
    is ambiguous. A wrong line number in a remedy is worse than none.
    """
    if not source or not text:
        return None
    needle = re.sub(r"\s+", " ", text).strip()
    hits = [
        index + 1
        for index, line in enumerate(source.splitlines())
        if needle in re.sub(r"\s+", " ", line)
    ]
    return hits[0] if len(hits) == 1 else None


def read_verdict(html: str, source: str | None = None) -> Verdict:
    """Read the FILE half out of the body GitHub rendered.

    ``source`` is the raw markdown, used only to recover line numbers for the
    failure messages.

    Raises :class:`Ambiguous` when more than one verdict heading renders. Two
    verdict sections is an AMBIGUOUS body, not a clean one; taking the first
    would silently pick a winner.
    """
    document = parse_html(html)
    ordered = list(_elements(document))
    headings = [
        (index, element)
        for index, element in enumerate(ordered)
        if element.tag in _HEADING_TAGS
        and VERDICT_HEADING_RE.match(_own_text(element)) is not None
    ]
    if len(headings) > 1:
        raise Ambiguous(f"the body renders {len(headings)} 'Review verdict' headings")
    if not headings:
        return Verdict(present=False, has_file_half=False, entries=())

    start, heading = headings[0]
    level = _heading_level(heading.tag)
    end = len(ordered)
    for index in range(start + 1, len(ordered)):
        tag = ordered[index].tag
        if tag in _HEADING_TAGS and _heading_level(tag) <= level:
            end = index
            break

    entries: list[FileEntry] = []
    has_file_half = False
    for element in ordered[start + 1 : end]:
        if element.tag not in {"li", "p"}:
            continue
        half = _HALF_RE.match(_own_text(element))
        if half is None or half.group("label").casefold() != "file":
            continue
        has_file_half = True
        children = _sub_items(element)
        if children:
            for child in children:
                for leaf in _leaves(child):
                    text = _own_text(leaf)
                    entries.append(
                        FileEntry(text=text, line_number=_locate(source, text))
                    )
        else:
            rest = half.group("rest").strip()
            if rest:
                entries.append(FileEntry(text=rest, line_number=_locate(source, rest)))
    return Verdict(present=True, has_file_half=has_file_half, entries=tuple(entries))


# ---------------------------------------------------------------------------
# Talking to GitHub
# ---------------------------------------------------------------------------


def issue_references(text: str) -> list[IssueReference]:
    """Every issue reference in ``text``, in order, duplicates kept."""
    found: list[IssueReference] = []
    for match in ISSUE_REFERENCE_RE.finditer(text):
        if match.group("url_number") is not None:
            slug = f"{match.group('url_owner')}/{match.group('url_repo')}"
            number = int(match.group("url_number"))
        else:
            owner = match.group("owner")
            repo = match.group("repo")
            slug = f"{owner}/{repo}" if owner and repo else DEFAULT_REPO_SLUG
            number = int(match.group("number"))
        found.append(
            IssueReference(
                slug=slug.lower(), number=number, matched_text=match.group(0)
            )
        )
    return found


def gh_renderer(runner: Callable[[list[str]], tuple[int, str, str]]) -> Renderer:
    """Render a body through ``POST /markdown``, ``mode=gfm``.

    The payload goes through a temp FILE rather than a command line: a pull
    request body is arbitrary text and belongs nowhere near an argv.
    """

    def render(body: str) -> str:
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", encoding="utf-8", delete=False
        ) as handle:
            json.dump({"text": body, "mode": "gfm"}, handle)
            payload = handle.name
        try:
            code, stdout, stderr = runner(
                [
                    "gh",
                    "api",
                    "/markdown",
                    "--method",
                    "POST",
                    "--input",
                    payload,
                    "-H",
                    "Content-Type: application/json",
                ]
            )
        finally:
            Path(payload).unlink(missing_ok=True)
        if code != 0:
            reason = stderr.strip() or stdout.strip() or f"exit {code}"
            if _RATE_LIMITED_RE.search(reason):
                reason += _reset_note(runner)
            raise Unrenderable(reason)
        return stdout

    return render


#: A refusal for the spent REST quota: HTTP 403 or 429, or the words GitHub uses.
_RATE_LIMITED_RE = re.compile(r"\b(?:403|429)\b|rate limit", re.IGNORECASE)


def _reset_note(runner: Callable[[list[str]], tuple[int, str, str]]) -> str:
    """``; the quota resets at <UTC time>``, or ``""`` when the lookup fails.

    ``GET /rate_limit`` does not spend the quota it reports, so asking it while
    the quota is spent works; the epoch it returns is the core bucket's reset,
    the bucket ``POST /markdown`` draws on (#11059).
    """
    try:
        code, stdout, _stderr = runner(
            ["gh", "api", "rate_limit", "--jq", ".resources.core.reset"]
        )
        if code != 0:
            return ""
        reset = datetime.fromtimestamp(int(stdout.strip()), tz=UTC)
    except (ValueError, OSError, OverflowError):
        return ""
    return f"; the shared REST quota resets at {reset:%Y-%m-%dT%H:%M:%SZ}"


def render_when_labelled(renderer: Renderer, body: str, label: re.Pattern[str]) -> str:
    """The body rendered, or ``""`` when the body does not hold the gate's label.

    A body without the label as written cannot render a line that carries it, so
    the verdict is the same without the call, and the Markdown API (the shared
    REST quota, 5,000 an hour for every agent) is not spent on it. A body that
    spells the label only through an escape or a character entity is therefore
    read as declaring nothing, never as a pass (#11059).
    """
    return renderer(body) if label.search(body) else ""


def gh_resolver(runner: Callable[[list[str]], tuple[int, str, str]]) -> Resolver:
    """Resolve a reference through ``gh api``.

    Split from the verdict reading so the decision table is provable without a
    network call -- a real injected callable, not a suppression-shaped mock.
    """

    def resolve(reference: IssueReference) -> Resolution:
        code, stdout, stderr = runner(
            ["gh", "api", f"repos/{reference.slug}/issues/{reference.number}"]
        )
        if code != 0:
            combined = f"{stdout}\n{stderr}"
            if "Not Found" in combined or "HTTP 404" in combined:
                return Resolution(kind="absent", detail=stderr.strip())
            return Resolution(
                kind="unreadable", detail=stderr.strip() or stdout.strip()
            )
        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError as error:  # pragma: no cover - defensive
            return Resolution(kind="unreadable", detail=str(error))
        if not isinstance(payload, dict):  # pragma: no cover - defensive
            return Resolution(kind="unreadable", detail="response was not an object")
        state = payload.get("state")
        state = state if isinstance(state, str) else ""
        if payload.get("pull_request") is not None:
            return Resolution(kind="pull_request", state=state)
        return Resolution(kind="issue", state=state)

    return resolve


def _run_gh(argv: list[str]) -> tuple[int, str, str]:  # pragma: no cover - I/O
    completed = subprocess.run(  # noqa: S603  # non-shell argv: the fixed literals "gh"/"api" plus either an API path whose only interpolated values are an owner/repo slug and an integer, both produced by ISSUE_REFERENCE_RE (no path separator, and no segment that is ALL dots -- so no "." or ".." traversal component; a LEADING dot is admitted since #7985 because ".github" is a real repository name and rejecting it bought nothing), or a temp-file path this module created. No pull-request text is ever placed on a command line. NOTE for anyone merging a competing edit to this justification: a wording that says "no leading dot" predates #7985 and is FALSE against the current grammar -- ".github" matches. Keep this sentence, not that one.
        argv, capture_output=True, text=True, check=False
    )
    return completed.returncode, completed.stdout, completed.stderr


# ---------------------------------------------------------------------------
# Judging
# ---------------------------------------------------------------------------


def find_violations(verdict: Verdict, resolve: Resolver) -> list[Violation]:
    """Every FILE entry that is a promise rather than a filed issue.

    Raises :class:`Unreadable` when a lookup fails for any reason other than
    the issue being absent: an unknown answer must not collapse into "clean".
    """
    if verdict.present and not verdict.has_file_half:
        return [
            Violation(
                entry_text="",
                reason=(
                    "the verdict section states no FILE half, so the review "
                    "aggregated instead of classifying"
                ),
                remedy=(
                    "add a FILE line to the verdict section: 'none' if every "
                    "finding blocks, otherwise the issue you filed for each "
                    "finding that does not"
                ),
            )
        ]
    if verdict.present and not verdict.entries:
        # The template ships both halves UNFILLED, so this is the state an
        # author reaches by opening a pull request and answering neither. It
        # has to red: a blank half that passed would make "no answer" the
        # cheapest answer, which is the aggregation this rule replaced.
        return [
            Violation(
                entry_text="",
                reason="the FILE half states nothing",
                remedy=(
                    "write 'none' if the review filed nothing, otherwise one "
                    "line per finding naming the issue you filed for it"
                ),
            )
        ]

    violations: list[Violation] = []
    for entry in verdict.entries:
        if entry.declares_empty_set:
            if len(verdict.entries) > 1:
                violations.append(
                    Violation(
                        line_number=entry.line_number,
                        entry_text=entry.text,
                        reason=(
                            "the empty set is declared alongside "
                            f"{len(verdict.entries) - 1} other FILE entr(y/ies), "
                            "so the half contradicts itself"
                        ),
                        remedy=(
                            "delete the 'none' line, or delete the entries beside it"
                        ),
                    )
                )
            continue
        references = entry.references
        if not references:
            violations.append(
                Violation(
                    line_number=entry.line_number,
                    entry_text=entry.text,
                    reason="names no issue, so it is a promise and not a filing",
                    remedy=(
                        "file the issue NOW and write its number on this line. "
                        "A FILE finding merges without being fixed; the issue "
                        "is the only artifact left behind"
                    ),
                )
            )
            continue
        for reference in references:
            resolution = resolve(reference)
            if resolution.kind == "issue":
                continue
            if resolution.kind == "unreadable":
                raise Unreadable(
                    f"{reference.canonical}: {resolution.detail or 'lookup failed'}"
                )
            if resolution.kind == "pull_request":
                violations.append(
                    Violation(
                        line_number=entry.line_number,
                        entry_text=entry.text,
                        reason=f"{reference.canonical} is a PULL REQUEST, not an issue",
                        remedy=(
                            "file an issue for the finding and cite that "
                            "number. A merged pull request is not a backlog "
                            "artifact -- it is the surface the finding has to "
                            "escape from"
                        ),
                    )
                )
                continue
            violations.append(
                Violation(
                    line_number=entry.line_number,
                    entry_text=entry.text,
                    reason=f"{reference.canonical} does not exist",
                    remedy=(
                        "file the issue and cite the number it actually got. "
                        "A number that does not resolve is the promise this "
                        "gate exists to catch"
                    ),
                )
            )
    return violations


def _read_body(path_text: str) -> str | None:
    if not path_text:
        sys.stderr.write(
            "review-verdict gate: NOT EVERYTHING WAS SCANNED -- no PR-body path "
            "was given. This is not a content verdict; the gate could not run.\n"
        )
        return None
    path = Path(path_text)
    if not path.is_file():
        sys.stderr.write(
            "review-verdict gate: NOT EVERYTHING WAS SCANNED -- the PR-body file "
            f"{path} does not exist. This is not a content verdict; the gate "
            "could not run.\n"
        )
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def main(
    argv: list[str] | None = None,
    *,
    resolve: Resolver | None = None,
    render: Renderer | None = None,
) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when a pull request's review verdict FILES a finding whose "
            "issue does not exist (issue #7622)."
        )
    )
    parser.add_argument(
        "--pr-body-file",
        required=True,
        help="File holding the PR body, fetched live (never the frozen event payload).",
    )
    args = parser.parse_args(argv)

    body = _read_body(args.pr_body_file)
    if body is None:
        return 3

    renderer = render if render is not None else gh_renderer(_run_gh)
    try:
        html = renderer(body)
    except Unrenderable as error:
        sys.stderr.write(
            "review-verdict gate: NOT EVERYTHING WAS SCANNED -- the body could "
            f"not be rendered ({error}). This gate reads the verdict out of the "
            "HTML GitHub produces, so with no rendering it does not know what "
            "the reader sees, and it will not guess. Re-run once the API is "
            "reachable. This is not a content verdict.\n"
        )
        return 3

    try:
        verdict = read_verdict(html, source=body)
    except Ambiguous as error:
        sys.stderr.write(
            f"review-verdict gate: NOT EVERYTHING WAS SCANNED -- {error}. Which "
            "one is the verdict is not something this gate may guess, so it "
            "refuses instead of picking a winner. Leave exactly one rendered "
            "'Review verdict' heading. This is not a content verdict.\n"
        )
        return 3

    if not verdict.present:
        # Determined and empty, said in words that cannot be read as a scan.
        print(
            "review-verdict gate: the rendered PR body carries no 'Review "
            "verdict' heading, so NO FILE ENTRY WAS SCANNED -- this is not a "
            "clean verdict. CONTRIBUTING_REVIEW.md requires the classified "
            "verdict and the default PR template ships the section; #7636 "
            "tracks turning this note into a red."
        )
        return 0

    resolver = resolve if resolve is not None else gh_resolver(_run_gh)
    try:
        violations = find_violations(verdict, resolver)
    except Unreadable as error:
        sys.stderr.write(
            "review-verdict gate: NOT EVERYTHING WAS SCANNED -- an issue lookup "
            f"failed ({error}). A reference that could not be read is UNKNOWN, "
            "not clean; re-run once the API is reachable, and check the job's "
            "token carries 'issues: read'. This is not a content verdict.\n"
        )
        return 3

    findings = [entry for entry in verdict.entries if not entry.declares_empty_set]
    looked_up = sum(len(entry.references) for entry in findings)
    scanned = (
        f"scanned {len(verdict.entries)} FILE entr(y/ies), of which "
        f"{len(findings)} name a finding, and looked up {looked_up} issue "
        "reference(s)"
    )
    if violations:
        sys.stderr.write(
            "review-verdict gate (#7622): the FILE half of this review verdict "
            "promises what it does not file.\n\n"
        )
        for violation in violations:
            sys.stderr.write(f"  {violation.where}: {violation.reason}\n")
            if violation.entry_text:
                sys.stderr.write(f"    entry: {violation.entry_text!r}\n")
            sys.stderr.write(f"    remedy: {violation.remedy}\n")
        sys.stderr.write(
            "\nA FILE finding is one the merge proceeds without fixing, so the "
            "issue is the ONLY thing left behind. This repository has already "
            "shipped a pull request claiming findings were recorded on issues "
            "where nothing had been posted -- which is why the artifact is what "
            "is checked here and the sentence is not.\n"
            f"\n{scanned}.\n"
        )
        return 1

    print(
        f"review-verdict gate: every FILE entry names a filed issue; {scanned}. "
        "This green says the FILE half named issues that EXIST -- it does not "
        "say any finding was classified correctly, which no gate can check."
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    sys.exit(main())
