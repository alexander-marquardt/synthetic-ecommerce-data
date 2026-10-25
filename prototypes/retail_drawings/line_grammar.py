"""The model-name grammar of a product line, per category family (gen#662).

A range name such as "Cloudrise" or "Cardigan Bay" leads a title the way a brand does, so a
shopper reads it as a second brand. Public retail listings name a model from plain words
instead, and what makes it read as a model is the part after the word: a generation number, a
sub-model or a code, then a use ("Ghost 18 Road Running Trainers"). The words differ by family:

- sport (running shoes, bikes): a performance word, an optional sub-model and a generation
  number or a code, then a use, e.g. "Tempo Max 3 Trail Running Shoes";
- bras, jeans, tees, trainers, boots and casual shoes (gen#663): the same shape from a family
  vocabulary of its own (:data:`VOCAB`), the brand first, e.g. "Bramblewood Comfort Pro 3
  Underwired Balcony Bra" or "Ottery Denim Original 101 High Rise Straight Jeans";
- dress shoes (brogues, loafers): the brand always leads, then an optional name-like model word
  (a first name such as "Merlin"), then the descriptors ``<fit> <material> <style> <type>
  <detail>`` and the color after "in", e.g. "Larkmoor Merlin Leather Smart Penny Loafers in Tan";
- appliances (dishwashers, fridges, laundry): the brand, the series it owns and a model code
  (gen#622, gen#631), e.g. "Frostholm Arden FJ12EW 12 Place Integrated Dishwasher".

A name-like word reads as a brand without its brand in front, so it appears only directly after
the brand (:func:`name_word_misplaced`). A family's model words are dealt to its brands, so a
model word belongs to one brand (gen#642).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from dataclasses import dataclass

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
    "Bra": "bra",
    "Jeans": "jeans",
    "Tee": "tee",
    "T-Shirt": "tee",
    "Trainers": "trainers",
    "Platform Trainers": "trainers",
    "Plimsolls": "trainers",
    "Barefoot Shoes": "trainers",
    "Walking Boots": "boots",
    "Chelsea Boots": "boots",
    "Ankle Boots": "boots",
    "Chukka Boots": "boots",
    "Knee High Boots": "boots",
    "Wellies": "boots",
    "Safety Boots": "boots",
    "Espadrilles": "casual",
    "Slippers": "casual",
    "Wedges": "casual",
    "Mules": "casual",
    "Sandals": "casual",
    "Clogs": "casual",
    "Jelly Shoes": "casual",
}  # fmt: skip


@dataclass(frozen=True)
class Vocab:
    """The words of a family whose model reads "<lead> [<sub>] <number>" (#663): the lead words
    its brands own, the sub-model words and the numbers or codes that follow."""

    leads: tuple[str, ...]
    numbers: tuple[int, ...]
    subs: tuple[str, ...] = ()


#: The sub-model word that may follow the lead.
SPORT_SUBS = ("Pro", "Max", "Elite", "Edge", "Lite", "Plus")
#: The generations a sport model is in.
GENERATIONS = tuple(range(2, 10))

#: family -> its vocabulary (#663), for the families that follow the sport structure. Each word is
#: a plain English word of public retail listings (Nike "Pegasus", Clarks "Desert", Levi's
#: "Original"); no lead is a coined brand-sounding word, a place name or a first name.
VOCAB = {
    "bra": Vocab(
        ("Comfort", "Support", "Everyday", "Balance", "Form", "Lift", "Shape", "Grace", "Poise",
         "Serene", "Haven", "Essence", "Harmony", "Bloom", "Charm", "Halo", "Aura", "Ease"),
        GENERATIONS, SPORT_SUBS,
    ),
    "jeans": Vocab(
        ("Original", "Heritage", "Core", "Authentic", "Staple", "Standard", "Icon", "Legacy",
         "Rider", "Ranger", "Drover", "Workwear", "Frontier", "Rodeo", "Basic", "Utility",
         "Craft", "Origin", "Anchor", "Forge", "Foundry", "Cadet"),
        (101, 205, 312, 418, 520, 625, 731, 840), SPORT_SUBS,
    ),
    "tee": Vocab(
        ("Daily", "Casual", "Weekend", "Easy", "Simple", "Fresh", "Breeze", "Sunday", "Saturday",
         "Studio", "Campus", "Varsity", "Retro", "Street", "Urban", "Skate", "Surf", "Camp",
         "Field", "Garage", "Social", "Club", "Lounge", "Basecamp"),
        GENERATIONS, SPORT_SUBS,
    ),
    "trainers": Vocab(
        ("Dash", "Cruise", "Court", "Terrace", "Flex", "Sprint", "Bounce", "Rally", "Volley",
         "Drift", "Orbit", "Pulse", "Spark", "Apex", "Vector", "Stealth", "Jump", "Hoop", "Lunge",
         "Switch"),
        GENERATIONS, SPORT_SUBS,
    ),
    "boots": Vocab(
        ("Summit", "Ascent", "Alpine", "Grit", "Rugged", "Anvil", "Timber", "Bedrock", "Granite",
         "Puddle", "Drizzle", "Storm", "Gale", "Hardy", "Sturdy", "Trek", "Wander", "Roam",
         "Ramble", "Scout", "Pioneer", "Forager", "Stomp", "Boulder"),
        GENERATIONS, SPORT_SUBS,
    ),
    "casual": Vocab(
        ("Siesta", "Fiesta", "Sorbet", "Mellow", "Cosy", "Snug", "Plush", "Lazy", "Sunset",
         "Sunrise", "Poolside", "Lido", "Parasol", "Gelato", "Picnic", "Hammock", "Tropic",
         "Carnival", "Flutter", "Twirl", "Swish", "Bliss", "Zest", "Cheer"),
        GENERATIONS, SPORT_SUBS,
    ),
}  # fmt: skip

#: The lead word of a sport model: a performance word.
SPORT_LEADS = (
    "Speed", "Ultra", "Fast", "Sport", "Performance", "Tempo", "Pace", "Race", "Aero", "Glide",
    "Rapid", "Boost", "Surge", "Velocity",
)  # fmt: skip
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

    A sport model is a lead word, then sub-model words, generation numbers or codes, at least
    one of them; a model of a :data:`VOCAB` family is one of its lead words, then its sub-model
    words and numbers, at least one number; a dress model is one name-like word; an appliance
    model is a series its brand owns (gen#622)."""
    words = line.split()
    if fam == "sport":
        rest = words[1:]
        return (len(words) >= 2 and words[0] in SPORT_LEADS
                and all(w in SPORT_SUBS or _code(w) for w in rest))  # fmt: skip
    if fam in VOCAB:
        vocab, rest = VOCAB[fam], words[1:]
        return (len(words) >= 2 and words[0] in vocab.leads
                and all(w in vocab.subs or w in map(str, vocab.numbers) for w in rest)
                and any(w in map(str, vocab.numbers) for w in rest))  # fmt: skip
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
    """The word of a model that a brand owns: the lead word of a model that has more words, a
    dress model's name."""
    return line if fam == "dress" else line.split()[0]


def _words(fam: str) -> tuple[str, ...]:
    """The words a family deals over its brands."""
    if fam == "sport":
        return SPORT_LEADS
    return VOCAB[fam].leads if fam in VOCAB else NAME_WORDS


class Deal:
    """A family's model words dealt over the brands that sell it, so each belongs to one brand
    (gen#642). An authored row's model word stays its brand's (``authored``: word -> brand), and
    the rest are dealt in turn over the brands in name order.

    A sport or :data:`VOCAB` brand builds its models from its lead words, a number and, past the
    first run of numbers, a sub-model: "Tempo 3", then "Tempo Pro 3". A dress brand names a model
    with one of its name words."""

    def __init__(self, fam: str, brands: Iterable[str], authored: dict[str, str]) -> None:
        self.fam = fam
        self.brands = sorted(set(brands))
        pool = [w for w in _words(fam) if w not in authored]
        count = len(self.brands) or 1
        self._owned = {
            b: tuple([w for w, o in authored.items() if o == b] + pool[i::count])
            for i, b in enumerate(self.brands)
        }
        vocab = VOCAB.get(fam)
        self._numbers = vocab.numbers if vocab else GENERATIONS
        self._subs = vocab.subs if vocab else SPORT_SUBS

    def of(self, brand: str) -> tuple[str, ...]:
        return self._owned[brand]

    def owned(self, brand: str, slot: int) -> str:
        """The model ``brand`` sells at ``slot``."""
        mine = self._owned[brand]
        word, k = mine[slot % len(mine)], slot // len(mine)
        if self.fam == "dress":
            return word
        sub = (None, *self._subs)[(k // len(self._numbers)) % (len(self._subs) + 1)]
        number = self._numbers[k % len(self._numbers)]
        return " ".join(str(p) for p in (word, sub, number) if p)


def _stated(rec: dict) -> str | None:
    """The model a row states: its ``product_line``, or the ``Line`` attribute an authored
    bra or jeans style carries."""
    if rec.get("product_line"):
        return str(rec["product_line"])
    return next((str(a["value"]) for a in rec.get("attributes", ()) if a["key"] == "line"), None)


def deals(tpls: list[dict], brands: dict[tuple[str, str], list[str]]) -> dict[str, Deal]:
    """family -> its :class:`Deal` over every brand a derived style of the family may carry.

    ``brands`` is the scale build's (department, product type) -> brand pool. An authored model
    that is not the family's own (a real brand's) reserves nothing."""
    out = {}
    for fam in ("sport", "dress", *VOCAB):
        authored = {
            _lead(fam, line): r["brand"]
            for r in tpls
            if family(r) == fam and (line := _stated(r))
            and is_model(fam, r["brand"], str(line))
        }  # fmt: skip
        mine = [pool for (_, kind), pool in brands.items() if FAMILIES.get(kind) == fam]
        out[fam] = Deal(fam, [b for pool in mine for b in pool], authored)
    return out


def _peel(title: str, words: Iterable[str]) -> str:
    """``title`` without any of ``words`` leading it, however many times and in any order."""
    done = False
    while not done:
        done = True
        for w in words:
            if title.startswith(f"{w} "):
                title, done = title[len(w) + 1 :], False
    return title


def retitle(rec: dict, tpl: dict, draw: int) -> None:
    """``rec``'s title in its family's grammar, once :func:`scale.derive` has put its model in.

    The template's brand and the drawn brand leave the title first (the template's, or a doubled
    one, would read "Treadmoor Treadmoor Pace Max 3"). A sport style then leads with its own
    brand, after a "Kids' " if it has one: "Stridewell Speed 5 Neutral Road Running Shoes". A
    dress style always leads with its brand and the name, and a style word follows the material in
    four draws of five: "Larkmoor Merlin Leather Smart Penny Loafers". A style of a
    :data:`VOCAB` family leads with its brand and its model: "Bramblewood Comfort Pro 3
    Underwired Balcony Bra". ``draw`` is the style's seeded number for these choices."""
    fam, brand, line = family(rec), rec["brand"], str(rec["product_line"])
    kids = "Kids' " if rec["title"].startswith("Kids' ") else ""
    title = rec["title"].removeprefix(kids)
    brands = (tpl["brand"], brand)
    if fam == "sport":
        title = f"{kids}{brand} {_peel(title, brands)}"
    elif fam == "dress":
        rest = _peel(title, (*brands, line))
        style = (None, *DRESS_STYLE)[draw % (len(DRESS_STYLE) + 1)]
        if style:
            lead = max((m for m in DRESS_MATERIAL if rest.startswith(f"{m} ")), key=len, default="")
            rest = f"{lead} {style} {rest[len(lead) :].strip()}".strip()
        title = f"{brand} {line} {rest}"
    else:
        title = f"{kids}{brand} {line} {_peel(title, (*brands, line, 'The'))}"
    rec["title"] = title


def color_suffix(rec: dict, color: str) -> str:
    """How a title names its color: "... in Tan" for a dress shoe, "..., Tan" otherwise."""
    return f" in {color}" if family(rec) == "dress" else f", {color}"
