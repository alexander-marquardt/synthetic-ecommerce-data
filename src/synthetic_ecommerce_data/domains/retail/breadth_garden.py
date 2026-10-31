"""The breadth rows of the Garden department (:mod:`breadth_rows`)."""

from __future__ import annotations

from synthetic_ecommerce_data.domains.retail.breadth_row import Row
from synthetic_ecommerce_data.domains.retail.variants import cw

# --------------------------------------------------------------------------
# Garden: one plant per leaf, so its every variety fits every template.
# --------------------------------------------------------------------------

_TREES = ("Garden", "Trees", "Bay Trees")
_OLIVES = ("Garden", "Trees", "Olive Trees")
_TULIP = ("Garden", "Bulbs", "Tulip Bulbs")
_BERRY = ("Garden", "Grow Your Own", "Strawberry Plants")
_MUSH = ("Garden", "Grow Your Own", "Mushroom Kits")
_XMAS = ("Garden", "Trees", "Christmas Trees")
_APPLE = ("Garden", "Trees", "Apple Trees")
_POT = cw("Terracotta", "#b5603a", "solid", "#4f7a3a")


def _form(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("form", "Form", v),)


def _var(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("variety", "Variety", v),)


def _flower(v: str) -> tuple[tuple[str, str, str], ...]:
    """A tulip's flower form: a variety would change the drawn color, a form does not."""
    return (("flower_form", "Flower form", v),)


#: One drawing color for every mushroom kit: a variety changes the cap color.
_MUSH_DRAWN = cw("Natural", "#e6dcc8", "solid", "#7a5a3a")

_HEIGHTS = (("60 cm", 25.0), ("90 cm", 40.0), ("1.2 m", 65.0))
_XMAS_FT = (("5 ft", 45.0), ("6 ft", 55.0), ("7 ft", 70.0))

# gen#509: plants named after a color and a scent, one leaf each (the shopper's word), so the
# category-node policy has a node to route a bare "lavender" or "sage" to. A leaf holds at least
# eight styles at the ceiling (tests/test_retail_plant_nodes_509.py).
_PLANTS = ("Garden", "Plants")
_LAVENDER = (*_PLANTS, "Lavender")
_SAGE = (*_PLANTS, "Herbs", "Sage")
_ROSEMARY = (*_PLANTS, "Herbs", "Rosemary")
_THYME = (*_PLANTS, "Herbs", "Thyme")
_EUCALYPTUS = (*_PLANTS, "Eucalyptus")
_PTERRA = cw("Terracotta", "#b5603a", "solid", "#4f7a3a")
_PZINC = cw("Zinc", "#9aa3a8", "solid", "#4f7a3a")
_PSTONE = cw("Stone", "#c9c1b3", "solid", "#4f7a3a")
_PBLACK = cw("Black", "#2a2a2e", "solid", "#4f7a3a")
_TW, _FN = "Thistle & Wren", "Fenwold Nursery"
_BLOOM, _SAGE_LEAF, _ROSE_LEAF, _THYME_LEAF = "#8c6bb1", "#8fa88a", "#6f8f6a", "#7a9a62"


def _heights(price: float, names: tuple[str, ...]) -> tuple[tuple[str, float], ...]:
    """A plant's height run: the price grows with the height."""
    return tuple((n, round(price * (1 + i * 0.45), 2)) for i, n in enumerate(names))


def _herb(code, title, brand, path, price, text, pot, value, leaves, bloom=""):
    """A potted herb (lavender, sage, rosemary, thyme): a variety, in flower when ``bloom``."""
    return Row(code, title, brand, "Garden", path, "Plant", price, "potted_herb", text, (pot,),
               _var(value), _heights(price, ("15 cm", "25 cm")), "Plant", colorless=True,
               params=(("leaves", leaves), *((("bloom", bloom),) * bool(bloom))))


def _tree(code, title, brand, path, price, text, pot, attrs, leaves):
    """A potted tree (olive, eucalyptus): a form or a species, in three heights."""
    return Row(code, title, brand, "Garden", path, "Plant", price, "potted_tree", text, (pot,),
               attrs, _heights(price, ("60 cm", "90 cm", "1.2 m")),
               "Plant" if path is _EUCALYPTUS else "Tree",
               colorless=True, params=(("leaves", leaves),))


GARDEN = (
    Row("BAYSTD", "Standard Bay Tree in Terracotta Pot", "Thistle & Wren", "Garden", _TREES,
        "Plant", 25.0, "potted_tree",
        "A clipped bay tree, hardy outdoors and handy in the kitchen. Water weekly in summer.",
        (_POT,), _form("Standard"), _HEIGHTS, "Bay", colorless=True),
    Row("OLVSTD", "Olive Tree in Terracotta Pot", "Thistle & Wren", "Garden", _OLIVES, "Plant",
        32.0, "potted_tree",
        "A silver-leaved olive tree for a sunny patio, hardy in a sheltered spot. Water sparingly.",
        (_POT,), _form("Standard"), _HEIGHTS, "Olive", colorless=True),
    Row("BAYZNC", "Pyramid Bay Tree in Zinc Planter", "Fenwold Nursery", "Garden", _TREES,
        "Plant", 30.0, "potted_tree",
        "A bay tree clipped to shape, in a galvanized planter with drainage holes.",
        (cw("Zinc", "#9aa3a8", "solid", "#4f7a3a"),), _form("Pyramid"),
        (("60 cm", 30.0), ("90 cm", 48.0)), "Bay", colorless=True),
    Row("BAYPAT", "Bush Bay Tree for Patios", "Thistle & Wren", "Garden", _TREES, "Plant", 18.0,
        "potted_tree",
        "A young bay tree in a 2-liter nursery pot, ready to clip or plant out.",
        (cw("Black", "#2a2a2e", "solid", "#4f7a3a"),), _form("Bush"), label="Bay",
        colorless=True),
    Row("TULP10", "Purple Parrot Tulip Bulbs, Pack of 10", "Fenwold Nursery", "Garden", _TULIP,
        "Bulbs", 5.0, "tulip",
        "Top-size bulbs for planting in fall, 15 cm deep, for flowers in late spring.",
        (cw("Purple", "#4b2238", "solid", "#4f7a3a"),), _flower("Parrot"), colorless=True),
    Row("TULP25", "Apricot Lily-Flowered Tulip Bulbs, Pack of 25", "Thistle & Wren", "Garden",
        _TULIP, "Bulbs", 10.0, "tulip",
        "A bag of bulbs for a border or a row of pots. Plant in fall for flowers in May.",
        (cw("Apricot", "#f2a65a", "solid", "#4f7a3a"),), _flower("Lily-Flowered"),
        colorless=True),
    Row("TULTIN", "White Fringed Tulip Bulbs in a Gift Tin", "Fenwold Nursery", "Garden", _TULIP,
        "Bulbs", 12.0, "tulip",
        "Twelve bulbs in a printed tin with planting notes, a gift for any gardener.",
        (cw("White", "#f4efe2", "solid", "#4f7a3a"),), _flower("Fringed"), colorless=True),
    Row("TULPOT", "Pink Double Early Tulips in a Ceramic Pot", "Thistle & Wren", "Garden", _TULIP,
        "Bulbs", 16.0, "tulip",
        "Bulbs pre-planted in a glazed pot, shooting already: water and wait for buds.",
        (cw("Pink", "#e27d9f", "solid", "#4f7a3a"),), _flower("Double Early"), colorless=True),
    Row("TULP50", "Red Single Late Tulip Bulbs, Pack of 50", "Fenwold Nursery", "Garden", _TULIP,
        "Bulbs", 18.0, "tulip",
        "A sack of bulbs for a long border or a cutting bed. Plant in fall, 15 cm deep.",
        (cw("Red", "#c8312e", "solid", "#4f7a3a"),), _flower("Single Late"), colorless=True),
    Row("STRP06", "Elsanta Strawberry Plants, Pack of 6", "Fenwold Nursery", "Garden", _BERRY,
        "Plant", 9.0, "strawberry",
        "Young plants in 9 cm pots for beds, bags or hanging baskets, fruiting in their "
        "first summer.",
        (cw("Red", "#c8312e", "solid", "#4f7a3a"),), _var("Elsanta"), colorless=True),
    Row("STRP12", "Honeoye Strawberry Plants, Pack of 12", "Thistle & Wren", "Garden", _BERRY,
        "Plant", 15.0, "strawberry",
        "Bare-root runners to plant 30 cm apart in a sunny bed, cropping from June.",
        (cw("Red", "#b8322f", "solid", "#4f7a3a"),), _var("Honeoye"), colorless=True),
    Row("STRBSK", "Florence Strawberry Hanging Basket", "Fenwold Nursery", "Garden", _BERRY,
        "Plant", 20.0, "strawberry",
        "A 30 cm basket planted with five plants, with a chain to hang it by the door.",
        (cw("Red", "#c8102e", "solid", "#4f7a3a"),), _var("Florence"), colorless=True),
    Row("MUSKIT", "Pearl Oyster Mushroom Growing Kit", "Thistle & Wren", "Garden", _MUSH,
        "Growing Kit", 18.0, "mushroom",
        "A ready-seeded box: open the front, mist twice a day, and pick in about ten days.",
        (_MUSH_DRAWN,), _var("Pearl Oyster"), colorless=True),
    Row("MUSLOG", "Shiitake Mushroom Log", "Fenwold Nursery", "Garden", _MUSH, "Growing Kit",
        28.0, "mushroom",
        "A seeded hardwood log for a shady corner, cropping in spring and fall for years.",
        (_MUSH_DRAWN,), _var("Shiitake"), colorless=True),
    Row("MUSBAG", "Lion's Mane Mushroom Grow Bag", "Thistle & Wren", "Garden", _MUSH,
        "Growing Kit", 14.0, "mushroom",
        "A grow bag that crops on a kitchen counter, out of direct sun. Two flushes or more.",
        (_MUSH_DRAWN,), _var("Lion's Mane"), colorless=True),
    Row("XMSCUT", "Cut Nordmann Fir Christmas Tree", "Thistle & Wren", "Garden", _XMAS,
        "Christmas Tree", 45.0, "christmas_tree",
        "Freshly cut and netted, with a fresh-cut base that drinks water in the stand.",
        (cw("Green", "#2f6b3c"),), _var("Nordmann Fir"), _XMAS_FT, colorless=True,
        size_key="height"),
    Row("XMSPOT", "Pot-Grown Fraser Fir Christmas Tree", "Fenwold Nursery", "Garden", _XMAS,
        "Christmas Tree", 40.0, "christmas_tree",
        "Grown in its pot, roots and all: keep it watered indoors, then plant it out in "
        "January.",
        (cw("Green", "#3e7a4a"),), _var("Fraser Fir"), (("4 ft", 40.0), ("5 ft", 55.0)),
        colorless=True, size_key="height"),
    Row("XMSMIN", "Mini Norway Spruce Christmas Tree", "Thistle & Wren", "Garden", _XMAS,
        "Christmas Tree", 15.0, "christmas_tree",
        "A tabletop tree about 60 cm tall in a jute-wrapped pot, for a desk or windowsill.",
        (cw("Green", "#4f7a3a"),), _var("Norway Spruce"), colorless=True),
    Row("APLBSH", "Gala Apple Tree, Patio Bush", "Fenwold Nursery", "Garden", _APPLE, "Plant",
        30.0, "potted_tree",
        "A self-fertile tree on dwarfing roots that stays under 2 m in a large pot.",
        (cw("Green", "#4f7a3a", "solid", "#c8312e"),), _var("Gala"), label="Apple",
        colorless=True),
    Row("APLBAR", "Bramley Apple Tree, Bare Root", "Thistle & Wren", "Garden", _APPLE, "Plant",
        24.0, "potted_tree",
        "A two-year tree, lifted in winter and sent bare root, to plant from November "
        "to March.",
        (cw("Green", "#3e7a4a", "solid", "#c8312e"),), _var("Bramley"), label="Apple",
        colorless=True),
    Row("APLCRD", "Braeburn Apple Tree, Cordon", "Fenwold Nursery", "Garden", _APPLE, "Plant",
        28.0, "potted_tree",
        "A single trained stem for a fence or wall, cropping in a narrow space.",
        (cw("Green", "#2f6b3c", "solid", "#c8312e"),), _var("Braeburn"), label="Apple",
        colorless=True),
    # Round 2 (gen#125): at the ceiling, garden held 75 styles against a half share of 91.
    Row("BAYCON", "Cone Bay Tree for a Doorstep", "Fenwold Nursery", "Garden", _TREES, "Plant",
        35.0, "potted_tree",
        "A dense, clipped bay tree, a matching pair for either side of a door.",
        (cw("Slate", "#5a6470", "solid", "#4f7a3a"),), _form("Cone"),
        (("90 cm", 35.0), ("1.2 m", 58.0)), "Bay", colorless=True),
    Row("BAYSPI", "Spiral Bay Tree, Statement Topiary", "Thistle & Wren", "Garden", _TREES,
        "Plant", 70.0, "potted_tree",
        "A bay tree trained to a neat shape. Trim twice a summer to keep its outline.",
        (_POT,), _form("Spiral"), label="Bay", colorless=True),
    Row("STRP09", "Cambridge Favourite Strawberry Plants, Pack of 9", "Thistle & Wren", "Garden",
        _BERRY, "Plant", 12.0, "strawberry",
        "Plug plants for a raised bed or a grow bag, heavy cropping in midsummer.",
        (cw("Red", "#c4302c", "solid", "#4f7a3a"),), _var("Cambridge Favourite"),
        colorless=True),
    Row("STRTWR", "Malling Centenary Strawberry Tower Planter", "Fenwold Nursery", "Garden",
        _BERRY, "Plant", 26.0, "strawberry",
        "A three-tier planter set with nine young plants, for a small patio or balcony.",
        (cw("Red", "#c22a2a", "solid", "#4f7a3a"),), _var("Malling Centenary"),
        colorless=True),
    Row("MUSKNG", "King Oyster Mushroom Starter Box", "Fenwold Nursery", "Garden", _MUSH,
        "Growing Kit", 20.0, "mushroom",
        "A boxed block for a cool room: cut a cross in the bag, keep it humid, and wait.",
        (_MUSH_DRAWN,), _var("King Oyster"), colorless=True),
    Row("MUSDWL", "Chestnut Mushroom Dowels for Logs", "Thistle & Wren", "Garden", _MUSH,
        "Growing Kit", 12.0, "mushroom",
        "Fifty spawn dowels to tap into fresh-cut logs, cropping from the second year.",
        (_MUSH_DRAWN,), _var("Chestnut"), colorless=True),
    Row("XMSNBL", "Noble Fir Christmas Tree, Delivered", "Fenwold Nursery", "Garden", _XMAS,
        "Christmas Tree", 60.0, "christmas_tree",
        "Cut to order and delivered on a chosen day in December, with a stand fitted.",
        (cw("Green", "#2c5e3a"),), _var("Noble Fir"), (("6 ft", 60.0), ("7 ft", 78.0)),
        colorless=True, size_key="height"),
    Row("XMSBLU", "Potted Blue Spruce Tabletop Tree", "Thistle & Wren", "Garden", _XMAS,
        "Christmas Tree", 22.0, "christmas_tree",
        "A small living tree in a 3-liter pot, for a table or a porch through the season.",
        (cw("Green", "#5d7f78"),), _var("Blue Spruce"), colorless=True),
    Row("APLMIN", "Cox Apple Tree, Minarette", "Thistle & Wren", "Garden", _APPLE, "Plant",
        32.0, "potted_tree",
        "A columnar tree for a large pot or a narrow border, fruiting on short spurs.",
        (cw("Green", "#4a7d3a", "solid", "#c8312e"),), _var("Cox"), label="Apple",
        colorless=True),
    Row("APLFAN", "Egremont Russet Apple Tree, Fan Trained", "Fenwold Nursery", "Garden",
        _APPLE, "Plant", 45.0, "potted_tree",
        "A tree with its branches spread flat on canes, ready to tie against a sunny wall.",
        (cw("Green", "#3a6b30", "solid", "#c8312e"),), _var("Egremont Russet"), label="Apple",
        colorless=True),
    # Round 4 (gen#125): at the 75K ceiling, garden held 155 styles against a half share of 154.
    Row("TULP20", "Yellow Triumph Tulip Bulbs, Pack of 20", "Thistle & Wren", "Garden", _TULIP,
        "Bulbs", 8.0, "tulip",
        "Sturdy bulbs for pots and borders, flowering in mid spring. Plant in fall, 15 cm deep.",
        (cw("Yellow", "#f2c641", "solid", "#4f7a3a"),), _flower("Triumph"), colorless=True),
    Row("STRP08", "Symphony Strawberry Plants, Pack of 8", "Fenwold Nursery", "Garden", _BERRY,
        "Plant", 11.0, "strawberry",
        "Young plants in 9 cm pots for a bed or a container, cropping from midsummer.",
        (cw("Red", "#c32b2b", "solid", "#4f7a3a"),), _var("Symphony"), colorless=True),
    Row("APLHLF", "Discovery Apple Tree, Half Standard", "Thistle & Wren", "Garden", _APPLE,
        "Plant", 38.0, "potted_tree",
        "A tree with a clear stem of about 1.2 m, for a lawn or a large border.",
        (cw("Green", "#457a35", "solid", "#c8312e"),), _var("Discovery"), label="Apple",
        colorless=True),
    # gen#198: with the Food & Drink and air freshener rows, these keep Garden and Cleaning
    # over half their fair share of styles once the tableware rows grew Home
    # (tests/test_retail_scale.py).
    Row("APLJAZ", "Jazz Apple Tree, Patio Bush", "Fenwold Nursery", "Garden", _APPLE, "Plant",
        30.0, "potted_tree", "A compact tree on a dwarfing root for a large pot on a sunny patio.",
        (cw("Green", "#457a35", "solid", "#c8312e"),), _var("Jazz"), label="Apple",
        colorless=True),
    Row("APLFIE", "Fiesta Apple Tree, Bare Root", "Thistle & Wren", "Garden", _APPLE, "Plant",
        24.0, "potted_tree", "Lifted in winter and sent bare root, to plant before spring.",
        (cw("Green", "#457a35", "solid", "#c8312e"),), _var("Fiesta"), label="Apple",
        colorless=True),
    # gen#509 plants. Lavender: a flowering shrub, four varieties.
    _herb("LAVENG", "English Lavender Plant in Terracotta Pot", _TW, _LAVENDER, 9.0,
          "A hardy, scented lavender for a sunny border or a pot, flowering from midsummer. "
          "Water sparingly.", _PTERRA, "English", "#9aab8f", _BLOOM),
    _herb("LAVHID", "Hidcote Lavender Plant for Low Hedges", _FN, _LAVENDER, 8.0,
          "A compact lavender with dense flower spikes, clipped after flowering to keep a tidy "
          "low hedge.", _PSTONE, "Hidcote", "#9aab8f", _BLOOM),
    _herb("LAVFRN", "French Lavender Plant with Tufted Flowers", _TW, _LAVENDER, 10.0,
          "A tender lavender with tufted flower heads that flowers from spring, best on a warm "
          "patio.", _PZINC, "French", "#8fa384", "#7a52a3"),
    _herb("LAVMUN", "Munstead Dwarf Lavender Plant", _FN, _LAVENDER, 7.5,
          "A small, early lavender for the front of a border, a path edge or a window box.",
          _PTERRA, "Munstead", "#9aab8f", _BLOOM),
    # Sage, rosemary and thyme: the kitchen herbs, under Herbs.
    _herb("SAGCMN", "Common Sage Plant in Terracotta Pot", _TW, _SAGE, 4.0,
          "A kitchen sage with soft downy leaves for stuffing and roasts. Pick little and often.",
          _PTERRA, "Common", _SAGE_LEAF),
    _herb("SAGBRG", "Berggarten Sage Plant with Broad Leaves", _FN, _SAGE, 4.5,
          "A sage with large, rounded leaves that rarely flowers, so it keeps its leaves for "
          "the kitchen.", _PZINC, "Berggarten", _SAGE_LEAF),
    _herb("SAGVAR", "Variegated Sage Plant for Containers", _TW, _SAGE, 5.0,
          "A sage with marked leaves, as good in a mixed pot by the back door as in the herb "
          "bed.", _PSTONE, "Variegated", "#a3b59a"),
    _herb("SAGNAR", "Narrow-Leaved Sage Plant, Hardy Perennial", _FN, _SAGE, 4.0,
          "A narrow-leaved sage that comes back every year and takes a dry spot in full sun.",
          _PTERRA, "Narrow-Leaved", _SAGE_LEAF),
    _herb("ROSUPR", "Upright Rosemary Plant in Terracotta Pot", _TW, _ROSEMARY, 5.0,
          "An upright rosemary with needle leaves for lamb, potatoes and a barbecue. Needs sun "
          "and good drainage.", _PTERRA, "Upright", _ROSE_LEAF),
    _herb("ROSPRO", "Prostrate Rosemary Plant for Walls and Banks", _FN, _ROSEMARY, 5.5,
          "A trailing rosemary that spills over a wall or a raised bed and flowers early.",
          _PSTONE, "Prostrate", _ROSE_LEAF),
    _herb("ROSJES", "Miss Jessopp Rosemary Plant for Hedging", _TW, _ROSEMARY, 6.0,
          "A tall, straight rosemary that clips into a scented hedge along a sunny path.",
          _PZINC, "Miss Jessopp", "#6a8a64"),
    _herb("ROSBEN", "Benenden Rosemary Plant, Fine Leaves", _FN, _ROSEMARY, 5.5,
          "A fine-leaved rosemary with a neat habit and plenty of flowers for bees.",
          _PTERRA, "Benenden", "#6a8a64"),
    _herb("THYCRP", "Creeping Thyme Plant for Paths and Paving", _TW, _THYME, 3.5,
          "A mat-forming thyme that scents the air when trodden, for gaps in paving and "
          "rockeries.", _PSTONE, "Creeping", _THYME_LEAF, "#d98fb0"),
    _herb("THYCMN", "Common Thyme Plant in Terracotta Pot", _FN, _THYME, 3.5,
          "A kitchen thyme with tiny leaves for stews, stocks and roast vegetables. Keep it on "
          "the dry side.", _PTERRA, "Common", _THYME_LEAF),
    _herb("THYDVY", "Doone Valley Thyme Plant, Mat-Forming", _TW, _THYME, 4.0,
          "A low thyme that scents the air when brushed, for a pot by the kitchen door.",
          _PZINC, "Doone Valley", "#8aa862"),
    _herb("THYWLY", "Woolly Thyme Plant for Rock Gardens", _FN, _THYME, 4.0,
          "A soft, hairy-leaved thyme that makes a low carpet in a gravel bed or a sink garden.",
          _PSTONE, "Woolly", "#a3b59a"),
    # Olive trees (the first, OLVSTD, is above) and eucalyptus: small trees in pots.
    _tree("OLVBSH", "Bush Olive Tree in Zinc Planter", _FN, _OLIVES, 28.0,
          "A bushy olive tree with a rounded crown for a sunny patio, hardy in a sheltered "
          "spot.", _PZINC, _form("Bush"), "#9aa88c"),
    _tree("OLVMLT", "Multi-Stem Olive Tree for a Patio", _TW, _OLIVES, 45.0,
          "An olive tree grown with several stems for a more natural shape. Water sparingly "
          "and feed in spring.", _PTERRA, _form("Multi-Stem"), "#9aa88c"),
    _tree("OLVHST", "Half-Standard Olive Tree in Stone Pot", _FN, _OLIVES, 40.0,
          "A half-standard olive tree with a clear trunk and a clipped head, for a doorstep "
          "pair.", _PSTONE, _form("Half-Standard"), "#a3b093"),
    _tree("OLVPLT", "Pleached Olive Tree, Flat Screen", _TW, _OLIVES, 60.0,
          "A flat-trained olive tree for a screen against a sunny wall or a fence, with a "
          "clear stem below.", _PBLACK, _form("Pleached"), "#9aa88c"),
    _tree("EUCGUN", "Eucalyptus Gunnii Plant, Cider Gum", _TW, _EUCALYPTUS, 14.0,
          "A fast-growing eucalyptus with round juvenile leaves that cut well for a vase. "
          "Hardy once established.", _PTERRA, _var("Gunnii"), "#8fb0aa"),
    _tree("EUCPAU", "Eucalyptus Pauciflora Snow Gum Plant", _FN, _EUCALYPTUS, 16.0,
          "A slow-growing eucalyptus with a mottled trunk, one of the hardiest in the garden.",
          _PSTONE, _var("Pauciflora"), "#86a89f"),
    _tree("EUCPAR", "Eucalyptus Parvula Plant, Small-Leaved Gum", _TW, _EUCALYPTUS, 15.0,
          "A slender eucalyptus with a graceful habit for a large pot, scented when "
          "crushed.", _PZINC, _var("Parvula"), "#8fb0aa"),
    _tree("EUCNIC", "Eucalyptus Nicholii Plant, Willow-Leaved", _FN, _EUCALYPTUS, 17.0,
          "A willow-leaved eucalyptus with a weeping habit and a fragrant crown.",
          _PTERRA, _var("Nicholii"), "#86a89f"),
)  # fmt: skip
