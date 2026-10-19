"""The retail image release: every image the export references, rendered and packaged (gen#125).

Usage::

    uv run python prototypes/retail_drawings/image_release.py \\
        --out out/retail-images --archive out/retail-images.tar.gz [--skus 20000]

Without ``--skus`` it releases the 328 authored styles; with it, the scaled
build that reaches that SKU count (:func:`scale.build`, the 20K catalog's input),
whose derived styles each name their own images.

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
import scale  # noqa: E402
from build_preview import drawing_svg  # noqa: E402
from build_preview4 import samples  # noqa: E402

from synthetic_ecommerce_data.core import bundle  # noqa: E402


def member_path(image_id: str) -> str:
    """``retail/<type>/<product>/<digest>.svg``: the file an ``image_url`` names."""
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
    """Every build record, in the export's order: the 328 authored styles, or with ``skus``
    the scaled build that reaches that SKU count (:func:`scale.build`, e.g. the 20K catalog)."""
    if skus is not None:
        return scale.build(skus).records
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
    parser.add_argument("--skus", type=scale._target, default=None)
    args = parser.parse_args(argv)
    recs = records(args.skus)
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
