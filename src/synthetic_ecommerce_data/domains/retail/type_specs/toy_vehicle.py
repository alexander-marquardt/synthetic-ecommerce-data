"""Toy Vehicle (Toys), registered by its spec (gen#537).

The single vehicles stay in the shared row module named by ``homes``, whose ``derivable`` says the
scaled build draws more of them. Add a single there, and a new type as its own spec file with its
rows.

The car packs (gen#749) are this spec's own rows, so they stay templates only: a title that says
"cars", for "toy cars" to prefer over the singles. Each kind sells a pack of 3 and a pack of 5, its
own product, at the multibuy factor of the cheapest single of its material. Each color is a SKU, so
every car of a pack is that color. The title leaves "toy" to the category, as the singles do.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_row import _mat, paint_range
from synthetic_ecommerce_data.domains.retail.type_registry import Home, TypeSpec, cw
from synthetic_ecommerce_data.domains.retail.underwear_rows import URow, _pack_attrs, _packs

PATH = ("Toys", "Vehicles", "Toy Vehicles")
COUNTS = {3: "three", 5: "five"}


def _car_packs(code: str, kind: str, brand: str, price: float, tail: str, hero: tuple) -> list[URow]:
    """``kind`` as a pack of each of :data:`COUNTS`, in the paint range of a single (gen#271)."""
    material = kind.split()[0]
    return [
        URow(f"{code}{n}", f"{kind}, Pack of {n}", brand, "Toys", PATH, "Toy Vehicle", price, "car",
             f"A pack of {word} {kind.lower()}, all in the same color, {tail}",
             paint_range(hero), (*_mat(material), *_pack_attrs(_packs(n))), audience="kids", packs=_packs(n))
        for n, word in COUNTS.items()
    ]  # fmt: skip


CAR_PACKS = (
    *_car_packs("CPKDIE", "Die-Cast Cars", "Puddlecombe Toys", 4.5,
                "each pocket-size with a pull-back motor. For ages 3 and up.", cw("Red", "#c8312e", "solid", "#f4f1ea")),
    *_car_packs("CPKWOD", "Wooden Racing Cars", "Little Fernby", 9.0,
                "each with rubber tires and a driver who lifts out. For ages 18 months and up.",
                cw("Blue", "#3f6fb5", "solid", "#f4f1ea")),
)  # fmt: skip

SPEC = TypeSpec(
    key="toy_vehicle",
    department="Toys",
    product_type="Toy Vehicle",
    rows=CAR_PACKS,
    homes=(Home("breadth_rows", True),),
)
