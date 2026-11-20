"""The Pets department's shared pieces (gen#967): its paths, brands, packs and rows.

Slice 3 adds Leash & Collar and Grooming Brush (``type_specs/leash_collar.py``,
``grooming_brush.py``), sold like the toys in the six main colors by size, and Small Pet Supply
(``small_pet_supply.py``: fish food, aquarium gravel, small-animal food, hay and bedding),
colorless and sold by the bag's weight like the food, all three drawn by :mod:`kit_pet_care`.

Slice 2 adds Dog Treats (``type_specs/dog_treats.py``, colorless, by the bag's net weight), Pet
Toy and Pet Bed (``pet_toy.py``, ``pet_bed.py``), sold in the six main colors (:data:`MAIN`,
ruling 2026-10-13, gen#275) by size, built by :func:`gear` and drawn by :mod:`kit_pet_gear`.

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
    kit_pet_care,  # noqa: F401 -- registers pet_leash, grooming_brush, small_pet_supply
    kit_pet_gear,  # noqa: F401 -- registers dog_treats, pet_toy, pet_bed
    kit_pets,  # noqa: F401 -- registers dry_pet_food, wet_pet_food, cat_litter
)
from synthetic_ecommerce_data.domains.retail.main_color_hex import MAIN_COLORS
from synthetic_ecommerce_data.domains.retail.type_registry import Row, cw

#: The build record's department, and the top level of every path.
DEPARTMENT = "Pets"
ROOT = "Pets"
DRY_DOG = (ROOT, "Dog Food", "Dry Dog Food")
WET_DOG = (ROOT, "Dog Food", "Wet Dog Food")
DRY_CAT = (ROOT, "Cat Food", "Dry Cat Food")
WET_CAT = (ROOT, "Cat Food", "Wet Cat Food")
LITTER = (ROOT, "Litter & Hygiene", "Cat Litter")
DENTAL = (ROOT, "Dog Treats", "Dental Chews")
BISCUITS = (ROOT, "Dog Treats", "Dog Biscuits")
TRAINING = (ROOT, "Dog Treats", "Training Treats")
DOG_TOYS = (ROOT, "Pet Toys", "Dog Toys")
CAT_TOYS = (ROOT, "Pet Toys", "Cat Toys")
DOG_BEDS = (ROOT, "Pet Beds", "Dog Beds")
CAT_BEDS = (ROOT, "Pet Beds", "Cat Beds")
DOG_LEASHES = (ROOT, "Leashes & Collars", "Dog Leashes")
RETRACTABLE = (ROOT, "Leashes & Collars", "Retractable Leashes")
DOG_COLLARS = (ROOT, "Leashes & Collars", "Dog Collars")
HARNESSES = (ROOT, "Leashes & Collars", "Dog Harnesses")
CAT_COLLARS = (ROOT, "Leashes & Collars", "Cat Collars")
DOG_BRUSHES = (ROOT, "Grooming", "Dog Brushes")
CAT_BRUSHES = (ROOT, "Grooming", "Cat Brushes")
FISH_FOOD = (ROOT, "Fish & Aquarium", "Fish Food")
GRAVEL = (ROOT, "Fish & Aquarium", "Aquarium Gravel")
SMALL_FOOD = (ROOT, "Small Animal", "Small Animal Food")
HAY = (ROOT, "Small Animal", "Hay")
BEDDING = (ROOT, "Small Animal", "Small Animal Bedding")

HOUND = "Hound & Heath"
BARKWELL = "Barkwell"
TAILMOOR = "Tailmoor"
WHISKERBY = "Whiskerby"
PURRSEY = "Purrsey Lane"
PINEHOLLOW = "Pinehollow"
CLUMPTON = "Clumpton"
#: Slice 3's fish and small-animal brands.
FINBROOK = "Finbrook"
BURROWELL = "Burrowell"
#: The brands of the text-match decoys: each holds the word its decoy's query names.
ALLEY_CAT = "Alley Cat Provisions"
KITTEN_MILL = "Kitten Mill"

#: Who makes each brand: the store's own label, or another house.
OWNERS = (
    (HOUND, "third_party"), (BARKWELL, "third_party"), (TAILMOOR, "own"),
    (WHISKERBY, "third_party"), (PURRSEY, "third_party"), (PINEHOLLOW, "third_party"),
    (CLUMPTON, "third_party"), (ALLEY_CAT, "third_party"), (KITTEN_MILL, "third_party"),
    (FINBROOK, "third_party"), (BURROWELL, "third_party"),
)  # fmt: skip

#: The pack colors: a bag's or a tin's print, which the drawing takes as its fill.
RUST = cw("Rust", "#b5522f", "solid", "#ffffff")
FOREST = cw("Forest", "#2f6b45", "solid", "#ffffff")
NAVY = cw("Navy", "#26406b", "solid", "#ffffff")
PLUM = cw("Plum", "#6e3b6e", "solid", "#ffffff")
TEAL = cw("Teal", "#1f7a7a", "solid", "#ffffff")
SAND = cw("Sand", "#d9c08c", "solid", "#2a2a2e")
SKY = cw("Sky", "#7fb2d9", "solid", "#2a2a2e")
#: The six main colors a toy or a bed is sold in (gen#275), each its own SKU and drawing.
MAIN = tuple(cw(name, hex_, "solid", "#2a2a2e" if name in ("Yellow", "White") else "#ffffff")
             for name, hex_ in MAIN_COLORS.items())  # fmt: skip


def grams(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """A bag's weights in kilograms as its SKU sizes: the net weight in grams, at its price."""
    return tuple((str(round(kg * 1000)), p) for kg, p in pairs)


def units(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    """A wet food's packs as its SKU sizes: the pouches, trays or tins in each, at its price."""
    return tuple((str(n), p) for n, p in pairs)


#: The attributes the pack prints, so its drawing shows them (:mod:`kit_pets`): two styles of one
#: leaf and price that differ in one read apart on a results grid.
DRAWN = ("life_stage", "flavor", "breed_size", "special_need", "scent", "treat_form", "toy_kind",
         "play_feature", "bed_style", "cover", "gear_kind", "material", "brush_kind", "coat_type",
         "supply_kind", "formula")  # fmt: skip


def row(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
        description: str, attrs: tuple[tuple, ...], sizes: tuple[tuple[str, float], ...],
        size_key: str, params: tuple[tuple[str, str], ...], color: tuple) -> Row:  # fmt: skip
    """One pet style: its sizes are its SKUs, and its one pack color is drawn, not sold. Each
    :data:`DRAWN` attribute joins ``params`` as its lower-cased value, so a derived style that
    swaps the value is drawn true (gen#512)."""
    drawn = tuple((k, v.lower()) for k, _, v in attrs if k in DRAWN)
    return Row(code, title, brand, DEPARTMENT, path, product_type, sizes[0][1], shape,
               description, (color,), attrs, sizes, colorless=True, params=params + drawn,
               size_key=size_key)  # fmt: skip


def gear(code: str, title: str, brand: str, path: tuple[str, ...], product_type: str, shape: str,
         description: str, attrs: tuple[tuple, ...], price: float,
         sizes: tuple[tuple[str, float], ...] = (), animal: str = "dog") -> Row:  # fmt: skip
    """One toy or bed style: its six main colors times its sizes (``Small`` to ``Extra Large``)
    are its SKUs, or its colors alone when it has one size. Each :data:`DRAWN` attribute joins
    ``params`` as its lower-cased value, as in :func:`row`."""
    drawn = tuple((k, v.lower()) for k, _, v in attrs if k in DRAWN)
    first = sizes[0][1] if sizes else price
    return Row(code, title, brand, DEPARTMENT, path, product_type, first, shape, description,
               MAIN, attrs, sizes, params=(("animal", animal), *drawn))  # fmt: skip


def decoy(base: Row, code: str, title: str, description: str, brand: str | None = None) -> Row:
    """A text-match decoy cut from ``base``: a title, a description or a brand that holds a word
    its structured fields do not (the fields tell the truth)."""
    return replace(base, code=code, title=title, description=description,
                   brand=brand or base.brand)  # fmt: skip
