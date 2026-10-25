"""The model-name grammar of a product line, per category family (gen#662).

A range name such as "Cloudrise" or "Cardigan Bay" leads a title the way a brand does, so a
shopper reads it as a second brand. Public retail listings name a model from plain words
instead, and what makes it read as a model is the part after the word: a generation number, a
sub-model or a code, then a use ("Ghost 18 Road Running Trainers"). The words differ by family:

- sport (running shoes, bikes): a performance word, an optional sub-model and a generation
  number or a code, then a use, e.g. "Tempo Max 3 Trail Running Shoes";
- dress shoes (brogues, loafers): the brand always leads, then an optional name-like model word
  (a first name such as "Merlin"), then the descriptors ``<fit> <material> <style> <type>
  <detail>`` and the color after "in", e.g. "Larkmoor Merlin Leather Smart Penny Loafers in Tan";
- appliances (dishwashers, fridges, laundry): the brand, the series it owns and a model code
  (gen#622, gen#631), e.g. "Frostholm Arden FJ12EW 12 Place Integrated Dishwasher";
- food and drink (pantry, drink, alcohol): the brand always leads, then a plain model word
  (``Basics``, ``Finest``), an optional sub-model and a number, then the product, e.g.
  "Hollin Finest Reserve 2 Strawberry Jam 340g" (gen#665).

A name-like word reads as a brand without its brand in front, so it appears only directly after
the brand (:func:`name_word_misplaced`). A family's model words are dealt to its brands, so a
model word belongs to one brand (gen#642).
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import appliance_model_numbers as amn

#: The food and drink kinds of each food family: the alcohol and the drinks, the rest is pantry.
ALCOHOL_KINDS = (
    "Wine", "Beer", "Cider", "Perry", "Mead", "Gin", "Vodka", "Rum", "Tequila", "Whisky",
    "Champagne", "Fortified Wine",
)  # fmt: skip
DRINK_KINDS = (
    "Tea", "Coffee", "Juice", "Soft Drink", "Milk", "Plant Milk", "Hot Chocolate", "Ginger Beer",
    "Root Beer",
)  # fmt: skip
PANTRY_KINDS = (
    "Baby Food", "Battered Fish", "Biscuit", "Biscuits", "Bread", "Butter & Spreads", "Cake",
    "Cereal", "Cereal Bar", "Cheese", "Chips", "Chocolate Bar", "Chocolate Box",
    "Christmas Pudding", "Chutney", "Cookies", "Crisps", "Doughnut", "Easy Peelers",
    "Festive Bake", "Fish", "Free From Snack", "Fresh Fruit", "Fresh Vegetables",
    "Frozen Vegetables", "Fruit", "Hamper", "Honey", "Ice Cream", "Jam", "Lemons",
    "Letterbox Gift", "Meat", "Nuts & Popcorn", "Olive Oil", "Oranges", "Panettone", "Pasta",
    "Pickle", "Pizza", "Porridge", "Potatoes", "Ready Meal", "Rice & Grains", "Sauce",
    "Seasoning", "Snack Bar", "Spread", "Sugar", "Sweets", "Tinned Food", "Vinegar",
    "World Food", "Yogurt",
)  # fmt: skip

#: product type -> its family. A kind not listed keeps the range names of :mod:`range_ownership`.
FAMILIES = {
    "Running Shoes": "sport",
    "Bicycle": "sport",
    "Brogues": "dress",
    "Loafers": "dress",
    "Dishwasher": "appliance",
    "Fridge & Freezer": "appliance",
    "Laundry Appliance": "appliance",
    **dict.fromkeys(PANTRY_KINDS, "pantry"),
    **dict.fromkeys(DRINK_KINDS, "drink"),
    **dict.fromkeys(ALCOHOL_KINDS, "alcohol"),
}

#: The lead word of a sport model: a performance word.
SPORT_LEADS = (
    "Speed", "Ultra", "Fast", "Sport", "Performance", "Tempo", "Pace", "Race", "Aero", "Glide",
    "Rapid", "Boost", "Surge", "Velocity",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SPORT_SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations a sport model is in.
GENERATIONS = tuple(range(2, 10))
#: What a running shoe is for, between the model and the kind.
SPORT_USES = ("Road", "Trail", "Neutral Road", "Cushioned Road", "Stability Road", "Neutral Trail")

#: The dress-shoe descriptors of public retail listings, in title order.
DRESS_FIT = ("Wide Fit", "WF")
DRESS_MATERIAL = (
    "Leather", "Real Leather", "Faux Leather", "Patent", "Suede", "Faux Suede", "Velvet",
    "Perforated Leather",
)  # fmt: skip
DRESS_STYLE = ("Smart", "Formal", "Classic", "Premium")
DRESS_TYPE = (
    "Derby", "Oxford", "Brogue", "Monk", "Double Monk", "Loafer", "Penny Loafer", "Tassel Loafer",
    "Toe Cap", "Apron Toe", "Ballet Flat",
)  # fmt: skip
DRESS_DETAIL = ("with Broguing Detail", "with Toe Cap", "with Apron Detail", "Two Strap")
DRESS_COLORS = ("Black", "Tan", "Brown", "Navy", "Stone", "Camel", "Wine")

#: The plain model words of a food family. They are plain adjectives, kept disjoint from every
#: other vocabulary on purpose, not a quoted list: only "Finest", "Basics", "Value", "Signature",
#: "Select" and "Choice" are real own-label tiers of public grocery listings. Each family has two
#: halves, one for the grocery build and one for the scale build, so a word belongs to one brand
#: across both (gen#642). A word is no name, no place and no brand-like coinage, and none is in a
#: food title, a description, a flavor, a brand, another family's vocabulary or the first word of
#: any other product's title (the range review of gen#623 would read it as a range shared by two
#: brands).
FOOD_LEADS = {
    "pantry": {
        "grocery": (
            "Trusty", "Humble", "Generous", "Fair", "Honest", "Tasty", "Savoury", "Hearty",
            "Proper", "Wholesome", "Simply", "Gourmet", "Deli", "Artisan", "Rustic", "Supreme",
            "Signature", "Heritage", "Finest", "Select", "Choice", "Homestyle", "Reliable",
            "Authentic", "Prime", "Dependable", "Cherished",
        ),
        "scale": (
            "Sunday", "Weekday", "Basics", "Value", "Steady", "Plenty", "Bountiful", "Kindly",
            "Comfort", "Wholefood",
        ),
    },
    "drink": {
        "grocery": (
            "Brisk", "Lively", "Evening", "Cosy", "Zesty", "Refresh", "Vital", "Balanced",
            "Lunchtime", "Cheery", "Cheerful", "Splash", "Sparkle", "Quench",
        ),
        "scale": (
            "Elevenses", "Teatime", "Poolside", "Winter", "Autumn", "Perky", "Breezy", "Vivid",
        ),
    },
    "alcohol": {
        "grocery": (
            "Cellar", "Grand", "Master", "Imperial", "Royal", "Crown", "Tavern", "Fireside",
            "Gantry", "Snug",
        ),
        "scale": (
            "Sovereign", "Merchant", "Vintner", "Landlord", "Hogshead", "Founders", "Taproom",
            "Regal",
        ),
    },
}  # fmt: skip
#: The sub-model word that may follow a food lead, per family.
FOOD_SUBS = {
    "pantry": ("Reserve", "Special", "Deluxe", "Edition", "Batch", "Series"),
    "drink": ("Batch", "Special", "Reserve", "Edition", "Series", "Deluxe"),
    "alcohol": ("Reserve", "Special", "Edition", "Batch", "Series", "Deluxe"),
}
FOOD_FAMILIES = tuple(FOOD_LEADS)

#: The name-like model words of a dress shoe: first names and place words, as public retail
#: listings use them. Each reads as a brand on its own, so it follows the brand directly.
NAME_WORDS = (
    "Merlin", "Luca", "Oslo", "Strand", "Eton", "Carter", "Clarence", "Connor", "Langdon",
    "Clinton", "Hugo", "Felix", "Arlo", "Rupert", "Jasper", "Milo", "Otis", "Rufus", "Ellis",
    "Hector", "Ivor", "Monty", "Percy", "Cecil", "Barnaby", "Alfie", "Edmund", "Gideon", "Lionel",
    "Nolan", "Oscar", "Quentin", "Roland", "Sidney", "Theo", "Victor", "Walter", "Ralph", "Leon",
    "Elliot", "Duncan",
)  # fmt: skip


def family(rec: dict) -> str | None:
    """The family of ``rec``'s product type, or None for a kind outside the grammar."""
    return FAMILIES.get(rec["product_type"])


def _code(token: str) -> bool:
    """A generation number or a model code: a token with a digit in it."""
    return any(c.isdigit() for c in token)


def is_model(fam: str, brand: str, line: str) -> bool:
    """Whether ``line`` is a model name of ``fam`` built from the family's words alone.

    A sport model is a lead word, then sub-model words, generation numbers or codes, at least
    one of them; a dress model is one name-like word; an appliance model is a series its brand
    owns (gen#622); a food model is a plain lead word of its family, then optionally a sub-model
    and a number (gen#665)."""
    words = line.split()
    if fam in FOOD_LEADS:
        leads = [w for half in FOOD_LEADS[fam].values() for w in half]
        sub, num = (words[1:2] or [None])[0], words[2:]
        return (bool(words) and words[0] in leads and len(words) <= 3
                and (sub is None or sub in FOOD_SUBS[fam])
                and all(_code(w) for w in num))  # fmt: skip
    if fam == "sport":
        rest = words[1:]
        return (len(words) >= 2 and words[0] in SPORT_LEADS
                and all(w in SPORT_SUBS or _code(w) for w in rest))  # fmt: skip
    if fam == "dress":
        return line in NAME_WORDS
    if fam == "appliance":
        return line in amn.SERIES.get(brand, ())
    return False


def name_word_misplaced(rec: dict) -> list[str]:
    """The name-like words in ``rec``'s title that do not come directly after its brand."""
    title, brand = rec["title"], rec["brand"]
    lead = len(brand.split()) if title.startswith(f"{brand} ") else None
    words = re.findall(r"[\w'&]+", title)
    return [w for i, w in enumerate(words) if w in NAME_WORDS and i != lead]


def _lead(fam: str, line: str) -> str:
    """The word of a model that a brand owns: a sport or food model's lead word, a dress model's
    name."""
    return line.split()[0] if fam == "sport" or fam in FOOD_LEADS else line


class Deal:
    """A family's model words dealt over the brands that sell it, so each belongs to one brand
    (gen#642). An authored row's model word stays its brand's (``authored``: word -> brand), and
    the rest are dealt in turn over the brands in name order.

    A sport brand builds its models from its lead words, a generation and, past the first eight
    generations, a sub-model: "Tempo 3", then "Tempo Pro 3". A dress brand names a model with
    one of its name words. A food brand builds a model from its lead words, the lead alone first
    ("Finest"), then with a sub-model ("Finest Reserve") and then with a number ("Finest Reserve
    2"). ``half`` is the half of a food family's lead words this build deals from (gen#665)."""

    def __init__(
        self, fam: str, brands: Iterable[str], authored: dict[str, str], half: str = "scale"
    ) -> None:
        self.fam = fam
        self.brands = sorted(set(brands))
        if fam in FOOD_LEADS:
            words = FOOD_LEADS[fam][half]
            assert len(words) >= len(self.brands), f"{fam}/{half}: {len(self.brands)} brands"
        else:
            words = SPORT_LEADS if fam == "sport" else NAME_WORDS
        pool = [w for w in words if w not in authored]
        count = len(self.brands) or 1
        self._owned = {
            b: tuple([w for w, o in authored.items() if o == b] + pool[i::count])
            for i, b in enumerate(self.brands)
        }

    def of(self, brand: str) -> tuple[str, ...]:
        return self._owned[brand]

    def owned(self, brand: str, slot: int) -> str:
        """The model ``brand`` sells at ``slot``."""
        mine = self._owned[brand]
        word, k = mine[slot % len(mine)], slot // len(mine)
        if self.fam in FOOD_LEADS:
            subs = FOOD_SUBS[self.fam]
            if k == 0:
                return word
            j = k - 1
            if j < len(subs):
                return f"{word} {subs[j]}"
            j -= len(subs)
            number = GENERATIONS[(j // len(subs)) % len(GENERATIONS)]
            return f"{word} {subs[j % len(subs)]} {number}"
        if self.fam != "sport":
            return word
        sub = (None, *SPORT_SUBS)[(k // len(GENERATIONS)) % (len(SPORT_SUBS) + 1)]
        gen = GENERATIONS[k % len(GENERATIONS)]
        return " ".join(str(p) for p in (word, sub, gen) if p)


def deals(tpls: list[dict], brands: dict[tuple[str, str], list[str]]) -> dict[str, Deal]:
    """family -> its :class:`Deal` over every brand a derived style of the family may carry.

    ``brands`` is the scale build's (department, product type) -> brand pool. An authored model
    that is not the family's own (a real brand's) reserves nothing."""
    out = {}
    for fam in ("sport", "dress", *FOOD_FAMILIES):
        authored = {
            _lead(fam, line): r["brand"]
            for r in tpls
            if family(r) == fam and (line := r.get("product_line"))
            and is_model(fam, r["brand"], str(line))
        }  # fmt: skip
        mine = [pool for (_, kind), pool in brands.items() if FAMILIES.get(kind) == fam]
        out[fam] = Deal(fam, [b for pool in mine for b in pool], authored)
    return out


def _strip(title: str, word: str) -> str:
    return title[len(word) + 1 :] if title.startswith(f"{word} ") else title


def retitle(rec: dict, tpl: dict, draw: int) -> None:
    """``rec``'s title in its family's grammar, once :func:`scale.derive` has put its model in.

    The template's brand leaves the title. A sport style then leads with its own brand, after a
    "Kids' " if it has one: "Stridewell Speed 5 Neutral Road Running Shoes". A dress style
    always leads with its brand and the name, and a style word follows the material in four
    draws of five: "Larkmoor Merlin Leather Smart Penny Loafers". A food style leads with its
    brand, then the model: "Hollin Finest Reserve 2 Strawberry Jam".
    ``draw`` is the style's seeded number for these choices."""
    fam, brand, line = family(rec), rec["brand"], str(rec["product_line"])
    title = _strip(rec["title"], tpl["brand"])
    if fam == "sport":
        kids = "Kids' " if title.startswith("Kids' ") else ""
        title = f"{kids}{brand} {title.removeprefix(kids)}"
    elif fam in FOOD_LEADS:
        title = f"{brand} {title}"
    elif fam == "dress":
        rest = _strip(title, line)
        style = (None, *DRESS_STYLE)[draw % (len(DRESS_STYLE) + 1)]
        if style:
            lead = max((m for m in DRESS_MATERIAL if rest.startswith(f"{m} ")), key=len, default="")
            rest = f"{lead} {style} {rest[len(lead) :].strip()}".strip()
        title = f"{brand} {line} {rest}"
    rec["title"] = title


def color_suffix(rec: dict, color: str) -> str:
    """How a title names its color: "... in Tan" for a dress shoe, "..., Tan" otherwise."""
    return f" in {color}" if family(rec) == "dress" else f", {color}"
