"""The Books department (gen#1119, slice 1): 480 invented titles, each in three formats.

``Books`` is both the store's department (the top level of ``category_path``, on
``core/departments.RETAIL``) and the build record's ``department`` (:mod:`departments`). Its one
type, Book (``type_specs/book.py``), holds eight leaves of 60 titles each: cookery, crafts,
gardening, DIY, pets, children's, fiction and travel. A title is one style, and its SKUs are its
formats (``format``: Ebook, Paperback, Hardback, cheapest first). A book carries no color: its
cover color is drawn, not sold (``colorless``).

Every title, author and publisher is invented (ruling 2026-11-21). A title is written by hand
when it collides with another department (:data:`COLLISIONS`: 'The Book of Chocolate' beside the
chocolate bars), and otherwise built from a subject in one or two of its leaf's frames. The id is
our own (``BRD-BOOK001``), never an ISBN. Each title of a leaf draws its own cover: its index
``i`` picks cover color ``i % 10`` and layout ``i // 10``, and the leaf picks the emblem
(:mod:`kit_books`).
"""

# ruff: noqa: E501 -- data rows read better whole than wrapped (prototype only).

from __future__ import annotations

import zlib

from synthetic_ecommerce_data.domains.retail import kit_books  # noqa: F401 -- registers book_cover
from synthetic_ecommerce_data.domains.retail.type_registry import Row, a, count, cw

#: The build record's department, and the top level of every path.
DEPARTMENT = "Books"
ROOT = "Books"
PRODUCT_TYPE = "Book"
SHAPE = "book_cover"
#: The SKU axis: a book's formats, cheapest first.
FORMATS = ("Ebook", "Paperback", "Hardback")
TITLES_PER_LEAF = 60

#: The invented publishing houses: each is a book's brand and its ``publisher`` attribute.
WRENHALLOW = "Wrenhallow Press"
MARLOWBY = "Marlowby Books"
THIMBLECOTE = "Thimblecote Press"
FERNCASTLE = "Ferncastle Editions"
ASHCOMBE = "Ashcombe & Rook"
LINDENQUAY = "Lindenquay Publishing"
MODDLEWICK = "Moddlewick Books"
GULLFEATHER = "Gullfeather Press"
PUBLISHERS = (WRENHALLOW, MARLOWBY, THIMBLECOTE, FERNCASTLE, ASHCOMBE, LINDENQUAY, MODDLEWICK,
              GULLFEATHER)  # fmt: skip
OWNERS = tuple((p, "third_party") for p in PUBLISHERS)

#: The cover colors: the drawing takes a title's as its fill (index ``i % 10``).
COVERS = (
    cw("Brick", "#a8432f", "solid", "#ffffff"), cw("Forest", "#2f6b45", "solid", "#ffffff"),
    cw("Navy", "#26406b", "solid", "#ffffff"), cw("Mustard", "#d4a62a", "solid", "#2a2a2e"),
    cw("Plum", "#6e3b6e", "solid", "#ffffff"), cw("Teal", "#1f7a7a", "solid", "#ffffff"),
    cw("Cream", "#efe6cf", "solid", "#2a2a2e"), cw("Coral", "#e0705a", "solid", "#ffffff"),
    cw("Charcoal", "#3a3a40", "solid", "#ffffff"), cw("Sky", "#7fb2d9", "solid", "#2a2a2e"),
)  # fmt: skip
#: The cover layouts (index ``i // 10``): see :func:`kit_books.book_cover`.
LAYOUTS = ("0", "1", "2", "3", "4", "5")

FIRST_NAMES = ("Alice", "Ben", "Clara", "Daniel", "Eleanor", "Felix", "Greta", "Harriet", "Isaac",
               "Jonah", "Katherine", "Leo", "Miriam", "Nathan", "Olive", "Patrick", "Rosalind",
               "Samuel", "Tessa", "Victor", "Wendy", "Ada", "Hugo", "Imogen", "Joel", "Lydia",
               "Martin", "Nina", "Owen", "Ruth")  # fmt: skip
SURNAMES = ("Ashdown", "Bramley", "Calloway", "Dunmore", "Ellery", "Fairweather", "Garside",
            "Hartley", "Inglis", "Jessop", "Kettering", "Lomax", "Marchbank", "Netherwood",
            "Ockenden", "Penhallow", "Quarrie", "Ravenhill", "Sowerby", "Thackray", "Upwood",
            "Vellacott", "Whitlock", "Yelland", "Abernethy", "Brackley", "Coverdale", "Denholm",
            "Edgecombe", "Fenwick")  # fmt: skip


class Leaf:
    """One leaf of the department: its label, genre, emblem, page range, blurb and titles."""

    def __init__(self, label: str, genre: str, emblem: str, pages: tuple[int, int], blurb: str,
                 hand: tuple[tuple[str, str], ...], subjects: tuple[str, ...],
                 frames: tuple[str, ...]) -> None:  # fmt: skip
        self.label = label
        self.genre = genre
        self.emblem = emblem
        self.pages = pages
        self.blurb = blurb
        self.hand = hand
        self.subjects = subjects
        self.frames = frames

    @property
    def path(self) -> tuple[str, ...]:
        return (ROOT, self.label)

    def titles(self) -> list[tuple[str, str]]:
        """The leaf's 60 ``(title, subject)`` pairs: the hand-written titles, then each subject
        in two of the frames (the last perhaps in one), cut to :data:`TITLES_PER_LEAF`."""
        out = list(self.hand)
        n = len(self.frames)
        for j, s in enumerate(self.subjects):
            for f in (self.frames[j % n], self.frames[(j + 2) % n]):
                t = f.format(s=s)
                out.append((t[0].upper() + t[1:], s))
        if len(out) < TITLES_PER_LEAF:
            raise ValueError(f"{self.label}: {len(out)} titles, fewer than {TITLES_PER_LEAF}")
        return out[:TITLES_PER_LEAF]


#: The age bands a children's title is written for, by the title's index.
AGE_BANDS = ("0-2 years", "3-5 years", "6-8 years", "9-12 years")
#: A children's book's pages by its age band.
AGE_PAGES = {"0-2 years": (12, 24), "3-5 years": (24, 40), "6-8 years": (64, 128),
             "9-12 years": (160, 352)}  # fmt: skip

COOKERY = Leaf(
    "Cookery Books", "Cookery & Baking", "cookery", (160, 320),
    "Recipes and kitchen know-how for {s}, tested in a home kitchen.",
    (
        ("The Book of Chocolate", "bars, truffles and bakes made with chocolate"),
        ("How to Make Brownies", "brownies, blondies and tray bakes"),
        ("Knife Skills", "chopping, slicing and carving"),
        ("Bread at Home", "loaves, rolls and flatbreads"),
        ("One More Slice of Cake", "sponges, loaf cakes and layer cakes"),
        ("Jam Jar Mornings", "jam, marmalade and fruit curds"),
        ("Pasta Sundays", "pasta made by hand"),
        ("The Pizza Oven Cookbook", "pizza from a wood-fired oven"),
        ("Honey from the Hive Kitchen", "cooking and baking with honey"),
        ("The Coffee Lover's Kitchen", "coffee drinks and coffee bakes"),
        ("A Pot of Tea and a Slice", "afternoon tea at home"),
        ("Porridge for Breakfast", "porridge, oats and grains"),
        ("The Ice Cream Parlour at Home", "ice cream, sorbets and sundaes"),
        ("Sauce: The Kitchen Secret", "sauces, gravies and dressings"),
        ("Biscuits for Every Tin", "biscuits and cookies"),
        ("One Saucepan Suppers", "suppers made in one saucepan"),
        ("Cooking with Wine", "stews and sauces cooked with wine"),
        ("The Cider Kitchen", "orchard cooking with cider"),
        ("Gin Cocktails at Home", "gin cocktails and syrups"),
        ("Cheese on the Table", "cheese boards and baked cheese"),
    ),
    ("Slow Cooking", "Weeknight Suppers", "Soups and Stews", "Vegetable Feasts", "One-Pot Meals",
     "Roast Dinners", "Summer Salads", "Curries", "Fish Suppers", "Barbecues",
     "Make-Ahead Meals", "Family Baking", "Breakfasts", "Steamed Puddings", "Tray Bakes",
     "Preserving", "Street Food", "Plant-Based Cooking", "Christmas Cooking", "Packed Lunches"),
    ("All About {s}", "The Little Book of {s}", "{s}: A Kitchen Guide",
     "The Kitchen Table Book of {s}"),
)  # fmt: skip

CRAFTS = Leaf(
    "Craft Books", "Crafts & Sewing", "craft", (128, 256),
    "Projects, patterns and techniques for {s}, from first steps to finished pieces.",
    (
        ("Learn to Sew", "sewing by hand and by machine"),
        ("Knit Your Own Jumper", "knitting a jumper"),
        ("The Cardigan Pattern Book", "knitted cardigans"),
        ("Wallpaper Projects", "projects with wallpaper offcuts"),
        ("Hook Your Own Rug", "hooked and braided rugs"),
        ("The Photo Frame Book", "frames for photos and prints"),
        ("Make and Fly a Paper Kite", "kites of paper and cane"),
        ("Make a Lampshade", "lampshades of fabric and paper"),
    ),
    ("Embroidery", "Needlepoint", "Crochet", "Quilting", "Patchwork", "Macrame", "Paper Crafts",
     "Origami", "Calligraphy", "Watercolour Painting", "Pottery", "Candle Making", "Soap Making",
     "Needle Felting", "Weaving", "Lino Printing", "Bookbinding", "Jewellery Making", "Mosaic",
     "Decoupage", "Card Making", "Basketry", "Woodcarving", "Dressmaking", "Hand Lettering",
     "Upcycling"),
    ("{s} for Beginners", "The Complete Book of {s}", "{s} Step by Step", "A Year of {s}"),
)  # fmt: skip

GARDENING = Leaf(
    "Gardening Books", "Gardening", "gardening", (144, 320),
    "A guide to {s}, with planting plans and a month-by-month calendar.",
    (
        ("The Garden Shed Handbook", "the garden shed and its tools"),
        ("Seeds to Plate", "growing food from seeds"),
        ("The Watering Can Year", "watering through the seasons"),
        ("Bulbs for Spring Colour", "spring bulbs"),
        ("A Year on the Lawn", "lawn care"),
        ("Hedge Laying for Beginners", "hedge laying and hedge care"),
        ("The Planter Garden", "gardens grown in planters and pots"),
        ("The Garden Bird Book", "birds that visit the garden"),
        ("One Plant at a Time", "choosing and placing plants"),
    ),
    ("Roses", "Herbs", "Vegetable Growing", "Fruit Trees", "Container Gardening",
     "Prairie Planting", "Country Gardens", "Small Gardens", "Woodland Planting", "Pond Making",
     "Composting", "Climbing Plants", "Cut Flowers", "Gravel Gardens", "Garden Design", "Pruning",
     "Greenhouse Growing", "Ferns", "Dahlias", "Tomatoes", "Organic Gardening", "Dry Gardens",
     "Balcony Gardens", "Ornamental Grasses", "Wildlife Gardening", "Alpines"),
    ("The Gardener's Guide to {s}", "{s} Through the Year", "A Beginner's Book of {s}",
     "Notes on {s}"),
)  # fmt: skip

DIY = Leaf(
    "DIY Books", "DIY & Home Improvement", "diy", (128, 288),
    "Illustrated steps for {s}, with the tools and materials each job needs.",
    (
        ("Drill and Fix", "drilling and fixing"),
        ("Paint Like a Decorator", "painting walls and woodwork"),
        ("Build a Bookcase", "building shelves and a bookcase"),
        ("Every Tool Explained", "the tools for jobs around the house"),
        ("Bulb, Socket and Plug", "lights, plugs and wiring"),
        ("Hang a Mirror, Fix a Shelf", "putting up mirrors and shelves"),
        ("Mend Your Own Clock", "clock repair"),
        ("Reupholster Your Sofa", "reupholstering a sofa"),
    ),
    ("Plumbing", "Tiling", "Plastering", "Woodworking", "Flooring", "Home Wiring", "Decorating",
     "Kitchen Fitting", "Bathroom Renovation", "Shelving", "Bricklaying", "Roofing", "Fencing",
     "Decking", "Insulation", "Damp Proofing", "Window Repairs", "Door Fitting",
     "Furniture Restoration", "Loft Conversions", "Garden Walls", "Home Maintenance", "Joinery",
     "Paving", "Guttering", "Stair Repairs"),
    ("{s} Without Fuss", "The DIY Guide to {s}", "{s}: The Complete Manual", "Get Started with {s}"),
)  # fmt: skip

PET_BOOKS = Leaf(
    "Pet Books", "Pets & Animals", "pets", (128, 256),
    "Everything an owner needs to know about {s}: feeding, health, training and care.",
    (
        ("Your First Puppy", "a new puppy"),
        ("The Cat Care Book", "a cat's care at home"),
        ("Treats Your Dog Will Love", "home-made dog treats"),
    ),
    ("Puppies", "Working Dogs", "Senior Dogs", "Kittens", "House Cats", "Rabbits", "Guinea Pigs",
     "Hamsters", "Chickens", "Ducks", "Goats", "Tropical Fish", "Pond Fish", "Horses", "Ponies",
     "Budgies", "Parrots", "Tortoises", "Lizards", "Snakes", "Ferrets", "Gundogs", "Sheepdogs",
     "Terriers", "Spaniels", "Rats and Mice", "Bees", "Canaries", "Aquarium Shrimp"),
    ("The Complete Guide to {s}", "Caring for {s}", "{s}: An Owner's Handbook", "Living with {s}"),
)  # fmt: skip

CHILDRENS = Leaf(
    "Children's Books", "Children's", "childrens", (24, 40),
    "A story about {s}, with colourful pictures on every page.",
    (
        ("The Kite That Flew Away", "a kite on a windy day"),
        ("Skateboard Sam", "a boy and his skateboard"),
        ("The Football Fox", "a fox who loves football"),
        ("The Lunch Box Monster", "a lunch box with a secret"),
        ("Bike Day", "learning to ride a bike"),
    ),
    ("Little Otter", "Pablo the Penguin", "Rosie Rabbit", "Bertie Bear", "Mo the Mole",
     "Hattie Hedgehog", "Tilly Tortoise", "Oscar Owl", "Freddie Fox", "Dottie Duck",
     "Sammy Squirrel", "Lulu the Lamb", "Barnaby Badger", "Primrose Pig", "Wilf the Whale",
     "Cleo the Cat", "Doris the Dragon", "Ziggy Zebra", "Milo Mouse", "Nell the Narwhal",
     "Toby Tiger", "Gus the Goose", "Ruby Robin", "Pickle the Pony", "Ellie Elephant",
     "Kit the Kitten", "Rory the Lion", "Bea the Bee"),
    ("{s} Goes to the Seaside", "Goodnight, {s}", "{s} Learns to Swim", "A Birthday for {s}",
     "Where Is {s}?"),
)  # fmt: skip

FICTION = Leaf(
    "Fiction", "Fiction", "fiction", (256, 480),
    "A novel of secrets and second chances, set in {s}.",
    (
        ("A Jar of Honey at Midnight", "a beekeeper's house"),
        ("Wine at the Harbour Inn", "a harbour inn and its regulars"),
        ("The Clock on Ferry Lane", "a clock-mender's shop"),
        ("A Mirror in the Attic", "a snowbound manor"),
        ("The Tea Room on Harbour Street", "a seaside tea room"),
        ("The Cider Orchard Letters", "an old cider orchard"),
    ),
    ("Ravensmoor", "Gullhaven", "Thornby Sands", "Merrowcombe", "Ashbury Fen", "Kestrel Point",
     "Wyndham Quay", "Holloway Down", "Saltmarsh End", "Brackenridge", "Fallowfield",
     "Pennick Harbour", "Larchmere", "Cobble Wynd", "Stormhaven", "Elderbrook", "Marram Bay",
     "Coldwater Fell", "Hartsmere", "Rookwood Hall", "Greystone Pike", "Dunmoor", "Wrenfield",
     "Ottery Mead", "Lantern Row", "Sorrel Hill", "Quillon Sands"),
    ("Summer at {s}", "The Last Letter from {s}", "Snow Falls on {s}", "A Stranger in {s}",
     "The Lighthouse at {s}"),
)  # fmt: skip

TRAVEL = Leaf(
    "Travel Books", "Travel", "travel", (192, 384),
    "Routes, places to stay and things to see in {s}, with maps for every chapter.",
    (
        ("Tent Nights", "camping under canvas"),
        ("One Suitcase, Twelve Cities", "city breaks with one suitcase"),
        ("Walking the Coast Path", "coastal walking routes"),
        ("Under the Stars with a Sleeping Bag", "wild camping"),
        ("With a Backpack Through the Balkans", "the Balkans on foot and by bus"),
    ),
    ("the Lake District", "Cornwall", "the Scottish Highlands", "Snowdonia", "the Norfolk Broads",
     "the Cotswolds", "the Yorkshire Dales", "the Peak District", "Northumberland",
     "Pembrokeshire", "the Isle of Skye", "Brittany", "Provence", "the Algarve", "Tuscany",
     "the Dolomites", "Andalusia", "the Black Forest", "the Norwegian Fjords", "Iceland",
     "the Greek Islands", "Sicily", "the Swiss Alps", "Normandy", "the Basque Country",
     "Copenhagen", "Lisbon", "Vienna"),
    ("{s}: Twelve Short Journeys", "Slow Days in {s}", "The Pocket Companion to {s}",
     "{s} by Rail and Ferry"),
)  # fmt: skip

LEAVES = (COOKERY, CRAFTS, GARDENING, DIY, PET_BOOKS, CHILDRENS, FICTION, TRAVEL)

#: The titles that collide with a type of another department: ``(title, type, word)``. The word
#: is in the title and in some title of that type in the build, so a search for the word finds
#: the book beside the product (``tests/test_retail_books_1119.py`` measures each on the build).
COLLISIONS = (
    ("The Book of Chocolate", "Chocolate Bar", "chocolate"),
    ("The Book of Chocolate", "Chocolate Box", "chocolate"),
    ("Knife Skills", "Kitchen Knife", "knife"),
    ("The Garden Shed Handbook", "Garden Storage", "shed"),
    ("Your First Puppy", "Dog Food", "puppy"),
    ("Bread at Home", "Bread", "bread"),
    ("One More Slice of Cake", "Cake", "cake"),
    ("Jam Jar Mornings", "Jam", "jam"),
    ("Pasta Sundays", "Pasta", "pasta"),
    ("The Pizza Oven Cookbook", "Pizza", "pizza"),
    ("Honey from the Hive Kitchen", "Honey", "honey"),
    ("The Coffee Lover's Kitchen", "Coffee", "coffee"),
    ("A Pot of Tea and a Slice", "Tea", "tea"),
    ("Porridge for Breakfast", "Porridge", "porridge"),
    ("The Ice Cream Parlour at Home", "Ice Cream", "ice cream"),
    ("Sauce: The Kitchen Secret", "Sauce", "sauce"),
    ("Biscuits for Every Tin", "Biscuits", "biscuits"),
    ("One Saucepan Suppers", "Saucepan", "saucepan"),
    ("Cooking with Wine", "Wine", "wine"),
    ("The Cider Kitchen", "Cider", "cider"),
    ("Gin Cocktails at Home", "Gin", "gin"),
    ("Knit Your Own Jumper", "Jumper", "jumper"),
    ("The Cardigan Pattern Book", "Cardigan", "cardigan"),
    ("Wallpaper Projects", "Wallpaper", "wallpaper"),
    ("Hook Your Own Rug", "Rug", "rug"),
    ("The Photo Frame Book", "Photo Frame", "frame"),
    ("Make and Fly a Paper Kite", "Kite", "kite"),
    ("Make a Lampshade", "Lampshade", "lampshade"),
    ("Seeds to Plate", "Seeds", "seeds"),
    ("The Watering Can Year", "Watering Can", "watering can"),
    ("Bulbs for Spring Colour", "Bulbs", "bulbs"),
    ("A Year on the Lawn", "Lawn Mower", "lawn"),
    ("Hedge Laying for Beginners", "Hedge Trimmer", "hedge"),
    ("The Planter Garden", "Planter", "planter"),
    ("The Garden Bird Book", "Bird Feeder", "bird"),
    ("One Plant at a Time", "Plant", "plant"),
    ("Drill and Fix", "Combi Drill", "drill"),
    ("Paint Like a Decorator", "Paint", "paint"),
    ("Build a Bookcase", "Bookcase", "bookcase"),
    ("Every Tool Explained", "Tool Kit", "tool"),
    ("Bulb, Socket and Plug", "Light Bulb", "bulb"),
    ("Hang a Mirror, Fix a Shelf", "Mirror", "mirror"),
    ("Mend Your Own Clock", "Clock", "clock"),
    ("Reupholster Your Sofa", "Sofa", "sofa"),
    ("The Cat Care Book", "Cat Food", "cat"),
    ("Treats Your Dog Will Love", "Dog Treats", "treats"),
    ("The Kite That Flew Away", "Kite", "kite"),
    ("Skateboard Sam", "Skateboard", "skateboard"),
    ("The Football Fox", "Football", "football"),
    ("The Lunch Box Monster", "Lunch Box", "lunch"),
    ("Bike Day", "Bicycle", "bike"),
    ("A Jar of Honey at Midnight", "Honey", "honey"),
    ("Wine at the Harbour Inn", "Wine", "wine"),
    ("The Clock on Ferry Lane", "Clock", "clock"),
    ("A Mirror in the Attic", "Mirror", "mirror"),
    ("The Tea Room on Harbour Street", "Tea", "tea"),
    ("Tent Nights", "Tent", "tent"),
    ("One Suitcase, Twelve Cities", "Suitcase", "suitcase"),
    ("Walking the Coast Path", "Walking Boots", "walking"),
    ("Under the Stars with a Sleeping Bag", "Sleeping Bag", "sleeping bag"),
    ("With a Backpack Through the Balkans", "Backpack", "backpack"),
)
#: The ruling's titles whose other half the catalogue does not sell yet (0 today): brownie mix
#: and tins come in slice 3, sewing machines with gen#1118. Each is a title now.
PENDING = (
    ("How to Make Brownies", "Brownie Mix", "brownies"),
    ("Learn to Sew", "Sewing Machine", "sew"),
)


def author(k: int) -> str:
    """The ``k``-th invented author: a first name and a surname, each pair used once (37 is
    prime to the 900 pairs, so ``k`` below 900 walks them without a repeat)."""
    pair = (k * 37) % (len(FIRST_NAMES) * len(SURNAMES))
    return f"{FIRST_NAMES[pair // len(SURNAMES)]} {SURNAMES[pair % len(SURNAMES)]}"


def _between(h: int, lo: int, hi: int) -> int:
    return lo + h % (hi - lo + 1)


def _prices(h: int, childrens: bool) -> tuple[float, float, float]:
    """Ebook, paperback and hardback prices, each ending .99, cheapest first."""
    if childrens:
        e, p, b = (_between(h, 1, 3), _between(h >> 5, 4, 7), _between(h >> 10, 9, 14))
    else:
        e, p, b = (_between(h, 3, 6), _between(h >> 5, 7, 12), _between(h >> 10, 14, 24))
    return (e + 0.99, p + 0.99, b + 0.99)


def rows() -> tuple[Row, ...]:
    """The department's 480 styles, leaf by leaf, each in the three :data:`FORMATS`."""
    out: list[Row] = []
    n = 0
    for li, leaf in enumerate(LEAVES):
        childrens = leaf is CHILDRENS
        for i, (title, subject) in enumerate(leaf.titles()):
            n += 1
            code = f"BOOK{n:03d}"
            h = zlib.crc32(code.encode())
            who = author(n // 2)
            brand = PUBLISHERS[(li + (i % 3) * 3) % len(PUBLISHERS)]
            band = AGE_BANDS[i % len(AGE_BANDS)] if childrens else ""
            lo, hi = AGE_PAGES[band] if childrens else leaf.pages
            pages = _between(h >> 3, lo // 4, hi // 4) * 4
            year = str(_between(h >> 7, 2015, 2026))
            attrs = (
                a("author", "Author", who), a("publisher", "Publisher", brand),
                a("genre", "Genre", leaf.genre), count("pages", "Pages", pages),
                a("publication_year", "Publication year", year),
                *((a("age_band", "Age band", band),) if childrens else ()),
            )  # fmt: skip
            prices = _prices(h, childrens)
            description = f"{leaf.blurb.format(s=subject)} Written by {who}."
            out.append(Row(
                code, title, brand, DEPARTMENT, leaf.path, PRODUCT_TYPE, prices[0], SHAPE,
                description, (COVERS[i % len(COVERS)],), attrs, tuple(zip(FORMATS, prices, strict=True)),
                colorless=True, size_key="format",
                params=(("layout", LAYOUTS[i // len(COVERS)]), ("genre", leaf.emblem)),
            ))  # fmt: skip
    return tuple(out)
