"""The beauty family of the line grammar: hand wash, make-up, creams, hair care (gen#666, gen#513).

A title leads with the brand and a model, then the shade or scent and the kind, e.g.
"Larkmoor Lasting Rich 3 Rose Lipstick". The lead words are plain words of public beauty
listings, not names, places or words another family uses.
"""

from __future__ import annotations

KINDS = (
    "Hand Wash", "Shower Gel", "Lipstick", "Foundation", "Hand Cream", "Body Cream",
    "Eye Cream", "Foot Cream", "Body Lotion", "Moisturiser", "Conditioner", "Shampoo",
    "Wash Bag", "Make-Up Bag", "Lip Balm", "Eyeliner", "Perfume",
)  # fmt: skip
#: The lead word of a model: a plain word of beauty listings ("Lasting", "Perfect").
LEADS = (
    "Lasting", "Perfect", "Flawless", "Nurture", "Renew", "Revive", "Lustrous", "Longwear",
    "Infinite", "Absolute", "Elegance", "Allure", "Ritual", "Nourish", "Radiance", "Define",
    "Sculpt",
    "Enhance", "Devotion", "Silken", "Indulge", "Whisper", "Cherish", "Velvet", "Desire",
    "Sublime", "Exquisite", "Divine", "Luxe", "Vitality", "Glamour", "Pristine", "Refine",
    "Restore",
    "Replenish", "Hydrate", "Soothe", "Prestige", "Serenity", "Supple",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Plus", "Lite", "Rich", "Pro", "Extra")
#: The generations a model is in.
NUMBERS = tuple(range(2, 10))
