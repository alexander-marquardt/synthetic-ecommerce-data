"""The redraw sweep of gen#1182: every turned product that stands on a shadow, by kit, and a
before/after sheet of them.

    uv run python scripts/shadow_sweep_1182.py --list
    uv run python scripts/shadow_sweep_1182.py --sheet out/after.svg [--ids PLT-ORBLOD,...]

``--list`` draws every authored and shared template (``scale.templates()``) that the catalogue
turns (``orientation.drawn_angle`` not 0) as it is served (``image_release.render``, its first SKU)
and prints, by kit and then by shape, how many stand on a shadow, and how many of those have a
shadow that is not flat (inside a rotation, or none outside one). After gen#1182 that last count is
0. ``--sheet`` writes one SVG: the Blood Oranges of the maintainer's report and one turned product
of each other kit with a shadow, each drawn as it is served, with its product id and angle under it.
``--ids`` names the products, so the sheet at the commit before the fix shows the same ones.

The script reads only the code beside it, so the "before" sheet is drawn by copying it into a tree
checked out at the commit before slice 1 and running it there.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from collections.abc import Iterable
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from synthetic_ecommerce_data.domains.retail import (  # noqa: E402
    image_release,
    kit,
    orientation,
    scale,
)

#: The product of the maintainer's report, first on the sheet.
ORANGES = "PLT-ORBLOD"
#: A shadow as served: the step's labelled ellipse, or before gen#1182 a kit's dark translucent one.
_ELLIPSE = re.compile(r"<ellipse\b[^>]*>")
_DARK = ("#000000", "#000", "black", kit.INK)
#: One cell of the sheet, in its units, and the cells per row.
CELL, CAPTION, COLUMNS = 240, 28, 5


def kit_of(shape: str) -> str:
    """The kit module that draws ``shape``: ``kit_produce`` -> ``produce``; ``kit`` -> ``kit``."""
    module = getattr(kit.shapes()[shape], "__module__", "kit").rsplit(".", 1)[-1]
    return module.removeprefix("kit_") or module


def _is_shadow(el: str) -> bool:
    if 'class="ground"' in el:
        return True
    fill = re.search(r'\bfill="([^"]+)"', el)
    alpha = re.search(r'\b(?:fill-)?opacity="([\d.]+)"', el)
    dark = fill is not None and fill.group(1).lower() in _DARK
    return bool(dark and alpha and float(alpha.group(1)) < 0.5)


def shadows(svg: str) -> tuple[int, int]:
    """``(shadows, turned)`` in a served SVG: the shadow ellipses, and how many of them lie inside
    a group that rotates."""
    found = turned = 0
    depth: list[bool] = []  # per open <g>: does it rotate
    for tag in re.finditer(r"<(/?)(g|ellipse)\b([^>]*?)(/?)>", svg):
        close, name, attrs, empty = tag.groups()
        if name == "g":
            if close:
                depth.pop()
            elif not empty:
                depth.append("rotate(" in attrs)
        elif _is_shadow(tag.group(0)):
            found += 1
            turned += any(depth)
    return found, turned


def turned_templates() -> Iterable[tuple[dict, int]]:
    """Every template the catalogue draws turned, with its angle, in build order."""
    for rec in scale.templates():
        angle = orientation.drawn_angle(rec)
        if angle and rec.get("skus"):
            yield rec, angle


def sweep() -> dict[tuple[str, str], list[int]]:
    """``(kit, shape) -> [turned products, with a shadow, with a shadow not flat]``."""
    rows: dict[tuple[str, str], list[int]] = {}
    for rec, _ in turned_templates():
        shape = rec["drawing"]["shape"]
        row = rows.setdefault((kit_of(shape), shape), [0, 0, 0])
        found, turned = shadows(image_release.render(rec, rec["skus"][0]).decode())
        row[0] += 1
        row[1] += found > 0
        row[2] += found > 0 and (turned > 0 or found > 1)
    return rows


def table(rows: dict[tuple[str, str], list[int]]) -> str:
    """The sweep as a Markdown table by kit, its shapes named, and a total row."""
    kits: dict[str, Counter] = {}
    shapes: dict[str, list[str]] = {}
    for (name, shape), (n, shadowed, bad) in sorted(rows.items()):
        kits.setdefault(name, Counter()).update(turned=n, shadow=shadowed, bad=bad)
        if shadowed:
            shapes.setdefault(name, []).append(f"{shape} {shadowed}")
    lines = [
        "| kit | turned | with a shadow | not flat | shapes (with a shadow) |",
        "|---|--:|--:|--:|---|",
    ]
    total = Counter()
    for name, c in sorted(kits.items(), key=lambda kv: (-kv[1]["shadow"], kv[0])):
        if not c["shadow"]:
            continue
        total.update(c)
        named = ", ".join(shapes[name])
        lines.append(f"| {name} | {c['turned']} | {c['shadow']} | {c['bad']} | {named} |")
    lines.append(f"| **all** | {total['turned']} | {total['shadow']} | {total['bad']} | |")
    return "\n".join(lines)


def sheet_ids() -> list[str]:
    """The Blood Oranges, then the first turned product with a shadow of each other kit."""
    ids, seen = [ORANGES], {kit_of("produce_pile")}
    for rec, _ in turned_templates():
        name = kit_of(rec["drawing"]["shape"])
        if name not in seen and shadows(image_release.render(rec, rec["skus"][0]).decode())[0]:
            seen.add(name)
            ids.append(rec["product_id"])
    return ids


def _inner(svg: str) -> tuple[str, str]:
    """A served SVG's viewBox and its contents."""
    view = re.search(r'viewBox="([^"]+)"', svg)
    body = svg[svg.index(">", svg.index("<svg")) + 1 : svg.rindex("</svg>")]
    return (view.group(1) if view else "0 0 400 400"), body


def sheet(ids: list[str], title: str) -> str:
    """One SVG of the products ``ids``, each as served, captioned with its id, kit and angle."""
    by_id = {rec["product_id"]: rec for rec in scale.templates()}
    rows = -(-len(ids) // COLUMNS)
    width, height = COLUMNS * CELL, 36 + rows * (CELL + CAPTION)
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="#ffffff"/>',
        f'<text x="8" y="24" font-family="sans-serif" font-size="18">{title}</text>',
    ]
    for i, pid in enumerate(ids):
        rec = by_id[pid]
        x, y = (i % COLUMNS) * CELL, 36 + (i // COLUMNS) * (CELL + CAPTION)
        view, body = _inner(image_release.render(rec, rec["skus"][0]).decode())
        label = f"{pid} {kit_of(rec['drawing']['shape'])} {orientation.drawn_angle(rec)}°"
        out += [
            f'<svg x="{x + 4}" y="{y}" width="{CELL - 8}" height="{CELL - 8}" '
            f'viewBox="{view}">{body}</svg>',
            f'<text x="{x + CELL / 2}" y="{y + CELL + 10}" font-family="sans-serif" font-size="13" '
            f'text-anchor="middle">{label}</text>',
        ]
    return "\n".join([*out, "</svg>"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--list", action="store_true", help="print the sweep's table by kit")
    parser.add_argument("--sheet", type=Path, help="write the sheet SVG here")
    parser.add_argument("--ids", help="comma-separated product ids for the sheet")
    parser.add_argument("--title", default="gen#1182: turned products on their shadow")
    args = parser.parse_args(argv)
    if args.list:
        print(table(sweep()))
    if args.sheet:
        ids = args.ids.split(",") if args.ids else sheet_ids()
        args.sheet.parent.mkdir(parents=True, exist_ok=True)
        args.sheet.write_text(sheet(ids, args.title))
        print(",".join(ids))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
