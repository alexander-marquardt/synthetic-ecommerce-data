"""Range cookers (#1116): dual fuel and induction, 90, 100 or 110 cm wide, six models each.

Home > Large Appliances > Range Cookers, drawn by :func:`kit_cooking.range_cooker`. A model's
width, fuel, oven count and energy rating are structured, and its width is in its title and its
model number (gen#622), so ``range cooker 90cm`` finds the 90 cm ones. The bare word "range" also
names a signal range or a product line elsewhere: a category policy, not the data, picks the
intent. A black range with red knobs is a color decoy. Every brand is invented. Not derivable:
the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import appliance_lineups as lineups
from synthetic_ecommerce_data.domains.retail import large_appliance_rows as lar
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_WORDS = {2: "two", 3: "three"}
#: The real finishes of a range: (black, stainless, red), (blue, black), (cream white, green).
_PALETTES = ((lar.BLACK, lar.SILVER, lar.RED), (lar.BLUE, lar.BLACK), (lar.WHITE, lar.GREEN))

#: The range cookers: (width cm, ovens, price); six of the twelve are 90 cm wide.
_RANGE_KINDS = (
    ("RCD", "dual_fuel", "Dual Fuel Range Cooker", "Range Cooker (Dual Fuel)", "Dual Fuel",
     "A dual fuel range cooker with gas burners on top and electric ovens below",
     ((90, 2, 899), (90, 2, 1049), (90, 3, 1199), (100, 2, 1299), (100, 3, 1449), (110, 3, 1699))),
    ("RCI", "induction", "Induction Range Cooker", "Range Cooker (Induction)", "Electric",
     "An electric range cooker with induction zones on top and electric ovens below",
     ((90, 2, 1099), (90, 2, 1249), (90, 3, 1399), (100, 2, 1499), (100, 3, 1649), (110, 3, 1899))),
)  # fmt: skip


def _attrs(kind_name: str, fuel: str, width: int, ovens: int, rating: str) -> tuple:
    return (a("appliance_type", "Type", kind_name), lar.cm(width), a("fuel_type", "Fuel type", fuel),
            lar.count("oven_count", "Number of ovens", ovens), a("energy_rating", "Energy rating", rating))  # fmt: skip


def range_cooker_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, fuel, lead, table in _RANGE_KINDS:
        models = lineups.line_up(pre, table, 2)

        def make(i, models=models, lead=lead, kind_name=kind_name, fuel=fuel, pre=pre):
            width, ovens, price = models[i]
            rating = lar.RATINGS[(i + len(pre)) % 3]
            says, sold_on = lineups.feature("Range Cooker", i)
            desc = f"{lead}. It is {width} cm wide with {_WORDS[ovens]} ovens and a storage drawer, energy rating {rating}.{says}"
            return float(price), desc, _PALETTES[i % 3], (*_attrs(kind_name, fuel, width, ovens, rating), *sold_on)
        rows = lar.kind_rows(pre, len(models), lar.RANGE_COOKERS, "Range Cooker", "range_cooker", (), title, make)
        out += [replace(r, params=(("kind", shape), ("width", str(w)), ("ovens", str(n))))
                for r, (w, n, _) in zip(rows, models, strict=True)]
    return tuple(out)


SPEC = TypeSpec(
    key="range_cooker",
    department="Home",
    product_type="Range Cooker",
    owners=lar.OWNERS,
    rows=range_cooker_rows(),
    decoys=(
        Decoy(1, "red range cooker", "color", lar.decoy_row(
            "RCR001", "Dual Fuel Range Cooker with Red Enamel Knobs", lar.BRANDS[3], lar.RANGE_COOKERS,
            "Range Cooker", 1149.0, "range_cooker",
            "A dual fuel range cooker in black. Its control knobs are red enamel. It is 90 cm wide "
            "with two ovens.", (lar.BLACK,),
            _attrs("Range Cooker (Dual Fuel)", "Dual Fuel", 90, 2, "A"),
            (("kind", "dual_fuel"), ("width", "90"), ("ovens", "2")))),
    ),
)
