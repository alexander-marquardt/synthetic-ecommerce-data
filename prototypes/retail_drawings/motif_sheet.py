"""Render twelve catalog records' drawings and one contact sheet (gen#125).

Usage::

    python3 prototypes/retail_drawings/motif_sheet.py --out-dir DIR

Writes ``<product_id>.svg`` for each record of :data:`PEEK`, drawn from the
record exactly as the preview draws it (:func:`build_preview.drawing_svg`, in
the brand's house style): placement, all-over and scatter prints from the
print range (:mod:`prints`) and multi-fruit produce packs, and
``contact_sheet.svg``, a grid of them captioned with title and product id.
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

from build_preview import drawing_svg  # noqa: E402
from distractors import corpus  # noqa: E402
from kit import SIZE  # noqa: E402
from real_classes import class_docs  # noqa: E402

#: The records the sheet shows: four singular/plural pairs (one placement graphic
#: titled singular beside a scatter or all-over repeat titled plural), two more
#: placement graphics, and produce drawn as many fruits as the pack holds.
PEEK = (
    "PLT-TEEM-WRENCH", "PLT-TEEMP-WRENCH", "PLT-TEEM-HAMMER", "PLT-SWM-HAMMER",
    "PLT-MUG-ORANGE", "PLT-TTW-ORANGE", "PLT-TEEW-LEMON", "PLT-LEMDRS",
    "PLT-TEEM-DRILL", "PLT-TEEK-DINOSAUR", "PLT-LEMONS", "PLT-ORNAVL",
)  # fmt: skip


def records() -> list[dict]:
    """The :data:`PEEK` records, in order, from the catalog the preview builds."""
    by_id = {d["product_id"]: d for d in (*corpus(), *class_docs())}
    return [by_id[pid] for pid in PEEK]


def drawings() -> dict[str, str]:
    """product id -> its standalone SVG document, as the preview draws it."""
    return {rec["product_id"]: drawing_svg(rec) for rec in records()}


def contact_sheet(svgs: dict[str, str], columns: int = 4, cell: int = 220,
                  titles: dict[str, str] | None = None) -> str:  # fmt: skip
    """The drawings in a grid, ``cell`` units each, each captioned with its title (from
    ``titles``, when given) and its product id."""
    titles = titles or {}
    rows = -(-len(svgs) // columns)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{columns * cell}" height="{rows * (cell + 40)}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    for n, (name, svg) in enumerate(svgs.items()):
        x, y = (n % columns) * cell, (n // columns) * (cell + 40)
        inner = re.sub(r"^<svg [^>]*>|</svg>$", "", svg)
        font = 'font-family="Helvetica, Arial, sans-serif" text-anchor="middle"'
        out.append(
            f'<svg x="{x}" y="{y}" width="{cell}" height="{cell}" viewBox="0 0 {SIZE} {SIZE}">{inner}</svg>'
            f'<text x="{x + cell / 2}" y="{y + cell + 14}" {font} font-size="12" font-weight="bold">'
            f'{escape(titles.get(name, ""))}</text>'
            f'<text x="{x + cell / 2}" y="{y + cell + 30}" {font} font-size="10">{escape(name)}</text>'
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
    titles = {rec["product_id"]: rec["title"] for rec in records()}
    sheet = contact_sheet(svgs, titles=titles)
    (args.out_dir / "contact_sheet.svg").write_text(sheet, encoding="utf-8")
    print(f"wrote {len(svgs)} drawings and contact_sheet.svg to {args.out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
