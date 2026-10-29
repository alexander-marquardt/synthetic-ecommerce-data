"""The tools family of the line grammar: tools (gen#664, gen#513).

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Drill Driver", "Combi Drill", "Hammer Drill", "Corded Drill", "Impact Driver",
    "SDS Hammer Drill", "Drill Bit Set", "Tool Kit", "Step Ladder",
    "Bit Set", "Screwdriver Set", "Socket Set", "Caulking Gun", "Glue Gun",
    "Jump Leads", "Cable Ties", "Foot Pumps", "Wireless Charger", "Fridge Thermometer", "Heater",
    "Desk Fan", "Pedestal Fan", "Tower Fan", "Ceiling Fan", "Handheld Fan",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Torque", "Grip", "Drive", "Anvil", "Lever", "Gear", "Crank", "Pivot", "Ratchet", "Forge",
    "Workshop", "Bench", "Rivet", "Power", "Volt", "Amp", "Watt", "Dynamo", "Breeze", "Gust",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (10, 20, 30, 40, 50, 60, 70, 80)
