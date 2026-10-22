"""One letter case for every category node and every attribute display name (gen#499).

The catalogue shows two conventions: industrial authored Title Case with distributor
abbreviations ("Handle Material", "Bore Dia.", "Hose, Tube, Fittings & Valves > Seals &
Gaskets > O-Ring Seals") and retail authored sentence case ("Handle material"). One key
(``handle_material``) was shown under both. A real retailer's feed is consistent after a
clean-up, so this module is that clean-up: **sentence case** for every category node and
every attribute display name, applied once, at export, to the finished document. The
authored literals are not edited (about 500 of them): the build keeps looking attributes
up by their authored name, and only the document it writes carries the new case. A machine
key (``handle_material``) is never touched.

The rule, per string (a category node, or an attribute name):

* the first letter is a capital, every later word is lower case;
* a word keeps its capitals when it is an acronym (two or more letters, all capitals:
  ``ANSI``, ``ER``, ``(EU)``), carries a digit (``AS568``), has a capital after its first
  letter (``iPhone``), is one capital letter standing alone or before a hyphen (the letter
  names a shape: ``T-slot nuts``, ``C-clamps``, ``V-belts``), or is on
  :data:`PROPER_NOUNS`;
* hyphen compounds are cased per part (``O-ring seals``, ``Cut-resistant gloves``).

:data:`PROPER_NOUNS` is the exception list: a brand, a person's name or a trade name keeps
its capital wherever it falls. A word is added to it with a reason, never "to make a test
pass". An acronym or a code needs no entry: the rule above keeps it.

Values are not part of this rule (a separate value-hygiene list is gen#497).
"""

from __future__ import annotations

import re
from collections.abc import Iterable
from typing import Any

#: The exception list: words that keep their capital in a sentence-case name. Each is a
#: brand, a person's name or a trade name. The key is the lower-case form, the value the
#: spelling to publish.
PROPER_NOUNS: dict[str, str] = {
    "torx": "Torx",  # a trade name: "Hex & Torx keys"
    "nike": "Nike",  # a real brand the retail catalogue carries (gen#332)
    "apple": "Apple",  # a real brand the retail catalogue carries (gen#332)
}

#: The file a build writes beside ``nested.jsonl``: ``{product_type: authored_names(...)}``.
AUTHORED_NAMES_FILE = "authored_names.json"

_PART = re.compile(r"[A-Za-z0-9]+")


def _keeps_capitals(part: str) -> bool:
    """True when ``part`` (letters and digits only) is an acronym, a code, a lone capital
    letter or has a capital inside it, so lower-casing it would change what it names."""
    if any(ch.isdigit() for ch in part):
        return True
    if part.isupper():  # ``ANSI``, ``ER``, and one capital letter (``T`` of ``T-slot``)
        return True
    return any(ch.isupper() for ch in part[1:])  # ``iPhone``


def sentence_case(name: str) -> str:
    """``name`` in sentence case under the exception list (see the module docstring)."""
    opened = False

    def part(match: re.Match[str]) -> str:
        nonlocal opened
        text = match.group(0)
        first, opened = not opened, True
        if text.lower() in PROPER_NOUNS:
            return PROPER_NOUNS[text.lower()]
        if _keeps_capitals(text):
            return text
        return text.capitalize() if first else text.lower()

    return _PART.sub(part, name)


def _renamed(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [entry | {"name": sentence_case(entry["name"])} for entry in entries]


def apply(doc: dict[str, Any]) -> dict[str, Any]:
    """A copy of ``doc`` (a nested or a flat document) with every category node and attribute
    display name in sentence case. Keys, values and ids are untouched."""
    out = dict(doc)
    if "category_path" in doc:
        out["category_path"] = [sentence_case(node) for node in doc["category_path"]]
        out["category_leaf"] = out["category_path"][-1]
    if "category_paths" in doc:
        out["category_paths"] = [[sentence_case(node) for node in p] for p in doc["category_paths"]]
    if "attributes" in doc:
        out["attributes"] = _renamed(doc["attributes"])
    if "variants" in doc:
        out["variants"] = [
            variant | {"attributes": _renamed(variant["attributes"])} if "attributes" in variant
            else variant
            for variant in doc["variants"]
        ]
    if "attribute_names" in doc:
        out["attribute_names"] = sorted({sentence_case(name) for name in doc["attribute_names"]})
    return out



def authored_names(names: Iterable[str]) -> dict[str, str]:
    """``{published: authored}`` for each authored name whose published form differs.

    The drawing code looks an attribute up by the name its type authored
    (``r["Milling Dia."]``), and the image bundle is rebuilt from the committed catalogue,
    whose names are sentence case (``Milling dia.``). The build writes this map beside the
    catalogue (:data:`AUTHORED_NAMES_FILE`) and :mod:`.bundle` reads the drawing input back
    through it, so a drawing is the same bytes and ``images.jsonl`` keeps its digests."""
    return {sentence_case(name): name for name in sorted(set(names)) if sentence_case(name) != name}
