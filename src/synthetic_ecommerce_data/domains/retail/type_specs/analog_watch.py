"""Analog Watch (gen#423): a new watch type beside the legacy ``Watch``, in Womens and Mens.

A SKU is a strap color times a case diameter in millimetres (``case_mm``, a measured option).
The strap (leather, mesh or fabric) and the case metal are drawn by :mod:`kit_jewellery`, so a
title that says "mesh" or "leather strap" is a drawing that shows it. A mesh strap is metal, so
its colors are metals; the other straps carry the six main colors (gen#275) between the styles
of each audience. The two decoys carry the word "analog" in their text and are not analog
watches for the query they target by their fields.

Each style states its ``watch_style`` (gen#1113): Dress (a thin case on leather or mesh), Sports (a
chronograph or a dive watch, water resistant to at least 100 m), Field or Everyday. A chronograph's
sub-dials and a dive watch's bezel are the ``dial`` its drawing takes, and a sports style's
silicone strap is drawn with its holes.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.audience import MENS, WOMENS
from synthetic_ecommerce_data.domains.retail.jewellery_rows import (
    BLACK,
    BLUE,
    BROWN,
    CALDERBY,
    GOLD,
    GREEN,
    HARBOUR,
    LARKMOOR,
    OWNED,
    RED,
    ROSE_GOLD,
    SILVER,
    SKERRY,
    TIDEWELL,
    WHITE,
    WRENFIELD,
    YELLOW,
    a,
    watch_row,
)
from synthetic_ecommerce_data.domains.retail.type_registry import Decoy, Option, TypeSpec

PTYPE = "Analog Watch"
WOMENS_MM = ((28, 0.0), (32, 3.0), (36, 6.0))
MENS_MM = ((40, 0.0), (42, 3.0), (44, 6.0))


def _row(code, title, brand, who, price, desc, colors, strap, case, water, strap_text, style="Everyday", dial="plain", **kw):
    mm = WOMENS_MM if who == WOMENS else MENS_MM
    params = (("strap", strap), ("case", case), *((("dial", dial),) if dial != "plain" else ()))
    return watch_row(
        code, title, brand, who, "Analog Watches", PTYPE, price, "analog_watch", desc, colors, strap_text, water,
        tuple((d, round(price + extra, 2)) for d, extra in mm), params,
        extra=(a("watch_type", "Watch type", "Analog"), a("watch_style", "Watch style", style), a("case_material", "Case material", "Stainless Steel")), **kw,
    )


SPEC = TypeSpec(
    key="analog_watch",
    department="Clothing",
    product_type=PTYPE,
    derivable=True,
    options=(Option("case_mm", "case_diameter", "Case diameter", "MMT"),),
    owners=OWNED,
    apparel_exempt="a watch: the color is the strap, not a printed or dyed garment color; it carries its own decoys (gen#423)",
    rows=(
        _row("ANWWLE", "Womens Slim Leather Strap Watch", WRENFIELD, WOMENS, 39.0,
             "A slim analog watch with a quartz movement, a plain dial and a soft leather strap.",
             (BLACK, BLUE, RED), "leather", "steel", 30, "Leather"),
        _row("ANWWFB", "Womens Woven Fabric Strap Watch", HARBOUR, WOMENS, 29.0,
             "A light analog watch with a quartz movement and a woven fabric strap that dries quickly.",
             (GREEN, YELLOW, WHITE), "fabric", "steel", 50, "Fabric"),
        _row("ANWWMS", "Womens Mesh Bracelet Watch", SKERRY, WOMENS, 49.0,
             "An analog watch on a fine mesh bracelet with a magnetic clasp and a quartz movement.",
             (GOLD, SILVER, ROSE_GOLD), "mesh", "gold", 30, "Stainless Steel Mesh"),
        _row("ANWMLE", "Mens Leather Strap Watch", CALDERBY, MENS, 55.0,
             "A classic analog watch with a quartz movement, a date window and a stitched leather strap.",
             (BLACK, WHITE, BLUE), "leather", "steel", 50, "Leather"),
        _row("ANWMFB", "Mens Fabric Strap Field Watch", TIDEWELL, MENS, 35.0,
             "A field analog watch with a clear dial, luminous hands and a tough woven fabric strap.",
             (RED, GREEN, YELLOW), "fabric", "steel", 100, "Fabric", "Field"),
        _row("ANWMMS", "Mens Mesh Bracelet Watch", WRENFIELD, MENS, 65.0,
             "An analog watch on a steel mesh bracelet with a sapphire coated glass and a quartz movement.",
             (SILVER, GOLD), "mesh", "steel", 100, "Stainless Steel Mesh"),
        _row("ANWMBR", "Mens Dress Watch with Leather Strap", HARBOUR, MENS, 75.0,
             "A thin analog dress watch with a slim case and a leather strap in a hand finished tan.",
             (BROWN, BLACK), "leather", "gold", 30, "Leather", "Dress"),
        _row("ANWWDR", "Womens Dress Watch with Leather Strap", LARKMOOR, WOMENS, 59.0,
             "A slim analog dress watch with a rose gold tone case, a plain white dial and a fine leather strap.",
             (BLACK, BROWN, RED), "leather", "rose", 30, "Leather", "Dress"),
        _row("ANWWDM", "Womens Dress Watch on a Mesh Bracelet", CALDERBY, WOMENS, 69.0,
             "An analog dress watch with a thin gold tone case and a fine mesh bracelet that closes with a sliding clasp.",
             (GOLD, ROSE_GOLD), "mesh", "gold", 30, "Stainless Steel Mesh", "Dress"),
        _row("ANWMDT", "Mens Ultra Thin Dress Watch", LARKMOOR, MENS, 89.0,
             "An ultra thin analog dress watch with a 6 mm case, a plain dial and a steel mesh bracelet.",
             (SILVER, GOLD), "mesh", "steel", 30, "Stainless Steel Mesh", "Dress"),
        _row("ANWMCH", "Mens Chronograph Sports Watch", TIDEWELL, MENS, 79.0,
             "An analog sports watch with a chronograph: three sub-dials, two pushers and a silicone strap, water resistant to 100 m.",
             (BLACK, BLUE, RED), "silicone", "steel", 100, "Silicone", "Sports", "chrono"),
        _row("ANWMDV", "Mens Dive Watch", SKERRY, MENS, 95.0,
             "A dive watch with a turning bezel, luminous hands and a silicone strap, water resistant to 200 m.",
             (BLACK, BLUE, YELLOW), "silicone", "steel", 200, "Silicone", "Sports", "dive"),
        _row("ANWWCH", "Womens Chronograph Sports Watch", HARBOUR, WOMENS, 69.0,
             "An analog sports watch with a chronograph: three sub-dials, two pushers and a silicone strap, water resistant to 100 m.",
             (WHITE, GREEN, BLUE), "silicone", "steel", 100, "Silicone", "Sports", "chrono"),
        _row("ANWWDV", "Womens Dive Watch", WRENFIELD, WOMENS, 79.0,
             "A smaller dive watch with a turning bezel, luminous hands and a silicone strap, water resistant to 200 m.",
             (WHITE, RED, BLACK), "silicone", "rose", 200, "Silicone", "Sports", "dive"),
        _row("ANWMCL", "Mens Chronograph Watch with Leather Strap", CALDERBY, MENS, 85.0,
             "An analog chronograph with three sub-dials and two pushers on a stitched leather strap, water resistant to 100 m.",
             (BROWN, BLACK), "leather", "steel", 100, "Leather", "Sports", "chrono"),
    ),
    decoys=(
        Decoy(5, "black leather watch", "color",
              _row("ANWDQZ", "Quartz Wrist Watch", SKERRY, MENS, 31.0,
                   "An analog quartz watch with a black dial and a black stitched edge on a brown leather strap.",
                   (BROWN,), "leather", "steel", 30, "Leather")),
        Decoy(4, "analog watch with date", "category",
              _row("ANWDPL", "Plain Face Watch", TIDEWELL, WOMENS, 33.0,
                   "An analog watch with a plain dial: no date window and no luminous hands.",
                   (BLACK,), "leather", "steel", 30, "Leather")),
    ),
)  # fmt: skip
