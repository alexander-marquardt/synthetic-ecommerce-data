"""What the bedding and food storage specs of gen#963 slice 2 share: the brands, the colors and
the table that turns a type's kinds into one style per brand.

Sheet sets and pillows (``type_specs/bed_sheet.py``, ``pillow.py``) sit beside the duvets under
``Home > Bedding``; food storage containers (``food_storage_container.py``) beside the storage
boxes under ``Home > Storage``. Their brands are invented brands other rows already carry
(ruling 2026-10-30, gen#720), so every one has its owner, its mark and its house style. A brand
new to the build would join the scale build's range-name deal (``scale._range_deal``), which
deals the names over every brand a derived style may carry, and so rename the derived styles of
every other department (gen#963 review); none of these brands is an ``EXTRA_BRANDS`` one, which a
template may not carry. A sheet set and a food storage container are each a line-grammar family of
their own (``line_grammar_families/sheets.py``, ``food_storage.py``): joining the soft or storage
family would add their brands to that family's deal and rename main's styles of it.
A sheet set and a container lid are sold in the six main colors (ruling 2026-10-13, gen#275);
a pillow keeps its natural white cover (``main_colors.EXCEPTIONS``).
"""

from __future__ import annotations

from dataclasses import dataclass, replace

from synthetic_ecommerce_data.domains.retail import (
    kit_bedding_storage,  # noqa: F401 -- registers sheet_set, food_storage
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.variants import BED, cw

DEPARTMENT = "Home"

#: The brands that sell bedding, with the three letters a row code ends in. The scaled build
#: makes one style per brand and title, so these brands bound each type's depth.
BEDDING_BRANDS = (
    ("Quillon Sleep", "QSL"), ("Thistle & Wren", "THW"), ("Hollinwray Knits", "HWK"),
    ("Brackenmere Home", "BRK"), ("Wrenfield", "WRN"), ("Larkmoor", "LRK"),
    ("Harbour & Pine", "HBP"), ("Little Fernby", "LFB"), ("Mirefield Naturals", "MFN"),
    ("Lanternby", "LNT"), ("Calderby & Lune", "CLD"), ("Puddlecombe Toys", "PDT"),
    ("Hearth & Table", "HRT"),
)  # fmt: skip
#: The brands that sell pillows: the bedding brands main's soft family of the line grammar
#: already deals its model words to. A pillow is of that family (``line_grammar_families/soft.py``)
#: and its words are dealt over the brands that sell the family (``line_grammar.Deal``), so a brand
#: new to it would re-deal them and rename main's cushions, towels, duvets and baby goods.
PILLOW_BRANDS = tuple(
    (b, t) for b, t in BEDDING_BRANDS
    if b not in ("Wrenfield", "Larkmoor", "Hollinwray Knits", "Harbour & Pine", "Puddlecombe Toys")
)  # fmt: skip
#: The brands that sell food storage.
KITCHEN_BRANDS = (
    ("Hearth & Table", "HRT"), ("Pantry Mill", "PNM"), ("Freshfold", "FRF"),
    ("Kettleby Tea Co.", "KTC"), ("Lanternby", "LNT"), ("Calderby & Lune", "CLD"),
    ("Little Fernby", "LFB"), ("Thistle & Wren", "THW"), ("Brackenmere Home", "BRK"),
    ("Mirefield Naturals", "MFN"), ("Harbour & Pine", "HBP"), ("Brewhollow Roasters", "BHR"),
    ("Wrenfield", "WRN"),
)  # fmt: skip

#: The six main colors, in the order a style lists them: the first is the hero the image shows.
RED = cw("Red", "#c8312e", "solid", "#2f2f35")
BLUE = cw("Blue", "#3f6fb5", "solid", "#f4f1ea")
GREEN = cw("Green", "#5f9a4a", "solid", "#f4f1ea")
YELLOW = cw("Yellow", "#f2c94c", "solid", "#2f2f35")
BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
WHITE = cw("White", "#f4f1ea", "solid", "#8f989f")
MAIN = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)

#: How a type's kinds are given: ``kind -> (price, description, sizes)``, each size at its price.
Kinds = dict[str, tuple[float, str, tuple[tuple[str, float], ...]]]


def colors(hero: tuple) -> tuple[tuple, ...]:
    """The six main colors with ``hero`` first."""
    return (hero, *(c for c in MAIN if c != hero))


@dataclass(frozen=True)
class ChartRow(Row):
    """A style whose sizes are entries of core's bedding chart (``variants.BED``): each SKU
    states the size in every system, UK, EU and US, as main's pillows and pillowcases do."""

    def skus(self) -> list[dict]:
        return [{"color": c[0], **dict(zip(("size_uk", "size_eu", "size_us"), BED[s], strict=True)),
                 "price": p, "in_stock": True}
                for c in self.colors for s, p in self.sizes]  # fmt: skip


def table(prefix: str, brands: tuple[tuple[str, str], ...], path: tuple[str, ...],
          product_type: str, shape: str, kind_attr: tuple[str, str], kinds: Kinds,
          design_attr: tuple[str, str], designs: tuple[str, ...], size_key: str,
          white_only: bool = False, design_param: str = "",
          row_type: type[Row] = Row) -> tuple[Row, ...]:  # fmt: skip
    """One style per brand: the brand's kind and design cycle through ``kinds`` and ``designs``,
    so every value is on a template. The title is the design, the kind and the product type,
    which the scaled build varies. ``white_only`` sells every style in white alone; else the six
    main colors, each style's hero in turn. The drawing's ``kind`` param is the kind, and
    ``design_param`` names a param that draws the design too (a pillow's support), so a derived
    style that changes either draws what it states (gen#512); ``row_type`` is :class:`ChartRow`
    for a type sized by the bedding chart."""
    names = list(kinds)
    out = []
    for i, (brand, tag) in enumerate(brands):
        kind = names[i % len(names)]
        design = designs[(i + i // len(names)) % len(designs)]
        price, description, sizes = kinds[kind]
        attrs = ((*kind_attr, kind), (*design_attr, design))
        palette = (WHITE,) if white_only else colors(MAIN[i % len(MAIN)])
        drawn_design = ((design_param, design.lower()),) if design_param else ()
        params = (("kind", kind.lower()), *drawn_design)
        out.append(row_type(f"{prefix}{tag}", f"{design} {kind} {product_type}", brand, DEPARTMENT,
                       path, product_type, sizes[0][1], shape, description, palette, attrs,
                       sizes, params=params, size_key=size_key))  # fmt: skip
    return tuple(out)


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: its title holds a word its structured fields do not
    (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
