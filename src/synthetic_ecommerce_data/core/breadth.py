"""The breadth table: one plain row per cheap category, read from a directory of YAML files.

The domain-neutral half of catalog breadth (#34, moved here by #125 step 2):
what a row holds (:class:`BreadthRow`) and how a table of row files is read
(:func:`read_rows`). A domain owns its own rows and the loop that turns a row
into a product line; the industrial domain's are in
``domains/industrial/breadth.py`` and ``domains/industrial/data/breadth_categories/``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from importlib.resources.abc import Traversable
from typing import Any

import yaml

from synthetic_ecommerce_data.core import typespec


@dataclass(frozen=True)
class BreadthRow:
    """One row: one file of a domain's breadth table."""

    key: str
    category: tuple[str, ...]
    family: str
    shape: str
    item: str
    size_attr: str
    size_values: tuple[str, ...]
    attributes: dict[str, tuple[str, ...]]
    skus: int
    reason: str
    #: This row's own price band in USD, ``(min, max)``, drawn from general
    #: knowledge of the category (alexander-marquardt/synthetic-ecommerce-data#37),
    #: for a row the price census did not measure. A measured row
    #: (``price.BREADTH_CENSUS``) declares none: it is priced from the census
    #: (:func:`.price.breadth_price`). ``min`` must be positive and strictly
    #: less than ``max``, held by ``tests/test_breadth.py``.
    price_range: tuple[float, float] | None = None
    descriptor_attr: str | None = None
    #: Size values ``reason`` names explicitly (quoted, before any "overlap"
    #: clause) -- these MUST appear among the row's SKUs; a plain rotation
    #: from index 0 cannot promise that (#35 review). Any SKU slots beyond
    #: these still come from :meth:`~.generate.Generator._rotate` over the
    #: remaining, non-featured values, so a row with no cited size keeps its
    #: old rotating behaviour untouched.
    featured_sizes: tuple[str, ...] = ()
    #: Line attribute VALUES ``reason`` names explicitly (e.g. a material the
    #: cited query names) -- fixed rather than drawn by ``rng.choice``, which
    #: otherwise misses the cited value some of the time. Keyed by attribute
    #: name; an attribute absent here is still drawn randomly, unchanged.
    featured_attrs: dict[str, str] = field(default_factory=dict)
    #: Set only when the block derived from ``key`` is another type's too
    #: (:func:`.typespec.check_collisions` names both); otherwise derived.
    part_number_block: int | None = None


def declared_block(raw: dict[str, Any], table: str) -> int | None:
    """The row's ``part_number_block:``, refused by row unless an unquoted integer.

    A quoted ``'4659'`` would otherwise reach the collision check as a string
    and fail there as a bare ``TypeError`` naming no row. ``table`` is the
    table's path as a refusal names it.
    """
    block = raw.get("part_number_block")
    if block is None or (isinstance(block, int) and not isinstance(block, bool)):
        return block
    raise typespec.TypeCollisionError(
        f"{table}/{raw['key']}.yaml declares part_number_block: {block!r}; "
        "write it as an unquoted four-digit integer"
    )


def row_from_dict(raw: dict[str, Any], table: str) -> BreadthRow:
    return BreadthRow(
        key=raw["key"],
        category=tuple(raw["category"]),
        family=raw["family"],
        shape=raw["shape"],
        item=raw["item"],
        size_attr=raw["size_attr"],
        size_values=tuple(raw["size_values"]),
        attributes={name: tuple(values) for name, values in raw["attributes"].items()},
        skus=int(raw["skus"]),
        reason=raw["reason"],
        price_range=(
            tuple(float(v) for v in raw["price_range"])  # type: ignore[assignment]
            if "price_range" in raw
            else None
        ),
        descriptor_attr=raw.get("descriptor_attr"),
        featured_sizes=tuple(raw.get("featured_sizes") or ()),
        featured_attrs=dict(raw.get("featured_attrs") or {}),
        part_number_block=declared_block(raw, table),
    )


def read_rows(directory: Traversable, table: str) -> tuple[BreadthRow, ...]:
    """Every row file in ``directory``, in file-name order; a file named for another key is refused.

    ``table`` is the directory's path as every refusal names it. The name check
    keeps ``<table>/<key>.yaml`` true as the path of ``key``'s row.
    """
    files = sorted(
        (entry for entry in directory.iterdir() if entry.name.endswith(".yaml")),
        key=lambda entry: entry.name,
    )
    rows = []
    for entry in files:
        raw = yaml.safe_load(entry.read_text("utf-8"))
        if f"{raw['key']}.yaml" != entry.name:
            raise ValueError(f"{table}/{entry.name} holds the row for {raw['key']!r}")
        rows.append(row_from_dict(raw, table))
    return tuple(rows)
