"""Write round 4's sneak peek: variant docs, planted distractors and the SKU report.

Usage::

    python3 prototypes/retail_drawings/build_preview4.py [--html PATH] [--ndjson PATH]

Writes ``preview4.html`` and ``samples4.ndjson`` beside this script (and the
extra copies named), and prints the SKU report per family. The 60 samples
mix deep docs (jeans, bras), shallow docs (bedding, beauty) and the planted
distractor table. Standard library only.
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

import kit_round4  # noqa: E402,F401 -- registers belt, hanger, outfit_set, trigger_spray
from build_preview import CSS, _attr_rows, _sizes, drawing_svg  # noqa: E402
from distractors import (  # noqa: E402
    GIFT_BAGS,
    GIFT_PRINTS,
    LEMONS,
    TABLE,
    corpus,
    duplicate_record,
    scores,
    table_markdown,
)
from real_classes import ROWS, class_docs  # noqa: E402
from variants import FAMILIES, sku_report, style_docs  # noqa: E402

#: family -> {style code: extra doc indexes beyond the first}.
EXTRA = {
    "Jeans": {"HARROW": (13,), "TOLLAND": (21,), "CORVEY": (7,), "KELDEN": (8,)},
    "Bras": {"HALDEN": (7,), "ROSEDENE": (4,)},
    "Bedding": {"COVPRT": (1,)},
    "Beauty": {"LIPSAT": (10,), "FNDFTH": (20, 39)},
}
SAMPLES = 206


def samples() -> dict[str, list[dict]]:
    """section -> its sample docs: each style's first doc and the extras, then the distractors."""
    out: dict[str, list[dict]] = {}
    for fam, styles in FAMILIES.items():
        mine = out.setdefault(fam, [])
        for s in styles:
            ds = style_docs(fam, s)
            mine += [ds[0], *(ds[i] for i in EXTRA[fam].get(s.code, ()))]
    out["Planted distractors"] = [
        LEMONS, *(x.doc for row in TABLE if not row.tail for x in row.distractors)
    ]  # fmt: skip
    out["Gift wrap"] = [GIFT_BAGS[i] for i in range(0, len(GIFT_BAGS), len(GIFT_PRINTS))]
    gift = next(row for row in TABLE if row.tail)
    out["Gift bag distractors"] = [x.doc for x in (*gift.distractors, *gift.tail)]
    out["Observed failure classes"] = class_docs()
    return out


def _planted() -> dict[str, tuple[str, str]]:
    return {
        **{
            x.doc["product_id"]: (row.query, x.fixed_by)
            for row in TABLE
            for x in (*row.distractors, *row.tail)
        },
        **{
            d["product_id"]: (row.query, fix)
            for row in ROWS
            for style, fix in row.distractors
            for d in style.docs()
        },
    }


#: The fields a policy reads that the round 4 records do not carry.
FACTS = ("product_type", "audience", "size_range", "neckline", "pattern", "leg_style", "rise",
         "color_family", "style_id")  # fmt: skip


def _facts(rec: dict) -> str:
    """A line of the policy-facing fields, or nothing for a record without them."""
    if "product_type" not in rec:
        return ""
    show = {k: ", ".join(v) if isinstance(v, list) else v for k, v in rec.items() if k in FACTS}
    parts = [f"{k}: {show[k]}" for k in FACTS if k in rec]
    parts.append(" > ".join(rec["category_path"]))
    # Food and furniture are colorless: no color facet, no swatches.
    swatches = f"{len(rec['swatches'])} swatches, " if "swatches" in rec else ""
    parts.append(f"{swatches}{rec['rating']} from {rec['review_count']}")
    if rec["badges"]:
        parts.append(" / ".join(rec["badges"]))
    if rec["price_max"] > rec["price_min"]:
        parts.append(f"£{rec['price_min']:.2f} - £{rec['price_max']:.2f}")
    parts.append(f"sold {rec['sold_last_5_days']} in 5 days, bestseller #{rec['bestseller_rank']}")
    if "was_price" in rec:
        parts.append(f"was £{rec['was_price']:.2f}")
    return f'<div class="vg">{escape(" · ".join(parts))}</div>'


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
        f'<div class="vg">{escape(rec["variant_group"])} · {rec["sku_count"]} SKU'
        f"{'s' if rec['sku_count'] != 1 else ''} in this doc</div>"
        f"{_facts(rec)}{note}"
        f'<div class="desc">{escape(rec["description"])}</div>'
        f'<table class="attrs">{_attr_rows(rec)}</table>'
        f"{_sizes(rec)}"
        "</div>"
    )


EXTRA_CSS = """
.vg{color:#1f4f8a;font-size:11px;margin-bottom:4px}.desc{color:#4b5560;margin:4px 0}
.plant{background:#fbe3e3;color:#8a1f1f;border-radius:4px;padding:2px 6px;margin:4px 0}
pre{background:#fff;border:1px solid #d9d7d0;padding:10px;font-size:12px}
table.dist td,table.dist th{border-bottom:1px solid #e3e1da;padding:4px 6px;vertical-align:top;white-space:normal}
"""


def _score_table() -> str:
    cat = corpus()
    rows = []
    for row in TABLE:
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
        f'<p class="note">{n} sample docs. One doc per style × colorway (× leg length for jeans); '
        "sizes are UK/EU/US arrays, so a doc's SKU count is its number of sizes. Jeans and bras "
        "are deep (crossed, rule-bound axes); bedding and beauty are shallow (one hand list per "
        "row). Every brand, line and shade name is invented.</p>"
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
