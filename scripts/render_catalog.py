"""Render drawings for a generated catalog, and report what could not be drawn.

    python scripts/render_catalog.py out/catalog/render.jsonl --out out/images

This drives the existing renderer; it does not contain one. Every drawing comes
from ``synthetic_industrial_products.render.render_record``, which is the same
code path ``sip-render`` uses.

**Refusals are the point, not a failure.** The renderer will not draw a record
whose dimensions contradict each other or whose dimensions are missing, because
a drawing produced from a defaulted value is a picture that disagrees with its
own record. The generated catalog reproduces measured defect and sparsity
rates, so a predictable share of it is undrawable -- roughly 8% of tools
publish a length of cut longer than the tool, and ``Overall Length`` is absent
from about 8% of records because it is absent from about that many real ones.
A run that drew 100% of this catalog would mean the renderer had started
inventing numbers.

So this reports refusals by class rather than swallowing them, and a non-zero
refusal count is the expected result.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import matplotlib  # noqa: E402

matplotlib.use("Agg")

from synthetic_industrial_products.render import PROFILES, render_record  # noqa: E402


def _render_one(job: tuple[dict, str, str]) -> tuple[str, str, int]:
    """Returns (sku, outcome, bytes). ``outcome`` is "ok" or the error class."""
    record, out_dir, profile_name = job
    sku = str(record.get("sku", "?"))
    profile = PROFILES[profile_name]
    path = Path(out_dir) / f"{sku}_{profile.name}.png"
    try:
        render_record(record, path, profile)
    except Exception as exc:  # noqa: BLE001 -- classify, never swallow
        return sku, type(exc).__name__, 0
    return sku, "ok", path.stat().st_size


def render_all(
    records: list[dict], out_dir: Path, profile: str, workers: int
) -> tuple[Counter, int]:
    out_dir.mkdir(parents=True, exist_ok=True)
    jobs = [(record, str(out_dir), profile) for record in records]
    outcomes: Counter[str] = Counter()
    total_bytes = 0
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for _sku, outcome, size in pool.map(_render_one, jobs, chunksize=16):
            outcomes[outcome] += 1
            total_bytes += size
    return outcomes, total_bytes


def _human(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} GiB"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, help="render.jsonl from sip-generate build")
    parser.add_argument("--out", type=Path, default=Path("out/images"))
    parser.add_argument("--limit", type=int, default=0, help="render only the first N records")
    parser.add_argument(
        "--detail-sample",
        type=int,
        default=200,
        help="how many records also get a detail drawing",
    )
    parser.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 4)))
    args = parser.parse_args(argv)

    records = [json.loads(line) for line in args.path.read_text("utf-8").splitlines() if line]
    if args.limit:
        records = records[: args.limit]
    print(f"{len(records)} records from {args.path}, {args.workers} workers")

    card_out = args.out / "card"
    outcomes, card_bytes = render_all(records, card_out, "card", args.workers)
    drawn = outcomes["ok"]
    print(f"\ncard   {drawn} drawn, {len(records) - drawn} refused, {_human(card_bytes)}")
    for name, count in outcomes.most_common():
        if name != "ok":
            print(f"       refused {count:>5}  {name}")

    detail_records = records[: args.detail_sample]
    detail_out = args.out / "detail"
    detail_outcomes, detail_bytes = render_all(detail_records, detail_out, "detail", args.workers)
    detail_drawn = detail_outcomes["ok"]
    print(
        f"\ndetail {detail_drawn} drawn of a {len(detail_records)}-record sample, "
        f"{len(detail_records) - detail_drawn} refused, {_human(detail_bytes)}"
    )
    for name, count in detail_outcomes.most_common():
        if name != "ok":
            print(f"       refused {count:>5}  {name}")

    print(
        f"\ntotal  {drawn + detail_drawn} images, {_human(card_bytes + detail_bytes)} "
        f"under {args.out}"
    )
    print(
        "\nRefusals are the renderer working: it will not draw a record whose\n"
        "dimensions are missing or self-contradictory, and this catalog contains\n"
        "both at their measured rates."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
