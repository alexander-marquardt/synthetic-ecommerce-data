"""The grocery row model: :class:`F`, :class:`Family` and the closed lists (:mod:`grocery_rows`)."""

# ruff: noqa: E501 -- one family's flavors read better on few lines than wrapped (data only).

from __future__ import annotations

from dataclasses import dataclass

#: The dietary labels a SKU may carry: one closed list (gen#296).
DIETARY: tuple[str, ...] = ("Vegan", "Vegetarian", "Gluten Free", "Dairy Free", "Nut Free", "Organic")

ALLERGENS = {"P": "Peanuts", "T": "Tree Nuts", "M": "Milk", "G": "Gluten", "S": "Soy", "E": "Egg", "F": "Fish"}


@dataclass(frozen=True)
class F:
    """One flavor, scent or variety: its name, pack color and contained allergens."""

    name: str
    hex: str
    codes: str = ""
    abv: float | None = None  # a beer's strength: an attribute, and in only some titles
    extras: tuple[tuple[str, str, str], ...] = ()  # more (key, name, value) attributes: grape, origin


@dataclass(frozen=True)
class Family:
    code: str
    path: tuple[str, ...]
    title: str  # "{line}" and, when a style carries one flavor, "{flavor}"
    product_type: str
    shape: str
    label: str
    storage: str
    grades: str  # the nutrition grades a style draws from
    price: float  # the first pack's price
    packs: tuple[str, ...]  # "100g", "4 x 35g", "1L", "6 pack"
    flavors: tuple[F, ...]
    brands: tuple[str, ...]
    weight: float  # share of the build's SKUs
    base: str = ""  # codes every flavor contains
    may: tuple[tuple[int, str], ...] = ((1, ""),)
    per_style: tuple[int, int] = (1, 1)  # flavors a style carries (min, max)
    axis: str = "flavor"  # or "scent" (a non-food), "variety" (fresh produce)
    department: str = "Food & Drink"
    params: tuple[tuple[str, str], ...] = ()
    noun: str = ""  # a non-food's description noun; "" keeps the overlap rows' own
    axis_name: str = ""  # the axis attribute's display name when it is not the capitalised key
    fits: str = ""  # a non-food's closing sentence, "{x}" the lower-cased axis value (else "Scented with")
    item_g: float = 0.0  # a per-item fruit's typical weight of one item, g: prices a weight pack beside count packs
    depth: bool = False  # built after the core families from its own stream (see ``grocery.build``)

    @property
    def food(self) -> bool:
        return self.department == "Food & Drink"
