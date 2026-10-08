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
    """One print style: ``motif`` in ``ink`` on each of ``grounds`` (its SKU colors)."""

    motif: str
    placement: str
    ink: str
    grounds: tuple[tuple[str, str], ...]  # (color name, hex)
    scale: float = motifs.LARGE_SCALE
    spacing: float = 0
    title: str | None = None
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
            except ValueError as e:
                problems.append(f"{line.code}: {e}")
    if problems:
        raise ValueError("refused prints:\n" + "\n".join(problems))


def _sold(code: str) -> int:
    return 20 + _digest(code) % 180


def _print_style(line: Line, p: Print) -> Style:
    label = motifs.motif(p.motif).label
    code = _code(line, p)
    title = p.title or f"{label} Print {line.noun}"
    description = p.description or (
        f"Our {label.lower()} print {line.noun.lower()}: {label.lower()} motifs on a soft ground."
    )
    colors = tuple((cw(name, hex_, "print", p.ink), _sold(code + name)) for name, hex_ in p.grounds)
    return Style(
        code, title, line.brand, line.department, line.path, line.price, description, line.noun,
        line.shape, colors, audience=line.style_audience, pattern="print", sizes=line.sizes,
        extra=(("motif", "Motif", label), ("print_placement", "Print placement", p.placement)),
        motif_print=(("motif", p.motif), ("placement", p.placement), ("scale", p.scale),
                     ("spacing", p.spacing)),
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
    return Print(motif, "all-over", ink, grounds, scale=0.1, spacing=96, **kw)


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
                   title="Orange Graphic Tee",
                   description="One big orange on the front: an orange graphic tee, orange on white."),
             Print("lemon", "placement", LEMON, (("Navy", NAVY),), title="Lemon Graphic Tee",
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
         ), (
             Print("hammer", "placement", STEEL, (("Grey", GREY),), title="Hammer Graphic Tee",
                   description="A big claw hammer graphic: the tee for the weekend fixer."),
             Print("drill", "placement", ORANGE, (("Black", BLACK),), title="Power Drill Graphic Tee",
                   description="A large cordless drill graphic on a black tee."),
         ), ADULT_SIZES),
    Line("TEEK", "tops", "kids", "core", "tshirt", "Tee", "Little Fernby", "Clothing",
         ("Kids", "Tops", "T-Shirts"), 8.0, (
             ("Kids' Crew Neck Tee", cw("White", WHITE), KIDS_TEE),
             ("Kids' Ringer Tee", cw("Navy", NAVY), "A kids' tee with a contrast neck and cuffs."),
             ("Kids' Pocket Tee", cw("Pink", PINK), "A kids' tee with a patch pocket."),
         ), (
             Print("dinosaur", "placement", GREEN, (("Sage", SAGE), ("White", WHITE)),
                   title="Kids' Dinosaur Tee",
                   description="A big dinosaur on the front: a roaring dinosaur tee for dinosaur fans."),
         ), KIDS_SIZES),
    Line("PJK", "nightwear", "kids", "core", "pyjamas", "Pyjamas", "Little Fernby",
         "Lingerie & Nightwear", ("Kids", "Nightwear", "Pyjamas"), 12.0, (
             ("Kids' Cotton Pyjamas", cw("Navy", NAVY), "A long-sleeve top and bottoms in soft cotton."),
             ("Kids' Short Pyjamas", cw("Pink", PINK), "A short-sleeve top and shorts for summer."),
             ("Kids' Waffle Pyjamas", cw("Oat", OAT), "Cosy waffle-knit pyjamas with cuffed legs."),
         ), (
             _all_over("dinosaur", GREEN, (("Navy", NAVY),), title="Kids' Dinosaur Pyjamas",
                       description="Dinosaur pyjamas: dinosaurs all over, a dinosaur bedtime."),
         ), KIDS_SIZES),
    Line("SWK", "sweatshirts", "kids", "core", "sweatshirt", "Sweatshirt", "Little Fernby",
         "Clothing", ("Kids", "Tops", "Sweatshirts"), 14.0, (
             ("Kids' Crew Sweatshirt", cw("Grey", GREY), "A brushed-back crew sweatshirt."),
             ("Kids' Zip Sweatshirt", cw("Navy", NAVY), "A half-zip sweatshirt with a stand collar."),
             ("Kids' Fleece Sweatshirt", cw("Cream", CREAM), "A soft fleece sweatshirt."),
         ), (
             Print("dinosaur", "placement", GREEN, (("Grey", GREY),),
                   title="Kids' Dinosaur Sweatshirt",
                   description="A dinosaur sweatshirt with one big dinosaur on the front."),
         ), KIDS_SIZES),
    Line("DRS", "dresses", "women", "core", "dress", "Tea Dress", "Larkmoor", "Clothing",
         ("Women", "Dresses", "Tea Dresses"), 38.0, (
             ("Plain Tea Dress", cw("Navy", NAVY), "A floaty tea dress with a tie waist."),
             ("Midi Tea Dress", cw("Sage", SAGE), "A midi tea dress with flutter sleeves."),
             ("Button Front Tea Dress", cw("Cream", CREAM), "A button front tea dress in crepe."),
         ), (
             _all_over("lemon", LEMON, (("White", WHITE),), code="LEMDRS",
                       title="Lemon Print Tea Dress",
                       description="A floaty tea dress in our lemon print: yellow lemons and green "
                       "leaves on white. The lemon print is back for summer."),
         ), ADULT_SIZES),
    Line("BEDK", "bedding", "kids", "core", "duvet", "Duvet Set", "Little Fernby", "Home",
         ("Home", "Kids' Bedding", "Bedding Sets"), 20.0, (
             ("Kids' Cotton Bedding Set", cw("White", WHITE), "A single cover and pillowcase in cotton."),
             ("Kids' Brushed Cotton Bedding Set", cw("Pink", PINK), "Brushed cotton for cold nights."),
             ("Kids' Seersucker Bedding Set", cw("Navy", NAVY), "A puckered seersucker set."),
         ), (
             _all_over("dinosaur", GREEN, (("White", WHITE),), code="DUVKID",
                       title="Kids' Dinosaur Duvet Set",
                       description="A printed single duvet set for kids: a duvet cover and "
                       "pillowcase. Duvet sold separately."),
         )),
    Line("DUVA", "bedding", "adult", "core", "duvet", "Duvet Cover", "Brackenmere Home", "Home",
         ("Home", "Bedding", "Duvet Covers"), 28.0, (
             ("Washed Linen Bed Cover", cw("Oat", OAT), "A washed linen cover, soft from the first night."),
         ), (
             _all_over("lemon", LEMON, (("White", WHITE),), title="Lemon Print Duvet Cover",
                       description="A lemon print cover: lemons and leaves on white. Lemon "
                       "bedding for a fresh lemon bedroom."),
         )),
    Line("TTW", "kitchen textiles", "adult", "core", "tea_towel", "Tea Towels", "Brackenmere Home",
         "Home", ("Home", "Kitchen", "Tea Towels"), 9.0, (
             ("Cotton Tea Towels, Set of 2", cw("White", WHITE), "Absorbent cotton tea towels."),
             ("Linen Tea Towels, Set of 2", cw("Stone", STONE), "Lint-free linen tea towels."),
             ("Waffle Tea Towels, Set of 2", cw("Grey", GREY), "Quick-drying waffle tea towels."),
         ), (
             Print("orange", "scatter", ORANGE, (("Cream", CREAM),), scale=0.12, spacing=140,
                   title="Orange Print Tea Towels, Set of 2",
                   description="Orange print tea towels: oranges scattered on cream. Orange "
                   "for the kitchen."),
         )),
    Line("MUG", "mugs", "adult", "core", "mug", "Mug", "Brackenmere Home", "Home",
         ("Home", "Kitchen", "Mugs"), 8.0, (
             ("Stoneware Mug", cw("White", WHITE), "A chunky stoneware mug, dishwasher safe."),
             ("Speckled Mug", cw("Oat", OAT), "A speckled glaze mug that holds 350ml."),
             ("Tall Latte Mug", cw("Navy", NAVY), "A tall mug for lattes."),
         ), (
             Print("orange", "placement", ORANGE, (("White", WHITE),), title="Orange Print Mug",
                   description="A mug with one big orange: orange on white, an orange mug."),
         )),
)  # fmt: skip
