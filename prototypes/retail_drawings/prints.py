"""The print range: plain and motif-print styles per product line (gen#125).

A :class:`Line` is one product line (women's tees, kids' pyjamas, mugs, ...):
its plain styles and its print styles. A :class:`Print` is one style: one
motif (:mod:`motifs`) laid out one way, sold on one or more grounds; each
ground is a SKU color, so the SKU ``color`` is the ground and the swatch its
hex. A print's doc carries ``pattern: "print"`` and the attributes ``motif``
and ``print_placement``; its drawing carries the motif, placement, scale and
spacing the tile is drawn from.

Two rules, both checked: one style per motif in a line (:func:`style_key`,
:func:`check_range`: another ground of the same motif is a SKU, never a second
style), and no category path more than :data:`MAX_PRINT_SHARE` prints over
the whole catalog (:func:`check_share`, run on :func:`distractors.corpus`).
Every name is invented. Standard library only.
"""

# ruff: noqa: E501 -- data rows read better whole (prototype only).

from __future__ import annotations

import functools
from collections import Counter
from dataclasses import dataclass

import motifs
from class_model import Style, _digest
from kit import Fill
from variants import Color, cw

#: The most of one category path that may be prints: a range is mostly plain.
MAX_PRINT_SHARE = 0.25

WHITE, NAVY, GREY, BLACK, SAGE = "#ffffff", "#26365c", "#b9bec4", "#2a2a2e", "#9bb08f"
CREAM, STONE, PINK, KHAKI, OAT = "#f3ead8", "#d9d0c1", "#f3c6cf", "#8a8456", "#e6dccb"
ORANGE, LEMON, STEEL, GREEN = "#f28c28", "#f2d14b", "#8e9aa6", "#5f9a4a"

ADULT_SIZES = ("XS", "S", "M", "L", "XL")
KIDS_SIZES = ("3-4 Yrs", "5-6 Yrs", "7-8 Yrs", "9-10 Yrs")


@dataclass(frozen=True)
class Print:
    """One print style: ``motif`` in ``ink`` on each of ``grounds`` (its SKU colors).

    ``count`` is the copies of the motif one repeat draws (:data:`kit.MOTIF_COUNTS`):
    1 for a placement graphic, 2 for the all-over half-drop, 3 to 6 for a scatter. It
    drives the drawing, the ``motif_count`` attribute and the title's number
    (:func:`title`), so there is no title field to disagree with it."""

    motif: str
    placement: str
    ink: str
    grounds: tuple[tuple[str, str], ...]  # (color name, hex)
    scale: float = motifs.LARGE_SCALE
    spacing: float = 0
    count: int = 1
    description: str | None = None
    #: A product id kept from an earlier round (a planted distractor's).
    code: str | None = None


@dataclass(frozen=True)
class Line:
    code: str
    group: str  # an :data:`motifs.ALLOW` product group
    audience: str  # women, men, kids or adult, as :data:`motifs.ALLOW` keys it
    range_: str  # core, novelty or gift
    shape: str
    noun: str
    brand: str
    department: str
    path: tuple[str, ...]
    price: float
    plains: tuple[tuple[str, Color, str], ...]  # (title, color, description)
    prints: tuple[Print, ...]
    sizes: tuple[str, ...] = ()
    #: Words a print's title ends with after the noun (", Set of 2").
    title_suffix: str = ""

    @property
    def style_audience(self) -> str:
        return "kids" if self.audience == "kids" else "adult"


def style_key(line: Line, p: Print) -> tuple[str, str]:
    """What makes a print a style of its own: its line and its motif. The placement and
    the grounds are not in it: one motif is one style, its grounds are SKUs."""
    return (line.code, p.motif)


def _code(line: Line, p: Print) -> str:
    return p.code or "-".join(style_key(line, p)).upper().replace("_", "")


def check_range(lines: tuple[Line, ...] | None = None) -> None:
    """ValueError naming every print that repeats a motif in its line, that its line's
    range may not print, or that its surface cannot take."""
    problems = []
    seen: set[tuple[str, str]] = set()
    for line in LINES if lines is None else lines:
        for p in line.prints:
            key = style_key(line, p)
            if key in seen:
                problems.append(f"{line.code}: {p.motif!r} twice: one style per motif")
            seen.add(key)
            if not motifs.allowed(line.group, line.audience, line.range_, p.motif):
                problems.append(f"{line.code}: a {line.range_} {line.audience} {line.group} "
                                f"range may not print {p.motif!r}")  # fmt: skip
            try:
                motifs.check_surface(line.shape, p.placement)
                Fill("print", motif=p.motif, placement=p.placement, scale=p.scale,
                     spacing=p.spacing, count=p.count)  # fmt: skip
            except ValueError as e:
                problems.append(f"{line.code}: {e}")
    if problems:
        raise ValueError("refused prints:\n" + "\n".join(problems))


def _sold(code: str) -> int:
    return 20 + _digest(code) % 180


def title(line: Line, p: Print) -> str:
    """The print's title. Its noun is singular iff one copy is drawn (maintainer ruling):
    "Wrench Graphic Tee" for a placement graphic, "Wrenches Print Tee" for a repeat."""
    m = motifs.motif(p.motif)
    noun, kind = (m.label, "Graphic") if p.count == 1 else (m.plural, "Print")
    kids = "Kids' " if line.audience == "kids" else ""
    return f"{kids}{noun} {kind} {line.noun}{line.title_suffix}"


def _print_style(line: Line, p: Print) -> Style:
    m = motifs.motif(p.motif)
    code = _code(line, p)
    description = p.description or (
        f"Our {m.label.lower()} graphic {line.noun.lower()}: one large {m.label.lower()} on the front."
        if p.count == 1
        else f"Our {m.plural.lower()} print {line.noun.lower()}: {m.plural.lower()} "
        f"{'all over' if p.placement == 'all-over' else 'scattered'} on a soft ground."
    )
    colors = tuple((cw(name, hex_, "print", p.ink), _sold(code + name)) for name, hex_ in p.grounds)
    return Style(
        code, title(line, p), line.brand, line.department, line.path, line.price, description,
        line.noun, line.shape, colors, audience=line.style_audience, pattern="print",
        sizes=line.sizes,
        extra=(("motif", "Motif", m.label), ("motif_count", "Motif count", str(p.count)),
               ("print_placement", "Print placement", p.placement)),
        motif_print=(("motif", p.motif), ("placement", p.placement), ("scale", p.scale),
                     ("spacing", p.spacing), ("count", p.count)),
    )  # fmt: skip


def styles(lines: tuple[Line, ...] | None = None) -> list[Style]:
    """Every style of the range, line by line: its plains, then its prints."""
    lines = LINES if lines is None else lines
    check_range(lines)
    out = []
    for line in lines:
        for n, (title, color, description) in enumerate(line.plains, 1):
            code = f"{line.code}{n}"
            out.append(Style(
                code, title, line.brand, line.department, line.path, line.price, description,
                line.noun, line.shape, ((color, _sold(code)),), audience=line.style_audience,
                pattern="plain", sizes=line.sizes,
            ))  # fmt: skip
        out += [_print_style(line, p) for p in line.prints]
    return out


@functools.cache
def _docs() -> tuple[dict, ...]:
    return tuple(s.doc() for s in styles())


def docs() -> list[dict]:
    """The range's documents (the same objects on every call, so a planted row shares them)."""
    return list(_docs())


def doc(product_id: str) -> dict:
    found = [d for d in _docs() if d["product_id"] == product_id]
    if len(found) != 1:
        raise ValueError(f"{product_id}: not one product of the print range")
    return found[0]


def is_print(d: dict) -> bool:
    return d.get("pattern") == "print" or d["drawing"].get("pattern") == "print"


def print_share(catalog: list[dict]) -> dict[tuple[str, ...], float]:
    """Category path -> the share of its products that are prints."""
    every = Counter(tuple(d["category_path"]) for d in catalog)
    printed = Counter(tuple(d["category_path"]) for d in catalog if is_print(d))
    return {path: printed[path] / n for path, n in every.items()}


def check_share(catalog: list[dict]) -> None:
    """ValueError naming every category path above :data:`MAX_PRINT_SHARE` prints."""
    over = [
        f"{' > '.join(path)}: {share:.0%} prints, above {MAX_PRINT_SHARE:.0%}"
        for path, share in print_share(catalog).items()
        if share > MAX_PRINT_SHARE
    ]
    if over:
        raise ValueError("too many prints:\n" + "\n".join(over))


def _all_over(motif: str, ink: str, grounds, **kw) -> Print:
    return Print(motif, "all-over", ink, grounds, scale=0.1, spacing=96, count=2, **kw)


def _scatter(motif: str, ink: str, grounds, count: int, **kw) -> Print:
    return Print(motif, "scatter", ink, grounds, scale=0.12, spacing=140, count=count, **kw)


def _plains(*rows: tuple[str, str, str, str]) -> tuple[tuple[str, Color, str], ...]:
    """(title, color name, hex, description) rows as a line's plain styles."""
    return tuple((t, cw(name, hex_), d) for t, name, hex_, d in rows)


TEE = "A soft cotton jersey tee with a ribbed crew neck."
KIDS_TEE = "A soft cotton tee for kids, with a tag-free neck."

LINES: tuple[Line, ...] = (
    Line("TEEW", "tops", "women", "core", "tshirt", "Tee", "Larkmoor", "Clothing",
         ("Women", "Tops", "T-Shirts"), 14.0, (
             ("Cotton Crew Neck Tee", cw("White", WHITE), TEE),
             ("Relaxed Boxy Tee", cw("Black", BLACK), "A dropped-shoulder boxy tee in heavy cotton."),
             ("Slim Fit Ribbed Tee", cw("Navy", NAVY), "A close-fitting rib tee that layers well."),
             ("Linen Blend Tee", cw("Stone", STONE), "A breezy linen blend tee for warm days."),
             ("Lemon Crew Neck Tee", cw("Lemon", LEMON),
              "Our crew neck tee in lemon: a sunny lemon yellow. A lemon tee for summer."),
             ("Bright Orange Crew Neck Tee", cw("Bright Orange", ORANGE),
              "Our crew neck tee in bright orange: a zesty orange that pops. Orange is the color."),
         ), (
             Print("orange", "placement", ORANGE, (("White", WHITE), ("Navy", NAVY)),
                   description="One big orange on the front: an orange graphic tee, orange on white."),
             Print("lemon", "placement", LEMON, (("Navy", NAVY),),
                   description="A large lemon graphic on a navy tee."),
         ), ADULT_SIZES),
    Line("TEEM", "tops", "men", "novelty", "tshirt", "Tee", "Wrenfield", "Clothing",
         ("Men", "Tops", "T-Shirts"), 16.0, (
             ("Essential Crew Neck Tee", cw("White", WHITE), TEE),
             ("Heavyweight Tee", cw("Black", BLACK), "A thick cotton tee that keeps its shape."),
             ("Pocket Tee", cw("Grey", GREY), "A crew neck tee with a chest pocket."),
             ("Henley Tee", cw("Navy", NAVY), "A three-button henley in slub cotton."),
             ("Longline Tee", cw("Khaki", KHAKI), "A longer cut tee with a curved hem."),
             ("Muscle Fit Tee", cw("Charcoal", "#4a4d52"), "A muscle fit tee in stretch cotton."),
             *_plains(
                 ("Organic Cotton Tee", "Olive", "#6b7046", "An everyday tee in organic cotton."),
                 ("Raglan Tee", "Grey", GREY, "A raglan sleeve tee in soft marl jersey."),
                 ("Waffle Knit Tee", "Oat", OAT, "A waffle-textured tee with a relaxed fit."),
                 ("Garment Dyed Tee", "Sage", SAGE, "A garment dyed tee with a lived-in feel."),
                 ("Slub Cotton Tee", "Stone", STONE, "A slub jersey tee with a soft drape."),
                 ("Ringer Tee", "White", WHITE, "A retro ringer tee with contrast cuffs."),
                 ("Oversized Tee", "Black", BLACK, "A roomy tee with dropped shoulders."),
                 ("Performance Tee", "Navy", NAVY, "A quick-dry tee for the gym."),
                 ("Mercerised Cotton Tee", "Charcoal", "#4a4d52", "A smooth tee with a subtle sheen."),
             ),
         ), (
             Print("hammer", "placement", STEEL, (("Grey", GREY),),
                   description="A big claw hammer graphic: the tee for the weekend fixer."),
             Print("drill", "placement", ORANGE, (("Black", BLACK),),
                   description="A large cordless drill graphic on a black tee."),
             Print("wrench", "placement", STEEL, (("Navy", NAVY),),
                   description="One big spanner graphic on a navy tee: the wrench, front and centre."),
             Print("screw", "placement", STEEL, (("White", WHITE),),
                   description="A single oversized screw graphic on a white tee."),
             Print("screwdriver", "placement", ORANGE, (("Grey", GREY),),
                   description="A large screwdriver graphic on a grey tee."),
         ), ADULT_SIZES),
    Line("TEEMP", "tops", "men", "novelty", "tshirt", "Tee", "Wrenfield", "Clothing",
         ("Men", "Tops", "T-Shirts"), 18.0, _plains(
             ("Washed Pocket Tee", "Khaki", KHAKI, "A washed tee with a chest pocket."),
             ("Tipped Tee", "Navy", NAVY, "A tee with tipped sleeve cuffs."),
             ("Breton Stripe Tee", "White", WHITE, "A striped tee in heavy cotton."),
             ("Brushed Cotton Tee", "Grey", GREY, "A brushed cotton tee for cool days."),
             ("Boxy Heavyweight Tee", "Black", BLACK, "A boxy tee in thick cotton jersey."),
             ("Linen Cotton Tee", "Stone", STONE, "A breezy linen and cotton tee."),
         ), (
             _scatter("wrench", STEEL, (("Navy", NAVY), ("Grey", GREY)), 4,
                      description="Wrenches scattered all over: a wrenches print tee for the toolbox crowd."),
             _scatter("screw", STEEL, (("Black", BLACK),), 5,
                      description="Screws scattered on a black tee: a screws print for the workshop."),
         ), ADULT_SIZES),
    Line("SWM", "sweatshirts", "men", "novelty", "sweatshirt", "Sweatshirt", "Wrenfield", "Clothing",
         ("Men", "Tops", "Sweatshirts"), 30.0, _plains(
             ("Loopback Sweatshirt", "Grey", GREY, "A loopback cotton sweatshirt."),
             ("Raglan Sweatshirt", "Navy", NAVY, "A raglan sweatshirt with ribbed cuffs."),
             ("Brushed Fleece Sweatshirt", "Charcoal", "#4a4d52", "A brushed-back fleece sweatshirt."),
             ("Half Zip Sweatshirt", "Black", BLACK, "A half-zip sweatshirt with a stand collar."),
             ("Waffle Sweatshirt", "Oat", OAT, "A waffle-knit sweatshirt."),
             ("Garment Dyed Sweatshirt", "Sage", SAGE, "A garment dyed sweatshirt, softly faded."),
             ("Heavyweight Sweatshirt", "Khaki", KHAKI, "A heavyweight sweatshirt in thick jersey."),
             ("Oversized Sweatshirt", "Stone", STONE, "A roomy sweatshirt with dropped shoulders."),
             ("Pocket Sweatshirt", "White", WHITE, "A sweatshirt with a kangaroo pocket."),
         ), (
             _all_over("hammer", STEEL, (("Navy", NAVY),),
                       description="Hammers all over a navy sweatshirt: a hammers print for DIY days."),
             _scatter("drill", ORANGE, (("Grey", GREY),), 3,
                      description="Three cordless drills scattered on a grey sweatshirt: drills print."),
             _scatter("screwdriver", ORANGE, (("Black", BLACK),), 6,
                      description="Screwdrivers scattered on a black sweatshirt: a screwdrivers print."),
         ), ADULT_SIZES),
    Line("TEEK", "tops", "kids", "core", "tshirt", "Tee", "Little Fernby", "Clothing",
         ("Kids", "Tops", "T-Shirts"), 8.0, (
             ("Kids' Crew Neck Tee", cw("White", WHITE), KIDS_TEE),
             ("Kids' Ringer Tee", cw("Navy", NAVY), "A kids' tee with a contrast neck and cuffs."),
             ("Kids' Pocket Tee", cw("Pink", PINK), "A kids' tee with a patch pocket."),
         ), (
             Print("dinosaur", "placement", GREEN, (("Sage", SAGE), ("White", WHITE)),
                   description="A big dinosaur on the front: a roaring dinosaur tee for dinosaur fans."),
         ), KIDS_SIZES),
    Line("PJK", "nightwear", "kids", "core", "pyjamas", "Pyjamas", "Little Fernby",
         "Lingerie & Nightwear", ("Kids", "Nightwear", "Pyjamas"), 12.0, (
             ("Kids' Cotton Pyjamas", cw("Navy", NAVY), "A long-sleeve top and bottoms in soft cotton."),
             ("Kids' Short Pyjamas", cw("Pink", PINK), "A short-sleeve top and shorts for summer."),
             ("Kids' Waffle Pyjamas", cw("Oat", OAT), "Cosy waffle-knit pyjamas with cuffed legs."),
         ), (
             _all_over("dinosaur", GREEN, (("Navy", NAVY),),
                       description="Dinosaur pyjamas: dinosaurs all over, a dinosaur bedtime."),
         ), KIDS_SIZES),
    Line("SWK", "sweatshirts", "kids", "core", "sweatshirt", "Sweatshirt", "Little Fernby",
         "Clothing", ("Kids", "Tops", "Sweatshirts"), 14.0, (
             ("Kids' Crew Sweatshirt", cw("Grey", GREY), "A brushed-back crew sweatshirt."),
             ("Kids' Zip Sweatshirt", cw("Navy", NAVY), "A half-zip sweatshirt with a stand collar."),
             ("Kids' Fleece Sweatshirt", cw("Cream", CREAM), "A soft fleece sweatshirt."),
         ), (
             Print("dinosaur", "placement", GREEN, (("Grey", GREY),),
                   description="A dinosaur sweatshirt with one big dinosaur on the front."),
         ), KIDS_SIZES),
    Line("DRS", "dresses", "women", "core", "dress", "Tea Dress", "Larkmoor", "Clothing",
         ("Women", "Dresses", "Tea Dresses"), 38.0, (
             ("Plain Tea Dress", cw("Navy", NAVY), "A floaty tea dress with a tie waist."),
             ("Midi Tea Dress", cw("Sage", SAGE), "A midi tea dress with flutter sleeves."),
             ("Button Front Tea Dress", cw("Cream", CREAM), "A button front tea dress in crepe."),
         ), (
             _all_over("lemon", LEMON, (("White", WHITE),), code="LEMDRS",
                       description="A floaty tea dress in our lemon print: yellow lemons and green "
                       "leaves on white. The lemon print is back for summer."),
         ), ADULT_SIZES),
    Line("BEDK", "bedding", "kids", "core", "duvet", "Duvet Set", "Little Fernby", "Home",
         ("Home", "Bedding", "Kids' Bedding"), 20.0, (
             ("Kids' Cotton Bedding Set", cw("White", WHITE), "A single cover and pillowcase in cotton."),
             ("Kids' Brushed Cotton Bedding Set", cw("Pink", PINK), "Brushed cotton for cold nights."),
             ("Kids' Seersucker Bedding Set", cw("Navy", NAVY), "A puckered seersucker set."),
         ), (
             _all_over("dinosaur", GREEN, (("White", WHITE),), code="DUVKID",
                       description="A printed single duvet set for kids: a duvet cover and "
                       "pillowcase. Duvet sold separately."),
         )),
    Line("DUVA", "bedding", "adult", "core", "duvet", "Duvet Cover", "Brackenmere Home", "Home",
         ("Home", "Bedding", "Duvet Covers"), 28.0, (
             ("Washed Linen Bed Cover", cw("Oat", OAT), "A washed linen cover, soft from the first night."),
         ), (
             _all_over("lemon", LEMON, (("White", WHITE),),
                       description="A lemon print cover: lemons and leaves on white. Lemon "
                       "bedding for a fresh lemon bedroom."),
         )),
    Line("TTW", "kitchen textiles", "adult", "core", "tea_towel", "Tea Towels", "Brackenmere Home",
         "Home", ("Home", "Kitchen & Dining", "Tea Towels"), 9.0, (
             ("Cotton Tea Towels, Set of 2", cw("White", WHITE), "Absorbent cotton tea towels."),
             ("Linen Tea Towels, Set of 2", cw("Stone", STONE), "Lint-free linen tea towels."),
             ("Waffle Tea Towels, Set of 2", cw("Grey", GREY), "Quick-drying waffle tea towels."),
             *_plains(
                 ("Striped Tea Towels, Set of 2", "Navy", NAVY, "Woven striped cotton tea towels."),
                 ("Herringbone Tea Towels, Set of 2", "Oat", OAT, "Herringbone weave tea towels."),
                 ("Recycled Cotton Tea Towels, Set of 2", "Sage", SAGE, "Tea towels in recycled cotton."),
                 ("Terry Tea Towels, Set of 2", "White", WHITE, "Thirsty terry loop tea towels."),
                 ("Chambray Tea Towels, Set of 2", "Stone", STONE, "Soft chambray tea towels."),
                 ("Ribbed Tea Towels, Set of 2", "Charcoal", "#4a4d52", "Ribbed cotton tea towels."),
                 ("Glass Cloths, Set of 2", "White", WHITE, "Lint-free cloths for glasses."),
                 ("Bamboo Tea Towels, Set of 2", "Khaki", KHAKI, "Tea towels in bamboo and cotton."),
                 ("Hemp Tea Towels, Set of 2", "Oat", OAT, "Hard-wearing hemp tea towels."),
             ),
         ), (
             _scatter("orange", ORANGE, (("Cream", CREAM),), 3,
                      description="Orange print tea towels: oranges scattered on cream. Orange "
                      "for the kitchen."),
             _scatter("apple", "#c8312f", (("White", WHITE),), 4,
                      description="Red apples scattered on white tea towels."),
             _scatter("strawberry", "#d9363e", (("Stone", STONE),), 5,
                      description="Strawberries scattered on stone tea towels, a summer kitchen."),
             _scatter("cherries", "#a3162b", (("White", WHITE), ("Navy", NAVY)), 6,
                      description="Cherries scattered on cotton tea towels."),
         ), title_suffix=", Set of 2"),
    Line("MUG", "mugs", "adult", "core", "mug", "Mug", "Brackenmere Home", "Home",
         ("Home", "Kitchen & Dining", "Drinkware", "Mugs"), 8.0, (
             ("Stoneware Mug", cw("White", WHITE), "A chunky stoneware mug, dishwasher safe."),
             ("Speckled Mug", cw("Oat", OAT), "A speckled glaze mug that holds 350ml."),
             ("Tall Latte Mug", cw("Navy", NAVY), "A tall mug for lattes."),
             *_plains(
                 ("Enamel Mug", "White", WHITE, "A camping style enamel mug with a steel rim."),
                 ("Reactive Glaze Mug", "Sage", SAGE, "A mug with a pooling reactive glaze."),
                 ("Ribbed Mug", "Stone", STONE, "A ribbed stoneware mug."),
                 ("Espresso Cup", "Black", BLACK, "A small cup for a strong espresso."),
                 ("Footed Mug", "Grey", GREY, "A mug on a small foot, 300ml."),
                 ("Matte Mug", "Charcoal", "#4a4d52", "A matte stoneware mug."),
                 ("Porcelain Mug", "White", WHITE, "A fine porcelain mug."),
                 ("Travel Mug", "Navy", NAVY, "A lidded travel mug that keeps drinks hot."),
                 ("Jumbo Mug", "Oat", OAT, "A jumbo mug that holds 500ml."),
             ),
         ), (
             Print("orange", "placement", ORANGE, (("White", WHITE),),
                   description="A mug with one big orange: orange on white, an orange mug."),
             Print("apple", "placement", "#c8312f", (("White", WHITE),),
                   description="One big red apple on a white mug."),
             Print("strawberry", "placement", "#d9363e", (("White", WHITE),),
                   description="A large strawberry graphic on a white mug."),
             Print("cherries", "placement", "#a3162b", (("Stone", STONE),),
                   description="A big pair of cherries on a stone mug."),
         )),
)  # fmt: skip
