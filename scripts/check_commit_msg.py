"""Refuse a commit message that credits an AI tool or a bot.

    python scripts/check_commit_msg.py <commit-message-file>

Run by the ``commit-msg`` hook in ``.pre-commit-config.yaml``. The PRISM
repositories carry no AI or bot attribution in commits: no co-author trailer
naming one, no "generated with" footer, no assistant named anywhere in the
message. The same rule is enforced in the sibling repositories' CI; this makes
the refusal local, before the commit exists.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

#: Lines a message may not contain, case-insensitively. Written as patterns
#: over the whole line so a trailer, a footer and a prose mention all match.
FORBIDDEN = (
    re.compile(r"co-authored-by:.*\b(claude|anthropic|chatgpt|openai|copilot|gemini|bot)\b", re.I),
    re.compile(r"generated (with|by) .*\b(claude|chatgpt|copilot|gemini|ai)\b", re.I),
    re.compile(r"\b(claude|anthropic|chatgpt|copilot)\b", re.I),
    re.compile(r"noreply@anthropic\.com", re.I),
)


def problems(message: str) -> list[str]:
    found = []
    for line in message.splitlines():
        if line.startswith("#"):
            continue  # git's own comment lines
        for pattern in FORBIDDEN:
            if pattern.search(line):
                found.append(line.strip())
                break
    return found


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: check_commit_msg.py <commit-message-file>", file=sys.stderr)
        return 2
    lines = problems(Path(argv[1]).read_text("utf-8"))
    for line in lines:
        print(f"commit message carries AI/bot attribution: {line!r}", file=sys.stderr)
    return 1 if lines else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
