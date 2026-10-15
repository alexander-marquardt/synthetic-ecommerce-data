"""Household templates for the scaled retail catalog (gen#200): data only.

The catalog had cleaning chemicals and storage baskets but no cookware, kitchen bins,
storage boxes, laundry baskets, mops or clothes airers, so a search for a pan, a bin or a
mop found a cleaning spray or nothing. Each type here is a leaf with its own drawing
(:mod:`kit_household`), its shopper attributes as structured entries, and SKUs over the
color and the type's own axis: a pan's diameter, a bin's or a box's capacity.

A measured axis (``diameter_cm``, ``capacity_l``) is on the SKUs alone, which the export
states with its unit (``export.OPTIONS``), as a knife's blade length is; a saucepan's
capacity follows its diameter on each SKU (:class:`HRow`). A fixed size is a product
entry. These styles are templates only: :func:`scale.derivable` leaves them out, as it
does the shirts, so the seeded derivation is what it was.
"""

from __future__ import annotations

from dataclasses import dataclass

import kit_household  # noqa: F401 -- registers saucepan, frying_pan, casserole, ...
from breadth_rows import Contents, Row
from variants import cw

_HW = "Home"
_CJ = "Cleaning & Janitorial"
_KD = ("Home", "Kitchen & Dining")
_LAUNDRY = ("Home", "Laundry & Ironing")
_H, _L, _C = "Hearth & Table", "Lanternby", "Calderby & Lune"


@dataclass(frozen=True)
class HRow(Row):
    """A row whose SKUs carry more than their size: ``extra`` maps a size to the other
    fields that SKU holds (a 16 cm saucepan's 1.4 l capacity)."""

    extra: tuple[tuple[str, tuple[tuple[str, str], ...]], ...] = ()

    def skus(self) -> list[dict]:
        more = {s: dict(kv) for s, kv in self.extra}
        out = super().skus()
        for sku in out:
            sku.update(more.get(sku.get(self.size_key, ""), {}))
        return out


def _a(key: str, name: str, v: str) -> tuple[str, str, str]:
    return (key, name, v)


def _l(v: float) -> tuple[str, str, str, str, float]:
    """A capacity in litres; its canonical value is in millilitres, as the core states it."""
    return ("capacity", "Capacity", f"{v:g}", "LTR", v * 1000)


def _count(key: str, name: str, n: int) -> tuple[str, str, str, str]:
    return (key, name, str(n), "C62")


def _hobs(*hobs: str) -> tuple:
    """One ``hob_type`` entry per hob, so a facet filters on each."""
    return tuple(_a("hob_type", "Hob type", h) for h in hobs)


ALL_HOBS = _hobs("Induction", "Gas", "Electric", "Ceramic")
NO_INDUCTION = _hobs("Gas", "Electric", "Ceramic")
YES, NO = "Yes", "No"


def _oven(temp: int | None) -> tuple:
    if temp is None:
        return (_a("oven_safe", "Oven safe", NO),)
    return (
        _a("oven_safe", "Oven safe", YES),
        ("oven_safe_temperature", "Oven safe temperature (°C)", str(temp)),
    )


def _cm(*pairs: tuple[int, float]) -> tuple[tuple[str, float], ...]:
    return tuple((str(cm), p) for cm, p in pairs)


def _litres(*pairs: tuple[float, float]) -> tuple[tuple[str, float], ...]:
    return tuple((f"{v:g}", p) for v, p in pairs)


def _pan_caps(*pairs: tuple[int, float]) -> tuple:
    return tuple((str(cm), (("capacity_l", f"{v:g}"),)) for cm, v in pairs)


SILVER = cw("Silver", "#cfd5da", "solid", "#8f989f")
BLACK = cw("Black", "#2f2f35", "solid", "#8f989f")
COPPER = cw("Copper", "#c27a4a", "solid", "#7a4a2a")
CLEAR = cw("Clear", "#e3eef0", "solid", "#7a7d82")
WHITE = cw("White", "#f4f1ea", "solid", "#b9b4a6")
GREY = cw("Grey", "#9a9ca0")
NATURAL = cw("Natural", "#c9a96e", "solid", "#7d5634")

# --------------------------------------------------------------------------
# Saucepans: a single pan sells by diameter (its capacity follows); a set by its pieces.
# --------------------------------------------------------------------------

_SP = (*_KD, "Saucepans")
_SET3 = Contents((1, "16 cm saucepan"), (1, "18 cm saucepan"), (1, "20 cm saucepan"))
_SET5 = Contents((1, "14 cm milk pan"), (1, "16 cm saucepan"), (1, "18 cm saucepan"),
                 (1, "20 cm saucepan"), (1, "24 cm stockpot"))  # fmt: skip


def _sp(material: str, coating: str, lid: str, hobs: tuple, kind: str = "Single") -> tuple:
    return (_a("material", "Material", material), _a("coating", "Coating", coating),
            _a("lid_material", "Lid material", lid), *hobs,
            _a("set_or_single", "Set or single", kind))  # fmt: skip


SAUCEPANS = (
    HRow("SPNTRI", "Tri-Ply Stainless Steel Saucepan with Glass Lid", _H, _HW, _SP, "Saucepan",
         22.0, "saucepan", "A straight-sided pan with a tri-ply base that heats evenly on every "
         "hob, induction included, and a vented glass lid. Dishwasher safe.",
         (SILVER,), (*_sp("Stainless Steel", "Uncoated", "Glass", ALL_HOBS), *_oven(220)),
         _cm((16, 22.0), (18, 26.0), (20, 30.0)), params=(("count", "1"), ("lid", "glass")),
         size_key="diameter_cm", extra=_pan_caps((16, 1.5), (18, 2.0), (20, 2.8))),
    HRow("SPNNST", "Non-Stick Aluminum Saucepan with Glass Lid", _L, _HW, _SP, "Saucepan", 14.0,
         "saucepan", "A light pan with a three-layer non-stick coating for sauces, porridge "
         "and rice. For gas, electric and ceramic hobs.",
         (BLACK, cw("Red", "#c8312e", "solid", "#2f2f35"),
          cw("Teal", "#1c7c7d", "solid", "#2f2f35")),
         (*_sp("Aluminum", "Non-Stick", "Glass", NO_INDUCTION), *_oven(180)),
         _cm((16, 14.0), (18, 16.0), (20, 19.0)), params=(("count", "1"), ("lid", "glass")),
         size_key="diameter_cm", extra=_pan_caps((16, 1.4), (18, 1.9), (20, 2.6))),
    HRow("SPNCOP", "Copper Saucepan with Stainless Steel Lid", _C, _HW, _SP, "Saucepan", 79.0,
         "saucepan", "A hammered copper pan lined with stainless steel, quick to heat and to "
         "cool, with a cast handle. For gas, electric and ceramic hobs.",
         (COPPER,), (*_sp("Copper", "Uncoated", "Stainless Steel", NO_INDUCTION), *_oven(260)),
         _cm((16, 79.0), (18, 95.0)), params=(("count", "1"), ("lid", "steel")),
         size_key="diameter_cm", extra=_pan_caps((16, 1.5), (18, 2.1))),
    HRow("SPNCST", "Enameled Cast Iron Saucepan", _C, _HW, _SP, "Saucepan", 85.0, "saucepan",
         "A heavy pan that holds its heat for slow sauces and custards, on every hob, "
         "induction included. Enameled inside and out, with a cast iron lid.",
         (cw("Red", "#b8322b", "solid", "#2f2f35"), cw("Navy", "#26365c", "solid", "#2f2f35"),
          cw("Cream", "#efe8d8", "solid", "#2f2f35")),
         (*_sp("Cast Iron", "Enamel", "Cast Iron", ALL_HOBS), *_oven(250)),
         _cm((16, 85.0), (18, 99.0), (20, 115.0)), params=(("count", "1"), ("lid", "steel")),
         size_key="diameter_cm", extra=_pan_caps((16, 1.4), (18, 1.8), (20, 2.4))),
    Row("SPNST3", _SET3.title("Stainless Steel Saucepan Set"), _H, _HW, _SP, "Saucepan", 60.0,
        "saucepan", _SET3.text("Each pan has a glass lid and an encapsulated base for every hob, "
        "induction included. Dishwasher safe."),
        (SILVER,), (*_sp("Stainless Steel", "Uncoated", "Glass", ALL_HOBS, "Set"), *_oven(220),
                        *_SET3.attrs),
        params=(("count", "3"), ("lid", "glass"))),
    Row("SPNST5", _SET5.title("Non-Stick Aluminum Saucepan Set"), _L, _HW, _SP, "Saucepan", 75.0,
        "saucepan", _SET5.text("Each pan has a glass lid and a hard-wearing non-stick coating. "
        "For gas, electric and ceramic hobs."),
        (BLACK, GREY), (*_sp("Aluminum", "Non-Stick", "Glass", NO_INDUCTION, "Set"), *_oven(180),
                        *_SET5.attrs),
        params=(("count", "5"), ("lid", "glass"))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Frying pans: the kind sets the drawn profile; color x diameter are the SKUs.
# --------------------------------------------------------------------------

_FP = (*_KD, "Frying Pans")


def _fp(kind: str, material: str, coating: str, hobs: tuple, temp: int | None) -> tuple:
    return (_a("pan_type", "Pan type", kind), _a("material", "Material", material),
            _a("coating", "Coating", coating), *hobs, *_oven(temp))  # fmt: skip


def _fpp(kind: str, coating: str) -> tuple[tuple[str, str], ...]:
    return (("kind", kind), ("coating", coating))


FRYING_PANS = (
    Row("FRYNST", "Non-Stick Aluminum Frying Pan", _L, _HW, _FP, "Frying Pan", 16.0, "frying_pan",
        "A light everyday pan with a three-layer non-stick coating and an induction base. Oven "
        "safe to 180 degrees.",
        (BLACK, GREY, cw("Blue", "#3f6fb5", "solid", "#2f2f35")),
        _fp("Frying Pan", "Aluminum", "Non-Stick", ALL_HOBS, 180),
        _cm((20, 16.0), (24, 20.0), (28, 24.0)), params=_fpp("frying", "non-stick"),
        size_key="diameter_cm"),
    Row("FRYCST", "Pre-Seasoned Cast Iron Skillet", _C, _HW, _FP, "Frying Pan", 28.0,
        "frying_pan", "A heavy skillet with two pouring lips and a helper handle, seasoned "
        "with oil and ready to sear, bake or go on a campfire.",
        (BLACK,), _fp("Skillet", "Cast Iron", "Pre-Seasoned", ALL_HOBS, 260),
        _cm((20, 28.0), (26, 38.0)), params=_fpp("skillet", "pre-seasoned"),
        size_key="diameter_cm"),
    Row("FRYENS", "Enameled Cast Iron Skillet", _H, _HW, _FP, "Frying Pan", 45.0, "frying_pan",
        "A cast iron skillet with a colored enamel outside and a matte enamel inside, "
        "on every hob, induction included.",
        (cw("Red", "#b8322b", "solid", "#2f2f35"), cw("Green", "#3f6b4a", "solid", "#2f2f35")),
        _fp("Skillet", "Cast Iron", "Enamel", ALL_HOBS, 250), _cm((20, 45.0), (26, 59.0)),
        params=_fpp("skillet", "enamel"), size_key="diameter_cm"),
    Row("FRYWOK", "Carbon Steel Wok with Wooden Handle", _H, _HW, _FP, "Frying Pan", 24.0,
        "frying_pan", "A deep, thin wok that heats fast for stir-frying, with a flat base for "
        "an induction hob and a helper loop. Season before first use.",
        (BLACK,), _fp("Wok", "Carbon Steel", "Uncoated", ALL_HOBS, None),
        _cm((30, 24.0), (36, 30.0)), params=_fpp("wok", "uncoated"), size_key="diameter_cm"),
    Row("FRYGRD", "Ceramic Non-Stick Griddle Pan", _L, _HW, _FP, "Frying Pan", 26.0,
        "frying_pan", "A round griddle pan with deep ridges that sear stripes and drain fat, "
        "in a ceramic non-stick coating. For gas and electric hobs.",
        (GREY, cw("Teal", "#1c7c7d")), _fp("Griddle", "Aluminum", "Ceramic", NO_INDUCTION, 200),
        _cm((24, 26.0), (28, 30.0)), params=_fpp("griddle", "ceramic"), size_key="diameter_cm"),
    Row("FRYCRP", "Non-Stick Crepe Pan", _C, _HW, _FP, "Frying Pan", 18.0, "frying_pan",
        "A flat pan with a low rim, so a pancake slides off in one turn. Induction base.",
        (BLACK, cw("Red", "#c8312e", "solid", "#2f2f35")),
        _fp("Crepe Pan", "Aluminum", "Non-Stick", ALL_HOBS, 180), _cm((24, 18.0), (28, 22.0)),
        params=_fpp("crepe", "non-stick"), size_key="diameter_cm"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Casserole dishes: the shape is drawn; color x capacity are the SKUs.
# --------------------------------------------------------------------------

_CS = (*_KD, "Casserole Dishes")


def _cs(material: str, shape: str, temp: int, hobs: tuple, coating: str | None = None) -> tuple:
    """An oven-only dish passes no hobs, so it states no ``hob_type``."""
    coat = (_a("coating", "Coating", coating),) if coating else ()
    return (_a("material", "Material", material), *coat, _a("shape", "Shape", shape),
            *_oven(temp), *hobs)  # fmt: skip


CASSEROLES = (
    Row("CASRND", "Enameled Cast Iron Round Casserole", _C, _HW, _CS, "Casserole Dish", 89.0,
        "casserole", "A heavy round casserole with a tight lid that keeps stews moist, from the "
        "hob to the oven to the table. Enameled inside and out.",
        (cw("Red", "#b8322b", "solid", "#2f2f35"), cw("Navy", "#26365c", "solid", "#2f2f35"),
         cw("Green", "#3f6b4a", "solid", "#2f2f35"), cw("Cream", "#efe8d8", "solid", "#2f2f35")),
        _cs("Cast Iron", "Round", 250, ALL_HOBS, "Enamel"),
        _litres((2.4, 89.0), (4.2, 119.0), (6.7, 149.0)),
        params=(("form", "round"), ("material", "cast iron")), size_key="capacity_l"),
    Row("CASOVL", "Cast Iron Oval Casserole", _H, _HW, _CS, "Casserole Dish", 69.0, "casserole",
        "A long oval casserole that takes a whole chicken or a joint, on any hob and in the "
        "oven, with a smooth glazed inside.",
        (BLACK, GREY), _cs("Cast Iron", "Oval", 250, ALL_HOBS), _litres((4.7, 69.0), (6.3, 85.0)),
        params=(("form", "oval"), ("material", "cast iron")), size_key="capacity_l"),
    Row("CASSTO", "Stoneware Oval Casserole Dish with Lid", _L, _HW, _CS, "Casserole Dish", 28.0,
        "casserole", "A glazed stoneware dish for the oven and the table. Not for the hob. "
        "Dishwasher safe.",
        (WHITE, cw("Blue", "#3f6fb5")), _cs("Stoneware", "Oval", 240, ()),
        _litres((1.5, 28.0), (2.5, 36.0)), params=(("form", "oval"), ("material", "stoneware")),
        size_key="capacity_l"),
    Row("CASGLS", "Glass Round Casserole Dish with Lid", _H, _HW, _CS, "Casserole Dish", 12.0,
        "casserole", "A clear dish that shows how a bake is browning, from the freezer to the "
        "oven. Not for the hob. Dishwasher safe.",
        (CLEAR,), _cs("Glass", "Round", 300, ()), _litres((1.5, 12.0), (2.5, 16.0), (3.5, 20.0)),
        params=(("form", "round"), ("material", "glass")), size_key="capacity_l"),
    Row("CASENA", "Enamel Round Casserole", _L, _HW, _CS, "Casserole Dish", 34.0, "casserole",
        "A light enamel-on-steel pot for soups and stews, on every hob and in the oven.",
        (WHITE, cw("Yellow", "#e8b931", "solid", "#2f2f35")),
        _cs("Steel", "Round", 250, ALL_HOBS, "Enamel"),
        _litres((2.5, 34.0), (4, 42.0)), params=(("form", "round"), ("material", "enamel")),
        size_key="capacity_l"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Kitchen bins: the kind (pedal, touch-top, sensor, recycling) is drawn.
# --------------------------------------------------------------------------

_KB = (*_KD, "Kitchen Bins")


def _kb(kind: str, material: str, compartments: int = 1) -> tuple:
    return (_a("bin_type", "Bin type", kind), _a("material", "Material", material),
            _count("compartments", "Compartments", compartments))  # fmt: skip


KITCHEN_BINS = (
    Row("BINPDL", "Stainless Steel Pedal Bin", _H, _HW, _KB, "Kitchen Bin", 25.0, "kitchen_bin",
        "A pedal bin with a soft-close lid and a removable inner bucket with a carry handle. "
        "Fingerprint-proof finish.",
        (SILVER, BLACK, cw("Cream", "#efe8d8", "solid", "#2f2f35")),
        _kb("Pedal", "Stainless Steel"),
        _litres((5, 25.0), (20, 39.0), (30, 49.0)), params=(("kind", "pedal"),),
        size_key="capacity_l"),
    Row("BINTCH", "Touch-Top Kitchen Bin", _L, _HW, _KB, "Kitchen Bin", 35.0, "kitchen_bin",
        "A tall bin whose lid springs open at a touch, with a liner ring that hides the bag.",
        (SILVER, BLACK, WHITE), _kb("Touch-Top", "Stainless Steel"),
        _litres((40, 35.0), (50, 42.0)), params=(("kind", "touch-top"),), size_key="capacity_l"),
    Row("BINSNS", "Sensor Kitchen Bin", _C, _HW, _KB, "Kitchen Bin", 59.0, "kitchen_bin",
        "A hands-free bin whose lid opens when a hand passes over the sensor and closes after "
        "three seconds. Runs on batteries or by USB lead.",
        (SILVER, BLACK), _kb("Sensor", "Stainless Steel"), _litres((42, 59.0), (58, 75.0)),
        params=(("kind", "sensor"),), size_key="capacity_l"),
    Row("BINRC2", "Recycling Pedal Bin with 2 Compartments", _H, _HW, _KB, "Kitchen Bin", 45.0,
        "kitchen_bin", "Two 20 l buckets behind one pedal, for rubbish and recycling, with "
        "colored tabs on the lids.",
        (SILVER, GREY), (*_kb("Recycling", "Stainless Steel", 2), _l(40)),
        params=(("kind", "recycling"), ("compartments", "2"))),
    Row("BINRC3", "Recycling Bin with 3 Compartments", _L, _HW, _KB, "Kitchen Bin", 55.0,
        "kitchen_bin", "Three 15 l compartments, each with a lid, for paper, plastic and "
        "glass, in a recycled plastic body.",
        (GREY, WHITE), (*_kb("Recycling", "Recycled Plastic", 3), _l(45)),
        params=(("kind", "recycling"), ("compartments", "3"))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Storage boxes: the form, the lid and a clear body are drawn; color x capacity the SKUs.
# --------------------------------------------------------------------------

_SB = ("Home", "Storage", "Storage Boxes")


def _sb(material: str, lid: str, stackable: str, clear: str, storage: str = "Storage Box") -> tuple:
    return (_a("material", "Material", material), _a("lid_type", "Lid type", lid),
            _a("stackable", "Stackable", stackable), _a("transparent", "Transparent", clear),
            _a("storage_type", "Storage type", storage))  # fmt: skip


def _sbp(form: str, lid: str, clear: str, material: str) -> tuple[tuple[str, str], ...]:
    return (("form", form), ("lid", lid), ("clear", clear), ("material", material))


STORAGE_BOXES = (
    Row("BOXCLR", "Clear Plastic Storage Box with Clip Lid", _H, _HW, _SB, "Storage Box", 6.0,
        "storage_box", "A see-through box with a lid that clips shut on both sides, so it "
        "stacks firmly and keeps dust out.",
        (CLEAR,), _sb("Plastic", "Clip Lid", YES, YES), _litres((9, 6.0), (24, 9.0), (45, 14.0)),
        params=_sbp("box", "yes", "yes", "plastic"), size_key="capacity_l"),
    Row("BOXUBD", "Clear Underbed Storage Box with Wheels", _L, _HW, _SB, "Storage Box", 14.0,
        "storage_box", "A low box on four wheels that rolls out from under a bed, with a clip "
        "lid that keeps bedding and clothes dust-free.",
        (CLEAR,), _sb("Plastic", "Clip Lid", YES, YES, "Underbed"),
        _litres((32, 14.0), (60, 19.0)), params=_sbp("underbed", "yes", "yes", "plastic"),
        size_key="capacity_l"),
    Row("BOXFAB", "Fabric Storage Box with Lid", _C, _HW, _SB, "Storage Box", 16.0,
        "storage_box", "A soft box with a stiffened base and a lift-off lid that folds flat "
        "when it is not in use.",
        (GREY, cw("Navy", "#26365c"), cw("Beige", "#d8c9a8")),
        _sb("Fabric", "Lift-Off Lid", NO, NO), _litres((30, 16.0), (48, 22.0)),
        params=_sbp("box", "yes", "no", "fabric"), size_key="capacity_l"),
    Row("BOXCRD", "Cardboard Storage Box with Lid", _L, _HW, _SB, "Storage Box", 5.0,
        "storage_box", "A sturdy box with a lift-off lid and a label window, for photos, "
        "papers or seasonal clothes.",
        (NATURAL, WHITE), _sb("Cardboard", "Lift-Off Lid", YES, NO), _litres((20, 5.0), (35, 7.0)),
        params=_sbp("box", "yes", "no", "cardboard"), size_key="capacity_l"),
    Row("BOXWOD", "Wooden Storage Crate", _H, _HW, _SB, "Storage Box", 18.0, "storage_box",
        "An open slatted crate with cut-out handles, for shoes, toys or vegetables.",
        (NATURAL, WHITE), _sb("Wood", "No Lid", YES, NO), _litres((20, 18.0), (32, 24.0)),
        params=_sbp("crate", "no", "no", "wood"), size_key="capacity_l"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Laundry baskets and clothes airers.
# --------------------------------------------------------------------------

_LB = (*_LAUNDRY, "Laundry Baskets")


def _lb(kind: str, material: str, litres: float, compartments: int = 1) -> tuple:
    return (_a("laundry_basket_type", "Laundry basket type", kind),
            _a("material", "Material", material), _l(litres),
            _count("compartments", "Compartments", compartments))  # fmt: skip


LAUNDRY_BASKETS = (
    Row("LDBWIC", "Wicker Laundry Hamper with Lid", _C, _HW, _LB, "Laundry Basket", 45.0,
        "laundry_basket", "A tall woven hamper with a removable cotton liner and a lid, 60 l.",
        (NATURAL, WHITE, GREY), _lb("Hamper", "Wicker", 60),
        params=(("kind", "hamper"), ("material", "wicker"))),
    Row("LDBPLS", "Plastic Laundry Basket", _H, _HW, _LB, "Laundry Basket", 8.0,
        "laundry_basket", "An oval basket with hand holds and air holes that hold a full wash "
        "load, 40 l.",
        (WHITE, GREY, cw("Blue", "#3f6fb5")), _lb("Basket", "Plastic", 40),
        params=(("kind", "basket"), ("material", "plastic"))),
    Row("LDBFLD", "Folding Fabric Laundry Basket", _L, _HW, _LB, "Laundry Basket", 12.0,
        "laundry_basket", "A pop-up fabric tub on a wire rim that folds flat to a disc, with two "
        "carry handles, 45 l.",
        (GREY, cw("Navy", "#26365c"), cw("Beige", "#d8c9a8")), _lb("Folding", "Fabric", 45),
        params=(("kind", "folding"), ("material", "fabric"))),
    Row("LDBTWO", "Two-Compartment Seagrass Laundry Sorter", _C, _HW, _LB, "Laundry Basket",
        65.0, "laundry_basket", "A wide sorter with two lidded sections, to sort lights from "
        "darks as you go, 80 l in all.",
        (NATURAL,), _lb("Two-Compartment", "Seagrass", 80, 2),
        params=(("kind", "two-compartment"), ("material", "seagrass"))),
)  # fmt: skip

_CA = (*_LAUNDRY, "Clothes Airers")


def _m(v: float) -> tuple[str, str, str, str, float]:
    return ("drying_length", "Drying length", f"{v:g}", "MTR", v * 1000)


def _ca(kind: str, metres: float, tiers: int) -> tuple:
    return (_a("airer_type", "Airer type", kind), _m(metres), _count("tiers", "Tiers", tiers))


CLOTHES_AIRERS = (
    Row("AIRFLD", "Folding Wing Clothes Airer, 18 m", _H, _HW, _CA, "Clothes Airer", 18.0,
        "clothes_airer", "A wing airer that folds flat behind a door, with 18 m of drying "
        "space and a rail for socks.",
        (WHITE, GREY), _ca("Folding", 18, 1), params=(("kind", "folding"), ("tiers", "1"))),
    Row("AIRTW3", "3 Tier Tower Clothes Airer", _L, _HW, _CA, "Clothes Airer", 30.0,
        "clothes_airer", "Three wide racks on a narrow tower that rolls on castors, 24 m of "
        "drying space in a small footprint.",
        (SILVER, WHITE), _ca("Tower", 24, 3), params=(("kind", "tower"), ("tiers", "3"))),
    Row("AIRTW4", "4 Tier Tower Clothes Airer", _H, _HW, _CA, "Clothes Airer", 38.0,
        "clothes_airer", "Four racks on castors with 30 m of drying space, for a big family "
        "wash.",
        (SILVER,), _ca("Tower", 30, 4), params=(("kind", "tower"), ("tiers", "4"))),
    Row("AIRHTD", "Heated Clothes Airer, 2 Tier", _C, _HW, _CA, "Clothes Airer", 69.0,
        "clothes_airer", "Heated aluminum bars that dry a load overnight indoors for a few "
        "pence, on two tiers with 14 m of drying space.",
        (SILVER,), _ca("Heated", 14, 2), params=(("kind", "heated"), ("tiers", "2"))),
    Row("AIRWAL", "Wall-Mounted Clothes Airer", _L, _HW, _CA, "Clothes Airer", 24.0,
        "clothes_airer", "Four bars that fold down from a wall plate over a bath or in the "
        "utility room, with 6 m of drying space.",
        (WHITE,), _ca("Wall-Mounted", 6, 1), params=(("kind", "wall-mounted"), ("tiers", "1"))),
)  # fmt: skip

# --------------------------------------------------------------------------
# Mops and buckets (Cleaning & Janitorial): the kind is drawn.
# --------------------------------------------------------------------------

_MB = ("Cleaning", "Cleaning Tools", "Mops & Buckets")


def _mb(kind: str, heads: int | None, litres: float | None = None) -> tuple:
    """``heads`` is None for a bucket with no mop: it has nothing to refill."""
    out = (_a("mop_type", "Mop type", kind),)
    if heads is not None:
        out += (_count("refill_heads", "Refill heads", heads),)
    return (*out, _l(litres)) if litres else out


MOPS = (
    Row("MOPSPN", "Spin Mop and Bucket Set", "Freshfold", _CJ, _MB, "Mop and Bucket", 25.0, "mop",
        "A microfiber mop that spins dry in its bucket at a press of the pedal, so hands stay "
        "dry. Comes with 2 refill heads; the bucket holds 10 l.",
        (GREY, cw("Blue", "#3f6fb5"), cw("Teal", "#1c7c7d")), _mb("Spin Mop", 2, 10),
        params=(("kind", "spin"),)),
    Row("MOPFLT", "Flat Mop with Washable Pads", "Pantry Mill", _CJ, _MB, "Mop and Bucket", 15.0,
        "mop", "A swivel flat mop that reaches under furniture, with 3 washable microfiber "
        "refill pads.",
        (GREY, cw("Green", "#3f8f4a")), _mb("Flat Mop", 3), params=(("kind", "flat"),)),
    Row("MOPSPG", "Sponge Mop with Wringer", "Clearbrook Household", _CJ, _MB, "Mop and Bucket",
        12.0, "mop", "A roller sponge mop with a lever wringer, for tiles and vinyl. Comes "
        "with 1 refill head.",
        (cw("Blue", "#3f6fb5"), cw("Yellow", "#e8b931")), _mb("Sponge Mop", 1),
        params=(("kind", "sponge"),)),
    Row("MOPBKT", "Mop Bucket with Wringer on Wheels", "Soapwell", _CJ, _MB, "Mop and Bucket",
        39.0, "mop", "A 20 l bucket on four castors with a press wringer, for kitchens, "
        "halls and shop floors. Color-coded to keep areas apart.",
        (cw("Yellow", "#e8b931"), cw("Blue", "#3f6fb5"), cw("Red", "#c8312e")),
        _mb("Mop Bucket", None, 20), params=(("kind", "bucket"),)),
)  # fmt: skip

ROWS = (*SAUCEPANS, *FRYING_PANS, *CASSEROLES, *KITCHEN_BINS, *STORAGE_BOXES, *LAUNDRY_BASKETS,
        *CLOTHES_AIRERS, *MOPS)  # fmt: skip


def docs() -> list[dict]:
    """Every household row's catalog document, type by type."""
    return [r.doc() for r in ROWS]
