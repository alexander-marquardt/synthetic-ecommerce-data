"""Brand line-ups of the large appliances (#1116): each own brand sells each kind in four models.

A kind's table holds six authored models, one a brand. :func:`line_up` appends three more a brand,
at other points of the same table, so one brand's models of a kind differ in size, price and
feature as they do at a retailer. A brand holds its place in the market across every kind
(:data:`PRICE_LEVEL`), and its sizes are a few litres or rpm off the table (``nudge``), as no two
makers build to one volume. :func:`feature` gives each added model the feature it is sold on.

The authored models come first in the table, unchanged, so their ids, brands, generations and
model numbers stay what they were. A brand's four models of a table take four generations in turn,
so no two of them share a model number; test 622 holds it across the tables of a kind too.
"""

from __future__ import annotations

from collections.abc import Callable

from synthetic_ecommerce_data.domains.retail import large_appliance_rows as lar

AUTHORED = 6
#: How many steps past its own point of a table each of a brand's added models sits, in turn.
STEPS = (1, 3, 5)

#: A brand's price against the table's, from the value brand to the premium one.
PRICE_LEVEL = {"Brimwell": 0.89, "Cleavewick": 0.94, "Frostholm": 0.99, "Tavorne": 1.05,
               "Hollinmere": 1.11, "Lunden & Voss": 1.19}  # fmt: skip

#: A brand's capacity against the table's, in litres.
LITRES_OFF = {"Brimwell": -2, "Cleavewick": -1, "Frostholm": 1, "Tavorne": 2, "Hollinmere": 3,
              "Lunden & Voss": 4}  # fmt: skip

#: What each product type's added models are sold on, one per step: (value, the sentence's words).
#: No word here is one that another department names a range with ("Chill" renamed five tees).
FEATURES: dict[str, tuple[tuple[str, str], ...]] = {
    "Fridge & Freezer": (
        ("Express Cooling", "an express cooling setting"),
        ("Door Alarm", "an alarm for an open door"),
        ("Holiday Mode", "a holiday mode"),
    ),
    "Dishwasher": (
        ("Third Rack", "a third rack for cutlery"),
        ("Delay Start", "a delay start"),
        ("Auto Door Opening", "a door that opens by itself to dry the load"),
    ),
    "Laundry Appliance": (
        ("Quick Cycle", "a quick cycle"),
        ("Delay Start", "a delay start"),
        ("App Control", "control from a phone app"),
    ),
    "Range Cooker": (
        ("Warming Zone", "a warming zone"),
        ("Catalytic Liners", "catalytic liners"),
        ("Programmable Timer", "a programmable timer"),
    ),
    "Built-in Oven": (
        ("Pyrolytic Cleaning", "pyrolytic cleaning"),
        ("Catalytic Liners", "catalytic liners"),
        ("Programmable Timer", "a programmable timer"),
    ),
    "Hob": (
        ("Child Lock", "a child lock"),
        ("Power Boost", "a power boost"),
        ("Zone Timer", "a timer for each zone"),
    ),
    "Cooker Hood": (
        ("LED Lighting", "LED lighting"),
        ("Filter Alert", "an alert when the filter is due a wash"),
        ("Intensive Setting", "an intensive setting"),
    ),
}


def brand_at(pre: str, i: int) -> str:
    """The brand :func:`large_appliance_rows.kind_rows` gives model ``i`` of table ``pre``."""
    return lar.BRANDS[(sum(map(ord, pre)) + i) % len(lar.BRANDS)]


def _price(brand: str, price: int) -> int:
    """The brand's price for a table price, kept on the table's own ending, a nine."""
    return round(price * PRICE_LEVEL[brand] / 10) * 10 - 1


def litres_off(model: tuple, brand: str) -> tuple:
    """A model whose first value is litres, moved by the brand's :data:`LITRES_OFF`."""
    return (model[0] + LITRES_OFF[brand], *model[1:])


def line_up(
    pre: str,
    models: tuple[tuple, ...],
    price_at: int,
    nudge: Callable[[tuple, str], tuple] | None = None,
    steps: tuple[int, ...] = STEPS,
) -> tuple[tuple, ...]:
    """``models`` and then three more a brand; ``price_at`` is where a model holds its price.

    Model ``i`` of the authored six is brand ``i``'s. Its added models take the table's points
    ``steps`` on, so a brand's four models are four different points. A table that shares its kind
    with another may name its own order, so no model number repeats between the two.
    """
    if len(models) != AUTHORED:
        raise ValueError(f"{pre}: {len(models)} authored models, not {AUTHORED}")
    out = list(models)
    for step in steps:
        for k in range(AUTHORED):
            brand = brand_at(pre, len(out))
            model = models[(k + step) % AUTHORED]
            model = (*model[:price_at], _price(brand, model[price_at]), *model[price_at + 1 :])
            out.append(nudge(model, brand) if nudge else model)
    return tuple(out)


def feature(ptype: str, i: int) -> tuple[str, tuple[tuple[str, str, str], ...]]:
    """Model ``i``'s feature as a description sentence and an attribute; none if authored."""
    if i < AUTHORED:
        return "", ()
    value, words = FEATURES[ptype][(i - AUTHORED) // AUTHORED]
    return f" It has {words}.", (lar.a("feature", "Feature", value),)


__all__ = ["FEATURES", "PRICE_LEVEL", "line_up"]
