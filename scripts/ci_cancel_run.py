#!/usr/bin/env python3
"""Cancel the rest of a pull request's CI run once a required check is red (#1175).

    ci_cancel_run.py            # the cancel-on-red-<job> job of every required job of ci.yaml

A red run used to keep every runner it held until each shard ended: on 2026-11-23 three red pull
request runs held 19 jobs and about 5 runner-hours after their first red check, while the merge
path's run queued behind them (docs/ci-sharding.md). Once a required job has ended red, a job of
its own calls this, which asks GitHub to cancel the run: the jobs still queued or running end as
cancelled, the red job stays red, and the pull request's next push runs them all again. It is never
called from inside the red job: GitHub then records that job as cancelled, not as failed
(tests/fixtures/cancelled_from_inside_1175.json).

Only a ``pull_request`` run is ever cancelled. A push to main and a dispatched run carry their
result as proof (#1029, agent-ops#1743), so the workflow job's ``if:`` names the event, and this
checks it again: a run of any other event prints why and cancels nothing.

It runs after the required job has already failed, so nothing here may add a red of its own.
Every outcome exits 0 and says what happened: a fork's read-only token (403), a run
another red job already cancelled (409), or a network error.
"""
from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping

#: The only event whose run is cancelled.
CANCELLED_EVENT = "pull_request"


def cancel_url(env: Mapping[str, str]) -> str:
    """The REST endpoint that cancels this workflow run."""
    api = env.get("GITHUB_API_URL", "https://api.github.com").rstrip("/")
    return f"{api}/repos/{env['GITHUB_REPOSITORY']}/actions/runs/{env['GITHUB_RUN_ID']}/cancel"


def post(url: str, token: str) -> int:
    """POST to ``url`` with the job's token; the HTTP status, as a number."""
    request = urllib.request.Request(
        url,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as error:
        return error.code


def cancel(env: Mapping[str, str], send: Callable[[str, str], int] = post) -> str:
    """Cancel the run ``env`` describes, if it is a pull request's; the line to print."""
    event = env.get("GITHUB_EVENT_NAME", "")
    if event != CANCELLED_EVENT:
        return f"ci_cancel_run: a {event or 'unnamed'} run is never cancelled (#1175)"
    token = env.get("GH_TOKEN", "")
    if not token or not env.get("GITHUB_REPOSITORY") or not env.get("GITHUB_RUN_ID"):
        return "ci_cancel_run: GH_TOKEN, GITHUB_REPOSITORY or GITHUB_RUN_ID is unset; no cancel"
    try:
        status = send(cancel_url(env), token)
    except OSError as error:
        return f"ci_cancel_run: the cancel request failed ({error}); the rest of the run goes on"
    run = env["GITHUB_RUN_ID"]
    if status == 202:
        return f"ci_cancel_run: a required job is red: the rest of run {run} is cancelled (#1175)"
    if status == 409:
        return f"ci_cancel_run: run {run} is already cancelled or done (409)"
    if status == 403:
        return f"ci_cancel_run: the token may not cancel run {run} (403: a fork's read-only token)"
    return f"ci_cancel_run: cancelling run {run} answered {status}; the rest of the run goes on"


def main() -> int:
    print(cancel(os.environ), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
