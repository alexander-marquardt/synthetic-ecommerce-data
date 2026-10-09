"""The one output standard every domain's documents meet (gen#125), in two shapes.

Who reads each shape:

- **flat**, one document per SKU (:func:`flat_documents`; industrial writes it as
  ``golden-catalog/flat.jsonl`` with ``emit.flat_documents``): the shape
  elastic/prism-industrial-products loads, as its ``catalog.ndjson``. A loader of
  the industrial file reads the retail one: same keys and types, but retail states
  ``price`` in ``currency`` and ``in_stock`` where industrial has ``price_usd`` and
  ``stock`` (the exact list: ``tests/test_output_standard.py``, ``*_ONLY_FLAT``).
- **nested**, one document per product, below: no loader reads it yet.

A domain emits one nested document per product, its SKUs nested in ``variants``, and
every fact a shopper can narrow on as a nested ``{key, name, value[, unit_code,
value_canonical]}`` attribute entry, at product or variant level. The fields are
:data:`PRODUCT_FIELDS` and :data:`VARIANT_FIELDS`; :data:`.emit.NESTED_MAPPING`
declares exactly these, so a field outside them is a field no query can see.

Price is ``price`` in ``currency`` (ISO 4217), never converted: the industrial
catalog prices in USD (it keeps ``price_usd`` for its loader), the retail one
in GBP. Availability is the ``in_stock`` yes/no; ``stock`` is the count, emitted
only by a domain that models one.

:func:`check_catalog` is the validator: every way a catalog breaks the standard,
empty when it holds. ``tests/test_output_standard.py`` runs it over each domain.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from typing import Any

from synthetic_ecommerce_data.core.entry import CANONICAL_PER_UNIT, RECIPROCAL_PER_UNIT, canonical

_STR, _INT, _NUM, _BOOL, _LIST = "str", "int", "number", "bool", "list"

#: Product-level fields: name -> (type, required). A new field is also added to emit.py's
#: NESTED_MAPPING and FLAT_MAPPING and to the flat tuples below (_FLAT_PRODUCT_FIELDS).
PRODUCT_FIELDS: dict[str, tuple[str, bool]] = {
    "product_id": (_STR, True),
    "product_type": (_STR, True),
    "title": (_STR, True),
    "brand": (_STR, True),
    "series": (_STR, False),
    "category_path": (_LIST, True),
    "category_leaf": (_STR, True),
    "category_depth": (_INT, True),
    "dimension_provenance": (_STR, False),
    "spec_quality": (_STR, False),
    "image_id": (_STR, True),
    "image_url": (_STR, True),
    "image_detail_url": (_STR, True),
    "ingredients": (_LIST, False),
    "attributes": (_LIST, True),
    "variant_count": (_INT, True),
    "variants": (_LIST, True),
}

#: Variant-level fields: name -> (type, required).
VARIANT_FIELDS: dict[str, tuple[str, bool]] = {
    "sku": (_STR, True),
    "title": (_STR, True),
    "description": (_STR, False),
    "price": (_NUM, True),
    "currency": (_STR, True),
    "in_stock": (_BOOL, True),
    "price_usd": (_NUM, False),
    "stock": (_INT, False),
    "image_id": (_STR, True),
    "image_url": (_STR, True),
    "image_detail_url": (_STR, True),
    "ingredients": (_LIST, False),
    "attributes": (_LIST, True),
}

ENTRY_FIELDS = frozenset({"key", "name", "value", "unit_code", "value_canonical"})
KEY_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_]*$")
CURRENCY_PATTERN = re.compile(r"^[A-Z]{3}$")
#: ``<type>/<product>/<drawing>``: the bundle path of the drawing, less ``.svg``.
IMAGE_ID_PATTERN = re.compile(r"^[a-z0-9_]+/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
#: A bare magnitude, the only spelling a measured ``value`` takes.
MAGNITUDE = re.compile(r"^(?:[0-9]+-[0-9]+/[0-9]+|[0-9]+/[0-9]+|[0-9]+(?:\.[0-9]+)?|\.[0-9]+)$")


def _typed(value: Any, kind: str) -> bool:
    if kind == _BOOL:
        return isinstance(value, bool)
    if isinstance(value, bool):
        return False
    return {
        _STR: lambda v: isinstance(v, str) and bool(v),
        _INT: lambda v: isinstance(v, int),
        _NUM: lambda v: isinstance(v, int | float),
        _LIST: lambda v: isinstance(v, list),
    }[kind](value)


def _fields(where: str, row: Mapping[str, Any], spec: Mapping[str, tuple[str, bool]]) -> list[str]:
    out = [f"{where}: {k!r} is not a field of the standard" for k in row if k not in spec]
    for name, (kind, required) in spec.items():
        if name not in row:
            if required:
                out.append(f"{where}: lacks {name!r}")
        elif not _typed(row[name], kind):
            out.append(f"{where}: {name!r} is not a {kind}: {row[name]!r}")
    return out


def check_entry(where: str, entry: Any) -> list[str]:
    """Every way one attribute entry breaks the entry shape (elastic/prism#9935)."""
    if not isinstance(entry, dict):
        return [f"{where}: an entry that is not an object: {entry!r}"]
    out = [f"{where}: entry field {k!r} is not standard" for k in entry if k not in ENTRY_FIELDS]
    if not KEY_PATTERN.fullmatch(str(entry.get("key") or "")):
        out.append(f"{where}: entry key {entry.get('key')!r} is not ^[a-z0-9][a-z0-9_]*$")
    for part in ("name", "value"):
        if not _typed(entry.get(part), _STR):
            out.append(f"{where}: entry {entry.get('key')!r} has no {part} string")
    unit, canon = entry.get("unit_code"), entry.get("value_canonical")
    if (unit is None) != (canon is None):
        out.append(f"{where}: entry {entry.get('key')!r} has unit_code or value_canonical alone")
    elif unit is not None:
        value = str(entry.get("value"))
        if unit not in CANONICAL_PER_UNIT and unit not in RECIPROCAL_PER_UNIT:
            out.append(f"{where}: entry {entry.get('key')!r} unit {unit!r} is not a known code")
        elif not MAGNITUDE.fullmatch(value):
            out.append(f"{where}: entry {entry.get('key')!r} value {value!r} is not a bare number")
        elif canon != canonical(value, unit):
            out.append(
                f"{where}: entry {entry.get('key')!r} canonical {canon!r} is not {value} {unit}"
            )
    return out


def _image(where: str, row: Mapping[str, Any]) -> list[str]:
    image_id = row.get("image_id")
    if not isinstance(image_id, str) or not IMAGE_ID_PATTERN.fullmatch(image_id):
        return [f"{where}: image_id {image_id!r} is not <type>/<product>/<drawing>"]
    return [
        f"{where}: {field} {row.get(field)!r} is not {image_id}.svg"
        for field in ("image_url", "image_detail_url")
        # absent or not a string is _fields' one problem, not a second one here
        if isinstance(row.get(field), str) and not row[field].endswith(f"/{image_id}.svg")
    ]


def check_document(doc: Mapping[str, Any]) -> list[str]:
    """Every way one nested product document breaks the standard; empty when it holds."""
    where = str(doc.get("product_id"))
    out = _fields(where, doc, PRODUCT_FIELDS)
    path = doc.get("category_path")
    if isinstance(path, list):
        if not path or not all(_typed(seg, _STR) for seg in path):
            out.append(f"{where}: category_path {path!r} is not a list of node names")
        elif doc.get("category_leaf") != path[-1] or doc.get("category_depth") != len(path):
            out.append(f"{where}: category_leaf/category_depth do not match {path!r}")
    out += _image(where, doc)
    out += [e for entry in doc.get("attributes") or () for e in check_entry(where, entry)]
    variants = doc.get("variants")
    if not isinstance(variants, list) or not variants:
        return [*out, f"{where}: no variants"]
    if doc.get("variant_count") != len(variants):
        out.append(f"{where}: variant_count {doc.get('variant_count')!r} is not {len(variants)}")
    if doc.get("image_id") != variants[0].get("image_id"):
        out.append(f"{where}: image_id is not its first variant's")
    for variant in variants:
        at = f"{where}/{variant.get('sku')}"
        out += _fields(at, variant, VARIANT_FIELDS)
        out += _image(at, variant)
        if _typed(variant.get("price"), _NUM) and variant["price"] <= 0:
            out.append(f"{at}: price {variant['price']!r} is not positive")
        currency = variant.get("currency")
        # absent or not a string is _fields' one problem, not a second one here
        if isinstance(currency, str) and not CURRENCY_PATTERN.fullmatch(currency):
            out.append(f"{at}: currency {currency!r} is not an ISO 4217 code")
        out += [e for entry in variant.get("attributes") or () for e in check_entry(at, entry)]
    return out


def words(text: str) -> str:
    """``text`` as space-padded lower-case words, ``&`` read as "and": " hook and loop "."""
    return " " + re.sub(r"[^a-z0-9]+", " ", text.lower().replace("&", " and ")).strip() + " "


def _names(padded: str, value: str) -> bool:
    phrase = words(value).strip()
    return bool(phrase) and f" {phrase} " in padded


def value_pools(docs: Iterable[Mapping[str, Any]]) -> dict[tuple[str, str], set[str]]:
    """(leaf, key) -> the worded values the leaf's product attributes carry: the values a
    title or description can contradict. A number or a measured value is never one."""
    pools: dict[tuple[str, str], set[str]] = {}
    for doc in docs:
        for entry in doc.get("attributes") or ():
            value = str(entry.get("value"))
            if "unit_code" not in entry and re.search(r"[A-Za-z]", value):
                pools.setdefault((str(doc.get("category_leaf")), str(entry.get("key"))), set()).add(
                    value
                )
    return pools


def text_contradictions(
    doc: Mapping[str, Any], pools: Mapping[tuple[str, str], set[str]]
) -> list[str]:
    """Each attribute the title or a description contradicts: the text names another value
    of the key's leaf pool and none of the document's own. A word inside another of the
    document's values ("Leather" on a rubber-soled leather loafer) contradicts nothing."""
    attrs = [e for e in doc.get("attributes") or () if isinstance(e, dict)]
    own: dict[str, set[str]] = {}
    for e in attrs:
        own.setdefault(str(e.get("key")), set()).add(str(e.get("value")))
    every = sorted({v for vs in own.values() for v in vs}, key=len, reverse=True)
    texts = [str(doc.get("title") or "")]
    texts += [str(v.get("description")) for v in doc.get("variants") or () if v.get("description")]
    out = []
    for key, mine in own.items():
        pool = pools.get((str(doc.get("category_leaf")), key), set()) - mine
        for text in dict.fromkeys(texts):
            padded = words(text)
            if not pool or any(_names(padded, v) for v in mine):
                continue
            for v in every:
                padded = padded.replace(words(v), " | ") if re.search(r"[A-Za-z]", v) else padded
            named = sorted(v for v in pool if _names(padded, v))
            if named:
                out.append(f"{doc.get('product_id')}: its text names {named[0]!r} but {key} is "
                           f"{sorted(mine)}: {text[:80]!r}")  # fmt: skip
                break
    return out


def check_catalog(docs: Iterable[Mapping[str, Any]], *, text_agrees: bool = True) -> list[str]:
    """Every way a catalog breaks the standard: each document's problems, then the ids
    that repeat and the keys that name two attributes or shadow a top-level field, and,
    with ``text_agrees``, every title or description that contradicts an attribute
    (:func:`text_contradictions`, against the catalog's own :func:`value_pools`)."""
    docs = list(docs)
    out: list[str] = []
    ids: dict[str, int] = {}
    names_by_key: dict[str, set[str]] = {}
    for doc in docs:
        out += check_document(doc)
        rows = [doc, *(doc.get("variants") or ())]
        for field, row in (("product_id", doc), *(("sku", v) for v in rows[1:])):
            ids[f"{field} {row.get(field)}"] = ids.get(f"{field} {row.get(field)}", 0) + 1
        for row in rows:
            for entry in row.get("attributes") or ():
                if isinstance(entry, dict):
                    names_by_key.setdefault(str(entry.get("key")), set()).add(
                        str(entry.get("name"))
                    )
    out += [f"{ident} is not unique ({n} times)" for ident, n in ids.items() if n > 1]
    out += [f"key {k!r} names {sorted(v)}" for k, v in sorted(names_by_key.items()) if len(v) > 1]
    shadow = set(names_by_key) & (set(PRODUCT_FIELDS) | set(VARIANT_FIELDS))
    out += [f"key {k!r} shadows a top-level field" for k in sorted(shadow)]
    if text_agrees:
        pools = value_pools(docs)
        out += [p for doc in docs for p in text_contradictions(doc, pools)]
    return out


#: A plain decimal, the only value a unitless entry in ``numeric_keys`` reads as a number.
_DECIMAL = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")


def _number(entry: Mapping[str, Any], numeric_keys: frozenset[str]) -> float | None:
    """The entry's value as a number in its own unit: a measured entry's magnitude
    (``28`` inches, as industrial's ``facets_num`` holds it), or a unitless one the
    domain names numeric (a rating). ``None`` for anything else (a UK size "4")."""
    value = str(entry.get("value"))
    if entry.get("unit_code") is not None:
        return float(canonical(value, "C62"))  # C62 is one: the magnitude itself
    if entry.get("key") in numeric_keys and _DECIMAL.fullmatch(value):
        return float(value)
    return None


def flat_documents(
    doc: Mapping[str, Any], numeric_keys: frozenset[str] = frozenset()
) -> list[dict[str, Any]]:
    """The flat one-document-per-SKU shape of one nested document, the shape
    industrial's ``emit.flat_documents`` writes and prism-industrial-products loads.

    A SKU's document is its variant's columns under its product's, its attributes
    the product's entries less the keys the variant states for itself (the style's
    list of colors gives way to the SKU's one color), then the variant's. From those
    entries: ``attribute_names``, ``facets`` (key -> values), ``facets_num`` (key ->
    the first value that is a number, :func:`_number`) and the searchable ``text``.
    Product fields the document lacks (``series``) stay absent, never null.
    """
    product = {k: doc[k] for k in _FLAT_PRODUCT_FIELDS if k in doc}
    out: list[dict[str, Any]] = []
    for variant in doc["variants"]:
        own = {e["key"] for e in variant["attributes"]}
        entries = [e for e in doc["attributes"] if e["key"] not in own] + variant["attributes"]
        facets: dict[str, list[str]] = {}
        numeric: dict[str, float] = {}
        for entry in entries:
            facets.setdefault(entry["key"], []).append(entry["value"])
            number = _number(entry, numeric_keys)
            if number is not None:
                numeric.setdefault(entry["key"], number)
        words = [variant["title"], doc["brand"], doc.get("series"), *doc["category_path"]]
        out.append(
            {"sku": variant["sku"], "product_id": doc["product_id"]}
            | {"product_type": doc["product_type"], "title": variant["title"]}
            | {k: variant[k] for k in ("description",) if k in variant}
            | {"parent_title": doc["title"]}
            | product
            | {k: variant[k] for k in _FLAT_VARIANT_FIELDS if k in variant}
            | {
                "attributes": entries,
                "attribute_names": sorted({e["name"] for e in entries}),
                "facets": facets,
                "facets_num": numeric,
                "text": " ".join(w for w in [*words, *(e["value"] for e in entries)] if w),
            }
        )
    return out


#: The product columns a flat document repeats, in industrial's order.
_FLAT_PRODUCT_FIELDS = (
    "brand",
    "series",
    "category_path",
    "category_leaf",
    "dimension_provenance",
    "spec_quality",
    "ingredients",
)
#: The variant columns a flat document carries, in industrial's order.
_FLAT_VARIANT_FIELDS = (
    "price",
    "currency",
    "in_stock",
    "price_usd",
    "stock",
    "image_id",
    "image_url",
    "image_detail_url",
    "ingredients",
)
