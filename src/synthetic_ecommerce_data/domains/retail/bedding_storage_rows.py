"""What the bedding and food storage specs of gen#963 slice 2 share: the brands, the colors and
the table that turns a type's kinds into one style per brand.

Sheet sets and pillows (``type_specs/bed_sheet.py``, ``pillow.py``) sit beside the duvets under
``Home > Bedding``; food storage containers (``food_storage_container.py``) beside the storage
boxes under ``Home > Storage``. Their brands are the invented Home brands other rows already
carry (ruling 2026-10-30, gen#720), so every one has its owner, its mark and its house style.
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
    ("Quillon Sleep", "QSL"), ("Hushwell", "HSH"), ("Dovecote Lane", "DVL"),
    ("Brackenmere Home", "BRK"), ("Wrenfield", "WRN"), ("Larkmoor", "LRK"),
    ("Harbour & Pine", "HBP"), ("Emberly Home", "EMB"), ("Larchwood Living", "LRW"),
    ("Lanternby", "LNT"), ("Calderby & Lune", "CLD"), ("Cobble & Kiln", "CBK"),
    ("Hearth & Table", "HRT"),
)  # fmt: skip
#: The brands that sell pillows: the bedding brands the line grammar's soft family already deals
#: its model words to (``line_grammar_families/soft.py`` has a word for each, and no more).
PILLOW_BRANDS = tuple((b, t) for b, t in BEDDING_BRANDS if b not in ("Wrenfield", "Larkmoor"))
#: The brands that sell food storage.
KITCHEN_BRANDS = (
    ("Hearth & Table", "HRT"), ("Pantry Mill", "PNM"), ("Freshfold", "FRF"),
    ("Clearbrook Household", "CLB"), ("Lanternby", "LNT"), ("Calderby & Lune", "CLD"),
    ("Emberly Home", "EMB"), ("Cobble & Kiln", "CBK"), ("Brackenmere Home", "BRK"),
    ("Larchwood Living", "LRW"), ("Harbour & Pine", "HBP"), ("Soapwell", "SPW"),
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
          white_only: bool = False, drawn: bool = True,
          row_type: type[Row] = Row) -> tuple[Row, ...]:  # fmt: skip
    """One style per brand: the brand's kind and design cycle through ``kinds`` and ``designs``,
    so every value is on a template. The title is the design, the kind and the product type,
    which the scaled build varies. ``white_only`` sells every style in white alone; else the six
    main colors, each style's hero in turn. ``drawn`` passes the kind to the drawing; ``row_type``
    is :class:`ChartRow` for a type sized by the bedding chart."""
    names = list(kinds)
    out = []
    for i, (brand, tag) in enumerate(brands):
        kind = names[i % len(names)]
        design = designs[(i + i // len(names)) % len(designs)]
        price, description, sizes = kinds[kind]
        attrs = ((*kind_attr, kind), (*design_attr, design))
        palette = (WHITE,) if white_only else colors(MAIN[i % len(MAIN)])
        params = (("kind", kind.lower()),) if drawn else ()
        out.append(row_type(f"{prefix}{tag}", f"{design} {kind} {product_type}", brand, DEPARTMENT,
                       path, product_type, sizes[0][1], shape, description, palette, attrs,
                       sizes, params=params, size_key=size_key))  # fmt: skip
    return tuple(out)


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: its title holds a word its structured fields do not
    (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
