"""The cleaning family of the line grammar: household cleaners (gen#666, gen#513).

A title leads with the brand and a model, then the scent and the kind, e.g.
"Soapwell Keen Plus 4 Lemon Floor Cleaner". The lead words are plain words of public
household-care listings, not names, places or words another family uses.
"""

from __future__ import annotations

KINDS = (
    "Laundry Detergent", "Floor Cleaner", "Bathroom Cleaner", "Dish Soap", "Glass Cleaner",
    "Air Freshener", "Fabric Softener", "Kitchen Cleaner", "Toilet Cleaner",
)  # fmt: skip
#: The lead word of a model: a plain word of household-care listings ("Keen", "Total").
LEADS = (
    "Keen", "Total", "Intense", "Express", "Advanced", "Ultimate", "Strong", "Maximum", "Turbo",
    "Mighty", "Dynamic", "Precision", "Optimum", "Exemplar", "Tough", "Solid", "Spotless", "Nimble",
    "Force", "Fusion", "Shield", "Defence", "Energy", "Aegis", "Focus", "Clarity", "Resolute",
    "Stalwart", "Zenith", "Expert", "Ideal", "Swift",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Plus", "Max", "Pro", "Ultra", "Extra")
#: The generations a model is in.
NUMBERS = tuple(range(2, 10))
