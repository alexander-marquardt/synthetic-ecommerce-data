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
zero-width characters removed, case-insensitive.
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

_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿­"))


def fold(text: str) -> str:
    return unicodedata.normalize("NFKC", text).translate(_ZERO_WIDTH)


def problems(message: str) -> list[str]:
    """``label: line`` for every attributing line; git's ``#`` comment lines are skipped."""
    found = []
    for line in fold(message).splitlines():
        if line.startswith("#"):
            continue
        for label, pattern in FAMILY:
            if pattern.search(line):
                found.append(f"{label}: {line.strip()}")
                break
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
    elif len(argv) == 2:
        messages = [("commit message", Path(argv[1]).read_text("utf-8"))]
    else:
        print("usage: check_commit_msg.py <file> | --range <git-range>", file=sys.stderr)
        return 2
    bad = 0
    for where, message in messages:
        for line in problems(message):
            print(f"{where}: AI/bot attribution -- {line}", file=sys.stderr)
            bad += 1
    print(f"checked {len(messages)} message(s): {'clean' if not bad else f'{bad} violation(s)'}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
