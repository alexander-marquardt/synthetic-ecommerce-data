"""Large appliance helpers (gen#334): what the fridge, dishwasher and laundry specs share.

Each spec (``type_specs/fridge_freezer.py``, ``dishwasher.py``, ``laundry_appliance.py``) holds
its own family's table and builder, so a change to one family touches one file (gen#659). Here
are the brands, the palettes, the attribute makers, :func:`kind_rows` and :func:`decoy_row`. A
style is one product (a model with its own capacity, width and rating); its color is the SKU
variant. Each kind is six models, so a kind has depth and the whole range is more than sixty
products. Every brand is invented (README, gen#334); the description states the numbers the
structured entries state, and no more.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail import appliance_model_numbers as amn
from synthetic_ecommerce_data.domains.retail import (
    kit_large_appliances,  # noqa: F401 -- registers fridge, dishwasher, washing_machine, ...
)
from synthetic_ecommerce_data.domains.retail.breadth_rows import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

HOME = "Home"
ROOT = ("Home", "Large Appliances")
FRIDGES = (*ROOT, "Fridges & Freezers")
DISHWASHERS = (*ROOT, "Dishwashers")
LAUNDRY = (*ROOT, "Laundry")
BRANDS = ("Frostholm", "Brimwell", "Tavorne", "Hollinmere", "Cleavewick", "Lunden & Voss")
#: Brands that also sell outside this range (#721): a few models each, in the specs that name them.
GOODLOOK, SINGINGSAM = "GoodLook", "SingingSam"
OWNERS = (*((b, "own") for b in BRANDS), (GOODLOOK, "third_party"), (SINGINGSAM, "third_party"))

WHITE = cw("White", "#f4f1ea", "solid", "#9a9ca0")
BLACK = cw("Black", "#2d2d33")
SILVER = cw("Silver", "#c3c8cc", "solid", "#6e757b")
RED = cw("Red", "#c8312e")
BLUE = cw("Blue", "#3f6fb5")
GREEN = cw("Green", "#4f8a3a")
YELLOW = cw("Yellow", "#f2c230")
SIX = (RED, BLUE, GREEN, YELLOW, BLACK, WHITE)
PALETTES = ((WHITE, BLACK, SILVER), (SILVER, BLACK), (WHITE, SILVER))
RATINGS = "ABCDE"
#: The generation letters of a model number. Never "A" or "I": those are English words, and a
#: generation value that reads as a word is "contradicted" by any description that starts "A ...".
GENERATIONS = "BCDEF"
DECOY_GENERATION = "H"


def a(key: str, name: str, value: str) -> tuple[str, str, str]:
    return (key, name, value)


def cm(v: int) -> tuple[str, str, str, str, float]:
    return ("item_width", "Item width", str(v), "CMT", float(v * 10))


def litres(v: int) -> tuple[str, str, str, str, float]:
    return ("capacity", "Capacity", str(v), "LTR", v * 1000.0)


def kg(key: str, name: str, v: int) -> tuple[str, str, str, str, float]:
    return (key, name, str(v), "KGM", v * 1000.0)


def count(key: str, name: str, v: int) -> tuple[str, str, str, str]:
    return (key, name, str(v), "C62")


def yn(key: str, name: str, on: bool) -> tuple[str, str, str]:
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


def kind_rows(pre: str, n: int, path, ptype, shape, params, title, make,
              brands: tuple[str, ...] = BRANDS) -> tuple[Row, ...]:
    """``n`` models of one kind: ``make(i)`` gives each model's (price, description, colors, attrs).

    The title reads brand, series, model number, spec, then the kind (gen#622).
    """
    out = []
    for i in range(n):
        price, desc, colors, attrs = make(i)
        brand = brands[(sum(map(ord, pre)) + i) % len(brands)]
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


__all__ = ["OWNERS"]
