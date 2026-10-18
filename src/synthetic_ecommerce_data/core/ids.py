"""Product id and SKU minting, domain-neutral (#128, blocker 5).

A domain mints its product ids and SKUs through an :class:`IdMinter` for each
product type, behind a per-domain prefix, so a second domain needs neither a
copy of the industrial generator's methods nor an import of the generator.

The prefix is what keeps ids unique across domains:

* A SKU is the prefix, then the type's ten-digit part number
  (:func:`.typespec.part_number`). Industrial SKUs are all digits, which is
  also what keeps them from wearing a reference SKU's code
  (``tests/test_catalog_noncopy.py``); a prefix is capital letters, so a
  prefixed SKU can never equal an unprefixed one.
* A product id is ``<brand code>-<series>-<block>-<index>``, with the prefix
  and a hyphen in front when the domain has one. Brand codes are three
  letters, a prefix is at most two, so the first field of a prefixed id can
  never be taken for an industrial brand code.

The industrial domain keeps the empty prefix, so its ids are the ones it
issued before this module existed.
"""

from __future__ import annotations

import re

from synthetic_ecommerce_data.core import typespec

#: A prefix is empty or one or two capital ASCII letters.
_PREFIX = re.compile(r"[A-Z]{0,2}")

#: The prefix each domain has claimed, by domain name (:func:`claim_prefix`).
PREFIXES: dict[str, str] = {}


def check_prefix(prefix: str) -> None:
    """Refuse a prefix that is not empty or one or two capital letters."""
    if not _PREFIX.fullmatch(prefix):
        raise ValueError(
            f"id prefix {prefix!r} must be empty or one or two capital letters A-Z: "
            "a digit would read as a part number and a third letter as a brand code"
        )


def claim_prefix(domain: str, prefix: str) -> None:
    """Record that ``domain`` mints with ``prefix``; refuse a prefix another domain holds.

    The same domain claiming the same prefix again is a no-op, so a module
    that is imported twice does not refuse itself.
    """
    check_prefix(prefix)
    for other, held in PREFIXES.items():
        if held == prefix and other != domain:
            raise ValueError(
                f"id prefix {prefix!r} is held by domain {other!r}; "
                f"domain {domain!r} needs its own"
            )
    if PREFIXES.setdefault(domain, prefix) != prefix:
        raise ValueError(
            f"domain {domain!r} already mints with prefix {PREFIXES[domain]!r}, not {prefix!r}"
        )


class IdMinter:
    """One type's product ids and SKUs, behind a per-domain prefix.

    ``block`` is the type's part-number block (:func:`.typespec.block_of`), which
    leads every SKU and product id the type issues. State is per minter: the
    SKU sequence and the product index each start at one.
    """

    def __init__(self, prefix: str, type_key: str, block: int) -> None:
        check_prefix(prefix)
        self.prefix = prefix
        self.type_key = type_key
        self.block = block
        self._sequence = 0
        self._index = 0
        self._used_skus: set[str] = set()

    def next_index(self) -> int:
        """The type's next product index; every draft takes one, made or not."""
        self._index += 1
        return self._index

    def new_sku(self) -> str:
        """The type's next SKU: the prefix, its block, then a scrambled sequence.

        Unique by construction rather than by retrying a random draw: a draw
        checked against every SKU issued so far couples each type to all the
        others.
        """
        self._sequence += 1
        sku = self.prefix + typespec.part_number(self.block, self._sequence)
        if sku in self._used_skus:  # pragma: no cover - the stride is coprime to 10**6
            raise RuntimeError(f"{self.type_key} issued part number {sku} twice")
        self._used_skus.add(sku)
        return sku

    def product_id(self, brand_code: str, series: str, index: int) -> str:
        """``<brand code>-<series>-<block>-<index>``: unique because the block is."""
        lead = f"{self.prefix}-" if self.prefix else ""
        return f"{lead}{brand_code}-{series}-{self.block:04d}-{index:04d}"
