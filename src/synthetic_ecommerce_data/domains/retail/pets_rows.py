"""The Pets department's shared pieces (gen#967): its paths, brands, packs and rows.

``Pets`` is both the store's department (the top level of ``category_path``, on
``core/departments.RETAIL``) and the build record's ``department`` (:mod:`departments`), which
keys the department's brand pools. Each type is a spec of its own (``type_specs/dog_food.py``,
``cat_food.py``, ``cat_litter.py``) drawn by :mod:`kit_pets`. Food and litter carry no color
(``colorless``): their one color is the pack's, and the drawing takes it. A dry food or a litter
is sold by its bag's net weight in grams (``net_weight_g``), a wet food by the pouches, trays or
tins in its pack (``units_per_pack``, which :mod:`pack_copies` draws as that many). Every brand
here is invented (ruling 2026-10-30, gen#720); :mod:`pet_brand_styles` gives each its house style.
"""

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import (
    kit_pets,  # noqa: F401 -- registers dry_pet_food, wet_pet_food, cat_litter
)
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The build record's department, and the top level of every path.
DEPARTMENT = "Pets"
ROOT = "Pets"
DRY_DOG = (ROOT, "Dog Food", "Dry Dog Food")
WET_DOG = (ROOT, "Dog Food", "Wet Dog Food")
DRY_CAT = (ROOT, "Cat Food", "Dry Cat Food")
WET_CAT = (ROOT, "Cat Food", "Wet Cat Food")
LITTER = (ROOT, "Litter & Hygiene", "Cat Litter")

HOUND = "Hound & Heath"
BARKWELL = "Barkwell"
FURROW = "Furrow & Field"
WHISKERBY = "Whiskerby"
PURRSEY = "Purrsey Lane"
PINEHOLLOW = "Pinehollow"
CLUMPTON = "Clumpton"
#: The brands of the text-match decoys: each holds the word its decoy's query names.
ALLEY_CAT = "Alley Cat Larder"
KITTEN_MILL = "Kitten Mill"

#: Who makes each brand: the store's own label, or another house.
OWNERS = (
    (HOUND, "third_party"), (BARKWELL, "third_party"), (FURROW, "own"),
    (WHISKERBY, "third_party"), (PURRSEY, "third_party"), (PINEHOLLOW, "third_party"),
    (CLUMPTON, "third_party"), (ALLEY_CAT, "third_party"), (KITTEN_MILL, "third_party"),
)  # fmt: skip

#: The pack colors: a bag's or a tin's print, which the drawing takes as its fill.
RUST = cw("Rust", "#b5522f", "solid", "#ffffff")
FOREST = cw("Forest", "#2f6b45", "solid", "#ffffff")
NAVY = cw("Navy", "#26406b", "solid", "#ffffff")
PLUM = cw("Plum", "#6e3b6e", "solid", "#ffffff")
TEAL = cw("Teal", "#1f7a7a", "solid", "#ffffff")
SAND = cw("Sand", "#d9c08c", "solid", "#2a2a2e")
SKY = cw("Sky", "#7fb2d9", "solid", "#2a2a2e")


def grams(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """A bag's weights in kilograms as its SKU sizes: the net weight in grams, at its price."""
    return tuple((str(round(kg * 1000)), p) for kg, p in pairs)


def units(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A wet food's packs as its SKU sizes: the pouches, trays or tins in each, at its price."""
    return tuple((str(n), p) for n, p in pairs)


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        size_key: str, params: tuple[tuple[str, str], ...], color: tuple) -> Row:  # fmt: skip
    """One pet style: its sizes are its SKUs, and its one pack color is drawn, not sold."""
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape,
               description, (color,), attrs, sizes, colorless=True, params=params,
               size_key=size_key)  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, brand: str | None = None) -> Row:
    """A text-match decoy cut from ``base``: a title, a description or a brand that holds a word
    its structured fields do not (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description,
                   brand=brand or base.brand)  # fmt: skip
