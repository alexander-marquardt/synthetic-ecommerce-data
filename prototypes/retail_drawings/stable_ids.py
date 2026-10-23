"""Product ids and SKUs that name what a product is, not where it sits (gen#626).

A partial reload writes a SKU as the Elasticsearch ``_id``. A SKU numbered by its row position
moves when a row is added before it, and then overwrites another product on the next load. So:

- :func:`sku_id` is ``<product id>-<hash of the SKU's own axes>``: its size, color and the other
  values that tell one SKU of a product from another. The price, the stock flag and the
  ingredient lists are what a SKU has, not what it is (:data:`NOT_AXES`), so a repricing keeps
  the SKU.
- :func:`style_id` is the id of a style derived from a template: the department prefix and a
  hash of the template's id and the signature (shown values and hero color family) that tells the
  style from its siblings, so it does not depend on how many styles were drawn before it.
- :func:`digest` and :func:`pick` are the seeded draws the build makes from such an identity: a
  hash, not a shared random stream, so a draw does not depend on the draws made before it.

A collision is an error, never resolved by bumping a counter: the second id would depend on the
first, and the order is exactly what this module takes away (:class:`IdCollision`).
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

#: SKU keys that are not part of the SKU's identity: changing one leaves the SKU the same SKU.
NOT_AXES = frozenset(
    {"sku", "price", "in_stock", "ingredients", "contains", "may_contain", "dietary"}
)

#: Hex characters of a SKU's axes hash: 16**8 values, against a few hundred SKUs per product.
SKU_HEX = 8
#: Hex characters of a derived style's hash: 16**12 values, against about 10**5 styles.
STYLE_HEX = 12


class IdCollision(ValueError):
    """Two products, or two SKUs, were given one id."""


def digest(*parts: Any) -> str:
    """A stable hex digest of ``parts`` (the same on every run and machine)."""
    text = json.dumps(parts, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def number(*parts: Any) -> int:
    """:func:`digest` as an integer: a seed, or a rank."""
    return int(digest(*parts), 16)


def unit(*parts: Any) -> float:
    """A hash of ``parts`` as a number in (0, 1]."""
    return (number(*parts) % 2**53 + 1) / 2**53


def pick(options: list, *parts: Any) -> Any:
    """The option whose hash with ``parts`` is highest (rendezvous hashing): adding an option
    changes the pick only when it is the new highest, so a bigger pool moves few draws."""
    return max(options, key=lambda o: number(*parts, o))


def axes(sku: dict) -> dict:
    """What tells ``sku`` from the other SKUs of its product."""
    return {k: v for k, v in sku.items() if k not in NOT_AXES}


def sku_id(product_id: str, sku: dict) -> str:
    """``<product id>-<hash of the SKU's axes>``, the same whatever row the SKU sits in."""
    return f"{product_id}-{digest(axes(sku))[:SKU_HEX].upper()}"


def style_id(prefix: str, *identity: Any) -> str:
    """``<prefix>-<hash of the identity>`` for a style derived from a template."""
    return f"{prefix}-{digest(*identity)[:STYLE_HEX].upper()}"


def check_skus(product_id: str, skus: list[dict]) -> None:
    """Raise :class:`IdCollision` when two SKUs of one product have one id."""
    seen: dict[str, dict] = {}
    for s in skus:
        if s["sku"] in seen:
            raise IdCollision(
                f"{product_id}: two SKUs are {s['sku']} ({axes(seen[s['sku']])} and {axes(s)}): "
                "give them an axis that tells them apart; the id is never bumped to fit"
            )
        seen[s["sku"]] = s


def check_unique(docs: list[dict]) -> None:
    """Raise :class:`IdCollision` when two documents share a product id or a SKU."""
    products: set[str] = set()
    skus: dict[str, str] = {}
    for d in docs:
        pid = d["product_id"]
        if pid in products:
            raise IdCollision(f"{pid} is built twice: give one of the two another identity")
        products.add(pid)
        for s in d.get("skus", ()):
            if s["sku"] in skus:
                raise IdCollision(
                    f"SKU {s['sku']} is on {skus[s['sku']]} and on {pid}: a SKU names one product"
                )
            skus[s["sku"]] = pid
