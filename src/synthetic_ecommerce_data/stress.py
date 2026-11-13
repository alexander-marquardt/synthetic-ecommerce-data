"""The stress catalog: every product's attributes copied under fixed numbered names (gen#948).

    ecom-generate build --stress-keys 50000 --stress-copies 3 --out out/stress

It shows that PRISM's attribute code works at 10K-50K attribute keys, each with several values.
The products do not need to be realistic for that. The expansion runs on each finished product
document, and is off unless ``--stress-keys`` is given:

1. **Fixed names.** Each base attribute has C numbered copies, ``color_0001`` ... ``color_<C>``.
   C is the key target divided by the number of base attributes in the catalog
   (:func:`copies_per_attribute`).
2. **Up to N copies per product.** For each attribute a product has, the original stays, and
   1 to N copies (``--stress-copies``) are added, their numbers drawn from 1..C.
3. **Values come from the product itself.** Each copy holds a random subset of the product's
   own entries for the base attribute (at least one), with the same unit. A key a variant
   states (a SKU's diameter) gets its copies on the variant, from that variant's entries.
4. **Reproducible.** Every draw comes from an RNG seeded by the product id, so two runs give
   the same output and a product can be expanded without the others.

With ``--stress-keys`` off the build is byte-identical to the standard one. With it on, the
build writes only the stress files (:func:`write`), into a directory that holds no standard
build.

It streams like the standard build (gen#952). C needs every base key in the catalog before the
first product is expanded, so the build writes each type's nested documents to a spool file
(:func:`spool`) and keeps only the keys. :func:`write` then reads the spool one document at a
time, expands it, writes its nested and flat lines and counts it in the census before it reads
the next. No list of documents is kept, so the peak does not grow with the catalog.

No category rules, frequency weighting, hashing, word lists or pathological variant
(the maintainer, 2026-11-12). See docs/stress-catalog.md.
"""

from __future__ import annotations

import json
import random
from collections.abc import Iterable, Iterator, Mapping
from pathlib import Path
from typing import Any, TextIO

from synthetic_ecommerce_data.core import emit, standard

#: The census of the written stress catalog.
CENSUS = "stress.json"
#: The standard nested documents, one per line, waiting to be expanded: the build writes it
#: into its staging directory and :func:`write` deletes it once it has read it.
SPOOL = "stress-spool.nested.jsonl"
#: A key on fewer products than this is counted, so a run shows whether C is too high for the
#: product count.
THIN_PRODUCTS = 5


def copy_key(key: str, number: int) -> str:
    """The fixed name of copy ``number`` of ``key``: ``color_0001``."""
    return f"{key}_{number:04d}"


def base_keys(docs: Iterable[Mapping[str, Any]]) -> list[str]:
    """Every attribute key the nested documents carry, product or variant, sorted."""
    return sorted({entry["key"] for doc in docs for entry in _entries(doc)})


def copies_per_attribute(target_keys: int, bases: int) -> int:
    """C: the key target shared over the base attributes, at least one copy each."""
    return max(1, target_keys // max(1, bases))


def expand_product(doc: Mapping[str, Any], copies: int, max_copies: int) -> dict[str, Any]:
    """``doc`` with up to ``max_copies`` numbered copies of each of its attributes.

    ``copies`` is C, the highest copy number. The originals stay where they are; each list of
    entries (the product's, each variant's) gets its copies after them. One base key takes the
    same copy numbers on the product and on every variant, so a SKU's flat document holds each
    copy once, as it holds the base.
    """
    rng = random.Random(f"stress:{doc['product_id']}")
    numbers: dict[str, list[int]] = {}
    for key in dict.fromkeys(entry["key"] for entry in _entries(doc)):
        count = min(copies, rng.randint(1, max_copies))
        numbers[key] = sorted(rng.sample(range(1, copies + 1), count))
    out = dict(doc)
    out["attributes"] = _with_copies(doc["attributes"], numbers, rng)
    out["variants"] = [
        dict(variant, attributes=_with_copies(variant["attributes"], numbers, rng))
        for variant in doc["variants"]
    ]
    return out


def _entries(doc: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [*doc["attributes"], *(e for variant in doc["variants"] for e in variant["attributes"])]


def _with_copies(
    entries: list[dict[str, Any]], numbers: Mapping[str, list[int]], rng: random.Random
) -> list[dict[str, Any]]:
    out = list(entries)
    for key in dict.fromkeys(entry["key"] for entry in entries):
        own = [entry for entry in entries if entry["key"] == key]
        for number in numbers[key]:
            picked = sorted(rng.sample(range(len(own)), rng.randint(1, len(own))))
            out.extend(
                dict(own[i], key=copy_key(key, number), name=f"{own[i]['name']} {number:04d}")
                for i in picked
            )
    return out


def _percentiles(counts: list[int]) -> dict[str, int]:
    """Nearest-rank min, p50, p90, p99 and max of ``counts`` (zeros when empty)."""
    ranked = sorted(counts) or [0]

    def rank(p: int) -> int:
        return ranked[max(0, -(-p * len(ranked) // 100) - 1)]

    return {"min": ranked[0], "p50": rank(50), "p90": rank(90), "p99": rank(99), "max": ranked[-1]}


class Census:
    """The census, counted one document at a time: per key, the products that carry it and the
    distinct values it takes. Nothing of a document is kept but its keys and values."""

    def __init__(self) -> None:
        self.products = 0
        self.carriers: dict[str, int] = {}
        self.values: dict[str, set[str]] = {}

    def add(self, doc: Mapping[str, Any]) -> None:
        self.products += 1
        for key in {entry["key"] for entry in _entries(doc)}:
            self.carriers[key] = self.carriers.get(key, 0) + 1
        for entry in _entries(doc):
            self.values.setdefault(entry["key"], set()).add(str(entry["value"]))

    def result(self) -> dict[str, Any]:
        return {
            "products": self.products,
            "distinct_keys": len(self.carriers),
            "products_per_key": _percentiles(list(self.carriers.values())),
            "values_per_key": _percentiles([len(seen) for seen in self.values.values()]),
            f"keys_on_fewer_than_{THIN_PRODUCTS}_products": sum(
                1 for count in self.carriers.values() if count < THIN_PRODUCTS
            ),
        }


def census(docs: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Products, distinct keys, products per key and distinct values per key, of nested docs."""
    tally = Census()
    for doc in docs:
        tally.add(doc)
    return tally.result()


def census_lines(figures: Mapping[str, Any]) -> list[str]:
    """The census as the build prints it."""

    def row(spread: Mapping[str, int]) -> str:
        return "  ".join(f"{name} {value}" for name, value in spread.items())

    thin = figures[f"keys_on_fewer_than_{THIN_PRODUCTS}_products"]
    return [
        f"stress catalog: {figures['products']} products, {figures['distinct_keys']} distinct keys",
        f"products per key: {row(figures['products_per_key'])}",
        f"values per key:   {row(figures['values_per_key'])}",
        f"keys on fewer than {THIN_PRODUCTS} products: {thin} of {figures['distinct_keys']}"
        + ("  (lower --stress-keys for this product count)" if thin else ""),
    ]


def spool(docs: Iterable[Mapping[str, Any]], handle: TextIO, keys: set[str]) -> None:
    """Write each standard nested document to the open spool ``handle`` and add its attribute
    keys, product or variant, to ``keys``: the build calls it once per type (gen#952)."""
    for doc in docs:
        keys.update(entry["key"] for entry in _entries(doc))
        handle.write(json.dumps(doc, ensure_ascii=False) + "\n")


def _spooled(path: Path) -> Iterator[dict[str, Any]]:
    with path.open(encoding="utf-8") as lines:
        for line in lines:
            yield json.loads(line)


def write(
    out: Path,
    bases: Iterable[str],
    target_keys: int,
    max_copies: int,
    mappings: Mapping[str, Any],
) -> list[str]:
    """Expand the documents spooled in ``out`` (:data:`SPOOL`) and write the stress catalog into
    ``out``; return the lines to print. ``bases`` is every base key the spooled documents carry.

    ``out`` gets ``nested.jsonl``, ``flat.jsonl`` (each SKU's flat document, from the expanded
    nested one by :func:`.core.standard.flat_documents`), the ``mappings`` and :data:`CENSUS`,
    and loses the spool. No ``images.jsonl``: a stress document keeps its standard image ids, so
    the standard catalog's image bundle serves it.

    One document at a time: each is read, expanded, written to both files and counted before the
    next is read, so nothing that grows with the catalog is held but the census (gen#952).
    """
    bases = sorted(set(bases))
    copies = copies_per_attribute(target_keys, len(bases))
    tally = Census()
    with (
        (out / "nested.jsonl").open("w", encoding="utf-8") as nested,
        (out / "flat.jsonl").open("w", encoding="utf-8") as flat,
    ):
        for doc in _spooled(out / SPOOL):
            expanded = expand_product(doc, copies, max_copies)
            emit.append_jsonl((expanded,), nested)
            emit.append_jsonl(standard.flat_documents(expanded), flat)
            tally.add(expanded)
    (out / SPOOL).unlink()
    for name, mapping in mappings.items():
        (out / name).write_text(json.dumps(mapping, indent=1) + "\n", encoding="utf-8")
    figures = tally.result()
    config = {"target_keys": target_keys, "max_copies": max_copies}
    config |= {"base_keys": len(bases), "copies_per_attribute": copies}
    (out / CENSUS).write_text(
        json.dumps({"config": config, "census": figures}, indent=1) + "\n", encoding="utf-8"
    )
    return [
        f"stress catalog: {len(bases)} base keys x up to {max_copies} of "
        f"{copies} numbered copies each (--stress-keys {target_keys})",
        *census_lines(figures),
    ]
