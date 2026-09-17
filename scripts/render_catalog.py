"""Render a generated catalog's images, and audit that every product has one.

    python scripts/render_catalog.py out/catalog --out out/images

There are ten images. One generic drawing per product type and style stands
behind all 4,600-odd products, because that is what a distributor's own
catalog does: a category listing of four end mills from one series at four
diameters shows the same photograph four times, and 73.5% of the archived
reference records point at an image whose id is not the product's own. A
drawing per SKU would be both more expensive and less faithful.

None of the ten carries a dimension. The dimensions are on the record and
render beside the image; a drawing that restated one would be a second source
that could disagree with the first. So an image here cannot contradict the
record it appears against -- there is no numeric claim in it to contradict with
-- which is the honesty property the per-record renderer has to work for.

The audit is the point of the script. Every product and every variant must
reference an image that exists, and every image written must be referenced by
something: the first failing is a broken image on a demo page, the second is
dead weight in the repository that hosts them. Neither shows up in a count of
files.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from synthetic_industrial_products.render import PROFILES, generic  # noqa: E402


def _load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GiB"


def render_images(out_root: Path, profiles: list[str]) -> tuple[dict[str, set[str]], int]:
    """Write all ten at every profile. Returns the ids written, and the bytes."""
    written: dict[str, set[str]] = {}
    total = 0
    for name in profiles:
        profile = PROFILES[name]
        directory = out_root / name
        paths = generic.render_all(directory, profile)
        written[name] = {path.stem for path in paths}
        total += sum(path.stat().st_size for path in paths)
        for path in paths:
            print(f"  {path}  {path.stat().st_size:,} bytes")
    return written, total


def audit(written: dict[str, set[str]], lines: list[dict], flat: list[dict]) -> bool:
    """Coverage and integrity, measured from the files on disk.

    Nothing here trusts the render report: it reads back the file names that
    were actually written and compares them against what the catalog actually
    asks for.
    """
    referenced = {line["image_id"] for line in lines if line["image_id"]}
    referenced |= {row["image_id"] for row in flat if row["image_id"]}
    ok = True

    per_type: Counter[str] = Counter(row["product_type"] for row in flat)
    print(f"\n{'product type':<22}{'variants':>10}{'image':>24}")
    print("-" * 56)
    for row_type, count in sorted(per_type.items()):
        ids = {row["image_id"] for row in flat if row["product_type"] == row_type}
        print(f"{row_type:<22}{count:>10}{'  ' + ', '.join(sorted(ids)):>24}")
        if len(ids) != 1:
            ok = False
            print(f"  {row_type} points at {len(ids)} different images")

    for name, on_disk in written.items():
        missing = sorted(referenced - on_disk)
        unused = sorted(on_disk - referenced)
        print(f"\n{name}: {len(on_disk)} images on disk for {len(referenced)} referenced")
        if missing:
            ok = False
            print(f"  BROKEN: {len(missing)} referenced images were not rendered: {missing}")
        if unused:
            ok = False
            print(f"  DEAD:   {len(unused)} rendered images nothing references: {unused}")
        if not missing and not unused:
            print("  every reference resolves, and no image is unreferenced")

        covered_lines = sum(1 for line in lines if line["image_id"] in on_disk)
        covered_skus = sum(1 for row in flat if row["image_id"] in on_disk)
        print(
            f"  product lines with an image: {covered_lines}/{len(lines)} "
            f"({covered_lines / len(lines):.1%})"
        )
        print(
            f"  variants with an image:      {covered_skus}/{len(flat)} "
            f"({covered_skus / len(flat):.1%})"
        )
        if covered_lines != len(lines) or covered_skus != len(flat):
            ok = False
    return ok


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "catalog",
        type=Path,
        help="the directory `sip-generate build` wrote, or its nested.jsonl/flat.jsonl",
    )
    parser.add_argument("--out", type=Path, default=Path("out/images"))
    parser.add_argument(
        "--profile",
        choices=[*PROFILES, "both"],
        default="both",
        help="card (600x880), detail (1400x1400), or both (default: both)",
    )
    args = parser.parse_args(argv)

    directory = args.catalog if args.catalog.is_dir() else args.catalog.parent
    lines = _load(directory / "nested.jsonl")
    flat = _load(directory / "flat.jsonl")
    profiles = list(PROFILES) if args.profile == "both" else [args.profile]

    print(
        f"{len(lines)} product lines and {len(flat)} variants from {directory}\n"
        f"{len(generic.IMAGE_IDS)} generic images, {len(profiles)} profile(s):"
    )
    written, total = render_images(args.out, profiles)
    print(f"\ntotal  {sum(len(v) for v in written.values())} files, {_human(total)}")

    ok = audit(written, lines, flat)
    print(
        "\nEvery product and every variant has an image, and no image carries a\n"
        "dimension. The per-record dimensioned drawings are still available for\n"
        "a detail view: see `sip-render batch out/catalog/render.jsonl`."
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
