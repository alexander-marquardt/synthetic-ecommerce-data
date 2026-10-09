"""Before/after tiles at 180 px: main (no plate), ad7af8b (36-unit plate),
this branch (56-unit plate). Same SKU in each column. Also reports each
figure's ink height in px inside the figure area, from the render."""

import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import sheet as S  # noqa: E402

HERE = S.HERE
TYPES = ["hex_key", "bolt_hex", "drill_jobber", "end_mill_square", "tap_spiral_point",
         "screw_socket_head", "hammer_ball_pein", "roller_chain", "bearing_radial_ball",
         "wheel_depressed_center"]


def main() -> None:
    out = Path(sys.argv[1])
    chosen = {}
    skus = sys.argv[2:]
    for row in map(json.loads, (S.ROOT / "golden-catalog/flat.jsonl").open()):
        chosen.setdefault(row["product_type"], row)
        if row["sku"] in skus:
            chosen[row["sku"]] = row
    rows = [chosen[t] for t in (skus or TYPES)]
    if skus:
        out = out / "skus"
        out.mkdir(exist_ok=True)
    items = []
    for label in ("main", "ad7", "after"):
        for r in rows:
            items.append((f"{label} {r['product_type'][:14]}", f"{'../' if not skus else '../../'}img-{label}/industrial/{r['image_id']}.svg"))
    S.COLS = len(rows)
    html = out / "compare.html"
    w, h = S.grid(items, out, html)
    png = out / "compare.png"
    S.shoot(html, png, w, h)
    img = np.asarray(Image.open(png).convert("L"), dtype=float)
    for c, r in enumerate(rows):
        heights = []
        for k in range(3):
            i = k * len(rows) + c
            x, y = (i % S.COLS) * S.CELL_W + 10, (i // S.COLS) * S.CELL_H + 10
            # figure area only: inside the frame, above the plate (236 units)
            fig = img[y + 8:y + int(236 * S.PX), x + 8:x + S.TILE_W - 8]
            paper = np.median(fig)
            ink = np.where((paper - fig).max(axis=1) > 60)[0]
            heights.append(int(ink[-1] - ink[0] + 1) if len(ink) else 0)
        print(f"{r['product_type']:24s} figure ink rows main/ad7/after: {heights}")
    print(png)


if __name__ == "__main__":
    main()
