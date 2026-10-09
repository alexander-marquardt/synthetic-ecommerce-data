"""Table-driven (light) types (#101): a modelled type stated as a table.

A type whose spec space is hard to generalise does not get a parametric
generator. Its module states a short table of real sizes, each with the
dimensions a published chart gives it, a few materials and the packs it is
sold in; :func:`spec` turns that :class:`TableType` into an ordinary modelled
:class:`.typespec.TypeSpec`. Nothing downstream can tell the difference: the
records go through the same builder post-pass, emit, unit handling and
drawing bundle as every modelled type's.

**Price.** A declared base and ladder, with no noise: the base is one pack
(the first of ``packs``) of the first row in the first material at the
standard brand tier; a larger size costs more (``size_slope``), a material
costs its declared ``factor``, and a larger pack costs more in total but less
per piece (``0 < pack_slope < 1``). It is declared ``measured=False``. A table
type has no ``price.CENSUS`` entry and borrows no model, so no census row
scores it: there is nothing measured to score it against.

**Drawing.** One function per type, ``draw(values)``, where ``values`` maps
each column to the SKU's own published length in inches (:func:`lengths`).
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.drawing.model import Figure
from synthetic_ecommerce_data.core.model import keyword_attribute, numeric_attribute
from synthetic_ecommerce_data.core.price import PriceModel
from synthetic_ecommerce_data.core.typespec import TypeSpec, discover
from synthetic_ecommerce_data.domains.industrial.drawing.figures import Drawn
from synthetic_ecommerce_data.domains.industrial.newtypes import (
    MM_PER_INCH,
    _window,
    table_provenance,
)
from synthetic_ecommerce_data.domains.industrial.vocab import AttrSpec

#: The attribute a pack is published under, as the census names it.
PACK = "Package Quantity"
#: A table price is shown as computed, to the cent: the census ending classes
#: (.99, .00) move a price by up to a quarter, which would reorder a ladder.
ENDINGS = {"other": 1.0}
#: See ``make``.
STRIDE = 5
#: The table behind each type key, as its type module first stated it. Kept by
#: key and not by the ``make`` handed out: a type that adds its own attributes
#: wraps that ``make``, and is a table type all the same. The first one stays,
#: because a variation on a table is built from one already stated.
_MADE: dict[str, TableType] = {}


@dataclass(frozen=True)
class Variant:
    """One material the type is sold in, its finish, and its price factor
    over the first variant's."""

    material: str
    finish: str
    factor: float


@dataclass(frozen=True)
class TableType:
    key: str
    category: tuple[str, ...]
    item: str
    standards_family: str
    #: The standard whose table the cited chart reproduces. It is what the
    #: provenance names and the one standard a record may claim.
    standard: str
    #: The published attribute of each column of ``rows``. The first is the
    #: size: the key dimension, which must rise down the table.
    columns: tuple[str, ...]
    #: One real size per row, in ``unit``.
    rows: tuple[tuple[float, ...], ...]
    variants: tuple[Variant, ...]
    packs: tuple[int, ...]
    #: USD: see the module docstring.
    base_price: float
    size_slope: float
    pack_slope: float
    #: ``draw(values)`` and the largest box it draws (docs/adding-a-type.md).
    draw: Callable[[Mapping[str, float]], Figure]
    extent: tuple[float, float]
    share: float
    series: str
    use_lines: tuple[str, ...] = ()
    unit: str = "mm"

    @property
    def per_inch(self) -> float:
        return MM_PER_INCH if self.unit == "mm" else 1.0

    @property
    def cells(self) -> int:
        """How many different products the table holds: a size in a material
        in a pack."""
        return len(self.rows) * len(self.variants) * len(self.packs)

    def inches(self, row: tuple[float, ...]) -> dict[str, float]:
        return {name: value / self.per_inch for name, value in zip(self.columns, row, strict=True)}

    @property
    def provenance(self) -> str:
        return table_provenance(*((name, self.standard) for name in self.columns))

    @property
    def price(self) -> PriceModel:
        return PriceModel(
            anchor=self.base_price,
            anchor_key=self.rows[0][0] / self.per_inch,
            slope=self.size_slope,
            group_sigma=0.0,
            sku_sigma=0.0,
            endings=ENDINGS,
            pack_attribute=PACK,
            pack_slope=self.pack_slope,
            pack_ref=float(self.packs[0]),
            measured=False,
            materials={v.material: v.factor for v in self.variants},
        )


def problems(table: TableType) -> list[str]:
    """What is wrong with a table, so :func:`spec` refuses it at import."""
    sizes = [row[0] for row in table.rows]
    factors = [v.factor for v in table.variants]
    checks = (
        (all(len(row) == len(table.columns) for row in table.rows), "a row misses a column"),
        (sizes == sorted(set(sizes)) and sizes[0] > 0, "the sizes do not rise down the table"),
        (len({v.material for v in table.variants}) == len(factors), "a material is listed twice"),
        (factors == sorted(factors) and factors[0] == 1.0, "the factors do not rise from 1.0"),
        (list(table.packs) == sorted(set(table.packs)), "the packs do not rise"),
        (table.size_slope > 0, "size_slope is not positive: a larger size must cost more"),
        (0 < table.pack_slope < 1, "pack_slope is not between 0 and 1: a piece must cost less"),
        (table.base_price > 0, "base_price is not positive"),
        (table.unit in ("mm", "in"), "unit is neither mm nor in"),
    )  # fmt: skip
    return [message for ok, message in checks if not ok]


def lengths(table: TableType, record: Mapping[str, str]) -> tuple[dict[str, float], str]:
    """Each column's length in inches for one SKU, and how much of it is the
    record's own (``record``, ``partial`` or ``nominal``, as
    :class:`.figures.Drawn` means them).

    A column the record does not publish takes the proportion of the table
    row nearest the SKU's size; a SKU with no readable size is drawn as the
    middle row.
    """
    own: dict[str, float] = {}
    for name in table.columns:
        try:
            own[name] = parse_length(record[name]).inches
        except (KeyError, DimensionParseError):
            continue
    size_name = table.columns[0]
    if size_name not in own:
        return table.inches(table.rows[len(table.rows) // 2]), "nominal"
    if len(own) == len(table.columns):
        return own, "record"
    size = own[size_name]
    nearest = table.inches(min(table.rows, key=lambda row: abs(row[0] / table.per_inch - size)))
    scale = size / nearest[size_name]
    return {name: own.get(name, nearest[name] * scale) for name in table.columns}, "partial"


def _make(table: TableType) -> Callable[..., Any]:
    def make(gen: Any, type_key: str, category: tuple[str, ...]) -> Any:
        # Imported here: generate.py imports the type tables, which discover the type modules.
        from synthetic_ecommerce_data.core import brands
        from synthetic_ecommerce_data.domains.industrial.generate import ChildDraft, LineDraft

        # A line is one brand's one material in one pack, over a run of sizes.
        # Rotated, not drawn, so every combination and every row is built.
        combos = [(variant, pack) for variant in table.variants for pack in table.packs]
        index = gen._rotate(f"combo:{type_key}", len(combos))
        variant, pack = combos[index]
        # Each combination starts its run STRIDE rows after the last one's,
        # so a build of a few lines spreads over the table.
        first = index * STRIDE % len(table.rows)
        pool = [*table.rows[first:], *table.rows[:first]]
        brand = brands.pick_brand(gen.rng, type_key, gen._exhausted)
        draft = LineDraft(
            item=table.item,
            brand=brand,
            series=f"{table.series}{gen.rng.randint(100, 999)}",
            category=category,
            provenance=table.provenance,
            standard=table.standard,
        )
        draft.line_attrs = [
            keyword_attribute("Item", table.item),
            keyword_attribute("Material", variant.material),
            keyword_attribute("Finish", variant.finish),
            numeric_attribute(PACK, str(pack), float(pack)),
        ]
        run = _window(gen, f"rows:{variant.material}:{pack}", pool, gen._variant_count())
        style = gen._style(table.unit)
        for row in sorted(run):
            child = ChildDraft(system=table.unit)
            child.attrs = [
                gen._length(name, inches, style) for name, inches in table.inches(row).items()
            ]
            child.primary = child.attrs[0]
            draft.children.append(child)
        return draft

    return make


def spec(table: TableType) -> TypeSpec:
    """The modelled :class:`.typespec.TypeSpec` a table declares."""
    wrong = problems(table)
    if wrong:
        raise ValueError(f"table type {table.key!r}: {'; '.join(wrong)}")

    def figure(record: dict[str, str]) -> Drawn:
        values, source = lengths(table, record)
        return Drawn(table.draw(values), source)

    def claims(facts: Mapping[str, str], **_: object) -> tuple[str, ...]:
        return (table.standard,)

    make = _make(table)
    _MADE.setdefault(table.key, table)
    return TypeSpec(
        table.key,
        category=table.category,
        standards_family=table.standards_family,
        vocab=(
            AttrSpec(name="Item", scope="line", presence=1.0, kind="keyword"),
            AttrSpec(name="Material", scope="line", presence=1.0, kind="keyword"),
            AttrSpec(name="Finish", scope="line", presence=0.85, kind="keyword"),
            AttrSpec(name=PACK, scope="line", presence=1.0, kind="count"),
            *(
                AttrSpec(name=name, scope="sku", presence=1.0, kind="length")
                for name in table.columns
            ),
        ),
        figure=figure,
        extent=table.extent,
        make=make,
        share=table.share,
        price=table.price,
        claims=claims,
        may_claim=frozenset({table.standard}),
        key_attributes=(table.columns[0],),
        use_lines=table.use_lines,
    )


def tables() -> dict[str, TableType]:
    """Every registered table type, by type key.

    Read off the registered types, so a gate that treats table types alike
    (no measured price, makers that overlap) names none of them. A table that
    went through :func:`spec` in no type module is not one.
    """
    return {key: _MADE[key] for key in discover() if key in _MADE}
