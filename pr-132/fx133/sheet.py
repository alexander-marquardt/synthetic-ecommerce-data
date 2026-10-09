"""Contact sheet of every brand at the Studio tile size, and the cap height
measured from the rendered pixels (not computed).

usage: python sheet.py <out-dir>
"""

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

from synthetic_ecommerce_data.core import brands
from synthetic_ecommerce_data.core.drawing import brand_mark, sheet

CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TILE_H, TILE_W = 180, 120
PX = TILE_H / 300.0
COLS = 9
CELL_W, CELL_H = 140, 215  # tile plus caption


def shoot(html: Path, png: Path, w: int, h: int) -> None:
    subprocess.run(
        [CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", f"--window-size={w},{h}",
         f"--screenshot={png}", html.as_uri()],
        check=True, capture_output=True,
    )


def grid(items, img_dir: Path, html: Path) -> tuple[int, int]:
    cells = []
    for i, (caption, path) in enumerate(items):
        x, y = (i % COLS) * CELL_W + 10, (i // COLS) * CELL_H + 10
        cells.append(
            f'<div style="position:absolute;left:{x}px;top:{y}px;width:{TILE_W}px">'
            f'<img src="{(img_dir / path).as_uri()}" style="display:block;width:{TILE_W}px;'
            f'height:{TILE_H}px;object-fit:contain">'
            f'<div style="font:10px sans-serif;margin-top:3px;white-space:nowrap">{caption}</div></div>'
        )
    rows = (len(items) + COLS - 1) // COLS
    w, h = COLS * CELL_W + 20, rows * CELL_H + 20
    html.write_text(
        '<html><body style="margin:0;background:#fff">' + "".join(cells) + "</body></html>"
    )
    return w, h


def cap_height(tile: np.ndarray, line: brand_mark.Line, size: float) -> tuple[int, float]:
    """Rows of the line's first capital that are at least half inked, and the
    summed ink coverage of its rows (a sub-pixel height)."""
    first = line.text[0]
    x0 = line.x * PX
    x1 = (line.x + brand_mark.text_width(first, size)) * PX
    y0 = (line.baseline - 0.95 * size) * PX
    y1 = (line.baseline + 0.12 * size) * PX
    win = tile[int(y0):int(np.ceil(y1)), int(x0) + 1:int(x1)]
    paper = 255.0
    dark = (paper - win.min(axis=1)) / (paper - win.min())
    return int((dark >= 0.5).sum()), float(dark.sum())


def main() -> None:
    out = Path(sys.argv[1])
    out.mkdir(parents=True, exist_ok=True)
    pick: dict[str, dict] = {}
    seen_types: set[str] = set()
    for row in map(json.loads, (ROOT / "golden-catalog/flat.jsonl").open()):
        b = row["brand"]
        # one SKU per brand, spread over types where possible
        if b not in pick or (pick[b]["product_type"] in seen_types and row["product_type"] not in seen_types):
            pick[b] = row
        seen_types.add(pick[b]["product_type"])
    names = sorted(brands.BY_NAME)
    missing = [n for n in names if n not in pick]
    assert not missing, missing
    items = [(f"{n} ({sheet.plate_lockup(n).layout})", pick[n]["image_id"] + ".svg") for n in names]
    html = out / "contact-sheet.html"
    w, h = grid(items, HERE / "img-after/industrial", html)
    png = out / "contact-sheet.png"
    shoot(html, png, w, h)
    img = np.asarray(Image.open(png).convert("L"), dtype=float)
    results = []
    for i, n in enumerate(names):
        x, y = (i % COLS) * CELL_W + 10, (i // COLS) * CELL_H + 10
        tile = img[y:y + TILE_H, x:x + TILE_W]
        lk = sheet.plate_lockup(n)
        for line in lk.placed:
            if line.text[0].isupper() and line.text[0] not in "QJ":
                rows, cov = cap_height(tile, line, lk.size)
                results.append((cov, rows, n, line.text, lk.size, lk.layout))
    results.sort()
    for r in results[:8]:
        print(f"coverage {r[0]:.2f} px  rows>=50% {r[1]}  {r[2]!r} line {r[3]!r} size {r[4]} {r[5]}")
    print("brands", len(names), "lines measured", len(results),
          "min rows>=50%", min(r[1] for r in results), "min coverage", round(results[0][0], 2))
    print(png)


if __name__ == "__main__":
    main()
