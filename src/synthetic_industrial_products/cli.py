"""Render product drawings from the command line.

sip-render fixtures --out out
sip-render sku 4LU10 33TN24 --profile card --out out
sip-render batch records.jsonl --out out
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections.abc import Iterable, Iterator
from pathlib import Path

from .records import FIXTURES
from .render import PROFILES, Profile, render_record


def png_dimensions(path: Path) -> tuple[int, int]:
    """Width and height straight out of the PNG's IHDR chunk."""
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    width, height = struct.unpack(">II", header[16:24])
    return width, height


def _profiles(name: str) -> list[Profile]:
    if name == "both":
        return [PROFILES["card"], PROFILES["detail"]]
    return [PROFILES[name]]


def _read_jsonl(path: Path) -> Iterator[dict]:
    with path.open(encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"{path}:{number}: expected a JSON object per line")
            yield record


def render_all(records: Iterable[dict], out_dir: Path, profiles: list[Profile]) -> list[Path]:
    written: list[Path] = []
    for record in records:
        sku = str(record.get("sku") or record.get("SKU") or f"record{len(written)}")
        for profile in profiles:
            written.append(render_record(record, out_dir / f"{sku}_{profile.name}.png", profile))
    return written


def _report(paths: list[Path]) -> None:
    for path in paths:
        width, height = png_dimensions(path)
        print(f"{path}  {width}x{height}  {path.stat().st_size:,} bytes")


def main(argv: list[str] | None = None) -> int:
    # The shared options are attached to the top level and to every
    # subcommand, so they work on either side of the subcommand name.
    common = argparse.ArgumentParser(add_help=False)
    # SUPPRESS, not a default value: an option repeated on a subparser would
    # otherwise re-apply its default and silently discard the one given before
    # the subcommand name.
    common.add_argument(
        "--out", type=Path, default=argparse.SUPPRESS, help="output directory (default: out)"
    )
    common.add_argument(
        "--profile",
        choices=[*PROFILES, "both"],
        default=argparse.SUPPRESS,
        help="card (600x880), detail (1400x1400), or both (default: both)",
    )

    parser = argparse.ArgumentParser(prog="sip-render", description=__doc__, parents=[common])
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("fixtures", help="render every bundled reference record", parents=[common])
    one = sub.add_parser("sku", help="render bundled records by sku", parents=[common])
    one.add_argument("skus", nargs="+")
    batch = sub.add_parser(
        "batch", help="render a JSONL file, one record per line", parents=[common]
    )
    batch.add_argument("path", type=Path)

    args = parser.parse_args(argv)
    out_dir = getattr(args, "out", Path("out"))
    profiles = _profiles(getattr(args, "profile", "both"))

    if args.command == "fixtures":
        records: Iterable[dict] = list(FIXTURES.values())
    elif args.command == "sku":
        missing = [sku for sku in args.skus if sku not in FIXTURES]
        if missing:
            parser.error(f"unknown sku(s): {', '.join(missing)}")
        records = [FIXTURES[sku] for sku in args.skus]
    else:
        # Read the whole file before drawing anything: a bad line on page two
        # should not leave half a batch on disk.
        records = list(_read_jsonl(args.path))

    _report(render_all(records, out_dir, profiles))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
