#!/usr/bin/env python3
"""Build the retail ceiling and its figures once for a CI run (#539).

    uv run python scripts/build_ceiling.py --out build/ceiling

The ``ceiling-catalogue`` job runs this and uploads ``--out``; each ``tests`` shard downloads the
directory and names it in ``RETAIL_FIGURES_CACHE``, where ``retail_figures.ceiling`` and
``retail_figures.figures`` read the two files instead of building. Anything already in ``--out``
goes first: a file left by an earlier tree would be read as this one's.
"""

from __future__ import annotations

import argparse
import os
import shutil
from pathlib import Path


def build(out: Path) -> list[str]:
    """Fill ``out`` with the two files; return their names."""
    from synthetic_ecommerce_data.domains.retail import retail_figures  # noqa: PLC0415

    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    os.environ[retail_figures.CACHE_ENV] = str(out)
    retail_figures.figures()
    names = [retail_figures.CEILING_FILE, retail_figures.FIGURES_FILE]
    missing = [name for name in names if not (out / name).is_file()]
    if missing:
        raise SystemExit(f"build_ceiling: the measurement left no {', '.join(missing)}")
    return names


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    for name in build(args.out):
        print(f"{args.out / name}: {(args.out / name).stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
