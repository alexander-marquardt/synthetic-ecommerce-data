"""The sport family of the line grammar: running shoes and bikes (gen#662, gen#513).

A model is a performance word, an optional sub-model and a generation number or a code, then a
use, e.g. "Tempo Max 3 Trail Running Shoes".
"""

from __future__ import annotations

KINDS = ("Running Shoes", "Bicycle")
#: The lead word of a model: a performance word.
LEADS = (
    "Speed", "Ultra", "Fast", "Sport", "Performance", "Tempo", "Pace", "Race", "Aero", "Glide",
    "Rapid", "Boost", "Surge", "Velocity",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations a model is in.
NUMBERS = tuple(range(2, 10))
#: What a running shoe is for, between the model and the kind.
USES = ("Road", "Trail", "Neutral Road", "Cushioned Road", "Stability Road", "Neutral Trail")
