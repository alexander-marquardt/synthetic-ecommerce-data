"""Large appliances of gen#334.

The washing machine's leaf is "Laundry", a node the Cleaning tree has too, so its decoys are
kept out of the department node instead.
"""

from __future__ import annotations

#: noun -> the category node of the product the noun really names.
NODES: dict[str, str] = {
    "fridge": "Fridges & Freezers",
    "dishwasher": "Dishwashers",
    "washing": "Large Appliances",
}
