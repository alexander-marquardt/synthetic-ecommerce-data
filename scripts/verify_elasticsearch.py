"""Load the generated catalog into Elasticsearch and prove the properties it exists for.

Run against a LOCAL TEST cluster only::

    python scripts/verify_elasticsearch.py --host http://127.0.0.1:9201

Every index this creates is named ``test-<date>-*`` and is deleted at the end.

The discipline that makes this worth running: **every number Elasticsearch
returns is compared against a number computed independently in Python, from
the same in-memory catalog objects.** An aggregation that agrees with itself
proves nothing -- it is perfectly possible for a wrong query to return a
self-consistent wrong answer, and a ground truth the search engine did not
produce is the only thing that catches it.
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from synthetic_industrial_products.catalog import emit  # noqa: E402
from synthetic_industrial_products.catalog.config import GeneratorConfig  # noqa: E402
from synthetic_industrial_products.catalog.generate import generate  # noqa: E402
from synthetic_industrial_products.catalog.vocab import STANDARDS_NAME  # noqa: E402

INDEX_PREFIX = "test-2026-09-17"
NESTED_INDEX = f"{INDEX_PREFIX}-sip-nested"
FLAT_INDEX = f"{INDEX_PREFIX}-sip-flat"

#: The live demo cluster. Refusing this explicitly is cheaper than
#: remembering not to type it.
FORBIDDEN_PORTS = (":9200",)


class Checks:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str, str]] = []

    def record(self, ok: bool, name: str, detail: str) -> None:
        self.rows.append((ok, name, detail))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        for line in detail.splitlines():
            print(f"         {line}")

    @property
    def failed(self) -> int:
        return sum(1 for ok, _, _ in self.rows if not ok)


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
        with urllib.request.urlopen(req, timeout=120) as response:
            return json.loads(response.read() or b"{}")
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8", "replace")
        raise SystemExit(f"{method} {path} -> {exc.code}\n{payload}") from exc


def bulk_load(host: str, index: str, rows: list[dict], id_field: str) -> None:
    chunk: list[str] = []
    total = 0
    for row in rows:
        chunk.append(json.dumps({"index": {"_id": row[id_field]}}))
        chunk.append(json.dumps(row, ensure_ascii=False))
        if len(chunk) >= 2000:
            result = request(host, "POST", f"/{index}/_bulk", "\n".join(chunk) + "\n")
            if result.get("errors"):
                first = next(item for item in result["items"] if item.get("index", {}).get("error"))
                raise SystemExit(f"bulk load failed: {json.dumps(first, indent=1)}")
            total += len(chunk) // 2
            chunk = []
    if chunk:
        result = request(host, "POST", f"/{index}/_bulk", "\n".join(chunk) + "\n")
        if result.get("errors"):
            first = next(item for item in result["items"] if item.get("index", {}).get("error"))
            raise SystemExit(f"bulk load failed: {json.dumps(first, indent=1)}")
        total += len(chunk) // 2
    request(host, "POST", f"/{index}/_refresh")
    print(f"  loaded {total} documents into {index}")


# ---------------------------------------------------------------------------
# ground truth, computed in Python and never from Elasticsearch
# ---------------------------------------------------------------------------


def ground_truth(catalog) -> dict[str, Any]:
    line_attr_products: dict[tuple[str, str], set[str]] = defaultdict(set)
    name_products: dict[str, set[str]] = defaultdict(set)
    name_entries: Counter[str] = Counter()
    names_by_type: dict[str, set[str]] = defaultdict(set)
    flat_names_by_type: dict[str, set[str]] = defaultdict(set)

    for line in catalog.lines:
        for attribute in line.attributes:
            values = attribute.values or (attribute.value,)
            for value in values:
                line_attr_products[(attribute.name, value)].add(line.product_id)
                name_entries[attribute.name] += 1
            name_products[attribute.name].add(line.product_id)
            names_by_type[line.type_key].add(attribute.name)
        for child in line.children:
            for attribute in catalog.merged_attributes(line, child):
                flat_names_by_type[line.type_key].add(attribute.name)

    return {
        "line_attr_products": line_attr_products,
        "name_products": name_products,
        "name_entries": name_entries,
        "names_by_type": names_by_type,
        "flat_names_by_type": flat_names_by_type,
    }


# ---------------------------------------------------------------------------
# the proofs
# ---------------------------------------------------------------------------


def check_reverse_nested_facet(host: str, truth: dict, checks: Checks) -> None:
    """A nested KV facet count must equal what clicking that facet returns."""
    name = "Fastener Material"
    agg = request(
        host,
        "POST",
        f"/{NESTED_INDEX}/_search",
        {
            "size": 0,
            "aggs": {
                "attrs": {
                    "nested": {"path": "attributes"},
                    "aggs": {
                        "named": {
                            "filter": {"term": {"attributes.name": name}},
                            "aggs": {
                                "values": {
                                    "terms": {"field": "attributes.value", "size": 50},
                                    "aggs": {"products": {"reverse_nested": {}}},
                                }
                            },
                        }
                    },
                }
            },
        },
    )
    buckets = agg["aggregations"]["attrs"]["named"]["values"]["buckets"]
    if not buckets:
        checks.record(False, "reverse_nested facet counts", f"no buckets for {name!r}")
        return

    mismatches = []
    for bucket in buckets:
        value = bucket["key"]
        facet_count = bucket["products"]["doc_count"]
        click = request(
            host,
            "POST",
            f"/{NESTED_INDEX}/_search",
            {
                "size": 0,
                "track_total_hits": True,
                "query": {
                    "nested": {
                        "path": "attributes",
                        "query": {
                            "bool": {
                                "filter": [
                                    {"term": {"attributes.name": name}},
                                    {"term": {"attributes.value": value}},
                                ]
                            }
                        },
                    }
                },
            },
        )
        click_count = click["hits"]["total"]["value"]
        expected = len(truth["line_attr_products"][(name, value)])
        if not (facet_count == click_count == expected):
            mismatches.append(f"{value}: facet={facet_count} click={click_count} truth={expected}")

    detail = "\n".join(
        f"{b['key']}: facet {b['products']['doc_count']} == click == python truth"
        for b in buckets[:5]
    )
    if mismatches:
        detail = "\n".join(mismatches)
    checks.record(
        not mismatches,
        f"nested facet count == click count == Python truth ({name}, {len(buckets)} values)",
        detail,
    )


def check_multivalued_overcount(host: str, truth: dict, checks: Checks) -> None:
    """The multi-valued attribute must over-report WITHOUT reverse_nested."""
    agg = request(
        host,
        "POST",
        f"/{NESTED_INDEX}/_search",
        {
            "size": 0,
            "aggs": {
                "attrs": {
                    "nested": {"path": "attributes"},
                    "aggs": {
                        "names": {
                            "terms": {"field": "attributes.name", "size": 200},
                            "aggs": {"products": {"reverse_nested": {}}},
                        }
                    },
                }
            },
        },
    )
    buckets = {b["key"]: b for b in agg["aggregations"]["attrs"]["names"]["buckets"]}

    multi = buckets.get(STANDARDS_NAME)
    if multi is None:
        checks.record(False, "multi-valued over-count", f"no {STANDARDS_NAME} bucket")
        return

    naive = multi["doc_count"]
    corrected = multi["products"]["doc_count"]
    truth_entries = truth["name_entries"][STANDARDS_NAME]
    truth_products = len(truth["name_products"][STANDARDS_NAME])

    ok = naive == truth_entries and corrected == truth_products and naive > corrected
    checks.record(
        ok,
        f"{STANDARDS_NAME} over-reports without reverse_nested",
        f"naive nested doc_count = {naive} (Python truth: {truth_entries} attribute entries)\n"
        f"reverse_nested count  = {corrected} (Python truth: {truth_products} products)\n"
        f"the naive count overstates products by {naive - corrected} "
        f"({(naive / corrected - 1) * 100:.1f}%)",
    )

    # A single-valued attribute is the control: the two numbers must AGREE.
    single = buckets.get("Item")
    if single is None:
        checks.record(False, "single-valued control", "no Item bucket")
        return
    agree = single["doc_count"] == single["products"]["doc_count"]
    checks.record(
        agree,
        "single-valued attribute: the two counts agree (control)",
        f"Item: naive {single['doc_count']} == reverse_nested "
        f"{single['products']['doc_count']}\n"
        "so the gap above is caused by multi-valuedness, not by the aggregation",
    )


def check_facet_discovery(host: str, truth: dict, checks: Checks) -> None:
    """Terms agg on the attribute-name field, scoped to one product type."""
    for type_key in ("hammer_ball_pein", "abrasive_flap_disc", "washer_flat"):
        agg = request(
            host,
            "POST",
            f"/{NESTED_INDEX}/_search",
            {
                "size": 0,
                "query": {"term": {"product_type": type_key}},
                "aggs": {
                    "attrs": {
                        "nested": {"path": "attributes"},
                        "aggs": {"names": {"terms": {"field": "attributes.name", "size": 200}}},
                    }
                },
            },
        )
        found = {b["key"] for b in agg["aggregations"]["attrs"]["names"]["buckets"]}
        expected = truth["names_by_type"][type_key]
        checks.record(
            found == expected,
            f"facet discovery scoped to {type_key} returns exactly its own names",
            f"{len(found)} names: {sorted(found)}\n"
            + (
                "matches the Python truth exactly"
                if found == expected
                else f"missing {sorted(expected - found)}, extra {sorted(found - expected)}"
            ),
        )


def check_numeric_range(host: str, catalog, checks: Checks) -> None:
    """A numeric range on the shared value_num, scoped by attribute name."""
    name = "Milling Dia."
    low, high = 0.25, 0.5

    expected = set()
    for line in catalog.lines:
        for child in line.children:
            for attribute in child.attributes:
                if (
                    attribute.name == name
                    and attribute.value_num is not None
                    and low <= attribute.value_num <= high
                ):
                    expected.add(child.sku)

    result = request(
        host,
        "POST",
        f"/{NESTED_INDEX}/_search",
        {
            "size": 0,
            "aggs": {
                "variants": {
                    "nested": {"path": "variants"},
                    "aggs": {
                        "attrs": {
                            "nested": {"path": "variants.attributes"},
                            "aggs": {
                                "matching": {
                                    "filter": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"variants.attributes.name": name}},
                                                {
                                                    "range": {
                                                        "variants.attributes.value_num": {
                                                            "gte": low,
                                                            "lte": high,
                                                        }
                                                    }
                                                },
                                            ]
                                        }
                                    },
                                    "aggs": {"skus": {"reverse_nested": {"path": "variants"}}},
                                }
                            },
                        }
                    },
                }
            },
        },
    )
    got = result["aggregations"]["variants"]["attrs"]["matching"]["skus"]["doc_count"]
    checks.record(
        got == len(expected),
        f"numeric range on value_num scoped by name ({name} in [{low}, {high}])",
        f"Elasticsearch: {got} SKUs\nPython truth : {len(expected)} SKUs",
    )

    # The correlation is the point: without the name filter the same range
    # matches any attribute at all, which is a strictly larger set.
    loose = request(
        host,
        "POST",
        f"/{NESTED_INDEX}/_search",
        {
            "size": 0,
            "aggs": {
                "variants": {
                    "nested": {"path": "variants"},
                    "aggs": {
                        "attrs": {
                            "nested": {"path": "variants.attributes"},
                            "aggs": {
                                "matching": {
                                    "filter": {
                                        "range": {
                                            "variants.attributes.value_num": {
                                                "gte": low,
                                                "lte": high,
                                            }
                                        }
                                    },
                                    "aggs": {"skus": {"reverse_nested": {"path": "variants"}}},
                                }
                            },
                        }
                    },
                }
            },
        },
    )
    unscoped = loose["aggregations"]["variants"]["attrs"]["matching"]["skus"]["doc_count"]
    checks.record(
        unscoped > got,
        "dropping the name filter widens the range match (the scoping does work)",
        f"scoped by name: {got} SKUs; unscoped: {unscoped} SKUs",
    )


def analyze(host: str, text: str) -> list[str]:
    """The tokens Elasticsearch actually produces for a value."""
    result = request(host, "POST", "/_analyze", {"analyzer": "standard", "text": text})
    return [token["token"] for token in result["tokens"]]


def carries_phrase(tokens: list[str], phrase: list[str]) -> bool:
    return any(tokens[i : i + len(phrase)] == phrase for i in range(len(tokens)))


def check_demo_case(host: str, catalog, checks: Checks) -> None:
    """Full text finds the token in the WRONG role; the structured filter excludes it.

    The Python ground truth here is defined against the ANALYSER, not against
    the raw strings. A value only reaches a phrase query if it tokenises to the
    phrase, and the published spellings do not all agree about that: 3/8" and
    3/8 in both tokenise to ["3", "8"], but 3/8in tokenises to ["3", "8in"] and
    a phrase query for "3/8" cannot reach it. Comparing the query against a
    startswith() truth reported that as a search failure when it is a
    tokenisation fact -- and it is a fact worth knowing, because it means the
    unit spelling a supplier chose decides whether a shopper's query finds the
    product at all.
    """
    token = "3/8"
    phrase = analyze(host, token)

    reachable: dict[str, bool] = {}

    def text_reachable(value: str) -> bool:
        if value not in reachable:
            reachable[value] = carries_phrase(analyze(host, value), phrase)
        return reachable[value]

    shank_only: set[str] = set()
    cutting: set[str] = set()
    unreachable_spellings: set[str] = set()
    for line in catalog.lines:
        for child in line.children:
            by_name = {a.name: a.value for a in child.attributes}
            shank = by_name.get("Shank Dia.")
            mill = by_name.get("Milling Dia.")
            if shank is None or mill is None:
                continue
            if shank.startswith(token) and not text_reachable(shank):
                unreachable_spellings.add(shank)
            if text_reachable(shank) and not text_reachable(mill):
                shank_only.add(child.sku)
            if text_reachable(mill):
                cutting.add(child.sku)

    if unreachable_spellings:
        print(
            f"         note: {sorted(unreachable_spellings)} start with {token!r} but do "
            "not tokenise to it, so no phrase query can reach them"
        )

    if not shank_only:
        checks.record(False, "demo case", "no product has 3/8 on the shank but not the cutter")
        return

    text_query = {"match_phrase": {"text": token}}
    found = request(
        host,
        "POST",
        f"/{FLAT_INDEX}/_search",
        {"size": 0, "track_total_hits": True, "query": text_query},
    )["hits"]["total"]["value"]

    # Does full text reach the products whose SHANK carries the value?
    reached = request(
        host,
        "POST",
        f"/{FLAT_INDEX}/_search",
        {
            "size": 0,
            "track_total_hits": True,
            "query": {
                "bool": {"filter": [text_query, {"terms": {"sku": sorted(shank_only)[:1000]}}]}
            },
        },
    )["hits"]["total"]["value"]
    sample = min(len(shank_only), 1000)
    checks.record(
        reached == sample,
        f"a full-text query for {token!r} DOES return products whose shank carries it",
        f"{reached} of {sample} shank-only products matched the text query\n"
        f"(the whole text query returns {found} documents)",
    )

    # Guard against a vacuous pass. If the structured filter matches nothing at
    # all -- a mis-mapped field, say -- then "it excluded the shank-only
    # products" is true and meaningless. This check failed once for exactly
    # that reason, so the precondition is now asserted before the exclusion is.
    filter_reach = request(
        host,
        "POST",
        f"/{FLAT_INDEX}/_search",
        {
            "size": 0,
            "track_total_hits": True,
            "query": {"prefix": {"facets.milling_dia": token}},
        },
    )["hits"]["total"]["value"]
    checks.record(
        filter_reach > 0,
        "the structured attribute filter matches something at all (anti-vacuity guard)",
        f"Milling Dia. prefix {token!r} matches {filter_reach} documents",
    )

    # Now add the structured filter. Those products must drop out.
    filtered = request(
        host,
        "POST",
        f"/{FLAT_INDEX}/_search",
        {
            "size": 0,
            "track_total_hits": True,
            "query": {
                "bool": {
                    "filter": [
                        text_query,
                        {"prefix": {"facets.milling_dia": token}},
                        {"terms": {"sku": sorted(shank_only)[:1000]}},
                    ]
                }
            },
        },
    )["hits"]["total"]["value"]
    checks.record(
        filtered == 0,
        "adding the structured attribute filter excludes every one of them",
        f"{filtered} shank-only products survive the Milling Dia. filter (expected 0)",
    )

    # And the filter keeps the products that really do have a 3/8 cutter.
    kept = request(
        host,
        "POST",
        f"/{FLAT_INDEX}/_search",
        {
            "size": 0,
            "track_total_hits": True,
            "query": {"bool": {"filter": [text_query, {"prefix": {"facets.milling_dia": token}}]}},
        },
    )["hits"]["total"]["value"]
    checks.record(
        kept == len(cutting),
        "and keeps exactly the products whose CUTTING diameter carries it",
        f"Elasticsearch: {kept}\nPython truth : {len(cutting)}",
    )


def check_flat_shape_loses_correlation(host: str, catalog, checks: Checks) -> None:
    """The flat shape cannot correlate name with value, and that is the point."""
    name, value = "Shank Dia.", '3/8"'
    truth = set()
    for line in catalog.lines:
        for child in line.children:
            for attribute in child.attributes:
                if attribute.name == name and attribute.value == value:
                    truth.add(child.sku)
    if not truth:
        checks.record(False, "flat correlation loss", f"no SKU has {name} = {value}")
        return

    naive = request(
        host,
        "POST",
        f"/{FLAT_INDEX}/_search",
        {
            "size": 0,
            "track_total_hits": True,
            "query": {
                "bool": {
                    "filter": [
                        {"term": {"attributes.name": name}},
                        {"term": {"attributes.value": value}},
                    ]
                }
            },
        },
    )["hits"]["total"]["value"]

    checks.record(
        naive > len(truth),
        "the FLAT shape over-matches a name+value filter (correlation is lost)",
        f"flat object filter: {naive} SKUs\nPython truth      : {len(truth)} SKUs\n"
        f"the flat shape returns {naive - len(truth)} SKUs that have a shank diameter\n"
        f"somewhere and a {value} somewhere, but not on the same attribute",
    )

    nested_count = request(
        host,
        "POST",
        f"/{NESTED_INDEX}/_search",
        {
            "size": 0,
            "aggs": {
                "variants": {
                    "nested": {"path": "variants"},
                    "aggs": {
                        "attrs": {
                            "nested": {"path": "variants.attributes"},
                            "aggs": {
                                "matching": {
                                    "filter": {
                                        "bool": {
                                            "filter": [
                                                {"term": {"variants.attributes.name": name}},
                                                {"term": {"variants.attributes.value": value}},
                                            ]
                                        }
                                    },
                                    "aggs": {"skus": {"reverse_nested": {"path": "variants"}}},
                                }
                            },
                        }
                    },
                }
            },
        },
    )["aggregations"]["variants"]["attrs"]["matching"]["skus"]["doc_count"]
    checks.record(
        nested_count == len(truth),
        "the NESTED shape gets the same filter exactly right",
        f"nested: {nested_count}\nPython truth: {len(truth)}",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="http://127.0.0.1:9201")
    parser.add_argument("--lines", type=int, default=GeneratorConfig.lines)
    parser.add_argument("--seed", type=int, default=GeneratorConfig.seed)
    parser.add_argument("--keep", action="store_true", help="do not delete the test indices")
    args = parser.parse_args(argv)

    for port in FORBIDDEN_PORTS:
        if port in args.host:
            raise SystemExit(f"refusing to touch {args.host}: {port} is the live demo cluster")

    info = request(args.host, "GET", "/")
    print(f"cluster {info['cluster_name']} version {info['version']['number']} at {args.host}")

    config = GeneratorConfig(seed=args.seed, lines=args.lines)
    catalog = generate(config)
    print(f"generated {len(catalog.lines)} lines / {catalog.sku_count} skus")
    truth = ground_truth(catalog)

    for index, mapping in ((NESTED_INDEX, emit.NESTED_MAPPING), (FLAT_INDEX, emit.FLAT_MAPPING)):
        request(args.host, "DELETE", f"/{index}?ignore_unavailable=true")
        request(args.host, "PUT", f"/{index}", mapping)

    bulk_load(args.host, NESTED_INDEX, list(emit.iter_nested(catalog)), "product_id")
    bulk_load(args.host, FLAT_INDEX, list(emit.iter_flat(catalog)), "sku")

    checks = Checks()
    print("\n-- 1. nested KV facet counts match what a click returns --")
    check_reverse_nested_facet(args.host, truth, checks)
    print("\n-- 2. the multi-valued attribute over-reports without reverse_nested --")
    check_multivalued_overcount(args.host, truth, checks)
    print("\n-- 3. facet discovery scoped to one product type --")
    check_facet_discovery(args.host, truth, checks)
    print("\n-- 4. numeric range on the shared value_num, scoped by name --")
    check_numeric_range(args.host, catalog, checks)
    print("\n-- 5. the demo case: role ambiguity in full text --")
    check_demo_case(args.host, catalog, checks)
    print("\n-- 6. what the flat shape cannot do --")
    check_flat_shape_loses_correlation(args.host, catalog, checks)

    if not args.keep:
        for index in (NESTED_INDEX, FLAT_INDEX):
            request(args.host, "DELETE", f"/{index}?ignore_unavailable=true")
        print(f"\ndeleted {NESTED_INDEX} and {FLAT_INDEX}")

    print(f"\n{len(checks.rows) - checks.failed} of {len(checks.rows)} checks passed")
    return 1 if checks.failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
