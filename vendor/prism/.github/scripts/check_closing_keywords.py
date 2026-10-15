"""Refuse a pull request that would close an issue it never declared.

This script implements the closing-keyword gate filed as issue #7407, and is
run from the ``audit-grep`` job in ``.github/workflows/audit-grep.yaml``.

Why this exists
---------------
GitHub's auto-close parser is purely lexical, and it reads more surfaces than
the manual prescription in ``CONTRIBUTING.md`` used to name. GitHub's own
documentation of "Linking a pull request to an issue" states three things this
gate is built on:

* nine keyword spellings close an issue -- ``close``, ``closes``, ``closed``,
  ``fix``, ``fixes``, ``fixed``, ``resolve``, ``resolves``, ``resolved``;
* the keyword may be followed by a colon and may be uppercase, so ``Closes: #10``
  and ``CLOSES #10`` both count;
* a closing keyword in a COMMIT MESSAGE closes the issue when the commit lands
  on the default branch -- and, unlike a body reference, the pull request is
  then not listed as a linked pull request, so nothing in the pull-request UI
  shows that it is going to happen.

That last point is what makes this repository specifically exposed. It merges
with ``squash_merge_commit_message: "COMMIT_MESSAGES"`` (readable with
``gh api repos/<owner>/<repo> --jq '.squash_merge_commit_message'``), so every
branch commit message is concatenated verbatim into the squash commit that
lands on ``main`` and is parsed there.

It already nearly fired. A pull request whose body had been correctly cleaned,
and whose ``closingIssuesReferences`` named only the issue it was actually for,
carried a backticked closing keyword inside one commit message while ARGUING
that the referenced issue must stay open. Backticks do not neutralise a lexical
parser. It was caught by a human verification pass; no job scanned for it.

The grammar this gate models, MEASURED (#9053)
----------------------------------------------
Everything above was read out of GitHub's documentation, and documentation is
not a parser. Measurement says the two surfaces this gate reads are parsed with
TWO DIFFERENT separator grammars -- the commit surface spans a line break, the
body surface does not -- which no documentation states and which the previous
revision of this file got wrong in the direction that ships live references.

Method, recorded so the next reader checks this against GitHub rather than
against the regex below. In a SCRATCH repository, one target issue per
spelling. The commit-surface rows are commits pushed straight to the default
branch, read back as each issue's OPEN/CLOSED state. The body-surface rows are
one pull request whose body carries every spelling, read back as
``closingIssuesReferences`` through the GraphQL API. Measured 2026-09-15.

The first column is the fixture name in ``MEASURED_SEPARATORS`` (the gate's
test module), and a test PARSES this table and asserts it agrees with that
fixture set row for row. A table stating the measurement in prose beside a
fixture set stating it in code is two statements of one fact that can drift,
which is the defect class this whole file is about.

    fixture name              | spelling                  | commit   | body
    ------------------------- | ------------------------- | -------- | ----------
    bare space                | ``KEYWORD<sp>#N``         | closes   | links
    bare tab                  | ``KEYWORD<tab>#N``        | closes   | not probed
    bare newline              | ``KEYWORD<nl>#N``         | closes   | NO link
    bare blank line           | ``KEYWORD<nl><nl>#N``     | closes   | NO link
    bare no-break space       | ``KEYWORD<nbsp>#N``       | NO close | not probed
    colon space               | ``KEYWORD:<sp>#N``        | closes   | links
    colon tab                 | ``KEYWORD:<tab>#N``       | closes   | not probed
    colon newline             | ``KEYWORD:<nl>#N``        | closes   | NO link
    colon blank line          | ``KEYWORD:<nl><nl>#N``    | closes   | NO link
    colon no space            | ``KEYWORD:#N``            | NO close | NO link
    colon no-break space      | ``KEYWORD:<nbsp>#N``      | NO close | not probed
    nothing at all            | ``KEYWORD#N``             | NO close | not probed
    bare newline then a word  | ``KEYWORD<nl>the issue #N`` | NO close | not probed
    colon newline then a word | ``KEYWORD:<nl>the issue #N`` | NO close | not probed

A reference with NO keyword in front of it closes nothing on either surface,
which is the negative control the whole probe needs and is pinned separately.

Three of those rows are load-bearing:

* the ``colon newline`` row CLOSES from a commit message. That is the row this
  gate used to miss: its colon branch admitted horizontal whitespace only while
  its bare branch admitted any whitespace, so the MORE EXPLICIT spelling was
  the LESS caught one. The gap was a real hole and not merely an internal
  inconsistency, and a commit carrying that spelling went green and landed on
  the default branch verbatim;
* the BODY surface spans NO line break, in either branch. The licence side's
  same-line rule is therefore the ACCURATE model of the parser it faces, rather
  than the conservative guess this file used to call it;
* ``KEYWORD:#N`` with no space closes nothing, on either surface, and is
  matched here on both sides anyway -- see the "wider" bullet above. That
  is the ``colon no space`` row.

Two boundary rows say why the reference must sit IMMEDIATELY after the
separator: with a word in between -- a keyword, a line break, ``the issue``,
then the reference -- nothing closes, on the commit surface, in either the
bare or the colon spelling. Two more confirm what the file previously assumed
without measuring: a keyword inside a fenced block in a commit message still
closes, and a leading word does not disarm one either -- the future-tense
spelling this gate has always treated as a hit really is one.

One consequence for the LICENCE side, which belongs to #7414 rather than here:
a body that declares with ``KEYWORD:#N`` is honoured by this gate and resolved
by GitHub into NO linked issue at all. The declaration is then invisible in the
pull-request UI while still licensing the commit-message twin. That is the
residual #7414 names -- the licence set is parsed from the body text, not read
back from ``closingIssuesReferences`` -- now with a measured instance.

The intent model
----------------
A pull request that MEANS to close an issue must still be able to, so the gate
cannot simply ban the keyword. It needs a signal for intent, and the pull
request body is the right one:

* the body is the author's DECLARATION -- it is what GitHub resolves into
  ``closingIssuesReferences``, what the pull-request UI shows as a linked
  issue, and what a reviewer reads;
* a keyword in a commit message or in the title closes just as effectively but
  is declared NOWHERE a reviewer looks.

So the rule is a set difference, not a ban:

    RED  <=>  {issues referenced by a closing keyword in any commit message
               or in the pull-request title}
              MINUS
              {issues referenced by a closing keyword in the body}
              is non-empty.

The asymmetry is deliberate. A body reference with no commit-message twin is
the normal, healthy case and is never a finding -- this gate has no opinion on
whether a DECLARED close is correct, which stays a review judgement. Only an
UNDECLARED close is mechanical, and only an undeclared close is what escaped.

The remedy is always cheap and never blocks real intent: if the close is meant,
write it in the body too, which is what makes it visible in the pull-request UI
in the first place. If it is not meant, reword the commit message.

What this gate does NOT do
--------------------------
* It does not judge a DECLARED close. An author who writes a closing keyword in
  the body for the wrong issue is still only caught by review; that is the
  manual half of the rule in ``CONTRIBUTING.md`` and it stays manual.
* It does not read repository merge settings. A gate whose verdict depends on
  state outside the commit reds pull requests that did not change -- the
  false-red class this repository has spent several rounds eliminating -- so
  the ``COMMIT_MESSAGES`` setting is documented, not queried. If that setting
  ever changes, this gate becomes conservative rather than wrong.
* It does not check that a DECLARATION the author wrote is one GitHub will
  actually resolve. The declared set is parsed from the body text, not read
  back from ``closingIssuesReferences``, so a declaration THIS gate honours
  can still be one the pull-request UI never renders as a linked issue.
  Building the licence set from ``closingIssuesReferences`` -- the set GitHub
  itself resolves -- remains filed as #7414. What that residual is NOT any
  more is a licence for a quotation: see "Two patterns, two jobs" below.
* It does not see a declaration written where a reviewer does not read it --
  a fenced or indented code block, an HTML comment, a ``<pre>``, a
  ``<details>`` -- because all of those are STRIPPED before the declaration
  scan. That direction is deliberate: a body whose only declaration is
  invisible reds, and the remedy is to write it in the open.
* It has EDGES, and they are filed rather than implied. The comment stripper
  runs before the fence walk, so an unterminated ``<!--`` inside a fence, or a
  comment spanning an opening fence, can blank or desync the remainder; and a
  declaration written mid-sentence does not count, which is intentional. All
  three cost a false RED and one reworded line -- never a licence -- and are
  recorded in #7970 with the measurement that bounds them.
* Its RED side is WIDER than GitHub, but not where this file used to say it
  was. The two respects it named -- the issue-URL reference form, and a keyword
  with another word in front of it, the future-tense spelling included -- were
  written down as unmeasured guesses; measured, GitHub performs BOTH, so the
  gate is exact there rather than generous. Where it is genuinely wider is the
  separator: ``KEYWORD:#N`` with no space, and a NO-BREAK SPACE in place of the
  space, each match here and close NOTHING on GitHub. Those two stay wide,
  because an undeclared close is worth a red whether or not GitHub performs it,
  and the remedy -- declare it in the body, or rephrase so that no closing
  keyword is immediately followed by the reference -- is identical either way.
  See "The grammar this gate models" below for the measurement.

Two patterns, two jobs (#7966)
------------------------------
The RED side and the LICENCE side are derived by SEPARATE patterns, and that
separation is load-bearing rather than tidiness. They pull in opposite
directions: widening a pattern strengthens the red side (more closing keywords
caught) and WEAKENS the licence side (more body text counted as a declaration).
One pattern serving both therefore cannot be right for both, and the version of
this gate that used one was measured turning green on two bodies that declared
nothing:

* the gate's OWN failure output pasted into the body -- the text names the
  issue, so the issue entered the declared set. The first thing a person does
  with a red is quote it while working out what it means, and that silenced it;
* a disclaimer saying the OPPOSITE of a declaration -- "this PR does not close
  #7947" -- which also matched, and also turned it green.

So:

* the RED pattern (``CLOSING_KEYWORD_RE``) stays liberal and unchanged. It
  matches a closing keyword ANYWHERE in a commit message or the title, in any
  spelling, with or without a leading word. Anything else would let a commit
  silently close an issue, which is the whole point of the gate;
* the DECLARATION pattern (``DECLARATION_RE``) is narrow. A declaration is a
  LINE of the body that BEGINS with a closing keyword immediately followed by
  the reference -- optionally after one list marker (bullet ``-``/``*``/``+``,
  ordered ``1.``/``1)``, either of those plus a task-list ``[x]``), which is
  how a body written as a list still declares. Nothing else declares.

The two sides use the SAME horizontal-whitespace class between the keyword and
the reference, and that is a correction rather than a detail: a first version
spelled the licence side ``[ \\t]`` while the red side's ``\\s`` matched U+00A0
and its relatives, so one NO-BREAK SPACE made the two patterns give OPPOSITE
answers about one string -- and the remedy text then told the author to write
what they had already written. Two patterns disagreeing about one input is the
subject of this whole file. See ``_H_SPACE`` for the containment argument.

What that buys, stated as the three shapes it refuses, each pinned by a test:

* a NEGATION -- "this PR does not close #7947" -- does not begin the line with
  the keyword, so it declares nothing;
* a QUOTATION of this gate's own output does not either. No line this script
  prints begins with a closing keyword followed by a reference, and a test
  runs the live failure text back through the declaration scan to keep it that
  way. The gate's output is paste-immune BY CONSTRUCTION, not by convention;
* a reference inside a FENCED CODE BLOCK, an INDENTED code block, an HTML
  comment, a ``<pre>`` or a ``<details>`` does not declare. A fence was never
  the only way to render a declaration as something a reviewer does not read:
  four spaces or a tab IS a code block in CommonMark, ``<pre>`` renders as
  code, and ``<details>`` renders COLLAPSED -- the last of which is common in
  real pull-request bodies and is the sharpest of the three, because this
  gate's entire intent model is that the body is what a REVIEWER READS.

This is the same defence ``check_review_verdict.py`` already uses for its own
body-parsed declaration -- ``_HALF_RE`` anchors ``FILE``/``BLOCKING`` at the
start of a line -- so the shape here is a second instance of a pattern this
repository had already found to be the right one, not a new invention.

Where the two patterns DO agree is the grammar of a reference itself -- the
nine keyword spellings, the colon form, ``#N`` / ``OWNER/REPO#N`` / issue-URL.
That fragment is shared deliberately, because a reference is the same object on
both sides; what differs is the CONTEXT each side demands around it. Sharing
the reference grammar is not sharing the pattern.

Both directions of the asymmetry are safe. A declaration this gate refuses to
honour costs the author one reworded line. A quotation it wrongly honours costs
a silently closed issue nobody notices.

Behaviour
---------
* exit 0 -- clean; prints the scanned-commit count and the declared set.
* exit 1 -- at least one undeclared closing reference; every one is named, with
  the commit that carries it.
* exit 3 -- the gate could not scan. An input file that does not exist, a
  commit record stream containing zero commits, and a stream whose RECORD
  STRUCTURE is not the one this gate reads -- the NUL terminators and the
  ``%H`` line -- are each reported as "nothing was scanned" and are NEVER
  reported as clean. A pull request always has at least one commit, so a zero
  count means the range was not computed, not that the branch is empty; and a
  structurally wrong stream does not fail to parse, it parses into FEWER
  records than it holds, which used to exit 0 over a fraction of the input
  (#9220).

  STRUCTURE IS NOT CONTENT, and this bullet used to say "not in the
  ``git log -z --format='%H%n%B'`` format", which claimed more than the code
  checks. ``--format='%H%n%b'`` -- ONE character off -- has the right
  terminators, the right SHA lines and the right count, and carries the BODY
  without the subject. It is accepted and it is scanned, over a surface with
  every subject line missing. See :func:`record_stream_defect`, which names
  that residue and why no cheap fourth arm closes it.

Exit 3 rather than exit 1 on purpose, and printed in those words: a red that
means "the gate could not read its input" is a different thing for a human to
act on than a red that means "your commit message closes something", and the
checks list shows only the color.

The referenced issue must be OPEN (#11221)
------------------------------------------
With ``--check-issue-state`` the gate also reads the state of every DECLARED
closing reference (the body's, never a prose mention) through the API, because
a PR that closes an already-closed issue is usually a duplicate or a stale
branch. Decided cases: a closed issue is refused, naming the issue and the
state; a number that is a pull request, and a reference to another repository
(the job's token reads this one), are noted and not judged; a 404 or an
unreachable API is "could not check", exit 3, neither a pass nor the closed
refusal; a closed issue outranks an unchecked one. On ``merge_group`` the
findings are printed and the exit is 0, since an earlier entry of the same
group or a sibling PR may have closed the issue after the review.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# The shared half: the GRAMMAR of a closing reference.
#
# Both sides of the set difference recognise the same object -- a keyword and
# the issue it names -- so these fragments are shared on purpose. What is NOT
# shared is the context each side demands around them; see "Two patterns, two
# jobs" in the module docstring for why sharing the whole pattern is the bug
# this separation fixes (#7966).
# ---------------------------------------------------------------------------

# The nine spellings GitHub honours, and only those. ``close[sd]?`` is close /
# closes / closed, ``fix(?:e[sd])?`` is fix / fixes / fixed, ``resolve[sd]?`` is
# resolve / resolves / resolved. ``re.IGNORECASE`` covers the uppercase form.
# A word boundary on each side stops ``prefixes`` and ``foreclosed`` matching.
_KEYWORD = r"\b(?P<keyword>close[sd]?|fix(?:e[sd])?|resolve[sd]?)\b"

# One segment of an ``owner/repo`` slug: at least one character, and never ALL
# dots. ``.`` and ``..`` are the path-traversal segments and are not repository
# names; ``.github`` is one, so a rule spelled "must open with an alphanumeric"
# would be one step broader than the hazard it is defending against and would
# drop ``elastic/.github#5`` on the floor.
#
# Why this is one definition and not two (#7985). ``check_review_verdict``
# interpolates the slug into ``gh api repos/<owner>/<repo>/issues/<n>`` and
# guarded its own copy against ``..``; this file's copy did not, so on the SAME
# PR body ``Closes ../..#5`` resolved here to the slug ``../..`` and there to a
# bare ``#5`` against the default repository. Two gates reading one body and
# naming two different issues is #7966 in another costume, so the grammar lives
# here once and that gate imports it.
_SLUG_SEGMENT = r"[A-Za-z0-9._-]*[A-Za-z0-9_-][A-Za-z0-9._-]*"

# The reference: a bare ``#N``, an ``OWNER/REPO#N`` cross-repository reference,
# or the issue-URL form.
REFERENCE_PATTERN = (
    r"(?:"
    r"https?://github\.com/(?P<url_owner>" + _SLUG_SEGMENT + r")"
    r"/(?P<url_repo>" + _SLUG_SEGMENT + r")/issues/(?P<url_number>\d+)"
    r"|(?:(?P<owner>" + _SLUG_SEGMENT + r")/(?P<repo>" + _SLUG_SEGMENT + r"))?"
    r"\#(?P<number>\d+)"
    r")"
)
"""The grammar of an issue reference, shared with ``check_review_verdict``.

Public because that gate compiles it as its own ``ISSUE_REFERENCE_RE``; the two
must honour the same three spellings or one gate answers for an issue the other
never saw. ``tests/test_issue_reference_grammar_single_source_7985.py`` pins it.
"""

# The RED side's separator, modelling GitHub's COMMIT-message parser as
# MEASURED -- see "The grammar this gate models" in the module docstring for
# the probe and its rows. BOTH branches admit any whitespace, line breaks
# included, because the measurement says that parser does: a colon ending one
# line and the reference opening the next CLOSES, and so does the same span
# with a blank line in it.
#
# The colon branch used to read ``:[ \t]*`` -- horizontal whitespace only --
# while the bare branch already read ``\s+``. A bare keyword at end of line was
# therefore a hit and the colon spelling of the same span was not, so the MORE
# EXPLICIT form was the LESS caught one and a commit carrying it went green
# (#9053). Recomputed over the 1000 most recent commits of this repository's
# own history, widening the branch adds exactly ONE red, and that one is the
# commit which prompted the issue.
#
# Still deliberately WIDER than the measurement in two places, both kept
# because an undeclared close is worth a red whether or not GitHub performs it:
# ``Closes:#1`` with no space matches here, and so does a NO-BREAK SPACE
# separator, and neither closes anything on GitHub. What must NOT match still
# does not: ``Closes#1`` has no separator at all, and this repository's
# ``fix(scope): ...`` subject prefix puts ``(`` where a separator would go.
_SEPARATOR = r"(?::\s*|\s+)"

# Horizontal whitespace: every whitespace character EXCEPT a line break. That
# is deliberately spelled as "not (non-whitespace or a line break)" rather than
# as ``[ \t]``, and the reason is the defect this file was just fixed for in
# miniature. ``\s`` on the red side matches U+00A0 NO-BREAK SPACE, U+2007 and
# U+202F -- all of which a Markdown editor or a paste can put between the
# keyword and the reference. A licence side spelling ``[ \t]`` would then answer
# NO to the very string the red side answers YES to, and the failure text would
# tell the author to write what they had already written. Two patterns
# disagreeing about one input is exactly #7966, so they are made to agree here
# on purpose.
#
# The containment argument, stated because it is what makes the asymmetry safe:
# horizontally, ``\s`` (red) is a SUBSET of ``[^\S\r\n]`` (licence) plus the
# line break. So no string can be a hit on the red side and unrecognisable on
# the licence side for a whitespace reason -- the only red-matches /
# licence-refuses whitespace case left is a LINE BREAK, which is the deliberate
# rule below.
#
# That containment now holds on BOTH branches of the separator, which it did
# not before #9053. The red side's COLON branch used to spell horizontal space
# as ``[ \t]`` while the licence side spelled it ``[^\S\r\n]``, so one
# NO-BREAK SPACE after a colon DECLARED without ever being able to red -- the
# same two-patterns-one-string shape as the defect above, mirrored. Widening
# the red colon branch to ``\s*`` removed it, and the reverse direction
# (licence strictly wider than red) is now EMPTY rather than merely harmless.
_H_SPACE = r"[^\S\r\n]"

# The declaration side spells the separator WITHOUT ``\s``, so it cannot span a
# newline. A line ending in a bare keyword and an unrelated next line beginning
# with a reference is not a declaration; on the red side that same span is a
# hit.
#
# That was documented as the CONSERVATIVE answer on each side, and the
# measurement upgrades it: GitHub's BODY parser resolves NO closing reference
# across a line break, in either the bare or the colon spelling, so this is the
# ACCURATE model of the parser this side faces -- not a guess that happens to
# lean safe. The two sides differ because the two GitHub parsers differ, which
# is the finding recorded in the module docstring.
_SEPARATOR_SAME_LINE = rf"(?::{_H_SPACE}*|{_H_SPACE}+)"

# One list marker, which is the only thing allowed in front of a declaration.
# Bullet (``-`` / ``*`` / ``+``), ordered (``1.`` / ``1)``), and a task-list
# checkbox after either -- GitHub honours a closing keyword in all of them, so
# refusing them would make the prose that says "a list marker" false (#7969
# review). ``\d{1,9}`` is CommonMark's own bound on an ordered-list number.
_LIST_MARKER = rf"(?:(?:[-*+]|\d{{1,9}}[.)]){_H_SPACE}+(?:\[[ xX]\]{_H_SPACE}+)?)?"

# Leading indent: at most THREE spaces. Four spaces or a tab opens an INDENTED
# code block in CommonMark, and a declaration inside one licenses a close while
# rendering as code -- the same shape as the fenced-block hole, so it gets the
# same answer. Costs a nested list item one reworded line; that is the cheap
# direction.
_LEADING_INDENT = r"^ {0,3}"

# ---------------------------------------------------------------------------
# The RED side. Deliberately liberal: a closing keyword ANYWHERE in a commit
# message or the title, in any spelling, is a hit. Narrowing this to agree with
# the declaration pattern would re-open the hole the gate exists to close.
# ---------------------------------------------------------------------------
CLOSING_KEYWORD_RE = re.compile(
    _KEYWORD + _SEPARATOR + REFERENCE_PATTERN,
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# The LICENCE side. A declaration is a LINE that BEGINS with a closing keyword
# immediately followed by the reference -- optionally after one list marker, so
# a body written as a bullet list still declares. That is the form GitHub's own
# documentation writes and the form CONTRIBUTING.md prescribes; anything else
# in the body is a MENTION and licenses nothing.
# ---------------------------------------------------------------------------
DECLARATION_RE = re.compile(
    _LEADING_INDENT
    + _LIST_MARKER
    + _KEYWORD
    + _SEPARATOR_SAME_LINE
    + REFERENCE_PATTERN,
    re.IGNORECASE | re.MULTILINE,
)

# Opening/closing fence of a Markdown code block, at the start of a line. Up to
# three spaces of indent, matching _LEADING_INDENT: at four it is an indented
# code block, which _LEADING_INDENT already refuses.
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")

# Raw-HTML regions a declaration must not hide in, each non-greedy and DOTALL
# because all three span lines and a body may carry several:
#
# * an HTML COMMENT renders as nothing at all;
# * ``<pre>`` renders as code, exactly like a fence;
# * ``<details>`` renders COLLAPSED. That one is the reason this is a licence
#   question and not a formatting one: this gate's whole intent model is that
#   the body is what a REVIEWER READS, and a declaration nobody expands is not
#   read. It is also common in real pull-request bodies.
#
# An UNTERMINATED region eats the rest of the body, which is the conservative
# direction -- fewer declarations, never more.
_HTML_REGIONS_RE = re.compile(
    r"<!--.*?(?:-->|\Z)"
    r"|<pre\b[^>]*>.*?(?:</pre\s*>|\Z)"
    r"|<details\b[^>]*>.*?(?:</details\s*>|\Z)",
    re.DOTALL | re.IGNORECASE,
)

# The repository a bare ``#N`` resolves against. Overridable so the same set
# arithmetic works when the gate runs in a fork or in a test fixture.
DEFAULT_REPO_SLUG = "elastic/prism"


@dataclass(frozen=True)
class ClosingReference:
    """One closing keyword and the issue it names."""

    keyword: str
    slug: str
    """Owner/repo the reference resolves against, lowercased."""
    number: int
    matched_text: str

    @property
    def canonical(self) -> str:
        """Set key. Two references close the same issue iff these are equal."""
        return f"{self.slug}#{self.number}"


@dataclass(frozen=True)
class Violation:
    """An undeclared closing reference, and the surface that carries it."""

    surface: str
    """Human-readable origin, e.g. ``commit 67a0ff21d`` or ``PR title``."""
    reference: ClosingReference


@dataclass(frozen=True)
class StateReading:
    """What the API says one closing reference points at."""

    kind: str
    """``issue`` / ``pull_request`` / ``absent`` / ``unreadable``."""
    state: str = ""
    """``open`` / ``closed`` when the API answered."""
    detail: str = ""


StateLookup = Callable[[ClosingReference], StateReading]


def _references(
    pattern: re.Pattern[str], text: str, repo_slug: str
) -> list[ClosingReference]:
    """Every match of ``pattern`` in ``text``, as references, in order.

    The two callers differ only in the pattern they pass; the match-to-
    reference conversion is one implementation so the two sides cannot drift
    in how they resolve a slug or a number.
    """
    found: list[ClosingReference] = []
    for match in pattern.finditer(text):
        if match.group("url_number") is not None:
            slug = f"{match.group('url_owner')}/{match.group('url_repo')}"
            number = int(match.group("url_number"))
        else:
            owner = match.group("owner")
            repo = match.group("repo")
            slug = f"{owner}/{repo}" if owner and repo else repo_slug
            number = int(match.group("number"))
        found.append(
            ClosingReference(
                keyword=match.group("keyword"),
                slug=slug.lower(),
                number=number,
                matched_text=match.group(0),
            )
        )
    return found


def closing_references(
    text: str, repo_slug: str = DEFAULT_REPO_SLUG
) -> list[ClosingReference]:
    """Every closing reference in ``text``, in order of appearance.

    The RED side. Liberal by design -- see the module docstring. Duplicates are
    kept: the caller reports per occurrence and de-duplicates only when
    building a set.
    """
    return _references(CLOSING_KEYWORD_RE, text, repo_slug)


def declaration_surface(body: str) -> str:
    """``body`` with the surfaces a declaration cannot live in removed.

    Fenced code blocks, HTML comments, ``<pre>`` and ``<details>`` are blanked
    out rather than deleted so line structure is preserved for the
    line-anchored declaration pattern. INDENTED code blocks need no work here:
    ``_LEADING_INDENT`` refuses four spaces or a tab directly.

    An UNTERMINATED fence or region blanks the rest of the body: a body that
    opens one and never closes it is one whose remainder a reader sees as code,
    as nothing, or collapsed, and counting a declaration there would be the
    licence-side error this gate was just fixed for.
    """
    body = _HTML_REGIONS_RE.sub(lambda match: "\n" * match.group(0).count("\n"), body)
    kept: list[str] = []
    fence: str | None = None
    for line in body.split("\n"):
        if fence is None:
            opening = _FENCE_RE.match(line)
            if opening is not None:
                fence = opening.group(1)[0]
                kept.append("")
                continue
            kept.append(line)
            continue
        closing = _FENCE_RE.match(line)
        if closing is not None and closing.group(1)[0] == fence:
            fence = None
        kept.append("")
    return "\n".join(kept)


def declared_references(
    body: str, repo_slug: str = DEFAULT_REPO_SLUG
) -> list[ClosingReference]:
    """Every closing reference the BODY actually DECLARES, in order.

    The LICENCE side, and narrow by design. The rule is POSITIONAL, not
    semantic: :data:`DECLARATION_RE` requires the line to BEGIN with the closing
    keyword (up to three spaces of indent and an optional list marker), so a
    mention inside a sentence, a NEGATION THAT DOES NOT BEGIN THE LINE WITH THE
    KEYWORD -- "this PR does not close #7947", the phrasing a body realistically
    contains -- a quotation of this gate's own output, and a reference inside a
    fenced or indented code block, an HTML comment, a ``<pre>`` or a
    ``<details>`` all fail to declare (#7966).

    Nothing here reasons about negation as a CLASS, and it must not be read as
    though it did: measured against this function, "Closes #7947? No -- it does
    not." DECLARES, because the line begins with the keyword. That is correct
    behaviour -- GitHub links the same line -- and it is what
    ``test_a_line_initial_negation_declares_because_the_rule_is_positional``
    pins. An earlier revision of this docstring listed "a negation" unqualified,
    dropping the mechanism the file states accurately 280 lines above and turning
    a true statement about one phrasing into a false one about a class (#8006).
    """
    return _references(DECLARATION_RE, declaration_surface(body), repo_slug)


# A record's first line, as ``%H`` emits it: hexadecimal and nothing else.
#
# Bounded 4..40 rather than pinned at 40 so that ``%h`` -- an abbreviated SHA,
# whose shortest form is git's own ``core.abbrev`` floor of 4 -- is admitted
# too. What it refuses is a first line that is a MESSAGE: every realistic
# commit subject carries a space or a non-hex character, and this repository's
# ``fix(scope): ...`` convention carries several.
#
# The residue, stated rather than implied: a subject that is a single hex-only
# word (``deadbeef``, and in English ``added`` / ``facade`` / ``decaf``) is
# indistinguishable from a short SHA by this rule alone. It costs a MISSED
# refusal, never a wrong verdict, and only on a stream that already lacks
# ``%H`` -- where every OTHER record has to be a hex-only word too, because the
# rule below is universally quantified over the records.
_SHA_LINE_RE = re.compile(r"[0-9a-fA-F]{4,40}")

# git's record terminator under ``-z``, named once so the two places that count
# it -- the refusal and the verdict line -- cannot come to spell it differently.
NUL = "\0"


def record_stream_defect(raw: str, records: list[tuple[str, str]]) -> str | None:
    """Why ``raw``'s RECORD STRUCTURE is not the one the gate reads, or ``None``.

    ``None`` means the two structural arms below found nothing, NOT that the
    stream carries what it was promised to carry; the residue at the end of
    this docstring is the difference and it is load-bearing.

    THIS IS THE ANSWER TO #9220, and the defect it closes is worth stating
    because the shape recurs. ``--commits-file`` is a stream this script does
    NOT produce: the workflow builds it in one step and hands it to the gate in
    another, and an ad-hoc caller builds it by hand. Nothing at that boundary
    asserted the format, so a stream in the WRONG format did not fail -- it
    degraded into a NARROWER scan that still exited 0 with a confident verdict.
    Measured on #9218: four commit messages in the wrong separator format were
    reported as ``scanned 1 commit message(s)`` and clean.

    The failure is silent in the only direction that matters -- FEWER inputs
    scanned, never more -- and its green is then read as evidence.

    Two independent arms, because the two realistic malformations are caught by
    different ones and neither subsumes the other:

    * the SEPARATOR arm. ``git log -z`` terminates every record with a NUL, and
      a NUL cannot appear inside a commit message, so the terminator count IS
      the supplied record count, measured without reference to the parse. A
      stream produced WITHOUT ``-z`` holds zero of them and parses as one giant
      record; a stream truncated mid-write holds one fewer than it parsed.
      Either way the two counts disagree and the gate refuses.

    * the RECORD-SHAPE arm. Every record must open with the ``%H`` line the
      format promises. A stream built with ``--format='%B'`` AND ``-z`` has the
      right terminator count and the wrong shape -- and it is the WORSE
      malformation, because :func:`parse_commit_records` then eats each
      message's SUBJECT as if it were a SHA. Measured: a subject reading
      ``fix(engine): closes #8825 by accident`` is a RED under the correct
      invocation and a GREEN under that one, with the count agreeing at 2 both
      times. The separator arm cannot see it; only the shape can.

    Returned as a sentence rather than raised so the CLI can print it under the
    same ``NOTHING WAS SCANNED`` banner every other unscannable input gets: the
    gate could not read its input is a different thing for a human to act on
    than your commit message closes something.

    THE RESIDUE, and it is the same class as the hex-word one above: BOTH arms
    read STRUCTURE, and structure does not determine CONTENT. A placeholder
    that is neither ``%B`` nor a superset of it produces a stream both arms
    accept, because a record is a SHA line and then some text and nothing here
    can tell which text.

    Measured, two commits whose first SUBJECT carries an undeclared close, with
    ``--min-commits 2`` so the workflow's third arm is satisfied too:

        --format='%H%n%B'  rc=1, names both undeclared references
        --format='%H%n%b'  rc=0, "scanned 2 ... of the 2 ... supplied", clean
        --format='%H%n%s'  rc=1 on THAT input -- and rc=0 when the same close
                           sits in the body instead, which is the mirror

    ``%b`` is the body WITHOUT the subject and ``%s`` is the subject without
    the body; each discards exactly the half the other keeps, and a one-letter
    slip from ``%B`` reaches the first. That is the very loss the RECORD-SHAPE
    arm's own paragraph says it exists to prevent, so this is written here
    rather than left implied.

    NO CHEAP FOURTH ARM EXISTS. A ``%b`` record and a ``%B`` record are
    shape-indistinguishable -- a SHA line followed by text -- so nothing in the
    bytes separates them, and the only thing that could is a second read of git
    for the same range, which is a verdict depending on state outside the input
    (the class the module docstring's "What this gate does NOT do" refuses).
    What the caller gets instead is this file naming the format ONCE, in the
    ``--commits-file`` help, in the refusal text, and in the workflow -- and
    the workflow, the only automated caller, is pinned to that spelling by
    ``test_the_commit_records_are_nul_terminated_with_the_sha``.
    """
    supplied = raw.count(NUL)
    if supplied != len(records):
        return (
            f"the stream holds {supplied} NUL record terminator(s) but parsed "
            f"into {len(records)} record(s). Every record git writes under "
            "``-z`` ends in a NUL and no commit message can contain one, so "
            "those two counts are the same number on a well-formed stream. "
            "They differ here, which means the stream was NOT produced by "
            "``git log -z`` (a stream without ``-z`` parses as ONE record no "
            "matter how many commits it holds) or was truncated"
        )
    malformed = [sha for sha, _ in records if _SHA_LINE_RE.fullmatch(sha) is None]
    if malformed:
        return (
            f"{len(malformed)} of {len(records)} record(s) do not open with "
            f"the SHA line the format promises -- the first is {malformed[0]!r}."
            " The format is ``%H%n%B``: a record whose first line is not a SHA "
            "means the stream was built without ``%H``, and this gate would "
            "then discard each message's SUBJECT LINE as if it were one -- the "
            "line a closing keyword is most likely to sit on"
        )
    return None


def parse_commit_records(raw: str) -> list[tuple[str, str]]:
    """Split ``git log -z --format='%H%n%B'`` output into (sha, message) pairs.

    ``-z`` terminates every commit record with NUL, so a commit message
    containing blank lines, or any separator a human might have chosen, cannot
    split one record into two. The first line of each record is the SHA.

    A trailing empty fragment after the final NUL is dropped; a stream that is
    entirely empty yields an empty list, which the CLI treats as "scanned
    nothing" rather than as "clean".

    THIS FUNCTION TRUSTS ITS INPUT and must stay that way: it is the parse, and
    the parse cannot also be the thing that judges whether the parse was given
    what it asked for. :func:`record_stream_defect` is that judgement, called
    on the raw stream and this function's output together (#9220).
    """
    records: list[tuple[str, str]] = []
    for chunk in raw.split(NUL):
        if not chunk.strip():
            continue
        sha, _, message = chunk.partition("\n")
        records.append((sha.strip(), message))
    return records


def find_violations(
    *,
    commits: list[tuple[str, str]],
    pr_title: str,
    declared: set[str],
    repo_slug: str = DEFAULT_REPO_SLUG,
) -> list[Violation]:
    """Closing references outside ``declared``.

    ``declared`` is the set of canonical keys the BODY declares, built by
    :func:`declared_references`. It is passed in rather than derived here so
    the caller that also PRINTS the declared set builds it exactly once: two
    derivations of one subject are two things that can drift, which is the
    whole subject of #7966.

    The body is the declaration; the commit messages and the title are the
    surfaces that close WITHOUT declaring. See "The intent model" above.
    """
    violations: list[Violation] = []
    for sha, message in commits:
        for ref in closing_references(message, repo_slug=repo_slug):
            if ref.canonical not in declared:
                violations.append(Violation(surface=f"commit {sha}", reference=ref))
    for ref in closing_references(pr_title, repo_slug=repo_slug):
        if ref.canonical not in declared:
            violations.append(Violation(surface="PR title", reference=ref))
    return violations


@dataclass(frozen=True)
class StateFinding:
    """One declared closing reference the state check has something to say about."""

    reference: ClosingReference
    outcome: str
    """``closed`` (refused), ``could-not-check``, or a note: ``pull-request`` /
    ``other-repository`` (neither is judged)."""
    detail: str = ""


def judge_issue_states(
    references: list[ClosingReference],
    lookup: StateLookup,
    repo_slug: str = DEFAULT_REPO_SLUG,
) -> list[StateFinding]:
    """The state findings for ``references``, one per distinct issue, in order.

    An OPEN issue yields nothing. The edge cases are decided here, and each is
    tested in ``tests/test_closing_keyword_issue_state_11221.py``:

    * a reference to ANOTHER repository is not looked up: the job's token is
      scoped to this repository, so an answer would be a 404 read as "absent";
    * a number that is a PULL REQUEST is noted and not judged: a closed or
      merged pull request is a normal state, not a stale branch;
    * a 404 or an unreachable API is ``could-not-check``, which is neither a
      pass nor the ``closed`` refusal.
    """
    findings: list[StateFinding] = []
    seen: set[str] = set()
    for ref in references:
        if ref.canonical in seen:
            continue
        seen.add(ref.canonical)
        if ref.slug != repo_slug.lower():
            findings.append(StateFinding(ref, "other-repository"))
            continue
        reading = lookup(ref)
        if reading.kind == "pull_request":
            findings.append(StateFinding(ref, "pull-request", reading.state))
        elif reading.kind == "issue":
            if reading.state != "open":
                findings.append(
                    StateFinding(ref, "closed", reading.state or "not open")
                )
        else:
            findings.append(
                StateFinding(
                    ref,
                    "could-not-check",
                    f"{reading.kind}: {reading.detail}".rstrip(": "),
                )
            )
    return findings


def gh_state_lookup() -> StateLookup:  # pragma: no cover - I/O
    """The live lookup: ``check_review_verdict``'s ``gh api`` resolver, kept by state.

    Imported inside the function because that module imports THIS one at load.
    """
    import check_review_verdict as verdict

    resolve = verdict.gh_resolver(verdict._run_gh)

    def lookup(ref: ClosingReference) -> StateReading:
        got = resolve(
            verdict.IssueReference(
                slug=ref.slug, number=ref.number, matched_text=ref.matched_text
            )
        )
        return StateReading(kind=got.kind, state=got.state, detail=got.detail)

    return lookup


def report_issue_states(findings: list[StateFinding], *, enforce: bool) -> int:
    """Print ``findings``; return the exit code (1 closed, 3 unchecked, else 0).

    ``enforce`` False (a ``merge_group`` run) reports everything and returns 0.
    """
    closed = [f for f in findings if f.outcome == "closed"]
    unchecked = [f for f in findings if f.outcome == "could-not-check"]
    for f in findings:
        name = f.reference.canonical
        if f.outcome == "closed":
            print(
                f"closing-keyword gate (#11221): {f.reference.matched_text!r} "
                f"names {name}, which is already CLOSED (state: {f.detail}). A "
                "PR that closes a closed issue is usually a duplicate or a stale "
                "branch: reopen the issue, or point the PR at the open one.",
                file=sys.stderr,
            )
        elif f.outcome == "could-not-check":
            print(
                f"closing-keyword gate (#11221): could not check {name} "
                f"({f.detail}); this is neither a pass nor a verdict that the issue is closed.",
                file=sys.stderr,
            )
        elif f.outcome == "pull-request":
            print(
                f"closing-keyword gate (#11221): {name} is a pull request; its "
                "state is not judged."
            )
        else:
            print(
                f"closing-keyword gate (#11221): {name} is in another "
                "repository; its state is not judged."
            )
    if not enforce:
        if closed or unchecked:
            print(
                "closing-keyword gate (#11221): merge_group run, so the state "
                "findings above are reported and do not fail: a sibling entry "
                "may have closed the issue after the review."
            )
        return 0
    if closed:
        return 1
    return 3 if unchecked else 0


def _read(path_text: str, label: str) -> str | None:
    """Read a required input file, or report why the gate cannot scan."""
    if not path_text:
        sys.stderr.write(
            f"closing-keyword gate: NOTHING WAS SCANNED -- no {label} path was "
            "given. This is not a content verdict; the gate could not run.\n"
        )
        return None
    path = Path(path_text)
    if not path.is_file():
        sys.stderr.write(
            f"closing-keyword gate: NOTHING WAS SCANNED -- the {label} file "
            f"{path} does not exist. This is not a content verdict; the gate "
            "could not run.\n"
        )
        return None
    return path.read_text(encoding="utf-8", errors="replace")


def main(
    argv: list[str] | None = None, *, state_lookup: StateLookup | None = None
) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail when a commit message or the PR title closes an issue the PR "
            "body does not declare (issue #7407)."
        )
    )
    parser.add_argument(
        "--commits-file",
        required=True,
        help="NUL-terminated records from: git log -z --format='%%H%%n%%B' BASE..HEAD",
    )
    parser.add_argument(
        "--pr-body-file",
        required=True,
        help="File holding the PR body, fetched live (never the frozen event payload).",
    )
    parser.add_argument(
        "--pr-title-file",
        required=True,
        help="File holding the PR title.",
    )
    parser.add_argument(
        "--repo-slug",
        default=DEFAULT_REPO_SLUG,
        help="Owner/repo a bare '#N' resolves against.",
    )
    parser.add_argument(
        "--min-commits",
        type=int,
        default=1,
        help=(
            "Refuse to report a verdict on fewer than this many commits. A pull "
            "request always has at least one, so the default 1 turns an "
            "uncomputed range into a loud refusal instead of a silent pass."
        ),
    )
    parser.add_argument(
        "--check-issue-state",
        action="store_true",
        help=(
            "Also refuse a DECLARED closing reference to an issue of this "
            "repository that is already closed (#11221). Needs GH_TOKEN."
        ),
    )
    parser.add_argument(
        "--event-name",
        default="pull_request",
        help="github.event_name; on merge_group the state check only reports.",
    )
    args = parser.parse_args(argv)

    raw_commits = _read(args.commits_file, "commit-records")
    pr_body = _read(args.pr_body_file, "PR-body")
    pr_title = _read(args.pr_title_file, "PR-title")
    if raw_commits is None or pr_body is None or pr_title is None:
        return 3

    commits = parse_commit_records(raw_commits)
    # Anti-vacuity, asserted on the COUNT and not on an exit code. A sibling
    # gate in this repository was found reporting success having processed zero
    # inputs; the only defence is to make the count itself the precondition.
    if len(commits) < args.min_commits:
        sys.stderr.write(
            "closing-keyword gate: NOTHING WAS SCANNED -- the commit-record "
            f"stream held {len(commits)} commit(s), fewer than the required "
            f"{args.min_commits}. A pull request always carries at least one "
            "commit, so this means the range was not computed, NOT that the "
            "branch is clean. This is not a content verdict.\n"
        )
        return 3

    # The FORMAT precondition, and the second half of the anti-vacuity rule
    # (#9220). The count check above catches a stream that parsed into NOTHING;
    # this catches one that parsed into FEWER records than it was handed, or
    # into records of the wrong shape. Both were silent passes: see
    # :func:`record_stream_defect` for the two arms and the measurement behind
    # each.
    #
    # It runs AFTER the count check so that an empty stream keeps reporting the
    # count message it has always reported -- an empty stream fails both, and
    # the zero is the more useful sentence of the two.
    defect = record_stream_defect(raw_commits, commits)
    if defect is not None:
        sys.stderr.write(
            "closing-keyword gate: NOTHING WAS SCANNED -- the commit-record "
            f"stream is not in the format this gate reads: {defect}. Rebuild "
            "it with exactly:\n\n"
            "    git log -z --format='%H%n%B' BASE..HEAD > <file>\n\n"
            "This is NOT a content verdict. A stream in the wrong format does "
            "not fail to parse -- it parses into FEWER or WRONGER records and "
            "the gate then reports a confident all-clear over a fraction of "
            "what it was given, which is the defect #9220 was filed for.\n"
        )
        return 3

    declared_set = {
        ref.canonical for ref in declared_references(pr_body, repo_slug=args.repo_slug)
    }
    declared = sorted(declared_set)
    violations = find_violations(
        commits=commits,
        pr_title=pr_title,
        declared=declared_set,
        repo_slug=args.repo_slug,
    )
    # Both counts, and the honest description of what that buys: by the time
    # this line is reached the separator arm has ALREADY required these two to
    # be equal, so this is ONE measurement printed twice and no mutation of the
    # equality can red it. It is kept anyway, and only for the reader: printing
    # solely what was READ is what let #9218's "scanned 1 commit message(s)"
    # pass as a complete answer over a four-commit input, and a line that names
    # the supplied count makes the coverage visible instead of inferable. Its
    # value is in the REPORT, not in the verdict -- the same distinction the
    # audit-grep tripwire doc draws about guard ORDER, and the reason to say it
    # plainly is that the first version of this comment called the two
    # "measurements taken by different rules", which is true only BEFORE the
    # guard runs and reads like a check when it is a restatement.
    supplied = raw_commits.count(NUL)
    scanned = (
        f"scanned {len(commits)} commit message(s) of the {supplied} the "
        f"record stream supplied, the PR title and the PR body; the body "
        f"declares {declared or 'nothing'}"
    )
    if violations:
        sys.stderr.write(
            "closing-keyword gate (#7407): a closing keyword names an issue this "
            "PR does not declare.\n\n"
        )
        for violation in violations:
            sys.stderr.write(
                f"  {violation.surface}: {violation.reference.matched_text!r} "
                f"would close {violation.reference.canonical}\n"
            )
        mentioned_only = sorted(
            {violation.reference.canonical for violation in violations}
            & {
                ref.canonical
                for ref in closing_references(pr_body, repo_slug=args.repo_slug)
            }
            - set(declared)
        )
        if mentioned_only:
            sys.stderr.write(
                "\nRead this before editing the body: it MENTIONS "
                f"{', '.join(mentioned_only)} without DECLARING it, and a "
                "mention is not a declaration (#7966). Quoting this message, "
                "writing the reference inside a sentence, denying the close in "
                "prose, or putting it in a code fence all leave the gate red -- "
                "which is the point: the gate used to go green on every one of "
                "those.\n"
            )
        sys.stderr.write(
            "\nThis repository squashes with the branch's concatenated COMMIT "
            "MESSAGES, so every line above lands on the default branch verbatim "
            "and GitHub's parser -- which is purely lexical, and is not stopped "
            "by backticks or a code fence -- will close each issue named.\n"
            "\nTwo remedies:\n"
            "  * the close IS intended -> DECLARE it in the PR body, on a line "
            "that BEGINS with the closing keyword and the reference and nothing "
            "in front of them (a list marker is allowed), which is what makes it "
            "visible as a linked issue;\n"
            "  * the close is NOT intended -> reword so that no closing "
            "keyword is immediately followed by the issue reference. Future "
            "tense does NOT disarm it: 'will close #1222' is a hit here, "
            "because the keyword still sits next to the number. A LINE BREAK "
            "does not disarm it either, with or without a colon in front of "
            "it: 'CLOSED:<newline>#1222' is a hit here, and measured against "
            "GitHub a commit message spelled that way really does close "
            "(#9053). These do not "
            "match: 'to be closed by PR E', 'the follow-up is #1222', 'PR E "
            "finishes #1222'. Rewording needs a history rewrite, so do it now "
            "rather than after the merge, when it cannot be undone.\n"
            f"\n{scanned}.\n"
        )
        return 1

    print(f"closing-keyword gate: no undeclared closing reference; {scanned}.")
    if args.check_issue_state:
        lookup = state_lookup if state_lookup is not None else gh_state_lookup()
        findings = judge_issue_states(
            declared_references(pr_body, repo_slug=args.repo_slug),
            lookup,
            repo_slug=args.repo_slug,
        )
        return report_issue_states(findings, enforce=args.event_name != "merge_group")
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    sys.exit(main())
