"""Two serialisations of one catalog.

Both shapes are emitted from the same generated objects, so they describe the
same products and any difference between what they return is a property of the
shape, not of the data.

**Nested** -- a parent document with its SKUs nested inside it, and key-value
attributes nested at both levels. This is the target shape: it is the only one
in which "how many PRODUCTS have this attribute value" is answerable, via
``reverse_nested``, and the only one in which two attributes of the same entry
stay correlated.

**Flat** -- one document per SKU with the line's attributes denormalised onto
it. Loadable today. The attribute array here is a plain ``object``, not
``nested``, which is exactly the limitation worth demonstrating: ``name`` and
``value`` become two independent multi-valued fields, so a filter for
*name = Shank Dia. AND value = 3/8"* matches any record that has a shank
diameter anywhere and a 3/8" anywhere, whether or not they are the same
attribute.

A sanitised ``facets`` object is emitted alongside, because an attribute name
like ``Milling Dia.`` cannot be an Elasticsearch field name -- the trailing dot
makes it an invalid path. The three spellings of the measurement-system
attribute deliberately sanitise to three different keys rather than being
folded into one: folding them here would hide the problem a field map exists
to solve.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from synthetic_ecommerce_data.core.dimensions import _METRIC_THREAD
from synthetic_ecommerce_data.core.entry import (
    sanitize as sanitize,  # re-exported: tests and readers call emit.sanitize
)
from synthetic_ecommerce_data.core.model import Attribute, Catalog, ProductLine, Sku
from synthetic_ecommerce_data.domains.industrial.taxonomy import (
    ImageIdError,
    product_type_for_image,
)

#: Where a record's image is served from: the bundle's folder, as the demo
#: serves it (elastic/prism#9770, the Studio images mount). Relative, so
#: nothing points at a third-party host; ``--image-base-url`` moves it.
#: The bundle's top-level folder. The archive's members live under it and the
#: demo serves the images folder at ``/images`` (elastic/prism#9770), so a URL
#: is ``/images/<IMAGE_ROOT>/<path>`` and deployments can sit side by side
#: under one images mount.
IMAGE_ROOT = "industrial"
DEFAULT_IMAGE_BASE_URL = f"/images/{IMAGE_ROOT}"

#: The ISO 4217 code of every industrial price. The nested standard's ``price`` is
#: in ``currency`` (:mod:`.standard`); ``price_usd`` stays beside it for the loader.
CURRENCY = "USD"


class UnresolvedImageError(Exception):
    """A catalog image id is not its SKU's own, so no URL can be built for it.

    Raised rather than skipped. Skipping would publish a catalog quietly
    missing images for reasons no reader could reconstruct.
    """


def image_path(image_id: str) -> str:
    """``end_mill_square/OST-K663-0001/97NR28.svg`` -- the path inside the bundle.

    Nothing is looked up: the id already reads ``<type>/<product>/<sku>``, so
    this validates and appends the extension. A second table of where each id
    goes is exactly how a record's URL and the manifest's path come to disagree.
    """
    product_type_for_image(image_id)
    return f"{image_id}.svg"


def image_url(image_id: str, base_url: str) -> str:
    return f"{base_url.rstrip('/')}/{image_path(image_id)}"


def check_image_ids(catalog: Catalog) -> None:
    """Every SKU names its own drawing, and every product its first SKU's.

    Checked once over the whole catalog, before any URL is published. Named
    separately, because "some image is broken" is not a report anyone can act
    on: an id that is not ``<type>/<product>/<sku>``; a SKU pointing at
    another SKU's drawing; a product not pointing at its first variant's.
    """
    malformed: list[str] = []
    mismatched: list[str] = []
    for line in catalog.lines:
        for child in line.children:
            try:
                product_type_for_image(child.image_id)
            except ImageIdError:
                malformed.append(child.image_id)
                continue
            expected = f"{line.type_key}/{line.product_id}/{child.sku}"
            if child.image_id != expected:
                mismatched.append(f"{child.sku} -> {child.image_id}")
        if line.children and line.image_id != line.children[0].image_id:
            mismatched.append(f"{line.product_id} -> {line.image_id} (not its first variant's)")
    problems = []
    if malformed:
        problems.append(
            f"{len(malformed)} image id(s) are not <type>/<product>/<sku>: {malformed[:5]}"
        )
    if mismatched:
        problems.append(f"{len(mismatched)} image id(s) are not their own: {mismatched[:5]}")
    if problems:
        raise UnresolvedImageError("; ".join(problems))


def drawing_record(catalog: Catalog, line: ProductLine, child: Sku) -> dict[str, str]:
    """What a SKU's drawing reads: its published attributes, name to value."""
    record: dict[str, str] = {}
    for attribute in catalog.merged_attributes(line, child):
        record[attribute.name] = (
            ", ".join(attribute.values) if attribute.values is not None else attribute.value
        )
    return record


def iter_drawings(catalog: Catalog) -> Iterator[tuple[ProductLine, Sku, bytes, str]]:
    """Every SKU's drawing: ``(line, sku, svg_bytes, geometry_source)``, in catalog order."""
    from synthetic_ecommerce_data.core.drawing import draw_product  # noqa: PLC0415

    for line in catalog.lines:
        records = [drawing_record(catalog, line, child) for child in line.children]
        drawn = draw_product(line.type_key, line.brand, records)
        for child, (data, source) in zip(line.children, drawn, strict=True):
            yield line, child, data, source


def iter_image_manifest(
    catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL
) -> Iterator[dict[str, Any]]:
    """One row per SKU image: its id, path, URL, and the sha256 of its bytes.

    The digest is what couples the committed catalog to the drawings: a
    regenerated drawing under an unchanged id has a new digest, so the bundle
    built from it cannot pass for the old one (the gap
    elastic/prism-industrial-products#78 recorded, where only file LISTS were
    compared). ``geometry`` says whether the drawing read every drawn value off
    the record (``record``), filled some with nominal proportions
    (``partial``), or none (``nominal``).
    """
    check_image_ids(catalog)
    for line, child, data, source in iter_drawings(catalog):
        yield {
            "image_id": child.image_id,
            "product_type": line.type_key,
            "product_id": line.product_id,
            "sku": child.sku,
            "path": image_path(child.image_id),
            "url": image_url(child.image_id, base_url),
            "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data),
            "geometry": source,
        }


def _attribute_entries(attributes: tuple[Attribute, ...]) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    for attribute in attributes:
        entries.extend(attribute.as_entries())
    return entries


def _searchable_text(line: ProductLine, child: Sku, attributes: tuple[Attribute, ...]) -> str:
    """Everything a full-text query should be able to reach.

    The attribute VALUES are in here on purpose. The demo case is a query for
    a bare dimension token matching a product whose shank -- not whose cutting
    diameter -- carries that value, and that can only happen if the shank's
    value is searchable as text.

    The DESCRIPTION is deliberately not in here, though it is searchable --
    except its cross-reference sentence, below. It
    is declared as a field of its own in the PRISM field map, and it opens
    with the title verbatim and then restates values this function already
    collects from the attributes -- so folding it in here would roughly double
    the term frequency of every title token against the rest of the corpus,
    which is a relevance change nothing in this repository measures. The only
    tokens it would add that are not already here are attribute NAMES, and
    those are published in ``attribute_names``.
    """
    parts = [child.title, line.brand, line.series, *line.category]
    for attribute in attributes:
        values = attribute.values or (attribute.value,)
        parts.extend(values)
        # A metric designation is ONE token to the standard analyzer
        # (``m12x1.75``), so a shopper's ``m12 socket cap screws`` reached no
        # screw at all -- while a hex key whose copy says "For M12 socket head
        # cap screws" matched every word. The diameter the designation names is
        # added beside it: a fact of this record, read from its own value.
        parts.extend(f"M{m.group('dia')}" for value in values if (m := _METRIC_THREAD.match(value)))
    # The cross-reference sentence IS folded in, unlike the rest of the
    # description: it names the OTHER product a query may be about (``For M12
    # socket head cap screws``), which is what makes a size query reach the
    # keys, taps and nuts that fit it as well as the screw -- and no attribute
    # carries it, deliberately (:mod:`.compat`).
    parts.append(child.compatibility)
    # The noise sentences likewise (:mod:`.noise`): what a search matches on
    # includes what the copy says a product is NOT, the siblings it comes in,
    # what it pairs with -- which is why a policy or a facet has to narrow.
    parts.append(child.noise)
    return " ".join(part for part in parts if part)


def nested_document(
    catalog: Catalog,
    line: ProductLine,
    base_url: str = DEFAULT_IMAGE_BASE_URL,
) -> dict[str, Any]:
    return {
        "product_id": line.product_id,
        "product_type": line.type_key,
        "title": line.title,
        "brand": line.brand,
        "series": line.series,
        "category_path": list(line.category),
        "category_leaf": line.category[-1],
        "category_depth": len(line.category),
        "dimension_provenance": line.dimension_provenance,
        "spec_quality": line.spec_quality,
        "image_id": line.image_id,
        "image_url": image_url(line.image_id, base_url),
        "image_detail_url": image_url(line.image_id, base_url),
        "attributes": _attribute_entries(line.attributes),
        "variant_count": len(line.children),
        "variants": [
            {
                "sku": child.sku,
                "title": child.title,
                "description": child.description,
                "price": child.price_usd,
                "currency": CURRENCY,
                "in_stock": child.stock > 0,
                "price_usd": child.price_usd,
                "stock": child.stock,
                "image_id": child.image_id,
                "image_url": image_url(child.image_id, base_url),
                "image_detail_url": image_url(child.image_id, base_url),
                "attributes": _attribute_entries(child.attributes),
            }
            for child in line.children
        ],
    }


def flat_documents(
    catalog: Catalog,
    line: ProductLine,
    base_url: str = DEFAULT_IMAGE_BASE_URL,
) -> Iterator[dict[str, Any]]:
    for child in line.children:
        merged = catalog.merged_attributes(line, child)
        facets: dict[str, list[str]] = {}
        numeric: dict[str, float] = {}
        for attribute in merged:
            key = attribute.facet_key
            values = list(attribute.values or (attribute.value,))
            facets.setdefault(key, []).extend(values)
            if attribute.value_num is not None:
                numeric.setdefault(key, attribute.value_num)
        yield {
            "sku": child.sku,
            "product_id": line.product_id,
            "product_type": line.type_key,
            "title": child.title,
            # The SKU's own copy, and the LINE's title beside it. They are two
            # different things and the description used to be the second: a
            # line title restates the brand, the series and the product type,
            # which is why six SKUs of one line showed six identical
            # descriptions. ``parent_title`` still ships -- it is what the
            # grouped view will head a card with -- but it is no longer what a
            # shopper reads under the title.
            "description": child.description,
            "parent_title": line.title,
            "brand": line.brand,
            "series": line.series,
            "category_path": list(line.category),
            "category_leaf": line.category[-1],
            "dimension_provenance": line.dimension_provenance,
            "spec_quality": line.spec_quality,
            "price_usd": child.price_usd,
            "stock": child.stock,
            "image_id": child.image_id,
            "image_url": image_url(child.image_id, base_url),
            "image_detail_url": image_url(child.image_id, base_url),
            "attributes": _attribute_entries(merged),
            "attribute_names": sorted({a.name for a in merged}),
            "facets": facets,
            "facets_num": numeric,
            "text": _searchable_text(line, child, merged),
        }


def iter_nested(
    catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL
) -> Iterator[dict[str, Any]]:
    check_image_ids(catalog)
    for line in catalog.lines:
        yield nested_document(catalog, line, base_url)


def iter_flat(catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL) -> Iterator[dict[str, Any]]:
    check_image_ids(catalog)
    for line in catalog.lines:
        yield from flat_documents(catalog, line, base_url)


def write_jsonl(rows: Iterator[dict[str, Any]], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


#: The attribute-set key ``value_normalized_field`` Prism reads (elastic/prism#10648),
#: relative to the nested ``attributes`` path, and the normalizer behind it.
VALUE_NORMALIZED_FIELD = "value.normalized"
VALUE_NORMALIZER = "value_folded"


def _value_column() -> dict[str, Any]:
    """The nested ``value`` column: verbatim keyword plus its folded sub-field."""
    sub = VALUE_NORMALIZED_FIELD.split(".", 1)[1]
    return {
        "type": "keyword",
        "fields": {sub: {"type": "keyword", "normalizer": VALUE_NORMALIZER}},
    }


#: Mapping for the nested shape. ``attributes`` and ``variants`` are nested so
#: that name and value stay correlated within one entry, and so that
#: ``reverse_nested`` can count parent products rather than attribute entries.
NESTED_MAPPING: dict[str, Any] = {
    "settings": {
        "analysis": {
            "normalizer": {
                VALUE_NORMALIZER: {"type": "custom", "filter": ["lowercase", "asciifolding"]}
            }
        }
    },
    "mappings": {
        "properties": {
            "product_id": {"type": "keyword"},
            "product_type": {"type": "keyword"},
            "title": {"type": "text"},
            "brand": {"type": "keyword"},
            "series": {"type": "keyword"},
            "category_path": {"type": "keyword"},
            "category_leaf": {"type": "keyword"},
            "category_depth": {"type": "integer"},
            "dimension_provenance": {"type": "keyword"},
            "spec_quality": {"type": "keyword"},
            "image_id": {"type": "keyword"},
            "image_url": {"type": "keyword"},
            "image_detail_url": {"type": "keyword"},
            "ingredients": {"type": "text"},
            "variant_count": {"type": "integer"},
            "attributes": {
                "type": "nested",
                "properties": {
                    "key": {"type": "keyword"},
                    "name": {"type": "keyword"},
                    "value": _value_column(),
                    "unit_code": {"type": "keyword"},
                    "value_canonical": {"type": "double"},
                },
            },
            "variants": {
                "type": "nested",
                "properties": {
                    "sku": {"type": "keyword"},
                    "title": {"type": "text"},
                    "description": {"type": "text"},
                    "price": {"type": "double"},
                    "currency": {"type": "keyword"},
                    "in_stock": {"type": "boolean"},
                    "price_usd": {"type": "double"},
                    "stock": {"type": "integer"},
                    "image_id": {"type": "keyword"},
                    "image_url": {"type": "keyword"},
                    "image_detail_url": {"type": "keyword"},
                    "ingredients": {"type": "text"},
                    "attributes": {
                        "type": "nested",
                        "properties": {
                            "key": {"type": "keyword"},
                            "name": {"type": "keyword"},
                            "value": _value_column(),
                            "unit_code": {"type": "keyword"},
                            "value_canonical": {"type": "double"},
                        },
                    },
                },
            },
        }
    },
}

#: Mapping for the flat shape. ``attributes`` is deliberately an OBJECT and
#: not nested: that is the shape an engine without nested-query support sees,
#: and the correlation loss it causes is one of the things worth measuring.
FLAT_MAPPING: dict[str, Any] = {
    "mappings": {
        "dynamic": False,
        # The facet keys are dynamic -- they come from whatever attribute names
        # the catalog happens to publish -- but their TYPE must not be. Left to
        # dynamic mapping a facet value becomes an analysed text field, and a
        # term or prefix filter against it silently matches nothing: the query
        # returns zero, which reads like "no such product" rather than like a
        # mapping mistake. A verification run caught exactly that, and a check
        # asserting such a filter EXCLUDED something passed vacuously because
        # the filter had matched nothing to begin with.
        "dynamic_templates": [
            {"facet_values": {"path_match": "facets.*", "mapping": {"type": "keyword"}}},
            {"facet_numbers": {"path_match": "facets_num.*", "mapping": {"type": "double"}}},
        ],
        "properties": {
            "sku": {"type": "keyword"},
            "product_id": {"type": "keyword"},
            "product_type": {"type": "keyword"},
            "title": {"type": "text"},
            "description": {"type": "text"},
            "parent_title": {"type": "text"},
            "brand": {"type": "keyword"},
            "series": {"type": "keyword"},
            "category_path": {"type": "keyword"},
            "category_leaf": {"type": "keyword"},
            "dimension_provenance": {"type": "keyword"},
            "spec_quality": {"type": "keyword"},
            "price_usd": {"type": "double"},
            "stock": {"type": "integer"},
            "image_id": {"type": "keyword"},
            "image_url": {"type": "keyword"},
            "image_detail_url": {"type": "keyword"},
            "ingredients": {"type": "text"},
            "attribute_names": {"type": "keyword"},
            "attributes": {
                "type": "object",
                "properties": {
                    "key": {"type": "keyword"},
                    "name": {"type": "keyword"},
                    "value": {"type": "keyword"},
                    "unit_code": {"type": "keyword"},
                    "value_canonical": {"type": "double"},
                },
            },
            "facets": {"type": "object", "dynamic": True},
            "facets_num": {"type": "object", "dynamic": True},
            "text": {"type": "text"},
        },
    }
}


def render_records(catalog: Catalog) -> Iterator[dict[str, Any]]:
    """Records in the shape the existing renderer already reads.

    Values are read out of a flat mapping keyed by the published name -- the
    shape :mod:`..records` uses -- plus two reserved keys that are not
    attributes: ``sku`` and ``product_type``. The type is what
    :func:`..render.kinds.classify` dispatches on; attribute names stopped
    identifying a type when one concept became one generic name across types
    (elastic/prism-industrial-products#103).
    """
    from synthetic_ecommerce_data.domains.industrial.render.kinds import TYPE_KIND  # noqa: PLC0415

    for line in catalog.lines:
        # Only the types that renderer draws: the newer ones exist only as
        # the catalog's own text-free drawings (:mod:`..drawing`).
        if line.type_key not in TYPE_KIND:
            continue
        for child in line.children:
            record: dict[str, Any] = {"sku": child.sku, "product_type": line.type_key}
            for attribute in catalog.merged_attributes(line, child):
                if attribute.values is not None:
                    record[attribute.name] = ", ".join(attribute.values)
                else:
                    record[attribute.name] = attribute.value
            yield record


def referenced_image_ids(catalog: Catalog) -> set[str]:
    """Every image anything in the catalog points at: one per SKU."""
    referenced = {line.image_id for line in catalog.lines}
    referenced.update(child.image_id for _, child in catalog.all_skus())
    return referenced - {""}
