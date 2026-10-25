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
- cleaning and beauty (detergent, hand wash, lipstick, creams): the brand, a plain word of the
  category, a sub-model and a number, then the scent or shade and the kind, e.g.
  "Soapwell Gentle Plus 4 Lemon Floor Cleaner" (gen#666).

A name-like word reads as a brand without its brand in front, so it appears only directly after
the brand (:func:`name_word_misplaced`). A family's model words are dealt to its brands, so a
model word belongs to one brand (gen#642).
"""

from __future__ import annotations

import re
from collections.abc import Iterable

import appliance_model_numbers as amn

#: product type -> its family. A kind not listed keeps the range names of :mod:`range_ownership`.
FAMILIES = {
    "Running Shoes": "sport",
    "Bicycle": "sport",
    "Brogues": "dress",
    "Loafers": "dress",
    "Dishwasher": "appliance",
    "Fridge & Freezer": "appliance",
    "Laundry Appliance": "appliance",
    **dict.fromkeys(
        (
            "Laundry Detergent", "Floor Cleaner", "Bathroom Cleaner", "Dish Soap", "Glass Cleaner",
            "Air Freshener", "Fabric Softener", "Kitchen Cleaner", "Toilet Cleaner",
        ),
        "cleaning",
    ),
    **dict.fromkeys(
        (
            "Hand Wash", "Shower Gel", "Lipstick", "Foundation", "Hand Cream", "Body Cream",
            "Eye Cream", "Foot Cream", "Body Lotion", "Moisturiser", "Conditioner", "Shampoo",
            "Wash Bag", "Make-Up Bag", "Lip Balm", "Eyeliner", "Perfume",
        ),
        "beauty",
    ),
}  # fmt: skip

#: The lead word of a sport model: a performance word.
SPORT_LEADS = (
    "Speed", "Ultra", "Fast", "Sport", "Performance", "Tempo", "Pace", "Race", "Aero", "Glide",
    "Rapid", "Boost", "Surge", "Velocity",
)  # fmt: skip
#: The sub-model word that may follow the lead.
SPORT_SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations a sport model is in.
GENERATIONS = tuple(range(2, 10))
#: The lead word of a cleaning model: a plain word of public household-care listings
#: ("Gentle", "Total", "Strong"). None is a name, a place or a word another family uses.
CLEAN_LEADS = (
    "Gentle", "Total", "Intense", "Express", "Advanced", "Ultimate", "Strong", "Maximum", "Turbo",
    "Mighty", "Dynamic", "Precision", "Optimum", "Prime", "Tough", "Sparkle", "Spotless", "Gleam",
    "Force", "Fusion", "Shield", "Defence", "Energy", "Core", "Focus", "Clarity", "Vital",
    "Select", "Premier", "Expert", "Ideal", "Swift",
)  # fmt: skip
#: The lead word of a beauty model: a plain word of public beauty listings ("Lasting", "Perfect").
BEAUTY_LEADS = (
    "Lasting", "Perfect", "Flawless", "Nurture", "Renew", "Revive", "Comfort", "Longwear",
    "Infinite", "Absolute", "Elegance", "Allure", "Ritual", "Tender", "Lustre", "Define", "Sculpt",
    "Enhance", "Devotion", "Delight", "Indulge", "Whisper", "Cherish", "Treasure", "Desire",
    "Sublime", "Exquisite", "Divine", "Luxe", "Vitality", "Glamour", "Poise", "Refine", "Restore",
    "Replenish", "Hydrate", "Soothe", "Prestige", "Serenity", "Supple",
)  # fmt: skip
#: The sub-model words that may follow a cleaning or beauty lead.
CLEAN_SUBS = ("Plus", "Max", "Pro", "Ultra", "Extra")
BEAUTY_SUBS = ("Plus", "Lite", "Rich", "Pro", "Extra")

#: family -> its lead words and its sub-model words, for the families whose model is a lead
#: word, a sub-model and a number. Each lead word is dealt to one brand (gen#642).
LEADS = {"sport": SPORT_LEADS, "cleaning": CLEAN_LEADS, "beauty": BEAUTY_LEADS}
SUBS = {"sport": SPORT_SUBS, "cleaning": CLEAN_SUBS, "beauty": BEAUTY_SUBS}
#: The scale build deals the even lead words and the grocery build the odd ones, so a lead word
#: of a cleaning or beauty model is one brand's across both builds (gen#666).
HALVES = {"scale": 0, "grocery": 1}
#: The families whose title leads with the brand and a model, then the scent or shade.
CARE = ("cleaning", "beauty")

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

    A sport, cleaning or beauty model is a lead word, then sub-model words, generation numbers
    or codes, at least one of them; a dress model is one name-like word; an appliance model is a
    series its brand owns (gen#622)."""
    words = line.split()
    if fam in LEADS:
        rest = words[1:]
        return (len(words) >= 2 and words[0] in LEADS[fam]
                and all(w in SUBS[fam] or _code(w) for w in rest))  # fmt: skip
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
    """The word of a model that a brand owns: its lead word, or a dress model's name."""
    return line.split()[0] if fam in LEADS else line


class Deal:
    """A family's model words dealt over the brands that sell it, so each belongs to one brand
    (gen#642). An authored row's model word stays its brand's (``authored``: word -> brand), and
    the rest are dealt in turn over the brands in name order.

    A sport, cleaning or beauty brand builds its models from its lead words, a generation and,
    past the first eight generations, a sub-model: "Tempo 3", then "Tempo Pro 3". A dress brand
    names a model with one of its name words.

    ``half`` (0 or 1) deals only the even or the odd lead words of a cleaning or beauty family,
    so a second build (the grocery one) can deal the other half to its own brands without
    giving one word to two brands (gen#666)."""

    def __init__(
        self, fam: str, brands: Iterable[str], authored: dict[str, str], half: int | None = None
    ) -> None:
        self.fam = fam
        self.brands = sorted(set(brands))
        words = LEADS.get(fam, NAME_WORDS)
        if half is not None:
            words = words[half::2]
        pool = [w for w in words if w not in authored]
        count = len(self.brands) or 1
        self._owned = {
            b: tuple([w for w, o in authored.items() if o == b] + pool[i::count])
            for i, b in enumerate(self.brands)
        }
        bare = [b for b, mine in self._owned.items() if not mine]
        if bare:
            raise ValueError(f"{fam}: {len(pool)} words for {len(self.brands)} brands: {bare}")

    def of(self, brand: str) -> tuple[str, ...]:
        return self._owned[brand]

    def owned(self, brand: str, slot: int) -> str:
        """The model ``brand`` sells at ``slot``."""
        mine = self._owned[brand]
        word, k = mine[slot % len(mine)], slot // len(mine)
        if self.fam not in LEADS:
            return word
        subs = (None, *SUBS[self.fam])
        if self.fam in CARE:
            # A care model sits in a short title, so two of one brand's models that differ in a
            # single token read as one listing (Jaccard 0.8). The sub-model and the generation
            # both move with each reuse of a word and with the word's place in the brand's list.
            shift = slot % len(mine) + k
            sub = subs[shift % len(subs)]
            gen = GENERATIONS[(shift + k // (len(subs) * 4)) % len(GENERATIONS)]
        else:
            sub = subs[(k // len(GENERATIONS)) % len(subs)]
            gen = GENERATIONS[k % len(GENERATIONS)]
        return " ".join(str(p) for p in (word, sub, gen) if p)


def deals(tpls: list[dict], brands: dict[tuple[str, str], list[str]]) -> dict[str, Deal]:
    """family -> its :class:`Deal` over every brand a derived style of the family may carry.

    ``brands`` is the scale build's (department, product type) -> brand pool. An authored model
    that is not the family's own (a real brand's) reserves nothing."""
    out = {}
    for fam in (*LEADS, "dress"):
        authored = {
            _lead(fam, line): r["brand"]
            for r in tpls
            if family(r) == fam and (line := r.get("product_line"))
            and is_model(fam, r["brand"], str(line))
        }  # fmt: skip
        mine = [pool for (_, kind), pool in brands.items() if FAMILIES.get(kind) == fam]
        half = HALVES["scale"] if fam in CARE else None
        out[fam] = Deal(fam, [b for pool in mine for b in pool], authored, half)
    return out


def _strip(title: str, word: str) -> str:
    return title[len(word) + 1 :] if title.startswith(f"{word} ") else title


def retitle(rec: dict, tpl: dict, draw: int) -> None:
    """``rec``'s title in its family's grammar, once :func:`scale.derive` has put its model in.

    The template's brand leaves the title. A sport style then leads with its own brand, after a
    "Kids' " if it has one: "Stridewell Speed 5 Neutral Road Running Shoes". A dress style
    always leads with its brand and the name, and a style word follows the material in four
    draws of five: "Larkmoor Merlin Leather Smart Penny Loafers". A cleaning or beauty style
    leads with its brand and its model, then the scent or shade and the kind: "Soapwell Gentle
    Plus 4 Lemon Floor Cleaner". ``draw`` is the style's seeded number for these choices."""
    fam, brand, line = family(rec), rec["brand"], str(rec["product_line"])
    title = _strip(rec["title"], tpl["brand"])
    if fam == "sport":
        kids = "Kids' " if title.startswith("Kids' ") else ""
        title = f"{kids}{brand} {title.removeprefix(kids)}"
    elif fam in CARE:
        # The model and the brand may each lead the title (a template names its brand by its
        # first word), so both leave it before they come back in order.
        first = tpl["brand"].split()[0]
        for _ in range(2):
            for word in (line, brand, tpl["brand"], first):
                title = _strip(title, word)
        title = f"{brand} {line} {title}"
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
