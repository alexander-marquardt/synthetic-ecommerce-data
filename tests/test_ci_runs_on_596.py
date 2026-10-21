"""Every CI job picks the self-hosted runner only for this repository's own runs (#596).

A fork's pull request must stay on GitHub-hosted runners: its code would otherwise run on the
agent VM. The variable gate lets the runner be switched off with no commit.

A push to main may ask for the runners reserved for it (agent-ops#189): the ``synth-ci-main`` label
that only the last slots of the VM register with, so a merge's run does not queue behind the pull
requests' jobs. Only a ``push`` asks for it, and only while ``SYNTH_CI_MAIN_RUNNER`` is ``true``.
"""
import json
import re
from pathlib import Path

import pytest
import yaml

CI = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yaml"
POOL = ["self-hosted", "synth-ci"]
MAIN = ["self-hosted", "synth-ci-main"]
RUNS_ON = (
    "${{ vars.SYNTH_CI_SELF_HOSTED == 'true' && (github.event_name != 'pull_request' || "
    "github.event.pull_request.head.repo.full_name == github.repository) && "
    "fromJSON(github.event_name == 'push' && vars.SYNTH_CI_MAIN_RUNNER == 'true' && "
    "'[\"self-hosted\",\"synth-ci-main\"]' || '[\"self-hosted\",\"synth-ci\"]') "
    "|| 'ubuntu-latest' }}"
)


def runs_on(event, *, self_hosted="true", main="true", head="o/r", repo="o/r"):
    """What the expression gives: GitHub's ``&&`` and ``||`` return an operand, as Python's do."""
    body = re.fullmatch(r"\$\{\{ (.*) \}\}", RUNS_ON).group(1)
    for gh, py in [
        (r"vars\.SYNTH_CI_SELF_HOSTED", "SELF_HOSTED"),
        (r"vars\.SYNTH_CI_MAIN_RUNNER", "MAIN"),
        (r"github\.event\.pull_request\.head\.repo\.full_name", "HEAD"),
        (r"github\.repository", "REPO"),
        (r"github\.event_name", "EVENT"),
        (r"fromJSON", "json.loads"),
        (r"&&", " and "),
        (r"\|\|", " or "),
    ]:
        body = re.sub(gh, py, body)
    names = {"json": json, "SELF_HOSTED": self_hosted, "MAIN": main, "HEAD": head, "REPO": repo}
    return eval(body, {**names, "EVENT": event})


def test_every_job_runs_on_the_one_expression():
    jobs = yaml.safe_load(CI.read_text())["jobs"]
    assert jobs
    wrong = {n: job.get("runs-on") for n, job in jobs.items() if job.get("runs-on") != RUNS_ON}
    assert wrong == {}


def test_the_expression_keeps_fork_pull_requests_on_hosted_runners():
    assert "github.event.pull_request.head.repo.full_name == github.repository" in RUNS_ON
    assert RUNS_ON.startswith("${{ vars.SYNTH_CI_SELF_HOSTED == 'true' && (")
    assert RUNS_ON.endswith("|| 'ubuntu-latest' }}")
    assert runs_on("pull_request", head="fork/r") == "ubuntu-latest"
    assert runs_on("pull_request", head="fork/r", main="false") == "ubuntu-latest"


@pytest.mark.parametrize("event, kw, want", [
    ("push", {}, MAIN),
    ("push", {"main": "false"}, POOL),                         # the variable is the switch
    ("push", {"main": ""}, POOL),                              # unset
    ("pull_request", {}, POOL),                                # a pull request never asks for it
    ("workflow_dispatch", {}, POOL),                           # merge_pr.sh --github-ci runs here
    ("push", {"self_hosted": "false"}, "ubuntu-latest"),       # the #596 switch still wins
    ("pull_request", {"self_hosted": "false"}, "ubuntu-latest"),
])
def test_only_a_push_with_the_variable_set_asks_for_the_reserved_runners(event, kw, want):
    assert runs_on(event, **kw) == want
