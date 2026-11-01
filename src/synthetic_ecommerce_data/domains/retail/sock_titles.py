"""A real sock's title says how the sock is made, so it is not the shortest of a query (gen#774).

A retailer's sock title is rarely three words, and a short one is what let the real socks fill the
top of a plain match for ``socks``: BM25 favors a short field, and a boot sock's ``text`` already
says the word three times. The generated socks (the color-word decoys and the men's depth rows)
take their detail here; the authored rows carry theirs in their own title. An apparel decoy of
class 1, 2, 6 or 7 keeps the shape its class holds it to (a named part last, a real compound, a
short brand title): it is a demo row of another query.
"""

from __future__ import annotations

#: product type -> what its title adds. Boot socks add the most: they have the shortest ``text``.
DETAIL = {
    "Socks": ", Cushioned Sole",
    "Boot Socks": ", Thick Knit, Cushioned Sole",
    "School Socks": ", Reinforced Heel",
}


def detailed(title: str, product_type: str) -> str:
    """``title`` with the detail of ``product_type``; any other type's title is unchanged."""
    return f"{title}{DETAIL.get(product_type, '')}"
