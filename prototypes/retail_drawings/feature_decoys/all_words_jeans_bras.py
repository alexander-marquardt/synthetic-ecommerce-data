"""Decoys for "mens black jeans" and "white minimiser bras" that hold every query word (gen#711).

The head tier of the live search keeps only products that hold every word of the query. So a
decoy of a three-word query reaches the page with interpretation off only if it holds all three
words. The color-word decoys of these two queries (a chino or a shirt from a range named "Black")
lack ``jeans`` and never reached the page, so it led with the real thing both with interpretation
off and with it on, and the demo had nothing to show.

Each row here is an accessory or a companion that a shop sells for the product and names after
it. Its title holds every word of the query:

* ``mens black jeans``: two men's black belts cut for jeans (Mens > Accessories > Belts),
  black hangers for men's jeans (Home > Storage > Hangers) and a men's black denim shirt, a
  "jeans shirt", cut to wear with black jeans (Mens > Tops > Shirts > Denim Shirts);
* ``white minimiser bras``: a wash bag and a travel case for white minimiser bras (Home >
  Laundry, Womens > Accessories > Travel) and the white briefs that match the minimiser bra
  (Womens > Lingerie > Knickers).

Each is a type the build already sells, filed in that type's own leaf, priced inside the band
of the ordinary products of that type, and drawn as what it is. None sits under Jeans or Bras,
so the category policy drops every one of them when interpretation is on. The rows are class 8
(``noun`` is the query's product word), made with the table's row maker. The jeans rows sell
fewer than the table's default, so that ``black jeans`` still leads with the decoys of gen#311.
``tests/test_retail_all_words_decoys_711.py`` holds the proof.
"""

from __future__ import annotations

from decoy_kind import Kind

_BELTS = ("Mens", "Accessories", "Belts")


def _belt(material: str, buckle: str, price: float) -> Kind:
    """A men's belt as the belt type spec states one: material, buckle and audience."""
    return Kind(
        "Clothing",
        _BELTS,
        "Belt",
        "belt_buckled",
        "Wrenfield",
        price,
        params=(("material", material), ("buckle", buckle)),
        extra=(
            ("material", "Material", material),
            ("buckle", "Buckle", buckle),
            ("audience", "Audience", "Mens"),
        ),
    )


KINDS = {
    "aw_leather_belt": _belt("Leather", "Pin", 18.0),
    "aw_canvas_belt": _belt("Canvas", "Plate", 10.0),
    "aw_denim_shirt": Kind(
        "Clothing",
        ("Mens", "Tops", "Shirts", "Denim Shirts"),
        "Shirt",
        "blouse",
        "Wrenfield",
        28.0,
        extra=(
            ("fit", "Fit", "Regular"),
            ("material", "Material", "Stretch Denim"),
            ("sleeve_length", "Sleeve length", "Long"),
            ("collar", "Collar", "Western Yoke"),
        ),
        sizes=("S", "M", "L", "XL", "XXL"),
        size_range="regular",
    ),
    "aw_briefs": Kind(
        "Lingerie & Nightwear",
        ("Womens", "Lingerie", "Knickers"),
        "Knickers",
        "knickers",
        "Saltmarsh",
        6.0,
        params=(("cut", "brief"), ("trim", "plain")),
        extra=(
            ("cut", "Cut", "Full Briefs"),
            ("fabric", "Fabric", "Microfiber"),
            ("pack_size", "Pack size", "Single"),
        ),
        sizes=("8", "10", "12", "14", "16", "18"),
        size_range="regular",
    ),
}


def word_rows(d):
    def jeans(n, kind, title, desc):
        # Sold below the table's default: at 2000 the rows took the top 3 of "black jeans"
        # from the sibling-color decoys of gen#311; at 600 they still lead "mens black jeans".
        return d(n, kind, title, desc, "Black", "mens black jeans", "jean", "category", sold=600)

    def bras(n, kind, title, desc):
        return d(n, kind, title, desc, "White", "white minimiser bras", "bra", "category")

    return (
        jeans(7110, "aw_leather_belt", "Mens Black Leather Jeans Belt",
              "A 4 cm black leather belt with a pin buckle, wide enough for the loops of men's "
              "jeans."),
        jeans(7111, "aw_canvas_belt", "Mens Black Canvas Jeans Belt",
              "A black woven canvas belt with a plate buckle that slides to fit, for jeans and "
              "chinos."),
        jeans(7112, "hangers", "Black Hangers for Mens Jeans",
              "Five black clip hangers that hold a pair of men's jeans by the waistband."),
        jeans(7116, "aw_denim_shirt", "Mens Black Jeans Shirt",
              "A black stretch denim shirt with a western yoke and press studs, cut to wear "
              "with black jeans."),
        bras(7113, "wash_bag", "White Minimiser Bra Wash Bag",
             "A white mesh bag with a zip that keeps a minimiser bra in shape in the wash."),
        bras(7114, "case", "White Minimiser Bra Travel Case",
             "A white padded zip case that holds two minimiser bras flat in a suitcase."),
        bras(7115, "aw_briefs", "White Minimiser Bra Matching Briefs",
             "White microfiber full briefs cut to match our minimiser bra, with a smooth edge."),
    )  # fmt: skip
