"""The repo root describes the repo to agent-ops in ``.agent-ops.yaml`` (#1279, agent-ops#3044).

agent-ops' ``v3/repofile.py onboard`` reads this file from main; its schema is agent-ops'
``v3/docs/each-product-repo-describes-itself-in-agent-ops-yaml.md``. A lane weight moves by
hand here and in agent-ops' copy, so this test pins only what the repo itself can vouch for:
the file names this repo and the required-checks list it points at is a real file in the tree.
"""

from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
FILE = ROOT / ".agent-ops.yaml"


def test_agent_ops_yaml_describes_this_repo_and_points_at_a_real_check_list() -> None:
    data = yaml.safe_load(FILE.read_text())
    assert data["version"] == 1
    assert data["repo"] == "alexander-marquardt/synthetic-ecommerce-data"
    assert data["stable_branch"] == "main"
    assert data["merge_method"] in {"merge-queue", "optimistic-gate"}
    assert data["lanes"] and all(
        name.startswith("lane:") and isinstance(weight, int) and weight >= 0
        for name, weight in data["lanes"].items()
    )
    checks = ROOT / data["required_checks"]
    assert checks.is_file(), f"required_checks: {data['required_checks']} is not in the tree"
    assert json.loads(checks.read_text())["required"], "the required-checks list is empty"
