"""The model-name grammar of a product line, per category family (gen#662).

A range name such as "Cloudrise" or "Cardigan Bay" leads a title the way a brand does, so a
shopper reads it as a second brand. Public retail listings name a model from plain words
instead, and what makes it read as a model is the part after the word: a generation number, a
sub-model or a code, then a use ("Ghost 18 Road Running Trainers"). The words differ by family:

- numbered families (sport: running shoes, bikes): a lead word, an optional sub-model and a
  generation number or a code, then a use, e.g. "Tempo Max 3 Trail Running Shoes". Each is a
  module of ``line_grammar_families/``, found by walking the package (gen#513), so a new one
  edits no file here;
- dress shoes (brogues, loafers): the brand always leads, then an optional name-like model word
  (a first name such as "Merlin"), then the descriptors ``<fit> <material> <style> <type>
  <detail>`` and the color after "in", e.g. "Larkmoor Merlin Leather Smart Penny Loafers in Tan";
- appliances (dishwashers, fridges, laundry): the brand, the series it owns and a model code
  (gen#622, gen#631), e.g. "Frostholm Arden FJ12EW 12 Place Integrated Dishwasher";
- the home, gifts, garden and toys kinds (gen#664): the same shape with a plain word of the
  family, e.g. "Stridewell Beam Plus 300 Fabric Shade Floor Lamp".

- cleaning and beauty (modules ``cleaning`` and ``beauty``, gen#666): the brand, a plain word of
  the category, a sub-model and a number, then the scent or shade and the kind, e.g.
  "Soapwell Keen Plus 4 Lemon Floor Cleaner".

A name-like word reads as a brand without its brand in front, so it appears only directly after
the brand (:func:`name_word_misplaced`). A family's model words are dealt to its brands, so a
model word belongs to one brand (gen#642).

``tests/test_line_grammar_families_513.py`` holds the family contract, and
``scripts/check_no_registry_append.py`` refuses a line appended to this file: a family is a
module, not a row, a constant and a branch here.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Iterable

import appliance_model_numbers as amn
import line_grammar_families

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

#: The product types of the core families, whose model shapes are their own.
_CORE = {
    "Brogues": "dress",
    "Loafers": "dress",
    "Dishwasher": "appliance",
    "Fridge & Freezer": "appliance",
    "Laundry Appliance": "appliance",
}
#: The numbered families: a module of ``line_grammar_families/`` each, by name.
_NUMBERED = line_grammar_families.families(core_kinds=_CORE, reserved=NAME_WORDS)
#: The names of the numbered families.
NUMBERED = tuple(_NUMBERED)
#: The scale build deals the even lead words of a cleaning or beauty family and the grocery build
#: the odd ones, so a lead word of a care model is one brand's across both builds (gen#666).
HALVES = {"scale": 0, "grocery": 1}
#: The families whose title leads with the brand and a model, then the scent or shade.
CARE = ("cleaning", "beauty")
#: product type -> its family. A kind not listed keeps the range names of :mod:`range_ownership`.
FAMILIES = {kind: fam.name for fam in _NUMBERED.values() for kind in fam.kinds} | _CORE


def family(rec: dict) -> str | None:
    """The family of ``rec``'s product type, or None for a kind outside the grammar."""
    return FAMILIES.get(rec["product_type"])


def _code(token: str) -> bool:
    """A generation number or a model code: a token with a digit in it."""
    return any(c.isdigit() for c in token)


def is_model(fam: str, brand: str, line: str) -> bool:
    """Whether ``line`` is a model name of ``fam`` built from the family's words alone.

    A numbered model is a lead word of the family, then sub-model words, generation numbers or
    codes, at least one of them; a dress model is one name-like word; an appliance model is a
    series its brand owns (gen#622)."""
    words = line.split()
    if fam in _NUMBERED:
        spec = _NUMBERED[fam]
        rest = words[1:]
        return (len(words) >= 2 and words[0] in spec.leads
                and all(w in spec.subs or _code(w) for w in rest))  # fmt: skip
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
    """The word of a model that a brand owns: a numbered model's lead word, a dress model's name."""
    return line.split()[0] if fam in _NUMBERED else line


class Deal:
    """A family's model words dealt over the brands that sell it, so each belongs to one brand
    (gen#642). An authored row's model word stays its brand's (``authored``: word -> brand), and
    the rest are dealt in turn over the brands in name order.

    A numbered-family brand builds its models from its lead words, a generation and, past the
    first cycle of generations, a sub-model: "Tempo 3", then "Tempo Pro 3". A dress brand names a
    model with one of its name words.

    ``half`` (0 or 1) deals only the even or the odd lead words of a cleaning or beauty family,
    so a second build (the grocery one) can deal the other half to its own brands without
    giving one word to two brands (gen#666)."""

    def __init__(
        self, fam: str, brands: Iterable[str], authored: dict[str, str], half: int | None = None
    ) -> None:
        self.fam = fam
        self.brands = sorted(set(brands))
        self.spec = _NUMBERED.get(fam)
        words = self.spec.leads if self.spec else NAME_WORDS
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
        if not self.spec:
            return word
        subs, numbers = self.spec.subs, self.spec.numbers
        if self.fam in CARE:
            # A care model sits in a short title, so two of one brand's models that differ in a
            # single token read as one listing (Jaccard 0.8). The sub-model and the generation
            # both move with each reuse of a word and with the word's place in the brand's list.
            shift = slot % len(mine) + k
            sub = (None, *subs)[shift % (len(subs) + 1)]
            gen = numbers[(shift + k // ((len(subs) + 1) * 4)) % len(numbers)]
        else:
            sub = (None, *subs)[(k // len(numbers)) % (len(subs) + 1)]
            gen = numbers[k % len(numbers)]
        return " ".join(str(p) for p in (word, sub, gen) if p)


def deals(tpls: list[dict], brands: dict[tuple[str, str], list[str]]) -> dict[str, Deal]:
    """family -> its :class:`Deal` over every brand a derived style of the family may carry.

    ``brands`` is the scale build's (department, product type) -> brand pool. An authored model
    that is not the family's own (a real brand's) reserves nothing."""
    out = {}
    for fam in (*NUMBERED, "dress"):
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

    The template's brand leaves the title. A numbered-family style then leads with its own
    brand, after a "Kids' " if it has one: "Stridewell Speed 5 Neutral Road Running Shoes". A dress
    style always leads with its brand and the name, and a style word follows the material in four
    draws of five: "Larkmoor Merlin Leather Smart Penny Loafers". A cleaning or beauty style
    leads with its brand and its model, then the scent or shade and the kind: "Soapwell Gentle
    Plus 4 Lemon Floor Cleaner". ``draw`` is the style's seeded number for these choices."""
    fam, brand, line = family(rec), rec["brand"], str(rec["product_line"])
    title = _strip(rec["title"], tpl["brand"])
    if fam in CARE:
        # The model and the brand may each lead the title (a template names its brand by its
        # first word), so both leave it before they come back in order.
        first = tpl["brand"].split()[0]
        for _ in range(2):
            for word in (line, brand, tpl["brand"], first):
                title = _strip(title, word)
        title = f"{brand} {line} {title}"
    elif fam in _NUMBERED:
        kids = "Kids' " if title.startswith("Kids' ") else ""
        title = title.removeprefix(kids)
        title = _strip(title, "The") if title.startswith(f"The {line} ") else title
        if title.startswith(f"{line} {brand} "):  # a template that led with its brand
            title = f"{line} {title[len(line) + len(brand) + 2 :]}"
        title = f"{kids}{brand} {title}"
    elif fam == "dress":
        rest = _strip(title, line)
        style = (None, *DRESS_STYLE)[draw % (len(DRESS_STYLE) + 1)]
        if style:
            lead = max((m for m in DRESS_MATERIAL if rest.startswith(f"{m} ")), key=len, default="")
            rest = f"{lead} {style} {rest[len(lead) :].strip()}".strip()
        title = f"{brand} {line} {rest}"
    rec["title"] = title


def lead_with_brand(recs: list[dict], line_of: Callable[[dict], str | None]) -> list[dict]:
    """``recs`` with every authored title of a numbered family that opens on its model put after
    its brand (gen#664): "Harwell Velvet Corner Sofa" is "Brackenmere Home Harwell Velvet Corner
    Sofa". ``line_of`` gives a row's model name."""
    for rec in recs:
        line = line_of(rec)
        if family(rec) in NUMBERED and line and rec["title"].startswith(f"{line} "):
            rec["title"] = f"{rec['brand']} {rec['title']}"
    return recs


def color_suffix(rec: dict, color: str) -> str:
    """How a title names its color: "... in Tan" for a dress shoe, "..., Tan" otherwise."""
    return f" in {color}" if family(rec) == "dress" else f", {color}"
