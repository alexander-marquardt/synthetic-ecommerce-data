"""The beauty family of the line grammar: hand wash, make-up, creams, hair care (gen#666, gen#513).

A title leads with the brand and a model, then the shade or scent and the kind, e.g.
"Larkmoor Lasting Rose Lipstick". The lead words are plain words of public beauty
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
#: More lead words the grocery build deals with the odd half of ``LEADS`` (#851). A grocery
#: hand wash or cream is one scent in its pack sizes, so a brand's titles are its words times
#: the scents, and a model is a word alone ("Prestige Honey Body Milk", never "Prestige Pro 4").
GROCERY_LEADS = (
    "Dew", "Elixir", "Cocoon", "Embrace", "Caress", "Lumina", "Opulence", "Grace", "Splendor",
    "Tranquil", "Adore", "Reverie", "Precious", "Purity", "Oasis", "Cosset", "Indulgence",
    "Enchant", "Enrich", "Featherlight", "Botanica", "Lush", "Dreamy", "Bespoke", "Timeless",
    "Ageless", "Youthful", "Rebalance", "Illuminate", "Cleanse", "Purify", "Nectar", "Gossamer",
    "Radiate", "Luminosity", "Starlit", "Moonlit", "Velveteen", "Sumptuous", "Decadence",
    "Splendid", "Majesty", "Royale", "Couture", "Chic", "Muse", "Belle", "Gorgeous", "Flourish",
    "Thrive", "Blissful", "Elysian", "Halcyon", "Idyll", "Heavenly", "Angelic", "Ethereal",
    "Celestial", "Reveal", "Rescue",
)  # fmt: skip
#: The sub-model word an authored model may carry after the lead.
SUBS = ("Plus", "Lite", "Rich", "Pro", "Extra")
#: The generations a model is in.
NUMBERS = tuple(range(2, 10))
