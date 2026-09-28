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
        "co-authored-by: some-bot <bot@example.invalid>",
        "Generated with ChatGPT",
        "Drafted with Copilot's help",
    ],
)
def test_attribution_is_refused(line):
    assert check.problems(f"Subject\n\nBody.\n\n{line}\n")


def test_an_ordinary_message_passes():
    message = "Census attribute names (#25)\n\nCo-Authored-By: A Person <a@example.invalid>\n"
    assert check.problems(message) == []


def test_git_comment_lines_are_ignored():
    assert check.problems("Subject\n# Please enter the commit message (claude)\n") == []


def test_the_hook_is_wired_for_commit_msg():
    config = (REPO / ".pre-commit-config.yaml").read_text("utf-8")
    assert "commit-msg" in config and "check_commit_msg.py" in config
