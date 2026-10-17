#!/usr/bin/env python3
"""The ONE definition of an INVISIBLE CHARACTER in this repository (#8649).

WHY THIS MODULE EXISTS
----------------------
Two pieces of machinery already knew about this character class and disagreed
about it. ``scripts/check_no_nul_bytes.py`` (now
:mod:`check_no_invisible_characters`) enforced *"spell the byte as an escape,
never embed it"* for exactly ONE codepoint, U+0000. ``.github/scripts/audit_grep_diff.py``
carried ``_AI_INVISIBLE_CHARS``, a hand-written string of six codepoints
(U+200B, U+200C, U+200D, U+2060, U+FEFF, U+00AD), stripped before its AI-attribution
scan so an inserted zero-width character could not split a banned token. Six is
not one, and neither is the class: U+00A0, the bidi overrides U+202A-U+202E and
every C0/C1 control were in neither.

Two spellings of one concept is the defect #8647 exists to close. So the class
is defined ONCE, here, and DERIVED rather than listed.

WHAT IS DERIVED, AND FROM WHAT
------------------------------
A character is INVISIBLE when its Unicode general category is one of
:data:`CATEGORIES` -- ``Cc`` (control), ``Cf`` (format), ``Zl`` (line
separator), ``Zp`` (paragraph separator) -- or it is a ``Zs`` space that is not
the plain ASCII space, MINUS the layout characters in :data:`ALLOWED`.

Derived, because a hand-maintained enumeration of this class has now failed
twice in this repository, in both available directions: ``check_no_nul_bytes``
listed one member of two hundred and fifty-three, and ``_AI_INVISIBLE_CHARS``
listed six. Nothing about either list said it was short. A category query
cannot be short.

:data:`ALLOWED` is the escape hatch and it is deliberately TINY: tab, newline
and carriage return are the layout characters a text file is built out of, and
a plain space. Everything else in the class is a character a reader cannot see,
a keyboard cannot type, and a diff cannot show -- which is the whole subject.
Note what is NOT in it: ``U+000C`` FORM FEED and ``U+000B`` VERTICAL TAB are
invisible under this definition, because they are, and this tree holds neither.

THE FAST PATH, AND WHY IT IS SOUND
----------------------------------
:func:`find` is called on every tracked file by the gate, so it must not cost a
per-character Python loop over a hundred megabytes. It pre-filters with
``str.isprintable()``, which is a C-level scan.

CPython defines a non-printable character as one whose category is ``Other``
(``Cc``, ``Cf``, ``Cs``, ``Co``, ``Cn``) or ``Separator`` (``Zs``, ``Zl``,
``Zp``), excepting the ASCII space. That set is a strict SUPERSET of this
module's class once :data:`ALLOWED` is removed from the text first -- it adds
the surrogate, private-use and unassigned codepoints, which this module does
NOT judge. A superset pre-filter can only send a clean file down the slow path,
never let a dirty one skip it, so the fast path cannot produce a false clean.
``TestTheDerivation.test_the_isprintable_fast_path_is_a_superset_of_the_class``
holds that property against an exhaustive walk of the codepoint space rather
than against this paragraph.

WHAT A CALLER DOES WITH A MEMBER
--------------------------------
Two different things, which is why :func:`has_no_advance_width` and
:func:`is_space_like` are separate from :func:`is_invisible`:

* A gate REFUSES it, and names the codepoint (:func:`describe`).
* A text-normalising scan FOLDS it -- and the two halves fold differently. A
  zero-width character is DELETED (removing it re-joins the token an attacker
  split); a space-like character becomes a plain SPACE (deleting it would weld
  two words together and destroy the very token the scan is looking for). That
  distinction is the reason ``audit_grep_diff`` could not simply widen its
  string: ``_AI_INVISIBLE_CHARS`` was a delete-list, and U+00A0 must not be
  deleted.
"""

from __future__ import annotations

import re
import sys
import unicodedata
from functools import lru_cache

#: General categories that are invisible outright.
#:
#: Pinned as an exact set by ``tests/test_no_invisible_character_gate_8423.py``:
#: an EQUALITY, never a membership, because a category dropped from this set
#: silently stops being judged and nothing else in the tree would say so.
CATEGORIES = frozenset({"Cc", "Cf", "Zl", "Zp"})

#: The ``Zs`` category is invisible EXCEPT for the plain ASCII space, which is
#: the one member of it a keyboard has a key for.
SPACING_CATEGORY = "Zs"

#: The layout characters a text file is legitimately built out of.
ALLOWED = frozenset({"\t", "\n", "\r", " "})


def is_invisible(ch: str) -> bool:
    """True when *ch* is an invisible character under this module's definition."""
    if ch in ALLOWED:
        return False
    category = unicodedata.category(ch)
    if category in CATEGORIES:
        return True
    return category == SPACING_CATEGORY


def has_no_advance_width(ch: str) -> bool:
    """True for an invisible character that occupies NO horizontal space.

    The half a normaliser DELETES. Removing one rejoins whatever it was
    inserted to split.
    """
    return is_invisible(ch) and unicodedata.category(ch) != SPACING_CATEGORY


def is_space_like(ch: str) -> bool:
    """True for an invisible character that reads on screen AS a space.

    The half a normaliser folds to ``" "``. Deleting one would weld the words
    on either side of it together, which destroys the token a scan is hunting
    rather than revealing it.
    """
    return is_invisible(ch) and unicodedata.category(ch) == SPACING_CATEGORY


def describe(ch: str) -> str:
    """One invisible character, named so a reader can act on it.

    ``U+2060 WORD JOINER``. A report that printed the character itself would
    print nothing, which is the failure mode this whole issue is about.

    The C0/C1 controls have no Unicode NAME -- ``unicodedata.name(chr(0))``
    raises -- so they fall back to their category. The CODEPOINT is the half a
    reader acts on either way: it is what they grep for and what tells them
    which escape to write.
    """
    try:
        name = unicodedata.name(ch)
    except ValueError:
        name = f"<unnamed, category {unicodedata.category(ch)}>"
    return f"U+{ord(ch):04X} {name}"


#: The PROSE spelling of an invisible codepoint: ``<U+2060>``.
#:
#: WHY THIS IS HERE AND NOT IN THE ONE FILE THAT WRITES IT. The gate's remedy
#: sends prose -- a comment, a docstring, a Markdown page -- to this notation
#: rather than to a language escape, because inside a non-raw Python docstring
#: an escape is not inert text, it IS the character. That makes the notation a
#: repository-wide CONVENTION, and a convention has readers: anything that scans
#: prose as DATA has to decode it or it stops matching.
#:
#: That is not a hypothetical. #8649's own respell replaced 22 literals in
#: ``docs/`` and ``specs/`` with this notation and took
#: ``tests/test_docs_vocab_composite_matches_emitter_8647.py`` -- a sweep that
#: re-derives every documented vocab composite from the emitter -- from 6 runs
#: to 0. Its vacuity guard caught it; nothing else would have. The decoder lives
#: here so the next such reader gets it from the same place the writer does,
#: instead of carrying a second copy of the convention.
NOTATION = re.compile(r"<U\+([0-9A-Fa-f]{4,6})>")


def notate(text: str) -> str:
    """*text* with every invisible character replaced by its ``<U+XXXX>`` form.

    The inverse of :func:`decode_notation` on this module's class. Rendering a
    string that holds one of these is otherwise a report that prints nothing,
    which is the failure mode the whole class is about.
    """
    return "".join(f"<U+{ord(ch):04X}>" if is_invisible(ch) else ch for ch in text)


def decode_notation(text: str) -> str:
    """*text* with every ``<U+XXXX>`` decoded back to the character it names.

    ONLY members of this module's class are decoded. A ``<U+0041>`` in prose is
    a mention of the letter A and is left exactly as written: decoding it would
    silently rewrite text that was never about an invisible character, which is
    a licence this helper has no reason to take.

    A value ABOVE ``U+10FFFF`` is left alone for a sharper reason than tidiness.
    ``chr()`` raises on it, and this helper runs over whole pages inside a test
    that scans the prose trees -- so ``<U+FFFFFF>`` written in a document about
    codepoints would not produce a wrong answer, it would produce a COLLECTION
    ERROR, and a suite that never ran reports zero findings in the vocabulary of
    a clean result.
    """

    def _one(match: re.Match[str]) -> str:
        value = int(match.group(1), 16)
        if value > sys.maxunicode:
            return match.group(0)
        ch = chr(value)
        return ch if is_invisible(ch) else match.group(0)

    return NOTATION.sub(_one, text)


def find(text: str) -> list[tuple[int, str]]:
    """Every ``(index, character)`` of *text* that is invisible, in order.

    The ``isprintable`` pre-filter is the fast path documented in this module's
    header: a superset test, so it can only skip a CLEAN file.
    """
    if text.translate(_ALLOWED_DROP).isprintable():
        return []
    return [(i, ch) for i, ch in enumerate(text) if is_invisible(ch)]


@lru_cache(maxsize=1)
def invisible_codepoints() -> frozenset[str]:
    """The whole derived class, as characters.

    Built by walking the codepoint space, which costs about a fifth of a second
    -- so it is LAZY and cached, and the gate's :func:`find` never needs it. The
    callers that do are the fold table in ``audit_grep_diff`` (built once per CI
    job) and the tests that pin the derivation.
    """
    return frozenset(
        chr(cp) for cp in range(sys.maxunicode + 1) if is_invisible(chr(cp))
    )


def members_between(low: int, high: int) -> frozenset[str]:
    """The class restricted to ``[low, high)`` -- the shape a pin is written as.

    A pin over the WHOLE class would move whenever the interpreter's Unicode
    version moves, which turns a real invariant into a version tripwire. A pin
    over a bounded window whose assignments have been stable for two decades is
    an equality that means something.
    """
    return frozenset(chr(cp) for cp in range(low, high) if is_invisible(chr(cp)))


_ALLOWED_DROP = str.maketrans(dict.fromkeys(ALLOWED - {" "}))
