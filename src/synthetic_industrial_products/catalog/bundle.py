"""The image bundle: every SKU's drawing, rebuilt from a committed catalog, in one archive.

    sip-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz

The drawings are NEVER committed (elastic/prism-industrial-products#103): the
repository commits the catalog, whose ``images.jsonl`` carries each SKU image's
path and sha256, and the bundle is rebuilt from that. This module is the
rebuild. It reads the committed ``nested.jsonl``, draws every variant, and
refuses unless every drawing's digest equals the one ``images.jsonl`` records --
so an archive built here IS the set the catalog names, byte for byte, and a
generator change that moved a drawing without a regeneration cannot ship
under the old catalog.

The archive is deterministic: members sorted, every timestamp and owner zeroed,
gzip header without a time. The same catalog makes the same archive, so its
sha256 is a pin a customization can hold (the ``images_release`` pin in
elastic/prism-industrial-products).
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path


class BundleMismatchError(Exception):
    """A drawing rebuilt from the catalog is not the one its manifest records."""


def _record(parent: dict, variant: dict) -> dict[str, str]:
    """A variant's drawing input, from the nested document: name to value.

    Multi-valued attributes arrive as several entries under one name and are
    joined with ``", "`` in order -- exactly how the generator joined them when
    it drew the same SKU, which is what makes the digests comparable.
    """
    record: dict[str, str] = {}
    for entry in [*parent["attributes"], *variant["attributes"]]:
        name, value = entry["name"], entry["value"]
        record[name] = f"{record[name]}, {value}" if name in record else value
    return record


def rebuild(catalog_dir: Path) -> list[tuple[str, bytes]]:
    """``(path, svg_bytes)`` for every SKU, checked against ``images.jsonl``."""
    from ..drawing import draw_sku  # noqa: PLC0415

    manifest = {
        row["image_id"]: row
        for row in (
            json.loads(line)
            for line in (catalog_dir / "images.jsonl").read_text("utf-8").splitlines()
            if line
        )
    }
    built: list[tuple[str, bytes]] = []
    mismatched: list[str] = []
    seen: set[str] = set()
    for line in (catalog_dir / "nested.jsonl").read_text("utf-8").splitlines():
        if not line:
            continue
        parent = json.loads(line)
        for variant in parent["variants"]:
            image_id = variant["image_id"]
            row = manifest.get(image_id)
            if row is None:
                mismatched.append(f"{image_id}: in the catalog, not in images.jsonl")
                continue
            data, _ = draw_sku(parent["product_type"], parent["brand"], _record(parent, variant))
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                mismatched.append(f"{image_id}: drawn bytes differ from the recorded sha256")
            seen.add(image_id)
            built.append((row["path"], data))
    missing = sorted(set(manifest) - seen)
    if missing:
        mismatched.append(f"{len(missing)} manifest rows name no SKU: {missing[:5]}")
    if mismatched:
        raise BundleMismatchError(
            f"{len(mismatched)} problem(s); regenerate the catalog before building the "
            f"bundle: {mismatched[:5]}"
        )
    return sorted(built)


def write_archive(files: list[tuple[str, bytes]], archive: Path) -> str:
    """Write a deterministic ``.tar.gz`` of ``files``; return its sha256."""
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w", format=tarfile.USTAR_FORMAT) as tar:
        for path, data in sorted(files):
            info = tarfile.TarInfo(name=path)
            info.size = len(data)
            info.mtime = 0
            info.mode = 0o644
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            tar.addfile(info, io.BytesIO(data))
    packed = io.BytesIO()
    with gzip.GzipFile(fileobj=packed, mode="wb", mtime=0, compresslevel=9) as gz:
        gz.write(raw.getvalue())
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.write_bytes(packed.getvalue())
    return hashlib.sha256(packed.getvalue()).hexdigest()


def write_files(files: list[tuple[str, bytes]], out_dir: Path) -> None:
    for path, data in files:
        target = out_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
