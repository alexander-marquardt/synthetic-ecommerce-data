"""Text-match decoys for ``beach towel`` (gen#605, the rule of #294 and #326).

Every top result for ``beach towel`` was a beach towel or a towel of another kind, so a search for
it showed nothing about how the engine tells a towel from something named for one. A shopper does
meet such products: terry-towelling clothes sold as a "beach towel stripe", a hooded towelling
poncho or robe for a child, a swim shorts and towel set, and a bag made to carry the towel. Each of
the eight rows holds the exact words ``beach`` and ``towel`` in a title of 3 to 5 words, in the
department and the category it really belongs to (Clothing, not Home). The structured fields and
the drawing tell the truth, so a department policy drops every one of them: none is in the
interpreted "Best" results, and only the raw text-match view shows them.

The three classes:

* women's terry clothes in a "beach towel stripe" (shorts, a shirt and a top). The stripe is the
  record's pattern and the drawing shows it (``decoy_product_words.Row.style`` draws a stripe
  colorway for a Kind whose pattern is stripe); the shorts' fabric is Towelling, as their text says;
* kids' and babies' hooded towelling ponchos and robes, in the kids' dressing gowns, drawn as a
  hooded towelling gown (a poncho with no belt);
* a swim shorts and towel set in the swim shorts, and a tote bag.

The rows are class 8 (``noun`` is ``towel``), made with the table's row maker.
``tests/test_retail_beach_towel_decoys_605.py`` holds the proof.
"""

from __future__ import annotations

from decoy_kind import Kind

_UK = ("6", "8", "10", "12", "14", "16")
_KIDS = ("3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs")
_BABY = ("0-3 Mths", "3-6 Mths", "6-9 Mths", "9-12 Mths")
_LETTER = ("S", "M", "L", "XL", "XXL")
_STRIPE = {"pattern": "stripe"}


def _gown(sizes: tuple[str, ...], belt: str, length: str, price: float) -> Kind:
    """A hooded towelling dressing gown of the kids' leaf (``belt`` "no" is a poncho)."""
    return Kind(
        "Lingerie & Nightwear",
        ("Kids", "Nightwear", "Dressing Gowns"),
        "Dressing Gown",
        "dressing_gown",
        "Little Fernby",
        price,
        "kids",
        params=(
            ("length", length),
            ("hood", "yes"),
            ("belt", belt),
            ("fabric", "towelling"),
        ),
        extra=(
            ("fabric", "Fabric", "Towelling"),
            ("length", "Length", length.capitalize()),
            ("hood", "Hood", "Yes"),
            ("belt", "Belt", belt.capitalize()),
        ),
        sizes=sizes,
        size_range="regular",
    )


KINDS = {
    "bt_shorts": Kind(
        "Clothing",
        ("Womens", "Shorts"),
        "Shorts",
        "shorts",
        "Larkmoor",
        16.0,
        params=(("length", "mid"), ("style", "sweat"), ("pocket", "yes")),
        extra=(
            ("shorts_style", "Style", "Sweat"),
            ("garment_length", "Length", "Mid Length"),
            ("fabric", "Fabric", "Towelling"),
            ("waist_type", "Waist type", "Elastic"),
            ("pockets", "Pockets", "Yes"),
        ),
        sizes=_UK,
        size_range="regular",
        **_STRIPE,
    ),
    "bt_shirt": Kind(
        "Clothing",
        ("Womens", "Tops", "Shirts", "Oxford Shirts"),
        "Shirt",
        "blouse",
        "Wrenfield",
        24.0,
        sizes=_UK,
        size_range="regular",
        **_STRIPE,
    ),
    "bt_top": Kind(
        "Clothing",
        ("Womens", "Tops", "Jersey Tops"),
        "Top",
        "top",
        "Larkmoor",
        14.0,
        sizes=_UK,
        size_range="regular",
        **_STRIPE,
    ),
    "bt_poncho": _gown(_KIDS, "no", "short", 14.0),
    "bt_robe": _gown(_KIDS, "yes", "knee", 16.0),
    "bt_baby_robe": _gown(_BABY, "yes", "knee", 12.0),
    "bt_swim_shorts": Kind(
        "Clothing",
        ("Mens", "Swimwear", "Swim Shorts"),
        "Swim Shorts",
        "swim_shorts",
        "Harbour & Pine",
        16.0,
        params=(("length", "mid"), ("waist", "drawstring")),
        extra=(
            ("length", "Length", "Mid"),
            ("waist_type", "Waist type", "Drawstring"),
            ("quick_dry", "Quick dry", "Yes"),
        ),
        sizes=_LETTER,
        size_range="regular",
    ),
}


def word_rows(d):
    def b(n, kind, title, desc, color, **kw):
        """A decoy of the Beach Towel: another department's product holding ``beach towel``."""
        return d(n, kind, title, desc, color, "beach towel", "towel", "department", **kw)

    return (
        b(6050, "bt_shorts", "Beach Towel Stripe Shorts",
          "Terry towelling shorts in a wide beach towel stripe, with an elastic waist and pockets.",
          "Blue"),
        b(6051, "bt_shirt", "Beach Towel Stripe Shirt",
          "A relaxed terry towelling shirt in a beach towel stripe, with a collar and buttons.",
          "Cream"),
        b(6052, "bt_top", "Beach Towel Stripe Top",
          "A soft terry towelling top in a beach towel stripe, with short sleeves.", "Pink"),
        b(6053, "bt_poncho", "Kids Hooded Beach Towel Poncho",
          "A towelling poncho with a hood, for a child to pull on after a swim.", "Blue"),
        b(6054, "bt_robe", "Kids Beach Towel Robe",
          "A towelling robe with a hood and a tie belt, for a child coming off the beach.",
          "Green"),
        b(6055, "bt_baby_robe", "Baby Beach Towel Robe",
          "A soft towelling robe with a hood and a tie belt, for a baby after a bath.", "Cream"),
        b(6056, "bt_swim_shorts", "Beach Towel & Shorts Set",
          "Mid length swim shorts with a drawstring waist, sold with a matching towelling wrap.",
          "Navy"),
        b(6057, "s_tote", "Beach Towel Tote Bag",
          "A canvas tote with a wide gusset, big enough to carry a rolled up towel.", "Navy"),
    )
