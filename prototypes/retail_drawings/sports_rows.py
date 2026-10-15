"""Camping and fitness templates for the scaled retail catalog (gen#265): data only.

The catalog had no sports department. This is its first increment: the **Sports & Outdoors**
root with two families, Camping (tents, sleeping bags, camping chairs) and Yoga & Fitness
(yoga mats, dumbbells, kettlebells, foam rollers). Each type is a leaf with its own drawing
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

ROWS = (*TENTS, *SLEEPING_BAGS, *CHAIRS, *YOGA_MATS, *DUMBBELLS, *KETTLEBELLS, *FOAM_ROLLERS)


def docs() -> list[dict]:
    """Every row's catalog document."""
    return [r.doc() for r in ROWS]
