"""A list item quoting `Review-Verdict: ARM` describes a verdict, it posts none (agent-ops#862).

The fixture is agent-ops' record of two comments on alexander-marquardt/synthetic-ecommerce-data
#768: the ARM at e7392793a413 (09:21:00Z) and a rethink at the same head (11:00:28Z) whose
bullet reads ``- `Review-Verdict: ARM` with `Reviewed-Head` at this head ...``. The check took
the bullet as a verdict with no head, so it became the newest verdict and the check failed at an
approved head. agent-ops#813 fixed agent-ops' copy of the check; this test pins the same rule on
this copy.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "check_review_binding.py"
SPEC = importlib.util.spec_from_file_location("check_review_binding_862", SCRIPT)
assert SPEC and SPEC.loader
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check  # a dataclass looks its own module up by name
SPEC.loader.exec_module(check)

RECORD = json.loads((ROOT / "tests/fixtures/bullet_verdict_813/pr_768_comments.json").read_text())
HEAD = RECORD["head"]
ARM, RETHINK = RECORD["comments"]
TIER = "production-runtime"
TIERS = ["docs", "ui", "gate-or-test", "rulebook", "production-runtime"]


def judge(entries):
    return check.judge(
        author="someone",
        head=HEAD,
        paths=["src/x.py"],
        entries=entries,
        needed=TIER,
        tiers=TIERS,
        delta=lambda old: check.Delta("changed", "src/x.py"),
        exemptions={},
    )


def test_the_recorded_rethink_bullet_is_no_verdict():
    assert check.parse_verdict(RETHINK["body"]) is None


@pytest.mark.parametrize("marker", ["- ", "* ", "+ ", "1. ", "2) ", "  - ", "- **", "* `"])
def test_a_list_item_is_no_field(marker):
    body = f"{marker}Review-Verdict: ARM\n{marker}Reviewed-Head: {HEAD}\n{marker}Tier: {TIER}\n"
    assert check.parse_verdict(body) is None


@pytest.mark.parametrize(
    "line",
    [
        "Review-Verdict: ARM",
        "**Review-Verdict: ARM**",
        "## Review-Verdict: ARM",
        "`Review-Verdict: ARM`",
        "  Review-Verdict: ARM",
    ],
)
def test_a_plain_bold_backticked_or_heading_field_still_reads(line):
    body = f"{line}\nReviewed-Head: {HEAD}\nTier: {TIER}\n"
    assert check.parse_verdict(body) == check.Verdict("ARM", HEAD, TIER)


def test_the_recorded_arm_still_reads_past_its_own_bullets():
    assert check.parse_verdict(ARM["body"]) == check.Verdict("ARM", HEAD, TIER)


@pytest.mark.parametrize(
    "entries", [[ARM, RETHINK], [RETHINK, ARM]], ids=["as-recorded", "reversed"]
)
def test_the_check_keeps_the_arm_as_the_newest_verdict_and_passes(entries):
    assert check.newest_verdict(entries) == check.Verdict("ARM", HEAD, TIER)
    result = judge(entries)
    assert result.ok, result.reason
    assert "ARM at the head" in result.reason
