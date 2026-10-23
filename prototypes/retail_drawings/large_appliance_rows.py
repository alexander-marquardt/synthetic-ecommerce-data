"""Large appliance rows (gen#334): fridges and freezers, dishwashers, laundry. Data and builders.

The three specs (``type_specs/fridge_freezer.py``, ``dishwasher.py``, ``laundry_appliance.py``)
each take their rows from here. A style is one product (a model with its own capacity, width and
rating); its color is the SKU variant. Each kind is six models, so a kind has depth and the
whole range is more than sixty products. Every brand is invented (README, gen#334); the
description states the numbers the structured entries state, and no more.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from dataclasses import replace

import appliance_model_numbers as amn
import kit_large_appliances  # noqa: F401 -- registers fridge, dishwasher, washing_machine, ...
from breadth_rows import Row
from variants import cw

HOME = "Home"
ROOT = ("Home", "Large Appliances")
FRIDGES = (*ROOT, "Fridges & Freezers")
DISHWASHERS = (*ROOT, "Dishwashers")
LAUNDRY = (*ROOT, "Laundry")
BRANDS = ("Frostholm", "Brimwell", "Tavorne", "Hollinmere", "Cleavewick", "Lunden & Voss")
OWNERS = tuple((b, "own") for b in BRANDS)

WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
BLACK = cw("Black", "#2d2d33")
SILVER = cw("Silver", "#c3c8cc", "solid", "#6e757b")
RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)
_PALETTES = ((WHITE, BLACK, SILVER), (SILVER, BLACK), (WHITE, SILVER))
_RATINGS = "ABCDE"
#: The generation letters of a model number. Never "A" or "I": those are English words, and a
#: generation value that reads as a word is "contradicted" by any description that starts "A ...".
GENERATIONS = "BCDEF"
DECOY_GENERATION = "H"


def a(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def _cm(v: int) -> tuple[str, str, str, str, float]:
    return ("item_width", "Item width", str(v), "CMT", float(v * 10))


def _litres(v: int) -> tuple[str, str, str, str, float]:
    return ("capacity", "Capacity", str(v), "LTR", v * 1000.0)


def _kg(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "KGM", v * 1000.0)


def _count(key: str, name: str, v: int) -> tuple[str, str, str, str]:
    return (key, name, str(v), "C62")


def _yn(key: str, name: str, on: bool) -> tuple[str, str, str]:
    return (key, name, "Yes" if on else "No")


def _row(pre: str, i: int, title: str, brand: str, path: tuple[str, ...], ptype: str, price: float,
         shape: str, params: tuple[tuple[str, str], ...], desc: str, colors, attrs,
         series: str = "", codes: tuple[tuple[str, str], ...] = ()) -> Row:
    return Row(f"{pre}{i + 1:03d}", title, brand, HOME, path, ptype, price, shape, desc, colors,
               attrs, params=params, product_line=series, color_codes=codes)  # fmt: skip


_CAPACITY_KEYS = ("load", "capacity", "place_settings")


def identify(brand: str, attrs, color: str, generation: str) -> tuple[str, str, tuple, str]:
    """A model's series, model number, the attributes that state them, and the title's spec.

    Read from the model's own attributes (its kind, capacity and spin speed), so the number and
    the structured entries cannot disagree (gen#622). ``color`` is the color the number names:
    the model's first, which the drawing and the first SKU carry.
    """
    got = {x[0]: x[2] for x in attrs}
    kind, spin = got["appliance_type"], int(got.get("spin_rpm", 0))
    capacity = int(next(got[k] for k in _CAPACITY_KEYS if k in got))
    series = amn.series_for(brand, kind)
    base = amn.base_model(brand, kind, capacity, spin, generation)
    extra = (a("generation", "Generation", generation),
             a("model_number", "Model number", base + amn.COLORS[color]),
             a("base_model", "Base model", base))  # fmt: skip
    return series, base + amn.COLORS[color], extra, amn.spec(kind, capacity, spin)


def color_codes(extra, colors) -> tuple[tuple[str, str], ...]:
    """Each color's model number: the base model of ``extra`` and that color's letter."""
    base = next(x[2] for x in extra if x[0] == "base_model")
    return tuple((c[0], base + amn.COLORS[c[0]]) for c in colors)


def _kind(pre: str, n: int, path, ptype, shape, params, title, make) -> tuple[Row, ...]:
    """Six models of one kind: ``make(i)`` gives each model's (price, description, colors, attrs).

    The title reads brand, series, model number, spec, then the kind (gen#622).
    """
    out = []
    for i in range(n):
        price, desc, colors, attrs = make(i)
        brand = BRANDS[(sum(map(ord, pre)) + i) % len(BRANDS)]
        generation = GENERATIONS[(sum(map(ord, pre)) + i) % 5]
        series, code, extra, spec = identify(brand, attrs, colors[0][0], generation)
        out.append(_row(pre, i, f"{brand} {series} {code} {spec} {title}", brand, path, ptype, price,
                        shape, params, desc, colors, (*attrs, *extra), series,
                        color_codes(extra, colors)))
    return tuple(out)


def decoy_row(code: str, name: str, brand: str, path, ptype: str, price: float, shape: str,
              desc: str, colors, attrs, params=()) -> Row:
    """A decoy with a series and a model number like every large appliance (gen#622).

    ``name`` is the title's tail, carrying the word that misleads ("Black Edition Fridge Freezer").
    Its generation is :data:`DECOY_GENERATION`, which no authored model takes, so its number is its own product's.
    """
    series, number, extra, spec = identify(brand, attrs, colors[0][0], DECOY_GENERATION)
    return Row(code, f"{brand} {series} {number} {spec} {name}", brand, HOME, path, ptype, price,
               shape, desc, colors, (*attrs, *extra), params=params, product_line=series,
               color_codes=color_codes(extra, colors))


# -- fridges and freezers: (capacity L, width cm, price, frost free) per model
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
            rating = _RATINGS[(i + len(pre)) % 5]
            desc = (f"{lead}. {cap} litres in all, {width} cm wide, energy rating {rating}"
                    f"{', frost free' if frost_free else ', manual defrost'}"
                    f"{'. A retro shape with rounded corners' if retro else ''}.")
            colors = SIX if retro else _PALETTES[i % 3]
            attrs = (a("appliance_type", "Type", kind_name), _litres(cap), _cm(width),
                     a("energy_rating", "Energy rating", rating), _yn("frost_free", "Frost free", frost_free))
            return float(price), desc, colors, attrs
        rows = _kind(pre, 6, FRIDGES, "Fridge & Freezer", "fridge", (("kind", shape),), title, make)
        if pre == "FFB":
            rows = tuple(
                r if i < 4 else replace(r, title=r.title.replace(title, f"Retro {title}"))
                for i, r in enumerate(rows)
            )
        out += rows
    return tuple(out)


# -- dishwashers: (place settings, width cm, price, noise dB)
_DISH_KINDS = (
    ("DWF", "full", "Full-Size Dishwasher", "Full-Size", "A freestanding dishwasher",
     ((12, 60, 329, 49), (13, 60, 379, 46), (14, 60, 429, 44), (14, 60, 489, 42), (15, 60, 549, 40), (16, 60, 649, 38))),
    ("DWS", "slim", "Slimline Dishwasher", "Slimline", "A slimline dishwasher for a narrow gap",
     ((9, 45, 299, 49), (10, 45, 349, 47), (10, 45, 399, 45), (10, 45, 449, 44), (11, 45, 499, 42), (11, 45, 579, 40))),
    ("DWI", "integrated", "Integrated Dishwasher", "Integrated", "A dishwasher that hides behind a cabinet door",
     ((12, 60, 399, 46), (13, 60, 449, 44), (14, 60, 499, 43), (14, 60, 549, 42), (15, 60, 629, 40), (15, 60, 699, 38))),
    ("DWT", "tabletop", "Table-Top Dishwasher", "Table-Top", "A small dishwasher for a worktop",
     ((4, 55, 189, 52), (4, 55, 209, 51), (5, 55, 229, 50), (6, 55, 249, 49), (6, 55, 279, 48), (6, 55, 299, 47))),
)  # fmt: skip


def dishwasher_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, title, kind_name, lead, models in _DISH_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, pre=pre):
            places, width, price, noise = models[i]
            rating = _RATINGS[(i + len(pre)) % 5]
            desc = (f"{lead}. It holds {places} place settings, is {width} cm wide and runs at "
                    f"{noise} dB, energy rating {rating}.")
            attrs = (a("appliance_type", "Type", kind_name), _count("place_settings", "Place settings", places),
                     _cm(width), a("energy_rating", "Energy rating", rating), a("noise_db", "Noise level (dB)", str(noise)))
            return float(price), desc, _PALETTES[i % 3], attrs
        out += _kind(pre, 6, DISHWASHERS, "Dishwasher", "dishwasher", (("kind", shape),), title, make)
    return tuple(out)


# -- laundry: (load kg, spin rpm or dry kg, price)
_LAUNDRY_KINDS = (
    ("LWM", "washing_machine", "", "Washing Machine", "Washing Machine", "A front-loading washing machine",
     ((7, 1200, 279), (8, 1400, 329), (9, 1400, 379), (10, 1400, 429), (10, 1600, 499), (12, 1600, 599))),
    ("LTH", "tumble_dryer", "heat_pump", "Heat Pump Tumble Dryer", "Tumble Dryer (Heat Pump)", "A heat pump tumble dryer",
     ((7, 0, 379), (8, 0, 429), (8, 0, 479), (9, 0, 529), (9, 0, 599), (10, 0, 699))),
    ("LTC", "tumble_dryer", "condenser", "Condenser Tumble Dryer", "Tumble Dryer (Condenser)", "A condenser tumble dryer",
     ((7, 0, 249), (8, 0, 279), (8, 0, 299), (9, 0, 329), (9, 0, 359), (10, 0, 399))),
    ("LTV", "tumble_dryer", "vented", "Vented Tumble Dryer", "Tumble Dryer (Vented)", "A vented tumble dryer with a hose for the window",
     ((6, 0, 179), (7, 0, 199), (7, 0, 219), (8, 0, 239), (8, 0, 259), (9, 0, 289))),
    ("LWD", "washer_dryer", "", "Washer Dryer", "Washer Dryer", "A washer dryer that washes and dries in one drum",
     ((8, 1400, 399), (8, 1400, 449), (9, 1400, 499), (9, 1600, 549), (10, 1600, 629), (10, 1600, 699))),
)  # fmt: skip


#: The washing machines titled "Washing Machine from <brand>, Model <code>", the second form.
_FROM_FORM = (2, 5)


def _from_form(r: Row) -> Row:
    code = next(x[2] for x in r.attrs if x[0] == "model_number")
    return replace(r, title=f"Washing Machine from {r.brand}, Model {code}")


def laundry_rows() -> tuple[Row, ...]:
    out: list[Row] = []
    for pre, shape, kind, title, kind_name, lead, models in _LAUNDRY_KINDS:
        def make(i, models=models, lead=lead, kind_name=kind_name, pre=pre):
            load, spin, price = models[i]
            rating = _RATINGS[(i + len(pre)) % 5]
            what = f"takes a {load} kg load" + (f" and spins at {spin} rpm" if spin else "")
            desc = f"{lead}. It {what}, energy rating {rating}."
            attrs = [a("appliance_type", "Type", kind_name), _kg("load", "Load capacity", load)]
            if spin:
                attrs.append(a("spin_rpm", "Spin speed (rpm)", str(spin)))
            attrs.append(a("energy_rating", "Energy rating", rating))
            return float(price), desc, _PALETTES[i % 3], tuple(attrs)
        params = (("kind", kind),) if kind else ()
        rows = _kind(pre, 6, LAUNDRY, "Laundry Appliance", shape, params, title, make)
        if pre == "LWM":
            rows = tuple(_from_form(r) if i in _FROM_FORM else r for i, r in enumerate(rows))
        out += rows
    return tuple(out)


__all__ = ["OWNERS", "dishwasher_rows", "fridge_rows", "laundry_rows"]
