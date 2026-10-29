"""The furniture family of the line grammar: sofas, beds, tables and storage furniture.

A model is a plain word of the family, an optional sub-model and a number, then the
descriptors and the kind. The lead words are plain English words, not coined brand-sounding
ones, names or places.
"""

from __future__ import annotations

#: The product types of the family.
KINDS = (
    "Sofa", "Corner Sofa", "Chaise Sofa", "Modular Sofa", "Recliner Sofa", "Sofa Bed", "Armchair",
    "Footstool", "Bed", "Dining Table", "Side Table", "Coffee Table", "Dining Chair", "Bookcase",
    "Wardrobe", "Chest of Drawers", "Hallway Stands", "Chairbed", "Mirror",
)  # fmt: skip
#: The lead word of a model.
LEADS = (
    "Settle", "Classic", "Modern", "Tradition", "Essential", "Signature", "Premier", "Relax",
    "Urban", "Heart", "Form", "Simple", "Easy", "Style", "Daily", "Retreat", "Habit", "Ease",
    "Basic", "Select",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SUBS = ("Mini", "Plus", "Max", "Duo", "Lite", "Pro")
#: The numbers a model may carry.
NUMBERS = (210, 220, 230, 240, 310, 320, 330, 340)
