"""Prove the failure classes of :mod:`real_classes` on a real Elasticsearch.

Loads :func:`real_classes.corpus` into a run-named index, runs each row's
baseline (BM25 x popularity) and its policy, writes the top 5 of each to
``real_classes_proof.json``, prints the README table and deletes the index.
Standard library only.

    python prototypes/retail_drawings/es_proof.py --host http://127.0.0.1:9201
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import real_classes as rc  # noqa: E402

PROOF = HERE / "real_classes_proof.json"


def call(host: str, method: str, path: str, body: object = None, ndjson: bool = False) -> dict:
    data = None
    if body is not None:
        data = (body if ndjson else json.dumps(body)).encode()
    kind = "application/x-ndjson" if ndjson else "application/json"
    req = urllib.request.Request(f"{host}{path}", data, {"Content-Type": kind}, method=method)
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read() or b"{}")


def hits(resp: dict) -> list[dict]:
    return [
        {"product_id": h["_source"]["product_id"], "title": h["_source"]["title"]}
        for h in resp["hits"]["hits"]
    ]


def matched(resp: dict) -> list[dict]:
    """Each hit with the SKUs its nested filter matched (``inner_hits``), as a UI reads them."""
    out = []
    for h in resp["hits"]["hits"]:
        inner = h.get("inner_hits", {}).get("skus", {}).get("hits", {}).get("hits", [])
        skus = [{k: s["_source"][k] for k in ("sku", "color", "size") if k in s["_source"]}
                for s in inner]  # fmt: skip
        out.append({"product_id": h["_source"]["product_id"], "title": h["_source"]["title"],
                    "matched_skus": skus})  # fmt: skip
    return out


def color_search(host: str, index: str) -> dict:
    """The color search of :data:`real_classes.COLOR_QUERY`: plain text, then a nested filter."""
    text, color = rc.COLOR_QUERY
    plain = rc.text_query(f"{color.lower()} {text}")
    base = call(host, "POST", f"/{index}/_search", rc._search(plain, list(rc.POPULARITY), 5))
    nested = call(host, "POST", f"/{index}/_search", rc.color_body(text, color))
    buckets = nested["aggregations"]["skus"]["colors"]["buckets"]
    return {
        "text": text,
        "color": color,
        "baseline": matched(base),
        "nested": matched(nested),
        "facet": [
            {"color": b["key"], "skus": b["doc_count"], "products": b["products"]["doc_count"]}
            for b in buckets
        ],
    }


def run(host: str, index: str) -> dict:
    catalog = rc.corpus()
    call(host, "PUT", f"/{index}", rc.index_body())
    try:
        lines = "".join(
            json.dumps({"index": {"_id": str(n)}}) + "\n" + json.dumps(rc.index_doc(d)) + "\n"
            for n, d in enumerate(catalog)
        )
        resp = call(host, "POST", f"/{index}/_bulk?refresh=true", lines, ndjson=True)
        if resp.get("errors"):
            raise SystemExit("bulk load reported errors")
        rows = [
            {
                "query": row.query,
                "baseline": hits(call(host, "POST", f"/{index}/_search", rc.baseline_body(row))),
                "policy": hits(call(host, "POST", f"/{index}/_search", rc.policy_body(row))),
            }
            for row in rc.ROWS
        ]
        # A control query is the word's other sense, run with the row's policy on.
        controls = [
            {
                "query": c.query,
                "of": row.query,
                "baseline": hits(call(host, "POST", f"/{index}/_search",
                                      rc.baseline_body(row, query=c.query))),
                "policy": hits(call(host, "POST", f"/{index}/_search",
                                    rc.policy_body(row, query=c.query))),
            }  # fmt: skip
            for row in rc.ROWS
            for c in row.controls
        ]
        color = color_search(host, index)
        version = call(host, "GET", "/")["version"]["number"]
    finally:
        call(host, "DELETE", f"/{index}")
    return {
        "elasticsearch": version,
        "docs": len(catalog),
        "fingerprint": rc.fingerprint(catalog),
        "rows": rows,
        "controls": controls,
        "color_search": color,
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--host", default="http://127.0.0.1:9201")
    ap.add_argument("--index", default=f"realcls-proof-{os.getpid()}-{int(time.time())}")
    ap.add_argument("--out", type=Path, default=PROOF)
    args = ap.parse_args(argv)
    proof = run(args.host, args.index)
    args.out.write_text(json.dumps(proof, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    catalog = rc.corpus()
    print(rc.markdown(proof, catalog))
    bad = rc.verdicts(proof, catalog)
    print("\n".join(bad) if bad else "claim holds for every row")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
