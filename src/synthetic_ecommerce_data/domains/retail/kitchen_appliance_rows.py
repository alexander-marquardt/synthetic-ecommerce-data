"""What the small kitchen appliance specs share (gen#963): the leaf, the brands, the colors.

Coffee makers, air fryers and blenders (``type_specs/coffee_maker.py``, ``air_fryer.py``,
``blender.py``) sit beside the kettles and toasters under ``Home > Small Appliances``. Each style
is sold in the six main colors (ruling 2026-10-13, gen#275), and its brands are the invented
Home brands the kettles and toasters already carry (ruling 2026-10-30, gen#720), so every one
has its owner, its mark and its house style.

The brands are only those a derivable template of the kitchen family already carries, and none
of :data:`scale.EXTRA_BRANDS`: the model words are dealt round the sorted set of the family's
brands (:class:`line_grammar.Deal`), and the range names were dealt round every brand a derived
style may carry, so a brand new to that set moved the range name of a style in every other
department (gen#963) until the scale deal took an append-only roster (#1052,
:data:`range_ownership.SCALE`).
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_kitchen_appliances,  # noqa: F401 -- registers coffee_maker, air_fryer, blender
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

DEPARTMENT = "Home"
SMALL_APPLIANCES = ("Home", "Small Appliances")

#: Every brand that sells a small kitchen appliance, with the three letters its row codes end in:
#: the Home brands of the kitchen family's templates, each already with an owner and a mark. The
#: scaled build adds the department's extra brands to each type's pool.
BRANDS = (
    ("Hearth & Table", "HRT"), ("Lanternby", "LNT"), ("Calderby & Lune", "CLD"),
    ("Brackenmere Home", "BRK"),
)  # fmt: skip

#: The six main colors, in the order a style lists them: the first is the hero the image shows.
RED = cw("Red", "#c8312e", "solid", "#2f2f35")
BLUE = cw("Blue", "#3f6fb5", "solid", "#f4f1ea")
GREEN = cw("Green", "#5f9a4a", "solid", "#f4f1ea")
YELLOW = cw("Yellow", "#f2c94c", "solid", "#2f2f35")
BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
WHITE = cw("White", "#f4f1ea", "solid", "#8f989f")
MAIN = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)


def colors(hero: tuple) -> tuple[tuple, ...]:
    """The six main colors with ``hero`` first."""
    return (hero, *(c for c in MAIN if c != hero))


def litres(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """A capacity in litres as the SKU sizes, each at its price."""
    return tuple((f"{v:g}", p) for v, p in pairs)


def row(code: str, title: str, brand: str, leaf: str, product_type: str, shape: str, kind: str,
        description: str, attrs: tuple[tuple, ...], hero: tuple, price: float,
        sizes: tuple[tuple[str, float], ...] = (), size_key: str = "size") -> Row:  # fmt: skip
    """One style under ``Home > Small Appliances > leaf``: its colors times its sizes are its SKUs,
    and ``kind`` is the lower-cased type value the drawing follows."""
    return Row(code, title, brand, DEPARTMENT, (*SMALL_APPLIANCES, leaf), product_type, price,
               shape, description, colors(hero), attrs, sizes, params=(("kind", kind),),
               size_key=size_key)  # fmt: skip


Kinds = dict[str, tuple[float, str, tuple[tuple[str, float], ...]]]


def table(prefix: str, leaf: str, product_type: str, shape: str, type_key: str, type_name: str,
          kinds: Kinds, design_key: str, design_name: str, designs: tuple[str, ...],
          size_key: str = "size") -> tuple[Row, ...]:  # fmt: skip
    """A style for each brand of :data:`BRANDS`, or for each type or design if there are more:
    the brand, the type and the design cycle together, so every value is on a template. A brand's
    second style ends its code in a number. ``kinds`` maps a type to its price, its description
    and its sizes (none: one SKU per color); the title is the design, the type and the product
    type, which the scaled build varies."""
    names = list(kinds)
    out = []
    for i in range(max(len(BRANDS), len(names), len(designs))):
        brand, tag = BRANDS[i % len(BRANDS)]
        tag += str(i // len(BRANDS) + 1) if i >= len(BRANDS) else ""
        kind = names[i % len(names)]
        design = designs[i % len(designs)]
        price, description, sizes = kinds[kind]
        attrs = ((type_key, type_name, kind), (design_key, design_name, design))
        hero = MAIN[i % len(MAIN)]
        out.append(row(f"{prefix}{tag}", f"{design} {kind} {product_type}", brand, leaf,
                       product_type, shape, kind.lower(), description, attrs, hero,
                       sizes[0][1] if sizes else price, sizes, size_key))  # fmt: skip
    return tuple(out)


def decoy(base: Row, code: str, title: str, description: str) -> Row:
    """A text-match decoy cut from ``base``: its title holds a word its structured fields do not
    (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description)
