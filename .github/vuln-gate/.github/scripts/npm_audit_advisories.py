"""Read an npm advisory report and answer the two questions CI asks of it.

One parser, two consumers — the two lanes ask genuinely different questions, so
neither duplicates the other:

* **"does the tree carry an advisory?"** — ``.github/workflows/npm-audit-advisory.yaml``
  (issue #5013), the scheduled scan, which files exactly one durable tracking
  issue per advisory and never fails a build.
* **"does this change ADD one?"** — ``.github/workflows/ui.yaml``'s
  ``npm audit gate`` step (issue #5695), which compares HEAD's advisory set
  against the base branch's via ``--baseline`` / ``--fail-on-new`` and fails only
  on arrivals.

Why this exists
---------------
``npm audit --audit-level=high`` used to run as a *build-failing* gate on every
push to ``main`` and in the nightly. That shape is wrong for supply-chain
advisories, and it cost the repo an 11-hour red ``main`` (#5007): a newly
published advisory against an **unchanged** lockfile reds whatever commit
happens to run next, forever, until somebody bumps the lockfile. The red is
real but it is not *attributable* to that commit and it blocks nothing, so it
is not actionable by the person who sees it — while the path-gated PR lane
keeps merging on top of it.

An advisory is **time-triggered**, not change-triggered. So detection moves to
a scheduled job, and the signal shape becomes a tracking issue in the already
watched ``ci-failure`` triage flow: one issue per advisory,
assignable, durable, and — crucially — filed **once**, not re-raised on every
subsequent push.

The failing gate is NOT removed: it still runs, in the PR lane, on pull
requests that actually change ``*-ui/package*.json``, where a vulnerable
dependency IS attributable to the change under review.

Attributable means ADDED, not present (#5695)
---------------------------------------------
The PR-lane gate originally asked ``npm audit --audit-level=high``, i.e. "does
the WHOLE tree carry a high advisory?". That is not the attributability
question, and the difference deadlocked the repo: once an advisory believed to
have no upstream remedy sat in ``main`` (#5653 — ``brace-expansion``
GHSA-mh99-v99m-4gvg, patched only in a release no parent reaches on its own
declared ranges; an intermediate ``minimatch`` pin later cleared it), every PR
touching ``*-ui/package*.json`` failed the required ``build`` check, while the
only way to CLEAR the advisory is a PR touching ``*-ui/package*.json``. Even
#5694, itself an advisory fix, was blocked.

So the gate now asks the attributability question directly: it fails on the
advisories the change **adds** relative to its base branch, and on nothing else.
Departures are fine. An advisory inherited from ``main`` is left to the lane
that owns it — the scheduled scan above, which has already filed a tracking
issue for it. The tolerated set is not a list anyone maintains: it is
recomputed from the base branch on every run, so it expires by construction the
moment the advisory leaves ``main``.

Two sources, one advisory model (#5793)
---------------------------------------
The report this script reads used to come from ``npm audit --json``. It now
comes from ``.github/scripts/npm_registry_advisories.py``, which queries the
registry's **bulk advisory endpoint** from the lockfile directly, because npm's
own audit transport broke in both of its endpoint paths: npm 10.9.0 falls back
to ``/audits/quick``, which the registry RETIRED (``400``, with a retirement
notice in the response headers), and npm 11 reaches the bulk endpoint but
cannot parse its undeclared-gzip body. See that script's docstring for the
measurements.

Only the SOURCE moved. The questions, the arrivals-vs-departures rule, and the
comparison key are unchanged, which is the property #5793 required:
``Advisory.advisory_id`` is the registry's numeric advisory id either way —
``via.source`` in an ``npm audit`` report, ``id`` in a bulk response, and they
are the same id from the same feed. Both shapes parse into the same
``Advisory``, so ``partition_against_baseline`` never learned that anything
changed.

Both readers are kept, and neither is decoration. ``parse_advisories`` is what
a contributor's local ``npm audit --json`` still produces (and is what the
captured real-resolver fixtures in ``tests/`` pin); ``parse_bulk_advisories``
is what CI runs. ``parse_report`` dispatches on the report's own self-declared
shape, and rejects anything that is neither — a file it cannot identify is
never read as a clean tree.

The one thing the bulk source cannot supply is npm's ``fixAvailable``, which is
a property of the TREE (is a patched version reachable given every parent's
declared range?) and not of the advisory feed. Rather than invent it,
``fix_available`` is ``None`` for a bulk-sourced advisory and renders as
"unknown" — an honest gap, where a fabricated ``false`` would be a claim the
data does not support. Nothing gates on it; it is guidance in the tracking
issue the scheduled scan files.

Contract
--------
``parse_advisories`` reads npm's ``auditReportVersion: 2`` JSON and returns the
distinct advisories at or above a severity floor; ``parse_bulk_advisories``
reads the registry bulk-endpoint envelope and returns the same thing.
``issue_payloads`` renders
those into the ``{title, body, labels}`` records the scheduled workflow's
``actions/github-script`` step files (that step owns the create/dedupe call, the
same mechanism ``main-ci-alert.yaml`` already uses — this script stays a pure
transformation with no GitHub dependency, which is also what makes it directly
unit-testable). ``partition_against_baseline`` splits a HEAD report's advisories
into arrivals and inherited for the PR-lane gate.

The **title is the dedupe key**, and it is keyed on the advisory, never on a run
— that is what turns a recurring red into exactly one durable signal. It is also
what the gate prints for each tolerated advisory, so "not gating here" always
resolves to "tracked there".

Exit codes: this script exits non-zero for a findings-present report **only**
under ``--fail-on-new``, and then only for advisories absent from ``--baseline``
— a published advisory is not, by itself, anybody's build failure. It always
exits non-zero on an empty or malformed report (either side), because a broken
scan reading as "all clear" is the silent-drop failure mode this whole design
exists to prevent.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# npm's severity ladder, ascending. The floor is expressed as a name and
# compared by index so ``--min-severity high`` also admits ``critical``.
SEVERITY_ORDER = ("info", "low", "moderate", "high", "critical")

# The label that routes a finding into the triage flow the team already watches
# (the nightly main-CI alert files under it too); the workflow adds the band.
ISSUE_LABELS = ("ci-failure",)

TITLE_PREFIX = "npm advisory"

# The marker key ``npm_registry_advisories.py`` stamps on its envelope, and the
# key ``parse_report`` dispatches on. Single-sourced as a literal rather than
# imported: these two scripts are invoked as separate processes by the
# workflows and share no import path, and the pair is pinned by
# ``tests/test_npm_registry_bulk_advisory_source_5793.py`` so they cannot drift.
BULK_REPORT_VERSION_KEY = "bulkAdvisoryReportVersion"


@dataclass(frozen=True)
class Advisory:
    """One distinct advisory, keyed by its registry advisory id.

    ``advisory_id`` is the registry's numeric advisory id — ``via.source`` in an
    ``npm audit`` report and ``id`` in a bulk-endpoint response, the same key
    from the same feed, which is why the source could move without the
    arrivals-vs-departures diff moving with it (#5793). ``ghsa`` is the
    human-facing GHSA slug parsed out of the advisory URL when present; it is
    display only, because a report can carry an advisory whose URL is not a
    GitHub advisory link.

    ``fix_available`` is ``None`` when the source does not report it — the bulk
    advisory feed describes the ADVISORY, while npm's ``fixAvailable`` describes
    this TREE. Unknown is rendered as unknown; see the module docstring.
    """

    advisory_id: int
    package: str
    severity: str
    title: str
    url: str
    vulnerable_range: str
    workspace: str
    fix_available: bool | None

    @property
    def ghsa(self) -> str:
        """The ``GHSA-…`` slug from the advisory URL, or "" when absent."""
        tail = self.url.rstrip("/").rsplit("/", 1)[-1]
        return tail if tail.startswith("GHSA-") else ""

    @property
    def issue_title(self) -> str:
        """The dedupe key.

        Keyed on the advisory id and the workspace ONLY — deliberately not on a
        date or a commit SHA. A date-keyed title (the shape the nightly alert
        uses) would file a fresh issue every single night for one unfixed
        advisory, which is the recurring-noise failure this change exists to
        end. One advisory, in one workspace, is one durable issue until a human
        closes it.
        """
        label = self.ghsa or f"npm:{self.advisory_id}"
        return f"{TITLE_PREFIX} {label}: {self.package} in {self.workspace}"


def _severity_at_least(severity: str, floor: str) -> bool:
    """True when ``severity`` sits at or above ``floor`` on npm's ladder.

    An unknown severity string is treated as ABOVE the floor: a report we can't
    grade is surfaced rather than dropped, because dropping is the unrecoverable
    direction.
    """
    try:
        floor_index = SEVERITY_ORDER.index(floor)
    except ValueError as exc:  # pragma: no cover - guarded by argparse choices
        raise ValueError(f"unknown severity floor: {floor}") from exc
    if severity not in SEVERITY_ORDER:
        return True
    return SEVERITY_ORDER.index(severity) >= floor_index


def _advisory_id(value: Any, *, context: str) -> int:
    """The registry advisory id, or a loud refusal.

    ``bool`` is excluded explicitly because it is a subclass of ``int`` in
    Python, so a ``true`` in the id slot would otherwise sail through as the id
    ``1`` and silently collide every such advisory into one finding.
    """
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(
            f"{context} has no integer advisory id: {value!r}. The id is the key "
            "the arrivals-vs-baseline comparison is built on, so a report "
            "without one cannot be compared and must not be read as clean."
        )
    return int(value)


def parse_advisories(
    report: dict[str, Any], *, workspace: str, min_severity: str = "high"
) -> list[Advisory]:
    """Extract the distinct advisories at/above ``min_severity`` from a report.

    npm's ``vulnerabilities`` map is keyed by package name; each entry's ``via``
    list holds either a *string* (the name of another package through which this
    one is reached — a transitive edge, no advisory of its own) or an *object*
    (the advisory itself). Only the objects carry an advisory, and the SAME
    advisory object appears under every package it propagates to, so the result
    is deduped by ``source``.
    """
    vulnerabilities = report.get("vulnerabilities")
    if vulnerabilities is None:
        # An empty/clean report has ``vulnerabilities: {}``; a missing key means
        # this is not an npm audit report at all. Fail loudly rather than
        # reporting "no advisories" for a file we failed to understand.
        raise ValueError(
            "not an npm audit report: no 'vulnerabilities' key "
            "(expected `npm audit --json` output, auditReportVersion 2) — and "
            f"no {BULK_REPORT_VERSION_KEY!r} either, so it is not a registry "
            "bulk advisory report from "
            "`.github/scripts/npm_registry_advisories.py`. Regenerate it with "
            "that script; note `npm audit` itself no longer reaches a working "
            "registry endpoint (#5793)."
        )
    by_id: dict[int, Advisory] = {}
    for package_name, entry in sorted(vulnerabilities.items()):
        fix_available = bool(entry.get("fixAvailable"))
        for via in entry.get("via", []):
            if not isinstance(via, dict):
                # Transitive edge, not an advisory — the advisory itself is
                # recorded on the package it actually applies to.
                continue
            severity = str(via.get("severity", ""))
            if not _severity_at_least(severity, min_severity):
                continue
            source = _advisory_id(
                via.get("source"), context=f"advisory under {package_name!r}"
            )
            if source in by_id:
                continue
            by_id[source] = Advisory(
                advisory_id=source,
                package=str(via.get("name") or via.get("dependency") or package_name),
                severity=severity,
                title=str(via.get("title", "")),
                url=str(via.get("url", "")),
                vulnerable_range=str(via.get("range", "")),
                workspace=workspace,
                fix_available=fix_available,
            )
    return sorted(by_id.values(), key=lambda a: (a.package, a.advisory_id))


def parse_bulk_advisories(
    report: dict[str, Any], *, workspace: str, min_severity: str = "high"
) -> list[Advisory]:
    """Extract the distinct advisories from a registry bulk-endpoint envelope.

    The envelope is written by ``.github/scripts/npm_registry_advisories.py``:
    ``{"bulkAdvisoryReportVersion": 1, "packagesQueried": N, "advisories":
    {package: [advisory, …]}}``, where each advisory object is the registry's,
    verbatim.

    The registry does the version matching server-side — it is sent the exact
    versions the lockfile resolves and returns only the advisories that apply —
    so there is no semver evaluation here that could disagree with npm's.

    Deduped by ``id`` for the same reason the ``npm audit`` reader dedupes by
    ``via.source``, and it is the same id: the bulk feed answers per package, so
    one advisory affecting two packages arrives twice and must stay ONE finding.

    Every structural surprise raises. A response whose shape we do not recognise
    is a broken scan, and a broken scan that returns "no advisories" is the
    silent-drop failure the whole design exists to prevent.
    """
    advisories = report.get("advisories")
    if not isinstance(advisories, dict):
        raise ValueError(
            "bulk advisory report has no 'advisories' object "
            f"(got {type(advisories).__name__}) — the scan did not produce a "
            "readable result and must not be read as a clean tree"
        )
    by_id: dict[int, Advisory] = {}
    for package_name, entries in sorted(advisories.items()):
        if not isinstance(entries, list):
            raise ValueError(
                f"bulk advisory report: {package_name!r} maps to "
                f"{type(entries).__name__}, expected a list of advisories"
            )
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError(
                    f"bulk advisory report: {package_name!r} carries a "
                    f"non-object advisory: {entry!r}"
                )
            severity = str(entry.get("severity", ""))
            if not _severity_at_least(severity, min_severity):
                continue
            identifier = _advisory_id(
                entry.get("id"), context=f"bulk advisory under {package_name!r}"
            )
            if identifier in by_id:
                continue
            by_id[identifier] = Advisory(
                advisory_id=identifier,
                package=str(entry.get("name") or package_name),
                severity=severity,
                title=str(entry.get("title", "")),
                url=str(entry.get("url", "")),
                # npm's ``range`` and the registry's ``vulnerable_versions`` are
                # the same string in the same syntax; only the field name moved.
                vulnerable_range=str(entry.get("vulnerable_versions", "")),
                workspace=workspace,
                # Not reported by this source, and not invented here — see the
                # module docstring.
                fix_available=None,
            )
    return sorted(by_id.values(), key=lambda a: (a.package, a.advisory_id))


def parse_report(
    report: Any, *, workspace: str, min_severity: str = "high"
) -> list[Advisory]:
    """Read either supported report shape, chosen by what the report says it is.

    Dispatch is on a key the producer STAMPS, never on a guess: a bulk envelope
    declares ``bulkAdvisoryReportVersion`` and an ``npm audit`` report carries
    ``vulnerabilities``. That matters because the empty cases are otherwise
    indistinguishable — ``{}`` could be a clean bulk answer or a truncated file,
    and resolving that ambiguity towards "clean" is the one direction that
    cannot be recovered from. Anything unidentifiable raises.
    """
    if not isinstance(report, dict):
        raise ValueError(
            "not an npm audit report and not a bulk advisory report: the file "
            f"holds a {type(report).__name__}, not a JSON object"
        )
    if BULK_REPORT_VERSION_KEY in report:
        return parse_bulk_advisories(
            report, workspace=workspace, min_severity=min_severity
        )
    return parse_advisories(report, workspace=workspace, min_severity=min_severity)


def issue_body(advisory: Advisory, *, run_url: str = "") -> str:
    """The tracking-issue body: what, where, how to fix, and why it is an issue."""
    if advisory.fix_available is None:
        # Honest gap, not a guess: the registry advisory feed describes the
        # advisory, while npm's ``fixAvailable`` describes whether a patched
        # version is REACHABLE in this tree given every parent's declared range.
        # Rendering "no fix available" here would be a claim the source does not
        # make, and it is the claim that froze the manifests in #5653 — where a
        # patched version turned out to be reachable after all, via an
        # intermediate pin.
        fix_line = (
            "Whether a patched version is reachable from this tree is **not "
            "reported** by the registry advisory feed. Check it directly: pin "
            "the vulnerable transitive with an `overrides` entry in "
            f"`{advisory.workspace}/package.json`, regenerate the lockfile, and "
            "re-run the scan below — if the advisory is gone, the fix is "
            "reachable."
        )
    elif advisory.fix_available:
        fix_line = (
            "A fix is available from the registry — regenerate the lockfile on "
            "the pinned resolver and open a PR."
        )
    else:
        fix_line = (
            "npm reports **no fix available** yet — track upstream, or "
            "pin/replace the dependency."
        )
    lines = [
        f"The npm registry reports a **{advisory.severity}** advisory against "
        f"the `{advisory.workspace}` dependency tree.",
        "",
        f"- Package: `{advisory.package}`",
        f"- Severity: `{advisory.severity}`",
        f"- Vulnerable range: `{advisory.vulnerable_range}`",
        f"- Advisory: {advisory.url or '(no URL in report)'}",
        f"- Title: {advisory.title}",
    ]
    if run_url:
        lines.append(f"- Detected by: {run_url}")
    lines += [
        "",
        fix_line,
        "",
        "To reproduce and fix, from the repo root:",
        "",
        "```sh",
        "python3 .github/scripts/npm_registry_advisories.py \\",
        f"    {advisory.workspace}/package-lock.json --out /tmp/advisories.json",
        "python3 .github/scripts/npm_audit_advisories.py /tmp/advisories.json \\",
        f"    --workspace {advisory.workspace} --min-severity high",
        "# then, on the pinned CI resolver, regenerate the lockfile:",
        f"(cd {advisory.workspace} && npx npm@10.9.0 install "
        "--package-lock-only --no-audit)",
        "```",
        "",
        "`npm audit` itself is NOT the reproduce path any more: npm 10.9.0 "
        "falls back to the registry's retired `/audits/quick` endpoint and npm "
        "11 cannot parse the bulk endpoint's undeclared-gzip body, so both "
        "produce an error object instead of a report (#5793). The script above "
        "queries the bulk endpoint directly.",
        "",
        "This issue is filed **once** per advisory (issue #5013). The advisory is "
        "not attributable to any commit of ours, so it deliberately does not fail "
        "anyone's build; it is tracked here instead. Close it when the lockfile no "
        "longer resolves to a vulnerable version — a later scan will re-file it if "
        "the advisory comes back.",
    ]
    return "\n".join(lines)


def issue_payloads(
    advisories: Iterable[Advisory], *, run_url: str = ""
) -> list[dict[str, Any]]:
    """Render advisories as the issue records the workflow files.

    One record per advisory. ``title`` is the dedupe key the filing step matches
    against the OPEN ``ci-failure`` issues, so a still-unfixed advisory
    re-detected by tomorrow's scan produces no second issue — "exactly one
    durable signal" (#5013) is a property of this key, not of the filing code.
    """
    return [
        {
            "title": advisory.issue_title,
            "body": issue_body(advisory, run_url=run_url),
            "labels": list(ISSUE_LABELS),
        }
        for advisory in advisories
    ]


def _fix_cell(fix_available: bool | None) -> str:
    """Render the fix-available column, including its honest third state.

    ``unknown`` is NOT folded into ``no``. The two mean different things to a
    reader deciding whether to spend an afternoon on a dependency, and the fold
    would report a claim the source never made.
    """
    if fix_available is None:
        return "unknown"
    return "yes" if fix_available else "no"


def advisory_table(advisories: Sequence[Advisory]) -> str:
    """The markdown table both summaries render advisories with."""
    rows = "\n".join(
        f"| `{a.package}` | `{a.severity}` | {a.ghsa or a.advisory_id} | "
        f"`{a.vulnerable_range}` | {_fix_cell(a.fix_available)} |"
        for a in advisories
    )
    return (
        "| package | severity | advisory | vulnerable range | fix available |\n"
        "| --- | --- | --- | --- | --- |\n"
        f"{rows}\n"
    )


def render_summary(advisories: Sequence[Advisory]) -> str:
    """Markdown for the Actions job summary (human-readable scan result)."""
    if not advisories:
        return "## npm advisory scan\n\nNo high or critical advisories found.\n"
    return (
        "## npm advisory scan\n\n"
        f"{len(advisories)} high/critical advisory(ies) found.\n\n"
        f"{advisory_table(advisories)}"
    )


def partition_against_baseline(
    head: Iterable[Advisory], baseline: Iterable[Advisory]
) -> tuple[list[Advisory], list[Advisory]]:
    """Split HEAD's advisories into the ones a change ADDS and the ones it inherits.

    This is the whole of the #5695 gate rule: **arrivals fail, inherited and
    departures do not**. The comparison key is ``advisory_id`` (npm's numeric
    ``source``), the same stable per-advisory key ``parse_advisories`` dedupes on
    — not the package name, because one advisory legitimately surfaces under
    every package it propagates through (the #5007 ``brace-expansion`` shape:
    eight vulnerable packages, one advisory).

    Keying on the advisory rather than on the (advisory, package) pair is
    deliberate. A change that reaches an ALREADY-present advisory through one
    more path adds no new exposure that fixing the advisory would not also fix,
    and the advisory itself is already tracked — so failing on it would re-create
    the freeze this rule exists to end, for no gain.
    """
    baseline_ids = {advisory.advisory_id for advisory in baseline}
    arrived = [a for a in head if a.advisory_id not in baseline_ids]
    inherited = [a for a in head if a.advisory_id in baseline_ids]
    return arrived, inherited


def render_gate_summary(
    arrived: Sequence[Advisory],
    inherited: Sequence[Advisory],
    *,
    workspace: str,
    gating: bool,
) -> str:
    """Markdown for the PR-lane gate: what this change added vs what it inherited.

    The inherited block is the auditability half of the design. An advisory that
    does not fail the build is still printed, by name, together with the EXACT
    title of the tracking issue ``npm-audit-advisory.yaml`` files for it — so
    "tolerated here" always resolves to "owned there", and a reviewer can find
    the owner without reading the workflow.

    ``gating`` is whether the caller passed ``--fail-on-new``. Without it the
    split is reported and the run still exits 0, so the summary must not claim
    a failure that did not happen — the summary is read on its own, away from
    the exit status.
    """
    lines = [f"## npm audit gate — `{workspace}`", ""]
    if arrived:
        verdict = (
            "gate failed"
            if gating
            else "reported only — this invocation is not gating (no `--fail-on-new`)"
        )
        lines += [
            f"**{len(arrived)} advisory(ies) ADDED by this change — {verdict}.**",
            "",
            advisory_table(arrived).rstrip(),
            "",
        ]
    else:
        lines += ["No new high/critical advisory is introduced by this change.", ""]
    if inherited:
        lines += [
            f"{len(inherited)} advisory(ies) already present on the base branch — "
            "not caused by this change, and not gating it. Each is tracked by its "
            "own issue, filed by the scheduled `npm advisory scan`:",
            "",
            *(f"- `{a.ghsa or a.advisory_id}` — {a.issue_title}" for a in inherited),
            "",
            "They are re-evaluated against the base branch on every run: once one "
            "leaves `main`, it stops being tolerated here from this PR's next "
            "event onward (the baseline is `base.sha`, refreshed on each push to "
            "the PR — not a live read of `main`).",
            "",
        ]
    return "\n".join(lines)


def report_advisories(
    path: Path, *, workspace: str, min_severity: str
) -> list[Advisory]:
    """Read one advisory report from disk, failing loudly on garbage.

    An empty file means the scan produced nothing at all — a broken scan, not a
    clean tree. Reading it as "all clear" is the silent-drop direction, which is
    unrecoverable, so it raises instead. Same for a file whose shape neither
    reader recognises (``parse_report``).
    """
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError(
            f"empty npm audit report at {path} — the scan produced no output, "
            "which is a broken scan, not a clean tree. Re-run the job; if it "
            "persists, run `python3 .github/scripts/npm_registry_advisories.py "
            f"{workspace}/package-lock.json --out /tmp/advisories.json` locally "
            "and read the error it prints."
        )
    try:
        report = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"unreadable advisory report at {path}: {exc}") from exc
    return parse_report(report, workspace=workspace, min_severity=min_severity)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "report",
        help=(
            "path to an advisory report — either "
            "`npm_registry_advisories.py --out` output (what CI produces) or "
            "`npm audit --json` output"
        ),
    )
    parser.add_argument("--workspace", required=True, help="the *-ui directory scanned")
    parser.add_argument("--min-severity", default="high", choices=SEVERITY_ORDER)
    parser.add_argument("--run-url", default="", help="Actions run URL for the body")
    parser.add_argument("--summary", default="", help="append job summary to this path")
    parser.add_argument(
        "--issues-out",
        default="",
        help="write the issue payloads (JSON list) here for the filing step",
    )
    parser.add_argument(
        "--baseline",
        default="",
        help=(
            "path to the BASE branch's advisory report; splits the "
            "report into arrivals vs inherited and reports both. REPORTING "
            "ONLY — on its own it never changes the exit status; pass "
            "--fail-on-new to turn an arrival into a failure (issue #5695)"
        ),
    )
    parser.add_argument(
        "--fail-on-new",
        action="store_true",
        help=(
            "exit non-zero when the report carries an advisory absent from "
            "--baseline. Requires --baseline"
        ),
    )
    args = parser.parse_args(argv)

    if args.fail_on_new and not args.baseline:
        # Without a baseline every advisory would look inherited, so the gate
        # would pass unconditionally — a gate that cannot fail is worse than no
        # gate, because it wears a green check. Refuse rather than degrade.
        parser.error(
            "--fail-on-new requires --baseline: with no base-branch report the "
            "gate has nothing to compare against and would pass unconditionally. "
            "Pass the base branch's advisory report via --baseline."
        )

    try:
        advisories = report_advisories(
            Path(args.report),
            workspace=args.workspace,
            min_severity=args.min_severity,
        )
    except ValueError as exc:
        print(f"::error::{exc}", file=sys.stderr)
        return 1

    if args.issues_out:
        Path(args.issues_out).write_text(
            json.dumps(issue_payloads(advisories, run_url=args.run_url), indent=1),
            encoding="utf-8",
        )

    if not args.baseline:
        summary = render_summary(advisories)
        print(summary)
        if args.summary:
            with open(args.summary, "a", encoding="utf-8") as fh:
                fh.write(summary)
        return 0

    try:
        baseline = report_advisories(
            Path(args.baseline),
            workspace=args.workspace,
            min_severity=args.min_severity,
        )
    except ValueError as exc:
        print(f"::error::baseline: {exc}", file=sys.stderr)
        return 1

    arrived, inherited = partition_against_baseline(advisories, baseline)
    summary = render_gate_summary(
        arrived, inherited, workspace=args.workspace, gating=args.fail_on_new
    )
    print(summary)
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write(summary)

    for advisory in inherited:
        print(
            f"::notice::{args.workspace}: {advisory.ghsa or advisory.advisory_id} "
            f"({advisory.package}) is already present on the base branch — not "
            f"introduced by this change. Tracked by: {advisory.issue_title}"
        )
    if not arrived:
        return 0
    if not args.fail_on_new:
        # --baseline is a REPORTING flag. Only --fail-on-new arms the failure,
        # and that split is load-bearing rather than cosmetic: the scheduled
        # `npm-audit-advisory.yaml` lane is documented as non-blocking and
        # always ends green, so adding --baseline there to get the nicer split
        # summary must not silently convert it into a failing gate — the #5013
        # shape this repo already fixed once. It is also what lets
        # `test_nightly_does_not_run_the_audit_gate` census the single literal
        # `--fail-on-new`: with the failure conditional on the flag, that
        # literal is the ONLY spelling of a build-failing audit through this
        # script.
        for advisory in arrived:
            print(
                f"::notice::{args.workspace}: "
                f"{advisory.ghsa or advisory.advisory_id} ({advisory.package}) "
                "is NEW relative to the baseline. Reporting only — this "
                "invocation passed no --fail-on-new, so it does not gate."
            )
        return 0
    for advisory in arrived:
        print(
            f"::error::{args.workspace}: this change ADDS a "
            f"{advisory.severity} advisory {advisory.ghsa or advisory.advisory_id} "
            f"against `{advisory.package}` ({advisory.vulnerable_range}): "
            f"{advisory.title}. Fix it here — prefer an `overrides` entry in "
            f"{args.workspace}/package.json pinning the vulnerable transitive to "
            "a patched version over a major bump of the direct dependency, then "
            "regenerate the lockfile with `npx npm@10.9.0 install "
            "--package-lock-only --no-audit`. Only advisories ALREADY on the base branch "
            "are tolerated (each has its own tracking issue); a new one is "
            "attributable to this change.",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
