"""Render motif prints to SVG files and one contact sheet (gen#125).

Usage::

    python3 prototypes/retail_drawings/motif_sheet.py --out-dir DIR

Writes one ``<name>.svg`` per entry of :data:`PEEK` (t-shirts in all three
placements on several grounds, plus a duvet cover, a mug, gift wrap and
multi-fruit packs) and ``contact_sheet.svg``, a grid of them with captions.
Standard library only.
"""

# ruff: noqa: E501 -- SVG literals and data rows read better whole (prototype only).

from __future__ import annotations

import argparse
import re
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import motifs  # noqa: E402,F401 -- registers every kit shape
from kit import SIZE, Fill, render  # noqa: E402
from kit_produce import pile_params  # noqa: E402

WHITE, NAVY, GREY, SAGE, BLACK = "#ffffff", "#26365c", "#b9bec4", "#9bb08f", "#2a2a2e"
ORANGE, LEMON, RED, STEEL = "#f28c28", "#f2d14b", "#d23b3b", "#8e9aa6"


def _print(ground: str, motif: str, color: str, placement: str, scale: float, spacing: float = 0) -> Fill:
    return Fill("print", ground, color, motif=motif, placement=placement, scale=scale, spacing=spacing)


#: name -> (shape, fill, label, params): what the peek folder shows.
PEEK: dict[str, tuple[str, Fill, str | None, dict | None]] = {
    "tee-hammer-placement-grey": ("tshirt", _print(GREY, "hammer", STEEL, "placement", 0.33), None, None),
    "tee-drill-placement-black": ("tshirt", _print(BLACK, "drill", ORANGE, "placement", 0.34), None, None),
    "tee-wrench-allover-navy": ("tshirt", _print(NAVY, "wrench", STEEL, "all-over", 0.11, 70), None, None),
    "tee-screw-scatter-white": ("tshirt", _print(WHITE, "screw", STEEL, "scatter", 0.1, 120), None, None),
    "tee-orange-placement-white": ("tshirt", _print(WHITE, "orange", ORANGE, "placement", 0.32), None, None),
    "tee-orange-allover-navy": ("tshirt", _print(NAVY, "orange", ORANGE, "all-over", 0.1, 64), None, None),
    "tee-orange-scatter-sage": ("tshirt", _print(SAGE, "orange", ORANGE, "scatter", 0.09, 110), None, None),
    "tee-lemon-allover-white": ("tshirt", _print(WHITE, "lemon", LEMON, "all-over", 0.11, 64), None, None),
    "tee-lemon-placement-navy": ("tshirt", _print(NAVY, "lemon", LEMON, "placement", 0.34), None, None),
    "tee-strawberry-scatter-white": ("tshirt", _print(WHITE, "strawberry", RED, "scatter", 0.1, 120), None, None),
    "tee-strawberry-allover-sage": ("tshirt", _print(SAGE, "strawberry", RED, "all-over", 0.1, 60), None, None),
    "duvet-lemon-allover-white": ("duvet", _print(WHITE, "lemon", LEMON, "all-over", 0.09, 56), None, None),
    "mug-hammer-placement-white": ("mug", _print(WHITE, "hammer", STEEL, "placement", 0.3), None, None),
    "giftwrap-orange-scatter-navy": ("wrapping_paper", _print(NAVY, "orange", ORANGE, "scatter", 0.08, 96), None, None),
    "produce-clementines-600g-net": ("produce_pile", Fill("solid", "#ef8a1f"), "Clementines",
                                     pile_params("clementine", "FOD-CLEM", "net", grams=600)),
    "produce-oranges-1kg-loose": ("produce_pile", Fill("solid", "#f08a24"), None,
                                  pile_params("orange", "ORNAVL", "loose", grams=1000)),
    "produce-lemons-pack-of-4-bag": ("produce_pile", Fill("solid", LEMON), "Lemons",
                                     pile_params("lemon", "PLT-LEMONS", "bag", count=4)),
}


def drawings() -> dict[str, str]:
    """name -> its standalone SVG document."""
    return {
        name: render(shape, fill, label=label, uid=name, params=params)
        for name, (shape, fill, label, params) in PEEK.items()
    }


def contact_sheet(svgs: dict[str, str], columns: int = 4, cell: int = 220) -> str:
    """The drawings in a grid, ``cell`` units each, each captioned with its name."""
    rows = -(-len(svgs) // columns)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{columns * cell}" height="{rows * (cell + 24)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    for n, (name, svg) in enumerate(svgs.items()):
        x, y = (n % columns) * cell, (n // columns) * (cell + 24)
        inner = re.sub(r"^<svg [^>]*>|</svg>$", "", svg)
        out.append(
            f'<svg x="{x}" y="{y}" width="{cell}" height="{cell}" viewBox="0 0 {SIZE} {SIZE}">{inner}</svg>'
            f'<text x="{x + cell / 2}" y="{y + cell + 16}" font-family="Helvetica, Arial, sans-serif" '
            f'font-size="11" text-anchor="middle">{escape(name)}</text>'
        )
    out.append("</svg>")
    return "".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out-dir", type=Path, required=True)
    args = ap.parse_args(argv)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    svgs = drawings()
    for name, svg in svgs.items():
        (args.out_dir / f"{name}.svg").write_text(svg, encoding="utf-8")
    (args.out_dir / "contact_sheet.svg").write_text(contact_sheet(svgs), encoding="utf-8")
    print(f"wrote {len(svgs)} drawings and contact_sheet.svg to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
