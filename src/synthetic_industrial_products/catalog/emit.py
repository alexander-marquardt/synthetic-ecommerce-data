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
from .taxonomy import ImageIdError, product_type_for_image

_NON_WORD = re.compile(r"[^a-z0-9]+")

#: Where the rendered images are published: one directory per product type,
#: inside it one directory per product line, and inside that one PNG per
#: profile.
#:
#: This is a real host, not a placeholder -- a record that carries a URL a
#: reader cannot fetch is worse than one that carries a bare reference, because
#: the bare reference does not claim to resolve.
DEFAULT_IMAGE_BASE_URL = "https://alexmarquardt.com/ecommerce-demo-assets/images/industrial"

#: The profile a catalog card shows, and the one a detail view shows. Both are
#: published, because the card's 600x880 is unreadable at 1400x1400's job and
#: the reverse.
CARD_PROFILE = "card"
DETAIL_PROFILE = "detail"


class UnresolvedImageError(Exception):
    """A catalog image id names no product line, so no URL can be built for it.

    Raised rather than skipped. Skipping would publish a catalog quietly
    missing images for reasons no reader could reconstruct.
    """


def image_path(image_id: str, profile: str = CARD_PROFILE) -> str:
    """``end_mill_square/OST-K663-0001/card.png`` -- the path under the base URL.

    One directory per PRODUCT TYPE, one per PRODUCT LINE inside it, one file
    per profile inside that. The type is the category a reader browsing the
    published tree gets an index of; the line is what the drawing is OF.
    Filing by profile instead would index the tree by *which size* an image is,
    which is a property of the file rather than a thing anybody browses for.

    Nothing is looked up. The image id already reads
    ``<product type>/<product id>`` -- :func:`..taxonomy.image_id_for` built it
    that way -- so this appends the profile and validates, rather than keeping
    a second table of where each id goes. A second table is exactly how a
    record's URL and the manifest's path come to disagree.
    """
    product_type_for_image(image_id)
    return f"{image_id}/{profile}.png"


def image_url(image_id: str, base_url: str, profile: str = CARD_PROFILE) -> str:
    return f"{base_url.rstrip('/')}/{image_path(image_id, profile)}"


def check_image_ids(catalog: Catalog) -> None:
    """Every image id in the catalog names one of its own product lines.

    Checked once over the whole catalog, before any URL is published. A URL
    built for an id no line owns is a dead link, and a dead link is worse than
    a bare id: the bare id does not claim to resolve.

    Three separate things can be wrong and each is named separately, because
    "some image is broken" is not a report anyone can act on:

    * an id that is not ``<product type>/<product id>`` at all;
    * a line whose id is not the id of that line -- which would publish one
      line's drawing under another line's URL;
    * a SKU pointing somewhere other than at its own line's drawing, which is
      the variant-grouping story breaking in the one place nothing else looks.
    """
    from ..render.generic import IMAGE_IDS  # noqa: PLC0415

    drawings = set(IMAGE_IDS)
    malformed: list[str] = []
    mismatched: list[str] = []
    undrawn: list[str] = []
    for line in catalog.lines:
        try:
            product_type_for_image(line.image_id)
        except ImageIdError:
            malformed.append(line.image_id)
            continue
        if line.image_id != f"{line.type_key}/{line.product_id}":
            mismatched.append(f"{line.product_id} -> {line.image_id}")
        if line.drawing not in drawings:
            undrawn.append(f"{line.product_id} -> {line.drawing!r}")
        for child in line.children:
            if child.image_id != line.image_id:
                mismatched.append(f"{child.sku} -> {child.image_id} (line {line.image_id})")
    problems = []
    if malformed:
        problems.append(
            f"{len(malformed)} image id(s) are not <type>/<product id>: {malformed[:5]}"
        )
    if mismatched:
        problems.append(
            f"{len(mismatched)} image id(s) do not name their own line: {mismatched[:5]}"
        )
    if undrawn:
        problems.append(
            f"{len(undrawn)} line(s) name a shape no drawing exists for: {undrawn[:5]}. "
            "Either the renderer lost a drawing or taxonomy.DRAWING gained a name "
            "it has no drawing for."
        )
    if problems:
        raise UnresolvedImageError("; ".join(problems))


def iter_image_manifest(
    catalog: Catalog, base_url: str = DEFAULT_IMAGE_BASE_URL
) -> Iterator[dict[str, Any]]:
    """One row per DISTINCT image: what it is, where it is hosted, who uses it.

    The catalog references an image once per product and once per variant that
    points at it, which for ten drawings and four thousand products is many
    thousands of times over; whatever hosts the files needs each one once.
    Emitting the manifest here means the host reads the paths off this file
    instead of re-deriving them from the catalog with a second copy of the
    naming rule -- and a second copy is how the two come to disagree.
    """
    check_image_ids(catalog)
    referenced_by: dict[str, int] = {}
    drawn_as: dict[str, str] = {}
    for line in catalog.lines:
        referenced_by[line.image_id] = referenced_by.get(line.image_id, 0) + 1
        drawn_as[line.image_id] = line.drawing
        for child in line.children:
            referenced_by[child.image_id] = referenced_by.get(child.image_id, 0) + 1
    for image_id in sorted(referenced_by):
        yield {
            "image_id": image_id,
            "product_type": product_type_for_image(image_id),
            "drawing": drawn_as[image_id],
            "path": image_path(image_id, CARD_PROFILE),
            "url": image_url(image_id, base_url, CARD_PROFILE),
            "detail_path": image_path(image_id, DETAIL_PROFILE),
            "detail_url": image_url(image_id, base_url, DETAIL_PROFILE),
            "referenced_by": referenced_by[image_id],
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
        "image_id": line.image_id,
        "image_url": image_url(line.image_id, base_url),
        "image_detail_url": image_url(line.image_id, base_url, DETAIL_PROFILE),
        "attributes": _attribute_entries(line.attributes),
        "variant_count": len(line.children),
        "variants": [
            {
                "sku": child.sku,
                "title": child.title,
                "price_usd": child.price_usd,
                "stock": child.stock,
                "image_id": child.image_id,
                "image_url": image_url(child.image_id, base_url),
                "image_detail_url": image_url(child.image_id, base_url, DETAIL_PROFILE),
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
            "image_id": child.image_id,
            "image_url": image_url(child.image_id, base_url),
            "image_detail_url": image_url(child.image_id, base_url, DETAIL_PROFILE),
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
            "image_id": {"type": "keyword"},
            "image_url": {"type": "keyword"},
            "image_detail_url": {"type": "keyword"},
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
                    "image_id": {"type": "keyword"},
                    "image_url": {"type": "keyword"},
                    "image_detail_url": {"type": "keyword"},
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
            "image_id": {"type": "keyword"},
            "image_url": {"type": "keyword"},
            "image_detail_url": {"type": "keyword"},
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


def referenced_image_ids(catalog: Catalog) -> set[str]:
    """Every image anything in the catalog points at, lines included.

    This is exactly the set of images the catalog needs to exist: one per
    product LINE, shared by that line's SKUs -- which is what a distributor's
    own listing does, several sizes of one end mill against one picture.
    """
    referenced = {line.image_id for line in catalog.lines}
    referenced.update(child.image_id for _, child in catalog.all_skus())
    return referenced - {""}
