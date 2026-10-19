"""Prove a PRISM deployment actually SERVES this catalog.

    python scripts/verify_prism_serves.py --studio http://127.0.0.1:8477

A field map that validates is not a served catalog, and a search that returns
documents is not a correct one. So every number PRISM reports here is compared
against one computed independently in Python from the same in-memory catalog
objects -- the discipline ``scripts/verify_elasticsearch.py`` already uses.
An aggregation that agrees with itself proves nothing: a wrong query can
return a self-consistent wrong answer.

The load-bearing check is FACET COUNT == CLICK RESULT. A facet that says "412"
and returns 380 when clicked is a lie told to a shopper, and it is a blocking
defect rather than a note.

Prerequisites -- a loaded index and a booted Engine + Studio pointing at the
TEST cluster::

    python scripts/load_prism_catalog.py --host http://127.0.0.1:9201
    PRISM_CUSTOMIZATION_PATH=<this repo> PRISM_RUNTIME_MODE=dev \\
      PRISM_ELASTICSEARCH_URL=http://127.0.0.1:9201 \\
      prism-engine serve --port 9477 --no-reload
    PRISM_ENGINE_URL=http://127.0.0.1:9477 ... prism-studio serve --port 8477
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from synthetic_ecommerce_data.core import emit  # noqa: E402
from synthetic_ecommerce_data.core.config import GeneratorConfig  # noqa: E402
from synthetic_ecommerce_data.domains.industrial.generate import generate  # noqa: E402

PERSONA = "Industrial"


class Checks:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str]] = []

    def record(self, ok: bool, name: str, detail: str = "") -> None:
        self.rows.append((ok, name))
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
        for line in detail.splitlines():
            if line.strip():
                print(f"         {line}")

    @property
    def failed(self) -> int:
        return sum(1 for ok, _ in self.rows if not ok)


def search(studio: str, body: dict[str, Any], **params: Any) -> dict:
    query = "&".join(f"{k}={v}" for k, v in {"persona": PERSONA, **params}.items())
    req = urllib.request.Request(
        f"{studio}/v1/search?{query}",
        data=json.dumps(body).encode("utf-8"),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            return json.loads(response.read())
    except urllib.error.HTTPError as exc:
        raise SystemExit(
            f"POST /v1/search -> {exc.code}\n{exc.read().decode('utf-8', 'replace')}"
        ) from exc


def facet(response: dict, name: str) -> dict | None:
    return next((f for f in response["facets"] if f["name"] == name), None)


def ids(response: dict) -> set[str]:
    return {r["id"] for r in response["results"]}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--studio", default="http://127.0.0.1:8477")
    parser.add_argument(
        "--click-samples",
        type=int,
        default=6,
        help="how many facet values to click per facet",
    )
    args = parser.parse_args(argv)
    checks = Checks()

    # ---- ground truth, computed in Python, never from Elasticsearch -------
    catalog = generate(GeneratorConfig())
    flat = list(emit.iter_flat(catalog))
    by_sku = {row["sku"]: row for row in flat}
    print(f"ground truth: {len(flat)} SKUs generated in memory\n")

    # =====================================================================
    print("1. a search returns products")
    # =====================================================================
    response = search(args.studio, {"query": "end mill", "size": 10})
    checks.record(
        response["total"] > 0 and len(response["results"]) == 10,
        "query 'end mill' returns results",
        f"total={response['total']} ({response['total_relation']}), "
        f"page carries {len(response['results'])}",
    )
    unknown = sorted(ids(response) - set(by_sku))
    checks.record(
        not unknown,
        "every returned id is a SKU the generator produced",
        f"unknown ids: {unknown[:5]}" if unknown else "all 10 resolve",
    )

    # =====================================================================
    print("\n2. a terms facet carries counts that match ground truth")
    # =====================================================================
    everything = search(args.studio, {"query": "", "size": 1})
    truth_type: Counter[str] = Counter(row["product_type"] for row in flat)
    pt = facet(everything, "product_type")
    assert pt is not None, "product_type facet missing"
    served = {value: count for value, count, _, _ in pt["buckets"]}
    mismatched = {
        value: (count, truth_type[value])
        for value, count in served.items()
        if count != truth_type[value]
    }
    checks.record(
        not mismatched and set(served) == set(truth_type),
        "product_type facet counts equal the generated counts",
        f"{len(served)} buckets; "
        + (f"mismatches {mismatched}" if mismatched else "every count matches Python"),
    )

    truth_material: Counter[str] = Counter()
    for row in flat:
        for value in row["facets"].get("material", []):
            truth_material[value] += 1
    fm = facet(everything, "material")
    assert fm is not None, "material facet missing"
    served_fm = {value: count for value, count, _, _ in fm["buckets"]}
    checks.record(
        served_fm == dict(truth_material),
        "material (a derived TERMS facet) matches ground truth",
        f"served {served_fm}\ntruth  {dict(truth_material)}",
    )

    # =====================================================================
    print("\n3. a numeric range facet on a dimension")
    # =====================================================================
    truth_shank = [
        row["facets_num"]["shank_dia"] for row in flat if "shank_dia" in row["facets_num"]
    ]
    sd = facet(everything, "shank_dia")
    assert sd is not None, "shank_dia facet missing"
    checks.record(
        sd["field_type"] == "numeric",
        "shank_dia is served as a NUMERIC facet",
        f"field_type={sd['field_type']}, min={sd['min']}, max={sd['max']}",
    )
    checks.record(
        sd["min"] is not None
        and sd["max"] is not None
        and abs(sd["max"] - max(truth_shank)) < 1e-9,
        "the range facet's max equals the catalog's max shank diameter",
        f"served max={sd['max']}  python max={max(truth_shank)}  "
        f"(n={len(truth_shank)} documents carry a shank diameter)",
    )

    # a real range NARROWS, and to the right documents
    lo, hi = 0.5, 0.75
    # ``size`` must be >= 1: the Engine rejects a zero page size (422,
    # page_size ge=1), so a count-only probe asks for one document and reads
    # ``total`` rather than asking for none.
    ranged = search(
        args.studio,
        {"query": "", "size": 1, "range_filters": [{"name": "shank_dia", "gte": lo, "lte": hi}]},
    )
    truth_ranged = sum(
        1
        for row in flat
        if "shank_dia" in row["facets_num"] and lo <= row["facets_num"]["shank_dia"] <= hi
    )
    checks.record(
        ranged["total"] == truth_ranged,
        f"range filter shank_dia [{lo}, {hi}] returns exactly the matching documents",
        f"served total={ranged['total']}  python={truth_ranged}",
    )

    # =====================================================================
    print("\n4. FACET COUNT == CLICK RESULT (blocking)")
    # =====================================================================
    for facet_name in ("product_type", "brand", "material", "item"):
        block = facet(everything, facet_name)
        if block is None:
            checks.record(False, f"{facet_name}: facet absent from the response")
            continue
        bad: list[str] = []
        sampled = block["buckets"][: args.click_samples]
        for value, count, _, _ in sampled:
            clicked = search(
                args.studio,
                {
                    "query": "",
                    "size": 1,
                    "facet_intents": [{"intent": "include", "field": facet_name, "value": value}],
                },
            )
            if clicked["total"] != count:
                bad.append(f"{value!r}: facet said {count}, click returned {clicked['total']}")
        checks.record(
            not bad,
            f"{facet_name}: every sampled facet count equals its click result",
            "\n".join(bad) if bad else f"{len(sampled)} values clicked, all equal",
        )

    # =====================================================================
    print("\n4b. every one of the 10 product types is actually servable")
    # =====================================================================
    # A facet bucket proves the documents are THERE; it does not prove a
    # search can reach them. Each type is clicked and its documents read back.
    unservable: list[str] = []
    for product_type, expected in sorted(truth_type.items()):
        clicked = search(
            args.studio,
            {
                "query": "",
                "size": 3,
                "facet_intents": [
                    {"intent": "include", "field": "product_type", "value": product_type}
                ],
            },
        )
        wrong = [sku for sku in ids(clicked) if by_sku[sku]["product_type"] != product_type]
        if clicked["total"] != expected or not clicked["results"] or wrong:
            unservable.append(
                f"{product_type}: total={clicked['total']} expected={expected} "
                f"page={len(clicked['results'])} wrong_type={wrong}"
            )
    checks.record(
        not unservable,
        "all 10 product types return their own documents, in the generated count",
        "\n".join(unservable)
        if unservable
        else f"{len(truth_type)} types, {sum(truth_type.values())} documents total",
    )

    # =====================================================================
    print("\n5. the demo case -- a dimension token in the query text")
    # =====================================================================
    # A query for a bare dimension token reaches products whose SHANK carries
    # that value, not only those whose CUTTING diameter does. That is the
    # attribute-role ambiguity this catalog exists to reproduce.
    token, value = '3/8"', 0.375

    def has(row: dict, name: str, wanted: float) -> bool:
        return abs(row["facets_num"].get(name, -1) - wanted) < 1e-9

    truth_shank_only = {
        row["sku"]
        for row in flat
        if row["product_type"].startswith("end_mill")
        and has(row, "shank_dia", value)
        and not has(row, "milling_dia", value)
    }
    checks.record(
        len(truth_shank_only) > 0,
        "the catalog contains end mills whose SHANK is 3/8 but whose CUTTING diameter is not",
        f"{len(truth_shank_only)} such SKUs -- these are the surprising hits",
    )

    text_only = search(args.studio, {"query": f"{token} end mill", "size": 100})
    returned = ids(text_only)
    surprising = returned & truth_shank_only
    checks.record(
        len(surprising) > 0,
        "the free-text query DOES return shank-carries-3/8 products",
        f"{len(surprising)} of the first {len(returned)} hits are shank-only matches, e.g. "
        + ", ".join(sorted(surprising)[:3]),
    )

    # Now the structured filter the shopper actually meant.
    filtered = search(
        args.studio,
        {
            "query": f"{token} end mill",
            "size": 100,
            "range_filters": [{"name": "milling_dia", "gte": value, "lte": value}],
        },
    )
    leaked = ids(filtered) & truth_shank_only
    checks.record(
        not leaked,
        "adding the structured milling_dia filter EXCLUDES the shank-only products",
        f"{len(ids(filtered))} hits after filtering, "
        + (f"LEAKED {sorted(leaked)[:5]}" if leaked else "none of them shank-only"),
    )
    wrong_dia = sorted(sku for sku in ids(filtered) if not has(by_sku[sku], "milling_dia", value))
    checks.record(
        not wrong_dia,
        "every document surviving the filter really has milling_dia == 3/8",
        f"violations: {wrong_dia[:5]}" if wrong_dia else f"{len(ids(filtered))} checked",
    )
    checks.record(
        filtered["total"] < text_only["total"],
        "the filter actually narrowed the result set",
        f"{text_only['total']} -> {filtered['total']}",
    )

    # =====================================================================
    print("\n6. the flat shape's known correlation loss, measured")
    # =====================================================================
    # Documented rather than asserted away: in the flat shape the per-attribute
    # facet keys keep name and value together, but the raw ``attributes`` array
    # does not. This measures how much over-matching the array would cause.
    # Both sides ask the SAME question -- "which documents publish
    # Shank dia. = 3/8\"" -- and differ only in how they match it.
    #
    #   naive:   the ``attributes`` array is a plain object, so ``name`` and
    #            ``value`` are two independent multi-valued fields. A filter
    #            for name=Shank dia. AND value=3/8" matches any document
    #            carrying a shank diameter ANYWHERE and a 3/8" ANYWHERE --
    #            the 3/8" may belong to a different attribute entirely.
    #   precise: the pairing held together, which is what the sanitised
    #            per-attribute ``facets.shank_dia`` field preserves.
    # An entry carries the token split (elastic/prism#9935): magnitude plus unit code.
    split_token = ("3/8", "INH")
    shank = "Shank dia."  # the name as published, not as authored
    naive = sum(
        1
        for row in flat
        if shank in {a["name"] for a in row["attributes"]}
        and split_token in {(a.get("value"), a.get("unit_code")) for a in row["attributes"]}
    )
    precise = sum(
        1
        for row in flat
        if any(
            a["name"] == shank and (a.get("value"), a.get("unit_code")) == split_token
            for a in row["attributes"]
        )
    )
    checks.record(
        naive > 0 and naive >= precise,  # naive == 0 measures a name no document carries
        "object-array filtering over-matches, which is why the field map uses facets.*",
        f"name+value over the flat object array matches {naive} documents; "
        f"the pairing held together matches {precise}; "
        f'over-match = {naive - precise} documents whose 3/8" belongs to a '
        f"DIFFERENT attribute than the shank",
    )

    print(f"\n{len(checks.rows) - checks.failed} of {len(checks.rows)} checks passed")
    if checks.failed:
        print(f"{checks.failed} FAILED")
    return 1 if checks.failed else 0


if __name__ == "__main__":
    sys.exit(main())
