"""The image release: every SKU's own image file, retail and industrial, in one archive (gen#706).

Usage::

    uv run python -m synthetic_ecommerce_data.domains.retail.image_release \\
        --out out/images --archive out/images.tar.gz [--skus 20000] \\
        [--industrial-catalog out/catalog-100k]
    uv run python -m synthetic_ecommerce_data.domains.retail.image_release \\
        --lookup <image_url | product id | sku> --drawings out/drawings.jsonl.gz

Without ``--skus`` it releases the 352 authored styles; with it, the scaled
build that reaches that SKU count (:func:`scale.build`, the 20K catalog's input),
whose derived styles each name their own images. ``--industrial-catalog`` adds
the drawings of an industrial catalog directory (``ecom-generate build``'s
output), rebuilt and checked by :func:`..core.bundle.rebuild`, so the combined
catalog ships ONE image set under ONE pin rather than a retail and an industrial
release side by side.

- ONE FILE PER SKU, never one shared by two. A SKU's ``image_id``
  (:func:`export.image_id`) is ``<type>/<product>/<sku>``, as industrial's is.
  What the file draws is its product's drawing in the SKU's color swatch, pack
  factor (:mod:`pack_scale`, gen#543), pack count (:mod:`pack_copies`, gen#728)
  and size rung (``size_ladder.py``): SKUs of one colorway, factor, count and
  rung draw the same picture (one
  :func:`export.drawing_id`), drawn once and written to each SKU's own file, so
  one SKU's parameters can change later without touching another's.
- LAYOUT. Every member is ``retail/<image_id>.svg`` (``retail`` is
  :data:`export.IMAGE_ROOT`) or ``industrial/<image_id>.svg``, and every
  ``image_url`` is ``/images/`` plus that member, so the demo serving the
  unpacked folder at ``/images`` resolves both halves from one folder.
- THE GUARD. The release is refused, and nothing written, unless every SKU of
  both halves names exactly one member, no member is named twice, and every
  member is named (:func:`..core.bundle.sku_file_problems`).
- THE PIN is the content digest (:func:`..core.bundle.files_digest`), printed
  and written beside the archive as ``<archive>.content-sha256`` with the file
  count; the archive's own sha256 goes in ``<archive>.sha256``. The archive is
  :func:`..core.bundle.write_archive`'s: sorted members, zeroed times and owners.

Unlike the industrial bundle there is no committed ``images.jsonl`` to check
the retail render against: the retail build is this folder's code, not a
committed catalog, so the render is the source. What is checked instead is that
one ``drawing_id`` never names two different drawings (:func:`image_files`).

THE DRAWINGS FILE (gen#924). Beside the archive, and in ``--out``, ``drawings.jsonl.gz`` holds
one row per image file, sorted by ``image_url``: the SKU, its product and title, and the
``drawing`` that rendered it (retail: the colorway drawing, ``shape``, fill as ``base``,
``pattern`` and ``accent``, ``params``; industrial: :func:`..core.drawing.drawing_spec`). A
title/image mismatch is traced by looking the image up (``--lookup``), with no cluster and no
re-derivation from the templates. It is not an archive member: the archive holds one file per
SKU, and its count names the images release.
"""

from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

from synthetic_ecommerce_data.core import bundle
from synthetic_ecommerce_data.domains.retail import (
    export,
    scale,
)
from synthetic_ecommerce_data.domains.retail.build_preview import drawing_svg
from synthetic_ecommerce_data.domains.retail.build_preview4 import samples

HERE = Path(__file__).resolve().parent


def member_path(image_id: str) -> str:
    """``retail/<type>/<product>/<sku>.svg``: the file an ``image_url`` names."""
    return f"{export.IMAGE_ROOT}/{image_id}.svg"


#: The drawing keys only a ``print`` fill carries (``kit.Fill``). Not ``detail``: a named part
#: (an apparel decoy's blue hem) is drawn on a solid garment too (gen#311).
MOTIF_KEYS = ("motif", "placement", "scale", "spacing", "count")


def colorway_drawing(rec: dict, sku: dict) -> dict:
    """The product's drawing in the SKU's color: the swatch's base and pattern, the color's accent.

    The product's own drawing is drawn in its first color, so its first
    colorway's image is that drawing unchanged. A color whose accent differs
    is in the drawing's ``accents`` (``variants.product`` puts it there, off
    ``color_options``). A SKU with no color draws the drawing as is. A SKU's
    own value of a drawing param (a lamp's ``finish``) replaces the product's.
    """
    drawing = {k: v for k, v in rec["drawing"].items() if k != "accents"}
    spec = export.drawing_spec(rec, sku)
    if "params" in spec:  # the SKU's own finish, shade color or diameter (gen#197)
        drawing["params"] = drawing.get("params", {}) | spec["params"]
    if "size_scale" in spec:  # the SKU's rung on its size ladder (gen#339)
        drawing["size_scale"] = spec["size_scale"]
    if "pack_scale" in spec:  # a smaller size of the line draws a smaller pack (gen#543)
        drawing["pack_scale"] = spec["pack_scale"]
    if "pack_count" in spec:  # a pack of N draws N items (gen#728)
        drawing["pack_count"] = spec["pack_count"]
    if "printed_count" in spec:  # a piece set not drawn item by item prints its count (gen#728)
        drawing["printed_count"] = spec["printed_count"]
    swatch = spec["swatch"]
    if swatch is None:
        return drawing
    accent = rec["drawing"].get("accents", {}).get(swatch["color"], drawing["accent"])
    if swatch["pattern"] != "print":  # a solid fill carries no motif (kit.Fill refuses one)
        drawing = {k: v for k, v in drawing.items() if k not in MOTIF_KEYS}
    return drawing | {"base": swatch["hex"], "pattern": swatch["pattern"], "accent": accent}


def render(rec: dict, sku: dict, styled: bool = True) -> bytes:
    """The SVG bytes of one SKU's image: its colorway's drawing, in its brand's house style
    (``styled=False``: on the plain sheet the shape is drawn on, as ``build_preview`` has it)."""
    return drawing_svg(rec | {"drawing": colorway_drawing(rec, sku)}, styled).encode()


def records(skus: int | None = None) -> list[dict]:
    """Every build record, in the export's order: the 352 authored styles, or with ``skus``
    the scaled build that reaches that SKU count (:func:`scale.build`, e.g. the 20K catalog)."""
    if skus is not None:
        return scale.build(skus).records
    return [rec for recs in samples().values() for rec in recs]


#: The file beside the image release naming what each image was drawn from (gen#924).
DRAWINGS_FILE = "drawings.jsonl.gz"


def drawing_rows(recs: list[dict]) -> list[dict]:
    """One row per retail SKU image: its ``image_url``, ``image_id``, ``product_id``, ``sku``,
    ``title``, ``drawing_id`` and the colorway ``drawing`` :func:`render` draws it from."""
    return [
        {
            "image_url": f"{export.IMAGE_BASE_URL}/{export.image_id(rec, sku)}.svg",
            "image_id": export.image_id(rec, sku),
            "product_id": rec["product_id"],
            "sku": sku["sku"],
            "title": rec["title"],
            "drawing_id": export.drawing_id(rec, sku),
            "drawing": colorway_drawing(rec, sku),
        }
        for rec in recs
        for sku in rec["skus"]
    ]


def write_drawings(rows: list[dict], path: Path) -> None:
    """Write ``rows`` to ``path`` as gzipped JSON lines, sorted by ``image_url``, with no
    timestamp in the gzip header: the same rows write the same bytes."""
    lines = [
        json.dumps(row, sort_keys=True, ensure_ascii=False)
        for row in sorted(rows, key=lambda row: row["image_url"])
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as raw, gzip.GzipFile(filename="", fileobj=raw, mode="wb", mtime=0) as gz:
        gz.write("".join(f"{line}\n" for line in lines).encode("utf-8"))


def read_drawings(path: Path) -> list[dict]:
    """The rows of a drawings file (:func:`write_drawings`)."""
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def drawing_for(path: Path, key: str) -> list[dict]:
    """The rows of the drawings file at ``path`` whose ``image_url``, ``product_id`` or ``sku``
    is ``key``. An absolute URL (``https://<demo>/images/...``) is matched on its path."""
    wanted = {key, urlsplit(key).path}
    return [
        row
        for row in read_drawings(path)
        if wanted & {row["image_url"], row["product_id"], row["sku"]}
    ]


def image_files(recs: list[dict] | None = None) -> list[tuple[str, bytes]]:
    """``(member path, svg bytes)`` for every SKU's own image file, sorted.

    Each drawing is rendered once, from its first SKU, and written to the file
    of every SKU that draws it. Raises ``ValueError`` when a ``drawing_id`` names
    two different colorway drawings: the id would then show one color's image
    on another color's SKU.
    """
    drawings: dict[str, tuple[dict, bytes]] = {}
    files: list[tuple[str, bytes]] = []
    for rec in records() if recs is None else recs:
        for sku in rec["skus"]:
            key = export.drawing_id(rec, sku)
            drawing = colorway_drawing(rec, sku)
            if key not in drawings:
                drawings[key] = (drawing, render(rec, sku))
            elif drawings[key][0] != drawing:
                raise ValueError(f"{key} names 2 different drawings ({sku['sku']})")
            files.append((member_path(export.image_id(rec, sku)), drawings[key][1]))
    return sorted(files)


def sku_urls(recs: list[dict]) -> list[tuple[str, str]]:
    """``(sku, image_url)`` of every SKU, as the export's documents carry them."""
    return [
        (variant["sku"], variant["image_url"])
        for doc in (export.standard_document(rec) for rec in recs)
        for variant in doc["variants"]
    ]


def industrial(catalog: Path) -> tuple[list[tuple[str, bytes]], list[tuple[str, str]]]:
    """An industrial catalog directory's drawings (checked against its ``images.jsonl``) and
    the ``(sku, image_url)`` of every one of its flat documents."""
    rows = (json.loads(line) for line in (catalog / "flat.jsonl").read_text("utf-8").splitlines()
            if line)  # fmt: skip
    return bundle.rebuild(catalog), [(row["sku"], row["image_url"]) for row in rows]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="image_release.py", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, default=Path("out/images"))
    parser.add_argument("--archive", type=Path, default=None)
    parser.add_argument("--skus", type=scale._target, default=None)
    parser.add_argument(
        "--industrial-catalog",
        type=Path,
        default=None,
        help="an `ecom-generate build` directory whose drawings ship in the same archive",
    )
    parser.add_argument(
        "--lookup",
        default=None,
        help="print the drawing rows of this image_url, product id or sku, and build nothing",
    )
    parser.add_argument(
        "--drawings",
        type=Path,
        default=None,
        help=f"the {DRAWINGS_FILE} --lookup reads (default: the one in --out)",
    )
    args = parser.parse_args(argv)
    if args.lookup is not None:
        found = drawing_for(args.drawings or args.out / DRAWINGS_FILE, args.lookup)
        for row in found:
            print(json.dumps(row, sort_keys=True, ensure_ascii=False))
        if not found:
            print(f"no image row names {args.lookup!r}", file=sys.stderr)
        return 0 if found else 1
    recs = records(args.skus)
    files = image_files(recs)
    skus = sku_urls(recs)
    drawings = drawing_rows(recs)
    try:
        if args.industrial_catalog is not None:
            drawn, named = industrial(args.industrial_catalog)
            files, skus = sorted(files + drawn), skus + named
            drawings += bundle.drawing_rows(args.industrial_catalog)
    except bundle.BundleMismatchError as exc:
        print(f"image release REFUSED: {exc}", file=sys.stderr)
        return 1
    problems = bundle.sku_file_problems(skus, [path for path, _ in files])
    if problems:
        print(f"image release REFUSED: {'; '.join(problems)}", file=sys.stderr)
        return 1
    bundle.write_files(files, args.out, root=export.IMAGE_ROOT)
    total = sum(len(data) for _, data in files)
    print(f"{args.out}  {len(files)} files for {len(skus)} SKUs, {total:,} bytes")
    write_drawings(drawings, args.out / DRAWINGS_FILE)
    print(f"{args.out / DRAWINGS_FILE}  {len(drawings)} drawing rows, one per image")
    content = bundle.files_digest(files)
    print(f"content digest (pin this) {content}  over {len(files)} files")
    if args.archive is not None:
        digest = bundle.write_archive(files, args.archive)
        args.archive.with_name(args.archive.name + ".sha256").write_text(
            f"{digest}  {args.archive.name}\n", encoding="utf-8"
        )
        args.archive.with_name(args.archive.name + ".content-sha256").write_text(
            f"{content}  {len(files)}\n", encoding="utf-8"
        )
        write_drawings(drawings, args.archive.with_name(DRAWINGS_FILE))
        print(f"{args.archive}  {args.archive.stat().st_size:,} bytes  archive sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
