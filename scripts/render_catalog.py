"""Render a generated catalog's drawings, and audit that every product has one.

    python scripts/render_catalog.py out/catalog --out out/images

One drawing per product LINE, shared by that line's 4 to 20 SKUs, at both
profiles. That is what a distributor's own catalog does -- a category listing
of four end mills from one series at four diameters shows the same photograph
four times, and 73.5% of the archived reference records point at an image whose
id is not the product's own -- and it is also what the nested shape's whole
variant-grouping story depends on: N SKUs are ONE product, so they share one
picture.

Each line's drawing is marked with that line's own published attributes: the
outline in its brand's colour, the fill in its coating's, the section hatched
for its material, the flutes at the published count, and a stamp setting every
published value verbatim. So the drawings differ exactly where the records do.

None of them carries a dimension. A line's SKUs span a median 5.5x range of
sizes, so a to-scale drawing would be wrong for most of the line it stands
behind; the sizes are on the record and render beside the image, where they are
the record's own values.

The audit is the point of the script, and it is measured from the files on
disk rather than from the render report:

* every product line and every variant resolves to a file that exists and is
  NOT EMPTY -- a zero-byte PNG is a present key and a broken image;
* no file is unreferenced, which would be dead weight in the repository that
  hosts them;
* the number of DISTINCT drawings, by bytes. Two lines may legitimately draw
  the same picture when they publish the same attributes, and the count of
  those is reported per product type so a change that quietly collapsed the
  encoding shows up as variety disappearing rather than as nothing at all.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from synthetic_industrial_products.render import PROFILES, batch  # noqa: E402


def _load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text("utf-8").splitlines() if line]


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GiB"


def audit(written, lines: list[dict], flat: list[dict], out_root: Path) -> bool:
    """Coverage, integrity and variety, all measured from the files on disk."""
    ok = True
    referenced = {line["image_id"] for line in lines if line["image_id"]}
    referenced |= {row["image_id"] for row in flat if row["image_id"]}
    by_type = {line["image_id"]: line["product_type"] for line in lines}

    for name, results in written.items():
        on_disk = {image_id for image_id, drawn in results.items() if drawn.size > 0}
        empty = sorted(image_id for image_id, drawn in results.items() if drawn.size == 0)
        missing = sorted(referenced - on_disk)
        unused = sorted(on_disk - referenced)
        total = sum(drawn.size for drawn in results.values())
        sizes = sorted(drawn.size for drawn in results.values())

        print(f"\n{name}: {len(on_disk)} drawings for {len(referenced)} referenced")
        print(f"  {_human(total)} total, {_human(sizes[0])}..{_human(sizes[-1])} per file")
        if empty:
            ok = False
            print(f"  EMPTY:  {len(empty)} files were written with no bytes in them: {empty[:5]}")
        if missing:
            ok = False
            print(f"  BROKEN: {len(missing)} referenced images were not rendered: {missing[:5]}")
        if unused:
            ok = False
            print(f"  DEAD:   {len(unused)} rendered images nothing references: {unused[:5]}")
        if not (empty or missing or unused):
            print("  every reference resolves to a non-empty file, and none is unreferenced")

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

        # Variety, by bytes. Two lines publishing identical attributes draw one
        # picture, which is correct; the number of them is what a collapsed
        # encoding would move, so it is printed per type rather than summed.
        groups: dict[tuple[str, str], list[str]] = defaultdict(list)
        for image_id, drawn in results.items():
            groups[(by_type[image_id], drawn.digest)].append(image_id)
        per_type: Counter[str] = Counter(by_type[i] for i in results)
        distinct: Counter[str] = Counter(type_key for type_key, _ in groups)
        print(f"\n  {'product type':<22}{'lines':>8}{'distinct':>10}{'collide':>9}")
        print("  " + "-" * 47)
        collisions = 0
        for type_key, count in sorted(per_type.items()):
            collide = count - distinct[type_key]
            collisions += collide
            print(f"  {type_key:<22}{count:>8}{distinct[type_key]:>10}{collide:>9}")
        print(
            f"  {'TOTAL':<22}{sum(per_type.values()):>8}{sum(distinct.values()):>10}{collisions:>9}"
        )
        for (type_key, _), members in sorted(groups.items()):
            if len(members) > 1:
                print(f"  same drawing ({type_key}): {', '.join(sorted(members))}")
    del out_root
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
    parser.add_argument(
        "--workers",
        type=int,
        default=batch.DEFAULT_WORKERS,
        help="render processes (default: one per core, capped at 8)",
    )
    args = parser.parse_args(argv)

    directory = args.catalog if args.catalog.is_dir() else args.catalog.parent
    lines = _load(directory / "nested.jsonl")
    flat = _load(directory / "flat.jsonl")
    profiles = list(PROFILES) if args.profile == "both" else [args.profile]

    print(
        f"{len(lines)} product lines and {len(flat)} variants from {directory}\n"
        f"one drawing per line, {len(profiles)} profile(s), {args.workers} worker(s):"
    )
    written = batch.render_lines(lines, args.out, profiles, args.workers)
    files = sum(len(v) for v in written.values())
    total = sum(drawn.size for results in written.values() for drawn in results.values())
    print(f"\ntotal  {files} files, {_human(total)}, under {args.out}")

    ok = audit(written, lines, flat, args.out)
    print(
        "\nEvery product and every variant has a drawing of its own product line,\n"
        "and no drawing carries a dimension. The per-record dimensioned drawings\n"
        "are still available for a detail view: see `sip-render batch`."
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
