"""What every table-driven type's test module asks of its build (#101).

A table type (:mod:`synthetic_ecommerce_data.catalog.tabletype`) states
its sizes, materials and packs, and declares a price ladder nobody measured.
So its gates are about ORDER and about the table, never about a price level:
each helper here takes the type's build and the table as the test module
restates it, and returns what is wrong plus how much it compared, so a gate
that compared nothing is red too.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence

from synthetic_ecommerce_data.catalog import brands, emit
from synthetic_ecommerce_data.catalog.config import GeneratorConfig
from synthetic_ecommerce_data.catalog.generate import generate
from synthetic_ecommerce_data.dimensions import parse_length
from synthetic_ecommerce_data.drawing import FIGURES, draw_sku
from synthetic_ecommerce_data.drawing.figures import Drawn

MM = 25.4
PACK = "Package Quantity"


def catalog(key: str, lines: int | None = None, defects: bool = False):
    """The type's own build; without the injected defects unless asked, so
    each value is the builder's."""
    config: dict = {} if defects else {"defect_scale": 0.0}
    if lines:
        config["lines"] = lines
    return generate(GeneratorConfig(**config), types=[key])


def docs(built) -> list[dict]:
    return [doc for line in built.lines for doc in emit.flat_documents(built, line)]


def values(doc: dict) -> dict[str, dict]:
    return {a["name"]: a for a in doc["attributes"]}


def row(doc: dict, columns: Sequence[str]) -> tuple[float, ...]:
    """A document's table row, in millimetres: ``value_canonical`` is
    millimetres whatever unit the value is written in."""
    published = values(doc)
    return tuple(round(float(published[name]["value_canonical"]), 3) for name in columns)


def price_order(
    documents: Sequence[dict], key: str, size: str, materials: Sequence[str]
) -> tuple[list[str], dict[str, int]]:
    """Where the build's prices break the three orders a table type promises,
    and how many pairs of each order it compared.

    Two documents are compared only at one brand tier and with every other
    term equal, so the pair differs in exactly the term under test.
    """
    cells: dict[tuple[str, str, int, float], set[float]] = defaultdict(set)
    for doc in documents:
        published = values(doc)
        cell = (
            brands.tier_of(doc["brand"], key),
            published["Material"]["value"],
            int(published[PACK]["value_canonical"]),
            round(float(published[size]["value_canonical"]), 3),
        )
        cells[cell].add(doc["price_usd"])
    wrong = [
        f"{cell} is priced {sorted(prices)}" for cell, prices in cells.items() if len(prices) > 1
    ]
    price = {cell: min(prices) for cell, prices in cells.items()}
    compared = {"size": 0, "material": 0, "pack": 0}

    def pairs(vary: int, order: Sequence):
        """Each two neighbouring cells that differ only at index ``vary``."""
        groups: dict[tuple, list[tuple]] = defaultdict(list)
        for cell in price:
            groups[cell[:vary] + cell[vary + 1 :]].append(cell)
        for group in groups.values():
            group.sort(key=lambda cell: order.index(cell[vary]))
            yield from zip(group, group[1:], strict=False)

    sizes = sorted({cell[3] for cell in price})
    packs = sorted({cell[2] for cell in price})
    for low, high in pairs(3, sizes):
        compared["size"] += 1
        if not price[low] < price[high]:
            wrong.append(f"larger costs no more: {low} {price[low]} vs {high} {price[high]}")
    for low, high in pairs(1, list(materials)):
        compared["material"] += 1
        if not price[low] < price[high]:
            wrong.append(
                f"dearer material costs no more: {low} {price[low]} vs {high} {price[high]}"
            )
    for low, high in pairs(2, packs):
        compared["pack"] += 1
        if not price[low] < price[high]:
            wrong.append(f"bigger pack costs no more: {low} {price[low]} vs {high} {price[high]}")
        if not price[low] / low[2] > price[high] / high[2]:
            wrong.append(
                f"bigger pack costs no less a piece: {low} {price[low]} vs {high} {price[high]}"
            )
    return wrong, compared


def drawings(
    built, key: str, columns: Sequence[str]
) -> dict[tuple[float, ...], tuple[Drawn, bytes]]:
    """One drawing per table row the build reaches: the figure, and the SVG in
    ONE brand's house style, so two rows' bytes differ only by their geometry."""
    figure, _ = FIGURES[key]
    drawn: dict[tuple[float, ...], tuple[Drawn, bytes]] = {}
    brand = built.lines[0].brand
    for line, child in built.all_skus():
        record: Mapping[str, str] = emit.drawing_record(built, line, child)
        size = tuple(round(parse_length(record[name]).inches * MM, 3) for name in columns)
        if size not in drawn:
            svg, _ = draw_sku(key, brand, record)
            drawn[size] = (figure(dict(record)), svg)
    return drawn
