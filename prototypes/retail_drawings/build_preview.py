"""Write the retail sneak peek: ``preview.html`` and ``samples.ndjson``.

Usage::

    python3 prototypes/retail_drawings/build_preview.py [--html PATH] [--ndjson PATH] [--svg-dir DIR]

Both files are always written beside this script; ``--html`` and ``--ndjson``
write extra copies, ``--svg-dir`` writes each drawing as its own .svg file
and ``--contact`` writes a drawings-only grid (both for rendering checks).
Standard library only.
"""

# ruff: noqa: E501 -- inline HTML and CSS literals (prototype only).

from __future__ import annotations

import argparse
import json
import sys
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import kit_garments  # noqa: E402,F401 -- registers the trousers and top shapes
import kit_home  # noqa: E402,F401 -- registers the home and beauty shapes
import motifs  # noqa: E402,F401 -- registers the motif, surface and produce_pile shapes
from house_styles import HOUSE_STYLES  # noqa: E402
from kit import Fill, render  # noqa: E402
from samples import records  # noqa: E402

SHOWN = (
    "audience",
    "color",
    "pattern",
    "fit",
    "leg_fit",
    "rise",
    "length",
    "waist",
    "neckline",
    "sleeve_length",
    "fabric",
    "hem_length",
    "pack_size",
    "storage",
    "dietary",
    "allergens",
    "flavour",
    "serves",
)
UNIT = {
    "LTR": "L", "MLT": "ml", "GRM": "g", "KGM": "kg", "C62": "", "CMT": " cm", "GM2": " gsm",
    "KEL": " K", "WTT": " W",
}  # fmt: skip
GARMENT = {"audience", "leg_fit", "rise", "length", "waist", "neckline", "sleeve_length"}


def drawing_svg(rec: dict, styled: bool = True) -> str:
    """The product's drawing as an SVG: in its brand's house style, or with ``styled=False`` on
    the plain 400 x 400 sheet the shape is drawn on, before the house style scales it into its
    frame (the sheet ``tests/test_retail_sheet_242.py`` measures)."""
    d = rec["drawing"]
    # A motif print's fields (gen#125) ride on the drawing beside its colors.
    fill = Fill(d["pattern"], d["base"], d["accent"], d["third"], motif=d.get("motif"),
                placement=d.get("placement"), scale=d.get("scale", 0.0),
                spacing=d.get("spacing", 0.0), count=d.get("count", 1),
                detail=(d["detail"]["part"], d["detail"]["color"]) if d.get("detail") else None)  # fmt: skip
    return render(
        d["shape"],
        fill,
        label=d["label"],
        brand=rec["brand"],
        uid=rec["product_id"],
        params=d.get("params"),
        size_scale=d.get("size_scale"),
        style=HOUSE_STYLES[rec["brand"]] if styled else None,
    )


def _attr_rows(rec: dict) -> str:
    grouped: dict[str, tuple[str, list[str]]] = {}
    for a in rec["attributes"]:
        value = a["value"] + (UNIT.get(a.get("unit_code", ""), "") if a["key"] != "serves" else "")
        grouped.setdefault(a["key"], (a["name"], []))[1].append(value)
    rows = []
    for key in [*SHOWN, *(k for k in grouped if k not in SHOWN)]:
        if key in grouped:
            name, values = grouped[key]
            cls = ' class="g"' if key in GARMENT else ""
            rows.append(
                f"<tr{cls}><th>{escape(name)}</th><td>{escape(', '.join(values))}</td></tr>"
            )
    return "".join(rows)


def _sizes(rec: dict) -> str:
    if "size_uk" not in rec:
        return ""
    rows = "".join(
        f"<tr><th>{system}</th><td>{escape(' · '.join(rec[f'size_{system.lower()}']))}</td></tr>"
        for system in ("UK", "EU", "US")
    )
    return f'<table class="sizes">{rows}</table>'


def card(rec: dict) -> str:
    chips = "".join(f'<span class="chip dept">{escape(d)}</span>' for d in rec["department"])
    chips += "".join(f'<span class="chip coll">{escape(c)}</span>' for c in rec["collections"])
    return (
        '<div class="card">'
        f'<div class="pic">{drawing_svg(rec)}</div>'
        f'<div class="title">{escape(rec["title"])}</div>'
        f'<div class="meta"><span class="brand">{escape(rec["brand"])}</span>'
        f'<span class="price">£{rec["price"]:.2f}</span></div>'
        f'<div class="chips">{chips}</div>'
        f'<div class="path">{escape(" › ".join(rec["category_path"]))}</div>'
        f'<table class="attrs">{_attr_rows(rec)}</table>'
        f"{_sizes(rec)}"
        "</div>"
    )


CSS = """
body{font-family:Helvetica,Arial,sans-serif;margin:24px;background:#f1f0ec;color:#2b3440}
h1{font-size:20px;margin:0 0 4px} p.note{margin:0 0 18px;color:#5b6570;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{background:#fff;border:1px solid #d9d7d0;border-radius:8px;padding:10px;font-size:12px}
.pic svg{width:100%;height:auto;display:block;border-radius:4px}
.title{font-weight:700;font-size:14px;margin:8px 0 2px}
.meta{display:flex;justify-content:space-between;margin-bottom:6px}
.brand{color:#5b6570}.price{font-weight:700}
.chip{display:inline-block;border-radius:10px;padding:1px 8px;margin:0 4px 4px 0;font-size:11px}
.dept{background:#dbe7f5;color:#1f4f8a}.coll{background:#f8e0c8;color:#8a4a12}
.path{color:#7a838c;font-size:11px;margin-bottom:6px}
table{border-collapse:collapse;width:100%;margin-top:4px}
th{text-align:left;color:#7a838c;font-weight:400;padding:1px 6px 1px 0;white-space:nowrap;vertical-align:top}
td{padding:1px 0} tr.g td{color:#1f4f8a;font-weight:700}
h2{font-size:16px;margin:26px 0 10px}
.sizes{border-top:1px solid #eee;margin-top:6px}.sizes th{font-weight:700;color:#2b3440;width:24px}
"""


SECTIONS = (
    (
        "Jeans and trousers: every leg fit and rise",
        lambda r: "trousers" in r["drawing"]["shape"] or "jeans" in r["drawing"]["shape"],
    ),
    (
        "Tops: necklines, sleeve lengths and knits",
        lambda r: r["drawing"]["shape"] in ("top", "tshirt", "blouse"),
    ),
    (
        "More clothing, footwear and lingerie",
        lambda r: r["department"][0] in ("clothing", "footwear", "lingerie"),
    ),
    ("Home", lambda r: r["department"][0] == "home"),
    ("Beauty and gifts", lambda r: r["department"][0] in ("beauty", "gifts")),
    ("Food", lambda r: True),
)


def _sections(recs: list[dict]) -> str:
    left, out = list(recs), []
    for title, wanted in SECTIONS:
        mine = [r for r in left if wanted(r)]
        left = [r for r in left if not wanted(r)]
        if mine:
            out.append(
                f'<h2>{escape(title)}</h2><div class="grid">{"".join(card(r) for r in mine)}</div>'
            )
    return "".join(out)


def page(recs: list[dict]) -> str:
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>Retail drawings: sneak peek</title>"
        f"<style>{CSS}</style></head><body>"
        "<h1>Retail drawings: sneak peek</h1>"
        f'<p class="note">{len(recs)} sample records in the #125 output shape. Drawings come from the '
        "parametric SVG kit (shape + fill + label + params) dressed in the brand's house style. "
        "Round 3 gives every brand a declared house style: paper, frame, outline hand and a "
        "composite logo mark, half of them as a full lockup with the name. The product's own "
        "color and pattern never depend on the brand. Structured garment attributes are in blue. "
        "All brands, shades and fragrance names are invented.</p>"
        f"{_sections(recs)}"
        "</body></html>"
    )


def outputs() -> tuple[str, str]:
    """(the preview page, the sample NDJSON) exactly as :func:`main` writes them."""
    recs = records()
    return page(recs), "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--html", type=Path, action="append", default=[])
    ap.add_argument("--ndjson", type=Path, action="append", default=[])
    ap.add_argument("--svg-dir", type=Path)
    ap.add_argument("--contact", type=Path, help="also write a drawings-only contact sheet")
    ap.add_argument("--contact-px", type=int, default=200)
    args = ap.parse_args(argv)

    recs = records()
    html, ndjson = outputs()
    for path in [HERE / "preview.html", *args.html]:
        path.write_text(html, encoding="utf-8")
    for path in [HERE / "samples.ndjson", *args.ndjson]:
        path.write_text(ndjson, encoding="utf-8")
    if args.contact:
        cells = "".join(
            f'<div style="width:{args.contact_px}px">{drawing_svg(r)}</div>' for r in recs
        )
        args.contact.write_text(
            "<!doctype html><html><head><meta charset='utf-8'><style>body{margin:0;display:flex;flex-wrap:wrap}"
            f"svg{{width:{args.contact_px}px;height:{args.contact_px}px;display:block}}</style></head>"
            f"<body>{cells}</body></html>",
            encoding="utf-8",
        )
    if args.svg_dir:
        args.svg_dir.mkdir(parents=True, exist_ok=True)
        for r in recs:
            (args.svg_dir / f"{r['product_id']}-{r['drawing']['shape']}.svg").write_text(
                drawing_svg(r), encoding="utf-8"
            )
    print(f"wrote {len(recs)} records")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
