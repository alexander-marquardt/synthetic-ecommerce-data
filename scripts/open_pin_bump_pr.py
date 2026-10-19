#!/usr/bin/env python3
"""Open the pin-bump pull request a generator release asks of the catalogue repository (gen#536).

    python3 scripts/open_pin_bump_pr.py --tag v1.2.3 --catalog build/release/catalog.ndjson \\
        --images-sidecar build/release/retail-images.tar.gz.content-sha256 --dry-run

The catalogue repository (``elastic/prism-retail-and-industrial``) pins the generator's output by
digest in two files, ``catalog_release.json`` (the catalog asset: the sha256 of the UNCOMPRESSED
documents and their count) and ``images_release_retail.json`` (the image archive: the content
digest and file count ``image_release.py`` writes beside it). A merged decoy or product reached
the catalogue only by hand. ``.github/workflows/release.yaml`` builds both assets on a ``v*`` tag,
uploads them to the release, and runs this script, which writes the two pin files with the new
digests and opens a pull request that carries them.

``--dry-run`` prints the pull request body and the two files and touches no network. Without it
the script needs ``PIN_BUMP_TOKEN`` in the environment: a token scoped to pull requests and
contents of the target repository only. It is read from the environment and never printed.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

#: Where the pins live in the catalogue repository.
TARGET_REPO = "elastic/prism-retail-and-industrial"
CATALOG_PIN = "src/prism_industrial_products/data/catalog_release.json"
IMAGES_PIN = "src/prism_industrial_products/data/images_release_retail.json"

CATALOG_ASSET = "catalog.ndjson.gz"
IMAGES_ASSET = "retail-images.tar.gz"
TOKEN_ENV = "PIN_BUMP_TOKEN"


def catalog_pin(catalog: Path, repository: str, tag: str) -> dict:
    """The catalog pin: the sha256 and line count of the UNCOMPRESSED documents."""
    data = catalog.read_bytes()
    return {
        "repository": repository,
        "tag": tag,
        "asset": CATALOG_ASSET,
        "content_sha256": hashlib.sha256(data).hexdigest(),
        "documents": data.count(b"\n"),
    }


def images_pin(sidecar: Path, repository: str, tag: str) -> dict:
    """The image pin, from the ``<digest>  <count>`` line ``image_release.py`` writes."""
    parts = sidecar.read_text(encoding="utf-8").split()
    if len(parts) != 2 or len(parts[0]) != 64 or not parts[1].isdigit():
        raise SystemExit(f"open_pin_bump_pr: {sidecar} is not '<sha256>  <file count>'")
    return {
        "repository": repository,
        "tag": tag,
        "asset": IMAGES_ASSET,
        "content_sha256": parts[0],
        "file_count": int(parts[1]),
    }


def render(pin: dict) -> str:
    return json.dumps(pin, indent=2) + "\n"


def body(tag: str, repository: str, catalog: dict, images: dict) -> str:
    """The pull request body: what moved, where the assets are, and how to check them."""
    url = f"https://github.com/{repository}/releases/tag/{tag}"
    return "\n".join(
        [
            f"Bump the generator pins to release `{tag}` of `{repository}`.",
            "",
            f"Release: {url}",
            "",
            f"- `{CATALOG_PIN}`: asset `{catalog['asset']}`, {catalog['documents']:,} documents,"
            f" content sha256 `{catalog['content_sha256']}` (of the uncompressed documents).",
            f"- `{IMAGES_PIN}`: asset `{images['asset']}`, {images['file_count']:,} files,"
            f" content sha256 `{images['content_sha256']}`.",
            "",
            "Both digests were computed by the release workflow from the files it uploaded.",
            "Check one yourself: download the asset, decompress the catalog, and compare its",
            "sha256 and line count with the pin above.",
            "",
        ]
    )


def _api(method: str, url: str, token: str, payload: dict | None = None) -> dict:
    request = urllib.request.Request(  # noqa: S310 -- an https GitHub API URL built below
        url,
        data=None if payload is None else json.dumps(payload).encode(),
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:  # noqa: S310
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as error:
        raise SystemExit(f"open_pin_bump_pr: {method} {url}: HTTP {error.code}") from error


def open_pull_request(
    token: str, target: str, branch: str, tag: str, text: str, files: dict
) -> str:
    """Push ``files`` (path -> text) to ``branch`` of ``target`` and open a PR; return its URL."""
    api = f"https://api.github.com/repos/{target}"
    default = _api("GET", api, token)["default_branch"]
    head = _api("GET", f"{api}/git/ref/heads/{default}", token)["object"]["sha"]
    _api("POST", f"{api}/git/refs", token, {"ref": f"refs/heads/{branch}", "sha": head})
    for path, content in files.items():
        current = _api("GET", f"{api}/contents/{path}?ref={default}", token)
        _api(
            "PUT",
            f"{api}/contents/{path}",
            token,
            {
                "message": f"chore(pins): bump {path.rsplit('/', 1)[-1]} to release {tag}",
                "content": base64.b64encode(content.encode()).decode(),
                "sha": current["sha"],
                "branch": branch,
            },
        )
    made = _api(
        "POST",
        f"{api}/pulls",
        token,
        {"title": f"chore(pins): bump the generator pins to {tag}", "head": branch,
         "base": default, "body": text},
    )  # fmt: skip
    return made["html_url"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tag", required=True, help="the release tag the assets are uploaded to")
    parser.add_argument(
        "--catalog", type=Path, required=True, help="the UNCOMPRESSED catalog NDJSON"
    )
    parser.add_argument("--images-sidecar", type=Path, required=True)
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "alexander-marquardt/synthetic-ecommerce-data"),
        help="the repository the release is in",
    )
    parser.add_argument("--target", default=TARGET_REPO, help="the repository that holds the pins")
    parser.add_argument(
        "--dry-run", action="store_true", help="print the body and the pins; no network"
    )
    args = parser.parse_args(argv)

    catalog = catalog_pin(args.catalog, args.repository, args.tag)
    images = images_pin(args.images_sidecar, args.repository, args.tag)
    text = body(args.tag, args.repository, catalog, images)
    files = {CATALOG_PIN: render(catalog), IMAGES_PIN: render(images)}
    if args.dry_run:
        print(f"DRY RUN: would open a pull request in {args.target} with this body:\n")
        print(text)
        for path, content in files.items():
            print(f"--- {path}\n{content}", end="")
        return 0
    token = os.environ.get(TOKEN_ENV, "")
    if not token:
        print(
            f"open_pin_bump_pr: {TOKEN_ENV} is not set; use --dry-run to print the body",
            file=sys.stderr,
        )
        return 2
    branch = f"pins/generator-{args.tag}"
    print(open_pull_request(token, args.target, branch, args.tag, text, files))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
