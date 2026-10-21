"""Text-match decoys for the cups (gen#620): bras named for their cup.

A bare ``cup`` meets drinkware and, in the baseline, the cup of a bra. The real cups now carry
realistic titles of six to ten words, so a short "Full Cup Bra" outscores them, as it does on a
shop's own search. Each decoy is a bra by every structured field (department, category path under
Bras, product type, drawing); only the title holds the word, and the title states the bra facet
its leaf implies (gen#165: a "Full Cup Bra" sits under Full Cup Bras, a "Demi Cup Bra" under Demi
Cup Bras), so the fields tell the truth and the title does not mislead about the bra. The category
policy of the cups (gen#125 class 15) routes ``cup`` to the drinkware and drops them. Relates to
gen#520 and gen#508, the plural-cups bras.

The rows are class 8 (``noun`` is ``cup``), made with the table's row maker; none crosses into
another department (a bra is Womens, so ``cross`` stays off).
"""

from __future__ import annotations

from decoy_kind import Kind

_BRAS = ("Womens", "Lingerie", "Bras")
_DEPARTMENT = "Lingerie & Nightwear"


def _bra(leaf: str, brand: str, price: float) -> Kind:
    return Kind(_DEPARTMENT, (*_BRAS, leaf), "Bra", "bra", brand, price, audience="adult")


KINDS = {
    "cup_bra_full": _bra("Full Cup Bras", "Saltmarsh", 22.0),
    "cup_bra_demi": _bra("Demi Cup Bras", "Wrenfield", 20.0),
    "cup_bra_moulded": _bra("Moulded Cup Bras", "Saltmarsh", 24.0),
    "cup_bra_soft": _bra("Soft Cup Bras", "Wrenfield", 16.0),
    "cup_bra_spacer": _bra("Spacer Cup Bras", "Saltmarsh", 26.0),
    "cup_bra_balcony": _bra("Balcony Bras", "Wrenfield", 21.0),
    "cup_bra_cotton": _bra("Cotton Bras", "Saltmarsh", 18.0),
}


def word_rows(d):
    def cup(n, kind, title, desc, color):
        """A bra whose short title holds ``cup``; the category policy drops it from a cup query."""
        return d(n, kind, title, desc, color, "cup", "cup", "category", cross=False)

    return (
        cup(620, "cup_bra_full", "Full Cup Bra",
            "A full cup bra in smooth fabric, with wide straps and a three hook back.", "Black"),
        cup(621, "cup_bra_demi", "Demi Cup Bra",
            "A demi cup bra with a low neckline, soft straps and a hook and eye back.", "Pink"),
        cup(622, "cup_bra_moulded", "Moulded Cup Bra",
            "A seamless bra with moulded cups that keep their shape under a fitted top.", "Navy"),
        cup(623, "cup_bra_balcony", "Quarter Cup Bra",
            "A bra with a quarter cup that sits low on the bust, for a wide neckline.", "White"),
        cup(624, "cup_bra_soft", "Soft Cup Bra",
            "A soft cup bra with no wire and no padding, for comfort all day.", "Cream"),
        cup(625, "cup_bra_spacer", "Spacer Cup Bra",
            "A bra with light spacer foam cups, smooth under a t-shirt.", "Navy"),
        cup(626, "cup_bra_cotton", "Cotton Full Cup Bra",
            "A cotton bra with full cups and a stretch band, for every day.", "White"),
    )
