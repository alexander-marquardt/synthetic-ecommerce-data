"""The sport family of the line grammar: running shoes and bikes (gen#662, gen#513).

A model is a performance word alone, then a use, e.g. "Tempo Trail Running Shoes": a
generation number read as synthetic (#851). A bike's model is a series its brand owns.
"""

from __future__ import annotations

KINDS = ("Running Shoes", "Bicycle")
#: The lead word of a model: a performance word.
LEADS = (
    "Speed", "Ultra", "Fast", "Sport", "Performance", "Tempo", "Pace", "Race", "Aero", "Glide",
    "Rapid", "Boost", "Surge", "Velocity", "Stride", "Momentum", "Cadence", "Kinetic",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations a model is in.
NUMBERS = tuple(range(2, 10))
