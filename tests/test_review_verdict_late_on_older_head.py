"""A verdict naming an older head does not outrank one at the PR's head (#775).

The fixture holds the two verdict comments of elastic/prism-retail-and-industrial#1047: an ARM at
the head and a FIX for the older head that carries the later comment time. The check judged the
FIX and failed. The rule is agent-ops#809's; this file stands apart from
`test_review_verdict_check.py`, which is the same in every repository that carries the check.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "check_review_binding.py"
SPEC = importlib.util.spec_from_file_location("check_review_binding_775", SCRIPT)
assert SPEC and SPEC.loader
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check  # a dataclass looks its own module up by name
SPEC.loader.exec_module(check)

RECORD = json.loads((ROOT / "tests/data/late_verdict/pr_1047_comments.json").read_text())
HEAD, OLDER = RECORD["head"], RECORD["older_head"]
FIX_LATE, ARM_AT_HEAD = RECORD["comments"]
TIERS = ["docs", "ui", "gate-or-test", "rulebook", "production-runtime"]
TIER = "production-runtime"
EARLY, LATE = ARM_AT_HEAD["created_at"], FIX_LATE["created_at"]


def entry(kind, head, at, login="alexander-marquardt"):
    body = f"Review-Verdict: {kind}\nReviewed-Head: {head}\nTier: {TIER}\n"
    return {"body": body, "created_at": at, "login": login}


def judge(entries, delta="changed", head=HEAD):
    return check.judge(
        author="someone",
        head=head,
        paths=["src/x.py"],
        entries=entries,
        needed=TIER,
        tiers=TIERS,
        delta=lambda old: check.Delta(delta, "src/x.py"),
        exemptions={},
    )


@pytest.mark.parametrize(
    "entries",
    [[FIX_LATE, ARM_AT_HEAD], [ARM_AT_HEAD, FIX_LATE]],
    ids=["as-recorded", "reversed"],
)
def test_the_recorded_late_fix_on_the_older_head_does_not_outrank_the_arm_at_the_head(entries):
    result = judge(entries)
    assert result.ok, result.reason
    assert "ARM at the head" in result.reason


@pytest.mark.parametrize(
    "older_at,head_at", [(LATE, EARLY), (EARLY, LATE)], ids=["older-late", "older-early"]
)
@pytest.mark.parametrize("kind", ["FIX", "BLOCK"])
def test_a_refusal_at_an_older_head_loses_to_the_arm_at_the_head_at_either_time(
    kind, older_at, head_at
):
    assert judge([entry(kind, OLDER, older_at), entry("ARM", HEAD, head_at)]).ok


@pytest.mark.parametrize(
    "older_at,head_at", [(LATE, EARLY), (EARLY, LATE)], ids=["older-late", "older-early"]
)
@pytest.mark.parametrize("delta", ["changed", "same-diff"])
def test_an_arm_at_an_older_head_loses_to_a_fix_at_the_head_at_either_time(
    delta, older_at, head_at
):
    result = judge([entry("ARM", OLDER, older_at), entry("FIX", HEAD, head_at)], delta)
    assert not result.ok
    assert "newest verdict is FIX" in result.reason


def test_the_head_is_matched_in_any_case():
    assert judge([FIX_LATE, ARM_AT_HEAD], head=HEAD.upper()).ok


def test_two_verdicts_at_the_head_are_decided_by_time():
    assert not judge([entry("ARM", HEAD, EARLY), entry("FIX", HEAD, LATE)]).ok
    assert judge([entry("FIX", HEAD, EARLY), entry("ARM", HEAD, LATE)]).ok


def test_with_no_verdict_at_the_head_the_newest_of_all_decides_as_before():
    assert not judge([entry("ARM", OLDER, EARLY), entry("FIX", "c" * 40, LATE)], "same-diff").ok
    assert judge([entry("FIX", "c" * 40, EARLY), entry("ARM", OLDER, LATE)], "same-diff").ok


def test_a_verdict_at_no_readable_head_is_no_older_head_and_keeps_its_time():
    malformed = entry("FIX", "abc123", LATE)
    assert not judge([entry("ARM", HEAD, EARLY), malformed]).ok
    assert judge([{**malformed, "created_at": EARLY}, entry("ARM", HEAD, LATE)]).ok


def test_a_bots_verdict_at_the_head_does_not_make_a_head():
    entries = [entry("ARM", HEAD, LATE, login="dependabot[bot]"), entry("FIX", OLDER, EARLY)]
    assert not judge(entries).ok
