"""A before-and-after strip of one line's sizes, for the docs (gen#543).

Usage::

    uv run python prototypes/retail_drawings/pack_scale_strip.py --out docs/images/pack-scale.svg

The top row is the line as it was drawn (one drawing for every size), the bottom row as it is
drawn now (each size by the cube root of its content, on the same sheet). The line is the
Cedar Woods Aftershave: 30, 50 and 100 ml.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import image_release  # noqa: E402
import scale  # noqa: E402
from build_preview import drawing_svg  # noqa: E402

LINE = "Cedar Woods Aftershave"
SHEET = 400
GAP = 20
CAPTION = 28


def _cell(svg: str, x: int, y: int) -> str:
    """One 400 x 400 drawing placed at ``(x, y)``: its own ``<svg>`` carries the position."""
    return svg.replace("<svg ", f'<svg x="{x}" y="{y}" ', 1)


def _caption(text: str, x: int, y: int, anchor: str = "start") -> str:
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="Helvetica, Arial, sans-serif" '
        f'font-size="20" fill="#2b3440">{text}</text>'
    )


def strip() -> str:
    """The strip's SVG: three sizes of the line, drawn before (top) and after (bottom)."""
    rec = next(r for r in scale.templates() if r["title"] == LINE)
    skus = sorted(rec["skus"], key=lambda s: float(s["net_volume_ml"]))
    width = len(skus) * (SHEET + GAP) + GAP
    height = 2 * (SHEET + CAPTION) + 3 * GAP
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">',
        f'<rect width="{width}" height="{height}" fill="#ffffff"/>',
    ]
    for row, label in enumerate(
        ("Before: one drawing for every size", "After: by the cube root of the volume")
    ):
        top = GAP + row * (SHEET + CAPTION + GAP)
        parts.append(_caption(label, GAP, top + 20))
        for col, sku in enumerate(skus):
            x = GAP + col * (SHEET + GAP)
            svg = drawing_svg(rec) if row == 0 else image_release.render(rec, sku).decode()
            parts.append(_cell(svg, x, top + CAPTION))
            parts.append(
                _caption(
                    f"{float(sku['net_volume_ml']):g} ml",
                    x + SHEET - 10,
                    top + CAPTION + 392,
                    "end",
                )
            )
    parts.append("</svg>")
    return "".join(parts) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="pack_scale_strip.py", description=__doc__.split("\n")[0])
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(strip(), encoding="utf-8")
    print(f"{args.out}  {args.out.stat().st_size:,} bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
