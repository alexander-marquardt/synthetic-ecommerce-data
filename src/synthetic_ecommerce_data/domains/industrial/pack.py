"""The PACKAGE-QUANTITY axis (#14): a line's second variant dimension, commercial, not physical.

One line sells a run of sizes at several pack quantities, and each (size, quantity) pair that
exists is a child SKU with its own price, title and card. Rulings on #14, 2026-09-18:

* **The matrix is SPARSE.** Quantity 1 offers every size and each larger quantity about half the
  sizes of the one before (:func:`offered`), as a listing offers eight sizes singly and two as a
  5-pack. A cross product would invent SKUs that do not exist.
* **The price is a discount, not a multiple** (:func:`.price.pack_price`).
* **The title leads with the count** above 1: ``5PCS ...``.
* **The card is per pair and the detail per item.** A pack's card draws N items fanned, and its
  ``image_detail_url`` is its size's single-unit SKU's drawing: a five-pack's specifications are
  one unit's, so nothing renders a dimensioned five-up.

This is not the ``Units per Pack`` a bolt publishes. There the pack is how one SKU's price is
quoted, and the SKU has no sibling at another quantity.

End mills take the axis on products of their own, ADDED after every other pass (as
:mod:`.grouped` does), so no SKU those passes build moves. The ear plug's one breadth line takes
it in place: that row's prices are boxed prices, so its singles are read back down the curve.
"""

from __future__ import annotations

import math
import random
import statistics
from collections.abc import Callable
from dataclasses import replace

from synthetic_ecommerce_data.core import price
from synthetic_ecommerce_data.core.model import (
    Attribute,
    ProductLine,
    Sku,
    numeric_attribute,
    pricing_unit_for,
)
from synthetic_ecommerce_data.domains.industrial.part_numbers import mfr_part_number
from synthetic_ecommerce_data.domains.industrial.taxonomy import image_id_for

#: Each type's quantities above 1, smallest first.
AXES: dict[str, tuple[int, ...]] = {
    "end_mill_square": (2, 5, 10),
    "end_mill_ball": (2, 5, 10),
    # Not 100: a fan of a hundred outlines inks over into a solid wedge, and N must be seen.
    "foam_ear_plugs": (10, 25, 50),
}

#: The quantity a type's drawn price is for, where it is not 1: the ear plug row's census prices
#: are boxed prices, around a box of 50.
PRICED_AT: dict[str, int] = {"foam_ear_plugs": 50}

#: The pack products of a modelled type, as a share of the products it already had.
SHARE = 0.03

#: The longest title, as :func:`.naming.build_title` caps one: a pack sheds a whole last segment.
TITLE_CAP = 100

#: The fewest sizes a line needs for its matrix to have a row to thin.
MIN_SIZES = 2


def offered(sizes: int, row: int) -> int:
    """How many of a line's ``sizes`` the ``row``-th quantity above 1 offers: half the last row."""
    return max(1, math.ceil(sizes / 2 ** (row + 1)))


def pairs(sizes: int, quantities: tuple[int, ...]) -> int:
    """The SKUs of a line of ``sizes`` sizes: every single, and each quantity's :func:`offered`."""
    return sizes + sum(offered(sizes, row) for row in range(len(quantities)))


def _attribute(quantity: int) -> Attribute:
    return numeric_attribute("Units per Pack", str(quantity), float(quantity))


def _per_pack(quantity: int) -> str:
    return f" {quantity} per pack."


def _brand_line(line: ProductLine, child: Sku) -> str:
    """What a description ends with (#937): ``<brand> <line> <mfr part number>``."""
    return f"{line.brand} {line.series} {child.mfr_part_number}"


def _details(line: ProductLine, child: Sku) -> str:
    """A description's remaining attributes, between ``<title> - `` and the brand line: empty,
    or ending with ``", "``."""
    return child.description.removeprefix(f"{child.title} - ").removesuffix(
        _brand_line(line, child)
    )


def _described(line: ProductLine, child: Sku, title: str, details: str, quantity: int) -> str:
    """``<title> - <attrs>, <quantity> Units per Pack, <brand> <line> <mfr part number>``."""
    return f"{title} - {details}{quantity} Units per Pack, {_brand_line(line, child)}"


def _pack(
    line: ProductLine,
    single: Sku,
    quantity: int,
    sku: str,
    rng: random.Random,
    seed: int,
) -> Sku:
    """The child SKU that sells ``quantity`` of ``single``: its size, a pack's copy and price."""
    lead = f"{quantity}PCS "
    title = single.title
    while len(lead + title) > TITLE_CAP and ", " in title:
        title = title.rsplit(", ", 1)[0]
    stock = (0, rng.randint(1, 40), rng.randint(40, 900))
    part = replace(single, mfr_part_number=mfr_part_number(seed, line.series, sku))
    details = _details(line, single).removesuffix("1 Units per Pack, ")
    return replace(
        part,
        sku=sku,
        title=lead + title,
        description=_described(line, part, lead + title, details, quantity),
        copy=single.copy[: -len(_per_pack(1))] + _per_pack(quantity),
        attributes=(*single.attributes[:-1], _attribute(quantity)),
        price_usd=price.pack_price(single.price_usd, quantity, price.ending_draw(seed, sku)),
        stock=rng.choices(stock, weights=(0.08, 0.42, 0.5))[0],
        image_id=image_id_for(line.type_key, line.product_id, sku),
        detail_image_id=single.image_id,
        pricing_unit=pricing_unit_for(str(quantity)),
    )


def _unit_price(line: ProductLine, child: Sku, seed: int) -> float:
    """What one of ``child`` costs. A row with :data:`PRICED_AT` reads it down the curve from the
    mean of its sizes: it spreads its census range over them, which a Corded and an Uncorded
    plug do not earn."""
    priced_at = PRICED_AT.get(line.type_key)
    if priced_at is None:
        return child.price_usd
    boxed = statistics.geometric_mean(c.price_usd for c in line.children)
    return price.pack_price(boxed, 1 / priced_at, price.ending_draw(seed, child.sku))


def widen(
    line: ProductLine, new_sku: Callable[[], str], rng: random.Random, seed: int
) -> ProductLine:
    """``line`` with its SKUs as the singles, and a child for each pair its matrix offers."""
    singles = [
        replace(
            child,
            attributes=(*child.attributes, _attribute(1)),
            description=_described(line, child, child.title, _details(line, child), 1),
            copy=child.copy + _per_pack(1),
            price_usd=_unit_price(line, child, seed),
        )
        for child in line.children
    ]
    packs: list[Sku] = []
    for row, quantity in enumerate(AXES[line.type_key]):
        keep = offered(len(singles), row)
        start = rng.randrange(len(singles) - keep + 1)
        for single in singles[start : start + keep]:
            packs.append(_pack(line, single, quantity, new_sku(), rng, seed))
    return replace(line, children=(*singles, *packs))
