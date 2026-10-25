"""Fridges and freezers (gen#334): eight kinds of six models in Home > Large Appliances.

70/30 and 50/50 fridge freezers, an American style side-by-side, an under-counter fridge, a
larder fridge, a chest freezer, an upright freezer and an integrated fridge, drawn by
:func:`kit_large_appliances.fridge`. A model's capacity, width, energy rating and frost-free
entry are structured; its finish is the SKU's color. The retro 50/50 models come in the six
main colors (gen#275). The two color decoys name a color in the title that the product is not:
a "Black Edition" fridge that is stainless steel, a "Red Line" larder fridge that is white.
Every brand name is invented. Not derivable: the range is authored.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from dataclasses import replace

import large_appliance_rows as lar
from breadth_rows import Row
from type_registry import Decoy, TypeSpec, a

_PTYPE = "Fridge & Freezer"

#: Per kind: (capacity L, width cm, price) of each of its six models.
_FRIDGE_KINDS = (
    ("FFA", "fridge_freezer_7030", "70/30 Fridge Freezer", "Fridge Freezer 70/30",
     "A tall fridge freezer, 70% fridge above and 30% freezer below",
     ((260, 55, 349), (290, 55, 399), (320, 60, 449), (345, 60, 499), (370, 60, 549), (400, 70, 649))),
    ("FFB", "fridge_freezer_5050", "50/50 Fridge Freezer", "Fridge Freezer 50/50",
     "A tall fridge freezer with the fridge and the freezer the same size",
     ((240, 55, 329), (270, 55, 379), (300, 60, 429), (330, 60, 479), (255, 55, 449), (285, 55, 499))),
    ("FSS", "side_by_side", "American Style Side-by-Side Fridge Freezer", "Side-by-Side",
     "An American style fridge freezer with two tall doors side by side",
     ((490, 91, 899), (530, 91, 999), (560, 91, 1099), (600, 91, 1199), (620, 91, 1349), (650, 91, 1499))),
    ("FUC", "under_counter", "Under-Counter Fridge", "Under-Counter Fridge",
     "A fridge that fits under a worktop",
     ((95, 48, 159), (110, 50, 179), (120, 55, 189), (130, 55, 209), (135, 60, 219), (150, 60, 249))),
    ("FLR", "larder", "Larder Fridge", "Larder Fridge",
     "A tall fridge that is all fridge, with shelves from top to bottom",
     ((260, 55, 299), (290, 55, 339), (310, 60, 369), (330, 60, 399), (350, 60, 429), (370, 70, 479))),
    ("FCH", "chest", "Chest Freezer", "Chest Freezer",
     "A freezer with a lid on top and one deep space",
     ((100, 55, 199), (142, 70, 239), (198, 85, 279), (250, 105, 319), (300, 126, 369), (385, 143, 429))),
    ("FUP", "upright_freezer", "Upright Freezer", "Upright Freezer",
     "A tall freezer with drawers",
     ((85, 55, 249), (120, 55, 289), (168, 60, 329), (190, 60, 369), (210, 60, 399), (240, 70, 449))),
    ("FIN", "integrated", "Integrated Fridge Freezer", "Integrated Fridge",
     "A fridge freezer that fits behind a kitchen cabinet door",
     ((220, 54, 499), (250, 54, 549), (270, 56, 599), (290, 56, 649), (250, 54, 579), (280, 56, 699))),
)  # fmt: skip


def fridge_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, lead, models in _FRIDGE_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, pre=pre):
            cap, width, price = models[i]
            frost_free = i % 3 != 2 or pre in {"FSS", "FCH"}
            retro = pre == "FFB" and i >= 4
            rating = lar.RATINGS[(i + len(pre)) % 5]
            desc = (f"{lead}. {cap} litres in all, {width} cm wide, energy rating {rating}"
                    f"{', frost free' if frost_free else ', manual defrost'}"
                    f"{'. A retro shape with rounded corners' if retro else ''}.")
            colors = lar.SIX if retro else lar.PALETTES[i % 3]
            attrs = (a("appliance_type", "Type", kind_name), lar.litres(cap), lar.cm(width),
                     a("energy_rating", "Energy rating", rating), lar.yn("frost_free", "Frost free", frost_free))
            return float(price), desc, colors, attrs
        rows = lar.kind_rows(pre, 6, lar.FRIDGES, "Fridge & Freezer", "fridge", (("kind", shape),), title, make)
        if pre == "FFB":
            rows = tuple(
                r if i < 4 else replace(r, title=r.title.replace(title, f"Retro {title}"))
                for i, r in enumerate(rows)
            )
        out += rows
    return tuple(out)


SPEC = TypeSpec(
    key="fridge_freezer",
    department="Home",
    product_type=_PTYPE,
    owners=lar.OWNERS,
    rows=fridge_rows(),
    decoys=(
        Decoy(4, "black fridge", "color", lar.decoy_row(
            "FDB001", "Black Edition Fridge Freezer", lar.BRANDS[0], lar.FRIDGES, _PTYPE,
            449.0, "fridge", "The Black Edition range in brushed stainless steel, a 70/30 fridge "
            "freezer with frost free cooling.", (lar.SILVER,),
            (a("appliance_type", "Type", "Fridge Freezer 70/30"), lar.litres(310),
             a("finish", "Finish", "Stainless Steel")),
            params=(("kind", "fridge_freezer_7030"),))),
        Decoy(1, "red fridge", "color", lar.decoy_row(
            "FDB002", "Red Line Larder Fridge", lar.BRANDS[1], lar.FRIDGES, _PTYPE, 329.0,
            "fridge", "A larder fridge from the Red Line range, finished in white, with glass shelves.",
            (lar.WHITE,), (a("appliance_type", "Type", "Larder Fridge"), lar.litres(300)),
            params=(("kind", "larder"),))),
    ),
)
