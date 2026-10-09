"""Write round 4's sneak peek: variant docs, planted distractors and the SKU report.

Usage::

    python3 prototypes/retail_drawings/build_preview4.py [--html PATH] [--ndjson PATH]

Writes ``preview4.html`` and ``samples4.ndjson`` beside this script (and the
extra copies named), and prints the SKU report per family. A sample is one
product document per style (gen#125), its color x size SKUs nested: deep
styles (jeans, bras), shallow ones (bedding, beauty), the planted distractors
and the observed failure classes. A card shows the style's color swatches and
size options, both derived from its SKUs. Standard library only.
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

import footwear_rows  # noqa: E402
import kit_footwear  # noqa: E402,F401 -- registers shoe, boot_sock
import kit_more  # noqa: E402,F401 -- registers the own-kind shapes (bouquet, socks, bed_frame, ...)
import kit_round4  # noqa: E402,F401 -- registers belt, hanger, outfit_set, trigger_spray
import prints  # noqa: E402
from build_preview import CSS, _attr_rows, drawing_svg  # noqa: E402
from distractors import (  # noqa: E402
    DINOSAUR_TOY,
    GIFT_BAGS,
    LEMONS,
    ORANGES,
    TABLE,
    corpus,
    duplicate_record,
    scores,
    table_markdown,
)
from real_classes import ROWS, class_docs  # noqa: E402
from variants import FAMILIES, SIZE_KEYS, sku_report, style_docs  # noqa: E402

#: One product per style: the whole round 4 corpus, the print range (gen#125),
#: footwear and every class record.
SAMPLES = 328


def samples() -> dict[str, list[dict]]:
    """section -> its sample products: every style's one document, then the distractors."""
    out: dict[str, list[dict]] = {}
    for fam, styles in FAMILIES.items():
        out[fam] = [d for s in styles for d in style_docs(fam, s)]
    out["Planted distractors"] = [
        LEMONS, ORANGES, DINOSAUR_TOY,
        *(x.doc for row in TABLE if not row.tail for x in row.distractors),
    ]  # fmt: skip
    planted = {d["product_id"] for d in out["Planted distractors"]}
    out["Print range"] = [d for d in prints.docs() if d["product_id"] not in planted]
    out["Gift wrap"] = list(GIFT_BAGS)
    gift = next(row for row in TABLE if row.tail)
    out["Gift bag distractors"] = [x.doc for x in (*gift.distractors, *gift.tail)]
    out["Observed failure classes"] = class_docs()
    out["Footwear"] = footwear_rows.docs()
    out["Footwear distractors"] = [x.doc for x in footwear_rows.BOOTS.distractors]
    return out


def _planted() -> dict[str, tuple[str, str]]:
    return {
        **{
            x.doc["product_id"]: (row.query, x.fixed_by)
            for row in (*TABLE, footwear_rows.BOOTS)
            for x in (*row.distractors, *row.tail)
        },
        **{
            f"PLT-{style.code}": (row.query, fix)
            for row in ROWS
            for style, fix in row.distractors
        },
    }


#: The fields a policy reads that the round 4 records do not carry.
FACTS = ("product_type", "audience", "size_range", "neckline", "pattern", "leg_style", "rise")


def _facts(rec: dict) -> str:
    """A line of the policy-facing fields, or nothing for a record without them."""
    if "product_type" not in rec:
        return ""
    show = {k: ", ".join(v) if isinstance(v, list) else v for k, v in rec.items() if k in FACTS}
    parts = [f"{k}: {show[k]}" for k in FACTS if k in rec]
    parts.append(" > ".join(rec["category_path"]))
    parts.append(f"{rec['rating']} from {rec['review_count']}")
    # The print range (gen#125) is not ranked with the class records: no rank, no badges.
    if rec.get("badges"):
        parts.append(" / ".join(rec["badges"]))
    if rec["price_max"] > rec["price_min"]:
        parts.append(f"£{rec['price_min']:.2f} - £{rec['price_max']:.2f}")
    rank = f", bestseller #{rec['bestseller_rank']}" if "bestseller_rank" in rec else ""
    parts.append(f"sold {rec['sold_last_5_days']} in 5 days{rank}")
    if "was_price" in rec:
        parts.append(f"was £{rec['was_price']:.2f}")
    return f'<div class="vg">{escape(" · ".join(parts))}</div>'


def _options(rec: dict) -> str:
    """The style's selectors: one swatch per color, then each size system's values."""
    rows = []
    if "color_options" in rec:
        dots = "".join(
            f'<span class="sw" style="background:{o["hex"]}" title="{escape(o["color"])}"></span>'
            for o in rec["color_options"]
        )
        names = " · ".join(o["color"] for o in rec["color_options"])
        rows.append(f"<tr><th>Color</th><td>{dots} {escape(names)}</td></tr>")
    for key in SIZE_KEYS:
        values = rec.get("size_options", {}).get(key)
        if values:
            label = key.replace("_", " ").capitalize()
            rows.append(f"<tr><th>{escape(label)}</th><td>{escape(' · '.join(values))}</td></tr>")
    return f'<table class="sizes">{"".join(rows)}</table>' if rows else ""


def card(rec: dict, planted: dict[str, tuple[str, str]]) -> str:
    chips = "".join(f'<span class="chip dept">{escape(d)}</span>' for d in rec["department"])
    note = ""
    if rec["product_id"] in planted:
        q, fix = planted[rec["product_id"]]
        note = f'<div class="plant">Distractor for <b>{escape(q)}</b>; fixed by {escape(fix)}</div>'
    return (
        '<div class="card">'
        f'<div class="pic">{drawing_svg(rec)}</div>'
        f'<div class="title">{escape(rec["title"])}</div>'
        f'<div class="meta"><span class="brand">{escape(rec["brand"])}</span>'
        f'<span class="price">£{rec["price"]:.2f}</span></div>'
        f'<div class="chips">{chips}</div>'
        f'<div class="path">{escape(" › ".join(rec["category_path"]))}</div>'
        f'<div class="vg">{escape(rec["product_id"])} · {rec["sku_count"]} SKU'
        f"{'s' if rec['sku_count'] != 1 else ''} in this product</div>"
        f"{_facts(rec)}{note}"
        f'<div class="desc">{escape(rec["description"])}</div>'
        f'<table class="attrs">{_attr_rows(rec)}</table>'
        f"{_options(rec)}"
        "</div>"
    )


EXTRA_CSS = """
.vg{color:#1f4f8a;font-size:11px;margin-bottom:4px}.desc{color:#4b5560;margin:4px 0}
.sw{display:inline-block;width:11px;height:11px;border-radius:50%;border:1px solid #b9b6ad;margin-right:2px;vertical-align:middle}
.plant{background:#fbe3e3;color:#8a1f1f;border-radius:4px;padding:2px 6px;margin:4px 0}
pre{background:#fff;border:1px solid #d9d7d0;padding:10px;font-size:12px}
table.dist td,table.dist th{border-bottom:1px solid #e3e1da;padding:4px 6px;vertical-align:top;white-space:normal}
"""


def _score_table() -> str:
    # The boots row is scored over the corpus with footwear in it: the boots it must lose to.
    rows, base = [], corpus()
    for row, cat in [*((r, base) for r in TABLE), (footwear_rows.BOOTS, footwear_rows.catalog())]:
        best, each = scores(row, cat)
        names = {x.doc["product_id"]: x.doc["title"] for x in row.distractors}
        cells = "<br>".join(f"{escape(names[p])}: {s:.2f}" for p, s in each)
        rows.append(
            f"<tr><td>{escape(row.cls)}</td><td><i>{escape(row.query)}</i> → {escape(row.intended)}"
            f" (best {best:.2f})</td><td>{cells}</td><td>{escape(row.policy)}</td></tr>"
        )
    return (
        '<table class="dist"><tr><th>Class</th><th>Query → intended (BM25)</th>'
        "<th>Distractors (BM25, title + description)</th><th>Fixed by</th></tr>"
        f"{''.join(rows)}</table>"
    )


def page(sections: dict[str, list[dict]]) -> str:
    planted = _planted()
    n = sum(len(v) for v in sections.values())
    body = "".join(
        f'<h2>{escape(title)}</h2><div class="grid">{"".join(card(r, planted) for r in recs)}</div>'
        for title, recs in sections.items()
    )
    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        "<title>Retail round 4: variants and planted distractors</title>"
        f"<style>{CSS}{EXTRA_CSS}</style></head><body>"
        "<h1>Retail round 4: variants and planted distractors</h1>"
        f'<p class="note">{n} products. One document per style: every color × size it is sold '
        "in is a SKU nested in it, and its color swatches and size options are derived from "
        "those SKUs. Jeans and bras are deep (crossed, rule-bound axes); bedding and beauty are "
        "shallow (one hand list per row). Every brand, line and shade name is invented.</p>"
        f"<h2>SKU report per family</h2><pre>{escape(sku_report())}</pre>"
        f"<h2>Planted distractor table</h2>{_score_table()}"
        f"{body}</body></html>"
    )


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--html", type=Path, action="append", default=[])
    ap.add_argument("--ndjson", type=Path, action="append", default=[])
    ap.add_argument(
        "--duplicate-listing",
        action="store_true",
        help="append a second listing of one product under another category (written only to "
        "the --ndjson paths: the committed samples never hold it)",
    )
    args = ap.parse_args(argv)

    html, ndjson = outputs(args.duplicate_listing)
    here = [] if args.duplicate_listing else [HERE]
    for path in [*(h / "preview4.html" for h in here), *args.html]:
        path.write_text(html, encoding="utf-8")
    for path in [*(h / "samples4.ndjson" for h in here), *args.ndjson]:
        path.write_text(ndjson, encoding="utf-8")
    print(sku_report())
    print(table_markdown())
    print(f"wrote {ndjson.count(chr(10))} records")
    return 0


def outputs(duplicate_listing: bool = False) -> tuple[str, str]:
    """(the preview page, the sample NDJSON) exactly as :func:`main` writes them."""
    sections = samples()
    recs = [r for recs in sections.values() for r in recs]
    if len(recs) != SAMPLES:
        raise SystemExit(f"{len(recs)} samples, not {SAMPLES}")
    if duplicate_listing:
        recs.append(duplicate_record())
    ndjson = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in recs)
    return page(sections), ndjson


if __name__ == "__main__":
    raise SystemExit(main())
