"""The non-copying guarantee, enforced rather than asserted.

The README promises: *no generated record may match a reference record on its
full attribute tuple, and the test suite checks it.* This module is the check.

**Why the full tuple, and not field by field.** A generated ``#10-32`` flat
head cap screw publishes ``Head Dia. = 0.411 in``, and so does every real one,
because that is what ASME B18.3.2 says a ``#10`` flat head is. Field-by-field
comparison would flag that as copying, and it is not: reproducing a dimension
fixed by a public standard is reproducing a fact about the physical world.
What would be copying is reproducing the *compilation* -- the particular
assembly of brand, series, finish, dimensions and inconsistencies that a
catalog editor put together. That assembly is exactly what a full attribute
tuple is, so that is what gets compared.

**Why hashes.** The reference corpus is someone else's compilation and never
ships. A hash of a tuple is not the tuple: it cannot be read back, it
redistributes no attribute value, and it still proves the property. The SKU
list is a different kind of thing -- bare identifiers with no catalog content
-- and ships in the clear so the generator can refuse to mint a code that
collides with a real archived one.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from functools import lru_cache
from importlib import resources

from .model import Attribute


@lru_cache(maxsize=1)
def _load() -> dict:
    text = (
        resources.files("synthetic_industrial_products.data")
        .joinpath("reference_fingerprints.json")
        .read_text("utf-8")
    )
    return json.loads(text)


@lru_cache(maxsize=1)
def reference_tuple_hashes() -> frozenset[str]:
    return frozenset(_load()["tuple_hashes"])


@lru_cache(maxsize=1)
def reference_dimension_hashes() -> frozenset[str]:
    return frozenset(_load()["dimension_tuple_hashes"])


@lru_cache(maxsize=1)
def _reference_skus() -> frozenset[str]:
    return frozenset(_load()["skus"])


#: Every SKU code the reference corpus published under. The generator checks
#: new codes against this so a synthetic item can never wear a real one's
#: number.
REFERENCE_SKUS: frozenset[str] = _reference_skus()


def pairs_of(attributes: Iterable[Attribute]) -> list[tuple[str, str]]:
    """The (name, value) pairs of an attribute set, multi-values expanded.

    A multi-valued attribute contributes one pair per value, so two records
    that publish the same standards in a different order still compare equal
    -- which is what "the same tuple" has to mean.
    """
    pairs: list[tuple[str, str]] = []
    for attribute in attributes:
        if attribute.values is not None:
            pairs.extend((attribute.name, value) for value in attribute.values)
        else:
            pairs.append((attribute.name, attribute.value))
    return sorted(pairs)


def fingerprint(attributes: Iterable[Attribute]) -> str:
    """The same hash the reference fingerprints were built with."""
    canonical = json.dumps(pairs_of(attributes), separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def fingerprint_mapping(attributes: dict[str, str]) -> str:
    """Fingerprint a plain name -> value mapping, as the builder script does."""
    pairs = sorted(
        (str(name), str(value)) for name, value in attributes.items() if name not in ("sku", "SKU")
    )
    canonical = json.dumps(pairs, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def matches_reference(attributes: Iterable[Attribute]) -> bool:
    return fingerprint(attributes) in reference_tuple_hashes()


def dimension_fingerprint(values: Iterable[str]) -> str:
    canonical = json.dumps([str(v) for v in values], separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def audit(catalog) -> dict:
    """Every way this catalog could be said to have copied, counted.

    Returns the collisions found rather than raising, so a caller can report
    the numbers; the test is what turns a non-zero count into a failure.
    """
    tuple_hits: list[str] = []
    sku_hits: list[str] = []
    dimension_hits: list[str] = []
    reference_tuples = reference_tuple_hashes()
    reference_dimensions = reference_dimension_hashes()

    for line, child in catalog.all_skus():
        merged = catalog.merged_attributes(line, child)
        if fingerprint(merged) in reference_tuples:
            tuple_hits.append(child.sku)
        if child.sku in REFERENCE_SKUS:
            sku_hits.append(child.sku)

        by_name = {a.name: a.value for a in merged}
        quad = (
            by_name.get("Milling Dia."),
            by_name.get("Length of Cut"),
            by_name.get("Overall Length"),
            by_name.get("Shank Dia."),
        )
        if all(quad) and dimension_fingerprint([v for v in quad if v]) in reference_dimensions:
            dimension_hits.append(child.sku)

    return {
        "n_skus_checked": catalog.sku_count,
        "full_tuple_collisions": tuple_hits,
        "sku_collisions": sku_hits,
        "verbatim_dimension_tuple_collisions": dimension_hits,
        "n_reference_tuples": len(reference_tuples),
        "n_reference_skus": len(REFERENCE_SKUS),
    }
