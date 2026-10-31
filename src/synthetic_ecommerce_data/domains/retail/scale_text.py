"""The keys and the words of a derived style: what varies and what it reads (:mod:`scale`)."""

from __future__ import annotations

import collections
import re

from synthetic_ecommerce_data.core.standard import words
from synthetic_ecommerce_data.domains.retail import line_grammar

#: Keys whose value never changes: who it is for, its name, its size range, the
#: pattern the drawing shows, how many motifs it prints where (the drawing's
#: ``count`` and ``placement``, which the description's wording follows), a
#: light's build (gen#197): a wall light's ``ip_rating`` (a bathroom light's text says
#: where it may go) and what a lampshade's ring fits (``fitting``).
#: A tableware kind (gen#198) fixes the drawn profile and the measured size beside it, so a
#: 27 cm dinner plate never becomes a side plate.
FROZEN_KEYS = frozenset(
    {"audience", "line", "size_range", "pattern", "motif_count", "print_placement",
     "ip_rating", "fitting",
     "plate_type", "bowl_type", "cutlery_type", "knife_type", "glass_type", "utensil_type"}
)  # fmt: skip


#: The plural nouns a template's text counts its colorways in ("in 12 washes", "in three
#: prints"), each with its singular. A derived style keeps a subset of the colorways, so
#: :func:`_restate_color_count` rewrites the count to the style's own (gen#143).
COLOR_COUNT_NOUNS = {
    "washes": "wash", "prints": "print", "colors": "color", "colorways": "colorway",
    "shades": "shade",
}  # fmt: skip
#: The counts a template spells out ("three prints"); index i is the word for i.
NUMBER_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "eleven", "twelve",
)  # fmt: skip
_COLOR_COUNT = re.compile(
    rf"\b(\d+|{'|'.join(NUMBER_WORDS[2:])})\s+({'|'.join(COLOR_COUNT_NOUNS)})\b", re.IGNORECASE
)


def _words(text: str) -> str:
    return words(text)


def _has_word(text: str, value: str) -> bool:
    return f" {_words(value).strip()} " in _words(text)


def value_pools(recs: list[dict]) -> dict[tuple[str, str], tuple[str, ...]]:
    """(leaf, key) -> the unit-free values the leaf's templates carry, in first-seen order."""
    pools: dict[tuple[str, str], dict[str, None]] = collections.defaultdict(dict)
    for r in recs:
        for a in r["attributes"]:
            if "unit_code" not in a:
                pools[(r["category_leaf"], a["key"])][str(a["value"])] = None
    return {k: tuple(v) for k, v in pools.items()}


def variable_keys(rec: dict, pools: dict[tuple[str, str], tuple[str, ...]]) -> list[str]:
    """The attribute keys a style derived from ``rec`` may change (see the module doc)."""
    names = " ".join([*rec["category_path"], rec["category_leaf"], rec["product_type"]])
    counts = collections.Counter(a["key"] for a in rec["attributes"])
    shared = collections.Counter(str(a["value"]).lower() for a in rec["attributes"])
    out = []
    for a in rec["attributes"]:
        key, value = a["key"], str(a["value"])
        if key in FROZEN_KEYS or "unit_code" in a or counts[key] > 1 or shared[value.lower()] > 1:
            continue
        if len(pools.get((rec["category_leaf"], key), ())) < 2 or _has_word(names, value):
            continue
        if any(value.lower() in t.lower() and not _has_word(t, value)
               for t in (rec["title"], rec["description"])):  # fmt: skip
            continue
        out.append(key)
    return out


def _line(rec: dict) -> str | None:
    if rec.get("product_line"):
        return str(rec["product_line"])
    return next((str(a["value"]) for a in rec["attributes"] if a["key"] == "line"), None)


def clone_key(rec: dict) -> tuple:
    """Leaf, brand, attributes and title, the range name taken out of both."""
    title, name = rec["title"], _line(rec)
    if name:
        title = re.sub(rf"\b{re.escape(name)}\b ?", "", title)
    if line_grammar.family(rec):  # a brand-led model is its plain twin (gen#662)
        title = re.sub(rf"^(Kids' )?{re.escape(rec['brand'])} ", r"\1", title)
    attrs = tuple(
        sorted((a["key"], str(a["value"])) for a in rec["attributes"] if a["key"] != "line")
    )
    return (rec["category_leaf"], rec["brand"], attrs, title.strip())


def twin_key(rec: dict) -> tuple:
    """Leaf, brand and title without the range name: two styles that share it read as one
    listing whatever their unseen attributes, so the build makes no second (clones included)."""
    leaf, brand, _, title = clone_key(rec)
    return (leaf, brand, title)


def _parts(value: str) -> list[str]:
    """A comma-joined attribute value's parts: "patent, suede" -> ["patent", "suede"]."""
    return [p.strip() for p in value.split(",")]


def _part_swaps(old: str, new: str) -> dict[str, str]:
    """Each part of ``old`` (lowercased) -> the part of ``new`` at its place, which a SKU
    holding that part takes; a shorter ``new`` gives its last part to the rest."""
    o, n = _parts(old), _parts(new)
    return {p.lower(): n[min(i, len(n) - 1)] for i, p in enumerate(o)}


def _sku_values(rec: dict, skus: list[dict], swaps: dict[str, dict[str, str]]) -> None:
    """Each SKU takes the values ``derive`` drew for a key it carries (``swaps``), then
    each style attribute whose key the SKUs carry lists only the parts they still hold:
    a shoe kept in its suede colors alone no longer says "patent, suede" (gen#145), and a
    title or description that names a dropped part names the first kept one instead
    ("Soft leather ballet flats" -> "Soft patent ballet flats", gen#148)."""
    for s in skus:
        for key, swap in swaps.items():
            if key in s:
                s[key] = swap.get(str(s[key]).lower(), s[key])
    for key in dict.fromkeys(a["key"] for a in rec["attributes"]):
        held = {str(s[key]).lower() for s in skus if key in s}
        if not held:
            continue
        entries = [a for a in rec["attributes"] if a["key"] == key]
        kept = [p for a in entries for p in _parts(str(a["value"])) if p.lower() in held]
        dropped = [p for a in entries for p in _parts(str(a["value"])) if p.lower() not in held]
        for a in entries:
            a["value"] = ", ".join(p for p in _parts(str(a["value"])) if p.lower() in held)
        if kept:  # an entry for a material no kept SKU holds goes (a style lists the ones it sells)
            rec["attributes"] = [a for a in rec["attributes"] if a["key"] != key or a["value"]]
        for part in dropped if kept else ():
            for text in ("title", "description"):
                rec[text] = _swap(rec[text], part, kept[0])


def _swap(text: str, old: str, new: str) -> str:
    """``old`` -> ``new`` as a whole word in any case, each occurrence keeping its case
    and an "a"/"an" before it agreeing with ``new`` (:func:`_article`):
    lower stays lower, a capital first letter stays capital, otherwise ``new`` as given.
    Its words match across a space or a hyphen, and ``&`` and "and" match each other, so
    "Hook & Loop" rewrites "hook and loop"."""
    body = re.sub(r"(?<![A-Za-z])and(?![A-Za-z])", r"\\&", re.escape(old))
    body = body.replace(r"\&", "(?:&|and)").replace(r"\-", r"[\s-]").replace(r"\ ", r"[\s-]+")
    pattern = r"(?:(?<![A-Za-z0-9])([Aa]n?) )?(?<![A-Za-z0-9])(" + body + r")(?![A-Za-z0-9])"

    def cased(m: re.Match[str]) -> str:
        article, hit = m.group(1), m.group(2)
        if hit.islower():
            word = new.lower()
        elif hit[0].isupper() and (len(hit) == 1 or hit[1:].islower()):
            word = new[0].upper() + new[1:]
        else:
            word = new
        if article is None:
            return word
        # An article just before the word agrees with the word that replaces it.
        fixed = _article(word)
        return f"{fixed.capitalize() if article[0].isupper() else fixed} {word}"

    return re.sub(pattern, cased, text, flags=re.IGNORECASE)


def _title(tpl: dict, name: str) -> str:
    old = _line(tpl)
    if old and re.search(rf"\b{re.escape(old)}\b", tpl["title"]):
        return re.sub(rf"\b{re.escape(old)}\b", name, tpl["title"], count=1)
    if tpl["title"].startswith("The "):
        return f"The {name} {tpl['title'][4:]}"
    return f"{name} {tpl['title']}"


def _article(word: str) -> str:
    return "an" if word[:1].lower() in "aeiou" else "a"


def _plural(word: str) -> str:
    if re.search(r"[^aeiou]y$", word):
        return word[:-1] + "ies"
    return word + ("es" if re.search(r"(s|x|z|ch|sh)$", word) else "s")


def _restate_color_count(text: str, n: int) -> str:
    """``text`` with each colorway count ("in 12 washes", "in three prints") made ``n``:
    "one wash" for a single colorway, else ``n`` in the template's own form (digits
    or a word). A title-cased noun ("3 Washes") stays title-cased ("One Wash")."""

    def restate(m: re.Match[str]) -> str:
        plural = m.group(2)
        if n == 1:
            phrase = f"one {COLOR_COUNT_NOUNS[plural.lower()]}"
            return phrase.title() if plural[0].isupper() else phrase
        if m.group(1).isdigit() or n >= len(NUMBER_WORDS):
            return f"{n} {plural}"
        word = NUMBER_WORDS[n]
        return f"{word.capitalize() if m.group(1)[0].isupper() else word} {plural}"

    return _COLOR_COUNT.sub(restate, text)


def _department(rec: dict) -> str:
    return str(rec["department"][0])
