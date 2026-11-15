"""The :class:`Row` of the breadth templates, its brands and its small helpers (gen#125)."""

from __future__ import annotations

import zlib
from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.departments import (
    check as check_departments,
)
from synthetic_ecommerce_data.domains.retail.variants import (
    Color,
    attr,
    cw,
    drawing,
    product,
    swatch,
)

#: Who makes each brand these rows carry: the retailer ("own") or another house.
OWNERS = {
    "Little Fernby": "own", "Puddlecombe Toys": "third_party",
    "Thistle & Wren": "third_party", "Fenwold Nursery": "third_party",
    "Lanternby": "third_party", "Calderby & Lune": "third_party",
    "Pantry Mill": "own", "Freshfold": "third_party",
    "Hearth & Table": "own", "Kettleby Tea Co.": "third_party",
    "Brewhollow Roasters": "third_party", "Mirefield Naturals": "third_party",
    "Hollin Hair": "third_party",
    "Dovecote Lane": "third_party", "Hushwell": "third_party", "Quillon Sleep": "own",
    "Wrenfield": "own", "Larkmoor": "own", "Hollinwray Knits": "third_party",
    "Harbour & Pine": "own",
    # The seating rows (sofa_rows.py, gen#196) and the furniture rows (furniture_rows.py,
    # gen#199) sell these furniture brands.
    "Brackenmere Home": "own", "Larchwood Living": "third_party", "Emberly Home": "third_party",
    "Cobble & Kiln": "third_party",
    # The mop rows (household_rows.py, gen#200) sell the cleaning department's extra brands.
    "Clearbrook Household": "third_party", "Soapwell": "third_party",
    # The toy rows (toys_rows.py, gen#201) sell the toy department's extra brand.
    "Pipwick Toys": "third_party",
    # The seasonal rows (seasonal_rows.py, gen#195) sell a make-up brand.
    "Kestlewood Cosmetics": "third_party",
    # The bicycle-only brands (type_specs/bicycle.py, gen#718).
    "Gorsecliff": "third_party", "Rindlemoor": "third_party", "Tolvaney": "third_party",
    "Ostlebury": "third_party", "Wattlebrook": "third_party", "Pipkinford": "third_party",
    "Hessenby": "third_party",
}  # fmt: skip


@dataclass(frozen=True)
class Row:
    """One style: its colors times its sizes are its SKUs (one SKU each when it has none).

    A ``colorless`` row's SKUs carry no color (a plant, a cleaner); its drawing still
    takes ``colors[0]``. A size is ``(name, price)``: a bigger size costs more. It is
    stored under ``size_key``: a measured one (``5 ft``, which the core classes as a length)
    goes under its own key (``item_height``), so ``size`` never mixes classed and unclassed values.
    """

    code: str
    title: str
    brand: str
    department: str
    path: tuple[str, ...]
    product_type: str
    price: float
    shape: str
    description: str
    colors: tuple[Color, ...]
    attrs: tuple[tuple, ...] = ()
    sizes: tuple[tuple[str, float], ...] = ()
    label: str | None = None
    audience: str = "adult"
    colorless: bool = False
    params: tuple[tuple[str, str], ...] = ()
    size_key: str = "size"
    #: Why this style keeps its one color when it is a toy vehicle or a ride-on (gen#271):
    #: the color is what the product is (a police livery, a taxi, a fire engine, bare wood).
    #: Empty for a free-paint style, which :func:`paint_range` gives the full range.
    fixed_color: str = ""
    #: The series the brand sells this style in (gen#622); empty when it has none. It is the
    #: document's ``product_line``, which export reads as the ``series`` field.
    product_line: str = ""
    #: Each color's own model number, ``(color, code)`` (gen#622): the SKU of that color states
    #: it as its ``model_number`` option, so the code on the box is found by a query for it.
    color_codes: tuple[tuple[str, str], ...] = ()

    @property
    def product_id(self) -> str:
        """The id of the row's document: ``BRD-`` and the code (a footwear row's is ``FTW-``)."""
        return f"BRD-{self.code}"

    def skus(self) -> list[dict]:
        sizes = [{self.size_key: s, "price": p} for s, p in self.sizes] or [{"price": self.price}]
        colors = self.colors[:1] if self.colorless else self.colors
        codes = dict(self.color_codes)
        return [
            {**({} if self.colorless else {"color": c[0]}), **s, "in_stock": True,
             **({"model_number": codes[c[0]]} if c[0] in codes else {})}
            for c in colors
            for s in sizes
        ]

    def doc(self) -> dict:
        check_departments([self.department], self.code)
        h = zlib.crc32(self.code.encode())
        skus = self.skus()
        swatches = {c[0]: swatch(c) for c in self.colors}
        return product(
            f"BRD-{self.code}", skus, swatches,
            title=self.title, brand=self.brand, brand_owner=OWNERS[self.brand],
            department=[self.department], product_type=self.product_type,
            category_path=list(self.path), category_leaf=self.path[-1],
            description=self.description,
            attributes=[attr(*a) for a in self.attrs],
            drawing=drawing(self.shape, self.colors[0], self.label, **dict(self.params)),
            collections=[], currency="GBP", audience=self.audience,
            sold_last_5_days=5 + h % 90, rating=round(3.8 + (h >> 8) % 11 / 10, 1),
            review_count=3 + (h >> 16) % 400,
            price_min=min(s["price"] for s in skus), price_max=max(s["price"] for s in skus),
            **({"product_line": self.product_line} if self.product_line else {}),
        )  # fmt: skip


def _fab(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("fabric", "Fabric", v),)


def _mat(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("material", "Material", v),)


#: The paint range of a toy vehicle or a ride-on whose color is a free choice (gen#271): the
#: shared color vocabulary's plain words, each its own SKU and its own drawing.
PAINTS = (
    cw("Red", "#c8312e", "solid", "#f4f1ea"), cw("Blue", "#3f6fb5", "solid", "#f4f1ea"),
    cw("Green", "#5f9a4a", "solid", "#f4f1ea"), cw("Yellow", "#f2c94c", "solid", "#2f2f35"),
    cw("Orange", "#e07a1f", "solid", "#2f2f35"), cw("Pink", "#f2a1b8", "solid", "#2f2f35"),
    cw("Purple", "#7b4fa0", "solid", "#f4f1ea"), cw("Black", "#2a2a2e", "solid", "#f4f1ea"),
    cw("White", "#f4f1ea", "solid", "#9a9ca0"), cw("Silver", "#c0c0c0", "solid", "#2f2f35"),
)  # fmt: skip
#: How many colors a free-paint toy vehicle or ride-on is sold in (the issue: about 8 to 10).
PAINT_COUNT = 10


def paint_range(*authored: Color) -> tuple[Color, ...]:
    """``authored`` colors first (the first stays the hero), then the shared paints this
    style does not have yet, up to :data:`PAINT_COUNT`."""
    have = {c[0] for c in authored}
    more = [c for c in PAINTS if c[0] not in have]
    return (*authored, *more)[: max(PAINT_COUNT, len(authored))]
