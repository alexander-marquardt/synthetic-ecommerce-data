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
        version = call(host, "GET", "/")["version"]["number"]
    finally:
        call(host, "DELETE", f"/{index}")
    return {
        "elasticsearch": version,
        "docs": len(catalog),
        "fingerprint": rc.fingerprint(catalog),
        "rows": rows,
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
