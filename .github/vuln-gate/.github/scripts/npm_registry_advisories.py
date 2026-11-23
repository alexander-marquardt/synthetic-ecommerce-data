"""Read a ``package-lock.json`` and ask the registry which of it is vulnerable.

This is the DATA SOURCE for both npm advisory lanes. It replaces
``npm audit --json`` — not the questions asked of the answer, which still live
in ``.github/scripts/npm_audit_advisories.py`` (the scheduled "does the tree
carry an advisory?" scan of #5013, and the PR-lane "does this change ADD one?"
gate of #5695). Only where the advisory list comes from moved (#5793).

Why ``npm audit`` stopped being usable (#5793)
----------------------------------------------
``npm audit`` has two registry paths and, as of this change, BOTH are broken
for reasons outside this repo:

* npm **10.9.0** (the pinned CI resolver) falls back to
  ``POST /-/npm/v1/security/audits/quick``, which the registry has RETIRED. It
  answers ``400 Bad Request`` with ``npm-notice: This endpoint is being
  retired. Use the bulk advisory endpoint instead.`` npm then writes its error
  object to stdout in place of a report, and the gate correctly refuses it
  ("not an npm audit report: no 'vulnerabilities' key"). That is a
  DEPRECATION, so it does not self-heal — measured on GitHub's runner, on an
  untouched ``main`` checkout, and on a single-dependency throwaway package.
* npm **11.4.2** reaches the bulk endpoint, and fails differently: the registry
  answers ``200`` with a **gzip body and no ``Content-Encoding`` header**, so
  npm's JSON parser chokes on the gzip magic bytes —
  ``invalid json response body … Unexpected token '\\x1f'``.

Both failures are in npm's transport, not in its data. So this script asks the
supported endpoint directly and does its own decoding, which is what makes the
undeclared-gzip case a non-event here: the body is sniffed for the gzip magic
number and decompressed whether or not the header admits it.

What it emits
-------------
The registry's advisory objects **verbatim**, wrapped in a small self-describing
envelope::

    {"bulkAdvisoryReportVersion": 1,
     "endpoint": "…/security/advisories/bulk",
     "packagesQueried": 501,
     "advisories": {"brace-expansion": [{"id": 1124334, "severity": "high", …}]}}

The envelope exists so a report can never be mistaken for something else:
``{}`` from a bulk response and ``{}`` from a truncated file are
indistinguishable, and "indistinguishable from empty" is precisely the
silent-drop direction this whole design refuses. The marker key is what
``npm_audit_advisories.py`` dispatches on; a file without it is rejected rather
than read as a clean tree. Key ORDER is load-bearing for the same reason and is
pinned by a test: ``json.dumps`` preserves insertion order, so the marker is
serialised first and ``advisories`` last — a truncated write therefore always
lands inside ``advisories`` and yields invalid JSON, never a shorter report
that would parse as a smaller advisory set.

``packagesQueried`` is a diagnostic, not a second gate: it is printed to the
step log and kept in the artifact so "the scan asked about 501 packages" is
readable after the fact. What actually prevents an empty scan reading as a
clean tree is ``lockfile_dependencies``, which refuses to build a query at all
from a lockfile it could not enumerate. No consumer branches on the number.

Advisory identity is UNCHANGED (#5793 acceptance)
-------------------------------------------------
The arrivals-vs-departures diff in ``npm_audit_advisories.py`` keys on the
registry's numeric advisory id. In an ``npm audit --json`` report that id is
``via.source``; in a bulk response it is ``id``. They are the same id from the
same feed — ``npm audit`` builds its ``via`` entries out of exactly these
objects — so the comparison key survives the source change untouched, and no
re-keying (GHSA slug, package/path pair) was needed.

The registry mints a NEW numeric id when an advisory's affected range is
revised, so an id is not eternal. That is harmless here and was equally true of
``npm audit``: the gate queries HEAD and its baseline in the same run against
the same registry state, so a re-mint moves both sides together and produces no
phantom arrival.

Failure direction
-----------------
Exit non-zero, loudly, on anything that is not a decoded advisory response: a
4xx (which is how the NEXT endpoint retirement will announce itself, and it
must red exactly as the last one did), an undecodable body, a lockfile that
enumerates no packages. A finding is NOT a failure — advisories are this
script's payload, so it exits 0 with them. Only ``npm_audit_advisories.py``
turns an advisory into a verdict.

What is retried, and what is not, is a distinction between "later" and "wrong".
Retried a few times, because a flaky gate teaches people to re-run rather than
to read: network errors (including a truncated body, which arrives as
``http.client.IncompleteRead`` and is NOT an ``OSError``), 5xx, a ``200`` whose
body will not decode, and the two 4xx codes that mean later — ``408`` and
``429``. Never retried: every other 4xx, because a request the registry rejects
does not become right by repetition, and a retirement is ``400`` / ``404`` /
``410``. Every path that exhausts its retries still FAILS; "retried" never
becomes "gave up and reported nothing".
"""

from __future__ import annotations

import argparse
import gzip
import http.client
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

# The endpoint npm's own ``npm audit`` uses (and the one its retirement notice
# for ``/audits/quick`` points at).
BULK_ENDPOINT = "https://registry.npmjs.org/-/npm/v1/security/advisories/bulk"

# The envelope marker. Bumped only if the envelope's SHAPE changes; the
# advisory objects inside are the registry's and are not versioned by us.
REPORT_VERSION_KEY = "bulkAdvisoryReportVersion"
REPORT_VERSION = 1

# Package names per request. One request carried all 501 of ``search-ui``'s
# packages in testing, so this is headroom against a bigger tree rather than a
# measured limit — the endpoint documents none, and a request that is refused
# for size would fail the whole scan rather than degrade.
CHUNK_SIZE = 400

# Retries apply to network errors, 5xx, and the two 4xx codes that mean "later"
# rather than "wrong" (see module docstring). 408 Request Timeout and 429 Too
# Many Requests are transient by definition; a retirement is 400 / 404 / 410, so
# carving these two out does not soften the fail-loudly-on-a-retirement rule.
RETRY_DELAYS = (1.0, 3.0)
RETRYABLE_CLIENT_ERRORS = frozenset({408, 429})

# A transport is (url, body) -> (status, bytes). Injected so the tests can
# drive the decoder over responses a live registry will not produce on demand.
Transport = Callable[[str, bytes], "tuple[int, bytes]"]


def lockfile_dependencies(lockfile: dict[str, Any]) -> dict[str, list[str]]:
    """Every ``name -> [versions]`` the lockfile resolves, as the bulk query wants it.

    Reads ``packages`` (lockfileVersion 2/3) and falls back to the legacy
    ``dependencies`` tree (lockfileVersion 1). Both are enumerated rather than
    only the top level, because a transitive dependency is exactly where the
    advisories that matter live (#5007's ``brace-expansion`` was eight levels
    of nobody's direct dependency).

    Skipped: the root entry (key ``""`` — the project itself is not published,
    and npm does not audit it), workspace links (``link: true``, whose real
    entry appears under its own path), and anything with no resolved version.

    A lockfile that yields NO packages raises. An empty query would come back
    empty, and an empty advisory set reads as a clean tree — the silent-drop
    direction. A tree with no dependencies is not a thing this repo has, so the
    honest reading of "zero packages" is "the lockfile was not understood".
    """
    packages = lockfile.get("packages")
    versions: dict[str, set[str]] = {}
    if isinstance(packages, dict):
        for path, entry in packages.items():
            if not path or not isinstance(entry, dict) or entry.get("link"):
                continue
            version = entry.get("version")
            if not isinstance(version, str) or not version:
                continue
            name = entry.get("name")
            if not isinstance(name, str) or not name:
                name = path.rsplit("node_modules/", 1)[-1]
            versions.setdefault(name, set()).add(version)
    elif isinstance(lockfile.get("dependencies"), dict):
        _walk_v1(lockfile["dependencies"], versions)
    else:
        raise ValueError(
            "not a package-lock.json: no 'packages' (lockfileVersion 2/3) and no "
            "'dependencies' (lockfileVersion 1) map. Regenerate the lockfile with "
            "`npx npm@10.9.0 install --package-lock-only --no-audit`."
        )
    if not versions:
        raise ValueError(
            "the lockfile resolved no packages at all, which is a lockfile this "
            "script failed to read, not a dependency-free tree — and an empty "
            "query would come back empty and read as a clean tree. Refusing."
        )
    return {name: sorted(found) for name, found in sorted(versions.items())}


def _walk_v1(tree: dict[str, Any], into: dict[str, set[str]]) -> None:
    """Collect ``name -> versions`` from a lockfileVersion 1 ``dependencies`` tree."""
    for name, entry in tree.items():
        if not isinstance(entry, dict):
            continue
        version = entry.get("version")
        if isinstance(version, str) and version:
            into.setdefault(name, set()).add(version)
        nested = entry.get("dependencies")
        if isinstance(nested, dict):
            _walk_v1(nested, into)


def decode_body(raw: bytes, *, url: str) -> Any:
    """Decode a registry response body, gzip-declared or not.

    The undeclared-gzip case is the live #5793 defect, not a hypothetical: the
    bulk endpoint answers ``200`` with a gzip body and NO ``Content-Encoding``
    header, which is what breaks npm 11's own audit. Sniffing the magic number
    handles it whether the header is present, absent or wrong.

    ``EOFError`` is caught alongside ``OSError`` because gzip damage splits into
    two exception families and only one of them is an ``OSError``: a corrupt
    middle or a bad header raises ``BadGzipFile`` (an ``OSError``), while a
    TRUNCATED tail — the likeliest damage on a flaky transfer, and the case the
    magic-number sniff guarantees we enter this branch for — raises a bare
    ``EOFError``, which is not. Uncaught it would escape ``main``'s handler too
    and surface as a traceback: still a non-zero exit and still no report
    written, but without the message that says why, and skipping the retry a
    truncated transfer is exactly the candidate for.
    """
    if raw[:2] == b"\x1f\x8b":
        try:
            raw = gzip.decompress(raw)
        except (OSError, EOFError) as exc:
            raise ValueError(
                f"{url} returned a body that starts as gzip but does not "
                f"decompress ({type(exc).__name__}: {exc}). A truncated or "
                "corrupt transfer is a broken scan, not a clean tree."
            ) from exc
    try:
        return json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError(
            f"{url} did not return JSON ({exc}). First bytes: {raw[:80]!r}. This "
            "is how an endpoint change announces itself — do not read it as a "
            "clean tree."
        ) from exc


ALLOWED_SCHEMES = frozenset({"http", "https"})


def _urllib_transport(url: str, body: bytes) -> tuple[int, bytes]:
    scheme = urllib.parse.urlsplit(url).scheme
    if scheme not in ALLOWED_SCHEMES:
        # ``--endpoint`` is caller-supplied, so the default being https is not
        # on its own a guarantee. Checking here rather than trusting the
        # default is what makes the suppression below TRUE: ``urlopen`` also
        # speaks ``file:`` and ``ftp:``, and an endpoint that reads a local
        # path would hand this script an "advisory report" of somebody's
        # choosing. Rejected explicitly rather than left to ruff's warning.
        raise ValueError(
            f"refusing to fetch advisories over {scheme!r}: --endpoint must be "
            f"http or https, got {url!r}"
        )
    request = urllib.request.Request(  # noqa: S310  # scheme checked immediately above
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    try:
        # noqa: S310 — same check; ``urlopen`` cannot reach a non-http scheme here.
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            return int(response.status), bytes(response.read())
    except urllib.error.HTTPError as exc:
        return int(exc.code), bytes(exc.read())


def _post(
    url: str,
    query: dict[str, list[str]],
    *,
    transport: Transport,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, Any]:
    """POST one chunk, retrying only what repetition can fix.

    Three outcomes are transient and retried — a network-level error, a 5xx, and
    a ``200`` whose body will not decode (the likeliest cause being a truncated
    transfer). One is not: a 4xx outside ``RETRYABLE_CLIENT_ERRORS``, which is
    the shape a retirement takes and does not become right by repetition.

    ``http.client.HTTPException`` sits beside ``OSError`` in the network arm
    because ``IncompleteRead`` — a truncated response body, the same damage
    class as the undecodable gzip above — derives from it and NOT from
    ``OSError``, so it would otherwise escape unretried and untranslated.
    """
    body = json.dumps(query).encode("utf-8")
    last = ""
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            status, raw = transport(url, body)
        except (OSError, http.client.HTTPException) as exc:
            # Network-level: DNS, reset, timeout, truncated body.
            last = f"network error: {type(exc).__name__}: {exc}"
        else:
            if status == 200:
                try:
                    decoded = decode_body(raw, url=url)
                except ValueError as exc:
                    last = str(exc)
                else:
                    if not isinstance(decoded, dict):
                        # A shape error is the registry answering a different
                        # question, not a damaged transfer — asking again gets
                        # the same answer, so fail now rather than in 4 seconds.
                        raise ValueError(
                            f"{url} returned {type(decoded).__name__}, expected "
                            "a {package: [advisory, …]} object"
                        )
                    return decoded
            else:
                last = f"HTTP {status}: {decode_error_text(raw)}"
                if status < 500 and status not in RETRYABLE_CLIENT_ERRORS:
                    # A 4xx is the shape a retirement takes (this is exactly how
                    # /audits/quick announced its own, #5793). Repetition cannot
                    # fix a request the registry rejects, and retrying would only
                    # delay the loud failure that is the correct outcome.
                    break
        if attempt < len(RETRY_DELAYS):
            sleep(RETRY_DELAYS[attempt])
    raise ValueError(
        f"the npm bulk advisory endpoint did not answer with a report — {last}. "
        "The advisory scan produced nothing, which is a broken scan and NOT a "
        "clean tree, so this fails rather than passing. If the endpoint itself "
        f"has changed, see {url} and https://api-docs.npmjs.com/#tag/Audit."
    )


def decode_error_text(raw: bytes) -> str:
    """A short, readable rendering of an error body for the failure message."""
    text = raw[:400].decode("utf-8", errors="replace").strip()
    return text or "(empty body)"


def fetch_advisories(
    query: dict[str, list[str]],
    *,
    endpoint: str = BULK_ENDPOINT,
    transport: Transport | None = None,
    chunk_size: int = CHUNK_SIZE,
    sleep: Callable[[float], None] = time.sleep,
) -> dict[str, list[Any]]:
    """Ask the bulk endpoint about every package, in chunks, and merge the answers.

    The endpoint does the semver matching: it is sent the versions the lockfile
    actually resolves and returns only the advisories that apply to them, so
    this script carries no semver implementation of its own to disagree with
    npm's.
    """
    post = transport or _urllib_transport
    names = list(query)
    merged: dict[str, list[Any]] = {}
    for start in range(0, len(names), chunk_size):
        chunk = {name: query[name] for name in names[start : start + chunk_size]}
        for name, advisories in _post(
            endpoint, chunk, transport=post, sleep=sleep
        ).items():
            if not isinstance(advisories, list):
                raise ValueError(
                    f"{endpoint} returned {type(advisories).__name__} for "
                    f"{name!r}, expected a list of advisories"
                )
            merged.setdefault(name, []).extend(advisories)
    return merged


def build_report(
    advisories: dict[str, list[Any]], *, packages_queried: int, endpoint: str
) -> dict[str, Any]:
    """Wrap the registry's answer in the self-describing envelope."""
    return {
        REPORT_VERSION_KEY: REPORT_VERSION,
        "endpoint": endpoint,
        "packagesQueried": packages_queried,
        "advisories": advisories,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lockfile", help="path to a package-lock.json")
    parser.add_argument(
        "--out", required=True, help="write the advisory report (JSON) here"
    )
    parser.add_argument(
        "--endpoint",
        default=BULK_ENDPOINT,
        help=(
            "the bulk advisory endpoint (default: the public registry). "
            "Overridden only by this repo's own tests, which stand a local HTTP "
            "server up so the response decoding is proven over a real socket "
            "rather than a stubbed transport"
        ),
    )
    args = parser.parse_args(argv)

    try:
        lockfile = json.loads(Path(args.lockfile).read_text(encoding="utf-8"))
        query = lockfile_dependencies(lockfile)
        advisories = fetch_advisories(query, endpoint=args.endpoint)
    except (OSError, ValueError) as exc:
        print(f"::error::{args.lockfile}: {exc}", file=sys.stderr)
        return 1

    report = build_report(
        advisories, packages_queried=len(query), endpoint=args.endpoint
    )
    Path(args.out).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(
        f"{args.lockfile}: queried {len(query)} packages, "
        f"{sum(len(v) for v in advisories.values())} advisory record(s) returned "
        f"across {len(advisories)} package(s) -> {args.out}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
