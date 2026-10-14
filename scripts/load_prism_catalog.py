"""Load the flat catalog into the index the PRISM customization serves.

    python scripts/load_prism_catalog.py --host http://127.0.0.1:9201

Unlike ``scripts/verify_elasticsearch.py``, which creates its indices and
deletes them again, this one LEAVES the index in place -- a PRISM Engine boots
against it and has to find documents there.

Run against a LOCAL TEST cluster only. ``http://127.0.0.1:9200`` is the live
demo cluster and is refused by name rather than by memory.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from prism_synthetic_industrial import FLAT_INDEX  # noqa: E402
from synthetic_ecommerce_data.core import emit  # noqa: E402
from synthetic_ecommerce_data.core.config import GeneratorConfig  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.generate import generate  # noqa: E402
from synthetic_ecommerce_data.prism.index import (  # noqa: E402
    flat_index_body,
    projected_documents,
)

#: The live demo cluster. Refusing it explicitly is cheaper than remembering
#: not to type it.
FORBIDDEN_PORTS = (":9200",)


def request(host: str, method: str, path: str, body: Any = None) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        if isinstance(body, str):
            data = body.encode("utf-8")
            headers["Content-Type"] = "application/x-ndjson"
        else:
            data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(f"{host}{path}", data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"{method} {path} -> {exc.code}\n{payload}") from exc


def bulk_load(host: str, index: str, rows: list[dict]) -> int:
    chunk: list[str] = []
    total = 0
    for row in rows:
        chunk.append(json.dumps({"index": {"_id": row["sku"]}}))
        chunk.append(json.dumps(row, ensure_ascii=False))
        if len(chunk) >= 2000:
            result = request(host, "POST", f"/{index}/_bulk", "\n".join(chunk) + "\n")
            if result.get("errors"):
                first = next(i for i in result["items"] if i.get("index", {}).get("error"))
                raise SystemExit(f"bulk load failed: {json.dumps(first, indent=1)}")
            total += len(chunk) // 2
            chunk = []
    if chunk:
        result = request(host, "POST", f"/{index}/_bulk", "\n".join(chunk) + "\n")
        if result.get("errors"):
            first = next(i for i in result["items"] if i.get("index", {}).get("error"))
            raise SystemExit(f"bulk load failed: {json.dumps(first, indent=1)}")
        total += len(chunk) // 2
    return total


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="http://127.0.0.1:9201")
    parser.add_argument("--index", default=FLAT_INDEX)
    parser.add_argument("--lines", type=int, default=GeneratorConfig.lines)
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    args = parser.parse_args(argv)

    for forbidden in FORBIDDEN_PORTS:
        if forbidden in args.host:
            raise SystemExit(
                f"refusing {args.host}: {forbidden} is the live demo cluster. "
                "This script only ever runs against a local test cluster."
            )
    if not args.index.startswith("test-"):
        raise SystemExit(
            f"refusing index {args.index!r}: this script only creates indices "
            "named test-<date>-* on a test cluster."
        )

    config = GeneratorConfig(seed=args.seed, lines=args.lines)
    catalog = generate(config)
    rows = list(projected_documents(emit.iter_flat(catalog)))

    request(args.host, "DELETE", f"/{args.index}?ignore_unavailable=true")
    request(args.host, "PUT", f"/{args.index}", flat_index_body())
    loaded = bulk_load(args.host, args.index, rows)
    request(args.host, "POST", f"/{args.index}/_refresh")
    count = request(args.host, "GET", f"/{args.index}/_count")["count"]

    mapping = request(args.host, "GET", f"/{args.index}/_mapping")
    props = mapping[args.index]["mappings"]["properties"]
    facet_fields = len(props.get("facets", {}).get("properties", {}))
    numeric_fields = len(props.get("facets_num", {}).get("properties", {}))

    print(f"{args.host}/{args.index}")
    print(f"  loaded {loaded} documents, cluster reports {count}")
    print(f"  facets.*     {facet_fields} keyword fields")
    print(f"  facets_num.* {numeric_fields} double fields")
    if loaded != count:
        print(f"MISMATCH: loaded {loaded} but cluster has {count}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
