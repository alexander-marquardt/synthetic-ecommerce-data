"""Camping and fitness templates for the scaled retail catalog (gen#265): data only.

The catalog had no sports department. This is its first increment: the **Sports & Outdoors**
root with two families, Camping (tents, sleeping bags, camping chairs) and Yoga & Fitness
(yoga mats, dumbbells, kettlebells, foam rollers). The second increment (gen#368) adds yoga blocks
and straps, resistance bands, lanterns, roll mats, bike pumps (Cycling), the Baseball family (bats,
gloves, balls, batting helmets), Swimming (goggles, caps, kickboards, armbands) and Team & Racket
Sports (footballs, tennis rackets, badminton sets). Each type is a leaf with its own drawing
(:mod:`kit_sports`), its shopper attributes as structured entries, and SKUs over its color and
its own axis: a tent's berth, a sleeping bag's length in centimetres, a mat's thickness, a weight's kilograms,
a roller's length.

The tree follows the shape the maintainer's guidance asked for (department, then sport, then
equipment, with the filters each leaf carries), and every name here is invented. No leaf was
checked against a retailer's tree: ``docs/retail-sports-tree.md`` lists the filters per leaf, says
so, and gives each type not built an issue or a reason (gen#290).

Every type offers the six main colors across its styles (gen#275). A measured axis (``berth``,
``thickness_mm``, ``weight_kg``, ``length_cm``) is on the SKUs alone, which the export states
with its unit (``export.OPTIONS``). These styles are templates only: :func:`scale.derivable`
leaves them out, as it does the accessory and household rows, so the department grows by
authored rows.
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import kit_sports  # noqa: F401 -- registers tent, sleeping_bag, camp_chair, yoga_mat, ...
from breadth_rows import Row
from variants import cw

from synthetic_ecommerce_data.core.entry import canonical

DEPARTMENT = "Sports & Outdoors"
_W, _H, _L = "Wrenfield", "Harbour & Pine", "Larkmoor"
_SO = DEPARTMENT
_TENTS = (_SO, "Camping", "Tents")
_CAMP = (_SO, "Camping")
_YOGA = (_SO, "Yoga & Fitness", "Yoga")
_WEIGHTS = (_SO, "Yoga & Fitness", "Weights")
_FIT = (_SO, "Yoga & Fitness")

RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
BLACK = cw("Black", "#2d2d33")
WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
ORANGE = cw("Orange", "#e07a1f")
GREY = cw("Grey", "#9a9ca0")


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _kg(key: str, name: str, kg: int) -> tuple[str, str, str, str, float]:
    """A weight in kilograms: the canonical value is in grams, as the core's ``KGM`` says."""
    return (key, name, str(kg), "KGM", float(canonical(str(kg), "KGM")))


def _mm(key: str, name: str, mm: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(mm), "MMT", float(mm))


def _season(n: int) -> tuple[str, str, str]:
    return _a("season_rating", "Season rating", f"{n} Season")


def _axis(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    """SKU values of a measured axis and the price at each."""
    return tuple((f"{v:g}", p) for v, p in pairs)


def _row(code: str, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, description: str, colors: tuple, attrs: tuple, sizes: tuple = (),
         size_key: str = "size", params: tuple = ()) -> Row:  # fmt: skip
    return Row(code, title, brand, DEPARTMENT, path, ptype, price, shape, description, colors,
               attrs, sizes, size_key=size_key, params=params)  # fmt: skip


# --------------------------------------------------------------------------
# Camping: the shell, bag or chair is drawn; berth, length and color are SKUs.
# --------------------------------------------------------------------------

_BERTHS = (2, 3, 4)

TENTS = (
    _row("TNTDOM", "Compact Dome Tent", _W, (*_TENTS, "Dome Tents"), "Tent", 49.0, "tent",
         "A two-pole dome tent with a sewn-in groundsheet and a porch door, quick to pitch for a "
         "weekend away.",
         (GREEN, BLUE, ORANGE, RED),
         (_a("tent_type", "Tent type", "Dome"), _season(3), _mm("hydrostatic_head", "Hydrostatic head", 3000),
          _a("material", "Material", "Polyester")),
         _axis((2, 49.0), (3, 59.0), (4, 72.0)), "berth", (("style", "dome"),)),
    _row("TNTBPK", "Lightweight Backpacking Dome Tent", _H, (*_TENTS, "Dome Tents"), "Tent", 89.0,
         "tent", "A light dome tent that packs small for the trail, with a taped flysheet and "
         "two guy lines.",
         (YELLOW, BLACK, GREEN, BLUE),
         (_a("tent_type", "Tent type", "Dome"), _season(4), _mm("hydrostatic_head", "Hydrostatic head", 4000),
          _a("material", "Material", "Ripstop Nylon")),
         _axis((1, 89.0), (2, 109.0), (3, 135.0)), "berth", (("style", "dome"),)),
    _row("TNTFAM", "Family Tunnel Tent", _L, (*_TENTS, "Tunnel Tents"), "Tent", 149.0, "tent",
         "A tunnel tent with a living area and separate sleeping pods, roomy enough to stand up "
         "in and stay dry on a wet weekend.",
         (WHITE, BLUE, GREEN, GREY),
         (_a("tent_type", "Tent type", "Tunnel"), _season(3), _mm("hydrostatic_head", "Hydrostatic head", 3000),
          _a("material", "Material", "Polyester")),
         _axis((4, 149.0), (6, 219.0), (8, 289.0)), "berth", (("style", "tunnel"),)),
    _row("TNTTRK", "Two Pole Tunnel Tent", _W, (*_TENTS, "Tunnel Tents"), "Tent", 119.0, "tent",
         "A low tunnel tent on two poles that pitches fast and holds up in the wind, with a "
         "vestibule for boots and bags.",
         (RED, YELLOW, BLACK, ORANGE),
         (_a("tent_type", "Tent type", "Tunnel"), _season(4), _mm("hydrostatic_head", "Hydrostatic head", 5000),
          _a("material", "Material", "Ripstop Nylon")),
         _axis((2, 119.0), (3, 149.0)), "berth", (("style", "tunnel"),)),
)

def _lengths(base: float) -> tuple[tuple[str, float], ...]:
    """A sleeping bag's SKU lengths in centimetres (a measured axis, no garment size), and the
    price at each."""
    return _axis((190, base), (210, base + 6.0))


SLEEPING_BAGS = (
    _row("SLPMUM", "Three Season Mummy Sleeping Bag", _W, (*_CAMP, "Sleeping Bags"), "Sleeping Bag",
         39.0, "sleeping_bag", "A tapered mummy bag with a hood and a two-way zip, warm enough for "
         "spring to autumn camping and light to carry.",
         (BLUE, GREEN, YELLOW, RED),
         (_a("bag_shape", "Bag shape", "Mummy"), _season(3), _a("fill", "Fill", "Hollow Fibre"),
          _a("material", "Material", "Polyester")),
         _lengths(39.0), "length_cm", (("style", "mummy"),)),
    _row("SLPWIN", "Four Season Mummy Sleeping Bag", _H, (*_CAMP, "Sleeping Bags"), "Sleeping Bag",
         79.0, "sleeping_bag", "A snug mummy bag with a draught collar and a deep hood for cold "
         "nights, packing into its own stuff sack.",
         (BLACK, WHITE, BLUE, GREEN),
         (_a("bag_shape", "Bag shape", "Mummy"), _season(4), _a("fill", "Fill", "Hollow Fibre"),
          _a("material", "Material", "Ripstop Nylon")),
         _lengths(79.0), "length_cm", (("style", "mummy"),)),
    _row("SLPRCT", "Two Season Rectangular Sleeping Bag", _L, (*_CAMP, "Sleeping Bags"),
         "Sleeping Bag", 24.0, "sleeping_bag", "A roomy rectangular bag that unzips flat to use as "
         "a quilt, for summer nights and sleepovers.",
         (RED, BLUE, GREEN, YELLOW),
         (_a("bag_shape", "Bag shape", "Rectangular"), _season(2), _a("fill", "Fill", "Hollow Fibre"),
          _a("material", "Material", "Polyester")),
         _lengths(24.0), "length_cm", (("style", "rectangular"),)),
)

CHAIRS = (
    _row("CHRFLD", "Folding Camping Chair", _W, (*_CAMP, "Camping Chairs"), "Camping Chair", 18.0,
         "camp_chair", "A light folding chair with a steel frame and a padded seat that packs into "
         "a carry bag.",
         (RED, BLUE, GREEN, YELLOW),
         (_a("frame_material", "Frame material", "Steel"), _kg("max_load_kg", "Maximum load", 100),
          _a("arms", "Arms", "No")),
         (), "size", (("arms", "no"),)),
    _row("CHRARM", "Folding Camping Armchair with Cup Holder", _H, (*_CAMP, "Camping Chairs"),
         "Camping Chair", 29.0, "camp_chair", "A folding armchair with a high back, padded arms and "
         "a cup holder, for long evenings round the fire.",
         (BLACK, WHITE, BLUE, GREEN),
         (_a("frame_material", "Frame material", "Steel"), _kg("max_load_kg", "Maximum load", 120),
          _a("arms", "Arms", "Yes")),
         (), "size", (("arms", "yes"),)),
)

# --------------------------------------------------------------------------
# Yoga and fitness: the kit is drawn; thickness, weight and length are SKUs.
# --------------------------------------------------------------------------

YOGA_MATS = (
    _row("YGMFLT", "Non-Slip Yoga Mat", _L, (*_YOGA, "Yoga Mats"), "Yoga Mat", 16.0, "yoga_mat",
         "A grippy mat with a textured top that stays put through a long flow, in a choice of "
         "thickness.",
         (BLUE, GREEN, RED, YELLOW),
         (_a("material", "Material", "PVC"), _a("surface", "Surface", "Non-Slip")),
         _axis((4, 16.0), (6, 20.0), (8, 25.0)), "thickness_mm", (("state", "flat"),)),
    _row("YGMTRV", "Foldable Travel Yoga Mat", _H, (*_YOGA, "Yoga Mats"), "Yoga Mat", 22.0,
         "yoga_mat", "A thin mat that rolls up small and fits in a bag, for the studio and "
         "for holidays.",
         (BLACK, WHITE, BLUE, GREEN),
         (_a("material", "Material", "Natural Rubber"), _a("surface", "Surface", "Suede")),
         _axis((1, 22.0), (2, 26.0)), "thickness_mm", (("state", "rolled"),)),
)

DUMBBELLS = (
    _row("DMBHEX", "Hex Rubber Dumbbell", _W, (*_WEIGHTS, "Dumbbells"), "Dumbbell", 14.0,
         "dumbbell", "A cast iron dumbbell in a rubber coat with hex heads that do not roll, "
         "sold singly in a range of weights.",
         (BLACK, BLUE),
         (_a("material", "Material", "Rubber Coated Iron"), _a("head_shape", "Head shape", "Hex"),
          _a("sold_as", "Sold as", "Single")),
         _axis((2, 14.0), (4, 24.0), (6, 34.0), (8, 44.0)), "weight_kg", (("style", "hex"),)),
    _row("DMBNEO", "Neoprene Dumbbell", _L, (*_WEIGHTS, "Dumbbells"), "Dumbbell", 6.0, "dumbbell",
         "A soft-coated dumbbell with a comfortable grip for home workouts, sold singly in a "
         "range of weights.",
         (RED, GREEN, YELLOW, WHITE),
         (_a("material", "Material", "Neoprene Coated Iron"), _a("head_shape", "Head shape", "Round"),
          _a("sold_as", "Sold as", "Single")),
         _axis((1, 6.0), (2, 9.0), (3, 12.0)), "weight_kg", (("style", "round"),)),
)

KETTLEBELLS = (
    _row("KTBCST", "Cast Iron Kettlebell", _H, (*_WEIGHTS, "Kettlebells"), "Kettlebell", 24.0,
         "kettlebell", "A solid cast kettlebell with a wide handle for swings, squats and "
         "presses.",
         (BLACK, BLUE),
         (_a("material", "Material", "Cast Iron"),),
         _axis((8, 24.0), (12, 34.0), (16, 44.0), (20, 54.0)), "weight_kg"),
    _row("KTBVIN", "Vinyl Coated Kettlebell", _W, (*_WEIGHTS, "Kettlebells"), "Kettlebell", 15.0,
         "kettlebell", "A kettlebell in a smooth vinyl coat that protects the floor, in light "
         "weights for beginners.",
         (RED, GREEN, YELLOW, WHITE),
         (_a("material", "Material", "Vinyl Coated Iron"),),
         _axis((4, 15.0), (6, 20.0), (8, 25.0)), "weight_kg"),
)

FOAM_ROLLERS = (
    _row("FMRSMT", "Smooth Foam Roller", _L, (*_FIT, "Foam Rollers"), "Foam Roller", 12.0,
         "foam_roller", "A firm foam roller with a smooth surface for stretching and easing tired "
         "muscles after a run.",
         (BLACK, BLUE, GREEN, RED),
         (_a("surface", "Surface", "Smooth"), _a("material", "Material", "EVA Foam")),
         _axis((33, 12.0), (45, 15.0), (60, 19.0)), "length_cm", (("texture", "smooth"),)),
    _row("FMRGRD", "Grid Foam Roller", _H, (*_FIT, "Foam Rollers"), "Foam Roller", 18.0,
         "foam_roller", "A foam roller with a grid of raised bumps for deeper massage along the "
         "back and legs.",
         (YELLOW, WHITE, BLUE, BLACK),
         (_a("surface", "Surface", "Grid"), _a("material", "Material", "EVA Foam")),
         _axis((33, 18.0), (45, 22.0)), "length_cm", (("texture", "grid"),)),
)


# --------------------------------------------------------------------------
# Second increment (gen#368): the remainder of gen#265. Every type has two styles from two
# brands; the two styles' colors together cover the six main colors.
# --------------------------------------------------------------------------

_CYCLING = (_SO, "Cycling", "Bike Pumps")
_BASEBALL = (_SO, "Baseball")
_SWIM = (_SO, "Swimming")
_TEAM = (_SO, "Team & Racket Sports")
_PRIMARY = (RED, BLUE, GREEN, YELLOW)
_NEUTRAL = (BLACK, WHITE, BLUE, GREEN)


def _cm(key: str, name: str, cm: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(cm), "CMT", float(cm * 10))


def _words(*pairs: tuple[str, float]) -> tuple[tuple[str, float], ...]:
    """A SKU axis of words (a resistance level, a grip size) and the price at each."""
    return pairs


YOGA_BLOCKS = (
    _row("YGBFOM", "Foam Yoga Block", _L, (*_YOGA, "Yoga Blocks"), "Yoga Block", 7.0, "yoga_block",
         "A firm EVA foam block to lift the floor closer in seated poses and deepen a stretch, sold singly.",
         _PRIMARY, (_a("material", "Material", "EVA Foam"), _a("sold_as", "Sold as", "Single")),
         _axis((7.5, 7.0), (10, 9.0)), "height_cm", (("material", "foam"),)),
    _row("YGBCRK", "Cork Yoga Block", _H, (*_YOGA, "Yoga Blocks"), "Yoga Block", 14.0, "yoga_block",
         "A dense natural cork block with a grippy surface that does not slip under damp hands, sold as a pair.",
         _NEUTRAL, (_a("material", "Material", "Cork"), _a("sold_as", "Sold as", "Pair")),
         _axis((7.5, 14.0), (10, 17.0)), "height_cm", (("material", "cork"),)),
)

YOGA_STRAPS = (
    _row("YGSRNG", "Cotton Yoga Strap with D-Rings", _W, (*_YOGA, "Yoga Straps"), "Yoga Strap", 6.0,
         "yoga_strap", "A woven cotton strap with two D-rings that hold a loop at any length, for binds and long holds.",
         _PRIMARY, (_a("material", "Material", "Cotton"), _a("closure", "Closure", "D-Ring")),
         _axis((183, 6.0), (244, 8.0)), "length_cm", (("buckle", "ring"),)),
    _row("YGSCLP", "Nylon Yoga Strap with Quick Clip", _H, (*_YOGA, "Yoga Straps"), "Yoga Strap", 9.0,
         "yoga_strap", "A soft nylon strap with a quick-release clip that snaps shut in one move and holds under tension.",
         _NEUTRAL, (_a("material", "Material", "Nylon"), _a("closure", "Closure", "Clip")),
         _axis((183, 9.0), (244, 11.0)), "length_cm", (("buckle", "clip"),)),
)

RESISTANCE_BANDS = (
    _row("RSBLOP", "Fabric Loop Resistance Band", _L, (*_FIT, "Resistance Bands"), "Resistance Band", 8.0,
         "resistance_band", "A wide woven loop band that stays put on the thighs for glute and hip work.",
         _PRIMARY, (_a("band_type", "Band type", "Loop"), _a("material", "Material", "Cotton blend")),
         _words(("Light", 8.0), ("Medium", 9.0), ("Heavy", 10.0)), "resistance", (("form", "loop"),)),
    _row("RSBTUB", "Tube Resistance Band with Handles", _W, (*_FIT, "Resistance Bands"), "Resistance Band", 12.0,
         "resistance_band", "A latex tube band with a handle at each end for rows, presses and curls anywhere.",
         _NEUTRAL, (_a("band_type", "Band type", "Tube"), _a("material", "Material", "Latex")),
         _words(("Light", 12.0), ("Medium", 14.0), ("Heavy", 16.0)), "resistance", (("form", "tube"),)),
)

LANTERNS = (
    _row("LNTLED", "Rechargeable LED Camping Lantern", _H, (*_CAMP, "Lanterns"), "Camping Lantern", 18.0,
         "lantern", "A bright LED lantern with a hanging hook, charged over USB and dimmable for the tent or the table.",
         _NEUTRAL, (_a("power", "Power", "Rechargeable"), _a("material", "Material", "ABS Plastic")),
         _words(("200", 18.0), ("400", 24.0), ("800", 34.0)), "brightness_lm", (("style", "led"),)),
    _row("LNTCLP", "Collapsible Battery Camping Lantern", _W, (*_CAMP, "Lanterns"), "Camping Lantern", 11.0,
         "lantern", "A pleated lantern that pushes flat for the pack and pulls up to light a whole picnic table.",
         _PRIMARY, (_a("power", "Power", "Battery"), _a("material", "Material", "Silicone")),
         _words(("150", 11.0), ("300", 15.0)), "brightness_lm", (("style", "collapsible"),)),
)

ROLL_MATS = (
    _row("RMTRLL", "Closed Cell Foam Roll Mat", _L, (*_CAMP, "Roll Mats"), "Roll Mat", 12.0, "roll_mat",
         "A light rolled foam mat that insulates from cold ground and straps to the outside of a rucksack.",
         _PRIMARY, (_a("material", "Material", "Closed Cell Foam"), _a("fold", "Fold", "Roll")),
         _axis((8, 12.0), (10, 15.0), (15, 20.0)), "thickness_mm", (("form", "rolled"),)),
    _row("RMTZFD", "Z-Fold Camping Mat", _W, (*_CAMP, "Roll Mats"), "Roll Mat", 16.0, "roll_mat",
         "A concertina mat that folds into a flat stack, with a ridged top that traps warmth.",
         _NEUTRAL, (_a("material", "Material", "EVA Foam"), _a("fold", "Fold", "Z-Fold")),
         _axis((14, 16.0), (20, 21.0)), "thickness_mm", (("form", "folded"),)),
)

BIKE_PUMPS = (
    _row("PMPFLR", "Floor Pump with Pressure Gauge", "Stridewell", (*_CYCLING,), "Bike Pump", 24.0, "bike_pump",
         "A steel-based floor pump with a wide gauge and a locking head that fits both valve types.",
         _PRIMARY, (_a("pump_type", "Pump type", "Floor"), _a("valve_type", "Valve type", "Presta and Schrader"),
                    _a("max_pressure", "Maximum pressure (psi)", "160")),
         (), "size", (("style", "floor"),)),
    _row("PMPHND", "Mini Hand Pump", _H, (*_CYCLING,), "Bike Pump", 12.0, "bike_pump",
         "A pocket hand pump with a fold-out foot peg and a short hose, for a puncture on the road.",
         _NEUTRAL, (_a("pump_type", "Pump type", "Hand"), _a("valve_type", "Valve type", "Presta and Schrader"),
                    _a("max_pressure", "Maximum pressure (psi)", "100")),
         (), "size", (("style", "hand"),)),
)

BASEBALL_BATS = (
    _row("BBTWOD", "Maple Baseball Bat", _W, (*_BASEBALL, "Baseball Bats"), "Baseball Bat", 38.0, "baseball_bat",
         "A turned maple bat with a balanced swing weight and a flared knob, for batting practice.",
         _NEUTRAL, (_a("material", "Material", "Maple"), _mm("barrel_diameter", "Barrel diameter", 64)),
         _axis((76, 38.0), (81, 40.0), (86, 42.0)), "length_cm", (("material", "wood"),)),
    _row("BBTALY", "Alloy Youth Baseball Bat", _L, (*_BASEBALL, "Baseball Bats"), "Baseball Bat", 44.0, "baseball_bat",
         "A lightweight alloy bat with a cushioned grip and a large barrel, for young hitters learning the swing.",
         _PRIMARY, (_a("material", "Material", "Aluminum Alloy"), _mm("barrel_diameter", "Barrel diameter", 69)),
         _axis((71, 44.0), (76, 47.0), (81, 50.0)), "length_cm", (("material", "alloy"),)),
)

BASEBALL_GLOVES = (
    _row("BGLINF", "Infield Baseball Glove", _H, (*_BASEBALL, "Baseball Gloves"), "Baseball Glove", 36.0,
         "baseball_glove", "A short-webbed leather glove with a shallow pocket for a quick transfer from glove to hand.",
         _NEUTRAL, (_a("material", "Material", "Leather"), _a("position", "Position", "Infield")),
         _axis((10.5, 36.0), (11.5, 42.0)), "glove_size_in", (("position", "infield"),)),
    _row("BGLOUT", "Outfield Baseball Glove", _L, (*_BASEBALL, "Baseball Gloves"), "Baseball Glove", 32.0,
         "baseball_glove", "A long glove with a deep web and a padded palm, built to reach and hold fly balls.",
         _PRIMARY, (_a("material", "Material", "Synthetic Leather"), _a("position", "Position", "Outfield")),
         _axis((11.5, 32.0), (12.5, 38.0)), "glove_size_in", (("position", "outfield"),)),
)

BASEBALLS = (
    _row("BBLLTH", "Leather Match Baseball", _W, (*_BASEBALL, "Baseballs"), "Baseball", 6.0, "baseball",
         "A cork-centered ball in a stitched leather cover, for match play and hard batting practice.",
         _NEUTRAL, (_a("cover", "Cover", "Leather"), _a("level", "Level", "Match"), _a("sold_as", "Sold as", "Single")),
         (), "size", (("cover", "leather"),)),
    _row("BBLPRC", "Soft Synthetic Practice Baseballs", _L, (*_BASEBALL, "Baseballs"), "Baseball", 14.0, "baseball",
         "A pack of six soft-core practice balls with a synthetic cover that is kind to hands and windows.",
         _PRIMARY, (_a("cover", "Cover", "Synthetic"), _a("level", "Level", "Practice"), _a("sold_as", "Sold as", "Pack of 6")),
         (), "size", (("cover", "synthetic"),)),
)

BATTING_HELMETS = (
    _row("BHLSNG", "Batting Helmet with Single Ear Flap", _H, (*_BASEBALL, "Batting Helmets"), "Batting Helmet", 29.0,
         "batting_helmet", "A hard-shell batting helmet with a flap over the ear facing the pitcher and a vented crown.",
         _NEUTRAL, (_a("material", "Material", "ABS Shell"), _a("ear_flaps", "Ear flaps", "Single")),
         _axis((54, 29.0), (57, 29.0), (60, 31.0)), "head_cm", (("flaps", "single"),)),
    _row("BHLDBL", "Batting Helmet with Double Ear Flaps", _W, (*_BASEBALL, "Batting Helmets"), "Batting Helmet", 34.0,
         "batting_helmet", "A batting helmet with flaps over both ears and a foam liner, for youth leagues that require them.",
         _PRIMARY, (_a("material", "Material", "ABS Shell"), _a("ear_flaps", "Ear flaps", "Double")),
         _axis((52, 34.0), (55, 34.0), (58, 36.0)), "head_cm", (("flaps", "double"),)),
)

SWIM_GOGGLES = (
    _row("SGGCLR", "Anti-Fog Swimming Goggles", _L, (*_SWIM, "Swimming Goggles"), "Swim Goggles", 9.0,
         "swim_goggles", "Comfortable training goggles with clear lenses, an anti-fog coating and a soft silicone seal.",
         _PRIMARY, (_a("lens", "Lens", "Clear"), _a("anti_fog", "Anti-fog", "Yes"), _a("strap_material", "Strap material", "Silicone")),
         (), "size", (("lens", "clear"),)),
    _row("SGGMIR", "Mirrored Racing Swimming Goggles", _H, (*_SWIM, "Swimming Goggles"), "Swim Goggles", 16.0,
         "swim_goggles", "Low-profile racing goggles with mirrored lenses that cut glare in an outdoor pool.",
         _NEUTRAL, (_a("lens", "Lens", "Mirrored"), _a("anti_fog", "Anti-fog", "Yes"), _a("strap_material", "Strap material", "Silicone")),
         (), "size", (("lens", "mirrored"),)),
)

SWIM_CAPS = (
    _row("SCPSIL", "Silicone Swim Cap", _W, (*_SWIM, "Swim Caps"), "Swim Cap", 6.0, "swim_cap",
         "A smooth, stretchy swim cap that keeps hair dry and cuts drag, free of latex.",
         _PRIMARY, (_a("material", "Material", "Silicone"), _a("latex_free", "Latex free", "Yes")),
         (), "size", (("material", "silicone"),)),
    _row("SCPLYC", "Lycra Swim Cap", _L, (*_SWIM, "Swim Caps"), "Swim Cap", 5.0, "swim_cap",
         "A soft panelled fabric cap for easy pulling on and long wear, a gentler fit for the pool.",
         _NEUTRAL, (_a("material", "Material", "Lycra"), _a("latex_free", "Latex free", "Yes")),
         (), "size", (("material", "lycra"),)),
)

KICKBOARDS = (
    _row("KBDPLN", "Foam Kickboard", _H, (*_SWIM, "Kickboards"), "Kickboard", 8.0, "kickboard",
         "A buoyant EVA foam float for kick sets, with a smooth finish and rounded edges.",
         _PRIMARY, (_a("material", "Material", "EVA Foam"), _a("grips", "Grips", "None")),
         _axis((38, 8.0), (42, 10.0)), "length_cm", (("grips", "none"),)),
    _row("KBDCUT", "Kickboard with Hand Cut-Outs", _W, (*_SWIM, "Kickboards"), "Kickboard", 11.0, "kickboard",
         "A kickboard with two cut-out hand holds for a secure grip through long sets.",
         _NEUTRAL, (_a("material", "Material", "EVA Foam"), _a("grips", "Grips", "Cut-Out Grips")),
         _axis((40, 11.0), (45, 13.0)), "length_cm", (("grips", "cutouts"),)),
)

SWIM_ARMBANDS = (
    _row("ARMTWO", "Two Chamber Swimming Armbands", _L, (*_SWIM, "Swim Armbands"), "Swim Armbands", 4.0,
         "swim_armbands", "Inflatable armbands with two air chambers each, for children learning to float.",
         _PRIMARY, (_a("material", "Material", "PVC"), _a("chambers", "Chambers", "Two")),
         _axis((15, 4.0), (30, 5.0)), "max_load_kg", (("chambers", "two"),)),
    _row("ARMTHR", "Three Chamber Swimming Armbands", _H, (*_SWIM, "Swim Armbands"), "Swim Armbands", 6.0,
         "swim_armbands", "Armbands with three separate air chambers, so one leak never takes away all the lift.",
         _NEUTRAL, (_a("material", "Material", "PVC"), _a("chambers", "Chambers", "Three")),
         _axis((15, 6.0), (30, 7.0)), "max_load_kg", (("chambers", "three"),)),
)

FOOTBALLS = (
    _row("FBLCLS", "Classic Panel Football", _W, (*_TEAM, "Footballs"), "Football", 12.0, "football",
         "A machine-stitched football with the classic pentagon panels, for training and park games.",
         _NEUTRAL, (_a("cover", "Cover", "Synthetic Leather"), _a("construction", "Construction", "Machine Stitched")),
         _axis((3, 10.0), (4, 11.0), (5, 12.0)), "ball_size", (("panels", "classic"),)),
    _row("FBLMOD", "Thermal Bonded Match Football", _L, (*_TEAM, "Footballs"), "Football", 26.0, "football",
         "A seamless match football with bonded panels that keep their shape and take on no water.",
         _PRIMARY, (_a("cover", "Cover", "Polyurethane"), _a("construction", "Construction", "Thermal Bonded")),
         _axis((4, 24.0), (5, 26.0)), "ball_size", (("panels", "modern"),)),
)

TENNIS_RACKETS = (
    _row("TRKOPN", "Graphite Tennis Racket with Open String Pattern", _H, (*_TEAM, "Tennis Rackets"), "Tennis Racket", 54.0,
         "tennis_racket", "A graphite racket with an open string pattern for spin and power, strung and ready to play.",
         _NEUTRAL, (_a("material", "Material", "Graphite"), _a("head_size", "Head size (sq in)", "100")),
         _words(("L1", 54.0), ("L2", 54.0), ("L3", 54.0)), "grip", (("strings", "open"),)),
    _row("TRKDNS", "Aluminum Tennis Racket with Dense String Pattern", _W, (*_TEAM, "Tennis Rackets"), "Tennis Racket", 28.0,
         "tennis_racket", "A tough aluminum racket with a dense string pattern for control, a good first racket.",
         _PRIMARY, (_a("material", "Material", "Aluminum"), _a("head_size", "Head size (sq in)", "105")),
         _words(("L1", 28.0), ("L2", 28.0)), "grip", (("strings", "dense"),)),
)

BADMINTON_SETS = (
    _row("BDMTWO", "Badminton Set for Two Players", _L, (*_TEAM, "Badminton Sets"), "Badminton Set", 18.0,
         "badminton_set", "Two steel-framed rackets and shuttlecocks in a carry bag, for the garden or the beach.",
         _PRIMARY, (_a("material", "Material", "Steel"), _a("net_included", "Net included", "No")),
         _axis((2, 18.0)), "players", (("players", "2"),)),
    _row("BDMFOU", "Badminton Set with Net for Four Players", _W, (*_TEAM, "Badminton Sets"), "Badminton Set", 42.0,
         "badminton_set", "Four aluminum rackets, a portable net with posts and a tube of shuttlecocks.",
         _NEUTRAL, (_a("material", "Material", "Aluminum"), _a("net_included", "Net included", "Yes")),
         _axis((4, 42.0)), "players", (("players", "4"),)),
)

ROWS = (
    *TENTS, *SLEEPING_BAGS, *CHAIRS, *YOGA_MATS, *DUMBBELLS, *KETTLEBELLS, *FOAM_ROLLERS,
    *YOGA_BLOCKS, *YOGA_STRAPS, *RESISTANCE_BANDS, *LANTERNS, *ROLL_MATS, *BIKE_PUMPS,
    *BASEBALL_BATS, *BASEBALL_GLOVES, *BASEBALLS, *BATTING_HELMETS, *SWIM_GOGGLES, *SWIM_CAPS,
    *KICKBOARDS, *SWIM_ARMBANDS, *FOOTBALLS, *TENNIS_RACKETS, *BADMINTON_SETS,
)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
