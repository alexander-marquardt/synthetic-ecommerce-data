"""The oracle of every move slice of gen#413: write the default retail build's outputs to a folder.

A slice that moves where a type is declared never changes what is generated. Run this on main and
on the branch, then ``diff -r BEFORE AFTER``: no output means the flat and nested documents of the
authored build, the SVG images (hashed in order), the scaled build at its ceiling (nested, flat
and image ids) and the measured stats are byte-identical. About 90 s, 500 MB per run.

    .venv/bin/python scripts/build_oracle.py OUTDIR
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RETAIL = Path(__file__).resolve().parent.parent / "prototypes" / "retail_drawings"
sys.path.insert(0, str(RETAIL))

import export  # noqa: E402
import image_release  # noqa: E402
import retail_figures  # noqa: E402
import scale  # noqa: E402

from synthetic_ecommerce_data.core.emit import write_jsonl  # noqa: E402


def _lines(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def main(argv: list[str]) -> int:
    out = Path(argv[1])
    out.mkdir(parents=True, exist_ok=True)
    write_jsonl(iter(export.documents()), out / "nested.jsonl")
    write_jsonl(iter(export.flat_documents()), out / "flat.jsonl")
    files = image_release.image_files()
    digest = hashlib.sha256()
    for path, data in files:
        digest.update(path.encode() + b"\0" + data)
    (out / "images.sha256").write_text(f"{digest.hexdigest()} {len(files)}\n", encoding="utf-8")
    scaled = scale.build(retail_figures.EXHAUST)
    docs = scale.documents(scaled)
    _lines(out / "ceiling_nested.jsonl", docs)
    _lines(out / "ceiling_flat.jsonl", scale.flat(docs))
    ids = sorted({export.image_id(rec, sku) for rec in scaled.records for sku in rec["skus"]})
    (out / "ceiling_image_ids.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")
    stats = retail_figures.render(retail_figures.measure())
    (out / "stats.json").write_text(stats, encoding="utf-8")
    for p in sorted(out.iterdir()):
        print(hashlib.sha256(p.read_bytes()).hexdigest()[:16], p.name, p.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
