"""Breadth templates for the scaled retail catalog (gen#125): data only.

:func:`scale.templates` builds these after :mod:`scale_rows`. The authored styles and
the deep-SKU rows left a general-retail catalog thin outside clothing and lingerie: at
the ceiling, toys, garden, gifts and cleaning held under 1% of the styles each, and
food and beauty under 5%. These rows give each thin department leaves of its own, so
that no department falls under half its fair share of the ceiling's styles
(``tests/test_retail_scale.py`` pins it).

A row adds capacity through a title-visible value its leaf varies (:func:`scale.value_pools`):
a fabric, a fragrance, a variety, an occasion. Every value of a leaf's pool fits every
template of that leaf, so a derived style stays coherent: a knitted whale and a corduroy
cat are both soft toys, and a variety is a variety of the leaf's one plant. The drawing
shows what never varies (the animal, the bottle, the tree).
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass

from departments import check as check_departments
from variants import Color, attr, cw, drawing, product, swatch

#: Who makes each brand these rows carry: the retailer ("own") or another house.
OWNERS = {
    "Little Fernby": "own", "Puddlecombe Toys": "third_party",
    "Thistle & Wren": "third_party", "Fenwold Nursery": "third_party",
    "Lanternby": "third_party", "Calderby & Lune": "third_party",
    "Pantry Mill": "own", "Freshfold": "third_party",
    "Hearth & Table": "own", "Kettleby Tea Co.": "third_party",
    "Brewhollow Roasters": "third_party", "Mirefield Naturals": "third_party",
    "Hollin Hair": "third_party",
}  # fmt: skip


@dataclass(frozen=True)
class Row:
    """One style: its colors times its sizes are its SKUs (one SKU each when it has none).

    A ``colorless`` row's SKUs carry no color (a plant, a cleaner); its drawing still
    takes ``colors[0]``. A size is ``(name, price)``: a bigger size costs more.
    """

    code: str
    title: str
    brand: str
    department: str
    path: tuple[str, ...]
    product_type: str
    price: float
    shape: str
    description: str
    colors: tuple[Color, ...]
    attrs: tuple[tuple[str, str, str], ...] = ()
    sizes: tuple[tuple[str, float], ...] = ()
    label: str | None = None
    audience: str = "adult"
    colorless: bool = False
    params: tuple[tuple[str, str], ...] = ()

    def skus(self) -> list[dict]:
        sizes = [{"size": s, "price": p} for s, p in self.sizes] or [{"price": self.price}]
        colors = self.colors[:1] if self.colorless else self.colors
        return [
            {**({} if self.colorless else {"color": c[0]}), **s, "in_stock": True}
            for c in colors
            for s in sizes
        ]

    def doc(self) -> dict:
        check_departments([self.department], self.code)
        h = zlib.crc32(self.code.encode())
        skus = self.skus()
        swatches = {c[0]: swatch(c) for c in self.colors}
        return product(
            f"BRD-{self.code}", skus, swatches,
            title=self.title, brand=self.brand, brand_owner=OWNERS[self.brand],
            department=[self.department], product_type=self.product_type,
            category_path=list(self.path), category_leaf=self.path[-1],
            description=self.description,
            attributes=[attr(k, n, v) for k, n, v in self.attrs],
            drawing=drawing(self.shape, self.colors[0], self.label, **dict(self.params)),
            collections=[], currency="GBP", audience=self.audience,
            sold_last_5_days=5 + h % 90, rating=round(3.8 + (h >> 8) % 11 / 10, 1),
            review_count=3 + (h >> 16) % 400,
            price_min=min(s["price"] for s in skus), price_max=max(s["price"] for s in skus),
        )  # fmt: skip


def _fab(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("fabric", "Fabric", v),)


def _mat(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("material", "Material", v),)


# --------------------------------------------------------------------------
# Toys: the animal or vehicle is drawn; the fabric, material or power varies.
# --------------------------------------------------------------------------

_SOFT = ("Toys", "Soft Toys", "Cuddly Animals")
_BATH = ("Toys", "Baby & Toddler", "Bath Toys")
_CARS = ("Toys", "Vehicles", "Toy Vehicles")
_FIG = ("Toys", "Figures & Playsets", "Animal Figures")
_LIGHT = ("Toys", "Nursery", "Night Lights")
_KIDS = "kids"

TOYS = (
    Row("SFTCAT", "Plush Cat Soft Toy", "Little Fernby", "Toys", _SOFT, "Soft Toy", 14.0, "cat",
        "A floppy plush cat with stitched eyes and a long tail, soft enough for bedtime. "
        "Surface washable.",
        (cw("Ginger", "#d9822b"), cw("Grey", "#9a9a9a"), cw("Black", "#2a2a2e")),
        _fab("Plush"), audience=_KIDS),
    Row("SFTOWL", "Knitted Owl Soft Toy", "Puddlecombe Toys", "Toys", _SOFT, "Soft Toy", 16.0,
        "bird",
        "A round knitted owl with felt wings and embroidered eyes, small enough for a cot. "
        "Hand wash.",
        (cw("Oat", "#d8c9a8"), cw("Sage", "#9bb08f")), _fab("Knitted"), audience=_KIDS),
    Row("SFTWHL", "Corduroy Whale Soft Toy", "Little Fernby", "Toys", _SOFT, "Soft Toy", 18.0,
        "whale",
        "A long whale with a squashy body and a stitched smile, filled with recycled fiber. "
        "Machine washable at 30 degrees.",
        (cw("Navy", "#26365c"), cw("Sky Blue", "#8fb8de")), _fab("Corduroy"), audience=_KIDS),
    Row("SFTDIN", "Faux Fur Dinosaur Soft Toy", "Puddlecombe Toys", "Toys", _SOFT, "Soft Toy",
        20.0, "dinosaur",
        "A big-footed dinosaur with soft spines down its back, made for hugging. "
        "Surface washable.",
        (cw("Moss Green", "#6f8f4a"), cw("Lilac", "#b9a3d0")), _fab("Faux Fur"), audience=_KIDS),
    Row("SFTBIR", "Organic Cotton Bird Soft Toy", "Little Fernby", "Toys", _SOFT, "Soft Toy",
        12.0, "bird",
        "A small bird with a crinkly tummy and a ribbon loop, safe from birth. "
        "Machine washable at 30 degrees.",
        (cw("Mustard", "#d1a03c"), cw("Coral", "#ef7b62")), _fab("Organic Cotton"),
        audience=_KIDS),
    Row("BTHWHL", "Silicone Whale Bath Squirter", "Little Fernby", "Toys", _BATH, "Bath Toy",
        7.0, "whale",
        "A whale that fills and squirts from its blowhole. It opens in two for cleaning, "
        "so no water sits inside.",
        (cw("Teal", "#1c7c7d"), cw("Yellow", "#f2d14b")), _mat("Silicone"), audience=_KIDS),
    Row("BTHDCK", "Natural Rubber Bath Duck", "Puddlecombe Toys", "Toys", _BATH, "Bath Toy",
        6.0, "bird",
        "A sealed bath duck that floats upright and never fills with water. "
        "For babies from 3 months.",
        (cw("Yellow", "#f2d14b"), cw("Pink", "#f2a1b8")), _mat("Natural Rubber"), audience=_KIDS),
    Row("BTHBOT", "Recycled Plastic Whale Bath Set", "Little Fernby", "Toys", _BATH, "Bath Toy",
        12.0, "whale",
        "A floating whale with three stacking cups that pour, sieve and sprinkle. "
        "Dishwasher safe.",
        (cw("Blue", "#3f6fb5"),), _mat("Recycled Plastic"), audience=_KIDS),
    Row("CARRCE", "Wooden Racing Car", "Little Fernby", "Toys", _CARS, "Toy Vehicle", 9.0, "car",
        "A chunky racing car with rubber tires and a driver who lifts out. For ages 18 months "
        "and up.",
        (cw("Red", "#c8312e"), cw("Blue", "#3f6fb5")), _mat("Wooden"), audience=_KIDS),
    Row("CARPOL", "Die-Cast Police Car", "Puddlecombe Toys", "Toys", _CARS, "Toy Vehicle", 6.0,
        "car",
        "A pocket-size police car with opening doors and a pull-back motor. For ages 3 and up.",
        (cw("White", "#ffffff", "solid", "#26365c"),), _mat("Die-Cast"), audience=_KIDS),
    Row("CARVIN", "Recycled Plastic Vintage Car", "Little Fernby", "Toys", _CARS, "Toy Vehicle",
        11.0, "car",
        "A rounded vintage car with a seat for a small figure and wheels that never come off.",
        (cw("Mint", "#a8d8c2"), cw("Cream", "#efe8d8")), _mat("Recycled Plastic"),
        audience=_KIDS),
    Row("CARTOW", "Wooden Tow Truck", "Puddlecombe Toys", "Toys", _CARS, "Toy Vehicle", 15.0, "car",
        "A tow truck with a working hook and winch that lifts a second car. "
        "For ages 2 and up.",
        (cw("Yellow", "#f2d14b"),), _mat("Wooden"), label="Tow", audience=_KIDS),
    Row("FIGCAT", "Resin Cat Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure", 5.0,
        "cat",
        "A sitting cat figure sized for small hands, finished in water-based paint.",
        (cw("Tabby", "#b07a43"),), _mat("Resin"), audience=_KIDS),
    Row("FIGWHL", "Wooden Whale Figure", "Little Fernby", "Toys", _FIG, "Toy Figure", 6.0,
        "whale", "A smooth whale figure with a rounded tail, for play in the bath or on the rug.",
        (cw("Navy", "#26365c"),), _mat("Wooden"), audience=_KIDS),
    Row("FIGBRD", "Rubber Bird Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure", 4.0,
        "bird", "A robin figure with a flat base so it stands up, soft enough to chew.",
        (cw("Red", "#c8312e", "solid", "#7a4a2a"),), _mat("Rubber"), audience=_KIDS),
    Row("LGTSTR", "Rechargeable Star Night Light", "Little Fernby", "Toys", _LIGHT, "Night Light",
        22.0, "star",
        "A soft-glow star that dims over 30 minutes, then stays on low all night.",
        (cw("Warm White", "#fbefc9"), cw("Pink", "#f2a1b8")), (("power", "Power", "Rechargeable"),),
        audience=_KIDS),
    Row("LGTWHL", "Plug-In Whale Night Light", "Puddlecombe Toys", "Toys", _LIGHT, "Night Light",
        18.0, "whale",
        "A silicone whale that glows when tapped and changes color with a second tap.",
        (cw("Blue", "#8fb8de"),), (("power", "Power", "Plug-In"),), audience=_KIDS),
    Row("LGTCAT", "Battery-Powered Cat Night Light", "Little Fernby", "Toys", _LIGHT,
        "Night Light", 15.0, "cat",
        "A sleeping cat lamp with a timer that switches it off after one hour.",
        (cw("White", "#ffffff"),), (("power", "Power", "Battery-Powered"),), audience=_KIDS),
    # Round 2 (gen#125): at 20K, toys held 23 styles against a half share of 30.
    # Each leaf takes one new value at most and the rest reuse its pool: a value its leaf
    # lacks multiplies the siblings that share a picture, and they then share a grid tile
    # (scale.grid_clones). Extra colors add styles that do not.
    Row("SFTFLC", "Plush Owl Sleep Buddy", "Puddlecombe Toys", "Toys", _SOFT, "Soft Toy", 15.0,
        "bird",
        "A flat owl with long wings to hold at night and a loop for a buggy. Machine washable.",
        (cw("Heather", "#b4a7c4"), cw("Oat", "#d8c9a8"), cw("Duck Egg", "#b7d3cf")),
        _fab("Plush"), audience=_KIDS),
    Row("SFTVLV", "Corduroy Dinosaur Cuddle Toy, Large", "Little Fernby", "Toys", _SOFT,
        "Soft Toy", 26.0, "dinosaur",
        "A long-necked dinosaur nearly 50 cm tall, weighted at the feet so it sits up.",
        (cw("Teal", "#1c7c7d"), cw("Rose", "#d98c9f"), cw("Mustard", "#d1a03c")),
        _fab("Corduroy"), audience=_KIDS),
    Row("BTHFOM", "Foam Cat Bath Floaters, Set of 3", "Puddlecombe Toys", "Toys", _BATH,
        "Bath Toy", 4.0, "cat",
        "Three cats that float and stick to the side of the bath when wet. Air dry after use.",
        (cw("Orange", "#e98a3a"), cw("Lilac", "#b9a3d0"), cw("Mint", "#a8d8c2")), _mat("Foam"),
        audience=_KIDS),
    Row("BTHVNL", "Natural Rubber Dinosaur Bath Squirter", "Little Fernby", "Toys", _BATH,
        "Bath Toy", 4.5, "dinosaur",
        "A squeezy dinosaur that squirts from its mouth, sized for a toddler's hand.",
        (cw("Green", "#6f8f4a"), cw("Purple", "#7d5ba6"), cw("Orange", "#e98a3a")),
        _mat("Natural Rubber"), audience=_KIDS),
    Row("BTHBMB", "Recycled Plastic Bird Pouring Cups", "Puddlecombe Toys", "Toys", _BATH,
        "Bath Toy", 10.0, "bird",
        "Four nesting cups with a bird on each, for pouring and stacking in the bath.",
        (cw("Sky Blue", "#8fb8de"), cw("Coral", "#ef7b62")), _mat("Recycled Plastic"),
        audience=_KIDS),
    Row("CARBMB", "Bamboo Fire Engine with Ladder", "Little Fernby", "Toys", _CARS,
        "Toy Vehicle", 18.0, "car",
        "A fire engine with a ladder that turns and extends. For ages 2 and up.",
        (cw("Red", "#c8312e"), cw("Yellow", "#f2d14b")), _mat("Bamboo"), label="Fire",
        audience=_KIDS),
    Row("CARTIN", "Die-Cast London Taxi", "Little Fernby", "Toys", _CARS, "Toy Vehicle", 4.5,
        "car", "A pocket-size taxi with a light on its roof and a pull-back motor. For ages 3 "
        "and up.",
        (cw("Black", "#2a2a2e"), cw("Yellow", "#f2d14b"), cw("Silver", "#c0c0c0")),
        _mat("Die-Cast"), label="Taxi", audience=_KIDS),
    Row("FIGFLT", "Felt Stegosaurus Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure", 7.0,
        "dinosaur", "A dinosaur figure with a long tail and a flat base, sized for small hands.",
        (cw("Moss Green", "#6f8f4a"), cw("Ochre", "#c8902e")), _mat("Felt"), audience=_KIDS),
    Row("FIGRCY", "Rubber Whale Bath Figure", "Little Fernby", "Toys", _FIG, "Toy Figure", 3.5,
        "whale", "A whale figure with no small parts, for play on the rug or in the bath.",
        (cw("Aqua", "#8fd1d0"), cw("Navy", "#26365c")), _mat("Rubber"), audience=_KIDS),
    Row("FIGPOR", "Wooden Cat Ornament Figure", "Puddlecombe Toys", "Toys", _FIG, "Toy Figure",
        4.0, "cat", "A small figure for a shelf or a dolls' house, for ages 3 and up.",
        (cw("Calico", "#c8a27a"), cw("Grey", "#9a9a9a")), _mat("Wooden"), audience=_KIDS),
    Row("LGTUSB", "USB-Powered Dinosaur Night Light", "Puddlecombe Toys", "Toys", _LIGHT,
        "Night Light", 16.0, "dinosaur",
        "A dinosaur lamp with a touch base that cycles through three brightness levels.",
        (cw("Green", "#6f8f4a"), cw("Sky Blue", "#8fb8de")), (("power", "Power", "USB-Powered"),),
        audience=_KIDS),
    Row("LGTSOL", "Rechargeable Star Lantern", "Little Fernby", "Toys", _LIGHT,
        "Night Light", 12.0, "star",
        "A star lantern for a bedroom shelf, with a soft glow that lasts all night.",
        (cw("Warm White", "#fbefc9"), cw("Lilac", "#b9a3d0")),
        (("power", "Power", "Rechargeable"),), audience=_KIDS),
    Row("LGTWND", "Battery-Powered Bird Night Light", "Puddlecombe Toys", "Toys", _LIGHT,
        "Night Light", 14.0, "bird",
        "A bird lamp with a soft glow and a sleep timer that switches off after 20 minutes.",
        (cw("Mint", "#a8d8c2"), cw("Peach", "#f4b893")),
        (("power", "Power", "Battery-Powered"),), audience=_KIDS),
)  # fmt: skip

# --------------------------------------------------------------------------
# Garden: one plant per leaf, so its every variety fits every template.
# --------------------------------------------------------------------------

_TREES = ("Garden", "Plants", "Bay Trees")
_TULIP = ("Garden", "Bulbs", "Tulip Bulbs")
_BERRY = ("Garden", "Grow Your Own", "Strawberry Plants")
_MUSH = ("Garden", "Grow Your Own", "Mushroom Kits")
_XMAS = ("Garden", "Christmas Trees", "Real Christmas Trees")
_APPLE = ("Garden", "Fruit Trees", "Apple Trees")
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

GARDEN = (
    Row("BAYSTD", "Standard Bay Tree in Terracotta Pot", "Thistle & Wren", "Garden", _TREES,
        "Plant", 25.0, "potted_tree",
        "A clipped bay tree, hardy outdoors and handy in the kitchen. Water weekly in summer.",
        (_POT,), _form("Standard"), _HEIGHTS, "Bay", colorless=True),
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
        (cw("Green", "#2f6b3c"),), _var("Nordmann Fir"), _XMAS_FT, colorless=True),
    Row("XMSPOT", "Pot-Grown Fraser Fir Christmas Tree", "Fenwold Nursery", "Garden", _XMAS,
        "Christmas Tree", 40.0, "christmas_tree",
        "Grown in its pot, roots and all: keep it watered indoors, then plant it out in "
        "January.",
        (cw("Green", "#3e7a4a"),), _var("Fraser Fir"), (("4 ft", 40.0), ("5 ft", 55.0)),
        colorless=True),
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
        colorless=True),
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
)  # fmt: skip

# --------------------------------------------------------------------------
# Gifts: the frame, the paper, the charm or the decoration is drawn.
# --------------------------------------------------------------------------

_FRAMES = ("Gifts", "Keepsakes", "Photo Frames")
_WRAP = ("Gifts", "Gift Wrap", "Wrapping Paper")
_CHARM = ("Gifts", "Keepsakes", "Charm Keyrings")
_DECOR = ("Gifts", "Christmas Gifts", "Tree Decorations")
_CANDLE = ("Gifts", "Home Fragrance", "Scented Candles")


def _occ(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("occasion", "Occasion", v),)


def _charm(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("charm", "Charm", v),)


def _scent(v: str) -> tuple[tuple[str, str, str], ...]:
    return (("fragrance", "Fragrance", v),)


_SILVER, _OAK = cw("Silver", "#c0c0c0"), cw("Oak", "#b08a5a")

GIFTS = (
    Row("FRMSLV", "Silver-Plated Wedding Photo Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 22.0, "photo_frame",
        "An engraved frame for a 5 x 7 in photo, with a velvet back and a fold-out stand.",
        (_SILVER,), _occ("Wedding"), (("5 x 7 in", 22.0), ("8 x 10 in", 32.0))),
    Row("FRMOAK", "Solid Oak New Baby Photo Frame", "Lanternby", "Gifts", _FRAMES,
        "Photo Frame", 18.0, "photo_frame",
        "A deep oak frame with a cream mount and a printed message, gift boxed.",
        (_OAK, cw("White", "#ffffff")), _occ("New Baby")),
    Row("FRMGLS", "Glass Anniversary Photo Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 15.0, "photo_frame",
        "Two glass panes that hold a 6 x 4 in photo between them, with a chrome stand.",
        (cw("Clear", "#e8f0f2"),), _occ("Anniversary")),
    Row("FRMMLT", "Graduation Multi-Photo Frame", "Lanternby", "Gifts", _FRAMES, "Photo Frame",
        28.0, "photo_frame",
        "A wall frame with five apertures, for a run of photos from one big day.",
        (cw("Black", "#2a2a2e"), _OAK), _occ("Graduation")),
    Row("WRPRLL", "Birthday Wrapping Paper Roll, 4 m", "Lanternby", "Gifts", _WRAP,
        "Wrapping Paper", 4.0, "wrapping_paper",
        "A roll of thick printed paper with a grid on the back for straight cuts.",
        (cw("Confetti", "#ffffff", "polka", "#d6267a"),
         cw("Pastel Spot", "#8fb8de", "polka", "#f2d14b")),
        _occ("Birthday")),
    Row("WRPSHT", "Christmas Wrapping Paper, 3 Sheets", "Calderby & Lune", "Gifts", _WRAP,
        "Wrapping Paper", 5.0, "wrapping_paper",
        "Three folded sheets with matching tags, printed on recycled paper.",
        (cw("Red Stripe", "#ffffff", "stripe", "#c8312e"),
         cw("Gold Star", "#1f2e4a", "polka", "#d4af37")),
        _occ("Christmas")),
    Row("WRPKRF", "Baby Shower Kraft Wrap and Ribbon Set", "Lanternby", "Gifts", _WRAP,
        "Wrapping Paper", 7.0, "wrapping_paper",
        "Two sheets of kraft paper, a printed sheet and 3 m of cotton ribbon.",
        (cw("Kraft", "#c9a77a", "stripe", "#ffffff"),), _occ("Baby Shower")),
    Row("CHMENM", "Enamel Fox Charm Keyring", "Lanternby", "Gifts", _CHARM, "Keyring", 8.0,
        "keyring", "A hard enamel charm on a split ring with a short chain, on a gift card.",
        (cw("Rust", "#a8502e"),), _charm("Fox")),
    Row("CHMPWT", "Pewter Hare Charm Keyring", "Calderby & Lune", "Gifts", _CHARM, "Keyring",
        12.0, "keyring", "A cast pewter charm on a leather tab, boxed with a care card.",
        (cw("Pewter", "#8a8d8f"),), _charm("Hare")),
    Row("CHMWOD", "Wooden Owl Charm Keyring", "Lanternby", "Gifts", _CHARM, "Keyring", 6.0,
        "keyring", "A laser-cut wooden charm, oiled and threaded on a cotton cord.",
        (cw("Natural", "#d8c9a8"),), _charm("Owl")),
    Row("CHMSLV", "Sterling Silver Bee Charm Keyring", "Calderby & Lune", "Gifts", _CHARM,
        "Keyring", 35.0, "keyring",
        "A hallmarked silver charm on a polished ring, in a lined gift box.",
        (_SILVER,), _charm("Bee")),
    Row("DECSTR", "Glitter Glass Star Decoration", "Lanternby", "Gifts", _DECOR,
        "Christmas Decoration", 6.0, "star",
        "A mouth-blown glass star with a ribbon loop, about 10 cm across.",
        (cw("Gold", "#d4af37"), cw("Silver", "#c0c0c0")), (("finish", "Finish", "Glitter"),)),
    Row("DECWST", "Painted Wooden Star Decoration Set", "Calderby & Lune", "Gifts", _DECOR,
        "Christmas Decoration", 9.0, "star",
        "Six flat wooden stars on jute loops, for a tree, a garland or a gift.",
        (cw("Red", "#c8312e"), cw("White", "#ffffff")), (("finish", "Finish", "Painted"),)),
    Row("DECSNO", "Glitter Glass Snowflake Decoration", "Lanternby", "Gifts", _DECOR,
        "Christmas Decoration", 7.0, "snowflake",
        "A flat glass snowflake that catches the tree lights, on a fine hanging thread.",
        (cw("Ice", "#dbe9f2"),), (("finish", "Finish", "Glitter"),)),
    Row("DECFLT", "Gilded Felt Snowflake Decoration", "Calderby & Lune", "Gifts", _DECOR,
        "Christmas Decoration", 5.0, "snowflake",
        "A hand-cut felt snowflake with stitched edges, light enough for any branch.",
        (cw("Cream", "#efe8d8"), cw("Red", "#c8312e")), (("finish", "Finish", "Gilded"),)),
    Row("CNDJAR", "Fig and Cedar Scented Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 18.0, "jar",
        "A soy wax candle in a reusable glass jar, about 40 hours of burn time.",
        (cw("Smoke", "#6f6a66"),), _scent("Fig and Cedar"), (("Medium", 18.0), ("Large", 28.0)),
        "Candle"),
    Row("CNDTIN", "Sea Salt Travel Tin Candle", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 8.0, "tin",
        "A small candle in a lidded tin, about 15 hours of burn time, for a bag or a desk.",
        (cw("Sand", "#d9c7a3"),), _scent("Sea Salt"), label="Candle"),
    Row("CNDTRW", "Amber Woods Three-Wick Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 32.0, "jar",
        "A wide candle with three cotton wicks that fills a room, about 50 hours of burn time.",
        (cw("Amber", "#c98a2e"),), _scent("Amber Woods"), label="Candle"),
    Row("CNDLIN", "Fresh Linen Candle Gift Set", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 24.0, "jar",
        "Three votive candles in frosted glass, boxed with a ribbon for giving.",
        (cw("White", "#ffffff"),), _scent("Fresh Linen"), label="Candle"),
    # Round 2 (gen#125): at 20K, gifts held 28 styles against a half share of 30.
    # As in toys: one new value per leaf at most, extra colors for the rest.
    Row("FRMCHR", "Pewter Christening Photo Frame", "Lanternby", "Gifts", _FRAMES,
        "Photo Frame", 26.0, "photo_frame",
        "A heavy frame for a 6 x 4 in photo with an easel back, boxed in tissue.",
        (cw("Pewter", "#8a8d8f"), cw("Brushed Gold", "#c9a85a")), _occ("Christening")),
    Row("FRMRET", "Graduation Signature Photo Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 30.0, "photo_frame",
        "A wide frame with a mount for a message from every friend around the photo.",
        (cw("Walnut", "#6b4a30"), _OAK, cw("Black", "#2a2a2e")), _occ("Graduation")),
    Row("WRPWED", "Wedding Gift Wrap Roll, 2 m", "Calderby & Lune", "Gifts", _WRAP,
        "Wrapping Paper", 6.0, "wrapping_paper",
        "A heavyweight paper with a soft sheen, wide enough for a boxed present.",
        (cw("Ivory Lace", "#f6f1e4", "polka", "#d4af37"),
         cw("Sage Leaf", "#c9d6c0", "stripe", "#ffffff")), _occ("Wedding")),
    Row("WRPANV", "Birthday Foil Wrapping Paper Pack", "Lanternby", "Gifts", _WRAP,
        "Wrapping Paper", 5.5, "wrapping_paper",
        "Two foil-printed sheets and two tags, folded flat in a card sleeve.",
        (cw("Ruby Spot", "#8e1b2c", "polka", "#d4af37"),
         cw("Navy Stripe", "#26365c", "stripe", "#c0c0c0")),
        _occ("Birthday")),
    Row("CHMBRS", "Brass Hedgehog Charm Keyring", "Lanternby", "Gifts", _CHARM, "Keyring",
        10.0, "keyring", "A solid brass charm that darkens with use, on a small gift card.",
        (cw("Brass", "#b5a642"), cw("Copper", "#b87333")), _charm("Hedgehog")),
    Row("CHMCER", "Ceramic Owl Charm Keyring", "Calderby & Lune", "Gifts", _CHARM, "Keyring",
        9.0, "keyring", "A glazed charm hand-painted in the studio, on a waxed cotton cord.",
        (cw("Glaze", "#e8e2d6"), cw("Celadon", "#a7c4a0")), _charm("Owl")),
    Row("CNDPOT", "Orange Blossom Ceramic Pot Candle", "Calderby & Lune", "Gifts", _CANDLE,
        "Scented Candle", 22.0, "jar",
        "A candle poured into a stoneware pot that makes a plant pot once it burns down.",
        (cw("Stone", "#c9c1b3"), cw("Terracotta", "#b5603a")), _scent("Orange Blossom"),
        label="Candle"),
    Row("CNDREF", "Sea Salt Candle Refill", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 12.0, "tin",
        "A wax refill that drops into an empty candle jar, about 35 hours of burn time.",
        (cw("Leaf", "#6f8f4a"),), _scent("Sea Salt"), label="Candle"),
    Row("DECFRS", "Frosted Glass Bauble Star", "Lanternby", "Gifts", _DECOR,
        "Christmas Decoration", 8.0, "star",
        "A hollow star with a crown cap and a loop, boxed singly in tissue.",
        (cw("Pale Blue", "#c9dcea"), cw("Blush", "#ecc6c6")), (("finish", "Finish", "Frosted"),)),
    Row("DECPRL", "Gilded Snowflake Ornament Trio", "Calderby & Lune", "Gifts", _DECOR,
        "Christmas Decoration", 10.0, "snowflake",
        "Three shatterproof snowflakes in graded sizes, on a card for giving.",
        (cw("Pearl", "#efe9e1"),), (("finish", "Finish", "Gilded"),)),
    Row("FRMLTH", "Leather Wedding Photo Album Frame", "Calderby & Lune", "Gifts", _FRAMES,
        "Photo Frame", 34.0, "photo_frame",
        "A stitched frame that folds like a book, holding two 6 x 4 in photos side by side.",
        (cw("Tan", "#a8743f"), cw("Black", "#2a2a2e")), _occ("Wedding")),
    Row("CNDBEE", "Amber Woods Beeswax Pillar Candle", "Lanternby", "Gifts", _CANDLE,
        "Scented Candle", 16.0, "jar",
        "A hand-poured pillar on a glass dish, about 30 hours of burn time.",
        (cw("Honey", "#e0a030"),), _scent("Amber Woods"), label="Candle"),
)  # fmt: skip

# --------------------------------------------------------------------------
# Cleaning: the fragrance varies; the bottle or the spray is drawn.
# --------------------------------------------------------------------------

_BATHRM = ("Cleaning", "Bathroom", "Bathroom Cleaners")
_GLASS = ("Cleaning", "Kitchen & Surfaces", "Glass Cleaners")
_DISH = ("Cleaning", "Kitchen & Surfaces", "Dish Soap")
_LAUND = ("Cleaning", "Laundry", "Laundry Detergent")
_SOFTEN = ("Cleaning", "Laundry", "Fabric Softener")
_LOO = ("Cleaning", "Bathroom", "Toilet Cleaners")
_AIR = ("Cleaning", "Air Care", "Air Fresheners")
_CJ = "Cleaning & Janitorial"


#: The bottle colors a cleaning row draws in.
_BOTTLE_HEX = {
    "Teal": "#1c7c7d", "Lilac": "#b9a3d0", "Blue": "#3f6fb5", "Green": "#4f7a3a",
    "White": "#ffffff", "Pink": "#f2a1b8", "Aqua": "#8fd1d0", "Yellow": "#f2d14b",
    "Cream": "#efe8d8", "Purple": "#7d5ba6",
}  # fmt: skip


def _spray(c: str, accent: str = "#2a2a2e") -> tuple[Color, ...]:
    return (cw(c, _BOTTLE_HEX[c], "solid", accent),)


CLEANING = (
    Row("BTHSPR", "Eucalyptus Bathroom Cleaner Spray 500ml", "Pantry Mill", _CJ, _BATHRM,
        "Bathroom Cleaner", 2.5, "trigger_spray",
        "Lifts limescale and soap scum from tiles, taps and glass. Scented with eucalyptus.",
        _spray("Teal"), _scent("Eucalyptus"), colorless=True),
    Row("BTHSHW", "Lavender Daily Shower Spray 750ml", "Freshfold", _CJ, _BATHRM,
        "Bathroom Cleaner", 3.5, "trigger_spray",
        "A no-rinse spray for after each shower that keeps screens and tiles clear. "
        "Scented with lavender.",
        _spray("Lilac"), _scent("Lavender"), colorless=True),
    Row("BTHMLD", "Pine Mold and Mildew Remover 500ml", "Pantry Mill", _CJ, _BATHRM,
        "Bathroom Cleaner", 3.0, "trigger_spray",
        "A thick spray for grout and sealant: leave ten minutes, then rinse. "
        "Scented with pine.",
        _spray("Green"), _scent("Pine"), colorless=True),
    Row("GLSSPR", "Ocean Breeze Glass Cleaner 500ml", "Freshfold", _CJ, _GLASS, "Glass Cleaner",
        2.0, "trigger_spray",
        "A streak-free spray for windows, mirrors and glass tables. Scented with ocean breeze.",
        _spray("Blue"), _scent("Ocean Breeze"), colorless=True),
    Row("GLSREF", "Mint Glass Cleaner Refill 1L", "Pantry Mill", _CJ, _GLASS, "Glass Cleaner",
        3.0, "bottle",
        "A refill for any trigger bottle, in a bottle made from recycled plastic. "
        "Scented with mint.",
        _spray("Aqua"), _scent("Mint"), label="Refill", colorless=True),
    Row("GLSWIP", "Eucalyptus Glass Cleaning Wipes, Pack of 40", "Freshfold", _CJ, _GLASS,
        "Glass Cleaner", 2.5, "tub",
        "Lint-free wipes for screens, mirrors and car windows. Scented with eucalyptus.",
        _spray("Teal", "#ffffff"), _scent("Eucalyptus"), label="Wipes", colorless=True),
    Row("DSHSOP", "Aloe Vera Dish Soap 500ml", "Pantry Mill", _CJ, _DISH, "Dish Soap", 1.5,
        "bottle",
        "A gentle soap that cuts grease and is kind to hands. Scented with aloe vera.",
        _spray("Green"), _scent("Aloe Vera"), label="Dish Soap", colorless=True),
    Row("DSHCON", "Green Tea Concentrated Dish Soap 1L", "Freshfold", _CJ, _DISH, "Dish Soap",
        2.8, "bottle",
        "A concentrated soap: a few drops do a sink of dishes. Scented with green tea.",
        _spray("Green", "#ffffff"), _scent("Green Tea"), label="Dish Soap", colorless=True),
    Row("DSHPMP", "Pomegranate Dish Soap Pump 400ml", "Pantry Mill", _CJ, _DISH, "Dish Soap",
        2.2, "bottle",
        "A pump bottle for the side of the sink, refillable. Scented with pomegranate.",
        _spray("Pink"), _scent("Pomegranate"), label="Pump", colorless=True),
    Row("LDRLIQ", "Fresh Cotton Laundry Detergent, 40 Washes", "Freshfold", _CJ, _LAUND,
        "Laundry Detergent", 6.0, "bottle",
        "A non-bio liquid that cleans at 20 degrees, gentle on sensitive skin. "
        "Scented with fresh cotton.",
        _spray("White", "#3f6fb5"), _scent("Fresh Cotton"), label="Detergent", colorless=True),
    Row("LDRCON", "Spring Meadow Bio Laundry Detergent, 60 Washes", "Pantry Mill", _CJ, _LAUND,
        "Laundry Detergent", 8.5, "bottle",
        "A concentrated bio liquid for stains at low temperatures. Scented with spring meadow.",
        _spray("Blue", "#ffffff"), _scent("Spring Meadow"), label="Detergent", colorless=True),
    Row("LDRPOD", "Lavender Laundry Pods, 30 Washes", "Freshfold", _CJ, _LAUND,
        "Laundry Detergent", 7.0, "tub",
        "Dissolving pods for a full drum at 30 degrees, in a child-lock tub. "
        "Scented with lavender.",
        _spray("Lilac", "#ffffff"), _scent("Lavender"), label="Pods", colorless=True),
    Row("SFTLAV", "Lavender Fabric Softener, 50 Washes", "Pantry Mill", _CJ, _SOFTEN,
        "Fabric Softener", 3.5, "bottle",
        "A softener that keeps towels fluffy and cuts creases. Scented with lavender.",
        _spray("Lilac", "#ffffff"), _scent("Lavender"), label="Softener", colorless=True),
    Row("SFTSEN", "Wild Jasmine Fabric Softener, 33 Washes", "Freshfold", _CJ, _SOFTEN,
        "Fabric Softener", 2.8, "bottle",
        "A softener with plant-based ingredients, in a recycled bottle. "
        "Scented with wild jasmine.",
        _spray("Pink", "#ffffff"), _scent("Wild Jasmine"), label="Softener", colorless=True),
    Row("LOOGEL", "Pine Thick Toilet Cleaner 750ml", "Pantry Mill", _CJ, _LOO, "Toilet Cleaner",
        1.8, "angled_bottle",
        "An angled-neck bottle of thick gel that clings under the rim. Scented with pine.",
        _spray("Green", "#ffffff"), _scent("Pine"), label="Cleaner", colorless=True),
    Row("LOOTAB", "Ocean Breeze Toilet Cleaning Tablets, Pack of 8", "Freshfold", _CJ, _LOO,
        "Toilet Cleaner", 3.0, "tub",
        "Drop-in tablets that fizz away limescale overnight. Scented with ocean breeze.",
        _spray("Aqua", "#ffffff"), _scent("Ocean Breeze"), label="Tablets", colorless=True),
    # Round 2 (gen#125): at 20K, cleaning held 22 styles against a half share of 30.
    Row("BTHLIM", "Citrus Limescale Remover Gel 750ml", "Freshfold", _CJ, _BATHRM,
        "Bathroom Cleaner", 2.8, "bottle",
        "A clinging gel for taps, shower heads and plug holes. Scented with citrus.",
        _spray("Yellow"), _scent("Citrus"), label="Gel", colorless=True),
    Row("BTHTEA", "Tea Tree Bathroom Foam Cleaner", "Pantry Mill", _CJ, _BATHRM,
        "Bathroom Cleaner", 3.2, "trigger_spray",
        "A foaming spray that sits on tiles and basins while it works. Scented with tea tree.",
        _spray("White", "#4f7a3a"), _scent("Tea Tree"), colorless=True),
    Row("GLSLEM", "Lemon Window Cleaner Concentrate", "Freshfold", _CJ, _GLASS,
        "Glass Cleaner", 3.5, "bottle",
        "Mix one capful with warm water in a bucket for windows and conservatory roofs. "
        "Scented with lemon.",
        _spray("Yellow", "#2a2a2e"), _scent("Lemon"), label="Concentrate", colorless=True),
    Row("GLSMIR", "Cucumber Mirror and Screen Spray", "Pantry Mill", _CJ, _GLASS,
        "Glass Cleaner", 2.6, "trigger_spray",
        "A fine mist that leaves no smears on mirrors, screens and shower glass. "
        "Scented with cucumber.",
        _spray("Aqua", "#ffffff"), _scent("Cucumber"), colorless=True),
    Row("DSHLEM", "Lemon Dishwashing Liquid, Value Size 1.5L", "Pantry Mill", _CJ, _DISH,
        "Dish Soap", 3.0, "bottle",
        "A family-size bottle with a flip cap, for daily washing up. Scented with lemon.",
        _spray("Yellow", "#ffffff"), _scent("Lemon"), label="Liquid", colorless=True),
    Row("DSHSEN", "Chamomile Sensitive Dish Soap", "Freshfold", _CJ, _DISH, "Dish Soap", 2.4,
        "bottle",
        "A dermatologically tested soap for dry or sensitive hands. Scented with chamomile.",
        _spray("Cream", "#4f7a3a"), _scent("Chamomile"), label="Dish Soap", colorless=True),
    Row("LDRPWD", "Cherry Blossom Laundry Powder, 50 Washes", "Pantry Mill", _CJ, _LAUND,
        "Laundry Detergent", 9.0, "box",
        "A biological powder in a cardboard box with a scoop, for whites and colors. "
        "Scented with cherry blossom.",
        _spray("Pink", "#ffffff"), _scent("Cherry Blossom"), label="Powder", colorless=True),
    Row("LDRSHT", "Sandalwood Laundry Sheets", "Freshfold", _CJ, _LAUND, "Laundry Detergent",
        6.5, "box",
        "Thin sheets that dissolve in the drum, one per load, in a plastic-free sleeve. "
        "Scented with sandalwood.",
        _spray("Cream", "#7a5a3a"), _scent("Sandalwood"), label="Sheets", colorless=True),
    Row("SFTVAN", "Vanilla Musk Fabric Conditioner 1.2L", "Freshfold", _CJ, _SOFTEN,
        "Fabric Softener", 3.0, "bottle",
        "A thick conditioner for the drawer, enough for 40 loads. Scented with vanilla musk.",
        _spray("Cream", "#2a2a2e"), _scent("Vanilla Musk"), label="Softener", colorless=True),
    Row("SFTBED", "Cotton Flower Scent Booster Beads", "Pantry Mill", _CJ, _SOFTEN,
        "Fabric Softener", 5.5, "tub",
        "Beads that go in the drum with the washing and last for weeks in the wardrobe. "
        "Scented with cotton flower.",
        _spray("Purple", "#ffffff"), _scent("Cotton Flower"), label="Beads", colorless=True),
    Row("LOOBLK", "Lemon Rim Block, Twin Pack", "Pantry Mill", _CJ, _LOO, "Toilet Cleaner",
        2.0, "rim_block",
        "Hang-on rim blocks that clean and freshen with every flush. Scented with lemon.",
        _spray("Yellow", "#ffffff"), _scent("Lemon"), label="Rim Block",
        colorless=True, params=(("units", "2"),)),
    Row("LOOBLE", "Lavender Toilet Bleach 750ml", "Freshfold", _CJ, _LOO, "Toilet Cleaner",
        1.5, "angled_bottle",
        "A thick bleach for under the rim that kills germs in five minutes. "
        "Scented with lavender.",
        _spray("Lilac", "#ffffff"), _scent("Lavender"), label="Bleach", colorless=True),
    Row("AIRSPR", "Fresh Linen Room Spray 300ml", "Freshfold", _CJ, _AIR, "Air Freshener",
        3.0, "trigger_spray",
        "A fine room mist that freshens soft furnishings and stale air. "
        "Scented with fresh linen.",
        _spray("White", "#3f6fb5"), _scent("Fresh Linen"), colorless=True),
    Row("AIRPLG", "Cherry Blossom Plug-In Diffuser Kit", "Pantry Mill", _CJ, _AIR,
        "Air Freshener", 5.0, "bottle",
        "A wall plug-in and one refill bottle, about 60 days on the low setting. "
        "Scented with cherry blossom.",
        _spray("Pink", "#ffffff"), _scent("Cherry Blossom"), label="Diffuser", colorless=True),
    Row("AIRREE", "Lime and Basil Reed Diffuser 100ml", "Freshfold", _CJ, _AIR,
        "Air Freshener", 9.0, "jar",
        "A glass bottle with eight rattan reeds; turn the reeds weekly. "
        "Scented with lime and basil.",
        _spray("Green", "#b08a5a"), _scent("Lime and Basil"), label="Reeds", colorless=True),
    Row("AIRGEL", "Vanilla Gel Air Freshener Pot", "Pantry Mill", _CJ, _AIR,
        "Air Freshener", 2.0, "tub",
        "A gel pot for a hallway or a small room that lasts about four weeks. "
        "Scented with vanilla.",
        _spray("Cream", "#ffffff"), _scent("Vanilla"), label="Gel", colorless=True),
    # Growth round 4: a new fragrance in each leaf, so every row in it may take one more.
    Row("LDRMEA", "Spring Meadow Laundry Liquid 1.4L", "Freshfold", _CJ, _LAUND,
        "Laundry Detergent", 7.5, "bottle",
        "A concentrated non-biological liquid for 40 washes, gentle on sensitive skin. "
        "Scented with spring meadow.",
        _spray("Aqua", "#ffffff"), _scent("Spring Meadow"), label="Liquid", colorless=True),
    Row("LDRCAP", "Ocean Breeze Laundry Capsules", "Pantry Mill", _CJ, _LAUND,
        "Laundry Detergent", 8.0, "tub",
        "Three-chamber capsules in a child-lock tub: one per load, straight into the drum. "
        "Scented with ocean breeze.",
        _spray("Blue", "#ffffff"), _scent("Ocean Breeze"), label="Capsules", colorless=True),
    Row("SFTJAS", "Jasmine Fabric Conditioner 1L", "Pantry Mill", _CJ, _SOFTEN,
        "Fabric Softener", 2.5, "bottle",
        "A light conditioner that softens towels and cuts creasing, for 33 loads. "
        "Scented with jasmine.",
        _spray("White", "#b9a3d0"), _scent("Jasmine"), label="Softener", colorless=True),
    Row("LOOTGL", "Pine Thick Toilet Gel 750ml", "Freshfold", _CJ, _LOO, "Toilet Cleaner",
        1.8, "angled_bottle",
        "An angled-neck gel that clings under the rim and lifts limescale overnight. "
        "Scented with pine.",
        _spray("Green", "#ffffff"), _scent("Pine"), label="Gel", colorless=True),
    Row("AIRAER", "Orange Blossom Air Freshener Aerosol 300ml", "Pantry Mill", _CJ, _AIR,
        "Air Freshener", 1.5, "bottle",
        "A quick burst for a kitchen or a bathroom that clears cooking smells. "
        "Scented with orange blossom.",
        _spray("Yellow", "#2a2a2e"), _scent("Orange Blossom"), label="Aerosol", colorless=True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Food & Drink: the tea's blend or the coffee's origin varies; the pack is drawn.
# --------------------------------------------------------------------------

_TEA = ("Food & Drink", "Tea & Coffee", "Tea")
_COFFEE = ("Food & Drink", "Tea & Coffee", "Coffee")
_JAM = ("Food & Drink", "Pantry", "Jam")
_CHUTNEY = ("Food & Drink", "Pantry", "Chutney")
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


_CRISPS = ("Food & Drink", "Snacks", "Crisps")
_OIL = ("Food & Drink", "Pantry", "Olive Oil")
_PASTA = ("Food & Drink", "Pantry", "Pasta")


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
        (("500ml", 6.0), ("1L", 10.5)), "Olive Oil", colorless=True),
    Row("OILSPA", "Spanish Extra Virgin Olive Oil", "Pantry Mill", _FD, _OIL, "Olive Oil", 5.0,
        "bottle", "A fruity first pressing in a dark glass bottle that keeps out the light.",
        (cw("Black", "#2a2a2e", "solid", "#d4af37"),), _origin("Spanish"),
        (("500ml", 5.0), ("1L", 9.0)), "Olive Oil", colorless=True),
    Row("OILITA", "Italian Extra Virgin Olive Oil Tin", "Freshfold", _FD, _OIL, "Olive Oil",
        12.0, "tin", "A 750 ml tin of peppery oil, picked early in the season.",
        (cw("Red", "#9e2a2b", "solid", "#efe8d8"),), _origin("Italian"), label="Olive Oil",
        colorless=True),
    Row("OILPOR", "Portuguese Extra Virgin Olive Oil", "Hearth & Table", _FD, _OIL, "Olive Oil",
        7.0, "bottle", "A mild, buttery oil for cooking and finishing, in a 500 ml bottle.",
        (cw("Teal", "#1c7c7d", "solid", "#d4af37"),), _origin("Portuguese"), label="Olive Oil",
        colorless=True),
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
)  # fmt: skip

# --------------------------------------------------------------------------
# Beauty: the hair type and the ingredient vary; the hand wash's fragrance varies.
# --------------------------------------------------------------------------

_SHAMPOO = ("Beauty", "Hair Care", "Shampoo")
_CONDIT = ("Beauty", "Hair Care", "Conditioner")
_HANDWASH = ("Beauty", "Bath & Body", "Hand Wash")


def _hair(hair: str, ingredient: str) -> tuple[tuple[str, str, str], ...]:
    return (("hair_type", "Hair type", hair), ("ingredient", "Ingredient", ingredient))


BEAUTY = (
    Row("SHPARG", "Argan Oil Shampoo for Dry Hair", "Mirefield Naturals", "Beauty", _SHAMPOO,
        "Shampoo", 6.0, "bottle",
        "A sulfate-free daily wash in a pump bottle, made without silicones.",
        (cw("Amber", "#c98a2e", "solid", "#ffffff"),), _hair("Dry", "Argan Oil"),
        (("250ml", 6.0), ("500ml", 10.0)), "Shampoo", colorless=True),
    Row("SHPROS", "Rosemary Shampoo for Curly Hair", "Hollin Hair", "Beauty", _SHAMPOO,
        "Shampoo", 8.0, "bottle",
        "A low-lather wash that cleans the scalp and leaves the lengths soft.",
        (cw("Sage", "#9bb08f", "solid", "#2a2a2e"),), _hair("Curly", "Rosemary"),
        label="Shampoo", colorless=True),
    Row("CNDARG", "Argan Oil Conditioner for Dry Hair", "Mirefield Naturals", "Beauty",
        _CONDIT, "Conditioner", 6.0, "bottle",
        "A rinse-out cream for the mid-lengths and ends. Leave on for one minute.",
        (cw("Cream", "#efe8d8", "solid", "#c98a2e"),), _hair("Dry", "Argan Oil"),
        (("250ml", 6.0), ("500ml", 10.0)), "Conditioner", colorless=True),
    Row("CNDCOC", "Coconut Conditioner for Curly Hair", "Hollin Hair", "Beauty", _CONDIT,
        "Conditioner", 8.0, "bottle",
        "A thick cream that defines the curl pattern and cuts frizz between washes.",
        (cw("White", "#ffffff", "solid", "#7a5a3a"),), _hair("Curly", "Coconut"),
        label="Conditioner", colorless=True),
    Row("HWSFIG", "Fig Leaf Hand Wash 300ml", "Mirefield Naturals", "Beauty", _HANDWASH,
        "Hand Wash", 5.0, "bottle",
        "A gentle pump wash with plant glycerin, for kitchen or bathroom. Scented with fig leaf.",
        (cw("Green", "#4f7a3a", "solid", "#ffffff"),), _scent("Fig Leaf"), label="Hand Wash",
        colorless=True),
    Row("HWSROS", "Rose & Geranium Hand Wash 500ml", "Hollin Hair", "Beauty", _HANDWASH,
        "Hand Wash", 7.0, "bottle",
        "A refillable glass pump bottle of hand wash. Scented with rose & geranium.",
        (cw("Pink", "#e27d9f", "solid", "#2a2a2e"),), _scent("Rose & Geranium"),
        label="Hand Wash", colorless=True),
    Row("HWSALM", "Sweet Almond Hand Wash Refill 1L", "Mirefield Naturals", "Beauty", _HANDWASH,
        "Hand Wash", 9.0, "bottle",
        "A recycled bottle with enough to refill a pump bottle four times. "
        "Scented with sweet almond.",
        (cw("Cream", "#efe8d8", "solid", "#7a5a3a"),), _scent("Sweet Almond"), label="Refill",
        colorless=True),
)  # fmt: skip

# --------------------------------------------------------------------------
# Home (growth round 3): the cushion's or towel's fabric and the basket's material
# vary; the shape is drawn in the hero color.
# --------------------------------------------------------------------------

_CUSH = ("Home", "Soft Furnishings", "Cushions")
_TOWEL = ("Home", "Bathroom", "Bath Towels")
_BASKET = ("Home", "Storage", "Storage Baskets")
_TWL = (("Hand Towel", 8.0), ("Bath Towel", 14.0), ("Bath Sheet", 22.0))

HOME = (
    Row("CSHVEL", "Velvet Piped Cushion", "Hearth & Table", "Home", _CUSH, "Cushion", 18.0,
        "cushion", "A square cushion with a piped edge and a feather pad. Zip opening.",
        (cw("Teal", "#1c7c7d"), cw("Mustard", "#d4a32a"), cw("Blush", "#e8b9b3"),
         cw("Navy", "#26365c")), _fab("Velvet"), (("45 x 45cm", 18.0), ("55 x 55cm", 24.0))),
    Row("CSHLIN", "Linen Fringed Cushion", "Lanternby", "Home", _CUSH, "Cushion", 22.0,
        "cushion", "A square cushion with a knotted fringe and a hollowfibre pad.",
        (cw("Oat", "#d8c9a8"), cw("Sage", "#9bb08f"), cw("Rust", "#a4502a")), _fab("Linen"),
        (("45 x 45cm", 22.0), ("55 x 55cm", 28.0))),
    Row("CSHBOU", "Boucle Bolster Cushion", "Calderby & Lune", "Home", _CUSH, "Cushion", 26.0,
        "cushion", "A long round bolster with gathered ends, for a sofa arm or a bed.",
        (cw("Cream", "#efe8d8"), cw("Taupe", "#8b7d6b"), cw("Charcoal", "#3b3b3e")),
        _fab("Boucle"), label="Bolster"),
    Row("CSHCHN", "Chenille Oblong Cushion", "Hearth & Table", "Home", _CUSH, "Cushion", 20.0,
        "cushion", "A 30 x 50 cm cushion with a feather pad, for a chair or a window seat.",
        (cw("Ochre", "#c9873a"), cw("Forest", "#2f5a3a"), cw("Dove Grey", "#b5b5b0")),
        _fab("Chenille")),
    Row("CSHCRD", "Corduroy Pleated Cushion", "Lanternby", "Home", _CUSH, "Cushion", 24.0,
        "cushion", "A round cushion pleated to a covered button at its centre.",
        (cw("Terracotta", "#c46a4a"), cw("Olive", "#6b6b3a"), cw("Ivory", "#f3ecd9")),
        _fab("Corduroy")),
    Row("TWLORG", "Organic Cotton Bath Towel", "Hearth & Table", "Home", _TOWEL, "Towel", 8.0,
        "bath_towel", "A soft, absorbent towel with a hanging loop. Machine wash at 40.",
        (cw("White", "#ffffff"), cw("Sage", "#9bb08f"), cw("Slate", "#5a6470"),
         cw("Blush", "#e8b9b3")), _fab("Organic Cotton"), _TWL),
    Row("TWLBAM", "Bamboo Bath Towel", "Calderby & Lune", "Home", _TOWEL, "Towel", 10.0,
        "bath_towel", "A silky, quick-drying towel with a woven border and a hanging loop.",
        (cw("Ivory", "#f3ecd9"), cw("Charcoal", "#3b3b3e"), cw("Duck Egg", "#a9c9c4")),
        _fab("Bamboo"), (("Hand Towel", 10.0), ("Bath Towel", 18.0), ("Bath Sheet", 28.0))),
    Row("TWLTRK", "Turkish Cotton Bath Towel", "Lanternby", "Home", _TOWEL, "Towel", 9.0,
        "bath_towel", "A heavy towel woven with long loops, with a hanging loop. Machine wash.",
        (cw("Navy", "#26365c"), cw("White", "#ffffff"), cw("Mustard", "#d4a32a"),
         cw("Stone", "#c9bfae")), _fab("Turkish Cotton"),
        (("Hand Towel", 9.0), ("Bath Towel", 16.0), ("Bath Sheet", 25.0))),
    Row("TWLZRO", "Zero Twist Cotton Bath Towel", "Hearth & Table", "Home", _TOWEL, "Towel",
        11.0, "bath_towel", "A light, fluffy towel that dries fast. Tumble dry low.",
        (cw("Pale Pink", "#f2c9cf"), cw("Teal", "#1c7c7d"), cw("Cloud Grey", "#cfd1d3")),
        _fab("Zero Twist Cotton"),
        (("Hand Towel", 11.0), ("Bath Towel", 19.0), ("Bath Sheet", 30.0))),
    Row("BSKSEA", "Seagrass Lidded Storage Basket", "Lanternby", "Home", _BASKET,
        "Storage Basket", 22.0, "box_wide",
        "A woven basket with a fitted lid and two handles, for blankets or toys.",
        (cw("Natural", "#c9a96e"), cw("Black", "#2a2a2e")), _mat("Seagrass"),
        (("Medium", 22.0), ("Large", 30.0))),
    Row("BSKRAT", "Rattan Round Storage Basket", "Calderby & Lune", "Home", _BASKET,
        "Storage Basket", 26.0, "box_wide",
        "A round woven basket with cut-out handles, for a shelf or a bathroom floor.",
        (cw("Honey", "#c48a3a"), cw("Natural", "#c9a96e")), _mat("Rattan"),
        (("Small", 18.0), ("Medium", 26.0))),
    Row("BSKHYA", "Water Hyacinth Storage Basket", "Hearth & Table", "Home", _BASKET,
        "Storage Basket", 24.0, "box_wide",
        "A chunky woven basket on a metal frame that keeps its shape, with rope handles.",
        (cw("Natural", "#c9a96e"), cw("Grey Wash", "#9a9a94")), _mat("Water Hyacinth"),
        (("Medium", 24.0), ("Large", 32.0))),
    Row("BSKFLT", "Felt Storage Basket", "Lanternby", "Home", _BASKET, "Storage Basket", 14.0,
        "box_wide", "A soft folding basket with stitched loop handles, for a cube shelf.",
        (cw("Grey Marl", "#9a9ca0"), cw("Charcoal", "#3b3b3e"), cw("Oat", "#d8c9a8")),
        _mat("Felt")),
)  # fmt: skip

#: Every breadth row, by department.
DEPARTMENTS = {
    "Toys": TOYS, "Garden": GARDEN, "Gifts": GIFTS, _CJ: CLEANING, _FD: FOOD, "Beauty": BEAUTY,
    "Home": HOME,
}  # fmt: skip


def docs() -> list[dict]:
    """Every breadth row's catalog document, department by department."""
    return [r.doc() for rows in DEPARTMENTS.values() for r in rows]
