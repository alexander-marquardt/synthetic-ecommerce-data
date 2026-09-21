#!/usr/bin/env python3
"""Every drawing this catalog references must already exist on the asset host.

    python scripts/verify_published_assets.py
    python scripts/verify_published_assets.py --manifest golden-catalog/images.jsonl

A regeneration mints new product ids, so it mints new image ids, so it
invalidates every URL the previous catalog published. Nothing coupled the two:
a catalog could be generated, committed, loaded onto a cluster and served while
the drawings its records point at had never been rendered, let alone published.
That is not hypothetical -- it shipped. 499 of this catalog's 500 image ids
were dead on the host, which is 4,680 of 4,689 products rendering a broken
image, and every gate on both sides of the seam was green: the generator's
audit measures the files the render run just wrote, and the host's tests
measure the site build. Neither one looks at the other.

This is that missing check, and it is a SET COMPARISON over the whole
manifest, deliberately. One image per product type -- the obvious cheap
version -- is exactly the shape that would have passed here: the single
surviving id was an ``end_mill_square``, so a per-type sample would have found
``end_mill_square`` alive and reported eleven dead types out of twelve while
the truth was 499 dead ids out of 500.

Where the host's file list comes from
-------------------------------------
The GitHub git-trees API, in one request for the whole tree. **Not** an HTTP
sweep of the URLs. The host is GitHub Pages behind Fastly and it answers a
concurrent sweep with 404s for files that exist: measured, a 16-way HEAD sweep
of these 1,000 URLs returned 998 404s and 2 200s, while the same URLs fetched
one at a time returned 200 for every file present. An HTTP prober that was
believed would have reported a catastrophe on a healthy host, and one that was
"fixed" by lowering the concurrency would take an hour. ``--probe-http`` is
kept for confirming a publish by hand, serialised and slow, and is not what CI
runs.

Ordering this imposes, which is the point
-----------------------------------------
Publish the drawings to the asset host FIRST, then land the catalog that
references them. A regeneration PR stays red until its images are live, which
is the coupling that did not exist.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

#: The repository serving https://alexmarquardt.com, and the path inside it
#: that the published URLs map onto.
HOST_REPO = "alexander-marquardt/alexmarquardt.com"
HOST_BRANCH = "main"
HOST_PREFIX = "static/ecommerce-demo-assets/images/industrial/"

#: The manifest keys naming a file that must be hosted. Both, because a record
#: carries a URL per profile and hosting one leaves the other a dead link.
#: Same keys the host's importer publishes from, for the same reason: the
#: manifest is the single place that decides what the published tree looks
#: like.
PATH_KEYS = ("path", "detail_path")


def published_paths(manifest: Path) -> dict[str, str]:
    """``{path relative to the host prefix: image id}`` for the whole manifest."""
    out: dict[str, str] = {}
    for number, line in enumerate(manifest.read_text("utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        row = json.loads(line)
        ref = row.get("image_id") or row.get("image_ref")
        if ref is None:
            raise SystemExit(
                f"{manifest}:{number}: row names no image id; it carries {sorted(row)}"
            )
        for key in PATH_KEYS:
            if key in row:
                out[str(row[key])] = str(ref)
    return out


def hosted_paths(repo: str, branch: str, prefix: str, token: str | None) -> set[str]:
    """Every file under ``prefix`` on the host, from ONE git-trees request."""
    url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "verify-published-assets"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    # A truncated tree is a silently short answer, and a short answer here
    # reads as "these files are missing". Refuse instead.
    if payload.get("truncated"):
        raise SystemExit(
            f"the git-trees response for {repo}@{branch} is TRUNCATED, so the hosted set "
            "would be understated and every absent path a false alarm. Clone the host "
            "and pass --host-tree instead."
        )
    return {
        entry["path"][len(prefix) :]
        for entry in payload.get("tree", ())
        if entry.get("type") == "blob" and entry["path"].startswith(prefix)
    }


def hosted_from_checkout(root: Path, prefix: str) -> set[str]:
    base = root / prefix
    return {str(path.relative_to(base)) for path in base.rglob("*") if path.is_file()}


def probe_http(
    paths: list[str], base_url: str, pause: float, attempts: int = 4
) -> dict[str, int | str]:
    """Fetch each URL, ONE AT A TIME. See the module docstring before parallelising.

    A transport failure is retried and an HTTP status is not. The two are
    different findings and only one of them is about the file: a sweep of
    1,000 URLs over this host dropped 10 connections on a run where every one
    of those 10 answered 200 when asked again, and reporting them beside real
    statuses would have read as ten broken images. A status -- 200, 404 -- is
    the host's answer and is taken as given.
    """
    out: dict[str, int | str] = {}
    for path in paths:
        url = base_url + urllib.parse.quote(path)
        delay = pause
        for attempt in range(attempts):
            request = urllib.request.Request(
                url, method="HEAD", headers={"User-Agent": "Mozilla/5.0"}
            )
            try:
                with urllib.request.urlopen(request, timeout=45) as response:
                    out[path] = response.status
                break
            except urllib.error.HTTPError as error:
                out[path] = error.code
                break
            except Exception as error:  # noqa: BLE001 -- a transport failure is not a 404
                out[path] = f"ERR:{type(error).__name__}"
                if attempt + 1 < attempts:
                    time.sleep(max(delay, 0.5) * (2**attempt))
        time.sleep(pause)
    return out


def main(argv: list[str] | None = None) -> int:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=root / "golden-catalog" / "images.jsonl")
    parser.add_argument("--repo", default=HOST_REPO)
    parser.add_argument("--branch", default=HOST_BRANCH)
    parser.add_argument("--prefix", default=HOST_PREFIX)
    parser.add_argument(
        "--host-tree",
        type=Path,
        default=None,
        help="a checkout of the host repository, instead of the git-trees API",
    )
    parser.add_argument("--token", default=None, help="GitHub token (public repo: not needed)")
    parser.add_argument(
        "--probe-http",
        action="store_true",
        help="additionally fetch every URL, serialised -- for confirming a publish by hand",
    )
    parser.add_argument("--pause", type=float, default=0.05, help="seconds between HTTP probes")
    parser.add_argument(
        "--base-url",
        default="https://alexmarquardt.com/ecommerce-demo-assets/images/industrial/",
    )
    args = parser.parse_args(argv)

    wanted = published_paths(args.manifest)
    if not wanted:
        raise SystemExit(
            f"{args.manifest} names no published file. An empty wanted set passes this check "
            "vacuously, so it is refused rather than reported as OK."
        )

    if args.host_tree is not None:
        hosted = hosted_from_checkout(args.host_tree, args.prefix)
    else:
        hosted = hosted_paths(args.repo, args.branch, args.prefix, args.token)
    if not hosted:
        raise SystemExit(
            f"no files found under {args.prefix} on {args.repo}@{args.branch}. That would make "
            "every referenced path look missing, so it is refused as a collection error rather "
            "than reported as 1,000 dead links."
        )

    missing = sorted(set(wanted) - hosted)
    unreferenced = sorted(hosted - set(wanted))

    print(f"manifest                 : {args.manifest}")
    print(f"image ids referenced     : {len(set(wanted.values()))}")
    print(f"files the catalog needs  : {len(wanted)}")
    print(f"files hosted             : {len(hosted)}")
    print(f"needed but NOT hosted    : {len(missing)}")
    print(f"hosted but unreferenced  : {len(unreferenced)}")

    if missing:
        by_type = Counter(path.split("/", 1)[0] for path in missing)
        print(f"\nDEAD: {len(missing)} of {len(wanted)} referenced files are not on the host.")
        for type_key, count in sorted(by_type.items()):
            print(f"  {type_key:<22}{count:>6}")
        for path in missing[:10]:
            print(f"  {path}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
        print(
            "\nRender and publish before landing this catalog:\n"
            "  python scripts/render_catalog.py golden-catalog --out out/images\n"
            "  # in a checkout of the host repository:\n"
            "  python3 scripts/import_industrial_images.py \\\n"
            "      --manifest <this repo>/golden-catalog/images.jsonl \\\n"
            "      --images   <this repo>/out/images"
        )

    # Unreferenced files are NOT a failure here. Previous generations are kept
    # on the host on purpose: the documented rollback for a catalog change is
    # to revert the commit, which re-binds the previous generation's index, and
    # that generation's records point at those files. Pruning them would make
    # the rollback publish 4,000 broken images.
    if unreferenced:
        print(
            f"\n{len(unreferenced)} hosted file(s) this catalog does not reference. Not a "
            "failure: earlier generations are retained so that reverting a catalog change "
            "still has its drawings."
        )

    if args.probe_http:
        print(f"\nfetching {len(wanted)} URLs one at a time ...")
        codes = probe_http(sorted(wanted), args.base_url, args.pause)
        tally = Counter(codes.values())
        print(f"  {dict(tally)}")
        bad = sorted(path for path, code in codes.items() if code != 200)
        for path in bad[:10]:
            print(f"  {codes[path]}  {path}")
        if bad:
            print(f"  {len(bad)} URL(s) did not return 200")
            return 1

    if missing:
        return 1
    print("\nOK: every file this catalog references is on the asset host.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
