"""Cooker hoods (#1116): chimney and integrated, 50 to 100 cm wide, six models each.

Home > Large Appliances > Cooker Hoods, drawn by :func:`kit_cooking.cooker_hood`. A hood's width,
extraction rate, fan speeds and energy rating are structured; its width is in its title and its
model number (gen#622). A stainless hood with a black glass canopy edge is a color decoy. Every
brand is invented. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from dataclasses import replace

from synthetic_ecommerce_data.domains.retail import large_appliance_rows as lar
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, TypeSpec, a

_WORDS = {3: "three", 4: "four"}
_CHIMNEY = ((lar.SILVER, lar.BLACK), (lar.BLACK, lar.WHITE), (lar.SILVER, lar.WHITE))
_INTEGRATED = ((lar.SILVER,), (lar.SILVER, lar.WHITE), (lar.SILVER, lar.BLACK))

#: The hoods: (width cm, extraction m3/h, fan speeds, price)
_HOOD_KINDS = (
    ("CHC", "chimney", "Chimney Cooker Hood", "Chimney Cooker Hood",
     "A chimney cooker hood that hangs on the wall above a hob", _CHIMNEY,
     ((60, 380, 3, 119), (60, 420, 3, 149), (70, 550, 3, 189), (90, 620, 3, 229), (90, 700, 4, 289), (100, 800, 4, 349))),
    ("CHI", "integrated", "Integrated Cooker Hood", "Integrated Cooker Hood",
     "A cooker hood that hides inside a kitchen cabinet", _INTEGRATED,
     ((50, 260, 3, 89), (60, 300, 3, 99), (60, 340, 3, 129), (60, 400, 4, 159), (90, 560, 4, 219), (90, 640, 4, 259))),
)  # fmt: skip


def _attrs(kind_name: str, width: int, rate: int, speeds: int, rating: str) -> tuple:
    return (a("appliance_type", "Type", kind_name), lar.cm(width),
            a("extraction_rate", "Extraction rate (m3/h)", str(rate)),
            lar.count("fan_speeds", "Fan speeds", speeds), a("energy_rating", "Energy rating", rating))  # fmt: skip


def cooker_hood_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, lead, palettes, models in _HOOD_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, palettes=palettes, pre=pre):
            width, rate, speeds, price = models[i]
            rating = lar.RATINGS[(i + len(pre)) % 5]
            desc = (f"{lead}. It is {width} cm wide, moves {rate} m3 of air an hour at its highest of "
                    f"{_WORDS[speeds]} speeds, energy rating {rating}.")
            return float(price), desc, palettes[i % 3], _attrs(kind_name, width, rate, speeds, rating)
        rows = lar.kind_rows(pre, 6, lar.COOKER_HOODS, "Cooker Hood", "cooker_hood", (), title, make)
        out += [replace(r, params=(("kind", shape), ("width", str(w))))
                for r, (w, *_) in zip(rows, models, strict=True)]
    return tuple(out)


SPEC = TypeSpec(
    key="cooker_hood",
    department="Home",
    product_type="Cooker Hood",
    owners=lar.OWNERS,
    rows=cooker_hood_rows(),
    decoys=(
        Decoy(1, "black cooker hood", "color", lar.decoy_row(
            "CHK001", "Chimney Cooker Hood with Black Glass Trim", lar.BRANDS[2], lar.COOKER_HOODS,
            "Cooker Hood", 239.0, "cooker_hood",
            "A chimney cooker hood in stainless steel. The trim along its canopy is black glass. It "
            "is 90 cm wide.", (lar.SILVER,),
            _attrs("Chimney Cooker Hood", 90, 620, 3, "B"),
            (("kind", "chimney"), ("width", "90")))),
    ),
)
