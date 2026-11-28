"""Every CI job picks the self-hosted runner only for this repository's own runs (#596).

A fork's pull request must stay on GitHub-hosted runners: its code would otherwise run on the
agent VM. The variable gate lets the runner be switched off with no commit.

A push to main may ask for the runners reserved for it (agent-ops#189): the ``synth-ci-main`` label
that only the last slots of the VM register with, so a merge's run does not queue behind the pull
requests' jobs. A ``push`` asks for it, and so does the merge train's batch run (a
``workflow_dispatch`` on a ``ci/batch-*`` ref, synthetic-ecommerce-data#1031), only while
``SYNTH_CI_MAIN_RUNNER`` is ``true``. merge_pr.sh's dispatch on ``ci/merge-<N>`` keeps the pool.
So does a pull request, but for one the fleet runs first (synthetic-ecommerce-data#1027): a red
main's fix, titled ``fix(main-red)...`` or labelled ``main-red-fix`` (agent-ops#1720), and a PR
v3 labels ``ci-first`` (agent-ops#1876). The labels are the launcher's ``FIRST_LABELS``.
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
    "fromJSON((github.event_name == 'push' || (github.event_name == 'workflow_dispatch' && "
    "startsWith(github.ref_name, 'ci/batch-')) || (github.event_name == 'pull_request' && "
    "(startsWith(github.event.pull_request.title, 'fix(main-red)') || "
    "contains(github.event.pull_request.labels.*.name, 'main-red-fix') || "
    "contains(github.event.pull_request.labels.*.name, 'ci-first')))) && "
    "vars.SYNTH_CI_MAIN_RUNNER == 'true' && "
    "'[\"self-hosted\",\"synth-ci-main\"]' || '[\"self-hosted\",\"synth-ci\"]') "
    "|| 'ubuntu-latest' }}"
)


def _contains(seq, item):
    """GitHub's ``contains``: an array holds an equal item, a string a substring; case ignored."""
    if isinstance(seq, list):
        return any(str(x).lower() == item.lower() for x in seq)
    return item.lower() in (seq or "").lower()


def runs_on(event, *, self_hosted="true", main="true", head="o/r", repo="o/r", ref="main",
            title="feat(x): y", labels=()):
    """What ci.yaml's expression gives: GitHub's ``&&`` and ``||`` return an operand, as Python's.

    It evaluates the ``lint`` job's ``runs-on`` as ci.yaml holds it, so a row here fails when the
    file routes a run wrong; ``test_every_job_runs_on_the_one_expression`` holds every job to it.
    """
    template = yaml.safe_load(CI.read_text())["jobs"]["lint"]["runs-on"]
    body = re.fullmatch(r"\$\{\{ (.*) \}\}", template).group(1)
    for gh, py in [
        (r"vars\.SYNTH_CI_SELF_HOSTED", "SELF_HOSTED"),
        (r"vars\.SYNTH_CI_MAIN_RUNNER", "MAIN"),
        (r"github\.event\.pull_request\.head\.repo\.full_name", "HEAD"),
        (r"github\.event\.pull_request\.title", "TITLE"),
        (r"github\.event\.pull_request\.labels\.\*\.name", "LABELS"),
        (r"github\.repository", "REPO"),
        (r"github\.event_name", "EVENT"),
        (r"github\.ref_name", "REF_NAME"),
        (r"fromJSON", "json.loads"),
        (r"startsWith", "starts_with"),
        (r"contains", "contains_"),
        (r"&&", " and "),
        (r"\|\|", " or "),
    ]:
        body = re.sub(gh, py, body)
    names = {"json": json, "SELF_HOSTED": self_hosted, "MAIN": main, "HEAD": head, "REPO": repo}
    # GitHub's startsWith ignores case and reads a missing value (a push has no PR title) as "".
    names["starts_with"] = lambda s, prefix: (s or "").lower().startswith(prefix.lower())
    names["contains_"] = _contains
    pr = event == "pull_request"
    return eval(body, {**names, "EVENT": event, "REF_NAME": ref,
                       "TITLE": title if pr else None, "LABELS": list(labels) if pr else []})


#: The jobs that cancel a red pull request run (#1175) are hosted, so they never queue behind the
#: pool they free. They read no pull request code but scripts/ci_cancel_run.py.
HOSTED = {
    "cancel-on-red-lint",
    "cancel-on-red-ceiling-catalogue",
    "cancel-on-red-tests",
    "cancel-on-red-commit-messages",
    "cancel-on-red-file-size",
    "cancel-on-red-red-commit-proof",
    "cancel-on-red-shuffled",
    "cancel-on-red-customer-name-check",
    "cancel-on-red-no-derived-files",
    "cancel-on-red-dependency-review",
}


def test_every_job_runs_on_the_one_expression():
    jobs = yaml.safe_load(CI.read_text())["jobs"]
    assert jobs.keys() - HOSTED
    want = {n: "ubuntu-latest" if n in HOSTED else RUNS_ON for n in jobs}
    wrong = {n: job.get("runs-on") for n, job in jobs.items() if job.get("runs-on") != want[n]}
    assert wrong == {}


def test_every_job_exempt_from_the_expression_exists():
    assert yaml.safe_load(CI.read_text())["jobs"].keys() >= HOSTED


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
    ("pull_request", {}, POOL),                                # a pull request asks only when first
    # a red main's fix (agent-ops#1720) and a ci-first PR (agent-ops#1876) ask, #1027
    ("pull_request", {"title": "fix(main-red): revert 52a262da"}, MAIN),
    ("pull_request", {"title": "Fix(Main-Red): revert"}, MAIN),     # startsWith ignores case
    ("pull_request", {"labels": ["main-red-fix"]}, MAIN),
    ("pull_request", {"labels": ["sev:1", "ci-first"]}, MAIN),
    ("pull_request", {"labels": ["main-red"]}, POOL),          # another label keeps the pool
    ("pull_request", {"labels": ["priority:1000", "sev:1"]}, POOL),
    ("pull_request", {"title": "fix(main): red tests"}, POOL),  # only the fix(main-red) prefix
    ("pull_request", {"title": "feat(x): fix(main-red) later"}, POOL),  # the prefix starts it
    ("pull_request", {"labels": ["main-red-fix"], "main": "false"}, POOL),  # the switch holds
    ("pull_request", {"title": "fix(main-red): x", "main": ""}, POOL),
    ("pull_request", {"labels": ["ci-first"], "head": "fork/r"}, "ubuntu-latest"),  # a fork
    ("pull_request", {"title": "fix(main-red): x", "self_hosted": "false"}, "ubuntu-latest"),
    ("workflow_dispatch", {"ref": "ci/merge-12"}, POOL),       # merge_pr.sh --github-ci runs here
    ("workflow_dispatch", {}, POOL),                           # a dispatch on main by hand
    # the merge train's batch run (agent-ops coordinator/gen_train.sh, #1031)
    ("workflow_dispatch", {"ref": "ci/batch-gen_train"}, MAIN),
    ("workflow_dispatch", {"ref": "ci/batch-gen_train", "main": "false"}, POOL),
    ("workflow_dispatch", {"ref": "ci/batch-gen_train", "main": ""}, POOL),
    ("workflow_dispatch", {"ref": "ci/batch-gen_train", "self_hosted": "false"}, "ubuntu-latest"),
    ("pull_request", {"ref": "ci/batch-gen_train"}, POOL),     # only a dispatch on the ref asks
    ("push", {"ref": "feature/ci/batch-x"}, MAIN),             # a push asks whatever its ref
    ("workflow_dispatch", {"ref": "feature/ci/batch-x"}, POOL),  # the prefix starts the ref
    ("push", {"self_hosted": "false"}, "ubuntu-latest"),       # the #596 switch still wins
    ("pull_request", {"self_hosted": "false"}, "ubuntu-latest"),
])
def test_a_push_a_batch_dispatch_or_a_first_pull_request_asks_for_the_reserved_runners(
    event, kw, want
):
    assert runs_on(event, **kw) == want


# --- the concurrency group (#614, #1029) --------------------------------------------------
# A merged sha's CI result is its proof (agent-ops#1743): a push to main has a group of its own
# sha and is never cancelled, so a later push cannot erase it. A pull request keeps its own
# group per number and cancels its older head; a dispatched run (merge_pr.sh --github-ci) is
# never cancelled, so its group is unique to the run.

def _concurrency_value(template, names):
    """What GitHub's ``${{ }}`` gives for ``template``, with the same &&/|| operand semantics."""
    if not isinstance(template, str):
        return template

    def evaluate(expr):
        for gh, py in [
            (r"github\.event\.pull_request\.number", "PR"),
            (r"github\.event_name", "EVENT"),
            (r"github\.run_id", "RUN"),
            (r"github\.sha", "SHA"),
            (r"github\.ref", "REF"),
            (r"format\(", "fmt("),
            (r"&&", " and "),
            (r"\|\|", " or "),
        ]:
            expr = re.sub(gh, py, expr)
        return eval(expr, {"fmt": lambda f, *a: f.format(*a), **names})

    whole = re.fullmatch(r"\$\{\{ (.*) \}\}", template)
    if whole:
        return evaluate(whole.group(1))
    return re.sub(r"\$\{\{ (.*?) \}\}", lambda m: str(evaluate(m.group(1))), template)


def concurrency(event, *, ref="refs/heads/main", pr=None, run=1, sha="6f0702fe"):
    """The (group, cancel-in-progress) the CI workflow gives a run of ``event``."""
    block = yaml.safe_load(CI.read_text())["concurrency"]
    names = {"EVENT": event, "REF": ref, "PR": pr, "RUN": run, "SHA": sha}
    return (
        _concurrency_value(block["group"], names),
        _concurrency_value(block["cancel-in-progress"], names),
    )


def test_a_newer_push_to_main_never_cancels_the_older_main_run():
    # 2026-11-15: the push of 6aeb4daa (#988) cancelled run 43755228001 on 6f0702fe (#1026)
    older = concurrency("push", run=101, sha="6f0702fe")
    newer = concurrency("push", run=102, sha="6aeb4daa")
    assert older[0] != newer[0]
    assert older[1] is False
    assert newer[1] is False


def test_no_push_run_cancels_whatever_its_ref():
    for ref in ["refs/heads/main", "refs/heads/other"]:
        assert concurrency("push", ref=ref)[1] is False


def test_a_pull_request_keeps_its_own_group_and_cancels_only_its_own_older_head():
    assert concurrency("pull_request", ref="refs/pull/7/merge", pr=7, run=1) == (
        concurrency("pull_request", ref="refs/pull/7/merge", pr=7, run=2)
    )
    seven = concurrency("pull_request", pr=7, run=1)
    eight = concurrency("pull_request", pr=8, run=1)
    assert seven[0] != eight[0]
    assert seven[1] is True


def test_a_pull_request_main_and_a_dispatched_run_never_share_a_group():
    assert concurrency("pull_request", pr=7)[0] != concurrency("push")[0]
    # a run id equal to a pull request number must not land in that pull request's group
    assert concurrency("pull_request", pr=7)[0] != concurrency("workflow_dispatch", run=7)[0]


def test_a_dispatched_run_is_never_cancelled_and_never_cancels_another():
    first = concurrency("workflow_dispatch", ref="refs/heads/ci/merge-7", run=1)
    second = concurrency("workflow_dispatch", ref="refs/heads/ci/merge-7", run=2)
    assert first[0] != second[0]
    assert first[0] != concurrency("push")[0]
    assert first[1] is False
