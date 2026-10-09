"""Failure classes 2 to 15 of gen#125, rebuilt from hand-searched live results.

Each :class:`ClassRow` is one query shape observed on a live retail site
(every name here is invented): the *targets* a shopper meant, the products
that win WITHOUT a policy, and the policy that fixes it. The records carry the
fields a policy reads and a title never states:

- ``product_type``, separate from the title;
- ``audience`` (:data:`AUDIENCES`) and ``size_range`` (:data:`SIZE_RANGES`);
- ``neckline``, ``pattern`` and ``leg_style`` (closed lists below);
- ``was_price``, present only on a sale item (``price < was_price``);
- popularity: ``sold_last_5_days`` and ``bestseller_rank`` (1 = best);
- the variant structure (:meth:`Style.doc`, gen#125 ruling): one document per
  style, its color x size SKUs nested in ``skus`` (each with ``color`` and
  ``color_family``), ``color_options`` and ``size_options`` derived from them,
  a pooled rating, ``price_min``/``price_max``, and a legwear ``size_range``
  derived by :func:`derive_size_range`.

The pre-existing records (:func:`distractors.corpus`) are unchanged and carry
none of these fields. The proof is Elasticsearch (:mod:`es_proof`): the
baseline is BM25 times a popularity boost (it mimics the live site); the
policy adds filters and boosts. Its result is committed in
``real_classes_proof.json`` and rendered into the README by :func:`markdown`.
Standard library only.

Where things live: the vocabularies and the record model (:class:`Style`,
:class:`Policy`, :class:`ClassRow`) are in :mod:`class_model`; the rows and
their styles are data in :mod:`class_rows`. This module builds the corpus,
the index and query bodies and the proof checks, and re-exports the names
the tests read as ``rc.<NAME>``.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable

from class_model import AUDIENCES as AUDIENCES
from class_model import BED_SIZE_DIMS as BED_SIZE_DIMS
from class_model import BED_SIZES as BED_SIZES
from class_model import BESTSELLER_TOP, ClassRow
from class_model import BRAND_OWNERS as BRAND_OWNERS
from class_model import COLOR_FAMILIES as COLOR_FAMILIES
from class_model import FINISHES as FINISHES
from class_model import INSIDE_LEGS as INSIDE_LEGS
from class_model import LEG_STYLES as LEG_STYLES
from class_model import LENGTH_RANGE as LENGTH_RANGE
from class_model import NECKLINES as NECKLINES
from class_model import PATH_SEPARATOR as PATH_SEPARATOR
from class_model import PATTERNS as PATTERNS
from class_model import RISES as RISES
from class_model import SIZE_RANGES as SIZE_RANGES
from class_model import derive_size_range as derive_size_range
from class_rows import BEAUTY, CREW_TEE, ROWS
from class_rows import COLLISIONS as COLLISIONS
from class_rows import HONEY as HONEY
from class_rows import OFFERS as OFFERS
from distractors import corpus as base_corpus


def badges(doc: dict) -> list[str]:
    """The tile badges of a ranked doc, in the one order a tile shows them."""
    return [
        label
        for label, on in (
            ("New In", doc["new_in"]),
            ("Bestseller", doc["bestseller_rank"] <= BESTSELLER_TOP),
            ("Trending", doc["trending"]),
            ("Online Only", doc["online_only"]),
        )
        if on
    ]


def class_docs() -> list[dict]:
    """Every record of :data:`ROWS` (targets first), then :data:`BEAUTY`, the
    :data:`OFFERS`, :data:`HONEY` and :data:`CREW_TEE`, each ranked and badged."""
    styles = [s for row in ROWS for s in (*row.targets, *(x for x, _ in row.distractors))]
    out = [s.doc() for s in (*styles, *BEAUTY, *OFFERS, HONEY, CREW_TEE)]
    ranked = sorted(out, key=lambda d: (-d["sold_last_5_days"], d["product_id"]))
    rank = {d["product_id"]: n for n, d in enumerate(ranked, 1)}
    docs = [{**d, "bestseller_rank": rank[d["product_id"]]} for d in out]
    return [{**d, "badges": badges(d)} for d in docs]


# ==========================================================================
# The category path: checked as data, projected at index time
# ==========================================================================

#: Merchandising buckets: a tile label or a landing page, never a path node.
BUCKETS = frozenset({"Sale", "Offers", "Clearance", "New In", "Bestsellers", "Trending",
                     "Petite", "Online Only"})  # fmt: skip
MIN_PATH_DEPTH = 3


def check_category_paths(docs: list[dict]) -> list[str]:
    """Every way the ``category_path`` of ``docs`` breaks the tree; empty when clean.

    A path has at least :data:`MIN_PATH_DEPTH` segments, each a clean shopper
    term (no separator, no "/" or ">") and none a :data:`BUCKETS` label; no
    product path is a strict prefix of another (a leaf is never a parent); and
    within one root a node name sits at one depth only.
    """
    out: list[str] = []
    paths = {tuple(d["category_path"]): d["product_id"] for d in docs}
    for path, pid in paths.items():
        if len(path) < MIN_PATH_DEPTH:
            out.append(f"{pid}: {' > '.join(path)} has fewer than {MIN_PATH_DEPTH} levels")
        for seg in path:
            if "/" in seg or ">" in seg or seg != seg.strip() or not seg:
                out.append(f"{pid}: {seg!r} is not one clean node name")
            if seg in BUCKETS:
                out.append(f"{pid}: {seg!r} is a merchandising bucket, not a category")
    for path, pid in paths.items():
        for other in paths:
            if len(other) > len(path) and other[: len(path)] == path:
                out.append(f"{pid}: the leaf {' > '.join(path)} is also a parent")
                break
    depths: dict[tuple[str, str], set[int]] = {}
    for path in paths:
        for n, seg in enumerate(path[1:], 1):
            depths.setdefault((path[0], seg), set()).add(n)
    out += [
        f"{root}: {seg!r} sits at depths {sorted(ns)}"
        for (root, seg), ns in sorted(depths.items())
        if len(ns) > 1
    ]
    return out


def index_doc(doc: dict) -> dict:
    """The doc as indexed: ``category_path_joined`` holds every ancestor, joined."""
    path = doc["category_path"]
    joined = [PATH_SEPARATOR.join(path[:n]) for n in range(1, len(path) + 1)]
    return {**doc, "category_path_joined": joined}


def corpus() -> list[dict]:
    """The catalog the proof indexes: the round 4 corpus, then every class record."""
    return [*base_corpus(), *class_docs()]


def fingerprint(catalog: list[dict]) -> str:
    """sha256 of the catalog as the proof indexed it: an indexed-field change makes the proof stale.

    The ``drawing`` field is left out. The index mapping is ``dynamic: false`` and maps no
    ``drawing``, so no query can see it: re-drawing a tile must not force an Elasticsearch re-run.
    """
    indexed = ({k: v for k, v in d.items() if k != "drawing"} for d in catalog)
    blob = "".join(json.dumps(d, sort_keys=True, ensure_ascii=False) + "\n" for d in indexed)
    return hashlib.sha256(blob.encode()).hexdigest()


# ==========================================================================
# The Elasticsearch bodies (the baseline mimics the live site)
# ==========================================================================

#: Search-time only: the over-broad style synonym class 3 observed.
SYNONYMS = ("balloon => balloon, barrel",)
KEYWORDS = ("product_id", "product_type", "audience", "size_range",
            "neckline", "pattern", "leg_style", "rise", "category_path", "category_leaf",
            "category_path_joined",
            "brand_owner", "badges", "sub_collection", "product_line",
            "unit_measure")  # fmt: skip
BOOLEANS = ("offer", "online_only", "new_in", "trending")
FLOATS = ("price_min", "price_max", "rating", "discount_pct", "abv", "unit_size")
#: Price and stock are per SKU, so a SKU match must stay inside one SKU.
SKUS = {
    "type": "nested",
    "properties": {
        "sku": {"type": "keyword"},
        "color": {"type": "keyword"},
        "color_family": {"type": "keyword"},
        "finish": {"type": "keyword"},
        "size": {"type": "keyword"},
        "waist": {"type": "keyword"},
        "inside_leg": {"type": "keyword"},
        "in_stock": {"type": "boolean"},
        "bed_size": {"type": "keyword"},
        "width_cm": {"type": "integer"},
        "length_cm": {"type": "integer"},
        "price": {"type": "float"},
    },
}
#: A routed policy multiplies a doc inside its category node by this.
ROUTE_WEIGHT = 25.0


def index_body() -> dict:
    text = {"type": "text", "analyzer": "plain", "search_analyzer": "with_synonyms"}
    chain = ["possessive", "lowercase"]
    return {
        "settings": {
            "number_of_shards": 1,
            "analysis": {
                "filter": {
                    "possessive": {"type": "stemmer", "language": "possessive_english"},
                    "stem": {"type": "stemmer", "language": "english"},
                    "styles": {"type": "synonym_graph", "synonyms": list(SYNONYMS)},
                },
                "analyzer": {
                    "plain": {"tokenizer": "standard", "filter": [*chain, "stem"]},
                    "with_synonyms": {
                        "tokenizer": "standard",
                        "filter": [*chain, "styles", "stem"],
                    },
                },
            },
        },
        "mappings": {
            "dynamic": False,
            "properties": {
                "title": text,
                "description": text,
                **{k: {"type": "keyword"} for k in KEYWORDS},
                "price": {"type": "float"},
                "was_price": {"type": "float"},
                "sold_last_5_days": {"type": "integer"},
                "bestseller_rank": {"type": "integer"},
                "units_per_pack": {"type": "integer"},
                **{k: {"type": "float"} for k in FLOATS},
                **{k: {"type": "boolean"} for k in BOOLEANS},
                "review_count": {"type": "integer"},
                "skus": SKUS,
            },
        },
    }


POPULARITY = (
    {"field_value_factor": {"field": "sold_last_5_days", "modifier": "log1p", "missing": 1}},
    {"filter": {"range": {"bestseller_rank": {"lte": BESTSELLER_TOP}}}, "weight": 1.5},
)
ON_SALE = "doc['was_price'].size() > 0 && doc['price'].value < doc['was_price'].value"


def _search(query: dict, functions: list[dict], size: int) -> dict:
    body = {
        "size": size,
        "_source": ["product_id", "title"],
        "query": {
            "function_score": {
                "query": query,
                "functions": functions,
                "score_mode": "multiply",
                "boost_mode": "multiply",
            }
        },
        "sort": ["_score", {"product_id": "asc"}],
    }
    return body


def text_query(q: str) -> dict:
    return {"multi_match": {"query": q, "fields": ["title^2", "description"], "tie_breaker": 0.3}}


def baseline_body(row: ClassRow, size: int = 5, query: str | None = None) -> dict:
    """BM25 over title and description, times the popularity boost: no policy.

    ``query`` replaces the row's own (a control query of :attr:`ClassRow.controls`).
    """
    return _search(text_query(row.query if query is None else query), list(POPULARITY), size)


def policy_body(row: ClassRow, size: int = 5, query: str | None = None) -> dict:
    """The baseline plus the row's :class:`Policy`, approximated in raw Elasticsearch.

    A query the policy's ``unless`` matches runs as the baseline: the policy is off.
    """
    q = row.query if query is None else query
    if not row.policy.applies(q):
        return baseline_body(row, size, q)
    p = row.policy
    filters: list[dict] = [{"terms": {f: list(v)}} for f, v in p.filters]
    if p.on_sale:
        filters.append({"script": {"script": ON_SALE}})
    if p.sku_filters:
        # One in-stock SKU must carry every value: the match stays inside it.
        sku = [{"terms": {f"skus.{f}": list(v)}} for f, v in p.sku_filters]
        filters.append({"nested": {"path": "skus", "query": {"bool": {
            "filter": sku, "must_not": [{"term": {"skus.in_stock": False}}]}}}})  # fmt: skip
    boosts = [{"filter": {"terms": {f: list(v)}}, "weight": w} for f, v, w in p.boosts]
    if p.route is None:
        scored = {"bool": {"must": text_query(q), "filter": filters}}
    else:
        # The node recalls its docs whatever their text says, and lifts them.
        node = {"term": {"category_path_joined": p.route}}
        scored = {"bool": {"should": [text_query(q), {"constant_score": {"filter": node}}],
                           "minimum_should_match": 1, "filter": filters}}  # fmt: skip
        boosts.append({"filter": node, "weight": ROUTE_WEIGHT})
    return _search(scored, [*POPULARITY, *boosts], size)


#: The ruling's color search: text "tee" with color Navy (:data:`CREW_TEE`).
COLOR_QUERY = ("tee", "Navy")


def color_body(text: str, color: str, size: int = 5) -> dict:
    """``text`` filtered to products with an in-stock SKU in ``color``.

    The nested filter returns the matching SKUs as ``inner_hits``, so a UI can
    preselect that color; the ``colors`` agg counts per SKU color both its SKUs
    and, through ``reverse_nested``, its products (the count a facet shows).
    """
    sku = {"bool": {"filter": [{"term": {"skus.color": color}}],
                    "must_not": [{"term": {"skus.in_stock": False}}]}}  # fmt: skip
    matched = {"nested": {"path": "skus", "query": sku, "inner_hits": {"size": 100}}}
    query = {"bool": {"must": text_query(text), "filter": [matched]}}
    body = _search(query, list(POPULARITY), size)
    body["aggs"] = {"skus": {"nested": {"path": "skus"}, "aggs": {"colors": {
        "terms": {"field": "skus.color", "size": 50},
        "aggs": {"products": {"reverse_nested": {}}}}}}}  # fmt: skip
    return body


# ==========================================================================
# The recorded proof, rendered for the README
# ==========================================================================


def verdicts(proof: dict, catalog: list[dict]) -> list[str]:
    """Every way ``proof`` fails the claim; empty when it holds over ``catalog``.

    The claim: the proof was taken over ``catalog``; per row, no target in the
    baseline top 3 (a row with ``baseline_holds`` claims that sense is in it instead) and only
    targets in the policy top 3.
    """
    by_id = {d["product_id"]: d for d in catalog}
    out = []
    if proof.get("fingerprint") != fingerprint(catalog):
        out.append("the proof was taken over another catalog: re-run es_proof.py")
    got = {r["query"]: r for r in proof.get("rows", [])}
    for row in ROWS:
        rec = got.get(row.query)
        if rec is None:
            out.append(f"{row.query!r}: not in the proof")
            continue
        base = [by_id[h["product_id"]] for h in rec["baseline"][:3] if h["product_id"] in by_id]
        pol = [by_id[h["product_id"]] for h in rec["policy"][:3] if h["product_id"] in by_id]
        if row.baseline_holds is not None:
            if not any(row.baseline_holds.is_intended(d) for d in base):
                held = row.baseline_holds.intended
                out.append(f"{row.query!r}: the baseline top 3 holds no {held}")
        elif any(row.is_intended(d) for d in base):
            out.append(f"{row.query!r}: a target is in the baseline top 3")
        if len(pol) != 3 or not all(row.is_intended(d) for d in pol):
            out.append(f"{row.query!r}: the policy top 3 is not all targets")
    controls = {r["query"]: r for r in proof.get("controls", [])}
    for row in ROWS:
        for c in row.controls:
            crec = controls.get(c.query)
            if crec is None:
                out.append(f"{c.query!r} (control): not in the proof")
                continue
            pol = [by_id[h["product_id"]] for h in crec["policy"][:3] if h["product_id"] in by_id]
            if len(pol) != 3 or not all(c.is_intended(d) for d in pol):
                out.append(f"{c.query!r} (control): the policy top 3 is not all {c.intended}")
    return out


def markdown(proof: dict, catalog: list[dict]) -> str:
    """The README's before and after table; a target is in bold."""
    by_id = {d["product_id"]: d for d in catalog}
    got = {r["query"]: r for r in proof["rows"]}

    def cell(is_intended: Callable[[dict], bool], hits: list[dict]) -> str:
        out = []
        for n, h in enumerate(hits, 1):
            name = f"{h['title']} `{h['product_id']}`"
            target = is_intended(by_id[h["product_id"]])
            out.append(f"{n}. **{name}**" if target else f"{n}. {name}")
        return "<br>".join(out)

    controls = {r["query"]: r for r in proof.get("controls", [])}

    lines = [
        "| # | Class | Query | Baseline top 5 (BM25 x popularity) | With the policy: top 5 "
        "| Policy (raw ES) |",
        "|---|---|---|---|---|---|",
    ]
    for row in ROWS:
        r = got[row.query]
        lines.append(
            f"| {row.n} | {row.cls} | *{row.query}* | {cell(row.is_intended, r['baseline'])} | "
            f"{cell(row.is_intended, r['policy'])} | {row.policy.describe()} |"
        )
        for c in row.controls:
            # The word's other sense, run with the same policy on: bold is that sense.
            r = controls[c.query]
            lines.append(
                f"| {row.n} (control) | The other sense stays reachable: {c.intended} | "
                f"*{c.query}* | {cell(c.is_intended, r['baseline'])} | "
                f"{cell(c.is_intended, r['policy'])} | the same policy, off for this query |"
            )
    return "\n".join(lines)
