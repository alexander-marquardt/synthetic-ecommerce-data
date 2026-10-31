"""The breadth rows of the Food & Drink department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

# --------------------------------------------------------------------------
# Food & Drink: the tea's blend or the coffee's origin varies; the pack is drawn.
# --------------------------------------------------------------------------

_TEA = ("Food & Drink", "Drinks", "Tea")
_COFFEE = ("Food & Drink", "Drinks", "Coffee")
_JAM = ("Food & Drink", "Food Cupboard", "Jam")
_CHUTNEY = ("Food & Drink", "Food Cupboard", "Chutney")
_FD = "Food & Drink"


def _fruit(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("fruit", "Fruit", v),)


def _flavor(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("flavor", "Flavor", v),)


def _blend(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("blend", "Blend", v),)


def _origin(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("origin", "Origin", v),)


def _shape(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("pasta_shape", "Pasta shape", v),)


_CRISPS = ("Food & Drink", "Biscuits & Snacks", "Crisps")
_OIL = ("Food & Drink", "Food Cupboard", "Olive Oil")
_PASTA = ("Food & Drink", "Food Cupboard", "Pasta")


FOOD = (
    Row("TEABRK", "English Breakfast Tea, 80 Bags", "Hearth & Table", _FD, _TEA, "Tea", 3.5,
        "box", "Round bags in a recyclable box, for a strong cup with or without milk.",
        (cw("Red", "#9e2a2b", "solid", "#efe8d8"),), _blend("English Breakfast"), label="Tea",
        colorless=True),
    Row("TEAASM", "Assam Loose Leaf Tea Caddy", "Kettleby Tea Co.", _FD, _TEA, "Tea", 7.0,
        "tin", "A 125 g caddy of whole leaf with a tight lid. Brew 4 minutes in boiled water.",
        (cw("Black", "#2a2a2e", "solid", "#d4af37"),), _blend("Assam"), label="Tea",
        colorless=True),
    Row("TEAJAS", "Jasmine Green Tea Gift Tin", "Kettleby Tea Co.", _FD, _TEA, "Tea", 9.0,
        "tin", "Twenty silk pyramid bags in a printed tin, gift ready with a ribbon.",
        (cw("Teal", "#1c7c7d", "solid", "#efe8d8"),), _blend("Jasmine Green"), label="Tea",
        colorless=True),
    Row("COFCOL", "Colombian Ground Coffee, 227g", "Pantry Mill", _FD, _COFFEE, "Coffee", 4.0,
        "tin", "Medium roast, ground for a French press or a filter machine. Reseal after use.",
        (cw("Brown", "#5a3a26", "solid", "#d4af37"),), _origin("Colombian"), label="Coffee",
        colorless=True),
    Row("COFETH", "Ethiopian Coffee Beans, 1kg", "Brewhollow Roasters", _FD, _COFFEE, "Coffee",
        16.0, "box",
        "Whole beans, roasted in small batches and packed with a one-way valve.",
        (cw("Cream", "#efe8d8", "solid", "#5a3a26"),), _origin("Ethiopian"), label="Coffee",
        colorless=True),
    Row("COFBRZ", "Brazilian Coffee Pods, Pack of 30", "Brewhollow Roasters", _FD, _COFFEE,
        "Coffee", 7.5, "box_wide",
        "Compostable pods for most pod machines, a smooth medium roast.",
        (cw("Black", "#2a2a2e", "solid", "#c98a2e"),), _origin("Brazilian"), label="Coffee",
        colorless=True),
    # Round 2 (gen#125): at the ceiling, food held 45 styles against a half share of 91.
    Row("TEAEGR", "Earl Grey Tea, 40 Bags", "Kettleby Tea Co.", _FD, _TEA, "Tea", 3.0, "box",
        "String-and-tag bags in a foil-lined box. Brew 3 minutes, best without milk.",
        (cw("Navy", "#26365c", "solid", "#d4af37"),), _blend("Earl Grey"), label="Tea",
        colorless=True),
    Row("TEAPEP", "Peppermint Tea Pyramids", "Hearth & Table", _FD, _TEA, "Tea",
        2.5, "box",
        "Fifteen pyramid bags of whole leaves, for a cup after a meal.",
        (cw("Green", "#4f7a3a", "solid", "#ffffff"),), _blend("Peppermint"), label="Tea",
        colorless=True),
    Row("TEAROO", "Rooibos Loose Tea Pouch, 250g", "Kettleby Tea Co.", _FD, _TEA, "Tea", 6.0,
        "tin", "A resealable pouch of cut leaf for a teapot or an infuser. Brew 5 minutes.",
        (cw("Rust", "#a8502e", "solid", "#efe8d8"),), _blend("Rooibos"), label="Tea",
        colorless=True),
    Row("COFSUM", "Sumatran Dark Roast Espresso Beans", "Brewhollow Roasters", _FD, _COFFEE,
        "Coffee", 9.0, "box",
        "Oily, full-bodied beans for an espresso machine or a stovetop pot, 500 g.",
        (cw("Charcoal", "#3a3a3e", "solid", "#c98a2e"),), _origin("Sumatran"),
        label="Coffee", colorless=True),
    Row("COFGUA", "Guatemalan Instant Coffee Jar", "Pantry Mill", _FD, _COFFEE, "Coffee", 5.0,
        "jar", "Freeze-dried granules in a 100 g glass jar: one spoon per mug.",
        (cw("Brown", "#5a3a26", "solid", "#efe8d8"),), _origin("Guatemalan"), label="Coffee",
        colorless=True),
    Row("JAMSTR", "Strawberry Jam, 340g", "Hearth & Table", _FD, _JAM, "Jam", 2.0, "jar",
        "A set jam made in small batches with whole fruit and cane sugar.",
        (cw("Red", "#b8322f", "solid", "#efe8d8"),), _fruit("Strawberry"), label="Jam",
        colorless=True),
    Row("JAMRSP", "Raspberry Extra Fruit Conserve", "Pantry Mill", _FD, _JAM, "Jam", 3.2,
        "jar", "A soft-set conserve with more fruit than sugar. Refrigerate once opened.",
        (cw("Raspberry", "#a3214a", "solid", "#ffffff"),), _fruit("Raspberry"), label="Jam",
        colorless=True),
    Row("JAMAPR", "Apricot Reduced Sugar Jam", "Hearth & Table", _FD, _JAM, "Jam", 2.4, "jar",
        "A lighter jam with a third less sugar, for toast, yogurt or a sponge filling.",
        (cw("Amber", "#e09a3a", "solid", "#efe8d8"),), _fruit("Apricot"), label="Jam",
        colorless=True),
    Row("JAMBLK", "Blackcurrant Jam Gift Jar", "Pantry Mill", _FD, _JAM, "Jam", 4.5, "jar",
        "A 450 g jar with a gingham lid cover and a tied label, ready to give.",
        (cw("Plum", "#4b2238", "solid", "#c8312e"),), _fruit("Blackcurrant"), label="Jam",
        colorless=True),
    Row("JAMDAM", "Damson Preserve, Farmhouse Recipe", "Hearth & Table", _FD, _JAM, "Jam", 3.0,
        "jar", "A rich preserve cooked slowly in open pans, in a 340 g jar.",
        (cw("Damson", "#4a2040", "solid", "#efe8d8"),), _fruit("Damson"), label="Jam",
        colorless=True),
    Row("CHTONI", "Caramelised Onion Chutney", "Hearth & Table", _FD, _CHUTNEY, "Chutney",
        2.8, "jar", "A sweet, sticky chutney for cheese boards and sausages, 300 g.",
        (cw("Brown", "#6b3f24", "solid", "#efe8d8"),), _flavor("Caramelised Onion"),
        label="Chutney", colorless=True),
    Row("CHTTOM", "Spiced Tomato Chutney, Large Jar", "Pantry Mill", _FD, _CHUTNEY, "Chutney",
        3.5, "jar", "A chunky chutney with a gentle warmth, in a 450 g jar.",
        (cw("Red", "#9e2a2b", "solid", "#efe8d8"),), _flavor("Spiced Tomato"),
        label="Chutney", colorless=True),
    Row("CHTMAN", "Mango Chutney with Nigella Seeds", "Hearth & Table", _FD, _CHUTNEY,
        "Chutney", 2.2, "jar", "A sweet chutney with a little spice. Keep chilled once opened.",
        (cw("Amber", "#e09a3a", "solid", "#2a2a2e"),), _flavor("Mango"), label="Chutney",
        colorless=True),
    Row("CHTAPL", "Apple and Ale Chutney Gift Jar", "Pantry Mill", _FD, _CHUTNEY, "Chutney",
        4.0, "jar", "A ploughman's chutney in a 340 g jar, boxed with a recipe card.",
        (cw("Brown", "#7a5a3a", "solid", "#d4af37"),), _flavor("Apple and Ale"),
        label="Chutney", colorless=True),
    # Growth round 3: crisps by flavor, olive oil by origin, pasta by shape.
    Row("CRSSEA", "Sea Salt Hand Cooked Crisps", "Pantry Mill", _FD, _CRISPS, "Crisps", 1.6,
        "crisps_bag", "Thick-cut potatoes cooked in small batches, in a sharing bag.",
        (cw("Navy", "#26365c", "solid", "#efe8d8"),), _flavor("Sea Salt"),
        (("150g", 1.6), ("6 x 25g", 2.2)), "Crisps", colorless=True),
    Row("CRSCHO", "Cheese & Onion Crinkle Cut Crisps", "Freshfold", _FD, _CRISPS, "Crisps", 1.5,
        "crisps_bag", "Ridged crisps with a crunch that holds a dip, in a sharing bag.",
        (cw("Green", "#4f7a3a", "solid", "#efe8d8"),), _flavor("Cheese & Onion"),
        (("150g", 1.5), ("6 x 25g", 2.0)), "Crisps", colorless=True),
    Row("CRSVIN", "Salt & Vinegar Lattice Crisps", "Hearth & Table", _FD, _CRISPS, "Crisps",
        1.8, "crisps_bag", "Lattice-cut potato crisps, cooked in sunflower oil.",
        (cw("Teal", "#1c7c7d", "solid", "#efe8d8"),), _flavor("Salt & Vinegar"),
        label="Crisps", colorless=True),
    Row("CRSPAP", "Smoked Paprika Ridged Crisps", "Pantry Mill", _FD, _CRISPS, "Crisps", 1.7,
        "crisps_bag", "Deep ridged crisps for a party bowl, in a resealable bag.",
        (cw("Red", "#9e2a2b", "solid", "#efe8d8"),), _flavor("Smoked Paprika"),
        label="Crisps", colorless=True),
    Row("OILGRK", "Greek Extra Virgin Olive Oil", "Hearth & Table", _FD, _OIL, "Olive Oil",
        6.0, "bottle", "Cold pressed from a single harvest, for dressings and dipping bread.",
        (cw("Green", "#4f7a3a", "solid", "#d4af37"),), _origin("Greek"),
        ((500.0, 6.0), (750.0, 8.5), (1000.0, 10.5)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
    Row("OILSPA", "Spanish Extra Virgin Olive Oil", "Pantry Mill", _FD, _OIL, "Olive Oil", 5.0,
        "bottle", "A fruity first pressing in a dark glass bottle that keeps out the light.",
        (cw("Black", "#2a2a2e", "solid", "#d4af37"),), _origin("Spanish"),
        ((500.0, 5.0), (750.0, 7.0), (1000.0, 9.0)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
    Row("OILITA", "Italian Extra Virgin Olive Oil Tin", "Freshfold", _FD, _OIL, "Olive Oil",
        9.0, "tin", "A tin of peppery oil, picked early in the season.",
        (cw("Red", "#9e2a2b", "solid", "#efe8d8"),), _origin("Italian"),
        ((500.0, 9.0), (750.0, 12.0), (1000.0, 15.5)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
    Row("OILPOR", "Portuguese Extra Virgin Olive Oil", "Hearth & Table", _FD, _OIL, "Olive Oil",
        7.0, "bottle", "A mild, buttery oil for cooking and finishing.",
        (cw("Teal", "#1c7c7d", "solid", "#d4af37"),), _origin("Portuguese"),
        ((500.0, 7.0), (750.0, 9.5), (1000.0, 12.0)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
    Row("PSTPEN", "Penne Durum Wheat Pasta", "Pantry Mill", _FD, _PASTA, "Pasta", 1.0, "box",
        "Bronze die cut for a rough surface that holds the sauce. Cooks in 11 minutes.",
        (cw("Blue", "#3f6fb5", "solid", "#efe8d8"),), _shape("Penne"),
        (("500g", 1.0), ("1kg", 1.8)), "Pasta", colorless=True),
    Row("PSTFUS", "Fusilli Durum Wheat Pasta", "Hearth & Table", _FD, _PASTA, "Pasta", 1.2,
        "box", "Slow dried at a low heat for a firm bite. Cooks in 10 minutes.",
        (cw("Red", "#9e2a2b", "solid", "#efe8d8"),), _shape("Fusilli"),
        (("500g", 1.2), ("1kg", 2.1)), "Pasta", colorless=True),
    Row("PSTRIG", "Rigatoni Organic Pasta", "Freshfold", _FD, _PASTA, "Pasta", 1.6, "box",
        "Made from organic durum wheat semolina and water, nothing else.",
        (cw("Green", "#4f7a3a", "solid", "#efe8d8"),), _shape("Rigatoni"), label="Pasta",
        colorless=True),
    Row("PSTFAR", "Farfalle Durum Wheat Pasta", "Pantry Mill", _FD, _PASTA, "Pasta", 1.1, "box",
        "A 500 g box for a family pasta bake. Cooks in 12 minutes.",
        (cw("Yellow", "#f2d14b", "solid", "#2a2a2e"),), _shape("Farfalle"), label="Pasta",
        colorless=True),
    # gen#198: the tableware rows grew Home, so these lift Food & Drink back over half its
    # fair share of styles (tests/test_retail_scale.py), as the round 2 food rows did.
    Row("PSTLIN", "Linguine Durum Wheat Pasta", "Freshfold", _FD, _PASTA, "Pasta", 1.3, "box",
        "Flat ribbons that carry a seafood or pesto sauce. Cooks in 9 minutes.",
        (cw("Orange", "#e07a1f", "solid", "#efe8d8"),), _shape("Linguine"), label="Pasta",
        colorless=True),
    Row("PSTCON", "Conchiglie Durum Wheat Pasta", "Hearth & Table", _FD, _PASTA, "Pasta", 1.1,
        "box", "Ridged shells that scoop up a chunky sauce. Cooks in 11 minutes.",
        (cw("Navy", "#26365c", "solid", "#efe8d8"),), _shape("Conchiglie"),
        (("500g", 1.1), ("1kg", 1.9)), "Pasta", colorless=True),
    Row("OILCRO", "Croatian Extra Virgin Olive Oil", "Freshfold", _FD, _OIL, "Olive Oil", 9.0,
        "bottle", "A green, peppery oil from Istrian groves.",
        (cw("Green", "#4f7a3a", "solid", "#d4af37"),), _origin("Croatian"),
        ((500.0, 9.0), (750.0, 12.5), (1000.0, 16.0)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
    Row("OILTUN", "Tunisian Extra Virgin Olive Oil", "Pantry Mill", _FD, _OIL, "Olive Oil", 6.0,
        "bottle", "A smooth, fruity oil for dressings and baking.",
        (cw("Yellow", "#f2d14b", "solid", "#2a2a2e"),), _origin("Tunisian"),
        ((500.0, 6.0), (750.0, 8.5), (1000.0, 10.5)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
    Row("OILSIC", "Sicilian Extra Virgin Olive Oil", "Hearth & Table", _FD, _OIL, "Olive Oil",
        10.0, "bottle", "A grassy, artichoke-sharp oil for bread and salads.",
        (cw("Green", "#4f7a3a", "solid", "#d4af37"),), _origin("Sicilian"),
        ((500.0, 10.0), (750.0, 13.5), (1000.0, 17.0)), "Olive Oil", colorless=True,
        size_key="net_volume_ml"),
)  # fmt: skip
