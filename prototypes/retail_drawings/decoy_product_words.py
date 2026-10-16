"""Class-8 text-match decoys: a title holds the shopper's product noun (gen#326).

The decoys of gen#294 and gen#311 mislead on a color, an audience, a material or a modifier. The
shopper's product word was still always right. Here it is not: "Dress for Success" black Oxford
shoes with red laces, a doll in a red dress, a sofa cover, jumper cables, black bow tie pasta. A
text search puts them beside the dresses, the sofas, the jumpers and the ties, and no text tuning
separates them, because the noun is really in the title. The category, department and color
policies read the structured fields and drop them, and :data:`TABLE` says which one each row needs.

Every decoy is a real product of its own type, with that type's normal attributes and a drawing of
the actual product (the shapes of :mod:`kit_goods` and the existing kits). The structured fields
are the truth: a title may name only a misleading color ("Sofa Cushion, Blue Trim" is cream with
blue piping;  is black shoes with red laces), and then the
drawing renders that detail (``trim`` and ``lace`` drawing params). A type this module needs and
the build lacks (shoe care, sofa covers, garment storage, cable ties, jumper cables, bike pumps,
pasta shapes ...) is a real type with a small floor of ordinary products (:data:`FLOOR`), not
only a decoy. A cross-department row sits in a root of its own (Home, Sports & Outdoors, Food &
Drink): the department policy of the All Departments persona drops it.

**Measured and dropped.** The prototype text search folds a plural only, so "dressing" does not
rank for "dress" and "coated" does not rank for "coat" here; the two food rows that rely on the
English stemmer (Red French Dressing, White Chocolate Coated Pretzels) are not counted and not
planted, as gen#326 asks. "Mushroom Caps" is not planted either: the kit has no edible mushroom
to draw.

**Blue Bull.** A class-7 color-word brand on footwear (gen#326, maintainer addition): shoes in
every color except blue, so "blue trainers", "blue shoes" and "blue boots" match the brand. It
has its own house style whose logo reads "Blue Bull".

The rows are templates: :func:`scale.derivable` leaves them out and :mod:`main_colors` neither
groups them nor completes their colors (:data:`IDS`).
"""

from __future__ import annotations

from dataclasses import dataclass

import kit_goods  # noqa: F401 -- registers the shapes below
from breadth_rows import OWNERS
from class_model import BRAND_OWNER, Style, one
from decoy_rows import COLORS, Kind
from decoy_rows import KINDS as BASE_KINDS
from variants import cw

#: The invented class-7 brand: a color word in the name of a footwear house (not a real shop).
NEW_BRANDS = ("Blue Bull",)
OWNERS.update(dict.fromkeys(NEW_BRANDS, "third_party"))
BRAND_OWNER.update(dict.fromkeys(NEW_BRANDS, "third_party"))

_BR = (("kind", "brogue"), ("material", "leather"), ("closure", "Lace-Up"))
_CARE = ("Mens", "Accessories", "Shoe Care")
_STORE = ("Home", "Storage")
_DIY = ("Home", "DIY & Car")
_SOFT = ("Home", "Soft Furnishings")
_WOMENS = (("audience", "Audience", "Womens"),)

#: Kinds this module adds (a decoy's true type), then the kinds of :mod:`decoy_rows` it reuses.
NEW_KINDS = {
    "brogue": Kind(
        "Footwear", ("Mens", "Shoes", "Brogues"), "Brogues", "shoe", "Stridewell", 54.0, params=_BR
    ),
    "polish": Kind(
        "Home",
        (*_CARE, "Shoe Polish"),
        "Shoe Polish",
        "tin",
        "Calderby & Lune",
        4.5,
        colorless=True,
    ),
    "laces": Kind(
        "Home", (*_CARE, "Shoe Laces"), "Shoe Laces", "shoe_laces", "Calderby & Lune", 2.5
    ),
    "cover": Kind(
        "Home", (*_SOFT, "Sofa Covers"), "Sofa Covers", "sofa_cover", "Hearth & Table", 34.0
    ),
    "throw": Kind("Home", (*_SOFT, "Throws"), "Throws", "throw", "Hearth & Table", 22.0),
    "carrier": Kind(
        "Home",
        (*_STORE, "Garment Storage"),
        "Garment Bags",
        "garment_bag",
        "Brackenmere Home",
        12.0,
    ),
    "hooks": Kind(
        "Home", (*_STORE, "Wall Hooks"), "Wall Hooks", "hook_rail", "Brackenmere Home", 15.0
    ),
    "stand": Kind(
        "Home",
        (*_STORE, "Hallway Stands"),
        "Hallway Stands",
        "coat_stand",
        "Brackenmere Home",
        38.0,
    ),
    "hangers": Kind(
        "Home", (*_STORE, "Hangers"), "Clothes Hangers", "hangers", "Brackenmere Home", 7.0
    ),
    "hat_box": Kind(
        "Home",
        (*_STORE, "Storage Boxes"),
        "Storage Boxes",
        "storage_box",
        "Brackenmere Home",
        14.0,
        params=(("form", "round"), ("lid", "yes")),
    ),
    "rack": Kind(
        "Home",
        ("Home", "Laundry", "Drying Racks"),
        "Drying Racks",
        "clothes_airer",
        "Brackenmere Home",
        26.0,
    ),
    "valance": Kind(
        "Home", ("Home", "Bedding", "Valances"), "Valances", "sheet", "Quillon Sleep", 18.0
    ),
    "wash_bag": Kind(
        "Home", ("Home", "Laundry", "Wash Bags"), "Wash Bags", "mesh_bag", "Brackenmere Home", 4.0
    ),
    "case": Kind(
        "Clothing",
        ("Womens", "Accessories", "Travel", "Travel Cases"),
        "Travel Cases",
        "pouch",
        "Hearth & Table",
        9.0,
        extra=_WOMENS,
    ),
    "waist": Kind(
        "Clothing",
        ("Womens", "Accessories", "Bags", "Waist Bags"),
        "Waist Bags",
        "pouch",
        "Larkmoor",
        19.0,
        extra=_WOMENS,
    ),
    "clip": Kind(
        "Clothing",
        ("Womens", "Accessories", "Keyrings", "Key Clips"),
        "Key Clips",
        "keyring",
        "Larkmoor",
        6.0,
        extra=_WOMENS,
    ),
    "beaker": Kind(
        "Home",
        ("Kids", "Baby", "Feeding", "Beakers"),
        "Baby Beakers",
        "mug",
        "Little Fernby",
        4.0,
        "kids",
    ),
    "parfum": Kind(
        "Beauty",
        ("Beauty", "Fragrance", "Eau de Parfum"),
        "Eau de Parfum",
        "fragrance",
        "Velling Apothecary",
        38.0,
    ),
    "ties": Kind(
        "Home",
        (*_DIY, "Cable Ties"),
        "Cable Ties",
        "cable_ties",
        "Brackenmere Home",
        3.5,
        units_per_pack=100,
    ),
    "jumper": Kind(
        "Home", (*_DIY, "Jump Leads"), "Jump Leads", "jumper_cables", "Brackenmere Home", 16.0
    ),
    "paint": Kind(
        "Home", (*_DIY, "Paint"), "Paint", "tin", "Brackenmere Home", 14.0, colorless=True
    ),
    "bike_pump": Kind(
        "Sports & Outdoors",
        ("Sports & Outdoors", "Cycling", "Bike Pumps"),
        "Bike Pumps",
        "pump",
        "Stridewell",
        12.0,
    ),
    "foot_pump": Kind(
        "Home", (*_DIY, "Foot Pumps"), "Foot Pumps", "pump", "Brackenmere Home", 10.0
    ),
    "pasta": Kind(
        "Food & Drink",
        ("Food & Drink", "Food Cupboard", "Pasta"),
        "Pasta",
        "box",
        "Pantry Mill",
        1.8,
        colorless=True,
    ),
    "potatoes": Kind(
        "Food & Drink",
        ("Food & Drink", "Fruit & Vegetables", "Potatoes"),
        "Potatoes",
        "tray",
        "Pantry Mill",
        2.2,
        params=(("label", "Potatoes"),),
        colorless=True,
    ),
    "crisps": Kind(
        "Food & Drink",
        ("Food & Drink", "Biscuits & Snacks", "Crisps"),
        "Crisps",
        "crisps_bag",
        "Copper Hill Preserves",
        1.2,
        colorless=True,
    ),
    "bb_trainer": Kind(
        "Footwear",
        ("Mens", "Shoes", "Trainers"),
        "Trainers",
        "shoe",
        "Blue Bull",
        42.0,
        params=(("kind", "trainer"), ("material", "canvas"), ("closure", "Lace-Up")),
    ),
    "bb_chelsea": Kind(
        "Footwear",
        ("Mens", "Shoes", "Boots", "Chelsea Boots"),
        "Chelsea Boots",
        "shoe",
        "Blue Bull",
        66.0,
        params=(("kind", "chelsea"), ("material", "leather"), ("closure", "Elastic Gusset")),
    ),
    "bb_court": Kind(
        "Footwear",
        ("Womens", "Shoes", "Heels", "Court Shoes"),
        "Court Shoes",
        "shoe",
        "Blue Bull",
        48.0,
        params=(("kind", "court"), ("material", "patent"), ("closure", "Slip-On")),
    ),
}
KINDS = {**BASE_KINDS, **NEW_KINDS}
#: The product types this module adds: each carries a floor of ordinary products (:data:`FLOOR`).


@dataclass(frozen=True)
class Row:
    """One row: a decoy (:data:`TABLE`) or an ordinary product of a type it needs."""

    code: str
    kind: str
    title: str
    desc: str
    color: str
    query: str = ""
    noun: str = ""  # the shopper's product noun the title holds ("" for a brand row)
    policy: str = ""  # category | department | color | special: <policy>
    detail: str = ""  # the color the title names for a detail the drawing renders
    detail_param: str = ""  # the drawing param that carries it (lace, trim)
    cross: bool = False  # a department other than the noun's own
    decoy: bool = True
    brand: str | None = None
    sibling: str = ""  # a special policy is proved on this sibling query
    sold: int = 2000

    @property
    def shape(self) -> str:
        return KINDS[self.kind].shape

    @property
    def ptype(self) -> str:
        return KINDS[self.kind].product_type

    def style(self) -> Style:
        k = KINDS[self.kind]
        params = k.params + (((self.detail_param, COLORS[self.detail]),) if self.detail else ())
        color = cw(self.color, COLORS.get(self.color, COLORS["Grey"]))
        return Style(
            self.code,
            self.title,
            self.brand or k.brand,
            k.department,
            k.path,
            k.price,
            self.desc,
            k.product_type,
            k.shape,
            one(color, self.sold),
            audience=k.audience,
            params=params,
            extra=k.extra,
            sizes=k.sizes,
            size_range=k.size_range,
            colorless=k.colorless,
            units_per_pack=k.units_per_pack,
            pattern=k.pattern,
            reviews=900 + self.sold if self.decoy else None,
        )


def _d(n, kind, title, desc, color, query, noun, policy, **kw) -> Row:
    return Row(f"DY{n:02d}", kind, title, desc, color, query, noun, policy, **kw)


_CAT, _DEP = "category", "department"
TABLE = (
    # -- dress: shoes, a doll, a perfume
    _d(
        1,
        "brogue",
        "Dress for Success, Red Laces",
        "Black leather Oxford shoes with red laces, polished for the office and the interview.",
        "Black",
        "red dress",
        "dress",
        _CAT,
        detail="Red",
        detail_param="lace",
    ),
    _d(
        2,
        "brogue",
        "Dress for Success Black Oxford",
        "Black leather Oxford shoes for a smart day at work.",
        "Black",
        "black dress",
        "dress",
        _CAT,
    ),
    _d(
        3,
        "doll",
        "Party Dress Doll",
        "A fashion doll in a red party dress, with four small accessories.",
        "Red",
        "red dress",
        "dress",
        _CAT,
    ),
    _d(
        4,
        "parfum",
        "Little Black Dress Parfum",
        "A warm evening eau de parfum in a black glass bottle.",
        "Black",
        "black dress",
        "dress",
        _CAT,
    ),
    # -- shoes and boots: shoe care, laces, socks
    _d(
        5,
        "polish",
        "Black Shoe Polish",
        "A black wax polish for leather shoes.",
        "Black",
        "black shoes",
        "shoe",
        _CAT,
    ),
    _d(
        6,
        "laces",
        "Red Shoe Laces",
        "Flat red laces with metal tips, one pair.",
        "Red",
        "red shoes",
        "shoe",
        _CAT,
    ),
    _d(
        7,
        "polish",
        "Black Boot Polish",
        "A black wax polish for leather boots.",
        "Black",
        "black boots",
        "boot",
        _CAT,
    ),
    _d(
        8,
        "socks_w",
        "Black Boot Socks",
        "Thick black socks to wear inside boots.",
        "Black",
        "black boots",
        "boot",
        _CAT,
    ),
    # -- trainers
    _d(
        9,
        "socks_m",
        "White Trainer Socks",
        "Five pairs of low white socks for trainers.",
        "White",
        "white trainers",
        "trainer",
        _CAT,
    ),
    _d(
        10,
        "beaker",
        "Trainer Cup, Blue",
        "A soft-spout baby beaker in blue, from six months.",
        "Blue",
        "blue trainers",
        "trainer",
        _DEP,
    ),
    _d(
        11,
        "laces",
        "White Trainer Laces",
        "Flat white laces for trainers, one pair.",
        "White",
        "white trainers",
        "trainer",
        _CAT,
    ),
    # -- coat, jacket
    _d(
        12,
        "hooks",
        "Black Coat Hooks",
        "A black wall rail with four hooks for coats.",
        "Black",
        "black coat",
        "coat",
        _CAT,
    ),
    _d(
        13,
        "stand",
        "Black Coat Stand",
        "A black metal stand with arms for coats and hats.",
        "Black",
        "black coat",
        "coat",
        _CAT,
    ),
    _d(
        14,
        "hangers",
        "Black Coat Hangers, 6 Pack",
        "Six slim black hangers for coats.",
        "Black",
        "black coat",
        "coat",
        _CAT,
    ),
    _d(
        15,
        "paint",
        "White Top Coat Paint",
        "A white gloss top coat for wood and metal.",
        "White",
        "white coat",
        "coat",
        _DEP,
        cross=True,
    ),
    _d(
        16,
        "potatoes",
        "Jacket Potatoes",
        "Four large baking potatoes for jacket potatoes.",
        "Brown",
        "jacket",
        "jacket",
        _DEP,
        cross=True,
    ),
    _d(
        17,
        "crisps",
        "Red Jacket Potato Crisps",
        "Jacket potato flavour crisps in a red bag.",
        "Red",
        "red jacket",
        "jacket",
        _DEP,
        cross=True,
    ),
    # -- jumper
    _d(
        18,
        "jumper",
        "Red Jumper Cables",
        "Red and black jump leads, three metres, with clamps.",
        "Red",
        "red jumper",
        "jumper",
        _DEP,
        cross=True,
    ),
    _d(
        19,
        "rack",
        "White Jumper Drying Rack",
        "A folding white rack that dries knitwear flat.",
        "White",
        "white jumper",
        "jumper",
        _CAT,
    ),
    # -- skirt
    _d(
        20,
        "valance",
        "White Bed Skirt",
        "A white pleated bed skirt that hides the base.",
        "White",
        "white skirt",
        "skirt",
        _CAT,
    ),
    _d(
        22,
        "hangers",
        "White Skirt Hangers, 4 Pack",
        "Four white clip hangers for skirts.",
        "White",
        "white skirt",
        "skirt",
        _CAT,
    ),
    # -- suit
    _d(
        23,
        "carrier",
        "Navy Suit Carrier",
        "A navy zipped carrier that keeps a suit uncreased.",
        "Navy",
        "navy suit",
        "suit",
        _CAT,
    ),
    _d(
        24,
        "carrier",
        "Navy Suit Cover, Breathable",
        "A navy breathable cover for one suit.",
        "Navy",
        "navy suit",
        "suit",
        _CAT,
    ),
    # -- bra
    _d(
        25,
        "wash_bag",
        "White Bra Wash Bag",
        "A white mesh bag that protects a bra in the wash.",
        "White",
        "white bra",
        "bra",
        _CAT,
    ),
    _d(
        26,
        "case",
        "White Bra Travel Case",
        "A white zipped case that keeps a bra in shape.",
        "White",
        "white bra",
        "bra",
        _CAT,
    ),
    # -- hat
    _d(
        27,
        "hat_box",
        "Pink Hat Box",
        "A round pink box with a lid for a hat.",
        "Pink",
        "pink hat",
        "hat",
        _CAT,
    ),
    _d(
        28,
        "stand",
        "Pink Hat Stand",
        "A pink metal stand with pegs for hats.",
        "Pink",
        "pink hat",
        "hat",
        _CAT,
    ),
    # -- belt
    _d(
        29,
        "waist",
        "Brown Leather Belt Bag",
        "A small brown leather bag worn on a belt.",
        "Brown",
        "brown leather belt",
        "belt",
        _CAT,
    ),
    _d(
        30,
        "clip",
        "Leather Belt Keyring, Brown",
        "A brown leather key clip for a belt loop.",
        "Brown",
        "brown leather belt",
        "belt",
        _CAT,
    ),
    # -- tie
    _d(
        31,
        "ties",
        "Black Cable Ties",
        "One hundred black nylon cable ties.",
        "Black",
        "black ties",
        "tie",
        _DEP,
        cross=True,
    ),
    _d(
        32,
        "pasta",
        "Black Bow Tie Pasta",
        "Squid ink farfalle, black bow tie pasta.",
        "Black",
        "black ties",
        "tie",
        _DEP,
        cross=True,
    ),
    _d(
        33,
        "hooks",
        "Black Tie Rack",
        "A black wall rack with hooks for ties and belts.",
        "Black",
        "black ties",
        "tie",
        _CAT,
    ),
    # -- sofa
    _d(
        34,
        "cover",
        "Blue Sofa Cover",
        "A blue stretch cover that fits a three seater sofa.",
        "Blue",
        "blue sofa",
        "sofa",
        _CAT,
    ),
    _d(
        35,
        "cushion",
        "Sofa Cushion, Blue Trim",
        "A cream scatter cushion piped in blue.",
        "Cream",
        "blue sofa",
        "sofa",
        _CAT,
        detail="Blue",
        detail_param="trim",
    ),
    _d(
        36,
        "throw",
        "Blue Sofa Throw",
        "A blue woven throw with a tassel fringe for a sofa.",
        "Blue",
        "blue sofa",
        "sofa",
        _CAT,
    ),
    # -- pumps
    _d(
        37,
        "bike_pump",
        "Black Bike Pump",
        "A black hand pump for bike tyres.",
        "Black",
        "black pumps",
        "pump",
        _DEP,
        cross=True,
    ),
    _d(
        38,
        "foot_pump",
        "Black Foot Pump",
        "A black foot pump for airbeds and tyres.",
        "Black",
        "black pumps",
        "pump",
        _DEP,
        cross=True,
    ),
    # -- food rows whose noun is its own token
    _d(
        39,
        "pasta",
        "Black Shoe String Pasta",
        "Squid ink pasta cut in thin shoe string ribbons.",
        "Black",
        "black shoes",
        "shoe",
        _DEP,
        cross=True,
    ),
    # -- Blue Bull: a color-word brand on footwear, every color but blue (class 7)
    _d(
        40,
        "bb_trainer",
        "Blue Bull Trainers",
        "White canvas lace-up trainers by Blue Bull.",
        "White",
        "blue trainers",
        "",
        "color",
        brand="Blue Bull",
    ),
    _d(
        41,
        "bb_chelsea",
        "Blue Bull Chelsea Boots",
        "Black leather Chelsea boots by Blue Bull.",
        "Black",
        "blue boots",
        "",
        "color",
        brand="Blue Bull",
    ),
    _d(
        42,
        "bb_court",
        "Blue Bull Court Shoes",
        "Red patent court shoes by Blue Bull.",
        "Red",
        "blue shoes",
        "",
        "color",
        brand="Blue Bull",
    ),
)

#: kind -> the ordinary products of the type: (title, color, description).
_F = {
    "polish": (
        ("Neutral Wax Polish", "Cream", "A neutral wax polish for any leather."),
        ("Brown Leather Cream", "Brown", "A nourishing cream in brown."),
        ("Quick Shine Sponge", "Black", "A black sponge that shines in seconds."),
    ),
    "laces": (
        ("Waxed Round Laces", "Brown", "Round waxed laces for boots."),
        ("Flat Cotton Laces", "White", "Flat cotton laces in white."),
        ("Reflective Laces", "Grey", "Grey laces that catch the light."),
    ),
    "cover": (
        ("Stretch Sofa Cover, Grey", "Grey", "A grey stretch cover for a sofa."),
        ("Quilted Sofa Cover", "Cream", "A quilted cream cover for a sofa."),
        ("Two Seater Sofa Cover", "Navy", "A navy cover for a two seater."),
    ),
    "throw": (
        ("Chunky Knit Throw", "Cream", "A thick cream knitted throw."),
        ("Fleece Throw", "Grey", "A soft grey fleece throw."),
        ("Velvet Throw", "Green", "A green velvet throw."),
    ),
    "carrier": (
        ("Travel Garment Bag", "Black", "A black bag that folds for travel."),
        ("Breathable Garment Cover", "White", "A white cover that lets cloth breathe."),
        ("Long Garment Bag", "Grey", "A long grey bag with a hanging hook."),
    ),
    "hooks": (
        ("Oak Hook Rail", "Brown", "An oak rail with four hooks."),
        ("Brass Hook Rail", "Gold", "A rail with four brass hooks."),
        ("Hallway Hook Rail", "White", "A white hallway rail."),
    ),
    "stand": (
        ("Oak Hallway Stand", "Brown", "A tall oak stand for the hall."),
        ("Tripod Hallway Stand", "Grey", "A grey metal tripod stand."),
        ("Bentwood Stand", "Black", "A black bentwood stand."),
    ),
    "hangers": (
        ("Wooden Hangers, Pack of 6", "Brown", "Six smooth wooden hangers."),
        ("Velvet Hangers, Pack of 10", "Grey", "Ten slim non-slip hangers."),
        ("Space Saving Hangers", "White", "Slim white hangers, pack of 20."),
    ),
    "hat_box": (
        ("Round Gift Box, Large", "Cream", "A large round box with a lid."),
        ("Round Storage Box", "Grey", "A grey round box with a lid."),
        ("Round Keepsake Box", "Pink", "A small pink round box."),
    ),
    "rack": (
        ("Folding Airer", "White", "A white folding airer."),
        ("Tiered Drying Rack", "Grey", "A grey tiered rack."),
        ("Wing Airer", "Grey", "A grey airer with wings."),
    ),
    "valance": (
        ("Pleated Valance", "Cream", "A cream pleated valance sheet."),
        ("Platform Valance", "Grey", "A grey valance for a divan."),
        ("Frilled Valance", "Navy", "A navy frilled valance."),
    ),
    "wash_bag": (
        ("Mesh Wash Bag, Large", "White", "A large white mesh wash bag."),
        ("Delicates Wash Bag", "Grey", "A grey bag for delicates."),
        ("Zipped Wash Bags, Pack of 3", "White", "Three zipped wash bags."),
    ),
    "case": (
        ("Cosmetic Travel Case", "Pink", "A pink zipped cosmetic case."),
        ("Passport Travel Pouch", "Navy", "A navy pouch for travel papers."),
        ("Zip Travel Organiser", "Grey", "A grey organiser for a bag."),
    ),
    "waist": (
        ("Running Waist Pack", "Black", "A black pack worn at the waist."),
        ("Festival Waist Bag", "Green", "A green zipped waist bag."),
        ("Canvas Waist Bag", "Cream", "A cream canvas waist bag."),
    ),
    "clip": (
        ("Brass Key Clip", "Gold", "A brass clip for keys."),
        ("Leather Key Clip", "Black", "A black leather key clip."),
        ("Carabiner Key Clip", "Grey", "A grey carabiner for keys."),
    ),
    "beaker": (
        ("Soft Spout Beaker", "Pink", "A pink soft-spout beaker."),
        ("Weaning Beaker", "Green", "A green beaker with two handles."),
        ("Free Flow Beaker", "Navy", "A navy free-flow beaker."),
    ),
    "ties": (
        ("Heavy Duty Cable Ties", "White", "Two hundred strong white ties."),
        ("Assorted Cable Ties", "Grey", "Three sizes of grey ties."),
        ("Releasable Cable Ties", "Cream", "Reusable cream ties, pack of 50."),
    ),
    "jumper": (
        ("Compact Jump Leads", "Red", "Short red leads for small engines."),
        ("Heavy Duty Jump Leads", "Black", "Black leads for large engines."),
        ("Long Jump Leads, 5m", "Red", "Five metre red leads."),
    ),
    "paint": (
        ("Matt Emulsion, White", "White", "A white matt emulsion."),
        ("Satin Wood Paint", "Cream", "A cream satin paint for wood."),
        ("Masonry Paint", "Grey", "A grey paint for outside walls."),
    ),
    "bike_pump": (
        ("Floor Pump with Gauge", "Red", "A red floor pump with a gauge."),
        ("Mini Frame Pump", "Black", "A black pump that fits a frame."),
        ("Track Pump", "Grey", "A grey track pump."),
    ),
    "foot_pump": (
        ("Airbed Foot Pump", "Grey", "A grey pump for airbeds."),
        ("Double Barrel Foot Pump", "Red", "A red double barrel pump."),
        ("Compact Foot Pump", "Blue", "A blue folding foot pump."),
    ),
    "pasta": (
        ("Penne Pasta", "Cream", "Penne rigate, cooks in ten minutes."),
        ("Fusilli Pasta", "Cream", "Twists of durum pasta."),
        ("Spaghetti", "Cream", "Long durum wheat spaghetti."),
    ),
    "potatoes": (
        ("Baking Potatoes", "Brown", "Large potatoes for baking."),
        ("New Potatoes", "Cream", "Small waxy new potatoes."),
        ("Maris Piper Potatoes", "Brown", "Floury potatoes for chips."),
    ),
    "crisps": (
        ("Ready Salted Crisps", "Gold", "Ready salted crisps."),
        ("Cheese and Onion Crisps", "Green", "Cheese and onion crisps."),
        ("Sea Salt Crisps", "Blue", "Sea salt crisps."),
    ),
}
FLOOR = tuple(
    Row(f"FY{n:02d}{i}", kind, title, desc, color, decoy=False, sold=120)
    for n, (kind, rows) in enumerate(_F.items(), 1)
    for i, (title, color, desc) in enumerate(rows)
)
NEW_TYPES = tuple(sorted({KINDS[k].product_type for k in _F}))
ROWS = (*TABLE, *FLOOR)
#: The decoys whose title names a detail color that is not their color: left out of the standard's
#: text-agrees check (a title and a color field that disagree are the point of the row).
TEXT_EXEMPT = frozenset(f"PLT-{r.code}" for r in TABLE if r.detail)
STYLES = tuple(r.style() for r in ROWS)
#: The product ids left out of the derivation and of the color completion.
IDS = frozenset(f"PLT-{s.code}" for s in STYLES)
#: product id -> its row (decoy or floor).
BY_ID = {f"PLT-{r.code}": r for r in ROWS}


def docs() -> list[dict]:
    """Every row's catalog document, decoys then floor."""
    return [s.doc() for s in STYLES]


def table_markdown() -> str:
    """The docs table: one line per decoy with its query, noun, product id, title and policy."""
    lines = [
        "| Query | Noun | Product id | Title | True type | Fixing policy |",
        "|---|---|---|---|---|---|",
    ]
    for r in TABLE:
        lines.append(
            f"| {r.query} | {r.noun or 'brand'} | PLT-{r.code} | {r.title} | {r.ptype} "
            f"| {r.policy} |"
        )
    return "\n".join(lines)
