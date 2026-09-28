"""Contact sheets of the per-SKU drawings, for judging them by eye before a full render.

    uv run python scripts/contact_sheet.py --catalog golden-catalog --out out/contact-sheets

Writes one HTML page with every drawing inline (``index.html``), so it opens in
any browser with nothing else installed. Every drawing on it is a real SKU of
the committed catalog, drawn by the same code the bundle uses -- the sheets
select, they never invent a record.

The sections are the ones the maintainer asked for on
elastic/prism-industrial-products#103:

* one screw across its lengths, for two brands (the same thread size and
  material, so what differs is length, and then house style);
* flat washers across sizes, materials and brands;
* every product type, twenty SKUs each, so the variation within a type and
  the difference between types can both be seen.

The page itself carries labels (type, brand, SKU) under each drawing so the
sheet can be read; the drawings carry none.
"""

from __future__ import annotations

import argparse
import base64
import html
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from synthetic_industrial_products.catalog.bundle import _record  # noqa: E402
from synthetic_industrial_products.drawing import draw_sku  # noqa: E402


def _load(catalog: Path) -> list[dict]:
    return [json.loads(line) for line in (catalog / "nested.jsonl").read_text("utf-8").splitlines()]


def _cell(parent: dict, variant: dict, caption: str) -> str:
    data, source = draw_sku(parent["product_type"], parent["brand"], _record(parent, variant))
    # An <img> per drawing, not inline SVG: each file is its own document, as
    # it is when served, so nothing on the page can reach into another.
    src = "data:image/svg+xml;base64," + base64.b64encode(data).decode("ascii")
    note = "" if source == "record" else f" · {source}"
    return (
        '<figure style="margin:4px;display:inline-block;width:150px;vertical-align:top">'
        f'<img src="{src}" width="150" height="225" alt="">'
        f'<figcaption style="font:11px system-ui;color:#555">{html.escape(caption)}{note}'
        "</figcaption></figure>"
    )


def _value(parent: dict, variant: dict, name: str) -> str:
    for entry in [*variant["attributes"], *parent["attributes"]]:
        if entry["name"] == name:
            return entry["value"]
    return ""


def _screw_lengths(products: list[dict]) -> list[str]:
    """One thread size and material, across its lengths, for the two best-stocked brands."""
    groups: dict[tuple, list[tuple[float, dict, dict]]] = defaultdict(list)
    for parent in products:
        if parent["product_type"] != "screw_socket_head":
            continue
        for variant in parent["variants"]:
            key = (
                _value(parent, variant, "Dia./Thread Size"),
                _value(parent, variant, "Material"),
                parent["brand"],
            )
            length = next(
                (e.get("value_num") for e in variant["attributes"] if e["name"] == "Length"), None
            )
            if length:
                groups[key].append((length, parent, variant))
    by_thread: dict[tuple, list[tuple]] = defaultdict(list)
    for (thread, material, brand), items in groups.items():
        distinct = {length for length, _, _ in items}
        by_thread[(thread, material)].append((len(distinct), brand, items))
    best = max(by_thread.items(), key=lambda kv: sorted(n for n, _, _ in kv[1])[-2:])
    (thread, material), brands = best
    cells = [f"<h3>{html.escape(thread)} {html.escape(material)} socket cap screws</h3>"]
    for _, brand, items in sorted(brands, reverse=True)[:2]:
        seen: dict[float, tuple] = {}
        for length, parent, variant in sorted(items, key=lambda t: t[0]):
            seen.setdefault(length, (parent, variant))
        cells.append(f"<div><b>{html.escape(brand)}</b><br>")
        for parent, variant in list(seen.values())[:8]:
            cells.append(_cell(parent, variant, _value(parent, variant, "Length")))
        cells.append("</div>")
    return cells


def _washers(products: list[dict]) -> list[str]:
    cells = ["<h3>Flat washers: sizes x materials x brands</h3>"]
    by: dict[tuple, tuple] = {}
    for parent in products:
        if parent["product_type"] != "washer_flat":
            continue
        for variant in parent["variants"]:
            key = (parent["brand"], _value(parent, variant, "Material"))
            by.setdefault(key + (_value(parent, variant, "Size"),), (parent, variant))
    brands = sorted({k[0] for k in by})[:4]
    for brand in brands:
        cells.append(f"<div><b>{html.escape(brand)}</b><br>")
        for key in sorted(k for k in by if k[0] == brand)[:10]:
            parent, variant = by[key]
            cells.append(_cell(parent, variant, f"{key[2]} {key[1]}"))
        cells.append("</div>")
    return cells


def _per_type(products: list[dict], per: int = 20) -> list[str]:
    cells: list[str] = []
    by_type: dict[str, list[tuple[dict, dict]]] = defaultdict(list)
    for parent in products:
        for variant in parent["variants"]:
            by_type[parent["product_type"]].append((parent, variant))
    for type_key in sorted(by_type):
        items = by_type[type_key]
        step = max(1, len(items) // per)
        cells.append(f"<h3>{html.escape(type_key)} ({len(items):,} SKUs)</h3><div>")
        for parent, variant in items[::step][:per]:
            cells.append(_cell(parent, variant, f"{parent['brand']} · {variant['sku']}"))
        cells.append("</div>")
    return cells


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", type=Path, default=Path("golden-catalog"))
    parser.add_argument("--out", type=Path, default=Path("out/contact-sheets"))
    args = parser.parse_args()
    products = _load(args.catalog)
    body = [
        "<!doctype html><meta charset=utf-8><title>Per-SKU drawings</title>",
        '<body style="font:13px system-ui;margin:16px">',
        "<h2>Per-SKU drawings: no text in any drawing; captions are the page's</h2>",
        *_screw_lengths(products),
        *_washers(products),
        *_per_type(products),
        "</body>",
    ]
    args.out.mkdir(parents=True, exist_ok=True)
    target = args.out / "index.html"
    target.write_text("\n".join(body), encoding="utf-8")
    print(target)
    return 0


if __name__ == "__main__":
    sys.exit(main())
