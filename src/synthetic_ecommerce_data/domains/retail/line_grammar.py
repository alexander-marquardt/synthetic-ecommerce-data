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

A name-like word reads as a brand without its brand in front, so it appears only directly after
the brand (:func:`name_word_misplaced`). A family's model words are dealt to its brands, so a
model word belongs to one brand (gen#642).

``tests/test_line_grammar_families_513.py`` holds the family contract, and
``scripts/check_no_registry_append.py`` refuses a line appended to this file: a family is a
module, not a row, a constant and a branch here.
"""

from __future__ import annotations

import re
import zlib
from collections.abc import Callable, Iterable

from synthetic_ecommerce_data.domains.retail import appliance_model_numbers as amn
from synthetic_ecommerce_data.domains.retail import line_grammar_families

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
FAMILIES = (
    {kind: fam.name for fam in _NUMBERED.values() for kind in fam.kinds}
    | _CORE
)


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
    series its brand owns (gen#622); a food model is a plain lead word of its family, then
    optionally one of its style words, and never a number (gen#665, gen#729)."""
    words = line.split()
    if fam in _NUMBERED:
        spec = _NUMBERED[fam]
        rest = words[1:]
        leads = (*spec.leads, *spec.grocery_leads)
        if spec.bare:
            return words[0] in leads and (not rest or " ".join(rest) in spec.subs)
        return (len(words) >= 2 and words[0] in leads
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
    """The word of a model that a brand owns: a numbered or food model's lead word, a dress
    model's name."""
    return line.split()[0] if fam in _NUMBERED else line


class Deal:
    """A family's model words dealt over the brands that sell it, so each belongs to one brand
    (gen#642). An authored row's model word stays its brand's (``authored``: word -> brand), and
    the rest are dealt in turn over the brands in name order.

    A numbered-family brand builds its models from its lead words, a generation and, past the
    first cycle of generations, a sub-model: "Tempo 3", then "Tempo Pro 3". A dress brand names a
    model with one of its name words. A food brand builds a model from its lead words, the lead
    alone first ("Finest"), then with each style word of the kind ("Finest Greek Style"). Past
    those the models repeat and :meth:`round` tells the caller how far past it went, so a title
    gains a true ingredient or claim of its own (:mod:`food_title_words`), never a number or an
    empty word (gen#729). ``half`` is the half of a food family's lead words this build deals from
    (gen#665). A cleaning or beauty family has one lead list and splits it instead: the scale build
    deals its even words and the grocery build its odd ones (:data:`HALVES`, gen#666)."""

    def __init__(
        self, fam: str, brands: Iterable[str], authored: dict[str, str], half: str = "scale"
    ) -> None:
        self.fam = fam
        self.brands = sorted(set(brands))
        self.spec = _NUMBERED.get(fam)
        if self.spec:
            if fam in CARE:
                words = self.spec.leads[HALVES[half] :: 2]
            else:
                words = self.spec.grocery_leads if half == "grocery" else self.spec.leads
            assert len(words) >= len(self.brands), f"{fam}/{half}: {len(self.brands)} brands"
        else:
            words = NAME_WORDS
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

    def owned(self, brand: str, slot: int, kind: str = "") -> str:
        """The model ``brand`` sells at ``slot``; a food family words it for its ``kind``."""
        mine = self._owned[brand]
        word, k = mine[slot % len(mine)], slot // len(mine)
        if self.spec and self.spec.bare:
            style = (None, *self.spec.styles[kind])[k % (len(self.spec.styles[kind]) + 1)]
            return f"{word} {style}" if style else word
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

    def round(self, brand: str, slot: int, kind: str) -> int:
        """How many times a food family's ``slot`` has gone through ``brand``'s models of
        ``kind``: 0 is the first pass, and a later one names a model an earlier one named."""
        spec = self.spec
        assert spec is not None and spec.bare, self.fam
        return slot // len(self._owned[brand]) // (len(spec.styles[kind]) + 1)


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
    for fam in (*NUMBERED, "dress"):
        authored = {
            _lead(fam, line): r["brand"]
            for r in tpls
            if family(r) == fam and (line := _stated(r))
            and is_model(fam, r["brand"], str(line))
        }  # fmt: skip
        mine = [pool for (_, kind), pool in brands.items() if FAMILIES.get(kind) == fam]
        out[fam] = Deal(fam, [b for pool in mine for b in pool], authored)
    return out


def brand_led(key: object) -> bool:
    """Whether the food title seeded by ``key`` leads with its brand: two in three do (gen#665).

    Real listings do not all name the brand, and the shorter ones are the demo's decoy-friendly
    titles, so the rest keep the model alone."""
    return zlib.crc32(str(key).encode()) % 3 != 0


def _strip(title: str, word: str) -> str:
    return title[len(word) + 1 :] if title.startswith(f"{word} ") else title


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
    one, would read "Treadmoor Treadmoor Pace Max 3"). A numbered-family style then leads with
    its own brand, after a "Kids' " if it has one: "Stridewell Speed 5 Neutral Road Running
    Shoes". A dress style always leads with its brand and the name, and a style word follows the
    material in four draws of five: "Larkmoor Merlin Leather Smart Penny Loafers". A food style
    leads with its brand, then the model, in two draws of three ("Hollin Finest Small Batch
    Strawberry Jam"); the others keep the model alone (:func:`brand_led`). A cleaning or beauty
    style leads with its brand and its model, then the scent or shade and the kind: "Soapwell Keen
    Plus 4 Lemon Floor Cleaner". ``draw`` is the style's seeded number for these choices."""
    fam, brand, line = family(rec), rec["brand"], str(rec["product_line"])
    brands = (tpl["brand"], brand)
    title = _peel(rec["title"], brands)
    if fam in CARE:
        # The model and the brand may each lead the title (a template names its brand by its
        # first word), so all of them leave it before they come back in order.
        title = _peel(title, (*brands, line, tpl["brand"].split()[0]))
        title = f"{brand} {line} {title}"
    elif fam in _NUMBERED:
        kids = "Kids' " if title.startswith("Kids' ") else ""
        title = _peel(title.removeprefix(kids), brands)
        title = _strip(title, "The") if title.startswith(f"The {line} ") else title
        if title.startswith(f"{line} {brand} "):  # a template that led with its brand
            title = f"{line} {title[len(line) + len(brand) + 2 :]}"
        if not _NUMBERED[fam].mixed_brand or brand_led(draw):
            title = f"{kids}{brand} {title}"
        else:
            title = f"{kids}{title}"
    elif fam == "dress":
        rest = _peel(title, (*brands, line))
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
        fam = family(rec)
        if (fam in NUMBERED and not _NUMBERED[fam].mixed_brand and line
                and rec["title"].startswith(f"{line} ")
                and not rec["title"].startswith(f"{rec['brand']} ")):  # fmt: skip
            rec["title"] = f"{rec['brand']} {rec['title']}"
    return recs


def color_suffix(rec: dict, color: str) -> str:
    """How a title names its color: "... in Tan" for a dress shoe, "..., Tan" otherwise."""
    return f" in {color}" if family(rec) == "dress" else f", {color}"
