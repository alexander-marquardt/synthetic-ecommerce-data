"""A preview of the industrial house styles: 40 golden products, drawn with ``house=True``.

Run: ``uv run python prototypes/industrial_drawings/build_industrial_preview.py --html X --ndjson Y``.

Writes one HTML page (a "same type, two brands" section first, then the rest)
and one NDJSON record per product (title, brand, category, price, a few
attributes and the opt-in drawing as ``image_svg``). Reads only the committed
golden catalog; writes nothing inside it.
"""

# ruff: noqa: E501 -- HTML literals read better whole than wrapped (prototype only).

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from industrial_styles import render  # noqa: E402

from synthetic_industrial_products.catalog import bundle  # noqa: E402

GOLDEN = HERE.parents[1] / "golden-catalog"

#: Types drawn twice, each by a different brand.
PAIRED = (
    "end_mill_square",
    "end_mill_ball",
    "drill_jobber",
    "tap_spiral_point",
    "hammer_ball_pein",
    "hex_key",
    "bearing_radial_ball",
    "abrasive_flap_disc",
    "wheel_depressed_center",
    "bolt_hex",
    "nut_hex",
    "washer_flat",
    "screw_socket_head",
    "shackles",
    "pillow_block_bearings",
    "roller_chain_sprockets",
    "o_rings",
)
#: Types the golden catalog has from one brand only: drawn once.
SINGLES = (
    "cut_resistant_gloves",
    "safety_glasses",
    "bench_vises",
    "combination_wrenches",
    "c_clamps",
    "ball_valves",
)


def pick(parents: list[dict]) -> list[tuple[str, dict]]:
    """(section, parent) for 40 products: favour brands not yet shown."""
    by_type: dict[str, list[dict]] = {}
    for p in parents:
        by_type.setdefault(p["product_type"], []).append(p)
    seen: dict[str, int] = {}
    chosen: list[tuple[str, dict]] = []
    for t, count, section in [(t, 2, "pair") for t in PAIRED] + [(t, 1, "single") for t in SINGLES]:
        taken: list[dict] = []
        for _ in range(count):
            pool = [p for p in by_type[t] if p["brand"] not in {q["brand"] for q in taken}]
            best = min(pool, key=lambda p: (seen.get(p["brand"], 0), p["product_id"]))
            taken.append(best)
            seen[best["brand"]] = seen.get(best["brand"], 0) + 1
        chosen += [(section, p) for p in taken]
    return chosen


def sample_records() -> list[dict]:
    parents = [json.loads(line) for line in (GOLDEN / "nested.jsonl").read_text().splitlines() if line]
    facets = bundle.flat_facets(GOLDEN)
    out = []
    for section, p in pick(parents):
        variant = p["variants"][0]
        svg = render(p["product_type"], p["brand"], bundle.records(p, facets), house=True)[0]
        out.append(
            {
                "product_id": p["product_id"],
                "sku": variant["sku"],
                "title": variant["title"],
                "brand": p["brand"],
                "product_type": p["product_type"],
                "category_path": p["category_path"],
                "price": variant["price_usd"],
                "currency": "USD",
                "attributes": [
                    {"key": a["key"], "name": a["name"], "value": a["value"]} for a in variant["attributes"][:4]
                ],
                "section": section,
                "image_svg": svg.decode("utf-8"),
            }
        )
    return out


def _card(r: dict) -> str:
    attrs = "".join(f"<li><b>{escape(a['name'])}</b> {escape(str(a['value']))}</li>" for a in r["attributes"])
    return (
        f'<div class="card"><div class="img">{r["image_svg"]}</div>'
        f'<div class="t">{escape(r["title"])}</div><div class="b">{escape(r["brand"])} · ${r["price"]:.2f}</div>'
        f"<ul>{attrs}</ul></div>"
    )


def page(recs: list[dict]) -> str:
    pairs = [r for r in recs if r["section"] == "pair"]
    rows = "".join(
        f'<div class="pair"><h3>{escape(pairs[i]["product_type"])}</h3>{_card(pairs[i])}{_card(pairs[i + 1])}</div>'
        for i in range(0, len(pairs), 2)
    )
    singles = "".join(_card(r) for r in recs if r["section"] == "single")
    return (
        "<!doctype html><html><head><meta charset='utf-8'><title>Industrial house styles, preview 1</title><style>"
        "body{font-family:Helvetica,Arial,sans-serif;margin:24px;background:#e9eaec;color:#222}"
        ".grid{display:flex;flex-wrap:wrap;gap:18px}.pair{display:flex;gap:10px;background:#fff;padding:10px;border-radius:6px;flex-wrap:wrap;width:440px}"
        ".pair h3{width:100%;margin:0 0 4px;font-size:12px;color:#666;font-weight:400}"
        ".card{width:210px;font-size:11px}.img svg{width:200px;height:300px;display:block;border:1px solid #ccc;background:#fff}"
        ".t{font-weight:700;margin-top:4px}.b{color:#555}ul{padding-left:14px;margin:4px 0}"
        "</style></head><body><h1>Industrial house styles: preview 1</h1>"
        "<p>Opt-in render (<code>house=True</code>); the emitted catalog's drawings are unchanged. "
        "Same-type pairs from two brands first.</p>"
        f'<h2>Same type, two brands</h2><div class="grid" id="pairs">{rows}</div>'
        f'<h2>More types</h2><div class="grid">{singles}</div></body></html>'
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--html", type=Path, required=True)
    ap.add_argument("--ndjson", type=Path, required=True)
    args = ap.parse_args(argv)
    recs = sample_records()
    args.html.write_text(page(recs), encoding="utf-8")
    args.ndjson.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs), encoding="utf-8")
    print(f"wrote {len(recs)} records, {len({r['brand'] for r in recs})} brands")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
