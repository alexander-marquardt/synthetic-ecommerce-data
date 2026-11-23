#!/usr/bin/env python3
"""The vulnerability gate: a known high or critical advisory fails the run (#16291).

The rule: contributing/vulnerability-gate.md, "The vulnerability gate fails on a
high or critical advisory (#16291)".

Two subcommands, both run by ``.github/workflows/vuln-gate.yaml``:

``pip-audit``
    Runs PyPA's ``pip-audit`` on an exported, hashed requirements file and exits
    0 when it wrote a readable JSON report, findings or none. pip-audit exits 1
    both on findings and on a failed download, so its own exit cannot tell the
    retry wrapper (``.github/scripts/retry.sh``) which one happened; this can. A
    finding is the gate's input, not a reason to fetch again.

``judge``
    Reads the pip-audit report, each npm advisory report (the registry bulk
    envelope ``npm_registry_advisories.py`` writes, or ``npm audit --json``) and
    each image's trivy report (``trivy image --format json``) against the
    checked-in allowlist ``.github/vuln-allowlist.json`` and exits:

    * 0: every high, critical or unknown-severity finding is covered by an
      allowlist entry, and every entry is live;
    * 1: a high, critical or unknown-severity finding no entry covers, an entry
      past its ``expires`` date, or an entry whose ``issue`` is no longer open;
    * 2: the gate could not judge (a report or the allowlist unreadable, or an
      OSV or GitHub lookup that failed three times). Never read as clean.

    Medium and low findings, and entries that match no finding, go to the job
    summary and fail nothing. An entry that expires within ``WARN_DAYS`` days
    (today up to today + 7, both counted) is a ``::warning::`` and a summary
    section, each day until it expires; it fails nothing, unless
    ``--fail-expiring`` is given: the workflow's daily scheduled run on main
    passes it, so the red run reaches main-ci-alert.yaml a week ahead (#16501).

Severity. npm advisories carry one. pip-audit's JSON does not, so each Python
advisory's severity is the ``database_specific.severity`` of its GHSA record on
OSV (the id itself or its first GHSA alias). An advisory with no GHSA record, or
one whose record names no severity, is ``unknown`` and blocks like a high: a
security gate that reads "could not tell" as clean fails in the one direction
nothing recovers from. trivy names a severity per finding (the distribution's
own for an OS package); its ``UNKNOWN`` blocks the same way.

An allowlist entry is ``{"advisory", "package", "issue", "expires"}``: an
advisory id (a GHSA, PYSEC or CVE id, any id or alias the report gives), the
package it is in, the ``owner/repo#N`` issue that fixes it, and the last day it
holds (``YYYY-MM-DD``). It covers a finding of that package carrying that id.
An image's OS package also matches by its source package, so one entry for
``util-linux`` covers the CVE in ``libblkid1``, ``libmount1`` and the rest.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess  # noqa: S404  # runs pip-audit and gh, fixed argv, no shell
import sys
import time
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import npm_audit_advisories  # noqa: E402  # sibling in .github/scripts, on the sys.path insert above

OSV_VULN_URL = "https://api.osv.dev/v1/vulns/{id}"
BLOCKING = ("critical", "high", "unknown")
# npm's ``moderate`` and GitHub's ``MODERATE`` are the issue's "medium".
_SEVERITY_NAMES = {
    "critical": "critical",
    "high": "high",
    "moderate": "medium",
    "medium": "medium",
    "low": "low",
    "info": "low",
}
_ISSUE = re.compile(r"^(?P<repo>[\w.-]+/[\w.-]+)#(?P<number>[1-9]\d*)$")
_ENTRY_KEYS = ("advisory", "package", "issue", "expires")
ATTEMPTS = 3
# An entry this many days or fewer from its last day is warned about (#16501).
WARN_DAYS = 7


class CannotJudge(Exception):
    """An input or a lookup the gate cannot read: exit 2, never clean."""


def normalise_severity(raw: object) -> str:
    """One of critical, high, medium, low or unknown."""
    return _SEVERITY_NAMES.get(str(raw or "").strip().lower(), "unknown")


def package_key(name: str) -> str:
    """PEP 503's normal form, which leaves an npm name as it is but for case."""
    return re.sub(r"[-_.]+", "-", name).lower()


@dataclass(frozen=True)
class Finding:
    ecosystem: str
    package: str
    version: str
    ids: tuple[str, ...]
    severity: str
    fix: str
    # An image's OS package: the distribution source package it was built from.
    source: str = ""

    @property
    def advisory(self) -> str:
        """The id a person looks up: the GHSA when there is one."""
        return next((i for i in self.ids if i.startswith("GHSA-")), self.ids[0])

    @property
    def blocking(self) -> bool:
        return self.severity in BLOCKING


@dataclass(frozen=True)
class Entry:
    advisory: str
    package: str
    issue: str
    expires: dt.date

    def covers(self, finding: Finding) -> bool:
        names = {package_key(finding.package)}
        if finding.source:
            names.add(package_key(finding.source))
        return package_key(self.package) in names and self.advisory in finding.ids


@dataclass
class Verdict:
    failures: list[str] = field(default_factory=list)
    allowlisted: list[tuple[Finding, Entry]] = field(default_factory=list)
    reported: list[Finding] = field(default_factory=list)
    unused: list[Entry] = field(default_factory=list)
    # Live entries whose last day is within WARN_DAYS of today (#16501).
    expiring: list[Entry] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures


def _retrying[T](what: str, call: Callable[[], T]) -> T:
    """``call()``, tried ``ATTEMPTS`` times; the last error is a CannotJudge."""
    for attempt in range(1, ATTEMPTS + 1):
        try:
            return call()
        except (OSError, ValueError, subprocess.CalledProcessError) as exc:
            if attempt == ATTEMPTS:
                raise CannotJudge(f"{what}: {exc}") from exc
            time.sleep(2 * attempt)
    raise AssertionError("unreachable")  # pragma: no cover


def osv_record(advisory_id: str) -> dict[str, Any] | None:
    """The OSV record of ``advisory_id``, or None when OSV has none (404)."""

    def fetch() -> dict[str, Any] | None:
        url = OSV_VULN_URL.format(id=advisory_id)
        try:
            with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310  # fixed https URL
                record: dict[str, Any] = json.load(response)
                return record
        except urllib.error.HTTPError as exc:
            if exc.code == 404:
                return None
            raise

    return _retrying(f"OSV lookup of {advisory_id}", fetch)


def severity_from_osv(record: dict[str, Any] | None) -> str:
    """The GHSA severity a record carries, ``unknown`` when it carries none."""
    if not record:
        return "unknown"
    return normalise_severity((record.get("database_specific") or {}).get("severity"))


def python_findings(
    report: Any, *, lookup: Callable[[str], dict[str, Any] | None] | None = None
) -> list[Finding]:
    """Every advisory in a pip-audit JSON report, its severity read from OSV."""
    lookup = lookup or osv_record
    deps = report.get("dependencies") if isinstance(report, dict) else None
    if not isinstance(deps, list):
        raise CannotJudge(
            "the pip-audit report has no 'dependencies' list, so it is not a "
            "readable result and is not read as a clean tree"
        )
    severities: dict[str, str] = {}
    findings: dict[tuple[str, str], Finding] = {}
    for dep in deps:
        if "vulns" not in dep:
            # pip-audit lists a dependency it skipped (not on PyPI) with a
            # ``skip_reason`` and no ``vulns``: say so rather than pass it.
            print(
                f"::warning::pip-audit skipped {dep.get('name')}: {dep.get('skip_reason')}"
            )
            continue
        for vuln in dep["vulns"]:
            ids = (vuln["id"], *vuln.get("aliases", []))
            ghsa = next((i for i in ids if i.startswith("GHSA-")), None)
            if ghsa is None:
                severity = "unknown"
            else:
                if ghsa not in severities:
                    severities[ghsa] = severity_from_osv(lookup(ghsa))
                severity = severities[ghsa]
            finding = Finding(
                ecosystem="python",
                package=dep["name"],
                version=dep["version"],
                ids=ids,
                severity=severity,
                fix=", ".join(vuln.get("fix_versions") or []) or "none listed",
            )
            findings.setdefault((package_key(finding.package), vuln["id"]), finding)
    return list(findings.values())


def npm_findings(report: Any, *, workspace: str) -> list[Finding]:
    """Every advisory in an npm report, by the parser the npm lanes share."""
    try:
        advisories = npm_audit_advisories.parse_report(
            report, workspace=workspace, min_severity="info"
        )
    except ValueError as exc:
        raise CannotJudge(f"{workspace}: {exc}") from exc
    return [
        Finding(
            ecosystem=f"npm ({workspace})",
            package=a.package,
            version=a.vulnerable_range,
            ids=tuple(i for i in (a.ghsa, str(a.advisory_id)) if i),
            severity=normalise_severity(a.severity),
            fix="unknown (see the advisory)",
        )
        for a in advisories
    ]


def image_findings(report: Any, *, image: str) -> list[Finding]:
    """Every vulnerability in a trivy image report (``SchemaVersion`` 2).

    An OS package's source package comes from the report's package list, which
    trivy's JSON carries by default; a library has none. The ids are trivy's
    ``VulnerabilityID`` and its ``VendorIDs`` (a CVE's GHSA), so a pip-audit
    entry by GHSA covers the same advisory found in the image.
    """
    if not isinstance(report, dict) or report.get("SchemaVersion") != 2:
        raise CannotJudge(f"{image}: not a trivy JSON report of schema version 2")
    results = report.get("Results")
    if not isinstance(results, list):
        raise CannotJudge(
            f"{image}: the trivy report has no 'Results' list, so it is not a "
            "readable result and is not read as a clean image"
        )
    findings: dict[tuple[str, str, str], Finding] = {}
    for result in results:
        sources = {
            (p.get("Identifier") or {}).get("UID"): p.get("SrcName") or ""
            for p in result.get("Packages") or []
        }
        for vuln in result.get("Vulnerabilities") or []:
            uid = (vuln.get("PkgIdentifier") or {}).get("UID")
            status = vuln.get("Status") or "unknown status"
            finding = Finding(
                ecosystem=f"image {image} ({result.get('Type')})",
                package=vuln["PkgName"],
                version=vuln.get("InstalledVersion", ""),
                ids=(vuln["VulnerabilityID"], *(vuln.get("VendorIDs") or [])),
                severity=normalise_severity(vuln.get("Severity")),
                fix=vuln.get("FixedVersion") or f"no fix published ({status})",
                source=sources.get(uid, ""),
            )
            key = (finding.package, finding.version, vuln["VulnerabilityID"])
            findings.setdefault(key, finding)
    return list(findings.values())


def load_allowlist(data: Any) -> list[Entry]:
    """The allowlist's entries; any malformed one is a CannotJudge."""
    raw = data.get("entries") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        raise CannotJudge("the allowlist has no 'entries' list")
    entries = []
    for index, item in enumerate(raw):
        where = f"allowlist entry {index}"
        if not isinstance(item, dict) or sorted(item) != sorted(_ENTRY_KEYS):
            raise CannotJudge(
                f"{where} must have exactly the keys {', '.join(_ENTRY_KEYS)}"
            )
        if not _ISSUE.match(str(item["issue"])):
            raise CannotJudge(f"{where}: issue {item['issue']!r} is not owner/repo#N")
        try:
            expires = dt.date.fromisoformat(str(item["expires"]))
        except ValueError as exc:
            raise CannotJudge(f"{where}: expires is not YYYY-MM-DD: {exc}") from exc
        entries.append(
            Entry(str(item["advisory"]), str(item["package"]), item["issue"], expires)
        )
    return entries


def github_issue_state(issue: str) -> str:
    """``open`` or ``closed``, from the GitHub API (``gh``, its token from GH_TOKEN)."""
    repo, _, number = issue.partition("#")  # load_allowlist checked the form
    argv = [
        "gh",
        "api",
        f"repos/{repo}/issues/{number}",
        "--jq",
        ".state",
    ]

    def fetch() -> str:
        proc = subprocess.run(  # noqa: S603  # fixed argv
            argv, check=True, capture_output=True, text=True
        )
        return proc.stdout.strip()

    return _retrying(f"the state of {issue}", fetch)


def judge(
    findings: Iterable[Finding],
    entries: Sequence[Entry],
    *,
    today: dt.date,
    issue_state: Callable[[str], str] | None = None,
    fail_expiring: bool = False,
) -> Verdict:
    issue_state = issue_state or github_issue_state
    verdict = Verdict()
    states = {issue: issue_state(issue) for issue in sorted({e.issue for e in entries})}
    for entry in entries:
        name = f"allowlist entry {entry.advisory} ({entry.package}, {entry.issue})"
        if entry.expires < today:
            verdict.failures.append(
                f"{name} expired on {entry.expires}: fix it, or extend it naming why"
            )
        elif entry.expires <= today + dt.timedelta(days=WARN_DAYS):
            verdict.expiring.append(entry)
            if fail_expiring:
                verdict.failures.append(
                    f"{name} expires on {entry.expires}, within {WARN_DAYS} days: "
                    "fix it, or extend it naming why"
                )
        if states[entry.issue] != "open":
            verdict.failures.append(
                f"{name}: {entry.issue} is {states[entry.issue]}, so the entry no longer "
                "names open work: remove it, or name the issue that still fixes it"
            )
    used: set[Entry] = set()
    for finding in findings:
        cover = next((e for e in entries if e.covers(finding)), None)
        if cover is not None:
            used.add(cover)
        if not finding.blocking:
            verdict.reported.append(finding)
        elif cover is not None:
            verdict.allowlisted.append((finding, cover))
        else:
            verdict.failures.append(
                f"{finding.severity} {finding.advisory} in {finding.ecosystem} "
                f"{finding.package} {finding.version} (fixed in {finding.fix}): "
                "upgrade it, or allowlist it naming the issue that fixes it"
            )
    verdict.unused = [e for e in entries if e not in used]
    return verdict


def _table(header: str, rows: list[tuple[str, ...]]) -> list[str]:
    cols = header.count("|") - 1
    return [
        header,
        "|" + "---|" * cols,
        *("| " + " | ".join(r) + " |" for r in rows),
        "",
    ]


def render(verdict: Verdict) -> str:
    out = [
        "### Vulnerability gate: "
        + ("passed" if verdict.passed else "FAILED")
        + " (#16291)",
        "",
    ]
    if verdict.failures:
        out += ["Fails the run:", "", *(f"- {f}" for f in verdict.failures), ""]
    if verdict.expiring:
        out.append(
            f"Allowlist entries that expire within {WARN_DAYS} days ({len(verdict.expiring)}): "
            "each fails the run the day after its date, so fix it or extend it naming why:"
        )
        out += _table(
            "| advisory | package | issue | expires |",
            [
                (e.advisory, e.package, e.issue, str(e.expires))
                for e in verdict.expiring
            ],
        )
    if verdict.allowlisted:
        out.append(
            f"Allowlisted ({len(verdict.allowlisted)}), each held by its issue until it expires:"
        )
        out += _table(
            "| severity | advisory | package | issue | expires |",
            [
                (
                    f.severity,
                    f.advisory,
                    f"{f.package} {f.version}",
                    e.issue,
                    str(e.expires),
                )
                for f, e in verdict.allowlisted
            ],
        )
    if verdict.reported:
        out.append(f"Medium and low ({len(verdict.reported)}), reported only:")
        out += _table(
            "| severity | advisory | package | fixed in |",
            [
                (f.severity, f.advisory, f"{f.package} {f.version}", f.fix)
                for f in verdict.reported
            ],
        )
    if verdict.unused:
        # The dependency and image jobs each judge their own reports, so an
        # entry for the other job's findings is listed here too.
        out += [
            "<details><summary>"
            f"Allowlist entries no finding matched in this job's reports ({len(verdict.unused)}): "
            "an entry no job matches can go once its fix merged"
            "</summary>",
            "",
            *(f"- {e.advisory} ({e.package}, {e.issue})" for e in verdict.unused),
            "",
            "</details>",
            "",
        ]
    return "\n".join(out)


def _read_json(path: str) -> Any:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise CannotJudge(f"{path}: {exc}") from exc


def run_pip_audit(argv: Sequence[str], out: Path) -> int:
    """Run pip-audit; 0 when ``out`` then holds a readable report."""
    out.unlink(missing_ok=True)
    proc = subprocess.run(  # noqa: S603  # argv from the workflow
        [*argv, "--format", "json", "--output", str(out)], check=False
    )
    try:
        report = json.loads(out.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(
            f"::error::pip-audit exited {proc.returncode} and wrote no readable report: {exc}"
        )
        return proc.returncode or 1
    if not isinstance(report, dict) or "dependencies" not in report:
        print(
            f"::error::pip-audit exited {proc.returncode} and its report has no dependencies list"
        )
        return proc.returncode or 1
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = parser.add_subparsers(dest="command", required=True)
    audit = sub.add_parser(
        "pip-audit", help="run pip-audit; 0 when it wrote a readable report"
    )
    audit.add_argument("--out", required=True, type=Path)
    audit.add_argument(
        "pip_audit", nargs=argparse.REMAINDER, help="-- then pip-audit's argv"
    )
    run = sub.add_parser("judge", help="judge the reports against the allowlist")
    run.add_argument("--allowlist", required=True)
    # Once per locked set: a sister repository may hold more than one uv.lock.
    run.add_argument(
        "--pip-audit",
        dest="pip_audit_reports",
        action="append",
        default=[],
        metavar="REPORT",
    )
    run.add_argument("--npm", action="append", default=[], metavar="WORKSPACE=REPORT")
    run.add_argument("--image", action="append", default=[], metavar="IMAGE=REPORT")
    run.add_argument("--summary", help="append the markdown summary here")
    run.add_argument("--today", type=dt.date.fromisoformat, default=None)
    run.add_argument(
        "--fail-expiring",
        action="store_true",
        help="fail on an entry within the warning window (the daily scheduled run)",
    )
    args = parser.parse_args(argv)

    if args.command == "pip-audit":
        command = [a for a in args.pip_audit if a != "--"]
        if not command:
            parser.error("pip-audit needs the command after --")
        return run_pip_audit(command, args.out)

    try:
        findings: list[Finding] = []
        for report in args.pip_audit_reports:
            findings += python_findings(_read_json(report))
        for spec in args.npm:
            workspace, sep, path = spec.partition("=")
            if not sep:
                raise CannotJudge(f"--npm {spec!r} is not WORKSPACE=REPORT")
            findings += npm_findings(_read_json(path), workspace=workspace)
        for spec in args.image:
            image, sep, path = spec.partition("=")
            if not sep:
                raise CannotJudge(f"--image {spec!r} is not IMAGE=REPORT")
            findings += image_findings(_read_json(path), image=image)
        entries = load_allowlist(_read_json(args.allowlist))
        verdict = judge(
            findings,
            entries,
            today=args.today or dt.datetime.now(dt.UTC).date(),
            fail_expiring=args.fail_expiring,
        )
    except CannotJudge as exc:
        print(
            f"::error::vulnerability gate could not judge, so this run is NOT VALIDATED: {exc}"
        )
        return 2
    summary = render(verdict)
    print(summary)
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as handle:
            handle.write(summary + "\n")
    for entry in verdict.expiring:
        print(
            f"::warning::allowlist entry {entry.advisory} ({entry.package}, {entry.issue}) "
            f"expires on {entry.expires}, and the gate fails the day after: "
            "fix it, or extend it naming why"
        )
    for failure in verdict.failures:
        print(f"::error::{failure}")
    return 0 if verdict.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
