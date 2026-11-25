"""``python -m synthetic_ecommerce_data.picture_products MANIFEST OUT_DIR`` (gen#1022, step 2)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from synthetic_ecommerce_data.picture_products import load_file, write


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, help="a picture manifest: a JSON list or JSON Lines")
    parser.add_argument("out", type=Path, help="the directory the products and pictures go in")
    args = parser.parse_args(argv)
    pictures = load_file(args.manifest)
    products = write(pictures)
    images = args.out / "images"
    images.mkdir(parents=True, exist_ok=True)
    with (args.out / "products.jsonl").open("w", encoding="utf-8") as fh:
        for p in products:
            fh.write(json.dumps(p.doc, sort_keys=True) + "\n")
            (images / p.image_name).write_text(p.svg, encoding="utf-8")
    print(f"{len(products)} products and pictures written to {args.out}, of {len(pictures)} rows")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
