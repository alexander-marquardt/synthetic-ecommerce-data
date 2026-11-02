"""Compose the domains' builds into ONE catalog (gen#125, slice 4 of the 2026-10-28 ruling).

    ecom-generate compose --domain industrial=out/industrial --domain retail=out/retail \\
        --out out/catalog

Red stub: the names only; nothing is read or written yet.
"""

from __future__ import annotations

import argparse
from pathlib import Path

CATALOG = "catalog.ndjson"
PROVENANCE = "provenance.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ecom-generate compose")
    parser.add_argument("--domain", action="append", default=[])
    parser.add_argument("--out", type=Path, required=True)
    parser.parse_args(argv)
    return 0
