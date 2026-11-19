"""The outdoors and winter types of gen#959 slice 3: no print decoy sits in their nodes.

"bottle" already names Bike Bottles and "bike" the bicycles, so the insulated water bottle decoys
carry "insulated", the bike light decoys "light" and the bike lock decoys "lock"; "goggle" is the
swimming goggles' word, so the ski goggles decoys carry "ski".
"""

from __future__ import annotations

#: noun -> the category node of the product the noun really names.
NODES: dict[str, str] = {
    "hiking": "Hiking Backpacks",
    "cooler": "Coolers",
    "insulated": "Insulated Water Bottles",
    "light": "Bike Lights",
    "lock": "Bike Locks",
    "sled": "Sleds",
    "snowboard": "Snowboards",
    "ski": "Ski Goggles",
}
