"""The retail image release: every image the export references, rendered and packaged (gen#125).

Usage::

    uv run python prototypes/retail_drawings/image_release.py \\
        --out out/retail-images --archive out/retail-images.tar.gz

The retail counterpart of ``ecom-generate images`` (:mod:`synthetic_ecommerce_data.core.bundle`),
in the same package shape, so the installer that fetches the industrial
release installs this one unchanged:

- ONE IMAGE PER STYLE AND COLORWAY, never per SKU. A SKU's ``image_id``
  (:func:`export.image_id`) is a digest of its product's drawing and its color
  swatch, so every size of one color shares an image; a style sold in no
  color has one image. The 328-style build is 629 images for 6,861 SKUs.
- LAYOUT. Every member is ``retail/<image_id>.svg`` (``retail`` is
  :data:`export.IMAGE_ROOT`), and every ``image_url`` is ``/images/`` plus that
  member, so the demo serving the unpacked folder at ``/images`` resolves it.
- THE PIN is the content digest (:func:`..core.bundle.files_digest`), printed
  and written beside the archive as ``<archive>.content-sha256`` with the file
  count; the archive's own sha256 goes in ``<archive>.sha256``. The archive is
  :func:`..core.bundle.write_archive`'s: sorted members, zeroed times and owners.

Unlike the industrial bundle there is no committed ``images.jsonl`` to check
the render against: the retail build is this folder's code, not a committed
catalog, so the render is the source. What is checked instead is that one
``image_id`` never names two different drawings (:func:`image_files`).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import export  # noqa: E402
from build_preview import drawing_svg  # noqa: E402
from build_preview4 import samples  # noqa: E402

from synthetic_ecommerce_data.core import bundle  # noqa: E402


def member_path(image_id: str) -> str:
    """``retail/<type>/<product>/<digest>.svg``: the file an ``image_url`` names."""
    return f"{export.IMAGE_ROOT}/{image_id}.svg"


def colorway_drawing(rec: dict, sku: dict) -> dict:
    """The product's drawing in the SKU's color: the swatch's base and pattern, the color's accent.

    The product's own drawing is drawn in its first color, so its first
    colorway's image is that drawing unchanged. A color whose accent differs
    is in the drawing's ``accents`` (``variants.product`` puts it there, off
    ``color_options``). A SKU with no color draws the drawing as is.
    """
    drawing = {k: v for k, v in rec["drawing"].items() if k != "accents"}
    swatch = export.drawing_spec(rec, sku)["swatch"]
    if swatch is None:
        return drawing
    accent = rec["drawing"].get("accents", {}).get(swatch["color"], drawing["accent"])
    return drawing | {"base": swatch["hex"], "pattern": swatch["pattern"], "accent": accent}


def render(rec: dict, sku: dict) -> bytes:
    """The SVG bytes of one SKU's image: its colorway's drawing, in its brand's house style."""
    return drawing_svg(rec | {"drawing": colorway_drawing(rec, sku)}).encode()


def records() -> list[dict]:
    """Every build record, in the export's order."""
    return [rec for recs in samples().values() for rec in recs]


def image_files(recs: list[dict] | None = None) -> list[tuple[str, bytes]]:
    """``(member path, svg bytes)`` for every distinct image the export references, sorted.

    Each image is drawn once, from its first SKU. Raises ``ValueError`` when an
    ``image_id`` names two different colorway drawings: the id would then show
    one color's image on another color's SKU.
    """
    drawings: dict[str, dict] = {}
    files: list[tuple[str, bytes]] = []
    for rec in records() if recs is None else recs:
        for sku in rec["skus"]:
            image = export.image_id(rec, sku)
            drawing = colorway_drawing(rec, sku)
            if image in drawings:
                if drawings[image] != drawing:
                    raise ValueError(f"{image} names 2 different drawings ({sku['sku']})")
                continue
            drawings[image] = drawing
            files.append((member_path(image), render(rec, sku)))
    return sorted(files)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="image_release.py", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, default=Path("out/retail-images"))
    parser.add_argument("--archive", type=Path, default=None)
    args = parser.parse_args(argv)
    recs = records()
    files = image_files(recs)
    skus = sum(len(rec["skus"]) for rec in recs)
    bundle.write_files(files, args.out, root=export.IMAGE_ROOT)
    total = sum(len(data) for _, data in files)
    print(f"{args.out}  {len(files)} images for {skus} SKUs, {total:,} bytes")
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
