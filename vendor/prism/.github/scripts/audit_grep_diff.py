"""Mechanical enforcement of the CONTRIBUTING.md "Pre-merge audit grep".

This script implements the CI gate filed as issue #1546.

Why this exists
---------------
CONTRIBUTING.md ships a copy-pasteable one-liner (the "audit grep") that
catches a small set of patterns CI has historically missed:

  - Studio-side wire-shape rewrites that violate "Engine output IS the
    wire query" (`defer_hard_filters`, `_inject_`, `_apply_suppression`,
    `search.post_filter(`, `add_filter(`, `.build_search()`).
  - Forked Ordered Pin shape detection on the FE
    (`looksLikeOrderedPinFilterGroups(`, `extractSlotGroup(`,
    subscript reads on `ordered_pin_mode` / `pin_group_id`).
  - Silenced failures (`@pytest.mark.skip`, `@pytest.mark.xfail`,
    `@ts-ignore`, `type: ignore`, broad `except Exception:`).
  - AI / process-method leakage (`Co-Authored-By Claude`, `checkloop`).

On top of that justification-gated family, this script also enforces a
**customer-name guard** (#2374, hardened in #3135): a small set of
scrubbed proprietary retailer customer names that must NEVER appear in
core. That guard is a HARD block — unlike every pattern above, a hit is
not something a PR body can justify; the proprietary customer's name in
core has no legitimate use, because it is the one string that identifies
them as a PRISM customer (CONTRIBUTING.md "Generalize, don't fork per
customer": core is never written FOR a named retailer, and no customer is
named as a PRISM customer). Scope, so this is not misread: the registry
below holds the customer names only — retailer / brand values occurring
in public open-data demo content are NOT what it looks for. Any
occurrence of a guarded name fails the job outright. The guard runs
over THREE surfaces, not just the diff: (1) added diff lines, (2) the
commit messages on the PR, and (3) the PR title + body. Surfaces (2)/(3)
close the gap that a name scrubbed from every blob could still leak back
in through a commit subject or a PR description (the #3135 history-scrub
motivation). Each surface reuses the SAME obfuscated
:data:`CUSTOMER_NAME_SPECS` regex, so the literal name lives nowhere in
this repository. See :data:`CUSTOMER_NAME_SPECS`,
:func:`scan_for_customer_names`, and :func:`scan_text_for_customer_names`.

A fourth family, :data:`COMPANION_PATTERN_SPECS` (#6116), is "banned UNLESS
accompanied by X". It is the only one whose verdict needs more than the single
added line, so it reads the diff a second time as HUNKS
(:func:`parse_diff_hunks`) and clears a hit whose hunk already carries the
required companion call. Its one row today is the bulk-write rule #6113 left
enforced by convention: a caller that disables ``bulk``'s own raising owes the
operator an explicit verdict from ``check_bulk_result(``, and nothing red'd if a
fifth caller omitted it. Scope is the HUNK, not the function — see that
registry's header for why that is the widest true statement a diff surface
supports, and why the family is justification-gated rather than a hard block.

The "Engine output IS the wire query" rule has been violated three times
(#894 / #934, #935 / #938, #1418). Each time, a manual reviewer was meant
to run the audit grep and forgot. This script removes the human from the
loop: on every PR, CI runs the grep against the diff and demands an
inline per-hit justification block in the PR body. If any hit is
unjustified, the job fails and merge is blocked.

Pattern source of truth
-----------------------
The pattern list is CONTRIBUTING.md § "Pre-merge audit grep". When the
list changes there, update :data:`PATTERN_SPECS` below in the same PR.
The companion test ``tests/test_audit_grep_diff.py`` asserts the two
lists agree, so a drift is caught at CI time.

Justification block format
--------------------------
For each hit, the PR body MUST contain a block of the form::

    Hit: <path>#<hash> <pattern>
    Rule: CONTRIBUTING.md "<which rule>"
    Justification: <one-line reason — cite the test that proves it>

``<hash>`` is the first 8 hex digits of the SHA-256 of the added line with its
surrounding whitespace stripped (:func:`line_content_hash`); the failure report
prints the whole ``Hit:`` line ready to paste (#7126). The key is the file plus
the line's CONTENT, so lines added or removed above the hit leave it valid
while an edit to the justified line itself voids it. Two identical lines in one
file are one key, so one block clears both.

The older ``Hit: <path>:<line> <pattern>`` form is still accepted, because
open pull requests carry it; it goes stale on any line shift, so prefer the
content form.

The matcher is whitespace-tolerant and case-insensitive on the literal
``Hit:`` / ``Rule:`` / ``Justification:`` labels. The ``<path>``,
``<hash>`` (or ``<line>``) and ``<pattern>`` tokens must match exactly.
Anything else in the PR body (prose, the issue link, code blocks) is ignored.

Text surfaces for the justification-gated family (#5615)
--------------------------------------------------------
With ``--scan-text-tripwires``, :data:`PATTERN_SPECS` is ALSO run over the
two surfaces a diff scan cannot see — the PR's commit messages and the PR
title+body. Until #5615 only the customer-name guard covered those, so a
banned token written into a commit body or a PR description shipped
silently; three such mentions were caught by hand on #5612 in the very PR
that closed the previous instance of this bug class.

Two deliberate differences from the diff surface, both load-bearing:

- **The justification key is LABEL-scoped, not line-scoped**
  (``Hit: <commit-messages> <label>``, no ``:<line>``). A commit-message
  line number moves on every rebase and a PR-body line number moves on
  every edit, so a line-keyed justification would go stale and red a PR
  for an edit it never made. A text surface is also ONE authored blob under
  one author's control, so "why does my prose name this token" is the
  right granularity. See :func:`parse_text_justifications`.
- **Justification-protocol lines are not scanned.** A block that clears a
  hit necessarily QUOTES the label on its ``Hit:`` line; scanning those
  lines would make writing the block create a fresh hit in the PR body.
  See :func:`_is_justification_protocol_line`.

The scoped (:data:`SCOPED_PATTERN_SPECS`), companion
(:data:`COMPANION_PATTERN_SPECS`) and frozen
(:data:`FROZEN_DERIVATION_SPECS`) families are deliberately NOT run over
text: each gates on a FILE PATH (a scope glob / an allowlist glob) and a
text surface has none, so there is nothing for them to decide.

The flag is opt-in rather than default because of ONE caller: the
``check-commit-msg-customer-name`` pre-commit hook invokes this same script
at commit time, where the clearing surface (the PR body) does not exist yet,
so defaulting it on would hard-block a commit whose message honestly
describes removing a suppression with no way to clear it.

Every OTHER caller passes it, and that is not a stylistic preference — a
caller that omits it reports PASS on a commit message CI will red, which is
the surprise-in-CI loop the local gates exist to prevent. There are three
callers, and ``tests/test_audit_grep_diff.py::TestTextTripwireWiring`` pins
each one by name:

  1. ``.github/workflows/audit-grep.yaml`` — passes it (the CI gate).
  2. ``scripts/preflight.sh`` — passes it. It supplies an empty title/body,
     so the flag only adds the commit-message surface: exactly the surface
     whose CI verdict it is promising to predict.
  3. the ``check-commit-msg`` pre-commit hook — deliberately does NOT.

An earlier revision of this docstring said "CI passes the flag; the local
hook does not", which read as an exhaustive inventory and was wrong:
preflight was a third caller that silently omitted it, so preflight passed
a commit body naming a banned token that CI then rejected.

Behaviour
---------
- Reads the diff from stdin (or via ``--diff-file``).
- Reads the PR body from ``--pr-body-file`` (or stdin if no diff file).
- Scans ADDED lines only (lines whose diff prefix is ``+`` and that are
  not the diff header ``+++``). Hits on removed / unchanged lines are
  ignored.
- Emits a per-hit report to stderr and exits non-zero if any hit lacks
  a justification block. Exits 0 if every hit is justified, or if the
  diff contains no hits at all.

Out of scope (per #1546)
------------------------
- Extending the pattern list (separate issue if needed).
- Auto-generating justification templates.
- Making the gate non-blocking.

Out of scope (per #5615)
------------------------
- Scanning the WHOLE TREE on a pull request. A pattern already on ``main``
  is real (#5611) but a PR-time whole-tree scan reds every open PR the
  moment anything pre-existing is found. That blind spot is closed by the
  SCHEDULED census in ``.github/scripts/audit_grep_tree.py``, which files
  a tracking issue instead of failing a PR.
"""

from __future__ import annotations

import argparse
import fnmatch
import hashlib
import re
import sys
import unicodedata
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

# The invisible-character class is DERIVED once, in ``scripts/``, and shared
# (#8649). This module used to carry its own six-codepoint string; the gate at
# ``scripts/check_no_invisible_characters.py`` carried a one-codepoint version
# of the same idea. Two spellings of one concept is the defect #8647 exists to
# close, and neither list said it was short.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from invisible_characters import (  # noqa: E402  (path is set up just above)
    describe,
    find,
    has_no_advance_width,
    invisible_codepoints,
    notate,
)

# WHAT A ``git log -z`` RECORD STREAM IS has exactly one definition in this
# tree, and it lives in the gate that consumes that stream by contract (#9220).
# This module needs the same judgement for one narrow purpose -- see
# :func:`_commit_surface_text` -- and restating it here would be two spellings
# of one format, which is the defect the import above exists to avoid in the
# invisible-character class. ``check_closing_keywords`` is a sibling script in
# this directory, not an installed package; ``check_review_verdict`` reaches it
# the same way for the same reason.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from check_closing_keywords import (  # noqa: E402  (path is set up just above)
    NUL,
    parse_commit_records,
    record_stream_defect,
)

# ---------------------------------------------------------------------------
# Pattern registry — mirrors CONTRIBUTING.md § "Pre-merge audit grep".
#
# Each entry: (human_label, compiled_regex). The label is what gets
# echoed in the report AND what the PR-body justification block must
# reference under ``Hit: <path>:<line> <label>``.
#
# IMPORTANT: keep this list in lock-step with the one-liner in
# CONTRIBUTING.md (around line 249). The companion test
# ``tests/test_audit_grep_diff.py`` pins both lists together so drift
# is caught at CI time.
# ---------------------------------------------------------------------------
PATTERN_SPECS: list[tuple[str, str]] = [
    ("defer_hard_filters", r"defer_hard_filters"),
    ("_inject_", r"_inject_"),
    ("_apply_suppression", r"_apply_suppression"),
    ("search.post_filter(", r"search\.post_filter\("),
    (".build_search()", r"\.build_search\(\)"),
    # #1571 / #1572 — tier-conditional engine-emit branch. The CONTRIBUTING.md
    # one-liner writes the quoted form as ``if tier == .tier_1.`` so the ``.``
    # grep-regex any-char matches the surrounding quote character (single or
    # double) in Python source. Same semantics here.
    #
    # ``TIERS[0]`` is the SECOND spelling of the same branch. #5766 made the
    # positional form the house idiom for "the head rung" and converted the
    # tree's last quoted site, which left this pattern matching ZERO sites while
    # the shape it guards was alive and being written in the new spelling — a
    # tripwire that silently stops firing is worse than none. Both spellings are
    # matched so the branch stays justification-gated however it is written.
    ('if tier == "tier_1"', r"if tier == (.tier_1.|TIERS\[0\])"),
    ("looksLikeOrderedPinFilterGroups(", r"looksLikeOrderedPinFilterGroups\("),
    ("extractSlotGroup(", r"extractSlotGroup\("),
    # Subscript reads on the ordered-pin marker fields. CONTRIBUTING.md
    # writes these as ``[.ordered_pin_mode.]`` / ``[.pin_group_id.]``
    # in the one-liner — ``.`` is the grep-regex any-char that matches
    # the surrounding quote character in either Python (``['k']``) or
    # TS (``["k"]``) source. Same semantics here.
    ("[ordered_pin_mode]", r"\[.ordered_pin_mode.\]"),
    ("[pin_group_id]", r"\[.pin_group_id.\]"),
    # #1575 — silent drop of user input on an unknown-key path. The
    # structlog event name ``skipped_<surface>_missing_facet`` is the
    # canonical telltale that a request-pipeline ``continue`` is dropping
    # a user-dispatched value (range_filters[*].name, filters[*].name,
    # future siblings) without surfacing the contract violation. The
    # class-of-bug shipped THREE times on the same input path: #1558
    # (BE plumbing absent) → #1567 (Pydantic accepted alias keys) →
    # #1575 (_range_filter_queries continue'd when name not in facets).
    # Any new occurrence MUST be justified in the PR body with a link to
    # the path's ``feedback-no-silent-failures`` contract.
    #
    # DO NOT cite "the test that pins the explicit-raise behavior" — this
    # comment asked for exactly that until 2026-08-14, and it had been a
    # false instruction since 2026-06-21. #2206 (closing #2203) deleted the
    # #1575 raise and inverted the tests that pinned it: the companion test
    # file ``tests/test_search/test_user_range_filter_dispatch.py`` now pins
    # the OPPOSITE contract, in
    # ``test_unknown_range_name_does_not_raise_422_in_studio``; the #1575-era
    # ``test_unknown_range_facet_raises_422`` became
    # ``test_unknown_range_name_does_not_raise`` in
    # ``tests/test_search/test_search_search_unit.py`` in the same PR.
    # The doctrine itself was never retracted and is
    # RE-AFFIRMED by the 2026-08-14 ruling (CONTRIBUTING.md "Fail loudly").
    # #7113 has since landed the ENGINE half, in the MODE-SCOPED form the
    # maintainer ruled on 2026-08-19: the request boundary REFUSES an
    # unresolvable name (422, ``kind`` ``request_names_unresolvable``) in a
    # process declaring ``PRISM_RUNTIME_MODE=dev``, and WARNS + COUNTS it in one
    # declaring ``production``. The STUDIO drop sites are still lenient and
    # #7111 tracks them. Cite the doctrine — and, for the request boundary, the
    # ruled two-row table — never a test that would contradict either.
    #
    # A CLEAR-GESTURE path that expresses no constraint at all (an
    # empty-bounds range entry — the FE's clear-range gesture) is exempt,
    # because it drops no input to surface, via the "test asserting silent
    # drop needs a docstring" rule under Testing. A STALE URL or stale saved
    # state naming a facet this deployment does not have is NOT within that
    # exemption — the wording once read "stale-URL / clear-gesture" and
    # collapsed two different things; the stale-name half is the disputed
    # class the 2026-08-14 ruling governs.
    ("skipped_*_missing_facet", r"skipped_.*_missing_facet"),
    ("@pytest.mark.skip", r"@pytest\.mark\.skip"),
    ("@pytest.mark.xfail", r"@pytest\.mark\.xfail"),
    # #1754 — bare ``pytest.skip(...)`` CALLS (not the decorator) that silence
    # a failure by treating a degraded environment as a legitimate gate. Four
    # such skips masked a bare-``:9201`` (no ELSER) run as if the absent
    # ``tier_3`` tier were expected. ``/rewrite`` is pure query-gen — a tier
    # compiles whenever ``settings.use_elser`` is on with no live model — so
    # the fix is to PIN the flag and assert the tier PRESENT (fail-loud), not
    # skip. Any newly-added ``pytest.skip(`` must be justified in the PR body:
    # allowed only as a skip carrying an EXPLICIT install path
    # (``PRISM_TEST_ES_MODE=docker uv run pytest …``) for a test that genuinely
    # needs live-model RESULTS. A bare reason ("needs ELSER/E5") is banned.
    ("pytest.skip(", r"pytest\.skip\("),
    ("@ts-ignore", r"@ts-ignore"),
    # POSIX ``[[:space:]]`` in CONTRIBUTING.md's grep one-liner; the
    # Python ``re`` module uses ``\s`` for the same character class.
    # Stored as the POSIX form so the parity test passes byte-for-byte
    # against the doc and translated below at compile time.
    ("type: ignore", r"type:[[:space:]]*ignore"),
    ("except Exception:", r"except Exception:"),
    ("Co-Authored-By Claude", r"Co-Authored-By Claude"),
    ("checkloop", r"checkloop"),
]


# ---------------------------------------------------------------------------
# AI-attribution registry (#8331) — TEXT SURFACES ONLY.
#
# WHAT THIS CLOSES. Until #8331 the ONLY AI-attribution row anywhere in this
# script was the ``Co-Authored-By Claude`` entry in :data:`PATTERN_SPECS`
# above: one literal, no colon. Measured on the planted corpus in
# ``tests/test_audit_grep_diff.py``, that row caught almost nothing — and the
# case it missed most consequentially is the CANONICAL git trailer, because the
# real trailer carries a colon the literal does not. The FIGURES are published
# in exactly one place, CONTRIBUTING.md § "AI-attribution text scan", and are
# re-derived from the live corpus by a test; they are deliberately not restated
# here, because five hand-maintained copies of a measurement is the drift this
# gate's own history is made of. Everything else a coding
# harness actually emits into a PR description — the robot-emoji "generated
# with" footer, a lower-cased trailer, an "assisted" credit — was green. That
# green was then read as coverage: CONTRIBUTING.md and CLAUDE.md both told
# readers the body surface was guarded "only by a narrow literal pattern",
# which documented the hole as a permanent limitation instead of filing it.
# A gate whose green is indistinguishable from "not checked" is the false
# enforcement citation this repository files as a defect, not a caveat.
#
# WHY A SEPARATE REGISTRY, AND WHY TEXT-ONLY. These rows are NOT added to
# :data:`PATTERN_SPECS`, and the difference is load-bearing in both
# directions:
#
#   * PATTERN_SPECS rows are CODE telltales and run over the DIFF as well as
#     the two text surfaces. An AI-vendor name is not a code telltale — it is
#     a word, and this repository's tree legitimately contains it in
#     ``CLAUDE.md``, ``.claude/``, ``scripts/check_attribution.sh`` and
#     ``scripts/strip_ai_attribution.py``. Running these rows over added diff
#     lines would red a PR for editing the very files that implement the ban.
#   * The two text surfaces are different: a commit message and a PR
#     description are prose an author writes ABOUT the change, and neither
#     has any legitimate need to carry an attribution footer.
#
#   So the family runs on the commit-message and PR-title/body surfaces only
#   (:func:`scan_text_for_ai_attribution`), and the whole-tree census
#   (``audit_grep_tree.py``) does not inherit it — a tree file cannot carry
#   PR metadata. The code-comment / docstring half of the same house rule is
#   NOT closed by this family and is tracked separately; see the "residue"
#   note at the end of this comment.
#
# WHY JUSTIFICATION-GATED RATHER THAN A HARD BLOCK. The customer-name guard
# is a hard block because a proprietary customer's name has no legitimate use
# anywhere. An AI-vendor token is different: this file, ``CONTRIBUTING.md``'s
# ban itself, and any PR that changes either one have to be DESCRIBED in a
# commit message and a PR body. Making that unwritable would produce a red
# whose only remedy is a euphemism, on exactly the PRs that strengthen the
# rule. So these hits join the same justification-gated pool as every other
# text tripwire: the default verdict is "rephrase", and the escape hatch is
# ONE reviewer-visible block per surface + label. The residual is deliberate
# and stated: an author who writes the block can still ship a mention — but
# they have then DECLARED it in the PR body, which is precisely the surface a
# reviewer reads, rather than passing silently as today.
#
# TWO TIERS, and why the split is not cosmetic:
#
#   * MENTION tier (``ai-vendor-name``, ``robot-emoji``) — a bare occurrence
#     is a hit, with no attribution SHAPE required. Measured, this tier is the
#     SOLE catcher of three corpus cases: a vendor name in ordinary prose, one
#     inside markdown link text, and one split across a wrapped line. Deleting
#     the tier and keeping only the shape rows reds exactly those (measured as
#     a mutation, not asserted).
#
#     Two things this tier does NOT solely account for, said plainly because
#     the first draft of this comment claimed otherwise and the measurement
#     contradicted it. The shape that actually keeps recurring here is a
#     sentence ASSERTING THE ABSENCE of a footer ("verified: this body carries
#     no such trailer"), written while quoting the token it says is absent —
#     three shipped in one session, one inside the paragraph explaining the
#     previous one. Those cases are caught by the mention tier AND by the
#     shape rows, because the shape rows here are deliberately UNANCHORED,
#     unlike ``check_attribution.sh``'s caret-anchored commit-body rows which
#     do miss them. So the design property that catches the recurring shape is
#     the ABSENCE OF LINE ANCHORING, and the mention tier is what makes the
#     family independent of attribution shape altogether. Both are load-bearing
#     and neither is the whole story.
#   * SHAPE tier (every other row) — the token alone is ambiguous, so the row
#     keys on the attribution shape instead. ``cursor`` is the clearest case:
#     a pagination cursor is ordinary vocabulary in a search repository, so
#     ``cursor`` is a hit ONLY in a ``Made-with:`` / ``Co-authored-by:`` /
#     "generated with" shape, never bare. Same reasoning for ``gpt``, ``ai``
#     and ``bot``. Keeping these OUT of the mention tier is why the corpus's
#     the clean cases — a pagination cursor, "the agent brief", "the chain of
#     aid", "the generated docs index" — stay green.
#
# RELATIONSHIP TO ``scripts/check_attribution.sh``. That script is the
# COMMIT-RANGE gate: it reads commit author/committer identity and the commit
# body, and it never sees a PR title or body. Its body patterns are anchored
# to ``^`` on purpose, so a commit body may document the policy in prose. This
# family is deliberately WIDER (mention-level, unanchored) because its surface
# is different, so a byte-for-byte parity test against it would be wrong.
# What IS pinned is a SUBSUMPTION property — every shape that script rejects
# in a commit body is also caught here — by
# ``tests/test_audit_grep_diff.py::TestAiAttributionSubsumesCommitGate``. That
# is the direction drift would hurt: a pattern added there and not here would
# leave the body surface behind again, which is the exact history this
# registry exists to end.
#
# EVASION FOLDING. The rows are matched against a FOLDED copy of the text
# (:func:`_fold_ai_confusables`) and, for the mention tier only, a second
# whitespace-removed pass (:func:`_dewrap_with_line_map`). Both exist because
# a line-by-line literal scan is defeated by transformations that change no
# rendered glyph: a name split across a wrapped line, a zero-width space, a
# full-width or Cyrillic lookalike. The dewrapped pass runs the MENTION tier
# only — a shape row keys on punctuation and word boundaries that removing
# whitespace destroys, so running it dewrapped would be a pattern matching
# something other than what it reads as.
#
# WHERE THIS GUARD STOPS, stated as the boundary rather than discovered as a
# gap. Four rounds of adversarial review hardened the registries behind this
# family, in a repeating shape worth naming once: each round pinned a thing,
# and the next round moved one level down to what that thing was DERIVED from
# — the pattern set, then the sets it reads, then the objects compiled from
# those sets, then the function body performing the substitution, then the
# callee that decides which lines are skipped at all. Every step was a real
# hole and every fix is measured. But the recursion has a floor, and this is
# it: THE GUARDS DEFEND AGAINST DRIFT AND OVERSIGHT, NOT AGAINST AN AUTHOR WHO
# IS EDITING THE ENFORCEMENT CODE ON PURPOSE. Anyone who can change this file
# can change the tests in the same commit; no assertion inside a system can
# bind an author who is rewriting that system. What the pins buy is that every
# such change must be VISIBLE — it has to touch a pinned artifact, name what it
# is widening, and survive review — which is exactly the property the original
# defect lacked, when a single narrow literal silently covered a surface
# nobody was watching.
#
# So the honest ending is the same sentence the coverage limits carry: a green
# is a floor. The next increment on this family belongs in review, not in
# another assertion.
#
# RESIDUE, stated rather than left to be discovered: (a) code comments and
# docstrings are still unscanned for AI mentions — the tree census inherits
# the ``*.md``-and-gate-own-files exemption and has no AI family; (b)
# ``check_attribution.sh``'s "generated by" row misses an intervening word
# between the verb and the vendor, measured on this corpus. Filed as #8368 and
# #8369 respectively; neither is closed here.
#
# Each entry: ``(human_label, regex)``. The label is echoed in the report AND
# is what a PR-body block references under ``Hit: <surface> <label>``. The
# list is pinned to CONTRIBUTING.md § "AI-attribution text scan" by
# ``tests/test_audit_grep_diff.py::TestAiAttributionParity``.
# ---------------------------------------------------------------------------

# The mention-tier labels, named once so the dewrapped pass and the tests
# cannot disagree with the registry about which rows are bare-token rows.
AI_MENTION_TIER_LABELS: frozenset[str] = frozenset(
    # ``llm-mention`` belongs here and sat in the shape tier until review caught
    # it: it is a bare-token row like the two above, matching a word with no
    # attribution shape around it, so classifying it as a shape row made the
    # registry's own tier rule false about one of its ten entries. Its base rate
    # over 600 real PR bodies is 0, so the misclassification changed no verdict
    # — which is exactly why only a reader comparing code against docs would
    # have found it.
    {"ai-vendor-name", "robot-emoji", "llm-mention"}
)

AI_ATTRIBUTION_SPECS: list[tuple[str, str]] = [
    # MENTION tier. Vendor/product names with no ordinary-English reading in
    # this repository's vocabulary. Deliberately NOT word-anchored: the
    # dewrapped pass has no word boundaries left to anchor to, and no clean
    # corpus case is reached by substring matching (``Claudia`` does not
    # contain ``claude`` — the fifth letter differs).
    ("ai-vendor-name", r"claude|anthropic|copilot|chatgpt|openai"),
    ("robot-emoji", "\U0001f916"),
    # SHAPE tier.
    (
        "ai-coauthor-trailer",
        r"co-?authored[- ]?by\s*:?[^\n]{0,40}"
        r"(claude|anthropic|copilot|openai|chatgpt|cursor|gpt|ai[- ]bot|llm"
        r"|(?<![/\w.])assistant)",
    ),
    (
        "generated-with-ai",
        r"generat(?:ed|ing)\s+(?:with|by|using)\b[^\n]{0,40}"
        r"(claude|copilot|chatgpt|openai|cursor|gpt|llm"
        r"|(?<![/\w.])assistant|\bai\b)",
    ),
    (
        "ai-assisted-phrasing",
        r"\bai[- ](?:assisted|generated|written|authored|drafted)\b",
    ),
    ("agent-logs-url-trailer", r"agent-logs-url\s*:"),
    (
        "made-with-tool-trailer",
        r"made[- ]with\s*:?[^\n]{0,40}?(?:cursor|copilot|claude|chatgpt|\bai\b)",
    ),
    ("copilot-autofix-subject", r"potential fix for pull request finding"),
    ("llm-mention", r"\bllms?\b"),
    (
        "authored-by-ai-prose",
        r"\b(?:written|drafted|authored)\s+by\b[^\n]{0,40}?"
        r"\b(?:ai|llms?|bot|assistant)\b",
    ),
]

# The invisible codepoints folded away before matching: inserting one changes
# no glyph a reviewer sees while defeating a literal scan.
#
# DERIVED from Unicode general category (:mod:`invisible_characters`), not
# listed. The hand-written string this replaces held six codepoints, and its
# guard was a SUBSET assertion -- which cannot red as the class grows, and said
# nothing about the ones never listed: U+00A0 and the bidi overrides
# U+202A-U+202E were in neither the list nor the guard.
_AI_INVISIBLE_CHARS: frozenset[str] = invisible_codepoints()

# HOW each half folds, which is why the class could not simply be widened in
# place. A ZERO-WIDTH character is DELETED -- removing it rejoins the token it
# was inserted to split. A SPACE-LIKE one (U+00A0 and its Zs siblings) folds to
# a plain SPACE instead: deleting it would weld the words on either side
# together and destroy the very token the scan is hunting. The old string was a
# delete-list, so admitting U+00A0 to it would have been a silent regression.
_AI_INVISIBLE_FOLD: dict[str, str | None] = {
    ch: (None if has_no_advance_width(ch) else " ") for ch in _AI_INVISIBLE_CHARS
}

# Homoglyph fold. Each key is a codepoint that RENDERS as the Latin value at
# normal reading size; the value is the Latin character the pattern registry
# above is written with. The vertical-stroke class (capital I, digit one,
# Cyrillic І, Greek Ι) folds to lowercase ``l`` rather than to ``i`` because
# the tokens being matched are matched case-insensitively and the glyph is
# ambiguous between the two — folding to a single representative is what makes
# the class collapse at all. The fold is applied ONLY to this family's input,
# so a collision it introduces elsewhere in the text (``Illinois`` becomes
# ``lllinois``) cannot reach another gate, and no clean corpus case is turned
# into a hit by it.
_AI_HOMOGLYPHS: dict[str, str] = {
    "I": "l",
    "1": "l",
    "І": "l",
    "Ӏ": "l",
    "Ι": "l",
    "Ⅰ": "l",
    "а": "a",
    "α": "a",
    "А": "a",
    "Α": "a",
    "е": "e",
    "Е": "e",
    "Ε": "e",
    "о": "o",
    "ο": "o",
    "О": "o",
    "Ο": "o",
    "0": "o",
    "р": "p",
    "ρ": "p",
    "Р": "p",
    "Ρ": "p",
    "с": "c",
    "ϲ": "c",
    "С": "c",
    "у": "y",
    "У": "y",
    "Υ": "y",
    "х": "x",
    "Х": "x",
    "Χ": "x",
    "і": "i",
    "ı": "i",
    "ι": "i",
    "ѕ": "s",
    "Ѕ": "s",
    "ԁ": "d",
    "գ": "g",
    "հ": "h",
    "ո": "n",
    "ս": "u",
    "В": "b",
    "Н": "h",
    "К": "k",
    "М": "m",
    "Т": "t",
    "Β": "b",
    "Η": "h",
    "Κ": "k",
    "Μ": "m",
    "Τ": "t",
    "Ν": "n",
    "Ζ": "z",
    "Ω": "w",
}
_AI_FOLD_TABLE = str.maketrans({**_AI_INVISIBLE_FOLD, **_AI_HOMOGLYPHS})

# The INVISIBLE half of that fold, on its own (#8715 review).
#
# WHY IT IS A SECOND TABLE AND NOT ``_AI_FOLD_TABLE`` REUSED. The AI fold is
# three transforms, and the other two are scoped to that family ON PURPOSE:
# NFKC rewrites compatibility forms, and :data:`_AI_HOMOGLYPHS` maps ``0``->``o``
# and ``1``->``l``, whose own comment records that the collision it introduces
# (``Illinois`` -> ``lllinois``) must not reach another gate. Handing that table
# to :data:`PATTERN_SPECS` would import both licences into a family that never
# asked for them. This table carries ONLY the class derived in
# :mod:`invisible_characters`, folded the two ways that class folds -- a
# zero-width character DELETED, a space-like one turned into a plain space.
_INVISIBLE_FOLD_TABLE = str.maketrans(_AI_INVISIBLE_FOLD)


def _fold_invisibles(text: str) -> str:
    """``text`` with the invisible class folded away and nothing else touched.

    See :data:`_INVISIBLE_FOLD_TABLE` for why this is not
    :func:`_fold_ai_confusables`.
    """
    return text.translate(_INVISIBLE_FOLD_TABLE)


# Repository ARTIFACT names that happen to contain a vendor token (#8331).
#
# WHY THIS EXISTS. The mention tier fires on a bare vendor token, and two of
# this repository's own file/directory names carry one: the agent-instruction
# file at the repository root and the harness config directory beside it.
# Naming either in a PR description is ordinary, frequent and entirely
# legitimate — the first draft of THIS change's own PR body was red purely for
# citing the instruction file alongside CONTRIBUTING.md. A gate that reds on a
# path a contributor has to be able to name is a gate that gets muted, and a
# muted gate is the state #8331 exists to leave.
#
# WHY IT IS NOT A BYPASS, and the scope is deliberately three-sided:
#
#   1. EXACT TOKENS ONLY. The two strings below are masked; nothing else is.
#      A vendor token anywhere else in the text still fires. THE MASKING
#      SURFACE IS :func:`_mask_ai_artifacts`, AND THIS TUPLE BOUNDS IT ONLY
#      BECAUSE THE DERIVATION IS ENFORCED. An earlier revision of this comment
#      said the tuple's membership WAS the whole security surface; review
#      falsified that by measurement — appending one alternation to the
#      compiled regex, routing extra names through a differently-named global,
#      or adding one ``.replace`` in the function each masked tokens the tuple
#      never named while the whole suite stayed green. So there are TWO
#      guards, not one, and the second is what makes the first mean anything:
#      the tuple is pinned by EQUALITY in
#      ``TestAiAttributionRegistriesArePinnedByEquality``, and
#      ``TestAiAttributionDerivationsAreEnforced`` compares what the function
#      DOES against a reference built from that tuple, so every route above
#      reds however the extra names are spelled or reached. Equality rather
#      than a property assertion, and the difference is not stylistic. It was measured: the
#      first version of this carve-out was guarded only by a per-member
#      property ("each name still reds inside a co-author trailer"), and that
#      guard was ANTI-CORRELATED with the risk. A name containing a vendor
#      substring satisfies it AUTOMATICALLY, because the shape row catches the
#      substring rather than the carve-out — so appending ``claude-code``,
#      ``.claude-config/``, ``CLAUDE.md.bak`` or ``anthropic-tools/`` left the
#      whole suite green while widening the vendor-masking surface, and
#      appending a harmless ``zzqq`` was the case that RED. DELETING an entry
#      was silent too. An equality pin fails on any change, in either
#      direction, which a per-member property provably cannot.
#
#      The general form, because this gate has the shape twice over: PINNING
#      THE BEHAVIOUR A REGISTRY PRODUCES IS NOT PINNING THE REGISTRY. The
#      residual's current EXTENT was pinned; the SET that determines that
#      extent was not, and those are different claims. That is the same shape
#      as the defect this whole family exists to close — a pattern registry
#      nobody was watching. Every registry the AI family reads is inventoried
#      in that test class under a FOUR-way taxonomy — equality, no-shrink plus
#      corpus, doc-table parity, and enforced derivation — with the reason each
#      registry lands where it does written beside it.
#   2. MENTION TIER ONLY — and this bound is REAL BUT PARTIAL, stated as
#      measured rather than as the circular claim an earlier revision made.
#      The SHAPE rows read the UNMASKED text, so a line like
#      ``Co-authored-by: <artifact name>`` or ``Made-with: <artifact name>``
#      is still a hit on the trailer shape it enumerates — verified both ways.
#      What that does NOT buy, because the earlier wording implied it did: the
#      mention tier is also the only row catching an attribution whose trailer
#      KEY the shape tier does not enumerate. Measured, five such lines
#      (``Assisted-by:``, ``Written-with:``, ``Credit:``, ``Tool:``,
#      ``Signed-off-by-agent:``, each naming the vendor by spelling it as this
#      repository's artifact filename) PASS with the mask and RED without it —
#      5 of 5, mask-on/mask-off delta. So the honest bound is: **the shape tier
#      reads unmasked text for the shapes it ENUMERATES**, and an attribution
#      using an unenumerated key plus the artifact spelling gets through.
#      It needs an author who deliberately spells the vendor as a filename, so
#      it is not a harness-default hole and no measured real body reaches it —
#      but it is a hole, it is pinned by
#      ``TestAiAttributionArtifactCarveOut.test_the_disclosed_residual_of_the_mask``
#      so it cannot widen unnoticed, and it is why this carve-out is worth
#      exactly the friction it removes and not one word more.
#   3. NOT REACHABLE FROM AN ATTACKER'S SURFACE IN ANY OTHER FORM. The carve-out
#      exempts an occurrence of the artifact NAME, not a path, a glob or a
#      prefix — ``CLAUDE.md.backup`` masks only its leading artifact token and
#      the remainder is still scanned.
#
# ``tests/test_audit_grep_diff.py::TestAiAttributionArtifactCarveOut`` drives
# all three sides, including the case that matters most: the artifact name and
# a real footer in the SAME body still reds.
_AI_ARTIFACT_NAMES: tuple[str, ...] = ("CLAUDE.md", ".claude/")
_AI_ARTIFACT_RE = re.compile(
    "|".join(re.escape(name) for name in _AI_ARTIFACT_NAMES), re.IGNORECASE
)
# What a masked artifact name is replaced BY. Must contain no vendor token and
# no whitespace: the dewrapped pass removes whitespace, and a placeholder that
# introduced a word boundary could change a neighbouring row's verdict.
_AI_ARTIFACT_MASK = "[repo-artifact]"


def _mask_ai_artifacts(text: str) -> str:
    """Blank this repository's own artifact names for the MENTION tier only.

    See :data:`_AI_ARTIFACT_NAMES` for why the carve-out exists and the three
    ways its scope is bounded.
    """
    return _AI_ARTIFACT_RE.sub(_AI_ARTIFACT_MASK, text)


# ---------------------------------------------------------------------------
# Scoped pattern registry — display-fidelity re-derivation tripwires (#2474,
# epic #2477). These differ from :data:`PATTERN_SPECS` in TWO ways:
#
#   1. They are PATH-SCOPED. Each entry carries a tuple of ``fnmatch`` globs;
#      the pattern is only a hit when the added line's file path matches one
#      of them. The globals above scan EVERY added line (any path); these
#      scan only the DISPLAY paths the rule governs (the FE debug tree, the
#      Studio not-reached stamping, the boost-table debug panels). A
#      re-derivation in those surfaces is the #2465 / #2469 bug class — a
#      DISPLAYED body / value synthesized on the FE instead of rendered
#      backend-verbatim. The same identifier in a non-display path (a real
#      ``reconstruct``-named util elsewhere) is out of this rule's scope.
#
#   2. They mirror a SEPARATE CONTRIBUTING.md subsection — "Display-fidelity
#      re-derivation guard" — not the legacy one-liner. The parity test
#      ``tests/test_audit_grep_diff.py::TestScopedPatternParity`` pins each
#      scoped label/pattern/scope against that subsection so the doc and the
#      gate cannot drift.
#
# Each entry: ``(human_label, grep_regex, path_globs)``. The label is echoed
# in the report AND is what the PR-body justification block references under
# ``Hit: <path>:<line> <label>``. The globs are matched with
# :func:`fnmatch.fnmatch` against the diff's ``b/<path>`` (``b/`` stripped),
# so ``search-ui/src/features/search/debug/*`` matches a file directly in the
# debug dir and the recursive ``.../debug/**`` form matches nested files too.
#
# WHY these patterns, and how existing legitimate uses are handled:
#
#   - ``*FromLevel(`` / ``bareTier*(`` — the FE recovering a tier's wire body
#     by unwrapping the cumulative-union ladder client-side
#     (``bareTierQueryFromLevel`` / ``tierBodyFromQuerySequence`` in
#     ``stepModel.ts``). This is HIGH-2 of the #2465 sweep; #2482 DELETED it in
#     favour of the engine-stamped verbatim body (only a ``// Issue #2465``
#     removal-record comment remains on ``main``). The CALL/DEF-shaped regexes
#     (identifier immediately followed by ``(``) trip on a re-introduced
#     definition or call but NOT on that prose removal comment; a re-derivation
#     always has a call site, so the anchor catches an arrow-function form too.
#   - ``reconstruct`` / ``decompose`` / ``synthes`` — anchored to a
#     FUNCTION-CALL shape (``…(``) so the many prose doc-comments in the debug
#     tree ("no synthesis", "the legacy reconstruction path", "further
#     decompose") do NOT trip; only an actual ``reconstructX(`` /
#     ``synthesizeX(`` call in the debug display code does. The ONE carve-out is
#     the exact ``reconstructed(`` token: that is the #2473 typed-provenance
#     constructor (``provenance.ts``) — calling it is how a surface MAKES a
#     non-executed value visible (tag the datum → the renderer badges it), the
#     blessed pattern, not a violation. The ``(?!ed\()`` lookahead in its regex
#     exempts that token only; ``reconstructBody(`` / ``reconstructedTier(`` /
#     any other synthesis seam still trips. The sibling provenance constructor
#     ``notExecuted(`` (#2473 part 1 — the split: a backend-VERBATIM body that
#     never ran, distinct from the FE-synthesized ``reconstructed``) is likewise
#     blessed; it does NOT match the ``reconstruct…`` anchor at all (different
#     identifier), so it never trips this rule — it makes non-execution visible,
#     it is not a synthesis seam. A regression test pins both: ``reconstructed(``
#     and ``notExecuted(`` are exempt; ``reconstructedTier(`` still trips.
#   - ``build_search().to_dict()`` (Studio) — re-deriving a body Studio then
#     DISPLAYS (the #2465 HIGH-1: ``tracking_helpers._mark_not_reached``
#     stamped ``ctx.searches[i].build_search().to_dict()`` for the not-reached
#     row). Scoped to the Studio search package but EXCLUDING the legacy /
#     passthrough path file ``step_execution.py``, where ``build_search()`` is
#     the documented standalone-fallback body source (and never chains
#     ``.to_dict()`` to feed a display). The exclusion is enforced in
#     :func:`_scope_matches` via the ``!`` negative-glob convention below.
#   - ``?? Math.`` — the #2469 boost-table class: a value display that falls
#     back to an arithmetic RECOMPUTE (``blk?.boost_at_max ?? Math.log(…)``,
#     ``matchedPurchase.frequency ?? Math.log1p(…)``) under the SAME source
#     label as the engine-verbatim value. Scoped to the debug panels. The
#     ``Math.`` anchor is deliberately narrow: the hundreds of benign
#     ``?? []`` / ``?? null`` / ``?? {}`` / ``?? 0`` / ``?? meta?.tier``
#     null-coalescings in the same files are NOT recompute fallbacks and must
#     not flood the gate. ``?? Math.`` is the precise telltale of a formula
#     fallback; a recompute that avoids ``Math.`` (e.g. ``?? frequency *
#     decay``) rides in the same flagged table and is justified alongside.
#
# A scoped entry whose ``path_globs`` start with ``!`` is a NEGATIVE glob: the
# pattern hits everywhere in the positive globs EXCEPT files matching the
# negative one. See :func:`_scope_matches`.
# ---------------------------------------------------------------------------
_FE_DEBUG_GLOBS: tuple[str, ...] = (
    "search-ui/src/features/search/debug/*",
    "search-ui/src/features/search/debug/**",
    "search-ui/src/features/search/components/debug/*",
    "search-ui/src/features/search/components/debug/**",
    # The debug panels that live directly under ``components/`` rather than
    # ``components/debug/`` but ARE debug surfaces (#2469 cites
    # ``ResultCardDebugPanel.tsx``). Listed explicitly so the value-recompute
    # rule reaches them without widening the glob to all of ``components/``.
    "search-ui/src/features/search/components/ResultCardDebugPanel.tsx",
    "search-ui/src/features/search/components/DebugPanel.tsx",
    "search-ui/src/features/search/components/DeveloperToolsPanelContent.tsx",
    # Test files are exempt by intent — same precedent as the global
    # patterns (a test that pins the ABSENCE of a re-derivation, or fixtures
    # a body shape, legitimately names the banned identifier). The negative
    # globs carve out ``__tests__`` dirs and ``*.test.*`` / ``*.spec.*``
    # files anywhere in the FE debug scope.
    "!search-ui/src/features/search/**/__tests__/**",
    "!search-ui/src/features/search/**/*.test.*",
    "!search-ui/src/features/search/**/*.spec.*",
)

# Studio search package, EXCLUDING the documented legacy / standalone /
# passthrough path. ``step_execution.py`` is where ``ProductSearch.build_search()``
# is the legitimate passthrough-fallback body source (rewrite disabled / no
# policies index); it never chains ``.to_dict()`` to feed a DISPLAY, so it is
# carved out via the leading-``!`` negative glob.
_STUDIO_NONLEGACY_GLOBS: tuple[str, ...] = (
    "packages/prism-studio/src/prism_studio/search/*.py",
    "!packages/prism-studio/src/prism_studio/search/step_execution.py",
)

# #4554 — the soft-boost weight→multiplier conversion. Scope is DELIBERATELY the
# whole product surface (engine src + studio src + the FE search feature), not a
# hand-listed set of today's boost-rendering files: the failure mode this tracks is a
# NEW module quietly growing its own copy of the arithmetic, which a file list by
# construction cannot see. Negative globs carve out (a) the ONE blessed home,
# ``tier_axis_wire.py``, where ``soft_boost_multiplier`` / ``combined_soft_boost_multiplier``
# ARE the conversion, and (b) test files, exempt by intent on the same precedent as every
# other family here (a test that pins the ABSENCE of the math must be able to name it).
_SOFT_BOOST_MATH_GLOBS: tuple[str, ...] = (
    "packages/prism-engine/src/prism_engine/**",
    "packages/prism-studio/src/prism_studio/**",
    "search-ui/src/**",
    # The single home of the conversion — the primitive the rest delegate to.
    "!packages/prism-engine/src/prism_engine/rewrite/tier_axis_wire.py",
    # The FE's BLESSED MIRROR of that primitive (#4704). The Merchandiser Settings
    # panel must preview a multiplier for a weight the merchandiser has typed but not
    # SAVED, for which no emit exists, so ``softBoostMultiplier`` lives here — pinned
    # to the Python canonical by the shared ``softBoostMultiplier.parity.json`` fixture
    # read from both languages, the same arrangement ``categoryNodeLabel`` has. The
    # panel reads the emitted ``filter_multiplier`` verbatim wherever one exists.
    "!search-ui/src/features/search/components/signalBoostFormat.ts",
    "!**/__tests__/**",
    "!**/*.test.*",
    "!**/*.spec.*",
    "!**/testing/**",
)


# #4652 — the category-path LEAF LABEL derivation. A path's short-form leaf
# (``Fruits/Citrus/Oranges`` -> ``Oranges``) is a DISPLAY fact with exactly ONE
# producer: :func:`prism_engine.category_path.category_leaf_label`, whose result the
# backend EMITS per value (``ActiveFilter.display_leaf`` / ``FacetResponse.display_leaves``)
# and every search surface renders VERBATIM. Four hand-rolled Python copies existed
# before #4651 and four TypeScript surface derivations before #4652; nothing red'd when
# one of them drifted, which is how the #4610 divergence shipped a blank Studio label
# beside a correct FE one.
#
# THE DISPLAY / IDENTITY LINE IS WHY THE CARVE-OUTS ARE BY FILE, NOT BY PATTERN. A
# category leaf is also used as a MATCHING / JOIN key (the per-tier fold index, the #3689
# count alias, the negation leaf match). Those splits must stay RAW -- trimming them would
# change which documents MATCH, i.e. MEMBERSHIP -- so they are deliberately NOT migrated
# and are named here as the three join-key homes. A NEW leaf split anywhere else is a
# display derivation until proven otherwise, and gets a justification block.
#
# ANCHORED ON A CODE SHAPE, per the ``reconstruct*(`` / #4554 discipline: the split must
# be on a ``sep`` / ``separator`` / ``path_separator`` IDENTIFIER, because a category
# separator is CONFIGURED (never a literal). That distinguishes a category leaf from the
# many legitimate literal splits in core -- a ``$ref`` JSON pointer (``rsplit("/", 1)``),
# a dotted module name, an attribute path -- none of which this can flag. Prose that
# merely DESCRIBES the retired derivation (``x.split(sep)[-1]`` inside a docstring) is
# still a hit by design: the anchor cannot read intent, and a one-line justification is
# the cheap resolution.
_LEAF_LABEL_PY_GLOBS: tuple[str, ...] = (
    "packages/prism-engine/src/prism_engine/**",
    "packages/prism-studio/src/prism_studio/**",
    "packages/prism-analytics/src/prism_analytics/**",
    # THE canonical home -- this module IS the derivation.
    "!packages/prism-engine/src/prism_engine/category_path.py",
    # The three JOIN-KEY homes (#4651 / #4652 kept these raw on purpose; see above).
    "!packages/prism-studio/src/prism_studio/search/facets/tier_contribution.py",
    "!packages/prism-studio/src/prism_studio/search/response_forwarding.py",
    "!packages/prism-engine/src/prism_engine/rewrite/negation_suppression.py",
    "!**/__tests__/**",
    "!**/*_test.py",
    "!**/test_*.py",
)

# The TypeScript half of the same rule. ``categoryNodeLabel`` is the FE's BLESSED MIRROR
# of the Python canonical, and after #4652 it has exactly ONE legitimate caller: the admin
# policy editor, which labels values living only in UNSAVED form state that never
# round-trip through a search response, so there is no emit for it to read. Every SEARCH
# surface reads the emitted leaf instead. Calling it from anywhere else re-opens the
# two-implementations-of-one-rule shape #4652 closed, so the call site is the anchor.
_LEAF_LABEL_TS_GLOBS: tuple[str, ...] = (
    "search-ui/src/**",
    # Its definition + the ONE genuine authoring exception.
    "!search-ui/src/features/search/utils/categoryPath.ts",
    "!search-ui/src/features/admin/**",
    "!**/__tests__/**",
    "!**/*.test.*",
    "!**/*.spec.*",
)


SCOPED_PATTERN_SPECS: list[tuple[str, str, tuple[str, ...]]] = [
    # ``add_filter(`` guards a PRODUCTION request path: Studio building an ES
    # filter itself instead of sending the Engine's wire query (#894, #935,
    # #1418). A test that calls it builds no request and cannot bypass anything,
    # so ``tests/**`` is exempt for THIS row only (#10787). It sits in the scoped
    # family for the negative glob, and the CONTRIBUTING.md one-liner stays whole.
    ("add_filter(", r"add_filter\(", ("*", "!tests/**")),
    # FE re-derivation of a tier wire body from the union ladder (#2465 HIGH-2).
    # Call/def shape (identifier immediately followed by ``(``) so the lingering
    # ``// Issue #2465 — the FE-side ``bareTierQueryFromLevel``…`` removal-record
    # comment on ``main`` (the deleted #2482 reshape) does NOT trip — only an
    # actual ``…FromLevel(`` definition or call does. A re-derivation always has
    # a call site, so the call-shape anchor still catches an arrow-function form.
    ("*FromLevel(", r"[A-Za-z]+FromLevel\(", _FE_DEBUG_GLOBS),
    ("bareTier*(", r"bareTier[A-Za-z]*\(", _FE_DEBUG_GLOBS),
    # FE synthesis seams — function-call shape only (prose comments exempt).
    # The ``(?!ed\()`` negative-lookahead exempts the EXACT blessed
    # ``reconstructed(`` provenance constructor (#2473) — that is the typed
    # primitive that makes a non-executed value VISIBLE (it tags the datum so the
    # renderer badges it), the OPPOSITE of an unlabeled synthesis seam, so its
    # call sites must not have to carry a justification block forever. Every other
    # ``reconstructX(`` (incl. ``reconstructBody(`` / ``reconstructedTier(``) is
    # still a hit — only the bare constructor token is carved out. The sibling
    # blessed constructor ``notExecuted(`` (#2473 part 1) is a DIFFERENT
    # identifier and never matches this ``reconstruct…`` anchor, so it needs no
    # lookahead — but it is documented + test-pinned as blessed for the same
    # reason (it makes non-execution visible; it does not synthesize a value).
    ("reconstruct*(", r"\breconstruct(?!ed\()[A-Za-z]*\(", _FE_DEBUG_GLOBS),
    ("decompose*(", r"\bdecompose[A-Za-z]*\(", _FE_DEBUG_GLOBS),
    ("synthes*(", r"\bsynthes[A-Za-z]*\(", _FE_DEBUG_GLOBS),
    # Studio re-derivation of a DISPLAYED body (#2465 HIGH-1).
    (
        "build_search().to_dict()",
        r"\.build_search\(\)\.to_dict\(\)",
        _STUDIO_NONLEGACY_GLOBS,
    ),
    # #2469 value-display arithmetic-recompute fallback in debug panels.
    ("?? Math.", r"\?\?\s*Math\.", _FE_DEBUG_GLOBS),
    # #4554 soft-boost magnitude math outside the ONE primitive. The engine applies
    # each soft boost as ``[{weight:1},{filter,weight:w}]`` with ``score_mode:sum``, so a
    # match multiplies by ``1 + w`` and stacked boosts by ``Pi(1 + wi)``. That arithmetic
    # was open-coded in FOUR places before #4554 while the chip displayed the raw weight
    # (``x1`` for a boost that DOUBLES the score).
    #
    # ANCHORED TO A CODE SHAPE, the same discipline the ``reconstruct*(`` family uses:
    # each pattern requires an ASSIGNMENT (``= 1 + w``, ``*= 1 + w``), a ``return``, or a
    # ``<...>multiplier *=`` accumulator. A bare ``1 + w`` anchor is unusable here because
    # the honest NOTATION is literally ``1 + Soft boost (w) = (1+w)x`` — every doc comment
    # and JSX label describing the display would trip it. Prose says "multiplies by
    # ``1 + w``" and "``1 + Soft boost (w) = (1+w)x``"; neither has an assignment
    # immediately left of the ``1``, so neither is a hit, while ``clause_multiplier=1 + w``
    # and ``effective *= 1.0 + w`` both are.
    #
    # The ``.0`` is optional deliberately: the first version of this guard pinned
    # ``1\.0\s*\+`` exactly and was evaded by writing ``1 + w``. Patterns are
    # alternation-free so each stays one row of the ``scoped-audit-grep`` doc table.
    #
    # SCOPE OF THE CLAIM — CORRECTED BY #4740. READ THIS BEFORE TRUSTING THESE ROWS.
    # A static scan catches readable spellings, not every possible one (arithmetic inside
    # a template interpolation, or via ``Math.pow``, will slip). These rows are also
    # DIFF-SCOPED: they see ADDED LINES ONLY and never sweep what is already in the tree.
    #
    # This comment used to end "These are the tree-wide net under that." That was FALSE,
    # and the correction is the point of this note. #4740 found FOUR open-coded Python
    # sites that had sat on main straight through the remedy these rows are — two of them
    # shipping numbers the engine never applied — for two independent reasons: the
    # diff-scoping above, and the fact that the five FORWARD rows anchor on
    # ``= ``/``return ``/``*= `` immediately before the literal ``1``, which
    # ``round(1.0 + w, 2)`` and f-string interpolation do not have. They were blind to
    # precisely the two spellings that were producing wrong numbers.
    #
    # PYTHON NOW HAS A SECOND, COMPLEMENTARY GUARD:
    # ``tests/test_soft_boost_multiplier_single_home_4740.py``, a tree-wide AST census —
    # not diff-scoped, and matched on the parsed tree rather than source text.
    #
    # THE TWO ARE COMPLEMENTARY, NOT NESTED. Neither subsumes the other, and #4740's
    # review established this by execution after an earlier draft of that PR wrongly
    # claimed the census was "strictly stronger" and narrowed these globs to the FE on
    # the strength of it:
    #   * the CENSUS is stronger on SPELLING (``round(...)``, f-strings, ``cast``/``.get``)
    #     and on SCOPE (whole tree, every run, not just added lines);
    #   * THESE ROWS are stronger on the OPERAND AXIS. The census is operand-NAME-anchored
    #     (it requires a name matching ``^w$|weight$``), whereas the ``return`` row is
    #     operand-AGNOSTIC — ``return 1 + <anything>`` matches regardless of what the
    #     operand is called. So ``return 1.0 + boost`` (an operand not named "weight") trips
    #     that row and NOT the census. (After #4663 the ``Pi(1+w)`` row is operand-anchored on
    #     ``boost`` and the accumulator row is RHS-agnostic but LHS-``[Bb]oost``-anchored — see
    #     the per-row note below — so business-signal ``*=`` math no longer counts as a hit.)
    # Keep both. Removing either opens an axis the other does not cover.
    #
    # NOTE the asymmetry, so nobody generalises the left-anchoring flaw further than it
    # goes: only the five FORWARD rows have it. The three REVERSED rows are
    # operand-anchored and would have caught ``round(weight + 1, 2)``. It is an asymmetry
    # inside one family, not a repo-wide pattern-design fault.
    #
    # The NON-evadable guard is behavioural — ``softBoostMagnitudeHonesty4554.test.tsx``
    # feeds an axis whose emitted ``effective_multiplier`` DISAGREES with the product of
    # its clause multipliers and requires the reader to return the EMITTED number, so any
    # recompute fails regardless of spelling. These rows are one text net under that.
    (
        "=1+w soft-boost math",
        r"=\s*1(?:\.0)?\s*\+\s*w\b",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    (
        "=1+weight soft-boost math",
        r"=\s*1(?:\.0)?\s*\+\s*[A-Za-z_.\[\]]*weight\b",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    (
        "return 1+w soft-boost math",
        r"return\s+1(?:\.0)?\s*\+",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    # BOTH `*=` rows were narrowed in #4663 to stop firing on BUSINESS-signal math — a
    # DIFFERENT family with the same ``Π(1 + contribᵢ)`` shape: Studio's
    # ``business_multiplier *= 1.0 + signal_contrib[sid]`` (score_explanation.py) and the
    # FE's ``localBusinessMultiplier *= 1 + contrib`` (boostBreakdown.ts). The two rows are
    # narrowed on DIFFERENT axes, each the least-lossy anchor for its own shape:
    #
    #   * ``Pi(1+w)`` is OPERAND-anchored on ``boost`` (mirrors the ``=1+weight`` sibling's
    #     operand anchor), NOT LHS-anchored. It matches ``<any> *= 1 + <…>boost`` — so a
    #     normally-spelled accumulator ``multiplier *= 1 + sb.boost`` / ``total *= 1 + boost``
    #     stays caught regardless of the accumulator's name — and it uniquely holds the
    #     PARENTHESISED form ``*= (1 + boost)`` that the ``=1+w`` / ``=1+weight`` rows miss
    #     (their leading ``=`` cannot reach across a ``(``). It goes quiet on the business
    #     lines because their operand is ``signal_contrib`` / ``contrib``, not a ``boost``.
    #     (LHS-anchoring THIS row instead would have dropped ``multiplier *= 1 + boost`` — a
    #     real forward hole — which is why the operand anchor is used here.)
    #   * ``soft-boost multiplier accumulator`` is the RHS-agnostic ``<…>multiplier *= <any
    #     factor>`` row: with no operand to anchor on, its only non-business anchor is the
    #     LHS, so it requires a ``[Bb]oost`` token in the accumulated identifier. It keeps
    #     ``localSoftBoostMultiplier *= layer`` (a boost-named VARIABLE-factor product, its
    #     unique coverage over ``Pi(1+w)``) while dropping ``business_multiplier *= …`` and a
    #     generic ``running_multiplier *= layer``.
    #
    # ACCEPTED COLLATERAL DROP (test-driven-removal pinned): a GENERIC non-boost-named
    # multiplier accumulator taking a non-``boost`` factor — ``running_multiplier *= layer`` —
    # was caught on ``main`` by the old operand-agnostic accumulator row and is now caught by
    # NEITHER this family NOR the ``^w$|weight$`` AST census, widening the #4759 intersection
    # seam along the ``*=`` axis. That drop is deliberate (acceptance needs predominantly-TP,
    # and the concrete FP removed is business math) and is pinned both by
    # ``test_business_signal_math_no_longer_trips`` (the intended business drops) and by
    # ``test_generic_multiplier_accumulator_drop_is_pinned`` (the collateral generic drop),
    # and disclosed in the #4759 census test. Rows stay alternation-free (one doc-table row).
    (
        "Pi(1+w) soft-boost stacking",
        r"\*=\s*\(?\s*1(?:\.0)?\s*\+\s*[A-Za-z_.\[\]]*boost\b",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    (
        "soft-boost multiplier accumulator",
        r"[A-Za-z_][A-Za-z0-9_.]*[Bb]oost[A-Za-z0-9_.]*multiplier\s*\*=",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    # #4705 — the REVERSED operand order. Every pattern above is written ``1 + <w>``;
    # none handled ``<w> + 1``, so ``relevance_boosts.py`` computed the same conversion
    # as ``entry.weight + 1.0`` for a year under a family that believed it covered the
    # file. Worse, the ``=1+weight`` row DID hit that file — on a PROSE COMMENT — so the
    # family looked like it was working BECAUSE of a false positive while the real code
    # went unseen. The FE guard already carried a reversed pattern for exactly this
    # reason; the knowledge simply never reached the tree-wide family.
    #
    # These cannot be as permissive as their forward twins: ``return 1 +`` is safe with
    # ANY right operand because the literal ``1`` on the left is distinctive, whereas a
    # bare ``… + 1`` is ordinary code (an index, a page, a count). So the reversed rows
    # anchor on the weight-bearing operand instead, and are alternation-free so each
    # stays one row of the ``scoped-audit-grep`` doc table.
    (
        "w+1 soft-boost math",
        r"\bw\s*\+\s*1(?:\.0)?\b",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    (
        "weight+1 soft-boost math",
        r"[A-Za-z_.\[\]]*[Ww]eight\s*\+\s*1(?:\.0)?\b",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    (
        "multiplier+1 soft-boost math",
        r"[A-Za-z_.\[\]]*[Mm]ultiplier\s*\+\s*1(?:\.0)?\b",
        _SOFT_BOOST_MATH_GLOBS,
    ),
    # #4652 category leaf-label derivation outside its ONE producer (both languages).
    # Patterns are ALTERNATION-FREE so each stays one row of the ``scoped-audit-grep``
    # doc table (which is ``|``-delimited).
    (
        "sep-split leaf derivation (py)",
        r"\.r?split\([^)]*sep[A-Za-z_]*[^)]*\)\s*\[\s*-\s*1\s*\]",
        _LEAF_LABEL_PY_GLOBS,
    ),
    (
        "sep-split leaf pop (ts)",
        r"\.split\([^)]*[Ss]ep[^)]*\)\s*\.pop\(",
        _LEAF_LABEL_TS_GLOBS,
    ),
    (
        "sep-split leaf at(-1) (ts)",
        r"\.split\([^)]*[Ss]ep[^)]*\)\s*\.at\(",
        _LEAF_LABEL_TS_GLOBS,
    ),
    (
        "categoryNodeLabel( outside the admin editor",
        r"\bcategoryNodeLabel\(",
        _LEAF_LABEL_TS_GLOBS,
    ),
    # The BLESSED splitters, tail-indexed. Both languages expose a canonical segment
    # splitter, and taking its LAST element reproduces the retired raw-tail semantics
    # exactly — re-creating #4610 through the front door rather than by hand-rolling a
    # split. Cheap to write, invisible to every anchor above, so each gets its own row.
    (
        "splitCategoryPath tail-popped (ts)",
        r"splitCategoryPath\([^)]*\)\s*\.pop\(",
        _LEAF_LABEL_TS_GLOBS,
    ),
    (
        "splitCategoryPath tail-indexed (ts)",
        r"splitCategoryPath\([^)]*\)\s*\.at\(",
        _LEAF_LABEL_TS_GLOBS,
    ),
    (
        "split_category_path tail-indexed (py)",
        r"split_category_path\([^)]*\)\s*\[\s*-\s*1\s*\]",
        _LEAF_LABEL_PY_GLOBS,
    ),
]


# ---------------------------------------------------------------------------
# Companion-required registry — "banned UNLESS accompanied by X" (#6116).
#
# A fourth family, and the only one whose verdict depends on more than the
# single added line. A pattern here is a hit ONLY when its COMPANION pattern is
# absent from the same diff HUNK. Read the scope note below before adding a row:
# the scope is the hunk, not the function, and that is a deliberate limit rather
# than an oversight.
#
# THE INCIDENT (#5678 / PR #6113, follow-up #6116). ``POST /_bulk`` answers 200
# even when every item was rejected — the per-item verdicts live in the response
# body — so a caller passing ``raise_on_error=False`` gets a transport-level
# success that is indistinguishable from a write which landed nothing. #6113
# extracted :func:`prism_engine.es_helpers.check_bulk_result` as the SINGLE home
# of the count+error verdict and routed all four callers through it. That fix is
# correct, but it left the routing enforced by CONVENTION: a fifth caller can
# pass ``raise_on_error=False`` and simply omit the check, and nothing reds. The
# issue names the hazard exactly — "before a third caller copies whichever it
# lands next to" — so the remedy is a machine-checked gate, per
# ``contributing/single-source-of-truth.md``'s preference for a gate over a
# documented convention.
#
# SCOPE IS THE DIFF HUNK — say so plainly, because #6116 asked for "the same
# function" and this gate has no function scope to give. Every other family here
# decides on ONE added line; nothing in this script reconstructs a post-image, so
# there is no enclosing-function body to search. The hunk — the added lines plus
# the context lines git ships around them — is the widest true statement the diff
# surface supports, and inventing a function boundary from a partial post-image
# would be guesswork wearing a precise name. Two consequences, both accepted:
#
#   * FALSE NEGATIVE (narrow): a caller could put the ``bulk`` call and a
#     ``check_bulk_result(`` for a DIFFERENT write in one hunk. The hunk is small
#     enough that this is a contrivance, not a spelling someone reaches by
#     accident.
#   * FALSE POSITIVE (the realistic one), and it is WIDER than a first reading
#     suggests, so here is the measurement rather than a reassurance. Re-adding
#     ONLY the call line of an existing, correctly-routed caller, with git's
#     default three lines of context, is a hit at THREE of the four live sites:
#     the check sits 13, 6 and 5 lines below the call (``personalization/cli.py``
#     twice, ``vocab_curation.py`` once) and only the fourth, two lines below,
#     is inside the context reach. That is why this family is
#     JUSTIFICATION-GATED (a PR-body block clears it) rather than a HARD block
#     like the customer-name / frozen-derivation guards. It is tolerable because
#     the shape that triggers it is rare — the keyword is ALREADY on those lines,
#     so only a re-add reaches it, while the case the rule exists for (a NEW
#     caller, whose whole function arrives in one hunk) is decided correctly.
#     ``test_a_live_call_site_sits_outside_the_default_context_reach`` pins the
#     residual so it cannot quietly stop being true.
#
# Widening the CONTEXT (``git diff -U10`` in the workflow) would shrink that
# residual, and was declined: it changes the input every family reads to soften
# one family's false positives, and a wider hunk is also a wider laundering
# window for the very hazard below. The block is cheaper than the coupling.
#
# Hunk scope also fails in the SAFE direction on the hazard the issue names. A
# per-FILE scope would be laxer and look friendlier, but it would let a new
# unchecked caller ride on an unrelated correct caller's check elsewhere in the
# same file — which is precisely "a third caller copies whichever it lands next
# to". A tighter scope catches that; the cost is a justification block.
#
# ANCHORED ON A CODE SHAPE, per the ``reconstruct*(`` / #4554 discipline. The
# leading ``[(,\s]`` requires the keyword to follow an open paren, a comma, or
# whitespace — an argument position. The engine's five PROSE mentions of the
# keyword all write it inside double backticks (````raise_on_error=False````),
# so a docstring edit in ``es_helpers.py`` / ``vocab_curation.py`` /
# ``personalization/cli.py`` does NOT trip while all four real call sites do,
# including the ruff-format-split spelling where the keyword starts its own
# line. Verified against the live lines by
# ``TestCompanionRequiredHitDetection::test_the_four_real_call_sites_all_match``
# and its prose sibling — not inferred from reading the regex.
#
# NOT run over the text surfaces (commit messages / PR body), for the same
# reason as the scoped and frozen families: it gates on a FILE PATH, and a text
# surface has none.
#
# NOT part of the scheduled whole-tree census either (``audit_grep_tree.py``
# imports the two line-scoped registries only). A census walks whole files, where
# "the same hunk" has no meaning; the honest whole-tree form of this rule is an
# AST function-scope walk, which is a separate build and deliberately not done
# here. Stated so the absence is a known gap rather than a silent one.
#
# Each entry: ``(human_label, grep_regex, companion_regex, path_globs)``. The
# label is echoed in the report AND is what a PR-body justification block
# references under ``Hit: <path>:<line> <label>``. Patterns are alternation-free
# so each stays one row of the ``|``-delimited ``companion-audit-grep`` doc
# table, which ``TestCompanionPatternParity`` pins against this registry.
# ---------------------------------------------------------------------------

# Bulk-write callers. Scope is the product packages' source plus ``scripts/``:
# the failure mode is a NEW caller, and a one-shot loader script is exactly where
# the next one gets written. Test files are exempt by intent — the same precedent
# every family here follows, and ``tests/test_bulk_write_loses_documents_5678_es.py``
# legitimately drives ``raise_on_error=False`` shapes to prove the rule bites.
_BULK_WRITE_GLOBS: tuple[str, ...] = (
    "packages/prism-engine/src/prism_engine/**",
    "packages/prism-studio/src/prism_studio/**",
    "packages/prism-analytics/src/prism_analytics/**",
    "scripts/**",
    "!**/__tests__/**",
    "!**/*_test.py",
    "!**/test_*.py",
)


COMPANION_PATTERN_SPECS: list[tuple[str, str, str, tuple[str, ...]]] = [
    (
        "raise_on_error=False without check_bulk_result",
        r"[(,\s]\s*raise_on_error\s*=\s*False",
        r"check_bulk_result\(",
        _BULK_WRITE_GLOBS,
    ),
]


# ---------------------------------------------------------------------------
# Customer-name registry — proprietary retailer names that must never appear
# in core (#2374). This family is DIFFERENT from the two above in one decisive
# way: a hit is a HARD BLOCK — there is no per-hit justification block that can
# let it through. The other two families exist because the flagged pattern can
# be a LEGITIMATE use that a reviewer signs off on inline (a passthrough
# ``.build_search()``, a labeled debug cross-check); the proprietary customer's
# name in core never has a legitimate use, because it is the one string that
# identifies them as a PRISM customer — CONTRIBUTING.md § "Generalize, don't
# fork per customer": core is never written FOR a named retailer, and no
# customer is named as a PRISM customer. That is the whole scope — this
# registry is a list of CUSTOMER names, not a scan for retailer or brand
# names generally, and public open-data brand values in demo content, tests
# and fixtures are fine (CONTRIBUTING.md § "Proprietary Customer Data — Never
# Commit" → "What does NOT count"). Routing it through the
# justification reconciliation would let a future PR quietly re-add the name by
# pasting a justification block, which is exactly what #2374 set out to
# prevent. So these are scanned on their own path (:func:`scan_for_customer_names`)
# and reported by :func:`render_customer_name_report`, BEFORE — and independent
# of — the justification machinery: any added line containing one fails the job
# outright.
#
# The guarded name is a private retailer customer name whose specifics belong
# in the private ``elastic/prism-<retailer>`` customization repo, never in core.
# #2374 / PR #2488 scrubbed it from the current tree and #3135 scrubbed it from
# the FULL git history; this guard keeps it scrubbed going forward.
#
# CRITICAL — no literal in source: the pattern below is an EXPLICIT case-fold
# CHARACTER-CLASS regex (``[mM][uU]…``), NOT the literal name. Writing the
# contiguous name here would re-introduce into this file exactly the string the
# #3135 rewrite removed from history — so ``git grep -i`` for the literal must
# stay 0 across the whole tree, this file included. The obfuscation is ALSO why
# the commit-message / PR-body text surfaces (below) need no separate
# self-exclusion: the char-class pattern cannot match its own source text, so a
# PR whose body or commits merely DOCUMENT the regex does not trip.
#
# The DIFF surface scans MARKDOWN, unlike every other family (#8019). The other
# families' patterns are CODE telltales, so a doc can only ever MENTION one and
# :func:`_is_self_or_doc` exempts ``*.md`` to keep the gate off its own
# documentation. This family does not have that property: a doc can genuinely
# USE the retailer's name, and a Markdown line naming the customer discloses
# that this retailer runs their ecommerce search on PRISM exactly as a line of
# code does — so the ONE family that is a hard block with no escape hatch was
# also the one family whose likeliest leak surface went unread. This scan
# therefore consumes the added-line list parsed with ``include_markdown=True``
# (see :func:`parse_diff_added_lines`): the gate's own script / test files stay
# excluded (:func:`_is_gate_own_file`), Markdown does not.
#
# Self-exclusion does NOT depend on that Markdown exemption, which is why
# dropping it here is safe: the pattern below is an explicit character class, so
# it cannot match its own source text, and the CONTRIBUTING.md "Customer-name
# guard" subsection and ``contributing/audit-grep-tripwires.md`` describe the
# rule the same way — by quoting the char class, never the contiguous name. The
# gate's own script / test files stay PATH-excluded for a different reason:
# their fixtures CONSTRUCT the real name at runtime (``CUSTOMER_NAME`` in
# ``tests/test_audit_grep_diff.py``, a ``printf`` octal escape in
# ``.github/scripts/test_audit_grep_diff.sh``) to prove the guard bites, and
# those constructed literals would trip it.
#
# Each entry: ``(human_label, grep_regex)``. The regex is the explicit case-fold
# character class so it matches ANY casing WITHOUT spelling the literal in
# source; ``re.IGNORECASE`` is also applied at compile time for parity with the
# documented ``grep -i`` form. Adding a future scrubbed customer name is a
# one-line append here + a row in the CONTRIBUTING.md table; the parity test
# pins the two together.
#
# THE SECOND CUSTOMIZATION, AND WHY ITS ROWS ARE A DIFFERENT SHAPE (#9247).
# Until #9247 this registry held ONE name. A second customization ships beside
# it — the industrial / MRO persona, whose customization lives in its own
# private ``elastic/prism-<retailer>`` repo — and the registry was blind to it,
# so on every PR touching that persona the gate's green was evidence about a
# name nobody was going to type and no evidence at all about the one an author
# might. That is a gate whose green is read as a property it does not check,
# which is the defect class #9220/#9224 and #9225/#9236 addressed on the
# commit-message surface.
#
# The two registrants are NOT the same problem, and the rows below are shaped
# by the difference rather than copied from each other. Measured on the tree at
# the commit that added them:
#
#   * The first name was SCRUBBED (#2374 scrubbed the tree, #3135 the history).
#     Its tree-wide count is zero BY CONSTRUCTION, so the whole contiguous name
#     is a safe pattern and ``test_no_tracked_file_carries_the_name`` can pin
#     the population at zero.
#   * The second name is NOT scrubbed and cannot be: this repository ships a
#     tracked demo profile for that persona, names its customization repo in a
#     clone URL an operator has to run, and records its catalog INDEX names in
#     measurement docs, docstrings and test fixtures. Measured on ``main`` at
#     ``84af9144``, over 4,465 tracked, present, non-binary files (the gate's
#     own five excluded): the three-letter abbreviation occurs on **172**
#     lines. These figures are ANCHORED to that commit on purpose — they exist
#     to show why a substring rule is unusable, not to track ``main``, and a
#     number that silently drifts is worse than one that names its tree. Of those, **103**
#     refer to the retailer through one of the artifact spellings this
#     repository sanctions, and **69** are ordinary camelCase spans (a terms
#     clause, a synonyms count, an npm-scripts helper, a WebAssembly
#     toolchain name) that a substring rule would red forever.
#
# So the second registrant's rows match the company's own NAME — the
# abbreviation, a separator, and the word(s) that follow it in the company's own
# prose — and nothing else. (That was #9247's decision. Since #10626 a third
# industrial row also matches the abbreviation on its own; see below.) That is
# the form a PR title, a PR body, a commit
# subject or a code comment uses when it says core was written FOR this
# retailer, which is the inference CONTRIBUTING.md "Generalize, don't fork per
# customer" protects against. Measured tree-wide, the two rows together matched
# **2** lines before this landed — both of them the PROSE row, a comment and a
# description string in the demo profile, removed in the same PR — and **0**
# after. The FORMAL row matched **0** before and after: it is registered for the
# spelling a leak would use, not for one the tree ever carried.
#
# WHY THE FORMAL ROW CARRIES THE THIRD TOKEN, decided deliberately rather than
# inherited. Its first draft stopped at the abbreviation plus the persona's
# sector word, and that is a COLLISION rather than a name: both halves are
# spellings this repository sanctions. The abbreviation on its own is the demo
# profile NAME an operator types (11 lines then; a row of its own since #10626),
# and the sector word is the tree's own adjective for this persona — it is in
# the ROW LABELS here, in the demo profile's own description, and in the
# directory names the nested-measurement work is producing now. Measured, that
# draft HARD-BLOCKED, with no escape hatch, on:
#
#     ## The <abbr> <sector> / MRO catalog                            RED
#     docs/measurements/<abbr>-<sector>/result.json                   RED
#     fix(engine): repoint the <abbr> <sector> demo onto end state A  RED
#     <ABBR>_<SECTOR>_TENANT = "x"                                    RED
#
# and the tree already pairs the two tokens with words between them on 5 lines
# in 4 files at ``84af9144``. On this branch a literal re-measure gives 4 lines
# in 4 files: 2 of the original 5 are the demo-profile prose this PR removes,
# and this file's own test module contributes one — so the figure is 3 OUTSIDE
# the gate's own files and 4 including them, and the exclusion is stated rather
# than folded into the arithmetic. One of them
# (``docs/measurements/nested-parity-oracle/README.md``) says "repoints the
# <sector> deployment onto end state A", which is the third line above minus one
# word. Anchored to its commit for the same reason the census figures are: it is
# exactly the kind of number the next measurement doc changes. A hard block one adjective away from a phrase the repository writes
# about itself is the guard that gets muted, which is the whole reason the
# distribution above was measured before a pattern was chosen. So the row is the
# company's REAL formal name, three tokens, which clears every line above.
#
# SINCE #10626 THE ABBREVIATION IS A ROW OF ITS OWN, so each line above that
# carries it reds on that row. The third token no longer decides WHETHER such
# a line reds; it decides only which row reports a full formal name.
#
# THE COST, as #9247 recorded it: the company's name carrying the sector word
# and NO third token was left to no row. Since #10626 the abbreviation row reds
# it, so that cost is no longer paid; the PROSE row still catches the company's
# ordinary name.
#
# AND THE THIRD TOKEN DOES NOT END THE COLLISION — IT MOVES IT ONE WORD OUT.
# Disclosed rather than fixed, because narrowing further would stop matching the
# company's actual formal name. The sector word and the third token are ALSO
# this repository's own compound adjective: ``docs/si/11`` is a tracked,
# ``docs/README.md``-linked document titled after it, and 8 tracked lines in 5
# files pair the two words (measured at ``84af9144``). Those 8 do NOT red — none
# carries the abbreviation — but a line that adds it does, with no escape hatch:
#
#     docs/measurements/<abbr>-<sector>-<tail>/result.json            RED
#     ## The <abbr> <sector>-<tail> catalog                           RED
#     the <abbr> <sector> <tail> chain demo is unaffected             RED
#
# ACCEPTED, because each of those does literally spell the company's full formal
# name, which is what this row is for. The escape is to name a slug or a heading
# after the CATALOG rather than the company, exactly as ``docs/si/11`` does.
# ``TestIndustrialRetailerFormalRowCollision`` pins these three as RED on
# purpose, so the cost is visible rather than discovered by whoever trips it.
#
# WHAT THESE ROWS DELIBERATELY DO NOT COVER — stated because this family is a
# character class, not a proof, and a green from it must not be read as "this
# PR does not name the industrial retailer":
#
#   * The CONTIGUOUS single-token spelling (abbreviation immediately followed
#     by the second word, no separator). That is the sister repo's own name,
#     and it occurs on 36 tracked lines at ``84af9144`` — production docstrings citing
#     ``elastic/prism-<retailer>#14``, the demo profile's clone URL, fixture
#     filenames, CHANGELOG prose. A row matching it would hard-block ordinary
#     work with no escape hatch. It is uncovered ON PURPOSE.
#   * The abbreviation inside a camelCase or PascalCase identifier
#     (``catalog<Abbr>Index``) or touching a digit (``<abbr>2``). The
#     abbreviation row below bounds the abbreviation by non-alphanumerics, and
#     the row is compiled case-insensitively, so it cannot tell a case change
#     from a word interior.
#   * A name split ACROSS LINES. Every surface here is scanned line by line.
#   * Any retailer that is not a registrant. This is a registry of named
#     customizations, not a retailer- or brand-name scan (see the scope
#     paragraph above), and the next customization to land will be invisible to
#     it until someone appends a row —
#     ``TestCustomerNameCoverageOfShippedCustomizations`` is what forces that
#     decision to be MADE and written down rather than skipped.
#
# THE BARE ABBREVIATION IS A ROW OF ITS OWN (#10626), and the reason it was not
# one before has gone. #9247 left it uncovered because the tree shipped it as
# the demo profile NAME an operator typed, as an identifier segment, and as an
# index-name segment (``catalog_<abbr>_<date>``): 9 + 11 + 41 lines, and a hard
# block on a served index name is a guard somebody mutes. #9922 retired the demo
# profile. The customization repo then renamed its package, its index names and
# its namespace prefix away from the abbreviation. Measured on ``main`` at
# ``7256b81cf``, the abbreviation bounded by non-alphanumerics occurs on 0
# tracked lines. So nothing sanctions it any more, and it leaked: a sister issue
# quoting an old index name would have carried it into 4 tracker titles
# (#10571), past every surface of this gate.
#
# The row matches the abbreviation as a whole word and as a segment of a
# snake_case, kebab-case or dotted identifier (``_<abbr>_``, ``-<abbr>-``,
# ``<abbr>_``, ``.<abbr>``), in any casing. It does not match inside a longer
# word: the lookarounds refuse an alphanumeric on either side. They are spelled
# ``[^\W_]`` rather than as a class with a letter range because the
# sister-tracker reconciler (#10571) widens every row by rewriting each letter
# of its source, and a range such as ``A-Z`` would become an invalid one; an
# escape survives that rewrite. ``[^\W_]`` is Unicode-alphanumeric, so an
# accented letter beside the abbreviation also suppresses a hit. Every line that
# carries the company's prose or formal name therefore also reds on this row,
# and the multi-token rows decide only which name the report says. That
# includes the sector-word spelling with no third token, which the formal row
# leaves out on purpose (argued above).
#
# COLLISIONS, measured so the false-positive cost is a number. In this tree:
# 0 lines. In the installed Python dependencies: 13 files, all of them one
# vendor's C compiler-version macro (``_<ABBR>_VER``) in C sources and headers,
# or a syntax highlighter's alias and file extension for a message-sequence-chart
# language. The installed npm dependencies have 1 line, the same highlighter
# alias. Outside code, the abbreviation is also a university degree and a Windows
# management-console file extension. A PR that vendors C headers, or that quotes
# either of those words, will red with no escape hatch. The remedy is to keep
# that text out of the diff.
#
# NOT A SHARED DERIVATION, and that is a judgement rather than a default. The
# two registrants share the SCANNERS (:func:`scan_for_customer_names`,
# :func:`scan_text_for_customer_names`), the compile step, the report and the
# hard-block verdict — one implementation, no mirror. What they do not share is
# a pattern BUILDER, and the decisive reason is that a builder would have to
# ERASE the difference measured above: one row is a whole scrubbed name, the
# others are a deliberately narrow multi-token pair chosen against a 172-line
# distribution and against a collision with this repository's own vocabulary,
# plus one bounded single token. A helper that turned a name into a class could
# not express "and then stop", which is the entire content of the pair.
#
# A weaker second reason is recorded as weaker on purpose: a builder taking the
# literal name would put that literal in this source, which #3135 forbids. It is
# not decisive, because a builder COULD take codepoints instead — this family's
# own tests construct both names that way — so the argument rests on the
# paragraph above, not on this one. Two rows that are genuinely different data,
# in one registry, read by one scanner, is the shape that carries no duplicate
# derivation.
# THE REGISTRANT MAP, and why a second structure earns its place (#9247
# review). The rows above are patterns; the facts the PROSE about this family
# keeps getting wrong are about the REGISTRANTS behind them — how many there
# are, and whether each one's name was scrubbed from the tree. Three rounds of
# review found four stale sentences asserting "one name" or "a registry of
# scrubbed names", each true before the second registrant landed and false
# after, in four different files. Correcting a copy does not end that; giving
# the fact ONE home that a test can read does.
#
# ``scrubbed`` is the load-bearing field and it is not a synonym for "guarded".
# The grocery registrant was removed from the tree (#2374) and from the history
# (#3135), so its tree-wide count is zero BY CONSTRUCTION. The industrial
# registrant is not scrubbed and cannot be: this repository ships its demo
# profile, its clone URL and its catalog index names on purpose. Both are
# guarded; only one is scrubbed, and a sentence that says otherwise is false of
# half the registry. ``TestNoProseHomeMisdescribesTheFamilysScope`` reads this
# map and refuses such a sentence in any tracked file that names this family.
CUSTOMER_NAME_REGISTRANTS: dict[str, dict[str, object]] = {
    "proprietary-grocery": {
        "rows": ("proprietary-retailer",),
        "scrubbed": True,
    },
    "industrial": {
        "rows": (
            "industrial-retailer",
            "industrial-retailer-formal",
            "industrial-retailer-abbr",
        ),
        "scrubbed": False,
    },
}


CUSTOMER_NAME_SPECS: list[tuple[str, str]] = [
    ("proprietary-retailer", r"[mM][uU][sS][gG][rR][aA][vV][eE]"),
    ("industrial-retailer", r"[mM][sS][cC][ _-]+[dD][iI][rR][eE][cC][tT]"),
    (
        "industrial-retailer-formal",
        r"[mM][sS][cC][ _-]+[iI][nN][dD][uU][sS][tT][rR][iI][aA][lL][ _-]+[sS][uU][pP][pP][lL][yY]",
    ),
    ("industrial-retailer-abbr", r"(?<![^\W_])[mM][sS][cC](?![^\W_])"),
]


# ---------------------------------------------------------------------------
# Dual-derivation freeze registry — the #3022 baseline+freeze guard.
#
# The codebase's single most recurrent bug class is DUAL DERIVATION OF ONE
# TRUTH: client / response-assembly code that RE-DERIVES a fact the Engine's
# response or emit already carries, instead of reading it (or extending the
# emit to carry it). It was fixed once per named instance and REGREW — the
# facet sidebar's ``collect_policy_*`` sidecars regrew AFTER the #1932 chip
# single-source cutover (#3004, RETIRED: the sidecar family is deleted and the
# sidebar reads the ``active_filters`` emit; its rules (a)/(c)/(c-wire) were
# dropped from this registry in the same PR); a TypeScript analyzer-fold
# mirror duplicated the Engine ``keyword_normalizer`` fold cross-language
# (#3006, RETIRED: the Engine now stamps an opaque ``fold_key`` and the mirror
# is deleted — rule (b) dropped in the same PR); a debug verdict mirror
# duplicates the engine's fold verdict (#3011). Fixed-once is not prevented. See
# ``contributing/single-source-of-truth.md`` § "Recurrence casebook" and the
# CONTRIBUTING_REVIEW.md checklist item #1 ("does this DERIVE a fact the
# Engine emit already carries?").
#
# This family is a BASELINE + FREEZE and differs from the three families above
# in its CLEARING mechanism:
#
#   - It is a HARD block, like the customer-name guard: a PR-body justification
#     block does NOT clear a hit. The reviewable escape hatch is editing the
#     ALLOWLIST itself (below) — a deliberate, diff-visible act a reviewer signs
#     off on — not a pasted block. That is what makes it a FREEZE: the pattern
#     may not SPREAD to a NEW file, while the existing (tracked-for-removal)
#     sites stay green until their cleanup issue deletes them.
#   - Each spec carries an ALLOWLIST of the files permitted to contain the
#     pattern TODAY (the current sites, derived by ``git grep`` on ``main``)
#     plus a categorical test exemption. A hit in any OTHER file fails the job
#     with a teaching message pointing at the emit to read / extend.
#   - Each spec names the ISSUE that RETIRES it. When that cleanup lands and
#     deletes the last site, drop the spec (and its allowlist) in the same PR —
#     each rule is independently removable.
#
# Patterns are compiled CASE-SENSITIVELY (unlike the IGNORECASE families
# above): these are exact-cased code identifiers, and case-insensitive
# matching would collide with legitimately-cased sibling names (the retired
# rule (c) demonstrated it: an insensitive ``policyFacetValues`` would have
# tripped on the shared helper name ``mergePolicyFacetValues`` — whose USE was
# the CORRECT single-source pattern, not a violation).
#
# The parity test ``tests/test_audit_grep_diff.py::TestFrozenDerivationParity``
# pins the label + regex of every spec against the CONTRIBUTING.md
# ``frozen-derivation-guard`` table so the doc and the gate cannot drift.
# ---------------------------------------------------------------------------

# Categorical test exemption shared by every frozen rule. Tests legitimately
# name these internals — a test that pins the ABSENCE of a re-derivation, or
# fixtures the builder shape, must be able to reference the identifier. Same
# precedent as the scoped family's ``__tests__`` / ``*.test.*`` / ``*.spec.*``
# exemption (and the Python suite lives under ``tests/``).
_FROZEN_TEST_ALLOWLIST: tuple[str, ...] = (
    "tests/**",
    "search-ui/src/**/__tests__/**",
    "search-ui/src/**/*.test.*",
    "search-ui/src/**/*.spec.*",
    "search-ui/test/**",
)


@dataclass(frozen=True)
class FrozenDerivationSpec:
    """One frozen dual-derivation pattern (#3022).

    ``label``     — echoed in the report; the ``frozen-derivation-guard``
                    doc-table key.
    ``regex``     — grep pattern; compiled CASE-SENSITIVELY.
    ``allowlist`` — ``fnmatch`` globs of files permitted to contain the pattern
                    TODAY (the current sites + the categorical test exemption).
                    A hit OUTSIDE the allowlist HARD-fails the job.
    ``retires``   — the cleanup issue that deletes this spec when it lands.
    ``teaching``  — one-line operator-facing reason: which emit to read instead.
    """

    label: str
    regex: str
    allowlist: tuple[str, ...]
    retires: str
    teaching: str


# The registry is currently EMPTY: all four founding rules are retired, each in
# the PR that deleted its frozen duplication (the by-design clearing mechanism —
# each rule is independently removable).
#
#   * Rules (a)/(c)/(c-wire) — the ``collect_policy_*`` sidecar family and its
#     builder-internal / wire-name reads — retired by #3004 (the family is
#     deleted; the sidebar reads the ``active_filters`` emit).
#   * Rule (b) — the FE analyzer-fold mirror (``facetValueFoldKey(``) — retired
#     by #3006: the Engine stamps an opaque ``fold_key`` on every facet bucket
#     and ``active_filters`` entry, clients match by KEY EQUALITY, and the
#     mirror (plus its ``normalizeValue`` sibling) is DELETED. Reintroduction is
#     gated by the FE tripwire test
#     ``search-ui/src/features/search/utils/__tests__/foldMirrorRetired.test.ts``
#     (a source-tree grep, stronger than this diff-based gate for a fully
#     deleted name); the one sanctioned local fallback (``foldKeyFallback``,
#     for values that never cross the wire with a key) is parity-pinned to the
#     Engine fold by the shared ``fold-key-vectors.json`` fixture.
#
# The machinery stays: the next frozen dual-derivation adds a spec here plus a
# row in the CONTRIBUTING.md ``frozen-derivation-guard`` block (the parity test
# keeps the two in lockstep) — do not re-use a retired rule's letter.
#
# Rules (d) / (e) — the ``elastic_transport`` response-body unwrap (#6570).
# ------------------------------------------------------------------------
# The rule "the raw body of an ES response is on ``.body``; the response object
# is neither a ``dict`` nor a ``Mapping``" had been authored in three homes with
# three different fallbacks nobody chose. #6570 gave it ONE home
# (``prism_engine.es_response``) and moved five sites onto it; the modules still
# authoring it by hand are inventoried in #6607, which retires both rules.
#
# This is the standing-violation policy made mechanical, and it is what closes
# the hole the #6610 adversarial review found: a file-scoped test can only guard
# the files it names, so the pattern could spread to a NEW module with nothing
# red. These specs hard-block exactly that while the tracked sites stay green.
#
# TWO rules rather than one because the doc-table row format is
# ``label | regex`` — split on ``|`` — so a spec regex cannot contain an
# alternation. Rule (d) uses ``attr\(`` rather than ``getattr\(`` so it covers
# the ``hasattr`` spelling in the same pattern: that is not hypothetical, it is
# the spelling the #6610 review used to defeat the first, ``getattr``-only
# detector while re-authoring a complete local copy of the rule.
#
# What these DON'T reach, stated so the gap is owned rather than assumed away:
# a body read that never names ``body`` at all — ``dict(resp)`` on an
# ``ApiResponse``, as the since-retired (#9504) typed-groups migration script did —
# is not greppable without matching every ``dict(...)`` in the tree. It is in
# #6607's inventory; it is not frozen here.
FROZEN_DERIVATION_SPECS: list[FrozenDerivationSpec] = [
    FrozenDerivationSpec(
        label="es-response-body-attr",
        regex=r'attr\([^)]*"body"',
        allowlist=(
            # THE HOME. Not tracked debt — this is the one authored copy, and it
            # stays after #6607 retires the rest.
            "packages/prism-engine/src/prism_engine/es_response.py",
            # Tracked debt, all annotated #6607. ``rewrite/__init__.py`` was here
            # until #6853: its one hand-authored unwrap fed the percolate's
            # ``took`` read, that read now takes the body the single home already
            # validated, and the file matches this pattern nowhere — an allowlist
            # entry for a clean file is an exemption nobody is using and a
            # standing invitation to re-author the rule there.
            "packages/prism-engine/src/prism_engine/es_helpers.py",
            "packages/prism-engine/src/prism_engine/rewrite/analyzer_drift.py",
            "packages/prism-engine/src/prism_engine/rewrite/index_resolution.py",
            "packages/prism-engine/src/prism_engine/rewrite/legacy_extract_value_check.py",
            "packages/prism-studio/src/prism_studio/search/elser_contributions.py",
            "tools/pool-chaos/run_chaos.py",
            *_FROZEN_TEST_ALLOWLIST,
        ),
        retires="#6607",
        teaching=(
            "read the body through prism_engine.es_response "
            "(read_es_body / require_es_body / read_es_count), never by hand"
        ),
    ),
    FrozenDerivationSpec(
        label="es-response-body-isinstance",
        regex=r"isinstance\([A-Za-z_][A-Za-z0-9_.]*\.body\b",
        allowlist=(
            "packages/prism-studio/src/prism_studio/data/cli_validate.py",
            "packages/prism-studio/src/prism_studio/data/_es_mapping_inspect.py",
            *_FROZEN_TEST_ALLOWLIST,
        ),
        retires="#6607",
        teaching=(
            "read the body through prism_engine.es_response "
            "(read_es_body / require_es_body / read_es_count), never by hand"
        ),
    ),
]


# ---------------------------------------------------------------------------
# GATE A — the provenance gate for the facet row's disclosure strings (#7162)
#
# ``specs/7043-facet-row-disclosure-strings.md`` §7.1 states the rule:
#
#   "Every user-visible string of the facet row disclosure surface is a field of
#    the per-value emit, composed in prism_studio/search/facets/marginal.py, and
#    rendered verbatim. The client owns none of them."
#
# §7.1 measures that rule 12/18 TRUE today, and the six client-composed strings
# it names — S7 (the depth-pill title), S9 (the ``+`` control), S10 (the ``−``
# control), S13 (the rung row title — retired by #9747), S17 (the covered-descendant cue) and the
# S8 fallback — are exactly where FOUR of #7043's seven issues live. That is not
# a coincidence: a string the producer cannot SEE is a string no producer-side
# fix can correct, which is why #6999 could fix ``count_aria_label`` and leave
# ``pillTitle`` stating a different removal on the same row.
#
# WHY THIS IS SEPARATE FROM GATE B, and why neither is worth having alone.
# §7.3 states it in one sentence: "Gate A alone would pass today's surface if
# every literal were moved producer-side unchanged and all of them were wrong.
# Gate B alone would pass a new client-side literal it never sees." Gate B is
# ``tests/test_search/test_facet_row_disclosure_strings_7043.py``; it drives the
# PRODUCER path and is structurally blind to a string the client composes.
#
# THE ANCHOR IS A COMPOSITION, NOT AN ATTRIBUTE. The rule reads on "a title=, an
# aria-label=, or JSX text", but an attribute anchor cannot see the composition:
# every one of the six is written ``title={pillTitle}`` with the prose assembled
# lines earlier, and a diff gate reads one line at a time. So the anchor is the
# COMPOSITION ITSELF — an interpolation sitting next to prose, so it is being
# read as a sentence rather than as a ``data-test-subj`` or a CSS length.
# Measured on the tree at the time this landed: 60 lines in scope and zero
# surviving false positives. That is a fact about TODAY'S TREE, not a property of
# the patterns: what keeps the two surviving non-prose shapes out — a COMMENT
# about a string, and a CSS length in a property position — is the scanner-side
# rule registry below, not the regexes. A test id, a class name, a log line and a
# thrown message are NOT exempted and DO hit; see the registry's docstring for
# why an exemption for a shape nobody writes is worse than the hit.
#
# WHAT IT DELIBERATELY DOES NOT REACH, so the gap is owned rather than assumed
# away:
#   * a CONSTANT literal with no interpolation ("Search categories", "Show
#     less"). It composes nothing and states no row fact; gating it would put
#     panel chrome in a row-disclosure rule and produce the noise that gets a
#     gate switched off.
#   * a composition spelled so the prose and the interpolation never share a
#     line, or assembled by ``.join`` / ``concat`` rather than a template
#     literal. Gate B is the behavioural net under this one for anything the
#     producer emits; a client string neither reaches is the residual, and it is
#     the reason §7.1's real remedy is MOVING these strings producer-side rather
#     than grepping for them.
#   * a NEW module in this directory whose name matches none of the globs.
#     ``rowDisclosureStrings.ts`` is invisible to BOTH layers — the diff scan
#     because it is out of scope, the census because it only walks in-scope
#     files. Closing it needs the whole ``components`` directory, measured at 86
#     unrelated lines, so it is OWNED here rather than closed: the name-shaped
#     scope makes the escape "call the file something else", and a reviewer
#     seeing a new file is the control for that. It is NOT a claim that the glob
#     cannot be dodged.
#   * a new shopper string written on a line that already carries an allowlisted
#     anchor IN THAT ANCHOR'S OWN FILE. Path-pairing narrowed this from "any file
#     in scope" to "the one module"; it does not remove it.
#   * a shape that is not shopper prose and is not exempted either — a
#     ``console.log``, a thrown message, a prose-spelled test id. Measured: no
#     such line exists on this surface, and an exemption for a shape nobody
#     writes buys nothing while costing an unconditional, path-unscoped hole.
#   * a shopper sentence sharing ONE LINE with an exempt construct, because every
#     rule in the registry is line-scoped. See that registry's note for the two
#     shapes that survive the ``^[^<>]*`` narrowing.
#   * anything outside the facet row surface.
#
# THE ALLOWLIST IS A CENSUS, AND THAT IS THE POINT. #7162 asks for an allowlist
# "naming each of the six client-composed strings that survive, so adding a
# seventh is a red build". It names those six by their ANCHOR — a stable
# fragment of the string itself — and, beside them, every other client-composed
# string the same scan finds today, each with the surface it draws and why it
# has not moved. A NEW composition matches no anchor and HARD-fails, exactly
# like the frozen family: the reviewable escape hatch is editing this list, not
# a pasted justification block.
#
# Anchors are matched against the HIT LINE, not the file, which is what makes
# "a seventh string" different from "a seventh line of an existing string". A
# REWORD that keeps the anchor stays green — §7.5 is explicit that this family
# does not adjudicate wording — while a new sentence needs a new entry.
# ---------------------------------------------------------------------------

#: The facet row disclosure surface. §7.3 names two component globs; this is wider on one
#: axis and the widening is measured. #6794 moved the client-composed sentences into
#: ``facetIncludeAffordanceCopy.ts``, and §2.1's own correction records that the move
#: *"does not change §7.1's 12/18 count — they are still client-composed"*. A glob that
#: named those four files, or even ``facet*Copy.ts``, would be escapable by naming the next
#: one ``rowDisclosureCopy.ts``: "escape by moving one directory over" becomes "escape by
#: renaming the file". So the scope is every facet-surface module in that ONE directory.
#:
#: THE COST, MEASURED AGAINST THE CONFIGURATION THAT SHIPS — narrow 53 lines, shipped 60,
#: so the widening costs **seven**, across FOUR files (``NumericRangeFacet.tsx``,
#: ``PriceRangeFacetBlock.tsx``, ``ResizableFacetSidebar.tsx``, ``facetSidebarHelpers.ts``),
#: every one a real client-composed string on a facet surface and all four already carried
#: by the allowlist. Widening further, to every ``.ts``/``.tsx`` in ``components``, costs
#: **86** and is rejected: a rule that reds on unrelated work is a rule that gets switched
#: off.
#:
#: ⚠️ RE-MEASURE THESE WHENEVER ANY INPUT TO THEM CHANGES — a GLOB, a PATTERN, **or a SKIP
#: RULE**. Both numbers have now been stale once, each time for a different reason and each
#: time in a paragraph that told the reader to re-measure:
#:   * "three" and "79" were the cost of the TWO-WORD arms alone, taken before the one-word
#:     and JSX arms were added and never re-measured when they were;
#:   * "85" was correct against the EIGHTEEN-token skip list and was written into the same
#:     commit that cut that list to two. One line moves: ``ScoreCompareFlyout.tsx:76``
#:     carries ``padding`` inside an inline style STRING, which the deleted ``padding``
#:     token exempted and the two-rule registry does not. 85 → 86.
_FACET_ROW_DISCLOSURE_GLOBS: tuple[str, ...] = (
    "search-ui/src/features/search/components/*Facet*.tsx",
    "search-ui/src/features/search/components/*Facet*.ts",
    "search-ui/src/features/search/components/facet*.ts",
    "search-ui/src/features/search/components/*Copy.ts",
    "!**/__tests__/**",
    "!**/*.test.*",
    "!**/*.spec.*",
)


@dataclass(frozen=True)
class NonVisibleLineRule:
    """One shape of line whose literal is NOT something a shopper reads.

    A registry rather than a token list, and every entry is held to the SAME standard the
    allowlist anchors are: it must be load-bearing on the tree, which
    ``TestClientComposedStringSkipList`` proves by removing it and requiring a new hit.

    That test is the mirror of ``test_every_allowlist_anchor_clears_something_on_the_tree``,
    and it exists because the first cut of this family did not apply its own reasoning to
    itself. That list held EIGHTEEN entries; measured over all 36 in-scope files and 17,960
    lines, removing one at a time, exactly TWO prevented a false positive. The other
    sixteen — ``className``, ``key={``, ``id={``, ``data-test-subj``, ``console.``,
    ``throw new``, ``padding``, ``margin`` and the rest — prevented nothing and were
    unconditional, path-unscoped exemptions. Two of them (``className`` and ``key={``) were
    the most idiomatic spellings of a facet ROW, which comes out of a ``.map()``:

        {rows.map((r) => <li key={r.value}>{r.removed} products removed</li>)}

    is a seventh client-composed string, and the exemption made it green — undoing, in the
    same commit, the JSX closure the JSX patterns were added for. A dead exemption is not
    neutral; it is a standing invitation to write a new string on the line it names.
    """

    label: str
    regex: str
    why: str


#: The measured rules. TWO, because two is what the tree needs.
#:
#: The CSS rule is what the ``(?<![0-9])`` lookbehind does NOT cover: that lookbehind
#: defends against a LITERAL digit width (``1px solid ${colour}``) and an interpolated one
#: (``${width}px solid ${colour}``) has no digit to look behind. It is anchored to a
#: PROPERTY POSITION (``border:`` / ``borderLeft:`` / ``borderTop:``) rather than matching
#: the substring anywhere on the line, so it cannot exempt a sentence that merely mentions a
#: border. Measured: it is load-bearing on exactly four lines and every one is a border
#: binding in a style object.
#:
#: ⚠️ EVERY RULE HERE IS LINE-SCOPED, AND THAT IS A HOLE WITH A SHAPE. A line carrying BOTH
#: an exempt construct and a shopper sentence is skipped whole. This disclosure was written
#: once, deleted when the token list became this registry, and is restored here because the
#: hole did not go with it — the ``^[^<>]*`` prefix below narrows it, it does not close it.
#: What that prefix buys, measured at ZERO census cost: a JSX element carrying an inline
#: style AND text on one line —
#:
#:     <div style={{ borderTop: "1px solid #ccc" }}>{removed} products removed</div>
#:
#: — is a HIT again. It was green without the prefix, and a styled element with text on one
#: line is at least as idiomatic as the ``className`` case this family closed. What remains
#: exempt, and is owned rather than claimed closed:
#:   * a NON-JSX object literal carrying a ``border:`` and a shopper string on ONE line
#:     (``{ border: `1px solid ${c}`, title: `${n} products removed` }``);
#:   * a shopper string written on a line that OPENS like a comment (`` * const t = … ``),
#:     which the comment rule skips whole.
#: Both are measured reachable through the real CLI. Neither is on the tree.
CLIENT_STRING_NON_VISIBLE_RULES: tuple[NonVisibleLineRule, ...] = (
    NonVisibleLineRule(
        label="comment",
        regex=r"^\s*(?:/[/*]|\*)",
        why=(
            "a comment ABOUT a string is not the string — the same code-shape discipline "
            "the reconstruct*( family uses. Load-bearing on two lines today, and without "
            "it a PR that merely MOVED one of them was hard-blocked with a report telling "
            "its author to compose a comment in marginal.py"
        ),
    ),
    NonVisibleLineRule(
        label="css-border-property",
        regex=r"^[^<>]*(?:^|[\s,{(])border[A-Za-z]*\s*:",
        why=(
            "a CSS length in a style object is not shopper prose, and an INTERPOLATED "
            "width slips the (?<![0-9]) lookbehind. Anchored to the property position so "
            "it cannot exempt a sentence that merely says the word, and prefixed with "
            "^[^<>]* so it stops at the first angle bracket — a JSX element carrying an "
            "inline style AND text on one line is a HIT, which it was not before. The rule "
            "is still LINE-scoped: see the registry note above for the two shapes that "
            "remain exempt"
        ),
    ),
)

_COMPILED_NON_VISIBLE: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (rule.label, re.compile(rule.regex)) for rule in CLIENT_STRING_NON_VISIBLE_RULES
)


@dataclass(frozen=True)
class ClientComposedStringSpec:
    """One shape in which the client composes a user-visible string (#7162).

    ``label``    — echoed in the report; the ``client-composed-string-guard``
                   doc-table key.
    ``regex``    — grep pattern, compiled CASE-SENSITIVELY (these are prose
                   fragments, and a case-insensitive match would drag in
                   identifiers).
    ``globs``    — the scope, :func:`_scope_matches` semantics.
    ``teaching`` — one line: what to do instead.
    """

    label: str
    regex: str
    globs: tuple[str, ...]
    teaching: str


_CLIENT_STRING_TEACHING = (
    "compose it in prism_studio/search/facets/marginal.py and render the "
    "emitted field verbatim (specs/7043-… §7.1); the client owns none of "
    "these strings"
)

#: SIX shapes, not one, because a doc-table row is split on ``|`` so a spec regex cannot
#: carry an alternation (the constraint the frozen family records), and the prose can sit
#: either side of the interpolation in each of three syntaxes:
#:
#: * a template literal with TWO adjacent words — the original pair;
#: * a template literal with ONE word adjacent to the interpolation. Added after review
#:   measured ```${removed} products``` and ```Removes ${removed}```
#:   walking straight through the two-word rule. Measured cost on this surface: 20
#:   additional lines, of which four were CSS ``border`` bindings (now skipped as
#:   non-visible) and the rest are real client-composed strings — including
#:   ```Excluding ${valueSubject} …``` and ```Including ${subject}…```,
#:   which are ARMS OF S7 AND S9 the two-word rule was not seeing;
#: * JSX text with an interpolation — ``<span>{removed} products in the results</span>``,
#:   which #7162's acceptance names explicitly and which no template-literal pattern can
#:   see. Measured cost on this surface: ZERO additional lines today.
CLIENT_COMPOSED_STRING_SPECS: list[ClientComposedStringSpec] = [
    ClientComposedStringSpec(
        label="facet-row-string prose-then-value",
        regex=r"`[^`]*(?<![0-9])[A-Za-z]{2} [A-Za-z]{2}[^`]*\$\{",
        globs=_FACET_ROW_DISCLOSURE_GLOBS,
        teaching=_CLIENT_STRING_TEACHING,
    ),
    ClientComposedStringSpec(
        label="facet-row-string value-then-prose",
        regex=r"\$\{[^`]*\}[^`]*(?<![0-9])[A-Za-z]{2} [A-Za-z]{2}[^`]*`",
        globs=_FACET_ROW_DISCLOSURE_GLOBS,
        teaching=_CLIENT_STRING_TEACHING,
    ),
    ClientComposedStringSpec(
        label="facet-row-string word-then-value",
        regex=r"`[^`]*(?<![0-9])[A-Za-z]{3} \$\{",
        globs=_FACET_ROW_DISCLOSURE_GLOBS,
        teaching=_CLIENT_STRING_TEACHING,
    ),
    ClientComposedStringSpec(
        label="facet-row-string value-then-word",
        regex=r"\$\{[^`]*\} (?<![0-9])[A-Za-z]{3}",
        globs=_FACET_ROW_DISCLOSURE_GLOBS,
        teaching=_CLIENT_STRING_TEACHING,
    ),
    ClientComposedStringSpec(
        label="facet-row-string jsx-value-then-prose",
        regex=r">\{[^}]*\}[^<]*(?<![0-9])[A-Za-z]{2} [A-Za-z]{2}",
        globs=_FACET_ROW_DISCLOSURE_GLOBS,
        teaching=_CLIENT_STRING_TEACHING,
    ),
    ClientComposedStringSpec(
        label="facet-row-string jsx-prose-then-value",
        regex=r">[^<{]*(?<![0-9])[A-Za-z]{2} [A-Za-z]{2}[^<]*\{[^}]*\}<",
        globs=_FACET_ROW_DISCLOSURE_GLOBS,
        teaching=_CLIENT_STRING_TEACHING,
    ),
]


@dataclass(frozen=True)
class AllowedClientString:
    """One client-composed string that SURVIVES today, named so a seventh cannot.

    ``anchors`` are fragments matched against the hit LINE, and ``paths`` are the files that
    anchor may clear in. BOTH are required, and the pairing is the fix for a laundering hole
    review found in the first cut: with anchors alone, a generic fragment like
    ``"products with "`` cleared a NEW string in ANY file of the scope. Scoping each anchor
    to the module that authors its string leaves the laundering surface at "another string
    in the same file", which is stated rather than claimed closed.

    Anchors are chosen to be the part of the sentence a reword is least likely to touch,
    because the guarantee this family gives is about PROVENANCE and not about wording (§7.5).

    ``covers`` names the §2.1 ids this entry accounts for. It is separate from ``id``
    because one authoring can carry more than one inventory row — S7 and the S8 fallback are
    the same composition, S8 being the name that falls back to the title.
    """

    #: A short name for the surface. Not necessarily a §2.1 id — see ``covers``.
    id: str
    surface: str
    paths: tuple[str, ...]
    anchors: tuple[str, ...]
    why: str
    #: §2.1 inventory ids this entry accounts for, if any.
    covers: tuple[str, ...] = ()


_DROPDOWN = ("search-ui/src/features/search/components/FacetPerTierDropdown.tsx",)
_TOGGLES = ("search-ui/src/features/search/components/FacetValueToggleButtons.tsx",)
_TREE = ("search-ui/src/features/search/components/CategoryTreeFacet.tsx",)


#: The census. Every client composition the scan finds on this surface today, each with the
#: module that authors it, the surface it draws, and why it has not moved producer-side.
#: The §2.1 ids #7162's acceptance names come first.
CLIENT_COMPOSED_STRING_ALLOWLIST: tuple[AllowedClientString, ...] = (
    AllowedClientString(
        id="depth-pill title",
        surface="FacetPerTierDropdown.pillTitle, and the name that falls back to it",
        paths=_DROPDOWN,
        # #9747 — ``pillCountClause}.`` anchors the applied arm's line, which #9747
        # shortened when it removed the depth-choice clause from it; the composition
        # itself is unchanged and is still this entry's.
        anchors=(
            "at this value",
            "products removed",
            "products with ",
            "Excluding ",
            "pillCountClause}.",
        ),
        why=(
            "#7161 made it honest and left it client-composed; §7.1's P6/M5 move "
            "producer-side is #7162's open half and is not done there. The S8 fallback is "
            "this same composition — #7242 gave the covered include row the emitted short "
            "name and every other path still falls back to the title — so it is covered "
            "here rather than by an entry of its own. An earlier cut gave S8 a separate "
            "entry anchored on the IDENTIFIER ``onClickAriaLabel``, which cleared nothing "
            "on the tree and cleared a brand-new sentence written on that line."
        ),
        covers=("S7", "S8 fallback"),
    ),
    AllowedClientString(
        id="include affordance copy",
        surface="the `+` control's title and aria-label",
        paths=(
            "search-ui/src/features/search/components/facetIncludeAffordanceCopy.ts",
        ),
        anchors=("Include results with ", "Including ", "Remove inclusion of "),
        why="#6794 gave it one home; the home is still the client",
        covers=("S9",),
    ),
    AllowedClientString(
        id="exclude control titles",
        surface="the `−` control's title and aria-label",
        paths=_TOGGLES,
        anchors=("Exclude results with ", "Remove exclusion of "),
        why="an exclude always narrows, so #6794 left the wording alone — and client-side",
        covers=("S10",),
    ),
    # #9747 RETIRED S13, the depth-rung row title: the rungs are no longer a control
    # (ruled 2026-09-28), so the title that invited a pick ("Include at <tier> … click to
    # apply") and its "this tier ran … informational only" twin are gone, and the row's
    # visible text is its only statement. One client-composed string fewer.
    AllowedClientString(
        id="covered-descendant cue",
        surface="the *unavailable via <ancestor>* cue",
        paths=(
            "search-ui/src/features/search/components/facetExcludedViaAncestorCueCopy.ts",
        ),
        anchors=("unavailable via ",),
        why="#7227 gave it one authoring; that authoring is client-side",
        covers=("S17",),
    ),
    AllowedClientString(
        id="depth-name joiner",
        surface="the dropdown's *Best and Relevant* joiner",
        paths=_DROPDOWN,
        anchors=("} and ${",),
        why=(
            "a grammar joiner rather than a sentence; the producer authors the same joiner "
            "for its own depth names (``_join_depth_names``), which is the duplication "
            "§7.1's move would end"
        ),
    ),
    AllowedClientString(
        id="exclude-override gesture",
        surface="the exclude-override copy",
        paths=("search-ui/src/features/search/components/facetExcludeOverrideCopy.ts",),
        anchors=("Stop excluding ", "which matches "),
        why="composed beside S9/S10 and moves producer-side with them",
    ),
    AllowedClientString(
        id="row-state cue",
        surface="the out-of-scope cue",
        paths=("search-ui/src/features/search/components/facetRowStateCueCopy.ts",),
        anchors=("no impact (outside ",),
        why="a row-state cue with no emitted field to read; part of the P6/M5 move",
    ),
    AllowedClientString(
        id="count-cluster controls",
        surface="the count box's own include/exclude control names",
        paths=("search-ui/src/features/search/components/FacetValueCountCluster.tsx",),
        anchors=("Remove inclusion of ", "Remove exclusion of "),
        why="the same two control names as S9/S10, on the count box rather than the buttons",
    ),
    AllowedClientString(
        id="applied-split tooltip",
        surface="the per-tier split's unmeasured-contribution tooltip",
        paths=("search-ui/src/features/search/components/FacetAppliedBreakdown.tsx",),
        anchors=("contribution not measured for this tier",),
        why="#7349 moved the NUMBER producer-side and left this explanation behind",
    ),
    AllowedClientString(
        id="excluded-value panel",
        surface="FacetExcludedControl's panel copy",
        paths=("search-ui/src/features/search/components/FacetExcludedControl.tsx",),
        anchors=("products no longer shown", "click to see ", " is excluded"),
        why="a panel, not a row string; #7215 rules what it may say, not where it lives",
    ),
    AllowedClientString(
        id="per-tier chips",
        surface="FacetPerTierChips' tier and all-tier chip titles",
        paths=("search-ui/src/features/search/components/FacetPerTierChips.tsx",),
        anchors=(
            "} tier`",
            "result${",
            "click to soften",
            "click to harden",
            "hard-filtered here",
            "All tiers hard-filtered:",
            "click to re-harden",
        ),
        why="the merchandiser-facing chip strip, adjacent to the row and not on it",
    ),
    AllowedClientString(
        id="category-tree row cues",
        surface="CategoryTreeFacet's inline row cues and its pager",
        paths=_TREE,
        anchors=(
            "already included via ",
            "Excluded at ",
            "still shown: ",
            "Show more (",
            "Collapse ${",
            "Expand ${",
        ),
        why=(
            "three row cues, an expander pair and a pager. The ``Excluded at ${…path}`` "
            "cue prints a raw ADDRESS where the sentence beside it prints the "
            "``display_name`` off the SAME record — filed as #7760, and this anchor is "
            "deleted by the PR that fixes it. It is recorded in an issue and not only "
            "here: an allowlist entry reads as approved, not as a known bug."
        ),
    ),
    AllowedClientString(
        id="facet group chrome",
        surface="FacetBlock's group header, search box and show-more controls",
        paths=("search-ui/src/features/search/components/FacetBlock.tsx",),
        anchors=(
            "filter group",
            "no active filters.",
            "Show fewer ",
            "Show more ${",
            "Filter by ",
            "Expand group to edit.",
            "Clear ${",
            "Search ${",
            "Show ${",
        ),
        why=(
            "panel chrome naming the FACET, never a row's quantity. "
            "``Show more ${`` (#8094) is the WITHHOLDING arm of the ``Show ${`` "
            "control already anchored beside it — the same accessible name with its "
            "count dropped, on a facet whose bucket list the aggregation's ``size`` "
            "cap cut, where stating a remainder would assert a completeness nobody "
            "measured. Anchored on ``Show more ${`` and NOT on the bare "
            "``Show more ``: this entry's warrant is that the string states no "
            "quantity, and the loose form does not enforce that — measured, it clears "
            "a planted ``Show more — ${hiddenCount} of ${totalValues} values were "
            "hidden`` that ``main`` reds, so the anchor would launder the very class "
            "it is justified by. The tight form keeps the shipped line green and reds "
            "the plant. Nothing rests on the loose form: the sibling literal "
            '``"Show more"`` in the tree and the flat control is not composed and '
            "is not flagged."
        ),
    ),
    AllowedClientString(
        id="facet value-list fetch state",
        surface="FacetBlock's notices while a windowed facet's complete list loads or fails",
        paths=("search-ui/src/features/search/components/FacetBlock.tsx",),
        anchors=(
            "Loading more ${",
            "values could not be loaded.",
        ),
        why=(
            "#9357 — the state of a FETCH the browser made (in flight, or failed), "
            "which no producer can know: the server answered the search before the "
            "shopper pressed Show more. The one number it may carry, the withheld "
            "row count, is ``window.rows_total`` minus the shipped rows — the same "
            "server number the ``Show ${`` control states — and the failed arm drops "
            "it on a facet whose aggregation was cut (``buckets_truncated``), as the "
            "control does."
        ),
    ),
    AllowedClientString(
        id="range facet chrome",
        surface="the numeric and price range blocks' group labels",
        paths=(
            "search-ui/src/features/search/components/NumericRangeFacet.tsx",
            "search-ui/src/features/search/components/PriceRangeFacetBlock.tsx",
        ),
        anchors=("Filter ${", "filter group"),
        why="chrome on a range facet, which draws no marginal row at all",
    ),
    AllowedClientString(
        id="sidebar chrome",
        surface="the sidebar's summary helpers and its resize handle",
        paths=(
            "search-ui/src/features/search/components/facetSidebarHelpers.ts",
            "search-ui/src/features/search/components/ResizableFacetSidebar.tsx",
        ),
        anchors=("} more", "} pixels", 'isLowerBound ? "at least "'),
        why=(
            "panel chrome and one widget measurement; neither states a row quantity. "
            "``} more`` is the collapsed group's ``+N more`` tail over the ACTIVE "
            "values it enumerates (#1201/#1246) — a count of the names this line "
            "elided, not of documents. #9307 DELETED two anchors from this entry "
            "rather than leaving them: ``option${`` cleared the collapsed subtitle's "
            "``<n> option(s).`` plural template, which moved to the group HEADER as "
            "an un-composed ``(<n>)`` and is composed here no longer, and "
            "``Expand group to edit.`` cleared the tail that same change removed from "
            "every branch. The two did NOT survive the same way, and the difference is "
            "the whole demonstration (#9322): ``option${`` survives nowhere in either "
            "file — which is why the presence-in-file anchor test correctly redded on "
            "it — while ``Expand group to edit.`` survives here only as PROSE in the "
            "composer's docstring, and stayed GREEN on it. That second half is the "
            "state an anchor must not be kept alive by, so the audit now asks whether "
            "an anchor sits on a line the patterns HIT rather than whether the text is "
            "present; before that, a comment quoting retired copy held a dead anchor "
            "green and would have licensed the next composed string that happened to "
            "contain it."
            " #9307's own follow-up then ADDED one back, which is why this entry "
            "grows rather than only shrinks: the header count parenthetical is "
            "COMPOSED here now that the cut-short arm hedges it (``at least "
            "1,001``). The previous ``over `` spelling tripped nothing — the "
            "one-word specs need the word directly against the ``${``, and here the "
            "prose sits inside a ternary two tokens away, so only the TWO-word "
            "``prose-then-value`` shape reaches it. Anchored on "
            '``isLowerBound ? "at least "`` and NOT on the bare ``at least ``: the '
            "warrant is this ONE composition, and the loose form would clear any "
            "later sentence in either file carrying those two words. What it hedges "
            "is ``facet.buckets.length`` — the rows THIS response carries for the "
            "facet, drawn in the group HEADER beside the ``} more`` tail — so it "
            "states no row quantity either, and #7043's producer-side move would "
            "take it with the rest of this entry rather than separately."
        ),
    ),
)

_COMPILED_CLIENT_STRINGS: list[tuple[str, re.Pattern[str], tuple[str, ...]]] = [
    (spec.label, re.compile(spec.regex), spec.globs)
    for spec in CLIENT_COMPOSED_STRING_SPECS
]

_CLIENT_STRING_SPEC_BY_LABEL: dict[str, ClientComposedStringSpec] = {
    spec.label: spec for spec in CLIENT_COMPOSED_STRING_SPECS
}


def client_string_is_allowlisted(path: str, content: str) -> str | None:
    """The allowlist id clearing *content* in *path*, or ``None`` if nothing does."""
    for allowed in CLIENT_COMPOSED_STRING_ALLOWLIST:
        if not _path_in_allowlist(path, allowed.paths):
            continue
        if any(anchor in content for anchor in allowed.anchors):
            return allowed.id
    return None


def client_string_line_is_user_visible(
    content: str, rules: Sequence[NonVisibleLineRule] | None = None
) -> bool:
    """False when the line's literal is not something a shopper reads.

    *rules* is injectable so the load-bearing test can remove one and re-measure; callers
    pass nothing and get :data:`CLIENT_STRING_NON_VISIBLE_RULES`.
    """
    if rules is None:
        compiled = _COMPILED_NON_VISIBLE
    else:
        compiled = tuple((rule.label, re.compile(rule.regex)) for rule in rules)
    return not any(pattern.search(content) for _label, pattern in compiled)


def client_string_pattern_label(
    path: str, content: str, rules: Sequence[NonVisibleLineRule] | None = None
) -> str | None:
    """The spec label whose shape *content* matches in *path*, or ``None`` if none does.

    Everything :func:`scan_for_client_composed_strings` asks of a line EXCEPT the
    allowlist: the line must carry a string a shopper actually reads
    (:func:`client_string_line_is_user_visible`), its path must be in the matching spec's
    scope, and that spec's pattern must hit it.

    Split out rather than re-derived by the caller that needs it (#9322). The allowlist
    audit — ``test_every_allowlist_anchor_clears_something_on_the_tree`` — has to ask
    exactly this question of every anchor: does it sit on a line the patterns HIT, or
    merely somewhere in the file? Two walks that agree today are still a duplication; the
    third reader picks a fourth walk. This is the one walk, and the gate uses it too, so
    the audit cannot drift from what it is auditing.

    The distinction is not hypothetical. The ``comment`` rule in
    :data:`CLIENT_STRING_NON_VISIBLE_RULES` means a docstring QUOTING retired copy is not
    a line this returns a label for — which is what an anchor held alive by commentary
    about itself was clearing: nothing.
    """
    if not client_string_line_is_user_visible(content, rules):
        return None
    for label, compiled, globs in _COMPILED_CLIENT_STRINGS:
        if not _scope_matches(path, globs):
            continue
        if compiled.search(content):
            return label
    return None


def scan_for_client_composed_strings(
    added_lines: Iterable[tuple[str, int, str]],
    rules: Sequence[NonVisibleLineRule] | None = None,
) -> list[Hit]:
    """One :class:`Hit` per NEW client-composed disclosure string (#7162, §7.3).

    An added line is a hit when it matches a :data:`CLIENT_COMPOSED_STRING_SPECS` shape, its
    path is in that spec's scope, the line carries a string a shopper actually reads
    (:func:`client_string_line_is_user_visible`), and no
    :data:`CLIENT_COMPOSED_STRING_ALLOWLIST` entry clears that anchor IN THAT FILE. The
    first three of those four live in :func:`client_string_pattern_label`, which the
    allowlist audit reuses so that "a line the patterns hit" means one thing here.

    A HARD block, like the customer-name and frozen-derivation families: the reviewable
    escape hatch is adding an entry to the allowlist — a diff-visible act a reviewer signs
    off on — not a pasted justification block.

    *rules* overrides :data:`CLIENT_STRING_NON_VISIBLE_RULES` and exists so the
    load-bearing test can remove one and re-measure; production callers pass nothing.
    """
    hits: list[Hit] = []
    for path, line_no, content in added_lines:
        if client_string_is_allowlisted(path, content) is not None:
            continue
        label = client_string_pattern_label(path, content, rules)
        if label is None:
            continue
        hits.append(
            Hit(
                path=path,
                line=line_no,
                pattern_label=label,
                snippet=content.rstrip("\n"),
            )
        )
    return hits


def render_client_composed_string_report(hits: Sequence[Hit]) -> str:
    """Operator-facing failure report for a NEW client-composed row string."""
    lines = [
        "audit-grep client-composed disclosure string (#7162, specs/7043-… §7.3):",
        "a facet row surface has grown a user-visible string the PRODUCER cannot",
        "see.",
        "",
        "§7.1's rule: every user-visible string of this surface is a field of the",
        "per-value emit, composed in",
        "packages/prism-studio/src/prism_studio/search/facets/marginal.py, and",
        "rendered verbatim. Four of #7043's seven issues live in the six strings",
        "that still break it (#7119, PR #7049, #7140, #7161 — every one found by",
        "a human reading the panel, none by a gate).",
        "",
        "This is a HARD block — do NOT add a justification block. Instead:",
        "  - compose the string in marginal.py and render the emitted field",
        "    verbatim, which is what makes it reachable by Gate B",
        "    (tests/test_search/test_facet_row_disclosure_strings_7043.py); or",
        "  - if this is a REWORD or a move of one of the strings already named,",
        "    keep its allowlist anchor on the line, or update the anchor in",
        "    .github/scripts/audit_grep_diff.py in THIS PR — a reviewable,",
        "    diff-visible act.",
        "",
        "New client-composed strings:",
    ]
    for hit in hits:
        spec = _CLIENT_STRING_SPEC_BY_LABEL.get(hit.pattern_label)
        lines.append(f"  {hit.path}:{hit.line} {hit.pattern_label}    {hit.snippet}")
        if spec is not None:
            lines.append(f"      -> {spec.teaching}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Text-surface names. These two strings are BOTH the human label a report
# prints in place of a file path AND — for the justification-gated family —
# the surface token a PR-body justification block must name
# (``Hit: <commit-messages> <label>``). They are constants rather than inline
# literals so the scan, the report and the justification parser cannot drift
# into three spellings of one surface.
#
# The angle brackets are deliberate: no real repository path looks like this,
# so :func:`parse_text_justifications` can tell a surface token from a path
# with no ambiguity, and a text-form ``Hit:`` line can never be mistaken for a
# diff-form one.
# ---------------------------------------------------------------------------
TEXT_SURFACE_COMMITS = "<commit-messages>"
TEXT_SURFACE_PR = "<pr-title-and-body>"

#: Accounts whose PR body carries upstream release notes the account did not
#: write (#11227). The login comes from the API (``--pr-author``), never from the
#: branch name, which a person can choose. ``[bot]`` cannot be registered by a
#: person, and ``app/`` is how ``gh`` spells an app's login.
BOT_AUTHOR_LOGINS: frozenset[str] = frozenset({"dependabot[bot]", "app/dependabot"})

_DETAILS_TAG = re.compile(r"<(/?)details(?![\w-])[^>]*>", re.IGNORECASE)


def strip_bot_quoted_blocks(body: str, author: str) -> str:
    """``body`` without the bot's quoted ``<details>`` blocks, for a bot author (#11227).

    A person's body is returned unchanged. For an author on
    :data:`BOT_AUTHOR_LOGINS` only a BALANCED, outermost ``<details>``...
    ``</details>`` pair is removed (nested pairs go with their parent). An opener
    that is never closed, and a stray closer, exempt nothing: the text after an
    unclosed opener stays judged.
    """
    if author not in BOT_AUTHOR_LOGINS:
        return body
    spans: list[tuple[int, int]] = []
    open_starts: list[int] = []
    for match in _DETAILS_TAG.finditer(body):
        if not match.group(1):
            open_starts.append(match.start())
        elif open_starts:
            start = open_starts.pop()
            if not open_starts:
                spans.append((start, match.end()))
    pieces: list[str] = []
    cursor = 0
    for start, end in spans:
        pieces.append(body[cursor:start])
        cursor = end
    pieces.append(body[cursor:])
    return "".join(pieces)


# ---------------------------------------------------------------------------
# EXIT STATUS — three values, not two (issue #7647)
# ---------------------------------------------------------------------------
# ``0`` — the scan ran and nothing was reported.
# ``1`` — the scan ran and something BLOCKS. The hits are listed.
# ``4`` — the scan ran, nothing blocks, and one or more ADVISORIES survived
#         that the caller MUST surface to its author.
#
# Why the third value exists. ``--text-tripwires-advisory`` (#5645) downgrades a
# text-surface hit to a WARNING for the one caller that has no PR body to justify
# against, ``scripts/preflight.sh``. That downgrade is correct, and it made the
# warning INVISIBLE: preflight's ``run_gate`` renders every exit-0 gate as a bare
# ``PASS`` and discards the log, so the warning whose own words are "resolve it
# now to avoid a red CI" was written to a temp file and deleted. Preflight
# attested green; CI then hard-blocked the same commit message; the remedy by
# then is a history rewrite — the exact loop #5645's rationale exists to prevent
# (#7647).
#
# A caller cannot re-derive "there were advisories" from the report text without
# grepping this script's prose, which is the kind of derived fact this repo
# forbids (CONTRIBUTING.md: read the emit, never re-derive it). So the STATUS
# carries it.
#
# WHY 4, AND NOT 3. A first revision of this chose 3 and argued that "two
# scripts in this tree must not spell two different meanings with one number" —
# an argument that was correct and, as written, FALSE, because three surfaces
# already spell 3 as very nearly the OPPOSITE of this:
#
#   .github/scripts/check_closing_keywords.py — "exit 3: the gate could not scan"
#   .github/scripts/check_review_verdict.py   — "exit 3: the gate could not judge,
#                                                and this is never reported as clean"
#   .github/workflows/audit-grep.yaml         — exit 3 when the diff could not be
#                                                READ; "nothing was scanned" —
#                                                inside the audit-grep job itself
#
# ``run_gate_advisory`` maps this status to a NON-BLOCKING warning, so a script
# meaning "I could not judge" run through it would have reported green: the next
# stand-in, pre-installed by the fix for the last one. 2 is likewise taken twice
# over — argparse's own usage-error status, and check_proprietary_data.py's "the
# scan did not run" (#7469's doctrine). 4 is unclaimed, and
# ``tests/test_preflight_gate_verdict_scope_7085_7647.py`` keeps it that way by
# requiring every script preflight runs through ``run_gate_advisory`` to DECLARE
# this constant with this value.
#
# Only a caller that passed ``--text-tripwires-advisory`` can ever see it, so CI
# and the commit-msg hook are unaffected: their verdicts stay 0/1.
ADVISORY_EXIT_STATUS = 4

# ``3`` — THE GATE COULD NOT SCAN (issue #9225). Not a content verdict: the
# surfaces this gate was asked to judge did not arrive in a shape it can vouch
# for, so it refuses to publish one rather than reporting the green that an
# unread surface always produces.
#
# 3 is not a new meaning invented here. It is already this repository's spelling
# of exactly this, in three places, and one of them is the job that runs this
# script:
#
#   .github/scripts/check_closing_keywords.py — "exit 3: the gate could not scan"
#   .github/scripts/check_review_verdict.py   — "exit 3: the gate could not judge,
#                                                and this is never reported as clean"
#   .github/workflows/audit-grep.yaml         — exit 3 when the diff could not be
#                                                READ; "nothing was scanned"
#
# The header above chose 4 for the ADVISORY status precisely BECAUSE 3 was
# taken by that meaning; this constant is the same reading from the other side.
# ``scripts/preflight.sh``'s ``_record_gate_outcome`` maps every non-zero that is
# not ``ADVISORY_EXIT_STATUS`` to FAIL, and the workflow step runs under
# ``set -euo pipefail``, so a refusal is loud in both automated callers.
UNSCANNABLE_EXIT_STATUS = 3


def count_commit_message_separators(commit_text: str) -> int:
    """How many commit-message RECORD TERMINATORS ``commit_text`` carries.

    This is a newline count, and the name says newline-count rather than
    "commit count" on purpose — see the residue below.

    WHAT IS MEASURED, and why it is the strongest floor this surface supports.
    ``--commit-messages-file`` takes a FLAT ``git log --format='%B'``
    concatenation. Unlike the NUL record stream the sibling closing-keyword
    gate parses (#9220), it carries no record boundary at all: a blank line
    inside one message is indistinguishable from the seam between two. So the
    supplied commit count cannot be recovered from the bytes, and any line that
    claimed to have recovered it would be a fabricated number.

    What CAN be recovered is a FLOOR. ``git log --format=<fmt>`` terminates
    every entry with a newline, and ``%B`` of an empty message is the empty
    string, so a commit contributes AT LEAST one newline and an empty-message
    commit contributes EXACTLY one. Measured under git 2.54.0 rather than
    argued from the documentation: three commits made with
    ``--allow-empty-message`` render as exactly three LF bytes and nothing else
    (3 newlines for 3 commits — the floor is tight), and a four-commit range
    mixing an empty message, a multi-paragraph message and a message stored
    without a trailing newline renders 11 newlines. So ``separators >= N`` holds
    for every range of N commits, and it FAILS for the 0-byte file that issue
    #9225 is about.

    THE RESIDUE, named rather than implied. This is a floor on newlines, not a
    count of commits, and FOUR shapes satisfy it while still under-scanning.
    The first three share a cause — the count is right and the FILE is wrong:

      * a file built from a DIFFERENT range whose messages happen to carry
        enough newlines,
      * a file truncated mid-range whose surviving messages carry enough
        newlines between them,
      * one long commit message standing in for many short ones.

    The fourth is not that, and it is the one worth reading twice: a DEGRADED
    ``$BASE``. The workflow takes the count from
    ``git rev-list --count "$BASE..$HEAD"`` in the SAME step that writes the
    file from ``$BASE..$HEAD``, so a ``$BASE`` that resolves too near ``HEAD``
    yields a short file AND a matching short count. Every arm agrees, the floor
    is satisfied, and the scan is short — the fault is in the ENDPOINTS, not in
    the reading, so no amount of counting the file's contents can see it. That
    is the live form of #5802's force-push / unreachable-head class, and neither
    remedy below touches it.

    WHAT WOULD CLOSE THE FIRST THREE, stated at the right level. It is tempting
    to say "the format has no record boundary", and that is one level too
    strong: the boundary is missing from the FILE THIS CALLER CHOSE, not from
    the surface. The same workflow step already writes ``commit_records.bin``
    (``git log -z --format='%H%n%B'``), and since #9220's fix this gate ACCEPTS
    such a stream — :func:`_commit_surface_text` recognises it and turns the NUL
    terminators back into newlines. So closing the first three shapes needs a
    new record-COUNTING arm here plus a caller that passes the record file, and
    that is not free: the ``%H`` SHA lines would join the scan surface of all
    four families that read this text, and every line number the reports print
    would shift. Deliberately out of scope here; #9225 is about the gate that
    published a verdict over an unread surface, not about re-shaping its input.

    ONE THING THIS DOES **NOT** REFUSE, because an earlier draft of this
    paragraph said it did: a second read of git BY THE CALLER. ``--min-commits``
    IS such a read — ``git rev-list --count`` walks the range without touching
    either file — and the sibling gate's third arm is the same thing. What
    #9220's design refuses is the SCRIPT shelling out to git to reach state its
    caller did not hand it; a caller deriving the number is exactly what both
    gates now rely on. (The sibling's own residue is a ``%b``/``%B`` format
    slip, which is not a counting problem at all.)

    So the floor is what is enforced and what the verdict line says; nothing
    here claims to have counted commits.
    ``TestTheFloorIsNotACommitCount`` pins all four shapes.
    """
    return commit_text.count("\n")


def render_commit_surface_refusal(
    commit_text: str | None, min_commits: int, separators: int
) -> str:
    """Operator-facing report for a commit surface that cannot meet ``min_commits``.

    Written to name what the caller asserted, what arrived, and — first — that
    this is NOT a clean verdict, because the failure mode being closed is a
    green being read as proof (#9225).
    """
    if commit_text is None:
        arrived = (
            "no --commit-messages-file was passed at all, so that surface\n"
            "was never read."
        )
    else:
        arrived = (
            f"the file supplied holds {len(commit_text)} byte(s) and "
            f"{separators} record terminator(s).\n"
            "A range of N commits cannot render fewer than N of those."
        )
    return (
        "audit-grep: NOTHING WAS SCANNED on the commit-message surface.\n"
        "\n"
        f"The caller asserted at least {min_commits} commit(s) in the range it\n"
        f"built this file from, and {arrived}\n"
        "\n"
        "This is NOT a content verdict. It means the range was not computed, or\n"
        "was computed over the wrong endpoints, NOT that the branch is clean.\n"
        "\n"
        "Four families read the commit-message surface and nothing else reads\n"
        "it, so a green published here is a green over zero input for all four:\n"
        "  * the customer-name guard (#2374 / #3135)  -- HARD, unclearable\n"
        "  * the invisible-character refusal (#8715)  -- HARD, unclearable\n"
        "  * the AI-attribution family (#8331)        -- PR-body clearable\n"
        "  * the #5615 tripwire family                -- PR-body clearable\n"
        "The first two reach permanent git history through a commit message,\n"
        "where the remedy stops being an edit and becomes a rewrite (#9225).\n"
        "\n"
        "Fix: rebuild the commit-message file from the same range the count came\n"
        "from (git log --format='%B' \"$BASE..$HEAD\"), or drop --min-commits if\n"
        "this caller genuinely has no range to assert.\n"
    )


def render_scanned_extent(
    *,
    diff_text: str,
    added_lines_with_markdown: int,
    added_lines: int,
    commit_text: str | None,
    min_commits: int,
    pr_title: str,
    pr_body_supplied: bool,
    pr_body: str,
) -> str:
    """One line per surface, naming HOW MUCH of it this run actually read.

    The whole of issue #9225 is that this gate printed a byte-identical green
    over a 0-byte commit-message file and over a branch's real commit messages.
    The assertion arm below can only bite for a caller that knows its range; an
    ad-hoc caller who points the flag at the wrong file has no such number, and
    for them the remedy is that the verdict SAYS what it read. That is the shape
    ``check_compose_dockerfiles.py``, ``check_proprietary_data.py`` and
    ``check_closing_keywords.py`` already print.

    Printed on every run that reaches a verdict, not only on a green: a report
    of the extent is as useful beside a red as beside a pass, and a line that
    appears only sometimes is a line a reader learns to stop looking for.

    Deliberately NOT phrased as "scanned N commit message(s)". This surface
    carries no record boundary, so that number does not exist here — see
    :func:`count_commit_message_separators`. Printing a number the input cannot
    support is the same defect one level down.
    """
    # TWO diff counts, not one, because the gate really does scan two different
    # subsets of the same added lines (:func:`parse_diff_added_lines`): the
    # customer-name guard keeps ``*.md`` and the tripwire families do not, and
    # both exempt this gate's own script and tests. Printing one number under
    # the label "added lines" would be the over-claim this function exists to
    # remove -- on a Markdown-heavy diff the two differ by most of the diff.
    lines = [
        "audit-grep: surfaces read by this run --",
        f"  diff:            {len(diff_text)} byte(s); of its added lines, "
        f"{added_lines_with_markdown} reach",
        f"                   the customer-name guard and {added_lines} reach the "
        "tripwire",
        "                   families (this gate's own script and tests are exempt "
        "from both,",
        "                   and *.md from the second)",
    ]
    if commit_text is None:
        lines.append(
            "  commit messages: NOT SUPPLIED (no --commit-messages-file) -- the "
            "customer-name,"
        )
        lines.append(
            "                   invisible-character, AI-attribution and #5615 "
            "scans did not"
        )
        lines.append("                   run on that surface at all")
    else:
        separators = count_commit_message_separators(commit_text)
        asserted = (
            f"caller asserted >= {min_commits} commit(s)"
            if min_commits > 0
            else "extent NOT asserted by the caller (no --min-commits)"
        )
        lines.append(
            f"  commit messages: {len(commit_text)} byte(s), {separators} record "
            f"terminator(s); {asserted}"
        )
    if pr_body_supplied:
        lines.append(f"  PR title/body:   {len(pr_title)} + {len(pr_body)} byte(s)")
    else:
        lines.append(
            f"  PR title/body:   {len(pr_title)} byte(s) of title; NO --pr-body-file "
            "(body read as empty)"
        )
    return "\n".join(lines) + "\n"


def _to_python_regex(grep_pattern: str) -> str:
    """Translate the POSIX-grep dialect used in CONTRIBUTING.md to the
    ``re`` module's dialect.

    Only one translation is currently needed: ``[[:space:]]`` →
    ``\\s``. Any other POSIX character class would need a matching
    entry here. Kept narrow on purpose so an accidentally-introduced
    POSIX construct surfaces as a regex compile error rather than a
    silent semantic divergence.
    """
    return grep_pattern.replace("[[:space:]]", r"\s")


def line_content_hash(text: str) -> str:
    """The 8-hex-digit content key of an added line (#7126).

    SHA-256 of the line with surrounding whitespace stripped, so re-indenting a
    justified line keeps its justification while any other edit voids it.
    """
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()[:8]


@dataclass(frozen=True)
class Hit:
    """One pattern hit on an added diff line."""

    path: str
    line: int
    pattern_label: str
    snippet: str

    def justification_key(self) -> str:
        """The legacy ``<path>:<line>`` key (still accepted, goes stale on a shift)."""
        return f"{self.path}:{self.line} {self.pattern_label}"

    def content_key(self) -> str:
        """The preferred key: file plus the line's content, immune to a shift (#7126)."""
        return f"{self.path}#{line_content_hash(self.snippet)} {self.pattern_label}"


# Per-pattern compiled regex, case-insensitive to match the
# CONTRIBUTING.md grep (``grep -iE``). Each pattern is compiled
# independently so the per-line scan can attribute each hit to its
# label without parsing match groups.
_COMPILED_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (label, re.compile(_to_python_regex(pat), re.IGNORECASE))
    for label, pat in PATTERN_SPECS
]

# Compiled AI-attribution patterns (#8331). Case-insensitive, like the
# justification-gated family they join: an attribution footer is not made
# acceptable by lower-casing it. See :data:`AI_ATTRIBUTION_SPECS`.
_COMPILED_AI_ATTRIBUTION: list[tuple[str, re.Pattern[str]]] = [
    (label, re.compile(_to_python_regex(pat), re.IGNORECASE))
    for label, pat in AI_ATTRIBUTION_SPECS
]


# Compiled scoped patterns: ``(label, compiled_regex, path_globs)``. Same
# per-pattern independent compilation as above so each hit attributes to its
# label; the third element is carried through so :func:`scan_for_hits` can
# gate the match on the file path.
_COMPILED_SCOPED_PATTERNS: list[tuple[str, re.Pattern[str], tuple[str, ...]]] = [
    (label, re.compile(_to_python_regex(pat), re.IGNORECASE), globs)
    for label, pat, globs in SCOPED_PATTERN_SPECS
]


# Compiled companion-required patterns: ``(label, compiled_regex,
# compiled_companion, path_globs)`` (#6116). Same per-pattern independent
# compilation; the companion regex rides alongside so :func:`scan_for_companion_required`
# can clear a hit whose hunk carries the required call.
_COMPILED_COMPANION_PATTERNS: list[
    tuple[str, re.Pattern[str], re.Pattern[str], tuple[str, ...]]
] = [
    (
        label,
        re.compile(_to_python_regex(pat), re.IGNORECASE),
        re.compile(_to_python_regex(companion), re.IGNORECASE),
        globs,
    )
    for label, pat, companion, globs in COMPANION_PATTERN_SPECS
]


# Compiled customer-name patterns. Case-insensitive (``grep -i`` parity) so a
# re-introduction in any casing is caught. Scanned independently of the two
# families above and NOT routed through justification — see
# :data:`CUSTOMER_NAME_SPECS`.
_COMPILED_CUSTOMER_NAMES: list[tuple[str, re.Pattern[str]]] = [
    (label, re.compile(_to_python_regex(pat), re.IGNORECASE))
    for label, pat in CUSTOMER_NAME_SPECS
]


# Compiled frozen dual-derivation patterns: ``(label, compiled_regex,
# allowlist)``. Compiled CASE-SENSITIVELY (NO ``re.IGNORECASE``) — see the
# note in the :data:`FROZEN_DERIVATION_SPECS` header: these are exact-cased
# identifiers and case-insensitivity would collide with the shared helper name
# ``mergePolicyFacetValues``. The allowlist rides through so
# :func:`scan_for_frozen_derivations` can gate the hit on the file path.
_COMPILED_FROZEN: list[tuple[str, re.Pattern[str], tuple[str, ...]]] = [
    (spec.label, re.compile(_to_python_regex(spec.regex)), spec.allowlist)
    for spec in FROZEN_DERIVATION_SPECS
]

# Label → spec, so the report can surface each hit's teaching message + the
# issue that retires the rule.
_FROZEN_SPEC_BY_LABEL: dict[str, FrozenDerivationSpec] = {
    spec.label: spec for spec in FROZEN_DERIVATION_SPECS
}


def _scope_matches(path: str, globs: Sequence[str]) -> bool:
    """True if ``path`` is in a scoped pattern's path scope.

    The ``globs`` are :mod:`fnmatch` patterns. A leading ``!`` marks a
    NEGATIVE glob (an exclusion): the path is in scope when it matches at
    least one positive glob AND no negative glob. With only positive globs
    this is a plain "matches any". A scope listing only negatives would
    match nothing (there is no positive to include) — that is a misconfig,
    not a useful rule, so we require at least one positive match.

    Examples (see :data:`SCOPED_PATTERN_SPECS`):

      - ``search-ui/.../debug/**`` includes every file under the debug tree.
      - ``packages/.../search/*.py`` + ``!.../search/step_execution.py``
        includes every ``.py`` in the Studio search package EXCEPT the
        legacy / passthrough body-source file.
    """
    positives = [g for g in globs if not g.startswith("!")]
    negatives = [g[1:] for g in globs if g.startswith("!")]
    if not any(fnmatch.fnmatch(path, g) for g in positives):
        return False
    if any(fnmatch.fnmatch(path, g) for g in negatives):  # noqa: SIM103  # keep the parallel guard-clause form: this is the 2nd of two positional `if <fails-a-glob-test>: return False` gates before `return True`; collapsing only the last into `return not (...)` would mix guard-clause and collapsed-boolean styles for two symmetric checks
        return False
    return True


# ---------------------------------------------------------------------------
# Diff parsing
# ---------------------------------------------------------------------------
# The gate's own definition + test files. These three paths inherently
# contain every tripwire pattern — the script's :data:`PATTERN_SPECS` /
# :data:`FROZEN_DERIVATION_SPECS` registries and explanatory comments QUOTE
# each pattern to document what is forbidden, and the Python test + shell
# smoke-test files embed them in diff FIXTURES (and in assertions about those
# fixtures) to prove the gate catches them. They are documentation / test
# scaffolding, not code that USES the patterns, so scanning them produces only
# self-referential false positives that recur every time the gate is edited
# (the shell self-test matters especially for the #3022 HARD-block frozen
# family, whose fixtures would otherwise be un-clearable). Matched as the exact
# relative path
# the diff's ``+++ b/<path>`` header reports (see :func:`parse_diff_added_lines`,
# which strips the ``b/`` prefix). Companion coverage:
# ``tests/test_audit_grep_diff.py`` asserts a tripwire added inside either
# of these files (or any ``.md``) yields zero hits, while the same pattern
# in an ordinary ``.py`` still hits.
_GATE_OWN_FILES: frozenset[str] = frozenset(
    {
        ".github/scripts/audit_grep_diff.py",
        ".github/scripts/test_audit_grep_diff.sh",
        "tests/test_audit_grep_diff.py",
        # The scheduled whole-tree census (#5615) and its tests. Same
        # reasoning: the census script's report renderer and its tests QUOTE
        # the patterns to prove the census finds them. The exemption is shared
        # by both gates — ``audit_grep_tree.py`` imports :func:`_is_self_or_doc`
        # rather than keeping a second list, so a file exempt from one is
        # exempt from the other by construction.
        ".github/scripts/audit_grep_tree.py",
        "tests/test_audit_grep_tree.py",
    }
)


def _is_gate_own_file(path: str | None) -> bool:
    """True if ``path`` is the gate's own script / test file.

    The narrower half of :func:`_is_self_or_doc`, split out for the
    customer-name family (#8019), which exempts these files but NOT ``*.md``:
    a doc can only MENTION a tripwire pattern, but it can genuinely USE a
    retailer's name. See :data:`CUSTOMER_NAME_SPECS` and the
    ``include_markdown`` parameter of :func:`parse_diff_added_lines`.
    """
    if path is None:
        return False
    return path in _GATE_OWN_FILES


def _is_self_or_doc(path: str | None) -> bool:
    """True if ``path`` is exempt from scanning: a Markdown doc OR the
    gate's own script / test file.

    This is the TRIPWIRE-family exemption (and the whole-tree census's, which
    imports it). The customer-name family deliberately does NOT use it — it
    uses :func:`_is_gate_own_file`, keeping the gate's own files exempt while
    scanning Markdown (#8019).

    The tripwire patterns are all CODE telltales. Three kinds of file can
    only MENTION such a pattern (as documentation, fixture, or assertion)
    rather than USE it, so scanning their added lines yields only false
    positives:

    - Any ``*.md`` — documentation. CONTRIBUTING.md, for example, must
      quote ``.build_search()`` as the canonical forbidden Studio
      wire-rewrite to explain the rule.
    - ``.github/scripts/audit_grep_diff.py`` — this gate's own source. Its
      pattern registry and comments necessarily spell out every pattern.
    - ``.github/scripts/test_audit_grep_diff.sh`` — this gate's own shell smoke
      test. Its heredoc fixtures embed the patterns to drive the CLI end-to-end.
    - ``tests/test_audit_grep_diff.py`` — this gate's own tests. They embed
      the patterns in synthetic diff fixtures (and assertions about them).

    Without this exemption the gate flags ITSELF: editing the rules doc,
    the script, or its tests reintroduces the patterns and the job goes
    red on documentation/fixtures rather than on code that uses them.
    """
    if path is None:
        return False
    if path.lower().endswith(".md"):
        return True
    return _is_gate_own_file(path)


def parse_diff_added_lines(
    diff_text: str, *, include_markdown: bool = False
) -> list[tuple[str, int, str]]:
    """Yield ``(path, new_line_number, content)`` for every added line.

    Tracks the post-image line counter from each ``@@ -a,b +c,d @@`` hunk
    header. Skips:

    - The ``+++`` and ``---`` file headers (``+++`` would otherwise look
      like an added line starting with ``+``).
    - Lines starting with ``\\`` (``\\ No newline at end of file``).
    - Pure removals (``-``) — they don't have a new-side line number.
    - Added lines in EXEMPT files (see :func:`_is_self_or_doc`): any
      Markdown doc, plus the gate's own script and test file. Every
      tripwire pattern in :data:`PATTERN_SPECS` is a CODE pattern — a
      Studio query-rewrite call, a ``type: ignore`` / ``pytest.skip(``
      silencer, an AI/process-method string, etc. These files can only
      MENTION such a pattern (documentation, fixture, or assertion), never
      USE it: the rules doc must quote the patterns to explain them, and
      the gate's own source/tests embed them in their pattern registry and
      diff fixtures. Scanning them produces only self-referential false
      positives that recur every time the doc or the gate is edited. We
      still advance the line counter for exempt files so subsequent
      non-exempt hunks in the same diff keep their correct line numbers —
      we simply do not RECORD their added lines as scannable hits.

    ``include_markdown=True`` narrows that exemption to the gate's own script
    / test files (:func:`_is_gate_own_file`), so ``*.md`` added lines ARE
    recorded. Exactly one caller asks for it: the customer-name guard (#8019).
    Its pattern is not a code telltale — a doc can genuinely USE a retailer's
    name, and a Markdown line naming the customer leaks their identity as a
    PRISM customer just as a line of code does — so the reasoning that makes
    the ``*.md`` exemption right for the tripwire families does not carry to
    it. Callers scanning the tripwire families must NOT pass it: they would
    red on the rules doc quoting the patterns it exists to explain. The two
    lists come from two calls over the same diff text rather than one filtered
    afterwards, so neither family can be handed the other's surface by
    accident; ``tests/test_audit_grep_diff.py::TestCustomerNameMarkdownSurface``
    pins both directions end-to-end through the CLI.

    The implementation is intentionally minimal: it handles the unified
    diff dialect ``git diff`` emits and nothing else. It does NOT depend
    on any third-party diff parser so the CI job has no install step.
    """
    is_exempt = _is_gate_own_file if include_markdown else _is_self_or_doc
    result: list[tuple[str, int, str]] = []
    current_path: str | None = None
    new_line: int | None = None
    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            # ``+++ b/path/to/file`` (or ``+++ /dev/null`` for deletes).
            target = raw[4:].strip()
            if target == "/dev/null":
                current_path = None
            elif target.startswith("b/"):
                current_path = target[2:]
            else:
                current_path = target
            new_line = None
            continue
        if raw.startswith("--- "):
            # We track the new side only; ``---`` is informational.
            continue
        if raw.startswith("@@"):
            m = hunk_re.match(raw)
            new_line = int(m.group(1)) if m else None
            continue
        if current_path is None or new_line is None:
            continue
        if raw.startswith("\\"):
            # ``\ No newline at end of file`` — not a real diff row.
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            # Exempt files (markdown docs + the gate's own script/test)
            # only MENTION the patterns; they don't USE them. Skip
            # recording their added lines as hits, but still advance the
            # new-side counter so later non-exempt hunks keep correct line
            # numbers. See :func:`_is_self_or_doc` and the docstring above.
            # Under ``include_markdown`` only the gate's own files are
            # exempt — a doc can USE a customer name (#8019).
            if not is_exempt(current_path):
                result.append((current_path, new_line, raw[1:]))
            new_line += 1
        elif raw.startswith("-"):
            # Removal — advances the old side only.
            continue
        else:
            # Context line — advances the new side.
            new_line += 1
    return result


@dataclass(frozen=True)
class Hunk:
    """One ``@@`` hunk of a unified diff, as the companion family sees it (#6116).

    ``path``  — the new-side path, ``b/`` already stripped.
    ``added`` — ``(new_line_number, content)`` for each ADDED line, i.e. exactly
                the rows :func:`parse_diff_added_lines` would report for this
                hunk. A companion hit is always reported on an added line, so
                this is what the scan iterates.
    ``body``  — every POST-IMAGE line of the hunk (added lines AND the context
                lines git ships around them), newline-joined. This is the
                COMPANION SEARCH SURFACE: a required call already present in the
                surrounding code shows up here as context even though the PR did
                not add it, which is the whole reason the companion is searched
                against the hunk rather than against the added lines alone.
                Removed lines are excluded — they are not in the post-image, so
                a check the PR DELETED must not clear the hit it just created.
    """

    path: str
    added: tuple[tuple[int, str], ...]
    body: str


def parse_diff_hunks(diff_text: str) -> list[Hunk]:
    """Yield one :class:`Hunk` per ``@@`` hunk in ``diff_text``.

    A second, coarser view of the SAME diff :func:`parse_diff_added_lines`
    parses line-by-line, kept separate rather than folded into that function so
    the three existing families' signature and behaviour are untouched. Both
    share the dialect assumptions (unified ``git diff``, nothing else) and the
    :func:`_is_self_or_doc` exemption — a hunk in an exempt file is dropped
    outright, since the gate's own script/tests and the rules doc can only
    MENTION a pattern, never USE it.

    Hunks with no added lines (a pure deletion) are dropped: there is nothing
    for a companion rule to report on.
    """
    hunks: list[Hunk] = []
    current_path: str | None = None
    new_line: int | None = None
    added: list[tuple[int, str]] = []
    body: list[str] = []
    hunk_re = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

    def flush() -> None:
        if current_path is not None and added:
            hunks.append(
                Hunk(path=current_path, added=tuple(added), body="\n".join(body))
            )
        added.clear()
        body.clear()

    for raw in diff_text.splitlines():
        if raw.startswith("+++ "):
            flush()
            target = raw[4:].strip()
            if target == "/dev/null":
                current_path = None
            elif target.startswith("b/"):
                current_path = target[2:]
            else:
                current_path = target
            if _is_self_or_doc(current_path):
                current_path = None
            new_line = None
            continue
        if raw.startswith("--- "):
            continue
        if raw.startswith("@@"):
            flush()
            m = hunk_re.match(raw)
            new_line = int(m.group(1)) if m else None
            continue
        if current_path is None or new_line is None:
            continue
        if raw.startswith("\\"):
            continue
        if raw.startswith("+") and not raw.startswith("+++"):
            added.append((new_line, raw[1:]))
            body.append(raw[1:])
            new_line += 1
        elif raw.startswith("-"):
            # Removal — old side only, and deliberately NOT part of ``body``.
            continue
        else:
            body.append(raw[1:] if raw.startswith(" ") else raw)
            new_line += 1
    flush()
    return hunks


# ---------------------------------------------------------------------------
# Hit detection
# ---------------------------------------------------------------------------
def scan_for_hits(added_lines: Iterable[tuple[str, int, str]]) -> list[Hit]:
    """Return one :class:`Hit` per pattern match on an added line.

    Each pattern is checked independently per line (a single line may
    match multiple patterns and produce multiple hits — each needs its
    own justification).

    Two pattern families are scanned:

    - :data:`_COMPILED_PATTERNS` — the global CONTRIBUTING.md one-liner
      patterns, checked against every added line regardless of path.
    - :data:`_COMPILED_SCOPED_PATTERNS` — the display-fidelity
      re-derivation patterns (#2474), checked ONLY when the line's file
      path is in the pattern's scope (see :func:`_scope_matches`). This
      keeps an FE synthesis tripwire from firing on backend code and the
      Studio ``build_search().to_dict()`` tripwire from firing on the
      legacy passthrough path.
    """
    hits: list[Hit] = []
    for path, line_no, content in added_lines:
        for label, compiled in _COMPILED_PATTERNS:
            if compiled.search(content):
                hits.append(
                    Hit(
                        path=path,
                        line=line_no,
                        pattern_label=label,
                        snippet=content.rstrip("\n"),
                    )
                )
        for label, compiled, globs in _COMPILED_SCOPED_PATTERNS:
            if _scope_matches(path, globs) and compiled.search(content):
                hits.append(
                    Hit(
                        path=path,
                        line=line_no,
                        pattern_label=label,
                        snippet=content.rstrip("\n"),
                    )
                )
    return hits


def scan_for_companion_required(hunks: Iterable[Hunk]) -> list[Hit]:
    """Return one :class:`Hit` per banned-without-its-companion added line (#6116).

    For each :data:`COMPANION_PATTERN_SPECS` row, an added line is a hit when
    ALL THREE hold: its file path is in the row's scope
    (:func:`_scope_matches`), the line matches the banned pattern, and the
    row's COMPANION pattern is absent from the hunk's post-image
    (:attr:`Hunk.body`). A hunk that carries the companion clears every
    occurrence in that hunk — the declaration being checked is "this write is
    routed through the required check", which is a property of the surrounding
    code, not of the individual line.

    These hits ARE justification-clearable, and route through the same
    reconciliation as :func:`scan_for_hits`. See the
    :data:`COMPANION_PATTERN_SPECS` header for why hunk scope (not function
    scope) is what this surface can honestly enforce, and why a false positive
    there is answered with a PR-body block rather than by widening the scope.
    """
    hits: list[Hit] = []
    for hunk in hunks:
        for label, compiled, companion, globs in _COMPILED_COMPANION_PATTERNS:
            if not _scope_matches(hunk.path, globs):
                continue
            if companion.search(hunk.body):
                continue
            for line_no, content in hunk.added:
                if compiled.search(content):
                    hits.append(
                        Hit(
                            path=hunk.path,
                            line=line_no,
                            pattern_label=label,
                            snippet=content.rstrip("\n"),
                        )
                    )
    return hits


def scan_for_customer_names(
    added_lines: Iterable[tuple[str, int, str]],
) -> list[Hit]:
    """Return one :class:`Hit` per scrubbed-customer-name match on an added line.

    Scans the added lines it is GIVEN for the proprietary customer names in
    :data:`CUSTOMER_NAME_SPECS`; the surface is the caller's choice, and
    :func:`main` gives it the list parsed with ``include_markdown=True`` so
    ``*.md`` added lines ARE scanned (#8019). Before that, this docstring
    claimed it scanned "every added line (any path)" while the list it received
    had already had every ``*.md`` line dropped — so the family with no
    justification escape hatch did not read the surface a documentation change
    uses, and the claim was false in the sentence that followed it.

    Markdown is scanned here and nowhere else because this family's pattern is
    not a CODE telltale: a doc can only MENTION a ``.build_search()``, but it
    can genuinely USE a retailer's name, and that use is the leak. The
    tripwire families keep the ``*.md`` exemption (:func:`_is_self_or_doc`)
    for exactly the reason it was written.

    The gate's own script / test files are still excluded by path
    (:func:`_is_gate_own_file`) because their fixtures CONSTRUCT the real name
    at runtime to prove the guard bites. Nothing else needs excluding: the
    registry pattern is a character class, so neither this module nor the docs
    that quote it can match themselves.

    These hits are a HARD BLOCK: unlike :func:`scan_for_hits`, the caller does
    NOT reconcile them against PR-body justification blocks. The proprietary
    customer's name in core has no legitimate use — it is the one string that
    identifies them as a PRISM customer (CONTRIBUTING.md § "Generalize, don't
    fork per customer") — so there is nothing to justify; any hit fails the
    job. Only the names in the registry match: a retailer or brand name in
    public open-data demo content is not a hit and is not meant to be. See
    :func:`render_customer_name_report`.
    """
    hits: list[Hit] = []
    for path, line_no, content in added_lines:
        for label, compiled in _COMPILED_CUSTOMER_NAMES:
            if compiled.search(content):
                hits.append(
                    Hit(
                        path=path,
                        line=line_no,
                        pattern_label=label,
                        snippet=content.rstrip("\n"),
                    )
                )
    return hits


def scan_text_for_customer_names(text: str, source: str) -> list[Hit]:
    """Return one :class:`Hit` per customer-name match in a free-text blob.

    Unlike :func:`scan_for_customer_names` (which scans DIFF added lines), this
    scans an arbitrary text surface — the PR title + body, or the concatenated
    commit messages on the PR — line by line, reusing the SAME obfuscated
    :data:`CUSTOMER_NAME_SPECS` regexes. This closes the gap that a name scrubbed
    from every blob (the #3135 history rewrite) could still leak back in through
    a commit subject or a PR description, which no diff scan sees.

    ``source`` is a human label for the surface (e.g. ``"<pr-title-and-body>"``
    or ``"<commit-messages>"``) reported in place of a file path; ``line`` is the
    1-based line number within ``text``.

    No separate self-exclusion is needed here: the char-class pattern cannot
    match its own source representation, so a PR whose body or commit message
    merely DOCUMENTS the regex (as this guard's own PR does) does not trip — only
    a line that actually spells the retailer name does.

    Like :func:`scan_for_customer_names`, these hits are a HARD block: the caller
    does NOT reconcile them against PR-body justification blocks.
    """
    hits: list[Hit] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        for label, compiled in _COMPILED_CUSTOMER_NAMES:
            if compiled.search(raw):
                hits.append(
                    Hit(
                        path=source,
                        line=idx,
                        pattern_label=label,
                        snippet=raw.rstrip("\n"),
                    )
                )
    return hits


def render_text_customer_name_report(hits: Sequence[Hit], surface: str) -> str:
    """Operator-facing failure report for a customer name in a text surface.

    ``surface`` names the human-readable place the name leaked in (a commit
    message, or the PR title / body) so the message is actionable. Like
    :func:`render_customer_name_report`, there is NO justification affordance —
    the only fix is to rewrite the offending commit message / PR text so the
    name does not appear.
    """
    lines = [
        "audit-grep customer-name guard (#2374 / #3135): scrubbed customer",
        f"name(s) present in {surface}.",
        "",
        "A SCRUBBED customer name must not appear anywhere that ships with the",
        "repo — including commit messages and the PR title/body, not just",
        "code — because it is the one string that identifies them as a PRISM",
        'customer. See CONTRIBUTING.md § "Generalize, don\'t fork per customer"',
        "and issues #2374 / #3135. This guard matches the CUSTOMER names only —",
        "a retailer or brand name in public open-data demo content is not what",
        "it looks for.",
        "",
        "THAT SENTENCE IS SCOPED, and the scope decides what you do next. It is",
        "true of a name this repository SCRUBBED and holds at zero. A",
        "customization whose name the repository still ships is NOT covered by",
        "it: this guard matches the rows in that subsection's",
        "customer-name-guard table and nothing wider, and the same subsection",
        "states, per row, what it deliberately does NOT cover (#9247). For the",
        "industrial registrant that includes its sister repo's contiguous slug",
        "in a repo path, which is legitimate and is not matched here. Its",
        "abbreviation on its own IS matched (#10626), in an index name or a",
        "profile name too.",
        "So: rewrite the name your hit reports. Do NOT scrub a repo path you",
        "were not asked about.",
        "",
        f"Fix: rewrite the offending {surface} so the name does not appear",
        "(rebase + reword the commit, or edit the PR title/body). This cannot be",
        "cleared with a justification block.",
        "",
        f"{surface} hits:",
    ]
    for hit in hits:
        lines.append(f"  {hit.path}:{hit.line} {hit.pattern_label}    {hit.snippet}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# A LITERAL invisible character on a TEXT surface (#8715)
# ---------------------------------------------------------------------------
# #8649 widened ``scripts/check_no_invisible_characters.py`` from NUL alone to
# the derived class in :mod:`invisible_characters`. That gate judges TRACKED
# FILES. Two surfaces ship with this repository and produce no diff, so it
# never saw them: the COMMIT MESSAGES and the PR TITLE/BODY. This is the
# residue #8715 closes, and it reuses the SAME derivation -- no second list.
#
# WHY IT IS NOT COSMETIC, MEASURED RATHER THAN ASSERTED. The repository's one
# unclearable guard is the customer-name scan below, and it matches a LITERAL
# character class. One U+200B inside the name defeats it on both text surfaces
# while changing no glyph a reviewer sees. Measured on this branch, with the
# name built mechanically out of ``CUSTOMER_NAME_SPECS`` rather than typed:
#
#     clean literal      -> scan_text_for_customer_names -> 1 hit  (control)
#     one U+200B inside  -> scan_text_for_customer_names -> 0 hits
#
# So this guard runs BEFORE that one -- and what that buys is the REPORT an
# author reads, not a different verdict. Stated precisely because a first
# revision of this comment claimed more: reversing the two leaves every verdict
# in the mutation matrix unchanged (a split name defeats the customer-name scan
# and falls through to this one either way; the sole input whose OUTCOME
# differs is a surface carrying a CLEAN name AND a literal elsewhere, where the
# order decides which of the two reports prints). That is worth having --
# telling an author their name is split beats telling them nothing was found --
# but it is report quality, not a correctness invariant, and
# ``test_the_invisible_guard_runs_before_the_customer_name_guard`` is written
# against the one input that can actually tell the two orders apart.
#
# REFUSE, NOT FOLD -- the two uses of one class, kept apart on purpose.
# :func:`_fold_ai_confusables` DELETES these characters before the
# AI-attribution match so an inserted one cannot split a banned token. That is
# a normalisation. THIS is a refusal, and it reads the RAW surface: folding
# first would delete the evidence and report a clean surface, which is the
# failure mode the whole issue is about.
# ``TestInvisibleCharactersOnTextSurfaces.test_the_ai_fold_would_erase_what_this_guard_refuses``
# holds that apart by measurement rather than by this paragraph.
#
# THE ESCAPE HATCH, which #8715 asked to be stated rather than assumed. There
# is no per-hit suppression comment of the kind a linter offers, and none is
# needed, because the remedy is
# LOSSLESS: every member of this class has a visible spelling, ``<U+XXXX>``,
# which is the repository convention #8649 established and which
# :func:`invisible_characters.notate` produces. The report prints the offending
# line ALREADY NOTATED so an author can paste it straight back. That covers the
# case #8715 named -- a body quoting a genuine log line -- and covers it better
# than the literal, which renders as nothing at all. A justification block is
# therefore NOT offered: unlike an AI-attribution mention, where the prose
# genuinely needs the word, nothing here needs the LITERAL.
#
# ONE EXCEPTION, and "lossless" above is scoped by it rather than hedged: see
# :data:`NON_LOSSLESS_REMEDY_NOTE`. A U+200D inside an EMOJI ZWJ SEQUENCE is
# load-bearing for the grapheme, so its notated form does not reproduce what
# was written -- that body is refused with no lossless fix. Base rate measured
# 0 across 300 pull requests and all 5,069 commits, which is why it is NAMED
# rather than allowed.
#
# THE ONE ALLOWANCE, and it is measured, narrow and provably non-weakening.
_MENTION_SUPPRESSION_PREFIX = "@"
_MENTION_SUPPRESSION_CHAR = "\u200b"
# Dependabot renders an upstream release note's ``@handle`` as ``@`` followed by
# U+200B so GitHub does not turn it into a mention. Measured over the 200 most
# recently merged pull requests on 2026-09-10: 2 of 2 dependabot bodies carried
# it (10 occurrences, all U+200B, all immediately after an ``@``), and 0 of 198
# human-authored titles/bodies carried anything in the class at all. A gate that
# reds every dependency bump forever, over a character a bot inserts correctly
# and a human cannot stop it re-inserting on the next rebase, is a gate that
# gets muted -- the state #8331's own artifact allowance exists to avoid.
#
# WHAT THE ALLOWANCE DOES AND DOES NOT REACH -- stated per family, because the
# universal a first revision of this comment asserted was MEASURED FALSE.
#
# That revision said "``@`` is in no scanned token, so an insertion in the one
# permitted position leaves every scanned token contiguous". The premise is
# true of ``CUSTOMER_NAME_SPECS`` and licenses nothing about the others:
# :data:`PATTERN_SPECS` carries THREE ``@``-initial rows --
# ``@pytest.mark.skip``, ``@pytest.mark.xfail``, ``@ts-ignore`` -- which
# :func:`scan_text_for_tripwires` reads on this very surface. Measured through
# the CLI: ``@pytest.mark.skip`` in a PR body rc=1, the same line with a U+200B
# after the ``@`` rc=0; likewise ``@ts-ignore`` in the PR TITLE. The allowance
# WAS an evasion channel for that family, on exactly the seam a positional rule
# creates.
#
# It is closed at the family, not at the allowance: :func:`scan_text_for_tripwires`
# now matches against :func:`_fold_invisibles` of the line. Measured after:
# 3 of 3 evasions caught; with the fold removed, 0 of 3. So, family by family:
#
#   * ``CUSTOMER_NAME_SPECS``  -- unreachable. No row carries an ``@``, so the
#     one permitted position is outside every token the family matches. Swept
#     over every insertion point in EACH of the three registered names,
#     constructed from codepoints: 0 evade. (Until the #9247 review the sweep
#     walked two of the three, so the figure backed less than the sentence.) ("An unbroken
#     run of character classes" was the older wording and stopped being true of
#     the registry at #9247, which added rows carrying separator classes; the
#     reach argument never rested on it.)
#   * ``PATTERN_SPECS``        -- WAS reachable, now folded. The three rows
#     above are the ones that were reachable, and the fold covers every row
#     rather than special-casing them.
#   * ``AI_ATTRIBUTION_SPECS`` -- unreachable. It already folded this class.
#   * the scoped / frozen / client-string families -- not on this surface at
#     all; each gates on a file path and a text surface has none.
#
# The lesson is the shape of the claim, not the hole: a positional allowance
# has to be argued against EVERY family that reads the surface, one at a time.
# ``test_the_mention_allowance_cannot_split_a_customer_name`` sweeps the first,
# and ``test_the_mention_allowance_does_not_defeat_an_at_initial_tripwire``
# pins the second WITH the mutation that reopens it.
#
# It applies to the PR TITLE/BODY only. The commit-message surface is where a
# literal reaches permanent git history, where the remedy stops being an edit
# and becomes a rewrite -- and it needs no allowance, on the WHOLE history
# rather than a window: over all 5,069 commits on ``origin/main``, FIVE carry a
# member of the class (12 x U+2060, 1 x U+00AD), about 1 in 1,000. Every one is
# maintainer prose about the wire joiner and every one has a lossless remedy
# that renders BETTER than today's mash -- ``organic<U+2060>DIETARY`` against
# the ``organicDIETARY`` a reader sees now. NONE is a dependabot commit: the
# release-notes block that carries the ``@`` idiom is rendered into the PR BODY
# and is not in the commit message, which is why one surface needs the
# allowance and the other does not. A first revision of this comment measured
# the most recent 400 and said ZERO, which was true and was a window effect.


#: Codepoints that RENDER BLANK yet sit OUTSIDE the derived class, named here
#: because a guard that implies total coverage is worse than one whose edge is
#: written down (#8714's review, restated for #8715).
#:
#: U+3164 HANGUL FILLER, U+115F HANGUL CHOSEONG FILLER, U+1160 HANGUL JUNGSEONG
#: FILLER and U+FFA0 HALFWIDTH HANGUL FILLER are ``Lo``; U+2800 BRAILLE PATTERN
#: BLANK is ``So``. FIVE, not the four a first revision of this claim listed --
#: it omitted U+1160 while the test that pinned the boundary already carried
#: it, so the prose and the pin disagreed about their own subject.
#:
#: None is a regression: the pre-#8649 six-codepoint list missed them too. They
#: are the standard next evasion, and widening
#: :mod:`invisible_characters` to reach them is a change to a module that now
#: gates every tracked text file -- it needs its own tree-wide census, and it is
#: not made here. ``test_the_stated_boundary_is_true`` pins their ABSENCE, so
#: the widening reds this claim rather than landing quietly beside it.
BLANK_RENDERING_OUTSIDE_THE_CLASS = ("3164", "115F", "1160", "FFA0", "2800")

#: The one remedy in this design that is NOT lossless, named for the same
#: reason (#8715 review).
#:
#: Every other member of the class has a ``<U+XXXX>`` spelling that says
#: everything the literal says. U+200D ZERO WIDTH JOINER inside an EMOJI ZWJ
#: SEQUENCE does not: it is load-bearing for the grapheme, and the notated form
#: renders as the component emoji side by side plus literal text, not as the
#: single glyph that was written. Such a body is REFUSED with no lossless fix.
#:
#: Measured base rate: 0 across 300 pull requests and all 5,069 commits on
#: ``origin/main``. It is named rather than allowed because the shape has not
#: occurred here -- but the exposure is real and asymmetric: dependabot quotes
#: upstream release notes verbatim, those routinely carry ZWJ emoji, and a
#: bot-authored body cannot be hand-fixed. If it ever fires, the answer is a
#: second MEASURED allowance in the shape of the mention one, not a widening of
#: the class. Tracked separately rather than pre-built against a rate of zero.
NON_LOSSLESS_REMEDY_NOTE = "U+200D inside an emoji ZWJ sequence"


@dataclass(frozen=True)
class InvisibleCharacterHit:
    """One literal invisible character found on a text surface (#8715).

    ``codepoint`` is :func:`invisible_characters.describe`'s naming --
    ``U+2060 WORD JOINER`` -- because a report that printed the character
    itself would print nothing. ``notated_line`` is the whole line with every
    member of the class rendered in the ``<U+XXXX>`` convention, which is both
    how a reader SEES the problem and the text they paste back as the fix.
    """

    surface: str
    line: int
    column: int
    codepoint: str
    notated_line: str


def _commit_surface_text(raw: str) -> str:
    """``raw`` with git's ``-z`` RECORD TERMINATORS turned back into newlines.

    Only when ``raw`` provably IS such a stream, which is the whole care in
    this function (#9220).

    The false positive it removes. The sibling closing-keyword gate is handed
    the same commits as ``git log -z --format='%H%n%B'``, and U+0000 is a
    member of the derived invisible-character class -- so feeding that stream
    here reported one "literal invisible character in a commit message" PER
    COMMIT, over messages that contain zero, with a remedy (rebase and reword)
    that addresses nothing. Measured on #9218's five commits: 5 hits, all
    U+0000, all at column 1 of a SHA line.

    WHICH CALLER ACTUALLY DOES THIS is worth being exact about, because the
    first version of this paragraph said the two gates are "routinely run over
    one file" and that is measurably false of both automated callers.
    ``audit-grep.yaml`` builds TWO files in one step -- ``commit_records.bin``
    (``-z``) for the closing-keyword gate and a separate flat ``%B``
    ``commit_messages.txt`` for this one -- and ``scripts/preflight.sh`` never
    invokes the closing-keyword gate at all. The one-file case is the AD-HOC
    caller: a contributor or an agent verifying their own pull request, who
    builds one record stream and points both gates at it. That is a real
    caller and the reason this exists, but it is one caller, not a routine.

    Why it is NOT an unconditional ``replace``, which is what the first draft
    of this fix was. U+0000 in a commit message is a deliberate red -- it is
    #8423's half of the class and ``_PLANTED_CODEPOINTS`` covers it -- and a
    blanket strip silently retires that guard while looking like a false-
    positive fix. So the normalisation is gated on the format: a stream whose
    NUL count equals its parsed record count and whose every record opens with
    a SHA line is a record stream, and a NUL in it is a terminator git wrote.
    Anything else -- the flat ``--format='%B'`` file the workflow actually
    passes, the single message the ``commit-msg`` hook passes, a message with a
    literal NUL planted mid-word -- fails that test and is returned untouched,
    so the guard keeps biting on every surface it bit on before.

    The judgement is IMPORTED rather than restated: two definitions of "this is
    a ``git log -z`` stream" is the drift this repository keeps paying for.

    Replaced with a newline rather than deleted, which is exactly what ``-z``
    displaced: the result is byte-for-byte the text ``git log --format='%H%n%B'``
    writes WITHOUT ``-z``, so the line-oriented scans below see the record
    boundaries they would otherwise have seen -- rather than two records run
    together on one line -- and the line numbers they report stay true.

    The residue, named rather than implied: a record stream carrying a literal
    NUL that happens to split a message into two chunks whose second one opens
    with a hex-only word would pass the format test and lose that NUL.

    That shape is unreachable through git, and that is now MEASURED rather than
    asserted from ``-z``'s design. ``git commit-tree`` refuses outright --
    ``error: a NUL byte in commit log message not allowed`` -- and a commit
    object hand-built with one and offered to ``git hash-object -t commit -w``
    is refused a second time, by fsck: ``nulInCommit: NUL byte in the commit
    object body`` / ``fatal: refusing to create malformed object``. Two layers,
    so there is no commit message whose NUL this drops.

    The OTHER text surface (the PR title and body) is never normalised: a NUL
    there is content, and stays a hit.
    """
    if NUL not in raw:
        return raw
    if record_stream_defect(raw, parse_commit_records(raw)) is not None:
        return raw
    return raw.replace(NUL, "\n")


def scan_text_for_invisible_characters(
    text: str,
    surface: str,
    *,
    allow_mention_suppression: bool = False,
) -> list[InvisibleCharacterHit]:
    """Every literal invisible character in ``text``, in order (#8715).

    ``surface`` is :data:`TEXT_SURFACE_COMMITS` or :data:`TEXT_SURFACE_PR`.
    The class is :mod:`invisible_characters`' -- ``find`` is called on the RAW
    text, never on a folded one; see this section's header for why.

    THE WHOLE TEXT IS SCANNED AS ONE STRING, and the line/column is arithmetic
    over it. It is NOT scanned line by line, which is how every other text
    guard in this file reads its surface, because ``str.splitlines()`` treats
    EIGHT members of this very class as line terminators and CONSUMES them:
    U+000B, U+000C, U+001C, U+001D, U+001E, U+0085, U+2028 and U+2029 each
    vanish into the split and are never present in any line handed to a
    matcher. A line-oriented scan would therefore have reported a confident
    ZERO for eight codepoints -- and U+2028 is not hypothetical, it is one of
    the eight codepoints #8714's census found literally in this tree. Lines are
    counted on ``\n`` alone for the same reason: a line NUMBER derived from a
    splitter that eats the subject would name the wrong line.

    THAT SET IS DERIVED, NOT LISTED, wherever it is tested. A first revision of
    this docstring hand-counted SEVEN and omitted U+001D GROUP SEPARATOR -- a
    hand list short by one, which is the exact defect
    :mod:`invisible_characters` exists to abolish, committed in the docstring
    of the guard that reuses it. The pin walks the codepoint space instead;
    the eight above are prose for a reader and are checked against that walk.
    ``test_a_line_oriented_scan_would_report_zero_for_eight_codepoints`` holds
    that property by measurement rather than by this paragraph.

    ``allow_mention_suppression`` skips a U+200B whose immediately preceding
    character is ``@`` (the header states the measurement, the narrowness and
    why the position cannot split a scanned token). Passed only for the PR
    title/body.

    These hits are a HARD block with no justification affordance, for the same
    reason :func:`scan_text_for_customer_names`' are: there is nothing to
    justify. The visible spelling says everything the literal says.
    """
    hits: list[InvisibleCharacterHit] = []
    for index, ch in find(text):
        if (
            allow_mention_suppression
            and ch == _MENTION_SUPPRESSION_CHAR
            and index > 0
            and text[index - 1] == _MENTION_SUPPRESSION_PREFIX
        ):
            continue
        line_start = text.rfind("\n", 0, index) + 1
        line_end = text.find("\n", index)
        segment = text[line_start:] if line_end == -1 else text[line_start:line_end]
        hits.append(
            InvisibleCharacterHit(
                surface=surface,
                line=text.count("\n", 0, index) + 1,
                column=index - line_start + 1,
                codepoint=describe(ch),
                notated_line=notate(segment),
            )
        )
    return hits


def render_invisible_character_report(
    hits: Sequence[InvisibleCharacterHit], surface_label: str
) -> str:
    """Operator-facing failure report for a literal invisible character (#8715).

    Names every codepoint as ``U+XXXX`` and prints each offending line in the
    ``<U+XXXX>`` notation -- which is simultaneously the diagnosis and the
    replacement text, so the remedy is a copy rather than a hunt for a
    character that renders as nothing.

    Like :func:`render_text_customer_name_report`, there is NO justification
    affordance.
    """
    lines = [
        "audit-grep invisible-character guard (#8649 / #8715): literal invisible",
        f"character(s) present in {surface_label}.",
        "",
        "A character with no glyph is invisible in review by construction: no",
        "reviewer can see it, no contributor can type it, and a reformatter can",
        "delete it without leaving a mark. On a commit message it reaches",
        "permanent git history, where removing it costs a rewrite rather than an",
        "edit. It also DEFEATS the guards that read these surfaces as text -- one",
        "zero-width character inside a scrubbed customer name takes the",
        "customer-name guard from 1 hit to 0 while changing no glyph.",
        "",
        "The class is the SINGLE derivation in scripts/invisible_characters.py,",
        "shared with the tracked-file gate scripts/check_no_invisible_characters.py",
        "so this repository holds ONE definition of an invisible character (#8647).",
        "",
        "Fix: write the codepoint VISIBLY, in the <U+XXXX> notation this",
        "repository already uses for it. Each line below is printed in exactly",
        "that form -- copy it back over the original. Then reword the commit",
        "(rebase + reword) or edit the PR title/body. This cannot be cleared with",
        "a justification block: nothing here needs the LITERAL, and the visible",
        "spelling says everything it says.",
        "",
        f"{surface_label} hits:",
    ]
    for hit in hits:
        lines.append(
            f"  {hit.surface}:{hit.line}:{hit.column} {hit.codepoint}\n"
            f"      {hit.notated_line}"
        )
    lines.append("")
    return "\n".join(lines)


def _path_in_allowlist(path: str, allowlist: Sequence[str]) -> bool:
    """True if ``path`` matches any allowlist glob (:mod:`fnmatch`).

    Unlike :func:`_scope_matches` (positive + negative globs for the scoped
    family), a frozen rule's allowlist is a plain "matches any" set of the
    files permitted to contain the pattern today — a hit whose path matches
    none of them is a NEW site and hard-fails.
    """
    return any(fnmatch.fnmatch(path, glob) for glob in allowlist)


def scan_for_frozen_derivations(
    added_lines: Iterable[tuple[str, int, str]],
) -> list[Hit]:
    """Return one :class:`Hit` per frozen dual-derivation match on a NEW site.

    For each :data:`FROZEN_DERIVATION_SPECS` pattern, an added line is a hit
    ONLY when it matches the (case-sensitive) pattern AND its file path is NOT
    in the pattern's allowlist — i.e. a NEW reader of a fact the Engine emit
    already carries, outside the current tracked-for-removal sites. The
    added-line list this receives has already had ``*.md`` docs and the gate's
    own script / shell-test / Python-test files removed by
    :func:`parse_diff_added_lines`, so the registry's own pattern definitions,
    the doc table, and the fixtures are excluded for free.

    These hits are a HARD block: like :func:`scan_for_customer_names`, the
    caller does NOT reconcile them against PR-body justification blocks. The
    reviewable escape hatch is editing the spec's allowlist in this file (a
    diff-visible act), not a pasted justification. See
    :func:`render_frozen_derivation_report` and :data:`FROZEN_DERIVATION_SPECS`.
    """
    hits: list[Hit] = []
    for path, line_no, content in added_lines:
        for label, compiled, allowlist in _COMPILED_FROZEN:
            if compiled.search(content) and not _path_in_allowlist(path, allowlist):
                hits.append(
                    Hit(
                        path=path,
                        line=line_no,
                        pattern_label=label,
                        snippet=content.rstrip("\n"),
                    )
                )
    return hits


# ---------------------------------------------------------------------------
# PR body justification parser
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Justification:
    """One parsed diff-surface ``Hit:`` line: the content form or the legacy line form."""

    path: str
    line: int
    pattern_label: str
    content_hash: str = ""

    def key(self) -> str:
        if self.content_hash:
            return f"{self.path}#{self.content_hash} {self.pattern_label}"
        return f"{self.path}:{self.line} {self.pattern_label}"


# A justification block:
#
#   Hit: path/to/file.py:42 some_pattern
#   Rule: CONTRIBUTING.md "Engine output IS the wire query"
#   Justification: this is the legitimate fallback path, see ...
#
# We parse it line-by-line and look for the ``Hit:`` line followed
# within a small window by ``Rule:`` and ``Justification:`` lines.
# Whitespace and case on the labels is tolerant; the content after
# ``Hit:`` is parsed strictly so ``<path>:<line>`` and ``<pattern>``
# round-trip exactly with what :class:`Hit` reports.
_HIT_LINE_RE = re.compile(
    r"^\s*Hit\s*:\s*(?P<path>\S+):(?P<line>\d+)\s+(?P<pattern>.+?)\s*$",
    re.IGNORECASE,
)
# The preferred diff-surface form (#7126): ``Hit: <path>#<hash> <pattern>``,
# ``<hash>`` = :func:`line_content_hash`. Tried before :data:`_HIT_LINE_RE`.
_CONTENT_HIT_LINE_RE = re.compile(
    r"^\s*Hit\s*:\s*(?P<path>\S+)#(?P<hash>[0-9a-f]{8})\s+(?P<pattern>.+?)\s*$",
    re.IGNORECASE,
)
_POLICY_LINE_RE = re.compile(r"^\s*Rule\s*:\s*\S", re.IGNORECASE)
_JUSTIFICATION_LINE_RE = re.compile(r"^\s*Justification\s*:\s*\S", re.IGNORECASE)


# The TEXT-surface justification block (#5615):
#
#   Hit: <commit-messages> type: ignore
#   Rule: CONTRIBUTING.md "Pre-merge audit grep"
#   Justification: the commit body names the token it DELETES; see ...
#
# Same three-line shape as the diff form, with the ``<path>:<line>`` token
# replaced by a bare surface name. There is deliberately NO line number: see
# the module docstring — a commit-message line moves on every rebase and a
# PR-body line on every edit, so a line-keyed text justification goes stale
# and reds a PR for an edit it never made.
_TEXT_HIT_LINE_RE = re.compile(
    r"^\s*Hit\s*:\s*(?P<surface><[a-z-]+>)\s+(?P<pattern>.+?)\s*$",
    re.IGNORECASE,
)


def _is_justification_protocol_line(line: str) -> bool:
    """True if ``line`` is part of the gate's own justification protocol.

    A justification block necessarily QUOTES the pattern label it clears on
    its ``Hit:`` line, and its ``Rule:`` line names the CONTRIBUTING.md rule.
    Scanning those lines on the PR-body text surface would mean that writing
    the block to clear a hit creates a FRESH hit on the block itself — the
    author could never converge. So the protocol lines are not scanned, for
    the same reason :func:`_is_self_or_doc` exempts the rules doc and this
    gate's own source on the diff surface: they can only MENTION a pattern,
    never USE it.

    ``Justification:`` is included for the same convergence reason — an
    author explaining a hit almost always names it in the explanation. The
    residual is deliberate and small: a banned token typed into a
    ``Justification:`` line is not re-flagged, but it sits inside an explicit,
    reviewer-visible declaration rather than in ordinary prose.

    A new regex added here must also go into the two pin lists in
    ``tests/test_audit_grep_diff.py`` (the pin test
    ``test_the_justification_protocol_regexes_are_pinned``).
    """
    return bool(
        _HIT_LINE_RE.match(line)
        or _CONTENT_HIT_LINE_RE.match(line)
        or _TEXT_HIT_LINE_RE.match(line)
        or _POLICY_LINE_RE.match(line)
        or _JUSTIFICATION_LINE_RE.match(line)
    )


@dataclass(frozen=True)
class TextHit:
    """One :data:`PATTERN_SPECS` match on a commit-message / PR-body line (#5615).

    Distinct from :class:`Hit` in exactly one way that matters: the
    justification key carries NO line number. ``line`` is kept for the report
    so a human can find the offending line, but it is not part of the key —
    see :func:`parse_text_justifications`.
    """

    surface: str
    line: int
    pattern_label: str
    snippet: str

    def justification_key(self) -> str:
        """Stable string the PR-body justification block must contain."""
        return f"{self.surface} {self.pattern_label}"


def scan_text_for_tripwires(text: str, surface: str) -> list[TextHit]:
    """Return one :class:`TextHit` per :data:`PATTERN_SPECS` match in ``text``.

    ``surface`` is one of :data:`TEXT_SURFACE_COMMITS` /
    :data:`TEXT_SURFACE_PR`. Lines belonging to the justification protocol are
    skipped (:func:`_is_justification_protocol_line`).

    Only the GLOBAL family is scanned. The scoped and frozen families both gate
    on a file path (a scope glob / an allowlist glob) and a text surface has
    none, so neither has anything to decide here.

    These hits ARE justification-clearable — unlike the customer-name guard on
    the same surfaces, which is a hard block. A commit message or PR body that
    honestly describes work on one of these patterns is legitimate prose; what
    #5615 closes is that such a mention was previously invisible, not that it is
    always wrong.
    """
    hits: list[TextHit] = []
    for idx, raw in enumerate(text.splitlines(), start=1):
        if _is_justification_protocol_line(raw):
            continue
        # Matched against the INVISIBLE-FOLDED line, reported as the RAW one
        # (#8715 review). The mention-suppression allowance in
        # :func:`scan_text_for_invisible_characters` lets exactly one shape
        # through to this scan -- a U+200B immediately after an ``@`` -- and
        # THREE rows of :data:`PATTERN_SPECS` are ``@``-initial
        # (``@pytest.mark.skip``, ``@pytest.mark.xfail``, ``@ts-ignore``), so
        # that one shape sat precisely on the seam. Measured through the CLI
        # before the fold: ``@pytest.mark.skip`` rc=1, the same line with a
        # U+200B after the ``@`` rc=0, on the PR body AND in the PR title. The
        # fold closes it for every row at once rather than special-casing the
        # three. The report still shows ``raw`` so an operator reads what was
        # actually written, not the form the matcher used.
        folded = _fold_invisibles(raw)
        for label, compiled in _COMPILED_PATTERNS:
            if compiled.search(folded):
                hits.append(
                    TextHit(
                        surface=surface,
                        line=idx,
                        pattern_label=label,
                        snippet=raw.rstrip("\n"),
                    )
                )
    return hits


def _fold_ai_confusables(text: str) -> str:
    """Return ``text`` with invisible and homoglyph evasions folded away.

    Three transforms, in order, each closing a way to change the BYTES a
    literal scan sees without changing the GLYPHS a reviewer sees:

    1. NFKC normalisation — collapses the full-width and compatibility forms
       (a full-width vendor name reads identically at normal size).
    2. The invisible-codepoint fold built in :data:`_AI_INVISIBLE_FOLD` over
       the derived class :data:`_AI_INVISIBLE_CHARS` — a zero-width character
       inside a name renders as nothing at all and is DELETED; a space-like one
       becomes a plain space, because deleting it would weld two words into one
       and lose the token being hunted.
    3. The homoglyph fold in :data:`_AI_HOMOGLYPHS` — Cyrillic and Greek
       lookalikes to the Latin letter the registry is written with.

    Applied ONLY to :data:`AI_ATTRIBUTION_SPECS` input. The report still shows
    the ORIGINAL line, so an operator reads what was actually written rather
    than the folded form the matcher used.
    """
    folded = unicodedata.normalize("NFKC", text)
    return folded.translate(_AI_FOLD_TABLE)


def _dewrap_with_line_map(lines: Sequence[tuple[int, str]]) -> tuple[str, list[int]]:
    """Join ``lines`` with ALL whitespace removed, keeping a per-character line map.

    ``lines`` is ``(line_number, text)`` pairs. Returns the concatenated
    whitespace-free text and a parallel list giving, for each surviving
    character, the 1-based line it came from — so a match that spans a wrapped
    line is still reported at the line where it STARTS rather than at a
    fabricated line 0.

    Note what this removes, because the wording here used to say "a wrapped
    line" and that understated it: ALL whitespace across the whole surface is
    removed, not only the newline at a wrap point. So the pass catches a vendor
    name split across a line break AND one split by any space or tab — and it is
    also why two adjacent words can concatenate into a token that appears in
    neither of them, which is a real (if rare) false-positive path and the
    reason only the MENTION tier runs here. Only the MENTION tier runs
    against this text: a shape row keys on the punctuation and word boundaries
    that removing whitespace destroys, so matching one here would be matching
    something other than what the pattern reads as.
    """
    chars: list[str] = []
    line_of: list[int] = []
    for lineno, raw in lines:
        for ch in raw:
            if ch.isspace():
                continue
            chars.append(ch)
            line_of.append(lineno)
    return "".join(chars), line_of


# Markup that a GFM renderer DELETES, so a token split by it reads as one word
# to every human who sees the PR description (#8331 review). An HTML comment
# renders as nothing at all; a run of emphasis markers renders as styling and no
# character. Both therefore split a vendor name without changing what anyone
# reads — the same property the zero-width codepoints have, so they are handled
# the same way and for the same reason.
_AI_MARKUP_NOISE_RE = re.compile(r"<!--.*?-->|[*_`~]+", re.DOTALL)


def _strip_ai_markup_noise(text: str) -> str:
    """Delete render-invisible markup so an intra-token split still matches.

    Applied only as an EXTRA variant unioned with the others, never in place of
    them (see :func:`_ai_variants`), so it can only add detections.
    """
    return _AI_MARKUP_NOISE_RE.sub("", text)


def _ai_variants(text: str) -> tuple[str, ...]:
    """Return the forms of ``text`` the AI family matches against.

    THE FOLD IS ADDITIVE, NEVER SUBSTITUTIVE, and this helper is what makes
    that true. The homoglyph table collapses an ambiguous glyph class onto one
    representative — the vertical-stroke class onto ``l`` — which is what makes
    a Cyrillic lookalike inside a vendor name match. But the same collapse
    REWRITES a legitimate token that contains a capital ``I``: the two-letter
    abbreviation the ``ai-assisted-phrasing`` row keys on folds to something
    that row no longer matches. Scanning the folded text ALONE therefore
    silences a real detection while looking like a hardening, which is the
    "tuned until quiet" failure this repository has measured before.

    So every form is matched and the results unioned: a hit in ANY is a hit.
    A transform can then only ever ADD detections, never remove one.

    FOUR forms, not two: the raw text; the confusable fold; the text with
    render-invisible markup deleted (:func:`_strip_ai_markup_noise`); and both
    transforms composed. The markup form was added when review found the corpus
    testing only the EASY spelling of two cases — an HTML comment or emphasis
    run WRAPPING the token, which a plain scan already sees past, rather than
    one splitting it INSIDE the name, which renders identically in GFM and was
    a clean miss.
    ``tests/test_audit_grep_diff.py::TestAiAttributionFoldIsAdditive`` pins the
    property over the whole planted corpus rather than over one example.
    """
    variants = [text]
    for candidate in (
        _fold_ai_confusables(text),
        _strip_ai_markup_noise(text),
        _strip_ai_markup_noise(_fold_ai_confusables(text)),
    ):
        if candidate not in variants:
            variants.append(candidate)
    return tuple(variants)


def scan_text_for_ai_attribution(text: str, surface: str) -> list[TextHit]:
    """Return one :class:`TextHit` per :data:`AI_ATTRIBUTION_SPECS` match (#8331).

    ``surface`` is :data:`TEXT_SURFACE_COMMITS` or :data:`TEXT_SURFACE_PR`.
    The hits are ordinary :class:`TextHit` objects and join the same
    justification-gated pool as :func:`scan_text_for_tripwires`, cleared by the
    same surface-keyed ``Hit: <surface> <label>`` block — see the registry's
    header for why this family is gated rather than a hard block.

    TWO passes, and the second is not redundant:

    * a per-line pass over the folded line (:func:`_fold_ai_confusables`),
      which is what produces the reported line number and snippet;
    * a whitespace-removed pass over the whole surface
      (:func:`_dewrap_with_line_map`), MENTION-tier rows only, which catches a
      token split across a wrapped line.

    The dewrapped pass reports a label only when the per-line pass did not
    already find it, so a token written normally yields ONE row rather than
    two. It is a de-duplication of the REPORT only: both passes key the same
    label, so one justification block clears either.

    Justification-protocol lines are skipped, for the same convergence reason
    :func:`scan_text_for_tripwires` skips them — a block clearing this family
    necessarily spells the label it clears.
    """
    hits: list[TextHit] = []
    kept: list[tuple[int, str]] = []
    seen_labels: set[str] = set()
    for idx, raw in enumerate(text.splitlines(), start=1):
        if _is_justification_protocol_line(raw):
            continue
        kept.append((idx, raw))
        masked = _mask_ai_artifacts(raw)
        for label, compiled in _COMPILED_AI_ATTRIBUTION:
            # The mention tier reads the text with this repository's own
            # artifact names blanked; every other row reads it verbatim. See
            # :data:`_AI_ARTIFACT_NAMES` for why the split is what keeps the
            # carve-out from becoming a container.
            subject = masked if label in AI_MENTION_TIER_LABELS else raw
            if not any(compiled.search(variant) for variant in _ai_variants(subject)):
                continue
            seen_labels.add(label)
            hits.append(
                TextHit(
                    surface=surface,
                    line=idx,
                    pattern_label=label,
                    snippet=raw.rstrip("\n"),
                )
            )

    # Only the mention tier runs dewrapped, so the whole dewrapped subject is
    # masked (see :data:`_AI_ARTIFACT_NAMES`).
    masked_kept = [(n, _mask_ai_artifacts(r)) for n, r in kept]
    for dewrapped, line_of in (
        _dewrap_with_line_map(masked_kept),
        _dewrap_with_line_map([(n, _fold_ai_confusables(r)) for n, r in masked_kept]),
    ):
        for label, compiled in _COMPILED_AI_ATTRIBUTION:
            if label not in AI_MENTION_TIER_LABELS or label in seen_labels:
                continue
            match = compiled.search(dewrapped)
            if match is None:
                continue
            seen_labels.add(label)
            lineno = line_of[match.start()] if line_of else 1
            hits.append(
                TextHit(
                    surface=surface,
                    line=lineno,
                    pattern_label=label,
                    snippet=(
                        "(token spans a line break or whitespace) "
                        + dict(kept).get(lineno, "").rstrip()
                    ),
                )
            )
    return hits


def _is_hit_line(line: str) -> bool:
    """True for a ``Hit:`` line in any of the three accepted forms."""
    return bool(
        _CONTENT_HIT_LINE_RE.match(line)
        or _HIT_LINE_RE.match(line)
        or _TEXT_HIT_LINE_RE.match(line)
    )


def _iter_justified_hit_lines(pr_body: str) -> Iterable[str]:
    """Yield every ``Hit:`` line whose block is well-formed.

    A block is well-formed when a ``Hit:`` line — in EITHER the diff form
    (``<path>:<line> <label>``) or the text-surface form
    (``<surface> <label>``) — is followed within the next four non-empty
    lines by both a ``Rule:`` line and a ``Justification:`` line. The window is
    generous enough to allow blank-line spacing inside a block but tight enough
    that two unrelated ``Hit:`` lines don't accidentally pair up.

    A ``Hit:`` line WITHOUT a paired ``Rule:`` and ``Justification:`` is
    silently dropped — the author hasn't actually justified the hit, so the
    surrounding gate treats it as unjustified and fails.

    Shared by :func:`parse_justifications` and
    :func:`parse_text_justifications` so the two forms cannot drift into two
    definitions of "well-formed".
    """
    lines = pr_body.splitlines()
    for idx, line in enumerate(lines):
        if not _is_hit_line(line):
            continue
        policy_seen = False
        justification_seen = False
        non_empty_seen = 0
        for follow in lines[idx + 1 : idx + 12]:
            stripped = follow.strip()
            if not stripped:
                continue
            non_empty_seen += 1
            if _POLICY_LINE_RE.match(follow):
                policy_seen = True
            elif _JUSTIFICATION_LINE_RE.match(follow):
                justification_seen = True
            elif _is_hit_line(follow):
                # Next Hit block started — stop scanning this one.
                break
            if non_empty_seen >= 4:
                break
        if policy_seen and justification_seen:
            yield line


def parse_justifications(pr_body: str) -> list[Justification]:
    """Pull every well-formed DIFF-surface justification block out of a PR body.

    See :func:`_iter_justified_hit_lines` for what "well-formed" means. Text
    surface blocks (``Hit: <surface> <label>``) are parsed by
    :func:`parse_text_justifications` instead; they do not match
    :data:`_HIT_LINE_RE` because a surface token carries no ``:<line>``.
    """
    justifications: list[Justification] = []
    for line in _iter_justified_hit_lines(pr_body):
        content_match = _CONTENT_HIT_LINE_RE.match(line)
        if content_match is not None:
            justifications.append(
                Justification(
                    path=content_match.group("path"),
                    line=0,
                    pattern_label=content_match.group("pattern").strip(),
                    content_hash=content_match.group("hash").lower(),
                )
            )
            continue
        hit_match = _HIT_LINE_RE.match(line)
        if hit_match is None:
            continue
        justifications.append(
            Justification(
                path=hit_match.group("path"),
                line=int(hit_match.group("line")),
                pattern_label=hit_match.group("pattern").strip(),
            )
        )
    return justifications


def parse_text_justifications(pr_body: str) -> set[str]:
    """Return the set of TEXT-surface justification keys in the PR body (#5615).

    Each key is ``"<surface> <label>"`` — see :meth:`TextHit.justification_key`.
    One block therefore clears EVERY occurrence of that label on that surface,
    which is the intended granularity: a text surface is one authored blob under
    one author's control, and the declaration being made is "my prose names this
    token, here is why", not a per-line claim.
    """
    keys: set[str] = set()
    for line in _iter_justified_hit_lines(pr_body):
        match = _TEXT_HIT_LINE_RE.match(line)
        if match is None:
            continue
        keys.add(f"{match.group('surface')} {match.group('pattern').strip()}")
    return keys


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------
def find_unjustified(
    hits: Sequence[Hit], justifications: Sequence[Justification]
) -> list[Hit]:
    """Return the hits that lack a matching justification block.

    A block matches by file plus the line's content (:meth:`Hit.content_key`,
    preferred) or by the legacy ``<path>:<line>`` key (:meth:`Hit.justification_key`).
    """
    justified_keys = {j.key() for j in justifications}
    return [
        hit
        for hit in hits
        if hit.content_key() not in justified_keys
        and hit.justification_key() not in justified_keys
    ]


def render_report(unjustified: Sequence[Hit]) -> str:
    """Operator-facing failure report listing each unjustified hit."""
    lines = [
        "audit-grep tripwire (#1546): unjustified diff hit(s).",
        "",
        "Each occurrence below matches a pattern from CONTRIBUTING.md",
        '§ "Pre-merge audit grep". Confirm the hit is legitimate, then',
        "add a justification block to the PR body of the form:",
        "",
        "    Hit: <path>#<hash> <pattern>",
        '    Rule: CONTRIBUTING.md "<which rule>"',
        "    Justification: <one-line reason — cite the test that proves it>",
        "",
        "Use the `Hit:` line printed under each hit below: <hash> is of the",
        "line's content, so lines added above it do not void the block (#7126).",
        "The older `Hit: <path>:<line> <pattern>` form is still accepted but",
        "goes stale on any line shift.",
        "",
        "If a hit cannot be justified, fix the underlying issue and push",
        "again. Do not work around the gate.",
        "",
        "Unjustified hits:",
    ]
    for hit in unjustified:
        lines.append(f"  {hit.path}:{hit.line} {hit.pattern_label}    {hit.snippet}")
        lines.append(f"      Hit: {hit.content_key()}")
    lines.append("")
    return "\n".join(lines)


def render_text_tripwire_report(
    hits: Sequence[TextHit], *, advisory: bool = False
) -> str:
    """Operator-facing report for tripwire patterns in commit messages / PR text.

    Unlike :func:`render_report`, the justification block this asks for names a
    SURFACE and no line number — a text-surface key is label-scoped so it does
    not go stale when a rebase or a body edit moves the line (#5615).

    The message leads with "rephrase" rather than "justify": a commit body or PR
    description almost never NEEDS to spell a banned token, and rewording is
    cheaper for a reader than a justification block. The block is the escape
    hatch for the case where the token genuinely must be quoted.

    ``advisory`` (#5645) switches the header from a hard-failure verdict to a
    non-blocking WARNING, for a caller that has no PR body to justify against
    (scripts/preflight.sh, pre-push). The remediation guidance below is
    identical either way — the difference is only that an advisory run does not
    fail, and says so, while CI (which has the PR body) still blocks.
    """
    if advisory:
        header = [
            "audit-grep tripwire (#5615) — ADVISORY (#5645): the PR's commit",
            "messages / title / body name banned token(s). This is a WARNING,",
            "NOT a failure: this gate runs before the PR exists, so there is no",
            "PR body to justify these against and it does not block on them. CI",
            "DOES have the PR body and WILL block unless each is reworded or",
            "cleared by a justification block — resolve it now to avoid a red CI.",
        ]
    else:
        header = [
            "audit-grep tripwire (#5615): unjustified hit(s) in the PR's commit",
            "messages / title / body.",
        ]
    lines = [
        *header,
        "",
        "These surfaces ship with the repository but produce no diff, so until",
        "#5615 nothing scanned them for this pattern family — three such",
        "mentions were caught by hand on #5612. Each occurrence below matches a",
        'pattern from CONTRIBUTING.md § "Pre-merge audit grep".',
        "",
        "Fix, in order of preference:",
        "  1. REPHRASE so the token is not spelled (reword the commit, or edit",
        '     the PR body) — e.g. "a type-checker suppression comment" instead',
        "     of the literal. This is what #5612 did.",
        "  2. If the token genuinely must be quoted, add ONE block to the PR",
        "     body per surface + pattern:",
        "",
        "         Hit: <surface> <pattern>",
        '         Rule: CONTRIBUTING.md "<which rule>"',
        "         Justification: <one-line reason>",
        "",
        f"     <surface> is {TEXT_SURFACE_COMMITS} or {TEXT_SURFACE_PR}.",
        "     There is NO line number in a text-surface block: the key is the",
        "     surface + pattern, so it survives a rebase or a body edit, and one",
        "     block clears every occurrence of that pattern on that surface.",
        "",
        "Unjustified hits:",
    ]
    for hit in hits:
        lines.append(f"  {hit.surface}:{hit.line} {hit.pattern_label}    {hit.snippet}")
    lines.append("")
    return "\n".join(lines)


def render_customer_name_report(hits: Sequence[Hit]) -> str:
    """Operator-facing failure report for re-introduced customer names (#2374).

    Unlike :func:`render_report`, this carries NO "add a justification block"
    affordance — a proprietary customer name in core cannot be justified. The
    only resolution is to remove the name (and move any retailer-specific
    material to the private ``elastic/prism-<retailer>`` repo).

    The hit may be on a ``*.md`` line since #8019, so the message says
    "documentation included" rather than naming code alone — an author whose
    hit is in a doc must not read the report as a false positive.
    """
    lines = [
        "audit-grep customer-name guard (#2374): scrubbed customer name(s)",
        "re-introduced into the repository.",
        "",
        "A SCRUBBED customer name must not appear anywhere in this repository —",
        "DOCUMENTATION included, not only code (#8019) — because it is the one",
        "string that identifies them as a PRISM customer, and proprietary",
        "specifics belong in the private elastic/prism-<retailer>",
        "customization repo, never in elastic/prism. See CONTRIBUTING.md",
        '§ "Generalize, don\'t fork per customer" (core is never written FOR a',
        "named retailer) and issues #2374 / #3135. This guard matches the",
        "CUSTOMER names only — a retailer or brand name in public open-data",
        "demo content is not what it looks for.",
        "",
        "THAT SENTENCE IS SCOPED, and the scope decides what you do next. It",
        "is true of a name this repository SCRUBBED and holds at zero. A",
        "customization whose name the repository still ships is NOT covered by",
        "it: this guard matches the rows in CONTRIBUTING.md",
        '\u00a7 "Customer-name guard" and nothing wider, and the same',
        "subsection states, per row, what it deliberately does NOT cover (#9247).",
        "For the industrial registrant that includes its sister repo's",
        "contiguous slug in a repo path, which is legitimate and is not matched",
        "here. Its abbreviation on its own IS matched (#10626), in an index name",
        "or a profile name too.",
        "So: remove the name your hit reports. Do NOT scrub a repo path you were",
        "not asked about.",
        "",
        "This hit cannot be justified in the PR body — remove the name (move any",
        "retailer-specific material to the private customization repo).",
        "",
        "Customer-name hits:",
    ]
    for hit in hits:
        lines.append(f"  {hit.path}:{hit.line} {hit.pattern_label}    {hit.snippet}")
    lines.append("")
    return "\n".join(lines)


def render_frozen_derivation_report(hits: Sequence[Hit]) -> str:
    """Operator-facing failure report for a NEW dual-derivation site (#3022).

    Like :func:`render_customer_name_report`, this carries NO "add a
    justification block" affordance — a frozen hit is a HARD block. The
    resolution is to READ the fact off the Engine emit (or EXTEND the emit to
    carry it), never re-derive it. Each hit surfaces its rule's teaching line
    and the issue that retires the freeze. The one reviewable escape hatch —
    for a legitimate move of an EXISTING reader as its cleanup issue lands — is
    editing the pattern's allowlist in this script, which the message names.
    """
    lines = [
        "audit-grep dual-derivation freeze (#3022): a NEW site re-derives a",
        "fact the Engine response / emit already carries.",
        "",
        "This is the codebase's most recurrent bug class — two derivations of",
        "one truth (#1932 chip cutover, #3004 sidebar sidecars, #3006 fold",
        "mirror, #3011 verdict mirror). Each pattern below is frozen to its",
        "current sites (tracked for removal); a NEW reader is not allowed.",
        "",
        "This is a HARD block — do NOT add a justification block. Instead:",
        "  - READ the fact off the Engine emit (or EXTEND the emit to carry",
        "    it), never re-derive it. See contributing/single-source-of-truth.md",
        '    § "Recurrence casebook" and the CONTRIBUTING_REVIEW.md checklist',
        '    item #1 ("does this DERIVE a fact the Engine emit already carries?").',
        "  - If this is a legitimate move of an EXISTING reader (e.g. the",
        "    retiring cleanup issue is landing), add the path to the pattern's",
        "    allowlist in .github/scripts/audit_grep_diff.py in THIS PR, with",
        "    the retiring-issue comment — a reviewable, diff-visible act.",
        "",
        "New-site hits:",
    ]
    for hit in hits:
        spec = _FROZEN_SPEC_BY_LABEL.get(hit.pattern_label)
        lines.append(f"  {hit.path}:{hit.line} {hit.pattern_label}    {hit.snippet}")
        if spec is not None:
            lines.append(f"      -> {spec.teaching} (frozen until {spec.retires})")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    """The gate's option inventory, as an OBJECT a caller can enumerate.

    Split out of ``main`` for #7705. ``tests/test_audit_grep_diff.py`` asserts
    that ``scripts/preflight.sh`` passes no FEWER flags than the CI workflow,
    and it derived the option inventory from this script's ``--help`` text. Two
    kinds of option are invisible there: one registered with
    ``help=argparse.SUPPRESS`` (absent from ``--help`` by design, so no widening
    of a text scan can reach it) and one spelled with an underscore (the scan's
    character class stopped at the ``_`` and recorded a truncated phantom). In
    both cases the flag fell outside the derived set, the comparison dropped it,
    and the test reported PASS while preflight was strictly shorter than the
    merge gate. The parser itself has neither blind spot, so the test reads
    this instead.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Run CONTRIBUTING.md's audit-grep patterns over a PR diff and "
            "verify each hit is justified in the PR body. See issue #1546."
        )
    )
    parser.add_argument(
        "--diff-file",
        type=Path,
        help="Path to a file containing the unified diff. Reads stdin if omitted.",
    )
    parser.add_argument(
        "--pr-body-file",
        type=Path,
        default=None,
        help=(
            "Path to a file containing the PR body. Scanned for justification "
            "blocks AND (with --pr-title) for scrubbed customer names. Optional "
            "so a commit-message-only invocation (the commit-msg hook) can omit "
            "it; when omitted the body is treated as empty."
        ),
    )
    parser.add_argument(
        "--pr-author",
        type=str,
        default="",
        help=(
            "The PR author's login, read from the API by the caller (#11227). For "
            "a login on BOT_AUTHOR_LOGINS the vendor-name and tripwire families "
            "skip the bot's quoted <details> release-notes blocks in the body; "
            "the title, the diff and body text outside those blocks are still "
            "judged. Defaults to empty, which is a person."
        ),
    )
    parser.add_argument(
        "--pr-title",
        type=str,
        default="",
        help=(
            "The PR title. Scanned together with the PR body for scrubbed "
            "customer names (#3135). Defaults to empty."
        ),
    )
    parser.add_argument(
        "--commit-messages-file",
        type=Path,
        default=None,
        help=(
            "Path to a file containing the concatenated commit messages on the "
            "PR. Scanned for scrubbed customer names (#3135) — closes the leak "
            "path a diff scan cannot see (a name in a commit subject/body). "
            "Optional; when omitted, no commit-message scan runs."
        ),
    )
    parser.add_argument(
        "--min-commits",
        type=int,
        default=0,
        help=(
            "The number of commits in the range the --commit-messages-file was "
            "built from. The gate refuses (exit 3, NOTHING WAS SCANNED) when the "
            "surface cannot account for that many, instead of publishing the "
            "green an unread surface always produces (#9225). Same flag name and "
            "same meaning as check_closing_keywords.py's, which reads the same "
            "commits from the same workflow step; the MECHANISM differs because "
            "the input does -- that gate parses NUL-terminated records and can "
            # argparse %-expands a help string, so the literal % below is
            # doubled. Python 3.14's add_argument validates this eagerly:
            # a single %B raises 'badly formed help string' at PARSER BUILD
            # time, before any argument is read, so every invocation of the
            # script fails -- including the ones that pass no flags at all.
            "count them, this one takes a flat --format='%%B' concatenation "
            "and "
            "can only floor the newline count (see "
            "count_commit_message_separators). Default 0, NOT 1: "
            "--commit-messages-file is itself optional, the commit-msg "
            "pre-commit hook passes exactly one message with no range to assert, "
            "and a commit made with --allow-empty-message legitimately writes a "
            "0-newline surface -- so a default floor would red callers that are "
            "behaving correctly. The two automated callers that DO compute a "
            "range (the audit-grep workflow and scripts/preflight.sh) pass it."
        ),
    )
    parser.add_argument(
        "--scan-text-tripwires",
        action="store_true",
        help=(
            "Also run the justification-gated PATTERN_SPECS family AND the "
            "AI_ATTRIBUTION_SPECS family (#8331) over the commit messages and "
            "the PR title/body (#5615), not just the diff. Both families ride "
            "this one flag deliberately: a second flag is a second thing a "
            "caller can omit, and the defect #8331 closed was a surface nobody "
            "had noticed was unscanned. Opt-in because the commit-msg "
            "pre-commit hook calls this script before a PR body exists, and a "
            "hit there could not be cleared; that surface is covered at commit "
            "time by scripts/check_attribution.sh --file instead. The CI "
            "workflow and scripts/preflight.sh both pass it; that hook is the "
            "only caller that does not."
        ),
    )
    parser.add_argument(
        "--text-tripwires-advisory",
        action="store_true",
        help=(
            "Report unjustified TEXT-surface tripwires (the commit-message and "
            "PR-title/body #5615 family) as a non-blocking WARNING instead of a "
            "hard failure (#5645). For a caller that has NO PR body to justify "
            "against — scripts/preflight.sh, which runs before the PR exists. "
            "Their only clearing surface is a PR-body justification block that "
            "does not exist yet, so a hard failure there is a false red whose "
            "only local remedy is a history rewrite, while CI (which has the PR "
            "body) would pass. Narrowly scoped: the diff-surface justification "
            "family and the HARD customer-name / dual-derivation guards — which "
            "have no PR-body clearing surface anywhere — still block. CI does "
            "NOT pass this flag, so its enforcement is unchanged. A run in "
            f"which advisories SURVIVE exits {ADVISORY_EXIT_STATUS}, not 0 "
            "(#7647) — non-blocking, but distinguishable by STATUS from "
            "'nothing to say', so a caller cannot render it as a bare PASS "
            "and discard the warning."
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.diff_file is not None:
        diff_text = args.diff_file.read_text(encoding="utf-8", errors="replace")
    else:
        diff_text = sys.stdin.read()
    if args.pr_body_file is not None:
        pr_body = args.pr_body_file.read_text(encoding="utf-8", errors="replace")
    else:
        pr_body = ""

    added = parse_diff_added_lines(diff_text)
    # The customer-name guard reads a WIDER diff surface than every other
    # family: the same diff parsed with ``*.md`` added lines KEPT (#8019). A
    # doc can only mention a code telltale, but it can USE a retailer's name.
    # Parsed as a second list rather than filtered from the first so no family
    # can be handed the other's surface by an argument slip.
    added_including_markdown = parse_diff_added_lines(diff_text, include_markdown=True)

    # Customer-name guard (#2374, hardened #3135): a HARD block, evaluated FIRST
    # over every surface and independent of the PR-body justification machinery.
    # A proprietary customer name has no legitimate use, so a hit fails the job
    # outright — there is nothing to justify and no early short-circuit may skip
    # it. Three surfaces are scanned with the SAME obfuscated regex:
    #
    #   1. commit messages on the PR (a name in a commit subject/body — invisible
    #      to a diff scan; the #3135 history-scrub leak path),
    #   2. the PR title + body (a name in the PR description — likewise unseen by
    #      the diff scan),
    #   3. the diff added lines, INCLUDING ``*.md`` (the original #2374
    #      surface, widened to Markdown in #8019).
    commit_text: str | None = None
    if args.commit_messages_file is not None:
        commit_text = args.commit_messages_file.read_text(
            encoding="utf-8", errors="replace"
        )
        commit_text = _commit_surface_text(commit_text)
    pr_text = f"{args.pr_title}\n{pr_body}"

    # THE COMMIT SURFACE HAS TO ARRIVE BEFORE ANY VERDICT IS PUBLISHED OVER IT
    # (#9225). Evaluated here — after the surfaces are read, before the first
    # scan — because a refusal that came AFTER a family had already printed
    # would be a second opinion on a verdict the reader has already seen. Four
    # families read this surface and nothing else reads it, two of them
    # unclearable hard blocks whose remedy in permanent history is a rewrite;
    # the defect being closed is that a 0-byte file took all four from "every
    # commit on the branch" to "nothing" with no change to the verdict, the exit
    # code, or the text a reviewer sees.
    #
    # Only a caller that asserted a range can be refused. An ad-hoc caller who
    # points the flag at the wrong file asserts nothing, and for them the remedy
    # is the extent line below, which SAYS what was read.
    separators = (
        0 if commit_text is None else count_commit_message_separators(commit_text)
    )
    if args.min_commits > 0 and (commit_text is None or separators < args.min_commits):
        sys.stderr.write(
            render_commit_surface_refusal(commit_text, args.min_commits, separators)
        )
        return UNSCANNABLE_EXIT_STATUS

    # What this run actually read, on every run that reaches a verdict — green,
    # red or advisory. See :func:`render_scanned_extent`.
    sys.stdout.write(
        render_scanned_extent(
            diff_text=diff_text,
            added_lines_with_markdown=len(added_including_markdown),
            added_lines=len(added),
            commit_text=commit_text,
            min_commits=args.min_commits,
            pr_title=args.pr_title,
            pr_body_supplied=args.pr_body_file is not None,
            pr_body=pr_body,
        )
    )

    # Invisible-character refusal (#8715), evaluated FIRST and over the RAW
    # surfaces. Also a HARD block, for the reason stated at
    # :func:`scan_text_for_invisible_characters`.
    #
    # BEFORE the customer-name guard, deliberately: one zero-width character
    # inside the name takes that guard from 1 hit to 0, so a surface that
    # carries one has to be refused before its verdict is read. It rides no
    # opt-in flag for the same reason -- the commit-msg pre-commit hook (which
    # passes neither ``--scan-text-tripwires`` nor a PR body) is the caller
    # where the remedy is still an edit rather than a history rewrite, and it
    # is the caller that must not be able to skip this.
    invisible_hits: list[InvisibleCharacterHit] = []
    invisible_surface = ""
    if commit_text is not None:
        invisible_hits = scan_text_for_invisible_characters(
            commit_text, TEXT_SURFACE_COMMITS
        )
        invisible_surface = "commit messages"
    if not invisible_hits:
        # ``allow_mention_suppression`` is the one narrow allowance and it is
        # PR-surface-only; the header records the measurement behind both
        # halves of that.
        invisible_hits = scan_text_for_invisible_characters(
            pr_text, TEXT_SURFACE_PR, allow_mention_suppression=True
        )
        invisible_surface = "the PR title/body"
    if invisible_hits:
        sys.stderr.write(
            render_invisible_character_report(invisible_hits, invisible_surface)
        )
        return 1

    if commit_text is not None:
        commit_hits = scan_text_for_customer_names(commit_text, TEXT_SURFACE_COMMITS)
        if commit_hits:
            sys.stderr.write(
                render_text_customer_name_report(commit_hits, "commit messages")
            )
            return 1

    pr_text_hits = scan_text_for_customer_names(pr_text, TEXT_SURFACE_PR)
    if pr_text_hits:
        sys.stderr.write(
            render_text_customer_name_report(pr_text_hits, "the PR title/body")
        )
        return 1

    customer_name_hits = scan_for_customer_names(added_including_markdown)
    if customer_name_hits:
        sys.stderr.write(render_customer_name_report(customer_name_hits))
        return 1

    # Dual-derivation freeze (#3022): also a HARD block, evaluated next and
    # independent of the PR-body justification machinery. A NEW reader of a
    # fact the Engine emit already carries is the codebase's most recurrent
    # bug class; the reviewable escape hatch is editing the spec allowlist, not
    # a pasted justification, so a hit fails the job with a teaching message.
    frozen_hits = scan_for_frozen_derivations(added)
    if frozen_hits:
        sys.stderr.write(render_frozen_derivation_report(frozen_hits))
        return 1

    # Gate A (#7162): a NEW client-composed string on the facet row disclosure
    # surface. A HARD block for the same reason the freeze above is one — the
    # reviewable escape hatch is editing the allowlist, and a string the
    # producer cannot see is a string no producer-side fix can correct. Placed
    # after the freeze and before the justification-gated pool so its report is
    # the only thing an author reads when it fires.
    client_string_hits = scan_for_client_composed_strings(added)
    if client_string_hits:
        sys.stderr.write(render_client_composed_string_report(client_string_hits))
        return 1

    # The justification-gated family, over every surface it covers. Both
    # surfaces are reconciled and BOTH reports print before returning: a run
    # that failed on the diff and also has a commit-message hit should say so
    # once, not make the author discover the second half on the next push.
    # The companion-required family (#6116) joins the same justification-gated
    # pool. It is the only family that needs more than one line to decide, so it
    # reads the diff a second time as HUNKS (see :func:`parse_diff_hunks`); its
    # hits are ordinary :class:`Hit` objects from there on, cleared by the same
    # ``Hit:`` / ``Rule:`` / ``Justification:`` block as every other row.
    hits = scan_for_hits(added) + scan_for_companion_required(
        parse_diff_hunks(diff_text)
    )
    unjustified = find_unjustified(hits, parse_justifications(pr_body))

    # Text surfaces (#5615) — opt-in; see the ``--scan-text-tripwires`` help.
    text_hits: list[TextHit] = []
    if args.scan_text_tripwires:
        if commit_text is not None:
            text_hits.extend(scan_text_for_tripwires(commit_text, TEXT_SURFACE_COMMITS))
            # The AI-attribution family (#8331) rides the SAME flag and the same
            # surfaces. It is wired here, beside the family it joins, rather than
            # behind a flag of its own: a second flag is a second thing a caller
            # can omit, and the defect this closes was a surface nobody had
            # noticed was unscanned. ``tests/test_audit_grep_diff.py::
            # TestTextTripwireWiring`` pins the three callers by name, so a
            # caller that stops passing the flag reds there.
            text_hits.extend(
                scan_text_for_ai_attribution(commit_text, TEXT_SURFACE_COMMITS)
            )
        # The vendor-name families judge what the author wrote: for the update bot
        # that excludes the upstream release notes it quotes (#11227). The
        # customer-name guard and the invisible-character refusal above read the
        # whole text.
        judged_text = (
            f"{args.pr_title}\n{strip_bot_quoted_blocks(pr_body, args.pr_author)}"
        )
        text_hits.extend(scan_text_for_tripwires(judged_text, TEXT_SURFACE_PR))
        text_hits.extend(scan_text_for_ai_attribution(judged_text, TEXT_SURFACE_PR))
    text_keys = parse_text_justifications(pr_body)
    unjustified_text = [h for h in text_hits if h.justification_key() not in text_keys]

    # A text-surface tripwire is BLOCKING by default, but ADVISORY (a warning,
    # non-fatal) when the caller declares it has no PR body to justify against
    # (#5645). Their sole clearing surface is a PR-body justification block that
    # does not exist pre-push, so scripts/preflight.sh would otherwise hard-red a
    # commit message CI clears — a false red whose only local remedy is a history
    # rewrite. The diff-surface family and the HARD guards are untouched: they
    # either have a local remedy (edit the added line) or no clearing surface
    # anywhere (a customer name), so neither is downgraded.
    text_blocks = bool(unjustified_text) and not args.text_tripwires_advisory

    if unjustified:
        sys.stderr.write(render_report(unjustified))
    if unjustified_text:
        sys.stderr.write(
            render_text_tripwire_report(
                unjustified_text, advisory=args.text_tripwires_advisory
            )
        )
    if unjustified or text_blocks:
        return 1

    # Reaching here means nothing BLOCKS. If unjustified text tripwires survived,
    # they were downgraded to advisories above (#5645) — the WARNING already
    # printed. Report an honest green-with-advisories verdict rather than the
    # "all justified in PR body" line, which would be a lie: nothing justified
    # them, this caller simply cannot evaluate that surface.
    if unjustified_text:
        print(
            f"audit-grep: {len(unjustified_text)} text tripwire(s) reported as "
            "ADVISORY — no PR body exists here to justify them against, so this "
            "gate does not block on them (#5645). The diff scan and the hard "
            "customer-name / dual-derivation guards are green. CI, which has the "
            "PR body, still requires each to be reworded or cleared by a "
            "justification block."
        )
        # Exit ADVISORY_EXIT_STATUS, not 0. Nothing BLOCKS, but the
        # caller owes its author this warning, and an exit-0 verdict is
        # indistinguishable from "nothing to say" to a caller that only reads
        # the status (#7647).
        return ADVISORY_EXIT_STATUS

    total = len(hits) + len(text_hits)
    if not total:
        print("audit-grep: no tripwire hits in diff or PR text; gate green.")
        return 0
    print(f"audit-grep: {total} hit(s) all justified in PR body; gate green.")
    return 0


if __name__ == "__main__":  # pragma: no cover - thin CLI wrapper
    sys.exit(main())
