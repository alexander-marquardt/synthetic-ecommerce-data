"""Class-8 decoys of the memory card (gen#796): "memory card" in another product's title.

The memory card has a home since gen#796 (Electronics > Accessories > Memory Cards), so the
"memory card" words now carry decoys of their own (the rule of gen#294). A zip wallet that stores
cards is a travel case of another department, dropped by the department policy; it sits in a
clothing root, so it is not a ``cross`` row (the gift card holder of gen#437 is not either). A laptop sleeve
with a pocket for a card stays in Electronics, so the category policy drops it. The toys' "Memory
Card Game" and the greeting cards were already cross-department "card" products and are not added
here. No title or description names a color.
"""

# ruff: noqa: E501 -- data tables and descriptions read better whole than wrapped.

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.decoy_kind import Kind

#: The sleeve is an Electronics laptop sleeve, drawn as one, under the house brand of the travel case.
KINDS = {
    "mc_sleeve": Kind("Electronics", ("Electronics", "Accessories", "Laptop Sleeves"), "Laptop Sleeve", "laptop_sleeve", "Hearth & Table", 21.0),
}  # fmt: skip

#: Rows of (number, kind, title, description, color, policy).
_ROWS = (
    (7960, "case", "Memory Card Storage Wallet", "A slim zip wallet with slots that hold eight SD and microSD cards safe from dust.", "Black", "department"),
    (7961, "mc_sleeve", "Memory Card Pocket Laptop Sleeve", "A padded sleeve for a laptop, with a small zipped pocket for spare cards and a USB stick.", "Grey", "category"),
)  # fmt: skip


def word_rows(d):
    return tuple(
        d(n, kind, title, desc, color, "memory card", "memory", policy, device_type="Memory Card")
        for n, kind, title, desc, color, policy in _ROWS
    )
