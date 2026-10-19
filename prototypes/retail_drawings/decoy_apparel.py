"""Text-match decoys on every clothing, footwear and lingerie type (gen#311).

gen#294's rule (:mod:`decoy_rows`): a decoy's words mislead a plain text search and its structured
fields tell the truth, so the color, category and audience policies, which read the fields, are
right. :mod:`decoy_rows` plants them for the demo queries; this module plants them on EVERY type
of the Womens, Mens and Kids clothing, footwear and lingerie, generated from the plan below
(:func:`types`), never written row by row. A type of the registry (``type_specs/``, gen#351)
carries its own plan in its spec, so a new clothing type edits no file but its spec.

A decoy is a clone of one real style of its type (the exemplar: its category leaf, sizes,
attributes and drawing), in one main color, with a new title, description and, for class 7, brand.
The classes (the numbers follow the issue):

1. **part**: the color word names a strap, a sole, a waistband ("Bra with Red Straps": the title
   names the misleading color only, the structured color is the true one and the drawing shows
   the named part in the named color, :mod:`details`).
2. **type**: another category's noun in a real compound ("Navy Shirt Dress", "Cream Trouser Socks";
   :data:`COMPOUNDS`, never an invented one such as "Dress Pyjamas").
3. **audience**: an audience word of a sibling version ("Black Mens-Style Jeans", a women's style).
4. **absent**: a material or feature named but absent ("Black Leather-Look Jacket").
5. **shade**: the shade is spelled in the description only ("Moonbeam Dress", "in soft ivory").
6. **incidental**: a range name, a place, holds a category word ("Jumper Lane Dress"). Never a
   color word (#444: "Red Harbour Dress" read as a red dress by a strange brand).
7. **brand**: an invented brand holds a color or a category word ("Red Plover Bra", blue); the
   brand field holds the same words and the drawing colors no part (#444).

Every type gets :attr:`Spec.per_class` decoys per class (three, more for Bra and Jeans, which
are large, so a type holds at least a tenth of its size), and at most eight of class 7 (one per
brand). Titles of classes 6 and 7 are five words or fewer, so
the word sits where the text score weights it most. A type missing from the catalog, or one the
catalog gains, reds ``tests/test_retail_apparel_decoys_311.py`` until it is planned or exempt.
Names are invented. :func:`ids` (``IDS``) is what :mod:`scale` leaves out of its derivation and
:mod:`main_colors` out of its color completion.
"""

from __future__ import annotations

import copy
import functools
import random
import re
import zlib
from dataclasses import dataclass, replace

import details
import facet_leaves
import real_brands
import type_colors
import type_registry
from class_model import SHADE_FAMILY
from decoy_plural_nonfood_rows import IDS as PLURAL_NONFOOD_IDS
from decoy_rows import COLORS
from variants import attr, cw, product, swatch

ROOTS = ("Womens", "Mens", "Kids")
DEPARTMENTS = type_registry.APPAREL_DEPARTMENTS
BRANDS = (("Red Plover", "red"), ("Blue Otter", "blue"), ("Green Stoat", "green"),
          ("Yellow Wagtail", "yellow"), ("Black Lapwing", "black"), ("White Dormouse", "white"),
          ("Jumper Jay", "jumper"), ("Coat Crake", "coat"))  # fmt: skip
#: The main colors a decoy is sold in, with the swatch hex of :mod:`decoy_rows`.
PRODUCT_COLORS = ("Black", "White", "Navy", "Cream", "Grey", "Brown", "Pink", "Red", "Blue",
                  "Green")  # fmt: skip
DETAIL_HEX = COLORS | {"Yellow": "#f2d14b"}  # the hex a named part's color is drawn in
DROPPED_KEYS = ("line", "pattern", "print", "color", "motif")  # a clone is plain, one color
MAIN_WORDS = ("red", "blue", "green", "yellow", "black", "white")
CLASSES = {
    1: "color names a part",
    2: "another category's noun as a modifier",
    3: "audience word of a sibling version",
    4: "material or feature named but absent",
    5: "shade spelled in the description only",
    6: "incidental word in a range name",
    7: "invented brand holding a color or category word",
}
POLICY = {4: "special: material claim"}


@dataclass(frozen=True)
class Spec:
    """A planned type: its ``product_type``, its word family (a: garment, b: bra, u: underwear,
    s: shoe, k: sock) and its decoys per class."""

    product_type: str
    family: str = "a"
    per_class: int = 3
    prefix: str = ""  # what a decoy id of the type starts with after ``PLT-D``
    compounds: tuple[tuple[str, str], ...] = ()  # a registry type's own (word, phrase) pairs

    @property
    def classes(self) -> dict[int, int]:
        n = self.per_class
        return {1: n, 2: n, 3: n, 4: n, 5: n, 6: n, 7: min(n, len(BRANDS))}


def _plan(family: str, *names: str) -> tuple[Spec, ...]:
    return tuple(Spec(n, family) for n in names)


_PLANNED: tuple[Spec, ...] = (
    *_plan("a", "Blouse", "Bodysuit", "Bomber Jacket", "Cardigan", "Coat", "Co-ord Set",
           "Cycling Shorts", "Denim Jacket", "Dress", "Joggers", "Jumper", "Leggings",
           "Outfit Set", "Puffer Jacket", "Shirt", "Shorts", "Skirt", "Suit Jacket", "Sweatshirt",
           "T-Shirt", "Tea Dress", "Tee", "Top", "Tracksuit", "Trousers"),
    Spec("Jeans", "a", 12),
    *_plan("k", "Socks", "Boot Socks"),
    *_plan("s", "Ankle Boots", "Ballet Pumps", "Block Heels", "Brogues", "Chelsea Boots",
           "Chukka Boots", "Court Shoes", "Kitten Heels", "Knee High Boots", "Loafers",
           "Running Shoes", "Safety Boots", "Sandals", "School Shoes", "Slippers", "Trainers",
           "Walking Boots", "Wellies"),
    Spec("Bra", "b", 10),  # gen#508: the plural-cups bras took the type past 620, a tenth is 63
    *_plan("u", "Boxers", "Dressing Gown", "Knickers", "Pyjama Shorts", "Pyjamas", "Shapewear",
           "Slip", "Tights", "Vest"),
    *_plan("a", "School Trousers", "School Skirt", "School Pinafore", "School Shirt"),  # gen#205
    *_plan("s", "Plimsolls", "Clogs", "Wedges", "Espadrilles", "Platform Trainers", "Mules",
           "Jelly Shoes", "Barefoot Shoes"),  # gen#216
)  # fmt: skip
#: The types planned here, numbered by their place in the plan: ``A00`` for the first. A type of
#: the registry is numbered by its key instead (``S`` and the key), so adding one moves no id. A
#: type of this plan moves into its spec only with its ids renumbered, so none has yet (Tracksuit,
#: a spec, keeps its plan here).
#: More decoys for the two types the neckline depth grew (gen#181): a large type carries a tenth.
#: The extra ids are the later ones of each class (``i`` 3 and up): no id is renamed, but an
#: existing id can change content (PLT-DA08602 does), so a decoy is never pinned by its id.
_MORE = {"Top": 6, "Dress": 5}
BASE_TYPES: tuple[Spec, ...] = tuple(
    replace(s, prefix=f"A{ti:02d}", per_class=_MORE.get(s.product_type, s.per_class))
    for ti, s in enumerate(_PLANNED)
)
#: Types of the three departments that carry no decoys, each with its reason.
BASE_EXEMPT = {
    "Belt": "an accessory, not a garment: its text words are those of the accessories batch",
    "Bracelet": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Earrings": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Necklace": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Ring": "jewellery: the color is the metal finish, not a printed or dyed color",
    "Watch": "a watch: the color is the metal finish, not a printed or dyed color",
    "Polo Shirt": "a type of the Mens clothing depth (gen#310), which carries its own decoys",
    "Jacket": "a type of the Mens clothing depth (gen#310), which carries its own decoys",
    "Mens Trousers": "a type of the Mens clothing depth (gen#310), which carries its own decoys",
    "Backpack": "an accessory, not a garment: its text words are those of the accessories batch",
    "Handbag": "an accessory, not a garment: its text words are those of the accessories batch",
    "Purse": "an accessory, not a garment: its text words are those of the accessories batch",
    "Tote Bag": "an accessory, not a garment: its text words are those of the accessories batch",
    "Umbrella": "an accessory, not a garment: its text words are those of the accessories batch",
    "Shoe Care Kit": "a care product sold in the footwear department, not footwear",
    "Shoe Polish": "a care product sold in the footwear department, not footwear",
    "Shoe Laces": "a care product sold in the footwear department, not footwear",
    "Key Clips": "an accessory, not a garment: it carries its own decoys (gen#326)",
    "Travel Cases": "an accessory, not a garment: it carries its own decoys (gen#326)",
    "Waist Bags": "an accessory, not a garment: it carries its own decoys (gen#326)",
}


def _code(spec: Spec, cls: int, i: int) -> str:
    return f"{spec.prefix}{cls}{i:02d}"


def _registered() -> tuple:
    """What the registry says of each spec, as a hashable key for :func:`_merged`."""
    return tuple(
        (key, sp.product_type, sp.apparel, sp.apparel_exempt,
         sp.department in DEPARTMENTS and any(r.path[0] in ROOTS for r in sp.rows))
        for key, sp in type_registry.specs().items()
    )  # fmt: skip


@functools.cache
def _merged_for(registered: tuple) -> tuple[tuple[Spec, ...], dict[str, str], frozenset[str]]:
    types = list(BASE_TYPES)
    exempt = dict(BASE_EXEMPT)
    seen = {t.product_type for t in BASE_TYPES} | set(BASE_EXEMPT)
    for key, ptype, plan, why, in_scope in registered:
        if (plan or why) and ptype in seen:
            raise type_registry.SpecError(f"{key}: {ptype} is already planned (apparel) here")
        if plan:
            prefix = f"S{key.upper()}"
            types.append(Spec(ptype, plan.family, plan.per_class, prefix, plan.compounds))
        elif why:
            exempt[ptype] = why
        elif in_scope and ptype not in seen:
            raise type_registry.SpecError(
                f"{key}: a {ptype} is clothing, footwear or lingerie: give its spec "
                "apparel=ApparelPlan() (or apparel_exempt=<reason>) for the apparel decoys"
            )
    ids = frozenset(
        f"PLT-D{_code(s, cls, i)}"
        for s in types for cls, n in s.classes.items() for i in range(n)
    )  # fmt: skip
    return tuple(types), exempt, ids


def _merged() -> tuple[tuple[Spec, ...], dict[str, str], frozenset[str]]:
    return _merged_for(_registered())


def types() -> tuple[Spec, ...]:
    """Every planned type: this plan, then the registry's, in key order."""
    return _merged()[0]


def ids() -> frozenset[str]:
    """Every decoy id of :func:`types`."""
    return _merged()[2]


def __getattr__(name: str):  # PEP 562: ``TYPES``, ``EXEMPT`` and ``IDS`` follow the registry
    if name == "TYPES":
        return types()
    if name == "EXEMPT":
        return _merged()[1]
    if name == "IDS":
        return ids()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# -- the words ------------------------------------------------------------------------------------
#: Class 2: the compounds a shopper reads as a real product name (dress shirt, shirt dress, slipper
#: socks), per type, each as (the word it targets, the phrase). A phrase keeps the type's head noun
#: and puts another category's noun before it; it drops the type's own modifier only where the
#: shorter name still describes the product (Sandal Boots for Ankle Boots). An invented compound
#: ("Dress Pyjamas", "Trouser Blouse") is in no row (#444); the test file holds the list apart.
COMPOUNDS = {
    "Blouse": (("dress", "Dress Blouse"), ("shirt", "Shirt Blouse"), ("tunic", "Tunic Blouse")),
    "Bodysuit": (("shirt", "Shirt Bodysuit"), ("corset", "Corset Bodysuit"),
                 ("cami", "Cami Bodysuit")),
    "Bomber Jacket": (("shirt", "Shirt Jacket"), ("blazer", "Blazer Jacket"),
                      ("biker", "Biker Jacket")),
    "Cardigan": (("kimono", "Kimono Cardigan"), ("duster", "Duster Cardigan"),
                 ("bomber", "Bomber Cardigan")),
    "Coat": (("dress", "Dress Coat"), ("puffer", "Puffer Coat"), ("duffle", "Duffle Coat")),
    "Co-ord Set": (("skirt", "Skirt Co-ord Set"), ("trouser", "Trouser Co-ord Set"),
                   ("shirt", "Shirt Co-ord Set"), ("short", "Short Co-ord Set")),
    "Cycling Shorts": (("dress", "Dress Shorts"), ("cargo", "Cargo Shorts"),
                       ("tailored", "Tailored Shorts")),
    "Denim Jacket": (("shirt", "Denim Shirt Jacket"), ("bomber", "Denim Bomber Jacket"),
                     ("biker", "Denim Biker Jacket")),
    "Dress": (("shirt", "Shirt Dress"), ("jumper", "Jumper Dress"), ("blazer", "Blazer Dress"),
              ("hoodie", "Hoodie Dress"), ("tunic", "Tunic Dress"), ("coat", "Coat Dress")),
    "Joggers": (("chino", "Chino Joggers"), ("cargo", "Cargo Joggers"),
                ("denim", "Denim Joggers")),
    "Jumper": (("tunic", "Tunic Jumper"), ("polo", "Polo Jumper")),
    "Leggings": (("cargo", "Cargo Leggings"), ("denim", "Denim Leggings"),
                 ("cycling", "Cycling Leggings")),
    "Outfit Set": (("skirt", "Skirt Set"), ("trouser", "Trouser Set"), ("short", "Short Set"),
                   ("blazer", "Blazer Set")),
    "Puffer Jacket": (("shirt", "Shirt Jacket"), ("bomber", "Bomber Jacket"),
                      ("biker", "Biker Jacket")),
    "Shirt": (("dress", "Dress Shirt"), ("polo", "Polo Shirt"), ("tunic", "Tunic Shirt")),
    "Shorts": (("dress", "Dress Shorts"), ("tailored", "Tailored Shorts"),
               ("jean", "Jean Shorts"), ("chino", "Chino Shorts"), ("cargo", "Cargo Shorts")),
    "Skirt": (("jean", "Jean Skirt"), ("slip", "Slip Skirt"), ("cargo", "Cargo Skirt")),
    "Suit Jacket": (("blazer", "Blazer Jacket"), ("dress", "Dress Jacket"),
                    ("shirt", "Shirt Jacket")),
    "Sweatshirt": (("polo", "Polo Sweatshirt"), ("hoodie", "Hoodie Sweatshirt"),
                   ("tunic", "Tunic Sweatshirt")),
    "T-Shirt": (("polo", "Polo T-Shirt"), ("tunic", "Tunic T-Shirt")),
    "Tea Dress": (("shirt", "Shirt Dress"), ("tunic", "Tunic Dress"), ("jumper", "Jumper Dress")),
    "Tee": (("polo", "Polo Tee"), ("tunic", "Tunic Tee")),
    "Top": (("vest", "Vest Top"), ("cami", "Cami Top"), ("polo", "Polo Top"),
            ("tunic", "Tunic Top"), ("bodysuit", "Bodysuit Top")),
    "Tracksuit": (("hoodie", "Hoodie Tracksuit"), ("short", "Short Tracksuit"),
                  ("jogger", "Jogger Tracksuit")),
    "Trousers": (("cargo", "Cargo Trousers"), ("chino", "Chino Trousers"),
                 ("jogger", "Jogger Trousers"), ("dress", "Dress Trousers")),
    "Jeans": (("cargo", "Cargo Jeans"), ("jogger", "Jogger Jeans")),
    "School Trousers": (("chino", "Chino School Trousers"), ("jogger", "Jogger School Trousers"),
                        ("cargo", "Cargo School Trousers")),
    "School Skirt": (("pinafore", "Pinafore School Skirt"),),
    "School Pinafore": (("dress", "School Pinafore Dress"),),
    "School Shirt": (("polo", "School Polo Shirt"), ("oxford", "Oxford School Shirt")),
    "Socks": (("boot", "Boot Socks"), ("trouser", "Trouser Socks"), ("slipper", "Slipper Socks"),
              ("trainer", "Trainer Socks"), ("sneaker", "Sneaker Socks")),
    "Boot Socks": (("welly", "Welly Boot Socks"), ("wellington", "Wellington Boot Socks"),
                   ("walking", "Walking Boot Socks")),
    "Ankle Boots": (("sandal", "Sandal Boots"), ("sneaker", "Sneaker Boots"),
                    ("loafer", "Loafer Boots"), ("shoe", "Shoe Boots")),
    "Ballet Pumps": (("slipper", "Ballet Slippers"), ("sandal", "Ballet Sandals")),
    "Block Heels": (("mule", "Mule Heels"), ("loafer", "Loafer Heels"), ("sandal", "Sandal Heels")),
    "Brogues": (("dress", "Dress Brogues"), ("derby", "Derby Brogues"),
                ("oxford", "Oxford Brogues")),
    "Chelsea Boots": (("sneaker", "Sneaker Boots"), ("loafer", "Loafer Boots"),
                      ("slipper", "Slipper Boots")),
    "Chukka Boots": (("sneaker", "Sneaker Boots"), ("loafer", "Loafer Boots"),
                     ("shoe", "Shoe Boots")),
    "Court Shoes": (("dress", "Dress Shoes"),),
    "Kitten Heels": (("mule", "Mule Heels"), ("sandal", "Sandal Heels"),
                     ("loafer", "Loafer Heels")),
    "Knee High Boots": (("sock", "Sock Boots"), ("sneaker", "Sneaker Boots"),
                        ("biker", "Biker Boots")),
    "Loafers": (("mule", "Mule Loafers"), ("brogue", "Brogue Loafers")),
    "Running Shoes": (("walking", "Walking Shoes"), ("tennis", "Tennis Shoes"),
                      ("training", "Training Shoes")),
    "Safety Boots": (("wellington", "Wellington Safety Boots"),
                     ("chelsea", "Chelsea Safety Boots"), ("hiker", "Hiker Safety Boots")),
    "Sandals": (("loafer", "Loafer Sandals"), ("mule", "Mule Sandals"),
                ("espadrille", "Espadrille Sandals")),
    "School Shoes": (("dress", "Dress Shoes"), ("loafer", "Loafer School Shoes"),
                     ("brogue", "Brogue School Shoes")),
    "Slippers": (("boot", "Boot Slippers"), ("sock", "Sock Slippers"),
                 ("loafer", "Loafer Slippers"), ("mule", "Mule Slippers")),
    "Trainers": (("sock", "Sock Trainers"), ("running", "Running Trainers"),
                 ("walking", "Walking Trainers")),
    "Walking Boots": (("chukka", "Chukka Walking Boots"),),
    "Plimsolls": (("sneaker", "Sneaker Plimsolls"),),
    "Clogs": (("mule", "Mule Clogs"),),
    "Wedges": (("sneaker", "Sneaker Wedges"),),
    "Espadrilles": (("sneaker", "Sneaker Espadrilles"),),
    "Platform Trainers": (("sock", "Sock Platform Trainers"),),
    "Mules": (("loafer", "Loafer Mules"), ("slipper", "Slipper Mules"), ("sandal", "Sandal Mules")),
    "Jelly Shoes": (("mary jane", "Mary Jane Jelly Shoes"),),
    "Barefoot Shoes": (("sandal", "Sandal Barefoot Shoes"),),
    "Wellies": (("chelsea", "Chelsea Wellies"),),
    "Bra": (("cami", "Cami Bra"), ("corset", "Corset Bra")),
    "Boxers": (("short", "Boxer Shorts"), ("brief", "Boxer Briefs"), ("trunk", "Boxer Trunks")),
    "Dressing Gown": (("hoodie", "Hoodie Dressing Gown"), ("kimono", "Kimono Dressing Gown")),
    "Knickers": (("short", "Short Knickers"), ("cami", "Cami Knickers"),
                 ("bikini", "Bikini Knickers")),
    "Pyjama Shorts": (("boxer", "Boxer Shorts"), ("cycling", "Cycling Shorts"),
                      ("bermuda", "Bermuda Shorts")),
    "Pyjamas": (("short", "Short Pyjamas"), ("cami", "Cami Pyjamas")),
    "Shapewear": (("bodysuit", "Bodysuit Shapewear"), ("cami", "Cami Shapewear"),
                  ("slip", "Slip Shapewear")),
    "Slip": (("dress", "Dress Slip"), ("skirt", "Skirt Slip"), ("cami", "Cami Slip")),
    "Tights": (("running", "Running Tights"), ("cycling", "Cycling Tights")),
    "Vest": (("cami", "Cami Vest"), ("dress", "Dress Vest"), ("sweater", "Sweater Vest")),
}
#: Types with fewer than three real class 2 compounds, each with its reason (#444): a phrase is
#: added only when a shopper meets it as a product name, so these types hold fewer, not an
#: invented third.
SHORT_COMPOUNDS: dict[str, str] = {
    "Swimsuit": "only the skirted swimsuit and the tank swimsuit pair another noun with a swimsuit",
    "Kids Swimsuit": "only the skirted and the rash vest kids swimsuit are names a shopper meets",
    "Bra": "only the cami bra and the corset bra are names; a t-shirt bra is a bra shape",
    "Blouse": "only the dress blouse and the tunic blouse are names a shopper meets",
    "Ballet Pumps": "only ballet slippers and ballet sandals pair another noun with a ballet pump",
    "Chukka Boots": "only sneaker boots and loafer boots are names; a shoe boot is not one",
    "Tee": "only the polo tee and the tunic tee name another category; a henley is a tee",
    "T-Shirt": "only the polo and tunic t-shirt name another category; a henley is a t-shirt",
    "Jumper": "only the tunic jumper and the polo jumper are names a shopper meets",
    "Jeans": "only cargo jeans and jogger jeans are names a shopper meets",
    "School Skirt": "only the pinafore school skirt is a name a shopper meets",
    "School Pinafore": "a school pinafore dress is the only compound name of it",
    "School Shirt": "only the school polo shirt and the oxford school shirt are names met",
    "Court Shoes": "only dress shoes pairs another category's noun with a court shoe",
    "Loafers": "only mule loafers and brogue loafers are names a shopper meets",
    "Walking Boots": "only the chukka walking boot is a name a shopper meets",
    "Plimsolls": "only the sneaker plimsoll is a name met; a pump or a trainer is a plimsoll",
    "Clogs": "only the mule clog is a name a shopper meets",
    "Wedges": "only the sneaker wedge is a name; a sandal wedge is a wedge sandal",
    "Espadrilles": "only the sneaker espadrille is a name; a wedge espadrille is an espadrille",
    "Platform Trainers": "only the sock platform trainer is a name a shopper meets",
    "Jelly Shoes": "only the mary jane jelly shoe is a name a shopper meets",
    "Barefoot Shoes": "only the sandal barefoot shoe is a name a shopper meets",
    "Wellies": "only the chelsea welly is a name a shopper meets",
    "Dressing Gown": "only hoodie and kimono dressing gowns are names a shopper meets",
    "Tights": "only running tights and cycling tights are names a shopper meets",
    "Pyjamas": "only short pyjamas and cami pyjamas are names a shopper meets",
}
AUDIENCE = {"Womens": (("Mens-Style", "mens"), ("Mens Fit", "mens"), ("Boys Fit", "boys")),
            "Mens": (("Womens-Style", "womens"), ("Womens Fit", "womens"), ("Girls Fit", "girls")),
            "Kids": (("Mini-Me Mens", "mens"), ("Mini-Me Womens", "womens"),
                     ("Mens-Style", "mens"))}  # fmt: skip
ABSENT = (("Leather-Look", "leather", "A finish made to look like leather; it holds no leather."),
          ("Suede-Look", "suede", "A soft finish that resembles suede; no suede is used."),
          ("Cashmere-Feel", "cashmere", "Soft to the touch like cashmere; it holds no cashmere."),
          ("Wool-Free", "wool", "Made without wool."),
          ("Silk-Feel", "silk", "A smooth finish that feels like silk; no silk is used."),
          ("Linen-Look", "linen", "Woven to look like linen; it holds no linen."),
          ("Lace-Free", "lace", "Made without lace."),
          ("Velvet-Feel", "velvet", "A plush finish that feels like velvet; no velvet is used."),
          ("Denim-Look", "denim", "Printed to look like denim; it holds no denim."),
          ("Satin-Look", "satin", "A sheen that resembles satin; no satin is used."),
          ("Mohair-Free", "mohair", "Made without mohair."),
          ("Tweed-Look", "tweed", "A weave that resembles tweed; it holds no tweed."),
          ("Fleece-Free", "fleece", "Made without fleece."),
          ("Corduroy-Look", "corduroy", "Ribbed to look like corduroy; it holds no corduroy."),
          ("Mesh-Free", "mesh", "Made without mesh."), ("Silk-Free", "silk", "Made without silk."),
          ("Canvas-Look", "canvas", "A weave that resembles canvas; it holds no canvas."),
          ("Rubber-Free", "rubber", "Made without rubber."))  # fmt: skip
SHADES = (("Moonbeam", "Ivory", "#f6f1e1", "cream"), ("Driftwood", "Taupe", "#8b7d6b", "brown"),
          ("Dune", "Beige", "#d9c6a5", "cream"), ("Ember", "Burgundy", "#6d1a2e", "red"),
          ("Lagoon", "Teal", "#2a7f80", "blue"), ("Willow", "Olive", "#7a7a3c", "green"),
          ("Pebble", "Ecru", "#e6dcc4", "cream"), ("Meadow", "Mint", "#a9d6b5", "green"),
          ("Harvest", "Rust", "#b5522b", "orange"), ("Seashell", "Coral", "#f26b5a", "orange"),
          ("Biscuit", "Champagne", "#f1e0c0", "cream"), ("Hearth", "Khaki", "#b5a57a", "green"),
          ("Cobble", "Camel", "#c19a6b", "brown"), ("Silt", "Stone", "#cfc6b8", "cream"),
          ("Tallow", "Oatmeal", "#d8cdb4", "cream"), ("Quill", "Aubergine", "#4b2a45", "brown"))  # fmt: skip  # noqa: E501
#: Class 6: a range name is a place, never a color (#444: "Red Harbour Dress" read as a red dress
#: by a strange brand, and a title may not claim a color the product lacks), so the first word is a
#: category word and the name is a place. At least twelve, for Jeans (twelve per class).
CATEGORY_RANGES = (("Jumper Lane", "a village lane"), ("Coat Hook", "a headland"),
                   ("Shirt Row", "a terrace of cottages"), ("Dress Circle", "a theatre tier"),
                   ("Boot Hill", "a wooded hill"), ("Skirt Point", "a rocky point"),
                   ("Jacket Quay", "a harbour quay"), ("Sock Hop", "a village dance"),
                   ("Shoe Lane", "a lane by the old market"), ("Cardigan Bay", "a wide bay"),
                   ("Blazer Court", "a courtyard of flats"), ("Slipper Brook", "a slow brook"),
                   ("Sandal Wood", "a stand of sandalwood"), ("Pump Lane", "a lane by a pump"),
                   ("Slip Road", "a road onto the moor"))  # fmt: skip


@dataclass(frozen=True)
class Row:
    """One planted decoy: its class, the misleading ``word``, the ``query`` it targets and its
    ``policy`` (``generic`` or ``special: <name>``); ``doc`` is the catalog document."""

    pid: str
    product_type: str
    cls: int
    word: str
    query: str
    policy: str
    doc: dict

    @property
    def title(self) -> str:
        return self.doc["title"]


def field_text(doc: dict) -> str:
    """Every attribute value, SKU text field and the category leaf, lowercased: what the
    structured fields say, so a misleading word is one this does not hold."""
    vals = [str(a["value"]) for a in doc["attributes"]] + [doc["product_type"]]
    vals += [
        str(v)
        for s in doc["skus"]
        for k, v in s.items()
        if isinstance(v, str) and not k.startswith("size") and k not in ("sku", "color")
    ]
    return " ".join(vals).lower()


def _in_path(word: str, doc: dict) -> bool:
    path = " ".join(doc["category_path"]) + " " + doc["product_type"]
    return re.search(rf"\b{re.escape(word)}s?\b", path.lower()) is not None


def _clone(
    ex: dict,
    code: str,
    title: str,
    desc: str,
    color: str,
    hexv: str,
    family: str,
    brand: str | None = None,
    detail: tuple[str, str] | None = None,
) -> dict:
    """``ex`` re-run through :func:`variants.product` in one color with a new title, description
    and (class 7) brand; its popularity is above the typical so the text score competes."""
    from class_model import BRAND_OWNER

    keep = {k: v for k, v in copy.deepcopy(ex).items()
            if k not in ("product_id", "price", "sku_count", "skus", "color_options",
                         "size_options", "was_price", "discount_pct", "promotion", "pattern",
                         "sub_collection", "product_line", "leg_style")}  # fmt: skip
    first = ex["skus"][0]["color"]
    color_tuple = cw(color, hexv)
    skus = [{**{k: v for k, v in s.items() if k != "sku"}, "color": color_tuple[0]}
            for s in ex["skus"] if s["color"] == first]  # fmt: skip
    if not any(s["in_stock"] for s in skus):
        skus[0]["in_stock"] = True
    sold = 500 + zlib.crc32(code.encode()) % 400
    prices = [s["price"] for s in skus]
    keep["attributes"] = [a for a in keep["attributes"]
                          if a["key"] not in DROPPED_KEYS]  # fmt: skip
    if ex.get("leg_style") and _fit(ex):  # the style is dropped above; its fit stays an attribute
        keep["attributes"].append(attr("leg_fit", "Leg fit", _fit(ex)))
    keep |= {"title": title, "description": desc, "sold_last_5_days": sold,
             "review_count": 900 + sold, "trending": False,
             "price_min": min(prices), "price_max": max(prices)}  # fmt: skip
    if brand is not None:
        keep |= {"brand": brand, "brand_owner": BRAND_OWNER[brand]}
    keep["drawing"] = {k: v for k, v in keep["drawing"].items() if k != "accents"} | {
        "pattern": "solid", "base": hexv, "accent": "#333333",
        "motif": None, "placement": None}  # fmt: skip
    if detail:  # a named part (class 1) is drawn in the named color: the title is true
        keep["drawing"]["detail"] = {"part": detail[0], "color": detail[1]}
    return product(f"PLT-D{code}", skus, {color_tuple[0]: swatch(color_tuple, family)}, **keep)


def _a(word: str) -> str:
    """The article before ``word``: "an oxford", "a boot"."""
    return "an" if word[:1].lower() in "aeiou" else "a"


def _options(cls: int, spec: Spec, ex: dict) -> list[dict]:
    """Every decoy of class ``cls`` this exemplar can carry: title, description, word, query,
    color. Any option whose word the exemplar's own fields hold is left out."""
    noun = spec.product_type
    n = noun.lower()
    path_has = lambda w: _in_path(w, ex)  # noqa: E731
    out = []
    if cls == 1:
        for part in details.parts_of(ex["drawing"]["shape"]):
            for sec in MAIN_WORDS:
                for c in PRODUCT_COLORS:
                    if c.lower() != sec:
                        out.append(
                            dict(
                                title=f"{noun} with {sec.title()} {part.title()}",
                                word=sec,
                                desc=f"{c} {n} with {sec} {part}.",
                                color=c,
                                query=f"{sec} {n}",
                                part=part,
                            )
                        )
    elif cls == 2:
        pairs = spec.compounds or COMPOUNDS.get(noun)
        if not pairs:
            raise ValueError(f"{noun}: no real class 2 compound; add it to COMPOUNDS")
        for word, phrase in (w for w in pairs if not path_has(w[0])):
            for c in PRODUCT_COLORS:
                out.append(
                    dict(
                        title=f"{c} {phrase}",
                        phrase=phrase,
                        word=word,
                        color=c,
                        desc=f"{c} {n} with {word}-style detailing, sold as "
                        f'"{phrase.lower()}". Not {_a(word)} {word}.',
                        query=word,
                    )
                )
    elif cls == 3:
        for phrase, word in AUDIENCE[ex["category_path"][0]]:
            for c in PRODUCT_COLORS:
                out.append(
                    dict(
                        title=f"{c} {phrase} {noun}",
                        word=word,
                        color=c,
                        desc=f"{c} {n} cut in a {phrase.lower()} fit.",
                        query=f"{word} {n}",
                    )
                )
    elif cls == 4:
        held = field_text(ex)
        for phrase, word, sentence in ABSENT:
            if word not in held:
                for c in PRODUCT_COLORS:
                    out.append(
                        dict(
                            title=f"{c} {phrase} {noun}",
                            word=word,
                            color=c,
                            desc=f"{c} {n}. {sentence}",
                            query=f"{word} {n}",
                        )
                    )
    elif cls == 5:
        for fancy, shade, hexv, family in SHADES:
            out.append(
                dict(
                    title=f"{fancy} {noun}",
                    word=shade.lower(),
                    color=shade,
                    hex=hexv,
                    family=family,
                    desc=f"{fancy} {n} in soft {shade.lower()}.",
                    query=f"{shade.lower()} {n}",
                )
            )
    elif cls == 6:
        for name, gloss in CATEGORY_RANGES:
            if not path_has(name.split()[0].lower()):
                for c in PRODUCT_COLORS:
                    out.append(
                        dict(
                            title=f"{name} {noun}",
                            word=name.split()[0].lower(),
                            color=c,
                            query=name.split()[0].lower(),
                            desc=f"{c} {n} from the {name} range, named for {gloss}.",
                        )
                    )
    else:
        for brand, word in BRANDS:
            if word in MAIN_WORDS or not path_has(word):
                for c in PRODUCT_COLORS:
                    if c.lower() != word:
                        out.append(
                            dict(
                                title=f"{brand} {noun}",
                                word=word,
                                color=c,
                                brand=brand,
                                desc=f"{c} {n} by {brand}.",
                                query=f"{word} {n}",
                            )
                        )
    return out


def _detail(ex: dict, cls: int, o: dict) -> tuple[str, str] | None:
    """The part a decoy draws in its title's color: the part a class 1 title names, else ``None``.
    A class 7 brand holds its color word in the brand field only (#444): the drawing colors no
    part, as no field says the product has one."""
    if cls != 1 or o["word"] not in MAIN_WORDS:
        return None
    part = o.get("part") or details.parts_of(ex["drawing"]["shape"])[0]
    return part, DETAIL_HEX[o["word"].title()]


def _fit(ex: dict) -> str | None:
    """The leg fit the exemplar's record files (:mod:`facet_leaves` reads it from the attribute,
    the failure-class ``leg_style`` or the leaf), or ``None``."""
    have = {a["key"]: a["value"] for a in ex["attributes"]}
    fit = have.get("leg_fit") or facet_leaves.LEG_STYLE_FITS.get(ex.get("leg_style", ""))
    if not fit and ex["product_type"] in facet_leaves.FIT_NODES:
        fit = facet_leaves._fit_of_leaf(
            ex["category_path"][-1], facet_leaves.FIT_NODES[ex["product_type"]]
        )
    return fit or None


def _title(ex: dict, spec: Spec, cls: int, o: dict) -> str:
    """The option's title, naming the exemplar's leg fit (the facet leaves' rule). A decoy title
    names only the misleading word: the real color is never appended (the maintainer ruling on
    #311; the output standard exempts decoy rows)."""
    title = o["title"]
    fit = _fit(ex)
    if fit and fit.lower() not in title.lower() and spec.product_type in title:
        # a class 2 compound takes the fit before it ("Slim Cargo Jeans"), never inside it
        head = o["phrase"] if cls == 2 else spec.product_type
        title = title.replace(head, f"{fit} {head}", 1)
    return title


def _names_its_drawing(ex: dict) -> bool:
    """A decoy's title names its type ("Boxers"), so its exemplar is drawn as that type: the
    boxers leaf also holds briefs, and "Boxers with Green Waistband" drawn as briefs (gen#447)
    is not a boxer."""
    fit = (ex["drawing"].get("params") or {}).get("fit")
    return not (ex["product_type"] == "Boxers" and fit == "brief")


def build(body: list[dict]) -> list[Row]:
    """Every decoy row for ``body`` (the templates without the decoys), in plan order."""
    pool: dict[str, list[dict]] = {}
    for d in sorted(body, key=lambda r: r["product_id"]):
        if (
            d["category_path"][0] in ROOTS
            and d["department"][0] in DEPARTMENTS
            and d.get("color_options")
            and d["product_id"] not in ids()
            and d["product_id"] not in PLURAL_NONFOOD_IDS  # a decoy is never a clone's source
            and d["brand"] not in real_brands.ALLOWED  # a real brand is never cloned (gen#341)
            and _names_its_drawing(d)
        ):
            pool.setdefault(d["product_type"], []).append(d)
    rows = []
    for spec in types():
        exemplars = pool[spec.product_type]
        used: set[tuple[str, str]] = set()
        words: set[tuple[int, str]] = set()
        step = 0
        for cls, n in spec.classes.items():
            rnd = random.Random(f"311-{spec.product_type}-{cls}")
            for i in range(n):
                ex = exemplars[step % len(exemplars)]
                step += 1
                opts = [o for o in _options(cls, spec, ex)
                        if type_colors.permits(ex["category_path"], o["color"])  # gen#448
                        and (cls not in (6, 7) or len(_title(ex, spec, cls, o).split()) <= 5)
                        and (o["title"], ex["category_path"][0]) not in used
                        and (cls not in (4, 5) or (cls, o["word"]) not in words)]  # fmt: skip
                if not opts:
                    raise ValueError(f"{spec.product_type} class {cls}: no option left")
                if cls in (4, 5):  # the common words first: leather, suede, cashmere; ivory
                    first = opts[0]["word"]
                    opts = [o for o in opts if o["word"] == first]
                code = _code(spec, cls, i)
                o = rnd.choice(opts)
                color = o["color"]
                hexv = o.get("hex") or COLORS[color]
                family = o.get("family") or SHADE_FAMILY.get(color, color.lower())
                doc = _clone(
                    ex,
                    code,
                    _title(ex, spec, cls, o),
                    o["desc"],
                    color,
                    hexv,
                    family,
                    o.get("brand"),
                    _detail(ex, cls, o),
                )
                words.add((cls, o["word"]))
                used.add((o["title"], ex["category_path"][0]))
                rows.append(
                    Row(
                        f"PLT-D{code}",
                        spec.product_type,
                        cls,
                        o["word"],
                        o["query"],
                        POLICY.get(cls, "generic"),
                        doc,
                    )
                )
    return rows


def docs(body: list[dict]) -> list[dict]:
    """Every row's catalog document, in plan order."""
    return [r.doc for r in build(body)]


def table_markdown(rows: list[Row]) -> str:
    """The docs table: one line per row, generated, never kept by hand."""
    lines = [
        "| Product id | Type | Class | Title | Word | Query | Policy |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r.pid} | {r.product_type} | {r.cls} {CLASSES[r.cls]} | {r.title} | "
            f"{r.word} | {r.query} | {r.policy} |"
        )
    return "\n".join(lines)


DOC = "docs/retail-apparel-decoys.md"
DOC_HEAD = """# Text-match decoys on every clothing, footwear and lingerie type (gen#311)

`prototypes/retail_drawings/decoy_apparel.py` plants, on every product type of the Womens, Mens and
Kids clothing, footwear and lingerie, products whose words mislead a plain text search while their
structured fields tell the truth (gen#294's rule; `decoy_rows.py` holds the demo-query rows). A
decoy is a clone of one real style of its type in one main color. The color, category and audience
policies read the fields and drop it. The classes: 1 a color word names a trim or strap; 2 another
category's noun in a real compound; 3 an audience word of a sibling version; 4 a material or
feature named but absent; 5 the shade is in the description only; 6 a short range name, a place,
holds a category word; 7 an invented brand holds a color or category word.

Each type holds at least three decoys per class (nine and twelve for bras and jeans, so a type
holds a tenth of its size), and one class 7 decoy per brand (at most eight).
Classes 6 and 7 have titles of five words or fewer. A title names the misleading color only
(never the real one); the drawing shows the named part (class 1) in that color, and nothing else
of it (`details.py`). A class 7 brand holds its color word in the brand field only, and its
drawing colors no part: "Yellow Wagtail Co-ord Set" is a blue co-ord set with no yellow part.

A decoy must read as a real product and describe what it is (#444). A color word sits in the
title only as an invented brand that is the product's brand field and is shown as the brand
(class 7: "Red Plover Bra"), or as a part that really is that color and the drawing shows
(class 1: "Bra with Red Straps"). So class 6 has no color variant: a range name such as "Red
Harbour" read as a red dress by a strange brand, with only the straps drawn red, and a range that
is a visible line of the product's brand would only repeat class 7. Class 6 keeps its category
word variant, a range named for a place ("Jumper Lane Dress"). Class 2 uses the compounds of
`decoy_apparel.COMPOUNDS` (dress shirt, shirt dress, slipper socks), each a real retail name,
never an invented one ("Dress Pyjamas"); a compound drops a type's own modifier only where the
shorter name still describes the product (Sandal Boots for Ankle Boots).
`tests/test_retail_apparel_decoys_311.py` holds the reviewed list of real compounds apart from the
generator's table, and a type holds at least three, except the declared exceptions below. The
Policy column is
`generic` where the color, category or audience policy separates the decoy, and
`special: <name>` where it needs its own
(a material claim: no field says the product is not leather). The exempt types are in
`decoy_apparel.EXEMPT`. The table is generated
(`python3 prototypes/retail_drawings/decoy_apparel.py`) and
`tests/test_retail_apparel_decoys_311.py` holds it verbatim.

"""


def short_compounds_text() -> str:
    """The docs paragraph naming each type with fewer than three real class 2 compounds."""
    items = "\n".join(f"- {t}: {why}." for t, why in sorted(SHORT_COMPOUNDS.items()))
    return (
        "Types with fewer than three real class 2 compounds (a third is never invented; "
        "#444):\n\n" + items + "\n\n"
    )


def render_doc(rows: list[Row]) -> str:
    return DOC_HEAD + short_compounds_text() + table_markdown(rows) + "\n"


def write_doc() -> str:
    """Write the docs table of :data:`DOC` from the registry; return its path."""
    import pathlib

    import scale

    root = pathlib.Path(__file__).resolve().parents[2]
    base = [d for d in scale.templates(baseline=False) if d["product_id"] not in ids()]
    (root / DOC).write_text(render_doc(build(base)), "utf-8")
    return str(root / DOC)


if __name__ == "__main__":
    print(f"wrote {write_doc()}")
