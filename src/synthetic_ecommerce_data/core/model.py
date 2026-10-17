"""The data model: a manufacturer's product line, and the SKUs under it.

The shape is settled and is the reason the catalog is worth loading:

* A **parent** is one manufacturer's product line. It carries the attributes
  that are constant across that line -- brand, series, material, coating,
  flute count, end type.
* Its **children** are the individual purchasable SKUs. They carry the
  attributes that vary -- diameter, length of cut, overall length, shank,
  price, stock.

Attributes are nested key-value at *both* levels, in **one** array rather than
separate keyword and numeric arrays. That matters: a dimension needs both
representations on the same entry, because a shopper filters on
``Milling Dia. = 3/8"`` as text and ranges over it as a number, and splitting
those into two arrays loses the fact that they are one attribute.

``value_num`` is **parsed back out of** ``value``, never carried alongside it.
Writing 3/8" in millimetres to two decimals gives 9.52mm, which is 0.37480" --
so a numeric field computed from the original magnitude would disagree with
the string actually published. Deriving the number from the published string
makes that disagreement impossible by construction.

An attribute that is not a measurement omits ``value_num`` entirely rather
than carrying a null, and so does a measurement whose value is deliberately
malformed (a unit-mixing spelling the mark cannot read). The mark decides the
unit: a value carrying a degree mark is an angle, one carrying an inch or
millimetre mark is a length, and no unit is taken from the attribute's name.
The generator writes no wrong-kind value (#404): an inch length is never
written under an angle key, so there is no such value for an entry to repair.

``value_num`` is internal: generation and measurement read it, and the flat
shape's ``facets_num`` publishes it. A nested ENTRY carries the split shape of
:mod:`.entry` instead -- ``{key, name, value[, unit_code, value_canonical]}`` --
read from the same published string (elastic/prism#9935).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from synthetic_ecommerce_data.core.dimensions import DimensionParseError, parse_length
from synthetic_ecommerce_data.core.entry import entry, sanitize


@dataclass(frozen=True)
class Attribute:
    """One published attribute: a name, the string, and maybe a number."""

    name: str
    value: str
    value_num: float | None = None
    #: Present only on a multi-valued attribute. When set, ``value`` is the
    #: first value and this holds all of them.
    values: tuple[str, ...] | None = None
    #: The unit a BARE published number is in, when the generator knows it and
    #: the name does not say it: a metric tap's ``Thread Pitch`` is millimetres
    #: (``MMT``), an inch tap's ``Threads per Inch`` is ``TPI``. See
    #: :func:`.entry.split`.
    bare_unit: str | None = None
    #: The machine key, set only where this name means a different concept
    #: than it does on another type (:func:`.entry.entry`); else derived.
    key: str | None = None

    @property
    def facet_key(self) -> str:
        """The flat ``facets`` key: :attr:`key` when set, else the sanitised name."""
        return self.key if self.key is not None else sanitize(self.name)

    @property
    def multivalued(self) -> bool:
        return self.values is not None and len(self.values) > 1

    def as_entries(self) -> tuple[dict[str, Any], ...]:
        """The nested entries this attribute becomes, each split by :func:`.entry.entry`.

        A multi-valued attribute becomes several entries under one name --
        which is the shape that makes a naive nested count over-report, and
        the reason the catalog carries one. Each value is split on its own.
        """
        values = self.values if self.values is not None else (self.value,)
        return tuple(entry(self.name, value, self.bare_unit, self.key) for value in values)


def length_attribute(name: str, published: str) -> Attribute:
    """A dimension attribute whose number is read back out of its own string.

    If the published string cannot be parsed -- which happens on purpose, for
    the defect classes the reference corpus exhibits -- the attribute carries
    no number at all. That is the honest representation: the catalog really
    does publish a value nothing can range over.
    """
    try:
        value_num = parse_length(published).inches
    except DimensionParseError:
        return Attribute(name=name, value=published)
    return Attribute(name=name, value=published, value_num=value_num)


def keyword_attribute(name: str, value: str) -> Attribute:
    return Attribute(name=name, value=value)


def numeric_attribute(name: str, value: str, value_num: float) -> Attribute:
    return Attribute(name=name, value=value, value_num=value_num)


def multi_attribute(name: str, values: tuple[str, ...]) -> Attribute:
    if not values:
        raise ValueError(f"{name} needs at least one value")
    return Attribute(name=name, value=values[0], values=tuple(values))


@dataclass(frozen=True)
class Sku:
    """One purchasable item under a product line."""

    sku: str
    title: str
    #: The shopper-facing copy under the title. It names what separates this
    #: SKU from its siblings -- see ``generate.Generator._build_description``
    #: for the grammar and why the overlap with the title is deliberate.
    description: str
    attributes: tuple[Attribute, ...]
    price_usd: float
    stock: int
    #: This SKU's OWN drawing, as ``<product type>/<product id>/<sku>``, drawn
    #: from its own published values (elastic/prism-industrial-products#103).
    image_id: str = ""
    #: The one cross-reference sentence this SKU's copy carries -- which
    #: screws a key drives, which drill a tap wants (:mod:`.compat`). Also in
    #: the description; kept separately so the searchable text can carry it
    #: without folding in the rest of the description.
    compatibility: str = ""
    #: The copy's noise sentences (:mod:`.noise`): true, distracting, and in
    #: the description and the searchable text only -- never an attribute.
    noise: str = ""

    def attribute_names(self) -> frozenset[str]:
        return frozenset(a.name for a in self.attributes)

    def get(self, name: str) -> Attribute | None:
        for attribute in self.attributes:
            if attribute.name == name:
                return attribute
        return None


@dataclass(frozen=True)
class ProductLine:
    """A parent: one manufacturer's line, and every SKU in it."""

    product_id: str
    type_key: str
    title: str
    brand: str
    series: str
    category: tuple[str, ...]
    attributes: tuple[Attribute, ...]
    children: tuple[Sku, ...]
    #: Where this line's dimensions came from: a standard designation for a
    #: fastener, or a plain statement that they were generated for a tool.
    dimension_provenance: str = ""
    #: ``"realistic"`` for the twelve original and newer types, whose specs
    #: are read from the reference census and standards; ``"fast_and_cheap"``
    #: for the breadth categories (:mod:`.breadth`), whose titles, specs and
    #: images are cheap filler chosen for category coverage, not the demo's
    #: exercised product. TOP-LEVEL and deliberately NOT a nested attribute
    #: (alexander-marquardt/synthetic-ecommerce-data#34): a nested
    #: attribute becomes a facet and searchable text on the industrial
    #: deployment, and this marker must be neither -- it exists so a breadth
    #: line can be found and removed, not so a shopper can filter on it.
    spec_quality: str = "realistic"
    #: The drawing a grouped card shows before a variant is selected: its
    #: first variant's. The product has no drawing of its own.
    image_id: str = ""
    #: Which of the twelve shapes the drawing is -- a square end mill, a flat
    #: washer. Separate from ``image_id`` because they stopped being the same
    #: thing when images went per line: a hundred lines share one shape and
    #: have a hundred drawings of it, each marked with its own line's
    #: published attributes.
    drawing: str = ""
    #: The shopper-readable name of the type (gen#331), set by the domain that
    #: builds the line, so the core never reaches into a domain's label table.
    type_label: str = ""

    def attribute_names(self) -> frozenset[str]:
        return frozenset(a.name for a in self.attributes)


@dataclass(frozen=True)
class Catalog:
    lines: tuple[ProductLine, ...]
    #: The configuration that produced it, for the report.
    stats: dict[str, Any] = field(default_factory=dict)

    @property
    def sku_count(self) -> int:
        return sum(len(line.children) for line in self.lines)

    def all_skus(self):
        for line in self.lines:
            for child in line.children:
                yield line, child

    def merged_attributes(self, line: ProductLine, child: Sku) -> tuple[Attribute, ...]:
        """A flat SKU's full attribute set: the line's, then its own.

        A child never redefines a name the line already carries, so this is a
        concatenation rather than a merge; :mod:`.generate` maintains that.
        """
        return line.attributes + child.attributes
