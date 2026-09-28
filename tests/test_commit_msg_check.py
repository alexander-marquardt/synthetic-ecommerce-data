"""The commit-msg hook refuses AI/bot attribution, and passes an ordinary message."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_commit_msg", REPO / "scripts" / "check_commit_msg.py"
)
assert _spec is not None and _spec.loader is not None
check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(check)


@pytest.mark.parametrize(
    "line",
    [
        "Co-Authored-By: Claude <noreply@anthropic.com>",
        "co-authored-by: helper[bot] <1+helper[bot]@users.noreply.github.com>",
        "Generated with ChatGPT",
        "Drafted with Copilot's help",
        # The review's gaps, each a plant:
        "Co-authored-by: Cursor Agent <cursoragent@cursor.com>",
        "Co-authored-by: Aider <aider@aider.chat>",
        "Generated with Cursor",
        "Written by Codex",
        "Made with Windsurf",
        "Assisted-by: Gemini",
        "Written with the help of an LLM",
        "Opus 5.5 drafted this",
        "Co-Authored-By: Cla\u200bude <x@example.invalid>",  # a zero-width split
    ],
)
def test_attribution_is_refused(line):
    assert check.problems(f"Subject\n\nBody.\n\n{line}\n")


@pytest.mark.parametrize(
    "message",
    [
        "Census attribute names (#25)\n\nCo-Authored-By: A Person <a@example.invalid>\n",
        "robot arm drawings, a hex bolt, the release bot's schedule\n",
        "bot_hex and bolt_hex types\n",
        "the cursor moves over the sheet\n",
    ],
)
def test_an_ordinary_message_passes(message):
    assert check.problems(message) == []


def test_the_core_family_is_vendored_verbatim_with_its_source():
    labels = [label for label, _ in check.CORE_FAMILY]
    assert labels[0] == "ai-vendor-name" and "llm-mention" in labels and len(labels) == 10
    assert "7f961d6d7" in check.CORE_SOURCE


def test_git_comment_lines_are_ignored():
    assert check.problems("Subject\n# Please enter the commit message (claude)\n") == []


def test_the_hook_is_wired_for_commit_msg():
    config = (REPO / ".pre-commit-config.yaml").read_text("utf-8")
    assert "commit-msg" in config and "check_commit_msg.py" in config
