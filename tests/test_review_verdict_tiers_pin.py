"""Pins this repository's tier routes (``.github/review_verdict_tiers.json``).

The shared test (``test_review_verdict_check.py``) proves the machinery with a fixture rule
set. This file pins the rules this repository ships, so a route edit that lowers the tier a
path needs, or widens the ``generated`` list, is a failing test.
"""

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".github" / "scripts" / "check_review_binding.py"
SPEC = importlib.util.spec_from_file_location("check_review_binding_pin", SCRIPT)
assert SPEC and SPEC.loader
check = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check
SPEC.loader.exec_module(check)

RULES = json.loads((ROOT / ".github" / "review_verdict_tiers.json").read_text())
FIELD_WEIGHTS = "src/prism_synthetic_industrial/data/field_weights"


@pytest.mark.parametrize(
    ("path", "tier"),
    [
        ("README.md", "docs"),
        ("docs/adding-a-type.md", "docs"),
        ("tests/test_x.py", "gate-or-test"),
        ("scripts/prepush.sh", "gate-or-test"),
        (".github/workflows/ci.yaml", "gate-or-test"),
        ("uv.lock", "gate-or-test"),
        ("CLAUDE.md", "rulebook"),
        ("CONTRIBUTING.md", "rulebook"),
        ("src/synthetic_ecommerce_data/x.py", "production-runtime"),
        ("golden-catalog/products.ndjson", "production-runtime"),
        (f"{FIELD_WEIGHTS}/synthetic_industrial_flat.yaml", "production-runtime"),
        # A Markdown file outside the named docs routes is not documentation.
        ("notes.md", "production-runtime"),
        ("claude/live.md", "production-runtime"),
    ],
)
def test_a_path_takes_the_tier_this_repository_pins(path, tier):
    assert check.required_tier([path], RULES) == tier


def test_the_generated_list_is_exactly_the_one_file_a_build_writes():
    assert RULES["generated"] == [f"{FIELD_WEIGHTS}/synthetic_industrial_flat.yaml"]


def test_no_lock_file_or_golden_catalog_is_generated():
    assert RULES["generated"], "the generated list names the built files"
    for pattern in RULES["generated"]:
        assert not pattern.endswith(("uv.lock", "combined.yaml"))
        assert not pattern.startswith("golden-catalog")
        assert "*" not in pattern
