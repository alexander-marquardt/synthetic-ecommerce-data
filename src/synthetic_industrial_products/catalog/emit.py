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

import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

from .model import Attribute, Catalog, ProductLine, Sku

_NON_WORD = re.compile(r"[^a-z0-9]+")

#: Where the rendered card images are published: one directory per product
#: type, one PNG per image reference, named for the reference.
#:
#: This is a real host, not a placeholder -- a record that carries a URL a
#: reader cannot fetch is worse than one that carries a bare reference, because
#: the bare reference does not claim to resolve.
DEFAULT_IMAGE_BASE_URL = "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial"


class UnresolvedImageError(Exception):
    """An image reference belongs to no product type, so no URL can be built.

    Raised rather than skipped. Skipping would publish a catalog that is
    quietly missing images for reasons no reader could reconstruct, and the
    reference pool is drawn from the catalog's own SKUs, so this cannot fire
    on a catalog this generator built. It fires if the reference SHAPE changes
    without :func:`image_index` being taught the new shape.
    """


def _owning_type(reference: str, by_sku: dict[str, str], types: frozenset[str]) -> str:
    """The product type whose drawing this reference names.

    An image reference is NOT the referring product's SKU three times in four
    -- reuse crosses brands and it crosses product types, so a hex bolt can
    reference an end mill's drawing. The directory a drawing lives in is a
    property of what is DRAWN, so it is resolved from the reference and never
    from the referring product.

    Three shapes resolve, in order:

    ``98WF97``
        a bare SKU: the drawing is of that product.
    ``437W02_AS01``
        a SKU with an asset suffix, for a product carrying more than one.
    ``end_mill_square_ball_nose``
        a GENERIC drawing, named for what it depicts rather than for any one
        product, because a family shares one image rather than having one
        each. Matched on the longest product-type prefix, so the style suffix
        can be whatever the renderer calls it without this needing to know.

    Anything else raises rather than being skipped: skipping would publish a
    catalog quietly missing images for reasons no reader could reconstruct.
    """
    if reference in by_sku:
        return by_sku[reference]
    base = reference.split("_", 1)[0]
    if base in by_sku:
        return by_sku[base]
    for type_key in sorted(types, key=len, reverse=True):
        if reference == type_key or reference.startswith(f"{type_key}_"):
            return type_key
    raise UnresolvedImageError(
        f"image reference {reference!r} is neither a SKU in this catalog nor "
        "named for one of its product types, so the directory its drawing "
        "belongs to cannot be determined"
    )


def image_index(catalog: Catalog) -> dict[str, str]:
    """Every image reference in the catalog, mapped to its product type.

    Built once over the whole catalog rather than per line, because a line's
    references reach outside it.
    """
    by_sku = {child.sku: line.type_key for line in catalog.lines for child in line.children}
    types = frozenset(line.type_key for line in catalog.lines)
    # NOTE: variant references only. If product LINES gain their own image
    # references, add them here too, or a line-level reference will carry no
    # URL while a variant's does.
    return {
        reference: _owning_type(reference, by_sku, types)
        for line in catalog.lines
        for child in line.children
        for reference in child.image_skus
    }


def image_path(reference: str, index: dict[str, str]) -> str:
    """``end_mill_square/98WF97.png`` -- the path under the image base URL."""
    return f"{index[reference]}/{reference}.png"


def image_urls(references: tuple[str, ...], index: dict[str, str], base_url: str) -> list[str]:
    return [f"{base_url.rstrip('/')}/{image_path(reference, index)}" for reference in references]


def iter_image_manifest(
    catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL
) -> Iterator[dict[str, Any]]:
    """One row per DISTINCT image reference: what it is, and where it is hosted.

    The catalog references an image once per SKU that points at it, which is
    many times over; whatever hosts the images needs each file once. Emitting
    the manifest here means the host reads the product type off this file
    instead of re-deriving it from the catalog with a second copy of the
    reuse rule -- and a second copy is how the two disagree later.
    """
    index = image_index(catalog)
    referenced_by: dict[str, int] = {}
    for line in catalog.lines:
        for child in line.children:
            for reference in child.image_skus:
                referenced_by[reference] = referenced_by.get(reference, 0) + 1
    base = base_url.rstrip("/")
    for reference in sorted(referenced_by):
        path = image_path(reference, index)
        yield {
            "image_ref": reference,
            "product_type": index[reference],
            "path": path,
            "url": f"{base}/{path}",
            "referenced_by": referenced_by[reference],
        }


def sanitize(name: str) -> str:
    """``Milling Dia.`` -> ``milling_dia``: a usable field name.

    Attribute names as published contain dots, slashes and trailing
    punctuation. A dot is a path separator in Elasticsearch and a trailing one
    is simply invalid, so a published name cannot be used as a field name
    as-is.
    """
    return _NON_WORD.sub("_", name.strip().lower()).strip("_")


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
    """
    parts = [child.title, line.brand, line.series, *line.category]
    for attribute in attributes:
        values = attribute.values or (attribute.value,)
        parts.extend(values)
    return " ".join(part for part in parts if part)


def nested_document(
    catalog: Catalog,
    line: ProductLine,
    index: dict[str, str] | None = None,
    base_url: str = DEFAULT_IMAGE_BASE_URL,
) -> dict[str, Any]:
    index = image_index(catalog) if index is None else index
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
        "attributes": _attribute_entries(line.attributes),
        "variant_count": len(line.children),
        "variants": [
            {
                "sku": child.sku,
                "title": child.title,
                "price_usd": child.price_usd,
                "stock": child.stock,
                "image_skus": list(child.image_skus),
                "image_urls": image_urls(child.image_skus, index, base_url),
                "attributes": _attribute_entries(child.attributes),
            }
            for child in line.children
        ],
    }


def flat_documents(
    catalog: Catalog,
    line: ProductLine,
    index: dict[str, str] | None = None,
    base_url: str = DEFAULT_IMAGE_BASE_URL,
) -> Iterator[dict[str, Any]]:
    index = image_index(catalog) if index is None else index
    for child in line.children:
        merged = catalog.merged_attributes(line, child)
        facets: dict[str, list[str]] = {}
        numeric: dict[str, float] = {}
        for attribute in merged:
            key = sanitize(attribute.name)
            values = list(attribute.values or (attribute.value,))
            facets.setdefault(key, []).extend(values)
            if attribute.value_num is not None:
                numeric.setdefault(key, attribute.value_num)
        yield {
            "sku": child.sku,
            "product_id": line.product_id,
            "product_type": line.type_key,
            "title": child.title,
            "parent_title": line.title,
            "brand": line.brand,
            "series": line.series,
            "category_path": list(line.category),
            "category_leaf": line.category[-1],
            "dimension_provenance": line.dimension_provenance,
            "price_usd": child.price_usd,
            "stock": child.stock,
            "image_skus": list(child.image_skus),
            "image_urls": image_urls(child.image_skus, index, base_url),
            "attributes": _attribute_entries(merged),
            "attribute_names": sorted({a.name for a in merged}),
            "facets": facets,
            "facets_num": numeric,
            "text": _searchable_text(line, child, merged),
        }


def iter_nested(
    catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL
) -> Iterator[dict[str, Any]]:
    index = image_index(catalog)
    for line in catalog.lines:
        yield nested_document(catalog, line, index, base_url)


def iter_flat(catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL) -> Iterator[dict[str, Any]]:
    index = image_index(catalog)
    for line in catalog.lines:
        yield from flat_documents(catalog, line, index, base_url)


def write_jsonl(rows: Iterator[dict[str, Any]], path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            count += 1
    return count


#: Mapping for the nested shape. ``attributes`` and ``variants`` are nested so
#: that name and value stay correlated within one entry, and so that
#: ``reverse_nested`` can count parent products rather than attribute entries.
NESTED_MAPPING: dict[str, Any] = {
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
            "variant_count": {"type": "integer"},
            "attributes": {
                "type": "nested",
                "properties": {
                    "name": {"type": "keyword"},
                    "value": {"type": "keyword"},
                    "value_num": {"type": "double"},
                },
            },
            "variants": {
                "type": "nested",
                "properties": {
                    "sku": {"type": "keyword"},
                    "title": {"type": "text"},
                    "price_usd": {"type": "double"},
                    "stock": {"type": "integer"},
                    "image_skus": {"type": "keyword"},
                    "image_urls": {"type": "keyword"},
                    "attributes": {
                        "type": "nested",
                        "properties": {
                            "name": {"type": "keyword"},
                            "value": {"type": "keyword"},
                            "value_num": {"type": "double"},
                        },
                    },
                },
            },
        }
    }
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
            "parent_title": {"type": "text"},
            "brand": {"type": "keyword"},
            "series": {"type": "keyword"},
            "category_path": {"type": "keyword"},
            "category_leaf": {"type": "keyword"},
            "dimension_provenance": {"type": "keyword"},
            "price_usd": {"type": "double"},
            "stock": {"type": "integer"},
            "image_skus": {"type": "keyword"},
            "image_urls": {"type": "keyword"},
            "attribute_names": {"type": "keyword"},
            "attributes": {
                "type": "object",
                "properties": {
                    "name": {"type": "keyword"},
                    "value": {"type": "keyword"},
                    "value_num": {"type": "double"},
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

    :func:`..render.renderer_for` dispatches on the attribute NAMES a record
    carries, not on a type field, and reads values out of a flat mapping keyed
    by the published name -- which is the shape :mod:`..records` uses. Emitting
    that shape means the drawings come from the existing renderer rather than
    from a second one written to a different contract.
    """
    for line in catalog.lines:
        for child in line.children:
            record: dict[str, Any] = {"sku": child.sku}
            for attribute in catalog.merged_attributes(line, child):
                if attribute.values is not None:
                    record[attribute.name] = ", ".join(attribute.values)
                else:
                    record[attribute.name] = attribute.value
            yield record
