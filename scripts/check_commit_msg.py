"""Refuse a commit message that credits an AI tool or a bot.

    python scripts/check_commit_msg.py <commit-message-file>     # the commit-msg hook
    python scripts/check_commit_msg.py --range origin/main..HEAD  # CI, over a PR's commits

The PRISM repositories carry no AI or bot attribution in commits: no co-author
trailer naming one, no "generated with" footer, no assistant named in the
message.

ONE LIST, NOT A FOURTH. :data:`CORE_FAMILY` is elastic/prism's AI-attribution
family (``AI_ATTRIBUTION_SPECS`` in ``.github/scripts/audit_grep_diff.py``),
copied VERBATIM at core commit :data:`CORE_SOURCE` -- this repository's CI cannot
read that private repository, so it is vendored rather than fetched, and its
provenance is recorded so a resync is a diff against a named commit.
:data:`ADDITIONS` are the gaps a review of this repository found that the core
family does not cover (Aider, Codex, Windsurf, Gemini, ``Assisted-by:``, bare
model names). They are candidates to upstream into the core family, not a
second standard.

Matching runs over the message folded the way the core scan folds it: NFKC,
zero-width characters removed, case-insensitive. The agent-instructions file
name is masked as the core scan masks it (:func:`mask_file_name`), and, as in
the core scan, only for the vendor-name row (core masks only the
``AI_MENTION_TIER_LABELS``): a commit that edits that file may say so. Every
shape row (a co-author trailer, "generated with", "made with") reads the
unmasked line, so ``Co-Authored-By: CLAUDE.md`` still fails.
"""

from __future__ import annotations

import re
import subprocess
import sys
import unicodedata
from pathlib import Path

#: The core commit the family below was copied from.
CORE_SOURCE = "elastic/prism@7f961d6d7 .github/scripts/audit_grep_diff.py AI_ATTRIBUTION_SPECS"

CORE_FAMILY: list[tuple[str, str]] = [
    ("ai-vendor-name", r"claude|anthropic|copilot|chatgpt|openai"),
    ("robot-emoji", "\U0001f916"),
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

#: Gaps the core family leaves, found reviewing this repository's hook.
ADDITIONS: list[tuple[str, str]] = [
    ("tool-name", r"\b(?:aider|codex|windsurf|gemini)\b"),
    ("assisted-by-trailer", r"^\s*assisted[- ]by\s*:"),
    ("coauthor-bot-account", r"co-?authored[- ]?by\s*:?[^\n]*\[bot\]"),
    ("model-name", r"\b(?:opus|sonnet|haiku|gpt-?\d[\w.]*|o\d-(?:mini|preview))\b"),
    ("anthropic-noreply", r"noreply@anthropic\.com"),
]

FAMILY = [(label, re.compile(rx, re.IGNORECASE | re.MULTILINE)) for label, rx in CORE_FAMILY]
FAMILY += [(label, re.compile(rx, re.IGNORECASE | re.MULTILINE)) for label, rx in ADDITIONS]

#: Characters that change nothing a reader sees: zero-width and soft-hyphen
#: characters, and the bidirectional controls (embeddings, overrides,
#: isolates), which can reorder a word on screen without changing its letters.
_INVISIBLE = dict.fromkeys(
    map(
        ord,
        "​‌‍⁠﻿­‎‏‪‫‬‭‮⁦⁧⁨⁩",
    )
)
#: Cyrillic and Greek letters that look like Latin ones, folded to them as the
#: core scan does, so a vendor name spelled with look-alikes still matches.
_HOMOGLYPHS = str.maketrans(
    "аеорсухіјкмтнвАЕОРСХКМТНВοαρεΟΑΡΕ",
    "aeopcyxijkmthbAEOPCXKMTHBoapeOAPE",
)


def fold(text: str) -> str:
    return unicodedata.normalize("NFKC", text).translate(_INVISIBLE).translate(_HOMOGLYPHS)


#: The agent-instructions file name, in a path with or without a directory:
#: ``CLAUDE.md``, ``docs/CLAUDE.md``, ``./CLAUDE.md``. Only the file name is
#: masked, in capitals and exactly: the directories stay in the text and are
#: matched like any other words, a glued prefix (``notCLAUDE.md``) or a longer
#: extension (``CLAUDE.mdx``) is not the file, and a vendor name beside it is
#: not masked, so ``Claude wrote CLAUDE.md`` still fails on ``Claude``.
_AGENT_FILE = re.compile(r"(?<![\w.-])CLAUDE\.md(?![\w-])")
_MASK = "<file>"
#: The one row that reads the masked text.
_MASKED_LABEL = "ai-vendor-name"


def mask_file_name(text: str) -> str:
    """``text`` with every agent-instructions file name masked."""
    return _AGENT_FILE.sub(_MASK, text)


def _first_match(text: str) -> str | None:
    """The label of the first rule ``text`` trips, or None.

    The vendor-name row reads the text with the file name masked; every other
    row reads it as written, so a shape row still sees the file name.
    """
    masked = mask_file_name(text)
    for label, pattern in FAMILY:
        if pattern.search(masked if label == _MASKED_LABEL else text):
            return label
    return None


def problems(message: str, skip_comment_lines: bool = True) -> list[str]:
    """``label: text`` for every attribution found.

    ``skip_comment_lines`` is for the commit-msg HOOK only: git strips ``#``
    lines from the message it records, so there they are its own help text.
    A RECORDED message (``--range``) keeps whatever it carries --
    ``git commit -m "# Co-Authored-By: ..."`` stores the line -- so there
    nothing is skipped. A phrase wrapped across two lines is also caught: the
    message is checked once more with its lines joined.
    """
    lines = fold(message).splitlines()
    if skip_comment_lines:
        lines = [line for line in lines if not line.startswith("#")]
    found = []
    for line in lines:
        label = _first_match(line)
        if label:
            found.append(f"{label}: {line.strip()}")
    if not found:
        joined = " ".join(line.strip() for line in lines)
        label = _first_match(joined)
        if label:
            found.append(f"{label} (across lines): {joined[:80]}")
    return found


def _range_messages(spec: str) -> list[tuple[str, str]]:
    shas = subprocess.run(
        ["git", "rev-list", spec], capture_output=True, text=True, check=True
    ).stdout.split()
    if not shas:
        raise SystemExit(f"{spec!r} resolves to no commits; nothing was checked")
    return [
        (
            sha,
            subprocess.run(
                ["git", "log", "-1", "--format=%B", sha], capture_output=True, text=True, check=True
            ).stdout,
        )
        for sha in shas
    ]


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[1] == "--range":
        messages = _range_messages(argv[2])
        hook = False
    elif len(argv) == 2:
        messages = [("commit message", Path(argv[1]).read_text("utf-8"))]
        hook = True
    else:
        print("usage: check_commit_msg.py <file> | --range <git-range>", file=sys.stderr)
        return 2
    bad = 0
    for where, message in messages:
        for line in problems(message, skip_comment_lines=hook):
            print(f"{where}: AI/bot attribution -- {line}", file=sys.stderr)
            bad += 1
    print(f"checked {len(messages)} message(s): {'clean' if not bad else f'{bad} violation(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
