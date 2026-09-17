"""Render product drawings from the command line.

sip-render generics --out out                     the ten product-type drawings
sip-render fixtures --out out
sip-render sku 4LU10 42SR26 --profile card --out out
sip-render batch records.jsonl --out out

``generics`` writes the ten drawings a generated catalog actually uses -- one
per product type and style, shared by every product of that type, and carrying
no dimension at all.

The other three run the per-record DIMENSIONED renderer, which is a different
thing and is for a detail view of a handful of products: it draws each record
to scale from that record's own attribute values. A record that does not
publish the dimensions its drawing needs, or publishes ones that contradict
each other, falls back to its generic drawing. The run reports the mix rather
than one total, because "4,600 images" and "4,600 dimensioned drawings" are
different claims and only one of them is true.
"""

from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter
from collections.abc import Iterable, Iterator
from dataclasses import dataclass, field
from pathlib import Path

from .records import BUNDLED
from .render import (
    PROFILES,
    AmbiguousProductError,
    Profile,
    UnknownProductError,
    draw_record,
    generic,
)
from .render.attrs import REFUSALS

#: Every way a record can end up with no image through nobody's fault: it
#: identifies nothing, it identifies two things, or it withholds something a
#: drawing would have to invent.
DECLINED: tuple[type[Exception], ...] = (
    UnknownProductError,
    AmbiguousProductError,
    *REFUSALS,
)


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


@dataclass
class BatchReport:
    """What a run drew, how, and what it could not draw at all."""

    paths: list[Path] = field(default_factory=list)
    #: Kind -> count, for records drawn to scale from their own attributes.
    to_scale: Counter = field(default_factory=Counter)
    #: Kind -> count, for records given the undimensioned type drawing.
    as_type: Counter = field(default_factory=Counter)
    #: Refusal class -> count. Why the ``as_type`` ones went that way.
    refusals: Counter = field(default_factory=Counter)
    #: Refusal class -> count, for records the renderer declined to draw at
    #: all: nothing identifies what they are, so not even a generic drawing is
    #: true of them. A refusal is the renderer working.
    refused: Counter = field(default_factory=Counter)
    #: Error class -> count, for records that broke something. A bug, not a
    #: property of the data, and the only thing that makes the run fail.
    failed: Counter = field(default_factory=Counter)

    @property
    def drawn(self) -> int:
        return sum(self.to_scale.values()) + sum(self.as_type.values())

    def lines(self) -> list[str]:
        out = [
            f"{self.drawn} drawn  "
            f"({sum(self.to_scale.values())} to scale, "
            f"{sum(self.as_type.values())} as their product type)",
        ]
        for kind in sorted(set(self.to_scale) | set(self.as_type)):
            out.append(
                f"  {kind:<12} {self.to_scale[kind]:>6} to scale  "
                f"{self.as_type[kind]:>6} as type"
            )
        if self.refusals:
            out.append("why the type drawing was used:")
            for name, count in self.refusals.most_common():
                out.append(f"  {name:<28} {count:>6}")
        if self.refused:
            out.append(f"{sum(self.refused.values())} refused, no image drawn:")
            for name, count in self.refused.most_common():
                out.append(f"  {name:<28} {count:>6}")
        if self.failed:
            out.append(f"{sum(self.failed.values())} FAILED:")
            for name, count in self.failed.most_common():
                out.append(f"  {name:<28} {count:>6}")
        return out


def render_all(
    records: Iterable[dict],
    out_dir: Path,
    profiles: list[Profile],
    *,
    keep_going: bool = False,
) -> BatchReport:
    """Draw every record, and report the mix.

    ``keep_going`` is what issue #2 was about: a driver over a whole catalog
    must not stop at the first record it cannot place. It classifies the
    failure, counts it, and carries on, so one bad line costs one image rather
    than the rest of the run.

    Refusals and failures are counted apart. A record the renderer declines to
    draw is the renderer working -- the catalog contains records that identify
    nothing, and the right answer for those is no image rather than a guessed
    one -- so it does not fail the run. Anything else does.
    """
    report = BatchReport()
    for index, record in enumerate(records):
        sku = str(record.get("sku") or record.get("SKU") or f"record{index}")
        for profile in profiles:
            try:
                drawn = draw_record(record, out_dir / f"{sku}_{profile.name}.png", profile)
            except Exception as exc:  # noqa: BLE001 -- classify, never swallow
                if not keep_going:
                    raise
                bucket = report.refused if isinstance(exc, DECLINED) else report.failed
                bucket[type(exc).__name__] += 1
                continue
            report.paths.append(drawn.path)
            if drawn.dimensioned:
                report.to_scale[drawn.kind] += 1
            else:
                report.as_type[drawn.kind] += 1
                report.refusals[drawn.refusal or "unknown"] += 1
    return report


def _print(report: BatchReport) -> None:
    for path in report.paths:
        width, height = png_dimensions(path)
        print(f"{path}  {width}x{height}  {path.stat().st_size:,} bytes")
    print()
    for line in report.lines():
        print(line)


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
    sub.add_parser(
        "generics", help="render the ten product-type drawings", parents=[common]
    )
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

    if args.command == "generics":
        written = [
            generic.render(image_id, out_dir / f"{image_id}_{profile.name}.png", profile)
            for profile in profiles
            for image_id in generic.IMAGE_IDS
        ]
        for path in written:
            width, height = png_dimensions(path)
            print(f"{path}  {width}x{height}  {path.stat().st_size:,} bytes")
        print(f"\n{len(written)} product-type drawings, carrying no dimension between them")
        return 0

    if args.command == "fixtures":
        records: Iterable[dict] = list(BUNDLED.values())
    elif args.command == "sku":
        missing = [sku for sku in args.skus if sku not in BUNDLED]
        if missing:
            parser.error(f"unknown sku(s): {', '.join(missing)}")
        records = [BUNDLED[sku] for sku in args.skus]
    else:
        # Read the whole file before drawing anything: a bad line on page two
        # should not leave half a batch on disk.
        records = list(_read_jsonl(args.path))

    report = render_all(records, out_dir, profiles, keep_going=True)
    _print(report)
    # Only an unexpected error fails the run. A refusal is named in the report
    # and is a property of the record, not a fault in the tool.
    return 1 if report.failed else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
