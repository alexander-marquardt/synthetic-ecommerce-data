"""Built-in ovens (#1116): single and double, six models each.

Home > Large Appliances > Built-in Ovens, drawn by :func:`kit_cooking.built_in_oven`. A model's
capacity (litres, in its title and model number, gen#622), width and energy rating are
structured; its finish is the SKU's color. A stainless oven with a black glass door is a color
decoy. Every brand is invented. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import large_appliance_rows as lar
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

#: The ovens: (capacity litres, price); a double oven's capacity is both cavities together.
_OVEN_KINDS = (
    ("OVS", "single", "Built-in Single Oven", "Single Oven", "A built-in single oven for a tall housing or under a worktop",
     ((65, 249), (68, 299), (70, 349), (71, 399), (72, 449), (75, 549))),
    ("OVD", "double", "Built-in Double Oven", "Double Oven", "A built-in double oven, a main oven below a smaller top oven",
     ((97, 449), (102, 499), (107, 549), (110, 629), (112, 699), (116, 799))),
)  # fmt: skip


def _attrs(kind_name: str, litres: int, rating: str) -> tuple:
    return (a("appliance_type", "Type", kind_name), lar.litres(litres), lar.cm(60),
            a("energy_rating", "Energy rating", rating))  # fmt: skip


def oven_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, lead, models in _OVEN_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, pre=pre):
            litres, price = models[i]
            rating = lar.RATINGS[(i + len(pre)) % 3]
            desc = f"{lead}. It holds {litres} litres and is 60 cm wide, energy rating {rating}."
            return float(price), desc, lar.PALETTES[i % 3], _attrs(kind_name, litres, rating)
        rows = lar.kind_rows(pre, 6, lar.OVENS, "Built-in Oven", "built_in_oven", (("kind", shape),), title, make)
        out += [replace(r, params=(("kind", shape),)) for r in rows]
    return tuple(out)


SPEC = TypeSpec(
    key="built_in_oven",
    department="Home",
    product_type="Built-in Oven",
    owners=lar.OWNERS,
    rows=oven_rows(),
    decoys=(
        Decoy(1, "black oven", "color", lar.decoy_row(
            "OVK001", "Built-in Single Oven with Black Glass Door", lar.BRANDS[4], lar.OVENS,
            "Built-in Oven", 379.0, "built_in_oven",
            "A built-in single oven in stainless steel. Its door is black glass. It holds 71 litres "
            "and is 60 cm wide.", (lar.SILVER,), _attrs("Single Oven", 71, "A"), (("kind", "single"),))),
    ),
)
