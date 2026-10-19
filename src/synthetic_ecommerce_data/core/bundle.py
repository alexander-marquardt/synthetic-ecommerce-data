"""The image bundle: every SKU's drawing, rebuilt from a committed catalog, in one archive.

    ecom-generate images --catalog golden-catalog --out out/images --archive out/images.tar.gz

The drawings are NEVER committed (elastic/prism-industrial-products#103): the
repository commits the catalog, whose ``images.jsonl`` carries each SKU image's
path and sha256, and the bundle is rebuilt from that. This module is the
rebuild. It reads the committed ``nested.jsonl`` and, for each SKU's published
spelling, ``flat.jsonl`` beside it (a nested entry carries no spelling, #42),
draws every variant, and refuses unless every drawing's digest equals the one
``images.jsonl`` records -- so an archive built here IS the set the catalog
names, byte for byte, and a generator change that moved a drawing without a
regeneration cannot ship under the old catalog.

LAYOUT. Every member is ``industrial/<type>/<product_id>/<sku>.svg``: the
top-level ``industrial/`` folder is :data:`..emit.IMAGE_ROOT`, so a
customization unpacks the archive into its images folder and the demo serves
that folder at ``/images`` (elastic/prism#9770) -- ``image_url`` is
``/images/industrial/...`` exactly.

THE PIN IS OF THE CONTENT, not of the compressed bytes. The archive is
deterministic on one toolchain (members sorted, times and owners zeroed, a
gzip header without a time), but gzip output depends on the zlib build, and
some Python builds ship a different one. So :func:`content_digest` -- the
sha256 of the sorted ``<path>\t<sha256 of the file>`` lines -- is what a
customization pins and what its installer re-computes after unpacking. It is
derivable from the committed ``images.jsonl`` alone, without building anything.
"""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import tarfile
from pathlib import Path

from synthetic_ecommerce_data.core.entry import published
from synthetic_ecommerce_data.core.letter_case import AUTHORED_NAMES_FILE


class BundleMismatchError(Exception):
    """A drawing rebuilt from the catalog is not the one its manifest records."""


def _record(
    parent: dict, variant: dict, facets: dict, authored: dict[str, str] | None = None
) -> dict[str, str]:
    """A variant's drawing input: name to PUBLISHED value.

    The names and their order come from the nested document; each value's
    spelling (``3/8 in.``, ``1,070 lbf``) comes from the SKU's flat ``facets``,
    because a nested entry carries only its magnitude and ``unit_code``.
    Multi-valued attributes arrive as several entries under one name and are
    joined with ``", "`` in order -- exactly how the generator joined them when
    it drew the same SKU, which is what makes the digests comparable.
    """
    record: dict[str, str] = {}
    for name, value in published([*parent["attributes"], *variant["attributes"]], facets):
        name = (authored or {}).get(name, name)
        record[name] = f"{record[name]}, {value}" if name in record else value
    return record


class SkuFacets(dict[str, dict]):
    """``{sku: facets}`` plus the catalogue's authored-name map (gen#499).

    ``authored`` is ``{product_type: {published name: authored name}}``, read from the file the
    build writes beside ``flat.jsonl``: the drawing code looks attributes up by the name a type
    authored, and the published names are sentence case."""

    authored: dict[str, dict[str, str]]


def flat_facets(catalog_dir: Path) -> SkuFacets:
    """``{sku: facets}`` from the catalog's ``flat.jsonl``: where the published spelling lives."""
    facets = SkuFacets(
        (doc["sku"], doc["facets"])
        for doc in (
            json.loads(line)
            for line in (catalog_dir / "flat.jsonl").read_text("utf-8").splitlines()
            if line
        )
    )
    names = catalog_dir / AUTHORED_NAMES_FILE
    facets.authored = json.loads(names.read_text("utf-8")) if names.exists() else {}
    return facets


def records(parent: dict, facets_by_sku: dict[str, dict]) -> list[dict[str, str]]:
    """Every variant's drawing input, joined to its flat document on ``sku``."""
    authored = getattr(facets_by_sku, "authored", {}).get(parent["product_type"])
    out = []
    for variant in parent["variants"]:
        facets = facets_by_sku.get(variant["sku"])
        if facets is None:
            raise BundleMismatchError(f"{variant['sku']}: in nested.jsonl, not in flat.jsonl")
        out.append(_record(parent, variant, facets, authored))
    return out


def member_path(path: str) -> str:
    """A drawing's path inside the archive: under the bundle's top-level folder."""
    from synthetic_ecommerce_data.core.emit import IMAGE_ROOT  # noqa: PLC0415

    return f"{IMAGE_ROOT}/{path}"


def content_digest(entries) -> str:
    """sha256 of the sorted ``<member path>\t<file sha256>`` lines: the pinnable digest."""
    lines = sorted(f"{path}\t{digest}\n" for path, digest in entries)
    return hashlib.sha256("".join(lines).encode("utf-8")).hexdigest()


def manifest_digest(catalog_dir: Path) -> str:
    """The content digest, from the committed ``images.jsonl`` alone."""
    rows = [
        json.loads(line)
        for line in (catalog_dir / "images.jsonl").read_text("utf-8").splitlines()
        if line
    ]
    return content_digest((member_path(row["path"]), row["sha256"]) for row in rows)


def files_digest(files: list[tuple[str, bytes]]) -> str:
    return content_digest((path, hashlib.sha256(data).hexdigest()) for path, data in files)


def rebuild(catalog_dir: Path) -> list[tuple[str, bytes]]:
    """``(path, svg_bytes)`` for every SKU, checked against ``images.jsonl``.

    Needs no registration step: the first read of the figure table registers
    the breadth rows and the type modules (:class:`.typespec.RegistryTable`).
    """
    from synthetic_ecommerce_data.core.drawing import draw_product  # noqa: PLC0415

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
    facets_by_sku = flat_facets(catalog_dir)
    for line in (catalog_dir / "nested.jsonl").read_text("utf-8").splitlines():
        if not line:
            continue
        parent = json.loads(line)
        drawn = draw_product(
            parent["product_type"], parent["brand"], records(parent, facets_by_sku)
        )
        for variant, (data, _) in zip(parent["variants"], drawn, strict=True):
            image_id = variant["image_id"]
            row = manifest.get(image_id)
            if row is None:
                mismatched.append(f"{image_id}: in the catalog, not in images.jsonl")
                continue
            if hashlib.sha256(data).hexdigest() != row["sha256"]:
                mismatched.append(f"{image_id}: drawn bytes differ from the recorded sha256")
            seen.add(image_id)
            built.append((member_path(row["path"]), data))
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


def write_files(files: list[tuple[str, bytes]], out_dir: Path, root: str | None = None) -> None:
    """Write the drawings under ``out_dir``, replacing any previous set there.

    The bundle's own folder (``root``: the industrial :data:`..emit.IMAGE_ROOT`
    unless a domain names its own, as the retail release does) is cleared
    first, so a drawing a regeneration dropped does not linger beside the new set.
    """
    import shutil  # noqa: PLC0415

    from synthetic_ecommerce_data.core.emit import IMAGE_ROOT  # noqa: PLC0415

    shutil.rmtree(out_dir / (root or IMAGE_ROOT), ignore_errors=True)
    for path, data in files:
        target = out_dir / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
