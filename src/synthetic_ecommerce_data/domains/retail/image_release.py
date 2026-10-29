"""The image release: every SKU's own image file, retail and industrial, in one archive (gen#706).

Usage::

    uv run python -m synthetic_ecommerce_data.domains.retail.image_release \\
        --out out/images --archive out/images.tar.gz [--skus 20000] \\
        [--industrial-catalog out/catalog-100k]

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
  factor (:mod:`pack_scale`, gen#543) and size rung (``size_ladder.py``): SKUs
  of one colorway, factor and rung draw the same picture (one
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
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

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
    args = parser.parse_args(argv)
    recs = records(args.skus)
    files = image_files(recs)
    skus = sku_urls(recs)
    try:
        if args.industrial_catalog is not None:
            drawn, named = industrial(args.industrial_catalog)
            files, skus = sorted(files + drawn), skus + named
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
        print(f"{args.archive}  {args.archive.stat().st_size:,} bytes  archive sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
