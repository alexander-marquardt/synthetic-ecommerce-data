"""Every CI job picks the self-hosted runner only for this repository's own runs (#596).

A fork's pull request must stay on GitHub-hosted runners: its code would otherwise run on the
agent VM. The variable gate lets the runner be switched off with no commit.
"""
from pathlib import Path

import yaml

CI = Path(__file__).resolve().parent.parent / ".github" / "workflows" / "ci.yaml"
RUNS_ON = (
    "${{ vars.SYNTH_CI_SELF_HOSTED == 'true' && (github.event_name != 'pull_request' || "
    "github.event.pull_request.head.repo.full_name == github.repository) && "
    "fromJSON('[\"self-hosted\",\"synth-ci\"]') || 'ubuntu-latest' }}"
)


def test_every_job_runs_on_the_one_expression():
    jobs = yaml.safe_load(CI.read_text())["jobs"]
    assert jobs
    wrong = {n: job.get("runs-on") for n, job in jobs.items() if job.get("runs-on") != RUNS_ON}
    assert wrong == {}


def test_the_expression_keeps_fork_pull_requests_on_hosted_runners():
    assert "github.event.pull_request.head.repo.full_name == github.repository" in RUNS_ON
    assert RUNS_ON.startswith("${{ vars.SYNTH_CI_SELF_HOSTED == 'true' && (")
    assert RUNS_ON.endswith("|| 'ubuntu-latest' }}")
