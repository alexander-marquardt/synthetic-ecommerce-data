#!/usr/bin/env python3
"""Print the pins a generator release gives the catalogue repository, and their body (gen#536).

    python3 scripts/open_pin_bump_pr.py --tag v1.2.3 \\
        --catalog build/release/catalog/catalog.ndjson \\
        --images-sidecar build/release/images.tar.gz.content-sha256

The catalogue repository (``elastic/prism-retail-and-industrial``) pins the generator's output by
digest in two files, ``catalog_release.json`` (the ONE catalog asset ``ecom-generate compose``
writes, every domain's documents, gen#125: the sha256 of the UNCOMPRESSED documents and their
count) and ``images_release.json`` (the ONE image archive of the combined
catalog, industrial and retail drawings together, gen#706: the content digest and file count
``image_release.py`` writes beside it). A merged decoy or product reached
the catalogue only by hand. ``.github/workflows/release.yaml`` builds both assets on a ``v*`` tag,
uploads the catalog to that release and the image archive to its own release, tagged
``images-<count>-<YYYYMMDD>`` (the archive's file count and the UTC day, gen#804), and runs this
script, which prints the two pin files with the new digests and a pull request body that names
them. It touches no network, opens nothing and reads no token: v3's catalogue load publishes and
pins the images (agent-ops#917, gen#1246).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

#: Where the pins live in the catalogue repository.
TARGET_REPO = "elastic/prism-retail-and-industrial"
#: One image pin for the combined catalog (gen#706): no separate retail and industrial sets.
CATALOG_PIN = "src/prism_retail_and_industrial/data/catalog_release.json"
IMAGES_PIN = "src/prism_retail_and_industrial/data/images_release.json"

CATALOG_ASSET = "catalog.ndjson.gz"
IMAGES_ASSET = "images.tar.gz"
#: The image release's tag: the archive's file count and the UTC day it was built (gen#804).
IMAGES_TAG = re.compile(r"images-(\d+)-(\d{8})")


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


def utc_day() -> str:
    return datetime.now(UTC).strftime("%Y%m%d")


def images_tag(images: dict, tag: str | None) -> str:
    """The image release's tag: ``tag`` checked against the pin, or the pin's count and today."""
    if tag is None:
        return f"images-{images['file_count']}-{utc_day()}"
    match = IMAGES_TAG.fullmatch(tag)
    if match is None:
        raise SystemExit(f"open_pin_bump_pr: --images-tag {tag} is not images-<count>-<YYYYMMDD>")
    try:
        datetime.strptime(match[2], "%Y%m%d")
    except ValueError:
        raise SystemExit(f"open_pin_bump_pr: --images-tag {tag} names no date") from None
    if int(match[1]) != images["file_count"]:
        raise SystemExit(
            f"open_pin_bump_pr: --images-tag {tag} counts {match[1]} files;"
            f" the archive holds {images['file_count']}"
        )
    return tag


def render(pin: dict) -> str:
    return json.dumps(pin, indent=2) + "\n"


def body(tag: str, repository: str, catalog: dict, images: dict) -> str:
    """The pull request body: what moved, where the assets are, and how to check them."""
    url = f"https://github.com/{repository}/releases/tag/"
    return "\n".join(
        [
            f"Bump the generator pins to release `{tag}` of `{repository}`.",
            "",
            f"Release: {url}{tag}",
            f"Images: {url}{images['tag']} (the one archive of the combined catalog)",
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tag", required=True, help="the release tag the assets are uploaded to")
    parser.add_argument(
        "--catalog", type=Path, required=True, help="the UNCOMPRESSED catalog NDJSON"
    )
    parser.add_argument("--images-sidecar", type=Path, required=True)
    parser.add_argument(
        "--images-tag",
        help="the image release's tag, images-<count>-<YYYYMMDD> (default: the count and today)",
    )
    parser.add_argument(
        "--repository",
        default=os.environ.get("GITHUB_REPOSITORY", "alexander-marquardt/synthetic-ecommerce-data"),
        help="the repository the release is in",
    )
    args = parser.parse_args(argv)

    catalog = catalog_pin(args.catalog, args.repository, args.tag)
    images = images_pin(args.images_sidecar, args.repository, args.tag)
    images["tag"] = images_tag(images, args.images_tag)
    text = body(args.tag, args.repository, catalog, images)
    files = {CATALOG_PIN: render(catalog), IMAGES_PIN: render(images)}
    print(f"The pins of {args.tag} for {TARGET_REPO}, and the body that names them:\n")
    print(text)
    for path, content in files.items():
        print(f"--- {path}\n{content}", end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
