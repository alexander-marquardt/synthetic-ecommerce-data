"""The class-8 decoy :class:`Row` and the first rows of the table (:mod:`decoy_product_words`)."""

from __future__ import annotations

from dataclasses import dataclass

from synthetic_ecommerce_data.domains.retail.class_model import Style, one
from synthetic_ecommerce_data.domains.retail.decoy_rows import COLORS, Kind
from synthetic_ecommerce_data.domains.retail.decoy_word_kinds import KINDS
from synthetic_ecommerce_data.domains.retail.variants import cw


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
    target: str = ""  # the Sports & Outdoors product type whose word the title holds (gen#368)
    gift_type: str = ""  # the Gifts product type whose word the title holds (gen#425)
    device_type: str = ""  # the Electronics product type whose word the title holds (gen#332)
    seeds: tuple[str, ...] = ()  # the homepage seed phrases the title or text holds whole (gen#460)
    seed: str = ""  # the two-word seed query the title holds whole (gen#461)
    pack: str = ""  # the pack_size the title names, when it differs from the Kind's (gen#461)
    sold: int = 2000

    @property
    def shape(self) -> str:
        return KINDS[self.kind].shape

    @property
    def ptype(self) -> str:
        return KINDS[self.kind].product_type

    def _extra(self, k: Kind) -> tuple[tuple[str, str, str], ...]:
        """The Kind's extra attributes, with the row's own pack size where its title names one."""
        if not self.pack:
            return k.extra
        return tuple((a, b, self.pack if a == "pack_size" else c) for a, b, c in k.extra)

    def style(self) -> Style:
        k = KINDS[self.kind]
        params = k.params + (((self.detail_param, COLORS[self.detail]),) if self.detail else ())
        base = COLORS.get(self.color, COLORS["Grey"])
        if k.pattern == "stripe":  # the record's pattern is the one the drawing shows (gen#605)
            light = self.color in ("Cream", "White", "Yellow", "Pink", "Clear")
            color = cw(self.color, base, "stripe", COLORS["Navy" if light else "White"])
        else:
            color = cw(self.color, base)
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
            extra=self._extra(k),
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
