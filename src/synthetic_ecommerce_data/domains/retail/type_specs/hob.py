"""Hobs (#1116): induction, ceramic and gas, 60 to 90 cm wide, six models each.

Home > Large Appliances > Hobs, drawn from above by :func:`kit_cooking.hob`. A model's width (in
its title and model number, gen#622) and its number of cooking zones are structured; its finish
is the SKU's color, black glass for an induction or ceramic hob. A stainless gas hob with black
pan supports is a color decoy. Every brand is invented. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import appliance_lineups as lineups
from synthetic_ecommerce_data.domains.retail import large_appliance_rows as lar
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_WORDS = {3: "three", 4: "four", 5: "five"}
_GLASS = ((lar.BLACK,),)
_GAS = ((lar.SILVER, lar.BLACK), (lar.BLACK,), (lar.WHITE, lar.SILVER))

#: The hobs: (width cm, cooking zones, price)
_HOB_KINDS = (
    ("HBI", "induction", "Induction Hob", "Induction Hob", "An induction hob in black glass, zones that heat the pan itself", _GLASS,
     ((60, 4, 249), (60, 4, 329), (70, 4, 399), (80, 4, 499), (80, 5, 599), (90, 5, 749))),
    ("HBC", "ceramic", "Ceramic Hob", "Ceramic Hob", "A ceramic hob in black glass, radiant rings under the glass", _GLASS,
     ((60, 4, 149), (60, 4, 179), (60, 4, 209), (70, 4, 249), (77, 4, 289), (80, 5, 349))),
    ("HBG", "gas", "Gas Hob", "Gas Hob", "A gas hob, burners under cast-iron pan supports", _GAS,
     ((60, 4, 179), (60, 4, 219), (70, 5, 279), (75, 5, 329), (90, 5, 399), (90, 5, 479))),
)  # fmt: skip


def _attrs(kind_name: str, width: int, zones: int) -> tuple:
    return (a("appliance_type", "Type", kind_name), lar.cm(width),
            lar.count("cooking_zones", "Cooking zones", zones))  # fmt: skip


def hob_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, lead, palettes, table in _HOB_KINDS:
        models = lineups.line_up(pre, table, 2)

        def make(i, models=models, lead=lead, kind_name=kind_name, palettes=palettes):
            width, zones, price = models[i]
            says, sold_on = lineups.feature("Hob", i)
            desc = f"{lead}. It is {width} cm wide with {_WORDS[zones]} cooking zones.{says}"
            return float(price), desc, palettes[i % len(palettes)], (*_attrs(kind_name, width, zones), *sold_on)
        rows = lar.kind_rows(pre, len(models), lar.HOBS, "Hob", "hob", (), title, make)
        out += [replace(r, params=(("kind", shape), ("width", str(w)), ("zones", str(z))))
                for r, (w, z, _) in zip(rows, models, strict=True)]
    return tuple(out)


SPEC = TypeSpec(
    key="hob",
    department="Home",
    product_type="Hob",
    owners=lar.OWNERS,
    rows=hob_rows(),
    decoys=(
        Decoy(1, "black gas hob", "color", lar.decoy_row(
            "HBK001", "Gas Hob with Black Cast-Iron Pan Supports", lar.BRANDS[5], lar.HOBS, "Hob",
            249.0, "hob",
            "A gas hob in stainless steel. Its pan supports are black cast iron. It is 70 cm wide "
            "with five cooking zones.", (lar.SILVER,), _attrs("Gas Hob", 70, 5),
            (("kind", "gas"), ("width", "70"), ("zones", "5")))),
    ),
)
