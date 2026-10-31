"""The breadth rows of the Cleaning & Janitorial department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_gifts import _scent
from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import Color, cw

# --------------------------------------------------------------------------
# Cleaning: the fragrance varies; the bottle or the spray is drawn.
# --------------------------------------------------------------------------

_BATHRM = ("Cleaning", "Bathroom", "Bathroom Cleaners")
_GLASS = ("Cleaning", "Kitchen & Surfaces", "Cleaners", "Glass Cleaners")
_DISH = ("Cleaning", "Kitchen & Surfaces", "Dish Soap")
_LAUND = ("Cleaning", "Laundry", "Laundry Detergent")
_SOFTEN = ("Cleaning", "Laundry", "Fabric Softener")
_LOO = ("Cleaning", "Bathroom", "Toilet Cleaners")
_AIR = ("Cleaning", "Air Care", "Air Fresheners")
_CJ = "Cleaning & Janitorial"


#: The bottle colors a cleaning row draws in.
_BOTTLE_HEX = {
    "Teal": "#1c7c7d", "Lilac": "#b9a3d0", "Blue": "#3f6fb5", "Green": "#4f7a3a",
    "White": "#ffffff", "Pink": "#f2a1b8", "Aqua": "#8fd1d0", "Yellow": "#f2d14b",
    "Cream": "#efe8d8", "Purple": "#7d5ba6",
}  # fmt: skip


def _spray(c: str, accent: str = "#2a2a2e") -> tuple[Color, ...]:
    return (cw(c, _BOTTLE_HEX[c], "solid", accent),)


CLEANING = (
    Row("BTHSPR", "Eucalyptus Bathroom Cleaner Spray 500ml", "Pantry Mill", _CJ, _BATHRM,
        "Bathroom Cleaner", 2.5, "trigger_spray",
        "Lifts limescale and soap scum from tiles, taps and glass. Scented with eucalyptus.",
        _spray("Teal"), _scent("Eucalyptus"), colorless=True),
    Row("BTHSHW", "Lavender Daily Shower Spray 750ml", "Freshfold", _CJ, _BATHRM,
        "Bathroom Cleaner", 3.5, "trigger_spray",
        "A no-rinse spray for after each shower that keeps screens and tiles clear. "
        "Scented with lavender.",
        _spray("Lilac"), _scent("Lavender"), colorless=True),
    Row("BTHMLD", "Pine Mold and Mildew Remover 500ml", "Pantry Mill", _CJ, _BATHRM,
        "Bathroom Cleaner", 3.0, "trigger_spray",
        "A thick spray for grout and sealant: leave ten minutes, then rinse. "
        "Scented with pine.",
        _spray("Green"), _scent("Pine"), colorless=True),
    Row("GLSSPR", "Ocean Breeze Glass Cleaner 500ml", "Freshfold", _CJ, _GLASS, "Glass Cleaner",
        2.0, "trigger_spray",
        "A streak-free spray for windows, mirrors and glass tables. Scented with ocean breeze.",
        _spray("Blue"), _scent("Ocean Breeze"), colorless=True),
    Row("GLSREF", "Mint Glass Cleaner Refill 1L", "Pantry Mill", _CJ, _GLASS, "Glass Cleaner",
        3.0, "bottle",
        "A refill for any trigger bottle, in a bottle made from recycled plastic. "
        "Scented with mint.",
        _spray("Aqua"), _scent("Mint"), label="Refill", colorless=True),
    Row("GLSWIP", "Eucalyptus Glass Cleaning Wipes, Pack of 40", "Freshfold", _CJ, _GLASS,
        "Glass Cleaner", 2.5, "tub",
        "Lint-free wipes for screens, mirrors and car windows. Scented with eucalyptus.",
        _spray("Teal", "#ffffff"), _scent("Eucalyptus"), label="Wipes", colorless=True),
    Row("DSHSOP", "Aloe Vera Dish Soap 500ml", "Pantry Mill", _CJ, _DISH, "Dish Soap", 1.5,
        "bottle",
        "A gentle soap that cuts grease and is kind to hands. Scented with aloe vera.",
        _spray("Green"), _scent("Aloe Vera"), label="Dish Soap", colorless=True),
    Row("DSHCON", "Green Tea Concentrated Dish Soap 1L", "Freshfold", _CJ, _DISH, "Dish Soap",
        2.8, "bottle",
        "A concentrated soap: a few drops do a sink of dishes. Scented with green tea.",
        _spray("Green", "#ffffff"), _scent("Green Tea"), label="Dish Soap", colorless=True),
    Row("DSHPMP", "Pomegranate Dish Soap Pump 400ml", "Pantry Mill", _CJ, _DISH, "Dish Soap",
        2.2, "bottle",
        "A pump bottle for the side of the sink, refillable. Scented with pomegranate.",
        _spray("Pink"), _scent("Pomegranate"), label="Pump", colorless=True),
    Row("LDRLIQ", "Fresh Cotton Laundry Detergent, 40 Washes", "Freshfold", _CJ, _LAUND,
        "Laundry Detergent", 6.0, "bottle",
        "A non-bio liquid that cleans at 20 degrees, gentle on sensitive skin. "
        "Scented with fresh cotton.",
        _spray("White", "#3f6fb5"), _scent("Fresh Cotton"), label="Detergent", colorless=True),
    Row("LDRCON", "Spring Meadow Bio Laundry Detergent, 60 Washes", "Pantry Mill", _CJ, _LAUND,
        "Laundry Detergent", 8.5, "bottle",
        "A concentrated bio liquid for stains at low temperatures. Scented with spring meadow.",
        _spray("Blue", "#ffffff"), _scent("Spring Meadow"), label="Detergent", colorless=True),
    Row("LDRPOD", "Lavender Laundry Pods, 30 Washes", "Freshfold", _CJ, _LAUND,
        "Laundry Detergent", 7.0, "tub",
        "Dissolving pods for a full drum at 30 degrees, in a child-lock tub. "
        "Scented with lavender.",
        _spray("Lilac", "#ffffff"), _scent("Lavender"), label="Pods", colorless=True),
    Row("SFTLAV", "Lavender Fabric Softener, 50 Washes", "Pantry Mill", _CJ, _SOFTEN,
        "Fabric Softener", 3.5, "bottle",
        "A softener that keeps towels fluffy and cuts creases. Scented with lavender.",
        _spray("Lilac", "#ffffff"), _scent("Lavender"), label="Softener", colorless=True),
    Row("SFTSEN", "Wild Jasmine Fabric Softener, 33 Washes", "Freshfold", _CJ, _SOFTEN,
        "Fabric Softener", 2.8, "bottle",
        "A softener with plant-based ingredients, in a recycled bottle. "
        "Scented with wild jasmine.",
        _spray("Pink", "#ffffff"), _scent("Wild Jasmine"), label="Softener", colorless=True),
    Row("LOOGEL", "Pine Thick Toilet Cleaner 750ml", "Pantry Mill", _CJ, _LOO, "Toilet Cleaner",
        1.8, "angled_bottle",
        "An angled-neck bottle of thick gel that clings under the rim. Scented with pine.",
        _spray("Green", "#ffffff"), _scent("Pine"), label="Cleaner", colorless=True),
    Row("LOOTAB", "Ocean Breeze Toilet Cleaning Tablets, Pack of 8", "Freshfold", _CJ, _LOO,
        "Toilet Cleaner", 3.0, "tub",
        "Drop-in tablets that fizz away limescale overnight. Scented with ocean breeze.",
        _spray("Aqua", "#ffffff"), _scent("Ocean Breeze"), label="Tablets", colorless=True),
    # Round 2 (gen#125): at 20K, cleaning held 22 styles against a half share of 30.
    Row("BTHLIM", "Citrus Limescale Remover Gel 750ml", "Freshfold", _CJ, _BATHRM,
        "Bathroom Cleaner", 2.8, "bottle",
        "A clinging gel for taps, shower heads and plug holes. Scented with citrus.",
        _spray("Yellow"), _scent("Citrus"), label="Gel", colorless=True),
    Row("BTHTEA", "Tea Tree Bathroom Foam Cleaner", "Pantry Mill", _CJ, _BATHRM,
        "Bathroom Cleaner", 3.2, "trigger_spray",
        "A foaming spray that sits on tiles and basins while it works. Scented with tea tree.",
        _spray("White", "#4f7a3a"), _scent("Tea Tree"), colorless=True),
    Row("GLSLEM", "Lemon Window Cleaner Concentrate", "Freshfold", _CJ, _GLASS,
        "Glass Cleaner", 3.5, "bottle",
        "Mix one capful with warm water in a bucket for windows and conservatory roofs. "
        "Scented with lemon.",
        _spray("Yellow", "#2a2a2e"), _scent("Lemon"), label="Concentrate", colorless=True),
    Row("GLSMIR", "Cucumber Mirror and Screen Spray", "Pantry Mill", _CJ, _GLASS,
        "Glass Cleaner", 2.6, "trigger_spray",
        "A fine mist that leaves no smears on mirrors, screens and shower glass. "
        "Scented with cucumber.",
        _spray("Aqua", "#ffffff"), _scent("Cucumber"), colorless=True),
    Row("DSHLEM", "Lemon Dishwashing Liquid, Value Size 1.5L", "Pantry Mill", _CJ, _DISH,
        "Dish Soap", 3.0, "bottle",
        "A family-size bottle with a flip cap, for daily washing up. Scented with lemon.",
        _spray("Yellow", "#ffffff"), _scent("Lemon"), label="Liquid", colorless=True),
    Row("DSHSEN", "Chamomile Sensitive Dish Soap", "Freshfold", _CJ, _DISH, "Dish Soap", 2.4,
        "bottle",
        "A dermatologically tested soap for dry or sensitive hands. Scented with chamomile.",
        _spray("Cream", "#4f7a3a"), _scent("Chamomile"), label="Dish Soap", colorless=True),
    Row("LDRPWD", "Cherry Blossom Laundry Powder, 50 Washes", "Pantry Mill", _CJ, _LAUND,
        "Laundry Detergent", 9.0, "box",
        "A biological powder in a cardboard box with a scoop, for whites and colors. "
        "Scented with cherry blossom.",
        _spray("Pink", "#ffffff"), _scent("Cherry Blossom"), label="Powder", colorless=True),
    Row("LDRSHT", "Sandalwood Laundry Sheets", "Freshfold", _CJ, _LAUND, "Laundry Detergent",
        6.5, "box",
        "Thin sheets that dissolve in the drum, one per load, in a plastic-free sleeve. "
        "Scented with sandalwood.",
        _spray("Cream", "#7a5a3a"), _scent("Sandalwood"), label="Sheets", colorless=True),
    Row("SFTVAN", "Vanilla Musk Fabric Conditioner", "Freshfold", _CJ, _SOFTEN,
        "Fabric Softener", 3.0, "bottle",
        "A thick conditioner for the drawer, enough for 40 loads. Scented with vanilla musk.",
        _spray("Cream", "#2a2a2e"), _scent("Vanilla Musk"), label="Softener", colorless=True,
        sizes=((850.0, 2.4), (1200.0, 3.0), (2000.0, 4.6)), size_key="net_volume_ml"),
    Row("SFTBED", "Cotton Flower Scent Booster Beads", "Pantry Mill", _CJ, _SOFTEN,
        "Fabric Softener", 5.5, "tub",
        "Beads that go in the drum with the washing and last for weeks in the wardrobe. "
        "Scented with cotton flower.",
        _spray("Purple", "#ffffff"), _scent("Cotton Flower"), label="Beads", colorless=True),
    Row("LOOBLK", "Lemon Rim Block, Twin Pack", "Pantry Mill", _CJ, _LOO, "Toilet Cleaner",
        2.0, "rim_block",
        "Hang-on rim blocks that clean and freshen with every flush. Scented with lemon.",
        _spray("Yellow", "#ffffff"), _scent("Lemon"), label="Rim Block",
        colorless=True, params=(("units", "2"),)),
    Row("LOOBLE", "Lavender Toilet Bleach 1L", "Freshfold", _CJ, _LOO, "Toilet Cleaner",
        2.0, "angled_bottle",
        "A thick bleach for under the rim that kills germs in five minutes. "
        "Scented with lavender.",
        _spray("Lilac", "#ffffff"), _scent("Lavender"), label="Bleach", colorless=True),
    Row("AIRSPR", "Fresh Linen Room Spray 300ml", "Freshfold", _CJ, _AIR, "Air Freshener",
        3.0, "trigger_spray",
        "A fine room mist that freshens soft furnishings and stale air. "
        "Scented with fresh linen.",
        _spray("White", "#3f6fb5"), _scent("Fresh Linen"), colorless=True),
    Row("AIRPLG", "Cherry Blossom Plug-In Diffuser Kit", "Pantry Mill", _CJ, _AIR,
        "Air Freshener", 5.0, "bottle",
        "A wall plug-in and one refill bottle, about 60 days on the low setting. "
        "Scented with cherry blossom.",
        _spray("Pink", "#ffffff"), _scent("Cherry Blossom"), label="Diffuser", colorless=True),
    Row("AIRREE", "Lime and Basil Reed Diffuser 100ml", "Freshfold", _CJ, _AIR,
        "Air Freshener", 9.0, "jar",
        "A glass bottle with eight rattan reeds; turn the reeds weekly. "
        "Scented with lime and basil.",
        _spray("Green", "#b08a5a"), _scent("Lime and Basil"), label="Reeds", colorless=True),
    Row("AIRGEL", "Vanilla Gel Air Freshener Pot", "Pantry Mill", _CJ, _AIR,
        "Air Freshener", 2.0, "tub",
        "A gel pot for a hallway or a small room that lasts about four weeks. "
        "Scented with vanilla.",
        _spray("Cream", "#ffffff"), _scent("Vanilla"), label="Gel", colorless=True),
    # Growth round 4: a new fragrance in each leaf, so every row in it may take one more.
    Row("LDRMEA", "Spring Meadow Laundry Liquid 1.4L", "Freshfold", _CJ, _LAUND,
        "Laundry Detergent", 7.5, "bottle",
        "A concentrated non-biological liquid for 40 washes, gentle on sensitive skin. "
        "Scented with spring meadow.",
        _spray("Aqua", "#ffffff"), _scent("Spring Meadow"), label="Liquid", colorless=True),
    Row("LDRCAP", "Ocean Breeze Laundry Capsules", "Pantry Mill", _CJ, _LAUND,
        "Laundry Detergent", 8.0, "tub",
        "Three-chamber capsules in a child-lock tub: one per load, straight into the drum. "
        "Scented with ocean breeze.",
        _spray("Blue", "#ffffff"), _scent("Ocean Breeze"), label="Capsules", colorless=True),
    Row("SFTJAS", "Jasmine Fabric Conditioner 1L", "Pantry Mill", _CJ, _SOFTEN,
        "Fabric Softener", 2.5, "bottle",
        "A light conditioner that softens towels and cuts creasing, for 33 loads. "
        "Scented with jasmine.",
        _spray("White", "#b9a3d0"), _scent("Jasmine"), label="Softener", colorless=True),
    Row("LOOTGL", "Pine Thick Toilet Gel 500ml", "Freshfold", _CJ, _LOO, "Toilet Cleaner",
        1.3, "angled_bottle",
        "An angled-neck gel that clings under the rim and lifts limescale overnight. "
        "Scented with pine.",
        _spray("Green", "#ffffff"), _scent("Pine"), label="Gel", colorless=True),
    Row("AIRAER", "Orange Blossom Air Freshener Aerosol 300ml", "Pantry Mill", _CJ, _AIR,
        "Air Freshener", 1.5, "bottle",
        "A quick burst for a kitchen or a bathroom that clears cooking smells. "
        "Scented with orange blossom.",
        _spray("Yellow", "#2a2a2e"), _scent("Orange Blossom"), label="Aerosol", colorless=True),
    Row("AIRSEA", "Sea Salt Reed Diffuser 100ml", "Pantry Mill", _CJ, _AIR, "Air Freshener",
        8.0, "jar", "A glass bottle with eight rattan reeds; turn the reeds weekly. "
        "Scented with sea salt.",
        _spray("Aqua", "#b08a5a"), _scent("Sea Salt"), label="Reeds", colorless=True),
    Row("AIRBRG", "Bergamot Room Spray 500ml", "Freshfold", _CJ, _AIR, "Air Freshener", 6.0,
        "bottle", "A fine mist for a hallway or a living room that lasts for hours. "
        "Scented with bergamot.",
        _spray("Lilac", "#2a2a2e"), _scent("Bergamot"), label="Room Spray", colorless=True),
    # gen#509: the scent sense of a plant word on a diffuser, beside the candles of GIFTS.
    Row("AIRLAV", "Lavender Reed Diffuser 100ml", "Freshfold", _CJ, _AIR, "Air Freshener",
        9.0, "jar", "A glass bottle with eight rattan reeds; turn the reeds weekly. "
        "Scented with lavender.",
        _spray("Lilac", "#b08a5a"), _scent("Lavender"), label="Reeds", colorless=True),
    Row("AIRSAG", "Sage Reed Diffuser 100ml", "Pantry Mill", _CJ, _AIR, "Air Freshener",
        9.0, "jar", "A glass bottle with eight rattan reeds; turn the reeds weekly. "
        "Scented with sage.",
        _spray("Green", "#b08a5a"), _scent("Sage"), label="Reeds", colorless=True),
    Row("AIREUC", "Eucalyptus Reed Diffuser 100ml", "Freshfold", _CJ, _AIR, "Air Freshener",
        9.0, "jar", "A glass bottle with eight rattan reeds; turn the reeds weekly. "
        "Scented with eucalyptus.",
        _spray("Teal", "#b08a5a"), _scent("Eucalyptus"), label="Reeds", colorless=True),
)  # fmt: skip
