"""Collect the archived pages behind the lock-nut and set-screw price census
entries (#69). Its parser is ``scripts/price_census_parse.py``.

    uv run python scripts/price_census_collect.py

Every request goes to web.archive.org and nowhere else: the CDX index to
enumerate captures, then the ``id_`` (unmodified) form of each capture.
Requests are serial, single process, 3-5 s jittered from the end of one
response to the next, with escalating backoff on 429 and 5xx. Each response is
cached under ``raw/price_census/`` (gitignored: pages are analysis input and
never ship), so a rerun sends only the requests whose cache file is missing,
and every request sent is appended to ``requests.jsonl`` for the request
accounting.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "raw" / "price_census"
LOG = RAW / "requests.jsonl"

#: The manifest's string carries a personal address; this one names only the
#: project, so the census can be rerun by anyone without impersonating it.
USER_AGENT = (
    "prism-demo-research/1.0 "
    "(+https://github.com/alexander-marquardt/synthetic-ecommerce-data)"
)
CDX = "https://web.archive.org/cdx/search/cdx"
WAYBACK = "https://web.archive.org/web/{ts}id_/{url}"
#: The 2015-2021 window #57 enumerated; 2024 captures are soft-404s.
WINDOW = {"from": "2015", "to": "2021"}
DELAY_S = (3.0, 5.0)
BACKOFF_S = (30, 60, 120, 240)

#: Group pages under the distributor's own label whose slug names a locknut.
#: Content decides what is kept: the parser keeps a page only when its group
#: specs say nylon insert.
LOCKNUT_GROUP_PREFIX = "www.grainger.com/product/GRAINGER-APPROVED-"
LOCKNUT_SLUG = re.compile(r"Locknut", re.I)
#: Slugs that name a locknut type that is not nylon-insert.
OTHER_LOCKNUT = re.compile(r"Conduit|Deformed|Serrated|Flange|Conical|Jam", re.I)
#: The category list pages: every brand's SKUs, one row each.
CATEGORY_PREFIXES = {
    "locknut_category": "www.grainger.com/category/locknuts/nuts/fasteners/ecatalog/N-8lj",
    "setscrew_category": "www.grainger.com/category/socket-set-screws/",
}
GROUP_PAGE = re.compile(r"-WP\d+")
#: At most this many category pages per type; 32 rows a page.
MAX_CATEGORY_PAGES = 40


def _get(url: str, phase: str) -> tuple[int, bytes]:
    """Fetch ``url`` once, backing off on 429/5xx, and log the request(s)."""
    for attempt, wait in enumerate((0, *BACKOFF_S)):
        if wait:
            time.sleep(wait)
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:  # noqa: S310
                status, body = resp.status, resp.read()
        except urllib.error.HTTPError as err:
            status, body = err.code, b""
        except (urllib.error.URLError, TimeoutError) as err:
            status, body = 0, str(err).encode()
        with LOG.open("a") as log:
            log.write(json.dumps({"phase": phase, "url": url, "status": status,
                                  "attempt": attempt, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ",
                                                                           time.gmtime())}) + "\n")
        time.sleep(random.uniform(*DELAY_S))  # noqa: S311
        if status not in (0, 429) and status < 500:
            return status, body
    return status, body


def cached(name: str, url: str, phase: str) -> bytes | None:
    """The cached response for ``name``, fetching ``url`` when it is missing."""
    path = RAW / name
    if path.exists():
        return path.read_bytes()
    status, body = _get(url, phase)
    if status != 200:
        print(f"  {status} {url}", file=sys.stderr)
        return None
    path.write_bytes(body)
    return body


def cdx(name: str, prefix: str) -> list[tuple[str, str]]:
    """``(timestamp, original)`` for every 200 capture under ``prefix`` in the
    window, one per URL key (the latest wins)."""
    query = {"url": prefix, "matchType": "prefix", **WINDOW, "fl": "timestamp,original,urlkey",
             "filter": "statuscode:200"}
    body = cached(f"cdx_{name}.txt", f"{CDX}?{urllib.parse.urlencode(query)}", "enumeration")
    latest: dict[str, tuple[str, str]] = {}
    for line in (body or b"").decode().splitlines():
        ts, original, key = line.split(" ", 2)
        if key not in latest or ts > latest[key][0]:
            latest[key] = (ts, original)
    return sorted(latest.values(), key=lambda capture: capture[1])


def page_name(kind: str, ts: str, url: str) -> str:
    digest = hashlib.sha256(url.encode()).hexdigest()[:12]
    return f"{kind}/{ts}_{digest}.html"


def main() -> None:
    for kind in ("locknut_group", *CATEGORY_PREFIXES):
        (RAW / kind).mkdir(parents=True, exist_ok=True)
    groups: dict[str, tuple[str, str]] = {}
    for ts, url in cdx("locknut_group", LOCKNUT_GROUP_PREFIX):
        path = urllib.parse.urlsplit(url).path
        if LOCKNUT_SLUG.search(path) and not OTHER_LOCKNUT.search(path) and GROUP_PAGE.search(path):
            # One capture per group page: the query-string variants are the same page.
            group = GROUP_PAGE.search(path).group(0)
            if group not in groups or ts > groups[group][0]:
                groups[group] = (ts, url)
    targets = [("locknut_group", ts, url) for ts, url in groups.values()]
    for kind, prefix in CATEGORY_PREFIXES.items():
        captures = cdx(kind, prefix)
        targets += [(kind, ts, url) for ts, url in captures[:MAX_CATEGORY_PAGES]]
    manifest = []
    for kind, ts, url in targets:
        name = page_name(kind, ts, url)
        phase = "fetch_group" if kind == "locknut_group" else "fetch_category"
        body = cached(name, WAYBACK.format(ts=ts, url=url), phase)
        manifest.append({"kind": kind, "timestamp": ts, "url": url,
                         "file": name if body is not None else None})
    (RAW / "pages.json").write_text(json.dumps(manifest, indent=1) + "\n")
    print(f"{len(manifest)} pages, {sum(1 for m in manifest if m['file'])} cached")


if __name__ == "__main__":
    main()
